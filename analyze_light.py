"""Analyze light.svg portrait structure."""
import re

with open('arifhaxn-main/light.svg', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print(f'Total lines: {len(lines)}')

# Find the portrait group
for i, line in enumerate(lines):
    if 'crispEdges' in line:
        print(f'Line {i+1}: {line[:300]}')
    if i > 0 and '</g>' == line.strip() and i > 30:
        # Check what follows
        if i+1 < len(lines) and ('tvlight' in lines[i+1] or 'tvdark' in lines[i+1] or '<defs>' in lines[i+1]):
            print(f'\nPortrait end at line {i+1}: {line[:50]}')
            print(f'  Next: {lines[i+1][:150]}')
            break

# Find portrait pixel bounding box
all_x = []
all_y = []
initial_groups = 0
for i, line in enumerate(lines):
    if 'crispEdges' in line:
        start_line = i
        break

for i in range(start_line, len(lines)):
    if '<g opacity="0">' in lines[i]:
        initial_groups += 1
    for match in re.finditer(r'M(\d+) (\d+)', lines[i]):
        all_x.append(int(match.group(1)))
        all_y.append(int(match.group(2)))
    if '</g>' == lines[i].strip() and i > start_line + 10:
        if i+1 < len(lines) and '<g transform' in lines[i+1] and 'crispEdges' in lines[i+1]:
            first_group_end = i + 1
            print(f'\nFirst portrait group: lines {start_line+1} to {first_group_end}')
            break

# Find fill color
fill_match = re.search(r'fill="(#[0-9A-Fa-f]+)"', lines[start_line])
if fill_match:
    print(f'Fill color: {fill_match.group(1)}')

# Find transform
transform_match = re.search(r'transform="([^"]+)"', lines[start_line])
if transform_match:
    print(f'Transform: {transform_match.group(1)}')

# Count groups
begin_times = []
for i in range(start_line, len(lines)):
    if '<g opacity="0">' in lines[i]:
        match = re.search(r'begin="([\d.]+)s"', lines[i])
        if match:
            begin_times.append(float(match.group(1)))

print(f'Initial groups with begin times: {len(begin_times)}')
if begin_times:
    print(f'Begin range: {min(begin_times):.2f}s to {max(begin_times):.2f}s')

# Find where second group starts/ends
second_start = None
for i in range(start_line+1, len(lines)):
    if 'crispEdges' in lines[i] and 'opacity="0"' in lines[i]:
        second_start = i
        print(f'\nSecond portrait group starts at line {i+1}: {lines[i][:200]}')
        break

if second_start:
    # Find end
    depth = 0
    for i in range(second_start, len(lines)):
        depth += lines[i].count('<g ') - lines[i].count('</g>')
        if depth <= 0 and i > second_start:
            print(f'Second portrait group ends at line {i+1}')
            if i+1 < len(lines):
                print(f'  Next: {lines[i+1][:150]}')
            break

# Bounding box
if all_x:
    print(f'\nBounding box: X({min(all_x)}-{max(all_x)}), Y({min(all_y)}-{max(all_y)})')
    print(f'Width: {max(all_x)-min(all_x)+1}, Height: {max(all_y)-min(all_y)+1}')
