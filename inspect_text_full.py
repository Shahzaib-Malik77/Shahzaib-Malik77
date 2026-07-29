import xml.etree.ElementTree as ET

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

def dump_text_elements(svg_path, out_file):
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f"===================== TEXT ELEMENTS IN {svg_path} =====================\n")
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        if 'aria-label' in root.attrib:
            f.write(f"[ROOT aria-label]: {root.attrib['aria-label']}\n")
            
        for elem in root.iter():
            tag = strip_ns(elem.tag)
            if tag == 'text':
                full_text = ""
                if elem.text:
                    full_text += elem.text
                tspans = []
                for child in elem:
                    if strip_ns(child.tag) == 'tspan':
                        txt = (child.text or '')
                        fill = child.attrib.get('fill', '')
                        fw = child.attrib.get('font-weight', '')
                        tspans.append(f"tspan(text='{txt}', fill='{fill}', font-weight='{fw}')")
                        full_text += txt
                    if child.tail:
                        full_text += child.tail
                x = elem.attrib.get('x', '')
                y = elem.attrib.get('y', '')
                f.write(f"x={x:<5} y={y:<5} | FULL: {full_text.strip()}\n")
                if tspans:
                    for ts in tspans:
                        f.write(f"    -> {ts}\n")

if __name__ == '__main__':
    dump_text_elements('arifhaxn-main/dark.svg', 'text_dump_utf8.txt')

