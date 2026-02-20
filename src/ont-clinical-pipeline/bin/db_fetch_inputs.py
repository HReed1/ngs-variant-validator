import argparse
import psycopg2
import json
import os

def fetch_sample_files(sample_id, db_host, db_user, db_pass, db_name):
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_pass)
    cursor = conn.cursor()
    
    # Query the file locations table
    query = """
        SELECT file_type, s3_uri 
        FROM file_locations 
        WHERE sample_id = %s;
    """
    cursor.execute(query, (sample_id,))
    results = cursor.fetchall()
    
    # Format as JSON for Nextflow
    output_data = {row[0]: row[1] for row in results}
    
    with open('inputs.json', 'w') as f:
        json.dump(output_data, f)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', required=True)
    args = parser.parse_args()
    
    # Credentials pulled from environment variables injected by Nextflow
    fetch_sample_files(
        args.sample,
        os.environ.get('DB_HOST'),
        os.environ.get('DB_USER'),
        os.environ.get('DB_PASS'),
        os.environ.get('DB_NAME')
    )