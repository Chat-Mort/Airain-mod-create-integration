#!/usr/bin/env python3
"""Supprime le scintillement (z-fighting) à l'intérieur des modèles : deux faces tournées du même côté, dans le même
plan, qui se recouvrent (une barre qui traverse un poteau, un cadre posé sur une dalle…).

Pour chaque paire, le plus gros des deux éléments recule cette face de 0,02 px : le plus petit (le détail) passe devant.
Les éléments tournés sont laissés tels quels. Relancer le script ne change plus rien.
Usage : python3 outils/corriger_zfight.py [dossier des modèles]
"""
import json, glob, os, sys

AXE = {'north': (2, 0), 'south': (2, 1), 'west': (0, 0), 'east': (0, 1), 'down': (1, 0), 'up': (1, 1)}
RECUL = 0.02

def plan(e, k):
    ax, cote = AXE[k]
    return ax, cote, (e['to'] if cote else e['from'])[ax]

def rect(e, ax):
    o = [i for i in range(3) if i != ax]
    f, t = e['from'], e['to']
    return (min(f[o[0]], t[o[0]]), max(f[o[0]], t[o[0]]), min(f[o[1]], t[o[1]]), max(f[o[1]], t[o[1]]))

def recouvre(a, b):
    return min(a[1], b[1]) - max(a[0], b[0]) > 0.01 and min(a[3], b[3]) - max(a[2], b[2]) > 0.01

def volume(e):
    v = 1
    for i in range(3): v *= abs(e['to'][i] - e['from'][i])
    return v

def corriger(m):
    E = [e for e in m.get('elements', []) if not e.get('rotation') or e['rotation'].get('angle', 0) == 0]
    n = 0
    for _ in range(4):                      # quelques passes : un recul peut en révéler un autre
        fait = 0
        for i, a in enumerate(E):
            for b in E[i + 1:]:
                for k in set(a.get('faces', {})) & set(b.get('faces', {})):
                    ax, cote, pa = plan(a, k)
                    _, _, pb = plan(b, k)
                    if abs(pa - pb) > 0.001 or not recouvre(rect(a, ax), rect(b, ax)): continue
                    gros = a if volume(a) >= volume(b) else b
                    epais = abs(gros['to'][ax] - gros['from'][ax])
                    if epais <= RECUL * 2: continue
                    if cote: gros['to'][ax] = round(gros['to'][ax] - RECUL, 4)
                    else: gros['from'][ax] = round(gros['from'][ax] + RECUL, 4)
                    fait += 1
        n += fait
        if not fait: break
    return n

racine = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/airain/models')
total = fichiers = 0
for p in glob.glob(os.path.join(racine, '**/*.json'), recursive=True):
    m = json.load(open(p))
    n = corriger(m)
    if n:
        json.dump(m, open(p, 'w'), indent=1, ensure_ascii=False)
        total += n; fichiers += 1
print(f"z-fighting : {total} faces reculées dans {fichiers} modèles")
