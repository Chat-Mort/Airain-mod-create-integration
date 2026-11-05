from rendu import *
V = [
 ("Potence", "lanternes, franges, fleuron pointe", dict(style=0, fond=0, orn=0, motif="rouage", forme=0, long=1, larg=1, vent=1, franges=1, fleuron=0, double=0, lanternes=1, h=6)),
 ("Vexillum", "2 blocs × 4, lanternes, couronne", dict(style=1, fond=1, orn=1, motif="couronne", forme=2, long=2, larg=3, vent=1, franges=1, fleuron=3, double=0, lanternes=1, h=7)),
 ("Cérémonie double", "mât de 8, bourrasque, rouage", dict(style=2, fond=2, orn=2, motif="ancre", forme=1, long=2, larg=1, vent=2, franges=0, fleuron=2, double=1, lanternes=0, h=8)),
 ("Potence double", "mât de 5, calme, globe", dict(style=0, fond=3, orn=0, motif="eclair", forme=2, long=0, larg=0, vent=0, franges=1, fleuron=1, double=1, lanternes=0, h=5)),
]
S = 5.2; PW, PH = 700, 1120
planche = Image.new("RGBA", (PW * len(V), PH + 70), (40, 42, 48, 255))
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30); f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
except Exception: font = f2 = ImageFont.load_default()
for i, (titre, sous, o) in enumerate(V):
    im = Image.new("RGBA", (PW, PH), (40, 42, 48, 255)); d = ImageDraw.Draw(im)
    dessiner(d, scene(o, VUE), S, PW / 2, PH - 120)
    planche.alpha_composite(im, (i * PW, 0))
    dd = ImageDraw.Draw(planche)
    dd.text((i * PW + PW / 2, PH + 4), titre, font=font, fill=(240, 205, 110), anchor="mt")
    dd.text((i * PW + PW / 2, PH + 40), sous, font=f2, fill=(210, 205, 190), anchor="mt")
planche.save("/home/claude/apercus/grand_etendard.png"); print("ok")
