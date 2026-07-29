import xml.etree.ElementTree as ET

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

with open("arifhaxn-main/dark.svg", "r", encoding="utf-8") as f:
    content = f.read()

tree = ET.ElementTree(ET.fromstring(content))
root = tree.getroot()

win_group = None
for elem in root:
    if 'clip-path' in elem.attrib:
        win_group = elem
        break

print("Inspecting children #6 to #15 of winClip group:")
for idx in range(5, min(15, len(win_group))):
    child = win_group[idx]
    tag = strip_ns(child.tag)
    print(f"\n--- Child #{idx+1}: <{tag}> {child.attrib} ---")
    if tag == 'g':
        subchildren = list(child)
        print(f"    Subchildren count: {len(subchildren)}")
        for sc_idx, sc in enumerate(subchildren[:10]):
            print(f"    Subchild #{sc_idx+1}: <{strip_ns(sc.tag)}> {sc.attrib}")
            for ssc in list(sc)[:5]:
                print(f"        -> <{strip_ns(ssc.tag)}> {ssc.attrib}")
                if strip_ns(ssc.tag) == 'path':
                    d = ssc.attrib.get('d', '')
                    print(f"           Path d length: {len(d)}, starts: {d[:30]}...")
