import numpy as np
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
r = rgb[:, :100, 0].astype(float)
g = rgb[:, :100, 1].astype(float)
b = rgb[:, :100, 2].astype(float)
bright = (r + g + b) / 3.0

print(f"Lake brightness < 50: {np.mean(bright < 50)*100:.2f}%")
print(f"Lake brightness < 55: {np.mean(bright < 55)*100:.2f}%")
print(f"Lake brightness < 60: {np.mean(bright < 60)*100:.2f}%")
print(f"Lake brightness 60-100: {np.mean((bright >= 60) & (bright <= 100))*100:.2f}%")
