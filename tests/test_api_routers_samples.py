import pytest
from datetime import datetime, timezone
from sqlalchemy import text
from api.models import FrontendSample

# ---------------------------------------------------------
# Test Suite for FastAPI Samples Router (REQ-API-01)
# ---------------------------------------------------------


@pytest.fixture
def seed_samples(db_session):
    """
    Seeds the test database with dummy records by inserting directly into 
    the base 'samples' table to satisfy NOT NULL constraints without 
    violating the FrontendSample ORM view schema.
    """
    insert_stmt = text("""
        INSERT INTO samples (sample_id, patient_id, assay_type, metadata, created_at, updated_at)
        VALUES 
        ('SAMP-TEST-001', 'PAT-TEST-001', 'WGS', '{"sequencer": "NovaSeq 6000", "status": "complete"}', NOW(), NOW()),
        ('SAMP-TEST-002', 'PAT-TEST-002', 'RNA-Seq', '{"sequencer": "MiSeq", "status": "processing"}', NOW(), NOW())
    """)
    
    db_session.execute(insert_stmt)
    db_session.flush()

def test_get_single_sample_success(client, seed_samples):
    """Ensure we can retrieve a specific sample and its relationships."""
    response = client.get("/samples/SAMP-TEST-001")
    
    assert response.status_code == 200
    data = response.json()
    assert data["sample_id"] == "SAMP-TEST-001"
    assert data["assay_type"] == "WGS"

def test_get_single_sample_not_found(client):
    """Ensure a missing sample correctly returns a 404 instead of crashing."""
    response = client.get("/samples/SAMP-DOES-NOT-EXIST")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Sample SAMP-DOES-NOT-EXIST not found"

def test_list_samples_no_filters(client, seed_samples):
    """Ensure the base list endpoint returns all samples (up to the limit)."""
    # Use the maximum allowed limit (100) to respect FastAPI's le=100 validation.
    # Because the endpoint sorts by created_at.desc(), our freshly seeded 
    # test data will always be at the top of these results anyway!
    response = client.get("/samples/?limit=100")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    
    # Extract just the IDs to verify our seeded data is present
    returned_ids = [s["sample_id"] for s in data]
    assert "SAMP-TEST-001" in returned_ids
    assert "SAMP-TEST-002" in returned_ids

def test_list_samples_with_assay_filter(client, seed_samples):
    """Ensure the assay_type query parameter successfully filters the SQL query."""
    response = client.get("/samples/?assay_type=RNA-Seq")
    
    assert response.status_code == 200
    data = response.json()
    
    # We seeded exactly one RNA-Seq sample
    assert len(data) == 1
    assert data[0]["sample_id"] == "SAMP-TEST-002"
    assert data[0]["assay_type"] == "RNA-Seq"

def test_list_samples_pagination(client, seed_samples):
    """Ensure the skip and limit parameters correctly slice the results."""
    # Limit to 1 result
    response_limit = client.get("/samples/?limit=1")
    assert response_limit.status_code == 200
    assert len(response_limit.json()) == 1
    
    # Skip the first result
    response_skip = client.get("/samples/?skip=1&limit=1")
    assert response_skip.status_code == 200
    assert len(response_skip.json()) == 1
    
    # Ensure they didn't return the exact same record
    assert response_limit.json()[0]["sample_id"] != response_skip.json()[0]["sample_id"]

def test_search_samples_by_metadata_success(client, seed_samples):
    """Ensure the JSONB search query correctly hunts through the schema-less column."""
    # Hunt for the specific sequencer used in Sample 1
    response = client.get("/samples/search/metadata?key=sequencer&value=NovaSeq 6000")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["sample_id"] == "SAMP-TEST-001"
    assert data[0]["metadata_col"]["sequencer"] == "NovaSeq 6000"

def test_search_samples_by_metadata_no_results(client, seed_samples):
    """Ensure searching for a missing metadata value cleanly returns an empty list."""
    response = client.get("/samples/search/metadata?key=sequencer&value=PacBio Revio")
    
    assert response.status_code == 200
    assert response.json() == []