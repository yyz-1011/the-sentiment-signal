"""Create blinded pilot worksheets or the full, deterministic review package."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
SEED = 6074

def prepare(source, out, full=False):
    data = pd.read_csv(source)
    country = data.country.replace({'Scotland': 'UK'})
    major = country.value_counts().loc[lambda x: x.ge(30)].index
    groups = data.assign(_country=country.where(country.isin(major), 'Other'))
    shuffled = groups.sample(frac=1, random_state=SEED)
    pilot = shuffled.groupby(['_country', 'platform'], sort=False).head(3)
    remaining = shuffled.loc[~shuffled.source_record.isin(pilot.source_record)]
    # Interleave geographic/platform cells before rotating A/B/C assignment.
    cells = [g.index.tolist() for _, g in remaining.groupby(['_country','platform'], sort=True)]
    sequence = [cell[i] for i in range(max(map(len, cells))) for cell in cells if i < len(cell)]
    batches = {'pilot': pilot}
    if full:
        for i, label in enumerate('ABC'):
            batches[label] = groups.loc[sequence[i::3]]
        assert [len(batches[k]) for k in ['pilot','A','B','C']] == [54,219,219,218]
    owners = {'pilot': ('Yizhou','Liwen','Yuwei'), 'A':('Yizhou','Liwen','Yuwei'),
              'B':('Liwen','Yuwei','Yizhou'), 'C':('Yuwei','Yizhou','Liwen')}
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory is not empty; choose a new version to protect completed reviews.')
    out.mkdir(parents=True, exist_ok=True)
    rows=[]
    for batch, frame in batches.items():
        a,b,arbiter=owners[batch]
        blank=frame[['source_record','text']].copy().assign(reviewed_sentiment='',review_note='')
        for i, person in enumerate((a,b),1):
            filename=f'{batch.lower()}_{person.lower()}.csv' if full else f'pilot_reviewer_{i}.csv'
            blank.to_csv(out/filename,index=False,mode='x')
        for record in frame.source_record:
            rows.append({'source_record':int(record),'batch':batch,'reviewer_1':a,'reviewer_2':b,'adjudicator':arbiter})
    assigned=pd.DataFrame(rows).sort_values('source_record')
    assigned.to_csv(out/'assignment_manifest.csv',index=False)
    if full:
        assert not assigned.source_record.duplicated().any()
        assert set(assigned.source_record)==set(data.source_record)
        data[['source_record']].assign(reviewed_sentiment='',decision_note='').to_csv(out/'adjudication_template.csv',index=False)
        assigned.merge(data[['source_record','country','platform']],on='source_record').groupby(
            ['batch','country','platform']).size().rename('posts').to_csv(out/'assignment_coverage.csv')
    report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'seed':SEED,
            'full_package':full,'rows':len(assigned),'batch_sizes':{k:len(v) for k,v in batches.items()},
            'completed_decisions':0,'status':'blank worksheets; independent human review pending'}
    (out/'package_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'generated/label_review')
    p.add_argument('--full-package',action='store_true')
    args=p.parse_args()
    try:print(json.dumps(prepare(ROOT/'data/processed/sentiment_cleaned.csv',args.out,args.full_package),indent=2))
    except (ValueError,OSError) as e:p.error(str(e))
