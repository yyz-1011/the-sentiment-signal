"""Optional machine-only review aid; never adjudicated labels or model ground truth."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import re
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
ROOT=Path(__file__).resolve().parents[1]

def suggest(source,out):
    d=pd.read_csv(source);analyzer=SentimentIntensityAnalyzer();rows=[]
    for record in d.itertuples():
        # Remove explicit hashtags in both triage and primary model input.
        text=re.sub(r'#\w+','',record.text)
        scores=analyzer.polarity_scores(text);v=scores['compound']
        label='positive' if v>=.05 else 'negative' if v<=-.05 else 'neutral'
        flags=[]
        if abs(v)<.15:flags.append('low_absolute_score')
        if scores['pos']>0 and scores['neg']>0:flags.append('both_positive_and_negative_lexicon_cues')
        if re.search(r"(?i)\b(?:not|never|no|but|although|however)\b|n['’]t",text):flags.append('negation_or_contrast')
        rows.append({'source_record':record.source_record,'text':record.text,'machine_suggestion':label,
                     'compound_without_hashtags':v,'triage_flags':';'.join(flags),
                     'review_status':'machine_only_not_reviewed'})
    out.mkdir(parents=True,exist_ok=True)
    frame=pd.DataFrame(rows);frame.to_csv(out/'machine_suggestions.csv',index=False)
    frame[frame.triage_flags.ne('')].to_csv(out/'triage_queue.csv',index=False)
    report={'rows':len(frame),'label_counts':frame.machine_suggestion.value_counts().to_dict(),
            'triage_rows':int(frame.triage_flags.ne('').sum()),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'method':'VADER lexicon/rules on text with explicit hashtags removed; +/-0.05 thresholds',
            'vader_version':importlib.metadata.version('vaderSentiment'),
            'source_labels_used':False,'human_reviewers':0,'valid_ground_truth':False,
            'score_is_probability':False,'evaluation_status':'No supervised performance is reported without reviewed labels.'}
    (out/'suggestion_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=ROOT/'generated/machine_assistance');a=p.parse_args()
    print(json.dumps(suggest(ROOT/'data/processed/sentiment_cleaned.csv',a.out),indent=2))
