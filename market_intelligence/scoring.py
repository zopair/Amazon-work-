"""Evidence-first market scoring for manually observed Kindle competitor listings.

Scores are comparative research signals, not sales estimates or revenue forecasts.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from statistics import median
from urllib.parse import urlparse
from typing import Any, Iterable


REQUIRED_FIELDS = (
    "marketplace", "niche", "category_path", "asin", "title", "price",
    "currency", "bsr", "review_count", "publication_date", "format",
    "evidence_url", "observed_at", "language", "gap_score_0_5",
    "differentiation_score_0_5",
)
EVIDENCE_FIELDS = (
    "price", "currency", "bsr", "review_count", "rating", "publication_date",
    "page_count", "format", "evidence_url", "observed_at", "cover_palette",
    "cover_style", "title_pattern", "font_style", "interior_style",
    "content_type", "content_value_notes", "review_gap_notes",
)
WEIGHTS = {
    "demand": 0.25,
    "entry": 0.20,
    "content_gap": 0.25,
    "differentiation": 0.15,
    "evidence": 0.15,
}


def _number(value: Any, field: str, *, minimum: float | None = None,
            maximum: float | None = None, integer: bool = False) -> float | int:
    try:
        number = int(value) if integer else float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a {'whole number' if integer else 'number'}") from None
    if minimum is not None and number < minimum:
        raise ValueError(f"{field} must be >= {minimum}")
    if maximum is not None and number > maximum:
        raise ValueError(f"{field} must be <= {maximum}")
    return number


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one observed competitor listing."""
    missing = [field for field in REQUIRED_FIELDS if not str(record.get(field, "")).strip()]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))

    normalized = {key: (value.strip() if isinstance(value, str) else value)
                  for key, value in record.items()}
    normalized["marketplace"] = str(normalized["marketplace"]).upper()
    normalized["asin"] = str(normalized["asin"]).upper()
    normalized["price"] = _number(normalized["price"], "price", minimum=0.01)
    normalized["bsr"] = _number(normalized["bsr"], "bsr", minimum=1, integer=True)
    normalized["review_count"] = _number(
        normalized["review_count"], "review_count", minimum=0, integer=True
    )
    normalized["gap_score_0_5"] = _number(
        normalized["gap_score_0_5"], "gap_score_0_5", minimum=0, maximum=5
    )
    normalized["differentiation_score_0_5"] = _number(
        normalized["differentiation_score_0_5"],
        "differentiation_score_0_5", minimum=0, maximum=5
    )
    rating_value = normalized.get("rating")\n    rating = "" if rating_value is None else str(rating_value).strip()
    normalized["rating"] = (
        _number(rating, "rating", minimum=0, maximum=5) if rating else None
    )
    pages_value = normalized.get("page_count")\n    pages = "" if pages_value is None else str(pages_value).strip()
    normalized["page_count"] = (
        _number(pages, "page_count", minimum=1, integer=True) if pages else None
    )
    try:
        normalized["publication_date_parsed"] = date.fromisoformat(
            str(normalized["publication_date"])
        )
        normalized["observed_at_parsed"] = date.fromisoformat(
            str(normalized["observed_at"])
        )
    except ValueError:
        raise ValueError("publication_date and observed_at must use YYYY-MM-DD") from None

    parsed_url = urlparse(str(normalized["evidence_url"]))
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("evidence_url must be an absolute HTTPS URL")

    for field in ("marketplace", "niche", "category_path", "asin", "title",
                  "currency", "format", "language"):
        if not str(normalized.get(field, "")).strip():
            raise ValueError(f"{field} cannot be empty")
    return normalized


def _distribution(records: list[dict[str, Any]], field: str) -> dict[str, int]:
    values = [str(row.get(field, "")).strip() for row in records
              if str(row.get(field, "")).strip()]
    return dict(Counter(values).most_common())


def _evidence_score(records: list[dict[str, Any]]) -> float:
    per_record = []
    for row in records:
        present = sum(row.get(field) is not None and bool(str(row.get(field, "")).strip())
                      for field in EVIDENCE_FIELDS)
        per_record.append(100.0 * present / len(EVIDENCE_FIELDS))
    return round(sum(per_record) / len(per_record), 2)


def _percentile_scores(groups: list[dict[str, Any]]) -> dict[tuple[str, str, str, str, str], float]:
    """Rank niche median BSR only against niches in the same market/category."""
    by_category: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for group in groups:
        if len(group["records"]) >= group["minimum_sample"]:
            by_category[(group["marketplace"], group["category_path"], group["format"], group["language"])].append(group)

    result: dict[tuple[str, str, str, str, str], float] = {}
    for peers in by_category.values():
        if len(peers) < 2:
            continue
        ordered = sorted(peers, key=lambda item: item["median_bsr"])
        count = len(ordered)
        index = 0
        while index < count:
            end = index
            while end + 1 < count and ordered[end + 1]["median_bsr"] == ordered[index]["median_bsr"]:
                end += 1
            average_rank = (index + end) / 2
            score = 100.0 * (count - 1 - average_rank) / (count - 1)
            for peer in ordered[index:end + 1]:
                key = (peer["marketplace"], peer["category_path"], peer["format"], peer["language"], peer["niche"])
                result[key] = round(score, 2)
            index = end + 1
    return result


