"""Gardiens d'airain en panne dans les structures (à lancer après les générateurs). usage : python3 gardiens_structures.py <pack>"""
import os, sys, random, zlib
import nbtlib
from nbtlib import Compound, List, Int, Double, Float, Byte, String

PACK = sys.argv[1]
RAC = os.path.join(PACK, "kubejs/data/kubejs/structure")
# pièce -> nombre de gardiens
CIBLES = {"tour": 1, "centre_fontaine": 1, "centre_horloge": 1, "enceinte_cite_a": 1, "enceinte_a": 1, "depot_caisses": 1}
AUTRES = {"fronts/champ_bataille.nbt": 3, "ruines/grand_relais.nbt": 1, "station/station_observation.nbt": 1}
NON_SOL = ("air", "water", "lava", "leaves", "_slab[type=bottom", "carpet", "snow[", "rail", "torch", "fence", "wall", "pane",
           "bars", "button", "pressure", "sign", "banner", "chain", "lantern", "flower", "short_grass", "tall_grass", "fern", "vine", "ladder", "trapdoor",
           "door", "jigsaw", "structure_void", "candle", "pot", "head", "skull", "bush", "dead_", "lichen", "moss_carpet", "cobweb")

def etat(e):
    s = str(e["Name"])
    if "Properties" in e: s += "[" + ",".join("%s=%s" % (k, v) for k, v in sorted(e["Properties"].items())) + "]"
    return s

def traiter(chemin, n):
    f = nbtlib.load(chemin)
    pal = [etat(e) for e in f["palette"]]
    B = {tuple(int(v) for v in b["pos"]): pal[int(b["state"])] for b in f["blocks"]}
    sx, sy, sz = (int(v) for v in f["size"])
    air = lambda p: B.get(p, "minecraft:air").split("[")[0] in ("minecraft:air", "minecraft:cave_air", "minecraft:structure_void", "minecraft:snow")
    sol = lambda p: (p not in B and p[1] == 0) or (p in B and not any(k in B[p] for k in NON_SOL))
    places = []
    for (x, y, z) in [(x, y, z) for x in range(sx) for y in range(1, sy) for z in range(sz)]:
        if y < 1 or x + 1 >= sx or z + 1 >= sz: continue
        if all(sol((x + dx, y - 1, z + dz)) for dx in (0, 1) for dz in (0, 1)) and \
           all(air((x + dx, y + dy, z + dz)) for dx in (0, 1) for dz in (0, 1) for dy in (0, 1, 2)):
            places.append((x, y, z))
    ents = [e for e in f.get("entities", []) if str(e["nbt"].get("id", "")) != "airain:guardian"]
    R = random.Random(zlib.crc32(chemin.encode()))
    R.shuffle(places)
    places.sort(key=lambda p: p[1])
    pris = []
    for (x, y, z) in places:
        if len(pris) >= n: break
        if any(abs(x - a) < 6 and abs(z - c) < 6 for a, _, c in pris): continue
        pris.append((x, y, z))
        ents.append(Compound({
            "pos": List[Double]([Double(x + 1.0), Double(float(y)), Double(z + 1.0)]),
            "blockPos": List[Int]([Int(x), Int(y), Int(z)]),
            "nbt": Compound({"id": String("airain:guardian"), "Panne": Byte(1), "PersistenceRequired": Byte(1),
                             "Rotation": List[Float]([Float(R.uniform(0, 360)), Float(0.0)])})}))
    f["entities"] = List[Compound](ents)
    f.save(chemin, gzipped=True)
    return len(pris)

total = 0
for climat in os.listdir(os.path.join(RAC, "avant_poste")):
    for nom, n in CIBLES.items():
        c = os.path.join(RAC, "avant_poste", climat, nom + ".nbt")
        if os.path.exists(c):
            k = traiter(c, n); total += k
            if k < n: print("place manquante :", climat, nom, k, "/", n)
for rel, n in AUTRES.items():
    k = traiter(os.path.join(RAC, rel), n); total += k
    if k < n: print("place manquante :", rel, k, "/", n)
print("gardiens placés :", total)
