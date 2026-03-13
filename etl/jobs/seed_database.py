import os
import random
import uuid
from cryptography.fernet import Fernet

# 1. Generate a temporary encryption key for local testing if one doesn't exist
if "ENCRYPTION_KEY" not in os.environ:
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    print(f"Set temporary ENCRYPTION_KEY: {os.environ['ENCRYPTION_KEY']}")

# Import your database session, models, and encryption manager
from etl.database import SessionLocal
from etl.etl_models import Patient, Sample, Run, FileLocation
from etl.security import crypto_manager

def generate_synthetic_data(num_runs: int = 50):
    db = SessionLocal()
    
    sequencers = ["PromethION 24", "GridION", "MinION Mk1B"]
    assays = ["ONT_WGS", "ONT_RNASEQ", "ONT_TARGETED"]
    
    # Create a smaller pool of patients and samples to demonstrate 1-to-many relationships
    num_patients = 15
    patients = [f"PT-{uuid.uuid4().hex[:8].upper()}" for _ in range(num_patients)]
    samples = [f"ONT-SMPL-{random.randint(10000, 99999)}" for _ in range(num_patients * 2)]
    
    try:
        for i in range(num_runs):
            raw_patient_id = random.choice(patients)
            sample_id = random.choice(samples)
            run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
            
            # Encrypt the PHI before insertion
            encrypted_phi = crypto_manager.encrypt_patient_id(raw_patient_id)
            
            # Step 1: Get or Create Patient
            patient_record = db.query(Patient).filter_by(patient_id=encrypted_phi).first()
            if not patient_record:
                patient_record = Patient(patient_id=encrypted_phi)
                db.add(patient_record)
                db.flush() 
            
            # Step 2: Get or Create Sample
            sample_record = db.query(Sample).filter_by(sample_id=sample_id).first()
            if not sample_record:
                sample_record = Sample(sample_id=sample_id, patient_id=encrypted_phi)
                db.add(sample_record)
                db.flush()
            
            # Generate synthetic coverage depth array (e.g., 100 data points representing genomic windows)
            # Simulating a normal distribution around 30x coverage
            synthetic_coverage = [max(0, int(random.gauss(30, 5))) for _ in range(100)]
            
            # Generate synthetic read quality (Phred scores) over time
            synthetic_quality = [max(10, min(40, int(random.gauss(32, 3)))) for _ in range(100)]

            # Step 3: Create the Run record
            run = Run(
                run_id=run_id,
                sample_id=sample_id,
                assay_type=random.choice(assays),
                metadata_col={
                    "sequencer": random.choice(sequencers),
                    "flowcell": f"FLO-PRO{random.randint(100, 999)}",
                    "qc_passed": random.choice([True, True, True, False]),
                    "basecalling_model": "dna_r10.4.1_e8.2_400bps_hac@v4.2.0",
                    # Injecting array data for the UI charting
                    "coverage_profile": synthetic_coverage,
                    "quality_profile": synthetic_quality
                }
            )
            db.add(run)
            
            # Step 4: Create the associated file locations (pointing to RUN)
            fastq_file = FileLocation(
                run_id=run_id,
                file_type="FASTQ_ONT",
                s3_uri=f"s3://my-ont-bucket/runs/{run_id}.fastq.gz"
            )
            ref_file = FileLocation(
                run_id=run_id,
                file_type="REFERENCE",
                s3_uri="s3://my-ont-bucket/refs/hg38.fa"
            )
            db.add_all([fastq_file, ref_file])
            
        # Commit all 50 records in a single transaction
        db.commit()
        print(f"Successfully seeded {num_runs} synthetic sequencing runs into the database.")
        
    except Exception as e:
        db.rollback()
        print(f"Failed to seed database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_synthetic_data()