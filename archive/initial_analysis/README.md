# Bootcamp sentiment analysis outputs

Open **initial_analysis_report.html** for the self-contained report with eight charts.
Use **sentiment_cleaned.csv** as the prepared data. Original input remains in the parent folder.
Complete **sentiment_label_review_template.csv** only after agreeing on a target taxonomy.
The script preserves an existing review template on rerun. It does not consume its proposed labels.

## Reproduce

```bash
python -m pip install -r requirements.txt
python preprocess_and_analyze.py
```

Optional arguments: `--input /path/to/source.csv --output-dir /path/to/results`.
The script is offline. The saved Kaggle metadata supplies provenance and field context.
CSV columns are documented in tables/data_dictionary.csv. Hashtag arrays are JSON strings.
Do not use source record numbers or export indices as model features.
All results describe synthetic examples, not measured social media behavior.
