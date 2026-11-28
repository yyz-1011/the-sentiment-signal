"""Evaluate text models using manually adjudicated labels and grouped splits."""
import argparse
import hashlib
import json
from pathlib import Path
import re

import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ["negative", "neutral", "positive"]
DECISIONS = set(CLASSES + ["exclude"])
SEED = 6074


def load_review(source, reviewed):
    d = pd.read_csv(source)
    r = pd.read_csv(reviewed)
    columns = ["source_record", "reviewed_sentiment", "decision_note"]
    if not set(columns).issubset(r):
        raise ValueError(f"Reviewed CSV must contain {columns}")
    if r.source_record.duplicated().any() or set(r.source_record) != set(d.source_record):
        raise ValueError("Provide exactly one adjudicated decision for every source_record.")
    if not r.reviewed_sentiment.isin(DECISIONS).all() or not r.decision_note.fillna("").str.strip().ne("").all():
        raise ValueError("Every decision requires an allowed label and a nonempty decision note.")
    merged = d.merge(r[columns], on="source_record", validate="one_to_one")
    included = merged[merged.reviewed_sentiment.ne("exclude")].reset_index(drop=True)
    if included.groupby("text_group_id").reviewed_sentiment.nunique().gt(1).any():
        raise ValueError("Resolve conflicting reviewed labels within identical text groups.")
    return merged, included


def folds(d, n):
    cv = StratifiedGroupKFold(n_splits=n, shuffle=True, random_state=SEED)
    pairs = list(cv.split(d.text, d.reviewed_sentiment, d.text_group_id))
    for train, test in pairs:
        assert not set(d.iloc[train].text_group_id) & set(d.iloc[test].text_group_id)
    if not all(set(d.iloc[idx].reviewed_sentiment) == set(CLASSES)
               for pair in pairs for idx in pair):
        raise ValueError("The split does not contain all classes in every train and evaluation partition.")
    return pairs


def candidates():
    return {"majority": lambda: DummyClassifier(strategy="most_frequent"),
            "logistic": lambda: make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1500, random_state=SEED)),
            "linear_svc": lambda: make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LinearSVC(random_state=SEED))}


def scores(d, pairs, text, variant):
    metrics, predictions, per_class = [], [], []
    for name, factory in candidates().items():
        for i, (train, val) in enumerate(pairs, 1):
            model = factory().fit(text.iloc[train], d.reviewed_sentiment.iloc[train])
            pred = model.predict(text.iloc[val])
            actual = d.reviewed_sentiment.iloc[val]
            metrics.append({"model": name, "fold": i, "variant": variant,
                            "macro_f1": f1_score(actual, pred, labels=CLASSES, average="macro", zero_division=0),
                            "accuracy": accuracy_score(actual, pred), "validation_posts": len(val)})
            report = classification_report(actual, pred, labels=CLASSES, output_dict=True, zero_division=0)
            per_class.extend({"model": name, "fold": i, "variant": variant,
                              "label": label, **report[label]} for label in CLASSES)
            predictions.extend({"source_record": int(d.iloc[j].source_record), "fold": i,
                                "model": name, "variant": variant, "actual": truth,
                                "predicted": guess} for j, truth, guess in zip(val, actual, pred))
    return metrics, predictions, per_class


