#!/usr/bin/env python3
"""Donne un uv explicite à chaque face d'élément qui dépasse du bloc et n'en a pas.

Sans uv, Minecraft prend les coordonnées de l'élément : hors de 0..16, il lit la texture voisine dans l'atlas
(les taches vertes/bleues en jeu). On reprend la règle de Minecraft, puis on ramène dans 0..16 par pas de 16
(motif décalé, jamais étiré). Signale aussi les uv de largeur nulle sur une face qui en a une.
Usage : python3 outils/corriger_uv.py [dossier des modèles]
"""
import json, glob, os, sys

def auto(k, f, t):
    x0, y0, z0 = f; x1, y1, z1 = t
    return {"down": [x0, 16 - z1, x1, 16 - z0], "up": [x0, z0, x1, z1],
            "north": [16 - x1, 16 - y1, 16 - x0, 16 - y0], "south": [x0, 16 - y1, x1, 16 - y0],
            "west": [z0, 16 - y1, z1, 16 - y0], "east": [16 - z1, 16 - y1, 16 - z0, 16 - y0]}[k]

def ramene(a, b):
    a, b = sorted((a, b))
    if b - a > 16: return 0, 16
    while a < 0: a, b = a + 16, b + 16
    while b > 16: a, b = a - 16, b - 16
    return a, b

def taille(k, f, t):
    d = [abs(t[i] - f[i]) for i in range(3)]
    return {"north": (d[0], d[1]), "south": (d[0], d[1]), "east": (d[2], d[1]), "west": (d[2], d[1]), "up": (d[0], d[2]), "down": (d[0], d[2])}[k]

racine = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/airain/models')
fichiers = corriges = 0
for p in glob.glob(os.path.join(racine, '**/*.json'), recursive=True):
    m = json.load(open(p)); change = False
    for e in m.get('elements', []):
        f, t = e['from'], e['to']
        dehors = min(f + t) < 0 or max(f + t) > 16
        for k, fc in e.get('faces', {}).items():
            uv = fc.get('uv'); a, b = taille(k, f, t)
            if uv is None and dehors:
                u0, v0, u1, v1 = auto(k, f, t)
                (u0, u1), (v0, v1) = ramene(u0, u1), ramene(v0, v1)
                fc['uv'] = [round(u0, 3), round(v0, 3), round(u1, 3), round(v1, 3)]; change = True; corriges += 1
            elif uv is not None and ((uv[0] == uv[2] and a > 0.01) or (uv[1] == uv[3] and b > 0.01)):
                # uv plat sur une vraie face : on lui rend sa taille, centrée
                a2, b2 = min(16, a), min(16, b)
                u = uv[0] if uv[0] != uv[2] else (16 - a2) / 2; v = uv[1] if uv[1] != uv[3] else (16 - b2) / 2
                fc['uv'] = [round(u, 3), round(v, 3), round(u + (a2 if uv[0] == uv[2] else uv[2] - uv[0]), 3), round(v + (b2 if uv[1] == uv[3] else uv[3] - uv[1]), 3)]
                change = True; corriges += 1
    if change:
        fichiers += 1
        json.dump(m, open(p, 'w'), indent=1, ensure_ascii=False)
print(f"uv corrigés : {corriges} faces dans {fichiers} modèles")
