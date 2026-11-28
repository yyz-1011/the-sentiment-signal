# Yizhou work report and operational handoff

Prepared 27 November 2026 for the 3 December presentation, starting from commit `30b74f7`. This report records work performed by the assistant on Yizhou's assigned workstream. It does not attest that Yizhou or another person has independently reviewed labels or approved the final model.

## Status at handoff

The user confirmed on 27 November that independent label review had not started. There are no adjudicated human labels, project-trained classifier results, final test scores, or real classification-error examples in this handoff. These are dependencies, not completed milestones. The supported fallback in the task division remains a transparent feasibility result if review cannot be finished responsibly.

Completed here: fresh environment installation, reproduction of cleaning and the three existing notebooks, source reconciliation, deterministic regeneration of the nine country tables, preparation of all eight independent reviewer worksheets and the adjudication template, optional text-only machine suggestions, a target validator, richer development evaluation exports, engineering tests, and step-by-step instructions for the remaining team work.

## Step 1 obtain the same input and environment

Use a fresh checkout, Python 3.12, and a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/reproduce.py
python scripts/country_explore.py --out generated/country_verify
python -m unittest discover -s tests -v
```

The dependency installation was executed successfully in a newly created virtual environment. The exact installed versions are in `reports/final/yizhou/environment_freeze.txt`; the reproduction receipt is in `reports/final/yizhou/reproduction_validation.json`. Notebook outputs were regenerated into `generated/` without overwriting committed snapshots. The test output is recorded separately. An assistant clean run is not a teammate's independent cross-review.

Raw data: 732 records. Cleaned snapshot: 710 records and 26 fields. Source SHA-256: `4c38dc7cc2a8a06a96c13e989541c024ce31e9ee6af890a5f429fbe1f892ec6a`. The cleaning rerun reconciles to the committed snapshot, including 22 removed observations. Original data and existing analytical findings were retained.

## Step 2 allocate the complete review from scratch

The committed blank package is `data/label_review/v1/`. Its input checksum and seed are recorded. Recreate in a new directory, never on top of completed work:

```bash
python scripts/prepare_label_review.py --full-package --out generated/review_v2
```

The same pilot procedure used previously selects 54 records. The other 656 are interleaved across geographic/platform cells and rotated into batches A/B/C. Assignment is deterministic; it is not a random sampling claim about real populations.

| Batch | Posts | First reviewer | Second reviewer | Adjudicator |
|---|---:|---|---|---|
| Pilot | 54 | Yizhou | Liwen | Yuwei |
| A | 219 | Yizhou | Liwen | Yuwei |
| B | 219 | Liwen | Yuwei | Yizhou |
| C | 218 | Yuwei | Yizhou | Liwen |

Each record belongs to exactly one batch. The assignment manifest covers all 710 unique source IDs. Every worksheet contains only ID, post text, a blank decision and a blank note; original labels, country, platform and model suggestions are omitted. The coverage table is for coordination, not for guiding a blind sentiment decision. Initial decisions are all blank. This is the complete coordination package, not completed annotation.

## Step 3 independently review and adjudicate

Read `docs/label_review.md` first. Each reviewer writes positive, negative, neutral, or a temporarily unresolved decision in a working copy, explains ambiguous cases, and does not consult the second reviewer's answers. Agree the rubric after the pilot and revisit pilot decisions if the rubric changes. Neutral is a semantic judgment, not the default for an unfamiliar emotion. Mixed/unclear cases must be adjudicated or explicitly excluded; do not guess labels merely to support three classes.

Preserve both reviewer files. Record disagreements before adjudication; measure agreement only from completed independent decisions. The named adjudicator resolves each disagreement and logs the reason. Include an explicit decision and note for every record in a completed copy of `adjudication_template.csv`. Keep the original template blank.

Publish approved decisions as `data/reviewed/adjudicated.csv`, with `source_record,reviewed_sentiment,decision_note`. All 710 source IDs are required. Allowed final decisions are negative, neutral, positive and exclude. Keep exclusion reasons and reviewer/adjudication logs alongside the file; do not silently remove rows or declare team approval that did not happen. Excluded posts remain available for descriptive EDA.

The assembly helper can reduce transcription after review. Run it with a NEW output directory:

```bash
python scripts/assemble_adjudication.py --package data/label_review/v1 --out generated/adjudication_pass1
```

It records completed agreements and exports a pending queue. For disagreements, create a separate resolution CSV with `source_record,reviewed_sentiment,decision_note,adjudicator`; pass it with `--resolutions` into a new assembly output directory. It checks the assigned adjudicator and requires both reviewer decisions/notes. Only a fully resolved package produces `adjudicated_for_validation.csv`. With today's blank worksheets it reports 710 pending and exports no labels. Identity and actual independence remain human responsibilities. Copy a fully approved output to the tracked final path and retain its provenance.

Then run:

```bash
python scripts/validate_label_review.py --reviewed data/reviewed/adjudicated.csv
```

The validator checks full unique-ID coverage, allowed values, notes and consistent included labels for identical text. It exports reviewed class support and country coverage. Its success means structural validity, not proof that the reviewers were independent or correct. Group counts must still support the actual evaluation splits.

## Step 4 optional machine assistance

`data/machine_assistance/v1/` contains VADER suggestions for all 710 posts, generated directly from post text with explicit hashtags removed. The supplied sentiment column was not used. Recreate with:

```bash
python scripts/suggest_review_labels.py --out generated/machine_assistance
```

VADER uses lexicon/rule scores. The initial categories use compound >= 0.05 for positive, <= -0.05 for negative, and neutral otherwise. The optional triage queue flags low absolute scores (<0.15), mixed lexicon cues, or simple negation/contrast patterns. These heuristic flags and thresholds are not calibrated confidence measures. See the [upstream method](https://github.com/cjhutto/vaderSentiment#about-the-scoring).

The run suggested positive 447, negative 182 and neutral 81, with 242 flagged records. These counts are not reviewed polarity distributions, not accuracy measurements, and not evidence of human agreement. Use suggestions only after independent first decisions if preserving the planned blind-review design. If reviewers instead consult suggestions up front, explicitly describe the process as machine-assisted and do not claim independent blind annotation. The suggestion column is deliberately named `machine_suggestion`, so it cannot be passed unchanged as an adjudicated target.

## Step 5 validate the modeling design before scores

The primary input is post text without explicit hashtags. Country, platform, engagement, source IDs and publisher labels are excluded from predictors. TF-IDF is fitted only inside training folds. Candidates remain majority class, logistic regression and linear SVM; the primary selection metric is mean development macro-F1. Original-text results are a paired hashtag sensitivity comparison, not a reason to tune against the test data.

The runner reserves one deterministic five-fold group-stratified split and uses the other groups for development. Development folds are tried in order 4, 3, 2, based on support. Every train/evaluation partition must contain all three classes; identical normalized text groups must not overlap. About 20% rather than exactly 20% of rows may be held out. Inspect the saved group manifests and class counts. The supplied 191-label task has 81 singleton labels; this is why broad targets need review before evaluation.

If the support checks fail, document why and agree a revised scope before modifying code. Do not force labels, drop a class silently or search random seeds. The corpus was explored previously, so call the reserved partition held out from model fitting and tuning, not an entirely unseen research dataset.

## Step 6 run development and diagnose errors after review

```bash
python scripts/evaluate_sentiment.py --reviewed data/reviewed/adjudicated.csv
```

Default outputs go to `generated/final/model/`:

- `development_scores.csv`: macro-F1, accuracy, support and fold for each candidate/variant.
- `development_class_metrics.csv`: class precision, recall, F1 and support per fold.
- `development_predictions.csv`: out-of-fold predictions on development records only.
- `development_errors.csv`: incorrect development predictions with text and context for diagnosis.
- `development_summary.csv`: fold summary; fold spread is descriptive, not a population confidence interval.
- `hashtag_sensitivity.csv`: paired original-minus-without-hashtag macro-F1 differences.
- `development_fold_manifest.csv` and `split_manifest.csv`: record/group membership, including the reserved partition.
- `review_coverage.csv`, `development_selection.csv`, `evaluation_manifest.json`: inclusion audit, chosen candidate and exact input/code version.

Yizhou and Liwen should inspect errors by negation, mixed emotion, unclear annotation and templates, not treat every disagreement as a model fault. Any rubric change requires a new label version and reconsideration of the split/evaluation design. Scores and real error examples cannot be supplied now because independent labels do not exist.

## Step 7 freeze and evaluate the reserved test once

After all three members approve the configuration and labels, use the SAME output directory:

```bash
python scripts/evaluate_sentiment.py --reviewed data/reviewed/adjudicated.csv --finalize
```

Finalization requires a matching development manifest containing source, labels, pipeline code hashes, seed and scikit-learn version. Once `final_test_results.csv` exists, the runner rejects subsequent development or finalization in that directory. This is a local guard, not a protection against deliberately using a new directory; the team's version log must preserve the single-test policy.

The output contains baseline/selected-model per-class and macro metrics, confusion matrices and predictions. Verify them and publish approved artifacts under `reports/final/model/`. Do not publish invented engineering-test metrics as project results. Do not claim the three-person approval or final test was completed by this assistant.

## Step 8 handoff and release

Read `docs/downstream_handoff.md` for member-specific actions and paths. November 23 label completion was a planned deadline that has passed without review; it is not a completed milestone. Given the December 3 presentation, prioritize full review immediately. Keep the November 28 configuration decision and November 29 evidence cutoff if review is complete; otherwise use the documented modeling-feasibility fallback. Drop the UI before dropping review or rehearsal. Do not turn the date into a justification for lower label standards.

Before final release, a teammate independently installs and runs the project from a fresh checkout, checks reviewed-label provenance, verifies model/country charts against tables, and tests the repository links. Session time, duration and the official submission cutoff still need confirmation.
