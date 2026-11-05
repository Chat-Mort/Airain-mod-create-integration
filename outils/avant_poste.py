#!/usr/bin/env python3
"""Avant-poste tempéré de l'Empire d'Airain, style steampunk : toutes les pièces (.nbt) + leur description pour les aperçus.
Règle de style : socle de pierre, murs en plaques de métal, toits en tôle de cuivre, tuyaux, engrenages, vapeur.
Jamais de créneaux, de herses ni de toits de bois.
usage : avant_poste.py <dossier du pack>"""
import json, os, random, sys, zlib
import nbtlib
from nbtlib import Compound, Byte, Int, List, String
from pieces import Piece, VOID, AIR, coffre, distributeur, panneau, livre_enchante
from style import *          # le vocabulaire steampunk commun à toutes les structures

PACK = sys.argv[1]
NS = "kubejs:avant_poste/tempere/"
R = random.Random(23)
def ch(*xs): return R.choice(xs)
def p(x): return R.random() < x
style_graine(R)

# ================================================================ LES COULEURS DE L'EMPIRE (mod Airain)
# Rouge impérial, ornements d'or, rouage. Les avant-postes sont abandonnés : toiles usées ou déchirées.
# Les grands étendards sont décoratifs (pas de titre, pas de place dans le registre) et hissés.
def _apparence(style, fond, orn, motif, forme, grand=(1, 1, 1, 0, 0, 0, 0, 0), partition=0, fond2=4, cmotif=0, etat=0, synchro=0):
    DEF, BITS, TAILLES = (1, 1, 1, 0, 0, 0, 0, 0), (2, 2, 2, 1, 2, 1, 1, 1), (3, 4, 3, 2, 4, 2, 2, 2)
    r = style | fond << 4 | orn << 8 | motif << 12 | forme << 16; dec = 20
    for k in range(8):
        r |= ((grand[k] - DEF[k]) % TAILLES[k]) << dec; dec += BITS[k]
    if r >= 1 << 31: r -= 1 << 32                          # Int signé (le bit du mode décoratif est le 31e)
    ext = partition | ((fond2 - 4) % 8) << 3 | cmotif << 6 | etat << 10 | synchro << 13
    return r, ext

def banniere_empire(rr, murale=False):
    etat = rr.choice((1, 1, 2))
    if murale:
        app, ext = _apparence(0, 0, 0, rr.choice((0, 0, 3)), rr.choice((0, 2)), partition=rr.choice((0, 0, 5)), fond2=7, etat=etat)
    else:      # longueur 64, largeur 28, vent moyen, franges, fleuron rouage, une seule toile, sans lanternes, décoratif
        app, ext = _apparence(0, 0, 0, 0, 0, grand=(2, 2, 1, 1, 2, 0, 0, 1), etat=etat, synchro=1)
    return Compound({"id": String("airain:foundation_stone"), "apparence": Int(app), "ext": Int(ext), "nom": String(""),
                     "devise": String(""), "rayon": Int(48), "hauteur": Int(6), "manuelle": nbtlib.Float(0.0)})

def grand_etendard(pc, x, y, z, face, rr):
    pc.put(x, y, z, "airain:great_standard[facing=%s,partie=0,sommet=false]" % face, banniere_empire(rr))
    for k in range(1, 7):
        pc.put(x, y + k, z, "airain:great_standard[facing=%s,partie=%d,sommet=%s]" % (face, k, "true" if k == 6 else "false"))

pieces = []
def piece(*a, **k):
    pc = Piece(*a, **k); pieces.append(pc); return pc

def usure_sol(pc, x1, z1, x2, z2, y=1, mousse=0.1):
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if pc.get(x, y, z) == AIR and p(mousse):
                pc.put(x, y, z, MOUSSE)

# ================================================================ PLACE CENTRALE : la fontaine à vapeur
c = piece(NS + "centre_fontaine", 15, 9, 15, fond=AIR)
for x in range(15):
    for z in range(15):
        bord = x in (0, 14) or z in (0, 14)
        rayon = x == 7 or z == 7                       # quatre allées de carreaux de cuivre vers la fontaine
        c.put(x, 0, z, "minecraft:tuff_bricks" if bord else (CARREAU_CUIVRE() if rayon else SOL()))
for x in range(5, 10):                                 # bassin cerclé de cuivre, à sec
    for z in range(5, 10):
        if x in (5, 9) or z in (5, 9):
            c.put(x, 1, z, "minecraft:waxed_weathered_cut_copper" if (x + z) % 2 else "minecraft:tuff_bricks")
        else:
            c.put(x, 0, z, ch("minecraft:coarse_dirt", "minecraft:mud", "minecraft:gravel"))
for y in range(1, 4):
    c.put(7, y, 7, "minecraft:oxidized_copper")
c.put(7, 4, 7, GRILLE_CUIVRE)
c.put(7, 5, 7, VAPEUR)                                  # un filet de vapeur s'échappe encore
for (dx, dz) in ((0, -1), (0, 1), (-1, 0), (1, 0)):     # quatre tuyaux qui partent du pilier vers le bassin
    ax = "z" if dx == 0 else "x"
    c.put(7 + dx, 2, 7 + dz, tuyau(ax)); c.put(7 + 2 * dx, 2, 7 + 2 * dz, tuyau(ax))
for (x, z) in ((2, 2), (12, 2), (2, 12), (12, 12)):
    lampadaire(c, x, z)
