# Final project plan

See [remaining tasks and team responsibilities](task_division.md) for individual assignments, label-review batches, handoffs, and completion checks.

## Problem and goals

An analyst comparing sentiment across countries needs to distinguish differences in the posts from differences in how many posts each country contributes, which platforms they appear on, and how sentiment is labeled.

1. **Primary question:** What differences in sentiment composition and recorded interactions can we describe across the better represented countries in this sample? Which patterns persist when we compare posts within platforms or check uneven time coverage?
2. **Secondary question:** Can a text classifier predict reviewed sentiment categories on held-out text groups better than a majority-class baseline? Where does it fail, and how sensitive is it to explicit hashtags?

The sample is synthetic. Its country field is a supplied geographic label, not an observation of culture, nationality, language, or residence. Country comparisons describe the sample only. Interactions means likes plus retweets; impressions are unavailable. A sentiment classifier and an optional exploration demo replace the recommendation-system language in the suggested timeline.

| Week | Work and exit criteria | Proposed lead |
|---|---|---|
| 5 | Agree the problem and label rubric; independently label and adjudicate a pilot; finish review; check class and group support; compare baselines on grouped development folds. If support fails, explain and resolve before scoring. | Yizhou, with all members reviewing |
| 6 | Explore coverage, sentiment shares, interactions and platform composition. Check 2023, sparse groups, and UK/Scotland mapping. Keep unexpected or null findings and alternative explanations in the exploration log. | Yuwei; Liwen verifies denominators |
| 7 | Review model errors on development data and compare with/without hashtags on the same splits. Review the strongest country patterns against plausible alternative explanations. Freeze model and label decisions. | Yizhou and Liwen; Yuwei checks interpretation |
| 8 | Run the final holdout once; freeze figures, versions, and claims. Reproduce from a clean checkout. Build an optional country filter or prediction demo only if the evidence and evaluation are ready. Keep screenshots as a fallback. | All; Liwen leads visuals/demo |
| 9 | Present the question, data, cross-country evidence, classifier results or feasibility limit, and what real-data validation would require. Confirm the time limit and rehearse with Q&A. | All |

## How to explore

Start with counts by country, platform and year. Compare proportions within each country; use the full denominator or state precisely which records are excluded. Plot medians with spread for interactions, then check within-platform comparisons and comparable time subsets. Inspect post wording or hashtags to explain unexpected patterns. Use the five largest geography groups as the first display; retain the other countries in the tables. The 30-post display cutoff is a reporting convention, not an inference threshold.

Keep one exploration log row per question: question, denominator, observed result, alternative explanation, next check, and whether the result was exploratory. The midterm hypotheses are starting points. If formal tests are warranted, document the hypothesis, small-cell and dependence checks, effect sizes and any multiple-comparison treatment; do not present a pattern found here as independently confirmed.

## What counts as done

- A reproducible country comparison, with counts and clear denominators, plus two or three defensible findings or limitations.
- A reviewed target and coverage audit. If there is adequate class support, a grouped model comparison and a reserved-test report; otherwise, a documented feasibility result.
- A final slide deck and a presenter script built from the completed evidence. Do not reuse midterm numbers as model results.
- A clean-checkout run with dependencies and unchanged inputs. An interface is optional; do not trade label review, sensitivity checks, or rehearsal time for UI polish.
