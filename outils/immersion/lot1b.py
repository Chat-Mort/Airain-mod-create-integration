"""Lot 1, reprise : cinq tableaux enrichis en détails."""
from outils5 import *
S = 128

def rivets(d, pts, c=LAITON[0], hl=LAITON[5]):
    for (x, y) in pts: d.point((x, y), fill=c); d.point((x - 1, y - 1), fill=hl)

def briques(d, x0, y0, x1, y1, c, joint, rnd, h=4, w=8, var=10):
    for j, y in enumerate(range(int(y0), int(y1), h)):
        off = (j % 2)*w//2
        for x in range(int(x0) - off, int(x1), w):
            v = rnd.randint(-var, var); d.rectangle([max(x0, x), y, min(x1, x + w - 2), min(y1, y + h - 2)], fill=(c[0] + v, c[1] + v, c[2] + v))
    for y in range(int(y0), int(y1), h): d.line([(x0, y + h - 1), (x1, y + h - 1)], fill=joint)

# ------------------------------------------------------------ TRANSFER : autel du souvenir
def skull_and_roses():
    rnd = random.Random(7)
    im = Image.new("RGB", (S, S), (20, 16, 18)); d = ImageDraw.Draw(im)
    briques(d, 0, 0, S, 92, (40, 32, 32), (22, 18, 18), rnd)                   # mur de briques
    poly_degrade(im, [(30, 0), (98, 0), (94, 70), (64, 80), (34, 70)], (130, 26, 22), (70, 12, 12))   # bannière de l'Empire
    d = ImageDraw.Draw(im)
    for x in range(34, 96, 6): d.line([(x, 2), (x + (x - 64)*0.05, 70)], fill=(100, 18, 16))           # plis
    d.rectangle([28, 0, 100, 4], fill=LAITON[2]); d.line([(28, 4), (100, 4)], fill=LAITON[0])
    d.line([(34, 70), (64, 80), (94, 70)], fill=OR[2])
    im = halo(im, 64, 30, 60, (60, 40, 30), 0.9); d = ImageDraw.Draw(im)
    poly_degrade(im, [(10, 92), (118, 92), (122, 100), (6, 100)], (120, 110, 100), (80, 72, 66))     # autel de pierre
    poly_degrade(im, [(14, 100), (114, 100), (114, 124), (14, 124)], (90, 82, 76), (50, 44, 40))
    d = ImageDraw.Draw(im)
    for x in range(20, 112, 18): d.line([(x, 102), (x, 122)], fill=(60, 54, 50))
    d.rectangle([40, 106, 88, 118], fill=LAITON[1]); d.rectangle([41, 107, 87, 117], fill=LAITON[3])
    texte(d, 48, 110, "TRANSFER", ENCRE); rivets(d, [(43, 109), (85, 109), (43, 115), (85, 115)])
    cx, cy = 64, 56                                                            # casque
    poly_degrade(im, [(cx - 24, cy + 30), (cx - 28, cy - 4), (cx - 16, cy - 24), (cx + 16, cy - 24), (cx + 28, cy - 4), (cx + 24, cy + 30)], FER[4], FER[0], axe="x")
    d = ImageDraw.Draw(im)
    d.line([(cx - 16, cy - 24), (cx + 16, cy - 24)], fill=FER[4])
    d.polygon([(cx - 3, cy - 30), (cx + 3, cy - 30), (cx + 2, cy - 4), (cx - 2, cy - 4)], fill=LAITON[3])   # crête
    d.line([(cx - 3, cy - 30), (cx - 2, cy - 4)], fill=LAITON[5])
    for y in (cy - 14, cy + 12): d.line([(cx - 26, y), (cx + 26, y)], fill=FER[1])   # jointures de plaques
    rivets(d, [(cx - 22 + k*8, cy - 11) for k in range(6)] + [(cx - 22 + k*8, cy + 15) for k in range(6)], FER[0], FER[4])
    d.rectangle([cx - 22, cy - 6, cx + 22, cy + 2], fill=(10, 8, 10)); d.line([(cx - 22, cy - 6), (cx + 22, cy - 6)], fill=FER[0])
    d.point((cx - 12, cy - 2), fill=(90, 30, 20)); d.point((cx + 12, cy - 2), fill=(70, 20, 14))     # braises mourantes
    for k in range(6): d.line([(cx - 12, cy + 18 + k*2), (cx + 12, cy + 18 + k*2)], fill=FER[1])
    d.line([(cx + 6, cy - 24), (cx + 10, cy - 12), (cx + 7, cy - 8)], fill=(20, 16, 16))               # fêlure et bosse
    d.arc([cx - 20, cy + 2, cx - 10, cy + 12], 200, 340, fill=FER[4])
    d.line([(cx - 24, cy - 2), (cx - 14, cy - 20)], fill=FER[5] if len(FER) > 5 else (210, 210, 220))   # reflet
    for k, x in enumerate((18, 110)):                                         # bougies
        d.rectangle([x - 3, 76, x + 3, 92], fill=(226, 214, 186)); d.line([(x - 3, 76), (x - 3, 92)], fill=(250, 240, 220))
        d.line([(x, 72), (x, 76)], fill=ENCRE); d.ellipse([x - 2, 66, x + 2, 73], fill=(255, 200, 90)); d.point((x, 69), fill=(255, 250, 220))
        d.rectangle([x - 5, 90, x + 5, 92], fill=LAITON[2])
        im = halo(im, x, 70, 22, (110, 70, 20)); d = ImageDraw.Draw(im)
    for k in range(8):                                                         # roses de cuivre détaillées
        x = 16 + k*13.5 + rnd.randint(-2, 2); y = 88 + (k % 2)*3
        d.line([(x, y), (x + rnd.randint(-4, 4), 96)], fill=(70, 96, 54))
        d.polygon([(x + 1, y + 4), (x + 7, y + 2), (x + 3, y + 7)], fill=(80, 116, 64))
        d.ellipse([x - 5, y - 5, x + 5, y + 4], fill=CUIVRE[1])
        d.ellipse([x - 4, y - 5, x + 4, y + 2], fill=CUIVRE[2]); d.arc([x - 3, y - 4, x + 3, y + 1], 30, 300, fill=CUIVRE[3])
        d.point((x, y - 2), fill=CUIVRE[0]); d.point((x - 2, y - 4), fill=(250, 200, 160))
    grain(im, 7, 3); d = ImageDraw.Draw(im); cadre(d, S, S, ENCRE, FER[1], ENCRE)
    return im

