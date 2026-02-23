import sys
import os
import json
import pytest
import psycopg2
from unittest.mock import patch, MagicMock

# --- Bypassing the hyphenated directory import issue ---
# We inject the script's directory into the Python path so we can import it normally
BIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'ont-clinical-pipeline', 'bin'))
sys.path.insert(0, BIN_DIR)

import db_log_outputs

# ---------------------------------------------------------
# Test Suite for Nextflow Output Logging CLI
# ---------------------------------------------------------

@patch("db_log_outputs.psycopg2.connect")
def test_main_success_with_metrics(mock_connect, tmp_path):
    """Ensure the script successfully parses args, reads metrics, and commits to the DB."""
    # 1. Create a temporary metrics JSON file for the script to read
    metrics_file = tmp_path / "qc_metrics.json"
    metrics_file.write_text(json.dumps({"coverage_depth": "45x"}))
    
    # 2. Simulate Nextflow executing the script via command line
    test_args = [
        "db_log_outputs.py",
        "--run", "SAMP-123",
        "--report", "s3://clinical-reports/SAMP-123_final.json",
        "--version", "v1.2.0",
        "--metrics", str(metrics_file)
    ]
    
    # 3. Setup our fake database connection and cursor
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    
    # 4. Run the main function while tricking it into reading our fake sys.argv
    with patch.object(sys, 'argv', test_args):
        db_log_outputs.main()
        
    # 5. Assertions
    mock_connect.assert_called_once()
    assert mock_cur.execute.call_count == 2  # Should run 1 INSERT and 1 UPDATE
    mock_conn.commit.assert_called_once()    # Crucial: Transaction must be committed
    mock_cur.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("db_log_outputs.psycopg2.connect")
def test_main_success_without_metrics(mock_connect):
    """Ensure the script functions correctly if the optional metrics file is omitted."""
    test_args = [
        "db_log_outputs.py",
        "--run", "SAMP-456",
        "--report", "s3://clinical-reports/SAMP-456_final.json",
        "--version", "v1.2.0"
    ]
    
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    
    with patch.object(sys, 'argv', test_args):
        db_log_outputs.main()
        
    # Verify the fallback to an empty dict {} worked and it committed safely
    mock_conn.commit.assert_called_once()

@patch("db_log_outputs.psycopg2.connect")
def test_main_db_error_triggers_rollback(mock_connect):
    """Ensure that if the database throws an error, we roll back and exit with code 1."""
    test_args = [
        "db_log_outputs.py",
        "--run", "SAMP-999",
        "--report", "s3://error-test.json",
        "--version", "v1.2.0"
    ]
    
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    
    # Force the cursor to simulate a database crash (e.g., constraint violation)
    mock_cur.execute.side_effect = psycopg2.Error("Simulated Database Crash")
    
    with patch.object(sys, 'argv', test_args):
        # The script is designed to call sys.exit(1) on failure, so we must catch it
        with pytest.raises(SystemExit) as exit_info:
            db_log_outputs.main()
            
    # Assertions for catastrophic failure handling
    assert exit_info.value.code == 1           # Must exit with an error code for Nextflow to catch
    mock_conn.rollback.assert_called_once()    # Must roll back to prevent partial states
    mock_conn.commit.assert_not_called()       # Must NOT commit
    mock_cur.close.assert_called_once()        # Finally block must still clean up
    mock_conn.close.assert_called_once()