# Feature Exploration and EDA

This folder completes Week 2 feature exploration and adds three descriptive EDA views for The Sentiment Signal. The cleaned input is `data/sentiment_cleaned.csv` (710 rows, 26 columns); the source values are preserved.

Start with `Feature_Exploration_Report.docx` and the executed `Feature_Exploration.ipynb`. The notebook and `feature_exploration.py` generate the tabular feature-exploration outputs and the three EDA charts. The EDA graphics, underlying CSV summaries and written findings are in `eda/`.

## EDA views

- Sentiment label distribution: top 12 labels and a combined tail category.
- Sentiment and engagement: total-interaction boxplots for the 12 most frequent labels with at least 8 posts.
- Temporal trend: yearly counts for the five most frequent labels, alongside total posts per year.

These are descriptive views. Sentiment labels are retained as supplied; no polarity score, statistical test or model is added. The publisher describes the posts as synthetic, and timestamp coverage is uneven.

## Run again

Create a virtual environment and install `requirements.txt`. Run all notebook cells from this folder, or run `python feature_exploration.py`. To refresh only the EDA charts and tables, run `python eda/eda.py` from this folder. The source hash check stops the main workflow if its input changes. Review and update the documented hash deliberately when changing datasets.

Rerunning the main script refreshes the generated CSV tables, the feature dataset, validation results, EDA charts, EDA summary tables and findings. The Word report is a saved handoff snapshot.

## Interpretation notes

The sentiment data has 191 labels, many with small support. Interaction comparisons show the sample sizes and are not evidence of statistical significance or causation. The timestamps span 2010–2023, but annual counts are uneven; 2023 contains a large share of records. Timestamp timezone is unspecified. Treat temporal patterns as sample coverage rather than population trends.
