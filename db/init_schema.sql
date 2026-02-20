CREATE TABLE samples (
    sample_id VARCHAR(50) PRIMARY KEY,
    
    -- accommodate application-level encryption
    patient_id VARCHAR(255) NOT NULL, 
    
    assay_type VARCHAR(50) NOT NULL,
    
    -- Schema-less storage for frontend metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_samples_metadata ON samples USING GIN (metadata);


CREATE TABLE file_locations (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(50) REFERENCES samples(sample_id) ON DELETE CASCADE,
    file_type VARCHAR(50) NOT NULL, 
    s3_uri TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_file_locations_sample_id ON file_locations(sample_id);


CREATE TABLE pipeline_results (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(50) REFERENCES samples(sample_id) ON DELETE CASCADE,
    clinical_report_json_uri TEXT,
    pipeline_version VARCHAR(50),
    
    -- Secondary JSONB for pipeline-specific outputs (e.g., QC metrics, read depths)
    metrics JSONB DEFAULT '{}'::jsonb, 
    
    run_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_results_sample_id ON pipeline_results(sample_id);
CREATE INDEX idx_pipeline_results_metrics ON pipeline_results USING GIN (metrics);


CREATE TABLE api_endpoints (
    id SERIAL PRIMARY KEY,
    sample_id VARCHAR(50) REFERENCES samples(sample_id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    endpoint_url TEXT NOT NULL,
    method VARCHAR(10) DEFAULT 'GET',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_endpoints_sample_id ON api_endpoints(sample_id);