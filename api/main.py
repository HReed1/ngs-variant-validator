from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from api.routers import samples
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session, selectinload
from api.models import FrontendSample
from api.schemas import SampleResponse

# Database Setup (using the frontend_api role we created)
DATABASE_URL = "postgresql+psycopg2://frontend_api:strong_frontend_password@localhost:5432/pipeline_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Bioinformatics Pipeline API",
    description="Frontend API for querying non-PHI sample metadata and pipeline outputs.",
    version="1.0.0"
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/samples/{sample_id}", response_model=SampleResponse)
def get_sample(sample_id: str, db: Session = Depends(get_db)):
    # selectinload prevents the "N+1 query problem" by fetching all related data efficiently
    stmt = (
        select(FrontendSample)
        .where(FrontendSample.sample_id == sample_id)
        .options(
            selectinload(FrontendSample.files),
            selectinload(FrontendSample.results),
            selectinload(FrontendSample.endpoints)
        )
    )
    
    result = db.execute(stmt).scalar_one_or_none()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Sample not found")
        
    return result

app.include_router(samples.router)

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}