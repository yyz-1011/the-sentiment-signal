"""Collect completed independent worksheets; never manufacture missing decisions."""
import argparse
import json
from pathlib import Path
import pandas as pd
ALLOWED={'positive','negative','neutral','exclude'}

def assemble(package,out,resolutions=None):
    assignments=pd.read_csv(package/'assignment_manifest.csv');sheets={};rows=[]
    if out.exists() and any(out.iterdir()):raise ValueError('Choose a new empty output directory to preserve earlier decisions.')
    for a in assignments.itertuples():
        batch=a.batch.lower()
        for person in (a.reviewer_1,a.reviewer_2):
            key=(batch,person)
            if key not in sheets:
                frame=pd.read_csv(package/f'{batch}_{person.lower()}.csv',keep_default_na=False)
                if frame.source_record.duplicated().any():raise ValueError('Duplicate worksheet IDs.')
                expected=set(assignments.loc[assignments.batch.eq(a.batch),'source_record'])
                if set(frame.source_record)!=expected:raise ValueError('Worksheet membership changed.')
                sheets[key]=frame.set_index('source_record')
        first=sheets[(batch,a.reviewer_1)].loc[a.source_record]
        second=sheets[(batch,a.reviewer_2)].loc[a.source_record]
        x,y=str(first.reviewed_sentiment).strip().lower(),str(second.reviewed_sentiment).strip().lower()
        notes=bool(str(first.review_note).strip() and str(second.review_note).strip())
        status='agreement' if x in ALLOWED and x==y and notes else 'needs_review_or_adjudication'
        rows.append({'source_record':a.source_record,'batch':a.batch,'reviewer_1':a.reviewer_1,'reviewer_2':a.reviewer_2,
                     'adjudicator':a.adjudicator,'reviewer_1_decision':x,'reviewer_2_decision':y,
                     'reviewer_1_note':first.review_note,'reviewer_2_note':second.review_note,
                     'reviewed_sentiment':x if status=='agreement' else '',
                     'decision_note':f'Two worksheet decisions agree. {first.review_note} / {second.review_note}' if status=='agreement' else '',
                     'status':status})
    combined=pd.DataFrame(rows)
    if resolutions:
        r=pd.read_csv(resolutions,keep_default_na=False)
        if not {'source_record','reviewed_sentiment','decision_note','adjudicator'}.issubset(r):raise ValueError('Resolution columns are incomplete.')
        if r.source_record.duplicated().any() or not set(r.source_record)<=set(assignments.source_record):raise ValueError('Invalid resolution IDs.')
        for row in r.itertuples():
            i=combined.index[combined.source_record.eq(row.source_record)][0]
            if row.adjudicator!=combined.loc[i,'adjudicator']:raise ValueError('Wrong named adjudicator for this record.')
            if row.reviewed_sentiment not in ALLOWED or not row.decision_note.strip():raise ValueError('Resolution needs allowed label and reason.')
            # Two independent usable decisions must exist before adjudication.
            if combined.loc[i,'reviewer_1_decision'] not in ALLOWED|{'mixed','unclear'} or combined.loc[i,'reviewer_2_decision'] not in ALLOWED|{'mixed','unclear'}:
                raise ValueError('Do not resolve records without both independent reviewer decisions.')
            if not str(combined.loc[i,'reviewer_1_note']).strip() or not str(combined.loc[i,'reviewer_2_note']).strip():raise ValueError('Both reviewer notes are required.')
            combined.loc[i,['reviewed_sentiment','decision_note','status']]=[row.reviewed_sentiment,row.decision_note,'adjudicated']
    out.mkdir(parents=True,exist_ok=True)
    combined.to_csv(out/'review_decisions_and_provenance.csv',index=False)
    pending=combined[combined.reviewed_sentiment.eq('')]
    pending.to_csv(out/'pending_queue.csv',index=False)
    report={'records':len(combined),'agreements':int(combined.status.eq('agreement').sum()),'adjudicated':int(combined.status.eq('adjudicated').sum()),
            'pending':len(pending),'labels_exported':len(pending)==0,
            'claim_limit':'Worksheet contents are recorded, not independent proof of human identity or approval.'}
    if not len(pending):combined[['source_record','reviewed_sentiment','decision_note']].to_csv(out/'adjudicated_for_validation.csv',index=False)
    (out/'assembly_status.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--resolutions',type=Path);a=p.parse_args()
    try:print(json.dumps(assemble(a.package,a.out,a.resolutions),indent=2))
    except (ValueError,OSError) as e:p.error(str(e))
