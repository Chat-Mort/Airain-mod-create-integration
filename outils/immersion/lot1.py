"""Lot 1 : les douze tableaux 2 x 2 (128 x 128), un sujet unique chacun."""
from outils5 import *
S = 128

# baroque — affiche « GLORY » : médaille de l'Empire sur rubans, rayons dorés
def baroque():
    im = Image.new("RGB", (S, S), (236, 220, 180)); d = ImageDraw.Draw(im); cx, cy = 64, 52
    for k in range(32):
        a1, a2 = 2*math.pi*k/32, 2*math.pi*(k + 0.5)/32
        d.polygon([(cx, cy), (cx + math.cos(a1)*200, cy + math.sin(a1)*200), (cx + math.cos(a2)*200, cy + math.sin(a2)*200)], fill=(222, 196, 140))
    for c, dx in ((ROUGE, -9), (BLEU_PLAN, 0), (ROUGE, 9)):                    # rubans
        d.polygon([(cx + dx - 6, 20), (cx + dx + 6, 20), (cx + dx + 6, 44), (cx + dx - 6, 44)], fill=c)
    d.polygon([(cx - 15, 12), (cx + 15, 12), (cx + 15, 22), (cx - 15, 22)], fill=OR[2])
    for k in range(8):                                                         # étoile à 8 branches
        a = k*math.pi/4 - math.pi/8; b = a + math.pi/8; c_ = a + math.pi/4
        pts = [(cx, cy + 12), (cx + math.cos(a)*14, cy + 12 + math.sin(a)*14), (cx + math.cos(b)*34, cy + 12 + math.sin(b)*34), (cx + math.cos(c_)*14, cy + 12 + math.sin(c_)*14)]
        poly_degrade(im, pts, OR[4], OR[1])
    d = ImageDraw.Draw(im)
    for k in range(8):
        b = k*math.pi/4; d.line([(cx, cy + 12), (cx + math.cos(b)*34, cy + 12 + math.sin(b)*34)], fill=OR[0])
    d.ellipse([cx - 16, cy - 4, cx + 16, cy + 28], fill=ROUGE2); d.ellipse([cx - 14, cy - 2, cx + 14, cy + 26], fill=ENCRE)
    roue_couronnee(d, cx, cy + 14, 9)
    im = halo(im, cx - 14, cy, 14, (90, 80, 40))
    d = ImageDraw.Draw(im)
    for k in range(5):                                                         # couronne de lauriers
        for s in (-1, 1):
            a = math.pi/2 + s*(0.9 + k*0.32); x, y = cx + math.cos(a)*44, cy + 12 + math.sin(a)*44
            d.ellipse([x - 4, y - 2, x + 4, y + 2], fill=(110, 130, 60)); d.point((x, y), fill=(160, 180, 90))
    d.rectangle([4, 104, 123, 123], fill=ENCRE); d.line([(6, 106), (121, 106)], fill=OR[2]); d.line([(6, 121), (121, 121)], fill=OR[2])
    texte2(d, (S - 5*8)//2 + 1, 108, "GLORY", OR[4]); texte(d, 10, 112, "", CREME)
    grain(im, 1, 4); d = ImageDraw.Draw(im); cadre(d, S, S, ENCRE, ROUGE2, ENCRE)
    return im

# bust — portrait officiel de l'Empereur dans un médaillon doré
def bust():
    im = degrade(S, S, [(70, 18, 24), (40, 10, 16), (20, 6, 10)]); d = ImageDraw.Draw(im)
    for x in range(0, S, 8): d.line([(x, 0), (x, S)], fill=(56, 14, 20))       # tenture
    im = halo(im, 64, 56, 70, (90, 40, 30), 0.8); d = ImageDraw.Draw(im)
    d.ellipse([18, 8, 110, 120], fill=OR[1]); d.ellipse([21, 11, 107, 117], fill=OR[3]); d.ellipse([25, 15, 103, 113], fill=OR[1])
    ellipse_degrade(im, [27, 17, 101, 111], (56, 66, 86), (16, 18, 28)); d = ImageDraw.Draw(im)
    poly_degrade(im, [(30, 111), (40, 86), (64, 80), (88, 86), (98, 111)], (40, 30, 34), (20, 14, 18))   # épaules
    d = ImageDraw.Draw(im)
    for s in (-1, 1):                                                          # épaulettes
        d.ellipse([64 + s*22 - 10, 82, 64 + s*22 + 10, 92], fill=OR[3])
        for k in range(5): d.line([(64 + s*22 - 8 + k*4, 91), (64 + s*22 - 8 + k*4, 97)], fill=OR[2])
    poly_degrade(im, [(48, 82), (80, 82), (78, 72), (50, 72)], LAITON[2], LAITON[0])      # gorgerin
    poly_degrade(im, [(46, 36), (82, 36), (84, 72), (44, 72)], LAITON[4], LAITON[1], axe="x")   # tête
    d = ImageDraw.Draw(im)
    d.rectangle([44, 50, 84, 56], fill=(30, 22, 20))                           # visière
    im = halo(im, 54, 53, 12, (255, 120, 40)); im = halo(im, 74, 53, 12, (255, 120, 40)); d = ImageDraw.Draw(im)
    d.rectangle([50, 52, 58, 54], fill=(255, 220, 140)); d.rectangle([70, 52, 78, 54], fill=(255, 220, 140))
    d.ellipse([67, 47, 81, 60], outline=OR[4]); d.line([(81, 54), (86, 76)], fill=OR[3])  # monocle et chaînette
    for k in range(6): d.line([(50, 62 + k*2), (78, 62 + k*2)], fill=LAITON[1])  # grille de bouche
    for k in range(5):                                                         # couronne
        x = 46 + k*9
        poly_degrade(im, [(x - 3, 36), (x + 5, 36), (x + 1, 20 if k % 2 == 0 else 26)], OR[4], OR[2])
    d = ImageDraw.Draw(im); d.rectangle([44, 33, 84, 37], fill=OR[2])
    for k in range(3): d.point((50 + k*14, 35), fill=(220, 40, 40) if k != 1 else (60, 140, 220))
    d.rectangle([42, 100, 86, 108], fill=OR[2]); d.rectangle([43, 101, 85, 107], fill=ENCRE); texte(d, 48, 102, "IMPERATOR", OR[4])
    grain(im, 2, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# earth — le Fragment des marées sous cloche, dans le laboratoire
def earth():
    im = degrade(S, S, [(20, 26, 32), (34, 40, 44), (26, 22, 22)]); d = ImageDraw.Draw(im)
    for y in range(0, 92, 12):                                                 # étagères du fond
        d.line([(0, y + 10), (S, y + 10)], fill=(46, 40, 36))
        for x in range(4, S, 9):
            if (x*7 + y) % 5 < 2: d.rectangle([x, y + 3, x + 4, y + 9], fill=random.Random(x + y).choice(((60, 80, 70), (90, 60, 50), (70, 70, 90))))
    poly_degrade(im, [(0, 96), (S, 96), (S, S), (0, S)], (70, 50, 36), (40, 28, 20))      # table
    d = ImageDraw.Draw(im)
    poly_degrade(im, [(44, 98), (84, 98), (88, 106), (40, 106)], LAITON[3], LAITON[0])   # socle
    im = halo(im, 64, 64, 60, (20, 90, 130), 1.0)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([44, 30, 84, 98], radius=20, outline=(170, 210, 230))   # cloche de verre
    d.line([(50, 40), (50, 88)], fill=(220, 240, 250)); d.line([(52, 36), (56, 33)], fill=(220, 240, 250))
    d.ellipse([60, 24, 68, 30], fill=LAITON[3])
    cx, cy = 64, 70                                                            # le fragment
    pts = [(cx, cy - 18), (cx + 9, cy - 4), (cx + 6, cy + 14), (cx - 5, cy + 16), (cx - 9, cy)]
    poly_degrade(im, pts, (180, 240, 255), (30, 110, 170))
    d = ImageDraw.Draw(im); d.line([(cx, cy - 18), (cx - 1, cy + 16)], fill=(220, 250, 255)); d.line([(cx - 9, cy), (cx + 9, cy - 4)], fill=(120, 200, 230))
    for k in range(5):                                                         # vaguelettes en suspension
        y = cy + 22 - k*9; d.arc([cx - 16, y - 3, cx + 16, y + 3], 200, 340, fill=(90, 190, 230))
    im = halo(im, cx, cy, 22, (60, 140, 160)); d = ImageDraw.Draw(im)
    d.rectangle([92, 92, 122, 100], fill=CREME); lignes(d, 94, 94, 26, 3, (90, 70, 50), 2)
    grain(im, 3, 4); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# fire — la coulée : creuset basculé, fonte en fusion
def fire():
    im = degrade(S, S, [(24, 14, 12), (40, 20, 14), (60, 26, 14)]); d = ImageDraw.Draw(im); rnd = random.Random(5)
    for x in range(0, S, 16):                                                  # piliers de la fonderie
        d.rectangle([x, 0, x + 5, S], fill=(30, 18, 16))
    d.rectangle([0, 14, S, 18], fill=(34, 20, 16))
    for k in range(3): d.line([(40 + k*14, 18), (52, 40)], fill=(70, 60, 56))   # chaînes
    poly = [(30, 36), (70, 30), (74, 58), (40, 66)]                            # creuset basculé
    poly_degrade(im, poly, (90, 70, 66), (40, 30, 30), axe="x")
    d = ImageDraw.Draw(im); d.line([(30, 36), (70, 30)], fill=(255, 190, 80), width=2)
    for y in range(36, 112):                                                   # filet de métal
        t = (y - 36)/76; x = 70 + 6*t + math.sin(y*0.4)*0.6
        d.line([(x - 2 - t*2, y), (x + 2 + t*2, y)], fill=mix((255, 250, 210), (255, 140, 30), t))
    ellipse_degrade(im, [42, 104, 112, 124], (255, 230, 150), (220, 90, 20))   # moule
    d = ImageDraw.Draw(im); d.arc([42, 104, 112, 124], 0, 180, fill=(70, 40, 30), width=2)
    im = halo(im, 76, 100, 70, (200, 90, 20), 1.0); im = halo(im, 72, 50, 30, (120, 70, 20))
    d = ImageDraw.Draw(im)
    etincelles(d, 76, 108, 50, rnd, (-30, 30), (-50, 0))
    d.rectangle([4, 96, 24, 124], fill=(20, 12, 10)); d.ellipse([6, 82, 22, 98], fill=(20, 12, 10))  # silhouette du fondeur
    d.rectangle([20, 100, 34, 103], fill=(20, 12, 10)); d.rectangle([10, 86, 18, 89], fill=(255, 160, 60))
    grain(im, 4, 4); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# humble — plan en coupe d'un dirigeable
def humble():
    im = degrade(S, S, [BLEU_PLAN2, BLEU_PLAN]); d = ImageDraw.Draw(im)
    for k in range(0, S, 8): d.line([(k, 0), (k, S)], fill=(44, 90, 156)); d.line([(0, k), (S, k)], fill=(44, 90, 156))
    T, T2 = TRAIT, (150, 186, 226); cx, cy = 60, 50
    d.ellipse([10, 26, 112, 74], outline=T)
    for k in range(1, 8):                                                      # couples de la carcasse
        x = 10 + k*12.75; h = 24*math.sqrt(max(0, 1 - ((x - 61)/51)**2)); d.line([(x, cy - h), (x, cy + h)], fill=T2)
    for k in range(3):                                                         # ballonnets
        x = 26 + k*24; d.ellipse([x, 36, x + 20, 64], outline=T); texte(d, x + 8, 48, str(k + 1) if str(k + 1) in POLICE else "", T)
    d.polygon([(108, 50), (122, 36), (120, 50)], outline=T); d.polygon([(108, 50), (122, 64), (120, 50)], outline=T)
    d.rectangle([44, 80, 80, 90], outline=T); d.line([(50, 74), (48, 80)], fill=T); d.line([(74, 74), (76, 80)], fill=T)
    for k in range(5): d.rectangle([47 + k*6, 83, 50 + k*6, 86], outline=T2)
    d.line([(10, 100), (112, 100)], fill=T); d.line([(10, 97), (10, 103)], fill=T); d.line([(112, 97), (112, 103)], fill=T)
    texte(d, 52, 92, "", T)
    d.ellipse([92, 80, 108, 96], outline=T)
    for k in range(4): a = k*math.pi/2 + 0.4; d.line([(100, 88), (100 + math.cos(a)*8, 88 + math.sin(a)*8)], fill=T)  # hélice
    d.line([(80, 85), (92, 88)], fill=T2)
    d.rectangle([66, 106, 123, 123], outline=T); texte2(d, 70, 110, "AIRSHIP", T, 1); texte(d, 70, 117, "CLASS III", T2)
    lignes(d, 8, 108, 50, 4, T2, 4)
    d = ImageDraw.Draw(im); cadre(d, S, S, (20, 40, 80), T2, (20, 40, 80))
    return im

# match — montre de gousset ouverte : le mouvement
def match():
    im = degrade(S, S, [(50, 16, 22), (28, 8, 14)]); d = ImageDraw.Draw(im); cx, cy = 64, 68
    im = halo(im, 50, 50, 80, (70, 40, 30)); d = ImageDraw.Draw(im)
    d.line([(64, 0), (64, 16)], fill=OR[2], width=2)                           # chaîne
    for y in range(0, 16, 4): d.ellipse([61, y, 67, y + 4], outline=OR[3])
    d.ellipse([58, 14, 70, 26], outline=OR[3], width=2)
    ellipse_degrade(im, [cx - 50, cy - 50, cx + 50, cy + 50], OR[4], OR[0]); d = ImageDraw.Draw(im)
    ellipse_degrade(im, [cx - 44, cy - 44, cx + 44, cy + 44], (60, 50, 44), (30, 24, 22)); d = ImageDraw.Draw(im)
    engrenage(d, cx - 12, cy + 8, 22, LAITON[3], LAITON[1], LAITON[5], dents=16, trou=(30, 24, 22))
    engrenage(d, cx + 20, cy - 14, 15, OR[3], OR[1], OR[4], dents=12, trou=(30, 24, 22))
    engrenage(d, cx + 22, cy + 22, 10, CUIVRE[2], CUIVRE[0], CUIVRE[3], dents=10, trou=(30, 24, 22))
    engrenage(d, cx - 22, cy - 24, 8, FER[3], FER[1], FER[4], dents=9, trou=(30, 24, 22))
    d.ellipse([cx + 8, cy - 40, cx + 34, cy - 14], outline=(190, 200, 210))   # balancier
    for k in range(3): d.arc([cx + 13 + k*2, cy - 35 + k*2, cx + 29 - k*2, cy - 19 - k*2], 0, 300, fill=(150, 160, 170))
    for (x, y) in ((cx - 30, cy + 26), (cx + 32, cy + 4), (cx - 4, cy - 30), (cx + 4, cy + 36)):
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(200, 30, 60)); d.point((x - 1, y - 1), fill=(255, 150, 170))   # rubis
    for k in range(12):
        a = 2*math.pi*k/12; d.point((cx + math.cos(a)*47, cy + math.sin(a)*47), fill=ENCRE)
    im = halo(im, cx - 26, cy - 26, 26, (70, 60, 40)); grain(im, 6, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# skull_and_roses — « TRANSFER » : casque d'automate et roses de cuivre, hommage
def skull_and_roses():
    im = degrade(S, S, [(24, 20, 22), (14, 12, 14)]); d = ImageDraw.Draw(im)
    im = halo(im, 64, 30, 70, (70, 50, 40), 0.9); d = ImageDraw.Draw(im)
    for k in range(9): d.line([(64, -10), (64 + (k - 4)*20, S)], fill=(34, 28, 28))   # rai de lumière
    cx, cy = 64, 58
    poly_degrade(im, [(cx - 26, cy + 26), (cx - 30, cy - 8), (cx - 18, cy - 28), (cx + 18, cy - 28), (cx + 30, cy - 8), (cx + 26, cy + 26)], FER[4], FER[0], axe="x")
    d = ImageDraw.Draw(im)
    d.rectangle([cx - 22, cy - 4, cx + 22, cy + 2], fill=(14, 10, 12))         # visière éteinte
    for k in range(7): d.line([(cx - 14, cy + 8 + k*2), (cx + 14, cy + 8 + k*2)], fill=FER[1])
    d.line([(cx - 4, cy - 28), (cx + 2, cy - 6)], fill=(20, 16, 16)); d.line([(cx + 2, cy - 6), (cx - 2, cy + 2)], fill=(20, 16, 16))  # fêlure
    for k in range(6): d.point((cx - 20 + k*8, cy - 18), fill=FER[4])
    rnd = random.Random(7)
    for k in range(7):                                                         # roses de cuivre
        x = 20 + k*15 + rnd.randint(-3, 3); y = 92 + (k % 2)*6
        d.line([(x, y), (x + rnd.randint(-6, 6), 112)], fill=(80, 100, 60), width=2)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=CUIVRE[2]); d.arc([x - 4, y - 4, x + 4, y + 4], 0, 270, fill=CUIVRE[3]); d.arc([x - 2, y - 2, x + 2, y + 2], 90, 360, fill=CUIVRE[0])
        d.ellipse([x + 4, y + 4, x + 9, y + 7], fill=(90, 120, 70))
    d.rectangle([4, 110, 123, 123], fill=ENCRE); texte2(d, (S - 8*8)//2, 113, "TRANSFER", (200, 180, 150))
    grain(im, 7, 4); d = ImageDraw.Draw(im); cadre(d, S, S, ENCRE, FER[1], ENCRE)
    return im

# stage — la Salle des capsules, une seule capsule éclairée au centre
def stage():
    im = degrade(S, S, [(16, 12, 20), (30, 22, 30), (12, 10, 14)]); d = ImageDraw.Draw(im); vx, vy = 64, 52
    for k in range(-8, 9): d.line([(vx, vy), (vx + k*24, S)], fill=(40, 30, 36))
    for j in range(6): y = vy + (S - vy)*(j/6)**1.8; d.line([(0, y), (S, y)], fill=(40, 30, 36))
    for rang in range(6, 0, -1):
        t = rang/6; ch = 70*(1.1 - t*0.85); cw = ch*0.42; gy = vy + (S - vy)*(1 - t)**1.3*0.85 + 6
        for s in (-1, 1):
            x = vx + s*(10 + 52*(1 - t)) - cw/2
            fade = t*0.75
            d.rounded_rectangle([x, gy - ch, x + cw, gy], radius=max(1, int(cw/2)), fill=mix(LAITON[2], (20, 16, 20), fade), outline=mix(LAITON[0], (20, 16, 20), fade))
            d.ellipse([x + cw*0.2, gy - ch*0.85, x + cw*0.8, gy - ch*0.85 + cw*0.6], fill=mix((60, 36, 90), (20, 16, 20), fade))
    cw, ch = 30, 64; x, gy = 49, 118                                           # la capsule éveillée
    im = halo(im, 64, 70, 60, (90, 50, 140)); d = ImageDraw.Draw(im)
    poly_degrade(im, [(x, gy - ch + 14), (x + cw, gy - ch + 14), (x + cw, gy), (x, gy)], LAITON[4], LAITON[1], axe="x"); d = ImageDraw.Draw(im)
    d.ellipse([x, gy - ch, x + cw, gy - ch + 28], fill=LAITON[3])
    ellipse_degrade(im, [x + 5, gy - ch + 8, x + cw - 5, gy - ch + 40], (230, 200, 255), (110, 60, 180)); d = ImageDraw.Draw(im)
    d.ellipse([x + 11, gy - ch + 18, x + 19, gy - ch + 26], fill=(255, 245, 255))
    for k in range(4): d.ellipse([x + 3, gy - 22 + k*5, x + 6, gy - 19 + k*5], fill=LAITON[0])
    d.rectangle([x + 10, gy - 16, x + 20, gy - 6], fill=ENCRE); d.rectangle([x + 12, gy - 14, x + 18, gy - 8], fill=(120, 230, 140))
    im = halo(im, 64, gy - ch + 24, 22, (120, 80, 160))
    grain(im, 8, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# void — l'Observatoire du bout du monde
def void():
    im = degrade(S, S, [(6, 4, 16), (24, 10, 44), (50, 20, 70)]); d = ImageDraw.Draw(im); rnd = random.Random(10)
    for _ in range(260): d.point((rnd.randrange(S), rnd.randrange(90)), fill=rnd.choice(((255, 255, 255), (200, 180, 255), (150, 130, 220))))
    im = halo(im, 88, 30, 40, (90, 30, 120)); d = ImageDraw.Draw(im)
    L = Image.new("RGB", (S, S)); dl = ImageDraw.Draw(L); pts = []
    for k in range(13):                                                        # faille du Vide : déchirure verticale
        y = 6 + k*5; w = 7*math.sin(math.pi*k/12); x = 96 + rnd.uniform(-3, 3)
        pts.append((x, y, w))
    for (x, y, w) in pts: dl.ellipse([x - w*1.8, y - 4, x + w*1.8, y + 4], fill=(70, 20, 100))
    im = ImageChops.add(im, L.filter(ImageFilter.GaussianBlur(4))); d = ImageDraw.Draw(im)
    gauche = [(x - w, y) for (x, y, w) in pts]; droite = [(x + w, y) for (x, y, w) in pts][::-1]
    d.polygon(gauche + droite, fill=(8, 0, 14)); d.line(gauche, fill=(230, 180, 255)); d.line(droite[::-1], fill=(190, 120, 240))
    for _ in range(12): x, y, w = rnd.choice(pts); d.point((x + rnd.uniform(-w, w)*0.6, y), fill=(255, 240, 255))
    poly_degrade(im, [(0, 104), (24, 92), (60, 96), (96, 88), (S, 98), (S, S), (0, S)], (60, 54, 40), (26, 22, 18))  # pierre de l'End
    d = ImageDraw.Draw(im)
    for k in range(30): x = rnd.randrange(S); y = rnd.randrange(100, S); d.point((x, y), fill=(90, 84, 60))
    poly_degrade(im, [(22, 100), (22, 70), (62, 70), (62, 100)], (60, 56, 70), (34, 30, 40), axe="x")   # dôme
    ellipse_degrade(im, [20, 48, 64, 92], (110, 100, 130), (50, 44, 60)); d = ImageDraw.Draw(im)
    d.rectangle([38, 48, 46, 72], fill=(20, 14, 24))                           # fente
    poly_degrade(im, [(40, 62), (46, 56), (84, 28), (80, 22)], LAITON[4], LAITON[1])   # lunette
    d = ImageDraw.Draw(im); d.ellipse([78, 20, 86, 28], fill=LAITON[0]); d.ellipse([80, 22, 84, 26], fill=(60, 40, 80))
    for k in range(4): d.rectangle([28 + k*9, 84, 32 + k*9, 90], fill=(250, 200, 110))
    d.line([(42, 46), (42, 40)], fill=LAITON[2]); d.point((42, 39), fill=(255, 80, 80))
    grain(im, 9, 3); d = ImageDraw.Draw(im); cadre(d, S, S, (30, 12, 50), (130, 70, 190), (60, 26, 96))
    return im

# water — la cloche de plongée sous les rayons
def water():
    im = degrade(S, S, [(70, 150, 170), (24, 80, 110), (8, 30, 50)], 0.8); d = ImageDraw.Draw(im); rnd = random.Random(11)
    L = Image.new("RGB", (S, S)); dl = ImageDraw.Draw(L)
    for k in range(6):                                                         # rayons de surface
        x = 10 + k*22; dl.polygon([(x, 0), (x + 8, 0), (x + 30, S), (x + 14, S)], fill=(26, 40, 40))
    im = ImageChops.add(im, L.filter(ImageFilter.GaussianBlur(3))); d = ImageDraw.Draw(im)
    for x in range(0, S, 4): d.line([(x, 2 + int(math.sin(x*0.3)*1.5)), (x + 3, 2)], fill=(200, 240, 240))
    d.line([(64, 0), (64, 34)], fill=(40, 40, 40), width=2)                    # câble
    ellipse_degrade(im, [36, 30, 92, 96], LAITON[4], LAITON[0]); d = ImageDraw.Draw(im)
    d.rectangle([34, 76, 94, 90], fill=LAITON[1]); d.line([(34, 76), (94, 76)], fill=LAITON[4])
    for k in range(8): d.ellipse([36 + k*7.5, 80, 40 + k*7.5, 84], fill=LAITON[0])
    for (x, y) in ((50, 54), (78, 54), (64, 46)):                              # hublots éclairés
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=LAITON[0]); ellipse_degrade(im, [x - 5, y - 5, x + 5, y + 5], (255, 236, 160), (230, 150, 50)); d = ImageDraw.Draw(im)
    im = halo(im, 64, 54, 30, (90, 70, 20), 0.8); d = ImageDraw.Draw(im)
    for k in range(14):                                                         # bulles
        x = 60 + rnd.randint(-6, 10); y = 28 - k*2 + rnd.randint(-1, 1)
        if y > 2: d.ellipse([x, y, x + 2, y + 2], outline=(190, 230, 240))
    poly_degrade(im, [(0, 112), (30, 104), (70, 110), (S, 102), (S, S), (0, S)], (60, 70, 60), (20, 30, 30)); d = ImageDraw.Draw(im)
    for k in range(9):                                                          # algues
        x = rnd.randrange(S); h = rnd.randint(10, 26)
        for y in range(h): d.point((x + math.sin(y*0.5)*2, S - 6 - y), fill=(50, 120, 70))
    for k in range(5):                                                          # poissons
        x, y = rnd.randint(8, 120), rnd.randint(20, 100)
        if abs(x - 64) < 34 and 28 < y < 96: continue
        d.ellipse([x - 3, y - 1, x + 3, y + 1], fill=(200, 210, 170)); d.polygon([(x + 3, y), (x + 6, y - 2), (x + 6, y + 2)], fill=(200, 210, 170))
    grain(im, 12, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# wind — station météo sur la falaise, sous l'orage
def wind():
    im = degrade(S, S, [(30, 34, 46), (60, 64, 80), (110, 106, 112)]); d = ImageDraw.Draw(im); rnd = random.Random(12)
    for k in range(6):                                                         # nuages d'orage
        x = rnd.randint(-20, 100); y = rnd.randint(0, 30); w = rnd.randint(40, 70)
        for j in range(4): xx = x + j*w/4; d.ellipse([xx, y - 4 + (j % 2)*5, xx + w/2, y + 18], fill=mix((34, 38, 50), (70, 74, 88), j/4))
    pts = [(96, 0), (90, 18), (98, 22), (86, 48), (94, 50), (80, 76)]          # éclair
    L = Image.new("RGB", (S, S)); dl = ImageDraw.Draw(L); dl.line(pts, fill=(160, 170, 230), width=5)
    im = ImageChops.add(im, L.filter(ImageFilter.GaussianBlur(3))); d = ImageDraw.Draw(im); d.line(pts, fill=(250, 250, 255))
    for _ in range(170):                                                       # pluie oblique
        x, y = rnd.randrange(-10, S), rnd.randrange(20, S); d.line([(x, y), (x + 2, y + 5)], fill=(116, 122, 140))
    poly_degrade(im, [(0, 86), (40, 76), (64, 80), (64, S), (0, S)], (60, 56, 50), (24, 22, 20))     # falaise
    d = ImageDraw.Draw(im)
    poly_degrade(im, [(64, S), (64, 96), (S, 110), (S, S)], (40, 60, 90), (20, 30, 50)); d = ImageDraw.Draw(im)   # mer
    for k in range(6): d.arc([70 + k*10, 104 + (k % 2)*6, 82 + k*10, 110 + (k % 2)*6], 180, 360, fill=(160, 180, 200))
    poly_degrade(im, [(22, 78), (34, 78), (32, 30), (24, 30)], FER[3], FER[0], axe="x"); d = ImageDraw.Draw(im)   # tour
    d.rectangle([20, 26, 36, 32], fill=LAITON[2]); d.rectangle([24, 36, 30, 42], fill=(255, 210, 120)); d.rectangle([24, 52, 30, 58], fill=(255, 210, 120))
    im = halo(im, 27, 39, 14, (120, 90, 30)); d = ImageDraw.Draw(im)
    d.line([(28, 26), (28, 12)], fill=FER[4])                                  # anémomètre
    for a in (0.2, 2.3, 4.4): x, y = 28 + math.cos(a)*9, 12 + math.sin(a)*3; d.line([(28, 12), (x, y)], fill=FER[4]); d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=CUIVRE[2])
    d.polygon([(28, 4), (38, 6), (28, 8)], fill=ROUGE)                          # manche à air
    dirigeable(d, 74, 58, 10)
    grain(im, 13, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# wither — plan du Triple Moteur
def wither():
    im = degrade(S, S, [BLEU_PLAN2, BLEU_PLAN]); d = ImageDraw.Draw(im)
    for k in range(0, S, 8): d.line([(k, 0), (k, S)], fill=(44, 90, 156)); d.line([(0, k), (S, k)], fill=(44, 90, 156))
    T, T2 = TRAIT, (150, 186, 226)
    d.rectangle([20, 50, 108, 62], outline=T)                                  # traverse
    for k, x in enumerate((30, 64, 98)):                                       # trois chaudières-têtes
        r = 15 if k == 1 else 11; y = 34 if k == 1 else 40
        d.ellipse([x - r, y - r, x + r, y + r], outline=T); d.ellipse([x - r + 4, y - r + 4, x + r - 4, y + r - 4], outline=T2)
        d.rectangle([x - r*0.6, y - 2, x - r*0.2, y + 1], outline=T); d.rectangle([x + r*0.2, y - 2, x + r*0.6, y + 1], outline=T)
        d.line([(x, y - r), (x, y - r - 8)], fill=T); d.rectangle([x - 2, y - r - 12, x + 2, y - r - 8], outline=T)
    d.rectangle([54, 62, 74, 98], outline=T)                                   # colonne
    for y in range(66, 98, 6): d.line([(54, y), (74, y)], fill=T2)
    for k in range(4): d.arc([46, 60 + k*8, 82, 76 + k*8], 20, 160, fill=T2)  # côtes
    d.line([(64, 98), (60, 106)], fill=T)
    d.line([(8, 34), (16, 34)], fill=T2); d.line([(8, 20), (8, 48)], fill=T2)
    d.rectangle([66, 106, 123, 123], outline=T); texte2(d, 70, 110, "TRIPLE", T, 1); texte(d, 70, 117, "ENGINE", T2)
    lignes(d, 8, 108, 50, 4, T2, 4)
    cadre(d, S, S, (20, 40, 80), T2, (20, 40, 80))
    return im

LOT1 = {"baroque": baroque, "bust": bust, "earth": earth, "fire": fire, "humble": humble, "match": match,
        "skull_and_roses": skull_and_roses, "stage": stage, "void": void, "water": water, "wind": wind, "wither": wither}
if __name__ == "__main__":
    import os; os.makedirs("v5", exist_ok=True); ims = []
    for n, f in LOT1.items(): im = f(); im.save(f"v5/{n}.png"); ims.append(im)
    apercu(ims, "/home/claude/apercus/v5_lot1.png", z=2)
