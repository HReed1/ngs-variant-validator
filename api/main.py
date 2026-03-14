import os
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from api.routers import samples
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session, selectinload
from api.models import FrontendSample
from api.schemas import SampleResponse

from api.database import SessionLocal

EXPECTED_API_KEY = os.environ.get("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == EXPECTED_API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

app = FastAPI(
    title="Bioinformatics Pipeline API",
    description="Frontend API for querying non-PHI sample metadata and pipeline outputs.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"], # Explicitly allow the Vite frontend
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

app.include_router(samples.router, dependencies=[Depends(get_api_key)])

@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}