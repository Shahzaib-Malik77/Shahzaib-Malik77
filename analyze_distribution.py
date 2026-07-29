import re
import numpy as np

with open('dist_out_utf8.txt', 'w', encoding='utf-8') as out:
    with open('arifhaxn-main/dark.svg', 'r', encoding='utf-8') as f:
        dark_lines = f.read().split('\n')
    with open('arifhaxn-main/light.svg', 'r', encoding='utf-8') as f:
        light_lines = f.read().split('\n')

    # Check if path data is identical between dark and light
    dark_paths = [re.search(r'<path d="([^"]*)"', l).group(1) for l in dark_lines[32:191] if '<path' in l and re.search(r'<path d="([^"]*)"', l)]
    light_paths = [re.search(r'<path d="([^"]*)"', l).group(1) for l in light_lines[32:193] if '<path' in l and re.search(r'<path d="([^"]*)"', l)]

    out.write(f"Dark path tags count: {len(dark_paths)}, Light path tags count: {len(light_paths)}\n")
    min_len = min(len(dark_paths), len(light_paths))
    matches = sum(1 for i in range(min_len) if dark_paths[i] == light_paths[i])
    out.write(f"Matching path strings between dark and light: {matches} / {min_len}\n")

    # Let's inspect the 60 initial groups in dark.svg (lines 33 to 93)
    out.write("\n--- Initial Fade-In Groups (Sample) ---\n")
    for idx in [33, 40, 50, 60, 92]:
        line = dark_lines[idx]
        coords = [int(m.group(2)) for m in re.finditer(r'M(\d+)\s+(\d+)', line)]
        if coords and 'begin=' in line:
            out.write(f"Line {idx+1} (begin {re.search(r'begin=\"([^\"]+)\"', line).group(1)}): Y range {min(coords)}..{max(coords)}, count {len(coords)}\n")

    # Let's inspect the 94 animated groups in dark.svg (lines 96 to 190)
    out.write("\n--- Second Animated Groups (Sample) ---\n")
    grid_boxes = []
    for idx in range(96, min(len(dark_lines), 191)):
        line = dark_lines[idx]
        if '<path d="' not in line:
            continue
        x_coords = [int(m.group(1)) for m in re.finditer(r'M(\d+)\s+(\d+)', line)]
        y_coords = [int(m.group(2)) for m in re.finditer(r'M(\d+)\s+(\d+)', line)]
        trans = re.search(r'values=\"([^\"]+)\"', line)
        trans_str = trans.group(1).split(';')[2] if (trans and ';' in trans.group(1)) else 'none'
        if x_coords:
            grid_boxes.append((min(x_coords), max(x_coords), min(y_coords), max(y_coords), trans_str, idx+1))

    for g in grid_boxes[:15]:
        out.write(f"Line {g[5]} (trans {g[4]:<8}): X({g[0]:3d}..{g[1]:3d}), Y({g[2]:3d}..{g[3]:3d})\n")

    canvas1 = np.zeros((350, 320), dtype=np.uint8)
    canvas2 = np.zeros((350, 320), dtype=np.uint8)

    for i in range(32, min(len(dark_lines), 94)):
        for m in re.finditer(r'M(\d+)\s+(\d+)h(\d+)v1h-\3z', dark_lines[i]):
            x, y, w = int(m.group(1)), int(m.group(2)), int(m.group(3))
            canvas1[y, x:x+w] = 1

    for i in range(95, min(len(dark_lines), 191)):
        for m in re.finditer(r'M(\d+)\s+(\d+)h(\d+)v1h-\3z', dark_lines[i]):
            x, y, w = int(m.group(1)), int(m.group(2)), int(m.group(3))
            canvas2[y, x:x+w] = 1

    diff = np.sum(canvas1 != canvas2)
    out.write(f"\nDifference in total pixels between fade-in set and animated set: {diff}\n")
    out.write(f"Set 1 total pixels: {np.sum(canvas1)}, Set 2 total pixels: {np.sum(canvas2)}\n")
