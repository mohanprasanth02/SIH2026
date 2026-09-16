import numpy as np
from PIL import Image
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
h, w = rgb.shape[:2]

import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import SegmentationAdapter

adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)
mask = out.data['mask']

# 1. False water in urban area: mask == 1 but x > 150
false_water = (mask == 1) & (np.arange(w)[None, :] > 150)
print(f"False water pixels (x > 150): {np.sum(false_water)}")
if np.sum(false_water) > 0:
    fw_r = rgb[:, :, 0][false_water].astype(float)
    fw_g = rgb[:, :, 1][false_water].astype(float)
    fw_b = rgb[:, :, 2][false_water].astype(float)
    fw_bright = (fw_r + fw_g + fw_b) / 3.0
    print(f"False water R: [{fw_r.min():.1f}, {fw_r.max():.1f}], mean={fw_r.mean():.1f}")
    print(f"False water G: [{fw_g.min():.1f}, {fw_g.max():.1f}], mean={fw_g.mean():.1f}")
    print(f"False water B: [{fw_b.min():.1f}, {fw_b.max():.1f}], mean={fw_b.mean():.1f}")
    print(f"False water Brightness: [{fw_bright.min():.1f}, {fw_bright.max():.1f}], mean={fw_bright.mean():.1f}")

# 2. Real lake in x < 110
real_lake = (mask == 1) & (np.arange(w)[None, :] < 110)
print(f"\nReal lake detected pixels (x < 110): {np.sum(real_lake)}")
rl_r = rgb[:, :, 0][real_lake].astype(float)
rl_g = rgb[:, :, 1][real_lake].astype(float)
rl_b = rgb[:, :, 2][real_lake].astype(float)
rl_bright = (rl_r + rl_g + rl_b) / 3.0
print(f"Real lake R: [{rl_r.min():.1f}, {rl_r.max():.1f}], mean={rl_r.mean():.1f}")
print(f"Real lake G: [{rl_g.min():.1f}, {rl_g.max():.1f}], mean={rl_g.mean():.1f}")
print(f"Real lake B: [{rl_b.min():.1f}, {rl_b.max():.1f}], mean={rl_b.mean():.1f}")
print(f"Real lake Brightness: [{rl_bright.min():.1f}, {rl_bright.max():.1f}], mean={rl_bright.mean():.1f}")

# 3. Why did false water get classified as water?
# Check which sub-rule triggered for false water
import scipy.ndimage as ndi
r = rgb[:, :, 0].astype(float)
g = rgb[:, :, 1].astype(float)
b = rgb[:, :, 2].astype(float)
brightness = (r + g + b) / 3.0
mean_b = ndi.uniform_filter(brightness, size=3)
mean_sq_b = ndi.uniform_filter(brightness**2, size=3)
local_std = np.sqrt(np.maximum(mean_sq_b - mean_b**2, 0))
ndwi_gr = (g - r) / (g + r + 1e-5)
ndwi_br = (b - r) / (b + r + 1e-5)

is_water_deep = (b > r * 1.05) & (b >= g * 0.80) & (r < 92) & (brightness < 112) & (local_std < 18.0)
is_water_turbid = (
    (g > r * 1.05) & (b >= r * 0.90) & (b >= g * 0.76) &
    (r < 96) & (brightness < 115) & (ndwi_gr > 0.03) & (local_std < 18.0)
)
is_water_blue = (ndwi_br > 0.05) & (r < 92) & (brightness < 120) & (local_std < 18.0)
is_water_green_lake = (
    (local_std < 5.5) &
    (g > r * 1.08) & (g > b * 1.08) &
    (r < 92) & (b < 85) &
    (brightness >= 30) & (brightness <= 105)
)

print(f"\nFalse water trigger breakdown:")
print(f"  deep: {np.sum(false_water & is_water_deep)}")
print(f"  turbid: {np.sum(false_water & is_water_turbid)}")
print(f"  blue: {np.sum(false_water & is_water_blue)}")
print(f"  green lake: {np.sum(false_water & is_water_green_lake)}")
