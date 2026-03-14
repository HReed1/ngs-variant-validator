import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

# We remove the hardcoded fallbacks to prevent privilege escalation.
# The process running this (API or ETL) MUST provide its specific role in the environment.
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "pipeline_db")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

if not DB_USER or not DB_PASSWORD:
    raise ValueError("CRITICAL: DB_USER and DB_PASSWORD must be set in the environment.")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Unified session generator for safe transactions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
