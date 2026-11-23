# Icônes de Create les plus vues, retracées à 48 px (règle du lot 5a : même dessin, traits nets, sans demi-teinte).
# Les autres icônes de la planche gardent leurs pixels d'origine, agrandis au pixel près.
import json, math, sys
from PIL import Image, ImageDraw
SRC = '/tmp/src5/create/src/main/resources/assets/create/textures/gui/icons.png'
POS = json.load(open('/tmp/l5b/icons_pos.json'))
K = 8
BL = (230, 230, 230, 255)
def calque(): m = Image.new('L', (48 * K, 48 * K)); return m, ImageDraw.Draw(m)
def P(pts): return [(x * K, y * K) for x, y in pts]
def plein(m): return m.resize((48, 48), Image.BOX).point(lambda v: 255 if v >= 128 else 0)
def trait(d, pts, w): d.line(P(pts), fill=255, width=int(w * K), joint='curve')
def rect(d, x0, y0, x1, y1, v=255): d.rectangle([x0 * K, y0 * K, x1 * K - 1, y1 * K - 1], fill=v)
def tri(d, pts, v=255): d.polygon(P(pts), fill=v)
def chevron(d, cx, cy, vers_bas, w=14, h=8, ep=7):
    s = 1 if vers_bas else -1
    tri(d, [(cx - w, cy - s * h / 2), (cx, cy + s * h / 2), (cx + w, cy - s * h / 2), (cx + w, cy - s * h / 2 - s * ep), (cx, cy + s * h / 2 - s * ep * 1.25), (cx - w, cy - s * h / 2 - s * ep)])
def fleche(d, x0, y0, x1, y1, ep=4, tete=8):
    a = math.atan2(y1 - y0, x1 - x0); bx, by = x1 - tete * math.cos(a), y1 - tete * math.sin(a)
    trait(d, [(x0, y0), (bx, by)], ep)
    n = (-math.sin(a), math.cos(a))
    tri(d, [(x1, y1), (bx + n[0] * tete * 0.7, by + n[1] * tete * 0.7), (bx - n[0] * tete * 0.7, by - n[1] * tete * 0.7)])

def confirm(d): trait(d, [(7, 26), (18, 37), (41, 14)], 7)
def trash(d):
    rect(d, 18, 5, 30, 9); rect(d, 9, 9, 39, 14); rect(d, 12, 16, 36, 43)
    for x in (18, 27): rect(d, x, 20, x + 3, 39, 0)
def add(d): rect(d, 21, 6, 27, 42); rect(d, 6, 21, 42, 27)
def grille(d):
    for j in range(3):
        for i in range(3): rect(d, 10 + 10 * i, 10 + 10 * j, 17 + 10 * i, 17 + 10 * j)
def deplacer(d):
    rect(d, 15, 15, 33, 33); rect(d, 19, 19, 29, 29, 0)
    tri(d, [(24, 3), (17, 11), (31, 11)]); tri(d, [(24, 45), (17, 37), (31, 37)]); tri(d, [(3, 24), (11, 17), (11, 31)]); tri(d, [(45, 24), (37, 17), (37, 31)])
def boite(d):
    rect(d, 5, 12, 29, 38); rect(d, 9, 16, 25, 34, 0); rect(d, 13, 12, 21, 20)       # caisse et sa bande
def envoi_reception(d):
    boite(d); fleche(d, 19, 27, 43, 27, 4, 9); fleche(d, 43, 14, 25, 14, 4, 0.01) if False else None
    fleche(d, 44, 15, 32, 15, 4, 8)
def envoi(d): boite(d); fleche(d, 19, 27, 43, 27, 4, 9)
def pile(d):
    for (y0, y1) in ((5, 15), (18, 28), (31, 42)): rect(d, 5, y0, 20, y1); rect(d, 10, y0, 14, y0 + 3, 0)
def partielle(d): pile(d); trait(d, [(25, 26), (31, 32), (43, 16)], 5)
def complete(d):
    pile(d)
    for j in range(5):
        for i in range(4):
            if (i + j) % 2 == 0: rect(d, 26 + 4 * i, 14 + 5 * j, 30 + 4 * i, 19 + 5 * j)
