#!/usr/bin/env python3
"""Le monde en trois fronts : l'abri réfractaire du Nether (sur un îlot du lac de lave, sur la route de la fuite) et le
champ de bataille de la surface (un marcheur de guerre de l'Empire abattu face à une barricade réfractaire).
Pièces + génération + butin + textes. usage : fronts.py <pack>"""
import json, os, random, sys
from nbtlib import Compound, String
from pieces import Piece, VOID, AIR, coffre
from style import *
P = sys.argv[1]; D = os.path.join(P, "kubejs/data")
def w(rel, obj):
    f = os.path.join(D, rel); os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)
pieces = []

# ======================================================================= L'ABRI RÉFRACTAIRE DU NETHER
r = random.Random(66)
S = 13
ab = Piece("kubejs:fronts/abri_nether", S, 8, S, fond=VOID); pieces.append(ab)
for x in range(S):
    for z in range(S):
        d = max(abs(x - 6), abs(z - 6))
        if d <= 5 or (d == 6 and r.random() < 0.5):
            ab.put(x, 0, z, r.choice(("minecraft:cracked_nether_bricks", "minecraft:nether_bricks", "minecraft:netherrack", "minecraft:blackstone",
                                      "minecraft:basalt[axis=y]")) if d >= 4 else r.choice(("minecraft:polished_blackstone_bricks", "minecraft:cracked_polished_blackstone_bricks", "minecraft:soul_soil")))
            if d <= 5:
                for y in range(1, 6): ab.put(x, y, z, AIR)
