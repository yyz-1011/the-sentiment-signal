# Mid-program presentation outline

The Sentiment Signal. Kevin (yy6074), Kelly (lx2455), Yuwei (yz13019).
Suggested duration: 8–10 minutes, plus questions. Speaking assignments below are proposals.

## 1. Project and team (45 seconds, Kevin)

Introduce the team. Explain the goal: build a reproducible sentiment-analysis workflow using a synthetic social media corpus. State immediately that the publisher generated the content with ChatGPT. The intended output is a demonstration classifier and an EDA narrative. No real public-opinion claims.

## 2. Dataset and provenance (60 seconds, Kevin)

732 records, 15 columns; unit is a simulated post. Introduce text, supplied emotion labels, timestamps, platform, hashtags, likes/retweets and location. Use the raw inventory and data dictionary. Name the Kaggle source and synthetic disclosure. Note unknown timezone and annotation protocol.

## 3. Cleaning and audit (60 seconds, Kevin)

Whitespace inflates labels and platform values. Normalize strings, exclude export indices from record matching, remove 22 repeated records, retain 710 posts. Keep removed-row provenance. All date and engagement checks pass. Explain why identical text with differing metadata remains but gets a split-group flag. Show the normalization log and quality audit.

## 4. Sentiment support (60 seconds, Kelly)

Show charts 01 and 09. The cleaned sample has 191 original labels; 81 have only one post. Positive, Joy and Excitement are the largest individual labels. Positive is one label, not the count of all positive emotions. Sparse support and overlapping meanings motivate a reviewed polarity target.

## 5. Coverage and composition (75 seconds, Kelly)

Show chart 10 plus 03/04 if time permits. Coverage is uneven across years and locations. The latest year ends in October. Platform counts: Instagram 251, Twitter 236, Facebook 223. Compare sample composition; avoid presenting counts as platform adoption or changes in real public mood. Country labels mix Scotland and UK.

## 6. Engagement and text features (75 seconds, Kelly)

Show charts 06, 11 and 12 selectively. Likes and retweets correlate at 0.9985. Every post has two hashtags. Text is short. Hashtags often directly cue a supplied label. Explain the implication: engagement fields are redundant and separate hashtags need sensitivity checks. These are feature observations, not significant or causal effects.

## 7. Problem statement and selected features (75 seconds, Yuwei)

Classify previously unseen simulated post text into reviewed Positive/Negative/Neutral polarity. Show the selected feature list: text is the baseline predictor; text_group_id controls splitting; supplied labels are targets; IDs, metadata and engagement are excluded from baseline predictors. Explain that the provided polarity mapping is unreviewed and contains an explicit review queue.

## 8. Progress, next steps and feedback (60 seconds, Yuwei)

Weeks 1–3 technical work is documented and executable. The next team action is target review, followed by instructor feedback. Week 5 compares simple text classifiers; Weeks 6–7 handle hypothesis tests. Ask whether the polarity target fits the assignment, whether a real-world corpus should support external evaluation, and how the instructor wants ambiguous examples and sparse Neutral handled.

## Backup material and questions

- Why remove only 22 rows? Equality uses all substantive fields after normalization, not just text. Four repeated-text groups remain because other metadata differs.
- Why no model scores? The current milestone ends at EDA and target design; training begins in Week 5.
- Why not use 191 labels? Eighty-one singleton categories cannot appear in both training and held-out evaluation.
- Are Instagram posts more engaging? The recorded mean differs descriptively; generated data, differing composition and unverified metric comparability prevent a real-world platform conclusion.
- Is label/hashtag overlap leakage? It is a cue-risk diagnostic. Leakage depends on the prediction setting, feature availability and how labels were created. Group separation and cue-removal comparisons are proposed checks.
- What happens to Mixed/Unclear? Preserve for EDA, adjudicate against text, and explicitly document any final model exclusion.
- Can we claim seasonality? Uneven synthetic coverage and a partial final year prevent a sound real-world seasonal claim.

## Rehearsal checklist

Each presenter should explain the source disclosure, duplicate rule and chosen target. Reproduce at least one summary from the notebook. Use only charts that support the spoken point. Keep draft target counts clearly marked as provisional. Reserve 2–3 minutes for instructor feedback and record decisions afterward.
