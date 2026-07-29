import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import sys

# Generate 8x8 Bayer matrix for digital halftone dithering
def get_bayer_matrix_8x8():
    b2 = np.array([[0, 2], [3, 1]])
    b4 = np.block([[4*b2 + 0, 4*b2 + 2], [4*b2 + 3, 4*b2 + 1]])
    b8 = np.block([[4*b4 + 0, 4*b4 + 2], [4*b4 + 3, 4*b4 + 1]])
    return (b8 + 0.5) / 64.0

def process_image_advanced(photo_path, is_dark_mode=True):
    # Load photo and prepare crop/resize to target 300x310 canvas
    orig = Image.open(photo_path).convert('L')
    target_w, target_h = 300, 310
    
    img_w, img_h = orig.size
    aspect_target = target_w / target_h
    aspect_img = img_w / img_h
    
    if aspect_img > aspect_target:
        new_w = int(img_h * aspect_target)
        left = (img_w - new_w) // 2
        img = orig.crop((left, 0, left + new_w, img_h))
    else:
        new_h = int(img_w / aspect_target)
        top = int((img_h - new_h) * 0.15) # favor top/face area
        img = orig.crop((0, top, img_w, top + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    
    # 1. ADAPTIVE LOCAL CONTRAST (Multi-scale Unsharp & Shadow Normalization)
    # Subtract low-frequency blur to balance shadows across face and background
    blur1 = np.array(img.filter(ImageFilter.GaussianBlur(radius=15)), dtype=np.float32) / 255.0
    blur2 = np.array(img.filter(ImageFilter.GaussianBlur(radius=3)), dtype=np.float32) / 255.0
    
    # Local frequency band: middle detail + sharp detail
    # We combine normalized global intensity (to preserve overall lighting) with local contrast
    local_detail = arr - blur1
    fine_detail = arr - blur2
    
    # High-pass edge map (facial features: eyes, lips, hair lines, beard contour)
    edges = np.array(img.filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
    edges = np.clip(edges * 3.0, 0, 1) # amplify edges
    
    # 2. CREATE SYNTHETIC DIGITAL NOISE VIGNETTE FOR BACKGROUND & BORDER
    # In original dark mode, there is a distinct textured background inside a rectangular box
    y_idx, x_idx = np.indices((target_h, target_w))
    center_x, center_y = target_w / 2.0, target_h * 0.45
    radius = np.sqrt((x_idx - center_x)**2 + ((y_idx - center_y)*0.8)**2)
    norm_radius = np.clip(radius / 150.0, 0, 1)
    
    # 3. TONE MAPPING & DENSITY TARGETING FOR DARK vs LIGHT THEMES
    bayer = get_bayer_matrix_8x8()
    bayer_tiled = np.tile(bayer, (int(np.ceil(target_h/8)), int(np.ceil(target_w/8))))[:target_h, :target_w]
    
    if is_dark_mode:
        # In dark mode: highlights on skin/face become purple dots, dark jacket & background stay sparse
        # We modulate brightness so face (low norm_radius) stands out, while jacket/background gets sparse halftone texture
        base_tone = arr * 0.6 + (local_detail * 1.2) + (fine_detail * 0.8) + (edges * 0.5)
        
        # Suppress solid white saturation: force even bright skin to have halftone gaps (never > 0.92)
        base_tone = np.clip(base_tone, 0.05, 0.90)
        
        # Add a subtle radial digital background pattern in outer area
        bg_texture = 0.18 * (1.0 - norm_radius) + 0.10 * np.sin(x_idx*0.5)*np.cos(y_idx*0.5)
        tone_map = np.where(arr < 0.2, np.maximum(base_tone, bg_texture * 0.5), base_tone)
        
        # We want exact target density ~17,087 pixels out of 93,000 (approx 18% of target window)
        # Let's calibrate a shift delta so that sum(tone_map > (bayer_tiled + delta)) == 17,087
        target_count = 17087
        
        # Optimize threshold shift to match exact pixel density
        delta_min, delta_max = -1.0, 1.0
        for _ in range(25):
            mid = (delta_min + delta_max) / 2.0
            # For edge preservation: strong edges bypass bayer threshold slightly
            threshold_grid = bayer_tiled + mid - (edges * 0.25)
            count = np.sum(tone_map > threshold_grid)
            if count > target_count:
                delta_min = mid # need higher threshold to reduce dots
            else:
                delta_max = mid
                
        threshold_grid = bayer_tiled + delta_max - (edges * 0.25)
        binary = (tone_map > threshold_grid).astype(np.uint8)
        
    else:
        # In light mode: shadows/dark areas (hair, beard, sunglasses/eyes, clothing contour) become purple dots
        # Invert tone so dark colors become active high-intensity signals
        inv_arr = 1.0 - arr
        base_tone = inv_arr * 0.7 + (inv_arr - (1.0 - blur1))*1.2 + (inv_arr - (1.0 - blur2))*0.8 + (edges * 0.6)
        base_tone = np.clip(base_tone, 0.05, 0.92)
        
        # Light mode original has ~39,324 active pixels (approx 42% density on 300x310 canvas)
        target_count = 39324
        delta_min, delta_max = -1.0, 1.0
        for _ in range(25):
            mid = (delta_min + delta_max) / 2.0
            threshold_grid = bayer_tiled + mid - (edges * 0.25)
            count = np.sum(base_tone > threshold_grid)
            if count > target_count:
                delta_min = mid
            else:
                delta_max = mid
                
        threshold_grid = bayer_tiled + delta_max - (edges * 0.25)
        binary = (base_tone > threshold_grid).astype(np.uint8)
        
    # Full canvas placement (350x320)
    full = np.zeros((350, 320), dtype=np.uint8)
    full[32:32+target_h, 0:0+target_w] = binary
    
    return full

def print_stats(canvas, label):
    total = np.sum(canvas)
    runs = []
    for y in range(350):
        row = canvas[y]
        diff = np.diff(np.concatenate(([0], row, [0])))
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        runs.extend(ends - starts)
    runs = np.array(runs)
    single_pct = np.sum(runs==1)/len(runs) if len(runs) > 0 else 0
    print(f"[{label}] Active pixels: {total}, Total runs: {len(runs)}, Single-pixel runs: {single_pct:.2%}, Mean run: {np.mean(runs):.2f}")

photo = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/media__1785335440634.jpg"

dark_res = process_image_advanced(photo, is_dark_mode=True)
light_res = process_image_advanced(photo, is_dark_mode=False)

print_stats(dark_res, "New Dark Bayer-Adaptive")
print_stats(light_res, "New Light Bayer-Adaptive")

# Save high-contrast colored verification previews (Purple on Dark / Purple on Light) exactly like screenshots!
dark_preview = np.full((350, 320, 3), [10, 16, 31], dtype=np.uint8) # #0A101F background
dark_preview[dark_res == 1] = [167, 139, 250] # #A78BFA purple dot
Image.fromarray(dark_preview).save(r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/bayer_preview_dark.png")

light_preview = np.full((350, 320, 3), [248, 250, 252], dtype=np.uint8) # #F8FAFC background
light_preview[light_res == 1] = [124, 58, 237] # #7C3AED purple dot
Image.fromarray(light_preview).save(r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/bayer_preview_light.png")

print("Saved bayer_preview_dark.png and bayer_preview_light.png to artifacts directory.")
