import xml.etree.ElementTree as ET
import re
import numpy as np
from PIL import Image

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

def parse_runs(d_str):
    runs = []
    for m in re.finditer(r'M(\d+)\s*(\d+)h(\d+)', d_str or ''):
        x, y, l = int(m.group(1)), int(m.group(2)), int(m.group(3))
        runs.append((x, y, l))
    return runs

def get_group_centroids(svg_path):
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    c2 = None
    for elem in root.iter():
        if strip_ns(elem.tag) == 'g' and elem.attrib.get('opacity', '1') == '0':
            tr = elem.attrib.get('transform', '')
            if 'translate(50,86)' in tr or 'scale(1.24' in tr:
                c2 = elem
                break
                
    centroids = []
    runs_per_group = []
    for child in c2:
        if strip_ns(child.tag) == 'g':
            for gc in child:
                if strip_ns(gc.tag) == 'path':
                    r = parse_runs(gc.attrib.get('d', ''))
                    runs_per_group.append(r)
                    if r:
                        pts_x = []
                        pts_y = []
                        for x, y, l in r:
                            for dx in range(l):
                                pts_x.append(x + dx)
                                pts_y.append(y)
                        centroids.append((np.mean(pts_x), np.mean(pts_y), np.min(pts_x), np.max(pts_x), np.min(pts_y), np.max(pts_y)))
                    else:
                        centroids.append((150, 150, 0, 300, 0, 338))
                    break
    return centroids, runs_per_group

def analyze_spatial_clustering():
    d_cents, d_runs = get_group_centroids("arifhaxn-main/dark_original_backup.svg")
    print(f"Dark Backup Container #2 has {len(d_cents)} spatial clusters.")
    # Verify if every pixel in the original backup is closest to its group centroid!
    correct = 0
    total = 0
    for g_idx, r_list in enumerate(d_runs):
        gx, gy = d_cents[g_idx][0], d_cents[g_idx][1]
        for x, y, l in r_list:
            mid_x = x + l/2.0
            # find closest centroid
            dists = [((mid_x - cx)**2 + (y - cy)**2) for cx, cy, _, _, _, _ in d_cents]
            closest_idx = np.argmin(dists)
            if closest_idx == g_idx:
                correct += 1
            total += 1
    print(f"Dark Backup Voronoi consistency: {correct} / {total} runs ({correct*100.0/total:.1f}%) directly match closest centroid!")
    
    # What if we assign each point to the group that contained the closest ORIGINAL pixel? (Nearest Neighbor to original pixels)
    print("If we assign each new pixel run to the group of the nearest original pixel run, we guarantee 100% spatial fidelity to the Flutter logo transform!")

def check_light_mode_image():
    # Why did light mode look bad? Let's check the histogram and density of light_original_backup vs our generated light
    l_cents, l_runs = get_group_centroids("arifhaxn-main/light_original_backup.svg")
    orig_light_dots = sum(sum(r[2] for r in r_list) for r_list in l_runs)
    print(f"\nOriginal Light Backup Total Active Dots in Container #2: {orig_light_dots} dots out of {300*338} ({orig_light_dots*100.0/(300*338):.2f}%)")

if __name__ == "__main__":
    analyze_spatial_clustering()
    check_light_mode_image()
