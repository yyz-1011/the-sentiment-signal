"""Audit the adjudicated target without training or opening a model test set."""
from pathlib import Path
import argparse
import hashlib
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def validate(source, reviewed, out):
    d=pd.read_csv(source);r=pd.read_csv(reviewed,keep_default_na=False)
    required={'source_record','reviewed_sentiment','decision_note'}
    if not required.issubset(r):raise ValueError(f'Required columns: {sorted(required)}')
    if r.source_record.duplicated().any() or set(r.source_record)!=set(d.source_record):
        raise ValueError('Expected exactly one decision per source record, with no missing or unknown IDs.')
    if not r.reviewed_sentiment.isin(['positive','negative','neutral','exclude']).all():
        raise ValueError('Blank, mixed or unknown final labels remain; complete adjudication first.')
    if not r.decision_note.astype(str).str.strip().ne('').all():raise ValueError('Decision notes are required.')
    merged=d.merge(r[list(required)],on='source_record',validate='one_to_one')
    included=merged[merged.reviewed_sentiment.ne('exclude')]
    if included.groupby('text_group_id').reviewed_sentiment.nunique().gt(1).any():
        raise ValueError('Identical text has conflicting included labels; adjudicate before evaluation.')
    counts=included.groupby('reviewed_sentiment').agg(posts=('source_record','size'),text_groups=('text_group_id','nunique')).reindex(['negative','neutral','positive'],fill_value=0)
    out.mkdir(parents=True,exist_ok=True)
    counts.to_csv(out/'reviewed_class_support.csv')
    merged.groupby(['country','reviewed_sentiment']).size().rename('posts').to_csv(out/'reviewed_country_coverage.csv')
    report={'status':'structurally_valid','rows':len(r),'included':len(included),'excluded':len(d)-len(included),
            'distinct_groups_per_class':counts.text_groups.to_dict(),
            'at_least_five_groups_per_class':bool(counts.text_groups.ge(5).all()),
            'reviewed_sha256':hashlib.sha256(reviewed.read_bytes()).hexdigest(),
            'claim_limit':'This validates schema and consistency, not independent review or human approval.'}
    (out/'review_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reviewed',required=True,type=Path)
    p.add_argument('--out',type=Path,default=ROOT/'generated/review_validation');a=p.parse_args()
    try:print(json.dumps(validate(ROOT/'data/processed/sentiment_cleaned.csv',a.reviewed,a.out),indent=2))
    except (ValueError,OSError) as e:p.error(str(e))
