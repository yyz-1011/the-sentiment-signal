# The Sentiment Signal

**Final project: cross-country sentiment exploration and text classification**

**Planned Final Presentation: Thursday, December 3, 2026.** Review the [dated team schedule](docs/task_division.md#dated-schedule-through-3-december): labels by November 23, configuration freeze November 28, final evidence November 29, deck/script November 30, and verification/rehearsals December 1–2. Session time, duration and the official submission cutoff remain to be confirmed.

How do sentiment and recorded interactions differ across country groups in our synthetic social media sample? How much do those comparisons depend on platform mix, time coverage, and label quality? We also plan to evaluate whether post text can predict reviewed sentiment categories better than a majority-class baseline.

Start with the [country findings](reports/final/country/findings.md), the [final project plan](docs/final_project_plan.md), the [task division and team handoffs](docs/task_division.md), and the [label review and model evaluation guide](docs/label_review.md). [Data provenance](data/README.md) explains how 732 source records became 710 cleaned posts. The country tables and full review worksheets are ready; independent adjudication, model scores and final presentation materials are pending.

## Yizhou preparation handoff — 27 November

Start with the [step-by-step work report](docs/yizhou_work_report.md) and [member-specific downstream actions](docs/downstream_handoff.md). A fresh-environment reproduction passed, the complete [blank review package](data/label_review/v1/) covers all 710 posts, and the evaluation workflow has engineering tests and richer development exports. The optional [machine suggestions](data/machine_assistance/v1/) are a review aid, **not human-reviewed labels or ground truth**.

Independent review is still outstanding. No supervised project scores, final model, or reserved-test results are claimed. The November 23 label target was missed; complete review before the planned November 28 configuration decision, or use the documented feasibility fallback. Keep the December 1–2 verification and rehearsal buffer.

## Evidence so far

- The five largest groups account for about 84% of posts after recording Scotland under UK for analysis. The source labels remain unchanged.
- Overall, 287 of 710 posts are dated 2023. Check time coverage before interpreting a geographic comparison.
- There are 191 supplied sentiment labels, 81 of them singletons. The country tables expose the original labels, while comparable broad categories require review.
- The [earlier EDA](reports/eda/findings.md) covers sentiment, platforms, hashtags and recorded interactions. Its results are descriptive.

The publisher describes this data as synthetic. Country labels do not directly measure culture, and likes plus retweets are recorded counts rather than exposure-normalized rates.

## Run locally

Use Python 3.12. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/reproduce.py
python scripts/country_explore.py
python scripts/prepare_label_review.py
python -m unittest discover -s tests -v
```

The first runner checks cleaning and reruns the existing notebooks. The country and review scripts write to `generated/`. After independent label review and adjudication, follow the [evaluation guide](docs/label_review.md). [Reproduction details](docs/reproducibility.md) cover the historical notebook outputs and dependencies.

| Location | What to find |
|---|---|
| [reports/final](reports/final/) | Country analysis and the final presentation outline |
| [notebooks](notebooks/) | Feature exploration, sentiment and time, platforms and hashtags |
| [data](data/) | Raw and cleaned snapshots and dictionary |
| [scripts](scripts/) | Reproduction, country analysis, blinded review worksheets and grouped evaluation |
| [archive](archive/) | Historical handoffs, including unreviewed draft mappings |
| [provenance](provenance/) | Historical source and validation records |

**Team:** Yizhou Yan (cleaning and feature exploration), Yuwei Zhang (sentiment, interactions and time), and Liwen Xu (platforms and hashtags).

**Source:** [Kashish Parmar’s Kaggle dataset](https://www.kaggle.com/datasets/kashishparmar02/social-media-sentiments-analysis-dataset/data). The cached publisher metadata lists CC0-1.0 for the dataset. See [reuse notes](LICENSE_NOTES.md) for scope.
