import os
import json
import importlib.util
from pathlib import Path
from unittest.mock import patch, MagicMock

# 1. Resolve the absolute path to the Nextflow bin script
test_dir = Path(__file__).resolve().parent
script_path = test_dir.parent / 'src' / 'ont-clinical-pipeline' / 'bin' / 'db_fetch_inputs.py'

# 2. Use importlib to securely load the standalone script directly from its file path
spec = importlib.util.spec_from_file_location("db_fetch_inputs", script_path)
db_fetch_inputs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_fetch_inputs)

def test_fetch_sample_files_success(tmpdir):
    """
    Test that the database fetcher correctly queries Postgres and writes the JSON output.
    We mock psycopg2 to prevent actual database connections during the unit test.
    """
    tmpdir.chdir()
    
    # 1. Arrange: Define our mock data
    target_sample = "SRR11032656"
    mock_db_results = [
        ("FASTQ_ONT", "s3://ngs-variant-validator-work/raw/SRR11032656.fastq.gz"),
        ("REFERENCE", "s3://ngs-variant-validator-work/ref/hg38.fasta")
    ]
    
    # 2. Patch (Mock) the database connection inside the loaded module
    with patch.object(db_fetch_inputs, 'psycopg2') as mock_psycopg2:
        # Configure the mock cursor to return our fake data when fetchall() is called
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_db_results
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_connection
        
        # 3. Act: Run the actual function
        db_fetch_inputs.fetch_sample_files(
            sample_id=target_sample,
            db_host="fake_host",
            db_user="fake_user",
            db_pass="fake_pass",
            db_name="fake_db"
        )
        
        # 4. Assert: Verify the SQL query was executed with the right sample ID
        mock_cursor.execute.assert_called_once()
        executed_query, query_params = mock_cursor.execute.call_args[0]
        assert query_params == (target_sample,)
        
        # 5. Assert: Verify the JSON file was created perfectly
        assert os.path.exists('inputs.json')
        with open('inputs.json', 'r') as f:
            output_data = json.load(f)
            
        assert output_data["sample_id"] == target_sample
        assert output_data["reads"] == "s3://ngs-variant-validator-work/raw/SRR11032656.fastq.gz"
        assert output_data["reference"] == "s3://ngs-variant-validator-work/ref/hg38.fasta"