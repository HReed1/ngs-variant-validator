CREATE TABLE samples (
    sample_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    assay_type VARCHAR(20) NOT NULL
);

CREATE TABLE file_locations (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(50) REFERENCES samples(sample_id),
    file_type VARCHAR(20) NOT NULL, -- e.g., 'FASTQ_R1', 'FASTQ_R2', 'REFERENCE'
    s3_uri TEXT NOT NULL
);

CREATE TABLE pipeline_results (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(50) REFERENCES samples(sample_id),
    clinical_report_json_uri TEXT,
    pipeline_version VARCHAR(20),
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);