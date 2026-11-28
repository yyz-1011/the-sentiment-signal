# Blank independent-review package

Generated 27 November 2026. All decision and note cells are blank. No independent review or adjudication is claimed. See [the operational report](../../../docs/yizhou_work_report.md) for the procedure and [the downstream handoff](../../../docs/downstream_handoff.md) for each person's exact files.

Pilot: 54 posts reviewed by Yizhou and Liwen, adjudicated by Yuwei. Remaining A/B/C sizes: 219/219/218, with reviewer pairs and adjudicators in assignment_manifest.csv. All 710 source IDs occur once in that manifest. Each assigned record appears in two blinded reviewer files; the separate adjudication_template.csv retains one blank final decision per record. It is not valid model input until completed and approved.

Save working and final copies under new paths and preserve originals. Do not read the machine suggestion files before the independent first pass. Country/platform coverage is supplied for coordination, not for deciding sentiment. Use the optional machine aid only with honest disclosure of when it was seen.

Recreate identical blank files in a NEW empty directory with `python scripts/prepare_label_review.py --full-package --out generated/new_review_version`. Existing nonempty output directories are rejected to protect completed work.
