import os
import re
import numpy as np
from PIL import Image, ImageFilter
import xml.etree.ElementTree as ET

def get_bayer_matrix_8x8():
    b2 = np.array([[0, 2], [3, 1]])
    b4 = np.block([[4*b2 + 0, 4*b2 + 2], [4*b2 + 3, 4*b2 + 1]])
    b8 = np.block([[4*b4 + 0, 4*b4 + 2], [4*b4 + 3, 4*b4 + 1]])
    return (b8 + 0.5) / 64.0

def generate_master_portrait_arrays(photo_path):
    orig = Image.open(photo_path).convert('L')
    target_w, target_h = 300, 307
    
    img_w, img_h = orig.size
    aspect_target = target_w / target_h
    aspect_img = img_w / img_h
    
    if aspect_img > aspect_target:
        new_w = int(img_h * aspect_target)
        left = (img_w - new_w) // 2
        img = orig.crop((left, 0, left + new_w, img_h))
    else:
        new_h = int(img_w / aspect_target)
        top = int((img_h - new_h) * 0.15)
        img = orig.crop((0, top, img_w, top + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    
    edges = np.array(img.filter(ImageFilter.FIND_EDGES), dtype=np.float32) / 255.0
    blur_edges = np.array(Image.fromarray((edges*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=4)), dtype=np.float32) / 255.0
    
    y_idx, x_idx = np.indices((target_h, target_w))
    center_dist_x = np.abs(x_idx - target_w/2.0) / (target_w / 2.0)
    center_dist_y = y_idx / float(target_h)
    
    is_bg = (blur_edges < 0.035) & (arr > 0.35) & ((center_dist_x > 0.35) | (center_dist_y < 0.25))
    is_bg = is_bg | ((center_dist_y < 0.55) & (center_dist_x > 0.45) & (blur_edges < 0.05))
    
    fg_mask = 1.0 - is_bg.astype(np.float32)
    fg_mask_img = Image.fromarray((fg_mask*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=3))
    fg_mask = np.array(fg_mask_img, dtype=np.float32) / 255.0

    blur_mid = np.array(img.filter(ImageFilter.GaussianBlur(radius=7)), dtype=np.float32) / 255.0
    sharp_detail = (arr - blur_mid) * 1.55
    enhanced = np.clip(arr + sharp_detail, 0.0, 1.0)
    
    bayer = get_bayer_matrix_8x8()
    bayer_tiled = np.tile(bayer, (int(np.ceil(target_h/8)), int(np.ceil(target_w/8))))[:target_h, :target_w]
    
    signal_dark = enhanced * fg_mask
    signal_dark = np.clip(signal_dark * 1.18, 0.0, 1.0)
    
    jacket_mask = (y_idx > target_h * 0.65).astype(np.float32)
    signal_dark = np.where((jacket_mask > 0) & (edges > 0.06) & (fg_mask > 0.5), np.maximum(signal_dark, 0.55), signal_dark)
    
    thresh_dark = bayer_tiled * 0.75 + 0.12
    binary_dark = (signal_dark > thresh_dark).astype(np.uint8)
    binary_dark[fg_mask < 0.2] = 0
    
    binary_dark[0:1, :] = 1; binary_dark[-1:, :] = 1; binary_dark[:, 0:1] = 1; binary_dark[:, -1:] = 1
    
    inv_enhanced = 1.0 - enhanced
    signal_light = inv_enhanced * fg_mask
    signal_light = np.clip(signal_light * 1.22, 0.0, 1.0)
    
    thresh_light = bayer_tiled * 0.68 + 0.15
    binary_light = (signal_light > thresh_light).astype(np.uint8)
    binary_light[fg_mask < 0.2] = 0
    
    binary_light[0:1, :] = 1; binary_light[-1:, :] = 1; binary_light[:, 0:1] = 1; binary_light[:, -1:] = 1
    
    canvas_dark = np.zeros((350, 320), dtype=np.uint8)
    canvas_dark[32:32+target_h, 0:target_w] = binary_dark
    
    canvas_light = np.zeros((350, 320), dtype=np.uint8)
    canvas_light[32:32+target_h, 0:target_w] = binary_light
    
    return canvas_dark, canvas_light

def extract_horizontal_runs(canvas):
    runs = []
    for y in range(350):
        row = canvas[y]
        diff = np.diff(np.concatenate(([0], row, [0])))
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        for s, e in zip(starts, ends):
            runs.append((s, y, e - s))
    return runs

def serialize_runs_to_path(runs):
    if not runs:
        return "M 0,0"
    parts = [f"M {x},{y} h {l}" for x, y, l in runs]
    return " ".join(parts)

def update_svg_file(source_svg, output_svg, new_canvas):
    print(f"Reading {source_svg}...")
    runs = extract_horizontal_runs(new_canvas)
    print(f"  Extracted {len(runs)} horizontal runs (Active pixels: {np.sum(new_canvas)}).")
    
    tree = ET.parse(source_svg)
    root = tree.getroot()
    
    portrait_group = None
    for elem in root.iter():
        if elem.tag.endswith('g') and elem.attrib.get('transform') == "translate(50,86) scale(1.2400,1.4471)":
            portrait_group = elem
            break
            
    if portrait_group is None:
        print(f"ERROR: Could not find portrait group in {source_svg}")
        return False
        
    set1, set2 = [], []
    for child in portrait_group:
        if child.tag.endswith('g'):
            if child.find('{*}animate') is not None or child.find('animate') is not None or child.attrib.get('opacity') == '0':
                set1.append(child)
            elif child.find('{*}animateTransform') is not None or child.find('animateTransform') is not None:
                set2.append(child)
                
    runs_sorted = sorted(runs, key=lambda r: (r[1], r[0]))
    total_runs = len(runs_sorted)
    
    if len(set1) > 0:
        chunk_size_1 = max(1, total_runs // len(set1))
        for i, grp in enumerate(set1):
            path = grp.find('{*}path')
            if path is None: path = grp.find('path')
            if path is not None:
                start = i * chunk_size_1
                end = (i + 1) * chunk_size_1 if i < len(set1) - 1 else total_runs
                path.set('d', serialize_runs_to_path(runs_sorted[start:end]))
                
    if len(set2) > 0:
        chunk_size_2 = max(1, total_runs // len(set2))
        for i, grp in enumerate(set2):
            path = grp.find('{*}path')
            if path is None: path = grp.find('path')
            if path is not None:
                start = i * chunk_size_2
                end = (i + 1) * chunk_size_2 if i < len(set2) - 1 else total_runs
                path.set('d', serialize_runs_to_path(runs_sorted[start:end]))
                
    tree.write(output_svg, encoding="UTF-8", xml_declaration=True)
    print(f"Successfully engineered and saved to {output_svg}!")
    return True

if __name__ == "__main__":
    brain_dir = r"C:/Users/M.Shahzaib/.gemini/antigravity/brain/d4cc5c92-ddf6-4f25-9f64-bcabfa9266d5"
    photo_file = os.path.join(brain_dir, "media__1785335440634.jpg")
    print("Executing Master Bayer-Adaptive Halftoning Pipeline...")
    dark_canvas, light_canvas = generate_master_portrait_arrays(photo_file)
    
    dark_preview = np.full((350, 320, 3), [10, 16, 31], dtype=np.uint8)
    dark_preview[dark_canvas == 1] = [167, 139, 250]
    Image.fromarray(dark_preview).save(os.path.join(brain_dir, "master_preview_dark.png"))
    
    light_preview = np.full((350, 320, 3), [248, 250, 252], dtype=np.uint8)
    light_preview[light_canvas == 1] = [124, 58, 237]
    Image.fromarray(light_preview).save(os.path.join(brain_dir, "master_preview_light.png"))
    
    dark_svg = r"c:\Users\M.Shahzaib\Desktop\updated github profile design\arifhaxn-main\dark.svg"
    light_svg = r"c:\Users\M.Shahzaib\Desktop\updated github profile design\arifhaxn-main\light.svg"
    
    out_dark = os.path.join(brain_dir, "dark_master_output.svg")
    out_light = os.path.join(brain_dir, "light_master_output.svg")
    
    update_svg_file(dark_svg, out_dark, dark_canvas)
    update_svg_file(light_svg, out_light, light_canvas)
    print("ALL DONE! Master outputs generated cleanly!")
