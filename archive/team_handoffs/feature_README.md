# Feature Exploration

This folder completes Week 2 feature exploration for The Sentiment Signal.
It does not add charts, perform hypothesis tests, fit models or finalize feature selection.

Start with Feature_Exploration_Report.docx and the executed Feature_Exploration.ipynb.
The source snapshot in data/sentiment_cleaned.csv contains 710 rows and 26 columns.
The exploration output in data/posts_feature_exploration.csv adds six fields, retaining all 710 rows.
Original labels and all input values are preserved. JSON hashtag arrays remain JSON strings in CSV.
The full 32-field dictionary is tables/exploration_data_dictionary.csv.

## Run again

Create a virtual environment, install requirements.txt, and run all notebook cells from this folder.
Alternatively run `python feature_exploration.py` from this folder. The source hash check stops execution
if the input changes. Review the source and update the documented hash deliberately when changing datasets.
Rerunning refreshes generated CSV tables, the feature dataset and validation_results.json.
The executed notebook was checked on 23 October 2026. The Word report is a fixed handoff snapshot.

## Manipulation examples

The filter example selects Instagram rows with at least 75 recorded interactions, then sorts them.
This query does not change the full dataset and does not define a validated popularity threshold.
Category percentages use all 710 posts. Hashtag shares count each token once per post and can total above 100%.
Group aggregates and crosstabs demonstrate Pandas manipulation and provide inputs for colleagues’ later EDA.
Timestamp coverage is sample coverage. The publisher discloses synthetic ChatGPT-generated content.
