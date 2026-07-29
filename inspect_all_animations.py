import xml.etree.ElementTree as ET

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

with open("arifhaxn-main/dark.svg", "r", encoding="utf-8") as f:
    content = f.read()

tree = ET.ElementTree(ET.fromstring(content))
root = tree.getroot()

print("Scanning dark.svg for all high-level groups and animations...")
for idx, elem in enumerate(root):
    tag = strip_ns(elem.tag)
    attrib = elem.attrib
    print(f"Top-level element {idx+1}: <{tag}> {attrib}")
    if tag == 'g':
        # count children
        children = list(elem)
        print(f"   -> has {len(children)} direct children")
        # print first few children and any animate tags
        for c_idx, c in enumerate(children[:5]):
            print(f"      Child {c_idx+1}: <{strip_ns(c.tag)}> {c.attrib}")
            for sc in c:
                if strip_ns(sc.tag) in ['animate', 'animateTransform', 'set', 'path']:
                    d_len = len(sc.attrib.get('d', '')) if strip_ns(sc.tag) == 'path' else '-'
                    print(f"         Sub-child: <{strip_ns(sc.tag)}> {sc.attrib} (d len: {d_len})")

# Also look specifically inside Container #2 (the one with opacity="0")
for elem in root.iter():
    if strip_ns(elem.tag) == 'g' and elem.attrib.get('opacity') == '0' and 'translate(50,86)' in elem.attrib.get('transform', ''):
        print("\n=== Detailed Analysis of Container #2 ===")
        print(f"Attributes: {elem.attrib}")
        for idx, child in enumerate(list(elem)[:3]):
            print(f"\nGroup #{idx+1}: {child.attrib}")
            for sc in child:
                if strip_ns(sc.tag) != 'path':
                    print(f"  Animation: <{strip_ns(sc.tag)}> {sc.attrib}")
                else:
                    print(f"  Path with length {len(sc.attrib.get('d', ''))}")
        break
