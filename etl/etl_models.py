from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

class Base(DeclarativeBase):
    pass

class Sample(Base):
    __tablename__ = "samples"
    
    sample_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    
    # The ETL worker maps the base table, so it has access to the encrypted PHI
    patient_id: Mapped[str] = mapped_column(String(255), nullable=False) 
    
    assay_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_col: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships pointing directly to the base Sample model
    files: Mapped[List["FileLocation"]] = relationship(
        back_populates="sample", 
        cascade="all, delete-orphan"
    )
    results: Mapped[List["PipelineResult"]] = relationship(
        back_populates="sample", 
        cascade="all, delete-orphan"
    )
    endpoints: Mapped[List["ApiEndpoint"]] = relationship(
        back_populates="sample", 
        cascade="all, delete-orphan"
    )


class FileLocation(Base):
    __tablename__ = "file_locations"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id", ondelete="CASCADE"))
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    s3_uri: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]

    sample: Mapped["Sample"] = relationship(back_populates="files")


class PipelineResult(Base):
    __tablename__ = "pipeline_results"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id", ondelete="CASCADE"))
    clinical_report_json_uri: Mapped[Optional[str]] = mapped_column(Text)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50))
    metrics: Mapped[dict] = mapped_column(JSONB, default={})
    run_date: Mapped[datetime]

    sample: Mapped["Sample"] = relationship(back_populates="results")


class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id", ondelete="CASCADE"))
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint_url: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str] = mapped_column(String(10), default="GET")
    created_at: Mapped[datetime]

    sample: Mapped["Sample"] = relationship(back_populates="endpoints")