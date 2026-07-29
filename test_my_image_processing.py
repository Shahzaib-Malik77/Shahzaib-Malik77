import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps

def test_inspect_and_crop():
    print("Loading 'my image.png'...")
    img = Image.open("my image.png")
    arr = np.array(img)
    
    h, w = arr.shape[:2]
    print(f"Original image shape: {arr.shape}")
    
    # Check alpha channel if present
    if arr.shape[2] == 4:
        alpha = arr[:, :, 3]
        fg_mask_alpha = (alpha > 20).astype(np.float32)
        print(f"Alpha channel > 20 ratio: {fg_mask_alpha.mean():.2%}")
    else:
        alpha = np.ones((h, w), dtype=np.uint8) * 255
        fg_mask_alpha = np.ones((h, w), dtype=np.float32)
        
    # Analyze background colors in non-transparent regions near borders
    rgb = arr[:, :, :3]
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    
    # Check if there is a colored or dark background behind the person where alpha > 0
    # Let's check top border rows where alpha > 20
    top_fg = lum[0:100, :][alpha[0:100, :] > 20]
    if len(top_fg) > 0:
        print(f"Top border luminance where alpha>20: min={top_fg.min():.1f}, mean={top_fg.mean():.1f}, max={top_fg.max():.1f}")
    else:
        print("Top border has no alpha>20 pixels (completely clean top background!)")
        
    # Find exact bounding box of foreground (where alpha > 20 and/or luminance is distinct)
    # Let's see rows and columns where alpha > 20
    rows = np.where(alpha.sum(axis=1) > 255 * 10)[0]
    cols = np.where(alpha.sum(axis=0) > 255 * 10)[0]
    
    min_y, max_y = (rows[0], rows[-1]) if len(rows) > 0 else (0, h-1)
    min_x, max_x = (cols[0], cols[-1]) if len(cols) > 0 else (0, w-1)
    
    print(f"Foreground bounding box (Y: {min_y} to {max_y}, X: {min_x} to {max_x})")
    print(f"Foreground box dimensions: height={max_y - min_y}, width={max_x - min_x}, aspect={ (max_x - min_x) / (max_y - min_y):.3f}")
    
    # Check corner pixel colors to see if there is any solid background that needs removal
    corners_rgb = [rgb[0, 0], rgb[0, -1], rgb[-1, 0], rgb[-1, -1]]
    print("Corner RGB values:", corners_rgb)

if __name__ == "__main__":
    test_inspect_and_crop()
