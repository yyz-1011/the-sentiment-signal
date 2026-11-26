# Yuwei: completed label-independent country handoff

**Prepared 27 November 2026 against base commit `30b74f7`.** Calculations are complete;
Liwen's independent review and the team's final claim approval are pending. No reviewed
sentiment labels, human annotation decisions, classifier results or final deck are claimed.

## Completed work

- Reconciled the 710-post input and the existing country counts, country/platform/year
  support, full-platform means, selected-label platform denominators and hashtag summaries.
- Built five date views using the same restriction in each country: all observed dates,
  before 2023, observed 2023, 2020–2022, and January–April 2023.
- Published country/window means, medians, IQRs and observed ranges, plus all 480
  country/platform/window support cells. All 32 geography groups remain represented.
- Checked the 75 main-country/platform/window cells. The `n < 10` flag discloses sparse
  support; it is not an inference threshold. Zero cells remain visible.
- Reproduced common-platform weighting and added separate pre-2023/2023 weighting.
  One pooled reference is fixed for all countries; no absent stratum is imputed or
  removed with weights renormalized. This is not a joint time/platform adjustment.
- Checked one-record-per-exact-text sensitivity while retaining all 710 posts in the
  authoritative primary analysis.
- Added an executable notebook, five PNG/SVG figures, underlying CSV tables, a standalone
  HTML report, three evidence/alternative/sensitivity/conclusion records, and speaker notes.

## Start here

- [Notebook](../notebooks/04_country_comparisons.ipynb)
- [Readable report](../reports/final/country/label_independent/report.html)
- [Report source and findings](../reports/final/country/label_independent/findings.md)
- [Figure/speaker handoff](../reports/final/country/label_independent/presentation_notes.md)
- [Exploration log](../reports/final/exploration_log.md)
- [Calculation checks](../reports/final/country/label_independent/calculation_validation.json)
- [Full reproduction check](../reports/final/country/label_independent/reproduction_validation.json)

## Three findings for review

1. **Support is concentrated and observed dates differ.** The main five groups contain
   594/710 posts (83.7%). Even within 2023, India stops in May and Australia in June,
   whereas USA/UK/Canada extend into October. A common year is not common calendar coverage.
2. **Distribution summaries can tell different stories.** USA has the largest mean
   (66.80), while Canada has the largest median (63; USA/UK 60). IQRs overlap. Recorded
   likes plus retweets are counts, not exposure-normalized engagement rates.
3. **Retain both stable and unstable results.** USA has the largest mean in the three
   full-period platform subsets and all five specified date views. But UK/Canada mean
   ordering reverses when 2023 is excluded. Common-platform weighting changes means by
   at most 0.167 interactions per post, a useful null sensitivity result.

These describe the supplied synthetic sample. They do not establish cultural, causal or
population differences. A low-count flag or persistence across overlapping subsets does
not establish statistical significance.

## Existing Liwen outputs: arithmetic review completed

The selected-ten-label platform chart has denominators Facebook **84**, Instagram **79**
and Twitter **72**, totaling **235**; the full platform totals are 223, 251 and 236.
The selected chart is not the complete platform sentiment distribution. Its values and
the 975 hashtag post-count/mean summaries reconcile to the source. Every retained post
has two hashtags, so hashtag presence/absence has no variation. Rare-tag means are
descriptive; wording such as "drives" or "significantly higher" is not supported here.
The future with/without-hashtag classifier comparison remains pending.

## Reproduce

Use the repository's Python 3.12 requirements from the repository root:

```text
python -m pip install -r requirements.txt
python scripts/country_comparisons.py
python scripts/check_country_comparisons.py
python scripts/reproduce.py
```

The ordinary commands write to `generated/`. The tracked report is a review copy under
`reports/final/country/label_independent/`. The notebook regenerates its report and runs
the calculation checker. The existing reproduction runner also discovers the new fourth
notebook, alongside the original three; source data is never rewritten.

On Windows, create a virtual environment with `py -3.12 -m venv .venv` and run commands
using `.venv\Scripts\python.exe`. On macOS/Linux use `.venv/bin/python` after creating
the environment. `.gitattributes` disables automatic CSV line-ending conversion so the
canonical data byte hashes remain valid on fresh Windows checkouts. No data file content
is changed by this handoff.

## Remaining dependencies and review questions

- Yizhou: provide the versioned independent reviews and adjudicated file, covering all
  710 `source_record` IDs with `reviewed_sentiment` and `decision_note`. We have not filled
  these from the publisher's original labels.
- Yuwei: independently review batches B/C and adjudicate pilot/A disagreements once
  the relevant worksheets and initial decisions are available. Those human tasks have
  not been performed by this analysis package.
- After labels arrive: add country positive/negative/neutral shares, exclusions and
  clear denominators; repeat supported platform/time comparisons using that label version.
- Liwen: verify mapping, denominators, the three findings and figure captions. The
  within-platform bars show IQRs, not confidence intervals. Check sparse cells before
  using any finer comparison in the presentation.
- Team: approve final wording and choose essential figures after the final duration
  is confirmed. The deck and text-classifier test evaluation remain with their assigned owners.

The repository's planned milestones use New York dates. The label-independent work here
is complete locally; a working analysis and a teammate's sign-off are distinct statuses.
