#!/usr/bin/env python3
"""Musiques du pack : remplace la musique du menu, ajoute nos morceaux aux listes de Minecraft en jeu.
usage : musique.py <dossier du pack>"""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
van = json.load(open(os.path.join(H, "mcmeta-assets/assets/minecraft/sounds.json")))
SOUTERRAIN = {"music.overworld.deep_dark", "music.overworld.dripstone_caves", "music.overworld.lush_caves"}
# morceau : (fichier, listes où il joue, part visée dans chaque liste)
MORCEAUX = {
    "main_theme": {"menu": True, "surface": 0.25},      # à la surface : nos deux morceaux, un sur cinq chacun
    "alone": {"surface": 0.25},
    "echoing_voices": {"end": 0.34},
    "almost_safe": {"end": 0.34},                        # End : nos deux morceaux et celui de Minecraft, un tiers chacun
    "hells_guards": {"nether": 0.35},                    # Nether (tous les biomes)
}
S = {}
for nom, regle in MORCEAUX.items():
    son = lambda poids=1: {"name": "kubejs:music/" + nom, "stream": True, "weight": poids}
    if regle.get("menu"):
        S["music.menu"] = {"replace": True, "sounds": [son()]}
    part = regle.get("surface")
    if part:
        for ev in ["music.game", "music.creative"] + [k for k in van if k.startswith("music.overworld.") and k not in SOUTERRAIN]:
            n = sum(s.get("weight", 1) if isinstance(s, dict) else 1 for s in van[ev]["sounds"])
            poids = max(1, round(n * part / (1 - part)))
            S.setdefault(ev, {"replace": False, "sounds": []})["sounds"].append(son(poids))
    part = regle.get("nether")
    if part:
        for ev in [k for k in van if k.startswith("music.nether.")]:
            n = sum(s.get("weight", 1) if isinstance(s, dict) else 1 for s in van[ev]["sounds"])
            poids = max(1, round(n * part / (1 - part)))
            S.setdefault(ev, {"replace": False, "sounds": []})["sounds"].append(son(poids))
    part = regle.get("end")
    if part:
        for ev in ["music.end"]:
            n = sum(s.get("weight", 1) if isinstance(s, dict) else 1 for s in van[ev]["sounds"])
            poids = max(1, round(n * part / (1 - part)))
            S.setdefault(ev, {"replace": False, "sounds": []})["sounds"].append(son(poids))
d = os.path.join(sys.argv[1], "kubejs/assets/minecraft"); os.makedirs(d, exist_ok=True)
json.dump(S, open(os.path.join(d, "sounds.json"), "w"), indent=2)
# thèmes de l'histoire : un événement chacun dans l'espace kubejs (le mod les joue)
THEMES = ["mechanical_love", "epilogue"]
json.dump({t: {"sounds": [{"name": "kubejs:music/" + t, "stream": True}]} for t in THEMES},
          open(os.path.join(sys.argv[1], "kubejs/assets/kubejs/sounds.json"), "w"), indent=2)
print(len(S), "listes modifiées,", len(THEMES), "thème(s)")
