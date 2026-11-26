"""Reproduce Yuwei's label-independent country, time and interaction comparisons.

Only the canonical cleaned snapshot is read. The analysis does not assign polarity
labels, train models, or perform population inference. Outputs are ready for team
review, not a record of independent teammate approval.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import platform
import base64

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/sentiment_cleaned.csv"
SOURCE_SHA = "4c38dc7cc2a8a06a96c13e989541c024ce31e9ee6af890a5f429fbe1f892ec6a"
BASE_COMMIT = "30b74f76653a6af56f558c264107a466f0f13571"
MAIN = ["USA", "UK", "Canada", "Australia", "India"]
PLATFORMS = ["Facebook", "Instagram", "Twitter"]
WINDOWS = ["all", "before_2023", "2023_observed", "2020_2022", "2023_Jan_Apr"]
WINDOW_LABELS = ["All dates", "Before 2023", "2023 observed", "2020-2022", "Jan-Apr 2023"]
COLORS = ["#3569A8", "#BE6541", "#36806B", "#8F6FA3", "#B08826"]
CELL_FLAG_N = 10  # A descriptive visibility flag, not an inference threshold.


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select_window(data, window):
    masks = {
        "all": pd.Series(True, index=data.index),
        "before_2023": data.year.lt(2023),
        "2023_observed": data.year.eq(2023),
        "2020_2022": data.year.between(2020, 2022),
        "2023_Jan_Apr": data.timestamp.ge("2023-01-01") & data.timestamp.lt("2023-05-01"),
    }
    return data.loc[masks[window]].copy()


def describe_cells(data, keys):
    return data.groupby(keys, observed=True).agg(
        posts=("source_record", "size"),
        mean_interactions=("total_interactions", "mean"),
        median_interactions=("total_interactions", "median"),
        q1_interactions=("total_interactions", lambda x: x.quantile(.25)),
        q3_interactions=("total_interactions", lambda x: x.quantile(.75)),
        min_interactions=("total_interactions", "min"),
        max_interactions=("total_interactions", "max"),
    ).reset_index()


def standardize(data, stratum, weights, countries=MAIN):
    """Use every fixed weight, or return NaN if a stratum is absent; never impute."""
    rows = []
    for country in countries:
        subset = data.loc[data.country_analysis.eq(country)]
        cells = subset.groupby(stratum).total_interactions.agg(["size", "mean"]).reindex(weights.index)
        complete = bool(cells["size"].fillna(0).gt(0).all())
        standardized = float((cells["mean"] * weights).sum()) if complete else np.nan
        observed = float(subset.total_interactions.mean()) if len(subset) else np.nan
        rows.append({"country_analysis": country, "posts": len(subset),
                     "observed_mean": observed, "standardized_mean": standardized,
                     "adjusted_minus_observed": standardized - observed,
                     "all_strata_observed": complete,
                     "minimum_stratum_posts": int(cells["size"].fillna(0).min())})
    return pd.DataFrame(rows)


def md_table(frame):
    frame = frame.fillna("—")
    def escape(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(map(escape, frame.columns)) + " |",
             "| " + " | ".join(["---"] * len(frame.columns)) + " |"]
    lines.extend("| " + " | ".join(map(escape, row)) + " |" for row in frame.itertuples(index=False, name=None))
    return "\n".join(lines)


def audit_existing_outputs(data):
    """Independently reconcile the earlier country/platform/hashtag handoffs."""
    checks = []
    published = ROOT / "reports/final/country"
    for dimension, filename in [("platform", "country_platform_counts.csv"), ("year", "country_year_counts.csv")]:
        actual = pd.crosstab(data.country_analysis, data[dimension])
        actual.columns = actual.columns.map(str)
        saved = pd.read_csv(published / filename, index_col=0)
        saved.columns = saved.columns.map(str)
        pd.testing.assert_frame_equal(actual.sort_index().sort_index(axis=1), saved.sort_index().sort_index(axis=1), check_names=False, check_dtype=False)
        checks.append({"check": filename, "status": "passed", "rows_or_posts": len(data)})
    saved_summary = pd.read_csv(published / "country_summary.csv").set_index("country_analysis")
    pd.testing.assert_series_equal(data.groupby("country_analysis").size().sort_index(), saved_summary.posts.sort_index(), check_names=False, check_dtype=False)
    checks.append({"check": "published country counts", "status": "passed", "rows_or_posts": len(data)})

    eda = ROOT / "reports/eda/tables"
    actual_platform = data.groupby("platform").agg(posts=("source_record", "size"), mean_interactions=("total_interactions", "mean"))
    saved_platform = pd.read_csv(eda / "platform_summary_verified.csv", index_col=0)
    pd.testing.assert_frame_equal(actual_platform.sort_index(), saved_platform.sort_index(), check_dtype=False, check_names=False)
    checks.append({"check": "Liwen full-platform counts and means", "status": "passed", "rows_or_posts": len(data)})

    saved_top = pd.read_csv(eda / "platform_sentiment_top10_pct_verified.csv", index_col=0)
    selected = data.loc[data.sentiment.isin(saved_top.columns)]
    counts = pd.crosstab(selected.platform, selected.sentiment).reindex(index=saved_top.index, columns=saved_top.columns, fill_value=0)
    actual_pct = counts.div(counts.sum(axis=1), axis=0) * 100
    np.testing.assert_allclose(actual_pct.to_numpy(), saved_top.to_numpy(), atol=1e-8)
    denominators = pd.read_csv(eda / "platform_sentiment_top10_denominators.csv", index_col=0).subset_posts
    pd.testing.assert_series_equal(counts.sum(axis=1), denominators, check_names=False, check_dtype=False)
    checks.append({"check": "Liwen selected-label composition denominators", "status": "passed", "rows_or_posts": len(selected)})

    tags = data[["source_record", "platform", "total_interactions", "hashtag_list"]].copy()
    tags["tag"] = tags.hashtag_list.map(json.loads)
    tags = tags.explode("tag").dropna(subset=["tag"]).drop_duplicates(["source_record", "tag"])
    tag_summary = tags.groupby("tag").agg(posts=("source_record", "size"), mean_interactions=("total_interactions", "mean"))
    saved_tags = pd.read_csv(eda / "hashtag_summary_verified.csv", index_col=0)
    pd.testing.assert_frame_equal(tag_summary.sort_index(), saved_tags.sort_index(), check_names=False, check_dtype=False, rtol=1e-7)
    checks.append({"check": "Liwen hashtag post counts and means", "status": "passed", "rows_or_posts": len(tags)})
    denominator_table = actual_platform.rename(columns={"posts": "all_platform_posts"}).join(denominators.rename("selected_label_posts"))
    denominator_table["selected_share_of_platform_pct"] = 100 * denominator_table.selected_label_posts / denominator_table.all_platform_posts
    return pd.DataFrame(checks), denominator_table.reset_index(), tag_summary.reset_index(), tags


def save_fig(fig, folder, name):
    for extension in ["png", "svg"]:
        fig.savefig(folder / f"{name}.{extension}", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def heatmap(ax, values, rows, columns, title, fmt="d", cmap="Blues", vmin=None, vmax=None):
    image = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(columns)), columns, fontsize=9)
    ax.set_yticks(range(len(rows)), rows, fontsize=10)
    ax.set_title(title, loc="left", fontsize=12, pad=12)
    threshold = (np.nanmin(values) + np.nanmax(values)) / 2
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            ax.text(j, i, format(value, fmt), ha="center", va="center", fontsize=9,
                    color="white" if value > threshold else "#202A35")
    return image


def make_figures(data, tables, folder):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    counts = data.country_analysis.value_counts()
    shown_counts = [int(counts[c]) for c in MAIN] + [int(len(data) - counts.reindex(MAIN).sum())]
    yearly = pd.crosstab(data.country_analysis, data.year).reindex(index=MAIN, columns=range(2010, 2024), fill_value=0)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.4), gridspec_kw={"width_ratios": [1, 1.8]})
    bars = axes[0].barh(MAIN + ["Other 27 groups"], shown_counts, color=COLORS + ["#B7BFC6"])
    axes[0].invert_yaxis()
    axes[0].bar_label(bars, labels=[f"n={n} ({100*n/len(data):.1f}%)" for n in shown_counts], padding=4, fontsize=9)
    axes[0].set(xlabel="Recorded posts (all 710 posts)", xlim=(0, 255), title="A. Country representation")
    im = heatmap(axes[1], yearly.to_numpy(), MAIN, yearly.columns.map(str), "B. Country-by-year post counts")
    axes[1].tick_params(axis="x", rotation=50)
    axes[1].add_patch(Rectangle((12.5, -.5), 1, 5, fill=False, edgecolor="#B45C33", linewidth=2))
    fig.colorbar(im, ax=axes[1], label="Posts", fraction=.035)
    fig.suptitle("The five largest country groups contain 594 of 710 posts (83.7%)", fontsize=14)
    fig.text(.02, .005, "Synthetic sample. UK includes the one Scotland record. Counts describe supplied geography, not population or culture.", fontsize=9)
    fig.tight_layout(rect=(0,.045,1,.94))
    save_fig(fig, folder, "01_country_coverage")

    monthly = tables["country_month_2023_counts"].set_index("country_analysis").reindex(MAIN)
    month_columns = [str(m) for m in range(1, 11)]
    row_labels = [f"{c} (n={int(monthly.loc[c, month_columns].sum())})" for c in MAIN]
    fig, ax = plt.subplots(figsize=(11, 4))
    im = heatmap(ax, monthly[month_columns].to_numpy(dtype=int), row_labels,
                 ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct"],
                 "2023 recorded posts: the observed months differ across countries")
    ax.add_patch(Rectangle((-.5,-.5),4,5,fill=False,edgecolor="#B45C33",linewidth=2))
    fig.colorbar(im, ax=ax, label="Posts", fraction=.03)
    fig.text(.02,.01,"Outline: common January-April window. Zero means no record in this file, not no real-world activity. Source timezone is unspecified.",fontsize=8.5)
    fig.tight_layout(rect=(0,.05,1,1))
    save_fig(fig,folder,"02_2023_monthly_support")

    fig, ax = plt.subplots(figsize=(10,4.5))
    arrays = [data.loc[data.country_analysis.eq(c), "total_interactions"].to_numpy() for c in MAIN]
    bp = ax.boxplot(arrays, orientation="horizontal", tick_labels=[f"{c} (n={len(a)})" for c,a in zip(MAIN,arrays)],
                    whis=(0,100), patch_artist=True, widths=.55, medianprops={"color":"#152C3C","linewidth":2})
    for patch,color in zip(bp["boxes"],COLORS): patch.set(facecolor=color,alpha=.45)
    ax.scatter([a.mean() for a in arrays],range(1,6),marker="D",s=45,c="#152C3C",label="Mean",zorder=3)
    ax.invert_yaxis()
    ax.set(xlabel="Recorded interactions per post (likes + retweets)",title="Country distributions overlap; mean and median answer different questions")
    ax.legend(loc="upper right")
    ax.grid(axis="x",alpha=.2)
    fig.text(.02,.005,"All observed dates. Boxes: Q1-Q3; center line: median; whiskers: observed min-max; diamond: mean. These are counts, not engagement rates.",fontsize=8.5)
    fig.tight_layout(rect=(0,.05,1,1))
    save_fig(fig,folder,"03_interaction_distributions")

    window_table = tables["country_window_summary"]
    means = window_table.pivot(index="country_analysis",columns="window",values="mean_interactions").reindex(index=MAIN,columns=WINDOWS)
    support = window_table.pivot(index="country_analysis",columns="window",values="posts").reindex(index=MAIN,columns=WINDOWS)
    fig,axes=plt.subplots(1,2,figsize=(14,4.4))
    im=heatmap(axes[0],means.to_numpy(),MAIN,WINDOW_LABELS,"A. Mean recorded interactions",fmt=".1f",vmin=40,vmax=75)
    for ax in axes: ax.tick_params(axis="x",rotation=30)
    fig.colorbar(im,ax=axes[0],fraction=.03,label="Interactions per post")
    im=heatmap(axes[1],support.to_numpy(dtype=int),MAIN,WINDOW_LABELS,"B. Posts used in each mean",fmt="d")
    fig.colorbar(im,ax=axes[1],fraction=.03,label="Posts")
    fig.text(.02,.005,"Windows use the same date rule for every country and overlap; columns are not independent samples. 2023 is observed only through October.",fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1))
    save_fig(fig,folder,"04_time_window_sensitivity")

    full = tables["country_platform_window_summary"].query("window == 'all'")
    fig,axes=plt.subplots(1,3,figsize=(14,4.3),sharey=True)
    for ax,plat in zip(axes,PLATFORMS):
        part=full.loc[full.platform.eq(plat)].set_index("country_analysis").reindex(MAIN)
        for pos,country in enumerate(MAIN):
            row=part.loc[country]
            ax.plot([row.q1_interactions,row.q3_interactions],[pos,pos],lw=6,alpha=.5,color=COLORS[pos],solid_capstyle="round")
            ax.scatter(row.median_interactions,pos,c=COLORS[pos],s=45,zorder=3)
            ax.scatter(row.mean_interactions,pos,facecolors="none",edgecolors="#152C3C",marker="D",s=35,zorder=4)
            ax.text(101,pos,f"n={int(row.posts)}",va="center",fontsize=9)
        ax.set(title=plat,xlabel="Interactions per post",xlim=(35,114),yticks=range(5),yticklabels=MAIN)
        ax.grid(axis="x",alpha=.2)
    axes[0].invert_yaxis()
    fig.suptitle("Within-platform distributions: country ordering depends on the statistic and platform",fontsize=14)
    fig.text(.02,.005,"All observed dates. Colored point: median; thick line: Q1-Q3 (not a confidence interval); hollow diamond: mean. All 15 cells have n >= 19.",fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.93))
    save_fig(fig,folder,"05_within_platform")


def write_report(tables, manifest, out):
    full=tables["country_window_summary"].query("window == 'all'").set_index("country_analysis").reindex(MAIN)
    support_table=full[["posts","mean_interactions","median_interactions","q1_interactions","q3_interactions"]].round(2).reset_index()
    ranges=tables["country_2023_date_ranges"].copy()
    adjusted=tables["standardized_interactions"]
    platform_delta=adjusted.query("adjustment == 'platform_mix' and window == 'all'").adjusted_minus_observed.abs().max()
    duplicate_delta=tables["exact_text_sensitivity"].mean_change.abs().max()
    segments=[]
    def section(title,text,table=None,image=None):
        segments.append((title,text,table,image))
    section("Scope and completion status",
        "We completed the label-independent country analysis on 27 November 2026, using the canonical 710-post synthetic snapshot. "
        "This report is ready for Liwen's independent calculation/interpretation review; it is not a record of team approval. "
        "We did not create reviewed sentiment labels, train a classifier, or run significance tests. "
        "All country-level means and proportions use the posts retained in the explicitly named window. "
        "UK includes the one Scotland source record, while the original country column is preserved.",
        image="01_country_coverage.png")
    section("Finding 1: support and calendar coverage limit country comparisons",
        "The five largest groups account for 594/710 posts (83.7%); the other 27 groups contain 116 posts. "
        "USA, UK and Canada have 100/184 (54.3%), 73/141 (51.8%) and 67/131 (51.1%) of their posts in 2023, "
        "versus 14/70 (20.0%) for Australia and 24/68 (35.3%) for India. "
        "Even within 2023 the observed endpoints differ: India's last record is in May and Australia's in June, "
        "while the other three groups extend into October. Zero records do not establish zero activity or a known collection interval. "
        "Alternative explanation: different observed years/months, rather than geography, can change an aggregate comparison. "
        "Sensitivity: we also use before-2023, 2020-2022 and January-April 2023 windows, selected from date support rather than favorable interaction results. "
        "January-April is a common calendar restriction, not proof of complete or random sampling.",
        table=ranges,image="02_2023_monthly_support.png")
    section("Finding 2: distributions overlap and the headline depends on the statistic",
        "Across all observed dates, USA has the largest mean (66.80 recorded interactions), but Canada has the largest median (63, versus 60 for USA/UK). "
        "The middle halves of all five distributions overlap. The summaries below show the entire retained group; no engagement outlier is removed. "
        "Alternative explanation: a mean can be influenced by the upper tail and by the mixture of posts. "
        "Sensitivity: display medians, IQRs and observed ranges as well as means, then compare the same countries within each platform. "
        "Conclusion: these are overlapping distributions in this sample, not evidence that one country's population is more engaged.",
        table=support_table,image="03_interaction_distributions.png")
    section("Finding 3: some descriptive patterns persist, but lower-country ordering changes",
        "USA has the highest mean in all three full-period platform subsets and all five specified date windows. "
        "Other comparisons change: UK exceeds Canada in the full-period mean (61.52 vs 61.20), but Canada exceeds UK before 2023 (60.27 vs 58.37). "
        "In January-April 2023, Canada has a mean of 48.09 (n=23), compared with 62.09 over all its observed 2023 posts (n=67). "
        f"Reweighting the five groups to one common full-period platform mix changes each mean by at most {platform_delta:.3f} interactions per post. "
        "This small adjustment is a null sensitivity result worth retaining; it does not show that platform, time, wording or sampling can never matter. "
        "We also publish separate common pre-2023/2023 weighting. Neither adjustment is a joint platform-by-time adjustment. "
        "Conclusion: the USA mean pattern is descriptively consistent across the specified views, while a complete country ranking is not stable.",
        image="04_time_window_sensitivity.png")
    sparse=tables["country_platform_window_summary"].query("sparse_flag")[['window','country_analysis','platform','posts']]
    section("Support guardrails and sensitivity limits",
        "All 15 full-period country-by-platform cells have at least 19 records. "
        f"Across the finer windows, {len(sparse)} of the 75 main-group platform-window cells have fewer than {CELL_FLAG_N} posts. "
        "For example, Australia in observed 2023 has Facebook/Instagram/Twitter counts of 6/4/4; "
        "Canada in January-April has only 2 Instagram records. "
        "The n<10 marker is a disclosure convention, not a statistical validity threshold. "
        "Sparse cells remain in the support tables and any descriptive weighting; no missing stratum is imputed or silently dropped. "
        "No separately adjusted country claim is made for an absent stratum, and no joint platform-by-year standardization is attempted. "
        f"Keeping one source-order record per exact normalized text group changes the main-country means by at most {duplicate_delta:.3f} interactions; "
        "this is a sensitivity check, not a replacement cleaned dataset, and it does not detect paraphrased synthetic templates.",
        table=sparse.reset_index(drop=True),image="05_within_platform.png")
    section("Independent arithmetic review of existing platform/hashtag outputs",
        "The saved country counts, platform-year coverage, full-platform counts/means, selected-label platform percentages and hashtag counts/means reconcile to the canonical file. "
        "Liwen's selected-label composition chart uses only 235 posts: Facebook 84, Instagram 79 and Twitter 72, not all 710 posts. "
        "Every retained post has two hashtags, so this dataset cannot compare presence versus absence of hashtags. "
        "The 975 hashtag identities can overlap within posts; high means for rare tags are not significance or causal effects. "
        "No with/without-hashtag classifier result is available to review. This arithmetic audit is not independent approval by Liwen or a review of future model results.",
        table=tables["platform_denominator_audit"].round(2))
    section("What remains dependent on the team",
        "Yizhou must provide the versioned independent review records and adjudicated decisions before we can finish country positive/negative/neutral proportions, "
        "exclusion rates and reviewed-label platform/time checks. We have not inferred these from the 191 supplied labels. "
        "Yuwei's human-review assignments (B/C independent review and pilot/A disagreement adjudication) remain unperformed here. "
        "Liwen should verify the new calculations and interpretations; the team must approve final claims and select country figures for the presentation. "
        "This report describes supplied geography and recorded interaction counts in synthetic posts, not measured culture, causal effects or exposure-normalized engagement rates.")
    section("Reproduction and source version",
        f"Base repository commit: {BASE_COMMIT}. Cleaned CSV SHA-256: {SOURCE_SHA}. "
        "Run python scripts/country_comparisons.py and python scripts/check_country_comparisons.py from the repository root. "
        "Open notebooks/04_country_comparisons.ipynb for the walkthrough. "
        "New generated outputs live in generated/final/country_label_independent; the tracked publication copy lives beside this report. "
        "Counts for all 32 country groups, including zero-filled country/platform/window cells, are retained in tables/. "
        "The manifest records the runtime versions, source hash, windows, disclosure rule and validation status.")
    markdown=["# Country comparisons before sentiment adjudication", "", "**Analysis complete; independent team review pending.**", ""]
    body=["<h1>Country comparisons before sentiment adjudication</h1>","<p class='status'>Analysis complete · Independent team review pending</p>"]
    for title,text,table,image in segments:
        markdown.extend([f"## {title}","",text,""])
        body.extend([f"<h2>{html.escape(title)}</h2>",f"<p>{html.escape(text)}</p>"])
        if table is not None:
            markdown.extend([md_table(table),""])
            body.append(table.to_html(index=False,border=0,classes="evidence",escape=True))
        if image:
            markdown.extend([f"![{title}](figures/{image})",""])
            encoded=base64.b64encode((out/'figures'/image).read_bytes()).decode()
            body.append(f'<img alt="{html.escape(title)}" src="data:image/png;base64,{encoded}">')
    (out/'findings.md').write_text("\n".join(markdown),encoding="utf-8")
    stylesheet="body{max-width:1120px;margin:40px auto;padding:0 28px;font:16px/1.65 Arial,sans-serif;color:#223242}h1{font-size:32px;line-height:1.25}h2{margin-top:38px;font-size:23px}.status{padding:12px 18px;background:#edf4fa;border-left:4px solid #3569a8}img{width:100%;height:auto;margin:14px 0}table{border-collapse:collapse;font-size:13px;width:100%;margin:20px 0}th,td{padding:7px 9px;border-bottom:1px solid #dbe2e8;text-align:right}th:first-child,td:first-child{text-align:left}th{background:#edf4fa}"
    (out/'report.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Yuwei: country comparisons</title><style>'+stylesheet+'</style></head><body>'+"\n".join(body)+'</body></html>',encoding='utf-8')


def build(source=SOURCE, out=None):
    source=Path(source)
    out=Path(out) if out is not None else ROOT/'generated/final/country_label_independent'
    if sha(source)!=SOURCE_SHA: raise ValueError("Input differs from the canonical cleaned snapshot; review the new version before analysis.")
    data=pd.read_csv(source,parse_dates=['timestamp'])
    assert data.shape==(710,26) and data.source_record.is_unique
    assert data.total_interactions.eq(data.likes+data.retweets).all()
    assert data.timestamp.dt.year.eq(data.year).all()
    data['country_analysis']=data.country.str.strip().replace({'Scotland':'UK'})
    assert data.country.nunique()==33 and data.country_analysis.nunique()==32
    assert data.country_analysis.value_counts().head(5).index.tolist()==MAIN
    out.mkdir(parents=True,exist_ok=True)
    (out/'tables').mkdir(exist_ok=True)
    (out/'figures').mkdir(exist_ok=True)
    tables={}
    tables['country_counts']=data.country_analysis.value_counts().rename_axis('country_analysis').rename('posts').reset_index()
    tables['country_counts']['share_of_all_posts_pct']=100*tables['country_counts'].posts/len(data)
    tables['country_year_counts']=pd.crosstab(data.country_analysis,data.year).reset_index()
    in_2023=data.loc[data.year.eq(2023)]
    monthly=pd.crosstab(in_2023.country_analysis,in_2023.month).reindex(index=sorted(data.country_analysis.unique()),columns=range(1,13),fill_value=0)
    monthly.columns=monthly.columns.map(str)
    tables['country_month_2023_counts']=monthly.reset_index()
    ranges=in_2023.loc[in_2023.country_analysis.isin(MAIN)].groupby('country_analysis').agg(posts=('source_record','size'),first_record=('timestamp','min'),last_record=('timestamp','max')).reindex(MAIN).reset_index()
    tables['country_2023_date_ranges']=ranges
    window_rows=[]; all_platform_rows=[]; window_definitions=[]; adjustments=[]; weight_rows=[]
    main=data.loc[data.country_analysis.isin(MAIN)]
    platform_weights=main.platform.value_counts(normalize=True).reindex(PLATFORMS)
    periods=main.assign(period=np.where(main.year.eq(2023),'2023','before_2023'))
    period_weights=periods.period.value_counts(normalize=True).sort_index()
    for stratum,weights in [('platform',platform_weights),('period',period_weights)]:
        weight_rows.extend({'stratum_type':stratum,'stratum':str(k),'weight':float(v),'reference_posts':len(main)} for k,v in weights.items())
    for window in WINDOWS:
        subset=select_window(data,window)
        summary=describe_cells(subset,['country_analysis'])
        summary.insert(0,'window',window)
        summary['main_display']=summary.country_analysis.isin(MAIN)
        window_rows.append(summary)
        cells=describe_cells(subset,['country_analysis','platform']).set_index(['country_analysis','platform'])
        full_index=pd.MultiIndex.from_product([sorted(data.country_analysis.unique()),PLATFORMS],names=['country_analysis','platform'])
        cells=cells.reindex(full_index).reset_index()
        cells['posts']=cells.posts.fillna(0).astype(int)
        cells.insert(0,'window',window)
        cells['main_display']=cells.country_analysis.isin(MAIN)
        cells['sparse_flag']=cells.posts.lt(CELL_FLAG_N)
        all_platform_rows.append(cells)
        window_definitions.append({'window':window,'all_country_posts':len(subset),'main_country_posts':int(subset.country_analysis.isin(MAIN).sum()),'first_record':str(subset.timestamp.min()),'last_record':str(subset.timestamp.max())})
        adjusted=standardize(subset,'platform',platform_weights)
        adjusted.insert(0,'window',window);adjusted.insert(1,'adjustment','platform_mix')
        adjustments.append(adjusted)
    temporal=standardize(periods,'period',period_weights)
    temporal.insert(0,'window','all');temporal.insert(1,'adjustment','two_period_mix')
    adjustments.append(temporal)
    tables['country_window_summary']=pd.concat(window_rows,ignore_index=True)
    tables['all_country_platform_window_support']=pd.concat(all_platform_rows,ignore_index=True)
    tables['country_platform_window_summary']=tables['all_country_platform_window_support'].query('main_display').reset_index(drop=True)
    tables['sparse_main_cells']=tables['country_platform_window_summary'].query('sparse_flag').reset_index(drop=True)
    tables['window_definitions']=pd.DataFrame(window_definitions)
    tables['standardized_interactions']=pd.concat(adjustments,ignore_index=True)
    tables['standardization_weights']=pd.DataFrame(weight_rows)
    tables['country_window_ranks']=tables['country_window_summary'].query('main_display').copy()
    tables['country_window_ranks']['mean_rank_within_window']=tables['country_window_ranks'].groupby('window').mean_interactions.rank(ascending=False,method='min')
    unique=data.sort_values('source_record').drop_duplicates('text_group_id')
    full=describe_cells(data,['country_analysis']).set_index('country_analysis')
    dedup=describe_cells(unique,['country_analysis']).set_index('country_analysis')
    tables['exact_text_sensitivity']=pd.DataFrame({'all_posts':full.posts,'one_per_exact_text_posts':dedup.posts,'all_mean':full.mean_interactions,'one_per_exact_text_mean':dedup.mean_interactions,'all_median':full.median_interactions,'one_per_exact_text_median':dedup.median_interactions}).reindex(MAIN).reset_index()
    tables['exact_text_sensitivity']['mean_change']=tables['exact_text_sensitivity'].one_per_exact_text_mean-tables['exact_text_sensitivity'].all_mean
    tables['repeated_text_records']=data.loc[data.text_group_id.duplicated(keep=False),['source_record','country','country_analysis','platform','timestamp','text_group_id','text','total_interactions']].sort_values(['text_group_id','source_record'])
    checks,denominators,tags,tag_rows=audit_existing_outputs(data)
    tables['existing_output_audit']=checks
    tables['platform_denominator_audit']=denominators
    tables['hashtag_arithmetic_audit']=tags
    for name,frame in tables.items(): frame.to_csv(out/'tables'/f'{name}.csv',index=False,float_format='%.9f')
    main_means=tables['country_window_summary'].query('main_display')
    assert all(main_means.loc[main_means.window.eq(w)].set_index('country_analysis').mean_interactions.idxmax()=='USA' for w in WINDOWS)
    assert len(tables['country_platform_window_summary'])==75
    manifest={'analysis_date':'2026-11-27','base_repository_commit':BASE_COMMIT,'source_sha256':SOURCE_SHA,
        'source_rows':len(data),'source_unchanged':sha(source)==SOURCE_SHA,'country_groups':32,'main_countries':MAIN,
        'main_posts':len(main),'windows':WINDOWS,'cell_flag_below_n':CELL_FLAG_N,
        'cell_flag_is_inference_threshold':False,'standardization':'Fixed pooled full-period main-country weights; no missing-stratum imputation',
        'excluded_rows':0,'reviewed_sentiment_used':False,'models_trained':0,'hypothesis_tests_run':0,
        'status':'calculation_checks_passed; independent team review pending','team_approved':False,
        'exact_text_unique_rows':len(unique),'hashtag_post_rows':len(tag_rows),
        'runtime':{'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'matplotlib':matplotlib.__version__}}
    make_figures(data,tables,out/'figures')
    write_report(tables,manifest,out)
    figure_rows=[{'figure':f'{n}.png','editable_vector':f'{n}.svg'} for n in ['01_country_coverage','02_2023_monthly_support','03_interaction_distributions','04_time_window_sensitivity','05_within_platform']]
    pd.DataFrame(figure_rows).to_csv(out/'figure_manifest.csv',index=False)
    (out/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return tables,manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'generated/final/country_label_independent')
    args=parser.parse_args()
    _,manifest=build(out=args.out)
    print(json.dumps(manifest,indent=2))
