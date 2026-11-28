# Optional machine-only suggestions

These are VADER lexicon/rule suggestions generated from post text with explicit hashtags removed. No supplied sentiment label was used. They are NOT independent human decisions, adjudicated targets, calibrated confidence, or test performance. Do not rename this file into the reviewed-label input and report its results as supervised validation.

The triage queue contains heuristic flags for close inspection. Unflagged records still require review. Suggested category counts are 447 positive, 182 negative, 81 neutral; 242 posts are flagged. Use the machine aid only after independent decisions if following the planned blind-review workflow. Inspecting suggestions up front changes the procedure to machine-assisted review and must be disclosed.

Recreate: `python scripts/suggest_review_labels.py --out generated/machine_assistance`. See [upstream VADER](https://github.com/cjhutto/vaderSentiment#about-the-scoring) and [the operational report](../../../docs/yizhou_work_report.md) for thresholds and limitations. VADER is an external lexicon/rule tool; no social-media culture claim or validation against team labels is implied.
