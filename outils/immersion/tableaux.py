"""Les tableaux deviennent les affiches, plans et vues de l'Empire d'Airain (pixel art à la taille vanilla)."""
import math, random, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, "../mobs")
from atelier import LAITON, CUIVRE, FER, SUIE, ramp, mix, OR, VIOLET_VERRE, ECHO, LAQUE_ROUGE

CREME, PAPIER, ENCRE = (232, 214, 172), (214, 194, 150), (34, 26, 22)
ROUGE, ROUGE2 = (168, 36, 28), (120, 22, 18)
BLEU_PLAN, BLEU_PLAN2, TRAIT = (28, 64, 120), (36, 80, 146), (214, 228, 244)
CREPUSCULE = [(52, 34, 58), (122, 64, 70), (204, 112, 66), (238, 170, 92)]

def cadre(d, W, H, c1=LAITON[1], c2=LAITON[3]):
    d.rectangle([0, 0, W-1, H-1], outline=c1); 
    if min(W, H) >= 32: d.rectangle([1, 1, W-2, H-2], outline=c2)

def roue_couronnee(d, cx, cy, r, c=LAITON[4], c2=LAITON[1], fond=ENCRE):
    dents = 8
    for k in range(dents):
        a = 2*math.pi*k/dents
        x, y = cx + math.cos(a)*r*1.05, cy + math.sin(a)*r*1.05
        d.rectangle([x - r*0.18, y - r*0.18, x + r*0.18, y + r*0.18], fill=c)
    d.ellipse([cx-r*0.9, cy-r*0.9, cx+r*0.9, cy+r*0.9], fill=c)
    d.ellipse([cx-r*0.45, cy-r*0.45, cx+r*0.45, cy+r*0.45], fill=fond)
    d.ellipse([cx-r*0.18, cy-r*0.18, cx+r*0.18, cy+r*0.18], fill=c2)
    # couronne
    w = r*1.5; top = cy - r*1.7; base = cy - r*0.95
    d.rectangle([cx-w/2, base - r*0.18, cx+w/2, base], fill=OR[3])
    for k in range(3):
        px = cx - w/2 + k*w/2
        d.polygon([(px - r*0.24, base - r*0.18), (px + r*0.24, base - r*0.18), (px, top)], fill=OR[4])

def rayons(d, W, H, c1, c2, cx, cy, n=16):
    for k in range(n):
        a1, a2 = 2*math.pi*k/n, 2*math.pi*(k+0.5)/n
        R = W + H
        d.polygon([(cx, cy), (cx + math.cos(a1)*R, cy + math.sin(a1)*R), (cx + math.cos(a2)*R, cy + math.sin(a2)*R)], fill=c1)
    
def lignes_texte(d, x0, y0, w, n, c):
    rnd = random.Random(int(x0*7 + y0*13 + w))
    for i in range(n):
        x = x0
        while x < x0 + w - 2:
            l = rnd.randint(2, 5)
            d.line([(x, y0 + i*3), (min(x0 + w - 1, x + l - 1), y0 + i*3)], fill=c); x += l + 1

