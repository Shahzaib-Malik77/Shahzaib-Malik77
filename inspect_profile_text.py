import xml.etree.ElementTree as ET

def inspect_svg(path):
    print(f"--- Inspecting {path} ---")
    tree = ET.parse(path)
    root = tree.getroot()
    
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag in ('text', 'tspan', 'a'):
            txt = (elem.text or '').strip()
            href = elem.attrib.get('{http://www.w3.org/1999/xlink}href') or elem.attrib.get('href') or ''
            attrs = str(elem.attrib)
            if txt or href or tag == 'a':
                print(f"[{tag}] text='{txt}' href='{href}' | attribs={elem.attrib}")

if __name__ == '__main__':
    inspect_svg("arifhaxn-main/dark.svg")
