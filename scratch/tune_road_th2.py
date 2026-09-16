import numpy as np
from PIL import Image
import rasterio
import scipy.ndimage as ndi

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
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

# --- 1. WATER BODIES ---
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
        v = np.where(counts >= 25)[0]
        v = v[v != 0]
        if len(v) > 0:
            water_mask |= np.isin(lw, v)

if np.any(is_w_green_lake):
    lw, nw = ndi.label(is_w_green_lake)
    if nw > 0:
        counts = np.bincount(lw.ravel())
        v = np.where(counts >= 300)[0]
        v = v[v != 0]
        if len(v) > 0:
            water_mask |= np.isin(lw, v)

if np.any(water_mask):
    water_mask = ndi.binary_fill_holes(water_mask)

# --- 2. VEGETATION ---
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

# --- 3. DISTINCT ROOFS ---
is_terracotta_roof = ~water_mask & ~veg_mask & (r > g * 1.12) & (r > b * 1.25) & (brightness > 55)
is_blue_roof = ~water_mask & ~veg_mask & (b > r * 1.15) & (b > g * 1.06) & (brightness >= 60)
primary_roofs = is_terracotta_roof | is_blue_roof

# --- 4. ROADS & HIGHWAYS ---
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

# --- 5. BARE LAND & SOIL ---
bare_mask = (
    ~water_mask & ~veg_mask & ~road_mask & ~primary_roofs &
    (r > g * 1.04) & (g > b * 1.02) &
    (brightness > 65) & (chroma >= 12)
)

# --- 6. BUILT-UP ---
built_mask = (
    ~water_mask & ~veg_mask & ~road_mask & ~bare_mask &
    (primary_roofs | (brightness >= 70))
)

# Assign to mask
mask[water_mask] = 1
mask[veg_mask] = 3
mask[road_mask] = 5
mask[bare_mask] = 6
mask[built_mask] = 4

# Unassigned fallback
unassigned = (mask == 0)
mask[unassigned & (brightness < 80) & (saturation < 0.25)] = 5
mask[unassigned] = 4

import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import LAND_COVER_CLASSES
total_px = mask.size
print("REFINED CLASSIFICATION BREAKDOWN:")
for c_id in sorted(LAND_COVER_CLASSES.keys()):
    cnt = int(np.sum(mask == c_id))
    pct = cnt / total_px * 100
    print(f"  {LAND_COVER_CLASSES[c_id]['name']} ({c_id}): {pct:.2f}% ({cnt} px)")

lake_crop = mask[:, :100]
lake_water = np.sum(lake_crop == 1)
print(f"\nLake (cols 0..100) Water Coverage: {lake_water / lake_crop.size * 100:.2f}% ({lake_water} / {lake_crop.size} px)")

bund_center = mask[50:180, 111]
print(f"Bund road center (x=111, y:50-180) Road coverage: {np.mean(bund_center == 5)*100:.1f}%")

hwy_center = mask[20:30, 150:200]
print(f"Top Highway center (y:20-30, x:150-200) Road coverage: {np.mean(hwy_center == 5)*100:.1f}%")

urban_water = np.sum(mask[:, 120:] == 1)
print(f"Urban area (x > 120) false water count: {urban_water} px")

cmap = np.zeros((h, w, 3), dtype=np.uint8)
for c_id, c_meta in LAND_COVER_CLASSES.items():
    cmap[mask == c_id] = c_meta['color']

Image.fromarray(cmap).save('C:/Users/mohan/.gemini/antigravity-ide/brain/0bc72704-fe0e-4cb6-8d9b-f7bc76149502/optimal_v2_map.png')
overlay = (rgb.astype(float) * 0.4 + cmap.astype(float) * 0.6).astype(np.uint8)
Image.fromarray(overlay).save('C:/Users/mohan/.gemini/antigravity-ide/brain/0bc72704-fe0e-4cb6-8d9b-f7bc76149502/optimal_v2_overlay.png')
print("Saved optimal_v2_map.png and optimal_v2_overlay.png")
