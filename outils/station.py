#!/usr/bin/env python3
"""La station d'observation n°2 : une île volante où Octave Lanfrey observait le ciel avant le Transfert.
Pièce + génération + butin + écrit. usage : station.py <pack>"""
import json, math, os, random, sys
from nbtlib import Compound, List, Int, String
from pieces import Piece, VOID, AIR, coffre
P = sys.argv[1]; D = os.path.join(P, "kubejs/data")
def w(rel, obj):
    f = os.path.join(D, rel); os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)

r = random.Random(1412)
S, H = 25, 34
C = 12
pc = Piece("kubejs:station/station_observation", S, H, S, fond=VOID)
TOP = 14      # niveau de l'herbe
# ---- l'île : un cône renversé de pierre, terre en haut, racines dessous
for y in range(TOP + 1):
    rr = 10.5 * (y / TOP) ** 0.7 + 0.8
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - C, z - C) + r.uniform(-0.6, 0.6)
            if d > rr: continue
            if y == TOP: s = "minecraft:grass_block[snowy=false]"
            elif y >= TOP - 2: s = "minecraft:dirt"
            else: s = r.choice(("minecraft:stone", "minecraft:stone", "minecraft:andesite", "minecraft:tuff", "minecraft:cobblestone"))
            if y < TOP - 2 and r.random() < 0.03: s = "minecraft:copper_ore"
            pc.put(x, y, z, s)
for _ in range(14):     # racines pendantes
    x, z = C + r.randint(-6, 6), C + r.randint(-6, 6)
    for y in range(TOP - 2, 0, -1):
        if pc.get(x, y, z) not in (VOID, AIR) and pc.get(x, y - 1, z) == VOID:
            for k in range(1, r.randint(2, 5)): pc.put(x, y - k, z, "minecraft:hanging_roots[waterlogged=false]" if k > 1 else "minecraft:rooted_dirt")
            break
# ---- la plate-forme et la coupole
Y = TOP + 1
for x in range(S):
    for z in range(S):
        d = math.hypot(x - C, z - C)
        if d <= 6.5: pc.put(x, Y - 1, z, "create:brass_casing" if 5.6 < d else "minecraft:polished_andesite")
        for y in range(Y, Y + 9):
            if d <= 6.5: pc.put(x, y, z, AIR)
# murs et coupole de cuivre patiné, une fente vers le nord-est pour la lunette
for y in range(Y, Y + 8):
    rr = 6 if y < Y + 3 else 6 * math.cos((y - Y - 3) / 5.2 * math.pi / 2)
    for x in range(S):
        for z in range(S):
            d = math.hypot(x - C, z - C)
            if rr - 1 < d <= rr + 0.2:
                a = math.atan2(z - C, x - C)
                fente = y >= Y + 3 and -1.3 < a < -0.6
                porte = y <= Y + 1 and abs(x - C) <= 0 and z > C
                fenetre = y == Y + 1 and abs(math.sin(a * 3)) < 0.18
                if fente or porte: pc.put(x, y, z, AIR)
                elif fenetre: pc.put(x, y, z, "minecraft:glass_pane")
                else: pc.put(x, y, z, "minecraft:weathered_copper" if r.random() < 0.7 else "minecraft:oxidized_copper")
pc.put(C, Y + 8, C, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
# la grande lunette : un tube de laiton incliné vers la fente
for k in range(9):
    t = k / 8
    x, y, z = C + round(t * 4), Y + 1 + round(t * 5), C - round(t * 4)
    pc.put(x, y, z, "create:brass_block" if k not in (0, 8) else "create:brass_casing")
pc.put(C, Y, C, "create:andesite_casing"); pc.put(C - 1, Y, C, "create:large_cogwheel[axis=x]")
pc.put(C + 5, Y + 6, C - 5, "minecraft:tinted_glass")
# le planétaire (rouages) et le bureau d'Octave
pc.put(C - 4, Y, C - 2, "minecraft:spruce_planks"); pc.put(C - 4, Y + 1, C - 2, "create:cogwheel[axis=y]")
pc.put(C - 4, Y + 2, C - 2, "minecraft:chain[axis=y,waterlogged=false]"); pc.put(C - 4, Y + 3, C - 2, "create:large_cogwheel[axis=y]")
livre = Compound({"id": String("minecraft:written_book"), "count": Int(1), "components": Compound({
    "minecraft:written_book_content": Compound({"title": String("Station n°2"), "author": String("Octave Lanfrey"),
        "pages": List[String]([String(json.dumps({"translate": "airain.station.p%d" % i})) for i in (1, 2, 3, 4)])}),
    "minecraft:custom_name": String(json.dumps({"translate": "airain.station.titre", "italic": False})),
    "minecraft:custom_data": Compound({"airain_doc": String("station")})})})
pc.put(C + 3, Y, C + 2, "minecraft:lectern[facing=west,has_book=true,powered=false]",
       Compound({"id": String("minecraft:lectern"), "Book": livre, "Page": Int(0)}))
pc.put(C + 3, Y, C + 3, "minecraft:spruce_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]")
for z in (C - 4, C - 3):
    pc.put(C + 4, Y, z, "minecraft:bookshelf"); pc.put(C + 4, Y + 1, z, "minecraft:bookshelf")
pc.put(*(C - 3, Y, C + 3), *coffre("kubejs:chests/station_observation", "east"))
pc.put(C - 2, Y + 3, C + 2, "minecraft:lantern[hanging=true,waterlogged=false]"); pc.put(C - 2, Y + 4, C + 2, "minecraft:chain[axis=y,waterlogged=false]")
pc.put(C + 2, Y + 3, C - 2, "minecraft:lantern[hanging=true,waterlogged=false]"); pc.put(C + 2, Y + 4, C - 2, "minecraft:chain[axis=y,waterlogged=false]")
# le ponton d'amarrage au sud, et l'enveloppe déchirée d'un ballon accrochée à un mât
for z in range(C + 7, C + 12):
    for x in (C - 1, C, C + 1): pc.put(x, Y - 1, z, "minecraft:spruce_planks")
    if z % 2 == 0: pc.put(C - 1, Y, z, "minecraft:spruce_fence"); pc.put(C + 1, Y, z, "minecraft:spruce_fence")
for y in range(Y, Y + 6): pc.put(C, y, C + 11, "minecraft:spruce_log[axis=y]")
for (dx, dy) in ((1, 5), (2, 5), (1, 4), (2, 4), (3, 4), (2, 3), (3, 3), (3, 2)):
    pc.put(C + dx, Y + dy, C + 11, "minecraft:white_wool" if r.random() < 0.7 else "minecraft:light_gray_wool")
pc.put(C - 1, Y + 5, C + 11, "minecraft:chain[axis=x,waterlogged=false]")
# un peu de nature sur l'île
for _ in range(18):
    x, z = C + r.randint(-9, 9), C + r.randint(-9, 9)
    if pc.get(x, TOP, z) == "minecraft:grass_block[snowy=false]" and pc.get(x, TOP + 1, z) == VOID:
        pc.put(x, TOP + 1, z, r.choice(("minecraft:short_grass", "minecraft:short_grass", "minecraft:fern", "minecraft:dandelion", "minecraft:moss_carpet")))
pc.ecrire(os.path.join(D, "kubejs/structure"))

# ---- génération : haut dans le ciel, rare, au-dessus des plaines et des collines
w("kubejs/worldgen/template_pool/station/station_observation.json", {"fallback": "minecraft:empty", "elements": [
  {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": "kubejs:station/station_observation",
                            "processors": "minecraft:empty", "projection": "rigid"}}]})
