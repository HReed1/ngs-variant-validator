import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the centralized models instead of redefining them locally
from etl.etl_models import Patient, Sample, Run, FileLocation
from etl.security import crypto_manager

# 1. ETL Database Setup (Using the highly-privileged etl_worker role)
DATABASE_URL = "postgresql+psycopg2://etl_worker:strong_etl_password@localhost:5432/pipeline_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. The Insertion Logic
def insert_pipeline_results(sample_id: str, raw_patient_id: str, assay: str, fastq_r1: str, fastq_r2: str):
    """
    Parses pipeline outputs and inserts them securely into the biological hierarchy.
    """
    
    # Concept: Encrypt the PHI before it touches the database
    encrypted_patient_id = crypto_manager.encrypt_patient_id(raw_patient_id)
    
    # Generate a unique Run ID for this specific sequencing event
    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    
    db = SessionLocal()
    
    try:
        # Step 1: Get or Create the Patient (Top of Hierarchy)
        patient = db.query(Patient).filter_by(patient_id=encrypted_patient_id).first()
        if not patient:
            patient = Patient(patient_id=encrypted_patient_id)
            db.add(patient)
            db.flush() # Ensure the DB recognizes it before creating the sample
        
        # Step 2: Get or Create the physical Sample
        sample = db.query(Sample).filter_by(sample_id=sample_id).first()
        if not sample:
            sample = Sample(sample_id=sample_id, patient_id=encrypted_patient_id)
            db.add(sample)
            db.flush()
            
        # Step 3: Create the sequencing Run (The Event)
        new_run = Run(
            run_id=run_id,
            sample_id=sample_id,
            assay_type=assay,
            metadata_col={
                "sequencer": "NovaSeq 6000",
                "flowcell": "HVKJVDSXX",
                "qc_passed": True
            }
        )
        db.add(new_run)
        
        # Step 4: Create the associated file records (Now tied to the Run, not the Sample)
        r1_file = FileLocation(run_id=run_id, file_type="FASTQ_R1", s3_uri=fastq_r1)
        r2_file = FileLocation(run_id=run_id, file_type="FASTQ_R2", s3_uri=fastq_r2)
        db.add_all([r1_file, r2_file])
        
        # Commit the transaction. If any step fails, the entire block rolls back.
        db.commit()
        print(f"Successfully inserted run {run_id} for sample {sample_id} into the database.")
        
    except Exception as e:
        db.rollback()
        print(f"ETL Insertion Failed: {e}")
        raise
    finally:
        db.close()

# Example Execution
if __name__ == "__main__":
    insert_pipeline_results(
        sample_id="SMPL-99801",
        raw_patient_id="PT-4459-X",
        assay="WGS",
        fastq_r1="s3://my-bio-bucket/runs/SMPL-99801_R1.fastq.gz",
        fastq_r2="s3://my-bio-bucket/runs/SMPL-99801_R2.fastq.gz"
    )