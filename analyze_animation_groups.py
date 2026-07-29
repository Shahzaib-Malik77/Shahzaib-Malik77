import xml.etree.ElementTree as ET
import re
import numpy as np

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

def parse_runs_from_path_d(d_str):
    runs = []
    for m in re.finditer(r'M(\d+)\s*(\d+)h(\d+)', d_str or ''):
        x, y, l = int(m.group(1)), int(m.group(2)), int(m.group(3))
        runs.append((x, y, l))
    return runs

def inspect_svg(svg_path, name):
    print(f"\n========== {name} ({svg_path}) ==========")
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    # Find all groups that contain child groups with paths
    containers = []
    for elem in root.iter():
        if strip_ns(elem.tag) == 'g':
            child_groups = []
            for c in elem:
                if strip_ns(c.tag) == 'g':
                    for gc in c:
                        if strip_ns(gc.tag) == 'path':
                            child_groups.append((c, gc))
                            break
            if child_groups:
                containers.append((elem, child_groups))
                
    print(f"Found {len(containers)} containers with path child groups:")
    for idx, (c, child_groups) in enumerate(containers):
        print(f"\n--- Container #{idx+1} | attributes: {c.attrib} | has {len(child_groups)} animated/path layers ---")
        
        # Check if there are animateTransform tags in these child groups
        has_animate = sum(1 for cg, p in child_groups if any(strip_ns(x.tag) in ['animate', 'animateTransform'] for x in cg))
        print(f"    Child groups with animate/animateTransform: {has_animate} of {len(child_groups)}")
        
        for g_idx in range(min(4, len(child_groups))):
            cg, path = child_groups[g_idx]
            runs = parse_runs_from_path_d(path.attrib.get('d', ''))
            if runs:
                xs = [r[0] for r in runs]
                ys = [r[1] for r in runs]
                lengths = [r[2] for r in runs]
                print(f"    Group #{g_idx+1} ({cg.attrib}): {len(runs)} runs | Y range: [{min(ys)}, {max(ys)}] | X range: [{min(xs)}, {max(xs)}]")
            else:
                print(f"    Group #{g_idx+1}: 0 runs (or different d format: {path.attrib.get('d', '')[:30]})")
                
        # Let's analyze how the runs are distributed across ALL groups in this container!
        all_y_min = []
        all_y_max = []
        for cg, path in child_groups:
            runs = parse_runs_from_path_d(path.attrib.get('d', ''))
            if runs:
                all_y_min.append(min([r[1] for r in runs]))
                all_y_max.append(max([r[1] for r in runs]))
        if all_y_min:
            print(f"    Across all {len(child_groups)} groups: Min Y ranges from {min(all_y_min)} to {max(all_y_min)}")
            print(f"    Across all {len(child_groups)} groups: Max Y ranges from {min(all_y_max)} to {max(all_y_max)}")

if __name__ == "__main__":
    inspect_svg("arifhaxn-main/dark_original_backup.svg", "Original Dark Backup")
    inspect_svg("arifhaxn-main/light_original_backup.svg", "Original Light Backup")
    inspect_svg("arifhaxn-main/dark.svg", "Current Dark SVG")
    inspect_svg("arifhaxn-main/light.svg", "Current Light SVG")