def prio_tb(d): chevron(d, 24, 16, True); chevron(d, 24, 30, True)
def prio_b(d): rect(d, 10, 11, 38, 16); chevron(d, 24, 29, True)
def prio_h(d): rect(d, 10, 32, 38, 37); chevron(d, 24, 19, False)
def prio_th(d): chevron(d, 24, 18, False); chevron(d, 24, 32, False)
def feuille(d):
    tri(d, [(8, 5), (32, 5), (41, 14), (41, 43), (8, 43)]); tri(d, [(32, 5), (32, 14), (41, 14)], 0)
    trait(d, [(32, 5), (32, 14), (41, 14)], 2)
def liste_blanche(d):
    feuille(d); m2, d2 = calque(); trait(d2, [(14, 25), (21, 33), (34, 18)], 5); return m2
def liste_noire(d):
    feuille(d); m2, d2 = calque(); trait(d2, [(15, 17), (33, 37)], 5); trait(d2, [(33, 17), (15, 37)], 5); return m2
def epee(d, x=0, y=0):
    trait(d, [(17 + x, 31 + y), (40 + x, 8 + y)], 6)
    trait(d, [(12 + x, 26 + y), (22 + x, 36 + y)], 4); trait(d, [(13 + x, 35 + y), (7 + x, 41 + y)], 4)
def ignore_nbt(d): epee(d)
def respect_nbt(d):
    epee(d, -3, -3); rect(d, 25, 25, 45, 43); 
    m2, d2 = calque(); rect(d2, 29, 30, 41, 32); rect(d2, 29, 35, 41, 37); return m2
def fleche_ronde(d, sens):
    # anneau ouvert en haut, tête de flèche au bout (sens horaire ou anti-horaire)
    m, dd = d
    dd.arc([8 * K, 8 * K, 40 * K, 40 * K], 300 if sens > 0 else 240 - 360 + 360, 240 if sens > 0 else 300, fill=255, width=7 * K)
def _anneau(d, debut, fin, sens):
    # anneau ouvert (angles PIL, sens horaire à l'écran), tête de flèche au bout, dans le sens du mouvement
    cx, cy, r = 24, 26, 13
    d.arc([(cx - r - 3.5) * K, (cy - r - 3.5) * K, (cx + r + 3.5) * K, (cy + r + 3.5) * K], debut, fin, fill=255, width=7 * K)
    a = math.radians(fin if sens > 0 else debut)
    ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
    tx, ty = (-math.sin(a), math.cos(a)) if sens > 0 else (math.sin(a), -math.cos(a))
    nx, ny = -ty, tx
    tri(d, [(ex + tx * 9, ey + ty * 9), (ex + nx * 8, ey + ny * 8), (ex - nx * 8, ey - ny * 8)])
def refresh(d): _anneau(d, 300, 200 + 360, 1)
def rotation(d): _anneau(d, 340, 240 + 360, -1)
ICONES = {'I_CONFIRM': confirm, 'I_TRASH': trash, 'I_ADD': add, 'I_3x3': grille, 'I_MOVE_GAUGE': deplacer,
          'I_SEND_AND_RECEIVE': envoi_reception, 'I_SEND_ONLY': envoi, 'I_PARTIAL_REQUESTS': partielle, 'I_FULL_REQUESTS': complete,
          'I_PRIORITY_VERY_LOW': prio_tb, 'I_PRIORITY_LOW': prio_b, 'I_PRIORITY_HIGH': prio_h, 'I_PRIORITY_VERY_HIGH': prio_th,
          'I_WHITELIST': liste_blanche, 'I_BLACKLIST': liste_noire, 'I_RESPECT_NBT': respect_nbt, 'I_IGNORE_NBT': ignore_nbt,
          'I_REFRESH': refresh, 'I_ROTATE_CCW': rotation}
def icone(nom):
    m, d = calque(); creux = ICONES[nom](d)
    im = Image.new('RGBA', (48, 48)); im.paste(Image.new('RGBA', (48, 48), BL), (0, 0), plein(m))
    if creux is not None: im.paste((0, 0, 0, 0), (0, 0), plein(creux))
    return im
def planche():
    src = Image.open(SRC).convert('RGBA'); out = src.resize((768, 768), Image.NEAREST)
    for n in ICONES:
        x, y = POS[n]; out.paste((0, 0, 0, 0), (x * 48, y * 48, x * 48 + 48, y * 48 + 48)); out.alpha_composite(icone(n), (x * 48, y * 48))
    return out
if __name__ == '__main__':
    planche().save(sys.argv[1] if len(sys.argv) > 1 else '/tmp/l5b/icons_hd.png')
