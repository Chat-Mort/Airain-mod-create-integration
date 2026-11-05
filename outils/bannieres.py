#!/usr/bin/env python3
"""Pose les bannières de l'Empire et des Réfractaires dans les structures déjà écrites (retouches comprises).
À lancer après les générateurs de structures. usage : bannieres.py <pack>"""
import glob, os, sys, nbtlib
from nbtlib import Compound, List, String, Int
P = sys.argv[1]; S = os.path.join(P, "kubejs/data/kubejs/structure")
EMPIRE = [("kubejs:roue_couronnee", "yellow"), ("kubejs:bordure_fine", "orange")]
REFRACTAIRES = [("kubejs:eclat_echo", "purple"), ("kubejs:franges", "purple")]
LIBRE = ("minecraft:air", "minecraft:structure_void", "minecraft:moss_carpet", "minecraft:snow")

class Fichier:
    def __init__(self, f):
        self.f = f; self.n = nbtlib.load(f); self.pal = self.n["palette"]
        self.idx = {tuple(int(v) for v in b["pos"]): i for i, b in enumerate(self.n["blocks"])}
        self.sx, self.sy, self.sz = (int(v) for v in self.n["size"]); self.poses = 0
    def nom(self, p):
        i = self.idx.get(p)
        return None if i is None else str(self.pal[int(self.n["blocks"][i]["state"])]["Name"])
    def libre(self, p): return self.nom(p) in (None,) + LIBRE
    def solide(self, p):
        n = self.nom(p)
        return n is not None and n not in LIBRE and not any(k in n for k in ("banner", "ladder", "rail", "pipe", "bars", "lantern", "slab", "torch"))
    def etat(self, nom, props):
        for i, e in enumerate(self.pal):
            if str(e["Name"]) == nom and dict((k, str(v)) for k, v in e.get("Properties", {}).items()) == props: return i
        self.pal.append(Compound({"Name": String(nom), "Properties": Compound({k: String(v) for k, v in props.items()})}))
        return len(self.pal) - 1
    def poser(self, p, nom, props, motifs):
        be = Compound({"id": String("minecraft:banner"), "patterns": List[Compound](
            [Compound({"pattern": String(m), "color": String(c)}) for m, c in motifs])})
        bloc = Compound({"pos": List[Int]([Int(v) for v in p]), "state": Int(self.etat(nom, props)), "nbt": be})
        if p in self.idx: self.n["blocks"][self.idx[p]] = bloc
        else: self.idx[p] = len(self.n["blocks"]); self.n["blocks"].append(bloc)
        self.poses += 1
    def murale(self, p, face, motifs):              # bannière murale : accrochée au bloc derrière elle
        d = {"north": (0, 0, 1), "south": (0, 0, -1), "east": (-1, 0, 0), "west": (1, 0, 0)}[face]
        appui = (p[0] + d[0], p[1], p[2] + d[2])
        if self.libre(p) and self.libre((p[0], p[1] - 1, p[2])) and self.solide(appui):
            self.poser(p, "minecraft:black_wall_banner", {"facing": face}, motifs)
    def debout(self, p, rotation, motifs):          # bannière sur pied : posée sur un bloc plein
        if self.libre(p) and self.libre((p[0], p[1] + 1, p[2])) and self.solide((p[0], p[1] - 1, p[2])):
            self.poser(p, "minecraft:black_banner", {"rotation": str(rotation)}, motifs)
    def ecrire(self):
        if self.poses: self.n.save(self.f, gzipped=True)
        return self.poses

bilan = {}
def noter(cle, n): bilan[cle] = bilan.get(cle, 0) + n
# --- enceintes : de chaque côté de chaque portail, sur la face intérieure des piliers (repérés par leurs grandes roues)
for f in glob.glob(S + "/avant_poste/*/enceinte_*.nbt"):
    F = Fichier(f); N = F.sx
    roues = [p for p, i in F.idx.items() if "large_cogwheel" in (F.nom(p) or "") and p[1] == 4
             and min(p[0], p[2], N - 1 - p[0], N - 1 - p[2]) == 0]
    vus = set()
    for (x, y, z) in roues:
        if x == 0:            cote, t, axe = "o", z, "z"
        elif x == N - 1:      cote, t, axe = "e", z, "z"
        elif z == 0:          cote, t, axe = "n", x, "x"
        else:                 cote, t, axe = "s", x, "x"
        pair = [r for r in roues if r != (x, y, z) and (r[2] if axe == "z" else r[0]) == t + 6 and
                ((r[0] == x) if axe == "z" else (r[2] == z))]
        if not pair: continue
        c = t + 3
        for tt in (c - 4, c + 4):
            pos = {"n": (tt, 6, 4), "s": (tt, 6, N - 5), "o": (4, 6, tt), "e": (N - 5, 6, tt)}[cote]
            face = {"n": "south", "s": "north", "o": "east", "e": "west"}[cote]
            F.murale(pos, face, EMPIRE)
    noter("portails d'enceinte", F.ecrire())
# --- la place à la fontaine : deux bannières qui encadrent le panneau
for f in glob.glob(S + "/avant_poste/*/centre_fontaine.nbt"):
    F = Fichier(f)
    for x in (5, 9): F.debout((x, 1, 1), 8, EMPIRE)
    noter("places à la fontaine", F.ecrire())
# --- la tour d'horloge : une bannière sous chaque cadran
for f in glob.glob(S + "/avant_poste/*/centre_horloge.nbt"):
    F = Fichier(f)
    for (p, face) in (((12, 10, 9), "north"), ((12, 10, 15), "south"), ((9, 10, 12), "west"), ((15, 10, 12), "east")):
        F.murale(p, face, EMPIRE)
    noter("tour d'horloge", F.ecrire())
# --- les marchés : deux bannières aux piliers du fond
for f in glob.glob(S + "/avant_poste/*/marche.nbt") + glob.glob(S + "/avant_poste/*/marche_c.nbt"):
    F = Fichier(f)
    F.murale((2, 3, 9), "east", EMPIRE); F.murale((8, 3, 9), "west", EMPIRE)
    noter("marchés", F.ecrire())
# --- Réfractaires : à l'entrée des camps et autour du feu, à l'entrée du sanctuaire et devant la tente d'Ada
for f in glob.glob(S + "/refractaires/camp_*.nbt"):
    F = Fichier(f)
    for p in ((11, 1, 26), (15, 1, 26), (13, 1, 8)): F.debout(p, 0, REFRACTAIRES)
    noter("camps réfractaires", F.ecrire())
F = Fichier(S + "/refractaires/sanctuaire.nbt")
for p in ((13, 1, 32), (19, 1, 32), (6, 1, 11), (10, 1, 11)): F.debout(p, 0, REFRACTAIRES)
noter("sanctuaire", F.ecrire())
print("bannières posées :", ", ".join("%s %d" % kv for kv in bilan.items()))
