#!/usr/bin/env python3
"""Avant-poste tempéré de l'Empire d'Airain : toutes les pièces (.nbt) + leur description pour les aperçus.
usage : avant_poste.py <dossier du pack>"""
import json, os, random, sys
from nbtlib import Compound, Byte, Int, List
from pieces import Piece, VOID, AIR, coffre, distributeur, panneau, livre_enchante

PACK = sys.argv[1]
OUT = os.path.join(PACK, "kubejs/data/kubejs/structure/avant_poste/tempere")
NS = "kubejs:avant_poste/tempere/"
R = random.Random(23)
def ch(*xs): return R.choice(xs)
def p(x): return R.random() < x

# ---------------------------------------------------------------- matériaux du climat tempéré
SOL = lambda: ch(*["minecraft:polished_tuff"] * 6, "minecraft:tuff", "minecraft:tuff_bricks", "minecraft:cobbled_deepslate", "minecraft:moss_block")
PAVE = lambda: ch("minecraft:tuff", "minecraft:cobbled_deepslate", "minecraft:gravel", "minecraft:coarse_dirt", "minecraft:dirt_path", "minecraft:dirt_path", "minecraft:polished_tuff")
MUR = lambda: ch(*["minecraft:tuff_bricks"] * 5, "minecraft:polished_tuff", "minecraft:mossy_cobblestone", "minecraft:cracked_deepslate_tiles")
PLANCHER = lambda: ch(*["minecraft:spruce_planks"] * 5, "minecraft:stripped_spruce_wood", "minecraft:coarse_dirt")
POTEAU = "minecraft:stripped_spruce_log[axis=y]"
TOIT = "minecraft:spruce_slab[type=bottom,waterlogged=false]"
MURET = "minecraft:tuff_brick_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]"
AMPOULE_ETEINTE = "minecraft:waxed_oxidized_copper_bulb[lit=false,powered=false]"
AMPOULE = "minecraft:waxed_copper_bulb[lit=true,powered=false]"
TOILE = "minecraft:cobweb"
MOUSSE = "minecraft:moss_carpet"

pieces = []
def piece(*a, **k):
    pc = Piece(*a, **k); pieces.append(pc); return pc

def lampadaire(pc, x, z, h=3):
    for y in range(1, h + 1):
        pc.put(x, y, z, MURET)
    pc.put(x, h + 1, z, AMPOULE_ETEINTE)

def usure_sol(pc, x1, z1, x2, z2, y=1, mousse=0.12):
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if pc.get(x, y, z) == AIR and p(mousse):
                pc.put(x, y, z, MOUSSE)

# ================================================================ PLACE CENTRALE : la fontaine à sec
c = piece(NS + "centre_fontaine", 15, 9, 15, fond=AIR)
for x in range(15):
    for z in range(15):
        bord = x in (0, 14) or z in (0, 14)
        c.put(x, 0, z, "minecraft:tuff_bricks" if bord else SOL())
# bassin à sec
for x in range(5, 10):
    for z in range(5, 10):
        if x in (5, 9) or z in (5, 9):
            c.put(x, 1, z, "minecraft:tuff_bricks" if not p(0.15) else "minecraft:mossy_cobblestone")
        else:
            c.put(x, 0, z, ch("minecraft:coarse_dirt", "minecraft:mud", "minecraft:coarse_dirt"))
            if p(0.3): c.put(x, 1, z, "minecraft:dead_bush")
for y in range(1, 4):
    c.put(7, y, 7, "minecraft:oxidized_copper")
