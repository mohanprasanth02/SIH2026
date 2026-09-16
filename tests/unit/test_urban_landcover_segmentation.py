import sys
from pathlib import Path
import pytest
import numpy as np

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.models.adapters.segmentation import get_segmentation_adapter, LAND_COVER_CLASSES


def test_synthetic_urban_scene_no_false_agriculture():
    """Test that synthetic urban structures (concrete roofs, terracotta tiles, asphalt) are not misclassified as agriculture."""
    adapter = get_segmentation_adapter()

    # Create synthetic urban block (100x100)
    # Background: dark asphalt road
    img = np.full((100, 100, 3), [60, 62, 55], dtype=np.uint8)

    # Building 1: Concrete rooftop (R=175, G=170, B=155)
    img[10:45, 10:45] = [175, 170, 155]

    # Building 2: Terracotta clay tile roof (R=180, G=90, B=65)
    img[10:45, 55:90] = [180, 90, 65]

    # Building 3: Bright reflective metal roof (R=210, G=215, B=205)
    img[55:90, 10:45] = [210, 215, 205]

    # Garden: Urban green tree canopy (R=35, G=85, B=25)
    img[55:90, 55:90] = [35, 85, 25]

    out = adapter.infer(image_array=img.astype(np.float32))
    assert out.success is True

    class_counts = out.data["class_counts"]
    # Agriculture (Class 2) must be 0% in an urban environment
    assert class_counts[2] == 0, f"Expected 0 agriculture pixels, got {class_counts[2]}"

    # Built-up (Class 4) must capture the 3 building blocks (~36-45%)
    built_pct = next(c["percentage"] for c in out.data["class_info"] if c["class_id"] == 4)
    assert 36.0 <= built_pct <= 45.0, f"Expected built-up ~36-45%, got {built_pct}%"

    # Road (Class 5) must capture the dark asphalt background (~40-52%)
    road_pct = next(c["percentage"] for c in out.data["class_info"] if c["class_id"] == 5)
    assert 40.0 <= road_pct <= 52.0, f"Expected road ~40-52%, got {road_pct}%"

    # Vegetation (Class 3) must correctly capture the garden (~10-15%)
    veg_pct = next(c["percentage"] for c in out.data["class_info"] if c["class_id"] == 3)
    assert 10.0 <= veg_pct <= 15.0, f"Expected vegetation ~10-15%, got {veg_pct}%"


def test_user_uploaded_satellite_scene():
    """Test the exact satellite scene uploaded by the user to verify fix for SIH issue."""
    import rasterio

    filepath = Path(__file__).resolve().parent.parent.parent / "backend/data/uploads/c29324c0-4def-4eb1-8a0d-67032bc2214e.tif"
    if not filepath.exists():
        pytest.skip(f"Test image not present at {filepath}")

    with rasterio.open(str(filepath)) as ds:
        arr = np.stack([ds.read(i + 1).astype(np.float32) for i in range(ds.count)], axis=-1)

    adapter = get_segmentation_adapter()
    out = adapter.infer(image_array=arr)
    assert out.success is True

    class_counts = out.data["class_counts"]
    total = out.data["total_pixels"]

    agri_pct = (class_counts[2] / total) * 100.0
    built_pct = (class_counts[4] / total) * 100.0

    # Agriculture should be negligible or 0% (down from 60.9%)
    assert agri_pct < 1.0, f"False agriculture still too high: {agri_pct}%"

    # Built-up should be the dominant class
    assert built_pct > 50.0, f"Built-up should be dominant, got: {built_pct}%"