def evaluate(reviewed, out, finalize=False, source=ROOT/"data/processed/sentiment_cleaned.csv"):
    output = out/"final_test_results.csv"
    manifest = out/"evaluation_manifest.json"
    version = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in
               {"source": source, "reviewed_labels": reviewed, "pipeline": Path(__file__)}.items()}
    version.update({"seed": SEED, "scikit_learn": sklearn.__version__})
    if output.exists():
        raise ValueError("Final results already exist. Preserve this run and do not tune against its test set.")
    if finalize and (not manifest.exists() or json.loads(manifest.read_text()) != version):
        raise ValueError("Run development first with the same data, labels, code and version, then review the selection before finalizing.")
    merged, d = load_review(source, reviewed)
    if d.groupby("reviewed_sentiment").text_group_id.nunique().reindex(CLASSES, fill_value=0).min() < 5:
        raise ValueError("Each reviewed class needs at least five distinct text groups for the fixed holdout design.")
    # With limited neutral support, fail clearly instead of reporting a score
    # on a test set missing a class or silently changing the task.
    train, test = folds(d, 5)[0]
    dev = d.iloc[train].reset_index(drop=True)
    for n in (4, 3, 2):
        try:
            pairs = folds(dev, n)
            break
        except ValueError:
            continue
    else:
        raise ValueError("Insufficient reviewed class support for grouped development evaluation.")
    clean_text = dev.text.map(lambda x: re.sub(r"#\w+", "", x))
    records, predictions, per_class = [], [], []
    for variant, inputs in [("without_hashtags", clean_text), ("original_text", dev.text)]:
        metric_rows, prediction_rows, class_rows = scores(dev, pairs, inputs, variant)
        records.extend(metric_rows); predictions.extend(prediction_rows); per_class.extend(class_rows)
    results = pd.DataFrame(records)
    # Predefined primary variant removes literal hashtags. Original text is
    # a sensitivity check, not a reason to tune on test labels.
    comparison = results[results.variant.eq("without_hashtags")].groupby("model").macro_f1.mean()
    winner = comparison.drop(index="majority").sort_values(ascending=False, kind="stable").index[0]
    out.mkdir(parents=True, exist_ok=True)
    results.to_csv(out/"development_scores.csv", index=False)
    pd.DataFrame(per_class).to_csv(out/"development_class_metrics.csv", index=False)
    oof = pd.DataFrame(predictions)
    oof.to_csv(out/"development_predictions.csv", index=False)
    oof[oof.actual.ne(oof.predicted)].merge(dev[["source_record", "text", "country", "platform"]], on="source_record", validate="many_to_one").to_csv(out/"development_errors.csv", index=False)
    results.groupby(["model", "variant"]).macro_f1.agg(["mean", "std", "min", "max"]).to_csv(out/"development_summary.csv")
    difference = results.pivot(index=["model", "fold"], columns="variant", values="macro_f1")
    difference["original_minus_without_hashtags"] = difference.original_text - difference.without_hashtags
    difference.to_csv(out/"hashtag_sensitivity.csv")
    merged.groupby(["country", "reviewed_sentiment"]).size().rename("posts").to_csv(out/"review_coverage.csv")
    split = d[["source_record", "text_group_id"]].copy()
    split["partition"] = "development"
    split.loc[test, "partition"] = "test"
    split.to_csv(out/"split_manifest.csv", index=False)
    memberships = []
    for i, (fit, validation) in enumerate(pairs, 1):
        for role, ids in [("train", fit), ("validation", validation)]:
            memberships.extend({"fold": i, "role": role, "source_record": int(dev.iloc[j].source_record),
                                "text_group_id": dev.iloc[j].text_group_id} for j in ids)
    pd.DataFrame(memberships).to_csv(out/"development_fold_manifest.csv", index=False)
    pd.DataFrame([{"candidate": winner, "candidate_development_macro_f1": comparison[winner],
                   "baseline_development_macro_f1": comparison["majority"], "folds": n}]).to_csv(out/"development_selection.csv", index=False)
    if not finalize:
        manifest.write_text(json.dumps(version, indent=2) + "\n")
        return
    held = d.iloc[test].reset_index(drop=True)
    held_text = held.text.map(lambda x: re.sub(r"#\w+", "", x))
    reports = []
    for name in ("majority", winner):
        pred = candidates()[name]().fit(clean_text, dev.reviewed_sentiment).predict(held_text)
        report = classification_report(held.reviewed_sentiment, pred, labels=CLASSES,
                                       output_dict=True, zero_division=0)
        for label in CLASSES + ["macro avg"]:
            reports.append({"model": name, "label": label, **report[label]})
        matrix = confusion_matrix(held.reviewed_sentiment, pred, labels=CLASSES)
        pd.DataFrame(matrix, index=CLASSES, columns=CLASSES).rename_axis("actual").to_csv(out/f"test_confusion_{name}.csv")
        pd.DataFrame({"source_record": held.source_record, "actual": held.reviewed_sentiment,
                      "predicted": pred}).to_csv(out/f"test_predictions_{name}.csv", index=False)
    pd.DataFrame(reports).to_csv(output, index=False)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reviewed", required=True, type=Path)
    p.add_argument("--out", type=Path, default=ROOT/"generated/final/model")
    p.add_argument("--finalize", action="store_true", help="Open the held-out test only after freezing model decisions.")
    args = p.parse_args()
    try:
        evaluate(args.reviewed, args.out, args.finalize)
    except (OSError, ValueError) as e:
        p.error(str(e))
