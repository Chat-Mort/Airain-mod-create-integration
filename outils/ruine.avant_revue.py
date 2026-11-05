#!/usr/bin/env python3
"""Ruine isolée n°1 : l'atelier effondré. Écrit deux .nbt (avec / sans coffre) + JSON pour les aperçus."""
import json, random, sys, os
import nbtlib
from nbtlib import Compound, List, Int, String
OUT = sys.argv[1]
SX, SY, SZ = 13, 8, 11          # y=0 : fondations enterrées d'un bloc
VOID = "minecraft:structure_void"

def construire(avec_coffre):
    random.seed(11)
    B = {}
    def put(x, y, z, s, nbt=None): B[(x, y, z)] = (s, nbt)
    def r(p): return random.random() < p
    # tout est vide par défaut : le terrain autour reste intact
    for x in range(SX):
        for y in range(SY):
            for z in range(SZ):
                put(x, y, z, VOID)
    # -------- dalle (y=0), partiellement arrachée ; à l'intérieur de l'atelier on vide l'air au-dessus
    SOL = ["minecraft:polished_tuff"] * 5 + ["minecraft:tuff_bricks", "minecraft:cracked_deepslate_tiles", "minecraft:tuff", "minecraft:coarse_dirt", "minecraft:gravel"]
    for x in range(1, 12):
        for z in range(1, 10):
            bord = x in (1, 11) or z in (1, 9)
            if bord and r(0.35):
                continue                       # dalle effritée sur les bords
            put(x, 0, z, random.choice(SOL))
            for y in range(1, 6):
                put(x, y, z, "minecraft:air")
    # -------- murs : nord (z=1) haut, ouest (x=1) à moitié, est en moignons ; sud disparu
    # style de l'Empire : socle de tuf sur 2 blocs, puis plaques de cuivre et de fer
    SOCLE = ["minecraft:tuff_bricks"] * 4 + ["minecraft:mossy_cobblestone", "minecraft:polished_tuff"]
    PLAQ = ["minecraft:weathered_copper", "minecraft:oxidized_copper", "minecraft:weathered_cut_copper", "create:weathered_iron_block", "create:weathered_iron_block"]
    def mur(y): return random.choice(SOCLE if y <= 2 else PLAQ)
    haut_nord = [5, 5, 4, 5, 3, 4, 5, 2, 3, 1, 2]           # profil cassé, x=1..11
    for i, x in enumerate(range(1, 12)):
        for y in range(1, haut_nord[i] + 1):
            put(x, y, 1, mur(y))
    for z in range(2, 10):
        h = [4, 4, 3, 3, 2, 2, 1, 0][z - 2]
        for y in range(1, h + 1):
            put(1, y, z, mur(y))
    for z, h in ((2, 2), (3, 1), (6, 1)):
        for y in range(1, h + 1):
            put(11, y, z, mur(y))
    # verrières de fonte du mur nord, l'une brisée
    put(4, 3, 1, "create:industrial_iron_window")
    put(7, 3, 1, "minecraft:air"); put(7, 2, 1, "minecraft:air")
    # conduite qui longe le mur nord côté intérieur, arrachée au milieu
    for x in range(2, 11):
        if x not in (6, 7):
            put(x, 4, 2, "create:fluid_pipe[down=false,east=true,north=false,south=false,up=false,west=true,waterlogged=false]")
    # montants de fonte aux angles, une poutre de fer tombée en travers
    for y in range(1, 6):
        put(1, y, 1, "create:industrial_iron_block")
    for y in range(1, 4):
        put(11, y, 1, "create:industrial_iron_block")
    for y in range(1, 3):
        put(1, y, 9, "create:industrial_iron_block")
    for x in range(2, 5):
        put(x, 5, 1 if x < 4 else 2, "create:weathered_iron_block")
    for x in range(5, 9):
        put(x, 1, 8, "create:weathered_iron_block")    # poutre effondrée au sol
    put(3, 1, 8, "create:weathered_copper_shingle_slab[type=bottom,waterlogged=false]")   # morceaux de toit
    put(9, 1, 7, "create:oxidized_copper_shingle_slab[type=bottom,waterlogged=false]")
    # -------- la machine : une chaudière de cuivre oxydé avec sa grande roue dentée
    for x in range(6, 9):
        for z in range(3, 6):
            for y in range(1, 4):
                coin = x in (6, 8) and z in (3, 5)
                s = "minecraft:oxidized_cut_copper" if coin else "minecraft:oxidized_copper"
                if y == 3 and coin and r(0.5):
                    s = "minecraft:air"
                put(x, y, z, s)
    put(7, 2, 6, "minecraft:oxidized_copper_grate[waterlogged=false]")            # foyer
    put(7, 1, 6, "minecraft:oxidized_copper_trapdoor[facing=south,half=bottom,open=true,powered=false,waterlogged=false]")
    put(7, 4, 4, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")   # cheminée
    put(7, 5, 4, "minecraft:chain[axis=y,waterlogged=false]")
    put(9, 2, 4, "create:large_cogwheel[axis=x]")                                     # roue sur le flanc est
    put(10, 2, 4, "create:shaft[axis=x]")
    put(5, 1, 4, "create:andesite_casing"); put(5, 2, 4, "create:shaft[axis=y]")
    put(5, 1, 3, "minecraft:oxidized_cut_copper_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]")
    put(8, 1, 7, "create:cogwheel[axis=y]")                                            # rouage tombé
    put(3, 1, 3, "minecraft:waxed_oxidized_copper_bulb[lit=false,powered=false]")
    # -------- établi et débris
    put(2, 1, 2, "minecraft:crafting_table")
    put(3, 1, 2, "minecraft:spruce_slab[type=bottom,waterlogged=false]")
    put(2, 1, 5, "minecraft:cobbled_deepslate"); put(2, 1, 6, "minecraft:tuff_slab[type=bottom,waterlogged=false]")
    put(4, 1, 7, "minecraft:tuff_slab[type=bottom,waterlogged=false]")
    put(10, 1, 8, "minecraft:cobbled_deepslate"); put(10, 2, 8, "minecraft:tuff_slab[type=bottom,waterlogged=false]")
    for p in [(2, 4, 2), (10, 3, 3), (6, 4, 2), (2, 1, 8)]:
        put(*p, "minecraft:cobweb")
    for x in range(1, 12):
        for z in range(1, 10):
            if B[(x, 1, z)][0] == "minecraft:air" and B[(x, 0, z)][0] != VOID and r(0.18):
                put(x, 1, z, "minecraft:moss_carpet")
    # -------- le coffre, sous la poutre, contre le mur ouest
    if avec_coffre:
        put(2, 1, 3, "lootr:lootr_chest[facing=east,type=single,waterlogged=false]",
            Compound({"id": String("lootr:lootr_chest"), "LootTable": String("kubejs:chests/ruine_atelier")}))
    return B

def ecrire(B, nom):
    palette, pidx, blocks = [], {}, []
    for (x, y, z), (state, nbt) in sorted(B.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        if state == VOID:
            continue                              # absent du fichier = structure_void
        if state not in pidx:
            name, props = (state[:-1].split("[") + [""])[:2] if "[" in state else (state, "")
            e = Compound({"Name": String(name)})
            if props:
                e["Properties"] = Compound({k: String(v) for k, v in (kv.split("=") for kv in props.split(","))})
            pidx[state] = len(palette); palette.append(e)
        b = Compound({"pos": List[Int]([Int(x), Int(y), Int(z)]), "state": Int(pidx[state])})
        if nbt is not None: b["nbt"] = nbt
        blocks.append(b)
    root = Compound({"DataVersion": Int(3955), "size": List[Int]([Int(SX), Int(SY), Int(SZ)]),
                     "palette": List[Compound](palette), "blocks": List[Compound](blocks), "entities": List[Compound]([])})
    dest = os.path.join(OUT, "kubejs/data/kubejs/structure/ruines"); os.makedirs(dest, exist_ok=True)
    nbtlib.File(root, root_name="").save(os.path.join(dest, nom + ".nbt"), gzipped=True)
    return len(blocks)

A = construire(True); Bsans = construire(False)
print(ecrire(A, "atelier_effondre"), ecrire(Bsans, "atelier_effondre_vide"))
here = os.path.dirname(os.path.abspath(__file__))
json.dump({"size": [SX, SY, SZ], "blocks": {f"{x},{y},{z}": s for (x, y, z), (s, n) in A.items()}},
          open(os.path.join(here, "ruine_blocks.json"), "w"))