# ------------------------------------------------------------ Salle des capsules
def capsule(im, x, gy, cw, ch, fade, rnd, eveillee=False):
    d = ImageDraw.Draw(im)
    c1, c2 = mix(LAITON[4], (16, 12, 18), fade), mix(LAITON[0], (16, 12, 18), fade)
    poly_degrade(im, [(x, gy - ch + cw/2), (x + cw, gy - ch + cw/2), (x + cw, gy), (x, gy)], c1, c2, axe="x"); d = ImageDraw.Draw(im)
    ellipse_degrade(im, [x, gy - ch, x + cw, gy - ch + cw], c1, mix(c1, c2, 0.5)); d = ImageDraw.Draw(im)
    vit = [x + cw*0.18, gy - ch + cw*0.18, x + cw*0.82, gy - ch + cw*1.05]
    if eveillee: ellipse_degrade(im, vit, (240, 214, 255), (120, 60, 190))
    else: ellipse_degrade(im, vit, mix((80, 50, 110), (16, 12, 18), fade), mix((30, 20, 46), (16, 12, 18), fade))
    d = ImageDraw.Draw(im); d.ellipse(vit, outline=mix(LAITON[0], (16, 12, 18), fade))
    if cw > 10:
        fx, fy = (vit[0] + vit[2])/2, (vit[1] + vit[3])/2                       # visage endormi derrière la vitre
        tc = (255, 250, 255) if eveillee else mix((130, 100, 160), (16, 12, 18), fade)
        d.rectangle([fx - cw*0.14, fy - cw*0.1, fx + cw*0.14, fy + cw*0.16], outline=tc)
        d.line([(fx - cw*0.1, fy), (fx - cw*0.03, fy)], fill=tc); d.line([(fx + cw*0.03, fy), (fx + cw*0.1, fy)], fill=tc)
        d.line([(x + cw*0.2, vit[1] + 2), (x + cw*0.3, vit[1] + 1)], fill=mix((255, 255, 255), (16, 12, 18), fade))
        for k in range(3): d.line([(x + 2, gy - ch*0.45 + k*3), (x + cw - 3, gy - ch*0.45 + k*3)], fill=c2)   # cerclages
        d.rectangle([x + cw*0.3, gy - ch*0.32, x + cw*0.7, gy - ch*0.2], fill=mix(ENCRE, (16, 12, 18), fade))   # plaque
        lum = (120, 230, 140) if eveillee or rnd.random() < 0.5 else (230, 80, 60)
        d.point((x + cw*0.5, gy - ch*0.12), fill=mix(lum, (16, 12, 18), fade))
    return ImageDraw.Draw(im)

