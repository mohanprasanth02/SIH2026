"""
SatQuery AI - Remote Sensing Metadata Service
Extracts real geospatial metadata from GeoTIFF/TIFF files using Rasterio.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import rasterio
    from rasterio.crs import CRS
    from rasterio.transform import Affine
    from rasterio.warp import transform_bounds
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    logger.warning("rasterio not available - geospatial features limited")

try:
    from PIL import Image as PILImage
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


@dataclass
class ImageMetadata:
    """Comprehensive metadata for an uploaded image."""
    # Basic
    filename: str = ""
    format: str = ""                  # geotiff | tiff | png | jpeg
    modality: str = "unknown"         # optical | sar | multispectral | unknown
    file_size: int = 0
    mime_type: str = ""

    # Dimensions
    width: int = 0
    height: int = 0
    band_count: int = 0
    dtype: str = ""
    band_descriptions: List[str] = field(default_factory=list)

    # Geospatial (None if not georeferenced)
    is_georeferenced: bool = False
    crs: Optional[str] = None         # "EPSG:32643"
    crs_wkt: Optional[str] = None
    crs_authority: Optional[str] = None
    resolution_x: Optional[float] = None   # pixel width in CRS units
    resolution_y: Optional[float] = None   # pixel height in CRS units
    resolution_m: Optional[float] = None   # approx meters/pixel
    bounds: Optional[Dict[str, float]] = None  # left, bottom, right, top
    bounds_wgs84: Optional[Dict[str, float]] = None  # always in lon/lat
    transform: Optional[List[float]] = None  # affine as 6 coefficients
    nodata: Optional[float] = None

    # Acquisition metadata (from TIFF tags, may be null)
    acquisition_date: Optional[str] = None
    sensor: Optional[str] = None
    cloud_cover: Optional[float] = None

    # Quality warnings
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetadataService:
    """
    Extracts metadata from uploaded satellite images.
    Supports: GeoTIFF, TIFF, PNG, JPEG
    """

    # Common tag IDs in GeoTIFF files that may contain acquisition info
    TIFF_ACQUISITION_TAGS = {
        "TIFFTAG_DATETIME": 306,
        "TIFFTAG_IMAGEDESCRIPTION": 270,
        "TIFFTAG_SOFTWARE": 305,
        "TIFFTAG_ARTIST": 315,
    }

    def extract(self, filepath: str) -> ImageMetadata:
        """
        Main entry point: extract all available metadata from image file.
        Returns ImageMetadata with as much detail as available.
        """
        path = Path(filepath)
        ext = path.suffix.lower()

        meta = ImageMetadata(filename=path.name)

        # File size
        try:
            meta.file_size = os.path.getsize(filepath)
        except OSError:
            pass

        # Determine format and route to appropriate extractor
        if ext in (".tif", ".tiff"):
            meta.format = "geotiff"
            meta.mime_type = "image/tiff"
            if RASTERIO_AVAILABLE:
                self._extract_rasterio(filepath, meta)
            elif PILLOW_AVAILABLE:
                self._extract_pillow(filepath, meta)
                meta.warnings.append("rasterio unavailable; geospatial extraction limited")
        elif ext == ".png":
            meta.format = "png"
            meta.mime_type = "image/png"
            if PILLOW_AVAILABLE:
                self._extract_pillow(filepath, meta)
        elif ext in (".jpg", ".jpeg"):
            meta.format = "jpeg"
            meta.mime_type = "image/jpeg"
            if PILLOW_AVAILABLE:
                self._extract_pillow(filepath, meta)
        else:
            meta.warnings.append(f"Unrecognised extension: {ext}")

        # Warn if no georeferencing
        if not meta.is_georeferenced and meta.format in ("geotiff", "tiff"):
            meta.warnings.append(
                "No CRS found. Physical area calculations unavailable."
            )

        # Warn about non-georeferenced non-tiff files
        if not meta.is_georeferenced and meta.format in ("png", "jpeg"):
            meta.warnings.append(
                "PNG/JPEG files are not georeferenced. "
                "Physical area and spatial statistics are unavailable."
            )

        # Detect modality heuristically
        meta.modality = self._detect_modality(meta)

        return meta

    def _extract_rasterio(self, filepath: str, meta: ImageMetadata) -> None:
        """Use rasterio to extract full geospatial metadata."""
        try:
            with rasterio.open(filepath) as ds:
                meta.width = ds.width
                meta.height = ds.height
                meta.band_count = ds.count
                meta.dtype = str(ds.dtypes[0]) if ds.dtypes else ""

                # Band descriptions
                descs = list(ds.descriptions)
                meta.band_descriptions = [
                    d if d else f"Band {i+1}" for i, d in enumerate(descs)
                ]

                # NoData
                if ds.nodata is not None:
                    meta.nodata = float(ds.nodata)

                # Transform
                t = ds.transform
                meta.transform = [t.a, t.b, t.c, t.d, t.e, t.f]
                meta.resolution_x = abs(t.a)
                meta.resolution_y = abs(t.e)

                # CRS
                if ds.crs is not None:
                    meta.is_georeferenced = True
                    try:
                        meta.crs = ds.crs.to_string()
                        meta.crs_wkt = ds.crs.to_wkt()
                        meta.crs_authority = ds.crs.to_epsg()
                        if meta.crs_authority:
                            meta.crs_authority = f"EPSG:{meta.crs_authority}"
                    except Exception:
                        meta.crs = str(ds.crs)

                    # Bounds in native CRS
                    b = ds.bounds
                    meta.bounds = {
                        "left": b.left, "bottom": b.bottom,
                        "right": b.right, "top": b.top
                    }

                    # Bounds in WGS84 for display
                    try:
                        lb, bb, rb, tb = transform_bounds(
                            ds.crs, "EPSG:4326",
                            b.left, b.bottom, b.right, b.top
                        )
                        meta.bounds_wgs84 = {
                            "lon_min": lb, "lat_min": bb,
                            "lon_max": rb, "lat_max": tb
                        }
                    except Exception as e:
                        logger.debug(f"Could not transform bounds to WGS84: {e}")

                    # Resolution in meters
                    meta.resolution_m = self._estimate_resolution_m(ds)
                else:
                    meta.is_georeferenced = False

                # Acquisition metadata from TIFF tags
                self._extract_tiff_tags(ds, meta)

        except rasterio.errors.RasterioIOError as e:
            meta.warnings.append(f"Could not read raster file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in rasterio extraction: {e}")
            meta.warnings.append(f"Partial metadata extraction: {e}")

    def _extract_pillow(self, filepath: str, meta: ImageMetadata) -> None:
        """Fallback: use Pillow for basic dimension/band extraction."""
        try:
            with PILImage.open(filepath) as img:
                meta.width, meta.height = img.size
                mode_to_bands = {
                    "L": 1, "RGB": 3, "RGBA": 4,
                    "P": 1, "CMYK": 4, "YCbCr": 3,
                    "I": 1, "F": 1,
                }
                meta.band_count = mode_to_bands.get(img.mode, 1)
                meta.dtype = self._pil_mode_to_dtype(img.mode)
                meta.band_descriptions = [
                    f"Band {i+1}" for i in range(meta.band_count)
                ]

                # EXIF acquisition date for JPEG
                try:
                    exif = img._getexif()
                    if exif:
                        date_tag = 36867  # DateTimeOriginal
                        if date_tag in exif:
                            meta.acquisition_date = exif[date_tag]
                except Exception:
                    pass

        except Exception as e:
            meta.warnings.append(f"Could not read image with Pillow: {e}")

    def _extract_tiff_tags(self, ds, meta: ImageMetadata) -> None:
        """Extract acquisition info from TIFF tags."""
        try:
            tags = ds.tags()
            if not tags:
                return

            # DateTime
            for key in ("TIFFTAG_DATETIME", "TIFFTAG_DATE", "ACQUISITION_DATE",
                        "DATE_TIME", "DATETIME", "SENSING_TIME"):
                if key in tags:
                    meta.acquisition_date = tags[key]
                    break

            # Sensor / instrument
            for key in ("TIFFTAG_IMAGEDESCRIPTION", "SENSOR", "INSTRUMENT",
                        "SPACECRAFT_ID", "SENSOR_TYPE", "SATELLITE"):
                if key in tags:
                    meta.sensor = tags[key]
                    break

            # Cloud cover
            for key in ("CLOUD_COVER", "CLOUDCOVER", "CLOUD_COVERAGE"):
                if key in tags:
                    try:
                        meta.cloud_cover = float(tags[key])
                    except ValueError:
                        pass
                    break

        except Exception as e:
            logger.debug(f"Could not read TIFF tags: {e}")

    def _estimate_resolution_m(self, ds) -> Optional[float]:
        """
        Estimate the pixel size in meters.
        For projected CRS: use the pixel size directly.
        For geographic CRS (degrees): convert using mid-latitude approximation.
        """
        try:
            crs = ds.crs
            t = ds.transform
            pixel_size = abs(t.a)  # x pixel size in CRS units

            if crs.is_projected:
                # Likely in meters already (most common projected CRS)
                # Check linear unit
                if hasattr(crs, 'linear_units'):
                    unit = crs.linear_units.lower()
                    if "feet" in unit or "foot" in unit:
                        return pixel_size * 0.3048
                    elif "metre" in unit or "meter" in unit:
                        return pixel_size
                return pixel_size
            elif crs.is_geographic:
                # Degrees → approximate meters at mid-latitude
                b = ds.bounds
                mid_lat = (b.top + b.bottom) / 2
                import math
                # 1 degree ≈ 111,132 m at equator, less at higher latitudes
                meters_per_degree = 111_132.92 - 559.82 * math.cos(2 * math.radians(mid_lat)) + 1.175 * math.cos(4 * math.radians(mid_lat))
                return pixel_size * meters_per_degree
            return None
        except Exception:
            return None

    def _detect_modality(self, meta: ImageMetadata) -> str:
        """Heuristically detect image modality from band count and descriptions."""
        band_count = meta.band_count
        band_descs_lower = [b.lower() for b in meta.band_descriptions]

        # SAR keywords
        sar_keywords = ["vv", "vh", "hh", "hv", "backscatter", "sar", "sigma", "gamma"]
        if any(kw in d for kw in sar_keywords for d in band_descs_lower):
            return "sar"

        # Multispectral
        ms_keywords = ["nir", "b08", "b8", "near-infrared", "infrared", "swir", "b11", "b12"]
        if any(kw in d for kw in ms_keywords for d in band_descs_lower):
            return "multispectral"

        # By band count
        if band_count == 1:
            return "sar"  # could also be grayscale, but in RS context often SAR
        elif band_count == 3:
            return "optical"
        elif band_count >= 4:
            return "multispectral"

        return "unknown"

    @staticmethod
    def _pil_mode_to_dtype(mode: str) -> str:
        mapping = {
            "L": "uint8", "RGB": "uint8", "RGBA": "uint8",
            "I": "int32", "F": "float32",
        }
        return mapping.get(mode, "uint8")
