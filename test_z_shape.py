import numpy as np
from PIL import Image, ImageDraw
import shutil
import os

img = Image.new('L', (320, 350), 0)
draw = ImageDraw.Draw(img)

# Let's refine the Z polygon for perfect visual harmony and balance
# Centered at (150, 175)
# Let's try width=170 (X: 65 to 235), height=170 (Y: 90 to 260)
# Bar thickness: 34 pixels
z_polygon = [
    (65, 90),
    (235, 90),
    (235, 124),
    (107, 226),
    (235, 226),
    (235, 260),
    (65, 260),
    (65, 226),
    (193, 124),
    (65, 124)
]
draw.polygon(z_polygon, fill=255)
mask = np.array(img)

# Find float step that yields exactly 900 unique coordinates
best_pts = None
for step in np.linspace(3.8, 5.2, 5000):
    pts = set()
    y_vals = np.arange(90, 261, step)
    x_vals = np.arange(65, 236, step)
    for y in y_vals:
        for x in x_vals:
            ix, iy = int(round(x)), int(round(y))
            if 0 <= iy < 350 and 0 <= ix < 320 and mask[iy, ix] > 0:
                pts.add((ix, iy))
    if len(pts) == 900:
        best_pts = sorted(list(pts), key=lambda p: (p[1], p[0]))
        print(f"FOUND EXACTLY 900 POINTS with step={step:.5f}!")
        break

if not best_pts:
    # If not exactly 900, let's take the closest step and adjust by trimming or padding from border
    counts = []
    for step in np.linspace(4.0, 4.6, 200):
        pts = set()
        y_vals = np.arange(90, 261, step)
        x_vals = np.arange(65, 236, step)
        for y in y_vals:
            for x in x_vals:
                ix, iy = int(round(x)), int(round(y))
                if 0 <= iy < 350 and 0 <= ix < 320 and mask[iy, ix] > 0:
                    pts.add((ix, iy))
        counts.append((abs(len(pts)-900), len(pts), step, sorted(list(pts), key=lambda p: (p[1], p[0]))))
    counts.sort(key=lambda item: item[0])
    diff, total, best_step, best_pts = counts[0]
    print(f"Closest match: {total} points at step={best_step:.5f} (diff: {diff})")
    
    # If total > 900, take 900 evenly spaced from the list
    if len(best_pts) > 900:
        idx_to_keep = np.linspace(0, len(best_pts) - 1, 900).astype(int)
        best_pts = [best_pts[i] for i in idx_to_keep]
    elif len(best_pts) < 900:
        # Pad by repeating a few central points or adding neighbor pixels
        y_idx, x_idx = np.where(mask > 0)
        all_mask_pts = set(zip(x_idx, y_idx)) - set(best_pts)
        extra_needed = 900 - len(best_pts)
        best_pts.extend(list(all_mask_pts)[:extra_needed])
        best_pts = sorted(best_pts, key=lambda p: (p[1], p[0]))

print(f"Final best_pts count: {len(best_pts)}")

# Render preview of Z dots to check aesthetics
preview = np.full((350, 320, 3), [10, 16, 31], dtype=np.uint8)
for x, y in best_pts:
    # draw dots in bright purple/cyan gradient or solid lavender #A78BFA
    preview[max(0, y-1):min(350, y+2), max(0, x-1):min(320, x+2)] = [167, 139, 250]

Image.fromarray(preview).save("z_logo_preview.png")

artifacts_dir = "C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5"
if os.path.exists(artifacts_dir):
    shutil.copyfile("z_logo_preview.png", os.path.join(artifacts_dir, "z_logo_preview.png"))
    print("Saved z_logo_preview.png to artifacts!")
