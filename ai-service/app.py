
import os, json, uuid, io
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from inference.image_model import ImageModel
from inference.clinical_model import ClinicalModel
from explainability.gradcam import make_gradcam_png
BASE_DIR=Path(__file__).resolve().parent
MODEL_DIR=Path(os.getenv('MODEL_DIR', str(BASE_DIR/'models'))); IMAGE_MODEL=MODEL_DIR/'image'/'image_model.pt'; CLINICAL_MODEL=MODEL_DIR/'clinical'/'model.joblib'; EXPLAIN_DIR=MODEL_DIR/'explanations'; EXPLAIN_DIR.mkdir(parents=True,exist_ok=True)
image_model=ImageModel(str(IMAGE_MODEL)) if IMAGE_MODEL.exists() else None; clinical_model=ClinicalModel(str(CLINICAL_MODEL)) if CLINICAL_MODEL.exists() else None

def derive_risk_and_classification(label, probs, confidence):
    probs = probs or {}
    cancer = float(probs.get('cancer', 0.0) or 0.0)
    opmd = float(probs.get('opmd', 0.0) or 0.0)
    no_lesion = float(probs.get('no_lesion', 0.0) or 0.0)
    normal = float(probs.get('normal_anatomic_variant', 0.0) or 0.0)
    benign = float(probs.get('benign', 0.0) or 0.0)
    developmental = float(probs.get('developmental_anomaly', 0.0) or 0.0)
    safe_prob = no_lesion + normal + benign
    concerning_prob = cancer + opmd + developmental

    if label in ('no_lesion', 'normal_anatomic_variant', 'benign') and safe_prob >= 0.7 and confidence >= 0.6:
        return 'low', 'safe'
    if label == 'cancer' or cancer >= 0.45 or (concerning_prob >= 0.6 and cancer >= 0.25):
        return 'high', 'high_risk'
    if label in ('opmd', 'developmental_anomaly') or opmd >= 0.25 or developmental >= 0.25 or concerning_prob >= 0.4:
        return 'medium', 'medium_risk'
    if safe_prob >= 0.6:
        return 'low', 'low_risk'
    return 'low', 'safe'

def multipart(body,content_type):
    boundary=content_type.split('boundary=',1)[1].encode(); parts=body.split(b'--'+boundary); out={}
    for part in parts:
        if b'Content-Disposition:' not in part: continue
        head,data=part.split(b'\r\n\r\n',1); data=data.rsplit(b'\r\n',1)[0]
        hs=head.decode('utf-8','ignore'); import re
        nm=re.search(r'name="([^"]+)"',hs); fn=re.search(r'filename="([^"]*)"',hs)
        if nm: out[nm.group(1)]={'filename':fn.group(1) if fn else None,'data':data.decode('utf-8','ignore') if not fn else data}
    return out
class H(BaseHTTPRequestHandler):
    def send_json(self,status,obj):
        b=json.dumps(obj).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Access-Control-Allow-Origin', os.getenv('CLIENT_ORIGIN','*')); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_OPTIONS(self):
        self.send_response(204); self.send_header('Access-Control-Allow-Origin', os.getenv('CLIENT_ORIGIN','*')); self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.end_headers()
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/health': return self.send_json(200,{'status':'ok','imageModelLoaded':image_model is not None,'clinicalModelLoaded':clinical_model is not None,'modelVersion':image_model.model_version if image_model else None})
        if p.startswith('/explanations/'):
            f=EXPLAIN_DIR/p.split('/')[-1]
            if not f.exists(): return self.send_json(404,{'message':'Not found'})
            b=f.read_bytes(); self.send_response(200); self.send_header('Content-Type','image/png'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        self.send_json(404,{'message':'Not found'})
    def do_POST(self):
        p=urlparse(self.path).path; n=int(self.headers.get('Content-Length','0')); body=self.rfile.read(n); ct=self.headers.get('Content-Type','')
        if p=='/predict/image':
            if image_model is None: return self.send_json(503,{'message':'Image model unavailable'})
            form=multipart(body,ct); image=form.get('image');
            if not image or not image['filename']: return self.send_json(400,{'message':'image file is required'})
            label,conf,probs,x=image_model.predict(image['data']); idx=list(probs).index(label); cam=image_model.grad_cam(x,idx); name=f'gradcam-{uuid.uuid4().hex}.png'; (EXPLAIN_DIR/name).write_bytes(make_gradcam_png(image['data'],cam)); cancer=probs.get('cancer',0); opmd=probs.get('opmd',0); no_lesion=probs.get('no_lesion',0); normal=probs.get('normal_anatomic_variant',0); benign=probs.get('benign',0); safe_prob=no_lesion+normal+benign; risk, classification = derive_risk_and_classification(label, probs, conf); clinical=clinical_conf=None
            if clinical_model: clinical,clinical_conf,_=clinical_model.predict({k:v['data'] for k,v in form.items() if v['filename'] is None})
            return self.send_json(200,{'prediction':label,'confidence':conf,'classProbabilities':probs,'risk':risk,'classification':classification,'safeProbability':safe_prob,'cancerProbability':cancer,'modelVersion':image_model.model_version,'explanationAvailable':True,'explanationPath':f'/explanations/{name}','clinicalPrediction':clinical,'clinicalConfidence':clinical_conf,'demoModel':True,'warning':'Image model is a research/demo model and is NOT clinically validated.'})
        if p=='/predict/clinical':
            if not clinical_model:return self.send_json(503,{'message':'Clinical model unavailable'})
            form=multipart(body,ct) if ct.startswith('multipart/form-data') else {}; data={k:v['data'] for k,v in form.items()}; label,conf,ver=clinical_model.predict(data); return self.send_json(200,{'clinicalPrediction':label,'confidence':conf,'modelVersion':ver,'demoModel':True,'warning':'Synthetic demo model; not clinically validated.'})
        self.send_json(404,{'message':'Not found'})
if __name__=='__main__': ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','6000'))),H).serve_forever()
