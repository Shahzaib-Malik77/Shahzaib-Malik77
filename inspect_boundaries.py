# Verify exact line indices for dark.svg and light.svg
def inspect_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
    print(f"\n--- {path} --- (Total lines: {len(lines)})")
    for idx in range(28, 36):
        print(f"Line {idx+1:3d}: {lines[idx][:120]}")
    print("...")
    for idx in range(90, 98):
        print(f"Line {idx+1:3d}: {lines[idx][:120]}")
    print("...")
    for idx in range(188, min(196, len(lines))):
        print(f"Line {idx+1:3d}: {lines[idx][:120]}")

inspect_file('arifhaxn-main/dark.svg')
inspect_file('arifhaxn-main/light.svg')
