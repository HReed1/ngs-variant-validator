from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

class Base(DeclarativeBase):
    pass

class Patient(Base):
    __tablename__ = "patients"
    
    # Primary Key is the application-level encrypted string
    patient_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    samples: Mapped[List["Sample"]] = relationship(
        back_populates="patient", 
        cascade="all, delete-orphan"
    )

class Sample(Base):
    __tablename__ = "samples"
    
    sample_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="samples")
    runs: Mapped[List["Run"]] = relationship(
        back_populates="sample", 
        cascade="all, delete-orphan"
    )

class Run(Base):
    __tablename__ = "runs"
    
    run_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    sample_id: Mapped[str] = mapped_column(ForeignKey("samples.sample_id", ondelete="CASCADE"), nullable=False)
    assay_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_col: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    sample: Mapped["Sample"] = relationship(back_populates="runs")
    
    # Downstream tables now link to the sequencing event (Run), not the physical material (Sample)
    files: Mapped[List["FileLocation"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    results: Mapped[List["PipelineResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    endpoints: Mapped[List["ApiEndpoint"]] = relationship(back_populates="run", cascade="all, delete-orphan")

class FileLocation(Base):
    __tablename__ = "file_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    s3_uri: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime]

    run: Mapped["Run"] = relationship(back_populates="files")

class PipelineResult(Base):
    __tablename__ = "pipeline_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    clinical_report_json_uri: Mapped[Optional[str]] = mapped_column(Text)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50))
    metrics: Mapped[dict] = mapped_column(JSONB, default={})
    run_date: Mapped[datetime]

    run: Mapped["Run"] = relationship(back_populates="results")

class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    endpoint_url: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str] = mapped_column(String(10), default="GET")
    created_at: Mapped[datetime]

    run: Mapped["Run"] = relationship(back_populates="endpoints")