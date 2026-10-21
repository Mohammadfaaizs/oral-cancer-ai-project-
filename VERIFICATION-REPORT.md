# OralAI Verification Report

Date: 2026-08-17

## Automated checks completed

- JavaScript syntax check: PASS for all server `.js` files.
- Python compilation: PASS for all AI `.py` files.
- Docker Compose YAML parse: PASS.
- AI model artifacts: PASS (`image_model.pt`, `clinical/model.joblib`).
- AI service `/health`: PASS; image and clinical models loaded.
- Direct image inference: PASS.
- Multipart image inference: PASS.
- Grad-CAM generation: PASS for all six classes.
- Bundled test set: 60/60 correct (100%) on the synthetic demo test set.
- Six-class inference verified: cancer, opmd, benign, developmental_anomaly, normal_anatomic_variant, no_lesion.

## Not falsely claimed

- MongoDB live integration was not executed in this build environment because a MongoDB server/Docker daemon was unavailable.
- The React production build was not executed in this build environment because npm dependency installation timed out.
- Docker Compose was validated syntactically but not executed because Docker was unavailable.
- The bundled model is NOT a MeMoSA-trained model and is NOT clinically validated. Its 100% test accuracy is only on the included synthetic demonstration dataset.

## Required for the real deployment

1. Run the stack with Docker Desktop or install Node.js, MongoDB, and Python locally.
2. Create a strong `JWT_SECRET`.
3. Create the first admin account.
4. For research use of MeMoSA, obtain authorized access through the official MeMoSA Workbench and train/evaluate a separate real model under its data-use/licensing requirements.
