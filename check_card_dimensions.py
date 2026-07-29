import xml.etree.ElementTree as ET

tree = ET.parse("arifhaxn-main/dark.svg")
root = tree.getroot()

print("SVG attributes:", root.attrib)

# Find any rects or containers around x=470 to see width
for elem in root.iter():
    tag = elem.tag.split('}')[-1]
    if tag == 'rect':
        x = float(elem.attrib.get('x', 0))
        y = float(elem.attrib.get('y', 0))
        w = float(elem.attrib.get('width', 0))
        h = float(elem.attrib.get('height', 0))
        if w > 500: # large background or frame rects
            print(f"Rect: x={x}, y={y}, width={w}, height={h}, fill={elem.attrib.get('fill')}")

    if tag == 'text' and elem.attrib.get('y') in ('162', '277', '29', '106'):
        print(f"Text y={elem.attrib.get('y')}: style={elem.attrib.get('style')} font-size={elem.attrib.get('font-size')} font-family={elem.attrib.get('font-family')}")
