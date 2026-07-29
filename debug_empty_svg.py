import xml.etree.ElementTree as ET

def strip_ns(tag):
    return tag.split('}')[-1] if '}' in tag else tag

def analyze_svg(path):
    print(f"=== {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    print("Root tag:", root.tag, "Attrib:", root.attrib)
    
    # Check groups
    for g in root.iter():
        if strip_ns(g.tag) == 'g':
            tr = g.attrib.get('transform', '')
            if 'translate(50' in tr or 'scale' in tr:
                print("Found Main Portrait Group:", g.attrib)
                for child in g:
                    if strip_ns(child.tag) in ['g', 'set', 'path', 'animate']:
                        print("  Child tag:", strip_ns(child.tag), "attribs:", child.attrib)
                        # Check first child of this group
                        if strip_ns(child.tag) == 'g':
                            for sub in child:
                                print("    Sub tag:", strip_ns(sub.tag), "attribs:", sub.attrib)
                                if strip_ns(sub.tag) == 'path':
                                    d = sub.attrib.get('d', '')
                                    print("    Path length:", len(d), "Preview:", d[:50])
                                break

analyze_svg("arifhaxn-main/dark_original_backup.svg")
analyze_svg("arifhaxn-main/dark.svg")
