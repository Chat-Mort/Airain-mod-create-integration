# Aperçu : la machine de l'Empereur (éteinte, Cœur posé, rallumée) et le résonateur du Grand Relais (Cœur posé, libération)
exec(open('v5.py').read().split('L = [("Empire · A')[0])
RUST, DARK, SOUL, SOUL2 = (96, 70, 52), (40, 40, 46), (120, 230, 240, 1), (200, 250, 255, 1)
DEEP, DEEP2, LODE, LODE2 = (52, 60, 58), (70, 80, 76), (120, 118, 116), (150, 150, 155)
def sphere(V, cx, cy, cz, r, c):
    for X in range(round((cx - r) * R), round((cx + r) * R)):
        for Y in range(round((cy - r) * R), round((cy + r) * R)):
            for Z in range(round((cz - r) * R), round((cz + r) * R)):
                if (X / R + .25 - cx) ** 2 + (Y / R + .25 - cy) ** 2 + (Z / R + .25 - cz) ** 2 <= r * r: V[(X, Y, Z)] = c
def coeur(V, cx, cy, cz, vivant):
    sphere(V, cx, cy, cz, 3.2, (235, 120, 40) if vivant else (110, 60, 40))
    anneau(V, cx, cy, cz - 0.5, cz + 0.5, 3.0, 4.0, GOLD if vivant else GOLD2)
    if vivant: sphere(V, cx, cy, cz - 2.6, 1.4, (255, 230, 150, 1))
def machine(etat):   # 0 éteinte, 1 Cœur posé, 2 rallumée
    V = {}
    metal, laiton = (DARK, RUST) if etat < 2 else (IRON2, BRASS)
    bx(V, -2, 0, -2, 18, 3, 18, metal); bx(V, -1, 3, -1, 17, 4, 17, laiton)            # socle
    cylY(V, 8, 8, 7, 4, 26, metal)                                                       # chambre du Cœur
    for y in (6, 15, 24): cylY(V, 8, 8, 7.4, y, y + 1.2, laiton)
    if etat:                                                                             # niche ouverte : le Cœur y est posé
        for k in [k for k in V if 3 * R <= k[0] < 13 * R and 11 * R <= k[1] < 21 * R and k[2] < 6 * R]: del V[k]
        bx(V, 3, 11, 5, 13, 21, 6, (200, 150, 60) if etat == 2 else RUST)
    else: bx(V, 3, 11, -0.4, 13, 21, 1.2, (60, 70, 80))                                    # volet fermé
    bx(V, 2.5, 10.5, -0.6, 13.5, 11, 1.4, laiton); bx(V, 2.5, 21, -0.6, 13.5, 21.5, 1.4, laiton)
    if etat: coeur(V, 8, 16, 1.5, etat == 2)
    rouageX(V, 15, 8, -2.5, 0, 5.5, laiton); rouageX(V, 15, 8, 16, 18.5, 5.5, laiton)    # rouages latéraux
    for x in (2, 14): cylY(V, x, 12, 1.2, 26, 32, metal); cylY(V, x, 12, 1.6, 31, 32, laiton)   # cheminées
    for k in range(6):                                                                   # fleurons
        a = k * math.pi / 3; bx(V, 8 + 6 * math.cos(a) - .6, 26, 8 + 6 * math.sin(a) - .6, 8 + 6 * math.cos(a) + .6, 29, 8 + 6 * math.sin(a) + .6, GOLD if etat == 2 else GOLD2, 0)
    if etat == 2:
        for k in range(14): bx(V, 1.5 + random.random(), 32 + k * 1.3, 11.5 + random.random(), 2.5 + random.random(), 33 + k * 1.3, 12.5 + random.random(), (235, 235, 235, 1), 0)
    return V
def resonateur(etat):   # 1 Cœur posé, 2 libération
    V = {}
    bx(V, 0, 0, 0, 16, 16, 16, DEEP); bx(V, 1, 15.5, 1, 15, 16, 15, DEEP2, 0)            # ardoise renforcée
    bx(V, 0, 16, 0, 16, 32, 16, LODE); bx(V, 2, 31.5, 2, 14, 32, 14, LODE2, 0); bx(V, 6, 32, 6, 10, 33, 10, IRON2)   # magnétite
    coeur(V, 8, 41, 8, False)
    for k in range(40):                                                                  # âmes
        a = random.random() * 2 * math.pi; r = random.random() * (4 if etat == 2 else 9); h = random.random() * (60 if etat == 2 else 14)
        y = (34 if etat == 2 else 36) + h
        bx(V, 8 + r * math.cos(a), y, 8 + r * math.sin(a), 8.8 + r * math.cos(a), y + 0.8, 8.8 + r * math.sin(a), SOUL if k % 3 else SOUL2, 0)
    if etat == 2: cylY(V, 8, 8, 2.2, 45, 96, (170, 240, 250, 1))
    return V
L = [("Machine éteinte", lambda: machine(0)), ("Cœur posé", lambda: machine(1)), ("Rallumée (fin Empire)", lambda: machine(2)),
     ("Résonateur : Cœur posé", lambda: resonateur(1)), ("Diapason : libération (fin Écho)", lambda: resonateur(2))]
out = Image.new('RGB', (5 * 300, 420), (32, 33, 38)); d = ImageDraw.Draw(out); f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
for i, (t, fn) in enumerate(L):
    im = rendu(F(fn()), T=3); im.thumbnail((280, 370)); x = i * 300 + 10
    out.paste(im, (x + (280 - im.width) // 2, 40 + (370 - im.height))); d.text((x, 8), t, fill=(230, 220, 200), font=f)
out.save('../fin_apercu.png'); print('ok')
