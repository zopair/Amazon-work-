import unittest

from market_intelligence.royalties import calculate_ebook_royalty


class KindleRoyaltyTests(unittest.TestCase):
    def test_us_buyer_uses_seventy_percent_when_price_is_eligible(self):
        result = calculate_ebook_royalty(
            list_price_usd=9.99,
            file_size_mb=1.5,
            buyer_country="US",
            royalty_option=70,
        )
        self.assertEqual(result["applied_option"], 70)
        self.assertEqual(result["delivery_cost_usd"], 0.23)
        self.assertEqual(result["royalty_usd"], 6.83)

    def test_egypt_is_a_seventy_percent_territory(self):
        result = calculate_ebook_royalty(
            list_price_usd=12.99,
            file_size_mb=2,
            buyer_country="EG",
            royalty_option=70,
        )
        self.assertEqual(result["applied_option"], 70)
        self.assertEqual(result["royalty_usd"], 8.88)

    def test_price_above_us_seventy_percent_band_falls_back_to_35_percent(self):
        result = calculate_ebook_royalty(
            list_price_usd=13.99,
            file_size_mb=1,
            buyer_country="US",
            royalty_option=70,
        )
        self.assertEqual(result["applied_option"], 35)
        self.assertEqual(result["delivery_cost_usd"], 0.0)
        self.assertEqual(result["royalty_usd"], 4.90)

    def test_select_markets_require_kdp_select_for_seventy_percent(self):
        without_select = calculate_ebook_royalty(
            list_price_usd=9.99,
            file_size_mb=1,
            buyer_country="BR",
            royalty_option=70,
            kdp_select_enrolled=False,
        )
        with_select = calculate_ebook_royalty(
            list_price_usd=9.99,
            file_size_mb=1,
            buyer_country="BR",
            royalty_option=70,
            kdp_select_enrolled=True,
        )
        self.assertEqual(without_select["applied_option"], 35)
        self.assertEqual(with_select["applied_option"], 70)

    def test_vat_is_removed_before_royalty_calculation(self):
        result = calculate_ebook_royalty(
            list_price_usd=9.99,
            file_size_mb=1,
            buyer_country="US",
            royalty_option=35,
            vat_rate=0.05,
        )
        self.assertEqual(result["applied_option"], 35)
        self.assertEqual(result["vat_usd"], 0.48)
        self.assertEqual(result["royalty_usd"], 3.33)

    def test_35_percent_minimum_depends_on_file_size(self):
        with self.assertRaises(ValueError):
            calculate_ebook_royalty(
                list_price_usd=1.99,
                file_size_mb=10,
                buyer_country="US",
                royalty_option=35,
            )

    def test_unknown_marketplace_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_ebook_royalty(
                list_price_usd=9.99,
                file_size_mb=1,
                buyer_country="US",
                royalty_option=70,
                marketplace="UK",
            )


if __name__ == "__main__":
    unittest.main()
