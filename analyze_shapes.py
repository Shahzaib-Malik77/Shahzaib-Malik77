import xml.etree.ElementTree as ET
import numpy as np

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

with open("arifhaxn-main/dark.svg", "r", encoding="utf-8") as f:
    content = f.read()

tree = ET.ElementTree(ET.fromstring(content))
root = tree.getroot()

# Find the winClip group and Child #14 (with 900 subchildren)
c3 = None
for elem in root.iter():
    if strip_ns(elem.tag) == 'g' and 'translate(50,86)' in elem.attrib.get('transform', ''):
        children = list(elem)
        if len(children) >= 800: # This is the dot container
            # Check if children are <use>
            if any(strip_ns(c.tag) == 'use' for c in children[:10]):
                c3 = elem
                break

if not c3:
    print("Could not find dot container!")
    exit()

print(f"Found dot container with {len(list(c3))} dots!")

flutter_coords = []
slash_coords = []
triangle_coords = []

for dot in c3:
    for sc in dot:
        if strip_ns(sc.tag) == 'animateTransform':
            vals = sc.attrib.get('values', '').split(';')
            if len(vals) == 9:
                # val2 is Flutter logo
                fx, fy = map(float, vals[2].split())
                flutter_coords.append((fx, fy))
                
                # val4 is < / >
                sx, sy = map(float, vals[4].split())
                slash_coords.append((sx, sy))
                
                # val6 is Triangle
                tx, ty = map(float, vals[6].split())
                triangle_coords.append((tx, ty))

flutter_coords = np.array(flutter_coords)
slash_coords = np.array(slash_coords)
triangle_coords = np.array(triangle_coords)

print("\n--- Flutter Logo Bounding Box ---")
print(f"X: {flutter_coords[:,0].min()} to {flutter_coords[:,0].max()} (Width: {flutter_coords[:,0].max() - flutter_coords[:,0].min()})")
print(f"Y: {flutter_coords[:,1].min()} to {flutter_coords[:,1].max()} (Height: {flutter_coords[:,1].max() - flutter_coords[:,1].min()})")
print(f"Center: ({flutter_coords[:,0].mean():.1f}, {flutter_coords[:,1].mean():.1f})")

print("\n--- < / > Symbol Bounding Box ---")
print(f"X: {slash_coords[:,0].min()} to {slash_coords[:,0].max()} (Width: {slash_coords[:,0].max() - slash_coords[:,0].min()})")
print(f"Y: {slash_coords[:,1].min()} to {slash_coords[:,1].max()} (Height: {slash_coords[:,1].max() - slash_coords[:,1].min()})")
print(f"Center: ({slash_coords[:,0].mean():.1f}, {slash_coords[:,1].mean():.1f})")

print("\n--- Triangle Bounding Box ---")
print(f"X: {triangle_coords[:,0].min()} to {triangle_coords[:,0].max()} (Width: {triangle_coords[:,0].max() - triangle_coords[:,0].min()})")
print(f"Y: {triangle_coords[:,1].min()} to {triangle_coords[:,1].max()} (Height: {triangle_coords[:,1].max() - triangle_coords[:,1].min()})")
print(f"Center: ({triangle_coords[:,0].mean():.1f}, {triangle_coords[:,1].mean():.1f})")
