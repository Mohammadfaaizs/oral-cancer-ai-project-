# Reference project integration

## Integrated from uploaded reference projects

### Clinical reference dataset
A copy of the uploaded 84,922-row CSV is included at `ai-service/data/raw/clinical_reference_dataset.csv` for reproducible research development.

The new training script explicitly excludes `ID`, tumor size, cancer stage, treatment type, survival rate, treatment cost, and economic burden from the predictive feature set because these may be post-diagnosis, outcome, or leakage-prone variables for a screening model.

Run:

`python training/train_clinical_safe.py`

This creates a pipeline model and real held-out metrics. The result must still not be described as clinically validated.

### Image reference project
The uploaded image repository was audited. Its useful ideas were its simple TFLite deployment pattern, explicit byte decoding with OpenCV, resize preprocessing, and a four-class output contract (`hbv`, `he`, `ipcl`, `le`). Its README describes laryngeal tissue classes rather than a directly compatible oral-lesion dataset, so its model and sample images were **not silently merged** into the oral-cancer model. Mixing incompatible label domains would make the project less reliable.

The project keeps the existing oral-lesion image model rather than replacing it with the unrelated TFLite model. A future benchmark can compare architectures only on the same authorized oral dataset and label taxonomy.
