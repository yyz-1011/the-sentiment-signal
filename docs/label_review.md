# Sentiment label review

Use **positive**, **negative**, or **neutral** for the dominant evaluation conveyed by the post. Neutral requires no clear positive or negative evaluation. When a post is genuinely mixed, ambiguous, context-dependent, unintelligible, or out of scope, record why; adjudicate it or assign **exclude**. Never default an unknown emotion label to neutral. Country, hashtags that merely name the label, and the publisher's label are not independent evidence of sentiment. Note when a hashtag materially changes the text interpretation.

Run `python scripts/prepare_label_review.py`. Give the two worksheets to different reviewers. Compare their independent decisions before adjudication, record agreement and disputed examples, revisit the rubric, and then review the remaining posts. Store reviewers' initial decisions separately from the adjudicated labels. Rotate assignments so that country patterns are not driven by reviewer assignment. Reviewers should read each post without looking up the original label where feasible.

The final input must include exactly one row per cleaned `source_record`, with columns `source_record,reviewed_sentiment,decision_note`. Allowed labels are `negative`, `neutral`, `positive`, and `exclude`. Give every row a reason; do not drop excluded rows. Identical text groups included in modeling need consistent labels. Versions and inclusion rules should be agreed before modeling. The archive's proposed mappings are reference material, not reviewed targets.

Run development evaluation only after the review:

```bash
python scripts/evaluate_sentiment.py --reviewed generated/label_review/adjudicated.csv
```

The runner reserves one group-stratified fold, verifies all classes are represented, and compares majority, logistic regression and linear SVM on common development folds. It reports macro-F1 and uses text without explicit hashtags as the primary model input; the original-text runs are a sensitivity check. Country, engagement and IDs are not predictors. The 20% test share is approximate. If support fails, report the gap and agree on a revised scope or resampling plan before proceeding. Do not try seeds until a preferred score appears.

Once labels, splits and the model configuration are frozen, add `--finalize` to evaluate the selected text model and majority baseline once in the same output directory. Record label version, class support, per-class metrics and errors. No real-world or cross-country generalization is established by results from this synthetic corpus.
