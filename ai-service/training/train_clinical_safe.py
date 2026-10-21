"""Train a leakage-reduced clinical screening model.
This is for research/decision-support only, not clinical diagnosis.
Source dataset columns are audited before training. Post-diagnosis/outcome fields are excluded.
"""
from pathlib import Path
import json, joblib, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, roc_auc_score

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/raw/clinical_reference_dataset.csv'
OUT=ROOT/'models/clinical/reference_candidate_model.joblib'
MET=ROOT/'models/clinical/reference_candidate.metrics.json'
TARGET='Oral Cancer (Diagnosis)'
# Only information intended to be available before confirmed diagnosis is considered.
FEATURES=['Age','Gender','Tobacco Use','Alcohol Consumption','HPV Infection','Betel Quid Use',
'Chronic Sun Exposure','Poor Oral Hygiene','Diet (Fruits & Vegetables Intake)',
'Family History of Cancer','Compromised Immune System','Oral Lesions','Unexplained Bleeding',
'Difficulty Swallowing','White or Red Patches in Mouth','Early Diagnosis']
LEAKAGE_EXCLUDED=['ID','Tumor Size (cm)','Cancer Stage','Treatment Type','Survival Rate (5-Year, %)',
'Cost of Treatment (USD)','Economic Burden (Lost Workdays per Year)']

def main():
    df=pd.read_csv(DATA)
    missing=[c for c in FEATURES+[TARGET] if c not in df.columns]
    if missing: raise SystemExit(f'Missing expected columns: {missing}')
    X=df[FEATURES].copy(); y=(df[TARGET].astype(str).str.strip().str.lower()=='yes').astype(int)
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.20,random_state=42,stratify=y)
    num=['Age']; cat=[c for c in FEATURES if c not in num]
    prep=ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),
                            ('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),cat)])
    model=RandomForestClassifier(n_estimators=300,random_state=42,class_weight='balanced_subsample',n_jobs=-1,min_samples_leaf=2)
    pipe=Pipeline([('preprocess',prep),('model',model)]); pipe.fit(Xtr,ytr)
    pred=pipe.predict(Xte); prob=pipe.predict_proba(Xte)[:,1]
    p,r,f,_=precision_recall_fscore_support(yte,pred,average='binary',zero_division=0)
    metrics={'dataset_rows':int(len(df)),'features':FEATURES,'excluded_for_leakage_or_post_diagnosis':LEAKAGE_EXCLUDED,
      'accuracy':float(accuracy_score(yte,pred)),'precision':float(p),'recall_sensitivity':float(r),'f1':float(f),
      'specificity':float(((pred[yte==0]==0).sum()/max(1,(yte==0).sum()))),'roc_auc':float(roc_auc_score(yte,prob)),
      'confusion_matrix':confusion_matrix(yte,pred).tolist(),'warning':'Research dataset/model only. Candidate is NOT promoted because internal held-out metrics must be meaningful and this run may indicate no predictive signal; not clinical validation.'}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump({'model':pipe,'version':'clinical-screening-v2-reference-dataset','feature_names':FEATURES,'positive_label':'yes'},OUT)
    MET.write_text(json.dumps(metrics,indent=2)); print(json.dumps(metrics,indent=2))
if __name__=='__main__': main()
