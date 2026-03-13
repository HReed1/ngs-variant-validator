import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

# Pull credentials from the environment
DB_HOST = os.environ.get("DB_HOST", ValueError("DB_HOST environment variable is not set"))
DB_PORT = os.environ.get("DB_PORT", ValueError("DB_PORT environment variable is not set"))
DB_NAME = os.environ.get("DB_NAME", ValueError("DB_NAME environment variable is not set"))
DB_USER = os.environ.get("DB_USER", ValueError("DB_USER environment variable is not set"))
DB_PASSWORD = os.environ.get("DB_PASSWORD", ValueError("DB_PASSWORD environment variable is not set"))

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