import sys
import re
import numpy as np

with open("deep_analysis_result.txt", "w", encoding="utf-8") as out:
    out.write(f"Python version: {sys.version}\n")
    for pkg in ['cv2', 'scipy', 'skimage', 'matplotlib', 'PIL']:
        try:
            __import__(pkg)
            out.write(f"Package {pkg}: AVAILABLE\n")
        except ImportError:
            out.write(f"Package {pkg}: NOT AVAILABLE\n")

    def analyze_portrait(filepath, name):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        canvas = np.zeros((350, 320), dtype=np.uint8)
        for line in content.split('\n')[32:193]:
            if '<path d="' in line and not '<set' in line:
                for m in re.finditer(r'M(\d+)\s+(\d+)h(\d+)v1h-\3z', line):
                    x, y, w = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    if y < 350 and x + w <= 320:
                        canvas[y, x:x+w] = 1

        total_pixels = np.sum(canvas)
        out.write(f"\n--- Statistical Analysis of Original: {name} ---\n")
        out.write(f"Total active pixels: {total_pixels} out of {350*320} ({total_pixels / (350*320):.2%})\n")
        
        runs = []
        for y in range(350):
            row = canvas[y]
            diff = np.diff(np.concatenate(([0], row, [0])))
            starts = np.where(diff == 1)[0]
            ends = np.where(diff == -1)[0]
            runs.extend(ends - starts)
        runs = np.array(runs)
        if len(runs) > 0:
            out.write(f"Run count: {len(runs)}, Mean length: {np.mean(runs):.2f}, Max length: {np.max(runs)}, Single-pixel runs (%): {np.sum(runs==1)/len(runs):.2%}\n")
        
        face_region = canvas[80:240, 80:220]
        bg_region_top_left = canvas[35:100, 10:80]
        jacket_region = canvas[250:330, 80:220]
        out.write(f"Density -> Face center area: {np.mean(face_region):.2%}, Background top-left: {np.mean(bg_region_top_left):.2%}, Lower body/jacket area: {np.mean(jacket_region):.2%}\n")

        shift_x2 = np.mean(face_region[:, :-2] == face_region[:, 2:])
        shift_x1 = np.mean(face_region[:, :-1] == face_region[:, 1:])
        out.write(f"Adjacent pixel symmetry (X+1): {shift_x1:.2%}, (X+2): {shift_x2:.2%}\n")
        
    analyze_portrait('arifhaxn-main/dark_original_backup.svg', 'Dark Original')
    analyze_portrait('arifhaxn-main/light_original_backup.svg', 'Light Original')
