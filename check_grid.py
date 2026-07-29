import re
import numpy as np

# Let's inspect how Set 2 (animated groups) partitions the canvas in dark.svg and light.svg
def analyze_set2_partition(filepath, start_idx, end_idx):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    
    # We want to see if each pixel position (x, y) belongs to exactly ONE group in Set 2
    # And what the spatial boundaries of each group are!
    boxes = []
    for g_idx, i in enumerate(range(start_idx, end_idx)):
        line = lines[i]
        if '<path d="' not in line:
            continue
        x_coords = []
        y_coords = []
        for m in re.finditer(r'M(\d+)\s+(\d+)h(\d+)v1h-\3z', line):
            x, y, w = int(m.group(1)), int(m.group(2)), int(m.group(3))
            for dx in range(w):
                x_coords.append(x + dx)
                y_coords.append(y)
        if x_coords:
            boxes.append((min(x_coords), max(x_coords), min(y_coords), max(y_coords), i+1))
            
    print(f"\n--- {filepath} ---")
    print(f"Total active animated groups: {len(boxes)}")
    # Let's check if they form a regular grid
    # Let's check how many distinct X ranges or Y ranges there are
    x_mins = sorted(list(set(b[0] for b in boxes)))
    print(f"X mins count: {len(x_mins)}, Sample X mins: {x_mins[:10]}")
    y_mins = sorted(list(set(b[2] for b in boxes)))
    print(f"Y mins count: {len(y_mins)}, Sample Y mins: {y_mins[:10]}")

    # Why not check if the groups are simply organized by X chunks or Y chunks, or let's print all 94 boxes!
    for idx, b in enumerate(boxes[:20]):
        print(f"Group {idx+1:2d} (line {b[4]:3d}): X=[{b[0]:3d}..{b[1]:3d}], Y=[{b[2]:3d}..{b[3]:3d}], W={b[1]-b[0]+1:2d}, H={b[3]-b[2]+1:2d}")

analyze_set2_partition('arifhaxn-main/dark.svg', 94, 191)
analyze_set2_partition('arifhaxn-main/light.svg', 94, 193)
