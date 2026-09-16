import sys
sys.path.insert(0, 'backend')
import numpy as np
import rasterio
import scipy.ndimage as ndi

src = rasterio.open('backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif')
rgb = np.transpose(src.read()[:3], (1, 2, 0))

r = rgb[:, :, 0].astype(float)
g = rgb[:, :, 1].astype(float)
b = rgb[:, :, 2].astype(float)
brightness = (r + g + b) / 3.0
mean_b = ndi.uniform_filter(brightness, size=3)
mean_sq_b = ndi.uniform_filter(brightness**2, size=3)
local_std = np.sqrt(np.maximum(mean_sq_b - mean_b**2, 0))

# In lake: cols 0..100
lake_r = r[:, :100]
lake_g = g[:, :100]
lake_b = b[:, :100]
lake_std = local_std[:, :100]

print("In lake:")
print(f"  g > r * 1.20: {np.mean(lake_g > lake_r * 1.20)*100:.1f}%")
print(f"  g > r * 1.25: {np.mean(lake_g > lake_r * 1.25)*100:.1f}%")
print(f"  b < g * 0.55: {np.mean(lake_b < lake_g * 0.55)*100:.1f}%")
print(f"  (local_std >= 6) & (g > r * 1.25) & (b < g * 0.55): {np.mean((lake_std >= 6) & (lake_g > lake_r * 1.25) & (lake_b < lake_g * 0.55))*100:.2f}%")
