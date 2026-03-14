import os
import random
import uuid
from cryptography.fernet import Fernet

# 1. Generate a temporary encryption key for local testing if one doesn't exist
if "ENCRYPTION_KEY" not in os.environ:
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    print(f"Set temporary ENCRYPTION_KEY: {os.environ['ENCRYPTION_KEY']}")

# Import your database session, models, and encryption manager
from core.database import SessionLocal
from etl.etl_models import Patient, Sample, Run, FileLocation
from etl.security import crypto_manager

def generate_synthetic_data(num_runs: int = 50):
    db = SessionLocal()
    
    sequencers = ["PromethION 24", "GridION", "MinION Mk1B"]
    assays = ["ONT_WGS", "ONT_RNASEQ", "ONT_TARGETED"]
    
    num_patients = 15
    patients = [f"PT-{uuid.uuid4().hex[:8].upper()}" for _ in range(num_patients)]
    samples = [f"ONT-SMPL-{random.randint(10000, 99999)}" for _ in range(num_patients * 2)]
    
    try:
        # --- 1. Generate 49 Standard Synthetic Runs ---
        for i in range(num_runs - 1):
            raw_patient_id = random.choice(patients)
            sample_id = random.choice(samples)
            run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
            
            encrypted_phi = crypto_manager.encrypt_patient_id(raw_patient_id)
            
            patient_record = db.query(Patient).filter_by(patient_id=encrypted_phi).first()
            if not patient_record:
                patient_record = Patient(patient_id=encrypted_phi)
                db.add(patient_record)
                db.flush() 
            
            sample_record = db.query(Sample).filter_by(sample_id=sample_id).first()
            if not sample_record:
                sample_record = Sample(sample_id=sample_id, patient_id=encrypted_phi)
                db.add(sample_record)
                db.flush()
            
            synthetic_coverage = [max(0, int(random.gauss(30, 5))) for _ in range(100)]
            synthetic_quality = [max(10, min(40, int(random.gauss(32, 3)))) for _ in range(100)]

            run = Run(
                run_id=run_id,
                sample_id=sample_id,
                assay_type=random.choice(assays),
                metadata_col={
                    "sequencer": random.choice(sequencers),
                    "qc_passed": random.choice([True, True, True, False]),
                    "coverage_profile": synthetic_coverage,
                    "quality_profile": synthetic_quality
                }
            )
            db.add(run)
            
            db.add_all([
                FileLocation(run_id=run_id, file_type="FASTQ_ONT", s3_uri=f"s3://my-ont-bucket/runs/{run_id}.fastq.gz"),
                FileLocation(run_id=run_id, file_type="REFERENCE", s3_uri="s3://my-ont-bucket/refs/hg38.fa")
            ])

        # --- 2. Generate the 1 "Golden Record" for Testing ---
        golden_run_id = "RUN-VIRAL-TEST"
        golden_sample_id = "SMPL-VIRAL-REAL"
        golden_phi = crypto_manager.encrypt_patient_id("PT-REAL-VIRAL")
        
        # Create Golden Patient/Sample
        db.add_all([
            Patient(patient_id=golden_phi),
            Sample(sample_id=golden_sample_id, patient_id=golden_phi)
        ])
        db.flush()
        
        db.add(Run(
            run_id=golden_run_id,
            sample_id=golden_sample_id,
            assay_type="ONT_WGS",
            metadata_col={"sequencer": "MinION Mk1B", "qc_passed": True, "note": "Micro-Dataset Execution Test"}
        ))
        
        # --- ACTIVE: MICRO DATASET (SARS-CoV-2 ~30kb) ---
        # Lightning fast, perfect for testing the DAG orchestration without burning compute
        db.add_all([
            FileLocation(
                run_id=golden_run_id, 
                file_type="FASTQ_ONT", 
                # A real, small SARS-CoV-2 Nanopore FASTQ from the European Nucleotide Archive (ENA) public HTTP endpoint
                s3_uri="http://ftp.sra.ebi.ac.uk/vol1/fastq/SRR111/044/SRR11140744/SRR11140744.fastq.gz" 
            ),
            FileLocation(
                run_id=golden_run_id, 
                file_type="REFERENCE", 
                # SARS-CoV-2 Reference Genome (NC_045512.2) from NCBI
                s3_uri="https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/009/858/895/GCF_009858895.2_ASM985889v3/GCF_009858895.2_ASM985889v3_genomic.fna.gz"
            )
        ])

        # --- INACTIVE: HEAVY HUMAN DATASET (HG002 ~3GB) ---
        # db.add_all([
        #     FileLocation(
        #         run_id=golden_run_id, 
        #         file_type="FASTQ_ONT", 
        #         s3_uri="https://s3-us-west-2.amazonaws.com/human-pangenomics/NHGRI_UCSC_panel/HG002/hpp_HG002_NA24385_son_v1/nanopore/downsampled/standard_unsheared/HG002_ucsc_Jan_2019_Guppy_3.4.4.fastq.gz"
        #     ),
        #     FileLocation(
        #         run_id=golden_run_id, 
        #         file_type="REFERENCE", 
        #         s3_uri="https://1000genomes.s3.amazonaws.com/1000G_2504_high_coverage/additional_references/GRCh38/GRCh38_full_analysis_set_plus_decoy_hla.fa"
        #     )
        # ])

        # Commit all records
        db.commit()
        print(f"Successfully seeded {num_runs} synthetic sequencing runs, including Golden Record: {golden_run_id}.")
        
    except Exception as e:
        db.rollback()
        print(f"Failed to seed database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_synthetic_data()