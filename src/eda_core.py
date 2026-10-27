from pathlib import Path
import html
import json
import math
import pandas as pd

PALETTE = ['#275DAD', '#48A9A6', '#F4A259', '#D95D39', '#7656A5', '#4F772D', '#E76F8A', '#5C677D', '#E9C46A', '#2A9D8F', '#A44A3F', '#577590']


def _svg_start(title, width, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#263238}.title{font-size:24px;font-weight:700}.subtitle{font-size:13px;fill:#56616a}.label{font-size:13px}.small{font-size:11px;fill:#56616a}.grid{stroke:#e5e9ed;stroke-width:1}</style>',
            f'<text class="title" x="48" y="42">{html.escape(title)}</text>']


def _write_svg(path, parts):
    path.write_text('\n'.join(parts + ['</svg>']), encoding='utf-8')


def _distribution_svg(counts, path):
    top = counts.head(12).copy()
    tail_n = int(counts.iloc[12:]['posts'].sum())
    if tail_n:
        top.loc[f'Other ({len(counts) - len(top)} labels)'] = tail_n
    w, h = 1050, 680
    left, right, top_y, bottom = 235, 970, 105, 620
    plot_h = bottom - top_y
    row_h = plot_h / len(top)
    max_v = int(top['posts'].max())
    p = _svg_start('Sentiment label distribution', w, h)
    p.append(f'<text class="subtitle" x="48" y="68">710 posts · top 12 labels shown; remaining labels grouped as Other</text>')
    for tick in range(0, max_v + 1, 10):
        x = left + (right-left) * tick / max_v
        p.extend([f'<line class="grid" x1="{x:.1f}" y1="{top_y}" x2="{x:.1f}" y2="{bottom}"/>',
                  f'<text class="small" text-anchor="middle" x="{x:.1f}" y="645">{tick}</text>'])
    for i, (label, row) in enumerate(top.iterrows()):
        y = top_y + i * row_h + 5
        value = int(row.posts)
        bw = (right-left) * value / max_v
        p.extend([f'<text class="label" text-anchor="end" x="{left-12}" y="{y+row_h*.63:.1f}">{html.escape(str(label))}</text>',
                  f'<rect x="{left}" y="{y:.1f}" width="{bw:.1f}" height="{row_h*.58:.1f}" rx="4" fill="{PALETTE[i%len(PALETTE)]}"/>',
                  f'<text class="small" x="{left+bw+8:.1f}" y="{y+row_h*.43:.1f}">{value} ({value/710*100:.1f}%)</text>'])
    p.append(f'<text class="small" text-anchor="middle" x="{(left+right)/2}" y="667">Posts</text>')
    _write_svg(path, p)


def _interaction_svg(df, counts, path):
    selected = counts[counts.posts >= 8].sort_values('posts', ascending=False).head(12).index.tolist()
    w, h = 1120, 650
    left, right, top_y, bottom = 215, 985, 112, 555
    p = _svg_start('Interactions by sentiment', w, h)
    p.append('<text class="subtitle" x="48" y="68">Boxplots of total interactions for the 12 most frequent labels with at least 8 posts · n shown in labels</text>')
    max_v = 120
    for tick in range(0, max_v+1, 20):
        x = left + (right-left)*tick/max_v
        p.extend([f'<line class="grid" x1="{x:.1f}" y1="{top_y}" x2="{x:.1f}" y2="{bottom}"/>',
                  f'<text class="small" text-anchor="middle" x="{x:.1f}" y="580">{tick}</text>'])
    row_h=(bottom-top_y)/len(selected)
    for i, label in enumerate(selected):
        group=df.loc[df.sentiment.eq(label), 'total_interactions'].astype(float)
        vals=group.quantile([0,.25,.5,.75,1]).tolist()
        y=top_y+i*row_h+row_h/2
        xvals=[left+(right-left)*v/max_v for v in vals]
        p.extend([f'<text class="label" text-anchor="end" x="{left-12}" y="{y+4:.1f}">{html.escape(str(label))} (n={len(group)})</text>',
                  f'<line x1="{xvals[0]:.1f}" y1="{y:.1f}" x2="{xvals[4]:.1f}" y2="{y:.1f}" stroke="#53616b" stroke-width="2"/>',
                  f'<line x1="{xvals[0]:.1f}" y1="{y-5:.1f}" x2="{xvals[0]:.1f}" y2="{y+5:.1f}" stroke="#53616b"/>',
                  f'<line x1="{xvals[4]:.1f}" y1="{y-5:.1f}" x2="{xvals[4]:.1f}" y2="{y+5:.1f}" stroke="#53616b"/>',
                  f'<rect x="{xvals[1]:.1f}" y="{y-8:.1f}" width="{max(1,xvals[3]-xvals[1]):.1f}" height="16" fill="#c9def4" stroke="#275DAD"/>',
                  f'<line x1="{xvals[2]:.1f}" y1="{y-8:.1f}" x2="{xvals[2]:.1f}" y2="{y+8:.1f}" stroke="#D95D39" stroke-width="2"/>'])
    p.append('<text class="small" text-anchor="middle" x="600" y="618">Total interactions (likes + retweets)</text>')
    p.append('<text class="small" x="48" y="640">Box: 25th–75th percentile; center line: median; whisker: observed minimum to maximum. No significance test performed.</text>')
    _write_svg(path, p)


