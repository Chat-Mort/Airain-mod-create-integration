"""Lot 1, deuxième reprise : les sept autres enrichis, retouches d'ensemble."""
from outils5 import *
from lot1b import rivets, briques
import lot1b
S = 128
POLICE.update({"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["110", "001", "010", "100", "111"],
               "3": ["110", "001", "010", "001", "110"], "5": ["111", "100", "110", "001", "110"], "6": ["011", "100", "111", "101", "111"],
               "7": ["111", "001", "010", "010", "010"], "8": ["111", "101", "111", "101", "111"], ".": ["000", "000", "000", "000", "010"],
               "-": ["000", "000", "111", "000", "000"], "X": ["101", "101", "010", "101", "101"], "Q": ["010", "101", "101", "110", "011"],
               "J": ["001", "001", "001", "101", "010"]})

def coins(d, W, H, c, c2):
    for (x, y, sx, sy) in ((6, 6, 1, 1), (W - 7, 6, -1, 1), (6, H - 7, 1, -1), (W - 7, H - 7, -1, -1)):
        d.line([(x, y), (x + sx*10, y)], fill=c); d.line([(x, y), (x, y + sy*10)], fill=c)
        d.point((x + sx*2, y + sy*2), fill=c2); d.arc([x + sx*2 - 3 + (0 if sx > 0 else -0), y + sy*2 - 3, x + sx*2 + 3, y + sy*2 + 3], 0, 360, fill=c)

def tampon(d, x, y, mot, c):
    d.ellipse([x - 13, y - 13, x + 13, y + 13], outline=c); d.ellipse([x - 11, y - 11, x + 11, y + 11], outline=c)
    texte(d, int(x - len(mot)*2 + 1), int(y - 2), mot, c)
    for k in range(10): a = 2*math.pi*k/10; d.point((x + math.cos(a)*12, y + math.sin(a)*12), fill=c)

