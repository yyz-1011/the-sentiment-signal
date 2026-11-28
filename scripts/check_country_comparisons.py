"""Independent denominator, support and weighting checks for country_comparisons."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

from country_comparisons import ROOT, SOURCE, SOURCE_SHA, MAIN, PLATFORMS, WINDOWS, select_window, standardize


def check(out):
    out = Path(out)
    data = pd.read_csv(SOURCE, parse_dates=["timestamp"])
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    data["country_analysis"] = data.country.str.strip().replace({"Scotland": "UK"})
    read = lambda name: pd.read_csv(out / "tables" / f"{name}.csv")
    counts = read("country_counts").set_index("country_analysis")
    assert counts.posts.sum() == 710
    assert counts.loc[MAIN].posts.tolist() == [184,141,131,70,68]
    assert counts.loc[MAIN].posts.sum() == 594
    assert np.isclose(counts.share_of_all_posts_pct.sum(),100)
    summary = read("country_window_summary")
    support = read("all_country_platform_window_support")
    main_cells = read("country_platform_window_summary")
    assert len(support) == 32 * 3 * 5 and len(main_cells) == 75
    assert main_cells.sparse_flag.equals(main_cells.posts.lt(10))
    assert main_cells.query("window == 'all'").posts.min() == 19
    for window in WINDOWS:
        subset = select_window(data,window)
        rows = support.loc[support.window.eq(window)]
        assert rows.posts.sum() == len(subset)
        assert rows.groupby("country_analysis").posts.sum().reindex(counts.index,fill_value=0).to_dict() == subset.country_analysis.value_counts().reindex(counts.index,fill_value=0).to_dict()
        for country in MAIN:
            original = subset.loc[subset.country_analysis.eq(country),"total_interactions"]
            saved = summary.loc[summary.window.eq(window) & summary.country_analysis.eq(country)].iloc[0]
            assert int(saved.posts) == len(original)
            np.testing.assert_allclose([saved.mean_interactions,saved.median_interactions,saved.q1_interactions,saved.q3_interactions],
                [original.mean(),original.median(),original.quantile(.25),original.quantile(.75)],atol=1e-8)
    # Boundary fixture: April 30 belongs to the common window; May 1 does not.
    fixture=pd.DataFrame({"timestamp":pd.to_datetime(["2023-01-01","2023-04-30 23:59:59","2023-05-01"],format="mixed"),"year":[2023]*3})
    assert select_window(fixture,"2023_Jan_Apr").index.tolist()==[0,1]
    assert main_cells.query("window == '2023_Jan_Apr' and country_analysis == 'Canada' and platform == 'Instagram'").posts.item()==2
    ranges = read("country_2023_date_ranges").set_index("country_analysis")
    assert ranges.loc["India","last_record"].startswith("2023-05-06")
    assert ranges.loc["Australia","last_record"].startswith("2023-06-15")

    # Weighting fixture: pooled weights are fixed, never renormalized to observed cells.
    fixture=pd.DataFrame({"country_analysis":["A","A","A","B"],"platform":["Facebook","Facebook","Instagram","Facebook"],"total_interactions":[10,30,80,10]})
    weights=pd.Series({"Facebook":.25,"Instagram":.75})
    got=standardize(fixture,"platform",weights,countries=["A","B"]).set_index("country_analysis")
    assert np.isclose(got.loc["A","standardized_mean"],65)
    assert not got.loc["B","all_strata_observed"] and pd.isna(got.loc["B","standardized_mean"])
    adjusted=read("standardized_interactions")
    pooled=data.loc[data.country_analysis.isin(MAIN)].platform.value_counts(normalize=True)
    for row in adjusted.query("adjustment == 'platform_mix'").itertuples():
        subset=select_window(data,row.window)
        cells=subset.loc[subset.country_analysis.eq(row.country_analysis)].groupby("platform").total_interactions.mean()
        if set(PLATFORMS)<=set(cells.index):
            assert np.isclose(row.standardized_mean,sum(pooled[p]*cells[p] for p in PLATFORMS))
        else:
            assert pd.isna(row.standardized_mean)
    published=pd.read_csv(ROOT/"reports/final/country/country_interactions_sensitivity.csv").set_index("country_analysis")
    fresh=adjusted.query("window == 'all' and adjustment == 'platform_mix'").set_index("country_analysis")
    np.testing.assert_allclose(fresh.loc[MAIN].standardized_mean,published.loc[MAIN].common_platform_mix_mean,atol=1e-6)
    assert fresh.adjusted_minus_observed.abs().max()<.17
    # The two-period adjustment has the same fixed reference across all five countries.
    reference=data.loc[data.country_analysis.isin(MAIN)].assign(period=lambda x:np.where(x.year.eq(2023),"2023","before_2023"))
    period_weights=reference.period.value_counts(normalize=True)
    for row in adjusted.query("adjustment == 'two_period_mix'").itertuples():
        group=reference.loc[reference.country_analysis.eq(row.country_analysis)].groupby('period').total_interactions.mean()
        assert np.isclose(row.standardized_mean,sum(group[k]*v for k,v in period_weights.items()))

    audit=read("existing_output_audit")
    assert len(audit)==6 and audit.status.eq("passed").all()
    denoms=read("platform_denominator_audit").set_index("platform")
    assert denoms.loc[PLATFORMS].all_platform_posts.tolist()==[223,251,236]
    assert denoms.loc[PLATFORMS].selected_label_posts.tolist()==[84,79,72]
    assert denoms.selected_label_posts.sum()==235
    assert data.hashtag_count.eq(2).all()
    tags=read("hashtag_arithmetic_audit")
    assert len(tags)==975 and tags.posts.sum()==1420
    assert data.text_group_id.nunique()==706
    duplicate=read("exact_text_sensitivity")
    assert duplicate.mean_change.abs().max()<.324
    ranks=read("country_window_ranks")
    assert ranks.query("mean_rank_within_window == 1").country_analysis.eq("USA").all()
    before=summary.query("window == 'before_2023'").set_index('country_analysis')
    assert before.loc['Canada','mean_interactions']>before.loc['UK','mean_interactions']
    assert fresh.loc['UK','observed_mean']>fresh.loc['Canada','observed_mean']
    manifest=json.loads((out/'analysis_manifest.json').read_text())
    assert not manifest['reviewed_sentiment_used'] and manifest['models_trained']==0 and not manifest['team_approved']
    assert len(list((out/'figures').glob('*.png')))==5
    assert len(list((out/'figures').glob('*.svg')))==5
    result={'status':'passed','source_sha256':SOURCE_SHA,'source_rows':710,'country_groups':32,
        'windows':5,'main_platform_window_cells':75,'all_country_platform_window_cells':480,
        'existing_handoff_checks':6,'weighting_fixture_and_calendar_boundaries':'passed',
        'raw_inputs_unchanged':True,'team_review':'pending'}
    (out/'calculation_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'generated/final/country_label_independent')
    args=parser.parse_args()
    print(json.dumps(check(args.out),indent=2))
