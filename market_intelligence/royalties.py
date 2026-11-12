"""Transparent Amazon.com Kindle eBook royalty estimator.

Rates and price bands are configurable constants sourced from current KDP help.
This estimator is not a substitute for the royalty preview in KDP Bookshelf.
"""
from __future__ import annotations

from math import ceil


US_70_PERCENT_MIN = 2.99
US_70_PERCENT_MAX = 12.99
US_35_PERCENT_MAX = 200.00
US_DELIVERY_COST_PER_MB = 0.15

SEVENTY_PERCENT_TERRITORIES = frozenset({
    "AD", "AU", "AT", "BH", "BE", "BR", "CA", "EG", "FR", "DE",
    "GI", "GG", "HK", "IN", "IE", "IM", "IT", "JP", "JE", "JO",
    "SA", "KW", "LB", "LI", "LU", "MO", "MX", "MC", "NL", "NZ",
    "OM", "QA", "SM", "CH", "ES", "TW", "TH", "AE", "GB", "US", "VA",
})
KDP_SELECT_REQUIRED = frozenset({"BR", "IN", "JP", "MX"})


def _round_money(value: float) -> float:
    return round(value + 1e-10, 2)


def _us_35_percent_minimum(file_size_mb: float) -> float:
    if file_size_mb < 3:
        return 0.99
    if file_size_mb < 10:
        return 1.99
    return 2.99


def calculate_ebook_royalty(
    *,
    list_price_usd: float,
    file_size_mb: float,
    buyer_country: str,
    royalty_option: int = 70,
    vat_rate: float = 0.0,
    kdp_select_enrolled: bool = False,
    marketplace: str = "US",
) -> dict:
    """Estimate one sale's royalty using Amazon.com KDP rules.

    vat_rate is a decimal VAT rate, e.g. 0.05 for 5%. It is applied as
    VAT-inclusive pricing: VAT = price * rate / (1 + rate).
    """
    if marketplace.upper() != "US":
        raise ValueError("Version 0.1 supports Amazon.com (US) pricing only")
    if royalty_option not in (35, 70):
        raise ValueError("royalty_option must be 35 or 70")
    if list_price_usd <= 0 or list_price_usd > US_35_PERCENT_MAX:
        raise ValueError("list_price_usd must be > 0 and <= 200")
    if file_size_mb < 0:
        raise ValueError("file_size_mb cannot be negative")
    if vat_rate < 0 or vat_rate > 1:
        raise ValueError("vat_rate must be between 0 and 1")

    country = buyer_country.strip().upper()
    if not country:
        raise ValueError("buyer_country is required")

    min_35_price = _us_35_percent_minimum(file_size_mb)
    if list_price_usd < min_35_price:
        raise ValueError(
            "Amazon.com 35% minimum for a " + str(file_size_mb)
            + " MB file is " + format(min_35_price, ".2f")
        )

    territory_eligible = country in SEVENTY_PERCENT_TERRITORIES
    select_required = country in KDP_SELECT_REQUIRED
    select_condition_met = not select_required or kdp_select_enrolled
    price_eligible = US_70_PERCENT_MIN <= list_price_usd <= US_70_PERCENT_MAX
    use_70 = (
        royalty_option == 70
        and territory_eligible
        and select_condition_met
        and price_eligible
    )

    vat_amount = list_price_usd * vat_rate / (1 + vat_rate)
    delivery_cost = 0.0
    reason = "35% option selected"

    if use_70:
        rounded_kb = ceil(file_size_mb * 1024)
        rounded_mb = rounded_kb / 1024
        delivery_cost = max(0.01, _round_money(rounded_mb * US_DELIVERY_COST_PER_MB))
        royalty_rate = 0.70
        applied_option = 70
        reason = "70% eligible: price band, buyer territory, and KDP Select conditions satisfied"
    else:
        royalty_rate = 0.35
        applied_option = 35
        if royalty_option == 70:
            if not territory_eligible:
                reason = "Buyer country is outside the 70% royalty territories; 35% applies"
            elif not select_condition_met:
                reason = "KDP Select is required for this buyer country; 35% applies"
            elif not price_eligible:
                reason = "Price is outside the Amazon.com 70% band ($2.99-$12.99); 35% applies"

    royalty_base = max(0.0, list_price_usd - vat_amount - delivery_cost)
    royalty = _round_money(royalty_rate * royalty_base)

    return {
        "marketplace": "US",
        "currency": "USD",
        "buyer_country": country,
        "list_price_usd": _round_money(list_price_usd),
        "file_size_mb": file_size_mb,
        "vat_rate": vat_rate,
        "vat_usd": _round_money(vat_amount),
        "delivery_cost_usd": _round_money(delivery_cost),
        "requested_option": royalty_option,
        "applied_option": applied_option,
        "royalty_rate": royalty_rate,
        "royalty_usd": royalty,
        "buyer_territory_eligible": territory_eligible,
        "kdp_select_required": select_required,
        "kdp_select_condition_met": select_condition_met,
        "price_eligible_for_70": price_eligible,
        "reason": reason,
        "source_policy": "KDP US eBook pricing and digital book pricing help; verify in KDP royalty preview before publishing",
    }
