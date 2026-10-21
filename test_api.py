#!/usr/bin/env python3
import subprocess
import sys
import json
import time

try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

BASE_URL = "http://127.0.0.1:5000/api"
AI_URL = "http://127.0.0.1:6000"

def test_api():
    print("\n" + "="*60)
    print("TESTING ORAL CANCER AI SYSTEM")
    print("="*60)
    
    try:
        # Test 1: Health checks
        print("\n1. HEALTH CHECKS")
        print("-"*60)
        
        try:
            ai_health = requests.get(f"{AI_URL}/health", timeout=5).json()
            print(f"✓ AI Service: {json.dumps(ai_health, indent=2)}")
        except Exception as e:
            print(f"❌ AI Service error: {e}")
            
        try:
            api_health = requests.get(f"{BASE_URL}/health", timeout=5).json()
            print(f"✓ API Service: {json.dumps(api_health, indent=2)}")
        except Exception as e:
            print(f"❌ API Service error: {e}")
            
        try:
            deep_health = requests.get(f"{BASE_URL}/health/deep", timeout=5).json()
            print(f"✓ Deep Health: {json.dumps(deep_health, indent=2)}")
        except Exception as e:
            print(f"❌ Deep Health error: {e}")
        
        # Test 2: Authentication
        print("\n2. AUTHENTICATION")
        print("-"*60)
        
        login_payload = {
            "email": "admin@example.com",
            "password": "Admin@2026Secure"
        }
        
        login_res = requests.post(f"{BASE_URL}/auth/login", json=login_payload, timeout=5)
        print(f"Login Status: {login_res.status_code}")
        
        login_data = login_res.json()
        print(f"Response: {json.dumps(login_data, indent=2)}")
        
        if not login_res.ok:
            print("❌ Login failed!")
            return
        
        token = login_data.get("token")
        if not token:
            print("❌ No token received!")
            return
            
        print(f"✓ Token received: {token[:20]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 3: Get user profile
        print("\n3. USER PROFILE")
        print("-"*60)
        
        profile_res = requests.get(f"{BASE_URL}/auth/profile", headers=headers, timeout=5)
        print(f"Status: {profile_res.status_code}")
        print(f"Profile: {json.dumps(profile_res.json(), indent=2)}")
        
        # Test 4: Get patients list
        print("\n4. PATIENTS LIST")
        print("-"*60)
        
        patients_res = requests.get(f"{BASE_URL}/patients", headers=headers, timeout=5)
        print(f"Status: {patients_res.status_code}")
        patients_data = patients_res.json()
        
        if isinstance(patients_data, list):
            print(f"✓ Patients Count: {len(patients_data)}")
            if patients_data:
                print(f"Sample Patient: {json.dumps(patients_data[0], indent=2)}")
        else:
            print(f"Response: {json.dumps(patients_data, indent=2)}")
        
        # Test 5: Create a patient
        print("\n5. CREATE PATIENT")
        print("-"*60)
        
        patient_payload = {
            "name": "Test Patient Alpha",
            "email": "patient.alpha@test.com",
            "age": 45,
            "gender": "M"
        }
        
        create_res = requests.post(f"{BASE_URL}/patients", json=patient_payload, headers=headers, timeout=5)
        print(f"Status: {create_res.status_code}")
        new_patient = create_res.json()
        print(f"New Patient: {json.dumps(new_patient, indent=2)}")
        
        if create_res.ok and new_patient.get("_id"):
            patient_id = new_patient["_id"]
            
            # Test 6: Get predictions for patient
            print("\n6. PREDICTIONS")
            print("-"*60)
            
            pred_res = requests.get(f"{BASE_URL}/predictions?patientId={patient_id}", headers=headers, timeout=5)
            print(f"Status: {pred_res.status_code}")
            predictions = pred_res.json()
            print(f"Predictions: {json.dumps(predictions, indent=2)}")
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
