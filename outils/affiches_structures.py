"""Affiches de propagande de l'Empire accrochées aux murs des avant-postes et des cités (après les générateurs).
usage : python3 affiches_structures.py <pack>"""
import os, sys, random, zlib
import nbtlib
from nbtlib import Compound, List, Int, Double, Float, Byte, String

PACK = sys.argv[1]
RAC = os.path.join(PACK, "kubejs/data/kubejs/structure/avant_poste")
AFFICHES = ["coeur_attend", "un_moteur", "echo_interdit", "fondateur", "capsule"]
PIECES = ["centre_fontaine", "centre_horloge", "marche", "marche_c", "dortoir", "dortoir_c", "entrepot", "entrepot_c",
          "atelier", "atelier_c", "kiosque_c", "grand_marche_c", "carrefour_c", "salle_cuivre", "salle_laiton_c", "enceinte_cite_a"]
# direction vers laquelle l'affiche regarde : (dx, dz, valeur 2D, sens anti-horaire (dx, dz))
DIRS = {"sud": (0, 1, 0, (1, 0)), "ouest": (-1, 0, 1, (0, 1)), "nord": (0, -1, 2, (-1, 0)), "est": (1, 0, 3, (0, -1))}
NON_MUR = ("air", "glass", "pane", "bars", "fence", "door", "trapdoor", "slab", "stairs", "leaves", "sign", "banner", "torch",
           "lantern", "chain", "rail", "carpet", "button", "lever", "vine", "ladder", "wall", "jigsaw", "structure_void", "water")

def etat(e):
    s = str(e["Name"])
    if "Properties" in e: s += "[" + ",".join("%s=%s" % (k, v) for k, v in sorted(e["Properties"].items())) + "]"
    return s

def traiter(chemin, graine):
    f = nbtlib.load(chemin)
    pal = [etat(e) for e in f["palette"]]
    B = {tuple(int(v) for v in b["pos"]): pal[int(b["state"])] for b in f["blocks"]}
    air = lambda p: B.get(p, "").split("[")[0] in ("minecraft:air", "minecraft:cave_air")
    mur = lambda p: p in B and not any(k in B[p] for k in NON_MUR)
    places = []
    for (x, y, z) in B:
        if y < 2: continue
        for nom, (dx, dz, v, (cx, cz)) in DIRS.items():
            # l'affiche occupe l'ancre et la case anti-horaire, sur trois rangs (y-1..y+1) ; le mur est derrière (-direction)
            cases = [(x + i * cx, y + j, z + i * cz) for i in (0, 1) for j in (-1, 0, 1)]
            if all(air(c) and mur((c[0] - dx, c[1], c[2] - dz)) and air((c[0] + dx, c[1], c[2] + dz)) for c in cases) \
               and mur((x - dx, y - 2, z - dz)) is not None:
                places.append((x, y, z, v))
    ents = [e for e in f.get("entities", []) if not str(e["nbt"].get("variant", "")).startswith("airain:affiche_")]
    if not places:
        f["entities"] = List[Compound](ents); f.save(chemin, gzipped=True); return 0
    R = random.Random(zlib.crc32(chemin.encode()))
    places.sort(key=lambda p: (p[1], p[0], p[2]))
    x, y, z, v = R.choice(places[:max(1, len(places) // 2)])     # plutôt bas, à hauteur d'yeux
    ents.append(Compound({
        "pos": List[Double]([Double(x + 0.5), Double(y + 0.5), Double(z + 0.5)]),
        "blockPos": List[Int]([Int(x), Int(y), Int(z)]),
        "nbt": Compound({"id": String("minecraft:painting"), "variant": String("airain:affiche_" + AFFICHES[graine % len(AFFICHES)]),
                         "facing": Byte(v), "Rotation": List[Float]([Float(0.0), Float(0.0)])})}))
    f["entities"] = List[Compound](ents)
    f.save(chemin, gzipped=True)
    return 1

total = 0
for i, climat in enumerate(sorted(os.listdir(RAC))):
    for j, nom in enumerate(PIECES):
        c = os.path.join(RAC, climat, nom + ".nbt")
        if os.path.exists(c): total += traiter(c, i + j)
print("affiches posées :", total)
