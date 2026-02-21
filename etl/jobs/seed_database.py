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
from etl.etl_models import Sample, FileLocation
from etl.security import crypto_manager

def generate_synthetic_data(num_records: int = 50):
    db = SessionLocal()
    
    sequencers = ["PromethION 24", "GridION", "MinION Mk1B"]
    assays = ["ONT_WGS", "ONT_RNASEQ", "ONT_TARGETED"]
    
    try:
        for i in range(num_records):
            # Generate dummy identifiers
            sample_id = f"ONT-SMPL-{random.randint(10000, 99999)}"
            raw_patient_id = f"PT-{uuid.uuid4().hex[:8].upper()}"
            
            # Encrypt the PHI before insertion
            encrypted_phi = crypto_manager.encrypt_patient_id(raw_patient_id)
            
            # Create the sample record
            sample = Sample(
                sample_id=sample_id,
                patient_id=encrypted_phi,
                assay_type=random.choice(assays),
                metadata_col={
                    "sequencer": random.choice(sequencers),
                    "flowcell": f"FLO-PRO{random.randint(100, 999)}",
                    "qc_passed": random.choice([True, True, True, False]), # Mostly True
                    "basecalling_model": "dna_r10.4.1_e8.2_400bps_hac@v4.2.0"
                }
            )
            db.add(sample)
            
            # Create the associated file locations (simulating S3 drop)
            fastq_file = FileLocation(
                sample_id=sample_id,
                file_type="FASTQ_ONT",
                s3_uri=f"s3://my-ont-bucket/runs/{sample_id}.fastq.gz"
            )
            ref_file = FileLocation(
                sample_id=sample_id,
                file_type="REFERENCE",
                s3_uri="s3://my-ont-bucket/refs/hg38.fa"
            )
            db.add_all([fastq_file, ref_file])
            
        # Commit all 50 records in a single transaction
        db.commit()
        print(f"Successfully seeded {num_records} synthetic samples into the database.")
        
    except Exception as e:
        db.rollback()
        print(f"Failed to seed database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_synthetic_data()