import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import fetch from "node-fetch";
import { connectDB } from "./src/config/db.js";
import { notFound, errorHandler } from "./src/middleware/errorMiddleware.js";
import authRoutes from "./src/routes/authRoutes.js";
import patientRoutes from "./src/routes/patientRoutes.js";
import predictionRoutes from "./src/routes/predictionRoutes.js";

dotenv.config();
await connectDB();
const app = express();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const allowedOrigins = [
  "http://localhost:5173",
  "http://127.0.0.1:5173",
  "http://localhost:5174",
  "http://127.0.0.1:5174",
  "http://localhost:4173",
  "http://127.0.0.1:4173",
  ...(process.env.CLIENT_ORIGIN || "").split(","),
].map((origin) => origin.trim()).filter(Boolean);
app.use(cors({
  origin(origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) return callback(null, true);
    return callback(new Error(`CORS blocked origin: ${origin}`));
  },
}));
app.disable("x-powered-by");
app.use(express.json({ limit: "1mb" }));
app.get("/api/health", (_, res) => { const database = mongoose.connection.readyState === 1 ? "connected" : "disconnected"; res.status(database === "connected" ? 200 : 503).json({ status: database === "connected" ? "ok" : "degraded", service: "api", database }); });
app.get("/api/health/deep", async (_, res) => {
  try {
    const r = await fetch(`${process.env.AI_SERVICE_URL || "http://127.0.0.1:6000"}/health`);
    const ai = await r.json();
    res.status(r.ok ? 200 : 503).json({ status: r.ok ? "ok" : "degraded", api: "ok", ai });
  } catch (e) { res.status(503).json({ status: "degraded", api: "ok", ai: { status: "unreachable", message: e.message } }); }
});
app.use("/api/auth", authRoutes);
app.use("/api/patients", patientRoutes);
app.use("/api/predictions", predictionRoutes);
app.use(notFound);
app.use(errorHandler);
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
