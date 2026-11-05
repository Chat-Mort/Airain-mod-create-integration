from rendu import *
B = dict(long=1, larg=1, vent=1, franges=0, fleuron=0, double=0, lanternes=0, h=6)
V = [
 ("Grand étendard", "coupé ivoire, motif argent, usée", "g", dict(B, style=0, fond=0, fond2=4, partition=1, orn=0, cmotif=0xD8DCE0, motif="rouage", forme=0, etat=1, franges=1, lanternes=1)),
 ("Grand étendard", "chevron, déchirée, en ruine", "g", dict(B, style=1, fond=3, fond2=0, partition=3, orn=2, motif="rouage_brise", forme=2, etat=2, larg=2, long=2, fleuron=1)),
 ("Bannière murale", "bordure, franges, lanternes, embouts globe", "m", dict(B, murale=True, style=1, fond=1, fond2=4, partition=5, orn=0, motif="couronne", forme=0, larg=2, long=1, franges=1, lanternes=1, fleuron=1, vent=0)),
 ("Bannière murale", "bande, déchirée, embouts rouage", "m", dict(B, murale=True, style=1, fond=5, fond2=3, partition=4, orn=3, motif="fiole", forme=2, larg=0, long=0, etat=2, fleuron=2, vent=0)),
 ("Petit étendard", "parti rouge et noir", "p", dict(B, petit=True, style=0, fond=0, fond2=3, partition=2, orn=0, motif="flamme", forme=0)),
]
S = 5.2; PW, PH = 560, 1000
planche = Image.new("RGBA", (PW * len(V), PH + 70 + 330), (40, 42, 48, 255))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26); f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
dd = ImageDraw.Draw(planche)
for i, (titre, sous, k, o) in enumerate(V):
    im = Image.new("RGBA", (PW, PH), (40, 42, 48, 255)); d = ImageDraw.Draw(im)
    if k == "g": dessiner(d, scene(o, VUE), S, PW / 2, PH - 100)
    elif k == "m": dessiner(d, scene_murale(o, VUE), S * 1.9, PW / 2 + 10, PH / 2 + 40)
    else: dessiner(d, scene_petit(o, VUE), S * 2.1, PW / 2 - 20, PH - 200)
    planche.alpha_composite(im, (i * PW, 0))
    dd.text((i * PW + PW / 2, PH + 4), titre, font=font, fill=(240, 205, 110), anchor="mt")
    dd.text((i * PW + PW / 2, PH + 38), sous, font=f2, fill=(210, 205, 190), anchor="mt")
# bandeau : les 6 partitions et les 3 états, à plat
y0 = PH + 100; noms = ["Uni", "Coupé", "Parti", "Chevron", "Bande", "Bordure", "Neuve", "Usée", "Déchirée"]
for n in range(9):
    o = dict(fond=1, fond2=4, orn=0, motif="ancre", forme=0, partition=n if n < 6 else 1, etat=max(0, n - 6))
    im = toile(o).resize((96, 192), Image.NEAREST)
    x = 60 + n * (PW * len(V) - 120) // 9 + 50
    planche.alpha_composite(im, (x, y0))
    dd.text((x + 48, y0 + 200), noms[n], font=f2, fill=(210, 205, 190), anchor="mt")
planche.save("/home/claude/apercus/bannieres_nouveautes.png"); print("ok")
