import express from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import FormData from "form-data";
import fetch from "node-fetch";
import { protect } from "../middleware/authMiddleware.js";
import Prediction from "../models/Prediction.js";
import Patient from "../models/Patient.js";
import OralImage from "../models/OralImage.js";

const router = express.Router();
router.use(protect);
const uploadDir = process.env.UPLOAD_DIR || "uploads";
fs.mkdirSync(uploadDir, { recursive: true });
const storage = multer.diskStorage({ destination: uploadDir, filename: (_, file, cb) => cb(null, `${Date.now()}-${Math.round(Math.random()*1e9)}${path.extname(file.originalname).toLowerCase()}`) });
const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 }, fileFilter: (_, file, cb) => cb(null, ["image/jpeg", "image/png", "image/webp"].includes(file.mimetype)) });
const canAccess = (user, patient) => user.role === "admin" || String(patient.createdBy) === String(user._id);
const escapeHtml = (value) => String(value ?? "N/A").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

router.post("/analyze", upload.single("image"), async (req, res, next) => {
  let savedFile;
  try {
    if (!req.file) return res.status(400).json({ message: "JPEG, PNG or WEBP image is required" });
    savedFile = req.file.path;
    const { patientId } = req.body;
    if (!patientId) return res.status(400).json({ message: "patientId is required" });
    const patient = await Patient.findById(patientId);
    if (!patient) return res.status(404).json({ message: "Patient not found" });
    if (!canAccess(req.user, patient)) return res.status(403).json({ message: "You are not authorized to analyze this patient" });
    const oralImage = await OralImage.create({ patientId, originalName: req.file.originalname, filename: req.file.filename, path: req.file.path, mimeType: req.file.mimetype, size: req.file.size, uploadedBy: req.user._id });
    const form = new FormData();
    const bytes = await fs.promises.readFile(req.file.path);
    form.append("image", bytes, { filename: req.file.originalname, contentType: req.file.mimetype });
    form.append("patientId", patientId);
    const clinicalFields = ["age","gender","smoking","betelQuid","alcohol","tobaccoUse","hpvInfection","chronicSunExposure","poorOralHygiene","dietFruitsVegetables","familyHistoryOfCancer","compromisedImmuneSystem","oralLesions","unexplainedBleeding","difficultySwallowing","whiteOrRedPatches"];
    for (const field of clinicalFields) form.append(field, String(patient[field] ?? "unknown"));
    form.append("earlyDiagnosis", "Unknown");
    const aiResponse = await fetch(`${process.env.AI_SERVICE_URL || "http://127.0.0.1:6000"}/predict/image`, { method: "POST", headers: form.getHeaders(), body: form, signal: AbortSignal.timeout(Number(process.env.AI_TIMEOUT_MS || 60000)) });
    if (!aiResponse.ok) return res.status(502).json({ message: "AI service error", detail: await aiResponse.text() });
    const result = await aiResponse.json();
    const prediction = await Prediction.create({ patientId, imageId: oralImage._id, imagePrediction: result.prediction, classProbabilities: result.classProbabilities, confidence: result.confidence, clinicalPrediction: result.clinicalPrediction, clinicalConfidence: result.clinicalConfidence, risk: result.risk, classification: result.classification || 'medium_risk', safeProbability: result.safeProbability || 0, cancerProbability: result.cancerProbability || 0, modelVersion: result.modelVersion, explanationPath: result.explanationPath || null, createdBy: req.user._id });
    res.status(201).json({ prediction, image: oralImage });
  } catch (err) { next(err); }
});

router.get("/images/:id", async (req, res, next) => {
  try {
    const image = await OralImage.findById(req.params.id).populate("patientId");
    if (!image) return res.status(404).json({ message: "Image not found" });
    if (!canAccess(req.user, image.patientId)) return res.status(403).json({ message: "Forbidden" });
    const filePath = path.resolve(image.path);
    if (!fs.existsSync(filePath)) return res.status(404).json({ message: "Image file not found" });
    res.type(image.mimeType);
    fs.createReadStream(filePath).pipe(res);
  } catch (e) { next(e); }
});

