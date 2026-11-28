# Remaining tasks and team responsibilities

Updated 19 November 2026 using the repository state at commit `8638cf8`. This document turns the [final project plan](final_project_plan.md) into individual assignments, handoffs, and completion checks. The planning presentation date is **Thursday, 3 December 2026**. Proposed working deadlines below use America/New_York local dates. Assignments remain for the team to confirm; the session time, duration, and official submission cutoff are still unknown. Dates are targets, not records of completed work.

## Actual progress on 27 November

See [Yizhou's work report](yizhou_work_report.md) for completed preparation and the [operational handoff](downstream_handoff.md) for each member's next action. Full review worksheets, machine-only triage, a validator and tested evaluation code are ready. The user confirmed no independent review is complete. November 23 label completion is overdue; no reviewed classifier scores or final-test results exist. Do not treat the remaining planned freeze dates as completed work.

## Shared purpose and current status

We will investigate how observed sentiment and recorded interactions differ across adequately represented country groups, check whether comparisons depend on sample composition, and evaluate whether text can predict reviewed sentiment categories better than a simple baseline.

The country column describes supplied geography, not measured culture. The source is synthetic. The previous hypotheses are starting questions; unexpected, null, or inconclusive findings should be retained and explained.

Cleaning, feature exploration, the original EDA, country tables, and initial country findings already exist. Reuse them. Reviewed sentiment labels, classifier results, and the final presentation are not yet committed at the reference version above. Preparing scripts is not the same as completing these analyses.

## Ownership and independent review

| Workstream | Primary owner | Reviewer | Required handoff |
|---|---|---|---|
| Label-review coordination and adjudicated file | Yizhou | All three approve decisions | Versioned labels, review records, coverage and exclusions |
| Country sentiment and time comparisons | Yuwei | Liwen | Reproducible tables, figures and interpretations |
| Platform and hashtag robustness | Liwen | Yuwei | Sensitivity results and alternative explanations |
| Model development and evaluation | Yizhou | Liwen | Baseline comparison, errors and final test report |
| Final figures and presentation assembly | Liwen | Yizhou and Yuwei | Consistent figures, slides and speech script |
| Reproduction and repository release | Yizhou | One teammate runs independently | Verified checkout and accurate README |

A reviewer checks calculations, denominators and interpretation, rather than merely approving a file. All members should understand both research questions and approve the final claims.

## First shared task: sentiment label review

This is the central dependency for broad country sentiment comparisons and meaningful classifier evaluation. Follow the [review guide](label_review.md).

### Pilot

Yizhou runs the existing command from the repository root:

```bash
python scripts/prepare_label_review.py
```

The current script prepares **54 pilot posts**, not worksheets for the whole dataset. It writes separate copies to `generated/label_review/` and refuses to overwrite an existing worksheet. Use a new output directory for a deliberately new version.

- **Yizhou and Liwen:** independently label the same 54 posts without consulting each other's decisions or looking up supplied labels where feasible.
- **Yuwei:** adjudicate disagreements and document confusing cases.
- **All three:** revise and freeze the rubric. Revisit pilot decisions if the rules change materially.

Use positive, negative or neutral for the dominant expressed evaluation. Record genuinely mixed or unclear cases for adjudication; do not default unfamiliar emotion labels to neutral. The archived proposed mapping is not reviewed ground truth.

### Remaining records

The complete blank worksheets for the **656 non-pilot records** are now committed in `data/label_review/v1/`. Yizhou prepared them using `python scripts/prepare_label_review.py --full-package`; independent review and adjudication remain outstanding. Split them into the following mixed-country, mixed-platform batches:

| Batch | Posts | Independent reviewers | Adjudicator |
|---|---:|---|---|
| A | 219 | Yizhou and Liwen | Yuwei |
| B | 219 | Liwen and Yuwei | Yizhou |
| C | 218 | Yuwei and Yizhou | Liwen |

Do not assign an entire country to a single pair. Keep the record IDs stable, verify that every non-pilot record appears in exactly one batch, and preserve both independent decisions before adjudication. Resolve inconsistent final decisions for identical text groups rather than allowing contradictory modeling targets.

### Final reviewed data

The adjudicated file must contain exactly one row per cleaned `source_record`, with:

```text
source_record,reviewed_sentiment,decision_note
```

Allowed final decisions are `positive`, `negative`, `neutral`, and `exclude`. Every row needs a note. Preserve original labels, initial reviewer decisions, adjudication reasons and the rule version in separate linked review records. Excluded records stay in EDA; report their distribution by country rather than silently removing them.

Yizhou checks all **710 records**, unique IDs, allowed values, decision notes and class/group support. Publish approved artifacts in a tracked location such as `data/reviewed/`; that directory must be created when the data is ready. `generated/` is Git-ignored and is not a publication location.

**Done when:** all records are adjudicated, conflicts are resolved, coverage and exclusions are summarized, and all three approve the label version. Do not invent human review or prefill final labels from the supplied sentiment column.

## Yizhou: modeling and reproducibility

### Before labels are ready

1. Reproduce the existing workflow and resolve dependency problems.
2. Confirm that the authoritative cleaned snapshot is unchanged.
3. Coordinate the review schema and assignments above.
4. Read the evaluation script and document its split and model-selection choices before examining scores.

### After adjudication

Run development evaluation with the approved file, for example:

```bash
python scripts/evaluate_sentiment.py \
  --reviewed data/reviewed/adjudicated.csv
```

The existing runner compares a majority baseline, logistic regression and linear SVM on common grouped splits. It uses text without explicit hashtags as the primary input and original text as a sensitivity comparison. Country, engagement and IDs are not primary predictors. Identical normalized text stays in one partition.

Produce:

- Reviewed class counts and inclusion/exclusion coverage.
- Development macro-F1 comparisons and fold variation.
- An explanation of class support and split design.
- Development errors involving mixed emotion, negation, ambiguous labels, rare classes or templates.
- A record of the selected configuration and a small, documented set of any refinements.

If the runner rejects class support, bring the issue to the team. Do not silently drop a class, try seeds until a preferred score appears, or bypass safeguards. A documented feasibility limitation is an acceptable result.

When the configuration and labels are frozen, run the same command with `--finalize` in the **same output directory**. This opens the reserved test evaluation. Preserve that run; do not use fresh directories to repeatedly tune against the test set. Publish approved result tables under `reports/final/model/` with the data/label version and split IDs; create that directory when results exist.

**Handoff to Liwen:** baseline and model comparison, per-class final metrics, confusion matrix, error examples, limitations and a plain-language explanation of improvement or failure to improve.

**Done when:** another member can reproduce the results, every score identifies its partition and support, and no exploratory development result is presented as final-test performance.

## Yuwei: country analysis and interpretation

Start with the [existing country findings](../reports/final/country/findings.md). The current analysis combines the one Scotland record with UK while retaining the original source column. Keep that rule consistent unless the team explicitly revises it.

### Work that can begin immediately

1. Inspect country-by-platform and country-by-year coverage.
2. Examine comparable time periods, particularly unequal representation in 2023.
3. Inspect interaction distributions and within-platform comparisons.
4. Identify cells that are too sparse for meaningful interpretation.

### Work after reviewed labels arrive

1. Compute reviewed sentiment proportions within each country.
2. Show exclusion counts or rates and state whether each chart uses all posts or only classifiable posts as its denominator.
3. Start main displays with the five largest groups; retain smaller groups descriptively with their support.
4. Check whether patterns persist within platforms and supported time subsets.
5. Inspect example posts and retain unexpected or null findings.

The existing country sentiment CSVs contain the **publisher's original labels**. They must not be described as reviewed polarity results. Extend the country workflow with new reviewed-label summaries rather than overwriting the source data.

For each of two or three final findings, write:

> Observed pattern → supporting table and denominator → alternative explanation → sensitivity result → justified conclusion.

Add these records to the [exploration log](../reports/final/exploration_log.md). Proposed new work can live in `notebooks/04_country_comparisons.ipynb`, with approved tables in `reports/final/country/`. Do not claim cultural differences or population-level effects from this synthetic sample.

**Handoff to Liwen:** reproducible figures and underlying tables, a short explanation of each, supported comparisons, unresolved questions and caveats.

**Done when:** charts state denominators, comparisons show support, exclusion effects are visible, and Liwen can independently verify the key calculations.

## Liwen: robustness, visualizations and presentation

### Analytical checks

1. Independently verify Yuwei's geography mapping, denominators and country counts.
2. Investigate whether platform composition explains a country pattern; build on the existing platform-mix check.
3. Review Yizhou's with/without-hashtag results on identical splits.
4. Inspect wording, hashtags and synthetic templates as alternative explanations.
5. Record contradictory, null and unresolved results rather than selecting only attractive differences.

A possible new notebook is `notebooks/05_robustness_checks.ipynb`. Only add analyses that answer the project questions. Formal tests require support and assumption checks, appropriate effect-size interpretation and disclosure of exploratory selection; significant results are not a required deliverable.

### Visuals and narrative

Select approximately four to six essential figures, subject to the final time limit:

- Country coverage.
- Reviewed sentiment composition by country.
- One meaningful sensitivity comparison.
- Model-versus-baseline results.
- A confusion matrix or selected errors when useful.

Use consistent colors, units, labels and support annotations. Each chart should answer a question. Assemble the deck using the [presentation outline](../reports/final/presentation_outline.md), with the speech script in a proposed `presentation/final/` directory once authored. These proposed paths do not indicate that the files are already complete.

An interface is optional. Build one only after analysis and evaluation are finished. A reliable notebook walkthrough or screenshots is sufficient. A text-only model's prediction should not silently change when the country selector changes, and uncalibrated scores should not be presented as probabilities.

**Done when:** Yuwei approves the geographic interpretation, Yizhou approves model numbers, all three approve the claims, and the final narrative fits the confirmed session duration.

## Dated schedule through 3 December

Start on 19 November; work proceeds in parallel where dependencies allow. Existing course Week 5–9 labels describe phases, not additional weeks available before this presentation.

| Dates in 2026 | Checkpoint and required outcome | Yizhou | Yuwei | Liwen |
|---|---|---|---|---|
| 19–20 November | **A — Scope and pilot, due 20 November.** Agree the question and rubric; independently review 54 pilot posts and adjudicate disagreements. Confirm the final-session time, duration and submission requirements. | Run pilot preparation, review independently, verify environment and data version | Adjudicate pilot; inspect country/year coverage | Independently review pilot; check existing charts and presentation outline |
| 21–23 November | **B — Reviewed labels, due 23 November.** Finish all 656 remaining records, adjudication, exclusions and class/group-support checks. Revisit pilot decisions if the rubric changed. | Coordinate batches, review assigned records, validate and version all 710 decisions | Review assigned records and adjudicate Batch A; continue label-independent country comparisons | Review assigned records and adjudicate Batch C; verify platform coverage |
| 24–25 November | First country findings and development model comparison due 25 November | Run grouped development evaluation; document baseline, candidate models and support | Produce reviewed within-country shares and exclusion rates; compare within platforms and supported time subsets | Check denominators, inspect platform/hashtag explanations and prepare initial final figures |
| 26–27 November | **C — Development evidence, due 27 November.** Cross-review country conclusions, model errors and sensitivity checks. Keep these days as a correction buffer, not a new feature sprint. | Review errors and a small set of development refinements; send result tables | Complete two or three claim–evidence–limitation records, including null findings | Verify country results and hashtag sensitivity; assemble a complete narrative draft |
| 28 November | **Configuration freeze.** Agree label version, eligibility, split IDs, primary model and configuration before opening the test results. Decide whether to omit the optional UI. | Record frozen versions and model-selection decision | Approve geographic interpretation and limits | Approve model presentation and essential figures; drop UI if it threatens readiness |
| 29 November | **D — Results freeze.** Run the reserved test once after configuration approval; document baseline and selected-model results or a feasibility limitation. Freeze analytical claims. | Execute final evaluation in the same output directory; publish approved tables and errors | Cross-check final country figures against tables | Cross-check model numbers and integrate all verified results |
| 30 November | Complete deck and speech draft due; establish the final submission bundle | Supply reproducibility and model-method explanation | Supply country findings and Q&A answers | Assemble slides and script to fit the confirmed duration; add repository URL and optional demo fallback |
| 1 December | Independent clean-checkout run and first timed rehearsal | Resolve reproduction issues and verify README links | Independently run the project, check chart claims and join rehearsal | Lead timed deck walkthrough and revise pacing |
| 2 December | **E — Presentation readiness.** Second rehearsal, final sign-off, accessible files and offline backup. Submit by the official cutoff if earlier than the presentation. | Verify repository release and submission contents | Verify interpretation, Q&A readiness and backup materials | Freeze slide/script layout and test display or demo fallback |
| **3 December** | **Final Presentation.** Arrive at the confirmed session time; use only the approved version. | Attend; explain data, labels and modeling as needed | Attend; explain country results and interpretation | Attend; operate or present visuals/demo as agreed |

**Freeze rules:** after 29 November, analytical changes are for documented factual or reproducibility corrections, not further test-driven model tuning. Rerun affected checks and obtain cross-review for a necessary correction. Visual and pacing edits may continue through 2 December without changing verified claims. Do not assume the midterm five-minute limit applies. Follow any earlier official submission cutoff once known.

**If a checkpoint slips:** assess label completion and class support on 23 November. If labels are unfinished, prioritize adjudication and remove optional features; do not manufacture reviewed labels or present unreviewed scores. If adequate support or reliable evaluation cannot be achieved by the 28 November decision, present the documented modeling feasibility limitation and the verified country analysis. Keep the 29 November evidence cutoff and 1–2 December verification/rehearsal buffer. Never turn a missed deadline into a completed status without evidence.

Keep brief progress checks on 20, 23, 25, 27 and 29 November, then use the 1 and 2 December rehearsals as final readiness checks. Record actual completion, open blockers and the owner of the next action in the team notes. No automated reminders or calendar invitations are created by this schedule.

## Final joint sign-off

- [ ] The problem statement and intended use are clear.
- [ ] Approved reviewed labels, tables, figures and results are accessible on GitHub.
- [ ] The README distinguishes completed results from plans.
- [ ] No draft mapping is presented as ground truth.
- [ ] Country comparisons have support, denominators and appropriate limits.
- [ ] Exploratory findings and final model evaluation are distinguished.
- [ ] A teammate reproduces the project from a fresh checkout.
- [ ] The 3 December session time, final duration and official submission cutoff are confirmed; slides, script and any demo fallback are rehearsed by 2 December.
- [ ] Names are Yizhou, Yuwei and Liwen; the team voice uses “we.”
- [ ] Everyone can explain label review, geography versus culture, imbalance, evaluation and limitations.

If time is tight, drop the optional interface first. Protect reviewed labels, defensible country findings, honest model evaluation and a clear final presentation.