# ------------------------------------------------------------------ motifs
def affiche(W, H, fond=CREME, ray=ROUGE):
    im = Image.new("RGB", (W, H), fond); d = ImageDraw.Draw(im)
    cy = H*0.42
    rayons(d, W, H, ray, fond, W/2, cy)
    r = min(W, H)*0.24
    d.ellipse([W/2 - r*1.35, cy - r*1.35, W/2 + r*1.35, cy + r*1.35], fill=ENCRE)
    roue_couronnee(d, W/2, cy + r*0.15, r*0.8)
    if H >= 32:
        bande = max(5, H//6)
        d.rectangle([0, H - bande, W, H], fill=ENCRE)
        lignes_texte(d, 3, H - bande + 2, W - 6, max(1, (bande - 2)//3), CREME)
    cadre(d, W, H, ENCRE, ROUGE2)
    return im

def ciel(d, W, H):
    for y in range(H):
        d.line([(0, y), (W, y)], fill=ramp(CREPUSCULE, y/H))

def silhouette_ville(d, W, H, base, rnd, tour=True):
    x = 0
    while x < W:
        w = rnd.randint(max(2, W//14), max(3, W//7)); h = rnd.randint(H//8, H//3)
        d.rectangle([x, base - h, x + w, base], fill=SUIE[1])
        if rnd.random() < 0.5: d.rectangle([x + 1, base - h - H//10, x + 2, base - h], fill=SUIE[1])   # cheminée
        for yy in range(base - h + 2, base - 1, 3):
            for xx in range(x + 1, x + w, 2):
                if rnd.random() < 0.25: d.point((xx, yy), fill=(240, 180, 90))
        x += w + 1
    if tour and W >= 32:                                                 # tour d'horloge
        tx = W*0.62; th = H*0.55
        d.rectangle([tx - 3, base - th, tx + 3, base], fill=SUIE[0])
        d.ellipse([tx - 3, base - th + 2, tx + 3, base - th + 8], fill=CREME)
        d.point((tx, base - th + 5), fill=ENCRE)
        d.polygon([(tx - 4, base - th), (tx + 4, base - th), (tx, base - th - 6)], fill=CUIVRE[1])

def dirigeable(d, cx, cy, s):
    d.ellipse([cx - s, cy - s*0.38, cx + s, cy + s*0.38], fill=CREME, outline=ENCRE)
    for k in (-0.5, 0, 0.5): d.line([(cx + k*s, cy - s*0.34), (cx + k*s, cy + s*0.34)], fill=PAPIER)
    d.rectangle([cx - s*0.35, cy + s*0.45, cx + s*0.35, cy + s*0.62], fill=LAITON[2], outline=ENCRE)
    d.line([(cx - s*0.3, cy + s*0.3), (cx - s*0.3, cy + s*0.45)], fill=ENCRE); d.line([(cx + s*0.3, cy + s*0.3), (cx + s*0.3, cy + s*0.45)], fill=ENCRE)
    d.polygon([(cx + s*0.95, cy), (cx + s*1.25, cy - s*0.3), (cx + s*1.25, cy + s*0.3)], fill=ROUGE)

def scene_ciel(W, H, sujet, graine):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im); rnd = random.Random(graine)
    ciel(d, W, H)
    d.ellipse([W*0.12, H*0.15, W*0.12 + H*0.22, H*0.15 + H*0.22], fill=(250, 214, 130))     # soleil voilé
    base = int(H*0.82)
    if sujet == "dirigeable":
        silhouette_ville(d, W, H, base, rnd)
        dirigeable(d, W*0.45, H*0.32, min(W, H*2)*0.2)
        if W >= 48: dirigeable(d, W*0.8, H*0.18, min(W, H*2)*0.09)
    elif sujet == "train":
        d.rectangle([0, base, W, H], fill=SUIE[2])
        d.line([(0, base + 1), (W, base + 1)], fill=FER[4])
        lx = W*0.2; lw = W*0.5; lh = H*0.28
        d.rectangle([lx, base - lh, lx + lw, base - 2], fill=LAQUE_ROUGE[3], outline=ENCRE)
        d.rectangle([lx + lw*0.65, base - lh*1.5, lx + lw, base - lh], fill=LAQUE_ROUGE[2], outline=ENCRE)   # cabine
        d.rectangle([lx + lw*0.1, base - lh*1.5, lx + lw*0.2, base - lh], fill=SUIE[0])                       # cheminée
        for k in range(3): d.ellipse([lx + lw*(0.1 + k*0.28), base - lh*0.45, lx + lw*(0.1 + k*0.28) + lh*0.5, base + lh*0.05], fill=SUIE[0], outline=LAITON[3])
        for k in range(5):                                                                                    # fumée
            r = 1 + k; x = lx + lw*0.15 - k*W*0.05; y = base - lh*1.6 - k*H*0.06
            d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 196, 190))
    elif sujet == "usine":
        silhouette_ville(d, W, H, base, rnd, tour=False)
        for k in range(4):
            x = W*(0.15 + 0.22*k); h = H*rnd.uniform(0.4, 0.6)
            d.rectangle([x, base - h, x + max(2, W//16), base], fill=SUIE[0])
            for j in range(4):
                r = 1 + j; d.ellipse([x + j*2 - r, base - h - j*H*0.07 - r, x + j*2 + r, base - h - j*H*0.07 + r], fill=(176, 170, 164))
    elif sujet == "navire":
        d.rectangle([0, base, W, H], fill=(36, 70, 80))
        for x in range(0, W, 3): d.point((x, base + 1 + (x//3) % 2), fill=(90, 130, 136))
        d.polygon([(W*0.2, base - 3), (W*0.8, base - 3), (W*0.72, base + 2), (W*0.28, base + 2)], fill=(98, 106, 114))
        d.rectangle([W*0.42, base - H*0.25, W*0.55, base - 3], fill=(124, 132, 140))
        d.rectangle([W*0.47, base - H*0.38, W*0.5, base - H*0.25], fill=SUIE[0])
    else:
        silhouette_ville(d, W, H, base, rnd)
    cadre(d, W, H)
    return im

def plan(W, H, sujet):
    im = Image.new("RGB", (W, H), BLEU_PLAN); d = ImageDraw.Draw(im)
    for x in range(0, W, 4): d.line([(x, 0), (x, H)], fill=BLEU_PLAN2)
    for y in range(0, H, 4): d.line([(0, y), (W, y)], fill=BLEU_PLAN2)
    cx, cy, r = W/2, H/2, min(W, H)*0.32
    if sujet == "engrenage":
        for k in range(10):
            a = 2*math.pi*k/10; x, y = cx + math.cos(a)*r, cy + math.sin(a)*r
            d.rectangle([x-1, y-1, x+1, y+1], outline=TRAIT)
        d.ellipse([cx-r*0.9, cy-r*0.9, cx+r*0.9, cy+r*0.9], outline=TRAIT); d.ellipse([cx-r*0.3, cy-r*0.3, cx+r*0.3, cy+r*0.3], outline=TRAIT)
        d.line([(cx - r*1.2, cy + r*1.2), (cx + r*1.2, cy + r*1.2)], fill=TRAIT)
    elif sujet == "capsule":
        d.rounded_rectangle([cx - r*0.5, cy - r*1.2, cx + r*0.5, cy + r*1.2], radius=max(2, int(r*0.45)), outline=TRAIT)
        d.ellipse([cx - r*0.25, cy - r*0.7, cx + r*0.25, cy - r*0.2], outline=TRAIT)
        d.line([(cx, cy + r*1.2), (cx, H)], fill=TRAIT)
    else:  # locomotive
        d.rectangle([W*0.15, cy - r*0.4, W*0.75, cy + r*0.4], outline=TRAIT); d.rectangle([W*0.6, cy - r*0.9, W*0.85, cy + r*0.4], outline=TRAIT)
        for k in range(3): d.ellipse([W*(0.2 + k*0.18), cy + r*0.3, W*(0.2 + k*0.18) + r*0.6, cy + r*0.9], outline=TRAIT)
    if H >= 32: lignes_texte(d, 3, H - 6, W//2, 1, TRAIT)
    cadre(d, W, H, (12, 30, 60), TRAIT)
    return im

def capsules(W, H):
    im = Image.new("RGB", (W, H), SUIE[1]); d = ImageDraw.Draw(im)
    cw = max(4, W//6); ch = max(8, H//2)
    for row in range(2):
        for k in range(0, W, cw + 2):
            y = H*0.12 + row*(ch*0.75)
            d.rounded_rectangle([k + 1, y, k + cw, y + ch*0.7], radius=max(1, cw//2), fill=LAITON[2], outline=LAITON[0])
            d.ellipse([k + cw*0.3, y + ch*0.12, k + cw*0.75, y + ch*0.28], fill=(40, 30, 60))
    for k in range(0, W, cw + 2): d.line([(k + cw//2, H*0.12 + ch*1.45), (k + cw//2, H)], fill=CUIVRE[1])
    cadre(d, W, H)
    return im

def echo(W, H, graine):
    im = Image.new("RGB", (W, H), (14, 6, 24)); d = ImageDraw.Draw(im); rnd = random.Random(graine)
    cx, cy = W/2, H/2
    for k in range(int(W*H/6)):
        a = rnd.uniform(0, 2*math.pi); r = rnd.uniform(0, min(W, H)/2)
        x, y = cx + math.cos(a + r/6)*r, cy + math.sin(a + r/6)*r
        d.point((x, y), fill=ramp(ECHO, 1 - r/(min(W, H)/2)))
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(250, 230, 255))
    cadre(d, W, H, (40, 20, 60), (110, 60, 160))
    return im

def buste(W, H):
    im = Image.new("RGB", (W, H), (40, 30, 26)); d = ImageDraw.Draw(im)
    for y in range(H): d.line([(0, y), (W, y)], fill=mix((60, 44, 36), (30, 22, 20), y/H))
    s = min(W, H)
    hx, hy = W/2, H*0.42
    d.rectangle([hx - s*0.28, H*0.68, hx + s*0.28, H], fill=LAITON[1])                        # épaules
    d.rectangle([hx - s*0.18, hy - s*0.22, hx + s*0.18, hy + s*0.2], fill=LAITON[3], outline=LAITON[0])   # tête
    d.rectangle([hx - s*0.14, hy - s*0.05, hx + s*0.14, hy], fill=SUIE[0])
    d.point((hx - s*0.08, hy - s*0.03), fill=(255, 170, 60)); d.point((hx + s*0.08, hy - s*0.03), fill=(255, 170, 60))
    d.rectangle([hx - s*0.06, hy + s*0.22, hx + s*0.06, H*0.68], fill=LAITON[0])
    cadre(d, W, H, OR[1], OR[3])
    return im

def engrenages(W, H, graine):
    im = Image.new("RGB", (W, H), (60, 40, 26)); d = ImageDraw.Draw(im); rnd = random.Random(graine)
    for k in range(max(2, W*H//300)):
        cx, cy, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(min(W, H)*0.12, min(W, H)*0.3)
        c = rnd.choice((LAITON[3], LAITON[2], CUIVRE[2], CUIVRE[3]))
        for j in range(10):
            a = 2*math.pi*j/10; x, y = cx + math.cos(a)*r, cy + math.sin(a)*r
            d.rectangle([x - r*0.15, y - r*0.15, x + r*0.15, y + r*0.15], fill=c)
        d.ellipse([cx - r*0.88, cy - r*0.88, cx + r*0.88, cy + r*0.88], fill=c)
        d.ellipse([cx - r*0.3, cy - r*0.3, cx + r*0.3, cy + r*0.3], fill=(40, 26, 16))
    cadre(d, W, H)
    return im

def icone(W, H, n):
    im = Image.new("RGB", (W, H), [CREME, (40, 30, 26), BLEU_PLAN, (14, 6, 24)][n % 4]); d = ImageDraw.Draw(im)
    if n % 4 == 0: roue_couronnee(d, W/2, H/2 + 1, 4.5, fond=CREME)
    elif n % 4 == 1: d.rounded_rectangle([5, 2, 10, 13], radius=2, fill=LAITON[2], outline=LAITON[0]); d.ellipse([6, 4, 9, 7], fill=(80, 50, 120))
    elif n % 4 == 2:
        for j in range(8):
            a = 2*math.pi*j/8; d.point((8 + math.cos(a)*5, 8 + math.sin(a)*5), fill=TRAIT)
        d.ellipse([4, 4, 11, 11], outline=TRAIT)
    else: d.ellipse([5, 5, 10, 10], fill=(200, 140, 250)); d.ellipse([7, 7, 8, 8], fill=(250, 230, 255))
    if n == 4:                                                    # sceau rouge
        d.rectangle([0, 0, W, H], fill=ROUGE); d.ellipse([3, 3, 12, 12], fill=OR[3]); d.ellipse([6, 6, 9, 9], fill=ROUGE2)
    if n == 5:                                                    # visage d'automate
        d.rectangle([0, 0, W, H], fill=(40, 30, 26)); d.rectangle([4, 3, 11, 12], fill=LAITON[3]); d.rectangle([5, 6, 10, 7], fill=SUIE[0])
        d.point((6, 6), fill=(255, 170, 60)); d.point((9, 6), fill=(255, 170, 60))
    if n == 6:                                                    # vanne sur tuyau
        d.rectangle([0, 0, W, H], fill=(60, 44, 32)); d.rectangle([0, 9, 15, 11], fill=CUIVRE[2]); d.line([(7, 9), (7, 5)], fill=FER[3])
        d.ellipse([4, 2, 10, 6], outline=(200, 40, 28))
    if n == 7:                                                    # cristal d'Écho
        d.rectangle([0, 0, W, H], fill=(14, 6, 24)); d.polygon([(8, 2), (11, 8), (8, 13), (5, 8)], fill=(170, 100, 240)); d.line([(8, 3), (8, 12)], fill=(240, 210, 255))
    cadre(d, W, H)
    return im

# ------------------------------------------------------------------ attribution, titres et auteurs
TABLEAUX = {
 # 16 x 16
 "alban": (lambda: icone(16, 16, 0), "La Roue couronnée", "The Crowned Wheel"),
 "aztec": (lambda: icone(16, 16, 1), "Capsule n°4", "Capsule No. 4"),
 "aztec2": (lambda: icone(16, 16, 2), "Croquis de rouage", "Gear Sketch"),
 "bomb": (lambda: icone(16, 16, 3), "Étincelle d'Écho", "Echo Spark"),
 "kebab": (lambda: icone(16, 16, 4), "Sceau de l'Empire", "Seal of the Empire"),
 "meditative": (lambda: icone(16, 16, 5), "Veille", "Vigil"),
 "plant": (lambda: icone(16, 16, 6), "Brouillon", "Draft"),
 "wasteland": (lambda: icone(16, 16, 7), "Résonance", "Resonance"),
 # 16 x 32
 "graham": (lambda: plan(16, 32, "capsule"), "Plan de capsule", "Capsule Blueprint"),
 "prairie_ride": (lambda: affiche(16, 32), "Servez l'Empire", "Serve the Empire"),
 "wanderer": (lambda: buste(16, 32), "L'Ingénieur", "The Engineer"),
 # 32 x 16
 "courbet": (lambda: scene_ciel(32, 16, "train", 1), "La Ligne impériale", "The Imperial Line"),
 "creebet": (lambda: scene_ciel(32, 16, "usine", 2), "Faubourg des forges", "Forge District"),
 "pool": (lambda: scene_ciel(32, 16, "navire", 3), "Le Torpilleur", "The Torpedo Boat"),
 "sea": (lambda: plan(32, 16, "locomotive"), "Étude de locomotive", "Locomotive Study"),
 "sunset": (lambda: scene_ciel(32, 16, "dirigeable", 4), "Crépuscule sur la cité", "Dusk over the City"),
 # 32 x 32
 "baroque": (lambda: affiche(32, 32), "Gloire à l'Airain", "Glory to the Airain"),
 "bust": (lambda: buste(32, 32), "Buste d'automate", "Automaton Bust"),
 "earth": (lambda: echo(32, 32, 5), "L'Écho", "The Echo"),
 "fire": (lambda: scene_ciel(32, 32, "usine", 6), "Les Hauts-Fourneaux", "The Blast Furnaces"),
 "humble": (lambda: plan(32, 32, "engrenage"), "Rouage maître", "Master Gear"),
 "match": (lambda: engrenages(32, 32, 7), "Mécanique", "Mechanism"),
 "skull_and_roses": (lambda: affiche(32, 32, fond=(30, 26, 24), ray=(60, 44, 30)), "Le Grand Transfert", "The Great Transfer"),
 "stage": (lambda: capsules(32, 32), "La Salle des capsules", "The Capsule Hall"),
 "void": (lambda: echo(32, 32, 8), "Le Vide", "The Void"),
 "water": (lambda: scene_ciel(32, 32, "navire", 9), "Les Marées", "The Tides"),
 "wind": (lambda: scene_ciel(32, 32, "dirigeable", 10), "Vents porteurs", "Fair Winds"),
 "wither": (lambda: plan(32, 32, "capsule"), "Prototype", "Prototype"),
 # 48 x 48
 "bouquet": (lambda: engrenages(48, 48, 11), "Engrenages", "Gearworks"),
 "cavebird": (lambda: scene_ciel(48, 48, "dirigeable", 12), "La Flotte du ciel", "The Sky Fleet"),
 "cotan": (lambda: buste(48, 48), "Portrait d'un régulateur", "Portrait of a Regulator"),
 "endboss": (lambda: echo(48, 48, 13), "Le Chœur", "The Choir"),
 "fern": (lambda: plan(48, 48, "engrenage"), "Théorie des rouages", "Theory of Gears"),
 "owlemons": (lambda: affiche(48, 48), "Unis dans le métal", "United in Metal"),
 "sunflowers": (lambda: scene_ciel(48, 48, "usine", 14), "L'Aube industrielle", "Industrial Dawn"),
 "tides": (lambda: scene_ciel(48, 48, "navire", 15), "Gardiens des marées", "Tide Guardians"),
 # 48 x 64
 "backyard": (lambda: affiche(48, 64), "Le Cœur bat pour tous", "The Core Beats for All"),
 "pond": (lambda: capsules(48, 64), "Entrez dans le métal", "Enter the Metal"),
 # 64 x 32
 "changing": (lambda: scene_ciel(64, 32, "train", 16), "Le Grand Express", "The Grand Express"),
 "fighters": (lambda: scene_ciel(64, 32, "dirigeable", 17), "Parade aérienne", "Air Parade"),
 "finding": (lambda: plan(64, 32, "locomotive"), "Plan de la Ligne 9", "Line 9 Blueprint"),
 "lowmist": (lambda: scene_ciel(64, 32, "usine", 18), "Brumes de l'atelier", "Workshop Mists"),
 "passage": (lambda: capsules(64, 32), "Le Passage", "The Passage"),
 # 64 x 48
 "donkey_kong": (lambda: scene_ciel(64, 48, "ville", 19), "La Cité d'Airain", "The Airain City"),
 "skeleton": (lambda: engrenages(64, 48, 20), "La Salle des machines", "The Engine Room"),
 # 64 x 64
 "burning_skull": (lambda: affiche(64, 64, fond=(30, 26, 24), ray=(90, 30, 24)), "L'Empire s'éveille", "The Empire Awakens"),
 "orb": (lambda: echo(64, 64, 21), "Ceux qui dorment dans le métal", "Those Who Sleep in the Metal"),
 "pigscene": (lambda: scene_ciel(64, 64, "dirigeable", 22), "Au-dessus des nuages", "Above the Clouds"),
 "pointer": (lambda: plan(64, 64, "engrenage"), "Le Cœur d'Airain, plan", "Airain's Core, Blueprint"),
 "unpacked": (lambda: affiche(64, 64), "Gloire à l'Empereur", "Glory to the Emperor"),
}
AUTEURS = ["Bureau de la Propagande", "Atelier Vael", "Ministère des Ponts et Rouages", "Cercle des Ingénieurs", "Anonyme réfractaire"]
AUTEURS_EN = ["Propaganda Bureau", "Vael Workshop", "Ministry of Bridges and Gears", "Engineers' Circle", "Anonymous Refractory"]
