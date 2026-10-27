# The Sentiment Signal: Weeks 1–3 handoff

Start with **weeks_1_3_report.html**. It is a self-contained report with the workflow checklist, project scope, findings, all 12 charts and a summary of decisions.

The original source CSV stays in the parent directory. This folder adds to the earlier `initial_analysis` folder without changing its files.

## Main files

- `weeks_1_3_analysis.ipynb`: executed notebook with source inspection, cleaning, NumPy/Pandas manipulation, EDA, visualizations, draft target and feature selection.
- `weeks_1_3_analysis.py`: equivalent code cells for a plain Python run. Requires IPython for rich displays, provided by the notebook dependencies.
- `project_charter.md`: confirmed roster, proposed roles, objectives and scope.
- `problem_and_features.md`: selected primary question, annotation rules and later evaluation plan.
- `workflow_checklist.csv`: completed work, pending decisions and future milestones.
- `mid_program_presentation_outline.md`: eight-part outline, suggested speaker notes and backup Q&A.
- `one_week_preparation_plan.md`: relative-day rehearsal plan.
- `data/posts_prepared.csv`: all 710 prepared EDA rows, with added features.
- `data/classification_corpus_draft.csv`: text, source IDs and draft targets; every row remains unreviewed.
- `data/polarity_mapping_proposed.csv`: proposed mappings for all 191 original labels. Save reviewed decisions separately.
- `data/annotation_review_sample_proposed.csv`: up to 20 examples per draft group for independent review. Save a separate reviewed copy.
- `tables/feature_selection.csv`: feature decisions and reasons.
- `tables/feature_dictionary_and_selection.csv`: definitions combined with feature decisions.

## Reproduce

Install `requirements.txt` in a virtual environment, open the notebook, select its Python kernel and run all cells from this folder. Alternatively run `python weeks_1_3_analysis.py`. All rows are read from the original CSV; no network access is required. Rerunning refreshes generated proposed files, so keep human annotations in separately named files. The EDA report is a saved handoff snapshot and must be updated if source data or claims change.

The full archive includes this folder, the earlier analysis and the original CSV in the expected relative layout.
