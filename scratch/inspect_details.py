import numpy as np
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))

# 1. Cyan line at middle right: y=110..120, x=430..490
cyan_strip = rgb[110:122, 430:490]
print("Strip at y:110-122, x:430-490:")
print("  R mean:", cyan_strip[:,:,0].mean(), "min:", cyan_strip[:,:,0].min(), "max:", cyan_strip[:,:,0].max())
print("  G mean:", cyan_strip[:,:,1].mean(), "min:", cyan_strip[:,:,1].min(), "max:", cyan_strip[:,:,1].max())
print("  B mean:", cyan_strip[:,:,2].mean(), "min:", cyan_strip[:,:,2].min(), "max:", cyan_strip[:,:,2].max())

# 2. Bottom right plot: y=185..214, x=480..510
br_plot = rgb[185:214, 480:510]
print("\nBottom right plot:")
print("  R mean:", br_plot[:,:,0].mean())
print("  G mean:", br_plot[:,:,1].mean())
print("  B mean:", br_plot[:,:,2].mean())

# 3. Main roads: lakeside road (x:105-118, y:50-180) vs gray rooftops
import scipy.ndimage as ndi
bright = rgb.mean(axis=2)
mean_b = ndi.uniform_filter(bright, size=3)
mean_sq_b = ndi.uniform_filter(bright**2, size=3)
local_std = np.sqrt(np.maximum(mean_sq_b - mean_b**2, 0))

road_std = local_std[50:180, 105:118]
print(f"\nLakeside Road local_std: mean={road_std.mean():.2f}, p90={np.percentile(road_std, 90):.2f}")

br_std = local_std[185:214, 480:510]
print(f"Bottom right plot local_std: mean={br_std.mean():.2f}, p90={np.percentile(br_std, 90):.2f}")
