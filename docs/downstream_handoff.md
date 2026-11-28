# Downstream handoff after Yizhou preparation

Prepared 27 November 2026. Presentation: 3 December 2026. Start with [Yizhou's step-by-step report](yizhou_work_report.md). No human-reviewed targets or classifier scores exist yet; the machine suggestion files are not ground truth.

## Immediate shared dependency

Complete the pilot, agree the rubric, review the remaining batches, preserve independent decisions and adjudicate. The complete package is [data/label_review/v1](../data/label_review/v1/). Reviewers should not inspect machine suggestions before independent first decisions. Save completed copies under a new, clearly versioned path. The blank templates and machine-only files must not be described as reviewed data.

| Member | Files to review | Additional adjudication |
|---|---|---|
| Yizhou | pilot_yizhou.csv, a_yizhou.csv, c_yizhou.csv | Batch B disagreements; consolidate full adjudicated output |
| Liwen | pilot_liwen.csv, a_liwen.csv, b_liwen.csv | Batch C disagreements |
| Yuwei | b_yuwei.csv, c_yuwei.csv | Pilot and Batch A disagreements |

Use `assignment_manifest.csv` to find the correct two reviewers and adjudicator for each ID. The country/platform coverage file is coordination metadata, not a labeling cue. Do not fill in a teammate's signature or independent decision.

## Yuwei

1. Begin label-independent time/platform/interaction checks now using existing country tables. Record new questions in `reports/final/exploration_log.md`.
2. After adjudication, use the approved `data/reviewed/adjudicated.csv` joined one-to-one on `source_record`, not machine suggestions or original-label shares, for broad country sentiment plots.
3. Include excluded posts in a coverage audit. If a plot uses only classifiable posts, state that denominator and show exclusion rates by country.
4. Use the existing UK/Scotland mapping consistently and retain counts for small countries. Compare supported country/platform/time cells; country is not a cultural measurement.
5. Send Liwen two or three claim–evidence–limitation records, source tables and figures. Suggested new file: `notebooks/04_country_comparisons.ipynb`.
6. Independently reproduce the final repository on December 1; log your actual run and findings rather than reusing the assistant's reproduction receipt as your own.

## Liwen

1. Complete your independent label worksheets and adjudicate Batch C.
2. Check Yuwei's geography mapping, source joins, denominators and exclusion audit. Investigate platform/time mix and hashtag/template explanations.
3. After Yizhou runs development, inspect `development_errors.csv`, `development_class_metrics.csv` and `hashtag_sensitivity.csv`. These contain development results only. Review negation, mixed text and annotation ambiguity before proposing limited refinements.
4. Verify the final test numbers ONLY after the approved one-time test run; do not use test errors to tune the same model.
5. Build essential figures and a clear presentation narrative from verified outputs. Label machine suggestions explicitly if used to explain the review process; do not plot them as country sentiment findings or quote them as evaluated accuracy.
6. Confirm session duration, prepare the deck/script by November 30, rehearse on December 1–2, and keep an offline fallback. An optional UI comes last.

## Yizhou and joint approval

Validate the completed labels with `scripts/validate_label_review.py`, run development with `scripts/evaluate_sentiment.py`, publish its evidence, and record the configuration decision before `--finalize`. Preserve all versions and the original output directory. All three should approve labels, exclusions, class support and the model-selection decision. If this cannot be done by the evidence cutoff, report that classifier evaluation remains infeasible/pending and present only verified descriptive findings.

## Acceptance checklist

- [ ] Independent review and adjudication are actually complete for all 710 records.
- [ ] Final labels have reviewer provenance and all exclusions are explained.
- [ ] Yuwei's country figures use approved labels and clear denominators.
- [ ] Liwen has checked country calculations and development metrics.
- [ ] The model decision is frozen before the reserved test is opened once.
- [ ] Final metrics, if produced, are traceable to versions and split manifests.
- [ ] A teammate reproduces from a clean checkout and records their actual run.
- [ ] Deck/script use only verified results; no machine suggestions are called reviewed truth.
- [ ] Presentation logistics and official submission cutoff are confirmed.
