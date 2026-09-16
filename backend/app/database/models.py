"""
SatQuery AI - Database Models (SQLAlchemy ORM)
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Enum as SAEnum, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    pass


def gen_uuid():
    return str(uuid.uuid4())


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class ImageFormat(str, enum.Enum):
    geotiff = "geotiff"
    tiff = "tiff"
    png = "png"
    jpeg = "jpeg"


class ImageModality(str, enum.Enum):
    optical = "optical"
    sar = "sar"
    multispectral = "multispectral"
    unknown = "unknown"


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class TaskType(str, enum.Enum):
    land_cover = "land_cover"
    water = "water"
    vegetation = "vegetation"
    agriculture = "agriculture"
    built_up = "built_up"
    roads = "roads"
    object_detection = "object_detection"
    vqa = "vqa"
    captioning = "captioning"
    grounding = "grounding"
    change_detection = "change_detection"
    change_vqa = "change_vqa"
    optical_sar = "optical_sar"
    general = "general"


class ModelStatus(str, enum.Enum):
    available = "available"
    loading = "loading"
    loaded = "loaded"
    unavailable = "unavailable"
    error = "error"


# ─────────────────────────────────────────────
# User
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.analyst, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Project
# ─────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="projects")
    images = relationship("UploadedImage", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("AnalysisJob", back_populates="project", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Uploaded Image
# ─────────────────────────────────────────────

class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)

    # File info
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)  # UUID-based safe filename
    filepath = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    format = Column(SAEnum(ImageFormat), nullable=False)
    modality = Column(SAEnum(ImageModality), default=ImageModality.unknown)

    # Raster dimensions
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    band_count = Column(Integer, nullable=True)
    band_descriptions = Column(JSON, nullable=True)  # list of band names
    dtype = Column(String, nullable=True)

    # Geospatial metadata (null for non-georeferenced)
    crs = Column(String, nullable=True)   # e.g. "EPSG:32643"
    crs_wkt = Column(Text, nullable=True)
    resolution_x = Column(Float, nullable=True)  # pixel size in CRS units
    resolution_y = Column(Float, nullable=True)
    resolution_m = Column(Float, nullable=True)  # approximate meters
    bounds_left = Column(Float, nullable=True)
    bounds_right = Column(Float, nullable=True)
    bounds_top = Column(Float, nullable=True)
    bounds_bottom = Column(Float, nullable=True)
    transform_json = Column(JSON, nullable=True)  # affine transform as dict
    nodata = Column(Float, nullable=True)
    is_georeferenced = Column(Boolean, default=False)

    # Acquisition info (from TIFF tags / metadata)
    acquisition_date = Column(String, nullable=True)
    sensor = Column(String, nullable=True)
    cloud_cover = Column(Float, nullable=True)

    # Processing info
    thumbnail_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="images")
    jobs_as_primary = relationship("AnalysisJob", foreign_keys="AnalysisJob.image_id", back_populates="primary_image")
    jobs_as_secondary = relationship("AnalysisJob", foreign_keys="AnalysisJob.image_b_id", back_populates="secondary_image")


# ─────────────────────────────────────────────
# Analysis Job
# ─────────────────────────────────────────────

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    image_id = Column(String, ForeignKey("uploaded_images.id"), nullable=False)
    image_b_id = Column(String, ForeignKey("uploaded_images.id"), nullable=True)  # bi-temporal or SAR

    # Query / task
    user_query = Column(Text, nullable=True)
    task_type = Column(SAEnum(TaskType), nullable=False)
    tools_used = Column(JSON, nullable=True)  # list of tool names
    parameters = Column(JSON, nullable=True)

    # Status
    status = Column(SAEnum(JobStatus), default=JobStatus.pending, nullable=False)
    stage = Column(String, nullable=True)   # current stage name
    progress = Column(Integer, default=0)   # 0-100
    error_message = Column(Text, nullable=True)

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="jobs")
    primary_image = relationship("UploadedImage", foreign_keys=[image_id], back_populates="jobs_as_primary")
    secondary_image = relationship("UploadedImage", foreign_keys=[image_b_id], back_populates="jobs_as_secondary")
    results = relationship("AnalysisResult", back_populates="job", cascade="all, delete-orphan")
    execution_steps = relationship("ExecutionStep", back_populates="job", cascade="all, delete-orphan", order_by="ExecutionStep.created_at")
    report = relationship("Report", back_populates="job", uselist=False, cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Analysis Result
# ─────────────────────────────────────────────

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    job_id = Column(String, ForeignKey("analysis_jobs.id"), nullable=False)

    result_type = Column(String, nullable=False)  # land_cover | change | vqa | caption | grounding

    # Land-cover per-class statistics
    class_name = Column(String, nullable=True)
    pixel_count = Column(BigInteger, nullable=True)
    total_pixels = Column(BigInteger, nullable=True)
    percentage = Column(Float, nullable=True)
    area_m2 = Column(Float, nullable=True)
    area_ha = Column(Float, nullable=True)
    area_km2 = Column(Float, nullable=True)

    # Change detection
    changed_pixels = Column(BigInteger, nullable=True)
    change_percentage = Column(Float, nullable=True)
    change_area_km2 = Column(Float, nullable=True)

    # VQA / Caption
    text_output = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)

    # Full structured data (masks paths, polygon files, raw model outputs)
    mask_path = Column(String, nullable=True)
    overlay_path = Column(String, nullable=True)
    geojson_path = Column(String, nullable=True)
    classification_map_path = Column(String, nullable=True)
    change_map_path = Column(String, nullable=True)
    extra_data = Column(JSON, nullable=True)

    # Provenance
    source_tool = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    device_used = Column(String, nullable=True)
    inference_time_ms = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)  # null if unavailable

    # Quality
    quality_warnings = Column(JSON, nullable=True)  # list of strings

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("AnalysisJob", back_populates="results")


# ─────────────────────────────────────────────
# Execution Step
# ─────────────────────────────────────────────

class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id = Column(String, primary_key=True, default=gen_uuid)
    job_id = Column(String, ForeignKey("analysis_jobs.id"), nullable=False)

    step_index = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)
    tool = Column(String, nullable=True)
    model = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    parameters = Column(JSON, nullable=True)
    status = Column(String, nullable=False)  # running | completed | failed | skipped
    output_summary = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("AnalysisJob", back_populates="execution_steps")


# ─────────────────────────────────────────────
# Model Registry
# ─────────────────────────────────────────────

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    task = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    hf_model_id = Column(String, nullable=True)
    status = Column(SAEnum(ModelStatus), default=ModelStatus.available)
    device = Column(String, nullable=True)
    loaded = Column(Boolean, default=False)
    loaded_at = Column(DateTime(timezone=True), nullable=True)
    inference_count = Column(Integer, default=0)
    avg_inference_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ─────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    job_id = Column(String, ForeignKey("analysis_jobs.id"), nullable=False)
    filepath = Column(String, nullable=False)
    format = Column(String, default="pdf")
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("AnalysisJob", back_populates="report")