def _temporal_svg(df, counts, path):
    years=sorted(df.timestamp.dt.year.unique().tolist())
    top_labels=counts.head(5).index.tolist()
    yearly=df.assign(year=df.timestamp.dt.year).groupby('year').size()
    yearly_sent=df.assign(year=df.timestamp.dt.year).groupby(['year','sentiment']).size().unstack(fill_value=0)
    w,h=1120,700
    left,right=90,1065
    p=_svg_start('Sentiment over time', w, h)
    p.append('<text class="subtitle" x="48" y="68">Annual post counts for the five most frequent sentiment labels, with total sample volume below</text>')
    y0,y1=130,405
    max_label=max(10,int(yearly_sent.reindex(columns=top_labels,fill_value=0).to_numpy().max()))
    for tick in range(0,max_label+1, max(1, math.ceil(max_label/5))):
        y=y1-(y1-y0)*tick/max_label
        p.extend([f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}"/>',
                  f'<text class="small" text-anchor="end" x="{left-10}" y="{y+4:.1f}">{tick}</text>'])
    coords={yr:left+(right-left)*i/max(1,len(years)-1) for i,yr in enumerate(years)}
    for j,label in enumerate(top_labels):
        pts=[]
        for yr in years:
            val=int(yearly_sent.loc[yr,label]) if label in yearly_sent.columns else 0
            y=y1-(y1-y0)*val/max_label
            pts.append(f'{coords[yr]:.1f},{y:.1f}')
        color=PALETTE[j]
        p.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{" ".join(pts)}"/>')
        for yr in years:
            val=int(yearly_sent.loc[yr,label]) if label in yearly_sent.columns else 0
            y=y1-(y1-y0)*val/max_label
            p.append(f'<circle cx="{coords[yr]:.1f}" cy="{y:.1f}" r="3.5" fill="{color}"/>')
        lx=165+j*185
        p.extend([f'<line x1="{lx}" y1="102" x2="{lx+25}" y2="102" stroke="{color}" stroke-width="3"/>',
                  f'<text class="small" x="{lx+32}" y="106">{html.escape(str(label))}</text>'])
    for yr in years:
        x=coords[yr]
        p.append(f'<text class="small" text-anchor="middle" x="{x:.1f}" y="425">{yr}</text>')
    b0,b1=485,620
    max_total=int(yearly.max())
    for i,yr in enumerate(years):
        bw=min(42,(right-left)/len(years)*.62)
        x=coords[yr]-bw/2
        bh=(b1-b0)*int(yearly.loc[yr])/max_total
        p.extend([f'<rect x="{x:.1f}" y="{b1-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#9eb2c5"/>',
                  f'<text class="small" text-anchor="middle" x="{coords[yr]:.1f}" y="{b1+18}">{yr}</text>'])
        if int(yearly.loc[yr]) == max_total:
            p.append(f'<text class="small" text-anchor="middle" x="{coords[yr]:.1f}" y="{b1-bh-7:.1f}">{max_total}</text>')
    p.append('<text class="small" text-anchor="middle" x="580" y="672">Year (top panel: posts by sentiment; bottom panel: all posts)</text>')
    _write_svg(path,p)


def load_eda_data(input_csv=None):
    """Locate and load the cleaned dataset from the project or its parent folder."""
    if input_csv is None:
        candidates = [Path.cwd(), *Path.cwd().parents]
        project_dir = None
        for candidate in candidates:
            if (candidate / 'data' / 'sentiment_cleaned.csv').exists():
                project_dir = candidate
                break
            nested = candidate / 'Feature Exploration'
            if (nested / 'data' / 'sentiment_cleaned.csv').exists():
                project_dir = nested
                break
        if project_dir is None:
            raise FileNotFoundError('Could not locate data/sentiment_cleaned.csv. Run from the Feature Exploration project folder.')
        input_csv = project_dir / 'data' / 'sentiment_cleaned.csv'
    else:
        input_csv = Path(input_csv).resolve()
        project_dir = input_csv.parent.parent
    df = pd.read_csv(input_csv)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='raise')
    return project_dir, df


def plot_sentiment_distribution(df, output_dir):
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    counts=df.groupby('sentiment',observed=True).size().sort_values(ascending=False).rename('posts').to_frame()
    counts['share_pct']=counts.posts/len(df)*100
    counts.to_csv(output_dir/'sentiment_distribution.csv',encoding='utf-8-sig')
    chart=output_dir/'01_sentiment_distribution.svg'
    _distribution_svg(counts,chart)
    return counts,chart


