import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Pull credentials from the environment
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "pipeline_db")

# Hardcoded fallback to the highly-privileged ETL role
DB_USER = os.environ.get("DB_USER", "etl_worker")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize the SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_etl_db():
    """
    Utility function for ETL scripts to safely open and close 
    transactions. 
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()