import numpy as np
from PIL import Image
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
h, w = rgb.shape[:2]

r = rgb[:, :, 0].astype(float)
g = rgb[:, :, 1].astype(float)
b = rgb[:, :, 2].astype(float)

import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import SegmentationAdapter

adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)
mask = out.data['mask']

false_water = (mask == 1) & (np.arange(w)[None, :] > 150)
real_lake = (mask == 1) & (np.arange(w)[None, :] < 110)

exg = 2.0 * g - r - b
gli = (2.0 * g - r - b) / (2.0 * g + r + b + 1e-5)
b_div_g = b / (g + 1e-5)
b_div_r = b / (r + 1e-5)
g_div_r = g / (r + 1e-5)

print("REAL LAKE (x < 110):")
print(f"  B / G: mean={b_div_g[real_lake].mean():.3f}, min={b_div_g[real_lake].min():.3f}, max={b_div_g[real_lake].max():.3f}")
print(f"  B / R: mean={b_div_r[real_lake].mean():.3f}, min={b_div_r[real_lake].min():.3f}, max={b_div_r[real_lake].max():.3f}")
print(f"  G / R: mean={g_div_r[real_lake].mean():.3f}, min={g_div_r[real_lake].min():.3f}, max={g_div_r[real_lake].max():.3f}")
print(f"  GLI:   mean={gli[real_lake].mean():.3f}, min={gli[real_lake].min():.3f}, max={gli[real_lake].max():.3f}")

print("\nFALSE WATER (x > 150):")
print(f"  B / G: mean={b_div_g[false_water].mean():.3f}, min={b_div_g[false_water].min():.3f}, max={b_div_g[false_water].max():.3f}")
print(f"  B / R: mean={b_div_r[false_water].mean():.3f}, min={b_div_r[false_water].min():.3f}, max={b_div_r[false_water].max():.3f}")
print(f"  G / R: mean={g_div_r[false_water].mean():.3f}, min={g_div_r[false_water].min():.3f}, max={g_div_r[false_water].max():.3f}")
print(f"  GLI:   mean={gli[false_water].mean():.3f}, min={gli[false_water].min():.3f}, max={gli[false_water].max():.3f}")
