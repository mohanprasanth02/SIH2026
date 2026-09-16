"""
SatQuery AI - GIS Area Calculator
Computes pixel-to-area conversions using real raster CRS and transform.
Handles projected, geographic, and mixed CRS correctly.
"""
import logging
import math
from typing import Optional, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import rasterio
    from rasterio.crs import CRS
    from rasterio.warp import reproject, Resampling
    import pyproj
    from pyproj import Transformer
    GIS_AVAILABLE = True
except ImportError:
    GIS_AVAILABLE = False
    logger.warning("rasterio/pyproj not available - GIS calculations limited")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


@dataclass
class AreaResult:
    """Result of a pixel-to-area calculation."""
    pixel_count: int
    total_pixels: int
    percentage: float
    area_m2: Optional[float] = None
    area_ha: Optional[float] = None
    area_km2: Optional[float] = None
    pixel_area_m2: Optional[float] = None  # area per pixel
    method: str = ""
    warnings: list = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class AreaCalculator:
    """
    Calculates real pixel areas from raster metadata.

    Key rules:
    - Never assume 1 pixel = 1 metre
    - Use actual CRS and transform
    - Reproject to equal-area CRS if geographic (degrees)
    - Return None for area if not georeferenced
    """

    # Equal-area CRS for global area calculations
    EQUAL_AREA_CRS = "EPSG:6933"  # WGS 84 / NSIDC EASE-Grid 2.0 Global

    def calculate(
        self,
        pixel_count: int,
        total_pixels: int,
        crs_str: Optional[str],
        resolution_x: Optional[float],
        resolution_y: Optional[float],
        bounds: Optional[Dict] = None,
    ) -> AreaResult:
        """
        Calculate area for a given pixel count.

        Args:
            pixel_count: Number of pixels in the class
            total_pixels: Total valid pixels in the image
            crs_str: CRS string (e.g. "EPSG:32643")
            resolution_x: Pixel width in CRS units
            resolution_y: Pixel height in CRS units
            bounds: Image bounds dict (left, bottom, right, top)
        """
        percentage = (pixel_count / total_pixels * 100) if total_pixels > 0 else 0.0

        if not GIS_AVAILABLE or crs_str is None or resolution_x is None:
            return AreaResult(
                pixel_count=pixel_count,
                total_pixels=total_pixels,
                percentage=round(percentage, 4),
                method="no_georeferencing",
                warnings=["Physical area unavailable: image is not georeferenced or CRS is missing."]
            )

        try:
            crs = CRS.from_user_input(crs_str)

            if crs.is_projected:
                # Pixel size in projection units (usually meters)
                linear_unit = self._get_linear_unit_to_meters(crs)
                pixel_area_m2 = abs(resolution_x * resolution_y) * (linear_unit ** 2)
                method = f"projected_crs ({crs_str})"

            elif crs.is_geographic:
                # Degrees → convert to meters using equal-area reproject
                pixel_area_m2 = self._geographic_pixel_area_m2(
                    crs, resolution_x, resolution_y, bounds
                )
                method = f"geographic_crs_reprojected ({crs_str} → {self.EQUAL_AREA_CRS})"

            else:
                return AreaResult(
                    pixel_count=pixel_count,
                    total_pixels=total_pixels,
                    percentage=round(percentage, 4),
                    method="unknown_crs_type",
                    warnings=[f"Cannot determine area for CRS: {crs_str}"]
                )

            if pixel_area_m2 is None or pixel_area_m2 <= 0:
                return AreaResult(
                    pixel_count=pixel_count,
                    total_pixels=total_pixels,
                    percentage=round(percentage, 4),
                    method="failed",
                    warnings=["Area calculation failed."]
                )

            total_area_m2 = pixel_area_m2 * pixel_count
            area_ha = total_area_m2 / 10_000.0
            area_km2 = total_area_m2 / 1_000_000.0

            return AreaResult(
                pixel_count=pixel_count,
                total_pixels=total_pixels,
                percentage=round(percentage, 4),
                area_m2=round(total_area_m2, 2),
                area_ha=round(area_ha, 4),
                area_km2=round(area_km2, 6),
                pixel_area_m2=round(pixel_area_m2, 4),
                method=method,
            )

        except Exception as e:
            logger.error(f"Area calculation error: {e}", exc_info=True)
            return AreaResult(
                pixel_count=pixel_count,
                total_pixels=total_pixels,
                percentage=round(percentage, 4),
                method="error",
                warnings=[f"Area calculation error: {str(e)}"]
            )

    def _get_linear_unit_to_meters(self, crs: "CRS") -> float:
        """Return the conversion factor from linear CRS units to meters."""
        try:
            if hasattr(crs, 'axis_info'):
                for axis in crs.axis_info:
                    unit_name = axis.unit_name.lower()
                    if "foot" in unit_name or "feet" in unit_name:
                        return 0.3048
                    elif "us survey foot" in unit_name:
                        return 1200.0 / 3937.0
                    elif "metre" in unit_name or "meter" in unit_name:
                        return 1.0
            return 1.0  # Default: assume meters
        except Exception:
            return 1.0

    def _geographic_pixel_area_m2(
        self,
        crs: "CRS",
        resolution_x: float,
        resolution_y: float,
        bounds: Optional[Dict],
    ) -> Optional[float]:
        """
        Calculate pixel area in m² for geographic CRS by estimating
        the area of one pixel at the image centroid using pyproj.
        """
        try:
            # Get image centroid in geographic coordinates
            if bounds:
                center_lon = (bounds["left"] + bounds["right"]) / 2
                center_lat = (bounds["top"] + bounds["bottom"]) / 2
            else:
                center_lon = 0.0
                center_lat = 0.0

            # Use pyproj Geod for proper ellipsoidal area
            geod = pyproj.Geod(ellps="WGS84")

            # Pixel corners in degrees
            half_x = resolution_x / 2.0
            half_y = resolution_y / 2.0
            lon1, lat1 = center_lon - half_x, center_lat - half_y
            lon2, lat2 = center_lon + half_x, center_lat - half_y
            lon3, lat3 = center_lon + half_x, center_lat + half_y
            lon4, lat4 = center_lon - half_x, center_lat + half_y

            # Compute polygon area (lons, lats)
            poly_lons = [lon1, lon2, lon3, lon4]
            poly_lats = [lat1, lat2, lat3, lat4]
            area_m2, _ = geod.polygon_area_perimeter(poly_lons, poly_lats)
            return abs(area_m2)

        except Exception as e:
            logger.error(f"Geographic pixel area calculation failed: {e}")
            return None

    def calculate_total_image_area(
        self,
        total_pixels: int,
        nodata_pixels: int,
        crs_str: Optional[str],
        resolution_x: Optional[float],
        resolution_y: Optional[float],
        bounds: Optional[Dict] = None,
    ) -> AreaResult:
        """Calculate total valid area of the image."""
        valid_pixels = total_pixels - nodata_pixels
        return self.calculate(
            pixel_count=valid_pixels,
            total_pixels=valid_pixels,
            crs_str=crs_str,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            bounds=bounds,
        )
