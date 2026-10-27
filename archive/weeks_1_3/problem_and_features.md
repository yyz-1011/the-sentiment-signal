# Problem statement and feature specification

## Selected primary problem

Given the text of a previously unseen simulated social media post, predict a reviewed sentiment polarity label: Positive, Negative or Neutral. Use a reviewed mapping of the publisher’s original labels as a starting point, inspect the post text, and evaluate generalization to held-out text groups from the same synthetic corpus. Use macro-F1 as the primary selection metric and report per-class support and error patterns. The result is an educational classifier for this corpus; external usefulness would require a real independently annotated evaluation dataset.

## Why this target

The original 191-label target has 81 singleton labels and many overlapping synonyms or topic-like entries. A model with all labels cannot represent every singleton in both training and evaluation. Coarse polarity gives a manageable primary objective. Original emotion-label EDA remains useful, and a reviewed emotion-family task can be a stretch goal.

The taxonomy choice is a project recommendation. The mapping remains provisional until the team reviews it against the text. We have not created new ground truth or claimed that all emotions have an unambiguous polarity.

## Draft target coverage

| Proposed group | Posts |
|---|---:|
| Positive | 328 |
| Needs review | 201 |
| Negative | 163 |
| Neutral | 18 |

All 710 posts remain in the analytical dataset. The draft classifier corpus also retains all rows and explicitly marks review status. `Needs review` is a review queue, not a fourth training class. No records have been silently discarded for their sentiment label.

## Annotation rules

- Positive: the post’s dominant expressed evaluation is favorable, pleased, grateful, hopeful or approving.
- Negative: its dominant expressed evaluation is unfavorable, sad, angry, fearful or dissatisfied.
- Neutral: the text makes no clear positive or negative evaluation. Emotional intensity alone does not define polarity. Calm, numb or indifferent words do not automatically make a post Neutral.
- Mixed or unclear: record `Mixed/Unclear` during review, inspect context and adjudicate. If it cannot fit the three-class rubric, retain it in EDA and explicitly exclude it from the three-class model with its reason. Report resulting coverage and class balance.
- Preserve negation, emoji and sarcasm cues. Text meaning takes precedence over a broad label lookup. Do not assign Neutral to an unknown label.

Two reviewers independently label the sample worksheet without seeing each other’s decisions. Adjudicate disagreements. Then review every mapping and all associated ambiguous posts; sample review alone does not validate 191 mappings. Inspect the remaining mapped posts for label-text inconsistencies before freezing a target. Save finalized decisions under a new filename so reruns preserve them. Record reviewer names and dates, agreement before adjudication and final inclusion/exclusion reasons. Report agreement only after actual independent reviews.

## Selected features

Primary baseline input: `text`. Derived word/character counts remain EDA and possible later auxiliary features. Apply TF-IDF inside the training pipeline in Week 5.

Split metadata: `text_group_id` prevents identical normalized text crossing folds. `source_record` traces rows to input. Neither is a predictor.

Excluded from baseline predictors: original sentiment, draft polarity and target-derived diagnostics; export indices and user IDs; all recorded engagement counts; country/platform/date metadata; separate hashtag fields; constant hashtag count. Reasons for all 30 candidate columns appear in `tables/feature_selection.csv`.

Hashtag cue diagnostic: 498/710 posts (70.1%) contain a hashtag that exactly matches the normalized supplied label. This is label-cue overlap, not proof of data leakage. Synonyms and semantic cues are not measured. A later robustness comparison should remove hashtags and compare performance, provided remaining text and split definitions stay consistent.

## Later modeling plan, not executed

1. Freeze reviewed labels and target inclusion rules, then summarize retained coverage.
2. Set aside about 20% of text groups for a final test set, with a fixed seed (6074). Inspect class representation and group overlap. Group splitting need not yield exactly 80/20 rows or perfect stratification. If the smallest class cannot support evaluation, revise the design transparently rather than forcing a misleading score.
3. Use group-aware cross-validation within training only. Choose folds based on the smallest reviewed class. Fit vocabulary/IDF and any balancing within each training fold.
4. Compare a majority-class baseline, TF-IDF plus logistic regression, and TF-IDF plus linear SVM. Consider class weights in training. Avoid synthetic oversampling of text before splitting.
5. Select using macro-F1. Report balanced accuracy, class precision/recall/F1/support and confusion matrix. Use the frozen test set once after model selection.
6. Inspect errors and compare hashtag removal. Document synthetic-origin, sparse-neutral and near-duplicate limitations. Exact-text grouping alone cannot eliminate paraphrase overlap in generated examples.
