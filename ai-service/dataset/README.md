# MeMoSA dataset

Do not place the MeMoSA dataset in this repository or redistribute it unless your approved Data Use Agreement permits that use.

Obtain the authorized collection(s) from the MeMoSA Workbench: https://workbench.memosa.my

After approval, extract the images and CSV metadata under a local directory and run:

```bash
python training/validate_dataset.py --data /path/to/memosa
python training/train_image.py --data /path/to/memosa --output models/image
python training/train_clinical.py --csv /path/to/memosa/<metadata.csv> --output models/clinical/model.joblib
```
