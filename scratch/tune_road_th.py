import numpy as np
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

# Test different |R - G| thresholds for roads
for th in [8, 10, 12, 14, 16]:
    road_cand = (saturation < 0.32) & (chroma < 40) & (np.abs(r - g) <= th) & (np.abs(g - b) <= 36) & (brightness >= 45) & (brightness < 160) & (gli < 0.10)
    
    # Bund road center coverage
    bund_cov = np.mean(road_cand[50:180, 111]) * 100
    
    # Top highway coverage
    hwy_cov = np.mean(road_cand[20:30, 150:200]) * 100
    
    # Residential roof false positive rate
    roof_fp = np.mean(road_cand[140:180, 380:450]) * 100
    
    total_pct = np.mean(road_cand) * 100
    print(f"Threshold |R-G| <= {th}: Bund={bund_cov:.1f}%, Hwy={hwy_cov:.1f}%, Roof FP={roof_fp:.1f}%, Total Image={total_pct:.1f}%")
