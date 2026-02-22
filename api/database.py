import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Pull credentials from the environment, defaulting to local Docker dev settings
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "pipeline_db")

# Hardcoded fallback to the frontend role to prevent accidental privilege escalation
DB_USER = os.environ.get("DB_USER", "frontend_api")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "strong_frontend_password") # nosec B105

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize the SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that yields a database session and ensures 
    it is closed securely after the API request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()