import pytest
from unittest.mock import MagicMock, patch

# This imports the module, which triggers the URL construction and engine creation
from etl.database import get_etl_db, DATABASE_URL

# ---------------------------------------------------------
# Test Suite for ETL Database Connection Manager
# ---------------------------------------------------------

def test_database_url_construction():
    """Ensure the connection string is successfully built from the conftest.py env vars."""
    assert "postgresql+psycopg2://" in DATABASE_URL
    # Verifies the user fallback or env var injection worked
    assert "etl_worker" in DATABASE_URL 

@patch("etl.database.SessionLocal")
def test_get_etl_db_yields_and_closes(mock_session_local):
    """Ensure the generator yields a session and cleanly closes it afterward."""
    # 1. Setup a fake database session
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    
    # 2. Start the generator
    db_gen = get_etl_db()
    
    # 3. Pull the session out (simulating what happens in a FastAPI Depends or ETL worker)
    db = next(db_gen)
    assert db == mock_session
    
    # The session should NOT be closed yet because the worker is still "using" it
    mock_session.close.assert_not_called()
    
    # 4. Exhaust the generator (simulating the worker finishing)
    with pytest.raises(StopIteration):
        next(db_gen)
        
    # 5. Assert the finally block successfully executed
    mock_session.close.assert_called_once()

@patch("etl.database.SessionLocal")
def test_get_etl_db_closes_on_exception(mock_session_local):
    """Ensure the finally block triggers even if the ETL worker crashes."""
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    
    db_gen = get_etl_db()
    db = next(db_gen)
    
    # Simulate a critical crash occurring while the worker is holding the session
    try:
        db_gen.throw(RuntimeError("Simulated ETL pipeline crash"))
    except RuntimeError:
        pass
        
    # The finally block MUST still execute to prevent memory leaks and zombie connections
    mock_session.close.assert_called_once()