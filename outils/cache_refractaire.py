#!/usr/bin/env python3
"""Caches réfractaires : petite cave enterrée (trappe au ras du sol), trouvée grâce aux cartes des camps réfractaires.
usage : python3 cache_refractaire.py <pack>"""
import json, os, random, sys
import nbtlib
from nbtlib import Compound, List, Int, String
P = sys.argv[1]; D = os.path.join(P, "kubejs/data/kubejs")
def w(rel, obj):
    f = os.path.join(D, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)

SX, SY, SZ = 5, 5, 5          # y=0 sol, y=1-2 pièce, y=3 plafond, y=4 = couche de surface (seule la trappe)
VOID = "minecraft:structure_void"

def construire():
    random.seed(5)
    B = {}
    def put(x, y, z, s, nbt=None): B[(x, y, z)] = (s, nbt)
    for x in range(SX):
        for y in range(SY):
            for z in range(SZ): put(x, y, z, VOID)
    TERRE = ["minecraft:coarse_dirt", "minecraft:packed_mud", "minecraft:rooted_dirt", "minecraft:coarse_dirt"]
    for x in range(SX):
        for z in range(SZ):
            put(x, 0, z, "minecraft:spruce_planks" if 0 < x < 4 and 0 < z < 4 else random.choice(TERRE))
            put(x, 3, z, "minecraft:spruce_planks" if 0 < x < 4 and 0 < z < 4 else random.choice(TERRE))
            for y in (1, 2):
                coin = x in (0, 4) and z in (0, 4)
                if x in (0, 4) or z in (0, 4):
                    put(x, y, z, "minecraft:stripped_spruce_log[axis=y]" if coin else random.choice(TERRE))
                else:
                    put(x, y, z, "minecraft:air")
    # puits d'accès : trappe au ras du sol, échelle contre le mur nord
    put(2, 3, 1, "minecraft:air")
    put(2, 4, 1, "minecraft:spruce_trapdoor[facing=south,half=top,open=false,powered=false,waterlogged=false]")
    for y in (1, 2, 3):
        put(2, y, 1, "minecraft:ladder[facing=south,waterlogged=false]")
    # mobilier : le coffre, un tonneau, une bougie, des toiles
    put(1, 1, 3, "lootr:lootr_chest[facing=east,type=single,waterlogged=false]",
        Compound({"id": String("lootr:lootr_chest"), "LootTable": String("kubejs:chests/cache_refractaire")}))
    put(3, 1, 3, "minecraft:barrel[facing=up,open=false]")
    put(3, 2, 3, "minecraft:candle[candles=2,lit=false,waterlogged=false]")
    put(3, 1, 2, "minecraft:red_carpet")       # le rouge des réfractaires
    put(1, 2, 1, "minecraft:cobweb")
    put(3, 2, 1, "minecraft:red_wall_banner[facing=south]",
        Compound({"id": String("minecraft:banner")}))
    return B

def ecrire(B, nom):
    palette, pidx, blocks = [], {}, []
    for (x, y, z), (state, nbt) in sorted(B.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
        if state == VOID: continue
        if state not in pidx:
            name, props = (state[:-1].split("[") + [""])[:2] if "[" in state else (state, "")
            e = Compound({"Name": String(name)})
            if props: e["Properties"] = Compound({k: String(v) for k, v in (kv.split("=") for kv in props.split(","))})
            pidx[state] = len(palette); palette.append(e)
        b = Compound({"pos": List[Int]([Int(x), Int(y), Int(z)]), "state": Int(pidx[state])})
        if nbt is not None: b["nbt"] = nbt
        blocks.append(b)
    root = Compound({"DataVersion": Int(3955), "size": List[Int]([Int(SX), Int(SY), Int(SZ)]),
                     "palette": List[Compound](palette), "blocks": List[Compound](blocks), "entities": List[Compound]([])})
    dest = os.path.join(D, "structure/refractaires"); os.makedirs(dest, exist_ok=True)
    nbtlib.File(root, root_name="").save(os.path.join(dest, nom + ".nbt"), gzipped=True)
    return len(blocks)

print("blocs :", ecrire(construire(), "cache"))

# ---------------------------------------------------------------- génération
w("worldgen/template_pool/refractaires/cache.json", {"fallback": "minecraft:empty", "elements": [
  {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": "kubejs:refractaires/cache",
                            "processors": "minecraft:empty", "projection": "rigid"}}]})
