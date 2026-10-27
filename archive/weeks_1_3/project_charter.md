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
