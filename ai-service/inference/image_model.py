
import io, json
from pathlib import Path
import numpy as np, torch, cv2
from PIL import Image
from torch import nn
CLASS_NAMES=["cancer","opmd","benign","developmental_anomaly","normal_anatomic_variant","no_lesion"]
class TinyOralCNN(nn.Module):
    def __init__(self,n=6):
        super().__init__(); self.features=nn.Sequential(nn.Conv2d(3,16,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(16,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(32,64,3,padding=1),nn.ReLU(),nn.AdaptiveAvgPool2d((1,1))); self.classifier=nn.Linear(64,n)
    def forward(self,x): return self.classifier(self.features(x).flatten(1))
class ImageModel:
    def __init__(self,path):
        self.path=Path(path); 
        try:
            ck=torch.load(self.path,map_location='cpu',weights_only=True)
        except TypeError:
            ck=torch.load(self.path,map_location='cpu')
        self.classes=ck.get('classes',CLASS_NAMES); self.input_size=int(ck.get('input_size',96)); self.model=TinyOralCNN(len(self.classes)); self.model.load_state_dict(ck['state_dict']); self.model.eval(); self.model_version=ck.get('model_version',self.path.stem); self._acts=None; self._grads=None
    def preprocess(self,b):
        im=Image.open(io.BytesIO(b)).convert('RGB').resize((self.input_size,self.input_size)); a=np.asarray(im,dtype=np.float32)/255.; return torch.from_numpy(a.transpose(2,0,1)).unsqueeze(0)
    def predict(self,b):
        x=self.preprocess(b); with_ctx=torch.enable_grad()
        with with_ctx:
            z=self.model(x); p=torch.softmax(z,1)[0]; idx=int(torch.argmax(p));
        return self.classes[idx],float(p[idx].detach()),{c:float(v) for c,v in zip(self.classes,p.detach().numpy())},x
    def grad_cam(self,x,class_index):
        acts=[]; grads=[]
        def fwd(m,i,o): acts.append(o)
        def bwd(m,gi,go): grads.append(go[0])
        layer=self.model.features[6]; h1=layer.register_forward_hook(fwd); h2=layer.register_full_backward_hook(bwd)
        self.model.zero_grad(); z=self.model(x); z[:,class_index].backward(); a=acts[0][0].detach().numpy(); g=grads[0][0].detach().numpy(); w=g.mean(axis=(1,2)); cam=np.maximum((a*w[:,None,None]).sum(0),0); cam/=cam.max()+1e-8; h1.remove(); h2.remove(); return cam
