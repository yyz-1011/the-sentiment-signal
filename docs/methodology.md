# Methodology

## Shared cleaning

Normalize Unicode and repeated whitespace, retain a source row identifier, exclude export-index columns when detecting full repeated observations, and keep the first copy. Parse timestamps, reconcile calendar columns, validate numeric counts, and preserve original text punctuation and negation. Derive lowercase text, text group hashes, lengths, calendar fields, normalized hashtag arrays and total interactions. This yields 710 rows and 26 fields; no missing cleaned values are present.

## Feature exploration

Yizhou used Pandas selection, filtering, sorting, grouping, crosstabs, date extraction and JSON hashtag expansion. NumPy supplies quantiles, moments, condition-based hour periods, weekend flags and log-transformed interactions. Six exploratory fields expand the data to 32 columns without removing observations. Some flags are constant in this sample and are diagnostics, not useful predictors. See the feature dictionary and Word report for definitions. Engagement and metadata are EDA variables; they are not automatically approved text-classifier features.

## EDA

Yuwei examined label frequencies, interaction boxplots and annual coverage. Liwen compared platform means, sentiment composition within a selected-label subset, and frequent hashtags. Original six PNG figures are retained. Current notebook copies use repository-relative data paths and write regenerated material to generated/. Quantitative claims are traceable to the supplied tables or independently verified summaries.

## Evaluation plan

Models have not been trained. Review a reduced target taxonomy and annotation rules before selecting an evaluation design. Keep identical text groups together, fit text processing only on training data, compare a majority baseline to simple text models, and report macro-F1 plus class support. Hypothesis tests are planned for later weeks and require clear hypotheses and assumptions.