w("kubejs/tags/worldgen/biome/station_observation.json", {"values": ["minecraft:" + b for b in (
  "plains", "sunflower_plains", "meadow", "forest", "birch_forest", "savanna", "windswept_hills", "taiga", "cherry_grove")]})
w("kubejs/worldgen/structure/station_observation.json", {"type": "minecraft:jigsaw", "biomes": "#kubejs:station_observation",
  "step": "surface_structures", "spawn_overrides": {}, "terrain_adaptation": "none", "start_pool": "kubejs:station/station_observation",
  "size": 1, "start_height": {"absolute": 170}, "max_distance_from_center": 80, "use_expansion_hack": False})
w("kubejs/worldgen/structure_set/stations_observation.json", {"structures": [{"structure": "kubejs:station_observation", "weight": 1}],
  "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 14, "salt": 14121412}})
def n(item, a, b, poids=1):
    return {"type": "minecraft:item", "name": item, "weight": poids, "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}}]}
w("kubejs/loot_table/chests/station_observation.json", {"type": "minecraft:chest", "pools": [
  {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 5}, "entries": [n("minecraft:spyglass", 1, 1, 2), n("numismatics:cog", 1, 2, 2),
    n("create:brass_ingot", 4, 10, 3), n("minecraft:paper", 3, 8, 2), n("minecraft:firework_rocket", 3, 8, 2), n("minecraft:phantom_membrane", 1, 3, 1),
    n("minecraft:clock", 1, 1, 1)]},
  {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.25}], "entries": [n("minecraft:elytra", 1, 1, 1)]}]})
TX = {"fr_fr": {
  "airain.station.titre": "Relevés de la station n°2",
  "airain.station.p1": "Station d'observation n°2.\nRelevés d'Octave Lanfrey, ingénieur en chef.\n\nNuit 1. Ciel clair. Je monte ici quand le bruit des forges m'empêche de penser.",
  "airain.station.p2": "Nuit 40. Une lumière violette au nord, au-dessus du fort scellé. Elle a duré une heure.\n\nLe lendemain, la moitié du quartier des ingénieurs était vide. Ada Vael n'était plus là.",
  "airain.station.p3": "Nuit 52. Le Conseil annonce que les Réfractaires sont morts dans les marais.\n\nJ'ai vu leur lumière partir vers le haut, pas vers le sud. Je n'ai rien dit.",
  "airain.station.p4": "Dernière nuit. Les ordres sont arrivés.\n\nJe redescends préparer deux capsules qui ne mènent nulle part. Si l'Empire a raison, je me serai trompé pour rien. S'il a tort, il faudra quelqu'un pour choisir.\n\n— O. L."},
 "en_us": {
  "airain.station.titre": "Readings of Station No. 2",
  "airain.station.p1": "Observation station no. 2.\nReadings of Octave Lanfrey, Engineer-in-Chief.\n\nNight 1. Clear sky. I come up here when the noise of the forges keeps me from thinking.",
  "airain.station.p2": "Night 40. A violet light to the north, above the sealed fortress. It lasted an hour.\n\nThe next day, half of the engineers' quarter was empty. Ada Vael was gone.",
  "airain.station.p3": "Night 52. The Council announces that the Refractories died in the marshes.\n\nI saw their light go up, not south. I said nothing.",
  "airain.station.p4": "Last night. The orders have arrived.\n\nI am going down to prepare two capsules that lead nowhere. If the Empire is right, I will have been wrong for nothing. If it is wrong, someone will have to choose.\n\n— O. L."}}
for code, t in TX.items():
    f = os.path.join(P, "kubejs/assets/kubejs/lang/%s.json" % code); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("station d'observation :", pc.size)
