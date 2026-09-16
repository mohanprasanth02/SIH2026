import numpy as np
import rasterio
import scipy.ndimage as ndi
from pathlib import Path
import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import LAND_COVER_CLASSES

def classify_opt(rgb):
    h, w = rgb.shape[:2]
    r = rgb[:, :, 0].astype(np.float32)
    g = rgb[:, :, 1].astype(np.float32)
    b = rgb[:, :, 2].astype(np.float32)

    brightness = (r + g + b) / 3.0
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    chroma = max_c - min_c
    saturation = chroma / (max_c + 1e-5)

    gli = (2.0 * g - r - b) / (2.0 * g + r + b + 1e-5)
    exg = 2.0 * g - r - b
    ndwi_gr = (g - r) / (g + r + 1e-5)
    ndwi_br = (b - r) / (b + r + 1e-5)

    mean_b = ndi.uniform_filter(brightness, size=3)
    mean_sq_b = ndi.uniform_filter(brightness**2, size=3)
    local_std = np.sqrt(np.maximum(mean_sq_b - mean_b**2, 0))

    mask = np.zeros((h, w), dtype=np.int32)

    # 1. Water
    is_w_clear = (b > r * 1.05) & (b >= g * 0.80) & (r < 92) & (brightness < 112) & (local_std < 18.0)
    is_w_turbid = (
        (g > r * 1.05) & (b >= r * 0.90) & (b >= g * 0.76) &
        (r < 96) & (brightness < 115) & (ndwi_gr > 0.03) & (local_std < 18.0)
    )
    is_w_blue = (ndwi_br > 0.05) & (r < 92) & (brightness < 120) & (local_std < 18.0)
    is_w_green_lake = (
        (g > r * 1.04) & (g > b * 1.08) &
        (r < 95) & (b >= 40) & (b < 90) &
        (brightness >= 55) & (brightness <= 112) &
        (local_std < 22.0)
    )

    water_mask = np.zeros((h, w), dtype=bool)
    w_blue_cand = is_w_clear | is_w_turbid | is_w_blue
    if np.any(w_blue_cand):
        lw, nw = ndi.label(w_blue_cand)
        if nw > 0:
            counts = np.bincount(lw.ravel())
            v = np.where(counts >= 60)[0]
            v = v[v != 0]
            if len(v) > 0:
                water_mask |= np.isin(lw, v)

    if np.any(is_w_green_lake):
        lw, nw = ndi.label(is_w_green_lake)
        if nw > 0:
            counts = np.bincount(lw.ravel())
            v = np.where(counts >= 250)[0]
            v = v[v != 0]
            if len(v) > 0:
                water_mask |= np.isin(lw, v)

    if np.any(water_mask):
        water_mask = ndi.binary_fill_holes(water_mask)

    # 2. Vegetation
    is_forest = (
        ~water_mask &
        (g > r * 1.08) & (g > b * 1.12) &
        (gli > 0.04) & (chroma >= 10) & (saturation >= 0.16)
    )
    is_shadow_veg = (
        ~water_mask &
        (brightness < 60) &
        (g > r * 1.08) & (g > b * 1.10) &
        (chroma >= 8)
    )
    veg_mask = is_forest | is_shadow_veg

    # 3. Roofs
    is_terracotta_roof = ~water_mask & ~veg_mask & (r > g * 1.12) & (r > b * 1.25) & (brightness > 55)
    is_blue_roof = ~water_mask & ~veg_mask & (b > r * 1.15) & (b > g * 1.06) & (brightness >= 60)
    primary_roofs = is_terracotta_roof | is_blue_roof

    # 4. Roads
    is_asphalt = (
        ~water_mask & ~veg_mask & ~primary_roofs &
        (saturation < 0.32) & (chroma < 42) &
        (np.abs(r - g) <= 15) & (np.abs(g - b) <= 38) &
        (brightness >= 45) & (brightness < 125) &
        (gli < 0.10)
    )
    is_concrete_hwy = (
        ~water_mask & ~veg_mask & ~primary_roofs &
        (saturation < 0.28) & (chroma < 40) &
        (np.abs(r - g) <= 16) & (np.abs(g - b) <= 38) &
        (brightness >= 125) & (brightness <= 185) &
        (gli < 0.08)
    )
    road_mask = is_asphalt | is_concrete_hwy

    # 5. Bare land
    bare_mask = (
        ~water_mask & ~veg_mask & ~road_mask & ~primary_roofs &
        (r > g * 1.04) & (g > b * 1.02) &
        (brightness > 65) & (chroma >= 12)
    )

    # 6. Built-up
    built_mask = (
        ~water_mask & ~veg_mask & ~road_mask & ~bare_mask &
        (primary_roofs | (brightness >= 70))
    )

    # 7. Agriculture (real farmland)
    agri_mask = (
        ~water_mask & ~veg_mask & ~road_mask & ~built_mask & ~bare_mask &
        (g > r * 1.05) & (g > b * 1.12) &
        (chroma >= 15) & (saturation >= 0.22) &
        (brightness >= 70) & (brightness <= 210) &
        (gli > 0.04)
    )

    mask[water_mask] = 1
    mask[agri_mask] = 2
    mask[veg_mask] = 3
    mask[built_mask] = 4
    mask[road_mask] = 5
    mask[bare_mask] = 6

    unassigned = (mask == 0)
    mask[unassigned & (brightness < 80) & (saturation < 0.25)] = 5
    mask[unassigned] = 4
    return mask

# Test on 6 images
test_files = [
    '2cb0885f-e1cc-49be-8904-d894c741857a.tif', # Coimbatore
    '1c63773b-f493-4fa5-b012-f7d1af7ae252.tif',
    '32d760d6-7ef6-4b7f-8e54-3d8048f8a896.tif',
    '56854a89-8a89-438c-b5dd-e3685a0ded25.tif',
    '79c10304-7885-4118-80c8-6ab2ecbd73ec.tif',
    '86f794de-dd49-4fcd-a330-a48a09291d7e.tif'
]

for fname in test_files:
    fpath = Path('backend/data/uploads') / fname
    if not fpath.exists():
        continue
    with rasterio.open(fpath) as src:
        arr = src.read()
    if arr.shape[0] >= 3:
        rgb = np.transpose(arr[:3], (1, 2, 0))
    else:
        rgb = np.stack([arr[0]]*3, axis=-1)
    
    m = classify_opt(rgb)
    tot = m.size
    print(f"\n--- {fname} ({rgb.shape[1]}x{rgb.shape[0]}) ---")
    for cid in [1, 2, 3, 4, 5, 6]:
        cnt = np.sum(m == cid)
        pct = cnt / tot * 100
        if pct > 0.1:
            print(f"  {LAND_COVER_CLASSES[cid]['name']}: {pct:.1f}%")
