# Cell 2
from pathlib import Path
import json, hashlib, re
import numpy as np
import pandas as pd
from IPython.display import display

BASE=Path.cwd()
if not (BASE/'data/sentiment_cleaned.csv').exists():
    BASE=BASE/'Feature Exploration'
INPUT=BASE/'data/sentiment_cleaned.csv'
EXPECTED_INPUT_SHA256='4c38dc7cc2a8a06a96c13e989541c024ce31e9ee6af890a5f429fbe1f892ec6a'
input_hash=hashlib.sha256(INPUT.read_bytes()).hexdigest()
assert input_hash==EXPECTED_INPUT_SHA256, 'Input changed. Review the snapshot and update the documented source before refreshing.'
source=pd.read_csv(INPUT)
df=source.copy(deep=True)
(BASE/'tables').mkdir(exist_ok=True)
def save_table(name,frame):
    frame.to_csv(BASE/'tables'/f'{name}.csv',index=False)
    return frame
print('Input shape:',source.shape)
print('Source SHA256:',input_hash)
display(source.head(3))

# Cell 4
before_types=source.dtypes.astype(str)
df['timestamp']=pd.to_datetime(df.timestamp,format='%Y-%m-%d %H:%M:%S',errors='raise')
integer_fields=['source_record','source_index_1','source_index_2','likes','retweets','year','month','day','hour',
                'text_char_count','text_word_count','total_interactions','hashtag_count']
for col in integer_fields:
    values=pd.to_numeric(df[col],errors='raise')
    assert values.mod(1).eq(0).all()
    df[col]=values.astype('Int64')
bool_map={'true':True,'false':False}
parsed_bool=df.repeated_text.astype(str).str.lower().map(bool_map)
assert parsed_bool.notna().all()
df['repeated_text']=parsed_bool.astype('boolean')
for col in ['sentiment','platform','country','weekday']:
    df[col]=df[col].astype('category')
df['hashtag_list']=df.hashtag_list.map(json.loads)
assert df.hashtag_list.map(lambda x:isinstance(x,list) and all(isinstance(t,str) for t in x)).all()
inventory=pd.DataFrame({
    'feature':source.columns,'csv_inferred_dtype':before_types.values,
    'prepared_dtype':[str(df[c].dtype) for c in source],
    'missing_cells':source.isna().sum().values,
    'unique_values':[source[c].nunique(dropna=True) for c in source],
})
inventory['unique_share_pct']=inventory.unique_values/len(df)*100
save_table('feature_inventory',inventory)
display(inventory)

# Cell 6
query_example=df.loc[(df.platform=='Instagram') & (df.total_interactions>=75),
    ['source_record','platform','text','likes','retweets','total_interactions']]
query_example=query_example.sort_values(['total_interactions','source_record'],ascending=[False,True])
save_table('filter_sort_example',query_example)
display(query_example.head(8))
hours=df.hour.to_numpy(dtype=int)
df=df.assign(
    hour_period=np.select([hours<6,hours<12,hours<18],['00–05','06–11','12–17'],default='18–23'),
    is_weekend=np.isin(df.timestamp.dt.weekday.to_numpy(),[5,6]),
    log1p_interactions=np.log1p(df.total_interactions.to_numpy(dtype=float)),
    has_url=df.text.str.contains(r'https?://|www\.',case=False,regex=True),
    has_mention=df.text.str.contains(r'(?<!\w)@\w+',regex=True),
    negation_cue_count=df.text.str.count(r"(?i)\b(?:no|not|never|neither|nor|cannot)\b|n['’]t\b"),
)
derived_cols=['hour_period','is_weekend','log1p_interactions','has_url','has_mention','negation_cue_count']
print('Added exploratory columns:',derived_cols)
display(df[['source_record','hour']+derived_cols].head(8))

# Cell 9
measured=['likes','retweets','total_interactions','text_char_count','text_word_count','hashtag_count']
summary=[]
for col in measured:
    x=df[col].to_numpy(dtype=float)
    q1,median,q3=np.quantile(x,[.25,.5,.75],method='linear')
    summary.append({'feature':col,'count':len(x),'minimum':np.min(x),'q1':q1,'median':median,'q3':q3,
                    'maximum':np.max(x),'mean':np.mean(x),'sample_std':np.std(x,ddof=1),
                    'zero_count':np.count_nonzero(x==0),'unique_values':np.unique(x).size})
