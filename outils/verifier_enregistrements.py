#!/usr/bin/env python3
"""Vérifie qu'aucun identifiant n'est enregistré deux fois dans le même registre (objets, blocs, entités…).
Un doublon compile sans erreur mais fait planter le jeu et le serveur au lancement (« Duplicate registration »).
Lancé par la CI avant la compilation."""
import re, sys, collections, pathlib
src = "\n".join(p.read_text(encoding="utf-8") for p in pathlib.Path("src/main/java").rglob("*.java"))
erreur = False
for reg in sorted(set(re.findall(r'\b([A-Z_]+)\.register\("', src))):
    ids = re.findall(r'\b' + reg + r'\.register\("([a-z0-9_/]+)"', src)
    for nom, n in collections.Counter(ids).items():
        if n > 1: print(f"ERREUR : {reg} enregistre « {nom} » {n} fois"); erreur = True
print("enregistrements : " + ("DOUBLONS" if erreur else "aucun doublon"))
sys.exit(1 if erreur else 0)
