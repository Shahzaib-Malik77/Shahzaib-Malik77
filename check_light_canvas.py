import re
import numpy as np
from PIL import Image

with open('arifhaxn-main/dark.svg', 'r', encoding='utf-8') as f:
    dark_lines = f.read().split('\n')
with open('arifhaxn-main/light.svg', 'r', encoding='utf-8') as f:
    light_lines = f.read().split('\n')

canvas_dark = np.zeros((350, 320), dtype=np.uint8)
canvas_light = np.zeros((350, 320), dtype=np.uint8)

for i in range(32, 94):
    for m in re.finditer(r'M(\d+)\s+(\d+)h(\d+)v1h-\3z', dark_lines[i]):
        x, y, w = int(m.group(1)), int(m.group(2)), int(m.group(3))
        canvas_dark[y, x:x+w] = 255

for i in range(32, min(len(light_lines), 110)):
    if '<g opacity="0">' in light_lines[i] and 'begin=' in light_lines[i] and not '<set' in light_lines[i]:
        for m in re.finditer(r'M(\d+)\s+(\d+)h(\d+)v1h-\3z', light_lines[i]):
            x, y, w = int(m.group(1)), int(m.group(2)), int(m.group(3))
            canvas_light[y, x:x+w] = 255

print(f"Dark white pixels: {np.sum(canvas_dark > 0)}, Light white pixels: {np.sum(canvas_light > 0)}")
diff = np.sum(canvas_dark != canvas_light)
print(f"Canvas difference between dark and light: {diff}")

# Let's save light portrait rendering as png in artifacts
out_light = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5/light_portrait_rendered.png"
Image.fromarray(canvas_light).save(out_light)

# Check exact line boundaries of light.svg
start_line = None
end_line = None
for i, line in enumerate(light_lines):
    if 'crispEdges' in line and start_line is None:
        start_line = i
    if start_line is not None and ('tvlight' in line or '<defs>' in line):
        end_line = i
        break

print(f"\nLight SVG portrait lines: {start_line+1} to {end_line}")
# Check how many fade-in groups vs animated groups exist in light.svg
fade_groups = 0
anim_groups = 0
for i in range(start_line, end_line):
    if '<animate attributeName="opacity" values="0;1"' in light_lines[i]:
        fade_groups += 1
    elif '<animateTransform attributeName="transform"' in light_lines[i] or ('<g opacity="1">' in light_lines[i] and not '<set' in light_lines[i]):
        anim_groups += 1

print(f"Light SVG -> Fade-in groups: {fade_groups}, Animated translate groups: {anim_groups}")

# Repeat for dark.svg
d_start, d_end = 31, 191
d_fade, d_anim = 0, 0
for i in range(d_start, d_end):
    if '<animate attributeName="opacity" values="0;1"' in dark_lines[i]:
        d_fade += 1
    elif '<animateTransform attributeName="transform"' in dark_lines[i] or ('<g opacity="1">' in dark_lines[i] and not '<set' in dark_lines[i]):
        d_anim += 1
print(f"Dark SVG -> Fade-in groups: {d_fade}, Animated translate groups: {d_anim}")
