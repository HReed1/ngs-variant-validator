import sys
import os
import json
from unittest.mock import patch, MagicMock

# Dynamically find the project root and point to the bin directory
# This resolves correctly no matter how deep the tests/ folder is nested
project_root = Path(__file__).resolve().parent
while project_root.name != 'ngs-variant-validator' and project_root.parent != project_root:
    project_root = project_root.parent

bin_path = project_root / 'src' / 'ont-clinical-pipeline' / 'bin'
sys.path.insert(0, bin_path)

import db_fetch_inputs

def test_fetch_sample_files_success(temp_workspace):
    """
    Test that the database fetcher correctly queries Postgres and writes the JSON output.
    We mock psycopg2 to prevent actual database connections during the unit test.
    """
    
    # 1. Arrange: Define our mock data
    target_sample = "SRR11032656"
    mock_db_results = [
        ("FASTQ_ONT", "s3://ngs-variant-validator-work/raw/SRR11032656.fastq.gz"),
        ("REFERENCE", "s3://ngs-variant-validator-work/ref/hg38.fasta")
    ]
    
    # 2. Patch (Mock) the database connection
    with patch('db_fetch_inputs.psycopg2.connect') as mock_connect:
        # Configure the mock cursor to return our fake data when fetchall() is called
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_db_results
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
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