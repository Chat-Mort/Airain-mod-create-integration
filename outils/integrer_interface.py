#!/usr/bin/env python3
"""Copie le thème de l'Empire (accueil/Airain-Interface) dans kubejs/assets/minecraft du pack. usage : integrer_interface.py <pack>"""
import os, shutil, sys
P = sys.argv[1]
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accueil/Airain-Interface/assets/minecraft")
DST = os.path.join(P, "kubejs/assets/minecraft")
for sous in ("textures/gui", "texts"):
    d = os.path.join(DST, sous)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(SRC, sous), d)
n = sum(len(f) for _, _, f in os.walk(os.path.join(DST, "textures/gui")))
print("thème de l'Empire :", n, "fichiers d'interface")
