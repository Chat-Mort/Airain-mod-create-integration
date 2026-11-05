"""Pack de ressources « Airain » : interface en laiton et bronze, titre, panorama, phrases, logo de chargement."""
import os, glob, json, shutil, random
from PIL import Image
SRC = "../mcmeta-assets/assets/minecraft/textures/gui"
OUT = "Airain-Interface"
G = os.path.join(OUT, "assets/minecraft/textures/gui")
# dégradé de luminosité : gris d'origine -> métal de l'Empire
STOPS = [(0, (20, 12, 6)), (40, (42, 26, 12)), (55, (58, 36, 16)), (85, (96, 62, 26)), (115, (110, 74, 34)),
         (139, (122, 84, 40)), (170, (160, 116, 52)), (198, (186, 140, 62)), (230, (230, 192, 104)), (255, (255, 234, 150))]
def metal(l):
    for (a, ca), (b, cb) in zip(STOPS, STOPS[1:]):
        if l <= b:
            t = (l - a) / (b - a) if b > a else 0
            return tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))
    return STOPS[-1][1]
def recolorer(src, dst, grain=True):
    im = Image.open(src).convert("RGBA"); px = im.load(); w, h = im.size
    R = random.Random(hash(os.path.basename(src)) & 0xffff)
    STRIES = [R.choice((-7, -4, -2, 0, 0, 2, 4, 6)) for _ in range(7)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0 or (max(r, g, b) - min(r, g, b) > 14 and "hotbar_selection" not in src): continue          # on ne touche qu'aux gris : les icônes restent
            l = (r + g + b) / 3
            c = metal(l)
            if grain and 150 < l < 215:                                          # métal brossé : stries horizontales
                k = STRIES[y % len(STRIES)] + R.randint(-2, 2); c = tuple(max(0, min(255, v + k)) for v in c)
            px[x, y] = c + (a,)
    if "/container/" in src.replace(os.sep, "/") and "creative_inventory" not in src and w >= 128:
        from ornements import cadre_fenetre
        cadre_fenetre(im)
        habiller(im, os.path.basename(src))
    os.makedirs(os.path.dirname(dst), exist_ok=True); im.save(dst)
# v2 : cases creusées et plaque de titre rivetée. Position de la plaque selon l'endroit où le jeu écrit le titre
# (à gauche par défaut, centré pour certains écrans).
GAUCHE, CENTRE = "g", "c"
PLAQUES = {"generic_54.png": (5, 112), "shulker_box.png": (5, 112), "hopper.png": (5, 112), "enchanting_table.png": (5, 112),
           "crafting_table.png": (26, 100), "inventory.png": (94, 76), "dispenser.png": (CENTRE, 104), "furnace.png": (CENTRE, 104),
           "blast_furnace.png": (CENTRE, 104), "smoker.png": (CENTRE, 104), "brewing_stand.png": (CENTRE, 104)}
def habiller(im, nom):
    px = im.load()
    for y in range(im.height):                                    # intérieur des cases plus sombre : des alvéoles
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and 100 < r < 135 and 70 < g < 95 and b < 55:
                px[x, y] = (int(r * 0.72), int(g * 0.7), int(b * 0.66), 255)
    if nom in PLAQUES:
        x, w = PLAQUES[nom]
        if x == CENTRE: x = (176 - w) // 2
        from ornements import LA, NOIR
        for j in range(11):
            for i in range(w):
                c = LA[3] if j in (0, 10) or i in (0, w - 1) else (LA[1] if j == 1 else LA[2])
                px[x + i, 3 + j] = c + (255,)
        for i in range(w): px[x + i, 14] = NOIR + (255,)
        for (rx, ry) in ((x + 2, 7), (x + w - 4, 7)):            # rivets
            px[rx, ry] = LA[0] + (255,); px[rx + 1, ry] = LA[1] + (255,); px[rx, ry + 1] = LA[2] + (255,); px[rx + 1, ry + 1] = LA[3] + (255,)

def tout():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    n = 0
    motifs = ["container/**/*.png", "sprites/**/*.png", "menu_background.png", "menu_list_background.png", "inworld_menu_background.png",
              "inworld_menu_list_background.png", "header_separator.png", "footer_separator.png", "inworld_header_separator.png",
              "inworld_footer_separator.png", "tab_header_background.png", "recipe_book.png"]
    for m in motifs:
        for f in glob.glob(os.path.join(SRC, m), recursive=True):
            rel = os.path.relpath(f, SRC)
            if rel.startswith(("sprites/icon/", "sprites/realm_status", "sprites/statistics", "sprites/spectator", "sprites/player_list")): continue
            recolorer(f, os.path.join(G, rel)); n += 1
            if os.path.exists(f + ".mcmeta"): shutil.copy(f + ".mcmeta", os.path.join(G, rel) + ".mcmeta")
    # boutons : conduite de cuivre, brides, demi-roues aux bouts (bords de 10 px pour que les roues ne s'étirent pas)
    from ornements import bouton, mcmeta_bouton
    for etat, nom in (("normal", "button"), ("survol", "button_highlighted"), ("off", "button_disabled")):
        d = os.path.join(G, "sprites/widget/%s.png" % nom); bouton(etat).save(d)
        json.dump(mcmeta_bouton(), open(d + ".mcmeta", "w"), indent=2)
    # cases de la table d'enchantement : parchemin bordé de laiton (les couleurs d'origine ne sont pas grises : à refaire)
    def case_ench(fond, clair, sombre, bc, bs, graine):
        r = random.Random(graine); im = Image.new("RGBA", (108, 19)); px = im.load()
        for y in range(19):
            for x in range(108):
                if x == 0 or y == 0: c = bc
                elif x == 107 or y == 18: c = bs
                elif x == 1 or y == 1: c = clair
                elif x == 106 or y == 17: c = sombre
                else:
                    k = r.randint(-5, 5) + (3 if (x * 7 + y * 3) % 23 == 0 else 0); c = tuple(max(0, min(255, v + k)) for v in fond)
                px[x, y] = c + (255,)
        for (x, y) in ((2, 2), (105, 2), (2, 16), (105, 16)): px[x, y] = bc + (255,)
        return im
    E = os.path.join(G, "sprites/container/enchanting_table")
    case_ench((222, 200, 152), (240, 224, 186), (186, 160, 112), (236, 196, 100), (120, 80, 30), 1).save(os.path.join(E, "enchantment_slot.png"))
    case_ench((246, 228, 178), (255, 244, 210), (210, 186, 130), (255, 236, 160), (170, 118, 44), 2).save(os.path.join(E, "enchantment_slot_highlighted.png"))
    case_ench((70, 52, 34), (88, 68, 46), (52, 38, 24), (120, 92, 50), (40, 26, 12), 3).save(os.path.join(E, "enchantment_slot_disabled.png"))
    # (en 1.21.1 les infobulles sont dessinées par le jeu, sans texture : elles gardent leur style d'origine)
    # titre, sous-titre, panorama, logo de chargement, phrases d'accueil
    T = os.path.join(G, "title"); os.makedirs(os.path.join(T, "background"), exist_ok=True)
    titre = Image.new("RGBA", (1024, 256), (0, 0, 0, 0)); l = Image.open("logo_titre_1024.png"); titre.paste(l, (0, 0), l); titre.save(os.path.join(T, "minecraft.png"))
    shutil.copy(os.path.join(SRC, "title/minecraft.png.mcmeta"), os.path.join(T, "minecraft.png.mcmeta"))
    titre.save(os.path.join(T, "minceraft.png")); shutil.copy(os.path.join(SRC, "title/minceraft.png.mcmeta"), os.path.join(T, "minceraft.png.mcmeta"))
    shutil.copy("edition.png", os.path.join(T, "edition.png"))
    shutil.copy("mojangstudios.png", os.path.join(T, "mojangstudios.png"))
    # le fond de l'accueil est l'image de Liam, affichée par FancyMenu (config/fancymenu/assets/fond_accueil.png) : pas de panorama ici
    os.makedirs(os.path.join(OUT, "assets/minecraft/texts"), exist_ok=True); shutil.copy("splashes.txt", os.path.join(OUT, "assets/minecraft/texts/splashes.txt"))
    json.dump({"pack": {"pack_format": 34, "description": "§6The Airain Empire§r · brass interface"}}, open(os.path.join(OUT, "pack.mcmeta"), "w"), ensure_ascii=False, indent=2)
    l.resize((256, 44), Image.NEAREST).crop((40, 0, 216, 44)).resize((128, 128), Image.NEAREST).save(os.path.join(OUT, "pack.png"))
    return n
if __name__ == "__main__":
    print(tout(), "textures d'interface recolorées")
