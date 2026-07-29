import re
import numpy as np

def inspect_set1(filepath, start_idx, end_idx):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    
    print(f"\n--- {filepath} Set 1 Inspection ---")
    for idx in range(start_idx, min(end_idx, start_idx+10)):
        line = lines[idx]
        if '<path d="' not in line:
            continue
        xs = [int(m.group(1)) for m in re.finditer(r'M(\d+)\s+(\d+)', line)]
        ys = [int(m.group(2)) for m in re.finditer(r'M(\d+)\s+(\d+)', line)]
        begin = re.search(r'begin=\"([^\"]+)\"', line)
        b_str = begin.group(1) if begin else 'none'
        print(f"Group {idx-start_idx+1:2d} (begin {b_str:6s}): X=[{min(xs):3d}..{max(xs):3d}], Y=[{min(ys):3d}..{max(ys):3d}], points={len(xs)}")

inspect_set1('arifhaxn-main/dark.svg', 32, 92)
inspect_set1('arifhaxn-main/light.svg', 32, 92)
