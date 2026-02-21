from etl.etl_models import Sample
from api.models import FrontendSample

def test_get_single_sample(client, db_session):
    # 1. Setup: Insert a test record using the ETL model (Base table)
    test_sample = Sample(
        sample_id="TEST-001",
        patient_id="ENCRYPTED_PHI_999",
        assay_type="WGS",
        metadata_col={"sequencer": "NovaSeq"}
    )
    db_session.add(test_sample)
    db_session.commit()

    # 2. Execution: Call the API endpoint
    response = client.get("/samples/TEST-001")

    # 3. Assertion: Verify the API logic and JSON serialization
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "TEST-001"
    assert data["assay_type"] == "WGS"
    assert data["metadata_col"]["sequencer"] == "NovaSeq"
    
    # Crucial Security Check: Ensure the API response does NOT contain PHI
    assert "patient_id" not in data