c.put(7, 4, 7, "minecraft:oxidized_copper_grate[waterlogged=false]")
c.put(7, 5, 7, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
for (dx, dz, f) in ((0, -1, "north"), (0, 1, "south"), (-1, 0, "west"), (1, 0, "east")):
    c.put(7 + dx, 3, 7 + dz, "minecraft:oxidized_cut_copper_stairs[facing=%s,half=top,shape=straight,waterlogged=false]" %
          {"north": "south", "south": "north", "west": "east", "east": "west"}[f])
for (x, z) in ((2, 2), (12, 2), (2, 12), (12, 12)):
    lampadaire(c, x, z)
# bancs de sapin tournés vers la fontaine
for x in (6, 8):
    c.put(x, 1, 3, "minecraft:spruce_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    c.put(x, 1, 11, "minecraft:spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
# panneau de la place
c.put(7, 1, 2, "minecraft:spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
c.put(7, 2, 2, "minecraft:spruce_planks")
c.put(*(7, 2, 1), *panneau("airain.avant_poste.place", face="north"))
usure_sol(c, 1, 1, 13, 13, mousse=0.06)
c.jigsaw(7, 1, 0, "north", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
c.jigsaw(14, 1, 7, "east", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
c.jigsaw(0, 0, 7, "west", "kubejs:batiment", "kubejs:batiment", NS + "marches", "minecraft:tuff_bricks")   # un marché garanti
c.jigsaw(7, 0, 14, "south", "kubejs:salle", "kubejs:salle", NS + "salles_scellees", "minecraft:tuff_bricks")

# ================================================================ RUES
def rue_droite(nom, longueur, rails):
    r = piece(NS + nom, 5, 2, longueur)
    for x in range(5):
        for z in range(longueur):
            r.put(x, 0, z, PAVE())
    if rails:
        for z in range(2, longueur - 2):
            if p(0.65):
                r.put(2, 1, z, "minecraft:rail[shape=north_south,waterlogged=false]")
            elif p(0.5):
                r.put(2, 1, z, MOUSSE)
    r.jigsaw(2, 1, 0, "north", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
    r.jigsaw(2, 1, longueur - 1, "south", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
    for z in range(3, longueur - 2, 5):
        r.jigsaw(0, 1, z, "west", "kubejs:batiment", "kubejs:batiment", NS + "batiments", VOID)
        r.jigsaw(4, 1, z, "east", "kubejs:batiment", "kubejs:batiment", NS + "batiments", VOID)
    return r
rue_droite("rue_rails", 13, True)
rue_droite("rue_pavee", 13, False)
rue_droite("rue_courte", 8, True)

x4 = piece(NS + "carrefour", 5, 2, 5)
for x in range(5):
    for z in range(5):
        x4.put(x, 0, z, PAVE())
x4.jigsaw(2, 1, 0, "north", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
x4.jigsaw(2, 1, 4, "south", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
x4.jigsaw(0, 1, 2, "west", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
x4.jigsaw(4, 1, 2, "east", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)

# ================================================================ FINS DE RUE : porte de la muraille, barricade
g = piece(NS + "porte", 11, 9, 4)
for x in range(11):
    for z in range(4):
        g.put(x, 0, z, PAVE() if 4 <= x <= 6 else "minecraft:tuff_bricks")
haut = [7, 7, 5, 5, 6, 6, 6, 5, 4, 7, 7]
for x in range(11):
    for z in (1, 2):
        for y in range(1, haut[x] + 1):
            if 4 <= x <= 6 and y <= 3:
                g.put(x, y, z, AIR); continue
            g.put(x, y, z, MUR())
for x in (3, 7):
    for y in range(1, 5):
        g.put(x, y, 0, POTEAU)
for x in range(3, 8):
    g.put(x, 4, 0, "minecraft:spruce_log[axis=x]")
g.put(4, 3, 1, "minecraft:iron_bars[east=true,north=false,south=false,waterlogged=false,west=false]")
g.put(6, 3, 2, "minecraft:iron_bars[east=false,north=false,south=false,waterlogged=false,west=true]")
g.put(1, 5, 0, "minecraft:oxidized_copper_grate[waterlogged=false]"); g.put(9, 5, 0, "minecraft:oxidized_copper_grate[waterlogged=false]")
g.put(5, 1, 3, "minecraft:cobbled_deepslate")
g.jigsaw(5, 1, 0, "north", "kubejs:rue", "kubejs:rue", "minecraft:empty", AIR)

b = piece(NS + "barricade", 5, 3, 3)
for x in range(5):
    for z in range(3):
        b.put(x, 0, z, PAVE())
for (x, y, z) in ((0, 1, 1), (1, 1, 1), (1, 2, 1), (3, 1, 1), (4, 1, 1), (4, 1, 2), (2, 1, 2), (0, 1, 2)):
    b.put(x, y, z, ch("minecraft:cobbled_deepslate", "minecraft:tuff", "minecraft:mossy_cobblestone"))
for x in range(1, 4):
    b.put(x, 2 if x == 1 else 1, 1 if x != 2 else 2, "minecraft:spruce_log[axis=x]")
b.jigsaw(2, 1, 0, "north", "kubejs:rue", "kubejs:rue", "minecraft:empty", AIR)

# ================================================================ BÂTIMENTS
def batiment(nom, sx, sy, sz, porte_x, mur_derriere=True):
    bt = piece(NS + nom, sx, sy, sz, fond=AIR)
    bt.jigsaw(porte_x, 0, 0, "north", "kubejs:batiment", "kubejs:batiment", "minecraft:empty", "minecraft:polished_tuff")
    if mur_derriere:
        bt.jigsaw(sx // 2, 0, sz - 1, "south", "kubejs:mur", "kubejs:mur", NS + "murs", "minecraft:tuff_bricks")
    return bt

def coque(bt, sx, sy, sz, porte_x, h, effondre=0.25, sol=PLANCHER):
    for x in range(sx):
        for z in range(sz):
            bt.put(x, 0, z, sol() if 0 < x < sx - 1 and 0 < z < sz - 1 else "minecraft:tuff_bricks")
    for y in range(1, h + 1):
        for x in range(sx):
            for z in range(sz):
                if x in (0, sx - 1) or z in (0, sz - 1):
                    coin = x in (0, sx - 1) and z in (0, sz - 1)
                    bt.put(x, y, z, POTEAU if coin else MUR())
    # toit de sapin, en partie effondré
    for x in range(sx):
        for z in range(sz):
            if not p(effondre):
                bt.put(x, h + 1, z, TOIT)
    # haut des murs abîmé
    for x in range(sx):
        for z in range(sz):
            if (x in (0, sx - 1) or z in (0, sz - 1)) and p(0.2):
                bt.put(x, h, z, AIR); bt.put(x, h + 1, z, AIR)
    for y in (1, 2):
        bt.put(porte_x, y, 0, AIR)
    # fenêtres
    for x in range(2, sx - 2, 3):
        if x != porte_x:
            bt.put(x, 2, 0, "minecraft:glass_pane[east=false,north=false,south=false,waterlogged=false,west=false]" if p(0.4) else AIR)

# ---------------------------------------------------------------- le marché : une halle ouverte et 3 emplacements de machines
m = batiment("marche", 11, 7, 11, 5, mur_derriere=False)
for x in range(11):
    for z in range(11):
        m.put(x, 0, z, "minecraft:tuff_bricks" if x in (0, 10) or z in (0, 10) else SOL())
for (x, z) in ((1, 1), (9, 1), (1, 9), (9, 9)):
    for y in range(1, 5):
        m.put(x, y, z, POTEAU)
for x in range(1, 10):
    for z in range(1, 10):
        if not p(0.35):
            m.put(x, 5, z, TOIT)
for x in range(1, 10):
    m.put(x, 5, 1, "minecraft:spruce_log[axis=x]"); m.put(x, 5, 9, "minecraft:spruce_log[axis=x]")
m.put(5, 4, 5, "minecraft:chain[axis=y,waterlogged=false]"); m.put(5, 3, 5, AMPOULE_ETEINTE)
m.put(4, 1, 4, "minecraft:barrel[facing=up,open=false]"); m.put(6, 1, 6, "minecraft:spruce_slab[type=bottom,waterlogged=false]")
usure_sol(m, 1, 1, 9, 9)
m.jigsaw(0, 0, 5, "west", "kubejs:machine", "kubejs:machine", NS + "machines", "minecraft:tuff_bricks")
m.jigsaw(10, 0, 5, "east", "kubejs:machine", "kubejs:machine", NS + "machines", "minecraft:tuff_bricks")
m.jigsaw(5, 0, 10, "south", "kubejs:machine", "kubejs:machine", NS + "machines", "minecraft:tuff_bricks")

# ---------------------------------------------------------------- l'entrepôt
e = batiment("entrepot", 9, 7, 11, 4)
coque(e, 9, 7, 11, 4, 4, effondre=0.3)
for (x, z) in ((1, 2), (1, 3), (1, 5), (7, 2), (7, 4), (7, 5), (6, 8), (2, 8)):
    for y in range(1, R.randint(2, 3)):
        e.put(x, y, z, "minecraft:barrel[facing=up,open=false]")
e.put(*(1, 1, 7), *coffre("kubejs:chests/avant_poste_entrepot", "east"))
e.put(*(7, 1, 7), *coffre("kubejs:chests/avant_poste_entrepot", "west"))
for (x, y, z) in ((1, 4, 1), (7, 4, 9), (4, 4, 5)):
    e.put(x, y, z, TOILE)
e.put(4, 4, 5, "minecraft:chain[axis=y,waterlogged=false]"); e.put(4, 3, 5, AMPOULE_ETEINTE)

# ---------------------------------------------------------------- l'atelier
a = batiment("atelier", 9, 7, 9, 4)
coque(a, 9, 7, 9, 4, 4, effondre=0.45, sol=SOL)
a.put(2, 1, 6, "create:andesite_casing"); a.put(2, 2, 6, "create:mechanical_press")
a.put(2, 1, 5, "create:depot")
a.put(3, 1, 7, "create:cogwheel[axis=x]"); a.put(4, 1, 7, "create:shaft[axis=x]"); a.put(5, 1, 7, "create:large_cogwheel[axis=x]")
a.put(6, 1, 6, "minecraft:crafting_table"); a.put(7, 1, 6, "minecraft:damaged_anvil[facing=north]")
a.put(*(7, 1, 2), *coffre("kubejs:chests/avant_poste_atelier", "west"))
a.put(1, 1, 2, "minecraft:smithing_table")
a.put(6, 1, 3, "create:andesite_casing"); a.put(6, 2, 3, "create:shaft[axis=y]")
for (x, y, z) in ((1, 4, 1), (7, 4, 7)):
    a.put(x, y, z, TOILE)

# ---------------------------------------------------------------- le dortoir
d = batiment("dortoir", 9, 7, 9, 4)
coque(d, 9, 7, 9, 4, 4, effondre=0.2)
for z in (2, 5):
    for (x, f) in ((1, "east"), (7, "west")):
        coul = ch("gray", "brown", "light_gray")
        dx = 1 if f == "east" else -1
        d.put(x, 1, z, "minecraft:%s_bed[facing=%s,occupied=false,part=head]" % (coul, "west" if f == "east" else "east"))
        d.put(x + dx, 1, z, "minecraft:%s_bed[facing=%s,occupied=false,part=foot]" % (coul, "west" if f == "east" else "east"))
d.put(*(4, 1, 7), *coffre("kubejs:chests/avant_poste_dortoir", "north"))
d.put(1, 1, 7, "minecraft:barrel[facing=up,open=false]"); d.put(7, 1, 7, "minecraft:spruce_trapdoor[facing=north,half=bottom,open=false,powered=false,waterlogged=false]")
for (x, y, z) in ((1, 4, 7), (7, 4, 1), (2, 1, 4)):
    d.put(x, y, z, TOILE)
d.put(4, 4, 4, "minecraft:chain[axis=y,waterlogged=false]"); d.put(4, 3, 4, AMPOULE_ETEINTE)

# ================================================================ MACHINES DE DISTRIBUTION (une par catégorie du catalogue)
CATALOGUE = {
 "batisseur": [("minecraft:stone_bricks", 32, dict(bevel=1)), ("minecraft:oak_planks", 32, dict(bevel=1)),
               ("minecraft:polished_tuff", 32, dict(bevel=1)), ("minecraft:bricks", 32, dict(bevel=2)),
               ("minecraft:glass", 16, dict(bevel=1)), ("minecraft:ladder", 16, dict(bevel=1)), ("minecraft:lantern", 4, dict(bevel=1))],
 "matieres": [("minecraft:coal", 16, dict(bevel=1)), ("minecraft:copper_ingot", 16, dict(sprocket=1)),
              ("minecraft:iron_ingot", 8, dict(sprocket=1)), ("create:zinc_ingot", 8, dict(sprocket=1)),
              ("minecraft:gold_ingot", 4, dict(sprocket=1)), ("minecraft:redstone", 16, dict(sprocket=1)),
              ("minecraft:lapis_lazuli", 16, dict(sprocket=1))],
 "agriculture": [("minecraft:wheat_seeds", 16, dict(spur=2)), ("minecraft:potato", 16, dict(spur=2)),
                 ("minecraft:carrot", 16, dict(spur=2)), ("minecraft:sugar_cane", 8, dict(bevel=1)),
                 ("minecraft:oak_sapling", 4, dict(spur=2)), ("minecraft:bone_meal", 16, dict(bevel=1)),
                 ("minecraft:white_wool", 8, dict(bevel=1))],
 "mecanique": [("minecraft:piston", 4, dict(sprocket=1)), ("minecraft:sticky_piston", 2, dict(sprocket=1)),
               ("minecraft:hopper", 4, dict(sprocket=1)), ("minecraft:repeater", 4, dict(bevel=1)),
               ("minecraft:rail", 16, dict(bevel=1))],
 "create": [("create:andesite_alloy", 16, dict(sprocket=1)), ("create:cogwheel", 8, dict(bevel=1)),
            ("create:large_cogwheel", 4, dict(bevel=1)), ("create:shaft", 16, dict(bevel=1)),
            ("minecraft:dried_kelp", 16, dict(bevel=1)), ("create:iron_sheet", 8, dict(sprocket=1))],
 "magie": [("minecraft:amethyst_shard", 8, dict(bevel=1)), ("ars_nouveau:blue_archwood_sapling", 2, dict(bevel=2))],
 "expedition": [("minecraft:torch", 16, dict(bevel=1)), ("minecraft:bread", 16, dict(bevel=1)),
                ("minecraft:arrow", 16, dict(bevel=1)), ("minecraft:bucket", 1, dict(bevel=1)), ("minecraft:map", 2, dict(bevel=1))],
}
for cat, objets in CATALOGUE.items():
    mc = piece(NS + "machine_" + cat, 7, 5, 2)
    debut = (7 - len(objets)) // 2
    for x in range(7):
        mc.put(x, 0, 0, "minecraft:polished_tuff"); mc.put(x, 0, 1, "minecraft:tuff_bricks")
        for y in range(1, 4):
            mc.put(x, y, 1, "create:copper_casing" if y < 3 else "minecraft:waxed_oxidized_cut_copper")
        i = x - debut
        if 0 <= i < len(objets):
            o, n, prix = objets[i]
            mc.put(*(x, 1, 0), *distributeur(o, n, "north", **prix))
        else:
            mc.put(x, 1, 0, "minecraft:waxed_oxidized_copper")
        mc.put(x, 2, 0, "minecraft:waxed_cut_copper_slab[type=top,waterlogged=false]")
        mc.put(x, 4, 1, "minecraft:waxed_cut_copper_slab[type=bottom,waterlogged=false]")
    mc.put(*(3, 3, 0), *panneau("airain.machine." + cat, face="north", couleur="white"))
    mc.put(1, 3, 0, AMPOULE); mc.put(5, 3, 0, AMPOULE)
    mc.jigsaw(3, 0, 0, "north", "kubejs:machine", "kubejs:machine", "minecraft:empty", "minecraft:polished_tuff")

# ================================================================ SALLES SCELLÉES (une par avant-poste, palier au hasard)
SCELLEES = {
 "cuivre": ("minecraft:waxed_copper_block", "minecraft:waxed_cut_copper", [
     ("minecraft:diamond", 1, dict(cog=1), None), ("minecraft:observer", 4, dict(sprocket=2), None),
     ("minecraft:enchanted_book", 1, dict(cog=1), livre_enchante("minecraft:efficiency", 2)),
     ("minecraft:enchanted_book", 1, dict(cog=1), livre_enchante("minecraft:protection", 2)),
     ("minecraft:enchanted_book", 1, dict(cog=1), livre_enchante("minecraft:unbreaking", 2))]),
 "laiton": ("create:brass_block", "create:brass_casing", [
     ("minecraft:quartz", 16, dict(sprocket=2), None), ("minecraft:comparator", 4, dict(cog=1), None),
     ("create:electron_tube", 4, dict(cog=1), None),
     ("minecraft:enchanted_book", 1, dict(cog=2), livre_enchante("minecraft:efficiency", 4)),
     ("minecraft:enchanted_book", 1, dict(cog=2), livre_enchante("minecraft:sharpness", 4))]),
 "ciel": ("minecraft:light_blue_glazed_terracotta", "create:brass_casing", [
     ("minecraft:ender_pearl", 16, dict(cog=2), None), ("minecraft:firework_rocket", 16, dict(cog=1), Compound({"minecraft:fireworks": Compound({"flight_duration": Byte(2), "explosions": List[Compound]([])})})),
     ("minecraft:enchanted_book", 1, dict(crown=1), livre_enchante("minecraft:mending", 1)),
     ("minecraft:enchanted_book", 1, dict(cog=4), livre_enchante("minecraft:protection", 4)),
     ("minecraft:enchanted_book", 1, dict(cog=4), livre_enchante("minecraft:fortune", 3))]),
}
for palier, (marque, garniture, ventes) in SCELLEES.items():
    s = piece(NS + "salle_" + palier, 7, 7, 7, fond=AIR)
    for x in range(7):
        for z in range(7):
            s.put(x, 0, z, "minecraft:polished_deepslate" if z > 0 else "minecraft:tuff_bricks")
            if z >= 1:
                for y in range(1, 5):
                    if x in (0, 6) or z in (1, 6):
                        s.put(x, y, z, "minecraft:deepslate_tiles" if y != 4 else garniture)
                s.put(x, 5, z, "minecraft:deepslate_tile_slab[type=bottom,waterlogged=false]")
    s.put(3, 1, 1, "minecraft:iron_door[facing=south,half=lower,hinge=left,open=false,powered=false]")
    s.put(3, 2, 1, "minecraft:iron_door[facing=south,half=upper,hinge=left,open=false,powered=false]")
    s.put(3, 3, 1, marque)                                   # la marque du sceau : le script la lit
    s.put(*(2, 3, 0), *panneau("", face="north", couleur="white", lignes=[
        '""', '{"translate":"airain.sceau.%s"}' % palier, '{"translate":"airain.sceau.requis.%s"}' % palier, '""']))
    s.put(4, 3, 0, AMPOULE)
    for i, (o, n, prix, comp) in enumerate(ventes):
        v = distributeur(o, n, "north", composants=comp, **prix)
        s.put(*(1 + i, 1, 5), *v)
        s.put(1 + i, 2, 5, garniture)
    s.put(3, 4, 3, AMPOULE)
    s.jigsaw(3, 0, 0, "north", "kubejs:salle", "kubejs:salle", "minecraft:empty", "minecraft:tuff_bricks")
    s.jigsaw(3, 1, 6, "south", "kubejs:rue", "kubejs:rue", NS + "rues", "minecraft:deepslate_tiles")   # une rue repart derrière la salle

# ================================================================ MURAILLE ET TOURS (derrière les bâtiments)
w = piece(NS + "mur", 9, 6, 2)
prof = [3, 4, 5, 5, 4, 5, 3, 2, 4]
for x in range(9):
    w.put(x, 0, 0, "minecraft:tuff_bricks"); w.put(x, 0, 1, "minecraft:tuff_bricks")
    for y in range(1, prof[x] + 1):
        w.put(x, y, 1, MUR())
    if x in (0, 8):
        for y in range(1, prof[x] + 2):
            w.put(x, y, 1, POTEAU)
w.put(4, 3, 1, "minecraft:iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]")
w.jigsaw(4, 0, 0, "north", "kubejs:mur", "kubejs:mur", "minecraft:empty", "minecraft:tuff_bricks")

t = piece(NS + "tour", 5, 11, 5, fond=AIR)
for x in range(5):
    for z in range(5):
        t.put(x, 0, z, "minecraft:tuff_bricks")
        for y in range(1, 8):
            if x in (0, 4) or z in (0, 4):
                t.put(x, y, z, POTEAU if x in (0, 4) and z in (0, 4) else MUR())
        t.put(x, 8, z, "minecraft:spruce_planks" if 0 < x < 4 and 0 < z < 4 else "minecraft:tuff_bricks")
        if (x in (0, 4) or z in (0, 4)) and (x + z) % 2 == 0:
            t.put(x, 9, z, "minecraft:tuff_brick_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]")
for y in range(1, 9):
    t.put(2, y, 3, "minecraft:ladder[facing=north,waterlogged=false]")
t.put(2, 8, 2, AIR)
for y in (1, 2):
    t.put(2, y, 0, AIR)
t.put(2, 5, 4, AIR); t.put(4, 5, 2, AIR); t.put(0, 5, 2, AIR)        # meurtrières
for (x, z) in ((1, 1), (3, 3), (3, 1)):
    if p(0.6): t.put(x, 9, z, VOID)
t.jigsaw(2, 0, 0, "north", "kubejs:mur", "kubejs:mur", "minecraft:empty", "minecraft:tuff_bricks")

# ================================================================ L'ENCEINTE : la pièce de départ, qui entoure tout l'avant-poste
# Pièce « qui épouse le terrain » : chaque colonne de la muraille suit le sol, donc pas de mur suspendu dans le vide.
# Tout l'intérieur est vide (le terrain reste) ; un bloc puzzle au centre fait pousser la place, puis le reste,
# et le jeu n'accepte que les pièces qui tiennent DANS l'enceinte.
CREN = "minecraft:tuff_brick_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]"
GRILLE = "minecraft:oxidized_copper_grate[waterlogged=false]"
ENC = 71                     # côté de l'enceinte (blocs)
MIL = ENC // 2

def enceinte(nom, graine):
    rr = random.Random(graine)
    e = Piece(NS + nom, ENC, 12, ENC); pieces.append(e)
    def dist_bord(x, z): return min(x, z, ENC - 1 - x, ENC - 1 - z)
    # --- parcours du périmètre (anneau 1-2) découpé en tronçons : intact / abîmé / effondré
    tour_ = []
    for i in range(1, ENC - 1): tour_.append((i, 1))
    for i in range(2, ENC - 1): tour_.append((ENC - 2, i))
    for i in range(ENC - 3, 0, -1): tour_.append((i, ENC - 2))
    for i in range(ENC - 3, 1, -1): tour_.append((1, i))
    hauteurs, k = {}, 0
    while k < len(tour_):
        long_ = rr.randint(6, 14)
        typ = rr.choices(["intact", "abime", "effondre"], [0.45, 0.35, 0.2])[0]
        for j in range(k, min(k + long_, len(tour_))):
            hauteurs[tour_[j]] = {"intact": 6, "abime": rr.randint(2, 4), "effondre": rr.choice([0, 0, 1])}[typ]
        k += long_
    def h_de(x, z):
        # la muraille fait 2 blocs d'épaisseur : l'anneau intérieur (2) prend la hauteur de l'anneau extérieur (1)
        if dist_bord(x, z) == 1: return hauteurs.get((x, z), 0)
        nx = 1 if x == 2 else (ENC - 2 if x == ENC - 3 else x)
        nz = 1 if z == 2 else (ENC - 2 if z == ENC - 3 else z)
        return hauteurs.get((nx, nz), hauteurs.get((x if x not in (2, ENC - 3) else nx, nz), 0))
    for x in range(ENC):
        for z in range(ENC):
            d = dist_bord(x, z)
            if d in (1, 2):
                h = h_de(x, z)
                e.put(x, 0, z, "minecraft:tuff_bricks")
                for y in range(1, h + 1):
                    e.put(x, y, z, MUR())
                if h == 6 and d == 1 and (x + z) % 2 == 0:
                    e.put(x, 7, z, CREN)
                if h <= 1 and rr.random() < 0.35:                 # gravats au pied des brèches
                    e.put(x + rr.choice((-1, 0, 1)) if 0 < x < ENC - 1 else x, 1, z, rr.choice(
                        ("minecraft:cobbled_deepslate", "minecraft:tuff", "minecraft:mossy_cobblestone")))
                # poteaux de sapin côté intérieur, tous les 8 blocs
                if d == 2 and h >= 3 and (x + z) % 8 == 0:
                    for y in range(1, h + 1):
                        e.put(x, y, z, POTEAU)
    # --- tours d'angle (7×7), l'une d'elles en ruine
    ruine = rr.randrange(4)
    for i, (ox, oz) in enumerate(((0, 0), (ENC - 7, 0), (0, ENC - 7), (ENC - 7, ENC - 7))):
        haut = 5 if i == ruine else 10
        for x in range(ox, ox + 7):
            for z in range(oz, oz + 7):
                bord = x in (ox, ox + 6) or z in (oz, oz + 6)
                e.put(x, 0, z, "minecraft:tuff_bricks")
                for y in range(1, haut + 1):
                    if bord:
                        coin = x in (ox, ox + 6) and z in (oz, oz + 6)
                        e.put(x, y, z, POTEAU if coin else MUR())
                    else:
                        e.put(x, y, z, AIR)
                if i != ruine:
                    e.put(x, haut, z, "minecraft:spruce_planks" if not bord else "minecraft:tuff_bricks")
                    if bord and (x + z) % 2 == 0:
                        e.put(x, haut + 1, z, CREN)
        for y in range(1, haut):
            e.put(ox + 3, y, oz + 5 if oz == 0 else oz + 1,
                  "minecraft:ladder[facing=%s,waterlogged=false]" % ("north" if oz == 0 else "south"))
        if i != ruine:
            e.put(ox + 3, haut, oz + 5 if oz == 0 else oz + 1, AIR)
            for (wx, wz) in ((ox + 3, oz), (ox, oz + 3), (ox + 6, oz + 3), (ox + 3, oz + 6)):
                e.put(wx, 6, wz, GRILLE)
        # porte d'accès côté intérieur
        px = ox + 6 if ox == 0 else ox
        for y in (1, 2):
            e.put(px, y, oz + 3, AIR)
    # --- une porte fortifiée au milieu de chaque côté
    def porte(cote):
        for t in range(MIL - 4, MIL + 5):
            for d in range(0, 4):
                x, z = {"n": (t, d), "s": (t, ENC - 1 - d), "o": (d, t), "e": (ENC - 1 - d, t)}[cote]
                flanc = t in (MIL - 4, MIL - 3, MIL + 3, MIL + 4)
                e.put(x, 0, z, PAVE() if not flanc else "minecraft:tuff_bricks")
                for y in range(1, 9):
                    if flanc and d in (0, 1, 2, 3):
                        e.put(x, y, z, MUR() if y < 8 else (CREN if (t + d) % 2 == 0 else AIR))
                    elif abs(t - MIL) <= 1 and y <= 4:
                        e.put(x, y, z, AIR)                       # passage de 3 de large
                    elif y in (5, 6) and d in (1, 2):
                        e.put(x, y, z, MUR())                     # linteau
                    elif y in (1, 2, 3, 4) and d in (1, 2):
                        e.put(x, y, z, AIR)
                    else:
                        e.put(x, y, z, VOID)
                if abs(t - MIL) <= 1 and d == 1:
                    e.put(x, 5, z, "minecraft:spruce_log[axis=%s]" % ("x" if cote in "ns" else "z"))
                if t == MIL - 1 and d == 2 and rr.random() < 0.7:                       # herse rouillée, à moitié tombée
                    e.put(x, 4, z, "minecraft:iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]")
    for cote in rr.sample("nseo", rr.choice((3, 4))):                   # parfois une porte murée par l'effondrement
        porte(cote)
    # --- le bloc puzzle central : la place s'accroche ici
    e.jigsaw(MIL, 1, MIL, "north", "kubejs:coeur", "kubejs:place", NS + "centres", VOID)
    return e

for i, g_ in enumerate((71, 1789, 4242)):
    enceinte("enceinte_%s" % "abc"[i], g_)

# la place centrale se pose sur le bloc puzzle de l'enceinte (au pied de la fontaine)
c.jigsaw(7, 1, 7, "south", "kubejs:place", "kubejs:coeur", "minecraft:empty", "minecraft:oxidized_copper")

# ================================================================ écriture
total = 0
pieces[:] = [pc for pc in pieces if pc.nom.split("/")[-1] not in ("porte", "mur")]   # remplacées par l'enceinte
for pc in pieces:
    total += pc.ecrire(os.path.join(PACK, "kubejs/data/kubejs/structure"))
here = os.path.dirname(os.path.abspath(__file__))
json.dump({pc.nom: pc.apercu() for pc in pieces}, open(os.path.join(here, "avant_poste_pieces.json"), "w"))
print(len(pieces), "pièces,", total, "blocs")
