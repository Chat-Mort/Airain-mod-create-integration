import sys
sys.path.insert(0, "../apercu_etendard")
from PIL import Image
from police import texte, largeur
import gui
RES = gui.RES
SP = Image.open(RES + "elements.png")
def sprite(im, sx, sy, w, h, x, y): im.alpha_composite(SP.crop((sx, sy, sx + w, sy + h)), (x, y))
BRUN = (58, 34, 14); CREME = (255, 233, 176); GRISE = (138, 128, 112)

def ecran_etendard(page):
    fond = Image.open(RES + "etendard.png").crop((0, 0, 310, 226))
    W, H = 330, 262
    im = Image.new("RGBA", (W, H), (34, 30, 30, 255))
    ox, oy = 10, 26                                     # panneau ; contenu à +10
    # onglets au-dessus
    for i, nom in enumerate(("General", "Toile", "Mat")):
        actif = i == page
        sprite(im, 0, 32 if actif else 48, 72, 16, ox + 14 + i * 74, oy - 13)
        texte(im, ox + 14 + i * 74 + 36, oy - 9, nom, BRUN if actif else (70, 50, 30), centre=True)
    im.alpha_composite(fond, (ox, oy))
    x, y = ox + 10, oy + 10
    texte(im, x + 4, y - 4, "Grand etendard : toile" if page == 1 else "Grand etendard : general", BRUN)
    lignes = [("Fond", "Rouge imperial"), ("Partition", "Coupe"), ("2e couleur", "Ivoire"), ("Ornements", "Or"), ("Motif", "Rouage"),
              ("Couleur motif", "Argent"), ("Forme du bas", "Queue d'aronde"), ("Etat", "Usee"), ("Broderie", "Lumineuse")]
    if page == 0:
        # champs de saisie
        for (yy, val, lab) in ((14, "Factory", None), (48, "Fondation de l'Empire", "Devise (sous le nom)")):
            if lab: texte(im, x, y + yy - 10, lab, BRUN)
            d = im.load()
            for j in range(20):
                for i in range(190):
                    c = (40, 26, 12) if 0 < i < 189 and 0 < j < 19 else (96, 62, 22)
                    if j == 19 or i == 189: c = (230, 192, 104)
                    d[x + i, y + yy + j] = c + (255,)
            texte(im, x + 5, y + yy + 6, val, CREME)
        lignes = [("Style", "Potence"), ("Hauteur du mat", "6 blocs"), ("Titre", "Affiche")]
        base, pas = 76, 21
    else:
        base, pas = 14, 18
    for n, (lab, val) in enumerate(lignes):
        ly = y + base + n * pas
        texte(im, x, ly + 6, lab, BRUN)
        sprite(im, 0, 16, 16, 16, x + 78, ly + 2); sprite(im, 16 if n != 1 else 48, 16, 16, 16, x + 186, ly + 2)
        d = im.load()
        for j in range(16):
            for i in range(88):
                c = (40, 26, 12)
                if j == 0 or i == 0: c = (96, 62, 22)
                if j == 15 or i == 87: c = (230, 192, 104)
                d[x + 96 + i, ly + 2 + j] = c + (255,)
        texte(im, x + 140, ly + 6, val, CREME, centre=True)
    # aperçu dans la vitrine
    sys.argv = ["x"]
    import rendu
    o = dict(fond=0, fond2=4, partition=1, orn=0, cmotif=0xD8DCE0, motif="rouage", forme=0, etat=1)
    t = rendu.toile(o).resize((56, 112), Image.NEAREST)
    im.alpha_composite(t, (ox + 222 + 40 - 28, oy + 16 + 18))
    # boutons du thème
    bout = Image.open("../accueil/bouton_normal.png").convert("RGBA")
    for i, lab in enumerate(("Valider", "Annuler")):
        b = bout.resize((94, 20)) if bout.size != (94, 20) else bout
        b = nine(bout, 94, 20); im.alpha_composite(b, (x + i * 96, y + 190))
        texte(im, x + i * 96 + 47, y + 196, lab, (255, 255, 255), ombre=True, centre=True)
    return im

def nine(src, w, h, L=10, T=3):
    src = src.convert("RGBA"); sw, sh = src.size
    if sw > 200: src = src.resize((200, 20), Image.NEAREST); sw, sh = 200, 20
    out = Image.new("RGBA", (w, h))
    out.paste(src.crop((0, 0, L, sh)), (0, 0)); out.paste(src.crop((sw - L, 0, sw, sh)), (w - L, 0))
    out.paste(src.crop((L, 0, L + (w - 2 * L), sh)), (L, 0))
    return out

def ecran_table():
    fond = Image.open(RES + "table_empire.png").crop((0, 0, 232, 222))
    im = Image.new("RGBA", (252, 242), (34, 30, 30, 255)); ox, oy = 10, 10
    im.alpha_composite(fond, (ox, oy))
    texte(im, ox + 10, oy + 6, "Table de l'Empire", BRUN)
    texte(im, ox + 35, oy + 129, "Inventaire", BRUN)
    ench = [("Efficacite", 5, 5, 3), ("Solidite", 3, 4, 3), ("Fortune", 3, 3, 1), ("Toucher de soie", 1, 1, 0), ("Reparation", 1, 1, 1), ("Malediction", 0, 0, 0)]
    d = im.load()
    for i, (nom, mx, tome, dispo) in enumerate(ench[:5]):
        y = oy + 18 + i * 18
        for yy in range(y + 1, y + 17):
            for xx in range(ox + 51, ox + 225):
                d[xx, yy] = ((62, 42, 22) if i != 1 else (82, 58, 30)) + (255,)
        for xx in range(ox + 51, ox + 225): d[xx, y + 17] = (40, 26, 12, 255)
        texte(im, ox + 54, y + 5, nom, (240, 220, 170))
        nmax = tome if tome > mx else mx
        for n in range(1, nmax + 1):
            bx = ox + 50 + 176 - (nmax - n + 1) * 16 - 2
            t = n > mx
            etat = (3 if dispo >= n else 5) if t else (0 if n <= dispo else 2)
            if i == 1 and n == 2: etat = 1
            sprite(im, etat * 16, 0, 15, 14, bx, y + 2)
            r = ["I", "II", "III", "IV", "V"][n - 1]
            texte(im, bx + 8, y + 5, r, (58, 34, 14) if etat in (0, 1, 3, 4) else (150, 140, 120), centre=True)
    return im

E = ecran_etendard(1).resize((990, 786), Image.NEAREST)
E0 = ecran_etendard(0).resize((990, 786), Image.NEAREST)
T = ecran_table().resize((756, 726), Image.NEAREST)
pl = Image.new("RGBA", (990 * 2 + 30, 786 + 30 + 726), (24, 22, 24, 255))
pl.alpha_composite(E0, (0, 0)); pl.alpha_composite(E, (1020, 0)); pl.alpha_composite(T, ((pl.width - 756) // 2, 816))
pl.save("/home/claude/apercus/gui_empire.png"); print("ok")
