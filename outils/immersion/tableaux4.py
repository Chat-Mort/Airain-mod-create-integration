"""Tableaux, troisième version : 64 px par bloc. Six tableaux redessinés pour profiter de la résolution."""
import math, random
from PIL import Image, ImageDraw
from tableaux2 import *

K = 4
SPEC = {  # nom : (largeur, hauteur en blocs, fonction, arguments)
 "alban": (1, 1, "icone", (0,)), "aztec": (1, 1, "icone", (1,)), "aztec2": (1, 1, "icone", (2,)), "bomb": (1, 1, "icone", (3,)),
 "kebab": (1, 1, "icone", (4,)), "meditative": (1, 1, "icone", (5,)), "plant": (1, 1, "icone", (6,)), "wasteland": (1, 1, "icone", (7,)),
 "graham": (1, 2, "plan", ("capsule", "N4")), "prairie_ride": (1, 2, "affiche", ("SERVE",)), "wanderer": (1, 2, "buste", ()),
 "courbet": (2, 1, "scene", ("train", 1)), "creebet": (2, 1, "scene", ("usine", 2)), "pool": (2, 1, "scene", ("navire", 3)),
 "sea": (2, 1, "plan", ("locomotive", "LINE")), "sunset": (2, 1, "scene", ("dirigeable", 4)),
 "baroque": (2, 2, "affiche", ("GLORY",)), "bust": (2, 2, "buste", ()), "earth": (2, 2, "echo", (5,)), "fire": (2, 2, "scene", ("usine", 6)),
 "humble": (2, 2, "plan", ("engrenage", "GEAR")), "match": (2, 2, "engrenages", (7,)), "skull_and_roses": (2, 2, "affiche_sombre", ("TRANSFER",)),
 "stage": (2, 2, "hall", ()), "void": (2, 2, "echo", (8,)), "water": (2, 2, "scene", ("navire", 9)), "wind": (2, 2, "scene", ("dirigeable", 10)),
 "wither": (2, 2, "plan", ("capsule", "PROTO")),
 "bouquet": (3, 3, "engrenages", (11,)), "cavebird": (3, 3, "scene", ("dirigeable", 12)), "cotan": (3, 3, "buste", ()), "endboss": (3, 3, "echo_ames", (13,)),
 "fern": (3, 3, "plan", ("engrenage", "THEORY")), "owlemons": (3, 3, "affiche", ("UNITED",)), "sunflowers": (3, 3, "scene", ("usine", 14)), "tides": (3, 3, "scene", ("navire", 15)),
 "backyard": (3, 4, "affiche", ("THE CORE BEATS",)), "pond": (3, 4, "capsules", ()),
 "changing": (4, 2, "scene", ("train", 16)), "fighters": (4, 2, "scene", ("dirigeable", 17)), "finding": (4, 2, "plan", ("locomotive", "LINE 9")),
 "lowmist": (4, 2, "scene", ("usine", 18)), "passage": (4, 2, "capsules", ()),
 "donkey_kong": (4, 3, "panorama", ()), "skeleton": (4, 3, "engrenages", (20,)),
 "burning_skull": (4, 4, "eveil", ()), "orb": (4, 4, "choeur", ()), "pigscene": (4, 4, "nuages", ()),
 "pointer": (4, 4, "plan_coeur", ()), "unpacked": (4, 4, "affiche", ("EMPEROR",)),
}
NOUVEAUX = ("donkey_kong", "burning_skull", "orb", "pigscene", "pointer", "stage")

def texte2(d, x, y, s, c, z=2):
    for ch in s:
        g = POLICE.get(ch, POLICE[" "])
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == "1": d.rectangle([x + i*z, y + j*z, x + i*z + z - 1, y + j*z + z - 1], fill=c)
        x += 4*z

