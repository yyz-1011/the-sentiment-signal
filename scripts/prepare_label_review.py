"""Create two identical blinded worksheets; adjudicate and export separately."""
import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT/"generated/label_review")
    opts = parser.parse_args()
    data = pd.read_csv(ROOT/"data/processed/sentiment_cleaned.csv")
    # Only the record key and text are shown to reviewers. Sample one wave
    # across country/platform cells; review the rest using the same rubric.
    country = data.country.replace({"Scotland": "UK"})
    major = country.value_counts().loc[lambda x: x.ge(30)].index
    groups = data.assign(_country=country.where(country.isin(major), "Other"))
    shuffled = groups.sample(frac=1, random_state=6074)
    pilot = shuffled.groupby(["_country", "platform"], sort=False).head(3)
    blind = pilot[["source_record", "text"]].copy()
    blind["reviewed_sentiment"] = ""
    blind["review_note"] = ""
    opts.out.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects work in progress.
    paths = [opts.out/f"pilot_reviewer_{i}.csv" for i in (1, 2)]
    if any(p.exists() for p in paths):
        parser.error("A worksheet already exists; choose a new --out directory.")
    for path in paths:
        blind.to_csv(path, index=False, mode="x")
    print(f"Prepared {len(blind)} blinded pilot rows per worksheet.")
