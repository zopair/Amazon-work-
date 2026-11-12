# KDP Market Intelligence

An evidence-first research layer alongside the existing book-production pipeline. It does not scrape Amazon, bypass access controls, or infer sales from Best Sellers Rank (BSR).

## Why this exists

Before producing a book, collect comparable competitor observations and identify a defensible reader-value gap. This package scores niches using transparent, reproducible signals. It is a screening aid, not a sales forecast.

## Data collection protocol

1. Select one Amazon marketplace, one Kindle format, one language, one category path, and one narrowly defined niche per sample.
2. Capture at least 50 relevant books per niche for a decision-grade study. Ten is the default minimum for a preliminary score. Five can be used only for an explicitly provisional screen; it is not enough to claim market demand.
3. Record each listing's ASIN, exact title/subtitle, price/currency, BSR as observed, review count, rating, publication date, format, page count when available, language, and product URL.
4. Inspect cover palette, cover style, cover image dimensions when observable, title/subtitle pattern, typography, interior style, audience, description structure, keyword themes, and content type. Record factual observations, not subjective assumptions. For reflowable Kindle eBooks, reader-controlled font size is not a stable product attribute; record font sizes only when a fixed-layout or print preview makes them measurable.
5. Read a structured sample of recent positive and critical reviews. Record recurring unmet needs in your own words; do not copy review text. Set gap_score_0_5 and differentiation_score_0_5 only after writing supporting notes.
6. Record observed_at as the date the listing was inspected. Keep a new snapshot rather than silently overwriting historical observations.
7. Use permitted public access, official Amazon interfaces, or clearly attributed third-party market snapshots. Do not run scraping against Amazon, evade rate limits, automate account actions, or republish Amazon reviews or copyrighted descriptions.

## Data dictionary

- marketplace: Amazon marketplace code, e.g. US, UK, DE.
- niche: narrowly scoped reader/problem segment.
- category_path: exact Amazon category path used for BSR comparability.
- asin: Amazon Standard Identification Number.
- category_list_rank: observed position in the selected Kindle category Best Sellers list (e.g. 1-100). Lower is a stronger position within that exact list; it is not units sold.
- bsr: the product-detail-page Best Sellers Rank, captured separately when visible. Do not substitute category_list_rank for BSR or compare BSR across categories.
- gap_score_0_5: human-reviewed strength of recurring unmet reader needs, supported by review-gap notes.
- differentiation_score_0_5: human-reviewed ability to create a meaningfully better/original product, supported by content-value notes.
- evidence_url, observed_at: provenance and observation timestamp.
- design/content fields capture cover palette/style/dimensions, title/subtitle pattern, typography, interior style, audience, description structure, keyword themes, content type, and value proposition. The report retains each competitor observation for audit.

## Scoring model

Only niches with at least ten observed books and at least two comparable niches in the same marketplace/category/format/language receive a composite score.

| Component | Weight | Definition |
|---|---:|---|
| Demand signal | 25% | Relative median category-list position among comparable niches only |
| Entry signal | 20% | Average of share with <=100 reviews and share published in the last 365 days |
| Reader-value gap | 25% | Mean human gap score normalized to 0-100 |
| Differentiation | 15% | Mean human differentiation score normalized to 0-100 |
| Evidence quality | 15% | Average of evidence-field completeness and observation freshness (100% when observed within 30 days) |

The weights and the <=100-review / 365-day entry thresholds are version 0.1 screening heuristics, not a statistically validated prediction model. Calibrate them against the first 3-6 months of our own KDP outcomes before using the score as a production decision rule. Gap and differentiation ratings must have written evidence notes. Observations older than 30 days reduce evidence quality; observations dated after the report date are rejected.

No score converts category-list position, BSR, or review counts into sales. A single-category sample cannot establish market size. Price and page count are descriptive outputs, not profitability estimates. KDP royalties must be calculated separately using current marketplace-specific terms and the actual delivery fee.

## Human scoring rubric

Use the same rubric across all niches and keep the written notes:

- Reader-value gap (0): no recurring unmet need found.
- 1: isolated or vague complaint; no pattern.
- 2: repeated but low-impact complaint in a small review sample.
- 3: recurring, specific need across independent recent reviews.
- 4: repeated high-impact need plus clear evidence current books do not solve it well.
- 5: critical, repeated need with a clearly defined reader outcome and no adequate competing solution found in the reviewed sample.

Differentiation (0): no meaningful improvement; 1: cosmetic changes; 2: modest organization or added material; 3: substantial original examples or exercises; 4: tested workflows, case studies, or reusable tools; 5: independently validated, distinctly superior outcome supported by original research or demonstrated results.

## Run locally

Python 3.12+; standard library only. The default minimum sample is ten books per niche; use --min-sample 5 only for a provisional screen.

    python -m unittest discover -s tests -v
    python -m market_intelligence.cli score data/templates/kdp_competitors.csv --as-of 2026-11-12 --output reports/kdp-market-score.json

The template contains headers only, so the scoring command will correctly reject it until real, sourced observations are added.

## Important KDP constraints

- KDP requires disclosure of AI-generated text, images, and translations. The publisher remains responsible for rights, accuracy, and content quality.
- KDP currently lists Arabic as eBook-only. RTL paperback support is limited to Hebrew, Yiddish, and Japanese. Do not assume an Arabic paperback or a bilingual RTL print layout will be accepted.
- Kindle eBook covers: ideal 1,600 x 2,560 px, RGB, JPEG/TIFF, under 50 MB; follow the current KDP cover requirements.
- Always use KDP's current language, manuscript, cover, pricing, and content rules at the point of upload.

## No-cost and resource policy

- This toolkit has no paid runtime dependencies.
- The public repository's GitHub Actions workflow runs only fast unit tests; no persistent cloud VM, paid runner, large model download, or paid API is required.
- GitHub Pages is not used as a commercial storefront. The repository and GitHub Releases are for source, research snapshots, and validated production artifacts.
- Do not create AWS resources or enable billable services without a separately reviewed zero-cost guarantee and explicit approval.
