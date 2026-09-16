import numpy as np
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
h, w = rgb.shape[:2]

r = rgb[:, :, 0].astype(float)
g = rgb[:, :, 1].astype(float)
b = rgb[:, :, 2].astype(float)
bright = (r + g + b) / 3.0
max_c = np.maximum(np.maximum(r, g), b)
min_c = np.minimum(np.minimum(r, g), b)
chroma = max_c - min_c
sat = chroma / (max_c + 1e-5)
gli = (2.0 * g - r - b) / (2.0 * g + r + b + 1e-5)
exg = 2.0 * g - r - b

# Real vegetation samples: dense green trees in parks/neighborhoods
# e.g. y: 60-90, x: 200-240
veg_crop = rgb[60:90, 200:240]
vr = veg_crop[:, :, 0].astype(float)
vg = veg_crop[:, :, 1].astype(float)
vb = veg_crop[:, :, 2].astype(float)
v_gr = vg / (vr + 1e-5)
v_gli = (2.0 * vg - vr - vb) / (2.0 * vg + vr + vb + 1e-5)

print("VEGETATION SAMPLE:")
print(f"  G/R: mean={v_gr.mean():.2f}, p10={np.percentile(v_gr, 10):.2f}, min={v_gr.min():.2f}")
print(f"  GLI: mean={v_gli.mean():.3f}, p10={np.percentile(v_gli, 10):.3f}")
print(f"  |R - G|: mean={np.abs(vr - vg).mean():.1f}")

# Lakeside road:
road_crop = rgb[50:180, 105:118]
rr = road_crop[:, :, 0].astype(float)
rg = road_crop[:, :, 1].astype(float)
rb = road_crop[:, :, 2].astype(float)
r_gr = rg / (rr + 1e-5)
r_gli = (2.0 * rg - rr - rb) / (2.0 * rg + rr + rb + 1e-5)

print("\nLAKESIDE ROAD:")
print(f"  G/R: mean={r_gr.mean():.2f}, p90={np.percentile(r_gr, 90):.2f}")
print(f"  GLI: mean={r_gli.mean():.3f}, p90={np.percentile(r_gli, 90):.3f}")
print(f"  |R - G|: mean={np.abs(rr - rg).mean():.1f}, p90={np.percentile(np.abs(rr - rg), 90):.1f}")
print(f"  Saturation: mean={sat[50:180, 105:118].mean():.3f}")
