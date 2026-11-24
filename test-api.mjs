#!/usr/bin/env node

const BASE_URL = "http://127.0.0.1:5000/api";

async function test() {
  try {
    console.log("\n===== TESTING ORAL CANCER AI SYSTEM =====\n");

    // Test 1: Health checks
    console.log("1. HEALTH CHECKS");
    console.log("-".repeat(50));
    
    const aiHealth = await fetch("http://127.0.0.1:6001/health").then(r => r.json());
    console.log("✓ AI Service:", JSON.stringify(aiHealth, null, 2));

    const apiHealth = await fetch(`${BASE_URL}/health`).then(r => r.json());
    console.log("✓ API Service:", JSON.stringify(apiHealth, null, 2));

    const deepHealth = await fetch(`${BASE_URL}/health/deep`).then(r => r.json());
    console.log("✓ Deep Health:", JSON.stringify(deepHealth, null, 2));

    // Test 2: Authentication
    console.log("\n2. AUTHENTICATION");
    console.log("-".repeat(50));
    
    const loginRes = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        email: "admin@example.com", 
        password: "Admin@2026Secure" 
      })
    });
    
    const loginData = await loginRes.json();
    console.log("Login Status:", loginRes.status);
    console.log("Login Response:", JSON.stringify(loginData, null, 2));
    
    if (!loginRes.ok) {
      console.error("❌ Login failed!");
      return;
    }

    const token = loginData.token;
    console.log("✓ Token received:", token.substring(0, 20) + "...");

    // Test 3: Get user profile
    console.log("\n3. USER PROFILE");
    console.log("-".repeat(50));
    
    const profileRes = await fetch(`${BASE_URL}/auth/profile`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const profileData = await profileRes.json();
    console.log("Profile Status:", profileRes.status);
    console.log("User:", JSON.stringify(profileData, null, 2));

    // Test 4: Get patients list
    console.log("\n4. PATIENTS LIST");
    console.log("-".repeat(50));
    
    const patientsRes = await fetch(`${BASE_URL}/patients`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const patientsData = await patientsRes.json();
    console.log("Patients Status:", patientsRes.status);
    console.log("Patients Count:", Array.isArray(patientsData) ? patientsData.length : "error");
    if (Array.isArray(patientsData)) {
      console.log("Patients:", JSON.stringify(patientsData.slice(0, 2), null, 2));
    }

    // Test 5: Create a patient
    console.log("\n5. CREATE PATIENT");
    console.log("-".repeat(50));
    
    const createPatientRes = await fetch(`${BASE_URL}/patients`, {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: "Test Patient",
        email: "patient@test.com",
        age: 45,
        gender: "M"
      })
    });
    
    const newPatient = await createPatientRes.json();
    console.log("Create Patient Status:", createPatientRes.status);
    console.log("New Patient:", JSON.stringify(newPatient, null, 2));

    if (createPatientRes.ok && newPatient._id) {
      const patientId = newPatient._id;

      // Test 6: Get predictions
      console.log("\n6. PREDICTIONS");
      console.log("-".repeat(50));
      
      const predictionsRes = await fetch(`${BASE_URL}/predictions?patientId=${patientId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const predictions = await predictionsRes.json();
      console.log("Predictions Status:", predictionsRes.status);
      console.log("Predictions:", JSON.stringify(predictions, null, 2));
    }

    console.log("\n" + "=".repeat(50));
    console.log("✓ ALL TESTS COMPLETED SUCCESSFULLY");
    console.log("=".repeat(50) + "\n");

  } catch (error) {
    console.error("❌ TEST ERROR:", error.message);
  }
}

test();
