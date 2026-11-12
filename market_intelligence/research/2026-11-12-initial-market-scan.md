# Initial Kindle Market Scan — 2026-11-12

## Scope and evidence level

This is a category-level discovery snapshot for Amazon.com Kindle eBooks. It is not a 50-book competitor audit and does not select a final book concept. Category medians and turnover figures below are reported by KDPTop from its daily crawl of Amazon public Best Sellers pages, as of 2026-11-11. KDPTop's opportunity score is its own proprietary screening metric; it is not an Amazon metric and is not used by this repository's scoring engine.

## Category comparison

| Category | Median listed price | Median reviews | Average rating | Share with <100 reviews | New releases in last 90 days | KDPTop opportunity score |
|---|---:|---:|---:|---:|---:|---:|
| Artificial Intelligence (Computer Science) | $9.99 | 92 | 4.6 | 52% | 30% | 36/100 |
| Computers & Technology | $3.99 | 136 | 4.5 | 47% | 28% | 32/100 |
| Education (Science & Math) | $8.99 | 69 | 4.5 | 55% | 8% | 27/100 |
| Business & Money | $11.99 | 2,298 | 4.6 | 26% | 29% | 38/100 |

Sources:
- [Artificial Intelligence Kindle eBooks — KDPTop, 2026-11-11](https://kdptop.com/kdp/categories/artificial-intelligence-16977170011/)
- [Computers & Technology Kindle eBooks — KDPTop, 2026-11-11](https://kdptop.com/kdp/categories/computers-technology-156116011/)
- [Education / Science & Math Kindle eBooks — KDPTop, 2026-11-11](https://kdptop.com/kdp/categories/education-158687011/)
- [Business & Money Kindle eBooks — KDPTop, 2026-11-11](https://kdptop.com/kdp/categories/business-money-154821011/)

## Preliminary interpretation

1. **Artificial Intelligence** is a strong candidate for deeper sampling: its median review count is materially below the broad Business & Money category, while 30% of current best sellers were published in the last 90 days. This indicates category turnover, not guaranteed demand for a new title.
2. **Computers & Technology** also shows a relatively low review barrier and recent list turnover, but its $3.99 median price suggests substantial low-price competition. We need narrower subcategories before evaluating economics.
3. **Education / Science & Math** has the lowest median review count and a higher median price than broad technology, but only 8% of current best sellers were published in the last 90 days. This may be a slower-moving, evergreen opportunity; it needs subject-level segmentation.
4. **Business & Money** has the highest median price but also a very high median review count. Its apparent commercial value should not be confused with easy entry.

## Important measurement caveat

Amazon says Best Sellers Rank is relative to customer activity, updates at least daily, and is not an accurate way to track a book's sales or compare activity across categories. Each format has its own independent rank. Therefore:
- Never convert BSR into units sold or monthly revenue without a separately validated model.
- Compare BSR only within the same marketplace, category path, format, and language.
- Treat category medians as directional snapshots, not market size.

Official reference: [KDP — Sales Ranking](https://kdp.amazon.com/en_US/help/topic/G201648140).

## Next research gate

Before approving a manuscript, collect at least 50 Kindle eBook observations for each of the two strongest narrow niches. For each listing capture ASIN, exact title/subtitle, price, BSR, review count, rating, publication date, page count when available, cover palette/style/dimensions, title pattern, typography where measurable, audience, description structure, keyword themes, content type, reader complaints, and dated evidence URL.

The first candidates for deeper sampling are:
- Applied AI workflows for a specific professional audience.
- Applied mathematics/statistics or data-literacy learning for a clearly defined reader.
- A narrowly scoped software/engineering reference where original examples and tested workflows create a defensible advantage.

No book concept is approved by this scan alone.


## Narrower subcategory signals

A second pass on subcategories produced two candidates worth comparing against the broad categories:

| Kindle eBook subcategory | Snapshot date | Median price | Median reviews | Average rating | New list entries that day | New releases in 90 days | Third-party opportunity score |
|---|---|---:|---:|---:|---:|---:|---:|
| Generative AI | 2026-11-11 | $7.99 | 10 | 4.6 | 35 | Not surfaced in this result | 39/100 |
| Mathematical & Statistical (Applications & Software) | 2026-11-09 | $24.48 | 42 | 4.5 | 13 | 10% | 30/100 |
| Probability & Statistics (Applied) | 2026-11-09 | $11.99 | 102 | 4.4 | 54 | 7% | 28/100 |
| Algebra (Pure Mathematics) | 2026-11-08 | $9.99 | 46 | 4.4 | 47 | 14% | 24/100 |

Sources:
- [Generative AI Kindle eBooks — KDPTop, 2026-11-11](https://kdptop.com/kdp/categories/generative-ai-214873938011/)
- [Mathematical & Statistical Kindle eBooks — KDPTop, 2026-11-09](https://kdptop.com/kdp/categories/mathematical-statistical-16977138011/)
- [Probability & Statistics Kindle eBooks — KDPTop, 2026-11-09](https://kdptop.com/kdp/categories/probability-statistics-158713011/)
- [Algebra Kindle eBooks — KDPTop, 2026-11-08](https://kdptop.com/kdp/categories/algebra-158734011/)

### Interpretation and risks

- Generative AI has the lowest observed review median and the highest third-party opportunity score among these subcategory snapshots. However, 35 list entries changing in one day indicates a volatile category; this is not proof that 35 new books were published or that demand is stable. The category may reward current, practical material but creates a high maintenance burden.
- Mathematical & Statistical has a much higher median listed price and a lower review median than broad Mathematics. It may support more valuable specialist references, but the sample is still category-level and its 10% new-release share suggests slower turnover.
- Probability & Statistics and Algebra show different price/review/turnover patterns. They should not be merged into one "math" segment.

### Research priority

Run a 50-book audit in each of these two primary candidate subcategories:
1. Generative AI — segment by reader/job-to-be-done (e.g. business workflow, developer implementation, education) before choosing a title.
2. Mathematical & Statistical — segment by practical application and audience (e.g. data practitioners, business analysts, exam learners).

Do not use KDPTop's proprietary opportunity scores as our score. The numbers above are discovery signals only; our repository scoring requires dated competitor observations and documented reader-value evidence.


## Book-level reference cases (not self-publishing benchmarks)

### Six Math Essentials — applied mathematics

- KDPTop reported it at category list position #3 in Applied Mathematics Kindle eBooks on its Nov 9 snapshot, at $13.99, 5.0 stars, and 2 reviews.
- The US publisher lists 128 pages for the US edition. The official cover uses a deep purple field, a subtle hexagonal grid, one central gold hexagon, and restrained gold serif typography.
- Its value proposition is a short, accessible tour of six mathematical ideas: numbers, algebra, geometry, probability, analysis, and dynamics.
- Interpretation: a new release can enter a subcategory ranking with few reviews, but this title benefits from a highly recognized author and an established publisher. Do not treat it as a realistic indie-author baseline.

Sources: [KDPTop Applied Mathematics Kindle list](https://kdptop.com/kdp/categories/applied-158706011/), [Macmillan official book page](https://us.macmillan.com/books/9780374621797/sixmathessentials/), [Apple Books edition details](https://books.apple.com/us/book/six-math-essentials/id6758016585).

### Co-Existence: The Next Phase of AI — general AI guide

- KDPTop reported it at category list position #1 in Artificial Intelligence Kindle eBooks on its Nov 11 snapshot, at $16.99, 4.7 stars, and 74 reviews.
- The publisher lists 240 pages and a 6 × 9 inch print edition. The content is positioned as a research-informed field guide: working productively with AI, preserving human judgment, distinguishing real capability from hype, and adapting work and education.
- Interpretation: a strong general-interest AI book can command a higher price, but this is a major-publisher title by an established academic author, not a direct self-publishing benchmark.

Sources: [KDPTop Artificial Intelligence Kindle list](https://kdptop.com/kdp/categories/artificial-intelligence-16977170011/), [Penguin Random House official book page](https://www.penguinrandomhouse.com/books/813026/co-existence-by-ethan-mollick/).

## Design and format conclusions so far

- There is no universal bestseller cover palette: the two references use very different visual languages. We must measure cover patterns across the full 50-book sample in each niche rather than generalize from two titles.
- Page counts vary by product promise and edition: the reference math title is 128 pages; the AI field guide is 240 pages. Neither number is a target by itself.
- Print trim dimensions and Kindle eBook page counts are not interchangeable. Capture format and edition separately.
- For reflowable Kindle eBooks, reader font size is controlled by the device/app; do not claim a single market-winning body font size. Measure typography only from a fixed-layout or print preview.
- Amazon.com expanded the 70% eBook royalty price band to USD 2.99-$12.99 effective July 7, 2026. Egypt is among the 70% territories, but eligibility depends on the buyer's country, list price, KDP Select conditions in certain countries, and delivery costs. A US list price of $13.99 is outside the current 70% band. See [KDP price requirements](https://kdp.amazon.com/en_US/help/topic/G200634560) and [royalty territories/calculation](https://kdp.amazon.com/en_US/help/topic/G200634500).

These examples are reference cases only. The 50-book audit remains the gate before choosing our first title.
