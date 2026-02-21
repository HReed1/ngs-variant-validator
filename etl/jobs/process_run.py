from datetime import datetime
from sqlalchemy import create_engine, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from etl.security import crypto_manager

# 1. ETL Database Setup (Using the highly-privileged etl_worker role)
DATABASE_URL = "postgresql+psycopg2://etl_worker:strong_etl_password@localhost:5432/pipeline_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# 2. The ETL Models (Mapped to the base tables, NOT the views)
class Sample(Base):
    __tablename__ = "samples"
    
    sample_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # The ETL worker has access to this column.
    # IN PRACTICE: This should be an encrypted ciphertext string, not plain text.
    patient_id: Mapped[str] = mapped_column(String(255)) 
    
    assay_type: Mapped[str] = mapped_column(String(50))
    metadata_col: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    
    # We let the database handle created_at/updated_at automatically
    # so we don't define them here unless we need to read them back immediately.

class FileLocation(Base):
    __tablename__ = "file_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[str] = mapped_column(String(50))
    file_type: Mapped[str] = mapped_column(String(50))
    s3_uri: Mapped[str] = mapped_column(Text)


# 3. The Insertion Logic
def insert_pipeline_results(sample_id: str, raw_patient_id: str, assay: str, fastq_r1: str, fastq_r2: str):
    """
    Parses pipeline outputs and inserts them into the database.
    """
    
    # Concept: Encrypt the PHI before it touches the database
    encrypted_patient_id = crypto_manager.encrypt_patient_id(raw_patient_id)
    
    db = SessionLocal()
    
    try:
        # Create the core sample record
        new_sample = Sample(
            sample_id=sample_id,
            patient_id=encrypted_patient_id, 
            assay_type=assay,
            metadata_col={
                "sequencer": "NovaSeq 6000",
                "flowcell": "HVKJVDSXX",
                "qc_passed": True
            }
        )
        db.add(new_sample)
        
        # Create the associated file records
        r1_file = FileLocation(
            sample_id=sample_id,
            file_type="FASTQ_R1",
            s3_uri=fastq_r1
        )
        r2_file = FileLocation(
            sample_id=sample_id,
            file_type="FASTQ_R2",
            s3_uri=fastq_r2
        )
        db.add_all([r1_file, r2_file])
        
        # Commit the transaction. If any step fails, the entire block rolls back,
        # preventing orphaned files or partial sample data.
        db.commit()
        print(f"Successfully inserted sample {sample_id} into the database.")
        
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
        raw_patient_id=crypto_manager.encrypt_patient_id("PT-4459-X"),
        assay="WGS",
        fastq_r1="s3://my-bio-bucket/runs/SMPL-99801_R1.fastq.gz",
        fastq_r2="s3://my-bio-bucket/runs/SMPL-99801_R2.fastq.gz"
    )