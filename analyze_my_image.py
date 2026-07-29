import numpy as np
from PIL import Image

img = Image.open("my image.png")
print(f"Image size: {img.size}, mode: {img.mode}")
arr = np.array(img)

if img.mode == 'RGBA':
    alpha = arr[:, :, 3]
    print(f"Alpha channel range: [{alpha.min()}, {alpha.max()}], percentage > 0: {(alpha > 0).mean():.2%}")
    print(f"Percentage == 255 (fully opaque): {(alpha == 255).mean():.2%}")
    
# Let's inspect RGB distribution
rgb = arr[:, :, :3]
lum = 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]
print(f"Luminance range: [{lum.min():.1f}, {lum.max():.1f}], mean: {lum.mean():.1f}")
print(f"Luminance percentiles (10, 25, 50, 75, 90): {np.percentile(lum, [10, 25, 50, 75, 90])}")

# Let's check borders to see if background is dark or uniform
top = lum[0:50, :]
bottom = lum[-50:, :]
left = lum[:, 0:50]
right = lum[:, -50:]
print(f"Border mean luminance -> Top: {top.mean():.1f}, Bottom: {bottom.mean():.1f}, Left: {left.mean():.1f}, Right: {right.mean():.1f}")