# ---------------------------------------------------------------- 1. La Cité d'Airain : panorama en trois plans
def panorama(W, H):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); rnd = random.Random(19)
    ciel(d, W, H, rnd)
    d.ellipse([W*0.7, H*0.12, W*0.7 + H*0.22, H*0.34], fill=(252, 214, 130)); d.ellipse([W*0.7 + 4, H*0.12 + 4, W*0.7 + H*0.22 - 4, H*0.34 - 4], fill=(255, 236, 180))
    for plan_, (base, teinte, hmin, hmax, lum) in enumerate(((0.62, (96, 66, 80), 0.08, 0.2, 0.08), (0.74, (60, 42, 54), 0.12, 0.3, 0.18), (0.9, (26, 20, 26), 0.14, 0.38, 0.4))):
        x = 0; b = int(H*base)
        while x < W:
            w = rnd.randint(W//30, W//12); h = int(H*rnd.uniform(hmin, hmax))
            d.rectangle([x, b - h, x + w, b], fill=teinte)
            if rnd.random() < 0.3: d.polygon([(x, b - h), (x + w, b - h), (x + w/2, b - h - w*0.6)], fill=teinte)   # toits
            if rnd.random() < 0.4: d.rectangle([x + w*0.6, b - h - H*0.06, x + w*0.6 + 3, b - h], fill=teinte)
            for yy in range(b - h + 4, b - 2, 6):
                for xx in range(x + 3, x + w - 2, 5):
                    if rnd.random() < lum: d.rectangle([xx, yy, xx + 1, yy + 2], fill=(250, 200, 110))
            x += w + rnd.randint(0, 3)
        d.rectangle([0, b, W, H], fill=teinte)
    tx, tb, th = W*0.4, H*0.9, H*0.7                                           # la grande tour d'horloge
    d.rectangle([tx - 12, tb - th, tx + 12, tb], fill=(20, 16, 22))
    for j in range(int(tb - th), int(tb), 10): d.line([(tx - 12, j), (tx + 12, j)], fill=(40, 30, 36))
    d.ellipse([tx - 11, tb - th + 6, tx + 11, tb - th + 28], fill=CREME, outline=LAITON[2])
    for k in range(12):
        a = 2*math.pi*k/12; d.point((tx + math.cos(a)*9, tb - th + 17 + math.sin(a)*9), fill=ENCRE)
    d.line([(tx, tb - th + 17), (tx, tb - th + 10)], fill=ENCRE); d.line([(tx, tb - th + 17), (tx + 6, tb - th + 17)], fill=ENCRE)
    d.polygon([(tx - 15, tb - th), (tx + 15, tb - th), (tx, tb - th - 26)], fill=CUIVRE[1]); d.line([(tx, tb - th - 26), (tx, tb - th - 34)], fill=LAITON[4])
    by = H*0.8                                                                  # pont ferroviaire et train
    d.rectangle([0, by, W, by + 3], fill=(40, 30, 34))
    for x in range(0, W, 24): d.arc([x, by, x + 24, by + 20], 180, 360, fill=(40, 30, 34))
    for k in range(5):
        wx = W*0.62 + k*16; d.rectangle([wx, by - 9, wx + 14, by - 1], fill=LAQUE_ROUGE[3] if k == 0 else (90, 60, 50))
        for j in range(2): d.rectangle([wx + 3 + j*6, by - 7, wx + 5 + j*6, by - 5], fill=(250, 210, 120))
    for j in range(6):
        r = 3 + j; d.ellipse([W*0.62 - j*10 - r, by - 14 - j*5 - r, W*0.62 - j*10 + r, by - 14 - j*5 + r], fill=mix((210, 200, 196), (140, 110, 120), j/6))
    dirigeable(d, W*0.2, H*0.26, W*0.11); dirigeable(d, W*0.86, H*0.42, W*0.05)
    cadre(d, W, H)
    return im

# ---------------------------------------------------------------- 2. L'Empire s'éveille : l'Empereur se dresse derrière l'emblème
def eveil(W, H):
    im = Image.new("RGB", (W, H), (34, 28, 26)); d = ImageDraw.Draw(im)
    cx, cy = W/2, H*0.5
    for k in range(24):
        a1, a2 = 2*math.pi*k/24, 2*math.pi*(k+0.5)/24; R = W + H
        d.polygon([(cx, cy*0.7), (cx + math.cos(a1)*R, cy*0.7 + math.sin(a1)*R), (cx + math.cos(a2)*R, cy*0.7 + math.sin(a2)*R)], fill=(100, 34, 26))
    s = W*0.46                                                                  # silhouette de l'Empereur
    d.rectangle([cx - s*0.5, H*0.42, cx + s*0.5, H], fill=(14, 10, 12))
    d.rectangle([cx - s*0.82, H*0.4, cx - s*0.5, H*0.62], fill=(14, 10, 12)); d.rectangle([cx + s*0.5, H*0.4, cx + s*0.82, H*0.62], fill=(14, 10, 12))
    d.rectangle([cx - s*0.26, H*0.16, cx + s*0.26, H*0.42], fill=(14, 10, 12))
    for k in range(3): d.polygon([(cx - s*0.26 + k*s*0.26, H*0.16), (cx - s*0.13 + k*s*0.26 - s*0.13, H*0.16), (cx - s*0.13 + k*s*0.26, H*0.07)], fill=(14, 10, 12))
    for k in (-0.11, 0.11):
        d.rectangle([cx + k*s - 6, H*0.27, cx + k*s + 6, H*0.3], fill=(255, 140, 40)); d.rectangle([cx + k*s - 3, H*0.275, cx + k*s + 3, H*0.295], fill=(255, 230, 160))
    for j in range(int(H*0.45), H, 8): d.line([(cx - s*0.5, j), (cx + s*0.5, j)], fill=(30, 22, 24))
    r = W*0.12
    d.ellipse([cx - r*1.4, H*0.66 - r*1.4, cx + r*1.4, H*0.66 + r*1.4], fill=LAITON[1]); d.ellipse([cx - r*1.3, H*0.66 - r*1.3, cx + r*1.3, H*0.66 + r*1.3], fill=ENCRE)
    roue_couronnee(d, cx, H*0.66 + r*0.2, r*0.78)
    d.rectangle([6, H - 26, W - 7, H - 7], fill=ENCRE); texte2(d, (W - len("THE EMPIRE AWAKENS")*8)//2, H - 21, "THE EMPIRE AWAKENS", OR[4])
    cadre(d, W, H, ENCRE, ROUGE2, ENCRE)
    return im

# ---------------------------------------------------------------- 3. Le Chœur : spirale d'Écho, âmes et pylône brisé du Grand Relais
def choeur(W, H):
    im = echo(W, H, 21, ames=False); d = ImageDraw.Draw(im); rnd = random.Random(4)
    for k in range(18):
        a = rnd.uniform(0, 2*math.pi); rr = rnd.uniform(0.25, 0.45)*W; x, y = W/2 + math.cos(a)*rr, H/2 + math.sin(a)*rr
        s = rnd.uniform(3, 6)
        d.ellipse([x - s, y - s*1.3, x + s, y + s*0.4], fill=(222, 196, 255)); d.polygon([(x - s, y), (x + s, y), (x + s*0.3, y + s*2.4), (x - s*0.4, y + s*1.6)], fill=(170, 120, 230))
        d.point((x - s*0.4, y - s*0.5), fill=(60, 20, 90)); d.point((x + s*0.4, y - s*0.5), fill=(60, 20, 90))
    b = H - 10                                                                  # pylône effondré
    d.polygon([(W*0.12, b), (W*0.2, b), (W*0.3, H*0.55), (W*0.26, H*0.53)], fill=(20, 12, 26))
    for t in range(6):
        y = b - t*(b - H*0.55)/6; x = W*0.16 + t*(W*0.12)/6
        d.line([(x - 6, y), (x + 6, y - 10)], fill=(40, 26, 50))
    d.line([(W*0.28, H*0.54), (W*0.42, H*0.62)], fill=(40, 26, 50), width=2)
    d.rectangle([0, b, W, H], fill=(20, 10, 28))
    cadre(d, W, H, (30, 12, 50), (130, 70, 190), (60, 26, 96))
    return im

# ---------------------------------------------------------------- 4. Au-dessus des nuages : flotte au-dessus d'une mer de nuages
def nuages(W, H):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); rnd = random.Random(22)
    for y in range(H): d.line([(0, y), (W, y)], fill=ramp([(30, 40, 90), (90, 100, 160), (230, 170, 130), (250, 210, 160)], (y/H)**1.2))
    for _ in range(140): d.point((rnd.randrange(W), rnd.randrange(int(H*0.3))), fill=(240, 240, 255))
    d.ellipse([W*0.38, H*0.5, W*0.62, H*0.74], fill=(255, 220, 150))
    for couche in range(4):                                                     # mer de nuages
        y0 = H*(0.62 + couche*0.09); c = mix((250, 220, 200), (180, 140, 150), couche/4)
        x = -20
        while x < W + 20:
            r = rnd.randint(12, 28); d.ellipse([x, y0 - r*0.6, x + r*2, y0 + r*0.8], fill=c); x += r*1.3
        d.rectangle([0, y0 + 6, W, H], fill=c)
    dirigeable(d, W*0.45, H*0.3, W*0.22)
    dirigeable(d, W*0.12, H*0.45, W*0.07); dirigeable(d, W*0.84, H*0.18, W*0.06)
    cadre(d, W, H)
    return im

# ---------------------------------------------------------------- 5. Le Cœur d'Airain : plan détaillé avec les quatre fragments
def plan_coeur(W, H):
    im = plan(W, H, "engrenage", ""); d = ImageDraw.Draw(im)
    cx, cy, r = W/2, H*0.45, W*0.3
    T, T2 = TRAIT, (150, 186, 226)
    for k, nom in enumerate(("GEARS", "TIDES", "FORGE", "VOID")):              # les quatre fragments
        a = math.pi/4 + k*math.pi/2; x, y = cx + math.cos(a)*r*1.25, cy + math.sin(a)*r*1.25
        d.rectangle([x - 8, y - 8, x + 8, y + 8], outline=T); d.line([(x, y), (cx + math.cos(a)*r*0.9, cy + math.sin(a)*r*0.9)], fill=T2)
        texte(d, int(x - len(nom)*2), int(y + 11 if y > cy else y - 17), nom, T)
    d.ellipse([cx - r*0.3, cy - r*0.3, cx + r*0.3, cy + r*0.3], outline=T); d.ellipse([cx - r*0.12, cy - r*0.12, cx + r*0.12, cy + r*0.12], fill=T2)
    d.rectangle([W - 108, H - 26, W - 7, H - 7], outline=T); texte2(d, W - 104, H - 21, "AIRAIN CORE", T)
    lignes(d, 10, H - 24, 80, 3, T2, pas=5)
    return im

# ---------------------------------------------------------------- 6. La Salle des capsules en perspective
def hall(W, H):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); rnd = random.Random(9)
    vx, vy = W/2, H*0.42
    for y in range(H): d.line([(0, y), (W, y)], fill=mix((44, 32, 36), (14, 10, 14), abs(y - vy)/H*1.6))
    for k in range(-6, 7):                                                     # dalles du sol en perspective
        d.line([(vx, vy), (vx + k*W*0.18, H)], fill=(60, 44, 40))
    for rang in range(7, 0, -1):                                               # deux rangées de capsules qui fuient
        t = rang/7; ch = H*0.5*(1.05 - t*0.8); cw = ch*0.38; gy = vy + (H - vy)*(1 - t)*0.95
        for cote in (-1, 1):
            x = vx + cote*(W*0.08 + (W*0.42)*(1 - t)) - cw/2
            d.rounded_rectangle([x, gy - ch, x + cw, gy], radius=max(1, int(cw/2)), fill=mix(LAITON[2], (30, 22, 24), t*0.7), outline=LAITON[0])
            d.ellipse([x + cw*0.22, gy - ch*0.86, x + cw*0.78, gy - ch*0.86 + cw*0.56], fill=(50, 30, 76))
            if rnd.random() < 0.3: d.point((x + cw/2, gy - ch*0.86 + cw*0.28), fill=(220, 170, 255))
            d.line([(x + cw/2, gy), (vx, vy + 4)], fill=mix(CUIVRE[1], (30, 22, 24), t*0.5))
    d.ellipse([vx - 4, vy - 4, vx + 4, vy + 4], fill=(170, 110, 240))
    cadre(d, W, H)
    return im

FONCTIONS = {
 "icone": icone, "plan": plan, "affiche": affiche, "buste": buste, "scene": scene, "engrenages": engrenages, "echo": echo,
 "affiche_sombre": lambda W, H, s: affiche(W, H, s, fond=(34, 28, 26), ray=(70, 50, 34), sombre=True),
 "echo_ames": lambda W, H, g: echo(W, H, g, ames=True), "capsules": capsules,
 "hall": hall, "panorama": panorama, "eveil": eveil, "choeur": choeur, "nuages": nuages, "plan_coeur": plan_coeur,
}
def generer(nom):
    w, h, f, args = SPEC[nom]
    W, H = w*16*K, h*16*K
    if f == "icone":
        im = FONCTIONS[f](32, 32, *args); return im.resize((W, H), Image.NEAREST)   # les 1 x 1 restent dessinés en 32 px, agrandis net
    return FONCTIONS[f](W, H, *args)
