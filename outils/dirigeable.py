#!/usr/bin/env python3
"""Le dirigeable amarré : un navire de la flotte du ciel, resté en vol depuis trois siècles avec son équipage d'automates.
Un donjon aérien à aborder avec son propre engin. Pièce + génération + butin + écrit. usage : dirigeable.py <pack>"""
import json, math, os, random, sys
from nbtlib import Compound, List, Int, String, Double, Float, Byte
from pieces import Piece, VOID, AIR, coffre
P = sys.argv[1]; D = os.path.join(P, "kubejs/data")
def w(rel, obj):
    f = os.path.join(D, rel); os.makedirs(os.path.dirname(f), exist_ok=True); json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)

r = random.Random(3110)
SX, SY, SZ = 15, 26, 33
C = 7                    # axe du navire (x)
pc = Piece("kubejs:dirigeable/dirigeable", SX, SY, SZ, fond=VOID)
PONT = 7
COQUE = "minecraft:dark_oak_planks"; COQUE2 = "minecraft:spruce_planks"; LAITON = "create:brass_casing"
def demi_largeur(z, y):
    """Demi-largeur de la coque à la longueur z (proue en z=2, poupe en z=30) et à la hauteur y (quille en y=2)."""
    t = (z - 2) / 28
    l = 4.5 * math.sin(math.pi * min(1, max(0, t * 1.15)) ** 0.8)
    if t > 0.85: l = max(l, 3.5)
    h = (y - 2) / (PONT - 2)
    return l * (0.35 + 0.65 * min(1, max(0, h)) ** 0.6)
for z in range(2, 31):
    for y in range(2, PONT + 1):
        l = demi_largeur(z, y)
        for x in range(SX):
            d = abs(x - C)
            if d <= l:
                interieur = d < l - 1 and 3 <= y < PONT and 4 <= z <= 28
                if y == PONT: pc.put(x, y, z, COQUE2 if d < l - 0.5 else LAITON)
                elif interieur: pc.put(x, y, z, AIR)
                else: pc.put(x, y, z, COQUE if (z % 4) else "minecraft:stripped_dark_oak_log[axis=y]")
# bastingage
for z in range(3, 30):
    l = demi_largeur(z, PONT)
    for s in (-1, 1):
        x = C + s * int(l)
        if 0 <= x < SX: pc.put(x, PONT + 1, z, "minecraft:dark_oak_fence")
# la cabine du capitaine, à la poupe
for z in range(22, 29):
    for x in range(C - 3, C + 4):
        for y in range(PONT + 1, PONT + 5):
            bord = x in (C - 3, C + 3) or z in (22, 28)
            if y == PONT + 4: pc.put(x, y, z, "minecraft:spruce_slab[type=bottom,waterlogged=false]")
            elif bord: pc.put(x, y, z, "minecraft:glass_pane" if y == PONT + 2 and (x + z) % 2 == 0 else "minecraft:spruce_planks")
            else: pc.put(x, y, z, AIR)
pc.put(C, PONT + 1, 22, AIR); pc.put(C, PONT + 2, 22, AIR)
livre = Compound({"id": String("minecraft:written_book"), "count": Int(1), "components": Compound({
    "minecraft:written_book_content": Compound({"title": String("Livre de bord"), "author": String("Le capitaine"),
        "pages": List[String]([String(json.dumps({"translate": "airain.dirigeable.p%d" % i})) for i in (1, 2, 3)])}),
    "minecraft:custom_name": String(json.dumps({"translate": "airain.dirigeable.titre", "italic": False})),
    "minecraft:custom_data": Compound({"airain_doc": String("dirigeable")})})})
pc.put(C + 2, PONT + 1, 27, "minecraft:lectern[facing=north,has_book=true,powered=false]",
       Compound({"id": String("minecraft:lectern"), "Book": livre, "Page": Int(0)}))