router.get("/", async (req, res, next) => { try { const q = {}; if (req.query.patientId) q.patientId = req.query.patientId; if (req.user.role !== "admin") q.createdBy = req.user._id; res.json(await Prediction.find(q).populate("patientId", "patientCode name").populate("imageId").sort({ createdAt: -1 }).limit(200)); } catch (e) { next(e); } });
router.get("/stats", async (req, res, next) => { try { const scope = req.user.role === "admin" ? {} : { createdBy: req.user._id }; const [patients, predictions, highRisk, monthly] = await Promise.all([Patient.countDocuments(req.user.role === "admin" ? {} : { createdBy: req.user._id }), Prediction.countDocuments(scope), Prediction.countDocuments({ ...scope, risk: "high" }), Prediction.countDocuments({ ...scope, createdAt: { $gte: new Date(new Date().getFullYear(), new Date().getMonth(), 1) } })]); res.json({ patients, predictions, highRisk, monthly }); } catch (e) { next(e); } });
router.get("/:id", async (req, res, next) => { try { const p = await Prediction.findById(req.params.id).populate("patientId", "patientCode name").populate("imageId"); if (!p) return res.status(404).json({ message: "Prediction not found" }); if (req.user.role !== "admin" && String(p.createdBy) !== String(req.user._id)) return res.status(403).json({ message: "Forbidden" }); res.json(p); } catch (e) { next(e); } });

