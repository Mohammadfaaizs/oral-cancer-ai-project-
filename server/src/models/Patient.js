import mongoose from "mongoose";

const patientSchema = new mongoose.Schema({
  patientCode: { type: String, required: true, unique: true, trim: true },
  name: { type: String, required: true, trim: true },
  age: { type: Number, min: 0, max: 130 },
  gender: { type: String, enum: ["male", "female", "other", "unknown"], default: "unknown" },
  contact: { type: String, trim: true },
  smoking: { type: String, enum: ["no", "occasionally", "yes", "unknown"], default: "unknown" },
  betelQuid: { type: String, enum: ["no", "occasionally", "yes", "unknown"], default: "unknown" },
  alcohol: { type: String, enum: ["no", "occasionally", "yes", "unknown"], default: "unknown" },
  tobaccoUse: { type: String, enum: ["no", "occasionally", "yes", "unknown"], default: "unknown" },
  hpvInfection: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  chronicSunExposure: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  poorOralHygiene: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  dietFruitsVegetables: { type: String, enum: ["low", "medium", "high", "unknown"], default: "unknown" },
  familyHistoryOfCancer: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  compromisedImmuneSystem: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  oralLesions: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  unexplainedBleeding: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  difficultySwallowing: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  whiteOrRedPatches: { type: String, enum: ["no", "yes", "unknown"], default: "unknown" },
  clinicalNotes: { type: String, trim: true, default: "" },
  createdBy: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
}, { timestamps: true });

export default mongoose.model("Patient", patientSchema);