# ------------------------------------------------------------ GLORY
def baroque():
    rnd = random.Random(1)
    im = Image.new("RGB", (S, S), (236, 220, 180)); d = ImageDraw.Draw(im); cx, cy = 64, 50
    for k in range(32):
        a1, a2 = 2*math.pi*k/32, 2*math.pi*(k + 0.5)/32
        d.polygon([(cx, cy), (cx + math.cos(a1)*200, cy + math.sin(a1)*200), (cx + math.cos(a2)*200, cy + math.sin(a2)*200)], fill=(222, 196, 140))
    for _ in range(14):                                                         # taches et pliures du papier
        x, y = rnd.randrange(S), rnd.randrange(S); r = rnd.randint(3, 9); d.ellipse([x - r, y - r, x + r, y + r], outline=(212, 190, 140))
    d.line([(S//2, 0), (S//2, 4)], fill=(200, 176, 130)); d.line([(0, S//2), (S, S//2)], fill=(226, 206, 160))
    d.rectangle([4, 4, 123, 15], fill=ROUGE2); texte(d, 30, 8, "FOR THE AIRAIN EMPIRE", CREME)
    for c, dx in ((ROUGE, -10), (BLEU_PLAN, 0), (ROUGE, 10)):                  # rubans rayés
        poly_degrade(im, [(cx + dx - 6, 20), (cx + dx + 6, 20), (cx + dx + 6, 40), (cx + dx - 6, 40)], mix(c, (255, 255, 255), 0.15), mix(c, (0, 0, 0), 0.3))
    d = ImageDraw.Draw(im)
    for x in (cx - 15, cx - 5, cx + 5, cx + 15): d.line([(x, 20), (x, 40)], fill=OR[3])
    poly_degrade(im, [(cx - 18, 17), (cx + 18, 17), (cx + 18, 23), (cx - 18, 23)], OR[4], OR[1]); d = ImageDraw.Draw(im)
    rivets(d, [(cx - 15, 20), (cx + 15, 20)], OR[0], OR[4])
    d.ellipse([cx - 4, 38, cx + 4, 46], outline=OR[2], width=2)                 # anneau
    for k in range(5):                                                          # couronne de lauriers, deux rangs
        for s in (-1, 1):
            for rr, dec in ((44, 0), (39, 0.16)):
                a = math.pi/2 + s*(0.85 + k*0.34 + dec); x, y = cx + math.cos(a)*rr, cy + 14 + math.sin(a)*rr
                d.ellipse([x - 4, y - 2, x + 4, y + 2], fill=(96, 120, 52)); d.line([(x - 3, y), (x + 3, y)], fill=(150, 176, 90))
    d.ellipse([cx - 4, cy + 54, cx + 4, cy + 60], fill=ROUGE)
    for k in range(8):                                                          # étoile biseautée
        a = k*math.pi/4 - math.pi/8; b = a + math.pi/8; c_ = a + math.pi/4
        o = (cx, cy + 14); p1 = (cx + math.cos(a)*14, cy + 14 + math.sin(a)*14); pb = (cx + math.cos(b)*34, cy + 14 + math.sin(b)*34); p2 = (cx + math.cos(c_)*14, cy + 14 + math.sin(c_)*14)
        clair = math.cos(b + 2.3) > 0
        poly_degrade(im, [o, p1, pb], OR[4] if clair else OR[2], OR[2] if clair else OR[0]); poly_degrade(im, [o, pb, p2], OR[3] if clair else OR[1], OR[1])
    d = ImageDraw.Draw(im)
    for k in range(8):
        b = k*math.pi/4; d.point((cx + math.cos(b)*30, cy + 14 + math.sin(b)*30), fill=(255, 250, 220))
    d.ellipse([cx - 17, cy - 3, cx + 17, cy + 31], fill=OR[1]); d.ellipse([cx - 15, cy - 1, cx + 15, cy + 29], fill=ROUGE2); d.ellipse([cx - 13, cy + 1, cx + 13, cy + 27], fill=ENCRE)
    for k in range(16): a = 2*math.pi*k/16; d.point((cx + math.cos(a)*14, cy + 14 + math.sin(a)*14), fill=OR[4])
    roue_couronnee(d, cx, cy + 16, 8)
    im = halo(im, cx - 12, cy + 4, 16, (90, 80, 40)); d = ImageDraw.Draw(im)
    d.rectangle([4, 102, 123, 123], fill=ENCRE); d.line([(6, 104), (121, 104)], fill=OR[2]); d.line([(6, 121), (121, 121)], fill=OR[2])
    texte2(d, (S - 5*8)//2 + 1, 104, "GLORY", OR[4]); texte(d, 29, 116, "TO THOSE WHO SERVE", (200, 170, 120))
    for x in (12, 116): d.polygon([(x - 4, 112), (x, 108), (x + 4, 112), (x, 116)], fill=OR[3])
    tampon(d, 106, 32, "N.4", (170, 50, 40))
    coins(d, S, S, (140, 110, 70), ROUGE)
    grain(im, 1, 4); d = ImageDraw.Draw(im); cadre(d, S, S, ENCRE, ROUGE2, ENCRE)
    return im

# ------------------------------------------------------------ Portrait de l'Empereur
def bust():
    rnd = random.Random(2)
    im = degrade(S, S, [(80, 20, 28), (44, 10, 18), (20, 6, 10)]); d = ImageDraw.Draw(im)
    for x in range(0, S, 6):                                                    # tenture plissée
        d.line([(x, 0), (x + 1, S)], fill=(60, 14, 22)); d.line([(x + 2, 0), (x + 3, S)], fill=(96, 28, 36))
    for k in range(0, S, 16):                                                   # motif de fleurs de lys en filigrane
        for j in range(8, S, 20): d.point((k + 8 + (j // 20 % 2)*8, j), fill=(110, 40, 40))
    im = halo(im, 64, 56, 72, (90, 40, 30), 0.8); d = ImageDraw.Draw(im)
    for s in (-1, 1):                                                           # embrasses et glands
        x = 64 + s*58; d.line([(x, 0), (x - s*4, 70)], fill=OR[2], width=2); d.ellipse([x - s*4 - 3, 68, x - s*4 + 3, 76], fill=OR[3])
        for k in range(4): d.line([(x - s*4 - 2 + k, 76), (x - s*4 - 2 + k, 84)], fill=OR[2])
    ellipse_degrade(im, [16, 6, 112, 122], OR[4], OR[0]); d = ImageDraw.Draw(im)
    for k in range(40):                                                         # moulure perlée
        a = 2*math.pi*k/40; d.point((64 + math.cos(a)*46, 64 + math.sin(a)*56), fill=OR[5] if len(OR) > 5 else (255, 240, 180))
    d.ellipse([22, 12, 106, 116], fill=OR[0])
    ellipse_degrade(im, [24, 14, 104, 114], (60, 70, 92), (16, 18, 28)); d = ImageDraw.Draw(im)
    im = halo(im, 50, 40, 40, (30, 34, 50)); d = ImageDraw.Draw(im)
    for k in range(9):                                                          # lauriers en haut du cadre
        for s in (-1, 1):
            a = -math.pi/2 + s*(0.2 + k*0.14); x, y = 64 + math.cos(a)*49, 64 + math.sin(a)*59
            d.ellipse([x - 3, y - 2, x + 3, y + 2], fill=(110, 130, 60)); d.point((x, y), fill=(170, 190, 100))
    poly_degrade(im, [(28, 110), (36, 84), (64, 78), (92, 84), (100, 110)], (34, 38, 64), (16, 18, 34)); d = ImageDraw.Draw(im)   # uniforme
    for k in range(5): d.point((64, 86 + k*5), fill=OR[4])                      # boutons
    d.line([(42, 84), (82, 108)], fill=ROUGE, width=4); d.line([(42, 83), (82, 107)], fill=(200, 60, 50))   # écharpe
    for s in (-1, 1):                                                           # épaulettes
        d.ellipse([64 + s*24 - 11, 80, 64 + s*24 + 11, 90], fill=OR[3]); d.arc([64 + s*24 - 11, 80, 64 + s*24 + 11, 90], 180, 300, fill=OR[5] if len(OR) > 5 else OR[4])
        for k in range(6): d.line([(64 + s*24 - 9 + k*3.6, 89), (64 + s*24 - 9 + k*3.6, 96)], fill=OR[2])
    for k, c in enumerate(((200, 40, 40), (60, 120, 200), (240, 220, 120))):   # médailles
        x = 74 + k*6; d.rectangle([x, 92, x + 3, 96], fill=c); d.ellipse([x - 1, 96, x + 4, 101], fill=OR[3])
    poly_degrade(im, [(48, 80), (80, 80), (78, 70), (50, 70)], LAITON[2], LAITON[0]); d = ImageDraw.Draw(im)
    for k in range(5): d.line([(52 + k*6, 71), (52 + k*6, 79)], fill=LAITON[1])
    poly_degrade(im, [(46, 36), (82, 36), (84, 70), (44, 70)], LAITON[4], LAITON[1], axe="x"); d = ImageDraw.Draw(im)
    d.line([(64, 37), (64, 48)], fill=LAITON[1]); rivets(d, [(48, 40), (80, 40), (48, 66), (80, 66)])
    d.line([(46, 38), (46, 68)], fill=LAITON[5])
    d.rectangle([44, 49, 84, 57], fill=(30, 22, 20)); d.line([(44, 49), (84, 49)], fill=LAITON[0])
    im = halo(im, 54, 53, 12, (255, 120, 40)); im = halo(im, 74, 53, 12, (255, 120, 40)); d = ImageDraw.Draw(im)
    d.rectangle([50, 52, 58, 54], fill=(255, 220, 140)); d.rectangle([70, 52, 78, 54], fill=(255, 220, 140))
    d.ellipse([67, 47, 81, 60], outline=OR[4]); d.point((70, 49), fill=(255, 255, 255)); d.line([(81, 54), (84, 66), (82, 82)], fill=OR[3])
    for k in range(6): d.line([(50, 61 + k*2), (78, 61 + k*2)], fill=LAITON[1] if k % 2 else LAITON[0])
    d.rectangle([43, 32, 85, 37], fill=OR[2]); d.line([(43, 32), (85, 32)], fill=OR[4])
    for k in range(5):
        x = 46 + k*9
        poly_degrade(im, [(x - 3, 33), (x + 5, 33), (x + 1, 17 if k % 2 == 0 else 24)], OR[4], OR[2])
        d = ImageDraw.Draw(im); d.ellipse([x - 1, (17 if k % 2 == 0 else 24) - 3, x + 3, (17 if k % 2 == 0 else 24) + 1], fill=OR[4])
    for k in range(3): d.ellipse([49 + k*14, 33, 53 + k*14, 37], fill=(220, 40, 40) if k != 1 else (60, 140, 220))
    d.rectangle([40, 104, 88, 113], fill=OR[2]); d.rectangle([41, 105, 87, 112], fill=ENCRE); texte(d, 46, 107, "IMPERATOR", OR[4])
    grain(im, 2, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# ------------------------------------------------------------ Laboratoire : le fragment des marées
def earth():
    rnd = random.Random(3)
    im = degrade(S, S, [(20, 26, 32), (34, 40, 44), (26, 22, 22)]); d = ImageDraw.Draw(im)
    briques(d, 0, 0, S, 96, (38, 42, 44), (24, 26, 28), rnd, h=5, w=10, var=5)
    for y in (24, 52):                                                          # étagères
        d.rectangle([0, y, 40, y + 2], fill=(80, 56, 36)); d.rectangle([88, y, S, y + 2], fill=(80, 56, 36))
        for x in list(range(3, 38, 7)) + list(range(91, 126, 7)):
            c = rnd.choice(((80, 200, 120), (200, 80, 70), (90, 120, 220), (220, 190, 70), (170, 90, 200)))
            if rnd.random() < 0.5:
                d.rectangle([x + 1, y - 9, x + 3, y - 6], fill=(150, 170, 170)); d.ellipse([x - 1, y - 7, x + 5, y], fill=(150, 170, 170)); d.ellipse([x, y - 4, x + 4, y - 1], fill=c)
            else:
                d.rectangle([x, y - 10, x + 4, y - 1], fill=(150, 170, 170)); d.rectangle([x + 1, y - 6, x + 3, y - 1], fill=c); d.rectangle([x, y - 12, x + 4, y - 10], fill=(110, 80, 60))
    for (gx, gy) in ((14, 70), (114, 70)):                                       # manomètres muraux
        d.ellipse([gx - 7, gy - 7, gx + 7, gy + 7], fill=LAITON[1]); d.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=CREME)
        d.line([(gx, gy), (gx + 3, gy - 3)], fill=ROUGE); d.line([(gx, gy + 7), (gx, 96)], fill=CUIVRE[1], width=2)
    d.line([(14, 77), (14, 84), (40, 84), (44, 92)], fill=CUIVRE[2], width=2); d.line([(114, 77), (114, 84), (88, 84), (84, 92)], fill=CUIVRE[2], width=2)
    poly_degrade(im, [(0, 96), (S, 96), (S, S), (0, S)], (86, 60, 40), (40, 28, 20)); d = ImageDraw.Draw(im)
    for y in range(100, S, 5): d.line([(0, y), (S, y + 1)], fill=(70, 48, 32))
    poly_degrade(im, [(42, 96), (86, 96), (90, 106), (38, 106)], LAITON[4], LAITON[0]); d = ImageDraw.Draw(im)
    rivets(d, [(44 + k*8, 101) for k in range(6)]); d.ellipse([60, 98, 68, 104], fill=(30, 140, 190))
    im = halo(im, 64, 64, 60, (20, 90, 130), 1.0); d = ImageDraw.Draw(im)
    for k in range(3):                                                          # bobines électriques
        x = 30 + k*34 if k != 1 else None
        if x is None: continue
        d.rectangle([x - 3, 70, x + 3, 96], fill=CUIVRE[1])
        for y in range(72, 95, 2): d.line([(x - 3, y), (x + 3, y)], fill=CUIVRE[3])
        d.ellipse([x - 5, 64, x + 5, 72], fill=FER[3])
    for (a, b) in (((30, 66), (46, 52)), ((98, 66), (82, 48))):                 # arcs électriques
        x0, y0 = a; x1, y1 = b; pts = [a]
        for t in (0.25, 0.5, 0.75): pts.append((x0 + (x1 - x0)*t + rnd.randint(-3, 3), y0 + (y1 - y0)*t + rnd.randint(-3, 3)))
        pts.append(b); d.line(pts, fill=(200, 240, 255))
    d.rounded_rectangle([44, 30, 84, 98], radius=20, outline=(170, 210, 230))
    d.line([(49, 42), (49, 88)], fill=(220, 240, 250)); d.line([(51, 37), (55, 33)], fill=(220, 240, 250)); d.line([(80, 50), (80, 70)], fill=(130, 170, 190))
    d.ellipse([58, 23, 70, 30], fill=LAITON[3]); d.rectangle([62, 18, 66, 23], fill=LAITON[1]); d.ellipse([61, 15, 67, 19], fill=LAITON[4])
    cx, cy = 64, 68
    pts = [(cx, cy - 18), (cx + 9, cy - 4), (cx + 6, cy + 14), (cx - 5, cy + 16), (cx - 9, cy)]
    poly_degrade(im, pts, (190, 245, 255), (30, 110, 170)); d = ImageDraw.Draw(im)
    d.line([(cx, cy - 18), (cx - 1, cy + 16)], fill=(220, 250, 255)); d.line([(cx - 9, cy), (cx + 9, cy - 4)], fill=(120, 200, 230)); d.line([(cx, cy - 18), (cx + 6, cy + 14)], fill=(80, 170, 220))
    for k in range(5): y = cy + 22 - k*9; d.arc([cx - 16, y - 3, cx + 16, y + 3], 200, 340, fill=(90, 190, 230))
    for _ in range(12): d.point((cx + rnd.randint(-14, 14), cy + rnd.randint(-20, 22)), fill=(170, 240, 255))
    im = halo(im, cx, cy, 24, (60, 140, 160)); d = ImageDraw.Draw(im)
    d.polygon([(94, 104), (122, 100), (124, 112), (96, 116)], fill=CREME); lignes(d, 98, 104, 22, 3, (90, 70, 50), 3)   # carnet et plume
    d.line([(112, 98), (122, 88)], fill=(240, 240, 230)); d.line([(113, 98), (121, 90)], fill=(190, 190, 180))
    d.ellipse([8, 104, 18, 112], fill=(40, 40, 50)); d.ellipse([10, 104, 16, 108], fill=(30, 30, 60))   # encrier
    grain(im, 3, 4); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# ------------------------------------------------------------ Fonderie : la coulée
def fire():
    rnd = random.Random(5)
    im = degrade(S, S, [(24, 14, 12), (40, 20, 14), (60, 26, 14)]); d = ImageDraw.Draw(im)
    briques(d, 0, 0, S, 104, (54, 30, 24), (30, 16, 12), rnd, h=5, w=10, var=6)
    for x in (0, 104):                                                         # piliers métalliques
        poly_degrade(im, [(x, 0), (x + 10, 0), (x + 10, S), (x, S)], FER[3], FER[0], axe="x"); d = ImageDraw.Draw(im)
        rivets(d, [(x + 2, y) for y in range(8, S, 12)] + [(x + 8, y) for y in range(8, S, 12)], FER[0], FER[4])
    poly_degrade(im, [(0, 8), (S, 8), (S, 16), (0, 16)], FER[3], FER[0]); d = ImageDraw.Draw(im)      # poutre du pont roulant
    for x in range(4, S, 8): d.line([(x, 8), (x + 4, 16)], fill=FER[1])
    d.rectangle([40, 16, 60, 22], fill=FER[2]); d.ellipse([46, 16, 54, 24], fill=LAITON[2])           # chariot
    for k in range(4): d.line([(46 + k*3, 24), (44 + k*4, 34)], fill=FER[4])
    for y in range(24, 40, 3): d.ellipse([50, y, 53, y + 3], outline=FER[4])                          # chaîne
    d.arc([46, 36, 58, 46], 0, 180, fill=FER[4], width=2)
    poly = [(28, 38), (70, 30), (76, 60), (40, 68)]
    poly_degrade(im, poly, (110, 86, 80), (40, 30, 30), axe="x"); d = ImageDraw.Draw(im)
    for t in (0.3, 0.65):                                                      # cerclages du creuset
        d.line([(28 + 42*t, 38 - 8*t), (40 + 36*t, 68 - 8*t)], fill=(60, 44, 40), width=2)
    d.line([(28, 38), (70, 30)], fill=(255, 200, 90), width=3); d.line([(30, 37), (68, 31)], fill=(255, 250, 200))
    d.line([(28, 40), (14, 50)], fill=FER[3], width=2); d.ellipse([10, 48, 16, 54], fill=FER[2])       # levier de basculement
    for y in range(36, 110):
        t = (y - 36)/74; x = 71 + 6*t + math.sin(y*0.4)*0.6
        d.line([(x - 2 - t*2, y), (x + 2 + t*2, y)], fill=mix((255, 252, 220), (255, 140, 30), t))
        if y % 7 == 0: d.point((x, y), fill=(255, 255, 255))
    for k in range(3):                                                         # rangée de moules
        x = 20 + k*30 if k < 2 else 96
        if k == 2: continue
    ellipse_degrade(im, [44, 102, 114, 124], (255, 236, 160), (220, 90, 20)); d = ImageDraw.Draw(im)
    d.arc([44, 102, 114, 124], 0, 180, fill=(70, 40, 30), width=2); d.arc([44, 102, 114, 124], 180, 360, fill=(120, 70, 40))
    for (x, w) in ((10, 26), (116, 10)):                                       # moules déjà coulés qui refroidissent
        d.rectangle([x, 112, x + w, 122], fill=(60, 40, 34)); d.rectangle([x + 2, 114, x + w - 2, 118], fill=(200, 70, 20))
    for k in range(5):                                                         # lingots refroidis
        d.polygon([(12 + k*5, 104), (16 + k*5, 104), (17 + k*5, 108), (11 + k*5, 108)], fill=FER[3] if k % 2 else FER[2])
    im = halo(im, 78, 100, 74, (210, 96, 20), 1.0); im = halo(im, 70, 46, 30, (130, 70, 20)); d = ImageDraw.Draw(im)
    etincelles(d, 78, 108, 70, rnd, (-36, 36), (-60, 0))
    for k in range(4):                                                         # fumées
        x = 64 + k*8; y = 30 - k*6; r = 5 + k*2; d.ellipse([x - r, y - r, x + r, y + r], outline=(90, 70, 60))
    x0 = 18                                                                    # fondeur en tablier, gaffe en main
    d.rectangle([x0 - 6, 84, x0 + 8, 112], fill=(24, 14, 12)); d.ellipse([x0 - 6, 70, x0 + 8, 86], fill=(24, 14, 12))
    d.rectangle([x0 - 2, 76, x0 + 8, 79], fill=(255, 170, 60)); d.rectangle([x0 - 4, 90, x0 + 6, 110], fill=(70, 44, 30))
    d.line([(x0 + 8, 92), (40, 100)], fill=FER[3], width=2); d.rectangle([x0 - 6, 112, x0 - 1, 118], fill=(24, 14, 12)); d.rectangle([x0 + 3, 112, x0 + 8, 118], fill=(24, 14, 12))
    d.line([(x0 + 8, 80), (x0 + 8, 100)], fill=(255, 130, 40))                # contre-jour
    grain(im, 4, 4); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

# ------------------------------------------------------------ Plans : fond commun
def fond_plan():
    im = degrade(S, S, [BLEU_PLAN2, BLEU_PLAN]); d = ImageDraw.Draw(im)
    for k in range(0, S, 4): d.line([(k, 0), (k, S)], fill=(38, 84, 150)); d.line([(0, k), (S, k)], fill=(38, 84, 150))
    for k in range(0, S, 16): d.line([(k, 0), (k, S)], fill=(52, 100, 170)); d.line([(0, k), (S, k)], fill=(52, 100, 170))
    rnd = random.Random(30)
    for _ in range(6): x, y = rnd.randrange(S), rnd.randrange(S); d.ellipse([x - 10, y - 8, x + 10, y + 8], outline=(42, 88, 154))   # taches d'usage
    return im, d

def cote(d, x0, y0, x1, y1, txt, c):
    d.line([(x0, y0), (x1, y1)], fill=c)
    if y0 == y1:
        d.polygon([(x0, y0), (x0 + 3, y0 - 2), (x0 + 3, y0 + 2)], fill=c); d.polygon([(x1, y1), (x1 - 3, y1 - 2), (x1 - 3, y1 + 2)], fill=c)
        texte(d, int((x0 + x1)/2 - len(txt)*2), y0 - 7, txt, c)
    else:
        d.polygon([(x0, y0), (x0 - 2, y0 + 3), (x0 + 2, y0 + 3)], fill=c); d.polygon([(x1, y1), (x1 - 2, y1 - 3), (x1 + 2, y1 - 3)], fill=c)
        texte(d, x0 + 3, int((y0 + y1)/2 - 2), txt, c)

def humble():
    im, d = fond_plan(); T, T2, R = TRAIT, (150, 186, 226), (230, 110, 90); cy = 46
    d.ellipse([12, 24, 112, 68], outline=T); d.ellipse([14, 26, 110, 66], outline=T2)
    for k in range(1, 8):
        x = 12 + k*12.5; h = 22*math.sqrt(max(0, 1 - ((x - 62)/50)**2)); d.line([(x, cy - h), (x, cy + h)], fill=T2)
    d.line([(12, cy), (112, cy)], fill=T2)
    for k in range(3):
        x = 26 + k*24; d.ellipse([x, 32, x + 20, 60], outline=T); d.ellipse([x + 3, 35, x + 17, 57], outline=T2); texte(d, x + 9, 44, str(k + 1), T)
    d.polygon([(108, 46), (122, 32), (120, 46)], outline=T); d.polygon([(108, 46), (122, 60), (120, 46)], outline=T)
    d.rectangle([44, 76, 82, 86], outline=T); d.line([(50, 68), (48, 76)], fill=T); d.line([(76, 68), (78, 76)], fill=T); d.line([(63, 68), (63, 76)], fill=T)
    for k in range(5): d.rectangle([47 + k*7, 79, 50 + k*7, 82], outline=T2)
    d.ellipse([88, 72, 104, 88], outline=T)
    for k in range(4): a = k*math.pi/2 + 0.4; d.line([(96, 80), (96 + math.cos(a)*8, 80 + math.sin(a)*8)], fill=T)
    d.line([(82, 81), (88, 80)], fill=T2)
    cote(d, 12, 18, 112, 18, "160", T2); cote(d, 6, 24, 6, 68, "48", T2)
    for (x, y, n) in ((36, 36, "A"), (96, 80, "B"), (63, 81, "C")):           # repères annotés
        d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=R); texte(d, x - 1, y - 2, n, R)
    texte(d, 8, 100, "A. GAS CELL", T2); texte(d, 8, 106, "B. PROPELLER", T2); texte(d, 8, 112, "C. GONDOLA", T2)
    d.rectangle([66, 100, 123, 123], outline=T); d.line([(66, 108), (123, 108)], fill=T)
    texte2(d, 69, 102, "AIRSHIP", T, 1); texte(d, 69, 111, "CLASS III", T2); texte(d, 69, 117, "SHEET 2-4", T2)
    tampon(d, 28, 84, "OK", R)
    cadre(d, S, S, (20, 40, 80), T2, (20, 40, 80))
    return im

def wither():
    im, d = fond_plan(); T, T2, R = TRAIT, (150, 186, 226), (230, 110, 90)
    d.rectangle([18, 50, 106, 60], outline=T); d.line([(18, 55), (106, 55)], fill=T2)
    for x in range(22, 106, 8): d.point((x, 52), fill=T); d.point((x, 58), fill=T)
    for k, x in enumerate((28, 62, 96)):
        r = 15 if k == 1 else 11; y = 32 if k == 1 else 38
        d.ellipse([x - r, y - r, x + r, y + r], outline=T); d.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3], outline=T2)
        d.rectangle([x - r*0.6, y - 2, x - r*0.2, y + 1], outline=T); d.rectangle([x + r*0.2, y - 2, x + r*0.6, y + 1], outline=T)
        d.line([(x - r*0.4, y + r*0.5), (x + r*0.4, y + r*0.5)], fill=T2)
        d.line([(x, y - r), (x, y - r - 6)], fill=T); d.rectangle([x - 2, y - r - 10, x + 2, y - r - 6], outline=T)
        for j in range(3): d.arc([x - 3 - j*2, y - r - 16 - j*4, x + 3 + j*2, y - r - 10 - j*4], 200, 340, fill=T2)   # vapeur
        d.line([(x, y + r), (x, 50)], fill=T)
    d.rectangle([52, 60, 72, 96], outline=T)
    for y in range(64, 96, 5): d.line([(52, y), (72, y)], fill=T2)
    for k in range(4): d.arc([44, 58 + k*8, 80, 74 + k*8], 20, 160, fill=T2)
    d.line([(62, 96), (58, 104)], fill=T); d.line([(58, 104), (60, 108)], fill=T)
    cote(d, 4, 13, 44, 13, "60", T2); cote(d, 108, 22, 108, 100, "120", T2)
    for (x, y, n) in ((62, 32, "A"), (62, 80, "B"), (96, 55, "C")):
        d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=R); texte(d, x - 1, y - 2, n, R)
    texte(d, 6, 84, "A. BOILER", T2); texte(d, 6, 90, "B. SPINE", T2); texte(d, 6, 96, "C. BEAM", T2)
    d.rectangle([66, 104, 123, 123], outline=T); d.line([(66, 112), (123, 112)], fill=T)
    texte2(d, 69, 106, "TRIPLE", T, 1); texte(d, 69, 115, "ENGINE  PROTO", T2)
    texte(d, 6, 112, "DO NOT", R); texte(d, 6, 118, "IGNITE", R)
    cadre(d, S, S, (20, 40, 80), T2, (20, 40, 80))
    return im

# ------------------------------------------------------------ Montre de gousset
def match():
    rnd = random.Random(6)
    im = degrade(S, S, [(56, 18, 26), (28, 8, 14)]); d = ImageDraw.Draw(im)
    for k in range(8):                                                          # plis du velours
        x = rnd.randint(0, S); d.line([(x, 0), (x + rnd.randint(-30, 30), S)], fill=(70, 24, 32)); d.line([(x + 2, 0), (x + 2 + rnd.randint(-30, 30), S)], fill=(40, 12, 20))
    im = halo(im, 50, 50, 80, (70, 40, 30)); d = ImageDraw.Draw(im)
    cx, cy = 58, 72
    lx, ly = 104, 34                                                            # couvercle ouvert gravé
    ellipse_degrade(im, [lx - 22, ly - 22, lx + 22, ly + 22], OR[3], OR[0]); d = ImageDraw.Draw(im)
    d.ellipse([lx - 18, ly - 18, lx + 18, ly + 18], outline=OR[1])
    for k in range(24): a = 2*math.pi*k/24; d.line([(lx + math.cos(a)*12, ly + math.sin(a)*12), (lx + math.cos(a)*17, ly + math.sin(a)*17)], fill=OR[1])
    roue_couronnee(d, lx, ly + 3, 6, fond=OR[2])
    d.line([(cx + 36, cy - 36), (lx - 16, ly + 14)], fill=OR[1], width=3)     # charnière
    d.line([(cx, cy - 52), (cx, 6)], fill=OR[2], width=2)
    for y in range(-2, cy - 52, 4): d.ellipse([cx - 3 + (y//4 % 2), y, cx + 3 + (y//4 % 2), y + 4], outline=OR[3])
    d.rectangle([cx - 4, cy - 58, cx + 4, cy - 50], fill=OR[3]); d.ellipse([cx - 6, cy - 64, cx + 6, cy - 56], outline=OR[3], width=2)
    for k in range(7): d.line([(cx - 4 + k, cy - 58), (cx - 4 + k, cy - 50)], fill=OR[1] if k % 2 else OR[4])   # couronne striée
    ellipse_degrade(im, [cx - 50, cy - 50, cx + 50, cy + 50], OR[4], OR[0]); d = ImageDraw.Draw(im)
    for k in range(60): a = 2*math.pi*k/60; d.point((cx + math.cos(a)*48, cy + math.sin(a)*48), fill=OR[1])
    ellipse_degrade(im, [cx - 45, cy - 45, cx + 45, cy + 45], (236, 226, 200), (190, 176, 150)); d = ImageDraw.Draw(im)   # cadran
    for k in range(60):
        a = 2*math.pi*k/60 - math.pi/2; r1 = 39 if k % 5 else 35
        d.line([(cx + math.cos(a)*r1, cy + math.sin(a)*r1), (cx + math.cos(a)*42, cy + math.sin(a)*42)], fill=ENCRE)
    ellipse_degrade(im, [cx - 32, cy - 32, cx + 32, cy + 32], (60, 50, 44), (24, 20, 18)); d = ImageDraw.Draw(im)   # mouvement squelette
    d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], outline=OR[2])
    engrenage(d, cx - 9, cy + 7, 16, LAITON[3], LAITON[1], LAITON[5], dents=16, trou=(28, 22, 20))
    engrenage(d, cx + 14, cy - 11, 11, OR[3], OR[1], OR[4], dents=12, trou=(28, 22, 20))
    engrenage(d, cx + 16, cy + 16, 7, CUIVRE[2], CUIVRE[0], CUIVRE[3], dents=10, trou=(28, 22, 20))
    engrenage(d, cx - 16, cy - 17, 6, FER[4], FER[2], FER[5], dents=9, trou=(28, 22, 20))
    d.ellipse([cx - 4, cy - 30, cx + 12, cy - 14], outline=(200, 206, 214))
    for k in range(3): d.arc([cx - 1 + k*2, cy - 27 + k*2, cx + 9 - k*2, cy - 17 - k*2], 0, 300, fill=(150, 160, 170))
    for (x, y) in ((cx - 24, cy + 18), (cx + 24, cy + 2), (cx, cy - 26), (cx + 2, cy + 26), (cx - 26, cy - 4)):
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(210, 30, 60)); d.point((x - 1, y - 1), fill=(255, 160, 180))
    for (x, y) in ((cx - 4, cy - 6), (cx + 26, cy - 22), (cx - 28, cy + 8)): d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(200, 200, 210)); d.point((x, y), fill=(60, 60, 70))   # vis bleuies
    d.line([(cx, cy), (cx + 22, cy - 18)], fill=(40, 60, 150), width=2); d.line([(cx, cy), (cx - 6, cy + 28)], fill=(40, 60, 150))   # aiguilles
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=OR[4])
    im = halo(im, cx - 24, cy - 26, 30, (80, 70, 50)); d = ImageDraw.Draw(im)
    d.arc([cx - 46, cy - 46, cx + 46, cy + 46], 200, 250, fill=(255, 255, 240))
    for k in range(3): x = 12 + k*6; d.ellipse([x, 112, x + 4, 116], fill=(200, 30, 60))                # rubis de rechange
    d.line([(96, 116), (124, 106)], fill=FER[4], width=2); d.line([(124, 106), (126, 104)], fill=FER[5])  # brucelles
    grain(im, 6, 3); d = ImageDraw.Draw(im); cadre(d, S, S)
    return im

LOT1C = {"baroque": baroque, "bust": bust, "earth": earth, "fire": fire, "humble": humble, "match": match, "wither": wither}
if __name__ == "__main__":
    ims = []
    for n, f in LOT1C.items(): im = f(); im.save(f"v5/{n}.png"); ims.append(im)
    apercu(ims, "/home/claude/apercus/v5_lot1c.png", z=3)