def score_market(records: Iterable[dict[str, Any]], *,
                 as_of: date | str,
                 minimum_sample: int = 5) -> list[dict[str, Any]]:
    """Score niches from observed listings; never infer units sold from BSR."""
    if minimum_sample < 2:
        raise ValueError("minimum_sample must be at least 2")
    if isinstance(as_of, str):
        try:
            as_of = date.fromisoformat(as_of)
        except ValueError:
            raise ValueError("as_of must use YYYY-MM-DD") from None

    normalized = [validate_record(row) for row in records]
    if not normalized:
        raise ValueError("No competitor records were supplied")

    grouped: dict[tuple[str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        grouped[(row["marketplace"], row["category_path"], row["niche"], row["format"], row["language"])].append(row)

    groups = []
    for (marketplace, category_path, niche, book_format, language), items in grouped.items():
        currencies = {item["currency"] for item in items}
        if len(currencies) != 1:
            raise ValueError(f"Mixed currencies in {marketplace}/{category_path}/{niche}")
        groups.append({
            "marketplace": marketplace,
            "category_path": category_path,
            "niche": niche,
            "format": book_format,
            "language": language,
            "currency": items[0]["currency"],
            "records": items,
            "minimum_sample": minimum_sample,
            "median_bsr": median(item["bsr"] for item in items),
        })

    demand = _percentile_scores(groups)
    output = []
    for group in groups:
        items = group["records"]
        key = (group["marketplace"], group["category_path"], group["format"], group["language"], group["niche"])
        sample_size = len(items)
        median_reviews = median(item["review_count"] for item in items)
        low_review_share = 100.0 * sum(item["review_count"] <= 100 for item in items) / sample_size
        recent_share = 100.0 * sum(
            0 <= (as_of - item["publication_date_parsed"]).days <= 365
            for item in items
        ) / sample_size
        entry_score = round((low_review_share + recent_share) / 2, 2)
        gap_score = round(
            20 * sum(item["gap_score_0_5"] for item in items) / sample_size, 2
        )
        differentiation_score = round(
            20 * sum(item["differentiation_score_0_5"] for item in items) / sample_size, 2
        )
        evidence_score = _evidence_score(items)
        demand_score = demand.get(key)
        peer_count = sum(
            1 for candidate in groups
            if candidate["marketplace"] == group["marketplace"]
            and candidate["category_path"] == group["category_path"]
            and candidate["format"] == group["format"]
            and candidate["language"] == group["language"]
            and len(candidate["records"]) >= minimum_sample
        )

        if sample_size < minimum_sample:
            status = "insufficient_sample"
        elif demand_score is None:
            status = "insufficient_comparators"
        else:
            status = "scored"

        opportunity_score = None
        if status == "scored":
            opportunity_score = round(
                demand_score * WEIGHTS["demand"]
                + entry_score * WEIGHTS["entry"]
                + gap_score * WEIGHTS["content_gap"]
                + differentiation_score * WEIGHTS["differentiation"]
                + evidence_score * WEIGHTS["evidence"],
                2,
            )

        page_counts = [item["page_count"] for item in items if item["page_count"] is not None]
        output.append({
            "marketplace": group["marketplace"],
            "category_path": group["category_path"],
            "niche": group["niche"],
            "format": group["format"],
            "language": group["language"],
            "status": status,
            "sample_size": sample_size,
            "category_comparator_count": peer_count,
            "median_bsr": group["median_bsr"],
            "median_review_count": median_reviews,
            "share_with_100_or_fewer_reviews_pct": round(low_review_share, 2),
            "share_published_within_365_days_pct": round(recent_share, 2),
            "demand_score": demand_score,
            "entry_score": entry_score,
            "content_gap_score": gap_score,
            "differentiation_score": differentiation_score,
            "evidence_quality_score": evidence_score,
            "opportunity_score": opportunity_score,
            "median_price": round(median(item["price"] for item in items), 2),
            "currency": group["currency"],
            "median_page_count": median(page_counts) if page_counts else None,
            "cover_palette_distribution": _distribution(items, "cover_palette"),
            "cover_style_distribution": _distribution(items, "cover_style"),
            "title_pattern_distribution": _distribution(items, "title_pattern"),
            "font_style_distribution": _distribution(items, "font_style"),
            "interior_style_distribution": _distribution(items, "interior_style"),
            "content_type_distribution": _distribution(items, "content_type"),
            "review_gap_evidence": [
                item["review_gap_notes"] for item in items
                if str(item.get("review_gap_notes", "")).strip()
            ],
            "evidence_urls": sorted({item["evidence_url"] for item in items}),
            "scoring_weights": WEIGHTS.copy(),
            "interpretation": (
                "Comparative opportunity signal only. BSR is a relative rank, "
                "not a unit-sales or revenue estimate."
            ),
        })

    return sorted(
        output,
        key=lambda item: (
            item["opportunity_score"] is not None,
            item["opportunity_score"] if item["opportunity_score"] is not None else -1,
        ),
        reverse=True,
    )
