import sys, math, random; sys.path.insert(0, '../balise7')
from concepts import rendu
from PIL import Image, ImageDraw, ImageFont
random.seed(4); R = 2
def bx(V, x0, y0, z0, x1, y1, z1, c, b=6):
    for X in range(round(x0*R), round(x1*R)):
        for Y in range(round(y0*R), round(y1*R)):
            for Z in range(round(z0*R), round(z1*R)):
                V[(X, Y, Z)] = c if len(c) == 4 else tuple(max(0, min(255, k + random.randint(-b, b))) for k in c)
def cylY(V, cx, cz, r, y0, y1, c):
    for X in range(round((cx-r)*R), round((cx+r)*R)):
        for Z in range(round((cz-r)*R), round((cz+r)*R)):
            if (X/R+.25-cx)**2+(Z/R+.25-cz)**2 <= r*r:
                for Y in range(round(y0*R), round(y1*R)): V[(X,Y,Z)] = c
def anneau(V, cx, cy, z0, z1, r0, r1, c):
    for X in range(round((cx-r1-1)*R), round((cx+r1+1)*R)):
        for Y in range(round((cy-r1-1)*R), round((cy+r1+1)*R)):
            d = math.hypot(X/R+.25-cx, Y/R+.25-cy)
            if r0 <= d <= r1:
                for Z in range(round(z0*R), round(z1*R)): V[(X,Y,Z)] = c
WH, GOLD, GOLD2, RED, IRON, IRON2, GLASS, BRASS, COPPER, WOOD, PAPER = (236,234,224),(232,192,72),(180,135,40),(150,26,32),(80,82,90),(55,56,62),(150,200,215,1),(200,150,60),(190,110,75),(110,74,42),(240,236,220)
NOIR, NOIR2, VIO, LAV, PALE = (24,20,34),(44,36,62),(96,58,156),(186,156,255,1),(232,218,255,1)
# --- Empire A : pupitre télégraphique (bureau, téléscripteur sous cloche, bande de papier)
def emp_pupitre():
    V = {}
    bx(V, 1, 0, 3, 15, 11, 13, WH); bx(V, 1, 11, 2, 15, 12, 14, GOLD)                 # bureau
    bx(V, 2, 1, 2.5, 14, 10, 3, GOLD2, 3); bx(V, 3, 2, 2.4, 13, 9, 2.6, WH)
    bx(V, 7, 5, 2.2, 9, 6, 2.6, GOLD)                                                 # poignée tiroir
    cylY(V, 8, 8, 3.5, 12, 13, IRON); cylY(V, 8, 8, 3, 13, 18, GLASS); cylY(V, 8, 8, 1.5, 18, 19, GOLD)  # cloche
    bx(V, 6, 13, 6, 10, 15, 10, BRASS); anneau(V, 8, 15.5, 7.5, 8.5, 0.5, 1.6, GOLD2)   # mécanisme
    for i in range(6): bx(V, 7.5, 11 - i*0.5, 2 - i*0.4 + 0.4, 8.5, 11.5 - i*0.5, 2.4 - i*0.4 + 0.4, PAPER, 2)  # bande
    bx(V, 12, 12, 10, 14, 13, 12, RED); bx(V, 12.6, 13, 10.6, 13.4, 17, 11.4, IRON); bx(V, 12, 17, 10, 14, 18, 12, RED)  # levier
    bx(V, 2, 12, 9, 5, 28, 12, GOLD2); bx(V, 2.5, 12, 9.5, 4.5, 28, 11.5, GLASS)     # tube pneumatique
    bx(V, 1.5, 27, 8.5, 5.5, 29, 12.5, GOLD)
    return V
# --- Empire B : colonne à cadrans (manomètres, rouages, guichet à capsules)
def emp_colonne():
    V = {}
    bx(V, 2, 0, 2, 14, 3, 14, IRON2); bx(V, 3, 3, 3, 13, 26, 13, BRASS); bx(V, 2, 26, 2, 14, 28, 14, IRON2)
    for y in (8, 15, 22):                                                                    # cadrans
        anneau(V, 8, y, 2.2, 3, 0, 2.6, WH); anneau(V, 8, y, 2.2, 3, 2.2, 2.8, IRON2); bx(V, 7.8, y, 2, 8.3, y + 2, 2.3, RED, 0)
    bx(V, 5, 4, 2.4, 11, 6, 3, IRON2); bx(V, 6, 4.5, 2.2, 10, 5.5, 2.4, (20,20,20))         # guichet à capsules
    anneau(V, 3, 18, 6, 7, 1.2, 2.6, IRON); anneau(V, 13, 12, 9, 10, 1.2, 2.6, IRON)        # rouages latéraux
    cylY(V, 8, 8, 1.2, 28, 31, COPPER); cylY(V, 8, 8, 2, 31, 32, COPPER)                     # cheminée
    return V
