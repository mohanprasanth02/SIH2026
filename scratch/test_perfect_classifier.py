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

# --- 1. WATER ---
# a) Clear/deep water
is_w_clear = (b > r * 1.05) & (b >= g * 0.80) & (r < 92) & (brightness < 112) & (local_std < 18.0)
# b) Turbid / sediment water
is_w_turbid = (
    (g > r * 1.05) & (b >= r * 0.90) & (b >= g * 0.76) &
    (r < 96) & (brightness < 115) & (ndwi_gr > 0.03) & (local_std < 18.0)
)
# c) Blue canal / reservoir
is_w_blue = (ndwi_br > 0.05) & (r < 92) & (brightness < 120) & (local_std < 18.0)
# d) Eutrophic green lake (Coimbatore lake):
# In green water: G > R * 1.04, G > B * 1.08, R < 95, B < 90, brightness 55..112
# Urban shadows have brightness < 55 and B < 40; the real lake has brightness 60-100 and B >= 40
is_w_green_lake = (
    (g > r * 1.04) & (g > b * 1.08) &
    (r < 95) & (b >= 40) & (b < 90) &
    (brightness >= 55) & (brightness <= 112) &
    (local_std < 22.0)
)

water_cand = is_w_clear | is_w_turbid | is_w_blue | is_w_green_lake

# Contiguous water bodies:
water_mask = np.zeros((h, w), dtype=bool)
if np.any(water_cand):
    labeled_w, num_w = ndi.label(water_cand)
    if num_w > 0:
        counts = np.bincount(labeled_w.ravel())
        # Require cluster >= 100 px so tiny 15px shadows in courtyards are ignored
        valid_ids = np.where(counts >= 100)[0]
        valid_ids = valid_ids[valid_ids != 0]
        if len(valid_ids) > 0:
            water_mask = np.isin(labeled_w, valid_ids)
            # Fill interior ripple/wave holes inside the contiguous water body!
            water_mask = ndi.binary_fill_holes(water_mask)

# --- 2. VEGETATION ---
# Real terrestrial vegetation has high green excess, vivid chroma, or high GLI
is_forest = (
    ~water_mask &
    (g > r * 1.10) & (g > b * 1.15) &
    (gli > 0.05) & (chroma >= 12) & (saturation >= 0.18)
)
is_shadow_veg = (
    ~water_mask &
    (brightness < 60) &
    (g > r * 1.08) & (g > b * 1.10) &
    (chroma >= 8)
)
veg_mask = is_forest | is_shadow_veg

# --- 3. ROADS & TRANSPORTATION CORRIDORS ---
# Evaluated BEFORE general agriculture to prevent dusty asphalt from being mislabeled!
# Roads are continuous corridors of neutral-gray to dusty asphalt:
# |R - G| <= 16, |G - B| <= 36, low saturation (< 0.32), brightness 45..190
is_asphalt = (
    ~water_mask & ~veg_mask &
    (saturation < 0.32) & (chroma < 40) &
    (np.abs(r - g) <= 16) & (np.abs(g - b) <= 36) &
    (brightness >= 45) & (brightness < 125) &
    (gli < 0.10)
)
is_concrete_hwy = (
    ~water_mask & ~veg_mask &
    (saturation < 0.28) & (chroma < 38) &
    (np.abs(r - g) <= 18) & (np.abs(g - b) <= 36) &
    (brightness >= 125) & (brightness <= 195) &
    (gli < 0.08)
)
road_mask = is_asphalt | is_concrete_hwy

# --- 4. BUILT-UP / ROOFTOPS / STRUCTURES ---
is_terracotta_roof = (r > g * 1.08) & (r > b * 1.15) & (brightness > 55)
is_blue_roof = (b > r * 1.12) & (b > g * 1.04) & (brightness >= 60) & ~water_mask
is_bright_structure = (brightness >= 175)
is_urban_texture = (local_std > 8.5) & (brightness >= 70) & (brightness <= 220) & (chroma < 35)

built_mask = (
    ~water_mask & ~veg_mask & ~road_mask &
    (is_terracotta_roof | is_blue_roof | is_bright_structure | is_urban_texture)
)

# --- 5. BARE LAND / SOIL / DIRT ---
bare_mask = (
    ~water_mask & ~veg_mask & ~road_mask & ~built_mask &
    (r > g * 1.02) & (g > b * 1.01) &
    (brightness > 60) & (chroma >= 10)
)

# --- 6. AGRICULTURE (Real cultivated crops / high saturation green fields) ---
agri_mask = (
    ~water_mask & ~veg_mask & ~road_mask & ~built_mask & ~bare_mask &
    (g > r * 1.04) & (g > b * 1.10) &
    (chroma >= 15) & (saturation >= 0.22) &
    (brightness >= 70) & (brightness <= 210) &
    (gli > 0.04)
)

# Assign to mask
mask[water_mask] = 1
mask[agri_mask] = 2
mask[veg_mask] = 3
mask[built_mask] = 4
mask[road_mask] = 5
mask[bare_mask] = 6

# Unassigned fallback
unassigned = (mask == 0)
mask[unassigned & (brightness < 80) & (saturation < 0.25)] = 5  # asphalt
mask[unassigned & (brightness >= 120) & (saturation < 0.25)] = 4 # built-up
mask[unassigned & (r > g) & (g > b)] = 6                         # bare soil
mask[unassigned & (g > r)] = 3                                   # vegetation
mask[unassigned] = 4                                             # default built-up in urban landscape

# Print results
import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import LAND_COVER_CLASSES
total_px = mask.size
print("NEW CLASSIFICATION BREAKDOWN:")
for c_id in sorted(LAND_COVER_CLASSES.keys()):
    cnt = int(np.sum(mask == c_id))
    pct = cnt / total_px * 100
    print(f"  {LAND_COVER_CLASSES[c_id]['name']} ({c_id}): {pct:.2f}% ({cnt} px)")

lake_crop = mask[:, :100]
print(f"\nLake (cols 0..100) Water Coverage: {np.mean(lake_crop == 1)*100:.2f}% ({np.sum(lake_crop == 1)} / {lake_crop.size} px)")
lake_veg = np.sum(lake_crop == 3)
print(f"Lake cols 0..100 false veg: {lake_veg} px ({lake_veg / lake_crop.size * 100:.2f}%)")

road_crop = mask[50:180, 105:118]
print(f"Lakeside Road crop (x:105-118, y:50-180) Road coverage: {np.mean(road_crop == 5)*100:.2f}% ({np.sum(road_crop == 5)} / {road_crop.size} px)")

# Save new visualization
cmap = np.zeros((h, w, 3), dtype=np.uint8)
for c_id, c_meta in LAND_COVER_CLASSES.items():
    cmap[mask == c_id] = c_meta['color']

Image.fromarray(cmap).save('C:/Users/mohan/.gemini/antigravity-ide/brain/0bc72704-fe0e-4cb6-8d9b-f7bc76149502/new_class_map.png')
overlay = (rgb.astype(float) * 0.4 + cmap.astype(float) * 0.6).astype(np.uint8)
Image.fromarray(overlay).save('C:/Users/mohan/.gemini/antigravity-ide/brain/0bc72704-fe0e-4cb6-8d9b-f7bc76149502/new_overlay.png')
print("Saved new_class_map.png and new_overlay.png")
