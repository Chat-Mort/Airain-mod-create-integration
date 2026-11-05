#!/usr/bin/env python3
"""Bannières murales du mod (airain:foundation_wall_banner) dans les camps et le sanctuaire des Réfractaires :
toiles noires ou rouges, cristal ou rouage brisé, usées ou déchirées. Repère des murs pleins avec deux blocs libres
dessous (la toile pend sur deux blocs), espacés d'au moins 6 blocs. À lancer après bannieres.py. usage : bannieres_airain.py <pack>"""
import glob, os, random, sys, nbtlib
from nbtlib import Compound, List, String, Int
P = sys.argv[1]; S = os.path.join(P, "kubejs/data/kubejs/structure/refractaires")
LIBRE = ("minecraft:air", "minecraft:cave_air")
FACES = {"north": (0, 0, 1), "south": (0, 0, -1), "east": (-1, 0, 0), "west": (1, 0, 0)}   # vers le mur

def apparence(fond, orn, motif, forme, partition, fond2, cmotif, etat, lumineux=0):
    """Même rangement que Apparence.pack() / packExt() (réglages du grand étendard à leur défaut)."""
    p = 0 | fond << 4 | orn << 8 | motif << 12 | forme << 16
    ext = partition | ((fond2 - 4) % 8) << 3 | cmotif << 6 | etat << 10 | lumineux << 12
    return p, ext

def toile(r):
    fond = r.choice([3, 3, 0, 5]); motif = r.choice([8, 8, 7])               # noir de fonte / rouge / pourpre ; cristal ou rouage brisé
    return apparence(fond, r.choice([2, 0, 3]), motif, r.choice([0, 2]), r.choice([0, 0, 1, 3, 4]),
                     r.choice([0, 3, 5]), r.choice([0, 10, 10, 5]), r.choice([1, 2, 2]), lumineux=1 if motif == 8 and r.random() < 0.4 else 0)

class Fichier:
    def __init__(self, f):
        self.f = f; self.n = nbtlib.load(f); self.pal = self.n["palette"]
        self.idx = {tuple(int(v) for v in b["pos"]): i for i, b in enumerate(self.n["blocks"])}
        self.sx, self.sy, self.sz = (int(v) for v in self.n["size"])
    def nom(self, p):
        i = self.idx.get(p)
        return None if i is None else str(self.pal[int(self.n["blocks"][i]["state"])]["Name"])
    def libre(self, p):
        return 0 <= p[1] < self.sy and self.nom(p) in LIBRE
    def solide(self, p):
        n = self.nom(p)
        return n is not None and n.startswith("minecraft:") and any(k in n for k in ("log", "planks", "stone", "brick", "wool", "deepslate", "tuff", "mud", "copper", "wood"))
    def etat(self, nom, props):
        for i, e in enumerate(self.pal):
            if str(e["Name"]) == nom and dict((k, str(v)) for k, v in e.get("Properties", {}).items()) == props: return i
        self.pal.append(Compound({"Name": String(nom), "Properties": Compound({k: String(v) for k, v in props.items()})}))
        return len(self.pal) - 1
    def existantes(self):
        return [p for p in self.idx if self.nom(p) == "airain:foundation_wall_banner"]
    def candidats(self):
        out = []
        for (x, y, z) in list(self.idx):
            p = (x, y, z)
            if not self.libre(p) or y < 2: continue
            for face, d in FACES.items():
                mur = (x + d[0], y, z + d[2])
                if self.solide(mur) and self.solide((mur[0], y - 1, mur[2])) and self.libre((x, y - 1, z)) and self.libre((x, y - 2, z)) \
                        and self.libre((x - d[0], y, z - d[2])):
                    out.append((p, face))
        cx, cz = self.sx / 2, self.sz / 2                       # au plus près du cœur du camp
        return sorted(out, key=lambda c: (abs(c[0][0] - cx) + abs(c[0][2] - cz), c))
    def poser(self, p, face, app):
        be = Compound({"id": String("airain:foundation_stone"), "apparence": Int(app[0]), "ext": Int(app[1]),
                       "nom": String(""), "devise": String(""), "rayon": Int(48), "hauteur": Int(6)})
        bloc = Compound({"pos": List[Int]([Int(v) for v in p]), "state": Int(self.etat("airain:foundation_wall_banner", {"facing": face})), "nbt": be})
        if p in self.idx: self.n["blocks"][self.idx[p]] = bloc
        else: self.idx[p] = len(self.n["blocks"]); self.n["blocks"].append(bloc)

def retirer(F):
    air = F.etat("minecraft:air", {})
    for p in F.existantes():
        b = F.n["blocks"][F.idx[p]]; b["state"] = Int(air)
        if "nbt" in b: del b["nbt"]

bilan = []
for f in sorted(glob.glob(S + "/camp_*.nbt") + [S + "/sanctuaire.nbt"]):
    F = Fichier(f); r = random.Random(os.path.basename(f))
    retirer(F)                                              # on repart de zéro à chaque passage
    poses = []; n = 1; maxi = 4 if "sanctuaire" in f else 2
    for p, face in F.candidats():
        if len(poses) >= maxi: break
        if any(abs(p[0] - q[0]) + abs(p[2] - q[2]) < 6 for q in poses): continue
        F.poser(p, face, toile(r)); poses.append(p); n += 1
    if n: F.n.save(f, gzipped=True)
    bilan.append("%s %d" % (os.path.basename(f)[:-4], len(poses)))
print("bannières réfractaires :", ", ".join(bilan))
