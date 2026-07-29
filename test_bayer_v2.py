import numpy as np
from PIL import Image, ImageFilter
import sys

def get_bayer_matrix_8x8():
    b2 = np.array([[0, 2], [3, 1]])
    b4 = np.block([[4*b2 + 0, 4*b2 + 2], [4*b2 + 3, 4*b2 + 1]])
    b8 = np.block([[4*b4 + 0, 4*b4 + 2], [4*b4 + 3, 4*b4 + 1]])
    return (b8 + 0.5) / 64.0

def process_portrait_v2(photo_path, is_dark_mode=True):
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
        top = int((img_h - new_h) * 0.15)
        img = orig.crop((0, top, img_w, top + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    
    # 1. BACKGROUND SUPPRESSION
    # Notice the wall in the photo is relatively bright and flat, especially in upper left/right corners
    corner_samples = np.concatenate((arr[0:40, 0:40].flatten(), arr[0:40, -40:].flatten()))
    bg_val = np.median(corner_samples)
    
    # Compute similarity to background wall color
    bg_diff = np.abs(arr - bg_val)
    # Also compute local texture/edges (wall has low texture, hair/face/clothes have high texture)
    edges = np.array(img.filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
    blur_edges = np.array(Image.fromarray((edges*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=5)), dtype=np.float32) / 255.0
    
    # Create foreground mask (high where person is, 0 on wall)
    y_idx, x_idx = np.indices((target_h, target_w))
    center_dist = np.sqrt(((x_idx - target_w/2.0)/(target_w*0.55))**2 + ((y_idx - target_h*0.45)/(target_h*0.55))**2)
    
    # Foreground indicator: diff from wall color + local texture + spatial centering
    fg_score = (bg_diff * 3.0) + (blur_edges * 8.0) + np.maximum(0, 1.2 - center_dist)
    # Smooth out the foreground mask
    fg_mask = np.clip((fg_score - 0.5) * 1.5, 0.0, 1.0)
    fg_mask_img = Image.fromarray((fg_mask*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=8))
    fg_mask = np.array(fg_mask_img, dtype=np.float32) / 255.0

    # 2. ADAPTIVE DETAIL ENHANCEMENT (Keep full range 0.0 to 1.0!)
    blur_mid = np.array(img.filter(ImageFilter.GaussianBlur(radius=8)), dtype=np.float32) / 255.0
    sharp_detail = (arr - blur_mid) * 1.5
    
    # Combine original intensity with enhanced detail
    enhanced = np.clip(arr + sharp_detail, 0.0, 1.0)
    
    bayer = get_bayer_matrix_8x8()
    bayer_tiled = np.tile(bayer, (int(np.ceil(target_h/8)), int(np.ceil(target_w/8))))[:target_h, :target_w]
    
    if is_dark_mode:
        # In dark mode, person's highlights (face, nose, fingers) should shine brightly (high probability of dots)
        # Background should be suppressed to zero or super subtle threshold
        signal = enhanced * fg_mask
        
        # Boost face highlights so that cheeks and forehead have solid dot clusters just like original banner
        signal = np.clip(signal * 1.15, 0.0, 1.0)
        
        # For jacket (lower part of image, low brightness), retain enough edge outline
        jacket_mask = (y_idx > target_h * 0.65).astype(np.float32)
        signal = np.where((jacket_mask > 0) & (edges > 0.08), np.maximum(signal, 0.6), signal)
        
        # Use Bayer matrix thresholding without forced clipping or target count quotas!
        # Threshold curve: lower threshold for highlights to make them solid, Bayer matrix for midtones
        thresh = bayer_tiled * 0.75 + 0.12
        binary = (signal > thresh).astype(np.uint8)
        
        # Add the signature 1px boundary box around the portrait frame!
        binary[0:2, :] = 1
        binary[-2:, :] = 1
        binary[:, 0:2] = 1
        binary[:, -2:] = 1
        
    else:
        # In light mode, person's dark features (hair, beard, sunglasses, jacket, facial shadows) become purple dots
        inv_enhanced = 1.0 - enhanced
        signal = inv_enhanced * fg_mask
        
        # Boost darks (hair/beard) to be crisp and rich
        signal = np.clip(signal * 1.2, 0.0, 1.0)
        
        # In light mode, jacket at bottom should be heavily filled with texture
        thresh = bayer_tiled * 0.70 + 0.15
        binary = (signal > thresh).astype(np.uint8)
        
        # Boundary box
        binary[0:2, :] = 1
        binary[-2:, :] = 1
        binary[:, 0:2] = 1
        binary[:, -2:] = 1

    full = np.zeros((350, 320), dtype=np.uint8)
    full[32:32+target_h, 0:0+target_w] = binary
    return full

photo = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/media__1785335440634.jpg"
dark_res = process_portrait_v2(photo, is_dark_mode=True)
light_res = process_portrait_v2(photo, is_dark_mode=False)

# Render previews
dark_preview = np.full((350, 320, 3), [10, 16, 31], dtype=np.uint8)
dark_preview[dark_res == 1] = [167, 139, 250]
Image.fromarray(dark_preview).save(r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/preview_v2_dark.png")

light_preview = np.full((350, 320, 3), [248, 250, 252], dtype=np.uint8)
light_preview[light_res == 1] = [124, 58, 237]
Image.fromarray(light_preview).save(r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/preview_v2_light.png")

print(f"Dark V2 active dots: {np.sum(dark_res)}")
print(f"Light V2 active dots: {np.sum(light_res)}")
print("Saved preview_v2_dark.png and preview_v2_light.png.")