pc.put(*(C - 2, PONT + 1, 27), *coffre("kubejs:chests/dirigeable_cabine", "south"))
pc.put(C, PONT + 3, 25, "minecraft:lantern[hanging=true,waterlogged=false]")
# la soute, sous le pont : on y descend par une trappe à la proue
pc.put(C, PONT, 8, "minecraft:spruce_trapdoor[facing=north,half=top,open=false,powered=false,waterlogged=false]")
for y in range(3, PONT): pc.put(C, y, 8, "minecraft:ladder[facing=south,waterlogged=false]")
pc.put(*(C - 1, 3, 15), *coffre("kubejs:chests/dirigeable_soute", "east"))
pc.put(*(C + 1, 3, 17), *coffre("kubejs:chests/dirigeable_soute", "west"))
for z in (12, 19, 21): pc.put(C + 1, 3, z, "minecraft:barrel[facing=up,open=false]")
pc.put(C, 4, 14, "minecraft:lantern[hanging=false,waterlogged=false]")
# l'enveloppe : un fuseau de laine blanche et rouge, au-dessus du pont
EC, EY, EL, ER = 15, 19, 14, 5.2
for z in range(SZ):
    for y in range(SY):
        for x in range(SX):
            dz = (z - EC) / EL; dy = (y - EY) / ER; dx = (x - C) / ER
            v = dz * dz + dy * dy + dx * dx
            if 0.72 < v <= 1.0:
                bande = (z // 3) % 2 == 0 and y > EY - 2
                pc.put(x, y, z, "minecraft:red_wool" if bande else "minecraft:white_wool")
            elif v <= 0.72 and pc.get(x, y, z) == VOID:
                pc.put(x, y, z, AIR)
# chaînes entre l'enveloppe et le pont
for (x, z) in ((C - 3, 9), (C + 3, 9), (C - 3, 20), (C + 3, 20)):
    for y in range(PONT + 1, EY - 3):
        if pc.get(x, y, z) in (VOID, AIR): pc.put(x, y, z, "minecraft:chain[axis=y,waterlogged=false]")
# les hélices, à la poupe : deux grands rouages sur un arbre
for s in (-1, 1):
    pc.put(C + s * 3, 4, 31, "create:large_cogwheel[axis=z]"); pc.put(C + s * 3, 4, 30, "create:shaft[axis=z]")
pc.put(C, 3, 31, "create:andesite_casing")
# un canon à la proue (fûts de fonte)
pc.put(C, PONT + 1, 4, "minecraft:polished_blackstone"); pc.put(C, PONT + 1, 3, "minecraft:polished_blackstone_wall")
pc.ecrire(os.path.join(D, "kubejs/structure"))

# l'équipage : des automates sur le pont (posés en entités dans la structure)
import nbtlib
f = os.path.join(D, "kubejs/structure/dirigeable/dirigeable.nbt"); n = nbtlib.load(f)
equipage = [("mebahelcreaturesdwarven:dwarven_spider", C - 1, 10), ("mebahelcreaturesdwarven:dwarven_spider", C + 1, 16),
            ("mebahelcreaturesdwarven:dwarven_sphere", C, 6), ("mebahelcreaturesdwarven:dwarven_spider_guardian", C, 19)]
n["entities"] = List[Compound]([Compound({"pos": List[Double]([Double(x + 0.5), Double(PONT + 1.0), Double(z + 0.5)]),
    "blockPos": List[Int]([Int(x), Int(PONT + 1), Int(z)]),
    "nbt": Compound({"id": String(e), "PersistenceRequired": Byte(1), "Rotation": List[Float]([Float(r.uniform(0, 360)), Float(0)])})})
    for e, x, z in equipage])
n.save(f, gzipped=True)

# ---- génération : dans le ciel, au-dessus de la surface, rare
w("kubejs/worldgen/template_pool/dirigeable/dirigeable.json", {"fallback": "minecraft:empty", "elements": [
  {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": "kubejs:dirigeable/dirigeable",
                            "processors": "minecraft:empty", "projection": "rigid"}}]})
