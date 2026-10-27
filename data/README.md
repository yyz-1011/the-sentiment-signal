# Data provenance

Source: [Social Media Sentiments Analysis Dataset](https://www.kaggle.com/datasets/kashishparmar02/social-media-sentiments-analysis-dataset/data), published by Kashish Parmar. The publisher metadata cached on 20 October 2026 is in [provenance/kaggle_metadata.json](provenance/kaggle_metadata.json). It describes synthetic, ChatGPT-generated content and lists CC0-1.0 for the dataset. The repository preserves this source attribution and license metadata. This source notice does not assign a license to team-authored code, text, or slides.

| File | Unit and shape | Purpose |
|---|---|---|
| `raw/sentimentdataset.csv` | 732 supplied records, 15 columns | Original input, unchanged |
| `processed/sentiment_cleaned.csv` | 710 retained posts, 26 columns | Shared input for current EDA |
| `processed/posts_feature_exploration.csv` | 710 posts, 32 columns | Same observations plus six exploratory fields |
| `input_data_dictionary.csv` | One row per cleaned field | Definitions and data roles |

The cleaned CSV SHA-256 is `4c38dc7cc2a8a06a96c13e989541c024ce31e9ee6af890a5f429fbe1f892ec6a`. Hashtag arrays are stored as JSON strings in CSV. Timestamps are timezone-naive because the source timezone is unspecified. The original labels are preserved and unreviewed broad mappings in the archive are proposals only. User identifiers and geographic fields come from the supplied synthetic dataset, not independently verified people or locations.

The reproduction runner checks row reconciliation, duplicate removal and equality with the committed cleaned snapshot. File hashes are also listed in the repository checksum manifest.
