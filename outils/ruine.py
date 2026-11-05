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

# ------------------------------------------------------------------ revue : sous-sol, automate, lierre, débris projetés
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import automate_abattu, lierre
BAS = 4                                   # quatre couches de sous-sol ajoutées sous la dalle
def etendre(B, avec_coffre):
    r = random.Random(4041)
    N = {}
    W, H, L = SX + 2, SY + BAS, SZ + 2
    for x in range(W):
        for y in range(H):
            for z in range(L):
                N[(x, y, z)] = (VOID, None)
    for (x, y, z), v in B.items():
        if v[0] == "lootr:lootr_chest[facing=east,type=single,waterlogged=false]": v = ("minecraft:barrel[facing=up,open=false]", None)
        N[(x + 1, y + BAS, z + 1)] = v
    get = lambda x, y, z: N.get((x, y, z), (None,))[0]
    def put(x, y, z, st, nbt=None):
        if (x, y, z) in N: N[(x, y, z)] = (st, nbt)
    # la cave de l'atelier : bloc de terre plein (pas de vide sous la ruine), pièce de 3×3 au centre
    for x in range(2, 7):
        for y in range(0, BAS):
            for z in range(4, 9):
                put(x, y, z, r.choice(("minecraft:dirt", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:tuff")))
    for x in range(3, 6):
        for z in range(5, 8):
            put(x, 0, z, "minecraft:polished_tuff")
            for y in range(1, BAS):
                put(x, y, z, "minecraft:air")
    for x in range(2, 7):
        for z in range(4, 9):
            if x in (2, 6) or z in (4, 8):
                for y in range(1, BAS):
                    put(x, y, z, "minecraft:tuff_bricks" if y < 3 else "create:weathered_iron_block")
    for y in range(1, BAS + 1):                                   # échelle et trappe dans la dalle
        put(4, y, 5, "minecraft:ladder[facing=south,waterlogged=false]")
    put(4, BAS, 4, "minecraft:tuff_bricks")
    put(4, BAS, 5, "minecraft:spruce_trapdoor[facing=south,half=top,open=false,powered=false,waterlogged=false]")
    put(4, BAS + 1, 5, "minecraft:air"); put(4, BAS + 2, 5, "minecraft:air")
    put(3, 1, 7, "minecraft:barrel[facing=up,open=false]"); put(3, 2, 7, "create:andesite_casing")
    put(5, 1, 5, "create:cogwheel[axis=y]"); put(3, 1, 5, "minecraft:cobweb")
    put(4, 3, 7, "minecraft:chain[axis=y,waterlogged=false]"); put(4, 2, 7, "minecraft:waxed_oxidized_copper_bulb[lit=false,powered=false]")
    if avec_coffre:
        put(5, 1, 7, "lootr:lootr_chest[facing=west,type=single,waterlogged=false]",
            Compound({"id": String("lootr:lootr_chest"), "LootTable": String("kubejs:chests/ruine_atelier")}))
    else:
        put(5, 1, 7, "minecraft:barrel[facing=west,open=false]")
    # l'automate de garde, écrasé par la chute du mur sud
    y0 = BAS + 1
    automate_abattu(put, 4, y0, 11, "x", 1)
    put(9, y0, 11, "create:weathered_iron_block"); put(10, y0, 11, "minecraft:weathered_cut_copper_slab[type=bottom,waterlogged=false]")
    # éclats de la chaudière projetés hors de l'atelier
    for _ in range(14):
        x, z = r.randint(0, W - 1), r.randint(0, L - 1)
        if get(x, y0, z) == VOID and (x in (0, 1, W - 2, W - 1) or z in (0, 1, L - 2, L - 1)):
            put(x, y0, z, r.choice(("create:weathered_copper_shingle_slab[type=bottom,waterlogged=false]", "minecraft:oxidized_copper",
                                    "create:shaft[axis=x]", "minecraft:weathered_cut_copper_slab[type=bottom,waterlogged=false]",
                                    "minecraft:moss_carpet", "minecraft:moss_carpet")))
    put(13, y0, 9, "create:large_cogwheel[axis=z]")               # la roue arrachée, roulée jusqu'ici
    # lierre sur la face extérieure du mur nord et sur le pignon ouest
    for x in range(2, 12, 2):
        for y in range(y0 + 4, y0, -1):
            if get(x, y, 2) not in (VOID, "minecraft:air", None) and get(x, y, 1) == VOID:
                lierre(get, put, x, y, 1, r.randint(2, 4)); break
    for z in range(3, 9, 2):
        for y in range(y0 + 3, y0, -1):
            if get(2, y, z) not in (VOID, "minecraft:air", None) and get(1, y, z) == VOID:
                lierre(get, put, 1, y, z, r.randint(1, 3)); break
    return N, (W, H, L)

A, dim = etendre(construire(True), True); Bsans, _ = etendre(construire(False), False)
SX, SY, SZ = dim
print(ecrire(A, "atelier_effondre"), ecrire(Bsans, "atelier_effondre_vide"))
here = os.path.dirname(os.path.abspath(__file__))
json.dump({"size": [SX, SY, SZ], "blocks": {f"{x},{y},{z}": s for (x, y, z), (s, n) in A.items()}},
          open(os.path.join(here, "ruine_blocks.json"), "w"))
