# Exploration log

| Question | Comparison and denominator | Observed result | Alternative explanation or limit | Next check |
|---|---|---|---|---|
| Are countries sampled evenly over time? | 2023 posts / all posts per country group | 20.0% in Australia vs 54.3% in the USA | Time coverage could drive a geographic contrast | Examine comparable years with sufficient support |
| Does common platform weighting change observed country means? | One mean per country × platform cell; pooled platform shares across five major groups | Less than 0.17 interactions per post change in each group | Other composition differences and the unknown sampling design remain | Check within-platform distributions and time subsets |
| Do reviewed sentiment profiles differ? | Reviewed category shares and exclusions within each country | Pending adjudicated labels | Sparse labels and reviewer assignment may matter | Show support, exclusions and a within-platform check |

All entries are exploratory. Add unexpected and null findings as the analysis progresses.

## Yuwei's label-independent extension — 27 November 2026

Calculation checks are complete; independent teammate review and final claim approval are pending.
The [report](country/label_independent/findings.md) and [notebook](../../notebooks/04_country_comparisons.ipynb)
provide reproducible evidence. No reviewed sentiment result or hypothesis test is claimed.

| Record | Observed pattern | Supporting evidence and denominator | Alternative explanation | Sensitivity result | Justified conclusion |
|---|---|---|---|---|---|
| 1: uneven support and dates | Five groups contain 594/710 posts; observed 2023 endpoints differ across countries | `country_counts.csv`, `country_2023_date_ranges.csv`, and monthly support in the new report's `tables/`; each proportion uses all posts in that country | Different years/months can change a geographic comparison | Five fixed date views, including January–April 2023, disclose their own support | Restrict to common observed windows before interpreting a contrast; these are not known population or collection-coverage estimates |
| 2: mean versus typical post | USA mean is 66.80; Canada median is 63 versus USA/UK 60; country IQRs overlap | Full-period `country_window_summary.csv`; USA 184, UK 141, Canada 131, Australia 70, India 68 posts | Upper-tail observations and sample composition affect means | Report medians, IQRs and observed ranges; inspect the same countries inside all three platforms | One mean ranking does not describe a typical post or establish a geographic effect |
| 3: stable and unstable views | USA retains the largest mean in the three full-period platforms and five date views; lower-country ordering changes | `country_platform_window_summary.csv`, `country_window_ranks.csv`, `standardized_interactions.csv`; every row supplies its post count | Time, platform, wording, templates and unknown sampling remain possible explanations | UK/Canada mean ordering reverses before 2023; common-platform weighting changes means by at most 0.167; one-per-exact-text sensitivity changes main-group means by at most 0.324 | Retain both the stable descriptive USA mean pattern and the unstable complete ranking; the small weighting change is a null check, not proof of no confounding |
