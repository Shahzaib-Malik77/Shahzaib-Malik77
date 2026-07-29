"""Analyze the dark.svg portrait structure to understand pixel art parameters."""
import re

with open('arifhaxn-main/dark.svg', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print(f'Total lines: {len(lines)}')

# Find the portrait panel container (line 32)
print(f'\nLine 32 (first 300 chars): {lines[31][:300]}')
print(f'\nLine 94 (closing tag): {lines[93][:200]}')
print(f'\nLine 95 (second group): {lines[94][:300]}')
print(f'\nLine 96 (set tag): {lines[95][:200]}')

# Count initial pixel groups (lines 33-93)
initial_groups = 0
begin_times = []
for i in range(32, 93):
    if '<g opacity="0">' in lines[i]:
        initial_groups += 1
        match = re.search(r'begin="([\d.]+)s"', lines[i])
        if match:
            begin_times.append(float(match.group(1)))

print(f'\nInitial pixel groups (fade-in): {initial_groups}')
if begin_times:
    print(f'Begin times range: {min(begin_times):.2f}s to {max(begin_times):.2f}s')
    print(f'Step between times: {(begin_times[1]-begin_times[0]):.4f}s')

# Count animated groups (line 97+)
animated_groups = 0
translate_values = []
for i in range(96, len(lines)):
    if '<g opacity="1">' in lines[i]:
        animated_groups += 1
        tmatch = re.search(r'type="translate" values="([^"]+)"', lines[i])
        if tmatch:
            translate_values.append(tmatch.group(1)[:50])

print(f'\nAnimated groups (post 3.2s): {animated_groups}')
if translate_values:
    print(f'Sample translate values: {translate_values[:3]}')

# Extract the transform on the parent group
transform_match = re.search(r'transform="([^"]+)"', lines[31])
if transform_match:
    print(f'\nParent transform: {transform_match.group(1)}')

# Count total pixels in first group
first_path = re.search(r'<path d="([^"]+)"', lines[33])
if first_path:
    path_data = first_path.group(1)
    pixel_count = path_data.count('M')
    print(f'\nFirst group pixel count: {pixel_count}')

# Count total pixels across ALL initial groups
total_pixels = 0
for i in range(32, 93):
    for match in re.finditer(r'<path d="([^"]+)"', lines[i]):
        total_pixels += match.group(1).count('M')
print(f'Total pixels in initial display: {total_pixels}')

# Count total pixels in animated groups
total_animated_pixels = 0
for i in range(96, len(lines)):
    for match in re.finditer(r'<path d="([^"]+)"', lines[i]):
        total_animated_pixels += match.group(1).count('M')
print(f'Total pixels in animated display: {total_animated_pixels}')

# Get the grid dimensions from path data
# Parse all M coordinates to find the bounding box
all_x = []
all_y = []
for i in range(32, 93):
    for match in re.finditer(r'M(\d+) (\d+)', lines[i]):
        all_x.append(int(match.group(1)))
        all_y.append(int(match.group(2)))
        
print(f'\nPixel art bounding box:')
print(f'  X range: {min(all_x)} to {max(all_x)}')
print(f'  Y range: {min(all_y)} to {max(all_y)}')
print(f'  Width: {max(all_x) - min(all_x) + 1}')
print(f'  Height: {max(all_y) - min(all_y) + 1}')

# Find where the second group ends and the rest of the SVG continues
for i in range(len(lines)-1, 0, -1):
    if '</g>' in lines[i] and i > 95:
        # Check if this closes the second portrait group
        pass
    if 'VISUAL.MAP' in lines[i] or 'STATS' in lines[i] or 'INFO' in lines[i]:
        print(f'\nFound section marker at line {i+1}: {lines[i][:100]}')

# Find end of portrait section
for i in range(95, min(len(lines), 200)):
    stripped = lines[i].strip()
    if stripped == '</g>' and i > 95:
        # Check what follows
        if i+1 < len(lines) and not lines[i+1].strip().startswith('<g'):
            print(f'\nPossible portrait end at line {i+1}: {lines[i][:50]}')
            if i+1 < len(lines):
                print(f'  Next line {i+2}: {lines[i+1][:100]}')
            break

# Let's look at the end of the portrait pixel art more carefully
# The second pixel group starts at line 95 with opacity="0" initially, set to 1 at 3.2s
# Let's find where it closes
depth = 0
for i in range(94, min(len(lines), 500)):
    opens = lines[i].count('<g ')
    closes = lines[i].count('</g>')
    depth += opens - closes
    if depth <= 0 and i > 94:
        print(f'\nSecond portrait group closes at line {i+1}')
        if i+1 < len(lines):
            print(f'  Next line: {lines[i+1][:150]}')
        break
