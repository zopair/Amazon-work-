"""Command-line interface for evidence-first KDP market research."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .scoring import score_market
from .royalties import calculate_ebook_royalty


def read_records(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV must include a header row")
        return list(reader)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    score_parser = subparsers.add_parser("score", help="score observed Kindle niches")
    score_parser.add_argument("csv_path", type=Path)
    score_parser.add_argument("--as-of", required=True, help="reference date YYYY-MM-DD")
    score_parser.add_argument("--min-sample", type=int, default=10)
    score_parser.add_argument("--output", type=Path, default=Path("reports/kdp-market-score.json"))

    royalty_parser = subparsers.add_parser("royalty", help="estimate one Amazon.com Kindle sale")
    royalty_parser.add_argument("list_price_usd", type=float)
    royalty_parser.add_argument("--file-size-mb", type=float, required=True)
    royalty_parser.add_argument("--buyer-country", required=True)
    royalty_parser.add_argument("--vat-rate", type=float, default=0.0)
    royalty_parser.add_argument("--royalty-option", type=int, choices=[35, 70], default=70)
    royalty_parser.add_argument("--kdp-select", action="store_true")

    args = parser.parse_args()

    if args.command == "royalty":
        result = calculate_ebook_royalty(
            list_price_usd=args.list_price_usd,
            file_size_mb=args.file_size_mb,
            buyer_country=args.buyer_country,
            royalty_option=args.royalty_option,
            vat_rate=args.vat_rate,
            kdp_select_enrolled=args.kdp_select,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if not args.csv_path.is_file():
        parser.error(f"input CSV does not exist: {args.csv_path}")
    results = score_market(
        read_records(args.csv_path),
        as_of=args.as_of,
        minimum_sample=args.min_sample,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "report_type": "kdp-market-opportunity-screen",
        "scoring_version": "0.1.0",
        "as_of": args.as_of,
        "source_file": str(args.csv_path),
        "niches": results,
        "limitations": [
            "This report ranks observed signals; it does not estimate sales from BSR.",
            "Competitor observations are snapshots and may change.",
            "Gap and differentiation scores require a documented human review.",
            "Compare category-list position only within the same marketplace, category, format, and language; keep product BSR separate.",
        ],
    }
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(results)} niche assessments to {args.output}")
    for item in results:
        print(f"- {item['niche']}: {item['status']} | score={item['opportunity_score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
