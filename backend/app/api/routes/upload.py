"""
SatQuery AI - Upload Route
POST /api/v1/upload
"""
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.services.upload_service import UploadService
from app.services.metadata_service import MetadataService
from app.services.evidence_service import EvidenceService

logger = logging.getLogger(__name__)
router = APIRouter()

upload_svc = UploadService()
metadata_svc = MetadataService()
evidence_svc = EvidenceService()


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    modality: Optional[str] = Form(None),  # optical | sar | multispectral
):
    """
    Upload and validate a satellite image.
    Performs:
    - MIME/magic-byte validation
    - Size check
    - Rasterio metadata extraction (CRS, bands, resolution, bounds)
    - Thumbnail generation
    
    Returns image ID and full metadata.
    """
    # Validate and store file
    try:
        stored_path, stored_filename, detected_mime = await upload_svc.save_upload(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Extract metadata
    try:
        meta = metadata_svc.extract(stored_path)
    except Exception as e:
        logger.warning(f"Metadata extraction failed for {stored_filename}: {e}")
        # Don't fail the upload; return partial metadata
        meta = None

    # Override modality if provided by user
    if modality and meta:
        meta.modality = modality

    # Generate thumbnail
    thumb_path = None
    try:
        thumb_path = evidence_svc.generate_thumbnail(stored_path)
    except Exception as e:
        logger.warning(f"Thumbnail generation failed: {e}")

    # Build response
    image_id = Path(stored_filename).stem  # UUID without extension
    response = {
        "image_id": image_id,
        "stored_filename": stored_filename,
        "stored_path": stored_path,
        "original_filename": file.filename,
        "detected_mime": detected_mime,
        "thumbnail_url": f"/results/{Path(thumb_path).name}" if thumb_path else None,
        "metadata": meta.to_dict() if meta else None,
    }

    return JSONResponse(content=response)


@router.get("/images/{image_id}/metadata")
async def get_image_metadata(image_id: str):
    """Return metadata for an uploaded image."""
    from app.config.settings import get_settings
    import os

    settings = get_settings()
    upload_dir = Path(settings.upload_dir)

    exact = upload_dir / image_id
    if exact.is_file():
        filepath = str(exact)
    else:
        matches = list(upload_dir.glob(f"{image_id}.*"))
        if not matches:
            matches = list(upload_dir.glob(f"*{image_id}*"))
        if not matches and len(image_id) >= 8:
            matches = list(upload_dir.glob(f"*{image_id[:8]}*"))
        if not matches:
            raise HTTPException(status_code=404, detail=f"Image {image_id} not found.")
        filepath = str(matches[0])
    try:
        meta = metadata_svc.extract(filepath)
        return JSONResponse(content=meta.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
