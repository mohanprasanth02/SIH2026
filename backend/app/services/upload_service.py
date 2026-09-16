"""
SatQuery AI - File Upload & Validation Service
Performs MIME validation, file structure checks, and safe storage.
"""
import os
import uuid
import hashlib
import mimetypes
import logging
from pathlib import Path
from typing import Tuple, Optional

from fastapi import UploadFile, HTTPException
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Allowed MIME types mapped to allowed extensions
ALLOWED_TYPES = {
    "image/tiff": [".tif", ".tiff"],
    "image/png": [".png"],
    "image/jpeg": [".jpg", ".jpeg"],
}

# Magic bytes for supported formats
MAGIC_BYTES = {
    "image/tiff": [
        b"\x49\x49\x2A\x00",  # Little-endian TIFF
        b"\x4D\x4D\x00\x2A",  # Big-endian TIFF
        b"\x49\x49\x2B\x00",  # Little-endian BigTIFF
        b"\x4D\x4D\x00\x2B",  # Big-endian BigTIFF
    ],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/jpeg": [b"\xFF\xD8\xFF"],
}


class UploadService:
    """
    Handles file upload validation and storage.
    - Validates file size
    - Validates MIME type against magic bytes (not just extension)
    - Stores file with UUID-based safe filename
    - Returns stored path and detected MIME type
    """

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = settings.max_upload_size

    async def save_upload(self, file: UploadFile) -> Tuple[str, str, str]:
        """
        Validate and save an uploaded file.

        Returns:
            Tuple[stored_path, stored_filename, detected_mime]

        Raises:
            HTTPException on validation failure.
        """
        # 1. Basic filename check
        original_name = file.filename or "unknown"
        ext = Path(original_name).suffix.lower()

        if ext not in [e for exts in ALLOWED_TYPES.values() for e in exts]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file extension '{ext}'. "
                       f"Supported: .tif .tiff .png .jpg .jpeg"
            )

        # 2. Read file content (stream to temp buffer)
        content = await file.read()
        file_size = len(content)

        # 3. Size check
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        if file_size > self.max_size:
            max_gb = self.max_size / (1024 ** 3)
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum size of {max_gb:.1f} GB."
            )

        # 4. Magic byte validation
        detected_mime = self._detect_mime(content[:16])
        if detected_mime is None:
            raise HTTPException(
                status_code=400,
                detail="File content does not match a supported image format. "
                       "Please upload a valid GeoTIFF, TIFF, PNG, or JPEG."
            )

        # 5. Cross-check: extension must match detected MIME
        allowed_exts_for_mime = ALLOWED_TYPES.get(detected_mime, [])
        if ext not in allowed_exts_for_mime:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '{ext}' does not match detected format "
                       f"'{detected_mime}'. Do not rename files."
            )

        # 6. Generate safe filename
        file_uuid = str(uuid.uuid4())
        safe_filename = f"{file_uuid}{ext}"
        stored_path = str(self.upload_dir / safe_filename)

        # 7. Write file
        try:
            with open(stored_path, "wb") as f:
                f.write(content)
        except OSError as e:
            logger.error(f"Failed to write uploaded file: {e}")
            raise HTTPException(status_code=500, detail="Failed to store uploaded file.")

        logger.info(
            f"Uploaded '{original_name}' ({file_size/1024/1024:.1f} MB) "
            f"→ {safe_filename} [{detected_mime}]"
        )

        return stored_path, safe_filename, detected_mime

    def _detect_mime(self, header: bytes) -> Optional[str]:
        """
        Detect file type from magic bytes only.
        Returns MIME string or None if unrecognised.
        """
        for mime, magic_list in MAGIC_BYTES.items():
            for magic in magic_list:
                if header[:len(magic)] == magic:
                    return mime
        return None

    def cleanup(self, filepath: str) -> None:
        """Remove a stored file (e.g. on job failure cleanup)."""
        try:
            Path(filepath).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Could not delete file {filepath}: {e}")

    def get_file_hash(self, filepath: str) -> str:
        """Compute SHA-256 hash of stored file for deduplication."""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
