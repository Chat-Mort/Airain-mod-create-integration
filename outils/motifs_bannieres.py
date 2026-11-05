#!/usr/bin/env python3
"""Motifs de bannière sur mesure (1.21.1 : registre banner_pattern), textures bannière + bouclier, noms traduits.
usage : motifs_bannieres.py <pack>"""
import json, os, sys
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "embleme"))
from emblemes3 import J_couronne, E_eclat, bordure, franges, centrer, W, H
P = sys.argv[1]
_A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcmeta-assets/assets/minecraft/textures/entity")
GRAIN_B = Image.open(os.path.join(_A, "banner/base.png")).convert("RGBA")      # le grain du tissu d'origine
GRAIN_S = Image.open(os.path.join(_A, "shield/base.png")).convert("RGBA")
MOTIFS = {
    "roue_couronnee": (centrer(J_couronne()), "Roue couronnée", "Crowned Wheel"),
    "eclat_echo": (centrer(E_eclat()), "Éclat d'Écho", "Echo Shard"),
    "bordure_fine": (bordure(), "Bordure fine", "Thin Border"),
    "franges": (franges(), "Franges", "Fringe"),
}
COULEURS = {"white": ("blanc", "White"), "orange": ("orange", "Orange"), "magenta": ("magenta", "Magenta"),
            "light_blue": ("bleu clair", "Light Blue"), "yellow": ("jaune", "Yellow"), "lime": ("vert clair", "Lime"),
            "pink": ("rose", "Pink"), "gray": ("gris", "Gray"), "light_gray": ("gris clair", "Light Gray"), "cyan": ("cyan", "Cyan"),
            "purple": ("violet", "Purple"), "blue": ("bleu", "Blue"), "brown": ("marron", "Brown"), "green": ("vert", "Green"),
            "red": ("rouge", "Red"), "black": ("noir", "Black")}
def ecrire(rel, obj):
    f = os.path.join(P, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)
lang = {"fr_fr": {}, "en_us": {}}
for nom, (m, fr, en) in MOTIFS.items():
    ecrire("kubejs/data/kubejs/banner_pattern/%s.json" % nom,
           {"asset_id": "kubejs:" + nom, "translation_key": "block.kubejs.banner." + nom})
    # bannière : face avant (x 1-20, y 1-40) et face arrière (x 22-41), en blanc, la couleur vient de la teinture
    b = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            if m[y][x]:
                for (px, py) in ((1 + x, 1 + y), (22 + (W - 1 - x), 1 + y)):
                    g = GRAIN_B.getpixel((px, py)); b.putpixel((px, py), (g[0], g[1], g[2], 255))
    d = os.path.join(P, "kubejs/assets/kubejs/textures/entity/banner"); os.makedirs(d, exist_ok=True); b.save(os.path.join(d, nom + ".png"))
    # bouclier : face 10 × 20 en (2, 2), réduction 2:1 (un pixel plein si au moins 2 des 4 le sont)
    s = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for y in range(20):
        for x in range(10):
            n = sum(m[2 * y + j][2 * x + i] for i in (0, 1) for j in (0, 1))
            if n >= 2:
                g = GRAIN_S.getpixel((2 + x, 2 + y)); s.putpixel((2 + x, 2 + y), (g[0], g[1], g[2], 255))
    d = os.path.join(P, "kubejs/assets/kubejs/textures/entity/shield"); os.makedirs(d, exist_ok=True); s.save(os.path.join(d, nom + ".png"))
    for c, (cfr, cen) in COULEURS.items():
        lang["fr_fr"]["block.kubejs.banner.%s.%s" % (nom, c)] = "%s %s" % (fr, cfr)
        lang["en_us"]["block.kubejs.banner.%s.%s" % (nom, c)] = "%s %s" % (cen, en)
# les quatre motifs se tissent au métier sans objet de motif : les joueurs peuvent pavoiser leur base
ecrire("kubejs/data/minecraft/tags/banner_pattern/no_item_required.json",
       {"replace": False, "values": ["kubejs:" + n for n in MOTIFS]})
L = os.path.join(P, "kubejs/assets/kubejs/lang")
for code, t in lang.items():
    f = os.path.join(L, code + ".json"); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print(len(MOTIFS), "motifs de bannière")
