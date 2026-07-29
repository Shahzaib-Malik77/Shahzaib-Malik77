import xml.etree.ElementTree as ET
import re
import numpy as np

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

def get_dot_grid(svg_path):
    grid = np.zeros((400, 400), dtype=bool)
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    # Inspect Container #1 since it contains all active dots in fade-in layers
    c1 = None
    for elem in root.iter():
        if strip_ns(elem.tag) == 'g' and elem.attrib.get('opacity', '1') == '1':
            tr = elem.attrib.get('transform', '')
            if 'translate(50,86)' in tr or 'scale(1.24' in tr:
                c1 = elem
                break
                
    if c1 is not None:
        for child in c1:
            for gc in child:
                if strip_ns(gc.tag) == 'path':
                    d = gc.attrib.get('d', '')
                    for m in re.finditer(r'M(\d+)\s*(\d+)h(\d+)', d):
                        x, y, l = int(m.group(1)), int(m.group(2)), int(m.group(3))
                        grid[y, x:x+l] = True
    return grid

def compare_grids():
    dark_grid = get_dot_grid("arifhaxn-main/dark_original_backup.svg")
    light_grid = get_dot_grid("arifhaxn-main/light_original_backup.svg")
    
    dark_count = np.sum(dark_grid)
    light_count = np.sum(light_grid)
    both_count = np.sum(dark_grid & light_grid)
    
    print(f"Original Dark Backup Active Dots: {dark_count}")
    print(f"Original Light Backup Active Dots: {light_count}")
    print(f"Dots active in BOTH dark and light: {both_count} ({both_count*100.0/dark_count:.1f}% of dark dots are ALSO active in light!)")
    
if __name__ == "__main__":
    compare_grids()
