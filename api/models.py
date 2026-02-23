from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, foreign
from sqlalchemy.dialects.postgresql import JSONB

class Base(DeclarativeBase):
    pass

class FrontendPatient(Base):
    __tablename__ = "frontend_patients"
    
    # patient_hash acts as an opaque surrogate key because patient_id is explicitly omitted
    patient_hash: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    samples: Mapped[List["FrontendSample"]] = relationship(
        back_populates="patient",
        primaryjoin="FrontendPatient.patient_hash == foreign(FrontendSample.patient_hash)"
    )

class FrontendSample(Base):
    __tablename__ = "frontend_samples"
    
    sample_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    patient_hash: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    patient: Mapped["FrontendPatient"] = relationship(
        back_populates="samples",
        primaryjoin="foreign(FrontendSample.patient_hash) == FrontendPatient.patient_hash"
    )
    runs: Mapped[List["FrontendRun"]] = relationship(
        back_populates="sample",
        primaryjoin="FrontendSample.sample_id == foreign(FrontendRun.sample_id)"
    )

class FrontendRun(Base):
    __tablename__ = "frontend_runs"
    
    run_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    sample_id: Mapped[str] = mapped_column(String(50))
    assay_type: Mapped[str] = mapped_column(String(50))
    metadata_col: Mapped[dict] = mapped_column("metadata", JSONB, default={})
    created_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    sample: Mapped["FrontendSample"] = relationship(
        back_populates="runs",
        primaryjoin="foreign(FrontendRun.sample_id) == FrontendSample.sample_id"
    )
    files: Mapped[List["FileLocation"]] = relationship(
        back_populates="run",
        primaryjoin="FrontendRun.run_id == foreign(FileLocation.run_id)"
    )
    results: Mapped[List["PipelineResult"]] = relationship(
        back_populates="run",
        primaryjoin="FrontendRun.run_id == foreign(PipelineResult.run_id)"
    )
    endpoints: Mapped[List["ApiEndpoint"]] = relationship(
        back_populates="run",
        primaryjoin="FrontendRun.run_id == foreign(ApiEndpoint.run_id)"
    )

# FileLocation, PipelineResult, and ApiEndpoint remain identical to the ETL side, 
# except their SQLAlchemy ForeignKeys and Relationships point to `runs.run_id` and `FrontendRun`.
class FileLocation(Base):
    __tablename__ = "file_locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    file_type: Mapped[str] = mapped_column(String(50))
    s3_uri: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime]

    run: Mapped["FrontendRun"] = relationship(
        back_populates="files",
        primaryjoin="foreign(FileLocation.run_id) == FrontendRun.run_id"
    )

# ... (PipelineResult and ApiEndpoint mirror FileLocation by pointing to run_id and FrontendRun)


class PipelineResult(Base):
    __tablename__ = "pipeline_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    clinical_report_json_uri: Mapped[Optional[str]] = mapped_column(Text)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50))
    metrics: Mapped[dict] = mapped_column(JSONB, default={})
    run_date: Mapped[datetime]

    run: Mapped["FrontendRun"] = relationship(
        back_populates="results",
        primaryjoin="foreign(PipelineResult.run_id) == FrontendRun.run_id"
    )


class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.run_id", ondelete="CASCADE"))
    service_name: Mapped[str] = mapped_column(String(100))
    endpoint_url: Mapped[str] = mapped_column(Text)
    method: Mapped[str] = mapped_column(String(10), default="GET")
    created_at: Mapped[datetime]

    run: Mapped["FrontendRun"] = relationship(
        back_populates="endpoints",
        primaryjoin="foreign(ApiEndpoint.run_id) == FrontendRun.run_id"
    )