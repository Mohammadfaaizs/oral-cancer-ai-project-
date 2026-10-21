import io, json, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

def test_model_artifacts():
    root=Path(__file__).resolve().parent
    assert (root/'models/image/image_model.pt').exists()
    assert (root/'models/clinical/model.joblib').exists()

def test_imports():
    import app
    assert app.image_model is not None
    assert app.clinical_model is not None

def test_inference_direct():
    import app
    image=next((Path(__file__).resolve().parent/'demo-dataset/test').glob('*/*.png'))
    result=app.image_model.predict(image.read_bytes())
    assert result[0] in app.image_model.classes
    assert 0 <= result[1] <= 1

if __name__ == '__main__':
    test_model_artifacts(); test_imports(); test_inference_direct(); print('PASS: AI artifact, imports, and direct inference')