numeric_profile=save_table('numeric_profile',pd.DataFrame(summary))
for row in summary:
    assert np.isclose(row['mean'],df[row['feature']].mean())
    assert np.isclose(row['sample_std'],df[row['feature']].std(ddof=1))
display(numeric_profile.round(3))
numeric_candidates=measured+['log1p_interactions','negation_cue_count']
constants=pd.DataFrame([{'feature':c,'constant_value':str(df[c].iloc[0]),'unique_values':df[c].nunique()}
                       for c in numeric_candidates+['has_url','has_mention','is_weekend','hour_period'] if df[c].nunique()==1])
save_table('constant_feature_flags',constants)
display(constants)

# Cell 11
counts={}
for col in ['sentiment','platform','country','weekday','hour_period']:
    freq=df[col].value_counts(dropna=False).rename_axis(col).reset_index(name='posts')
    freq['share_pct']=freq.posts/len(df)*100
    assert freq.posts.sum()==len(df)
    counts[col]=save_table(col+'_value_counts',freq)
category_summary=save_table('category_summary',pd.DataFrame([
    {'feature':c,'unique_values':df[c].nunique(),'most_frequent_value':str(counts[c].iloc[0,0]),
     'most_frequent_posts':int(counts[c].iloc[0].posts)} for c in counts]))
platform_aggregation=df.groupby('platform',observed=True).agg(
    posts=('source_record','size'),mean_likes=('likes','mean'),median_likes=('likes','median'),
    mean_retweets=('retweets','mean'),median_retweets=('retweets','median'),
    median_interactions=('total_interactions','median')).reset_index()
save_table('platform_aggregation_example',platform_aggregation)
assert platform_aggregation.posts.sum()==len(df)
assert np.isclose((platform_aggregation.mean_likes*platform_aggregation.posts).sum(),df.likes.sum())
cross=pd.crosstab(df.platform,df.country)
save_table('platform_country_crosstab',cross.reset_index())
assert cross.to_numpy().sum()==len(df)
display(category_summary)
display(platform_aggregation.round(2))
display(cross.iloc[:,:6])
print('Crosstab preview shows six location columns; the exported table includes all locations.')

# Cell 13
coverage=df.groupby(df.timestamp.dt.year).agg(posts=('source_record','size'),
    first_timestamp=('timestamp','min'),last_timestamp=('timestamp','max')).reset_index(names='year')
save_table('annual_coverage',coverage)
user_frequency=df.groupby('user',observed=True).size().rename('posts').reset_index().sort_values(['posts','user'],ascending=[False,True])
save_table('user_post_counts',user_frequency)
repeated=df.loc[df.repeated_text,['source_record','text_group_id','text','sentiment','platform','timestamp']]
save_table('repeated_text_records',repeated)
tags=df[['source_record','hashtag_list']].explode('hashtag_list').rename(columns={'hashtag_list':'hashtag'})
assert tags.hashtag.notna().all()
assert not tags.duplicated(['source_record','hashtag']).any()
tags=tags.merge(df[['source_record','platform']],on='source_record',how='left',validate='many_to_one')
save_table('post_hashtags_long',tags)
tag_frequency=tags.hashtag.value_counts().rename_axis('hashtag').reset_index(name='posts')
tag_frequency['post_share_pct']=tag_frequency.posts/len(df)*100
save_table('hashtag_post_counts',tag_frequency)
support_bands=pd.cut(counts['sentiment'].posts,bins=[0,1,4,9,np.inf],labels=['1','2–4','5–9','10+'])
label_support=counts['sentiment'].assign(support_band=support_bands).groupby('support_band',observed=False).agg(
    labels=('sentiment','size'),posts=('posts','sum')).reset_index()
