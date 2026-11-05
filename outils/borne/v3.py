import sys, math, random; sys.path.insert(0, '.')
exec(open('v2.py').read().split('# --- Empire A')[0])
from concepts import rendu
INK = (30, 26, 24); KEY = (40, 40, 44); KEYTOP = (220, 214, 196)
def incline(V, x0, x1, ybas, zbas, longueur, epais, angle, coul):
    """plaque inclinée (pente vers l'avant = z min) : de (ybas, zbas) en remontant vers l'arrière."""
    a = math.radians(angle)
    for i in range(round(longueur * R)):
        t = i / R
        y = ybas + math.sin(a) * t; z = zbas + math.cos(a) * t
        for e in range(round(epais * R)):
            for X in range(round(x0 * R), round(x1 * R)):
                V[(X, round(y * R + e), round(z * R))] = coul(t, X / R) if callable(coul) else coul
# --- Écho : autel-lutrin (pupitre incliné, grimoire, anneau)
def echo_autel():
    V = {}
    bx(V, 2, 0, 2, 14, 2, 14, VIO); bx(V, 5, 2, 5, 11, 10, 11, NOIR); bx(V, 4, 10, 4, 12, 11, 12, VIO)
    for y in (4, 7): bx(V, 6, y, 4.5, 10, y + 1, 5, LAV)
    incline(V, 2, 14, 11, 2.5, 11, 1, 30, NOIR2)                                   # pupitre incliné
    incline(V, 3, 7.7, 12, 3.2, 9, 0.5, 30, PALE); incline(V, 8.3, 13, 12, 3.2, 9, 0.5, 30, PALE)   # pages
    incline(V, 7.7, 8.3, 11.8, 3.2, 9, 0.6, 30, VIO)
    anneau(V, 8, 24, 11.5, 12.5, 3.5, 4.5, LAV); bx(V, 7.2, 23.2, 11.2, 8.8, 24.8, 12.8, PALE)
    return V
# --- Empire 1 : lutrin du commissaire (pupitre incliné en laiton, grand registre rouge, tube pneumatique)
def emp_lutrin():
    V = {}
    bx(V, 2, 0, 2, 14, 2, 14, GOLD2); bx(V, 6, 2, 6, 10, 10, 10, WH); bx(V, 5, 4, 5, 11, 5, 11, GOLD); bx(V, 4, 10, 4, 12, 11, 12, GOLD)
    incline(V, 1, 15, 11, 2.5, 11, 1, 30, BRASS)
    incline(V, 2, 7.7, 12, 3.2, 9.5, 0.5, 30, lambda t, x: INK if int(t * 2) % 3 == 0 and 3 < x < 7 else PAPER)
    incline(V, 8.3, 14, 12, 3.2, 9.5, 0.5, 30, lambda t, x: INK if int(t * 2) % 3 == 0 and 9 < x < 13 else PAPER)
    incline(V, 7.7, 8.3, 11.8, 3.2, 9.5, 0.6, 30, RED); incline(V, 1.5, 2, 11.8, 3, 10, 0.8, 30, RED); incline(V, 14, 14.5, 11.8, 3, 10, 0.8, 30, RED)
    bx(V, 12, 11, 12, 15, 28, 15, GOLD2); bx(V, 12.5, 11, 12.5, 14.5, 28, 14.5, GLASS); bx(V, 11.5, 27, 11.5, 15.5, 29, 15.5, GOLD)
    return V
# --- Empire 2 : machine à écrire de commande (bureau, grande machine, feuille qui sort)
def emp_machine():
    V = {}
    bx(V, 1, 0, 2, 15, 9, 14, WH); bx(V, 1, 9, 1, 15, 10, 15, GOLD)
    bx(V, 2, 10, 4, 14, 13, 13, IRON2); bx(V, 3, 13, 8, 13, 16, 13, IRON2)
    for r, y in enumerate((10.5, 11.5, 12.5)):
        for k in range(6): bx(V, 3 + k * 1.8, y + 0.5, 3.2 + r * 1.3, 4.2 + k * 1.8, y + 1, 4.2 + r * 1.3, KEYTOP, 2)
    bx(V, 1, 15, 9, 15, 17, 11, KEY); bx(V, 0, 15.5, 9.5, 1, 16.5, 10.5, GOLD); bx(V, 15, 15.5, 9.5, 16, 16.5, 10.5, GOLD)   # rouleau
    bx(V, 4, 16, 9.5, 12, 24, 10, lambda: None) if False else None
    for y in range(32, 48):
        for X in range(8, 24): V[(X, y, 19)] = INK if (y % 3 == 0 and 10 < X < 22) else PAPER
    bx(V, 13, 10, 3, 14, 15, 4, RED); bx(V, 12.5, 15, 2.5, 14.5, 16, 4.5, RED)
    return V
# --- Empire 3 : tableau des arrivages (panneau à palettes sur pied de laiton, pupitre en dessous)
def emp_tableau():
    V = {}
    bx(V, 3, 0, 5, 13, 2, 11, IRON2); bx(V, 7, 2, 7, 9, 16, 9, BRASS)
    bx(V, 0, 16, 6, 16, 30, 10, IRON2); bx(V, 0.5, 16.5, 5.5, 15.5, 29.5, 6, (20, 22, 26))
    for r in range(4):
        for k in range(6):
            bx(V, 1.2 + k * 2.4, 17.5 + r * 3, 5, 3.2 + k * 2.4, 19.5 + r * 3, 5.5, (230, 200, 120) if (r + k) % 3 else WH, 3)
    bx(V, 0, 30, 5, 16, 31, 11, GOLD); bx(V, 3, 9, 3, 13, 10, 9, GOLD)
    incline(V, 3, 13, 10, 3, 6, 0.6, 25, BRASS)
    return V
def F(V): return {(x, y, -z): c for (x, y, z), c in V.items()}
L = [("Écho · Autel-lutrin", echo_autel), ("Empire 1 · Lutrin du commissaire", emp_lutrin), ("Empire 2 · Machine à écrire", emp_machine), ("Empire 3 · Tableau des arrivages", emp_tableau)]
from PIL import Image, ImageDraw, ImageFont
out = Image.new('RGB', (4 * 300, 360), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
for i, (t, fn) in enumerate(L):
    im = rendu(F(fn()), T=4); im.thumbnail((280, 310)); x = i * 300 + 10
    out.paste(im, (x + (280 - im.width) // 2, 36 + (310 - im.height))); d.text((x, 8), t, fill=(230, 220, 200), font=f)
out.save('apercu_bornes_v3.png'); print('ok')
