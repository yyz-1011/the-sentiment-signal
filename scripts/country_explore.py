"""Build descriptive country comparisons from the canonical snapshot."""
import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def build(source, out):
    d = pd.read_csv(source)
    d["country_analysis"] = d.country.str.strip().replace({"Scotland": "UK"})
    mapping = d[["country", "country_analysis"]].drop_duplicates().sort_values("country")
    totals = d.groupby("country_analysis").agg(
        posts=("source_record", "size"),
        labels=("sentiment", "nunique"),
        median_interactions=("total_interactions", "median"),
        q1_interactions=("total_interactions", lambda x: x.quantile(.25)),
        q3_interactions=("total_interactions", lambda x: x.quantile(.75)),
        posts_2023=("year", lambda x: x.eq(2023).sum()),
    ).sort_values("posts", ascending=False)
    totals["sample_share_pct"] = 100 * totals.posts / len(d)
    totals["within_country_2023_pct"] = 100 * totals.posts_2023 / totals.posts
    totals["main_display"] = totals.posts.ge(30)
    platform = pd.crosstab(d.country_analysis, d.platform)
    year = pd.crosstab(d.country_analysis, d.year)
    counts = pd.crosstab(d.country_analysis, d.sentiment)
    shares = counts.div(counts.sum(axis=1), axis=0).mul(100)
    main = totals.index[totals.main_display]
    sub = d[d.country_analysis.isin(main)]
    # The weights are the pooled platform frequencies for the main display countries.
    w = sub.platform.value_counts(normalize=True).sort_index()
    cells = sub.groupby(["country_analysis", "platform"]).total_interactions.agg(
        posts="size", mean_interactions="mean", median_interactions="median")
    means = cells.mean_interactions.unstack().reindex(columns=w.index)
    standardized = means.mul(w).sum(axis=1, min_count=len(w))
    contrast = pd.DataFrame({"observed_mean": sub.groupby("country_analysis").total_interactions.mean(),
                             "common_platform_mix_mean": standardized})
    contrast["adjusted_minus_observed"] = contrast.common_platform_mix_mean - contrast.observed_mean
    assert totals.posts.sum() == len(d)
    assert counts.sum(axis=1).equals(platform.sum(axis=1))
    assert shares.sum(axis=1).round(8).eq(100).all()
    assert year.sum().sum() == len(d)
    out.mkdir(parents=True, exist_ok=True)
    for name, frame in {"country_mapping": mapping, "country_summary": totals,
                        "country_platform_counts": platform, "country_year_counts": year,
                        "country_supplied_label_counts": counts, "country_supplied_label_pct": shares,
                        "country_platform_interactions": cells, "common_platform_weights": w.rename("weight"),
                        "country_interactions_sensitivity": contrast}.items():
        frame.to_csv(out / f"{name}.csv", index=name != "country_mapping", float_format="%.6f")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, default=ROOT/"generated/final/country")
    options = p.parse_args()
    build(ROOT/"data/processed/sentiment_cleaned.csv", options.out)
