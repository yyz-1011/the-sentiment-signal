"""Reproduce the bootcamp preprocessing and descriptive EDA. No network access required.

Usage: python preprocess_and_analyze.py [--input PATH] [--output-dir PATH]
Dependencies: pandas, numpy, matplotlib. Python 3.10+.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import html
import json
import platform
import re
import unicodedata

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input', type=Path, default=HERE.parent / 'data/raw/sentimentdataset.csv')
parser.add_argument('--output-dir', type=Path, default=HERE.parent / 'generated/cleaning')
args = parser.parse_args()
OUT = args.output_dir.resolve()
for folder in [OUT, OUT / 'tables', OUT / 'figures']:
    folder.mkdir(parents=True, exist_ok=True)
raw = pd.read_csv(args.input)
source_hash = hashlib.sha256(args.input.read_bytes()).hexdigest()
df = raw.copy()
changes = []
for col in df.select_dtypes('object'):
    original = df[col].copy()
    df[col] = df[col].map(lambda v: re.sub(r'\s+', ' ', unicodedata.normalize('NFC', v)).strip() if isinstance(v, str) else v)
    df[col] = df[col].replace('', pd.NA)
    changes.append({'column': col, 'rows_changed': int((original.fillna('') != df[col].fillna('')).sum()),
                    'unique_before': int(original.nunique()), 'unique_after': int(df[col].nunique())})
pd.DataFrame(changes).to_csv(OUT / 'tables/normalization_log.csv', index=False)

# Export indices are kept as provenance, but excluded when identifying repeated observations.
df.insert(0, 'source_record', np.arange(2, len(df) + 2))
df = df.rename(columns={'Unnamed: 0.1': 'source_index_1', 'Unnamed: 0': 'source_index_2'})
keys = [c for c in df if c not in ['source_record', 'source_index_1', 'source_index_2']]
repeated = df.duplicated(subset=keys, keep='first')
first_record = df.groupby(keys, dropna=False)['source_record'].transform('min')
removed = df.loc[repeated].copy()
removed['duplicate_of_source_record'] = first_record[repeated]
removed.to_csv(OUT / 'removed_duplicate_records.csv', index=False)
df = df.loc[~repeated].copy()
df.columns = [re.sub(r'(?<!^)(?=[A-Z])', '_', c).lower() if c not in ['source_record', 'source_index_1', 'source_index_2'] else c for c in df.columns]
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
date_mismatches = {}
for col in ['year', 'month', 'day', 'hour']:
    date_mismatches[col] = int((pd.to_numeric(df[col], errors='coerce') != getattr(df.timestamp.dt, col)).sum())
    df[col] = getattr(df.timestamp.dt, col).astype('Int64')
invalid_numeric = {}
for col in ['likes', 'retweets']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    invalid_numeric[col] = int((df[col].isna() | (df[col] < 0) | (df[col] % 1 != 0)).sum())
    if invalid_numeric[col] == 0:
        df[col] = df[col].astype('Int64')
df['text_lower'] = df.text.str.lower()
df['text_group_id'] = df.text_lower.map(lambda x: hashlib.sha256(x.encode('utf-8')).hexdigest()[:16])
df['repeated_text'] = df.text_group_id.duplicated(keep=False)
df['text_char_count'] = df.text.str.len()
df['text_word_count'] = df.text.str.split().str.len()
df['total_interactions'] = df.likes + df.retweets
df['year_month'] = df.timestamp.dt.strftime('%Y-%m')
df['weekday'] = df.timestamp.dt.day_name()
df['hashtag_list'] = df.hashtags.map(lambda s: sorted(set(re.findall(r'#(\w+)', s.lower()))) if isinstance(s, str) else [])
df['hashtag_count'] = df.hashtag_list.str.len()
export = df.copy()
export['hashtag_list'] = export.hashtag_list.map(lambda v: json.dumps(v, ensure_ascii=False))
export.to_csv(OUT / 'sentiment_cleaned.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')

tables = {}
def save(name, frame):
    tables[name] = frame
    frame.to_csv(OUT / 'tables' / (name + '.csv'), index=False)
    return frame

n = len(df)
sentiment = df.sentiment.value_counts().rename_axis('sentiment').reset_index(name='posts')
sentiment['share_pct'] = sentiment.posts / n * 100
save('sentiment_distribution', sentiment)
review = sentiment.copy()
review['proposed_broad_label'] = ''
review['review_notes'] = ''
review_path = OUT / 'sentiment_label_review_template.csv'
if not review_path.exists():
    review.to_csv(review_path, index=False)
def group_summary(col):
    x = df.groupby(col, dropna=False).agg(posts=('source_record', 'size'), mean_likes=('likes', 'mean'),
        median_likes=('likes', 'median'), mean_retweets=('retweets', 'mean'), median_retweets=('retweets', 'median'),
        mean_total_interactions=('total_interactions', 'mean'), median_total_interactions=('total_interactions', 'median'))
    x['share_pct'] = x.posts / n * 100
    return x.reset_index().sort_values('posts', ascending=False)
platforms = save('platform_summary', group_summary('platform'))
countries = save('country_summary', group_summary('country'))
save('sentiment_engagement', group_summary('sentiment'))
years = save('year_summary', group_summary('year').sort_values('year'))
months = save('year_month_summary', group_summary('year_month').sort_values('year_month'))
save('hour_summary', group_summary('hour').sort_values('hour'))
save('weekday_summary', group_summary('weekday'))
save('platform_sentiment_counts', pd.crosstab(df.platform, df.sentiment).reset_index())
save('platform_sentiment_share_pct', pd.crosstab(df.platform, df.sentiment, normalize='index').mul(100).reset_index())
save('year_sentiment_counts', pd.crosstab(df.year, df.sentiment).reset_index())
save('year_sentiment_share_pct', pd.crosstab(df.year, df.sentiment, normalize='index').mul(100).reset_index())
save('country_sentiment_counts', pd.crosstab(df.country, df.sentiment).reset_index())
save('country_sentiment_share_pct', pd.crosstab(df.country, df.sentiment, normalize='index').mul(100).reset_index())
tags = df[['source_record', 'platform', 'sentiment', 'total_interactions', 'hashtag_list']].explode('hashtag_list').dropna(subset=['hashtag_list']).rename(columns={'hashtag_list': 'hashtag'})
tag_stats = tags.groupby('hashtag').agg(posts=('source_record', 'size'), mean_total_interactions=('total_interactions', 'mean'), median_total_interactions=('total_interactions', 'median')).reset_index().sort_values(['posts', 'hashtag'], ascending=[False, True])
tag_stats['post_share_pct'] = tag_stats.posts / n * 100
save('hashtag_summary', tag_stats)
save('post_hashtags', tags)
save('numeric_summary', df[['likes', 'retweets', 'total_interactions', 'text_char_count', 'text_word_count', 'hashtag_count']].describe().T.reset_index(names='feature'))
save('repeated_text_records', df.loc[df.repeated_text, ['source_record', 'text_group_id', 'text', 'sentiment', 'platform', 'timestamp']])
quality = pd.DataFrame({'column': df.columns, 'missing': df.isna().sum().values, 'unique_nonmissing': [df[c].astype(str).nunique() for c in df]})
save('column_quality', quality)
metrics = ['likes', 'retweets', 'total_interactions', 'text_word_count', 'hashtag_count']
correlations = []
for i, a in enumerate(metrics):
    for b in metrics[i + 1:]:
        pair = df[[a, b]].astype(float).dropna()
        constant = pair[a].nunique() < 2 or pair[b].nunique() < 2
        correlations.append({'feature_1': a, 'feature_2': b, 'n': len(pair),
            'pearson_r': np.nan if constant else pair[a].corr(pair[b]),
            'spearman_rho': np.nan if constant else pair[a].rank().corr(pair[b].rank()),
            'status': 'undefined: constant feature' if constant else 'computed'})
save('correlations', pd.DataFrame(correlations))
# Quantify the effect of deduplication on platform comparisons.
raw_platform = raw.Platform.str.strip().value_counts()
sensitivity = platforms[['platform', 'posts', 'mean_total_interactions']].rename(columns={'posts': 'deduplicated_posts', 'mean_total_interactions': 'deduplicated_mean_interactions'})
sensitivity['all_rows_posts'] = sensitivity.platform.map(raw_platform)
raw_engagement = raw.assign(platform=raw.Platform.str.strip(), interactions=raw.Likes + raw.Retweets).groupby('platform').interactions.mean()
sensitivity['all_rows_mean_interactions'] = sensitivity.platform.map(raw_engagement)
save('duplicate_sensitivity', sensitivity)

pearson = float(df.likes.astype(float).corr(df.retweets.astype(float)))
rho = float(df.likes.astype(float).rank().corr(df.retweets.astype(float).rank()))
double_likes = int((df.likes == 2 * df.retweets).sum())
audit = {
    'input_path': str(args.input.resolve()), 'input_sha256': source_hash,
    'raw_rows': len(raw), 'raw_columns': len(raw.columns), 'clean_rows': n,
    'removed_duplicate_rows': int(repeated.sum()), 'duplicate_definition': 'All 13 original substantive columns after NFC/whitespace normalization; export indices excluded; keep first occurrence.',
    'normalized_sentiment_labels': int(df.sentiment.nunique()), 'single_observation_labels': int((sentiment.posts == 1).sum()),
    'labels_with_fewer_than_5_posts': int((sentiment.posts < 5).sum()), 'posts_in_labels_with_fewer_than_5_posts': int(sentiment.loc[sentiment.posts < 5, 'posts'].sum()),
    'date_min': str(df.timestamp.min()), 'date_max': str(df.timestamp.max()), 'invalid_timestamps': int(df.timestamp.isna().sum()),
    'date_component_mismatches': date_mismatches, 'invalid_engagement_values': invalid_numeric,
    'raw_missing_cells': int(raw.isna().sum().sum()), 'clean_missing_cells': int(df.isna().sum().sum()),
    'repeated_text_rows': int(df.repeated_text.sum()), 'repeated_text_groups': int(df.loc[df.repeated_text, 'text_group_id'].nunique()),
    'conflicting_label_text_groups': int((df.groupby('text_group_id').sentiment.nunique() > 1).sum()),
    'likes_retweets_pearson': pearson, 'likes_retweets_spearman': rho,
    'likes_equals_twice_retweets_posts': double_likes,
    'runtime': {'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
}
(OUT / 'data_quality_audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.titleweight': 'bold', 'figure.facecolor': 'white', 'axes.labelcolor': '#34445b'})
figures = []
def finish(name, fig):
    fig.text(.99, .01, 'Synthetic data • Deduplicated posts • Descriptive only', ha='right', color='#657286', fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, 1))
    fig.savefig(OUT / 'figures' / (name + '.png'), dpi=165, bbox_inches='tight')
    plt.close(fig)
    figures.append(name)

fig, ax = plt.subplots(figsize=(10, 6))
s = sentiment.head(15).iloc[::-1]
ax.barh(s.sentiment, s.posts, color='#2865a7')
ax.set(title='Most frequent original sentiment labels', xlabel='Posts')
finish('01_top_sentiments', fig)
fig, axs = plt.subplots(1, 2, figsize=(11, 5))
axs[0].bar(platforms.platform, platforms.posts, color='#2865a7')
axs[0].set(title='Posts by platform', ylabel='Posts')
for p, g in df.groupby('platform'):
    axs[1].scatter([p] * len(g), g.total_interactions, alpha=.10, s=14, color='#2865a7')
axs[1].plot(platforms.platform, platforms.median_total_interactions, 'D', color='#cb5b32', label='Median')
axs[1].set(title='Recorded interactions per post', ylabel='Likes + retweets (count)')
axs[1].legend()
finish('02_platforms', fig)
fig, axs = plt.subplots(1, 2, figsize=(12, 5))
axs[0].bar(years.year.astype(str), years.posts, color='#2865a7')
axs[0].tick_params(axis='x', rotation=60)
axs[0].set(title='Uneven annual coverage', ylabel='Posts', xlabel='Year')
latest = int(df.year.max())
year_data = df[df.year == latest]
year_labels = year_data.groupby('month').size().reindex(range(1, 13))
axs[1].bar(year_labels.index, year_labels.values, color='#2f8b80')
axs[1].set(title=f'{latest} monthly coverage', xlabel='Month', ylabel='Posts', xticks=range(1, 13))
axs[1].set_ylim(0, year_labels.max() * 1.25)
axs[1].text(.02, .96, 'Missing months left blank; final year is partial', transform=axs[1].transAxes, va='top', fontsize=9)
finish('03_temporal_coverage', fig)
fig, ax = plt.subplots(figsize=(10, 6))
c = countries.head(10).iloc[::-1]
ax.barh(c.country, c.posts, color='#2f8b80')
ax.set(title='Geographic coverage: top 10 location labels', xlabel='Posts')
finish('04_geographic_coverage', fig)
fig, ax = plt.subplots(figsize=(10, 6))
h = tag_stats.head(15).iloc[::-1]
ax.barh('#' + h.hashtag, h.posts, color='#2865a7')
ax.set(title='Most common hashtags', xlabel='Posts containing hashtag (once per post)')
finish('05_hashtags', fig)
fig, axs = plt.subplots(1, 2, figsize=(11, 5))
axs[0].hist(df.likes.astype(float), bins=18, color='#2865a7', alpha=.85, label='Likes')
axs[0].hist(df.retweets.astype(float), bins=18, color='#2f8b80', alpha=.65, label='Retweets')
axs[0].set(title='Engagement distributions', xlabel='Recorded count', ylabel='Posts')
axs[0].legend()
axs[1].scatter(df.retweets, df.likes, alpha=.25, color='#2865a7')
axs[1].set(title=f'Likes and retweets: Pearson r = {pearson:.4f}', xlabel='Retweets', ylabel='Likes')
finish('06_engagement', fig)
toplabels = sentiment.head(8).sentiment.tolist()
ct = pd.crosstab(df.platform, df.sentiment)
display = ct.reindex(columns=toplabels).copy()
display['Other labels'] = ct.sum(axis=1) - display.sum(axis=1)
display = display.div(ct.sum(axis=1), axis=0) * 100
fig, ax = plt.subplots(figsize=(11, 5))
display.plot.barh(stacked=True, ax=ax, colormap='tab20', width=.6)
ax.set(title='Label mix within each platform', xlabel='Share of platform posts (%)', ylabel='Platform', xlim=(0, 100))
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)
finish('07_platform_sentiment_mix', fig)
fig, ax = plt.subplots(figsize=(10, 5))
eng = tables['sentiment_engagement'].query('posts >= 10').sort_values('median_total_interactions')
ax.barh(eng.sentiment + ' (n=' + eng.posts.astype(str) + ')', eng.median_total_interactions, color='#2f8b80')
ax.set(title='Median interactions by sentiment, groups with at least 10 posts', xlabel='Median likes + retweets')
finish('08_sentiment_engagement', fig)

# Human-readable dictionary for every exported field.
definitions = {
 'source_record': '1-based logical CSV record number including header; provenance only.',
 'source_index_1': 'Original Unnamed: 0.1 export index; provenance only.',
 'source_index_2': 'Original Unnamed: 0 export index; provenance only.',
 'text': 'NFC Unicode and whitespace-normalized post; retains case, emoji, punctuation, hashtags and negation.',
 'sentiment': 'Publisher-supplied label, whitespace normalized. No synonyms merged and no inferred polarity.',
 'timestamp': 'Parsed source date/time; timezone unspecified, no UTC conversion.',
 'user': 'Normalized synthetic user identifier; case preserved.',
 'platform': 'Normalized source platform, including Twitter as named in the source.',
 'hashtags': 'Whitespace-normalized source hashtag string.',
 'retweets': 'Source retweet count, also present for non-Twitter platforms; comparability unverified.',
 'likes': 'Source like count.',
 'country': 'Normalized source location label; Scotland and UK remain separate to avoid silently changing geography.',
 'year': 'Year recomputed from timestamp.', 'month': 'Month recomputed from timestamp, 1–12.',
 'day': 'Day of month recomputed from timestamp.', 'hour': 'Hour recomputed from timestamp, timezone unknown.',
 'text_lower': 'Lowercase text feature retaining punctuation/emoji/negation; not a final model vocabulary.',
 'text_group_id': 'First 16 hex characters of SHA-256 of text_lower; group identical text together when splitting models.',
 'repeated_text': 'True for every member of a repeated text group after full-record deduplication.',
 'text_char_count': 'Character count of normalized text.', 'text_word_count': 'Whitespace-separated token count, includes punctuation/emoji tokens.',
 'total_interactions': 'Likes + retweets; count proxy, not engagement rate. No impressions/follower denominator available.',
 'year_month': 'Calendar year-month from timestamp.', 'weekday': 'Day name from timestamp; timezone unspecified.',
 'hashtag_list': 'JSON array of unique lowercased hashtag tokens per post, extracted from Hashtags only.',
 'hashtag_count': 'Number of unique extracted hashtags in the post.'}
save('data_dictionary', pd.DataFrame([{'field': c, 'dtype_in_memory': str(df[c].dtype), 'definition': definitions[c]} for c in df]))

source_url = 'https://www.kaggle.com/datasets/kashishparmar02/social-media-sentiments-analysis-dataset/data'
source_note = ('Publisher metadata explicitly identifies the dataset as generated by ChatGPT to simulate social media content. '
               'It does not represent real individuals or events. A metadata snapshot is saved in sources/kaggle_metadata.json. '
               'The data card describes the fields but does not establish a sampling frame, annotation protocol or timestamp timezone.')
findings = [
 f'The input has {len(raw):,} rows and {len(raw.columns)} columns. Full-record deduplication removes {repeated.sum():,} rows ({repeated.mean():.1%}), leaving {n:,} posts.',
 f'Trimming whitespace reduces sentiment values from {raw.Sentiment.nunique()} to {df.sentiment.nunique()}. There are {audit["single_observation_labels"]} labels with one post and {audit["labels_with_fewer_than_5_posts"]} labels with fewer than five posts ({audit["posts_in_labels_with_fewer_than_5_posts"]} posts in total).',
 'The leading labels are ' + ', '.join(f'{r.sentiment}: {r.posts} ({r.share_pct:.1f}%)' for r in sentiment.head(3).itertuples()) + '. These labels are distinct; Positive is not the total positive-polarity share.',
 'Platform coverage is ' + ', '.join(f'{r.platform}: {r.posts} ({r.share_pct:.1f}%)' for r in platforms.itertuples()) + '.',
 f'Posts range from {df.timestamp.min():%Y-%m-%d} through {df.timestamp.max():%Y-%m-%d}. {latest} contributes {len(year_data):,} posts ({len(year_data)/n:.1%}) and ends in October. Uneven, incomplete coverage prevents a defensible claim about seasonality or population sentiment trends.',
 f'There are {df.country.nunique()} location labels. The top five contain {countries.head(5).posts.sum()/n:.1%} of posts. The source mixes geographic levels, for example Scotland and UK; country comparisons need explicit harmonization decisions.',
 f'Likes and retweets are nearly redundant: Pearson r={pearson:.4f}, Spearman rho={rho:.4f}; {double_likes}/{n} posts ({double_likes/n:.1%}) have likes exactly twice retweets. These generated metrics should not be treated as independent evidence of popularity.',
 f'Every retained post has exactly two extracted hashtags. Hashtag count is constant and its correlations are undefined; hashtag identity still varies across posts.',
 f'After record deduplication, {audit["repeated_text_rows"]} rows form {audit["repeated_text_groups"]} repeated text groups. They are retained because other fields differ. Split model data by text_group_id to prevent identical text appearing in both training and evaluation.',
 f'No raw missing cells were found. Parsed timestamps, engagement count validity and year/month/day/hour consistency pass for this file. See the quality audit for exact checks.'
]
method = [
 'Preserve the input CSV. Normalize Unicode to NFC and collapse/trim whitespace in string fields; preserve sentiment semantics and country labels.',
 'Exclude the two export indices from duplicate detection. Keep the earliest input occurrence of each identical substantive record; save every removed row and its retained source record.',
 'Parse timestamps without guessing a timezone. Validate nonnegative integer engagement counts and compare supplied calendar parts with parsed dates, then recompute those parts.',
 'Retain expressive text features (emoji, punctuation and negation). Add lowercase text, text lengths, repeated-text grouping, unique lowercase hashtag tokens and total interactions.',
 f'Compute summaries on the {n} retained posts. Show group sizes and both means and medians. Hashtags are counted at most once per post, and percentages can sum above 100% because posts have multiple hashtags.',
 'Use full original sentiment labels for EDA. Other labels in the stacked chart is a display remainder, not a training class. No stemming, stopword deletion, balancing, vectorizer fitting or model training is performed.'
]
next_steps = [
 'Define the target with the group: polarity (positive/negative/neutral) or a small set of emotion families. These are different tasks. Review the provided label template with at least two reviewers, record rules and disagreements, and manually inspect text-label consistency.',
 'Avoid a 191-class supervised model on 710 posts. Singletons cannot appear in both training and held-out evaluation. If broader labels are approved, split by repeated-text group before fitting TF-IDF and a simple classifier; compare against a majority-class baseline and report macro-F1 plus per-class support.',
 'Fit text processing and any feature selection on training data only. Keep supplied sentiment and any sentiment-derived feature out of predictors. Use hashtags only if they will be available at prediction time, and compare a text-only model with a version that removes explicit hashtag cues.',
 'For exploratory comparisons, retain counts alongside percentages, inspect small groups and use the duplicate-sensitivity table. A minimum group size such as 10 is a display filter, not proof of statistical reliability.',
 'Use a documented real-world, independently annotated dataset if the final project aims to make claims about actual public sentiment, geographic differences or platform behavior.'
]
def table_html(frame, limit=20):
    return frame.head(limit).to_html(index=False, border=0, float_format=lambda x: f'{x:,.2f}', escape=True)
parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
 '<title>Social media sentiment: initial analysis</title><style>body{font:16px/1.65 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#243349;background:#f4f6fa;margin:0}main{max-width:1100px;margin:auto;background:white;padding:42px}h1{font-size:36px;line-height:1.2}h2{margin-top:38px;color:#173b61}a{color:#1765a1}.notice{background:#fff4df;padding:18px;border-left:4px solid #cb7932}li{margin:10px 0}table{border-collapse:collapse;font-size:14px;width:100%}td,th{padding:9px;border-bottom:1px solid #dae1e9;text-align:right}td:first-child,th:first-child{text-align:left}th{background:#edf2f8}figure{margin:30px 0}img{max-width:100%;height:auto}.scroll{overflow-x:auto}code{overflow-wrap:anywhere}@media(max-width:650px){main{padding:20px}h1{font-size:28px}}</style><main>',
 '<p>DATA SCIENCE BOOTCAMP · INITIAL ANALYSIS · 20 OCTOBER 2026</p><h1>Social media sentiment analysis</h1>',
 f'<p class="notice"><b>Synthetic dataset.</b> {html.escape(source_note)}</p>',
 '<h2>Initial findings</h2><ol>' + ''.join('<li>'+html.escape(x)+'</li>' for x in findings) + '</ol>',
 '<h2>Preprocessing decisions</h2><ol>' + ''.join('<li>'+html.escape(x)+'</li>' for x in method) + '</ol>',
 '<h2>Platform and engagement overview</h2><p>Interactions are recorded counts, not rates. Retweets are populated on all platforms, so cross-platform comparability is unverified.</p><div class="scroll">' + table_html(platforms) + '</div>',
 '<h2>Visual exploration</h2>']
captions = [
 'The top 15 original labels show fragmentation. Synonyms such as Happy and Happiness remain separate until a reviewed mapping is approved.',
 'Platform post counts and recorded interaction distributions. Orange diamonds indicate medians; overlaid observations can overlap.',
 'Annual and latest-year monthly counts show collection coverage. Blank months are not evidence of zero real-world activity.',
 'The top 10 source location labels show concentration. Smaller groups should not be used to rank real-world countries.',
 'Common hashtags are topics in this dataset. Frequency alone does not establish a hashtag trend or a causal engagement effect.',
 'Engagement fields have an unusually deterministic relationship consistent with the disclosed synthetic origin.',
 'Within-platform percentages use all posts on each platform as the denominator. The remaining labels are combined only for visualization.',
 'Sentiment engagement comparisons retain groups with at least 10 posts and display sample sizes. Differences are descriptive and can reflect label, time and platform composition.'
]
for name, caption in zip(figures, captions):
    encoded = base64.b64encode((OUT / 'figures' / (name + '.png')).read_bytes()).decode()
    parts.append(f'<figure><img src="data:image/png;base64,{encoded}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>')
parts += ['<h2>Next steps for the group</h2><ol>' + ''.join('<li>'+html.escape(x)+'</li>' for x in next_steps) + '</ol>',
 '<h2>Files and reproducibility</h2><p>Use sentiment_cleaned.csv for exploration. The tables folder contains complete summaries, the data dictionary and normalization log. The figures folder contains eight PNG charts. removed_duplicate_records.csv provides the removal audit; data_quality_audit.json contains validation metrics and the input SHA-256.</p>',
 '<p>To regenerate: install requirements.txt and run <code>python preprocess_and_analyze.py</code> from this folder. The default input is the original CSV in the parent folder. Existing generated outputs will be refreshed; the source CSV is read only.</p>',
 f'<p>Source: <a href="{source_url}">Kashish Parmar, Social Media Sentiments Analysis Dataset, Kaggle</a>. Publisher metadata accessed 20 October 2026. Analysis is based on the local file; no data rows were downloaded or replaced.</p>',
 f'<p>Input SHA-256: <code>{source_hash}</code></p></main></html>']
(OUT / 'initial_analysis_report.html').write_text('\n'.join(parts), encoding='utf-8')
md = '# Social media sentiment: initial analysis\n\n' + source_note + '\n\n## Findings\n\n' + '\n'.join('- '+x for x in findings)
md += '\n\n## Preprocessing\n\n' + '\n'.join('- '+x for x in method)
md += '\n\n## Charts\n\n' + '\n\n'.join(f'![{caption}](figures/{name}.png)\n\n{caption}' for name, caption in zip(figures, captions))
md += '\n\n## Recommended next steps\n\n' + '\n'.join('- '+x for x in next_steps)
md += f'\n\nSource: [Kaggle dataset]({source_url}). See sources/kaggle_metadata.json for the synthetic-origin disclosure.\n'
(OUT / 'initial_analysis_report.md').write_text(md, encoding='utf-8')
(OUT / 'requirements.txt').write_text(f'pandas=={pd.__version__}\nnumpy=={np.__version__}\nmatplotlib=={matplotlib.__version__}\n', encoding='utf-8')
(OUT / 'README.md').write_text('''# Bootcamp sentiment analysis outputs

Open **initial_analysis_report.html** for the self-contained report with eight charts.
Use **sentiment_cleaned.csv** as the prepared data. Original input remains in the parent folder.
Complete **sentiment_label_review_template.csv** only after agreeing on a target taxonomy.
The script preserves an existing review template on rerun. It does not consume its proposed labels.

## Reproduce

```bash
python -m pip install -r requirements.txt
python preprocess_and_analyze.py
```

Optional arguments: `--input /path/to/source.csv --output-dir /path/to/results`.
The script is offline. The saved Kaggle metadata supplies provenance and field context.
CSV columns are documented in tables/data_dictionary.csv. Hashtag arrays are JSON strings.
Do not use source record numbers or export indices as model features.
All results describe synthetic examples, not measured social media behavior.
''', encoding='utf-8')

# Reconciliation checks appropriate to the data transformation.
assert len(raw) == len(df) + len(removed)
assert not df.duplicated(subset=['text', 'sentiment', 'timestamp', 'user', 'platform', 'hashtags', 'retweets', 'likes', 'country', 'year', 'month', 'day', 'hour']).any()
assert df.source_record.is_unique
assert platforms.posts.sum() == countries.posts.sum() == sentiment.posts.sum() == years.posts.sum() == n
assert tags.groupby('source_record').size().sum() == df.hashtag_count.sum()
assert hashlib.sha256(args.input.read_bytes()).hexdigest() == source_hash
reloaded = pd.read_csv(OUT / 'sentiment_cleaned.csv')
assert len(reloaded) == n
assert reloaded.hashtag_list.map(json.loads).str.len().sum() == len(tags)
assert (reloaded.total_interactions == reloaded.likes + reloaded.retweets).all()
print(json.dumps(audit, indent=2))
print('Saved report, cleaned CSV, audits, tables and eight charts to', OUT)