# la couche y=4 tombe sur le bloc de surface : seule la trappe le remplace
w("worldgen/structure/cache_refractaire.json", {"type": "minecraft:jigsaw", "biomes": "#kubejs:ruines_isolees",
  "step": "underground_structures", "spawn_overrides": {}, "terrain_adaptation": "none",
  "start_pool": "kubejs:refractaires/cache", "size": 1, "start_height": {"absolute": -5},
  "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 80, "use_expansion_hack": False})
w("worldgen/structure_set/caches_refractaires.json", {"structures": [{"structure": "kubejs:cache_refractaire", "weight": 1}],
  "placement": {"type": "minecraft:random_spread", "spacing": 34, "separation": 12, "salt": 14142135,
                "exclusion_zone": {"other_set": "kubejs:avant_postes", "chunk_count": 3}}})
w("tags/worldgen/structure/caches_refractaires.json", {"values": ["kubejs:cache_refractaire"]})

# ---------------------------------------------------------------- butin de la cache
n = lambda item, a, b, wgt=1: {"type": "minecraft:item", "name": item, "weight": wgt,
  "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}}]}
w("loot_table/chests/cache_refractaire.json", {"type": "minecraft:chest", "pools": [
  {"rolls": {"type": "minecraft:uniform", "min": 4, "max": 6}, "entries": [
    n("minecraft:iron_ingot", 3, 7, 3), n("minecraft:copper_ingot", 4, 10, 3), n("create:zinc_ingot", 2, 5, 2),
    n("minecraft:diamond", 1, 2, 1), n("minecraft:golden_apple", 1, 1, 1), n("minecraft:experience_bottle", 2, 5, 2),
    n("minecraft:gunpowder", 2, 6, 2), n("minecraft:arrow", 8, 16, 2), n("minecraft:cooked_mutton", 2, 5, 2),
    n("numismatics:sprocket", 1, 3, 2), n("numismatics:cog", 1, 1, 1)]},
  {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.25}],
   "entries": [{"type": "minecraft:item", "name": "minecraft:ominous_bottle"}]},
  {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:written_book", "functions": [
    {"function": "minecraft:set_written_book_pages", "mode": "replace_all",
     "pages": [{"translate": "airain.cache.p%d" % i} for i in (1, 2, 3)]},
    {"function": "minecraft:set_name", "name": {"translate": "airain.cache.titre", "italic": False}},
    {"function": "minecraft:set_custom_data", "tag": "{airain_doc:\"cache\"}"}]}]}]})

# ---------------------------------------------------------------- textes
L = os.path.join(P, "kubejs/assets/kubejs/lang")
TX = {"fr_fr": {
  "airain.carte_refractaire": "Carte réfractaire",
  "airain.carte_refractaire.l1": "Tracée à la main, au charbon. Une croix rouge.",
  "airain.carte_refractaire.l2": "« Creusez sous la croix. Ce qui est dessous est à nous. »",
  "airain.cache.titre": "Inventaire de la cache",
  "airain.cache.p1": "Cache n°7, creusée de nuit, loin des routes de l'Empire.\n\nDe quoi tenir un hiver : outils, vivres, quelques pièces.\n\nLes patrouilles ne fouillent jamais sous la terre.",
  "airain.cache.p2": "Si tu as trouvé la croix, c'est qu'un des nôtres t'a fait confiance.\n\nPrends ce qu'il te faut. Laisse le reste pour le suivant.",
  "airain.cache.p3": "Ada dit que le Cœur finira par manquer d'âmes. Ce jour-là, il viendra chercher les dernières.\n\nCe jour-là, nous serons sous terre."},
 "en_us": {
  "airain.carte_refractaire": "Refractory Map",
  "airain.carte_refractaire.l1": "Drawn by hand, in charcoal. A red cross.",
  "airain.carte_refractaire.l2": "\"Dig under the cross. What lies beneath is ours.\"",
  "airain.cache.titre": "Cache Inventory",
  "airain.cache.p1": "Cache no. 7, dug at night, far from the Empire's roads.\n\nEnough to last a winter: tools, food, a few coins.\n\nPatrols never search under the ground.",
  "airain.cache.p2": "If you found the cross, one of ours trusted you.\n\nTake what you need. Leave the rest for the next one.",
  "airain.cache.p3": "Ada says the Core will run out of souls one day. That day, it will come for the last ones.\n\nThat day, we will be underground."}}
for code, t in TX.items():
    f = os.path.join(L, code + ".json"); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("ok")
