
from pathlib import Path
import argparse,json
import numpy as np, joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
FEATURES=['age','smoking','betelQuid','alcohol']
MAP={'no':0,'unknown':0,'occasionally':1,'yes':2}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',default='models/clinical/model.joblib'); a=ap.parse_args(); rng=np.random.default_rng(7); X=[];y=[]
 for _ in range(900):
  age=int(rng.integers(18,81)); s=int(rng.integers(0,3)); b=int(rng.integers(0,3)); al=int(rng.integers(0,3)); score=(age>55)+s*1.1+b*1.4+al*.5; label='elevated' if score>=3.0 else 'lower'; X.append([age,s,b,al]); y.append(label)
 X=np.array(X); x1,x2,y1,y2=train_test_split(X,y,test_size=.2,random_state=7,stratify=y); m=LogisticRegression(max_iter=500).fit(x1,y1); acc=accuracy_score(y2,m.predict(x2)); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); joblib.dump({'model':m,'features':FEATURES,'version':'clinical-demo-v1'},out); (out.with_suffix('.metrics.json')).write_text(json.dumps({'accuracy':float(acc),'dataset':'synthetic_demo_not_clinical'},indent=2)); print('clinical_test_accuracy',acc)
if __name__=='__main__': main()
