#!/usr/bin/env python3
import subprocess
import sys
import json
import time
import os

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

BASE_URL = "http://127.0.0.1:5000/api"
AI_URL = "http://127.0.0.1:6000"

def test_ai_inference():
    print("\n" + "="*60)
    print("TESTING AI INFERENCE & PREDICTIONS")
    print("="*60)
    
    try:
        # Find a test image
        test_image_dir = "ai-service/demo-dataset/test"
        test_images = []
        
        if os.path.exists(test_image_dir):
            for root, dirs, files in os.walk(test_image_dir):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_images.append(os.path.join(root, file))
                        if len(test_images) >= 1:
                            break
                if test_images:
                    break
        
        if test_images:
            test_image_path = test_images[0]
            print(f"\n[OK] Found test image: {test_image_path}")
            
            # Test AI inference endpoint
            print("\n1. AI IMAGE INFERENCE")
            print("-"*60)
            
            with open(test_image_path, 'rb') as f:
                files = {'file': f}
                inf_res = requests.post(f"{AI_URL}/predict/image", files=files, timeout=10)
            
            print(f"Status: {inf_res.status_code}")
            inf_data = inf_res.json()
            print(f"Response: {json.dumps(inf_data, indent=2)}")
            
            if inf_res.ok:
                print("[OK] AI Inference successful!")
                
                # Check prediction results
                predictions = inf_data.get("predictions", {})
                for class_name, confidence in predictions.items():
                    print(f"  - {class_name}: {confidence:.2%}")
        else:
            print("[WARN] No test images found")
        
        # Test clinical inference
        print("\n2. CLINICAL MODEL INFERENCE")
        print("-"*60)
        
        clinical_data = {
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
        
        clin_res = requests.post(f"{AI_URL}/predict/clinical", json=clinical_data, timeout=10)
        print(f"Status: {clin_res.status_code}")
        clin_data = clin_res.json()
        print(f"Response: {json.dumps(clin_data, indent=2)}")
        
        if clin_res.ok:
            print("[OK] Clinical inference successful!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

def test_predictions_flow():
    print("\n" + "="*60)
    print("TESTING PREDICTIONS WORKFLOW")
    print("="*60)
    
    try:
        # Login
        login_payload = {
            "email": "admin@example.com",
            "password": "Admin@2026Secure"
        }
        login_res = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=5)
        
        if not login_res.ok:
            print("[ERROR] Login failed!")
            return
        
        token = login_res.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"[OK] Authenticated")
        
        # Create a patient
        print("\n1. CREATE PATIENT")
        print("-"*60)
        
        patient_payload = {
            "patientCode": "TEST001",
            "name": "Test Patient Alpha",
            "age": 50,
            "gender": "M",
            "contact": "9876543210",
            "smoking": "yes",
            "betelQuid": "no",
            "alcohol": "yes",
            "tobaccoUse": "yes",
            "hpvInfection": "no",
            "chronicSunExposure": "yes",
            "poorOralHygiene": "yes",
            "dietFruitsVegetables": "low",
            "familyHistoryOfCancer": "yes",
            "compromisedImmuneSystem": "no",
            "oralLesions": "yes",
            "unexplainedBleeding": "no",
            "difficultySwallowing": "no",
            "whiteOrRedPatches": "yes"
        }
        
        create_res = requests.post(f"{BASE_URL}/patients", json=patient_payload, headers=headers, timeout=5)
        print(f"Status: {create_res.status_code}")
        
        patient = create_res.json()
        print(f"Response: {json.dumps(patient, indent=2)}")
        
        if not create_res.ok:
            print(f"[ERROR] Patient creation failed!")
            return
        
        patient_id = patient.get("_id") or patient.get("id") or patient.get("patientCode")
        print(f"[OK] Patient created: {patient_id}")
        print(f"  Name: {patient.get('name', 'N/A')}")
        print(f"  Code: {patient.get('patientCode', 'N/A')}")
        
        # Get predictions for patient
        print("\n2. GET PREDICTIONS")
        print("-"*60)
        
        pred_res = requests.get(f"{BASE_URL}/predictions?patientId={patient_id}", headers=headers, timeout=5)
        print(f"Status: {pred_res.status_code}")
        predictions = pred_res.json()
        
        if isinstance(predictions, list):
            print(f"[OK] Predictions Count: {len(predictions)}")
            if predictions:
                print(f"Sample: {json.dumps(predictions[0], indent=2)}")
        else:
            print(f"Response: {json.dumps(predictions, indent=2)}")
        
        # Update patient
        print("\n3. UPDATE PATIENT")
        print("-"*60)
        
        update_payload = {
            "clinicalNotes": "Updated test notes - patient showing improvement"
        }
        
        update_res = requests.put(f"{BASE_URL}/patients/{patient_id}", json=update_payload, headers=headers, timeout=5)
        print(f"Status: {update_res.status_code}")
        
        if update_res.ok:
            print("[OK] Patient updated successfully")
        else:
            print(f"Error: {json.dumps(update_res.json(), indent=2)}")
        
        print("\n" + "="*60)
        print("[OK] PREDICTIONS WORKFLOW COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_inference()
    test_predictions_flow()
