from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Child Schemas ---
class FileLocationResponse(BaseModel):
    id: int
    file_type: str
    s3_uri: str
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class PipelineResultResponse(BaseModel):
    id: int
    clinical_report_json_uri: Optional[str]
    pipeline_version: Optional[str]
    metrics: Dict[str, Any]
    run_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ApiEndpointResponse(BaseModel):
    id: int
    service_name: str
    endpoint_url: str
    method: str
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- The Sequencing Event (Run) Schema ---
class RunResponse(BaseModel):
    run_id: str
    assay_type: str
    metadata_col: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Nested relationships for the Run
    files: List[FileLocationResponse] = []
    results: List[PipelineResultResponse] = []
    endpoints: List[ApiEndpointResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- The Physical Material (Sample) Schema ---
class SampleResponse(BaseModel):
    sample_id: str
    patient_hash: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # A single sample can have multiple sequencing runs (e.g., WGS & RNA-Seq)
    runs: List[RunResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# --- The Root Subject (Patient) Schema ---
class PatientResponse(BaseModel):
    patient_hash: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    samples: List[SampleResponse] = []
    
    model_config = ConfigDict(from_attributes=True)