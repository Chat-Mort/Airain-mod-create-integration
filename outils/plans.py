#!/usr/bin/env python3
"""Plans de l'Empire : schémas de Create (format structure vanilla) vendus au bureau d'études.
Écrit <pack>/schematics/airain_<plan>.nbt (client) et <pack>/schematics/uploaded/airain/airain_<plan>.nbt (serveur).
usage : plans.py <pack>"""
import os, shutil, sys
from pieces import Piece, AIR, panneau
P = sys.argv[1]
OUT = os.path.join(P, "schematics"); SRV = os.path.join(OUT, "uploaded", "airain")
os.makedirs(SRV, exist_ok=True)
plans = []
def plan(nom, sx, sy, sz):
    pc = Piece("airain:airain_" + nom, sx, sy, sz, fond=AIR); plans.append(pc); return pc
PIERRE = "minecraft:stone_bricks"; DALLE = "minecraft:polished_andesite"
def sh(axe): return "create:shaft[axis=%s,waterlogged=false]" % axe
def cog(axe): return "create:cogwheel[axis=%s,waterlogged=false]" % axe

# ------------------------------------------------ 1. Moulin à vent : 17 voiles en croix sur un roulement, arbre de sortie à l'arrière.
# Clic droit sur le roulement pour l'assembler. Sortie : l'arbre au bout du mât (axe nord-sud).
m = plan("moulin_vent", 9, 9, 4)
for y in range(0, 4): m.put(4, y, 1, PIERRE)                       # le mât
m.box(3, 0, 1, 5, 0, 3, DALLE)
m.put(4, 4, 1, "create:windmill_bearing[facing=north]")
for k in range(-4, 5):
    m.put(4 + k, 4, 0, "create:white_sail[facing=north]")
    m.put(4, 4 + k, 0, "create:white_sail[facing=north]")
for z in (2, 3): m.put(4, 4, z, sh("z"))
m.put(4, 3, 3, PIERRE); m.put(4, 3, 2, PIERRE)
m.put(*(5, 1, 2), *panneau("airain.plan.signe.sortie", face="east", couleur="black"))

# ------------------------------------------------ 2. Centrale à roues : six roues à eau sur un même arbre, un canal à remplir d'eau.
# Versez un seau d'eau sur chaque case marquée de la rangée du haut (au nord) : l'eau coule vers le sud par-dessus les roues.
c = plan("centrale_roues", 10, 4, 5)
for x in range(1, 9):
    for z in range(0, 5): c.put(x, 0, z, PIERRE)
for x in range(1, 7):
    c.put(x, 1, 2, "create:water_wheel[facing=east,waterlogged=false]")
    c.put(x, 1, 1, PIERRE)                       # appui de la source d'eau
    c.put(x, 1, 3, PIERRE)                       # l'eau passe au-dessus et retombe plus loin
    c.put(x, 2, 0, "minecraft:stone_brick_wall") # rebord derrière les sources
for z in range(0, 5):
    c.put(0, 1, z, PIERRE); c.put(0, 2, z, PIERRE); c.put(7, 2, z, PIERRE)
c.put(7, 1, 2, sh("x")); c.put(8, 1, 2, sh("x")); c.put(9, 1, 2, sh("x"))
c.put(7, 1, 1, PIERRE); c.put(7, 1, 3, PIERRE)
c.put(*(8, 2, 1), *panneau("airain.plan.signe.eau", face="north", couleur="blue"))

# ------------------------------------------------ 3. Meunerie : trois meules alimentées par une rangée de rouages ; coffres d'entrée
# au-dessus (entonnoirs), entonnoirs de sortie dessous vers un coffre commun. Force : l'arbre vertical sous le premier rouage.
u = plan("meunerie", 6, 5, 4)
for x in range(0, 6):
    for z in range(0, 4): u.put(x, 0, z, DALLE)
for x in (1, 2, 3):
    u.put(x, 2, 1, "create:millstone")
    u.put(x, 3, 1, "minecraft:hopper[enabled=true,facing=down]")
    u.put(x, 4, 1, "minecraft:chest[facing=south,type=single,waterlogged=false]")
    u.put(x, 1, 1, "minecraft:hopper[enabled=true,facing=east]")
    u.put(x, 2, 2, cog("y"))
u.put(4, 1, 1, "minecraft:chest[facing=south,type=single,waterlogged=false]")
u.put(0, 2, 2, cog("y")); u.put(0, 1, 2, sh("y"))
u.put(*(0, 1, 3), *panneau("airain.plan.signe.force", face="south", couleur="black"))

for pc in plans:
    pc.ecrire(OUT)
    f = pc.nom.split(":")[-1] + ".nbt"
    shutil.copy(os.path.join(OUT, f), os.path.join(SRV, f))
print("plans :", ", ".join(pc.nom.split(":")[-1] for pc in plans))
