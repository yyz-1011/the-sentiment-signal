# EDA Findings

- The dataset contains **710 posts** and **191 distinct sentiment labels**. The most frequent label is **Positive** (45 posts, 6.3%). The distribution has a long tail; the 12-label chart groups the remaining labels as Other.
- Interaction distributions overlap across sentiment labels. Among labels with at least 8 posts, the highest medians are Contentment (75), Excitement (75), Happy (67); the lowest are Confusion (43), Loneliness (49), Acceptance (49). These are descriptive comparisons, not evidence of statistical significance or causation.
- Records span 2010-05-15 to 2023-10-22. Annual coverage is uneven; 287 posts (40.4%) are dated 2023. The annual trend should be read as the sample’s recorded coverage, not a population-level change over time.
- Source note: the publisher describes this dataset as synthetic, ChatGPT-generated content. The source timezone is unspecified; no timezone conversion was applied.

## Files
- `01_sentiment_distribution.svg`: counts and shares for the 12 most frequent labels plus Other.
- `02_sentiment_interactions.svg`: observed interaction boxplots for the 12 most frequent sentiment labels with at least 8 posts.
- `03_sentiment_over_time.svg`: annual counts for the five most frequent labels and total posts per year.
- CSV files contain the underlying frequency, interaction and temporal summaries.

## Reproduce
From the `Feature Exploration` directory, run `python eda/eda.py`. The script reads `data/sentiment_cleaned.csv` and refreshes the SVG charts and CSV summaries.
