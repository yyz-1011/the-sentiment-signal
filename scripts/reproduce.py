"""Reproduce current cleaning and EDA without modifying committed data snapshots."""
from pathlib import Path
import argparse
import hashlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys

import pandas as pd
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'generated'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-notebooks', action='store_true', help='Refresh saved output cells in the three main notebooks after execution.')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    raw_path = ROOT/'data/raw/sentimentdataset.csv'
    clean_path = ROOT/'data/processed/sentiment_cleaned.csv'
    raw_hash, clean_hash = sha(raw_path), sha(clean_path)
    assert clean_hash == '4c38dc7cc2a8a06a96c13e989541c024ce31e9ee6af890a5f429fbe1f892ec6a'
    raw, clean = pd.read_csv(raw_path), pd.read_csv(clean_path)
    assert raw.shape == (732, 15) and clean.shape == (710, 26)
    subprocess.run([sys.executable, str(ROOT/'src/preprocess_and_analyze.py'), '--input',str(raw_path), '--output-dir',str(OUT/'cleaning')],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    regenerated = pd.read_csv(OUT/'cleaning/sentiment_cleaned.csv')
    pd.testing.assert_frame_equal(clean, regenerated, check_dtype=False)
    removed = pd.read_csv(OUT/'cleaning/removed_duplicate_records.csv')
    assert len(raw) == len(clean) + len(removed) and len(removed) == 22
    sys.path.insert(0,str(ROOT/'src'))
    from eda_core import run_eda
    core = run_eda(clean_path,OUT/'eda_core')
    print('Cleaning and core EDA reconciled.', flush=True)
    executed_dir=OUT/'executed_notebooks';executed_dir.mkdir(exist_ok=True)
    notebook_results=[]
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        print('Executing',path.name,flush=True)
        nb=nbformat.read(path,as_version=4)
        manager=KernelManager(kernel_name='python3')
        manager.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
        client=NotebookClient(nb,km=manager,timeout=180,allow_errors=False,resources={'metadata':{'path':str(ROOT)}})
        try:
            client.execute()
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
        errors=[o for c in nb.cells if c.cell_type=='code' for o in c.outputs if o.output_type=='error']
        assert not errors
        # Keep machine-specific directory names out of saved public notebook output.
        for cell in nb.cells:
            if cell.cell_type=='code':
                for output in cell.outputs:
                    if 'text' in output:
                        output.text=output.text.replace(str(ROOT),'.')
        nbformat.write(nb,executed_dir/path.name)
        if args.refresh_notebooks:nbformat.write(nb,path)
        notebook_results.append({'notebook':path.relative_to(ROOT).as_posix(),'code_cells_executed':sum(c.cell_type=='code' for c in nb.cells),'errors':len(errors)})
    counts=pd.read_csv(ROOT/'reports/eda/tables/sentiment_distribution.csv').set_index('sentiment').posts
    pd.testing.assert_series_equal(clean.sentiment.value_counts().sort_index(),counts.sort_index(),check_names=False)
    med=pd.read_csv(ROOT/'reports/eda/tables/sentiment_interactions.csv').set_index('sentiment').median_interactions
    pd.testing.assert_series_equal(clean.groupby('sentiment').total_interactions.median().sort_index(),med.sort_index(),check_names=False)
    annual=pd.read_csv(ROOT/'reports/eda/tables/annual_post_counts.csv').set_index('year').posts
    pd.testing.assert_series_equal(clean.groupby('year').size().sort_index(),annual.sort_index(),check_names=False)
    assert sha(raw_path)==raw_hash and sha(clean_path)==clean_hash
    versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','matplotlib','seaborn','nbformat','nbclient','ipykernel','ipython']}
    report={'status':'passed','raw_rows':len(raw),'cleaned_rows':len(clean),'removed_duplicates':len(removed),'raw_sha256':raw_hash,'cleaned_sha256':clean_hash,'sentiment_labels':int(clean.sentiment.nunique()),'singleton_labels':int(clean.sentiment.value_counts().eq(1).sum()),'source_unchanged':True,'cleaning_reconciled_to_snapshot':True,'supplied_eda_tables_reconciled':True,'notebooks':notebook_results,'python':sys.version.split()[0],'versions':versions,'models_trained':0,'hypothesis_tests_run':0,'checks_do_not_include':['Native PowerPoint execution','Word report regeneration','Independent sentiment annotation','Model performance']}
    (OUT/'reproduction_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
