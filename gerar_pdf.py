"""Gera um PDF A4 pesquisável do roteiro, sem dependências externas."""
from pathlib import Path
import re
import textwrap
import zlib
from PIL import Image

base = Path(__file__).resolve().parent
source = (base / "README.md").read_text(encoding="utf-8")
dest = base / "pratica-node-red.pdf"
W, H = 595, 842
pages = [[]]
y = 788
images = {}

def esc(s):
    for a, b in {"→":"->", "←":"<-", "►":">", "─":"-", "│":"|", "┐":"+", "┘":"+", "≈":"~", "☰":"menu"}.items():
        s = s.replace(a, b)
    return s.encode("cp1252", "replace").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")

def new_page():
    global y
    pages.append([])
    y = 788

def draw(s, size=10, font="F1", indent=0, color="0.13 0.17 0.25"):
    global y
    lead = size * 1.4
    if y - lead < 48:
        new_page()
    pages[-1].append(f"BT /{font} {size} Tf {color} rg 1 0 0 1 {48+indent} {y:.1f} Tm (".encode()+esc(s)+b") Tj ET\n")
    y -= lead

def clean(s):
    s = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    return s.replace("**", "").replace("`", "")

def para(s, indent=0, size=10, font="F1", chars=98):
    global y
    for row in textwrap.wrap(clean(s), chars - indent//7, break_long_words=False, break_on_hyphens=False):
        draw(row, size, font, indent)
    y -= 5

def figure(path):
    global y
    img = Image.open(base / path).convert("RGB")
    name = "Im" + str(len(images) + 1)
    images[name] = img
    width = 499
    height = width * img.height / img.width
    if y - height < 48:
        new_page()
    bottom = y - height
    pages[-1].append(f"q {width:.1f} 0 0 {height:.1f} 48 {bottom:.1f} cm /{name} Do Q\n".encode())
    y = bottom - 12

buf = []
code = False
def flush():
    if buf:
        para(" ".join(buf))
        buf.clear()

for raw in source.splitlines():
    s = raw.rstrip()
    if s.startswith("```"):
        flush()
        code = not code
        y -= 5
    elif code:
        rows = textwrap.wrap(s, 102, replace_whitespace=False, drop_whitespace=False, break_long_words=True) or [""]
        for row in rows:
            draw(row, 8, "F3", 6, "0.12 0.25 0.32")
    elif not s:
        flush()
    elif s.startswith("!["):
        flush()
        match = re.match(r"!\[[^]]*\]\(([^)]+)\)", s)
        if match:
            figure(match.group(1))
    elif s.startswith("#"):
        flush()
        level = len(s) - len(s.lstrip("#"))
        if level <= 3:
            y -= 12 if level > 1 else 2
            title = clean(s[level:].strip())
            for part in textwrap.wrap(title, {1:47, 2:67, 3:80}[level], break_long_words=False):
                draw(part, {1:20, 2:14, 3:11}[level], "F2", color="0.06 0.20 0.40")
            y -= 5
    elif s.startswith("|"):
        flush()
        cells = [clean(x.strip()) for x in s.strip("|").split("|")]
        if not all(re.fullmatch(r":?-+:?", c or "") for c in cells):
            para("  |  ".join(cells), size=9, chars=109)
    elif re.match(r"^[-*] |^\d+\. ", s):
        flush()
        para(s, indent=9, size=9.5, chars=103)
    else:
        buf.append(s)
flush()

objs=[]
def add(v):
    objs.append(v)
    return len(objs)
catalog=add(b"")
root=add(b"")
f1=add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
f2=add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
f3=add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>")
image_refs = {}
for name, img in images.items():
    pixels = zlib.compress(img.tobytes(), 7)
    image_refs[name] = add(f"<< /Type /XObject /Subtype /Image /Width {img.width} /Height {img.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(pixels)} >>\nstream\n".encode() + pixels + b"\nendstream")
ids=[]
for n, p in enumerate(pages, 1):
    header=b"BT /F2 8 Tf 0.06 0.20 0.40 rg 1 0 0 1 48 817 Tm (Redes para Controle e Automacao) Tj ET\n"
    footer=f"BT /F1 8 Tf 0.4 0.4 0.4 rg 1 0 0 1 48 28 Tm (Pratica TCP e Node-RED  |  {n}/{len(pages)}) Tj ET\n".encode()
    content=header+b"".join(p)+footer
    stream=add(f"<< /Length {len(content)} >>\nstream\n".encode()+content+b"endstream")
    xobjects = " ".join(f"/{name} {ref} 0 R" for name, ref in image_refs.items())
    ids.append(add(f"<< /Type /Page /Parent {root} 0 R /MediaBox [0 0 {W} {H}] /Resources << /Font << /F1 {f1} 0 R /F2 {f2} 0 R /F3 {f3} 0 R >> /XObject << {xobjects} >> >> /Contents {stream} 0 R >>".encode()))
objs[catalog-1]=f"<< /Type /Catalog /Pages {root} 0 R >>".encode()
objs[root-1]=f"<< /Type /Pages /Kids [{' '.join(f'{p} 0 R' for p in ids)}] /Count {len(ids)} >>".encode()
pdf=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
offsets=[0]
for i, obj in enumerate(objs, 1):
    offsets.append(len(pdf))
    pdf.extend(f"{i} 0 obj\n".encode()+obj+b"\nendobj\n")
start=len(pdf)
pdf.extend(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode())
for offset in offsets[1:]:
    pdf.extend(f"{offset:010d} 00000 n \n".encode())
pdf.extend(f"trailer\n<< /Size {len(objs)+1} /Root {catalog} 0 R >>\nstartxref\n{start}\n%%EOF\n".encode())
dest.write_bytes(pdf)
print(f"{dest} ({len(pages)} páginas)")
