#!/bin/bash

# Start with a clean slate
./utils/stop_dev.sh --clean

# Start the dev environment
./utils/start_dev.sh

uvicorn api.main:app --reload --port 8000

# Run the Alembic Migration
venv/bin/alembic upgrade head

# Seed the database with synthetic data
venv/bin/python -m etl.jobs.seed_database

# Try to query PHI using the restricted API role (Expected: Permission Denied)
docker exec -it pipeline_postgres_local psql -U frontend_api -d pipeline_db -c "SELECT patient_id FROM samples;"

# Query the sanitized view using the restricted API role (Expected: Success):
docker exec -it pipeline_postgres_local psql -U frontend_api -d pipeline_db -c "SELECT * FROM frontend_samples LIMIT 5;"

# Disocvery Github Project and Field IDs for information
venv/bin/python utils/discover_ids.py 

# Check API Key authentication
curl -H "X-API-Key: ${API_KEY}" "http://localhost:8000/samples/search/metadata?key=assay_type&value=ONT_WGS"
