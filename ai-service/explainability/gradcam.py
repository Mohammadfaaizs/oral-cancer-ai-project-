
import io, cv2, numpy as np
from PIL import Image
# True Grad-CAM for the bundled PyTorch CNN.
def make_gradcam_png(original_bytes, heatmap):
    image=Image.open(io.BytesIO(original_bytes)).convert('RGB'); rgb=np.array(image); heat=cv2.resize(heatmap,(rgb.shape[1],rgb.shape[0])); heat8=np.uint8(255*heat); hm=cv2.applyColorMap(heat8,cv2.COLORMAP_JET); hm=cv2.cvtColor(hm,cv2.COLOR_BGR2RGB); overlay=np.clip(.55*rgb+.45*hm,0,255).astype(np.uint8); out=io.BytesIO(); Image.fromarray(overlay).save(out,'PNG'); return out.getvalue()
