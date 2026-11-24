# DEPLOYMENT & USAGE GUIDE

## Project Overview

**Oral Cancer AI** is a full-stack web application for oral cancer risk assessment combining:
- Image-based AI predictions (PyTorch CNN)
- Clinical risk scoring (Scikit-learn Logistic Regression)
- Patient management system
- Medical history tracking
- GradCAM explainability

---

## Quick Start (Manual Setup - Tested & Verified)

### Prerequisites
- **Node.js 22+** (tested: v22.20.0)
- **Python 3.11+** (tested: 3.14.7)  
- **MongoDB 8** (or MongoDB Atlas - already configured)
- **npm 10+** (tested: 10.9.3)

### Step 1: Clone Repository
```bash
cd "path/to/oral-cancer-ai"
```

### Step 2: Start AI Service (Terminal 1)
```bash
cd ai-service

# Create Python environment
python -m venv .venv

# Activate environment
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start service (Runs on port 6001)
python app.py

# ✓ Expected output:
# Serving on 0.0.0.0:6001
# Models loaded successfully
```

### Step 3: Start Backend API (Terminal 2)
```bash
cd server

# Install dependencies
npm install

# Create admin user (required before first startup)
npm run create-admin -- --name "System Admin" --email admin@example.com --password "Admin@2026Secure"

# Start server (Runs on port 5000)
npm start

# ✓ Expected output:
# MongoDB connected: [connection string]
# Server running on http://localhost:5000
```

### Step 4: Start Frontend (Terminal 3)
```bash
cd client

# Install dependencies
npm install

# Start dev server (Runs on port 5173)
npm run dev

# ✓ Expected output:
# VITE v5.4.21 ready in 399 ms
# ➜ Local: http://localhost:5173/
```

### Step 5: Access Application
```
Frontend:    http://localhost:5173
API Server:  http://localhost:5000
AI Service:  http://localhost:6001

Login with:
Email:    admin@example.com
Password: Admin@2026Secure
```

---

## Docker Deployment (Alternative)

### Prerequisites
- **Docker Desktop** installed and running

### Quick Start
```bash
# Build and start all services
docker compose up --build -d

# Create admin user
docker compose exec server npm run create-admin -- --name "System Admin" --email admin@example.com --password "Admin@2026Secure"

# Check services
docker compose ps

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Services
- **Frontend:** http://localhost:4173 (served via Vite)
- **API:** http://localhost:5000
- **AI Service:** http://localhost:6001
- **MongoDB:** localhost:27017

---

## API Documentation

### Authentication

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "Admin@2026Secure"
}

Response:
{
  "_id": "user-id",
  "name": "System Admin",
  "email": "admin@example.com",
  "role": "admin",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Using Token
```bash
Authorization: Bearer {token}
# Include in all subsequent requests
```

### Patients

#### Get All Patients
```bash
GET /api/patients
Authorization: Bearer {token}

Response: Array of patient objects
[
  {
    "_id": "patient-id",
    "patientCode": "2051",
    "name": "John Doe",
    "age": 45,
    "gender": "male",
    ...
  }
]
```

#### Create Patient
```bash
POST /api/patients
Authorization: Bearer {token}
Content-Type: application/json

{
  "patientCode": "TEST001",
  "name": "Patient Name",
  "age": 50,
  "gender": "male",           # Enum: male, female, other, unknown
  "contact": "9876543210",
  "smoking": "yes",           # Enum: no, occasionally, yes, unknown
  "betelQuid": "no",          # Enum: no, occasionally, yes, unknown
  "alcohol": "yes",           # Enum: no, occasionally, yes, unknown
  "tobaccoUse": "yes",        # Enum: no, occasionally, yes, unknown
  "hpvInfection": "no",       # Enum: no, yes, unknown
  "chronicSunExposure": "yes",# Enum: no, yes, unknown
  "poorOralHygiene": "yes",   # Enum: no, yes, unknown
  "dietFruitsVegetables": "low", # Enum: low, medium, high, unknown
  "familyHistoryOfCancer": "yes", # Enum: no, yes, unknown
  "compromisedImmuneSystem": "no", # Enum: no, yes, unknown
  "oralLesions": "yes",       # Enum: no, yes, unknown
  "unexplainedBleeding": "no",# Enum: no, yes, unknown
  "difficultySwallowing": "no",# Enum: no, yes, unknown
  "whiteOrRedPatches": "yes",
  "clinicalNotes": "Optional clinical notes"
}

Response: Created patient object with _id
```

#### Update Patient
```bash
PUT /api/patients/{patientId}
Authorization: Bearer {token}
Content-Type: application/json

{
  "clinicalNotes": "Updated notes",
  "gender": "female",
  ...
}
```

#### Get Patient
```bash
GET /api/patients/{patientId}
Authorization: Bearer {token}
```

#### Delete Patient
```bash
DELETE /api/patients/{patientId}
Authorization: Bearer {token}
```

### AI Predictions

#### Get Predictions for Patient
```bash
GET /api/predictions?patientId={patientId}
Authorization: Bearer {token}

Response: Array of predictions
[
  {
    "_id": "prediction-id",
    "patientId": "patient-id",
    "imageUrl": "path/to/image.jpg",
    "prediction": "cancer",
    "confidence": 0.95,
    "risk": "high",
    "createdAt": "2026-09-02T10:30:00Z"
  }
]
```

### AI Service Endpoints

#### Health Check
```bash
GET http://localhost:6001/health

Response:
{
  "status": "ok",
  "imageModelLoaded": true,
  "clinicalModelLoaded": true,
  "modelVersion": "demo-cnn-v1"
}
```

#### Clinical Prediction
```bash
POST http://localhost:6001/predict/clinical
Content-Type: application/json

