import os
import shutil
import numpy as np
from PIL import Image, ImageFilter

def load_and_crop_photo(photo_path, target_w=300, target_h=307):
    img = Image.open(photo_path)
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    
    alpha = arr[:, :, 3] / 255.0
    row_alpha = alpha.sum(axis=1)
    top_y = np.where(row_alpha > target_w * 0.1)[0][0]
    
    start_y = max(0, top_y - 25)
    orig_h, orig_w = arr.shape[:2]
    target_aspect = target_w / target_h
    desired_h = int(round(orig_w / target_aspect))
    
    if start_y + desired_h <= orig_h:
        cropped = img.crop((0, start_y, orig_w, start_y + desired_h))
    else:
        avail_h = orig_h - start_y
        desired_w = int(round(avail_h * target_aspect))
        left_x = (orig_w - desired_w) // 2
        cropped = img.crop((left_x, start_y, left_x + desired_w, orig_h))
        
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    res_arr = np.array(resized, dtype=np.float32)
    return res_arr

def test_light_variations():
    res_arr = load_and_crop_photo("my image.png", 300, 307)
    rgb = res_arr[:, :, :3] / 255.0
    alpha = res_arr[:, :, 3] / 255.0
    
    alpha_img = Image.fromarray((alpha * 255).astype(np.uint8))
    alpha_smooth = np.array(alpha_img.filter(ImageFilter.GaussianBlur(radius=0.5)), dtype=np.float32) / 255.0
    fg_mask = (alpha_smooth > 0.15).astype(np.float32)
    
    lum = 0.28 * rgb[:, :, 0] + 0.57 * rgb[:, :, 1] + 0.15 * rgb[:, :, 2]
    
    lum_img = Image.fromarray((np.clip(lum, 0, 1) * 255).astype(np.uint8))
    blur_large = np.array(lum_img.filter(ImageFilter.GaussianBlur(radius=10)), dtype=np.float32) / 255.0
    blur_med   = np.array(lum_img.filter(ImageFilter.GaussianBlur(radius=3)), dtype=np.float32) / 255.0
    blur_fine  = np.array(lum_img.filter(ImageFilter.GaussianBlur(radius=0.8)), dtype=np.float32) / 255.0
    
    detail_fine = lum - blur_fine
    detail_med  = lum - blur_med
    local_norm  = lum / (blur_large + 0.05)
    
    edge_detector = np.array(lum_img.filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
    edges = np.clip(edge_detector * 2.0, 0, 1) * fg_mask
    
    bayer_8x8 = np.array([
        [ 0, 32,  8, 40,  2, 34, 10, 42],
        [48, 16, 56, 24, 50, 18, 58, 26],
        [12, 44,  4, 36, 14, 46,  6, 38],
        [60, 28, 52, 20, 62, 30, 54, 22],
        [ 3, 35, 11, 43,  1, 33,  9, 41],
        [51, 19, 59, 27, 49, 17, 57, 25],
        [15, 47,  7, 39, 13, 45,  5, 37],
        [63, 31, 55, 23, 61, 29, 53, 21]
    ], dtype=np.float32) / 64.0
    
    h, w = lum.shape
    tiled_bayer = np.tile(bayer_8x8, (int(np.ceil(h / 8)), int(np.ceil(w / 8))))[:h, :w]
    
    # In light mode, we want dark ink (#7C3AED) on shadows and dark features!
    inv_lum = 1.0 - lum
    # -detail_med and -detail_fine are positive when features are darker than surroundings (eyes, eyebrows, beard, glasses)
    base_tone = inv_lum * 0.75 + (1.0 - local_norm) * 0.15 - detail_med * 1.8 - detail_fine * 1.4
    base_tone += edges * 0.45
    base_tone = np.clip(base_tone, 0, 1) * fg_mask
    
    artifacts_dir = "C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5"
    
    # Test densities with CORRECT binary search!
    for target_density in [0.16, 0.20, 0.24, 0.28, 0.35]:
        low, high = -1.0, 1.0
        for _ in range(25):
            mid = (low + high) / 2.0
            thresh = (tiled_bayer * 0.70 + 0.10) + mid
            binary = (base_tone > thresh).astype(np.uint8) * (fg_mask > 0.3).astype(np.uint8)
            binary = np.where(edges > 0.40, 1, binary) * (fg_mask > 0.3).astype(np.uint8)
            binary[0, :] = 1; binary[-1, :] = 1; binary[:, 0] = 1; binary[:, -1] = 1
            
            density = binary.mean()
            # If density is LESS than target, we need more dots -> lower threshold -> lower mid!
            if density < target_density:
                high = mid
            else:
                low = mid
                
        actual_density = binary.mean()
        print(f"Target Density: {target_density:.2f} -> Actual: {actual_density:.2%}")
        
        light_preview = np.full((h, w, 3), [248, 250, 252], dtype=np.uint8)
        light_preview[binary == 1] = [124, 58, 237]
        out_name = f"light_density_{int(target_density*100)}.png"
        Image.fromarray(light_preview).save(out_name)
        if os.path.exists(artifacts_dir):
            shutil.copyfile(out_name, os.path.join(artifacts_dir, out_name))
            
    print("All light mode variations saved and copied to artifacts!")

if __name__ == "__main__":
    test_light_variations()
