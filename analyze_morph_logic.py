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

def inspect_container_2(svg_path):
    print(f"\n==================== Inspecting Container #2 of {svg_path} ====================")
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    # Find Container #2 (opacity="0" initially, transform translate(50,86))
    c2 = None
    for elem in root.iter():
        if strip_ns(elem.tag) == 'g':
            tr = elem.attrib.get('transform', '')
            op = elem.attrib.get('opacity', '1')
            if ('translate(50,86)' in tr or 'scale(1.24' in tr) and op == '0':
                c2 = elem
                break
                
    if not c2:
        print("Could not find Container #2!")
        return

    child_groups = []
    for child in c2:
        if strip_ns(child.tag) == 'g':
            path = None
            anims = []
            for gc in child:
                if strip_ns(gc.tag) == 'path':
                    path = gc
                elif strip_ns(gc.tag) in ['animate', 'animateTransform']:
                    anims.append(gc)
            if path is not None:
                child_groups.append((child, path, anims))
                
    print(f"Container #2 has {len(child_groups)} child groups.")
    for idx, (cg, p, anims) in enumerate(child_groups[:10]):
        runs = parse_runs_from_path_d(p.attrib.get('d', ''))
        xs = [r[0] for r in runs] if runs else [0]
        ys = [r[1] for r in runs] if runs else [0]
        anim_desc = []
        for a in anims:
            anim_desc.append(f"{a.attrib.get('attributeName')}={a.attrib.get('values', '')[:40]}... (dur={a.attrib.get('dur')})")
        print(f"  Grp #{idx+1}: {len(runs)} runs | X:[{min(xs)},{max(xs)}] Y:[{min(ys)},{max(ys)}] | Anims: {'; '.join(anim_desc)}")

    # Check how runs are distributed across all 94/96 groups in Container 2!
    # Is it sliced by X, by Y, by grid blocks, or how?
    all_centers = []
    for idx, (cg, p, anims) in enumerate(child_groups):
        runs = parse_runs_from_path_d(p.attrib.get('d', ''))
        if runs:
            avg_x = np.mean([r[0] + r[2]/2.0 for r in runs])
            avg_y = np.mean([r[1] for r in runs])
            all_centers.append((avg_x, avg_y))
        else:
            all_centers.append((0, 0))
            
    print("\nFirst 15 Group Center coordinates (Avg X, Avg Y):")
    for i in range(min(15, len(all_centers))):
        print(f"  Grp #{i+1}: ({all_centers[i][0]:.1f}, {all_centers[i][1]:.1f})")
    print("\nLast 15 Group Center coordinates (Avg X, Avg Y):")
    for i in range(max(0, len(all_centers)-15), len(all_centers)):
        print(f"  Grp #{i+1}: ({all_centers[i][0]:.1f}, {all_centers[i][1]:.1f})")

if __name__ == "__main__":
    inspect_container_2("arifhaxn-main/dark_original_backup.svg")
    inspect_container_2("arifhaxn-main/light_original_backup.svg")
