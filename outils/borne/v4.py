import sys, math, random; sys.path.insert(0, '.')
exec(open('v3.py').read().split('# --- Écho : autel-lutrin')[0])
def F(V): return {(x, y, -z): c for (x, y, z), c in V.items()}
def rouage(V, cx, cy, z0, z1, r, c, dents=8, trou=0.8):
    for X in range(round((cx - r - 1.2) * R), round((cx + r + 1.2) * R)):
        for Y in range(round((cy - r - 1.2) * R), round((cy + r + 1.2) * R)):
            x, y = X / R + .25 - cx, Y / R + .25 - cy; d = math.hypot(x, y); a = math.atan2(y, x)
            if trou < d <= r or (d <= r + 1 and math.cos(a * dents) > 0.5):
                for Z in range(round(z0 * R), round(z1 * R)): V[(X, Y, Z)] = c
def rouageX(V, cy, cz, x0, x1, r, c, dents=8):
    for Y in range(round((cy - r - 1.2) * R), round((cy + r + 1.2) * R)):
        for Z in range(round((cz - r - 1.2) * R), round((cz + r + 1.2) * R)):
            y, z = Y / R + .25 - cy, Z / R + .25 - cz; d = math.hypot(y, z); a = math.atan2(z, y)
            if 0.6 < d <= r or (d <= r + 1 and math.cos(a * dents) > 0.5):
                for X in range(round(x0 * R), round(x1 * R)): V[(X, Y, Z)] = c
# --- A : machine différentielle (colonnes de roues chiffrées, manivelle, cadre de laiton)
def babbage():
    V = {}
    bx(V, 1, 0, 3, 15, 2, 13, IRON2); bx(V, 1, 2, 3, 2, 26, 4, BRASS); bx(V, 14, 2, 3, 15, 26, 4, BRASS)
    bx(V, 1, 2, 12, 2, 26, 13, BRASS); bx(V, 14, 2, 12, 15, 26, 13, BRASS); bx(V, 1, 26, 3, 15, 28, 13, BRASS)
    for c, x in enumerate((4.5, 8, 11.5)):
        for k in range(6):
            y = 4 + k * 3.5
            cylY(V, x, 8, 2.6, y, y + 1.6, GOLD if (k + c) % 2 else COPPER)
            bx(V, x - 0.4, y + 0.3, 5.2, x + 0.4, y + 1.3, 5.5, INK, 0)
        cylY(V, x, 8, 0.6, 2, 26, IRON)
    rouageX(V, 14, 8, 15, 16, 3, GOLD2); bx(V, 16, 13.5, 7.5, 17, 14.5, 8.5, IRON); bx(V, 16, 13.5, 8, 17, 18, 9, IRON); bx(V, 15.5, 17.5, 8, 17.5, 19, 9, RED)  # manivelle
    return V
# --- B : métier à cartes perforées (rouleau de cartes, aiguilles, roue, pupitre)
def jacquard():
    V = {}
    bx(V, 1, 0, 2, 15, 10, 14, WH); bx(V, 1, 10, 1, 15, 11, 15, GOLD)
    bx(V, 2, 11, 9, 14, 22, 13, IRON2)                                                     # corps de la machine
    for k in range(10):                                                                   # cartes perforées en chaîne
        z = 8.5 - k * 0.7; y = 22 - k * 1.1
        bx(V, 3, y, z, 13, y + 0.5, z + 0.7, PAPER, 2)
        for h in range(4): bx(V, 4 + h * 2.4, y + 0.5, z + 0.2, 4.6 + h * 2.4, y + 0.55, z + 0.5, INK, 0) if (k + h) % 2 else None
    cylY(V, 8, 11, 0, 0, 0, IRON)
    rouageX(V, 22, 11, 14, 15, 3.5, GOLD2, 10); rouageX(V, 22, 11, 1, 2, 3.5, GOLD2, 10)
    for k in range(5): bx(V, 3.5 + k * 2, 11, 7.5, 4.2 + k * 2, 14, 8.2, GOLD)            # aiguilles
    bx(V, 6, 22, 10, 10, 30, 12, BRASS); bx(V, 6.5, 22, 10.5, 9.5, 30, 11.5, GLASS)        # tube
    anneau(V, 12.5, 16, 8.6, 9, 0, 1.6, WH); anneau(V, 12.5, 16, 8.6, 9, 1.3, 1.8, GOLD2)  # manomètre
    return V
# --- C : machine à écrire impériale (feuille, rouages apparents, manomètre, tube pneumatique)
def machine2():
    V = {}
    bx(V, 1, 0, 2, 15, 9, 14, WH); bx(V, 1, 9, 1, 15, 10, 15, GOLD); bx(V, 2, 1, 1.6, 14, 8, 2, GOLD2, 3)
    bx(V, 2, 10, 4, 14, 13, 13, IRON2); bx(V, 3, 13, 8, 13, 16, 13, IRON2)
    for r, y in enumerate((10.5, 11.5, 12.5)):
        for k in range(6): bx(V, 3 + k * 1.8, y + 0.5, 3.2 + r * 1.3, 4.2 + k * 1.8, y + 1, 4.2 + r * 1.3, KEYTOP, 2)
    bx(V, 1, 15, 9, 15, 17, 11, KEY); bx(V, 0, 15.5, 9.5, 1, 16.5, 10.5, GOLD); bx(V, 15, 15.5, 9.5, 16, 16.5, 10.5, GOLD)
    for y in range(32, 46):
        for X in range(8, 24): V[(X, y, 19)] = INK if (y % 3 == 0 and 10 < X < 22) else PAPER
    rouage(V, 4, 15, 12.6, 13.2, 2.2, GOLD, 8); rouage(V, 7.5, 16.5, 12.6, 13.2, 1.6, COPPER, 6)   # rouages à l'arrière
    anneau(V, 13, 13.5, 3.6, 4, 0, 1.4, WH); anneau(V, 13, 13.5, 3.6, 4, 1.1, 1.6, GOLD2); bx(V, 12.9, 13.4, 3.4, 13.3, 14.4, 3.6, RED, 0)  # manomètre
    bx(V, 12, 13, 11, 15, 30, 14, GOLD2); bx(V, 12.5, 13, 11.5, 14.5, 30, 13.5, GLASS); bx(V, 11.5, 29, 10.5, 15.5, 31, 14.5, GOLD)  # tube
    bx(V, 0, 5, 7, 1, 6, 8, IRON); bx(V, -1, 5, 7, 0, 9, 8, IRON); bx(V, -1.5, 9, 6.5, 0.5, 10, 8.5, RED)   # levier d'envoi
    return V
L = [("A · Machine différentielle", babbage), ("B · Métier à cartes perforées", jacquard), ("C · Machine à écrire impériale", machine2)]
from PIL import Image, ImageDraw, ImageFont
out = Image.new('RGB', (3 * 320, 380), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
for i, (t, fn) in enumerate(L):
    im = rendu(F(fn()), T=4); im.thumbnail((300, 330)); x = i * 320 + 10
    out.paste(im, (x + (300 - im.width) // 2, 40 + (330 - im.height))); d.text((x, 8), t, fill=(230, 220, 200), font=f)
out.save('apercu_bornes_v4.png'); print('ok')
