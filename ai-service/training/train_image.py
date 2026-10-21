
from pathlib import Path
import argparse, json, random
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import numpy as np
CLASSES=["cancer","opmd","benign","developmental_anomaly","normal_anatomic_variant","no_lesion"]
SIZE=96
class FolderDataset(Dataset):
    def __init__(self, root):
        self.items=[]
        for i,c in enumerate(CLASSES):
            for p in sorted((Path(root)/c).glob('*.png')): self.items.append((p,i))
    def __len__(self): return len(self.items)
    def __getitem__(self,idx):
        p,y=self.items[idx]; a=np.asarray(Image.open(p).convert('RGB').resize((SIZE,SIZE)),dtype=np.float32)/255.0
        x=torch.from_numpy(a.transpose(2,0,1)); return x, y
class TinyOralCNN(nn.Module):
    def __init__(self):
        super().__init__(); self.features=nn.Sequential(nn.Conv2d(3,16,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(16,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(32,64,3,padding=1),nn.ReLU(),nn.AdaptiveAvgPool2d((1,1))); self.classifier=nn.Linear(64,len(CLASSES))
    def forward(self,x): return self.classifier(self.features(x).flatten(1))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data',default='demo-dataset/train'); ap.add_argument('--test',default='demo-dataset/test'); ap.add_argument('--output',default='models/image'); ap.add_argument('--epochs',type=int,default=18); a=ap.parse_args(); random.seed(1); torch.manual_seed(1)
    ds=FolderDataset(a.data); test=FolderDataset(a.test); dl=DataLoader(ds,batch_size=32,shuffle=True); td=DataLoader(test,batch_size=64)
    m=TinyOralCNN(); opt=torch.optim.Adam(m.parameters(),lr=1e-3); lossfn=nn.CrossEntropyLoss()
    for ep in range(a.epochs):
        m.train(); total=correct=0
        for x,y in dl:
            opt.zero_grad(); z=m(x); loss=lossfn(z,y); loss.backward(); opt.step(); total+=len(y); correct+=(z.argmax(1)==y).sum().item()
        print(f'epoch {ep+1}/{a.epochs} train_acc={correct/total:.3f}')
    m.eval(); total=correct=0; cm=np.zeros((len(CLASSES),len(CLASSES)),dtype=int)
    with torch.no_grad():
        for x,y in td:
            z=m(x); pred=z.argmax(1); total+=len(y); correct+=(pred==y).sum().item()
            for yy,pp in zip(y.numpy(),pred.numpy()): cm[yy,pp]+=1
    out=Path(a.output); out.mkdir(parents=True,exist_ok=True); torch.save({'state_dict':m.state_dict(),'classes':CLASSES,'input_size':SIZE,'model_version':'demo-cnn-v1'},out/'image_model.pt'); (out/'labels.json').write_text(json.dumps(CLASSES,indent=2)); (out/'metrics.json').write_text(json.dumps({'accuracy':float(correct/total),'confusion_matrix':cm.tolist(),'dataset':'synthetic_demo_not_clinical'},indent=2)); print('test_accuracy',correct/total); print(cm)
if __name__=='__main__': main()
