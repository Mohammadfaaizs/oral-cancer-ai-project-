# Verification status

## Completed in this build
- AI image artifact loading and direct inference smoke test.
- Safe clinical dataset copied into the project and training pipeline configured.
- Data-leakage columns excluded from the clinical training pipeline.
- Real authentication UI replaces the former client-side demo-admin bypass.
- Protected client routes and logout added.
- Clinical patient fields are persisted and forwarded to the AI service.

## Requires environment at runtime
- MongoDB must be reachable for persistence and full user/admin workflow.
- Run clinical training to regenerate the clinical model from the included research dataset.
- Full browser E2E testing requires a running stack.

Medical limitation: software functionality does not equal clinical validation.
