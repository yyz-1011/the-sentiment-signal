# Reproduction details

The supported entry point is `python scripts/reproduce.py` from the repository root after installing requirements.txt in Python 3.12. The version pins record the environment used to verify this handoff. A different Python or library version has not been tested. For interactive editing, install JupyterLab separately with `python -m pip install jupyterlab` and run `jupyter lab`; open the notebooks in order. The automated runner does not require JupyterLab.

The runner uses the current Python executable as the notebook kernel. It writes new outputs to generated/ and executed notebook copies to generated/executed_notebooks/. Pass `--refresh-notebooks` to replace the main notebooks’ saved output cells with the successful fresh run. This flag is used when preparing this package; ordinary reproduction leaves committed snapshots alone.

The runner checks the source SHA-256, raw and cleaned shapes, shared source hash, cleaning output equality, duplicate reconciliation, notebook execution, original label counts, annual counts and tabulated interaction medians. It recomputes current source tables but does not regenerate fixed Word reports or PowerPoint styling. Those are saved handoff artifacts.

The six original figures are author-supplied PNGs. Regenerated charts may differ in fonts, layout or tie order while preserving the explicit numerical selection in the repository edition. See docs/adaptations.md for the fixed ten-label subset and observed-range boxplot convention.

Historical scripts under archive/ are preserved for review and are not the supported reproduction entry points. They may assume their original directory structure. Raw and processed data are never rewritten by the standard runner. Expected data checksums are in provenance/file_checksums.csv. generated/ is excluded from version control; a summarized validated run is retained in provenance/validation_report.json.

## Yizhou preparation verification

A fresh virtual environment installed the declared requirements and ran the three original notebooks, cleaning reconciliation and country-table regeneration on 27 November. The receipt and installed versions are in `reports/final/yizhou/`. Run `python -m unittest discover -s tests -v` for the review and evaluation guards. Model tests use invented engineering fixtures; their metrics are not project performance. The workflow remains runnable after labels arrive, but actual development/error/final-test reports are pending independent adjudication. See `docs/yizhou_work_report.md`.
