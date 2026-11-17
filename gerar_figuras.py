"""Desenha os esquemas da prática como imagens nítidas para o PDF."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

OUT = Path(__file__).resolve().parent / "figuras"
OUT.mkdir(exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
navy = "#163557"
teal = "#168e94"
blue = "#3972b8"
orange = "#cc7434"
gray = "#5d6b78"

def text(d, xy, value, size=30, color=navy, bold=False, anchor="mm"):
    d.text(xy, value, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color, anchor=anchor)

def box(d, xy, title, subtitle="", fill="#eef4f8", outline=navy):
    d.rounded_rectangle(xy, radius=22, fill=fill, outline=outline, width=4)
    x0,y0,x1,y1=xy
    center=((x0+x1)/2,(y0+y1)/2)
    title_size = 31
    while d.textbbox((0, 0), title, font=ImageFont.truetype(BOLD, title_size))[2] > x1 - x0 - 24:
        title_size -= 1
    text(d,(center[0],center[1]-(17 if subtitle else 0)),title,title_size,bold=True)
    if subtitle:
        subtitle_size = 23
        while d.textbbox((0, 0), subtitle, font=ImageFont.truetype(FONT, subtitle_size))[2] > x1 - x0 - 24:
            subtitle_size -= 1
        text(d,(center[0],center[1]+25),subtitle,subtitle_size,color=gray)

def arrow(d, start, end, color=teal, width=7):
    d.line([start,end],fill=color,width=width)
    angle=math.atan2(end[1]-start[1],end[0]-start[0])
    length=21
    p1=(end[0]-length*math.cos(angle-0.55),end[1]-length*math.sin(angle-0.55))
    p2=(end[0]-length*math.cos(angle+0.55),end[1]-length*math.sin(angle+0.55))
    d.polygon([end,p1,p2],fill=color)

im=Image.new("RGB",(1600,700),"white")
d=ImageDraw.Draw(im)
text(d,(800,47),"Arquitetura da prática",42,bold=True)
box(d,(50,165,390,580),"Computador do aluno","VS Code + navegador",fill="#f3f6fa")
box(d,(465,165,875,580),"EC2 A: clientes Python","sensor.py  |  atuador.py",fill="#eaf4f4",outline=teal)
box(d,(1050,165,1550,580),"EC2 B: Node-RED","2 servidores TCP + planta",fill="#edf2fa",outline=blue)
arrow(d,(390,225),(465,225),blue)
text(d,(427,195),"SSH",22,color=blue,bold=True)
arrow(d,(875,295),(1050,295),teal)
text(d,(962,260),"TCP 5001",23,color=teal,bold=True)
text(d,(962,335),"medida h",22,color=gray)
arrow(d,(875,460),(1050,460),orange)
text(d,(962,425),"TCP 5002",23,color=orange,bold=True)
text(d,(962,500),"controle u",22,color=gray)
arrow(d,(1050,365),(875,365),blue)
text(d,(962,385),"saída h",22,color=blue)
d.line([(220,165),(220,110),(1300,110),(1300,165)],fill=gray,width=5)
text(d,(805,86),"Túnel SSH para editor: localhost:1880",24,color=gray,bold=True)
text(d,(800,643),"As EC2 usam IP privado entre si; o editor é acessado pelo túnel SSH.",25,color=gray)
if not (OUT/"arquitetura.png").exists():
    im.save(OUT/"arquitetura.png")

im=Image.new("RGB",(1600,780),"white")
d=ImageDraw.Draw(im)
text(d,(800,45),"Fluxo no Node-RED",42,bold=True)
box(d,(45,145,335,245),"TCP in sensor","porta 5001",fill="#eaf4f4",outline=teal)
box(d,(45,305,335,405),"TCP in atuador","porta 5002",fill="#fff1e8",outline=orange)
box(d,(385,145,660,245),"Validar medida","HELLO ou h",fill="#eaf4f4",outline=teal)
box(d,(385,305,660,405),"Validar u","número >= 0",fill="#fff1e8",outline=orange)
box(d,(735,235,1110,440),"Planta discreta","h[k+1] = a h[k] + K(1-a)u[k]",fill="#edf2fa",outline=blue)
box(d,(1210,175,1550,275),"TCP out sensor","resposta na 5001",fill="#eaf4f4",outline=teal)
box(d,(1210,400,1550,500),"Debug","k, u, h",fill="#f3f6fa",outline=gray)
box(d,(165,555,520,655),"Inject h = 0","corrige estado",fill="#eaf4f4",outline=teal)
box(d,(670,555,1025,655),"Inject u = 10","avança 1 amostra",fill="#fff1e8",outline=orange)
arrow(d,(335,195),(385,195),teal)
arrow(d,(335,355),(385,355),orange)
arrow(d,(660,195),(735,280),teal)
arrow(d,(660,355),(735,355),orange)
arrow(d,(1110,285),(1210,225),teal)
arrow(d,(1110,385),(1210,450),gray)
arrow(d,(520,605),(735,425),teal)
arrow(d,(1025,605),(1030,440),orange)
text(d,(800,735),"O sensor inicializa h; cada comando u gera uma nova amostra e uma resposta TCP.",25,color=gray)
if not (OUT/"fluxo-node-red.png").exists():
    im.save(OUT/"fluxo-node-red.png")
