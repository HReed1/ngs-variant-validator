#!/usr/bin/env python3
import os
import sys
import json
import argparse
import psycopg2
from psycopg2.extras import Json

def main():
    parser = argparse.ArgumentParser(description="Log Nextflow pipeline outputs to PostgreSQL.")
    parser.add_argument("--sample", required=True, help="The Sample ID")
    parser.add_argument("--report", required=True, help="S3 URI of the final clinical report JSON")
    parser.add_argument("--version", required=True, help="Pipeline version string (e.g., v1.2.0)")
    parser.add_argument("--metrics", required=False, help="Path to a JSON file containing QC metrics")
    
    args = parser.parse_args()

    # Parse the metrics file into a dictionary if provided
    metrics_data = {}
    if args.metrics and os.path.exists(args.metrics):
        with open(args.metrics, 'r') as f:
            metrics_data = json.load(f)

    # Pull connection credentials from environment variables injected by Nextflow secrets
    db_host = os.environ.get("DB_HOST", None)
    db_port = os.environ.get("DB_PORT", None)
    db_name = os.environ.get("DB_NAME", None)
    db_user = os.environ.get("DB_USER", None)
    db_pass = os.environ.get("DB_PASSWORD", None)

    conn = None
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_pass
        )
        cur = conn.cursor()

        # 1. Insert the new pipeline run record
        # psycopg2.extras.Json automatically serializes the Python dictionary for Postgres JSONB
        insert_query = """
            INSERT INTO pipeline_results 
            (sample_id, clinical_report_json_uri, pipeline_version, metrics)
            VALUES (%s, %s, %s, %s);
        """
        cur.execute(insert_query, (
            args.sample, 
            args.report, 
            args.version, 
            Json(metrics_data)
        ))

        # 2. Update the parent sample to flag it as complete
        # The || operator in Postgres natively merges the new key/value pair into the 
        # existing JSONB metadata without deleting other dynamic tags (e.g. sequencer type).
        update_query = """
            UPDATE samples 
            SET metadata = metadata || '{"status": "complete"}'::jsonb 
            WHERE sample_id = %s;
        """
        cur.execute(update_query, (args.sample,))

        # Commit the transaction so both the insert and update apply simultaneously
        conn.commit()
        print(f"Successfully logged pipeline outputs for {args.sample}.")

    except psycopg2.Error as e:
        # If any step fails, roll back the entire transaction to prevent partial data states
        if conn:
            conn.rollback()
        print(f"Database error during logging: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    main()