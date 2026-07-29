import re
from PIL import Image
import numpy as np

# 1. Reconstruct original portrait from dark.svg to understand the visual style
with open('arifhaxn-main/dark.svg', 'r', encoding='utf-8') as f:
    dark_svg = f.read()

lines = dark_svg.split('\n')
# Get all M coordinates in initial group (lines 32 to 93)
orig_canvas = np.zeros((350, 320), dtype=np.uint8)

# In SVG path d="M133 40h1v1h-1zM200 64h2v1h-2z..."
# Notice some runs have width > 1! e.g., h2, h13, h29!
for i in range(32, 93):
    path_match = re.search(r'<path d="([^"]+)"', lines[i])
    if not path_match:
        continue
    d = path_match.group(1)
    # Parse commands like M133 40h1v1h-1z or M108 98h13v1h-13z
    matches = re.finditer(r'M(\d+)\s+(\d+)h(\d+)v1h-\3z', d)
    for m in matches:
        x, y, w = int(m.group(1)), int(m.group(2)), int(m.group(3))
        orig_canvas[y, x:x+w] = 255

print("Original portrait canvas stats:")
print(f"Total white pixels drawn: {np.sum(orig_canvas > 0)}")

# Save original portrait rendering as png in artifacts directory so we can inspect it if needed
out_orig = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/orig_portrait_rendered.png"
Image.fromarray(orig_canvas).save(out_orig)
print(f"Saved original portrait render to {out_orig}")

# Let's inspect the distribution of pixels in orig_canvas by rows and columns
y_indices, x_indices = np.where(orig_canvas > 0)
print(f"Y min: {y_indices.min()}, Y max: {y_indices.max()}")
print(f"X min: {x_indices.min()}, X max: {x_indices.max()}")
print(f"Aspect ratio of drawn area: {(x_indices.max()-x_indices.min()) / (y_indices.max()-y_indices.min()):.2f}")

# Now let's analyze how we should process the user's uploaded image
user_img_path = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/media__1785335440634.jpg"
with Image.open(user_img_path) as uimg:
    # Resize to fit within 300 x 307 while maintaining aspect ratio or crop-to-fit
    target_w, target_h = 300, 307
    
    # Check current aspect
    uw, uh = uimg.size
    print(f"User image aspect: {uw/uh:.2f}, Target aspect: {target_w/target_h:.2f}")
    
    # Let's do a center crop to match target aspect ratio exactly
    target_aspect = target_w / target_h
    current_aspect = uw / uh
    if current_aspect > target_aspect:
        # Too wide, crop width
        new_w = int(uh * target_aspect)
        left = (uw - new_w) // 2
        cropped = uimg.crop((left, 0, left + new_w, uh))
    else:
        # Too tall, crop height
        new_h = int(uw / target_aspect)
        top = (uh - new_h) // 2
        cropped = uimg.crop((0, top, uw, top + new_h))
        
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    gray = resized.convert('L')
    
    # Save a few variations of binary conversion:
    # 1. Simple Otsu/mean thresholding
    # 2. Dithering (Floyd-Steinberg - default Pillow '1' mode)
    # 3. High-contrast thresholding + edge blending
    
    # Dithered version
    dithered = gray.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    out_dither = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/user_dithered.png"
    dithered.save(out_dither)
    d_arr = np.array(dithered)
    print(f"Dithered white pixel count: {np.sum(d_arr > 0)}")
    
    # Thresholded version (let's check different thresholds to see which gives ~10k-15k white pixels or best contrast)
    g_arr = np.array(gray)
    for thresh in [100, 128, 150, 170, 180]:
        t_arr = (g_arr > thresh).astype(np.uint8) * 255
        print(f"Threshold {thresh} white pixels: {np.sum(t_arr > 0)}")
        
    # Let's also check edge detection + dithering
    from PIL import ImageFilter
    edges = gray.filter(ImageFilter.FIND_EDGES)
    out_edges = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/user_edges.png"
    edges.save(out_edges)
