import os, re

SRC_DIR = r"C:\Users\mauri\OneDrive\Desktop\sistema-informatico\rodlerIcons"
for name in os.listdir(SRC_DIR):
    if not name.lower().endswith(".svg"): 
        continue
    if name.lower().endswith("_white.svg"):
        continue
    src = os.path.join(SRC_DIR, name)
    dst = os.path.join(SRC_DIR, os.path.splitext(name)[0] + "_white.svg")
    try:
        with open(src, "r", encoding="utf-8") as f:
            svg = f.read()
        # Reemplazos básicos (no destructivos)
        svg = re.sub(r'fill="[^"]*"', 'fill="#FFFFFF"', svg, flags=re.IGNORECASE)
        svg = re.sub(r'stroke="[^"]*"', 'stroke="#FFFFFF"', svg, flags=re.IGNORECASE)
        # Si no había fill/stroke, podés inyectar un estilo global simple:
        if 'fill=' not in svg and 'stroke=' not in svg:
            svg = svg.replace("<svg", '<svg style="fill:#FFFFFF;stroke:#FFFFFF;"', 1)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(svg)
        print("OK:", dst)
    except Exception as e:
        print("ERR:", name, e)