for x in (6, 8):                                       # bancs
    c.put(x, 1, 3, "minecraft:spruce_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    c.put(x, 1, 11, "minecraft:spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
c.put(7, 1, 2, "create:copper_bars"); c.put(7, 2, 2, "minecraft:waxed_cut_copper")          # panneau de la place
c.put(*(7, 2, 1), *panneau("airain.avant_poste.place", face="north"))
usure_sol(c, 1, 1, 13, 13, mousse=0.05)
c.jigsaw(7, 1, 0, "north", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
c.jigsaw(14, 1, 7, "east", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
c.jigsaw(0, 0, 7, "west", "kubejs:batiment", "kubejs:batiment", NS + "marches", "minecraft:tuff_bricks")   # un marché garanti
c.jigsaw(7, 0, 14, "south", "kubejs:salle", "kubejs:salle", NS + "salles_scellees", "minecraft:tuff_bricks")
c.jigsaw(7, 1, 7, "south", "kubejs:place", "kubejs:coeur", "minecraft:empty", "minecraft:oxidized_copper")   # accroche à l'enceinte

# ================================================================ RUES : pavés, anciens rails, conduites
def rue_droite(nom, longueur, rails, conduite, debut=3, pas=5):
    r = piece(NS + nom, 5, 2, longueur)
    for x in range(5):
        for z in range(longueur):
            r.put(x, 0, z, PAVE())
    if rails:
        for z in range(2, longueur - 2):
            if p(0.7):
                r.put(2, 1, z, "minecraft:rail[shape=north_south,waterlogged=false]")
            elif p(0.5):
                r.put(2, 1, z, MOUSSE)
    if conduite:                                       # une conduite posée au sol, cassée par endroits
        for z in range(1, longueur - 1):
            if z % 5 != 3 and p(0.8):
                r.put(4, 1, z, tuyau("z"))
    r.jigsaw(2, 1, 0, "north", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
    r.jigsaw(2, 1, longueur - 1, "south", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
    for z in range(debut, longueur - 2, pas):
        r.jigsaw(0, 1, z, "west", "kubejs:batiment", "kubejs:batiment", NS + "batiments", VOID)
        r.jigsaw(4, 1, z, "east", "kubejs:batiment", "kubejs:batiment", NS + "batiments", VOID)
    return r
rue_droite("rue_rails", 13, True, False)
rue_droite("rue_pavee", 13, False, True)
rue_droite("rue_courte", 8, True, False)
# avenues des cités : plus longues, une façade tous les 10 blocs pour que les grands bâtiments tiennent côte à côte
rue_droite("avenue", 19, True, False, debut=4, pas=10)
rue_droite("avenue_pavee", 19, False, True, debut=4, pas=10)

x4 = piece(NS + "carrefour", 5, 2, 5)
for x in range(5):
    for z in range(5):
        x4.put(x, 0, z, PAVE())
x4.put(2, 0, 2, GRILLE_CUIVRE)                          # bouche d'égout
x4.jigsaw(2, 1, 0, "north", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
x4.jigsaw(2, 1, 4, "south", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
x4.jigsaw(0, 1, 2, "west", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)
x4.jigsaw(4, 1, 2, "east", "kubejs:rue", "kubejs:rue", NS + "rues", VOID)

b = piece(NS + "barricade", 5, 3, 3)                    # chariot renversé, tuyaux et rouage tombés
for x in range(5):
    for z in range(3):
        b.put(x, 0, z, PAVE())
for (x, y, z) in ((0, 1, 1), (1, 1, 1), (4, 1, 1), (4, 1, 2), (0, 1, 2)):
    b.put(x, y, z, ch("minecraft:cobbled_deepslate", "minecraft:weathered_copper", "create:weathered_iron_block"))
b.put(1, 2, 1, "create:large_cogwheel[axis=z]")
b.put(2, 1, 2, tuyau("x")); b.put(3, 1, 2, tuyau("x")); b.put(3, 1, 1, "minecraft:weathered_cut_copper_slab[type=bottom,waterlogged=false]")
b.jigsaw(2, 1, 0, "north", "kubejs:rue", "kubejs:rue", "minecraft:empty", AIR)

# ================================================================ BÂTIMENTS : ateliers de métal sur socle de pierre
def batiment(nom, sx, sy, sz, porte_x):
    bt = piece(NS + nom, sx, sy, sz, fond=AIR)
    bt.jigsaw(porte_x, 0, 0, "north", "kubejs:batiment", "kubejs:batiment", "minecraft:empty", "minecraft:polished_tuff")
    bt.jigsaw(sx // 2, 0, sz - 1, "south", "kubejs:mur", "kubejs:mur", NS + "murs", "minecraft:tuff_bricks")
    return bt

def coque(bt, sx, sz, porte_x, h, effondre=0.25, sol=None, cheminee=None, base=0):
    """Bâtiment de l'Empire ; `base` = hauteur du rez-de-chaussée dans la pièce (sous-sol en dessous)."""
    sol = sol or PLANCHER
    _put = bt.put
    def put(x, y, z, s): _put(x, y + base, z, s)
    for x in range(sx):
        for z in range(sz):
            put(x, 0, z, sol() if 0 < x < sx - 1 and 0 < z < sz - 1 else "minecraft:tuff_bricks")
    for y in range(1, h + 1):
        for x in range(sx):
            for z in range(sz):
                if x in (0, sx - 1) or z in (0, sz - 1):
                    coin = x in (0, sx - 1) and z in (0, sz - 1)
                    nervure = (x % 4 == 0 and z in (0, sz - 1)) or (z % 4 == 0 and x in (0, sx - 1))
                    if y == 1:
                        put(x, y, z, "minecraft:tuff_bricks")                    # socle de pierre
                    elif coin or nervure:
                        put(x, y, z, "create:industrial_iron_block")             # montants rivetés
                    else:
                        put(x, y, z, PLAQUE())                                    # plaques de cuivre et de fer
    # bandeau de grilles sous le toit
    for x in range(sx):
        for z in range(sz):
            if (x in (0, sx - 1) or z in (0, sz - 1)) and not (x in (0, sx - 1) and z in (0, sz - 1)) and p(0.5):
                put(x, h, z, GRILLE_CUIVRE)
    # toit en tôle de cuivre, percé par endroits
    for x in range(sx):
        for z in range(sz):
            if not p(effondre):
                put(x, h + 1, z, TOLE_DALLE())
    for y in (1, 2):
        put(porte_x, y, 0, AIR)
    put(porte_x, 3, 0, "create:copper_casing")                                     # linteau
    for x in range(2, sx - 2, 3):                                                      # verrières
        if abs(x - porte_x) > 1:
            put(x, 2, 0, FENETRE if p(0.7) else AIR); put(x, 3, 0, FENETRE if p(0.7) else AIR)
    for z in range(2, sz - 2, 3):
        put(0, 2, z, FENETRE if p(0.6) else AIR); put(sx - 1, 2, z, FENETRE if p(0.6) else AIR)
    if cheminee:                                                                       # cheminée d'usine
        cx, cz, haut = cheminee
        for y in range(1, h + 1 + haut):
            put(cx, y, cz, "minecraft:bricks" if y <= h + 1 else ("minecraft:bricks" if y < h + haut else "create:weathered_iron_block"))
        put(cx, h + 1 + haut, cz, VAPEUR)

def conduite_facade(bt, sx, y):
    """Tuyau le long de la façade, juste derrière le mur avant (côté intérieur)."""
    for x in range(1, sx - 1):
        if bt.get(x, y, 1) == AIR and p(0.85):
            bt.put(x, y, 1, tuyau("x"))

# ---------------------------------------------------------------- le marché : une halle de fonte et de tôle, 3 emplacements de machines
m = piece(NS + "marche", 11, 8, 11, fond=AIR)
m.jigsaw(5, 0, 0, "north", "kubejs:batiment", "kubejs:batiment", "minecraft:empty", "minecraft:polished_tuff")
for x in range(11):
    for z in range(11):
        m.put(x, 0, z, "minecraft:tuff_bricks" if x in (0, 10) or z in (0, 10) else (CARREAU_CUIVRE() if (x + z) % 4 == 0 else SOL()))
for (x, z) in ((1, 1), (9, 1), (1, 9), (9, 9)):          # piliers de fonte
    m.put(x, 1, z, "minecraft:tuff_bricks")
    for y in range(2, 5):
        m.put(x, y, z, "create:industrial_iron_block")
for x in range(1, 10):                                  # poutres de fer
    m.put(x, 5, 1, "create:weathered_iron_block"); m.put(x, 5, 9, "create:weathered_iron_block")
for z in range(2, 9):
    m.put(1, 5, z, "create:weathered_iron_block"); m.put(9, 5, z, "create:weathered_iron_block")
for x in range(1, 10):                                  # toit à deux pans en tôle de cuivre, avec verrière au faîte
    for z in range(1, 10):
        if p(0.25): continue
        m.put(x, 6, z, "create:framed_glass" if x == 5 else TOLE_DALLE())        # verrière au faîte
m.put(5, 5, 5, "minecraft:chain[axis=y,waterlogged=false]"); m.put(5, 4, 5, AMPOULE_ETEINTE)
m.put(4, 1, 4, "minecraft:barrel[facing=up,open=false]"); m.put(6, 1, 6, "create:depot")
usure_sol(m, 1, 1, 9, 9)
m.jigsaw(0, 0, 5, "west", "kubejs:machine", "kubejs:machine", NS + "machines", "minecraft:tuff_bricks")
m.jigsaw(10, 0, 5, "east", "kubejs:machine", "kubejs:machine", NS + "machines", "minecraft:tuff_bricks")
m.jigsaw(5, 0, 10, "south", "kubejs:machine", "kubejs:machine", NS + "machines", "minecraft:tuff_bricks")

# ---------------------------------------------------------------- l'entrepôt
e = batiment("entrepot", 9, 8, 11, 4)
coque(e, 9, 11, 4, 4, effondre=0.3)
for (x, z) in ((1, 2), (1, 3), (1, 5), (7, 2), (7, 4), (7, 5), (6, 8), (2, 8)):
    for y in range(1, R.randint(2, 3)):
        e.put(x, y, z, "minecraft:barrel[facing=up,open=false]")
e.put(*(1, 1, 7), *coffre("kubejs:chests/avant_poste_entrepot", "east"))
e.put(*(7, 1, 7), *coffre("kubejs:chests/avant_poste_entrepot", "west"))
for z in range(2, 9):                                     # convoyeur hors service au milieu
    e.put(4, 1, z, "minecraft:rail[shape=north_south,waterlogged=false]" if z % 3 else "minecraft:weathered_cut_copper_slab[type=bottom,waterlogged=false]")
for x in range(1, 8):                                     # pont roulant
    e.put(x, 4, 5, "create:weathered_iron_block")
e.put(4, 3, 5, "minecraft:chain[axis=y,waterlogged=false]"); e.put(4, 2, 5, "minecraft:weathered_copper")
e.put(7, 4, 9, TOILE)

# ---------------------------------------------------------------- l'atelier
a = batiment("atelier", 9, 10, 9, 4)
coque(a, 9, 9, 4, 4, effondre=0.4, sol=SOL, cheminee=(7, 7, 3))
a.put(2, 1, 6, "create:andesite_casing"); a.put(2, 2, 6, "create:mechanical_press")
a.put(2, 1, 5, "create:depot")
a.put(3, 1, 7, "create:cogwheel[axis=x]"); a.put(4, 1, 7, "create:shaft[axis=x]"); a.put(5, 2, 7, "create:large_cogwheel[axis=x]")
a.put(6, 1, 5, "minecraft:crafting_table"); a.put(6, 1, 4, "minecraft:damaged_anvil[facing=north]")
a.put(*(7, 1, 2), *coffre("kubejs:chests/avant_poste_atelier", "west"))
a.put(1, 1, 2, "minecraft:smithing_table")
a.put(6, 1, 3, "create:andesite_casing"); a.put(6, 2, 3, "create:shaft[axis=y]"); a.put(6, 3, 3, "create:cogwheel[axis=y]")
for x in range(1, 8):                                     # arbre de transmission sous le toit
    a.put(x, 4, 4, "create:shaft[axis=x]")
conduite_facade(a, 9, 3)

# ---------------------------------------------------------------- le dortoir
d = batiment("dortoir", 9, 8, 9, 4)
coque(d, 9, 9, 4, 4, effondre=0.2)
for z in (2, 5):
    for (x, f) in ((1, "east"), (7, "west")):
        coul = ch("gray", "brown", "light_gray")
        dx = 1 if f == "east" else -1
        d.put(x, 1, z, "minecraft:%s_bed[facing=%s,occupied=false,part=head]" % (coul, "west" if f == "east" else "east"))
        d.put(x + dx, 1, z, "minecraft:%s_bed[facing=%s,occupied=false,part=foot]" % (coul, "west" if f == "east" else "east"))
d.put(*(4, 1, 7), *coffre("kubejs:chests/avant_poste_dortoir", "north"))
d.put(1, 1, 7, "minecraft:barrel[facing=up,open=false]")
for x in range(1, 8):                                     # radiateur : tuyau de chauffage le long du mur du fond
    if x not in (1, 4):
        d.put(x, 2, 7, tuyau("x"))
for (x, y, z) in ((1, 4, 7), (7, 4, 1)):
    d.put(x, y, z, TOILE)
d.put(4, 4, 4, "minecraft:chain[axis=y,waterlogged=false]"); d.put(4, 3, 4, AMPOULE_ETEINTE)

# ================================================================ MACHINES DE DISTRIBUTION (une par catégorie du catalogue)
# Pas de « Magie sauvage » : l'Empire a interdit l'Écho. Ce sont les camps réfractaires qui le vendent.
def carte(k): return Compound({"minecraft:custom_data": Compound({"cible": String(k)})})
def plan(k): return Compound({"minecraft:custom_data": Compound({"plan": String(k)})})
# Les comptoirs ne vendent que ce qu'on ne fait pas soi-même en un clin d'œil : des pièces de Create par lots (contre les
# fabrications à répétition) et des cartes vers les structures (contre les recherches). Les paliers suivants sont dans
# les salles scellées. Chaque objet : (id, nombre, prix, composants ou None).
CATALOGUE = {
 "pieces": [("create:shaft", 32, dict(bevel=1), None), ("create:cogwheel", 16, dict(bevel=1), None),
            ("create:large_cogwheel", 8, dict(bevel=1), None), ("create:andesite_casing", 16, dict(bevel=2), None),
            ("create:gearbox", 8, dict(bevel=2), None), ("create:belt_connector", 16, dict(bevel=2), None),
            ("create:andesite_funnel", 16, dict(bevel=1), None)],
 "cartographe": [("airain:empire_map", 1, dict(sprocket=1), carte(k)) for k in
                 ("avant_poste", "camp", "ruine", "epreuve", "bataille", "enfouie")],
 "plans": [("airain:blueprint", 1, dict(sprocket=1), plan(k)) for k in ("moulin_vent", "centrale_roues", "meunerie")]
          + [("minecraft:gunpowder", 16, dict(bevel=2), None), ("create:empty_schematic", 4, dict(bevel=1), None)],
}
for cat, objets in CATALOGUE.items():
    mc = piece(NS + "machine_" + cat, 7, 6, 2)
    debut = (7 - len(objets)) // 2
    for x in range(7):
        mc.put(x, 0, 0, "minecraft:polished_tuff"); mc.put(x, 0, 1, "minecraft:tuff_bricks")
        for y in range(1, 4):
            mc.put(x, y, 1, "create:copper_casing" if y < 3 else "minecraft:waxed_oxidized_cut_copper")
        i = x - debut
        if 0 <= i < len(objets):
            o, n, prix, comp = objets[i]
            mc.put(*(x, 1, 0), *distributeur(o, n, "north", composants=comp, **prix))
        else:
            mc.put(x, 1, 0, "minecraft:waxed_oxidized_copper")
        mc.put(x, 2, 0, "minecraft:waxed_cut_copper_slab[type=top,waterlogged=false]")
        mc.put(x, 4, 1, tuyau("x"))                                     # alimentation de la machine
    mc.put(0, 4, 1, "create:copper_casing"); mc.put(6, 4, 1, "create:copper_casing")
    mc.put(3, 5, 1, "create:cogwheel[axis=z]")
    mc.put(*(3, 3, 0), *panneau("airain.machine." + cat, face="north", couleur="white"))
    mc.put(1, 3, 0, AMPOULE); mc.put(5, 3, 0, AMPOULE)
    mc.jigsaw(3, 0, 0, "north", "kubejs:machine", "kubejs:machine", "minecraft:empty", "minecraft:polished_tuff")

# ================================================================ SALLES SCELLÉES : coffres-forts de fonte, roue de verrouillage
SCELLEES = {
 "cuivre": ("minecraft:waxed_copper_block", "minecraft:waxed_cut_copper", [
     ("create:fluid_pipe", 32, dict(bevel=2), None), ("create:mechanical_pump", 4, dict(sprocket=1), None),
     ("create:fluid_tank", 8, dict(sprocket=1), None), ("create:copper_casing", 16, dict(bevel=2), None),
     ("create:spout", 2, dict(sprocket=1), None), ("create:item_drain", 2, dict(sprocket=1), None),
     ("minecraft:enchanted_book", 1, dict(cog=1), livre_enchante("minecraft:unbreaking", 2))]
   + [("airain:empire_map", 1, dict(sprocket=2), carte(k)) for k in ("monument", "relais", "cite", "epave")]),
 "laiton": ("create:brass_block", "create:brass_casing", [
     ("create:electron_tube", 8, dict(sprocket=1), None), ("create:brass_casing", 16, dict(sprocket=1), None),
     ("create:precision_mechanism", 4, dict(sprocket=2), None), ("create:mechanical_arm", 2, dict(sprocket=2), None),
     ("create:deployer", 4, dict(sprocket=2), None)]
   + [("airain:empire_map", 1, dict(cog=1), carte(k)) for k in ("forteresse", "bastion", "cite_antique", "capsules", "sanctuaire", "grand_relais")]),
 "ciel": ("minecraft:light_blue_glazed_terracotta", "create:brass_casing", [
     ("minecraft:ender_pearl", 16, dict(cog=2), None),
     ("minecraft:firework_rocket", 16, dict(cog=1), Compound({"minecraft:fireworks": Compound({"flight_duration": Byte(2), "explosions": List[Compound]([])})})),
     ("minecraft:enchanted_book", 1, dict(crown=1), livre_enchante("minecraft:mending", 1)),
     ("minecraft:totem_of_undying", 1, dict(crown=1), None),
     ("minecraft:enchanted_book", 1, dict(cog=4), livre_enchante("minecraft:fortune", 3))]
   + [("airain:empire_map", 1, dict(cog=2), carte(k)) for k in ("station", "citadelle", "dirigeable")]),
}
# places des distributeurs dans une salle : le mur du fond (5), puis les murs de côté (3 + 3), face à l'intérieur
PLACES_SALLE = [(1 + i, 5, "north") for i in range(5)] + [(1, 4 - i, "east") for i in range(3)] + [(5, 4 - i, "west") for i in range(3)]
for palier, (marque, garniture, ventes) in SCELLEES.items():
    s = piece(NS + "salle_" + palier, 7, 8, 7, fond=AIR)
    for x in range(7):
        for z in range(7):
            s.put(x, 0, z, "create:industrial_iron_block" if z > 0 else "minecraft:tuff_bricks")
            if z >= 1:
                for y in range(1, 5):
                    if x in (0, 6) or z in (1, 6):
                        s.put(x, y, z, "minecraft:tuff_bricks" if y == 1 else ("create:industrial_iron_block" if y != 4 else garniture))
                s.put(x, 5, z, "create:industrial_iron_block")
    s.put(3, 1, 1, "minecraft:iron_door[facing=south,half=lower,hinge=left,open=false,powered=false]")
    s.put(3, 2, 1, "minecraft:iron_door[facing=south,half=upper,hinge=left,open=false,powered=false]")
    s.put(3, 3, 1, marque)                                   # la marque du sceau : le script la lit
    s.put(5, 2, 0, "create:large_cogwheel[axis=z]")          # roue de verrouillage du coffre-fort
    s.put(*(1, 3, 0), *panneau("", face="north", couleur="white", lignes=[
        '""', '{"translate":"airain.sceau.%s"}' % palier, '{"translate":"airain.sceau.requis.%s"}' % palier, '""']))
    for x in range(1, 6):                                     # conduites sur le toit
        s.put(x, 6, 3, tuyau("x"))
    s.put(5, 6, 5, "create:weathered_iron_block"); s.put(5, 7, 5, VAPEUR)
    for (o, n, prix, comp), (x, z, face) in zip(ventes, PLACES_SALLE):
        s.put(*(x, 1, z), *distributeur(o, n, face, composants=comp, **prix))
        s.put(x, 2, z, garniture)
    s.put(3, 4, 3, AMPOULE)
    s.jigsaw(3, 0, 0, "north", "kubejs:salle", "kubejs:salle", "minecraft:empty", "minecraft:tuff_bricks")
    s.jigsaw(3, 1, 6, "south", "kubejs:rue", "kubejs:rue", NS + "rues", "create:industrial_iron_block")   # une rue repart derrière

# ================================================================ TOUR DE GUET (à l'intérieur de l'enceinte)
# Cabine de tôle au pied, fût à poteaux de fonte contreventés, dos plein pour l'échelle, poste couvert en haut.
t = piece(NS + "tour", 5, 15, 5, fond=VOID)
for x in range(5):
    for z in range(5):
        t.put(x, 0, z, "minecraft:tuff_bricks")
        coin = x in (0, 4) and z in (0, 4)
        bord = x in (0, 4) or z in (0, 4)
        for y in range(1, 10):
            if coin:
                t.put(x, y, z, "minecraft:tuff_bricks" if y == 1 else "create:industrial_iron_block")
            elif z == 4:                                        # dos plein : l'échelle s'y accroche
                t.put(x, y, z, MUR_SOCLE() if y <= 2 else PLAQUE())
            elif bord and y <= 3:                                # cabine de tôle au pied
                t.put(x, y, z, MUR_SOCLE() if y == 1 else PLAQUE())
            elif bord and y in (5, 7):                           # entretoises reliées
                t.put(x, y, z, "create:copper_bars")
            elif bord and y in (4, 8):
                t.put(x, y, z, "create:weathered_iron_block")
            elif not bord:
                t.put(x, y, z, AIR)
        t.put(x, 9, z, "create:weathered_iron_block" if bord else "create:copper_tiles")   # plancher du poste
t.put(2, 1, 0, AIR); t.put(2, 2, 0, AIR)                       # porte de la cabine
t.put(2, 3, 0, "create:weathered_iron_block")
for y in range(1, 10):
    t.put(2, y, 3, "create:copper_ladder[facing=north,waterlogged=false]")
for (x, z) in ((0, 1), (0, 2), (0, 3), (4, 1), (4, 2), (4, 3), (1, 0), (3, 0)):
    t.put(x, 2, z, FENETRE)                                     # hublots de la cabine
# le poste de guet : garde-corps, poteaux, toit de tôle, projecteur suspendu
for x in range(5):
    for z in range(5):
        coin = x in (0, 4) and z in (0, 4)
        if coin:
            for y in (10, 11):
                t.put(x, y, z, "create:industrial_iron_block")
        elif x in (0, 4) or z in (0, 4):
            t.put(x, 10, z, "create:copper_bars")
        t.put(x, 12, z, "create:weathered_iron_block" if x in (0, 4) or z in (0, 4) else "create:copper_tiles")
        if 0 < x < 4 and 0 < z < 4:
            t.put(x, 13, z, TOLE_DALLE())
t.put(2, 13, 2, "create:weathered_copper_shingles"); t.put(2, 14, 2, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
t.put(2, 11, 2, "minecraft:chain[axis=y,waterlogged=false]"); t.put(2, 10, 2, "minecraft:redstone_lamp[lit=false]")
t.put(2, 9, 3, AIR)
t.put(4, 13, 4, VAPEUR)
# la tour s'accroche par son dos plein (au mur ou derrière un bâtiment) : sa porte donne toujours sur la cour                                         # soupape sur le toit
t.jigsaw(2, 0, 4, "south", "kubejs:mur", "kubejs:mur", "minecraft:empty", "minecraft:tuff_bricks")

# ================================================================ L'ENCEINTE : muraille de tôle sur socle de pierre
HAUT_ENC = 64        # la boîte de l'enceinte : tout ce qui pousse à l'intérieur doit y tenir, relief compris
def enceinte(nom, graine, ENC=71, centres="centres", abords="abords"):
    """Muraille carrée de côté ENC ; son bloc puzzle central fait pousser la place du pool `centres`.
    La pièce épouse le terrain (ses blocs suivent le sol quelle que soit la hauteur de sa boîte) : on lui donne une
    boîte très haute, descendue sous le sol par la structure (start_height), pour que les bâtiments posés sur une
    pente ou une butte n'en dépassent pas — sinon le jeu les refuse et la cour reste vide."""
    MIL = ENC // 2
    rr = random.Random(graine)
    e = Piece(NS + nom, ENC, HAUT_ENC, ENC); pieces.append(e)
    def dist_bord(x, z): return min(x, z, ENC - 1 - x, ENC - 1 - z)
    def le_long(x, z):                              # axe de la muraille à cet endroit
        return "x" if min(z, ENC - 1 - z) <= min(x, ENC - 1 - x) else "z"
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
            hauteurs[tour_[j]] = {"intact": 7, "abime": rr.randint(2, 5), "effondre": rr.choice([0, 1, 1])}[typ]
        k += long_
    def h_ext(x, z):
        nx = 1 if x == 2 else (ENC - 2 if x == ENC - 3 else x)
        nz = 1 if z == 2 else (ENC - 2 if z == ENC - 3 else z)
        return hauteurs.get((x, z), hauteurs.get((nx, nz), 0))
    for x in range(ENC):
        for z in range(ENC):
            d = dist_bord(x, z)
            if d not in (1, 2):
                continue
            h = h_ext(x, z)
            e.put(x, 0, z, "minecraft:tuff_bricks")
            for y in range(1, h + 1):
                if y <= 2:
                    e.put(x, y, z, MUR_SOCLE())                 # socle de pierre
                elif y == 4:
                    e.put(x, y, z, GRILLE_CUIVRE if d == 1 and (x + z) % 3 == 0 else PLAQUE())
                else:
                    e.put(x, y, z, PLAQUE())                    # plaques de cuivre et de fer
            if h == 7:
                e.put(x, 8, z, "create:weathered_iron_block" if d == 2 else "create:copper_bars")   # chemin de ronde + garde-corps
            if h <= 1 and rr.random() < 0.4:                     # gravats au pied des brèches
                e.put(x, 1, z, rr.choice(("minecraft:cobbled_deepslate", "minecraft:weathered_copper", "create:weathered_iron_block", "minecraft:tuff")))
    # conduite de vapeur côté intérieur (anneau 3), qui court le long des tronçons intacts
    for x in range(ENC):
        for z in range(ENC):
            if dist_bord(x, z) == 3 and (7 < x < ENC - 8 or 7 < z < ENC - 8):
                hx = h_ext(1 if x == 3 else (ENC - 2 if x == ENC - 4 else x), 1 if z == 3 else (ENC - 2 if z == ENC - 4 else z))
                if hx >= 5:
                    e.put(x, 5, z, tuyau(le_long(x, z)))
                if hx >= 4 and (x + z) % 8 == 0:               # contreforts de fonte
                    for y in range(1, 5):
                        e.put(x, y, z, "minecraft:tuff_bricks" if y == 1 else "create:industrial_iron_block")
    # tours d'angle : deux châteaux d'eau, une cheminée d'usine, une ruine
    roles = ["reservoir", "cheminee", "reservoir", "ruine"]; rr.shuffle(roles)
    for i, (ox, oz) in enumerate(((0, 0), (ENC - 7, 0), (0, ENC - 7), (ENC - 7, ENC - 7))):
        role = roles[i]
        haut = 4 if role == "ruine" else 9
        for x in range(ox, ox + 7):
            for z in range(oz, oz + 7):
                bord = x in (ox, ox + 6) or z in (oz, oz + 6)
                coin = x in (ox, ox + 6) and z in (oz, oz + 6)
                e.put(x, 0, z, "minecraft:tuff_bricks")
                for y in range(1, haut + 1):
                    if bord:
                        e.put(x, y, z, MUR_SOCLE() if y <= 2 else ("create:industrial_iron_block" if coin else PLAQUE()))
                    else:
                        e.put(x, y, z, AIR)
                if role != "ruine":
                    e.put(x, haut, z, "create:copper_tiles" if not bord else "create:weathered_iron_block")
                    if bord:
                        e.put(x, haut + 1, z, "create:copper_bars")
        if role == "reservoir":                       # cuve de cuivre de 5×5, posée sur la tour
            for x in range(ox + 1, ox + 6):
                for z in range(oz + 1, oz + 6):
                    rond = not (x in (ox + 1, ox + 5) and z in (oz + 1, oz + 5))
                    for y in range(haut + 1, haut + 5):
                        if rond and (x in (ox + 1, ox + 5) or z in (oz + 1, oz + 5) or y == haut + 4):
                            e.put(x, y, z, "minecraft:oxidized_copper" if y != haut + 2 else GRILLE_CUIVRE)
            e.put(ox + 3, haut + 5, oz + 3, VAPEUR)
        elif role == "cheminee":                     # cheminée de briques de 3×3 qui fume encore
            for x in range(ox + 2, ox + 5):
                for z in range(oz + 2, oz + 5):
                    for y in range(haut + 1, haut + 9):
                        if x in (ox + 2, ox + 4) or z in (oz + 2, oz + 4):
                            e.put(x, y, z, "minecraft:bricks" if y < haut + 8 else "create:weathered_iron_block")
            e.put(ox + 3, haut + 7, oz + 3, VAPEUR)
        else:                                        # tour effondrée : débris de cuve
            for _ in range(10):
                e.put(ox + rr.randint(0, 6), rr.randint(1, 2), oz + rr.randint(0, 6),
                      rr.choice(("minecraft:oxidized_copper", "create:weathered_iron_block", GRILLE_CUIVRE)))
        for y in range(1, haut):
            e.put(ox + 3, y, oz + 5 if oz == 0 else oz + 1,
                  "create:copper_ladder[facing=%s,waterlogged=false]" % ("north" if oz == 0 else "south"))
        if role != "ruine":
            e.put(ox + 3, haut, oz + 5 if oz == 0 else oz + 1, AIR)
            for (wx, wz) in ((ox + 3, oz), (ox, oz + 3), (ox + 6, oz + 3), (ox + 3, oz + 6)):
                e.put(wx, 5, wz, FENETRE)
        px = ox + 6 if ox == 0 else ox
        for y in (1, 2):
            e.put(px, y, oz + 3, AIR)
    # portails : cadre de cuivre, grandes roues dentées de part et d'autre, rails dessous
    def portail(cote):
        def pos(t, d): return {"n": (t, d), "s": (t, ENC - 1 - d), "o": (d, t), "e": (ENC - 1 - d, t)}[cote]
        ax_long = "x" if cote in "ns" else "z"                 # axe le long du mur
        ax_trav = "z" if cote in "ns" else "x"                 # axe qui traverse le mur
        for t in range(MIL - 4, MIL + 5):
            for d in range(0, 4):
                x, z = pos(t, d)
                pilier = t in (MIL - 4, MIL - 3, MIL + 3, MIL + 4)
                e.put(x, 0, z, "minecraft:tuff_bricks" if pilier else PAVE())
                for y in range(1, 10):
                    if pilier:
                        if y <= 2: e.put(x, y, z, MUR_SOCLE())
                        elif y <= 8: e.put(x, y, z, "create:industrial_iron_block" if d in (0, 3) else PLAQUE())
                        elif y == 9: e.put(x, y, z, TOLE_DALLE())
                    elif y <= 4:
                        e.put(x, y, z, AIR)
                    elif y in (5, 6) and d in (1, 2):
                        e.put(x, y, z, "create:copper_casing" if y == 5 else PLAQUE())    # linteau de cuivre
                    else:
                        e.put(x, y, z, VOID)
        # rails sous le portail, perpendiculaires au mur
        for d in range(0, 4):
            x, z = pos(MIL, d)
            e.put(x, 1, z, "minecraft:rail[shape=%s,waterlogged=false]" % ("north_south" if cote in "ns" else "east_west"))
        # grandes roues dentées sur la face extérieure des piliers, et tuyau au-dessus du passage
        for t in (MIL - 3, MIL + 3):
            x, z = pos(t, 0)
            e.put(x, 4, z, "create:large_cogwheel[axis=%s]" % ax_trav)
        for t in range(MIL - 2, MIL + 3):
            x, z = pos(t, 0)
            e.put(x, 6, z, tuyau(ax_long))
        x, z = pos(MIL, 0); e.put(x, 7, z, AMPOULE_ETEINTE)
    for cote in rr.sample("nseo", rr.choice((3, 4))):
        portail(cote)
    e.jigsaw(MIL, 1, MIL, "north", "kubejs:coeur", "kubejs:place", NS + centres, VOID)
    # abords : bâtiments, tours et dépôts adossés au mur, porte vers la cour (loin des portails et des angles)
    pas = (13, 23) if ENC < 100 else (13, 25, 37)
    for t_ in list(pas) + [ENC - 1 - v for v in pas]:
        for (x, z, f) in ((t_, 3, "south"), (t_, ENC - 4, "north"), (3, t_, "east"), (ENC - 4, t_, "west")):
            e.jigsaw(x, 0, z, f, "kubejs:abord", "kubejs:mur", NS + abords, "minecraft:tuff_bricks")
    # quelques caisses et barils au pied du mur entre les emplacements
    for _ in range(ENC // 6):
        cote = rr.choice("nseo"); t_ = rr.randint(9, ENC - 10)
        if abs(t_ - MIL) < 7 or any(abs(t_ - v) < 6 for v in list(pas) + [ENC - 1 - v for v in pas]):
            continue
        x, z = {"n": (t_, 4), "s": (t_, ENC - 5), "o": (4, t_), "e": (ENC - 5, t_)}[cote]
        e.put(x, 1, z, rr.choice(("minecraft:barrel[facing=up,open=false]", "create:andesite_casing", "create:copper_casing")))
        if rr.random() < 0.5:
            e.put(x, 2, z, rr.choice(("minecraft:barrel[facing=up,open=false]", "create:andesite_casing")))
    return e

for i, g_ in enumerate((71, 1789, 4242)):
    enceinte("enceinte_%s" % "abc"[i], g_)

# ================================================================ CITÉ MÉCANIQUE : place de la tour d'horloge, grande enceinte
h = piece(NS + "centre_horloge", 25, 26, 25, fond=AIR)
for x in range(25):
    for z in range(25):
        bord = x in (0, 24) or z in (0, 24)
        rayon = x == 12 or z == 12
        h.put(x, 0, z, "minecraft:tuff_bricks" if bord else (CARREAU_CUIVRE() if rayon else SOL()))
T0, T1 = 10, 14                                           # la tour : 5×5, 18 de haut
for y in range(1, 19):
    for x in range(T0, T1 + 1):
        for z in range(T0, T1 + 1):
            bord = x in (T0, T1) or z in (T0, T1)
            coin = x in (T0, T1) and z in (T0, T1)
            if bord:
                h.put(x, y, z, MUR_SOCLE() if y <= 2 else ("create:industrial_iron_block" if coin else
                      (FENETRE if y % 5 == 0 and not coin else PLAQUE())))
h.put(12, 1, T0, AIR); h.put(12, 2, T0, AIR)
for y in range(1, 18):
    h.put(12, y, T1 - 1, "create:copper_ladder[facing=north,waterlogged=false]")
for x in range(T0 + 1, T1):
    for z in range(T0 + 1, T1):
        h.put(x, 17, z, "create:copper_tiles")
h.put(12, 17, T1 - 1, AIR)
h.put(12, 16, 12, "minecraft:bell[attachment=ceiling,facing=north,powered=false]")
# quatre cadrans : grandes roues dentées sur chaque face
for (x, z, ax) in ((12, T0 - 1, "z"), (12, T1 + 1, "z"), (T0 - 1, 12, "x"), (T1 + 1, 12, "x")):
    h.put(x, 14, z, "create:large_cogwheel[axis=%s]" % ax)
    h.put(x, 12, z, AMPOULE)
# toit pyramidal de tôle et flèche
for niv, (a0, a1) in enumerate(((T0, T1), (T0 + 1, T1 - 1), (T0 + 2, T1 - 2))):
    for x in range(a0, a1 + 1):
        for z in range(a0, a1 + 1):
            if x in (a0, a1) or z in (a0, a1) or niv == 2:
                h.put(x, 19 + niv, z, "create:weathered_copper_shingles")
h.put(12, 22, 12, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
h.put(12, 23, 12, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
h.put(T0, 19, T0, VAPEUR)                                 # soupape qui fume à un angle
for (x, z) in ((3, 3), (21, 3), (3, 21), (21, 21), (8, 8), (16, 8), (8, 16), (16, 16)):
    lampadaire(h, x, z)
for (x, z) in ((T0 - 1, T0 - 1), (T1 + 1, T0 - 1), (T0 - 1, T1 + 1), (T1 + 1, T1 + 1)):   # tuyaux qui descendent de la tour
    for y in range(1, 10):
        h.put(x, y, z, tuyau("y"))
usure_sol(h, 1, 1, 23, 23, mousse=0.04)
h.jigsaw(12, 1, 0, "north", "kubejs:rue", "kubejs:rue", NS + "rues_cite", VOID)
h.jigsaw(24, 1, 12, "east", "kubejs:rue", "kubejs:rue", NS + "rues_cite", VOID)
h.jigsaw(12, 1, 24, "south", "kubejs:rue", "kubejs:rue", NS + "rues_cite", VOID)
h.jigsaw(0, 1, 12, "west", "kubejs:rue", "kubejs:rue", NS + "rues_cite", VOID)
h.jigsaw(5, 0, 0, "north", "kubejs:salle", "kubejs:salle", NS + "salles_cuivre_c", "minecraft:tuff_bricks")
h.jigsaw(24, 0, 5, "east", "kubejs:salle", "kubejs:salle", NS + "salles_laiton_c", "minecraft:tuff_bricks")
h.jigsaw(19, 0, 24, "south", "kubejs:salle", "kubejs:salle", NS + "salles_ciel_c", "minecraft:tuff_bricks")
h.jigsaw(20, 0, 0, "north", "kubejs:batiment", "kubejs:batiment", NS + "marches_cite", "minecraft:tuff_bricks")
h.jigsaw(5, 0, 24, "south", "kubejs:batiment", "kubejs:batiment", NS + "marches_cite", "minecraft:tuff_bricks")
h.jigsaw(12, 1, 12, "south", "kubejs:place", "kubejs:coeur", "minecraft:empty", AIR)

for i, g_ in enumerate((303, 9090)):
    enceinte("enceinte_cite_%s" % "ab"[i], g_, ENC=111, centres="centres_cite", abords="abords_cite")

# ================================================================ PETITES PIÈCES DE REMPLISSAGE (avant-postes et cités)
k = piece(NS + "kiosque", 5, 7, 5, fond=AIR)                 # kiosque à toit de tôle
for x in range(5):
    for z in range(5):
        k.put(x, 0, z, CARREAU_CUIVRE() if 0 < x < 4 and 0 < z < 4 else "minecraft:tuff_bricks")
for (x, z) in ((0, 0), (4, 0), (0, 4), (4, 4)):
    for y in range(1, 4):
        k.put(x, y, z, "create:copper_bars")
for x in range(5):
    for z in range(5):
        k.put(x, 4, z, TOLE_DALLE())
k.put(2, 5, 2, "create:weathered_copper_shingles"); k.put(2, 6, 2, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
k.put(2, 3, 2, "minecraft:chain[axis=y,waterlogged=false]"); k.put(2, 2, 2, AMPOULE_ETEINTE)
k.put(1, 1, 3, "minecraft:spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
k.put(3, 1, 3, "minecraft:spruce_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
k.jigsaw(2, 0, 0, "north", "kubejs:batiment", "kubejs:batiment", "minecraft:empty", "minecraft:tuff_bricks")
k.jigsaw(2, 0, 4, "south", "kubejs:mur", "kubejs:mur", "minecraft:empty", "minecraft:tuff_bricks")

rs = piece(NS + "chateau_eau", 5, 11, 5, fond=VOID)          # petit château d'eau sur pieds de fonte
for x in range(5):
    for z in range(5):
        rs.put(x, 0, z, "minecraft:tuff_bricks")
for (x, z) in ((0, 0), (4, 0), (0, 4), (4, 4)):
    for y in range(1, 6):
        rs.put(x, y, z, "create:industrial_iron_block")
for x in range(5):
    for z in range(5):
        rond = not (x in (0, 4) and z in (0, 4))
        for y in range(6, 9):
            if rond and (x in (0, 4) or z in (0, 4) or y in (6, 8)):
                rs.put(x, y, z, "minecraft:oxidized_copper" if y != 7 else GRILLE_CUIVRE)
for y in range(1, 6):
    rs.put(2, y, 2, tuyau("y"))
rs.put(2, 9, 2, "create:weathered_iron_block"); rs.put(2, 10, 2, VAPEUR)
rs.jigsaw(2, 0, 0, "north", "kubejs:batiment", "kubejs:batiment", "minecraft:empty", "minecraft:tuff_bricks")
rs.jigsaw(2, 0, 4, "south", "kubejs:mur", "kubejs:mur", "minecraft:empty", "minecraft:tuff_bricks")

# ================================================================ ABORDS : dépôts adossés au mur (s'accrochent par le dos)
def abord(nom, sx, sy, sz):
    pc = piece(NS + nom, sx, sy, sz, fond=VOID)
    pc.jigsaw(sx // 2, 0, sz - 1, "south", "kubejs:mur", "kubejs:mur", "minecraft:empty", "minecraft:coarse_dirt")
    return pc
dp = abord("depot_caisses", 7, 6, 5)                    # caisses, barils et petite grue de chargement
for x in range(7):
    for z in range(5):
        dp.put(x, 0, z, PAVE())
for (x, z, h, bloc) in ((0, 4, 2, "minecraft:barrel[facing=up,open=false]"), (1, 4, 1, "minecraft:barrel[facing=up,open=false]"),
                        (0, 3, 1, "create:andesite_casing"), (2, 4, 3, "create:andesite_casing"), (3, 4, 2, "create:copper_casing"),
                        (4, 4, 1, "create:andesite_casing"), (1, 2, 1, "minecraft:barrel[facing=north,open=false]"),
                        (3, 3, 1, "create:copper_casing")):
    for y in range(1, h + 1):
        dp.put(x, y, z, bloc)
for y in range(1, 6):
    dp.put(6, y, 4, "create:industrial_iron_block")
for z in range(1, 5):
    dp.put(6, 5, z, "create:weathered_iron_block")      # flèche de la grue
dp.put(5, 5, 4, "create:cogwheel[axis=x]")
dp.put(6, 4, 1, "minecraft:chain[axis=y,waterlogged=false]"); dp.put(6, 3, 1, "minecraft:chain[axis=y,waterlogged=false]")
dp.put(6, 2, 1, "create:copper_casing")                 # une caisse encore suspendue
dp.put(5, 1, 1, "minecraft:rail[shape=north_south,waterlogged=false]"); dp.put(5, 1, 2, "minecraft:rail[shape=north_south,waterlogged=false]")

fr = abord("ferraille", 7, 4, 5)                        # tas de ferraille : pièces d'automates démontés
R2 = random.Random(5)
for x in range(7):
    for z in range(5):
        fr.put(x, 0, z, R2.choice(("minecraft:gravel", "minecraft:coarse_dirt", "minecraft:tuff")))
        h = max(0, 3 - abs(x - 3) - (4 - z) // 2 + R2.randint(-1, 0))
        for y in range(1, h + 1):
            fr.put(x, y, z, R2.choice(("create:weathered_iron_block", "minecraft:oxidized_copper", "minecraft:weathered_cut_copper",
                                       "minecraft:coal_block", GRILLE_CUIVRE, "create:industrial_iron_block")))
fr.put(1, 1, 1, "create:large_cogwheel[axis=y]"); fr.put(5, 1, 1, tuyau("x")); fr.put(6, 1, 1, tuyau("x"))
fr.put(3, 3, 4, "create:cogwheel[axis=z]"); fr.put(4, 2, 2, "create:shaft[axis=x]")
fr.put(2, 1, 0, "minecraft:weathered_copper_bulb[lit=false,powered=false]")      # une « tête » d'automate

ab = abord("abri", 7, 6, 5)                             # appentis de réparation : établi, enclume, meule
for x in range(7):
    for z in range(5):
        ab.put(x, 0, z, PLANCHER())
        if z == 4:
            for y in range(1, 5):
                ab.put(x, y, z, MUR_SOCLE() if y == 1 else PLAQUE())
        if x in (0, 6) and z == 0:
            for y in range(1, 4):
                ab.put(x, y, z, "create:industrial_iron_block")
        if x in (0, 6) and 0 < z < 4:
            ab.put(x, 1, z, MUR_SOCLE())
        ab.put(x, 4, z, TOLE_DALLE() if z < 4 else "create:weathered_iron_block")
ab.put(1, 1, 3, "minecraft:crafting_table"); ab.put(2, 1, 3, "minecraft:chipped_anvil[facing=east]")
ab.put(4, 1, 3, "minecraft:grindstone[face=floor,facing=north]"); ab.put(5, 1, 3, "minecraft:barrel[facing=up,open=false]")
ab.put(5, 2, 3, "minecraft:barrel[facing=up,open=false]"); ab.put(3, 1, 2, "create:depot")
ab.put(3, 3, 2, "minecraft:chain[axis=y,waterlogged=false]"); ab.put(3, 2, 2, AMPOULE_ETEINTE)

# ================================================================ STAND DE TIR (cités)
sd = batiment("stand_tir", 9, 7, 17, 4)
for x in range(9):
    for z in range(17):
        sd.put(x, 0, z, "minecraft:tuff_bricks" if x in (0, 8) or z in (0, 16) else (SOL() if z < 5 else "minecraft:coarse_dirt"))
        if x in (0, 8):
            for y in range(1, 4):
                sd.put(x, y, z, "minecraft:tuff_bricks" if y == 1 else PLAQUE())
for x in range(9):
    for z in range(0, 5):
        sd.put(x, 5, z, TOLE_DALLE())                     # auvent au-dessus du pas de tir
    for y in range(1, 5):
        sd.put(x, y, 16, "minecraft:hay_block[axis=y]" if 0 < x < 8 and y < 4 else "minecraft:tuff_bricks")   # butte de paille
for (x, z) in ((0, 0), (8, 0), (0, 4), (8, 4)):
    for y in range(1, 5):
        sd.put(x, y, z, "create:industrial_iron_block")
sd.put(4, 1, 0, AIR); sd.put(4, 2, 0, AIR)
for x in (1, 2, 3, 5, 6, 7):
    sd.put(x, 1, 0, PLAQUE()); sd.put(x, 2, 0, AIR)
for x in range(1, 8):                                     # comptoir du pas de tir
    if x not in (2, 4, 6):
        sd.put(x, 1, 3, "minecraft:waxed_cut_copper_slab[type=top,waterlogged=false]")
for x in (3, 5):
    for z in range(5, 15):
        sd.put(x, 1, z, "create:copper_bars")
for x in (2, 4, 6):
    sd.put(x, 1, 15, "minecraft:target[power=0]"); sd.put(x, 2, 15, "minecraft:target[power=0]")
    sd.put(x, 1, 9, "create:industrial_iron_block"); sd.put(x, 2, 9, "minecraft:target[power=0]")
sd.put(*(1, 1, 1), *coffre("kubejs:chests/stand_tir", "south"))
sd.put(7, 1, 1, "minecraft:barrel[facing=up,open=false]"); sd.put(7, 2, 1, "minecraft:barrel[facing=up,open=false]")
sd.put(*(4, 3, 1), *panneau("airain.cite.stand_tir", face="south", couleur="white"))
sd.put(4, 4, 2, AMPOULE)

# ================================================================ LABORATOIRE D'ESSAIS (cités) : atelier en surface, salle d'essai en sous-sol
B0 = 6                                                    # niveau du rez-de-chaussée dans la pièce
lb = piece(NS + "laboratoire", 11, B0 + 9, 11, fond=AIR)
lb.jigsaw(5, B0, 0, "north", "kubejs:batiment", "kubejs:batiment", "minecraft:empty", "minecraft:polished_tuff")
lb.jigsaw(5, B0, 10, "south", "kubejs:mur", "kubejs:mur", NS + "murs", "minecraft:tuff_bricks")
coque(lb, 11, 11, 5, 5, effondre=0.15, sol=SOL, cheminee=(9, 9, 3), base=B0)
# rez-de-chaussée : établis et prototypes
lb.put(2, B0 + 1, 2, "minecraft:crafting_table"); lb.put(3, B0 + 1, 2, "minecraft:smithing_table")
lb.put(8, B0 + 1, 2, "create:andesite_casing"); lb.put(8, B0 + 2, 2, "create:mechanical_press")
lb.put(7, B0 + 1, 2, "create:depot"); lb.put(2, B0 + 1, 6, "create:millstone")
lb.put(2, B0 + 2, 6, "create:cogwheel[axis=y]"); lb.put(3, B0 + 1, 7, "create:encased_fan[facing=up]")
for x in range(2, 9):
    lb.put(x, B0 + 4, 5, "create:shaft[axis=x]")
lb.put(*(8, B0 + 1, 8), *coffre("kubejs:chests/laboratoire_essais", "west"))
# trappe et échelle vers le sous-sol
lb.put(1, B0, 9, "minecraft:iron_trapdoor[facing=north,half=top,open=true,powered=false,waterlogged=false]")
for y in range(1, B0):
    lb.put(1, y, 9, "create:copper_ladder[facing=north,waterlogged=false]")
# sous-sol : salle de contrôle (z 1-3) | vitre | fosse d'essai (z 5-9)
for x in range(11):
    for z in range(11):
        bord = x in (0, 10) or z in (0, 10)
        lb.put(x, 0, z, "create:industrial_iron_block")
        for y in range(1, B0):
            lb.put(x, y, z, "create:industrial_iron_block" if bord else AIR)
lb.put(1, B0 - 1, 9, AIR)
for x in range(1, 10):
    for y in range(1, B0):
        lb.put(x, y, 4, "create:framed_glass" if 2 <= y <= 3 and 2 <= x <= 8 else "create:industrial_iron_block")
lb.put(9, 1, 4, AIR); lb.put(9, 2, 4, AIR)                # porte vers la fosse
for x in range(1, 10):
    for z in range(5, 10):
        lb.put(x, 0, z, ch("minecraft:blackstone", "minecraft:polished_blackstone", "minecraft:coal_block", "create:industrial_iron_block"))
# l'expérience : un automate démonté dans une cage de cuivre, relié à une bobine
for x in range(3, 8):
    for z in range(6, 9):
        if x in (3, 7) or z in (6, 8):
            for y in range(1, 4):
                lb.put(x, y, z, "create:copper_bars")
lb.put(5, 1, 7, "minecraft:weathered_copper"); lb.put(5, 2, 7, "minecraft:oxidized_copper_bulb[lit=true,powered=false]")
lb.put(4, 1, 7, "create:cogwheel[axis=x]"); lb.put(6, 2, 7, "create:cogwheel[axis=x]")
lb.put(5, 4, 7, "minecraft:lightning_rod[facing=down,powered=false,waterlogged=false]")
for z in range(5, 10):
    lb.put(5, 5, z, "minecraft:chain[axis=z,waterlogged=false]")
lb.put(1, 1, 8, "minecraft:copper_block"); lb.put(1, 2, 8, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
# salle de contrôle : pupitre avec le journal d'essais, leviers, ampoules
journal = Compound({"id": String("minecraft:written_book"), "count": Int(1), "components": Compound({
    "minecraft:written_book_content": Compound({"title": String("Essais"), "author": String("Labo 3"),
        "pages": List[String]([String(json.dumps({"translate": "airain.essais.p%d" % i})) for i in (1, 2, 3)])}), "minecraft:custom_data": Compound({"airain_doc": String("essais")})})})
lb.put(5, 1, 2, "minecraft:lectern[facing=south,has_book=true,powered=false]",
       Compound({"id": String("minecraft:lectern"), "Book": journal, "Page": Int(0)}))
for x in (3, 7):
    lb.put(x, 1, 3, "minecraft:lever[face=floor,facing=south,powered=false]")
    lb.put(x, 4, 2, AMPOULE)
lb.put(8, 1, 1, "minecraft:barrel[facing=up,open=false]")

# ================================================================ GRAND MARCHÉ (cités) : 6 machines
gm = piece(NS + "grand_marche", 15, 9, 15, fond=AIR)
gm.jigsaw(7, 0, 0, "north", "kubejs:batiment", "kubejs:batiment", "minecraft:empty", "minecraft:polished_tuff")
for x in range(15):
    for z in range(15):
        gm.put(x, 0, z, "minecraft:tuff_bricks" if x in (0, 14) or z in (0, 14) else (CARREAU_CUIVRE() if (x + z) % 4 == 0 else SOL()))
for (x, z) in ((1, 1), (13, 1), (1, 13), (13, 13), (7, 1), (7, 13), (1, 7), (13, 7)):
    gm.put(x, 1, z, "minecraft:tuff_bricks")
    for y in range(2, 6):
        gm.put(x, y, z, "create:industrial_iron_block")
for i in range(1, 14):
    for (x, z) in ((i, 1), (i, 13), (1, i), (13, i)):
        gm.put(x, 6, z, "create:weathered_iron_block")
for x in range(1, 14):
    for z in range(1, 14):
        if not p(0.15):
            gm.put(x, 7, z, "create:framed_glass" if x == 7 or z == 7 else TOLE_DALLE())
gm.put(7, 6, 7, "minecraft:chain[axis=y,waterlogged=false]"); gm.put(7, 5, 7, AMPOULE)
gm.put(7, 1, 7, "minecraft:waxed_copper_block"); gm.put(7, 2, 7, "create:large_cogwheel[axis=x]")
for (x, z, f) in ((0, 3, "west"), (0, 11, "west"), (14, 3, "east"), (14, 11, "east"), (3, 14, "south"), (11, 14, "south")):
    gm.jigsaw(x, 0, z, f, "kubejs:machine", "kubejs:machine", NS + "machines", "minecraft:tuff_bricks")
usure_sol(gm, 1, 1, 13, 13, mousse=0.05)

_rr = random.Random(1805)
grand_etendard(c, 10, 1, 4, "east", _rr)              # deux étendards de part et d'autre de la fontaine
grand_etendard(c, 4, 1, 10, "west", _rr)

# ================================================================ RETOUCHES DE LIAM (avant les copies cité et climats, qui en héritent)
from pieces import appliquer_retouches
print("retouches :", appliquer_retouches(pieces, lambda nom: "/tempere/" in nom))
# les salles retouchées en jeu gardent leurs décors, mais reçoivent les ventes du catalogue actuel
for pc_ in pieces:
    court = pc_.nom.split("/")[-1]
    if court.startswith("salle_") and court.split("_")[1] in SCELLEES:
        marque_, garniture_, ventes_ = SCELLEES[court.split("_")[1]]
        for (o, n, prix, comp), (x, z, face) in zip(ventes_, PLACES_SALLE):
            ici = pc_.get(x, 1, z) or ""
            if ici in (AIR, VOID) or "vendor" in ici:
                pc_.put(*(x, 1, z), *distributeur(o, n, face, composants=comp, **prix))
                if (pc_.get(x, 2, z) or "") in (AIR, VOID): pc_.put(x, 2, z, garniture_)

# bannières aux portails, posées APRÈS les retouches (qui remplacent toute l'enceinte) : seulement là où il y a
# vraiment un portail (passage libre dessous, linteau plein derrière, rien devant)
def bannieres_portails(e):
    ENC = e.size[0]; MIL = ENC // 2; n = 0
    plein = lambda st: st not in (VOID, AIR) and not any(k in st for k in ("pipe", "bars", "chain", "bulb", "rail"))
    for cote, face in (("n", "north"), ("s", "south"), ("o", "west"), ("e", "east")):
        def pos(t, d): return {"n": (t, d), "s": (t, ENC - 1 - d), "o": (d, t), "e": (ENC - 1 - d, t)}[cote]
        for t in (MIL - 2, MIL + 2):
            x, z = pos(t, 0); xi, zi = pos(t, 1)
            if e.get(x, 5, z) in (VOID, AIR) and plein(e.get(xi, 5, zi)) and all(e.get(x, y, z) in (VOID, AIR) for y in (1, 2, 3, 4)):
                e.put(x, 5, z, "airain:foundation_wall_banner[facing=%s]" % face, banniere_empire(random.Random("%s%s%d" % (e.nom, cote, t)), murale=True))
                n += 1
    return n
print("bannières aux portails :", {pc.nom.split("/")[-1]: bannieres_portails(pc) for pc in pieces if "enceinte" in pc.nom})

# ================================================================ VERSIONS « CITÉ » DES PIÈCES : mêmes blocs, pools plus denses
CITE_SEULEMENT = {"stand_tir", "laboratoire", "grand_marche", "avenue", "avenue_pavee"}
POOLS_CITE = {"rues": "rues_cite", "batiments": "batiments_cite", "murs": "murs_cite", "machines": "machines_cite"}
def pool_cite(pool):
    nom = pool.split("/")[-1]
    return pool[: -len(nom)] + POOLS_CITE[nom] if nom in POOLS_CITE else pool
A_CLONER = ("avenue", "avenue_pavee", "carrefour", "marche", "entrepot", "atelier", "dortoir",
             "stand_tir", "laboratoire", "grand_marche", "kiosque", "chateau_eau", "salle_cuivre", "salle_laiton", "salle_ciel")
CLONES_CITE = {n + "_c" for n in A_CLONER}
for nom in A_CLONER:
    src = next(pc for pc in pieces if pc.nom == NS + nom)
    dst = Piece(NS + nom + "_c", *src.size); dst.B = dict(src.B)
    dst.jig = [(x, y, z, f, n, c, pool_cite(pl), fi) for (x, y, z, f, n, c, pl, fi) in src.jig]
    pieces.append(dst)
pieces[:] = [pc for pc in pieces if pc.nom.split("/")[-1] not in CITE_SEULEMENT]   # seules leurs versions « _c » servent

# ================================================================ VARIANTES DE CLIMAT : mêmes plans, autres pierres et bois
# Le cuivre et le fer restent : c'est la signature de l'Empire. Seuls le socle, les sols et le bois changent.
CLIMATS = {
 "desert": {"minecraft:tuff_bricks": "minecraft:cut_sandstone", "minecraft:polished_tuff": "minecraft:smooth_sandstone",
            "minecraft:tuff": "minecraft:sandstone", "minecraft:mossy_cobblestone": "minecraft:orange_terracotta",
            "minecraft:cobbled_deepslate": "minecraft:sandstone", "minecraft:moss_block": "minecraft:sand",
            "minecraft:moss_carpet": AIR, "minecraft:coarse_dirt": "minecraft:sand", "minecraft:gravel": "minecraft:sand",
            "minecraft:dirt_path": "minecraft:smooth_sandstone", "minecraft:mud": "minecraft:sand",
            "minecraft:bricks": "minecraft:terracotta", "minecraft:spruce_planks": "minecraft:jungle_planks",
            "minecraft:spruce_stairs": "minecraft:jungle_stairs"},
 "froid": {"minecraft:tuff_bricks": "minecraft:stone_bricks", "minecraft:polished_tuff": "minecraft:polished_andesite",
           "minecraft:tuff": "minecraft:cobblestone", "minecraft:mossy_cobblestone": "minecraft:cracked_stone_bricks",
           "minecraft:moss_block": "minecraft:snow_block", "minecraft:moss_carpet": "minecraft:snow[layers=1]",
           "minecraft:coarse_dirt": "minecraft:snow_block", "minecraft:dirt_path": "minecraft:gravel", "minecraft:mud": "minecraft:packed_ice"},
 "savane": {"minecraft:tuff_bricks": "minecraft:mud_bricks", "minecraft:polished_tuff": "minecraft:packed_mud",
            "minecraft:tuff": "minecraft:mud_bricks", "minecraft:mossy_cobblestone": "minecraft:packed_mud",
            "minecraft:moss_block": "minecraft:coarse_dirt", "minecraft:moss_carpet": AIR, "minecraft:mud": "minecraft:coarse_dirt",
            "minecraft:cobbled_deepslate": "minecraft:packed_mud",
            "minecraft:spruce_planks": "minecraft:acacia_planks", "minecraft:spruce_stairs": "minecraft:acacia_stairs"},
}
def convertir(etat, table):
    nom, _, props = etat.partition("[")
    if nom in table:
        n2 = table[nom]
        return n2 if "[" in n2 or not props else n2 + "[" + props
    return etat
# Le climat use le cuivre à sa façon : le désert le brûle (patine claire), le froid humide le verdit, la savane le dore.
def patine(etat, sens, h):
    nom = etat.split("[")[0]
    if "copper" not in nom or "airain:" in nom or any(k in nom for k in ("copper_bars", "copper_ladder", "copper_casing", "copper_valve")):
        return etat
    if sens == 2:    # désert : le soleil a brûlé toute la patine
        if "weathered_" in etat: return etat.replace("weathered_", "exposed_", 1)
        if "oxidized_" in etat: return etat.replace("oxidized_", "exposed_" if h < 0.7 else "weathered_", 1)
    if sens == 1:    # savane : cuivre doré, quelques plaques encore vertes
        if "weathered_" in etat and h < 0.75: return etat.replace("weathered_", "exposed_", 1)
        if "oxidized_" in etat: return etat.replace("oxidized_", "weathered_", 1)
    elif sens < 0:   # plus vert
        if "exposed_" in etat: return etat.replace("exposed_", "weathered_", 1)
        if "weathered_" in etat and h < 0.5: return etat.replace("weathered_", "oxidized_", 1)
    return etat
SENS = {"desert": 2, "froid": -1, "savane": 1}
PART_SAVANE = 1.0                                    # (toute la savane passe par la patine)
def hachage(nom, k):
    return random.Random(zlib.crc32(("%s:%d:%d:%d" % ((nom.split("/")[-1],) + tuple(k))).encode())).random()
NEIGE_NON = ("slab[type=bottom", "stairs", "bars", "pipe", "chain", "campfire", "trapdoor", "rail", "ladder", "carpet", "cogwheel",
             "shaft", "lantern", "jigsaw", "structure_void", "air", "ice", "leaves", "airain:", "lootr", "vendor", "sign", "lectern",
             "rod", "bell", "snow", "glass_pane", "fence", "door", "anvil", "grindstone", "depot", "torch", "button", "lever", "target")
def enneiger(pc):
    """Une couche de neige sur tout ce qui voit le ciel ; les toits de tôle en dalle deviennent doubles pour la porter."""
    sx, sy, sz = pc.size
    for x in range(sx):
        for z in range(sz):
            for y in range(sy - 2, -1, -1):
                s, n = pc.B[(x, y, z)]
                if s in (VOID, AIR) or s.startswith("minecraft:structure_void"): continue
                if "shingle_slab[type=bottom" in s:
                    s = s.replace("type=bottom", "type=double"); pc.B[(x, y, z)] = (s, n)
                if not any(k in s for k in NEIGE_NON) and pc.B[(x, y + 1, z)][0] in (VOID, AIR):
                    pc.B[(x, y + 1, z)] = ("minecraft:snow[layers=%d]" % (1 + (x * 7 + z * 3) % 2), None)
                break
tempere = [pc for pc in pieces if "/tempere/" in pc.nom and "cite" not in pc.nom and "horloge" not in pc.nom and pc.nom.split("/")[-1] not in CLONES_CITE]
for clim, table in CLIMATS.items():
    for src in tempere:
        froid = clim == "froid" and "enceinte" not in src.nom      # l'enceinte a déjà de la place au-dessus
        sx, sy, sz = src.size
        dst = Piece(src.nom.replace("/tempere/", "/%s/" % clim), sx, sy + (1 if froid else 0), sz, fond=VOID)
        for k, (st, n) in src.B.items():
            h = hachage(src.nom, k)
            st = convertir(st, table)
            if clim != "savane" or h < PART_SAVANE: st = patine(st, SENS[clim], h)
            dst.B[k] = (st, n)
        if clim == "froid" and not froid:
            enneiger(dst)
        if froid:
            for x in range(sx):
                for z in range(sz):     # la rangée ajoutée en haut reprend le fond de la pièce
                    dst.B[(x, sy, z)] = (src.B[(x, sy - 1, z)][0] if src.B[(x, sy - 1, z)][0] in (VOID, AIR) else VOID, None)
            enneiger(dst)
        dst.jig = [(x, y, z, f, nom, cib, pool.replace("/tempere/", "/%s/" % clim), convertir(fin, table))
                   for (x, y, z, f, nom, cib, pool, fin) in src.jig]
        pieces.append(dst)

# ================================================================ écriture
total = 0
for pc in pieces:
    total += pc.ecrire(os.path.join(PACK, "kubejs/data/kubejs/structure"))
here = os.path.dirname(os.path.abspath(__file__))
json.dump({pc.nom: pc.apercu() for pc in pieces}, open(os.path.join(here, "avant_poste_pieces.json"), "w"))
print(len(pieces), "pièces,", total, "blocs")
