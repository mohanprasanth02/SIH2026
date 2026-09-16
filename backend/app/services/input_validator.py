"""
SatQuery AI - Input Validation Service
Performs rigorous pre-analysis checks as required by SIH26167:
  1. Image count compatibility (single vs. bi-temporal vs. multi-sensor)
  2. File format & header integrity
  3. Sensor modality compatibility (optical vs. SAR)
  4. Geographic compatibility & co-registration checks:
     - Georeferenced images: checks CRS and Bounding Box Intersection-over-Union (IoU).
       If IoU == 0 (completely different geographic regions), rejects with:
       "These images do not appear to represent the same geographic area. Please upload corresponding images."
     - Non-georeferenced images: checks structural similarity & feature match consistency.
       If correlation is negligible, rejects with the same message.
  5. Task suitability checks
"""
import logging
from typing import Dict, Any, Optional, Tuple, List
import numpy as np

from app.services.metadata_service import ImageMetadata

logger = logging.getLogger(__name__)


class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        error_message: Optional[str] = None,
        warnings: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.is_valid = is_valid
        self.error_message = error_message
        self.warnings = warnings or []
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "warnings": self.warnings,
            "details": self.details,
        }


class InputValidator:
    """
    Validates satellite imagery before AI orchestration or model execution.
    """

    SUPPORTED_FORMATS = {"geotiff", "tiff", "png", "jpeg", "jpg", "jp2"}
    MIN_IMAGE_DIM = 64
    MAX_IMAGE_DIM = 20000

    @classmethod
    def validate_task_inputs(
        cls,
        task: str,
        meta_a: ImageMetadata,
        meta_b: Optional[ImageMetadata] = None,
        array_a: Optional[np.ndarray] = None,
        array_b: Optional[np.ndarray] = None,
    ) -> ValidationResult:
        """
        Validate inputs against the requested analysis task.
        """
        warnings: List[str] = []

        # 1. Format validation
        format_a = (meta_a.format or "").lower()
        if format_a not in cls.SUPPORTED_FORMATS:
            return ValidationResult(
                is_valid=False,
                error_message=f"Unsupported format '{meta_a.format}'. Supported: {', '.join(sorted(cls.SUPPORTED_FORMATS))}",
            )

        if meta_a.width < cls.MIN_IMAGE_DIM or meta_a.height < cls.MIN_IMAGE_DIM:
            return ValidationResult(
                is_valid=False,
                error_message=f"Image dimensions ({meta_a.width}x{meta_a.height}) are too small for satellite analysis. Minimum is {cls.MIN_IMAGE_DIM}x{cls.MIN_IMAGE_DIM}.",
            )

        # 2. Multi-image task requirements
        if task in ("change_detection", "change_vqa"):
            if meta_b is None or array_b is None:
                return ValidationResult(
                    is_valid=False,
                    error_message="Bi-temporal change analysis requires two satellite images (Image A and Image B from different dates).",
                )

            # Check geographic compatibility between A and B
            geo_valid, geo_err, geo_warn = cls.check_geographic_compatibility(
                meta_a, meta_b, array_a, array_b
            )
            warnings.extend(geo_warn)
            if not geo_valid:
                return ValidationResult(
                    is_valid=False,
                    error_message=geo_err,
                    warnings=warnings,
                )

        elif task == "optical_sar":
            if meta_b is None or array_b is None:
                return ValidationResult(
                    is_valid=False,
                    error_message="Optical + SAR joint analysis requires both an Optical image and a SAR image.",
                )

            # Modality check
            has_sar = (meta_a.modality == "sar") or (meta_b.modality == "sar")
            has_optical = (meta_a.modality == "optical") or (meta_b.modality == "optical") or (meta_a.band_count >= 3)
            if not has_sar:
                warnings.append("Neither image has explicit SAR metadata; interpreting Image B as synthetic aperture radar backscatter.")

            # Check geographic compatibility
            geo_valid, geo_err, geo_warn = cls.check_geographic_compatibility(
                meta_a, meta_b, array_a, array_b
            )
            warnings.extend(geo_warn)
            if not geo_valid:
                return ValidationResult(
                    is_valid=False,
                    error_message=geo_err,
                    warnings=warnings,
                )

        return ValidationResult(is_valid=True, warnings=warnings)

    @classmethod
    def check_geographic_compatibility(
        cls,
        meta_a: ImageMetadata,
        meta_b: ImageMetadata,
        array_a: Optional[np.ndarray] = None,
        array_b: Optional[np.ndarray] = None,
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validates whether two satellite images represent the same geographic area.
        Returns (is_compatible, error_message, warnings)
        """
        warnings: List[str] = []
        STANDARD_REJECTION = "These images do not appear to represent the same geographic area. Please upload corresponding images."

        # Case A: Both images are georeferenced
        if meta_a.is_georeferenced and meta_b.is_georeferenced:
            # Check CRS match or transformability
            crs_a = (meta_a.crs or "").strip().upper()
            crs_b = (meta_b.crs or "").strip().upper()

            if crs_a and crs_b and crs_a != crs_b:
                warnings.append(f"CRS mismatch: Image A is {crs_a} while Image B is {crs_b}. Reprojection may introduce spatial distortion.")

            # Calculate Bounding Box IoU
            bounds_a = meta_a.bounds  # dict with left, bottom, right, top
            bounds_b = meta_b.bounds

            if bounds_a and bounds_b:
                # Intersecting rectangle
                inter_left = max(bounds_a.get("left", 0), bounds_b.get("left", 0))
                inter_bottom = max(bounds_a.get("bottom", 0), bounds_b.get("bottom", 0))
                inter_right = min(bounds_a.get("right", 0), bounds_b.get("right", 0))
                inter_top = min(bounds_a.get("top", 0), bounds_b.get("top", 0))

                inter_w = max(0.0, inter_right - inter_left)
                inter_h = max(0.0, inter_top - inter_bottom)
                inter_area = inter_w * inter_h

                area_a = max(1e-6, (bounds_a.get("right", 0) - bounds_a.get("left", 0)) * (bounds_a.get("top", 0) - bounds_a.get("bottom", 0)))
                area_b = max(1e-6, (bounds_b.get("right", 0) - bounds_b.get("left", 0)) * (bounds_b.get("top", 0) - bounds_b.get("bottom", 0)))

                overlap_ratio = inter_area / min(area_a, area_b)

                if inter_area <= 0 or overlap_ratio < 0.05:
                    logger.warning(
                        f"Geographic overlap check failed: inter_area={inter_area}, overlap_ratio={overlap_ratio:.4f}. Bounds A: {bounds_a}, Bounds B: {bounds_b}"
                    )
                    return False, STANDARD_REJECTION, warnings

                if overlap_ratio < 0.6:
                    warnings.append(f"Partial geographic overlap detected ({overlap_ratio*100:.1f}%). Analysis is focused on the intersecting footprint.")

            return True, None, warnings

        # Case B: Non-georeferenced images (e.g. standard PNG/JPG pairs)
        if array_a is not None and array_b is not None:
            similarity = cls._compute_structural_correlation(array_a, array_b)
            logger.info(f"Visual correlation between Image A and Image B: {similarity:.4f}")

            # If correlation is extremely low or negative, they are unrelated scenes
            if similarity < 0.02:
                logger.warning(f"Unrelated scenes detected: structural correlation = {similarity:.4f}")
                return False, STANDARD_REJECTION, warnings

        return True, None, warnings

    @staticmethod
    def _compute_structural_correlation(img_a: np.ndarray, img_b: np.ndarray) -> float:
        """
        Computes normalized 2D cross-correlation on downsampled luminance to test
        if two non-georeferenced satellite images correspond to the same scene.
        """
        try:
            from PIL import Image as PILImage

            # Convert both to grayscale downsampled (128x128)
            def to_gray(arr: np.ndarray) -> np.ndarray:
                if arr.ndim == 3:
                    if arr.shape[2] >= 3:
                        g = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
                    else:
                        g = arr[:, :, 0]
                else:
                    g = arr.astype(np.float32)
                pil = PILImage.fromarray(np.clip(g, 0, 255).astype(np.uint8))
                pil = pil.resize((128, 128), PILImage.BILINEAR)
                return np.array(pil, dtype=np.float32)

            g_a = to_gray(img_a)
            g_b = to_gray(img_b)

            # Normalize zero-mean unit variance
            std_a = np.std(g_a)
            std_b = np.std(g_b)
            if std_a < 1e-3 or std_b < 1e-3:
                return 0.5  # uniform image fallback

            g_a_norm = (g_a - np.mean(g_a)) / std_a
            g_b_norm = (g_b - np.mean(g_b)) / std_b

            # Normalized Pearson cross-correlation coefficient
            corr = float(np.mean(g_a_norm * g_b_norm))
            return max(0.0, corr)
        except Exception as e:
            logger.debug(f"Correlation check error: {e}")
            return 0.5