save_table('label_support_bands',label_support)
diagnostics=pd.DataFrame([
    {'measure':'distinct_users','value':df.user.nunique()},
    {'measure':'distinct_text_groups','value':df.text_group_id.nunique()},
    {'measure':'repeated_text_rows','value':int(df.repeated_text.sum())},
    {'measure':'repeated_text_groups','value':df.loc[df.repeated_text,'text_group_id'].nunique()},
    {'measure':'distinct_hashtags','value':tag_frequency.hashtag.nunique()},
    {'measure':'post_hashtag_rows','value':len(tags)},
    {'measure':'url_flagged_posts','value':int(df.has_url.sum())},
    {'measure':'mention_flagged_posts','value':int(df.has_mention.sum())},
    {'measure':'posts_with_listed_negation_cues','value':int(df.negation_cue_count.gt(0).sum())},
])
save_table('text_and_identifier_diagnostics',diagnostics)
display(diagnostics)
display(coverage)
display(label_support)

# Cell 15
original_dictionary=pd.read_csv(BASE/'data/input_data_dictionary.csv')
definitions=original_dictionary.set_index('field').definition.to_dict()
definitions.update({
    'hour_period':'Source hour intervals: 00–05, 06–11, 12–17 or 18–23. Timezone unknown.',
    'is_weekend':'True when timestamp weekday is Saturday or Sunday. NumPy membership operation.',
    'log1p_interactions':'Natural log of 1 + likes + retweets. NumPy numeric transformation for exploration only.',
    'has_url':'True for text matching https?:// or www. (case insensitive). Limited lexical pattern.',
    'has_mention':'True for an at-sign followed by word characters outside a word. Limited lexical pattern.',
    'negation_cue_count':"Count of no, not, never, neither, nor, cannot or n’t contractions. Limited lexical pattern.",
})
data_dictionary=pd.DataFrame([{'feature':c,'role':'Source or previously derived' if c in source else 'New exploration feature',
    'dtype_in_memory':str(df[c].dtype),'definition':definitions[c]} for c in df])
save_table('exploration_data_dictionary',data_dictionary)
exported=df.copy()
exported['hashtag_list']=exported.hashtag_list.map(lambda x:json.dumps(x,ensure_ascii=False))
exported.to_csv(BASE/'data/posts_feature_exploration.csv',index=False,date_format='%Y-%m-%d %H:%M:%S')
loaded=pd.read_csv(BASE/'data/posts_feature_exploration.csv')
assert loaded.shape==(710,32)
assert loaded.source_record.tolist()==source.source_record.tolist()
pd.testing.assert_frame_equal(loaded[source.columns],source,check_dtype=False)
assert df.hashtag_count.eq(df.hashtag_list.str.len()).all()
assert len(tags)==int(df.hashtag_count.sum())
assert not df.groupby('text_group_id',observed=True).sentiment.nunique().gt(1).any()
assert hashlib.sha256(INPUT.read_bytes()).hexdigest()==input_hash
results={
    'source_rows':len(source),'source_columns':len(source.columns),'exploration_rows':len(df),'exploration_columns':len(df.columns),
    'added_columns':derived_cols,'missing_input_cells':int(source.isna().sum().sum()),
    'sentiment_labels':df.sentiment.nunique(),'singleton_labels':int(counts['sentiment'].posts.eq(1).sum()),
    'platforms':df.platform.nunique(),'location_labels':df.country.nunique(),'users':df.user.nunique(),
    'distinct_hashtags':len(tag_frequency),'post_hashtag_rows':len(tags),
    'url_flagged_posts':int(df.has_url.sum()),'mention_flagged_posts':int(df.has_mention.sum()),
    'posts_with_listed_negation_cues':int(df.negation_cue_count.gt(0).sum()),
    'constant_features':constants.feature.tolist(),'input_sha256':input_hash,
    'date_min':str(df.timestamp.min()),'date_max':str(df.timestamp.max()),
    'validation':'All reconciliation and reload checks passed',
    'charts_created':0,'models_trained':0,'hypothesis_tests_run':0,
    'versions':{'python':__import__('sys').version.split()[0],'pandas':pd.__version__,'numpy':np.__version__},
}
(BASE/'validation_results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))