# --- Empire C : guichet-cabine (cabine étroite, auvent rouge, hublot)
def emp_cabine():
    V = {}
    bx(V, 1, 0, 3, 15, 2, 15, GOLD2); bx(V, 2, 2, 4, 14, 26, 14, WH)
    bx(V, 1, 26, 2, 15, 27, 15, GOLD); bx(V, 0, 22, 1, 16, 23, 5, RED); bx(V, 0, 23, 2, 16, 24, 5, RED)   # auvent
    anneau(V, 8, 15, 3.4, 4.2, 0, 3.6, GLASS); anneau(V, 8, 15, 3.4, 4.2, 3.2, 4.2, GOLD)    # hublot
    bx(V, 4, 8, 3, 12, 9, 4.2, GOLD); bx(V, 5, 9, 3.4, 11, 10, 4, IRON2)                      # comptoir
    bx(V, 5, 4, 3.6, 11, 7, 4, RED)
    bx(V, 6, 27, 6, 10, 30, 10, GOLD2); bx(V, 7, 30, 7, 9, 31, 9, RED)                        # lanterne
    return V
# --- Écho A : autel de résonance (piédestal bas, anneau flottant, grimoire ouvert)
def echo_autel():
    V = {}
    bx(V, 2, 0, 2, 14, 2, 14, VIO); bx(V, 4, 2, 4, 12, 10, 12, NOIR); bx(V, 3, 10, 3, 13, 11, 13, VIO)
    bx(V, 4, 11, 5, 12, 12, 11, NOIR2); bx(V, 4.5, 12, 5.5, 7.8, 12.5, 10.5, PALE); bx(V, 8.2, 12, 5.5, 11.5, 12.5, 10.5, PALE)  # grimoire
    for i in range(4): bx(V, 5 + i*0.6, 12.5, 6.5 + i, 7.5, 12.6, 6.7 + i, VIO, 0)
    anneau(V, 8, 21, 7.5, 8.5, 4, 5, LAV); bx(V, 7, 20, 7, 9, 22, 9, PALE)                   # anneau + cristal
    for y in (4, 7): bx(V, 5, y, 3.5, 11, y + 1, 4, LAV)
    return V
# --- Écho B : grand diapason (socle, diapason, orbe entre les branches)
def echo_diapason():
    V = {}
    bx(V, 3, 0, 3, 13, 3, 13, NOIR); bx(V, 4, 3, 4, 12, 4, 12, VIO)
    bx(V, 7, 4, 7, 9, 12, 9, NOIR2)
    bx(V, 4, 12, 7, 12, 14, 9, NOIR2); bx(V, 4, 14, 7, 6, 28, 9, NOIR2); bx(V, 10, 14, 7, 12, 28, 9, NOIR2)
    bx(V, 4, 27, 7, 6, 28, 9, LAV); bx(V, 10, 27, 7, 12, 28, 9, LAV)
    for X in range(round(6.5*R), round(9.5*R)):
        for Y in range(round(18.5*R), round(21.5*R)):
            for Z in range(round(6.5*R), round(9.5*R)):
                if (X/R-8)**2 + (Y/R-20)**2 + (Z/R-8)**2 <= 2.1: V[(X,Y,Z)] = PALE
    return V
# --- Écho C : miroir arcanique (cadre ovale debout, vitre violette lumineuse)
def echo_miroir():
    V = {}
    bx(V, 2, 0, 5, 14, 2, 11, NOIR); bx(V, 7, 2, 7, 9, 4, 9, NOIR2)
    for X in range(round(1*R), round(15*R)):
        for Y in range(round(4*R), round(31*R)):
            u, v = (X/R+.25-8)/6.6, (Y/R+.25-17.5)/13
            d = u*u + v*v
            for Z in range(round(7*R), round(9*R)):
                if d <= 1 and d > 0.78: V[(X,Y,Z)] = VIO if (Y//3) % 2 else NOIR2
                elif d <= 0.78 and Z == round(8*R): V[(X,Y,Z)] = (150, 110, 230, 1) if (X+Y) % 5 else PALE
    return V
def F(V): return {(x, y, -z): c for (x, y, z), c in V.items()}
L = [("Empire A · Pupitre télégraphique", emp_pupitre), ("Empire B · Colonne à cadrans", emp_colonne), ("Empire C · Guichet-cabine", emp_cabine),
     ("Écho A · Autel de résonance", echo_autel), ("Écho B · Grand diapason", echo_diapason), ("Écho C · Miroir arcanique", echo_miroir)]
out = Image.new('RGB', (3 * 330, 2 * 340), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
for i, (t, fn) in enumerate(L):
    im = rendu(F(fn()), T=4); im.thumbnail((310, 290)); x = (i % 3) * 330 + 10; y = (i // 3) * 340 + 8
    out.paste(im, (x + (310 - im.width) // 2, y + 32 + (290 - im.height))); d.text((x, y), t, fill=(230, 220, 200), font=f)
out.save('apercu_bornes_v2.png'); print('ok')
