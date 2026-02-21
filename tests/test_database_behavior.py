import time
from sqlalchemy import text
from etl.etl_models import Sample

def test_updated_at_trigger_fires(db_session):
    """
    Verifies that the Postgres trigger 'update_modified_column' 
    successfully intercepts updates and changes the timestamp.
    """
    # Insert initial record
    test_sample = Sample(
        sample_id="TRIGGER-TEST",
        patient_id="PHI",
        assay_type="RNA-Seq"
    )
    db_session.add(test_sample)
    db_session.commit()
    
    # Fetch original timestamp
    initial_record = db_session.query(Sample).filter_by(sample_id="TRIGGER-TEST").first()
    original_time = initial_record.updated_at
    
    time.sleep(0.1) # Small delay to ensure timestamp difference
    
    # Update the record
    initial_record.assay_type = "RNA-Seq-V2"
    db_session.commit()
    
    # Fetch updated timestamp
    updated_record = db_session.query(Sample).filter_by(sample_id="TRIGGER-TEST").first()
    new_time = updated_record.updated_at
    
    assert new_time > original_time

def test_frontend_role_cannot_access_phi(db_session):
    """
    Verifies that the 'frontend_api' PostgreSQL role is explicitly 
    blocked from querying the base table containing patient_id.
    """
    # Create a raw SQL connection using the restrictive frontend credentials
    frontend_engine = create_engine("postgresql+psycopg2://frontend_api:strong_frontend_password@localhost:5432/pipeline_db")
    
    try:
        with frontend_engine.connect() as conn:
            # Attempt to bypass the View and hit the base table directly
            conn.execute(text("SELECT patient_id FROM samples"))
            # If the query succeeds, the security design has failed
            assert False, "Frontend API was able to access the restricted base table!"
    except Exception as e:
        # We expect a psycopg2 ProgrammingError (Permission denied)
        assert "permission denied for table samples" in str(e).lower()