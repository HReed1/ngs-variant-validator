from etl.etl_models import Patient, Sample, Run

def test_get_single_sample(client, db_session):
    # 1. Setup: Insert the full hierarchy using the ETL models (Base tables)
    test_patient = Patient(patient_id="ENCRYPTED_PHI_999")
    test_sample = Sample(sample_id="TEST-001", patient_id="ENCRYPTED_PHI_999")
    test_run = Run(
        run_id="RUN-TEST-001",
        sample_id="TEST-001",
        assay_type="WGS",
        metadata_col={"sequencer": "NovaSeq"}
    )
    
    db_session.add_all([test_patient, test_sample, test_run])
    db_session.commit()

    # 2. Execution: Call the API endpoint
    response = client.get("/samples/TEST-001")

    # 3. Assertion: Verify the API logic and JSON serialization
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "TEST-001"
    
    # Assert against the nested run data
    assert data["runs"][0]["assay_type"] == "WGS"
    assert data["runs"][0]["metadata_col"]["sequencer"] == "NovaSeq"
    
    # Crucial Security Check: Ensure the API response does NOT contain PHI
    assert "patient_id" not in data
    # Ensure our MD5 surrogate key projection worked successfully
    assert "patient_hash" in data