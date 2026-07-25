import httpx

def run_tests():
    print("Testing POST /api/v1/complaints/public/submit")
    payload = {
        "transaction_id": "UTR2025TEST001",
        "victim_name": "Test User",
        "victim_email": "test@example.com",
        "incident_type": "DIGITAL_ARREST",
        "amount_lost": 50000.0,
        "description": "Test complaint from script"
    }
    
    with httpx.Client(base_url="http://localhost:8000") as client:
        res = client.post("/api/v1/complaints/public/submit", json=payload)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}. Response: {res.text}"
        
        data = res.json()
        assert data["success"] is True
        complaint_number = data["complaint_number"]
        print(f"  [OK] Submitted successfully. Tracking ID: {complaint_number}")
        
        print("\nTesting GET /api/v1/complaints/public/status/{id}")
        status_res = client.get(f"/api/v1/complaints/public/status/{complaint_number}")
        assert status_res.status_code == 200, f"Expected 200, got {status_res.status_code}"
        status_data = status_res.json()
        assert status_data["success"] is True
        assert status_data["complaint_number"] == complaint_number
        print(f"  [OK] Status check successful: {status_data['status']}")
        
        print("\nTesting GET /api/v1/reports?report_type=VICTIM_COMPLAINT (Admin View)")
        admin_res = client.get("/api/v1/reports?report_type=VICTIM_COMPLAINT")
        assert admin_res.status_code == 200
        admin_data = admin_res.json()
        assert len(admin_data["data"]) > 0
        found = False
        for report in admin_data["data"]:
            if report["report_number"] == complaint_number:
                found = True
                break
        assert found is True, "Complaint was not found in the reports list!"
        print(f"  [OK] Admin can see the complaint in the Reports list.")
        
        print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