# palissade de tiges distordues (le bois de l'Écho), percée d'une entrée au sud
for x in range(1, 12):
    for z in range(1, 12):
        if max(abs(x - 6), abs(z - 6)) == 5 and not (5 <= x <= 7 and z == 11) and r.random() > 0.12:
            h = r.choice((2, 3, 3))
            for y in range(1, h + 1): ab.put(x, y, z, "minecraft:warped_stem[axis=y]")
            if h == 3 and r.random() < 0.4: ab.put(x, 4, z, "minecraft:warped_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
# la tente : laine noire et pourpre, en A, ouverte vers le feu
for i in range(4):
    for (dz, y) in ((0, 1), (0, 2), (2, 1), (2, 2), (1, 3)):
        ab.put(3 + i, y, 3 + dz, "minecraft:%s_wool" % ("purple" if (i + dz + y) % 3 else "black"))
    ab.put(3 + i, 1, 4, AIR); ab.put(3 + i, 2, 4, AIR)
ab.put(4, 1, 4, "minecraft:purple_carpet"); ab.put(5, 1, 4, "minecraft:purple_carpet")
ab.put(*(3, 1, 4), *coffre("kubejs:chests/abri_nether", "east"))
# le feu d'âmes au centre, un cercle d'améthyste (l'Écho garde ceux qui le respectent)
ab.put(6, 1, 7, "minecraft:soul_campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
for (x, z) in ((4, 7), (8, 7), (6, 9), (6, 5)):
    ab.put(x, 0, z, "minecraft:amethyst_block"); ab.put(x, 1, z, "minecraft:amethyst_cluster[facing=up,waterlogged=false]")
ab.put(9, 1, 9, "minecraft:barrel[facing=up,open=false]"); ab.put(9, 2, 9, "minecraft:soul_lantern[hanging=false,waterlogged=false]")
ab.put(9, 1, 3, "minecraft:warped_planks"); ab.put(9, 2, 3, "minecraft:warped_slab[type=bottom,waterlogged=false]")
ab.put(8, 1, 3, "minecraft:warped_stairs[facing=east,half=bottom,shape=straight,waterlogged=false]")
for (x, z) in ((2, 9), (10, 6)): ab.put(x, 1, z, "minecraft:soul_fire"); ab.put(x, 0, z, "minecraft:soul_soil")
# une plaque de cuivre arrachée à l'Empire, clouée en rempart
for y in (1, 2): ab.put(10, y, 10, "minecraft:weathered_copper"); ab.put(10, y, 9, "create:weathered_iron_block")

# ======================================================================= LE CHAMP DE BATAILLE
r = random.Random(1812)
S = 21
cb = Piece("kubejs:fronts/champ_bataille", S, 11, S, fond=VOID); pieces.append(cb)
C = 10
for x in range(S):
    for z in range(S):
        d = ((x - C) ** 2 + (z - C) ** 2) ** 0.5
        if d < 10 and r.random() < 1.05 - d / 11:
            cb.put(x, 0, z, r.choice(("minecraft:coarse_dirt", "minecraft:gravel", "minecraft:coarse_dirt", "minecraft:tuff", "minecraft:blackstone")))
# le cratère de l'Écho (là où le marcheur est tombé) : calcite, sculk, améthyste
for x in range(5, 11):
    for z in range(6, 13):
        d = ((x - 8) ** 2 + (z - 9) ** 2) ** 0.5
        if d < 3.2:
            cb.put(x, 0, z, r.choice(("minecraft:calcite", "minecraft:sculk", "minecraft:calcite", "minecraft:amethyst_block")))
            if r.random() < 0.18: cb.put(x, 1, z, "minecraft:amethyst_cluster[facing=up,waterlogged=false]")
# le marcheur de guerre de l'Empire, couché : torse de fonte, tête-projecteur, une jambe dressée, le bras-canon
for x in range(9, 15):
    for y in range(1, 4):
        for z in range(8, 12):
            bord = y in (1, 3) or z in (8, 11) or x in (9, 14)
            if bord and not (y == 3 and x in (11, 12) and z in (9, 10)):     # éventré sur le dessus
                cb.put(x, y, z, r.choice(("create:industrial_iron_block", "create:weathered_iron_block", "create:weathered_iron_block", "minecraft:weathered_copper")))
for z in (9, 10):
    for x in (10, 13): cb.put(x, 2, z, "create:large_cogwheel[axis=z]") if z == 9 else None
cb.put(12, 2, 10, "create:shaft[axis=x]"); cb.put(11, 2, 9, "minecraft:copper_block")
for (x, y, z) in ((15, 2, 9), (15, 2, 10), (16, 2, 9), (16, 2, 10), (16, 3, 9), (16, 3, 10)):
    cb.put(x, y, z, "minecraft:waxed_oxidized_copper" if y == 2 else "minecraft:waxed_oxidized_copper_bulb[lit=false,powered=false]")
cb.put(17, 2, 9, "minecraft:glass_pane[east=false,north=false,south=false,waterlogged=false,west=false]")
for y in range(1, 8):                                                  # la jambe dressée vers le ciel, tordue
    x = 10 + (1 if y > 4 else 0)
    cb.put(x, y + 3, 12, "create:industrial_iron_block" if y % 3 else "minecraft:weathered_copper")
cb.put(11, 10, 12, "create:cogwheel[axis=x]")
for x in range(3, 9):                                                  # le bras-canon, tombé devant
    cb.put(x, 1, 10, "create:industrial_iron_block" if x > 4 else "minecraft:blackstone")
cb.put(2, 1, 10, "minecraft:campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")   # le canon fume encore
cb.put(6, 2, 10, "create:shaft[axis=x]")
# la barricade réfractaire, au nord : sacs de boue, pieux, toile rouge déchirée
for x in range(3, 18):
    if r.random() < 0.8:
        cb.put(x, 1, 3, r.choice(("minecraft:packed_mud", "minecraft:mud_bricks", "minecraft:packed_mud")))
        if r.random() < 0.5: cb.put(x, 2, 3, "minecraft:mud_brick_slab[type=bottom,waterlogged=false]")
    if x % 3 == 0:
        cb.put(x, 1, 2, "minecraft:spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
        cb.put(x, 2, 2, "minecraft:spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
for (x, y) in ((7, 3), (8, 3), (8, 2)): cb.put(x, y, 2, "minecraft:red_wool")
cb.put(14, 1, 4, "minecraft:spruce_trapdoor[facing=north,half=bottom,open=false,powered=false,waterlogged=false]")
# éclats et débris projetés
for _ in range(26):
    x, z = r.randint(1, S - 2), r.randint(1, S - 2)
    if cb.get(x, 1, z) == VOID and cb.get(x, 0, z) != VOID:
        cb.put(x, 1, z, r.choice(("create:weathered_iron_block", "minecraft:weathered_cut_copper_slab[type=bottom,waterlogged=false]",
                                  "create:shaft[axis=x]", "minecraft:moss_carpet", "minecraft:moss_carpet", "create:cogwheel[axis=y]")))
for (x, z) in ((4, 15), (16, 15)): cb.put(x, 1, z, "minecraft:soul_fire"); cb.put(x, 0, z, "minecraft:soul_soil")
from style import automate_abattu
automate_abattu(cb.put, 15, 1, 15, "x", -1)                             # un fantassin de l'Empire
cb.put(*(5, 1, 4), *coffre("kubejs:chests/champ_bataille", "south"))  # la caisse de la barricade

for pc in pieces: pc.ecrire(os.path.join(D, "kubejs/structure"))

# ======================================================================= génération
el = lambda loc: {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": loc, "processors": "minecraft:empty", "projection": "rigid"}}
w("kubejs/worldgen/template_pool/fronts/abri_nether.json", {"fallback": "minecraft:empty", "elements": [el("kubejs:fronts/abri_nether")]})
w("kubejs/worldgen/template_pool/fronts/champ_bataille.json", {"fallback": "minecraft:empty", "elements": [el("kubejs:fronts/champ_bataille")]})
w("kubejs/tags/worldgen/biome/abris_nether.json", {"values": ["minecraft:nether_wastes", "minecraft:soul_sand_valley", "minecraft:warped_forest"]})
w("kubejs/tags/worldgen/biome/front.json", {"values": ["minecraft:" + b for b in ("savanna", "savanna_plateau", "windswept_hills", "windswept_gravelly_hills", "windswept_forest", "windswept_savanna")]})
w("kubejs/worldgen/structure/abri_nether.json", {"type": "minecraft:jigsaw", "biomes": "#kubejs:abris_nether", "step": "surface_structures",
  "spawn_overrides": {}, "terrain_adaptation": "beard_box", "start_pool": "kubejs:fronts/abri_nether", "size": 1,
  "start_height": {"absolute": 31}, "max_distance_from_center": 80, "use_expansion_hack": False})     # sur un îlot, au niveau du lac de lave
w("kubejs/worldgen/structure/champ_bataille.json", {"type": "minecraft:jigsaw", "biomes": "#kubejs:front", "step": "surface_structures",
  "spawn_overrides": {}, "terrain_adaptation": "beard_thin", "start_pool": "kubejs:fronts/champ_bataille", "size": 1,
  "start_height": {"absolute": -1}, "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 80, "use_expansion_hack": False})
w("kubejs/worldgen/structure_set/abris_nether.json", {"structures": [{"structure": "kubejs:abri_nether", "weight": 1}],
  "placement": {"type": "minecraft:random_spread", "spacing": 32, "separation": 12, "salt": 30111978}})
w("kubejs/worldgen/structure_set/champs_bataille.json", {"structures": [{"structure": "kubejs:champ_bataille", "weight": 1}],
  "placement": {"type": "minecraft:random_spread", "spacing": 24, "separation": 9, "salt": 18121812,
                "exclusion_zone": {"other_set": "kubejs:avant_postes", "chunk_count": 4}}})

# ======================================================================= butin et écrits
def n(item, a, b, poids=1):
    return {"type": "minecraft:item", "name": item, "weight": poids, "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}}]}
def ecrit(cle, titre, doc):
    return {"type": "minecraft:item", "name": "minecraft:written_book", "functions": [
        {"function": "minecraft:set_written_book_pages", "mode": "replace_all", "pages": [{"translate": "airain.%s.p%d" % (cle, i)} for i in (1, 2, 3)]},
        {"function": "minecraft:set_name", "name": {"translate": "airain.%s.titre" % cle, "italic": False}},
        {"function": "minecraft:set_custom_data", "tag": "{airain_doc:\"%s\"}" % doc}]}
w("kubejs/loot_table/chests/abri_nether.json", {"type": "minecraft:chest", "pools": [
  {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 5}, "entries": [n("minecraft:gold_nugget", 3, 9, 3), n("minecraft:quartz", 2, 6, 2),
    n("minecraft:bread", 1, 3, 2), n("minecraft:amethyst_shard", 2, 5, 2), n("kubejs:fragment_resonance", 1, 1, 1), n("minecraft:fire_charge", 1, 2, 1),
    n("numismatics:bevel", 1, 3, 2)]},
  {"rolls": 1, "entries": [ecrit("abri_nether", "", "abri_nether")]}]})
w("kubejs/loot_table/chests/champ_bataille.json", {"type": "minecraft:chest", "pools": [
  {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 5}, "entries": [n("kubejs:ferraille", 2, 6, 3), n("kubejs:huile_machine", 1, 2, 2),
    n("minecraft:arrow", 4, 12, 2), n("minecraft:gunpowder", 1, 4, 2), n("kubejs:rouage_brise", 1, 2, 1), n("numismatics:spur", 3, 8, 2),
    n("minecraft:iron_ingot", 1, 3, 1)]},
  {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.6}], "entries": [ecrit("champ_bataille", "", "champ_bataille")]}]})
TX = {"fr_fr": {
  "airain.abri_nether.titre": "Carnet de route",
  "airain.abri_nether.p1": "Troisième nuit dans les forges d'en bas. Huit pas ici, c'est un jour de marche là-haut : les patrouilles ne nous suivront pas si vite.\n\nAda dit que la porte est sous la salle du Conseil.",
  "airain.abri_nether.p2": "Les forgerons de l'abîme nous ont laissés passer. Ils toussent la même fumée que nous. L'un d'eux m'a montré ses mains : brûlées par les âmes qu'on leur fait enfourner.",
  "airain.abri_nether.p3": "Demain on remonte. Si la porte s'ouvre, on part là où l'Écho chante assez fort pour couvrir le bruit des machines.\n\nLaissez le feu d'âmes allumé pour ceux qui suivent.",
  "airain.champ_bataille.titre": "Lettre jamais envoyée",
  "airain.champ_bataille.p1": "Le marcheur est arrivé par l'est à l'aube. Trois étages de fonte, un canon à la place du bras. Nos pieux n'ont servi à rien.",
  "airain.champ_bataille.p2": "Mira a appelé l'Écho. Je n'avais jamais vu ça : la terre est devenue blanche, du cristal a poussé dans la fonte, et il est tombé.\n\nElle n'est pas revenue du cratère.",
  "airain.champ_bataille.p3": "On lève le camp cette nuit. On dit qu'il existe un refuge, au-delà d'une porte que l'Empire garde sous terre.\n\nSi tu lis ceci, garde la caisse. Nous n'en aurons plus besoin."},
 "en_us": {
  "airain.abri_nether.titre": "Road Notebook",
  "airain.abri_nether.p1": "Third night in the lower forges. Eight steps here is a day's walk up there: the patrols won't follow us that fast.\n\nAda says the gate is beneath the Council's hall.",
  "airain.abri_nether.p2": "The abyss smiths let us through. They cough the same smoke we do. One of them showed me his hands: burned by the souls they're made to stoke.",
  "airain.abri_nether.p3": "Tomorrow we go back up. If the gate opens, we leave for where the Echo sings loud enough to drown the noise of machines.\n\nLeave the soul fire lit for those who follow.",
  "airain.champ_bataille.titre": "Letter Never Sent",
  "airain.champ_bataille.p1": "The walker came from the east at dawn. Three storeys of cast iron, a cannon for an arm. Our stakes were useless.",
  "airain.champ_bataille.p2": "Mira called the Echo. I had never seen that: the ground turned white, crystal grew in the iron, and it fell.\n\nShe never came back from the crater.",
  "airain.champ_bataille.p3": "We break camp tonight. They say there's a refuge, beyond a gate the Empire guards underground.\n\nIf you read this, keep the crate. We won't need it anymore."}}
for code, t in TX.items():
    f = os.path.join(P, "kubejs/assets/kubejs/lang/%s.json" % code); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("fronts :", ", ".join(pc.nom.split("/")[-1] for pc in pieces))
