# Final engineering verification

Date: generated from the current project package.

## Passed
- Python compilation for the AI service and clinical inference code.
- `ai-service/test_smoke.py`: model artifacts, imports, model loading and direct inference passed.
- Live AI HTTP health endpoint returned HTTP 200 with both image and clinical models loaded.
- Live multipart image analysis using `demo-mouth-patient.png` returned HTTP 200, a prediction, probabilities, risk, and a Grad-CAM explanation path.
- Server JavaScript syntax checks passed for all `.js` files.
- Client-side demo-admin bypass was removed and replaced with real login/register/authenticated route logic.
- Clinical reference CSV (84,922 rows) was copied into the training pipeline. Leakage/post-diagnosis columns are excluded.

## Important finding about the supplied clinical reference dataset
A held-out run of the leakage-reduced candidate model produced approximately chance-level discrimination (ROC-AUC ~0.50, accuracy ~0.50). Therefore this candidate is intentionally **not promoted** to the production clinical model. This prevents a low-quality model from silently replacing the existing artifact. The candidate files are kept only for research/audit.

## Not fully verified in this environment
- MongoDB CRUD and complete persistence flow: requires a running MongoDB service.
- Full browser E2E user/admin workflow: requires the client dependencies and browser automation environment.
- Client production build: `node_modules` was not available and package installation did not complete within this environment.

## Honest status
The AI core and HTTP image-analysis service were directly tested successfully. Authentication and full-stack integration code were repaired, but a live MongoDB-backed browser end-to-end test still depends on the runtime services.

Medical note: the image model remains a research/demo model and is not clinically validated for diagnosis.