{
  "age": 45,
  "gender": "M",
  "smoking": 1,
  "betelQuid": 1,
  "alcohol": 1,
  "tobaccoUse": 1,
  "hpvInfection": 0,
  "chronicSunExposure": 1,
  "poorOralHygiene": 1,
  "dietFruits": 0,
  "dietVegetables": 0,
  "familyHistory": 1,
  "immunocompromised": 0,
  "oralLesions": 1,
  "unexplainedBleeding": 1,
  "difficultySwallowing": 0
}

Response:
{
  "clinicalPrediction": "lower",
  "confidence": 0.9999996636869947,
  "modelVersion": "clinical-demo-v1",
  "demoModel": true,
  "warning": "Synthetic demo model; not clinically validated."
}
```

#### Image Prediction
```bash
POST http://localhost:6001/predict/image
Content-Type: multipart/form-data

Form Data:
- image: [binary image file]
- age: 45
- gender: M
- ... (clinical factors as form fields)

Response:
{
  "prediction": "cancer",
  "confidence": 0.92,
  "classProbabilities": {
    "cancer": 0.92,
    "opmd": 0.05,
    "benign": 0.02,
    "no_lesion": 0.01,
    "normal_anatomic_variant": 0.00,
    "developmental_anomaly": 0.00
  },
  "risk": "high",
  "classification": "high_risk",
  "safeProbability": 0.03,
  "cancerProbability": 0.92,
  "explanationAvailable": true,
  "explanationPath": "/explanations/gradcam-{uuid}.png",
  "clinicalPrediction": "higher",
  "clinicalConfidence": 0.87,
  "demoModel": true,
  "warning": "Image model is a research/demo model and is NOT clinically validated."
}
```

---

## Important Notes

### Model Disclaimer
⚠️ **All models are DEMO/SYNTHETIC models trained on demonstration data**

- **NOT clinically validated**
- **NOT suitable for clinical diagnosis**
- For real clinical deployment, requires:
  - Training with MeMoSA dataset (30K+ real clinical images)
  - Clinical validation studies
  - Regulatory approval (FDA, CE mark, etc.)
  - HIPAA compliance setup

### Data Validation Rules

#### Required Fields
- `patientCode`: Unique identifier (string, required)
- `name`: Patient name (string, required)

#### Optional Fields
- `age`: 0-130 years
- `contact`: Phone number
- `clinicalNotes`: Free text

#### All Enum Fields (Case-Sensitive, Lowercase)
All boolean-like fields require **exact lowercase values**:

```
Gender Values:
- male
- female
- other
- unknown

Risk Factor Values (Yes/No/Unknown):
- no
- yes
- unknown

Smoking/Alcohol/Tobacco (4-option):
- no
- occasionally
- yes
- unknown

Diet Values:
- low
- medium
- high
- unknown
```

### Common Issues & Solutions

#### Issue: "gender: `M` is not a valid enum value"
**Solution:** Use lowercase values only
```javascript
// ✗ Wrong
gender: "M"

// ✓ Correct
gender: "male"
```

#### Issue: "image file is required"
**Solution:** Use correct form field name
```javascript
// ✗ Wrong
formData.append('file', imageFile);

// ✓ Correct
formData.append('image', imageFile);
```

#### Issue: "Cast to ObjectId failed"
**Solution:** Use valid MongoDB object ID
```javascript
// Make sure patientId exists and is valid format
GET /api/patients?patientId=507f1f77bcf86cd799439011
```

---

## Testing

### Test All Services
```bash
cd project_root
python test_api.py       # Basic API tests
python test_full.py      # Full workflow tests
node scripts/verify-stack.mjs  # Stack verification
```

### Test AI Service Only
```bash
cd ai-service
python test_smoke.py     # AI service smoke test
```

---

## Production Deployment Checklist

- [ ] Change `JWT_SECRET` to long random value (environment variable)
- [ ] Set `NODE_ENV=production`
- [ ] Configure MongoDB connection string for production
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up reverse proxy (nginx/Apache)
- [ ] Configure rate limiting
- [ ] Enable CORS for specific origins only
- [ ] Set up logging and monitoring
- [ ] Configure automated backups
- [ ] Review security settings
- [ ] Load test with production data
- [ ] Set up CI/CD pipeline
- [ ] Documentation for ops team

---

## Monitoring & Maintenance

### Health Checks
```bash
# Check all services
curl http://localhost:5000/api/health/deep

# Check AI service
curl http://localhost:6001/health

# Check MongoDB
# Via API health endpoint
```

### Logs
```bash
# Frontend
npm run dev  # Shows in terminal

# Backend
npm start    # Shows in terminal

# AI Service
python app.py  # Shows in terminal

# Docker
docker compose logs -f
docker compose logs server  # Specific service
```

### Database Backup
```bash
# MongoDB backup
mongodump --uri "mongodb://connection-string" --out ./backup/

# Restore
mongorestore --uri "mongodb://connection-string" ./backup/
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # Linux/Mac

# Kill process
taskkill /PID {PID} /F
```

### MongoDB Connection Failed
```bash
# Check connection string in .env
# Verify MongoDB is running
# Test connection: mongosh --uri "your-connection-string"
```

### Module Not Found
```bash
# Frontend
npm install

# Backend
npm install

# AI Service
pip install -r requirements.txt
```

### Port Conflicts
```bash
# Change port in .env or environment variables
PORT=5001 npm start  # Backend
PORT=6001 python app.py  # AI Service
```

---

## Support & Resources

- **Test Report:** [TEST_REPORT.md](TEST_REPORT.md)
- **Quick Fix Guide:** [QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md)
- **README:** [README.md](README.md)

---

**Last Updated:** September 2, 2026  
**Version:** 1.0.0 (Demo/Prototype)  
**Status:** Ready for Testing & Demonstration
