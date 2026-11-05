"""Pistes pour une interface v2 : plaque de titre rivetée, cases plus creusées, variante bronze sombre."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/accueil")
from PIL import Image
from police import texte
import gui
P = "/home/claude/empire-airain-pack/kubejs/assets/minecraft/textures/gui/"
coffre = Image.open(P + "container/generic_54.png").convert("RGBA").crop((0, 0, 176, 222))
def plaque_titre(im, w=96):
    gui.plaque(im, 5, 3, w, 11)
def creuser(im):
    """Cases : fond plus sombre et bord intérieur d'ombre, pour qu'elles se lisent comme des alvéoles."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and 100 < r < 135 and 70 < g < 95 and b < 55:          # intérieur des cases
                px[x, y] = (int(r * 0.72), int(g * 0.7), int(b * 0.66), 255)
    return im
def bronze(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and r > 140 and g > 100 and b < 120 and r - b > 60:     # le laiton clair du panneau → bronze patiné
                l = (r + g + b) / 3
                px[x, y] = (int(l * 0.78 + 20), int(l * 0.6 + 8), int(l * 0.38), 255)
    return im
A = coffre.copy(); B = creuser(coffre.copy()); plaque_titre(B); C = bronze(creuser(coffre.copy())); plaque_titre(C)
cells = []
for im, nom in ((A, "Actuel"), (B, "A · plaque + cases creusées"), (C, "B · bronze patiné")):
    c = im.copy(); texte(c, 9 if nom == "Actuel" else 12, 6, "Coffre", (58, 34, 14) if nom != "B · bronze patiné" else (40, 20, 8))
    texte(c, 8, 128, "Inventaire", (58, 34, 14))
    cells.append((c, nom))
from PIL import ImageDraw, ImageFont
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
pl = Image.new("RGBA", (176 * 3 * 3 + 60, 222 * 3 + 40), (30, 30, 34, 255)); d = ImageDraw.Draw(pl)
for i, (c, n) in enumerate(cells):
    pl.alpha_composite(c.resize((528, 666), Image.NEAREST), (i * 548, 36)); d.text((i * 548 + 264, 8), n, font=f, fill=(240, 205, 110), anchor="mt")
pl.save("/home/claude/apercus/gui_v2_pistes.png"); print("ok")
