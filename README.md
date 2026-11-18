# The Sentiment Signal

**Final project: cross-country sentiment exploration and text classification**

How do sentiment and recorded interactions differ across country groups in our synthetic social media sample? How much do those comparisons depend on platform mix, time coverage, and label quality? We also plan to evaluate whether post text can predict reviewed sentiment categories better than a majority-class baseline.

Start with the [country findings](reports/final/country/findings.md), the [final project plan](docs/final_project_plan.md), and the [label review and model evaluation guide](docs/label_review.md). [Data provenance](data/README.md) explains how 732 source records became 710 cleaned posts. The country tables are ready to review; model scores and final presentation materials are pending.

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
