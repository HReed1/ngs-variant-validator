export interface FileLocation {
    id: number;
    file_type: string;
    s3_uri: string;
    created_at?: string;
}

export interface PipelineResult {
    id: number;
    clinical_report_json_uri?: string;
    pipeline_version?: string;
    metrics: Record<string, any>;
    run_date?: string;
}

export interface Run {
    run_id: string;
    assay_type: string;
    metadata_col: Record<string, any>;
    created_at?: string;
    updated_at?: string;
    files: FileLocation[];
    results: PipelineResult[];
}

// Ensure this specific block exists and is exported
export interface Sample {
    sample_id: string;
    patient_hash: string;
    created_at?: string;
    updated_at?: string;
    runs: Run[];
}