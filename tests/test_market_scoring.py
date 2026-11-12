import unittest
from datetime import date, timedelta

from market_intelligence.scoring import score_market, validate_record


AS_OF = date(2026, 11, 12)


def record(asin, niche, bsr, reviews, published, category="Books > Business", marketplace="US"):
    return {
        "marketplace": marketplace,
        "niche": niche,
        "category_path": category,
        "asin": asin,
        "title": f"Evidence-backed title {asin}",
        "price": "4.99",
        "currency": "USD",
        "bsr": str(bsr),
        "review_count": str(reviews),
        "rating": "4.5",
        "publication_date": published.isoformat(),
        "format": "Kindle eBook",
        "page_count": "180",
        "evidence_url": f"https://www.amazon.com/dp/{asin}",
        "observed_at": AS_OF.isoformat(),
        "gap_score_0_5": "4",
        "differentiation_score_0_5": "4",
        "cover_palette": "navy, gold",
        "cover_style": "minimal editorial",
        "title_pattern": "outcome-led",
        "font_style": "sans-serif display",
        "interior_style": "structured practical guide",
        "content_type": "nonfiction",
        "content_value_notes": "Includes reproducible workflows and worksheets",
        "review_gap_notes": "Readers request more implementation examples",
    }


class MarketScoringTests(unittest.TestCase):
    def test_demand_is_compared_only_inside_same_marketplace_and_category(self):
        rows = []
        for i in range(5):
            rows.append(record(f"A{i}", "Niche A", 1000 + i * 100, 40, AS_OF - timedelta(days=30)))
            rows.append(record(f"B{i}", "Niche B", 50000 + i * 1000, 600, AS_OF - timedelta(days=600)))
            rows.append(record(f"C{i}", "Niche C", 100 + i * 10, 10, AS_OF - timedelta(days=20), category="Books > Education"))
        scored = {item["niche"]: item for item in score_market(rows, as_of=AS_OF)}
        self.assertGreater(scored["Niche A"]["demand_score"], scored["Niche B"]["demand_score"])
        self.assertIsNone(scored["Niche C"]["demand_score"])
        self.assertEqual(scored["Niche C"]["status"], "insufficient_comparators")

    def test_recent_books_and_low_review_counts_improve_entry_signal(self):
        rows = []
        for i in range(5):
            rows.append(record(f"LOW{i}", "Accessible niche", 1000 + i, 20, AS_OF - timedelta(days=30)))
            rows.append(record(f"HIGH{i}", "Mature niche", 2000 + i, 2000, AS_OF - timedelta(days=900)))
        scored = {item["niche"]: item for item in score_market(rows, as_of=AS_OF)}
        self.assertGreater(scored["Accessible niche"]["entry_score"], scored["Mature niche"]["entry_score"])

    def test_small_samples_are_not_given_an_opportunity_score(self):
        rows = [record(f"ONE{i}", "Small sample", 1000 + i, 20, AS_OF) for i in range(4)]
        result = score_market(rows, as_of=AS_OF)[0]
        self.assertEqual(result["status"], "insufficient_sample")
        self.assertIsNone(result["opportunity_score"])

    def test_invalid_evidence_url_is_rejected(self):
        item = record("BAD1", "Invalid", 1000, 10, AS_OF)
        item["evidence_url"] = "javascript:alert(1)"
        with self.assertRaises(ValueError):
            validate_record(item)

    def test_scores_are_bounded_and_no_sales_estimate_is_claimed(self):
        rows = []
        for i in range(5):
            rows.append(record(f"A{i}", "Niche A", 1000 + i, 20, AS_OF))
            rows.append(record(f"B{i}", "Niche B", 50000 + i, 600, AS_OF - timedelta(days=800)))
        results = score_market(rows, as_of=AS_OF)
        for result in results:
            self.assertGreaterEqual(result["opportunity_score"], 0)
            self.assertLessEqual(result["opportunity_score"], 100)
            self.assertNotIn("estimated_sales", result)
            self.assertNotIn("monthly_revenue", result)


if __name__ == "__main__":
    unittest.main()
