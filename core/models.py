from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy.dialects.postgresql import JSONB

class FileLocationMixin:
    @declared_attr
    def __tablename__(cls):
        return "file_locations"
        
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    s3_uri: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]

class PipelineResultMixin:
    @declared_attr
    def __tablename__(cls):
        return "pipeline_results"
        
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    clinical_report_json_uri: Mapped[Optional[str]] = mapped_column(Text)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50))
    metrics: Mapped[dict] = mapped_column(JSONB, default={})
    run_date: Mapped[datetime]

class ApiEndpointMixin:
    @declared_attr
    def __tablename__(cls):
        return "api_endpoints"
        
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint_url: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str] = mapped_column(String(10), default="GET")
    created_at: Mapped[datetime]
