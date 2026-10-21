# OralAI — full runnable software demo

## Fastest option: Docker Desktop

Requirements: Docker Desktop.

1. Open a terminal in this folder.
2. Run `docker compose up --build -d`.
3. Open http://localhost:4173
4. AI health: http://localhost:6000/health
5. API health: http://localhost:5000/api/health

Create the first admin:

```bash
docker compose exec server npm run create-admin -- --name "System Admin" --email admin@example.com --password "Admin@2026Secure"
```

Then login with those credentials.

## Manual mode

1. Install Node.js 22+, Python 3.11+, and MongoDB 8 (or use MongoDB Atlas).
2. `cd ai-service && python -m venv .venv` then install `requirements.txt`.
3. Start AI: `python app.py`.
4. Copy `server/.env.example` to `server/.env`, set `MONGO_URI`, a long `JWT_SECRET`, and `AI_SERVICE_URL=http://127.0.0.1:6000`.
5. `cd server && npm install && npm run create-admin -- --name "System Admin" --email admin@example.com --password "Admin@2026Secure" && npm start`.
6. `cd client && npm install && npm run build && npm run dev`.

## Automated checks

AI-only: `cd ai-service && python test_smoke.py`
Stack: after services are running, from the project root run `node scripts/verify-stack.mjs`.

## Model/data notice

The bundled model is a software demonstration model trained on synthetic images. It proves the end-to-end software path but is not clinically validated and is not a MeMoSA-trained model. The real MeMoSA dataset must be obtained through its official access process before training a MeMoSA model.
