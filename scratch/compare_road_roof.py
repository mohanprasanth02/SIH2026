import numpy as np
import rasterio
import scipy.ndimage as ndi

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
bright = rgb.mean(axis=2).astype(float)

# Bund road center line: x = 111, y from 50 to 180
road_line = bright[50:180, 111]
road_r = rgb[50:180, 111, 0]
road_g = rgb[50:180, 111, 1]
road_b = rgb[50:180, 111, 2]

print("BUND ROAD CENTER LINE (x=111, y:50-180):")
print(f"  R: mean={road_r.mean():.1f}, std={road_r.std():.1f}")
print(f"  G: mean={road_g.mean():.1f}, std={road_g.std():.1f}")
print(f"  B: mean={road_b.mean():.1f}, std={road_b.std():.1f}")
print(f"  Brightness: mean={road_line.mean():.1f}, min={road_line.min():.1f}, max={road_line.max():.1f}")

# Top highway curve: y: 20-30, x: 150-200
hwy_r = rgb[20:30, 150:200, 0]
hwy_g = rgb[20:30, 150:200, 1]
hwy_b = rgb[20:30, 150:200, 2]
hwy_bright = (hwy_r + hwy_g + hwy_b)/3.0
print("\nTOP HIGHWAY (y:20-30, x:150-200):")
print(f"  R: mean={hwy_r.mean():.1f}")
print(f"  G: mean={hwy_g.mean():.1f}")
print(f"  B: mean={hwy_b.mean():.1f}")
print(f"  Brightness: mean={hwy_bright.mean():.1f}")

# Residential rooftops: y: 140-180, x: 380-450
roof_r = rgb[140:180, 380:450, 0]
roof_g = rgb[140:180, 380:450, 1]
roof_b = rgb[140:180, 380:450, 2]
roof_bright = (roof_r + roof_g + roof_b)/3.0
print("\nRESIDENTIAL ROOFS (y:140-180, x:380-450):")
print(f"  R: mean={roof_r.mean():.1f}")
print(f"  G: mean={roof_g.mean():.1f}")
print(f"  B: mean={roof_b.mean():.1f}")
print(f"  Brightness: mean={roof_bright.mean():.1f}")
print(f"  R - G: mean={(roof_r - roof_g).mean():.1f}")