w("kubejs/tags/worldgen/biome/dirigeable.json", {"values": ["#minecraft:is_overworld"]})
w("kubejs/worldgen/structure/dirigeable.json", {"type": "minecraft:jigsaw", "biomes": "#kubejs:dirigeable",
  "step": "surface_structures", "spawn_overrides": {}, "terrain_adaptation": "none", "start_pool": "kubejs:dirigeable/dirigeable",
  "size": 1, "start_height": {"absolute": 150}, "max_distance_from_center": 80, "use_expansion_hack": False})
w("kubejs/worldgen/structure_set/dirigeables.json", {"structures": [{"structure": "kubejs:dirigeable", "weight": 1}],
  "placement": {"type": "minecraft:random_spread", "spacing": 44, "separation": 16, "salt": 31101999}})
def it(item, a, b, poids=1):
    return {"type": "minecraft:item", "name": item, "weight": poids, "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}}]}
w("kubejs/loot_table/chests/dirigeable_soute.json", {"type": "minecraft:chest", "pools": [
  {"rolls": {"type": "minecraft:uniform", "min": 4, "max": 7}, "entries": [it("createbigcannons:solid_shot", 2, 6, 3), it("createbigcannons:powder_charge", 2, 6, 3),
    it("kubejs:ferraille", 3, 8, 3), it("kubejs:huile_machine", 1, 3, 2), it("create:brass_ingot", 3, 8, 2), it("numismatics:cog", 1, 2, 2),
    it("minecraft:gunpowder", 3, 8, 2), it("create:precision_mechanism", 1, 2, 1)]}]})
w("kubejs/loot_table/chests/dirigeable_cabine.json", {"type": "minecraft:chest", "pools": [
  {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 5}, "entries": [it("numismatics:crown", 1, 1, 1), it("numismatics:cog", 2, 4, 3),
    it("minecraft:spyglass", 1, 1, 2), it("minecraft:filled_map", 1, 1, 1), it("minecraft:golden_apple", 1, 2, 2), it("minecraft:totem_of_undying", 1, 1, 1),
    it("minecraft:experience_bottle", 4, 10, 2)]}]})
TX = {"fr_fr": {
  "airain.dirigeable.titre": "Livre de bord",
  "airain.dirigeable.p1": "Livre de bord du croiseur « Infatigable », flotte du ciel.\n\nOrdre du Cœur, reçu au cycle 412 : rester en vol et garder le ciel jusqu'au retour.\n\nL'équipage vivant a rejoint les capsules. Les automates tiennent le navire.",
  "airain.dirigeable.p2": "Les automates ne dorment pas. Ils graissent les hélices, recousent l'enveloppe, tournent autour des mêmes nuages.\n\nIls ne savent pas compter les années. Moi si. J'en suis à quarante.",
  "airain.dirigeable.p3": "Je ne descendrai pas. Si quelqu'un monte à bord un jour, qu'il sache que ce navire obéit encore au Cœur.\n\nEt que le Cœur, lui, n'a jamais dit qu'il nous rendrait.\n\n— Le capitaine"},
 "en_us": {
  "airain.dirigeable.titre": "Ship's Log",
  "airain.dirigeable.p1": "Log of the cruiser \"Tireless\", sky fleet.\n\nOrder from the Core, received on cycle 412: stay aloft and guard the sky until the return.\n\nThe living crew has joined the capsules. The automatons hold the ship.",
  "airain.dirigeable.p2": "The automatons do not sleep. They grease the propellers, mend the envelope, circle the same clouds.\n\nThey cannot count years. I can. I am at forty.",
  "airain.dirigeable.p3": "I will not go down. If someone comes aboard one day, let them know this ship still obeys the Core.\n\nAnd that the Core never said it would give us back.\n\n— The captain"}}
for code, t in TX.items():
    fj = os.path.join(P, "kubejs/assets/kubejs/lang/%s.json" % code); j = json.load(open(fj)); j.update(t)
    json.dump(j, open(fj, "w"), indent=2, ensure_ascii=False)
print("dirigeable :", pc.size)
