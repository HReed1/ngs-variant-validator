from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign
from sqlalchemy.dialects.postgresql import JSONB

class Base(DeclarativeBase):
    pass

class FrontendSample(Base):
    __tablename__ = "frontend_samples"
    # Important: Tell SQLAlchemy this acts as a primary key for the ORM's sake
    sample_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    assay_type: Mapped[str] = mapped_column(String(50))
    metadata_col: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships to child tables
    files: Mapped[List["FileLocation"]] = relationship(
        back_populates="sample",
        primaryjoin="FrontendSample.sample_id == foreign(FileLocation.sample_id)"
    )
    results: Mapped[List["PipelineResult"]] = relationship(
        back_populates="sample",
        primaryjoin="FrontendSample.sample_id == foreign(PipelineResult.sample_id)"
    )
    endpoints: Mapped[List["ApiEndpoint"]] = relationship(
        back_populates="sample",
        primaryjoin="FrontendSample.sample_id == foreign(ApiEndpoint.sample_id)"
    )


class FileLocation(Base):
    __tablename__ = "file_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id", ondelete="CASCADE"))
    file_type: Mapped[str] = mapped_column(String(50))
    s3_uri: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime]

    sample: Mapped["FrontendSample"] = relationship(
        back_populates="files",
        primaryjoin="foreign(FileLocation.sample_id) == FrontendSample.sample_id"
    )


class PipelineResult(Base):
    __tablename__ = "pipeline_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id", ondelete="CASCADE"))
    clinical_report_json_uri: Mapped[Optional[str]] = mapped_column(Text)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50))
    metrics: Mapped[dict] = mapped_column(JSONB, default={})
    run_date: Mapped[datetime]

    sample: Mapped["FrontendSample"] = relationship(
        back_populates="results",
        primaryjoin="foreign(PipelineResult.sample_id) == FrontendSample.sample_id"
    )


class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id", ondelete="CASCADE"))
    service_name: Mapped[str] = mapped_column(String(100))
    endpoint_url: Mapped[str] = mapped_column(Text)
    method: Mapped[str] = mapped_column(String(10), default="GET")
    created_at: Mapped[datetime]

    sample: Mapped["FrontendSample"] = relationship(
        back_populates="endpoints",
        primaryjoin="foreign(ApiEndpoint.sample_id) == FrontendSample.sample_id"
    )