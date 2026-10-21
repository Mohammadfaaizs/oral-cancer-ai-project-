import mongoose from "mongoose";

const predictionSchema = new mongoose.Schema({
  patientId: { type: mongoose.Schema.Types.ObjectId, ref: "Patient", required: true },
  imageId: { type: mongoose.Schema.Types.ObjectId, ref: "OralImage", required: true },
  imagePrediction: { type: String, required: true },
  classProbabilities: { type: Map, of: Number, default: {} },
  confidence: { type: Number, required: true },
  clinicalPrediction: { type: String, default: null },
  clinicalConfidence: { type: Number, default: null },
  risk: { type: String, enum: ["low", "medium", "high"], required: true },
  classification: { type: String, enum: ["safe", "low_risk", "medium_risk", "high_risk"], default: "medium_risk" },
  safeProbability: { type: Number, default: 0 },
  cancerProbability: { type: Number, default: 0 },
  modelVersion: { type: String, required: true },
  explanationPath: { type: String, default: null },
  disclaimer: { type: String, default: "AI output is decision support and not a diagnosis." },
  createdBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
}, { timestamps: true });

export default mongoose.model("Prediction", predictionSchema);
