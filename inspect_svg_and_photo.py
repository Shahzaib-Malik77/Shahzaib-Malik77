import os
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np

out_lines = []
def log(msg=""):
    print(msg)
    out_lines.append(str(msg))

def inspect_svg(svg_path):
    log(f"\n=================== INSPECTING {svg_path} ===================")
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    log(f"Total lines in SVG: {len(lines)}")
    
    for i, line in enumerate(lines[:200]):
        if "translate(" in line and ("50" in line or "86" in line) or "scale(1.24" in line:
            log(f"Line {i+1}: found portrait container -> {line[:150]}...")
        if '<set attributeName="opacity"' in line or 'animateTransform' in line:
            if i < 150:
                log(f"Line {i+1}: animation tag -> {line[:120]}...")
                
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    portrait_groups = []
    for idx, elem in enumerate(root.iter()):
        if elem.tag.endswith('g'):
            transform = elem.attrib.get('transform', '')
            if 'translate(50,86)' in transform or 'scale(1.24' in transform or 'translate(50' in transform:
                portrait_groups.append((elem, transform, elem.attrib.get('opacity', '1')))
                
    log(f"\nFound {len(portrait_groups)} portrait-related group containers!")
    for i, (grp, tr, op) in enumerate(portrait_groups):
        paths = list(grp.iter(f"{{{root.tag.split('}')[0].strip('{')}}}path")) if '}' in root.tag else list(grp.iter('path'))
        if not paths:
            paths = [p for p in list(grp.iter()) if p.tag.endswith('path')]
        log(f"  Container #{i+1}: transform='{tr}', opacity='{op}', direct children={len(list(grp))}, total paths inside={len(paths)}")
        for j, child in enumerate(list(grp)[:8]):
            tag_name = child.tag.split('}')[-1]
            anim = [c.tag.split('}')[-1] for c in child]
            log(f"    Child {j+1}: <{tag_name}> attrib={child.attrib}, child tags={anim}")
            # check if child has paths or is a group of paths
            child_paths = [p for p in list(child.iter()) if p.tag.endswith('path')]
            if len(child_paths) > 0 and len(child_paths) <= 5:
                for cp in child_paths:
                    d_len = len(cp.attrib.get('d', ''))
                    log(f"      path d length={d_len}")
            elif len(child_paths) > 5:
                log(f"      contains {len(child_paths)} paths")

def inspect_photo(photo_path):
    log(f"\n=================== INSPECTING PHOTO {photo_path} ===================")
    if not os.path.exists(photo_path):
        log(f"ERROR: file {photo_path} not found!")
        return
    img = Image.open(photo_path)
    log(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
    arr = np.array(img.convert('RGB'))
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    log(f"R range: [{R.min()}, {R.max()}], mean: {R.mean():.1f}")
    log(f"G range: [{G.min()}, {G.max()}], mean: {G.mean():.1f}")
    log(f"B range: [{B.min()}, {B.max()}], mean: {B.mean():.1f}")
    
    top_border = arr[0:10, :, :].mean(axis=(0,1))
    left_border = arr[:, 0:10, :].mean(axis=(0,1))
    right_border = arr[:, -10:, :].mean(axis=(0,1))
    bottom_border = arr[-10:, :, :].mean(axis=(0,1))
    log(f"Estimated Background Colors (RGB mean):")
    log(f"  Top border:    {top_border.round(1)}")
    log(f"  Left border:   {left_border.round(1)}")
    log(f"  Right border:  {right_border.round(1)}")
    log(f"  Bottom border: {bottom_border.round(1)}")

if __name__ == "__main__":
    inspect_svg("arifhaxn-main/dark_original_backup.svg")
    inspect_photo("my image.png")
    with open("inspection_output_utf8.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
