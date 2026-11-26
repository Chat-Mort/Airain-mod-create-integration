# Maquette : Table du carreleur (onglets Création / Sols / Murs / Plafonds) et fenêtre d'aperçu du carton
import sys
sys.path.insert(0, '/home/claude/travail/lot11'); sys.path.insert(0, '/home/claude/travail/lot9')
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from carton import carton, hx
S = 3
B = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/block/'
FT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 8 * S - 1)
FTB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 8 * S - 1)
ARD, ARD2, CREUX = (54, 58, 68), (47, 51, 60), (30, 33, 40)
ROUGE, ROUGE_S, ROUGE_C = (175, 29, 37), (110, 15, 22), (214, 80, 70)
OR, OR_S = (225, 186, 110), (138, 94, 46)
BLANC = (235, 230, 220)
def tex(n): return Image.open(B + n + '.png').convert('RGBA').crop((0, 0, 16, 16))
class Ecran:
    def __init__(s, w, h):
        s.im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def R(s, x, y, w, h, c): s.d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=c)
    def panneau(s, x, y, w, h):
        s.R(x, y, w, h, ROUGE_S); s.R(x + 1, y + 1, w - 2, h - 2, ROUGE); s.R(x + 2, y + 2, w - 4, h - 4, ARD)
        for yy in range(y + 4, y + h - 3, 3): s.d.line([(x + 3) * S, yy * S, (x + w - 3) * S, yy * S], fill=ARD2, width=1)
        for (cx, cy) in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)): s.R(cx, cy, 1, 1, ROUGE_C)
    def case(s, x, y, n=18):
        s.R(x, y, n, n, ROUGE); s.R(x + 1, y + 1, n - 2, n - 2, ROUGE_S); s.R(x + 2, y + 2, n - 4, n - 4, CREUX)
    def creux(s, x, y, w, h, bord=ROUGE):
        s.R(x, y, w, h, bord); s.R(x + 1, y + 1, w - 2, h - 2, CREUX)
    def objet(s, img, x, y, k=1):
        s.im.alpha_composite(img.resize((16 * S * k, 16 * S * k), Image.NEAREST), (x * S, y * S))
    def texte(s, t, x, y, c=BLANC, gras=False): s.d.text((x * S, y * S), t, font=FTB if gras else FT, fill=c)
    def bouton(s, t, x, y, w, h=12, actif=False):
        s.R(x, y, w, h, OR_S); s.R(x, y, w - 1, h - 1, OR if actif else (190, 150, 90)); s.R(x + 1, y + 1, w - 3, h - 3, (240, 205, 130) if actif else (205, 170, 105))
        tw = s.d.textlength(t, font=FT) / S; s.texte(t, x + (w - tw) / 2, y + 1.5, (60, 30, 10))
    def onglet(s, x, y, icone, actif):
        h = 24 if actif else 21
        s.R(x, y + (0 if actif else 3), 26, h, ROUGE_S); s.R(x + 1, y + 1 + (0 if actif else 3), 24, h - 1, ROUGE if actif else (120, 30, 34))
        s.R(x + 2, y + 2 + (0 if actif else 3), 22, h - 2, ARD if actif else (44, 47, 56))
        s.objet(icone, x + 5, y + 5 + (0 if actif else 2))
    def inventaire(s, x, y):
        for r in range(3):
            for c in range(9): s.case(x + c * 18, y + r * 18)
        for c in range(9): s.case(x + c * 18, y + 58)

def motif_grille(n, f):
    """Aperçu vu du dessus : n x n blocs, f(x, z) -> texture."""
    im = Image.new('RGBA', (n * 16, n * 16))
    for z in range(n):
        for x in range(n): im.alpha_composite(f(x, z), (x * 16, z * 16))
    return im

# icônes d'onglets (16 x 16)
def ic_creation():
    im = carton().resize((16, 16), Image.NEAREST); return im
def ic_sol():
    im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im)
    for z in range(4):
        for x in range(4): d.rectangle([x * 4, z * 4 + 2, x * 4 + 3, z * 4 + 5], fill=(232, 228, 220, 255) if (x + z) % 2 else (44, 42, 48, 255))
    return im.crop((0, 2, 16, 18)).resize((16, 16))
def ic_mur():
    im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im)
    for r in range(4):
        dec = 0 if r % 2 else 4
        for c in range(-1, 3):
            x0 = c * 8 + dec; d.rectangle([x0 + 1, r * 4 + 1, x0 + 7, r * 4 + 3], fill=(178, 92, 60, 255))
    return im
def ic_plafond():
    im = Image.new('RGBA', (16, 16)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 15, 15], fill=(120, 84, 50, 255))
    for (x, y) in ((1, 1), (9, 1), (1, 9), (9, 9)): d.rectangle([x, y, x + 5, y + 5], fill=(225, 186, 110, 255)); d.rectangle([x + 1, y + 1, x + 4, y + 4], fill=(190, 140, 80, 255))
    return im
ICONES = [ic_creation(), ic_sol(), ic_mur(), ic_plafond()]
