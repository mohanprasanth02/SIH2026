"""
SatQuery AI - Band-Aware Spectral Indices
Calculates NDVI, NDWI, NDBI etc. only when required bands are present.
Never fabricates spectral index results.
"""
import logging
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import rasterio
    AVAILABLE = True
except ImportError:
    AVAILABLE = False
    logger.warning("numpy/rasterio unavailable - spectral indices disabled")


@dataclass
class IndexResult:
    """Result of a spectral index calculation."""
    index_name: str
    available: bool
    reason: str = ""          # why unavailable, if not available
    index_array: Optional["np.ndarray"] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean_val: Optional[float] = None
    std_val: Optional[float] = None
    positive_percentage: Optional[float] = None  # fraction of pixels > threshold
    bands_used: List[str] = None

    def __post_init__(self):
        if self.bands_used is None:
            self.bands_used = []


class SpectralIndices:
    """
    Calculates standard remote-sensing spectral indices.

    All methods check if the required bands are present before computing.
    Returns IndexResult with available=False and descriptive reason
    if required bands are missing.
    """

    # Common band name patterns for each semantic band
    BAND_PATTERNS = {
        "red":   ["red", "b4", "b04", "band4", "band_4", "r"],
        "green": ["green", "b3", "b03", "band3", "band_3", "g"],
        "blue":  ["blue", "b2", "b02", "band2", "band_2", "b"],
        "nir":   ["nir", "b8", "b08", "band8", "band_8", "near-infrared", "nearir",
                  "b7", "b07", "nir08", "nir09"],
        "swir1": ["swir1", "swir-1", "b11", "b5", "b05", "band11", "band_11"],
        "swir2": ["swir2", "swir-2", "b12", "b7", "b07", "band12", "band_12"],
    }

    def find_band_index(
        self,
        band_descriptions: List[str],
        semantic: str,
    ) -> Optional[int]:
        """
        Find the 1-based band index for a semantic band name.
        Returns None if not found.
        """
        patterns = self.BAND_PATTERNS.get(semantic, [])
        for i, desc in enumerate(band_descriptions):
            desc_lower = desc.lower().strip()
            for pat in patterns:
                if pat in desc_lower or desc_lower == pat:
                    return i + 1  # 1-based
        return None

    def load_band(
        self, filepath: str, band_index: int, nodata: Optional[float] = None
    ) -> Optional["np.ndarray"]:
        """Load a single band as float32 array, masking nodata."""
        if not AVAILABLE:
            return None
        try:
            with rasterio.open(filepath) as ds:
                arr = ds.read(band_index).astype(np.float32)
                if nodata is not None:
                    arr[arr == nodata] = np.nan
                return arr
        except Exception as e:
            logger.error(f"Failed to load band {band_index}: {e}")
            return None

    def ndvi(
        self,
        filepath: str,
        band_descriptions: List[str],
        nodata: Optional[float] = None,
    ) -> IndexResult:
        """
        Normalized Difference Vegetation Index.
        NDVI = (NIR - Red) / (NIR + Red)
        Range: [-1, 1]. Vegetation typically > 0.2
        Requires: NIR, Red bands.
        """
        nir_idx = self.find_band_index(band_descriptions, "nir")
        red_idx = self.find_band_index(band_descriptions, "red")

        if nir_idx is None or red_idx is None:
            return IndexResult(
                index_name="NDVI",
                available=False,
                reason=(
                    "NDVI unavailable: NIR band not found in image. "
                    f"Detected bands: {band_descriptions}. "
                    "Required: NIR (e.g. B08 for Sentinel-2) and Red (e.g. B04)."
                ),
            )

        if not AVAILABLE:
            return IndexResult(index_name="NDVI", available=False, reason="numpy/rasterio unavailable")

        nir = self.load_band(filepath, nir_idx, nodata)
        red = self.load_band(filepath, red_idx, nodata)

        if nir is None or red is None:
            return IndexResult(index_name="NDVI", available=False, reason="Failed to load band data")

        with np.errstate(divide="ignore", invalid="ignore"):
            ndvi = np.where(
                (nir + red) != 0,
                (nir - red) / (nir + red),
                np.nan,
            )

        valid = ndvi[~np.isnan(ndvi)]
        if valid.size == 0:
            return IndexResult(index_name="NDVI", available=False, reason="All pixels are NoData")

        veg_threshold = 0.2
        veg_pixels = np.sum(valid > veg_threshold)
        total_valid = valid.size

        return IndexResult(
            index_name="NDVI",
            available=True,
            index_array=ndvi,
            min_val=float(np.nanmin(ndvi)),
            max_val=float(np.nanmax(ndvi)),
            mean_val=float(np.nanmean(ndvi)),
            std_val=float(np.nanstd(ndvi)),
            positive_percentage=float(veg_pixels / total_valid * 100),
            bands_used=[f"NIR (Band {nir_idx})", f"Red (Band {red_idx})"],
        )

    def ndwi(
        self,
        filepath: str,
        band_descriptions: List[str],
        nodata: Optional[float] = None,
    ) -> IndexResult:
        """
        Normalized Difference Water Index (McFeeters, 1996).
        NDWI = (Green - NIR) / (Green + NIR)
        Range: [-1, 1]. Water typically > 0.0
        Requires: Green, NIR bands.
        """
        green_idx = self.find_band_index(band_descriptions, "green")
        nir_idx = self.find_band_index(band_descriptions, "nir")

        if green_idx is None or nir_idx is None:
            missing = []
            if green_idx is None:
                missing.append("Green")
            if nir_idx is None:
                missing.append("NIR")
            return IndexResult(
                index_name="NDWI",
                available=False,
                reason=(
                    f"NDWI unavailable: missing band(s): {', '.join(missing)}. "
                    f"Detected bands: {band_descriptions}."
                ),
            )

        if not AVAILABLE:
            return IndexResult(index_name="NDWI", available=False, reason="numpy/rasterio unavailable")

        green = self.load_band(filepath, green_idx, nodata)
        nir = self.load_band(filepath, nir_idx, nodata)

        if green is None or nir is None:
            return IndexResult(index_name="NDWI", available=False, reason="Failed to load band data")

        with np.errstate(divide="ignore", invalid="ignore"):
            ndwi = np.where(
                (green + nir) != 0,
                (green - nir) / (green + nir),
                np.nan,
            )

        valid = ndwi[~np.isnan(ndwi)]
        if valid.size == 0:
            return IndexResult(index_name="NDWI", available=False, reason="All pixels are NoData")

        water_threshold = 0.0
        water_pixels = np.sum(valid > water_threshold)
        total_valid = valid.size

        return IndexResult(
            index_name="NDWI",
            available=True,
            index_array=ndwi,
            min_val=float(np.nanmin(ndwi)),
            max_val=float(np.nanmax(ndwi)),
            mean_val=float(np.nanmean(ndwi)),
            std_val=float(np.nanstd(ndwi)),
            positive_percentage=float(water_pixels / total_valid * 100),
            bands_used=[f"Green (Band {green_idx})", f"NIR (Band {nir_idx})"],
        )

    def ndbi(
        self,
        filepath: str,
        band_descriptions: List[str],
        nodata: Optional[float] = None,
    ) -> IndexResult:
        """
        Normalized Difference Built-up Index.
        NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
        Range: [-1, 1]. Built-up typically > 0.0
        Requires: SWIR1, NIR bands.
        """
        swir1_idx = self.find_band_index(band_descriptions, "swir1")
        nir_idx = self.find_band_index(band_descriptions, "nir")

        if swir1_idx is None or nir_idx is None:
            missing = []
            if swir1_idx is None:
                missing.append("SWIR1")
            if nir_idx is None:
                missing.append("NIR")
            return IndexResult(
                index_name="NDBI",
                available=False,
                reason=(
                    f"NDBI unavailable: missing band(s): {', '.join(missing)}. "
                    f"Detected bands: {band_descriptions}."
                ),
            )

        if not AVAILABLE:
            return IndexResult(index_name="NDBI", available=False, reason="numpy/rasterio unavailable")

        swir1 = self.load_band(filepath, swir1_idx, nodata)
        nir = self.load_band(filepath, nir_idx, nodata)

        if swir1 is None or nir is None:
            return IndexResult(index_name="NDBI", available=False, reason="Failed to load band data")

        with np.errstate(divide="ignore", invalid="ignore"):
            ndbi = np.where(
                (swir1 + nir) != 0,
                (swir1 - nir) / (swir1 + nir),
                np.nan,
            )

        valid = ndbi[~np.isnan(ndbi)]
        if valid.size == 0:
            return IndexResult(index_name="NDBI", available=False, reason="All pixels are NoData")

        builtup_threshold = 0.0
        bu_pixels = np.sum(valid > builtup_threshold)
        total_valid = valid.size

        return IndexResult(
            index_name="NDBI",
            available=True,
            index_array=ndbi,
            min_val=float(np.nanmin(ndbi)),
            max_val=float(np.nanmax(ndbi)),
            mean_val=float(np.nanmean(ndbi)),
            std_val=float(np.nanstd(ndbi)),
            positive_percentage=float(bu_pixels / total_valid * 100),
            bands_used=[f"SWIR1 (Band {swir1_idx})", f"NIR (Band {nir_idx})"],
        )
