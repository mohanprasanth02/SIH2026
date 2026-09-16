import numpy as np
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))

# Top highway: y 10..35, x 120..220
hwy = rgb[10:35, 120:220]
hr = hwy[:,:,0].astype(float)
hg = hwy[:,:,1].astype(float)
hb = hwy[:,:,2].astype(float)
h_rg = np.abs(hr - hg)
h_gb = np.abs(hg - hb)
h_bright = (hr + hg + hb) / 3.0
print("TOP HIGHWAY:")
print(f"  |R-G|: mean={h_rg.mean():.1f}, p90={np.percentile(h_rg, 90):.1f}")
print(f"  |G-B|: mean={h_gb.mean():.1f}, p90={np.percentile(h_gb, 90):.1f}")
print(f"  Brightness: mean={h_bright.mean():.1f}, p10={np.percentile(h_bright, 10):.1f}, p90={np.percentile(h_bright, 90):.1f}")

# Bottom right solar/facility: y 185..214, x 460..510
br = rgb[185:214, 460:510]
br_r = br[:,:,0].astype(float)
br_g = br[:,:,1].astype(float)
br_b = br[:,:,2].astype(float)
br_rg = np.abs(br_r - br_g)
br_bright = (br_r + br_g + br_b) / 3.0
print("\nBOTTOM RIGHT FACILITY:")
print(f"  |R-G|: mean={br_rg.mean():.1f}, p90={np.percentile(br_rg, 90):.1f}")
print(f"  Brightness: mean={br_bright.mean():.1f}")
print(f"  R: mean={br_r.mean():.1f}, G: mean={br_g.mean():.1f}, B: mean={br_b.mean():.1f}")
