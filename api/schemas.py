from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Child Schemas ---
class FileLocationResponse(BaseModel):
    id: int
    file_type: str
    s3_uri: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PipelineResultResponse(BaseModel):
    id: int
    clinical_report_json_uri: Optional[str]
    pipeline_version: Optional[str]
    metrics: Dict[str, Any]
    run_date: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ApiEndpointResponse(BaseModel):
    id: int
    service_name: str
    endpoint_url: str
    method: str
    
    model_config = ConfigDict(from_attributes=True)

# --- Parent Schema ---
class SampleResponse(BaseModel):
    sample_id: str
    assay_type: str
    metadata_col: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    # Nested relationships
    files: List[FileLocationResponse] = []
    results: List[PipelineResultResponse] = []
    endpoints: List[ApiEndpointResponse] = []
    
    model_config = ConfigDict(from_attributes=True)