"""Engineering tests only. Invented targets below are not project sentiment labels."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
import unittest
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_label_review import prepare
from assemble_adjudication import assemble
from evaluate_sentiment import evaluate, CLASSES
from validate_label_review import validate

class WorkflowTests(unittest.TestCase):
    def fixture(self,path):
        d=pd.DataFrame([(j*100+i,f'{label} sample {i}',f'{j}-{i//2}',label,'fixture','fixture')
                        for j,label in enumerate(CLASSES) for i in range(60)],
                       columns=['source_record','text','text_group_id','reviewed_sentiment','country','platform'])
        source=path/'source.csv';reviewed=path/'reviewed.csv'
        d.drop(columns='reviewed_sentiment').to_csv(source,index=False)
        d[['source_record','reviewed_sentiment']].assign(decision_note='invented engineering fixture').to_csv(reviewed,index=False)
        return source,reviewed

    def test_full_review_coverage_blinding_and_no_overwrite(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/'review';prepare(ROOT/'data/processed/sentiment_cleaned.csv',out,True)
            manifest=pd.read_csv(out/'assignment_manifest.csv')
            self.assertEqual(manifest.batch.value_counts().to_dict(),{'A':219,'B':219,'C':218,'pilot':54})
            self.assertEqual(manifest.source_record.nunique(),710)
            for f in out.glob('*_yizhou.csv'):
                frame=pd.read_csv(f);self.assertEqual(list(frame),['source_record','text','reviewed_sentiment','review_note'])
                self.assertTrue(frame.reviewed_sentiment.isna().all())
            with self.assertRaises(ValueError):prepare(ROOT/'data/processed/sentiment_cleaned.csv',out,True)

    def test_assembly_does_not_export_blank_targets(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp);prepare(ROOT/'data/processed/sentiment_cleaned.csv',p/'review',True)
            result=assemble(p/'review',p/'out')
            self.assertEqual(result['pending'],710)
            self.assertFalse(result['labels_exported'])
            self.assertFalse((p/'out/adjudicated_for_validation.csv').exists())
            r=pd.DataFrame([{'source_record':int(pd.read_csv(p/'review/assignment_manifest.csv').iloc[0].source_record),
                             'reviewed_sentiment':'positive','decision_note':'attempt','adjudicator':pd.read_csv(p/'review/assignment_manifest.csv').iloc[0].adjudicator}])
            r.to_csv(p/'resolution.csv',index=False)
            with self.assertRaises(ValueError):assemble(p/'review',p/'bad',p/'resolution.csv')

    def test_blank_and_incomplete_labels_rejected(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp);source,reviewed=self.fixture(p)
            r=pd.read_csv(reviewed);r.iloc[:-1].to_csv(reviewed,index=False)
            with self.assertRaises(ValueError):validate(source,reviewed,p/'audit')
            source,reviewed=self.fixture(p);r=pd.read_csv(reviewed);r.loc[0,'reviewed_sentiment']='';r.to_csv(reviewed,index=False)
            with self.assertRaises(ValueError):evaluate(reviewed,p/'model',source=source)

    def test_conflicting_text_and_missing_notes_rejected(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp);source,reviewed=self.fixture(p)
            r=pd.read_csv(reviewed);r.loc[0,'reviewed_sentiment']='positive';r.to_csv(reviewed,index=False)
            with self.assertRaises(ValueError):validate(source,reviewed,p/'audit')
            source,reviewed=self.fixture(p);r=pd.read_csv(reviewed);r.loc[0,'decision_note']='';r.to_csv(reviewed,index=False)
            with self.assertRaises(ValueError):validate(source,reviewed,p/'audit')

    def test_development_and_single_test_guard(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp);source,reviewed=self.fixture(p);out=p/'model'
            with self.assertRaises(ValueError):evaluate(reviewed,out,True,source)
            evaluate(reviewed,out,source=source)
            self.assertFalse((out/'final_test_results.csv').exists())
            split=pd.read_csv(out/'split_manifest.csv')
            self.assertTrue(split.groupby('text_group_id').partition.nunique().eq(1).all())
            pred=pd.read_csv(out/'development_predictions.csv')
            testids=set(split.loc[split.partition.eq('test'),'source_record'])
            self.assertFalse(set(pred.source_record)&testids)
            self.assertTrue(pred.groupby(['model','variant','source_record']).size().eq(1).all())
            folds=pd.read_csv(out/'development_fold_manifest.csv')
            self.assertTrue(folds.groupby(['fold','text_group_id']).role.nunique().eq(1).all())
            evaluate(reviewed,out,True,source)
            self.assertEqual(len(pd.read_csv(out/'final_test_results.csv')),8)
            with self.assertRaises(ValueError):evaluate(reviewed,out,True,source)

    def test_changed_review_requires_development_again(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp);source,reviewed=self.fixture(p);out=p/'model';evaluate(reviewed,out,source=source)
            r=pd.read_csv(reviewed);r.loc[0,'decision_note']='changed';r.to_csv(reviewed,index=False)
            with self.assertRaises(ValueError):evaluate(reviewed,out,True,source)

if __name__=='__main__':unittest.main(verbosity=2)
