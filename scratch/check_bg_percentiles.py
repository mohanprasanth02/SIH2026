import numpy as np
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
r = rgb[:, :, 0].astype(float)
g = rgb[:, :, 1].astype(float)
b = rgb[:, :, 2].astype(float)

# Lake area: columns 0 to 100
lake_r = r[:, :100]
lake_g = g[:, :100]
lake_b = b[:, :100]
lake_bg = lake_b / (lake_g + 1e-5)
lake_br = lake_b / (lake_r + 1e-5)

print("Lake B/G percentiles:")
for p in [1, 5, 10, 25, 50, 75, 90, 99]:
    print(f"  p{p}: {np.percentile(lake_bg, p):.3f}")

print("\nLake B/R percentiles:")
for p in [1, 5, 10, 25, 50, 75, 90, 99]:
    print(f"  p{p}: {np.percentile(lake_br, p):.3f}")

# And what about the urban foliage that was falsely marked?
# y in [180, 214], x in [240, 300]
urban_r = r[180:214, 240:300]
urban_g = g[180:214, 240:300]
urban_b = b[180:214, 240:300]
urban_bg = urban_b / (urban_g + 1e-5)
print("\nUrban shadow B/G percentiles:")
for p in [1, 5, 10, 25, 50, 75, 90, 99]:
    print(f"  p{p}: {np.percentile(urban_bg, p):.3f}")
