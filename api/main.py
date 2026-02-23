from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware  # <-- ADD THIS IMPORT
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Explicitly allow the Vite frontend
    allow_credentials=True,
    allow_methods=["*"], # Allow GET, POST, OPTIONS, etc.
    allow_headers=["*"], # Crucial: Allows our custom X-API-Key header to pass through
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(samples.router)

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}