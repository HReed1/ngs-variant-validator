-- Create the roles
CREATE ROLE etl_worker WITH LOGIN PASSWORD 'strong_etl_password';
CREATE ROLE frontend_api WITH LOGIN PASSWORD 'strong_frontend_password';

-- Grant basic connection rights
GRANT CONNECT ON DATABASE pipeline_db TO etl_worker, frontend_api;
GRANT USAGE ON SCHEMA public TO etl_worker, frontend_api;