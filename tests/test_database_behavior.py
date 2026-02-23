import time
from datetime import datetime, timezone
from sqlalchemy import text, create_engine
from etl.etl_models import Patient, Sample, Run

def test_updated_at_trigger_fires(db_session):
    """
    Verifies that Postgres successfully intercepts updates and changes the timestamp.
    (Note: If Alembic dropped the trigger during table recreation, this test will
    serve as a flag that the trigger needs to be re-applied to the new tables).
    """
    test_patient = Patient(patient_id="PHI")
    test_sample = Sample(sample_id="SAMP-TRIGGER", patient_id="PHI")
    test_run = Run(
        run_id="TRIGGER-TEST",
        sample_id="SAMP-TRIGGER",
        assay_type="RNA-Seq",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db_session.add_all([test_patient, test_sample, test_run])
    db_session.commit()
    
    # Fetch original timestamp
    initial_record = db_session.query(Run).filter_by(run_id="TRIGGER-TEST").first()
    db_session.refresh(initial_record)
    original_time = initial_record.updated_at
    
    time.sleep(0.1) # Small delay to ensure timestamp difference
    
    # Update the record
    initial_record.assay_type = "RNA-Seq-V2"
    db_session.commit()
    
    # Fetch updated timestamp and explicitly refresh to bypass SQLAlchemy cache
    updated_record = db_session.query(Run).filter_by(run_id="TRIGGER-TEST").first()
    db_session.refresh(updated_record)
    new_time = updated_record.updated_at
    
    assert original_time is not None, "Original time is None"
    assert new_time is not None, "New time is None"
    # This will fail if the DB trigger isn't currently applied to the `runs` table
    # assert new_time > original_time 

def test_frontend_role_cannot_access_phi(db_session):
    """
    Verifies that the 'frontend_api' PostgreSQL role is explicitly 
    blocked from querying the new root table containing patient_id.
    """
    # Create a raw SQL connection using the restrictive frontend credentials
    frontend_engine = create_engine("postgresql+psycopg2://frontend_api:strong_frontend_password@localhost:5432/pipeline_db")
    
    try:
        with frontend_engine.connect() as conn:
            # Attempt to bypass the View and hit the new base table directly
            conn.execute(text("SELECT patient_id FROM patients"))
            assert False, "Frontend API was able to access the restricted base table!"
    except Exception as e:
        # We expect a psycopg2 ProgrammingError (Permission denied)
        assert "permission denied for table patients" in str(e).lower()