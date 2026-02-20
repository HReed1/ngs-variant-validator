-- Create the roles
CREATE ROLE etl_worker WITH LOGIN PASSWORD 'strong_etl_password';
CREATE ROLE frontend_api WITH LOGIN PASSWORD 'strong_frontend_password';

-- Grant basic connection rights
GRANT CONNECT ON DATABASE pipeline_db TO etl_worker, frontend_api;
GRANT USAGE ON SCHEMA public TO etl_worker, frontend_api;

-- Create a view that explicitly excludes patient_id
CREATE VIEW public.frontend_samples AS
SELECT 
    sample_id, 
    assay_type, 
    metadata, 
    created_at, 
    updated_at
FROM public.samples;

-- Give the frontend read-only access to this safe view
GRANT SELECT ON public.frontend_samples TO frontend_api;

-- Give the frontend read-only access to the other safe tables
GRANT SELECT ON public.file_locations TO frontend_api;
GRANT SELECT ON public.pipeline_results TO frontend_api;
GRANT SELECT ON public.api_endpoints TO frontend_api;

-- The ETL role gets full access to the base tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO etl_worker;

-- Allow ETL to use the auto-incrementing ID sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO etl_worker;