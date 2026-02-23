from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from api.database import get_db
from api.models import FrontendSample, FrontendRun
from api.schemas import SampleResponse

router = APIRouter(
    prefix="/samples",
    tags=["Samples"]
)

@router.get("/{sample_id}", response_model=SampleResponse)
def get_single_sample(sample_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific sample by its ID, including all associated sequencing runs, 
    files, pipeline results, and downstream endpoints.
    """
    stmt = (
        select(FrontendSample)
        .where(FrontendSample.sample_id == sample_id)
        # Deep eager loading to prevent N+1 query bottlenecks
        .options(
            selectinload(FrontendSample.runs).selectinload(FrontendRun.files),
            selectinload(FrontendSample.runs).selectinload(FrontendRun.results),
            selectinload(FrontendSample.runs).selectinload(FrontendRun.endpoints)
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
    
    # If filtering by assay, we must join the child run table
    if assay_type:
        stmt = stmt.join(FrontendSample.runs).where(FrontendRun.assay_type == assay_type)
        
    stmt = stmt.options(
        selectinload(FrontendSample.runs).selectinload(FrontendRun.files),
        selectinload(FrontendSample.runs).selectinload(FrontendRun.results),
        selectinload(FrontendSample.runs).selectinload(FrontendRun.endpoints)
    )
    
    stmt = stmt.order_by(FrontendSample.created_at.desc(), FrontendSample.sample_id.desc()).offset(skip).limit(limit)
    
    # .unique() is required by SQLAlchemy when fetching joined collections to deduplicate the root objects
    results = db.execute(stmt).scalars().unique().all()
    return results

@router.get("/search/metadata", response_model=List[SampleResponse])
def search_samples_by_metadata(
    key: str = Query(..., description="The metadata key to search for (e.g., 'sequencer')"),
    value: str = Query(..., description="The value of the metadata key (e.g., 'NovaSeq 6000')"),
    db: Session = Depends(get_db)
):
    """
    Query the schema-less JSONB metadata column on the nested run.
    The GIN index on runs.metadata keeps this query highly performant.
    """
    stmt = (
        select(FrontendSample)
        .join(FrontendSample.runs)
        # The ->> operator extracts a JSON object field as text for fast evaluation
        .where(FrontendRun.metadata_col[key].astext == value)
        .options(
            selectinload(FrontendSample.runs).selectinload(FrontendRun.files),
            selectinload(FrontendSample.runs).selectinload(FrontendRun.results),
            selectinload(FrontendSample.runs).selectinload(FrontendRun.endpoints)
        )
        .limit(100)
    )
    
    results = db.execute(stmt).scalars().unique().all()
    return results