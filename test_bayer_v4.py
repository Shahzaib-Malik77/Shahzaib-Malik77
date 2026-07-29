import numpy as np
from PIL import Image, ImageFilter
import sys

def get_bayer_matrix_8x8():
    b2 = np.array([[0, 2], [3, 1]])
    b4 = np.block([[4*b2 + 0, 4*b2 + 2], [4*b2 + 3, 4*b2 + 1]])
    b8 = np.block([[4*b4 + 0, 4*b4 + 2], [4*b4 + 3, 4*b4 + 1]])
    return (b8 + 0.5) / 64.0

def process_portrait_v4(photo_path, is_dark_mode=True):
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
    
    # 1. BOUNDARY FLOOD-FILL WALL SEGMENTATION (Zero Halo, Zero Boxes)
    # Wall is connected to top, left, right edges in upper half and has relatively smooth intensity (> 0.25)
    # We build a connectivity-based mask using iterative dilation from upper edges on non-dark, low-edge pixels
    edges = np.array(img.filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
    blur_edges = np.array(Image.fromarray((edges*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=3)), dtype=np.float32) / 255.0
    
    # Candidate wall pixels: not deep shadows (arr > 0.22), low local texture (blur_edges < 0.08)
    wall_candidates = (arr > 0.22) & (blur_edges < 0.08)
    
    # Initialize seed from top edge and upper sides
    wall_mask = np.zeros_like(wall_candidates, dtype=bool)
    wall_mask[0:15, :] = wall_candidates[0:15, :]
    wall_mask[0:200, 0:10] = wall_candidates[0:200, 0:10]
    wall_mask[0:200, -10:] = wall_candidates[0:200, -10:]
    
    # Iterative region growing from boundary seeds to envelope the wall without crossing hair/face boundaries
    # Simple NumPy morphology simulation using shifting
    for _ in range(40): # 40 iterations of neighborhood expansion
        up = np.roll(wall_mask, -1, axis=0)
        down = np.roll(wall_mask, 1, axis=0)
        left = np.roll(wall_mask, -1, axis=1)
        right = np.roll(wall_mask, 1, axis=1)
        neighbors = wall_mask | up | down | left | right
        new_mask = neighbors & wall_candidates
        if np.array_equal(new_mask, wall_mask):
            break
        wall_mask = new_mask
        
    # Any residual non-wall at the top corners that isn't hair/face gets swept into wall_mask
    y_idx, x_idx = np.indices((target_h, target_w))
    wall_mask = wall_mask | ((y_idx < 100) & (arr > 0.40) & (blur_edges < 0.05))
    
    fg_mask = 1.0 - wall_mask.astype(np.float32)
    # Tiny smooth at hair boundary to avoid jagged edges
    fg_mask = np.array(Image.fromarray((fg_mask*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=2)), dtype=np.float32) / 255.0

    # 2. ADAPTIVE LOCAL CONTRAST FOR MASTERPIECE DETAILED PORTRAIT
    blur_mid = np.array(img.filter(ImageFilter.GaussianBlur(radius=6)), dtype=np.float32) / 255.0
    sharp_detail = (arr - blur_mid) * 1.5
    enhanced = np.clip(arr + sharp_detail, 0.0, 1.0)
    
    bayer = get_bayer_matrix_8x8()
    bayer_tiled = np.tile(bayer, (int(np.ceil(target_h/8)), int(np.ceil(target_w/8))))[:target_h, :target_w]
    
    if is_dark_mode:
        signal = enhanced * fg_mask
        # Face highlights pop out cleanly
        signal = np.clip(signal * 1.15, 0.0, 1.0)
        
        # Lower jacket silhouette texture
        jacket_mask = (y_idx > target_h * 0.65).astype(np.float32)
        signal = np.where((jacket_mask > 0) & (edges > 0.06) & (fg_mask > 0.5), np.maximum(signal, 0.55), signal)
        
        thresh = bayer_tiled * 0.75 + 0.12
        binary = (signal > thresh).astype(np.uint8)
    else:
        inv_enhanced = 1.0 - enhanced
        signal = inv_enhanced * fg_mask
        signal = np.clip(signal * 1.2, 0.0, 1.0)
        
        thresh = bayer_tiled * 0.68 + 0.15
        binary = (signal > thresh).astype(np.uint8)
        
    binary[fg_mask < 0.2] = 0

    # Signature sharp 1px frame around the canvas
    binary[0:1, :] = 1
    binary[-1:, :] = 1
    binary[:, 0:1] = 1
    binary[:, -1:] = 1

    full = np.zeros((350, 320), dtype=np.uint8)
    full[32:32+target_h, 0:0+target_w] = binary
    return full

photo = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/media__1785335440634.jpg"
dark_res = process_portrait_v4(photo, is_dark_mode=True)
light_res = process_portrait_v4(photo, is_dark_mode=False)

dark_preview = np.full((350, 320, 3), [10, 16, 31], dtype=np.uint8)
dark_preview[dark_res == 1] = [167, 139, 250]
Image.fromarray(dark_preview).save(r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/preview_v4_dark.png")

light_preview = np.full((350, 320, 3), [248, 250, 252], dtype=np.uint8)
light_preview[light_res == 1] = [124, 58, 237]
Image.fromarray(light_preview).save(r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/preview_v4_light.png")

print("Saved preview_v4_dark.png and preview_v4_light.png.")