def plot_sentiment_interactions(df, output_dir):
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    summary=df.groupby('sentiment',observed=True).agg(posts=('source_record','size'),
        median_interactions=('total_interactions','median'),mean_interactions=('total_interactions','mean'),
        median_likes=('likes','median'),median_retweets=('retweets','median')).sort_values('posts',ascending=False)
    summary.to_csv(output_dir/'sentiment_interactions.csv',encoding='utf-8-sig')
    chart=output_dir/'02_sentiment_interactions.svg'
    counts=summary[['posts']]
    _interaction_svg(df,counts,chart)
    return summary,chart


def plot_sentiment_over_time(df, output_dir):
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    annual=df.groupby(df.timestamp.dt.year).agg(posts=('source_record','size'),
        first_timestamp=('timestamp','min'),last_timestamp=('timestamp','max')).reset_index(names='year')
    annual['share_pct']=annual.posts/len(df)*100
    annual.to_csv(output_dir/'annual_post_counts.csv',index=False,encoding='utf-8-sig')
    annual_sent=df.assign(year=df.timestamp.dt.year).groupby(['year','sentiment'],observed=True).size().rename('posts').reset_index()
    annual_sent.to_csv(output_dir/'annual_sentiment_counts.csv',index=False,encoding='utf-8-sig')
    chart=output_dir/'03_sentiment_over_time.svg'
    counts=df.groupby('sentiment',observed=True).size().sort_values(ascending=False).rename('posts').to_frame()
    _temporal_svg(df,counts,chart)
    return annual,chart


def run_eda(input_csv, output_dir=None):
    input_csv=Path(input_csv)
    output_dir=Path(output_dir) if output_dir else input_csv.parent.parent/'eda'
    output_dir.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(input_csv)
    df['timestamp']=pd.to_datetime(df['timestamp'], errors='raise')
    assert {'sentiment','timestamp','likes','retweets','total_interactions'}.issubset(df.columns)
    counts,_=plot_sentiment_distribution(df,output_dir)
    summary,_=plot_sentiment_interactions(df,output_dir)
    annual,_=plot_sentiment_over_time(df,output_dir)
    mode=str(counts.index[0]); mode_n=int(counts.iloc[0].posts)
    yr_2023=int(annual.loc[annual.year.eq(2023),'posts'].iloc[0]) if annual.year.eq(2023).any() else None
    common=counts[counts.posts.ge(8)].index
    top_medians=summary.loc[common].sort_values('median_interactions',ascending=False).head(3)
    low_medians=summary.loc[common].sort_values('median_interactions').head(3)
    findings=[
        '# EDA Findings', '',
        f'- The dataset contains **{len(df):,} posts** and **{df.sentiment.nunique()} distinct sentiment labels**. The most frequent label is **{mode}** ({mode_n} posts, {mode_n/len(df)*100:.1f}%). The distribution has a long tail; the 12-label chart groups the remaining labels as Other.',
        f'- Interaction distributions overlap across sentiment labels. Among labels with at least 8 posts, the highest medians are {", ".join(f"{label} ({float(row.median_interactions):g})" for label,row in top_medians.iterrows())}; the lowest are {", ".join(f"{label} ({float(row.median_interactions):g})" for label,row in low_medians.iterrows())}. These are descriptive comparisons, not evidence of statistical significance or causation.',
        f'- Records span {df.timestamp.min():%Y-%m-%d} to {df.timestamp.max():%Y-%m-%d}. Annual coverage is uneven; {yr_2023} posts ({yr_2023/len(df)*100:.1f}%) are dated 2023. The annual trend should be read as the sample’s recorded coverage, not a population-level change over time.',
        '- Source note: the publisher describes this dataset as synthetic, ChatGPT-generated content. The source timezone is unspecified; no timezone conversion was applied.',
        '', '## Files',
        '- `01_sentiment_distribution.svg`: counts and shares for the 12 most frequent labels plus Other.',
        '- `02_sentiment_interactions.svg`: observed interaction boxplots for the 12 most frequent sentiment labels with at least 8 posts.',
        '- `03_sentiment_over_time.svg`: annual counts for the five most frequent labels and total posts per year.',
        '- CSV files contain the underlying frequency, interaction and temporal summaries.',
        '', '## Reproduce',
        'From the `Feature Exploration` directory, run `python eda/eda.py`. The script reads `data/sentiment_cleaned.csv` and refreshes the SVG charts and CSV summaries.',
    ]
    (output_dir/'findings.md').write_text('\n'.join(findings)+'\n',encoding='utf-8')
    return {'rows':len(df),'sentiment_labels':int(df.sentiment.nunique()),'most_common_sentiment':mode,
            'most_common_count':mode_n,'date_min':str(df.timestamp.min()),'date_max':str(df.timestamp.max()),
            'year_2023_count':yr_2023,'chart_files':3,'output_dir':str(output_dir)}

if __name__=='__main__':
    base=Path(__file__).resolve().parent.parent
    input_csv=base/'data/processed/sentiment_cleaned.csv'
    result=run_eda(input_csv,base/'generated/eda_core')
    print(json.dumps(result,indent=2))
