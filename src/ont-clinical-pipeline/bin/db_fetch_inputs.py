#!/usr/bin/env python3
import argparse
import psycopg2
import json
import os

def fetch_run_files(run_id, db_host, db_user, db_pass, db_name):
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_pass)
    cursor = conn.cursor()
    
    # Query the file locations table using the new run_id foreign key
    query = """
        SELECT file_type, s3_uri 
        FROM file_locations 
        WHERE run_id = %s;
    """
    cursor.execute(query, (run_id,))
    results = cursor.fetchall()
    
    # Convert the list of tuples into a dictionary
    results_dict = {row[0]: row[1] for row in results}
    
    # Format as JSON for Nextflow
    output_data = {
        "run_id": run_id,
        "reads": results_dict.get("FASTQ_ONT", ""),
        "reference": results_dict.get("REFERENCE", "")
    }
    
    with open('inputs.json', 'w') as f:
        json.dump(output_data, f)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True, help="The Run ID for the pipeline execution")
    args = parser.parse_args()
    
    # Credentials pulled from environment variables injected by Nextflow
    fetch_run_files(
        args.run,
        os.environ.get('DB_HOST', ValueError("DB_HOST environment variable is not set")),
        os.environ.get('DB_USER', ValueError("DB_USER environment variable is not set")),
        os.environ.get('DB_PASSWORD', ValueError("DB_PASSWORD environment variable is not set")),
        os.environ.get('DB_NAME', ValueError("DB_NAME environment variable is not set"))
    )