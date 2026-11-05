"""Ornements steampunk de l'interface : boutons en conduite de cuivre avec demi-roues aux bouts, cadres de fenêtres en tuyau, roues aux coins."""
import json, os, math
from PIL import Image
CU = [(250, 196, 140), (222, 146, 88), (186, 108, 58), (138, 74, 38), (92, 46, 22)]      # cuivre, du reflet à l'ombre
LA = [(255, 236, 160), (236, 196, 100), (200, 150, 62), (150, 104, 38), (96, 62, 22)]     # laiton
NOIR = (22, 12, 6)
def demi_roue(im, cx, cy, r, couleurs, cote):
    """Roue dentée coupée par le bord du bouton : on n'en voit qu'une part, comme si elle tournait derrière."""
    px = im.load(); occ = set()
    for y in range(im.height):
        for x in range(im.width):
            dx, dy = x + .5 - cx, y + .5 - cy
            d = math.hypot(dx, dy); a = math.atan2(dy, dx)
            dent = math.cos(8 * a + 0.4) > 0.15
            if d < r - 2.4 or (d < r and dent):
                occ.add((x, y))
                if d < 2.4: px[x, y] = NOIR + (255,); continue
                c = couleurs[1] if dy < -3 else couleurs[2] if dy < 3 else couleurs[3]
                if d < 3.6: c = couleurs[0]
                px[x, y] = c + (255,)
    for (x, y) in list(occ):                                             # détourage sombre
        for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + i, y + j)
            if q not in occ and 0 <= q[0] < im.width and 0 <= q[1] < im.height: px[q] = NOIR + (255,)
def bouton(etat):
    W, H = 200, 20
    plaque = {"normal": [(124, 84, 44), (110, 72, 36), (98, 64, 30)], "survol": [(170, 122, 58), (152, 106, 48), (138, 94, 40)],
              "off": [(58, 44, 34), (52, 40, 30), (46, 36, 28)]}[etat]
    tube = {"normal": CU, "survol": LA, "off": [(110, 96, 86), (92, 80, 72), (76, 66, 60), (60, 52, 46), (40, 34, 30)]}[etat]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = im.load()
    for y in range(H):
        for x in range(W):
            k = (0, 1, 1, 2, 1, 0, 1, 2, 2, 1, 0, 1, 2, 1, 1, 0, 1, 2, 1, 0)[y]   # stries horizontales du métal brossé
            if (x * 7 + y * 13) % 29 == 0: k = max(0, k - 1)
            px[x, y] = plaque[k] + (255,)
    for x in range(W):                                                    # conduite en haut et en bas (3 px)
        for i, c in enumerate((tube[0], tube[1], tube[3])):
            px[x, i] = c + (255,)
        for i, c in enumerate((tube[1], tube[2], tube[4])):
            px[x, H - 3 + i] = c + (255,)
        if x % 20 in (0, 1) and 12 <= x < W - 12:                         # brides
            for y in (0, 1, 2, H - 3, H - 2, H - 1): px[x, y] = (tube[0] if x % 20 == 0 else tube[3]) + (255,)
    for y in range(H):                                                    # cadre sombre
        px[0, y] = px[W - 1, y] = NOIR + (255,)
    for x in range(W): px[x, 0] = px[x, H - 1] = NOIR + (255,)
    # demi-roues aux deux bouts, comme si une grande roue tournait derrière le bouton
    rc = {"normal": LA, "survol": LA, "off": tube}[etat]
    demi_roue(im, 1.5, 10, 9.5, rc, "g"); demi_roue(im, W - 1.5, 10, 9.5, rc, "d")
    for y in range(H): px[0, y] = px[W - 1, y] = NOIR + (255,)
    return im
def mcmeta_bouton():
    return {"gui": {"scaling": {"type": "nine_slice", "width": 200, "height": 20,
                                "border": {"left": 10, "right": 10, "top": 3, "bottom": 3}}}}
ROUE8 = ["...##...", ".######.", ".##..##.", "###..###", "###..###", ".##..##.", ".######.", "...##..."]
def cadre_fenetre(im):
    """Remplace le liseré clair et l'ombre du bord du panneau par un tuyau de cuivre, et pose une roue à chaque coin."""
    px = im.load(); w, h = im.size
    # bornes du panneau principal (en haut à gauche de la texture)
    xs = [x for x in range(w) if px[x, 4][3] > 0]; ys = [y for y in range(h) if px[4, y][3] > 0]
    if not xs or not ys: return
    x1 = max(x for x in xs if all(px[i, 4][3] for i in range(4, x + 1))); y1 = max(y for y in ys if all(px[4, i][3] for i in range(4, y + 1)))
    if x1 < 60 or y1 < 60: return
    for y in range(0, y1 + 1):
        for x in range(0, x1 + 1):
            if not px[x, y][3]: continue
            d = min(x, y, x1 - x, y1 - y)
            if d in (1, 2, 3):
                c = CU[{1: 1, 2: 2, 3: 3}[d]]
                long = x if min(y, y1 - y) == d else y
                if long % 16 in (0, 1) and 8 < long < (x1 if min(y, y1 - y) == d else y1) - 8:
                    c = LA[1] if long % 16 == 0 else LA[3]                # brides de laiton
                px[x, y] = c + (255,)
    # quart de grande roue à chaque coin, comme si elle tournait derrière le cadre ; elle s'arrête avant les cases
    for (cx, cy) in ((0.5, 0.5), (x1 + 0.5, 0.5), (0.5, y1 + 0.5), (x1 + 0.5, y1 + 0.5)):
        occ = set()
        for y in range(max(0, int(cy) - 11), min(h, int(cy) + 12)):
            for x in range(max(0, int(cx) - 11), min(w, int(cx) + 12)):
                if not (0 <= x <= x1 and 0 <= y <= y1): continue
                dx, dy = x + .5 - cx, y + .5 - cy; d = math.hypot(dx, dy); a = math.atan2(dy, dx)
                dent = math.cos(10 * a) > 0.1
                if d < 7.4 or (d < 9.6 and dent):
                    occ.add((x, y))
                    c = LA[1] if d < 3.5 else LA[2] if d < 6 else LA[3]
                    if 3.5 <= d < 4.6: c = LA[4]
                    px[x, y] = c + (255,)
        for (x, y) in list(occ):
            for (i, j) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + i, y + j)
                if q not in occ and 0 <= q[0] <= x1 and 0 <= q[1] <= y1: px[q] = NOIR + (255,)
