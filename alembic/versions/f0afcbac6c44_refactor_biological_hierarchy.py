"""refactor_biological_hierarchy

Revision ID: f0afcbac6c44
Revises: 
Create Date: 2026-02-22 23:12:16.429939

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f0afcbac6c44'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Clear existing views to remove dependency locks
    op.execute("DROP VIEW IF EXISTS public.frontend_samples CASCADE;")

    # 2. Drop legacy flat tables
    op.drop_table('api_endpoints')
    op.drop_table('pipeline_results')
    op.drop_table('file_locations')
    op.drop_table('samples')

    # 3. Create the Normalized Base Tables
    op.create_table(
        'patients',
        sa.Column('patient_id', sa.String(length=255), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    op.create_table(
        'samples',
        sa.Column('sample_id', sa.String(length=50), primary_key=True),
        sa.Column('patient_id', sa.String(length=255), sa.ForeignKey('patients.patient_id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    op.create_table(
        'runs',
        sa.Column('run_id', sa.String(length=50), primary_key=True),
        sa.Column('sample_id', sa.String(length=50), sa.ForeignKey('samples.sample_id', ondelete='CASCADE'), nullable=False),
        sa.Column('assay_type', sa.String(length=50), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Re-apply GIN index for high-speed metadata querying
    op.execute("CREATE INDEX idx_runs_metadata ON runs USING GIN (metadata);")

    # 4. Recreate Downstream tables tied to `run_id` instead of `sample_id`
    op.create_table(
        'file_locations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.String(length=50), sa.ForeignKey('runs.run_id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('s3_uri', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    op.create_table(
        'pipeline_results',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.String(length=50), sa.ForeignKey('runs.run_id', ondelete='CASCADE'), nullable=False),
        sa.Column('clinical_report_json_uri', sa.Text(), nullable=True),
        sa.Column('pipeline_version', sa.String(length=50), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('run_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.execute("CREATE INDEX idx_pipeline_results_metrics ON pipeline_results USING GIN (metrics);")

    op.create_table(
        'api_endpoints',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.String(length=50), sa.ForeignKey('runs.run_id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('endpoint_url', sa.Text(), nullable=False),
        sa.Column('method', sa.String(length=10), server_default='GET'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # 5. Build Zero-Trust Views
    # We explicitly omit patient_id and project an MD5 hash surrogate key for the frontend
    op.execute("""
        CREATE VIEW public.frontend_patients AS
        SELECT 
            md5(patient_id) AS patient_hash,
            created_at,
            updated_at
        FROM public.patients;
    """)

    op.execute("""
        CREATE VIEW public.frontend_samples AS
        SELECT 
            sample_id,
            md5(patient_id) AS patient_hash,
            created_at,
            updated_at
        FROM public.samples;
    """)

    op.execute("""
        CREATE VIEW public.frontend_runs AS
        SELECT 
            run_id,
            sample_id,
            assay_type,
            metadata,
            created_at,
            updated_at
        FROM public.runs;
    """)

    # 6. Re-apply strict RBAC
    # ETL worker retains all access; Frontend API is restricted exclusively to views & child tables
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO etl_worker;")
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO etl_worker;")

    op.execute("GRANT SELECT ON public.frontend_patients TO frontend_api;")
    op.execute("GRANT SELECT ON public.frontend_samples TO frontend_api;")
    op.execute("GRANT SELECT ON public.frontend_runs TO frontend_api;")
    op.execute("GRANT SELECT ON public.file_locations TO frontend_api;")
    op.execute("GRANT SELECT ON public.pipeline_results TO frontend_api;")
    op.execute("GRANT SELECT ON public.api_endpoints TO frontend_api;")


def downgrade() -> None:
    # 1. Drop the hierarchical Zero-Trust views
    op.execute("DROP VIEW IF EXISTS public.frontend_runs CASCADE;")
    op.execute("DROP VIEW IF EXISTS public.frontend_samples CASCADE;")
    op.execute("DROP VIEW IF EXISTS public.frontend_patients CASCADE;")
    
    # 2. Drop the normalized tables
    op.drop_table('api_endpoints')
    op.drop_table('pipeline_results')
    op.drop_table('file_locations')
    op.drop_table('runs')
    op.drop_table('samples')
    op.drop_table('patients')

    # 3. Recreate the original flattened 'samples' base table
    op.create_table(
        'samples',
        sa.Column('sample_id', sa.String(length=50), primary_key=True),
        sa.Column('patient_id', sa.String(length=255), nullable=False),
        sa.Column('assay_type', sa.String(length=50), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.execute("CREATE INDEX idx_samples_metadata ON samples USING GIN (metadata);")

    # 4. Recreate original downstream tables referencing 'sample_id'
    op.create_table(
        'file_locations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sample_id', sa.String(length=50), sa.ForeignKey('samples.sample_id', ondelete='CASCADE')),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('s3_uri', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.execute("CREATE INDEX idx_file_locations_sample_id ON file_locations(sample_id);")

    op.create_table(
        'pipeline_results',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sample_id', sa.String(length=50), sa.ForeignKey('samples.sample_id', ondelete='CASCADE')),
        sa.Column('clinical_report_json_uri', sa.Text(), nullable=True),
        sa.Column('pipeline_version', sa.String(length=50), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True),
        sa.Column('run_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.execute("CREATE INDEX idx_pipeline_results_sample_id ON pipeline_results(sample_id);")
    op.execute("CREATE INDEX idx_pipeline_results_metrics ON pipeline_results USING GIN (metrics);")

    op.create_table(
        'api_endpoints',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sample_id', sa.String(length=50), sa.ForeignKey('samples.sample_id', ondelete='CASCADE')),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('endpoint_url', sa.Text(), nullable=False),
        sa.Column('method', sa.String(length=10), server_default='GET'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.execute("CREATE INDEX idx_api_endpoints_sample_id ON api_endpoints(sample_id);")

    # 5. Recreate the original Zero-Trust view for the API
    op.execute("""
        CREATE VIEW public.frontend_samples AS
        SELECT 
            sample_id, 
            assay_type, 
            metadata, 
            created_at, 
            updated_at
        FROM public.samples;
    """)

    # 6. Re-apply the original RBAC permissions
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO etl_worker;")
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO etl_worker;")

    op.execute("GRANT SELECT ON public.frontend_samples TO frontend_api;")
    op.execute("GRANT SELECT ON public.file_locations TO frontend_api;")
    op.execute("GRANT SELECT ON public.pipeline_results TO frontend_api;")
    op.execute("GRANT SELECT ON public.api_endpoints TO frontend_api;")
