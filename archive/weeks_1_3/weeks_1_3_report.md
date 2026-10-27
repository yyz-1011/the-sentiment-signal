# The Sentiment Signal: Weeks 1–3 handoff

## Cleaning

732 raw records become 710 after removing 22 full-record duplicates. Zero missing cells and no invalid dates or engagement counts were found.

## Label support

279 raw label values normalize to 191. Eighty-one labels occur once, and 150 labels have fewer than five posts.

## Composition

Instagram has 251 retained posts, Twitter 236 and Facebook 223. The top five location labels account for 83.5% of posts. These counts describe synthetic sample composition.

## Calendar coverage

The sample spans May 2010 to October 2023. The uneven annual coverage and partial final year limit trend and seasonality interpretations.

## Engagement

Pearson correlation between likes and retweets is 0.9985. For 412 of 710 posts, likes equal twice retweets. Recorded counts do not provide an engagement rate.

## Text and hashtags

Every retained post has two extracted hashtags. 498 posts (70.1%) contain an exact normalized match between a hashtag and the supplied emotion label. This is a cue-risk diagnostic, not proof of leakage.

## Split design

Four repeated-text groups cover eight retained rows. Keep these groups together in later training and evaluation. Paraphrases may still overlap semantically.

## Selected baseline

Use post text as the primary predictor. Keep IDs and label-derived values out of predictors. Review the polarity target before Week 5; no models or tests have run.

# The Sentiment Signal: project charter

## Team

| Member | NetID | Proposed lead responsibility | Proposed cross-review |
|---|---|---|---|
| Kevin | yy6074 | Source inventory, cleaning and reproducibility | Check Kelly’s EDA calculations |
| Kelly | lx2455 | Feature exploration, charts and EDA interpretation | Check Yuwei’s target rubric |
| Yuwei | yz13019 | Problem statement, target review and presentation narrative | Check Kevin’s cleaning audit |

The roster and team name are confirmed by the user. Role allocations are proposals for the team to confirm. Everyone should explain the whole workflow and share annotation work. A fourth member is not required.

## Project introduction

We study a synthetic collection of social media posts to practice sentiment analysis and explore how supplied labels, text features and recorded engagement vary across platforms, locations and time. We aim to build a transparent, reproducible educational workflow and then test a bounded sentiment classifier. Findings concern the simulated sample.

## Objectives and research questions

1. Establish dataset structure, provenance and quality. Which formatting issues or duplicate records affect analysis?
2. Describe the emotion-label distribution. Does label support permit reliable evaluation of the original classification task?
3. Explore platform and geographic composition, hashtags and calendar coverage. Which apparent patterns reflect the sample construction?
4. Inspect engagement distributions, feature redundancy and text length. Which fields should inform EDA or a future predictor?
5. Define a text-only polarity classification target with an explicit review process and a leakage-aware evaluation plan.

## Scope through Week 3

Data acquisition verification, cleaning, data dictionary, descriptive EDA, visualizations, target proposal and feature selection. Models begin in Week 5. Hypothesis tests begin in Weeks 6–7. No predictive performance, significant effects or causal relationships are claimed at the mid-program stage.

## Data and limitations

- One local source: `../sentimentdataset.csv`, 732 records and 15 columns. Unit: simulated post. Retained observations: 710.
- Publisher: Kashish Parmar, Kaggle, CC0-1.0. Local source version is identified by its SHA-256 in the audit; no version equivalence is assumed merely from filename.
- The publisher explicitly discloses ChatGPT-generated synthetic content. Original timestamps span 2010–2023, but there is no verified sampling design, timezone or independent annotation protocol.
- Retweets appear for Instagram and Facebook as well as Twitter. Their meanings across platforms are unverified. Likes plus retweets is a count proxy, not an engagement rate.
- Geography labels mix UK and Scotland. They remain as supplied after whitespace normalization. Real-world country rankings, seasonality claims and influencer conclusions are outside scope.

## Definition of success at the mid-program presentation

All source rows reconcile to retained or audited duplicates; notebook cells execute without errors; every chart states its denominator or unit; each headline claim has a supporting table; selected features have reasons; unreviewed labels and proposed responsibilities remain visibly unconfirmed.

## Sources

- [Dataset card](https://www.kaggle.com/datasets/kashishparmar02/social-media-sentiments-analysis-dataset/data).
- [Publisher metadata](https://www.kaggle.com/api/v1/datasets/metadata/kashishparmar02/social-media-sentiments-analysis-dataset), cached in `../initial_analysis/sources/kaggle_metadata.json` on 20 October 2026.


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


# Final week before the mid-program presentation

Use relative days because the actual presentation date was not supplied. No calendar dates or reminders have been assumed.

| When | Action | Proposed lead | Done when |
|---|---|---|---|
| T−7 to T−6 | Confirm roles and reproduce notebook outputs | Kevin | All cells run; roster and file locations verified |
| T−6 to T−5 | Independently review annotation sample and inspect ambiguous labels | Kelly and Yuwei | Both reviewer columns completed, disagreements listed |
| T−5 to T−4 | Adjudicate examples and agree target scope | Entire team | Rubric and inclusion policy documented; remaining uncertainty listed |
| T−4 to T−3 | Choose 5–6 charts and prepare the presentation using the outline | Kelly, with all members | Every claim has a table or chart and a limitation |
| T−2 | Rehearse the 8–10 minute narrative | Entire team | All members explain methods and stay within time |
| T−1 | Freeze the EDA handoff and back up files | Kevin | Notebook, report and presentation materials open on presentation laptop |
| T | Present and record feedback | Entire team; Yuwei records feedback | Instructor decisions captured, future plan updated |

Target review can continue after the mid-program milestone if the team clearly presents its provisional status. It must finish before training a model on the proposed polarity labels.

Feedback log fields: topic; instructor comment; agreed decision; owner; due milestone; status. No feedback has been invented or pre-filled.
