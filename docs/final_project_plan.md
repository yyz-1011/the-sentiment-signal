# Final project plan

See [remaining tasks and team responsibilities](task_division.md) for individual assignments, label-review batches, handoffs, and completion checks.

## Problem and goals

An analyst comparing sentiment across countries needs to distinguish differences in the posts from differences in how many posts each country contributes, which platforms they appear on, and how sentiment is labeled.

1. **Primary question:** What differences in sentiment composition and recorded interactions can we describe across the better represented countries in this sample? Which patterns persist when we compare posts within platforms or check uneven time coverage?
2. **Secondary question:** Can a text classifier predict reviewed sentiment categories on held-out text groups better than a majority-class baseline? Where does it fail, and how sensitive is it to explicit hashtags?

The sample is synthetic. Its country field is a supplied geographic label, not an observation of culture, nationality, language, or residence. Country comparisons describe the sample only. Interactions means likes plus retweets; impressions are unavailable. A sentiment classifier and an optional exploration demo replace the recommendation-system language in the suggested timeline.

| Phase and deadline | Work and exit criteria | Proposed lead |
|---|---|---|
| Scope/pilot — 19–20 November | Agree questions and rubric; independently review pilot and adjudicate; confirm presentation logistics | Yizhou and Liwen review; Yuwei adjudicates |
| Reviewed labels — 21–23 November | Review remaining records; resolve disagreements; version labels, exclusions and class/group support | All; Yizhou coordinates |
| Development and exploration — 24–27 November | Compare baseline and text models on development data; complete reviewed country comparisons, platform/time checks, errors and hashtag sensitivity | Yizhou: models; Yuwei: countries; Liwen: checks/figures |
| Configuration freeze — 28 November | Agree data, labels, splits and model configuration before test evaluation; omit optional UI if necessary | All |
| Final evidence — 29 November | Run reserved test once; publish model results or a feasibility limitation; freeze country findings and final claims | Yizhou; all cross-review |
| Deck/script — 30 November | Complete a timed narrative from verified results; add repository URL and demonstration fallback if applicable | Liwen integrates; all contribute |
| Verification/rehearsal — 1–2 December | Independent clean-checkout run; two timed rehearsals; final sign-off, submission and offline backup | All |
| Presentation — 3 December | Present problem, methodology, country evidence, model results or limits, and future validation needs | All attend; speaking roles agreed in rehearsal |

If an official submission deadline is earlier, move the relevant freeze and delivery tasks forward. Treat 26–27 November as a correction buffer. Optional UI work must not delay evidence, validation or rehearsal. If reviewed labels or class support are not ready, follow the feasibility fallback in the task division rather than bypassing review or evaluation safeguards.

## How to explore

Start with counts by country, platform and year. Compare proportions within each country; use the full denominator or state precisely which records are excluded. Plot medians with spread for interactions, then check within-platform comparisons and comparable time subsets. Inspect post wording or hashtags to explain unexpected patterns. Use the five largest geography groups as the first display; retain the other countries in the tables. The 30-post display cutoff is a reporting convention, not an inference threshold.

Keep one exploration log row per question: question, denominator, observed result, alternative explanation, next check, and whether the result was exploratory. The midterm hypotheses are starting points. If formal tests are warranted, document the hypothesis, small-cell and dependence checks, effect sizes and any multiple-comparison treatment; do not present a pattern found here as independently confirmed.

## What counts as done

- A reproducible country comparison, with counts and clear denominators, plus two or three defensible findings or limitations.
- A reviewed target and coverage audit. If there is adequate class support, a grouped model comparison and a reserved-test report; otherwise, a documented feasibility result.
- A final slide deck and a presenter script built from the completed evidence. Do not reuse midterm numbers as model results.
- A clean-checkout run with dependencies and unchanged inputs. An interface is optional; do not trade label review, sensitivity checks, or rehearsal time for UI polish.
