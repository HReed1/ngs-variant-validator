import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set mock environment variables for tests BEFORE importing application code
# so that load_dotenv() uses these instead of real .env values.
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "pipeline_db"
os.environ["DB_USER"] = "etl_worker"
os.environ["DB_PASSWORD"] = "strong_etl_password"
os.environ["API_KEY"] = "test_api_key_123"

from api.main import app
from core.database import get_db

# Connect to a dedicated test database (or your local docker instance)
TEST_DATABASE_URL = "postgresql+psycopg2://etl_worker:strong_etl_password@localhost:5432/pipeline_db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database session for a test and rolls back 
    any changes after the test completes, leaving the DB pristine.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Overrides the FastAPI get_db dependency to use the test session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, headers={"X-API-Key": "test_api_key_123"})