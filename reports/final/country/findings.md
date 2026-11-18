# Country evidence from the cleaned sample

These are exploratory summaries of synthetic posts. The [country mapping](country_mapping.csv) preserves all 33 original location values and combines the one Scotland entry with UK for this analysis, leaving 32 groups. The raw and cleaned files are unchanged.

| Country group | Posts | Share dated 2023 | Median recorded interactions |
|---|---:|---:|---:|
| USA | 184 | 54.3% | 60 |
| UK (including Scotland) | 141 | 51.8% | 60 |
| Canada | 131 | 51.1% | 63 |
| Australia | 70 | 20.0% | 54 |
| India | 68 | 35.3% | 54 |

1. **Coverage is concentrated and differs over time.** The five largest groups contain 594 of 710 posts (83.7%). There are at least 68 posts per displayed group; the next largest has 17. More than half of the USA, UK and Canada posts are dated 2023, compared with one fifth of Australian posts. Check like-for-like periods before attributing a difference to geography.
2. **One platform-mix check barely moves the mean interaction counts.** Reweighting each of the five groups to the pooled platform frequencies across those groups changes each observed mean by less than 0.17 interactions per post. These calculations use [country-by-platform means](country_platform_interactions.csv) and [shared weights](common_platform_weights.csv), with no imputation. This check does not adjust for time or sentiment, measure sampling uncertainty, or establish a country effect. The country medians and middle 50% ranges in the [summary](country_summary.csv) also show why mean rankings do not describe every post.
3. **Comparing broad sentiment across countries is still an open task.** The supplied labels are sparse. The [original-label shares](country_supplied_label_pct.csv) divide each label count by all posts in that country group. They are provided alongside the [counts](country_supplied_label_counts.csv); they are not reviewed polarity results. After label review, report reviewed shares and exclusion rates, compare within platforms, and inspect whether the patterns persist outside 2023 wherever support permits.

Supporting coverage: [country × platform](country_platform_counts.csv), [country × year](country_year_counts.csv), and [platform-mix sensitivity](country_interactions_sensitivity.csv). Regenerate with `python scripts/country_explore.py`. Interactions means likes plus retweets, not exposure-normalized engagement. No statistical test or cultural inference is reported.
