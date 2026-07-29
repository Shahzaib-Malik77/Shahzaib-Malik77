import xml.etree.ElementTree as ET

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

with open("arifhaxn-main/dark.svg", "r", encoding="utf-8") as f:
    content = f.read()

tree = ET.ElementTree(ET.fromstring(content))
root = tree.getroot()

c3 = None
for elem in root.iter():
    if strip_ns(elem.tag) == 'g' and 'translate(50,86)' in elem.attrib.get('transform', ''):
        if len(list(elem)) >= 800:
            c3 = elem
            break

triangle_pts = []
for dot in list(c3)[:50]:
    for sc in dot:
        if strip_ns(sc.tag) == 'animateTransform':
            vals = sc.attrib.get('values', '').split(';')
            if len(vals) == 9:
                triangle_pts.append(vals[6])

print("First 50 triangle coordinates:", triangle_pts[:20])