router.get("/:id/report", async (req, res, next) => { 
  try { 
    const p = await Prediction.findById(req.params.id).populate("patientId").populate("imageId"); 
    if (!p) return res.status(404).json({ message: "Prediction not found" }); 
    if (req.user.role !== "admin" && String(p.createdBy) !== String(req.user._id)) return res.status(403).json({ message: "Forbidden" }); 
    const patient = p.patientId; 
    const classification = p.classification || "medium_risk"; 
    const classificationText = classification === "safe" ? "Safe & Good - No concerning findings" : classification === "high_risk" ? "High Risk - Immediate clinical consultation required" : "Medium Risk - Clinical evaluation recommended"; 
    const classificationColor = classification === "safe" ? "#10b981" : classification === "high_risk" ? "#ef4444" : "#f59e0b"; 
    const riskBgColor = classification === "safe" ? "#d1fae5" : classification === "high_risk" ? "#fee2e2" : "#fef3c7"; 
    const riskTextColor = classification === "safe" ? "#065f46" : classification === "high_risk" ? "#991b1b" : "#92400e"; 
    const allProbs = p.classProbabilities || {}; 
    const probHtml = Object.entries(allProbs).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f3f4f6"><span style="text-transform:capitalize">${k.replace(/_/g," ")}</span><strong>${(Number(v)*100).toFixed(2)}%</strong></div>`).join(""); 
    res.type("html").send(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Oral Cancer AI Detailed Medical Report</title><style>body{font-family:'Segoe UI',Arial,sans-serif;padding:30px;max-width:900px;margin:auto;color:#1f2937;background:#f9fafb}.header{background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 100%);color:white;padding:30px;border-radius:16px;margin-bottom:30px}.header h1{margin:0 0 10px 0;font-size:28px}.header p{margin:0;opacity:0.9}.section{background:white;padding:25px;border-radius:12px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}.section h2{margin:0 0 20px 0;color:#1e3a8a;border-bottom:2px solid #e5e7eb;padding-bottom:10px;font-size:20px}.patient-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px}.patient-item label{display:block;font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:5px}.patient-item p{margin:0;font-size:16px;font-weight:500}.classification-banner{background:${classificationColor};color:white;padding:25px;border-radius:12px;text-align:center;margin:20px 0}.classification-banner h2{margin:0;font-size:24px}.risk-level{background:${riskBgColor};color:${riskTextColor};padding:20px;border-radius:10px;text-align:center;margin:15px 0;font-weight:bold;font-size:18px}.clinical-factors{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.factor{padding:10px;background:#f3f4f6;border-radius:8px;text-align:center}.factor-label{font-size:11px;color:#6b7280;text-transform:uppercase;margin-bottom:5px}.factor-value{font-weight:600;font-size:14px}.disclaimer{background:#fef3c7;border-left:4px solid #f59e0b;padding:15px;margin-top:20px;border-radius:8px}.disclaimer p{margin:0;font-size:13px;color:#92400e}.footer{margin-top:30px;text-align:center;color:#6b7280;font-size:12px}@media print{body{background:white}.section{box-shadow:none;border:1px solid #e5e7eb}}</style></head><body><div class="header"><h1>🏥 Oral Cancer AI Medical Report</h1><p>Comprehensive AI-Powered Analysis Report</p><p style="font-size:14px;margin-top:10px">Generated: ${escapeHtml(new Date(p.createdAt).toLocaleString())}</p></div><div class="classification-banner"><h2 style="margin:0">${classificationText}</h2></div><div class="section"><h2>👤 Patient Information</h2><div class="patient-grid"><div class="patient-item"><label>Patient Name</label><p>${escapeHtml(patient.name)}</p></div><div class="patient-item"><label>Patient Code</label><p>${escapeHtml(patient.patientCode)}</p></div><div class="patient-item"><label>Age</label><p>${escapeHtml(patient.age)} years</p></div><div class="patient-item"><label>Gender</label><p>${escapeHtml(patient.gender)}</p></div><div class="patient-item"><label>Contact</label><p>${escapeHtml(patient.contact||"N/A")}</p></div></div></div><div class="section"><h2>🎯 AI Analysis Results</h2><div class="risk-level">Risk Level: ${escapeHtml(p.risk).toUpperCase()}</div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-top:15px"><div><label style="font-size:12px;color:#6b7280">Predicted Class</label><p style="margin:5px 0 0 0;font-size:18px;font-weight:bold">${escapeHtml(p.imagePrediction)}</p></div><div><label style="font-size:12px;color:#6b7280">Confidence</label><p style="margin:5px 0 0 0;font-size:18px;font-weight:bold">${(Number(p.confidence)*100).toFixed(1)}%</p></div><div><label style="font-size:12px;color:#6b7280">Classification</label><p style="margin:5px 0 0 0;font-size:18px;font-weight:bold">${escapeHtml(classification).replace(/_/g," ").toUpperCase()}</p></div><div><label style="font-size:12px;color:#6b7280">Model Version</label><p style="margin:5px 0 0 0;font-size:14px">${escapeHtml(p.modelVersion)}</p></div></div></div><div class="section"><h2>📊 Probability Analysis</h2><div style="margin-bottom:15px"><label style="font-size:12px;color:#6b7280">Cancer Probability</label><div style="display:flex;align-items:center;gap:10px;margin-top:5px"><div style="flex:1;height:24px;background:#e5e7eb;border-radius:12px;overflow:hidden"><div style="width:${Math.min(100,Number(p.cancerProbability||0)*100)}%;height:100%;background:linear-gradient(90deg,#ef4444,#dc2626);border-radius:12px"></div></div><strong style="width:70px;text-align:right">${(Number(p.cancerProbability||0)*100).toFixed(1)}%</strong></div></div><div style="margin-bottom:15px"><label style="font-size:12px;color:#6b7280">Safe Probability</label><div style="display:flex;align-items:center;gap:10px;margin-top:5px"><div style="flex:1;height:24px;background:#e5e7eb;border-radius:12px;overflow:hidden"><div style="width:${Math.min(100,Number(p.safeProbability||0)*100)}%;height:100%;background:linear-gradient(90deg,#10b981,#059669);border-radius:12px"></div></div><strong style="width:70px;text-align:right">${(Number(p.safeProbability||0)*100).toFixed(1)}%</strong></div></div><div style="margin-top:20px"><label style="font-size:12px;color:#6b7280">Detailed Class Probabilities</label><div style="margin-top:10px;background:#f9fafb;padding:15px;border-radius:8px">${probHtml}</div></div></div><div class="section"><h2>🔬 Clinical Assessment</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:15px"><div class="factor"><div class="factor-label">Clinical Prediction</div><div class="factor-value">${escapeHtml(p.clinicalPrediction||"N/A")}</div></div><div class="factor"><div class="factor-label">Clinical Confidence</div><div class="factor-value">${p.clinicalConfidence?((Number(p.clinicalConfidence)*100).toFixed(1)+"%"):"N/A"}</div></div></div><div class="clinical-factors"><div class="factor"><div class="factor-label">Smoking</div><div class="factor-value">${escapeHtml(patient.smoking||"Unknown")}</div></div><div class="factor"><div class="factor-label">Betel Quid</div><div class="factor-value">${escapeHtml(patient.betelQuid||"Unknown")}</div></div><div class="factor"><div class="factor-label">Alcohol</div><div class="factor-value">${escapeHtml(patient.alcohol||"Unknown")}</div></div><div class="factor"><div class="factor-label">Tobacco Use</div><div class="factor-value">${escapeHtml(patient.tobaccoUse||"Unknown")}</div></div><div class="factor"><div class="factor-label">HPV Infection</div><div class="factor-value">${escapeHtml(patient.hpvInfection||"Unknown")}</div></div><div class="factor"><div class="factor-label">Oral Hygiene</div><div class="factor-value">${escapeHtml(patient.poorOralHygiene||"Unknown")}</div></div></div></div><div class="section"><h2>📝 Clinical Notes</h2><p style="color:#374151;line-height:1.6">${escapeHtml(patient.clinicalNotes||"No clinical notes provided")}</p></div><div class="disclaimer"><p><strong>⚠️ MEDICAL DISCLAIMER:</strong> This AI-powered analysis is intended for screening and decision support purposes only. It should not be used as a substitute for professional medical diagnosis. All patients should undergo proper clinical examination by qualified healthcare professionals. The results provided here are based on a research model and may not reflect actual clinical outcomes. Always consult with healthcare providers for medical advice and treatment decisions.</p></div><div class="footer"><p>Oral Cancer AI Decision Support System | Report ID: ${escapeHtml(p._id)} | Generated: ${new Date().toLocaleString()}</p></div></body></html>`); 
  } catch (e) { next(e); } });

export default router;