def stage():
    rnd = random.Random(8)
    im = degrade(S, S, [(14, 10, 18), (30, 22, 30), (12, 10, 14)]); d = ImageDraw.Draw(im); vx, vy = 64, 50
    for k in range(5):                                                         # arches du plafond
        t = k/5; w = 64*(1 - t*0.8); y = vy - 46*(1 - t*0.85)
        d.arc([vx - w, y, vx + w, y + w*1.2], 180, 360, fill=mix(LAITON[1], (14, 10, 18), t*0.8), width=2)
        d.line([(vx, y), (vx, y + 4)], fill=(60, 50, 50)); d.ellipse([vx - 2, y + 4, vx + 2, y + 7], fill=mix((255, 200, 120), (14, 10, 18), t*0.6))
    for k in range(-8, 9): d.line([(vx, vy), (vx + k*24, S)], fill=(36, 28, 34))   # dallage
    for j in range(7): y = vy + (S - vy)*(j/7)**1.8; d.line([(0, y), (S, y)], fill=(36, 28, 34))
    for k in (-1, 1):                                                          # conduites au sol
        d.line([(vx + k*3, vy + 2), (vx + k*14, S)], fill=CUIVRE[1], width=2); d.line([(vx + k*3, vy + 2), (vx + k*14, S)], fill=CUIVRE[3])
    for rang in range(7, 0, -1):
        t = rang/7; ch = 74*(1.1 - t*0.85); cw = ch*0.42; gy = vy + (S - vy)*(1 - t)**1.3*0.85 + 6
        for s in (-1, 1):
            x = vx + s*(12 + 54*(1 - t)) - cw/2
            d = capsule(im, x, gy, cw, ch, t*0.7, rnd)
            d.line([(x + cw/2, gy - ch), (x + cw/2, max(0, gy - ch - 8*(1 - t) - 3))], fill=mix(CUIVRE[1], (14, 10, 18), t*0.6))
    im = halo(im, 64, 74, 64, (90, 50, 140)); d = ImageDraw.Draw(im)
    d = capsule(im, 47, 120, 34, 72, 0, rnd, eveillee=True)
    d.ellipse([46, 116, 82, 124], fill=LAITON[1])
    for k in range(5): d.point((50 + k*7, 120), fill=LAITON[5])
    im = halo(im, 64, 66, 24, (120, 80, 170))
    d = ImageDraw.Draw(im)
    for k in range(10): x = rnd.uniform(44, 84); y = rnd.uniform(40, 110); d.point((x, y), fill=(230, 200, 255))   # poussière d'Écho
    for k in range(3): d.arc([36 + k*6, 108 - k*4, 52 + k*6, 118 - k*4], 180, 320, fill=(120, 110, 120))            # vapeur
    grain(im, 8, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# ------------------------------------------------------------ Observatoire du bout du monde
def void():
    rnd = random.Random(10)
    im = degrade(S, S, [(6, 4, 16), (24, 10, 44), (50, 20, 70)]); d = ImageDraw.Draw(im)
    for _ in range(300): d.point((rnd.randrange(S), rnd.randrange(96)), fill=rnd.choice(((255, 255, 255), (200, 180, 255), (150, 130, 220), (90, 80, 140))))
    for (x, y) in ((14, 14), (40, 30), (118, 70)): d.point((x, y), fill=(255, 255, 255)); [d.point(p, fill=(150, 140, 200)) for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))]
    L = Image.new("RGB", (S, S)); dl = ImageDraw.Draw(L); pts = []
    for k in range(13):
        y = 6 + k*5; w = 7*math.sin(math.pi*k/12); x = 98 + rnd.uniform(-3, 3); pts.append((x, y, w))
    for (x, y, w) in pts: dl.ellipse([x - w*2, y - 5, x + w*2, y + 5], fill=(70, 20, 100))
    im = ImageChops.add(im, L.filter(ImageFilter.GaussianBlur(5))); d = ImageDraw.Draw(im)
    gauche = [(x - w, y) for (x, y, w) in pts]; droite = [(x + w, y) for (x, y, w) in pts][::-1]
    d.polygon(gauche + droite, fill=(8, 0, 14)); d.line(gauche, fill=(230, 180, 255)); d.line(droite[::-1], fill=(190, 120, 240))
    for _ in range(14): x, y, w = rnd.choice(pts); d.point((x + rnd.uniform(-w, w)*0.6, y), fill=(255, 240, 255))
    for _ in range(18): x, y, w = rnd.choice(pts); d.point((x + rnd.uniform(-18, 18), y + rnd.uniform(-6, 30)), fill=(180, 110, 230))   # particules aspirées
    for (ix, iy, iw) in ((16, 56, 20), (82, 74, 14)):                          # îles flottantes lointaines
        d.polygon([(ix, iy), (ix + iw, iy), (ix + iw*0.6, iy + iw*0.5), (ix + iw*0.3, iy + iw*0.4)], fill=(60, 56, 64)); d.line([(ix, iy), (ix + iw, iy)], fill=(130, 124, 100))
        d.rectangle([ix + iw*0.4, iy - iw*0.9, ix + iw*0.6, iy], fill=(30, 20, 40))   # pilier d'obsidienne
    poly_degrade(im, [(0, 102), (24, 92), (60, 96), (96, 88), (S, 98), (S, S), (0, S)], (150, 146, 106), (60, 56, 40)); d = ImageDraw.Draw(im)
    for _ in range(26):                                                        # cratères de pierre de l'End
        x, y, r = rnd.randrange(S), rnd.randrange(100, S), rnd.randint(1, 3); d.ellipse([x - r, y - r*0.5, x + r, y + r*0.5], fill=(110, 106, 76)); d.arc([x - r, y - r*0.5, x + r, y + r*0.5], 0, 180, fill=(170, 166, 120))
    for (px, ph) in ((104, 22), (116, 14), (8, 16)):                           # plantes de chorus
        for k in range(ph): d.point((px + (k//5 % 2)*2, 96 - k), fill=(130, 90, 140))
        d.ellipse([px - 2, 96 - ph - 3, px + 3, 96 - ph + 2], fill=(200, 160, 210))
    poly_degrade(im, [(20, 102), (20, 70), (64, 70), (64, 102)], (110, 104, 120), (40, 36, 46), axe="x"); d = ImageDraw.Draw(im)   # bâtiment
    for y in range(72, 102, 4): d.line([(20, y), (64, y)], fill=(50, 46, 56))
    for x in range(22, 64, 7): d.line([(x, 70), (x, 102)], fill=(60, 56, 66))
    ellipse_degrade(im, [17, 46, 67, 94], (150, 140, 170), (50, 44, 60)); d = ImageDraw.Draw(im)   # dôme
    for k in range(1, 6): a = math.pi*(k/6); d.arc([42 - 25*math.cos(a)*0 - 25, 46, 42 + 25, 94], 180, 360, fill=(60, 54, 70)) if False else d.line([(42 + 25*math.cos(a), 70 - 24*math.sin(a)), (42 + 25*math.cos(a)*0.2, 47)], fill=(80, 72, 92))
    d.arc([17, 46, 67, 94], 190, 260, fill=(200, 190, 220))
    d.rectangle([38, 46, 46, 72], fill=(16, 10, 22)); d.line([(38, 46), (38, 72)], fill=(90, 80, 100))
    poly_degrade(im, [(40, 64), (46, 58), (86, 26), (80, 21)], LAITON[4], LAITON[1]); d = ImageDraw.Draw(im)   # lunette
    for t in (0.3, 0.6): d.line([(40 + 40*t, 64 - 40*t), (46 + 40*t, 58 - 36*t)], fill=LAITON[0])
    d.ellipse([78, 19, 87, 28], fill=LAITON[0]); d.ellipse([80, 21, 85, 26], fill=(60, 40, 80)); d.point((81, 22), fill=(220, 200, 255))
    for k in range(4):
        d.rectangle([25 + k*10, 84, 30 + k*10, 92], fill=(250, 200, 110)); d.line([(27 + k*10, 84), (27 + k*10, 92)], fill=(140, 90, 40)); d.line([(25 + k*10, 88), (30 + k*10, 88)], fill=(140, 90, 40))
    im = halo(im, 42, 88, 22, (90, 60, 20)); d = ImageDraw.Draw(im)
    d.rectangle([38, 94, 46, 102], fill=(40, 26, 20)); d.point((44, 98), fill=LAITON[4])                  # porte
    for k in range(5): d.line([(46 + k*2, 102 + k), (52 + k*2, 102 + k)], fill=(120, 116, 90))           # marches
    d.line([(64, 70), (64, 58)], fill=FER[3]); d.line([(60, 58), (68, 58)], fill=FER[3]); d.point((64, 57), fill=(255, 80, 80))   # antenne
    grain(im, 9, 3); d = ImageDraw.Draw(im); cadre(d, S, S, (30, 12, 50), (130, 70, 190), (60, 26, 96))
    return im

# ------------------------------------------------------------ Cloche de plongée et épave
def water():
    rnd = random.Random(11)
    im = degrade(S, S, [(80, 160, 176), (24, 84, 112), (8, 30, 50)], 0.8); d = ImageDraw.Draw(im)
    L = Image.new("RGB", (S, S)); dl = ImageDraw.Draw(L)
    for k in range(7): x = 4 + k*20; dl.polygon([(x, 0), (x + 8, 0), (x + 34, S), (x + 16, S)], fill=(26, 40, 40))
    im = ImageChops.add(im, L.filter(ImageFilter.GaussianBlur(3))); d = ImageDraw.Draw(im)
    for x in range(0, S, 4): d.line([(x, 2 + int(math.sin(x*0.3)*1.5)), (x + 3, 2)], fill=(210, 245, 245))
    d.polygon([(0, 84), (10, 70), (30, 68), (44, 80), (40, 100), (0, 104)], fill=(24, 54, 70))           # épave en fond
    d.line([(16, 70), (8, 40)], fill=(24, 54, 70), width=2); d.line([(8, 46), (20, 50)], fill=(24, 54, 70))
    for x in range(8, 40, 6): d.ellipse([x, 84, x + 3, 87], fill=(16, 40, 54))
    d.polygon([(100, 90), (112, 62), (124, 90)], fill=(24, 58, 74))                                      # rocher
    poly_degrade(im, [(0, 112), (30, 104), (70, 110), (S, 102), (S, S), (0, S)], (110, 104, 80), (40, 40, 34)); d = ImageDraw.Draw(im)
    for _ in range(40): x, y = rnd.randrange(S), rnd.randrange(108, S); d.point((x, y), fill=rnd.choice(((150, 140, 110), (70, 66, 54))))
    for x in range(0, S, 2):                                                   # caustiques au sol
        if math.sin(x*0.45) + math.sin(x*0.17) > 1.1: d.point((x, 108 + int(math.sin(x*0.3)*2)), fill=(170, 210, 190))
    for (cx_, cc) in ((14, (200, 90, 90)), (108, (220, 140, 80)), (90, (180, 100, 160))):              # coraux
        for k in range(5): a = -math.pi/2 + (k - 2)*0.35; d.line([(cx_, 114), (cx_ + math.cos(a)*9, 114 + math.sin(a)*9)], fill=cc, width=2)
    for k in range(10):
        x = rnd.randrange(S); h = rnd.randint(10, 28)
        for y in range(h): d.point((x + math.sin(y*0.5)*2, S - 6 - y), fill=(50, 130, 70)); d.point((x + 1 + math.sin(y*0.5)*2, S - 6 - y), fill=(30, 90, 50))
    d.line([(64, 0), (64, 30)], fill=(30, 30, 30), width=2); d.line([(70, 0), (74, 34)], fill=(60, 50, 40))    # câble et tuyau d'air
    ellipse_degrade(im, [36, 28, 92, 94], LAITON[4], LAITON[0]); d = ImageDraw.Draw(im)
    for y in (44, 62): d.arc([36, 28, 92, 94], 200, 340, fill=LAITON[1]) if False else d.line([(40 + abs(61 - y)*0.2, y), (88 - abs(61 - y)*0.2, y)], fill=LAITON[1])
    rivets(d, [(42 + k*7, 46) for k in range(7)] + [(40 + k*7, 64) for k in range(8)])
    d.arc([40, 30, 88, 92], 200, 250, fill=LAITON[5])
    d.ellipse([60, 26, 68, 32], fill=LAITON[2]); d.rectangle([62, 22, 66, 26], fill=LAITON[1])
    d.rectangle([32, 74, 96, 88], fill=LAITON[1]); d.line([(32, 74), (96, 74)], fill=LAITON[4]); d.line([(32, 88), (96, 88)], fill=LAITON[0])
    for k in range(9): d.ellipse([34 + k*7, 79, 38 + k*7, 83], fill=LAITON[0]); d.point((35 + k*7, 80), fill=LAITON[5])
    for (x, y, r) in ((50, 56, 7), (78, 56, 7), (64, 44, 6)):                  # hublots à boulons
        d.ellipse([x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=LAITON[0])
        for k in range(6): a = k*math.pi/3; d.point((x + math.cos(a)*(r + 1), y + math.sin(a)*(r + 1)), fill=LAITON[5])
        ellipse_degrade(im, [x - r, y - r, x + r, y + r], (255, 236, 160), (230, 150, 50)); d = ImageDraw.Draw(im)
        d.point((x - r*0.4, y - r*0.5), fill=(255, 255, 240))
    d.ellipse([46, 52, 54, 60], fill=(60, 40, 30)); d.ellipse([47, 52, 53, 58], fill=LAITON[4]); d.rectangle([48, 54, 52, 56], fill=(80, 120, 140))   # scaphandrier au hublot
    im = halo(im, 64, 54, 34, (90, 70, 20), 0.8); d = ImageDraw.Draw(im)
    d.line([(96, 82), (110, 80), (116, 88)], fill=(70, 60, 50), width=2)       # bras de prélèvement
    d.polygon([(114, 88), (120, 86), (118, 92)], fill=FER[2])
    for k in range(16):
        x = 60 + rnd.randint(-6, 12); y = 26 - k*2 + rnd.randint(-1, 1)
        if y > 3: r = rnd.choice((1, 1, 2)); d.ellipse([x, y, x + r, y + r], outline=(200, 236, 244))
    for k in range(9):                                                          # banc de poissons
        x, y = 100 + rnd.randint(-14, 14), 30 + rnd.randint(-8, 8)
        d.line([(x - 2, y), (x + 2, y)], fill=(220, 226, 200)); d.point((x + 3, y - 1), fill=(220, 226, 200)); d.point((x + 3, y + 1), fill=(220, 226, 200))
    grain(im, 12, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# ------------------------------------------------------------ Station météo sous l'orage
def wind():
    rnd = random.Random(12)
    im = degrade(S, S, [(26, 30, 42), (56, 60, 76), (100, 98, 108)]); d = ImageDraw.Draw(im)
    for k in range(9):
        x = rnd.randint(-30, 110); y = rnd.randint(-6, 34); w = rnd.randint(40, 70)
        for j in range(4): xx = x + j*w/4; d.ellipse([xx, y - 4 + (j % 2)*5, xx + w/2, y + 18], fill=mix((30, 34, 46), (74, 78, 92), (j + k % 3)/6))
    pts = [(98, 0), (92, 16), (100, 20), (88, 46), (96, 48), (84, 74)]; br = [(92, 16), (84, 26), (86, 32), (78, 40)]
    L = Image.new("RGB", (S, S)); dl = ImageDraw.Draw(L); dl.line(pts, fill=(160, 170, 230), width=6); dl.line(br, fill=(100, 110, 170), width=4)
    im = ImageChops.add(im, L.filter(ImageFilter.GaussianBlur(3))); d = ImageDraw.Draw(im); d.line(pts, fill=(250, 250, 255)); d.line(br, fill=(200, 205, 240))
    L = Image.new("RGB", (S, S)); dl = ImageDraw.Draw(L)                       # faisceau du phare
    dl.polygon([(28, 44), (S, 20), (S, 44)], fill=(60, 54, 30)); im = ImageChops.add(im, L.filter(ImageFilter.GaussianBlur(2))); d = ImageDraw.Draw(im)
    poly_degrade(im, [(64, S), (60, 96), (S, 104), (S, S)], (44, 64, 94), (16, 24, 40)); d = ImageDraw.Draw(im)   # mer agitée
    for k in range(14):
        x, y = rnd.randint(56, 124), rnd.randint(100, 124); d.arc([x, y, x + 10, y + 5], 180, 360, fill=(170, 190, 210)); d.point((x + 8, y), fill=(230, 240, 250))
    d.polygon([(96, 112), (104, 100), (112, 112)], fill=(30, 30, 34)); d.polygon([(110, 118), (116, 108), (124, 118)], fill=(30, 30, 34))   # récifs
    for k in range(12): x, y = 98 + rnd.randint(-8, 26), 98 + rnd.randint(-8, 4); d.point((x, y), fill=(230, 240, 250))                      # embruns
    poly_degrade(im, [(0, 84), (30, 74), (54, 76), (68, 96), (64, S), (0, S)], (86, 80, 70), (26, 24, 22)); d = ImageDraw.Draw(im)       # falaise
    for y in range(90, S, 6): d.line([(0, y), (60 + (y - 90)*0.1, y + 2)], fill=(50, 46, 40))                                            # strates
    for x in range(0, 56, 3): h = rnd.randint(2, 5); d.line([(x, 80 - x*0.15), (x + 2, 80 - x*0.15 - h)], fill=(70, 96, 50))           # herbe couchée
    d.rectangle([36, 66, 54, 80], fill=(70, 62, 56)); d.polygon([(34, 66), (56, 66), (45, 58)], fill=(60, 34, 30))                       # maisonnette
    d.rectangle([40, 70, 44, 74], fill=(255, 200, 110)); d.rectangle([48, 72, 52, 80], fill=(40, 28, 22)); d.rectangle([50, 56, 52, 62], fill=(50, 40, 36))
    for x in range(4, 34, 5): d.line([(x, 82 - x*0.15), (x, 78 - x*0.15)], fill=(90, 70, 50))                                             # clôture
    d.line([(4, 79), (34, 75)], fill=(90, 70, 50))
    poly_degrade(im, [(20, 80), (32, 80), (30, 32), (22, 32)], (190, 186, 180), (100, 96, 94), axe="x"); d = ImageDraw.Draw(im)       # tour
    for y in range(34, 80, 4): d.line([(21, y), (31, y)], fill=(130, 126, 120))
    for y in (46, 60): d.rectangle([20, y, 32, y + 3], fill=ROUGE)
    d.rectangle([17, 30, 35, 32], fill=FER[1]); d.line([(17, 26), (35, 26)], fill=FER[3])
    for x in range(17, 36, 3): d.line([(x, 26), (x, 30)], fill=FER[3])                                                                     # rambarde
    d.rectangle([21, 18, 31, 26], fill=(255, 220, 130)); d.line([(26, 18), (26, 26)], fill=FER[1]); d.polygon([(19, 18), (33, 18), (26, 12)], fill=CUIVRE[1])
    im = halo(im, 26, 22, 16, (140, 110, 40)); d = ImageDraw.Draw(im)
    d.line([(26, 12), (26, 4)], fill=FER[4])
    for a in (0.2, 2.3, 4.4): x, y = 26 + math.cos(a)*7, 5 + math.sin(a)*2; d.line([(26, 5), (x, y)], fill=FER[4]); d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=CUIVRE[2])
    for _ in range(190):
        x, y = rnd.randrange(-10, S), rnd.randrange(16, S); d.line([(x, y), (x + 2, y + 5)], fill=(116, 122, 140))
    dirigeable(d, 74, 60, 11)
    d.line([(70, 68), (66, 76)], fill=(60, 50, 50))                            # ancre traînante dans la tempête
    grain(im, 13, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

LOT1B = {"skull_and_roses": skull_and_roses, "stage": stage, "void": void, "water": water, "wind": wind}
if __name__ == "__main__":
    ims = []
    for n, f in LOT1B.items(): im = f(); im.save(f"v5/{n}.png"); ims.append(im)
    apercu(ims, "/home/claude/apercus/v5_lot1b.png", z=3)
