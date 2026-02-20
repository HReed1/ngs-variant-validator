from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

# Import our database dependencies, models, and schemas
from api.database import get_db
from api.models import FrontendSample
from api.schemas import SampleResponse

# Set up the router
router = APIRouter(
    prefix="/samples",
    tags=["Samples"]
)

@router.get("/{sample_id}", response_model=SampleResponse)
def get_single_sample(sample_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific sample by its ID, including all associated files, 
    pipeline results, and downstream endpoints.
    """
    stmt = (
        select(FrontendSample)
        .where(FrontendSample.sample_id == sample_id)
        # selectinload fetches child tables efficiently to prevent N+1 query bottlenecks
        .options(
            selectinload(FrontendSample.files),
            selectinload(FrontendSample.results),
            selectinload(FrontendSample.endpoints)
        )
    )
    
    result = db.execute(stmt).scalar_one_or_none()
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"Sample {sample_id} not found")
        
    return result

@router.get("/", response_model=List[SampleResponse])
def list_samples(
    skip: int = Query(0, ge=0, description="Pagination: rows to skip"),
    limit: int = Query(50, ge=1, le=100, description="Pagination: max rows to return"),
    assay_type: Optional[str] = Query(None, description="Filter by assay type (e.g., WGS, RNA-Seq)"),
    db: Session = Depends(get_db)
):
    """
    List samples with optional filtering by assay_type and basic pagination.
    """
    stmt = select(FrontendSample)
    
    # Apply optional assay filter
    if assay_type:
        stmt = stmt.where(FrontendSample.assay_type == assay_type)
        
    # Apply pagination and sorting (sorting by created_at is good practice)
    stmt = stmt.order_by(FrontendSample.created_at.desc()).offset(skip).limit(limit)
    
    # Execute query
    results = db.execute(stmt).scalars().all()
    return results

@router.get("/search/metadata", response_model=List[SampleResponse])
def search_samples_by_metadata(
    key: str = Query(..., description="The metadata key to search for (e.g., 'sequencer')"),
    value: str = Query(..., description="The value of the metadata key (e.g., 'NovaSeq 6000')"),
    db: Session = Depends(get_db)
):
    """
    Query the schema-less JSONB metadata column. 
    Because we added a GIN index to this column in Postgres, this search 
    will remain extremely fast even at 1,000,000+ records.
    """
    # The ->> operator in Postgres extracts a JSON object field as text
    stmt = (
        select(FrontendSample)
        .where(FrontendSample.metadata_col[key].astext == value)
        .limit(100)
    )
    
    results = db.execute(stmt).scalars().all()
    return results