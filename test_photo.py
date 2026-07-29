import os
from PIL import Image
import numpy as np

img_path = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/media__1785335440634.jpg"
print(f"Image exists: {os.path.exists(img_path)}")
if os.path.exists(img_path):
    with Image.open(img_path) as img:
        print(f"Original image size: {img.size}, mode: {img.mode}")
        # Resize to 300x307 (or similar aspect ratio) to check
        # Let's inspect brightness distribution
        gray = img.convert('L')
        arr = np.array(gray)
        print(f"Min intensity: {arr.min()}, Max intensity: {arr.max()}, Mean: {arr.mean():.2f}")

# Compare dark.svg and light.svg group count and timing exactly
def get_structure(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    
    start_line = None
    end_line = None
    for i, line in enumerate(lines):
        if 'crispEdges' in line and start_line is None:
            start_line = i
        elif start_line is not None and ('tvdark' in line or 'tvlight' in line or '<defs><rect' in line):
            end_line = i
            break
            
    print(f"\n--- {filepath} ---")
    print(f"Portrait section from line {start_line+1} to {end_line}")
    
    # Extract all non-path tags inside this section to see exact structure
    tags_structure = []
    for i in range(start_line, end_line):
        line = lines[i]
        # remove path d="..." to just see structure
        import re
        clean_line = re.sub(r'<path d="[^"]*"/>', '<PATH_HERE/>', line)
        tags_structure.append((i+1, clean_line))
    
    return tags_structure, lines[start_line:end_line]

dark_struct, dark_lines = get_structure('arifhaxn-main/dark.svg')
light_struct, light_lines = get_structure('arifhaxn-main/light.svg')

print(f"Dark lines count: {len(dark_struct)}, Light lines count: {len(light_struct)}")

# Check if the structure (ignoring color and path coordinates) is identical
diffs = 0
for i in range(min(len(dark_struct), len(light_struct))):
    d_line = dark_struct[i][1].replace('#A78BFA', '#COLOR#').replace('tvdark', 'tvcolor')
    l_line = light_struct[i][1].replace('#7C3AED', '#COLOR#').replace('tvlight', 'tvcolor')
    if d_line != l_line:
        print(f"Mismatch at line idx {i}:")
        print(f"  Dark ({dark_struct[i][0]}):  {d_line[:100]}")
        print(f"  Light ({light_struct[i][0]}): {l_line[:100]}")
        diffs += 1
        if diffs > 5:
            break

if diffs == 0:
    print("Structures (animations, timing, groups) are 100% IDENTICAL between dark and light!")
else:
    print(f"Total structure differences found: {diffs}")
