#!/usr/bin/env python3
"""Génération des ruines isolées : structure, pool, usure, ensemble, biomes, butin, textes."""
import json, os, sys
P = sys.argv[1]; D = os.path.join(P, "kubejs/data/kubejs")
def w(rel, obj):
    f = os.path.join(D, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)
TERRE = ["plains", "sunflower_plains", "snowy_plains", "ice_spikes", "desert", "swamp", "forest", "flower_forest",
 "birch_forest", "old_growth_birch_forest", "dark_forest", "taiga", "snowy_taiga", "old_growth_pine_taiga",
 "old_growth_spruce_taiga", "savanna", "savanna_plateau", "windswept_hills", "windswept_gravelly_hills",
 "windswept_forest", "windswept_savanna", "jungle", "sparse_jungle", "bamboo_jungle", "badlands",
 "eroded_badlands", "wooded_badlands", "meadow", "cherry_grove", "grove", "snowy_slopes"]
w("tags/worldgen/biome/ruines_isolees.json", {"values": ["minecraft:" + b for b in TERRE]})
w("tags/block/ruine_friable.json", {"values": ["minecraft:tuff_bricks", "minecraft:mossy_cobblestone",
  "minecraft:polished_tuff", "minecraft:tuff", "minecraft:moss_carpet", "minecraft:cobweb", "minecraft:weathered_copper",
  "minecraft:oxidized_copper", "minecraft:weathered_cut_copper", "create:weathered_iron_block", "create:fluid_pipe"]})
# usure : chaque ruine est un peu différente (blocs manquants, mousse, fissures)
w("worldgen/processor_list/ruine_usure.json", {"processors": [
  {"processor_type": "minecraft:block_rot", "integrity": 0.88, "rottable_blocks": "#kubejs:ruine_friable"},
  {"processor_type": "minecraft:rule", "rules": [
    {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": "minecraft:tuff_bricks", "probability": 0.15},
     "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:mossy_cobblestone"}},
    {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": "minecraft:weathered_copper", "probability": 0.3},
     "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:oxidized_copper"}},
    {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": "minecraft:polished_tuff", "probability": 0.12},
     "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:moss_block"}}]}]})
w("worldgen/template_pool/ruines/atelier.json", {"fallback": "minecraft:empty", "elements": [
  {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": "kubejs:ruines/atelier_effondre",
                            "processors": "kubejs:ruine_usure", "projection": "rigid"}},
  {"weight": 1, "element": {"element_type": "minecraft:single_pool_element", "location": "kubejs:ruines/atelier_effondre_vide",
                            "processors": "kubejs:ruine_usure", "projection": "rigid"}}]})
w("worldgen/structure/ruine_atelier.json", {"type": "minecraft:jigsaw", "biomes": "#kubejs:ruines_isolees",
  "step": "surface_structures", "spawn_overrides": {}, "terrain_adaptation": "beard_thin",
  "start_pool": "kubejs:ruines/atelier", "size": 1, "start_height": {"absolute": -5},
  "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 80, "use_expansion_hack": False})
# un seul ensemble pour toutes les ruines isolées : les suivantes s'y ajouteront
# l'ensemble ruines_isolees (les 3 sortes de ruines) est écrit par structures_plus.py
# butin : de quoi démarrer, jamais de quoi sauter un palier
page = lambda n: {"type": "minecraft:item", "name": "minecraft:written_book", "functions": [
  {"function": "minecraft:set_written_book_pages", "mode": "replace_all",
   "pages": [{"translate": "airain.ruine.page%d" % n}]},
  {"function": "minecraft:set_name", "name": {"translate": "airain.ruine.titre", "italic": False}}]}
n = lambda item, a, b, wgt=1: {"type": "minecraft:item", "name": item, "weight": wgt,
  "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}}]}
w("loot_table/chests/ruine_atelier.json", {"type": "minecraft:chest", "pools": [
  {"rolls": {"type": "minecraft:uniform", "min": 3, "max": 5}, "entries": [
    n("minecraft:iron_nugget", 4, 9, 3), n("minecraft:copper_ingot", 2, 5, 3), n("create:andesite_alloy", 1, 4, 3),
    n("create:zinc_nugget", 3, 7, 2), n("minecraft:coal", 2, 6, 2), n("minecraft:bread", 1, 3, 2),
    n("minecraft:string", 2, 4, 1), n("numismatics:spur", 3, 8, 2), n("numismatics:bevel", 1, 2, 1)]},
  {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.45}],
   "entries": [page(1), page(2), page(3)]}]})
# textes
L = os.path.join(P, "kubejs/assets/kubejs/lang")
TX = {"fr_fr": {
  "airain.ruine.titre": "Page arrachée",
  "airain.ruine.page1": "Atelier 12, relève de nuit.\n\nLe contremaître dit que le Transfert ne fait pas mal. Alors pourquoi ceux du premier convoi ne répondent plus à nos lettres ?\n\nJe garde la chaudière chaude, au cas où.",
  "airain.ruine.page2": "Ordre du Conseil, à afficher dans chaque atelier :\n\nAprès le départ, toutes les machines resteront sous pression.\n\nOn ne nous a pas dit pour qui.",
  "airain.ruine.page3": "Si quelqu'un trouve ceci : je refuse.\n\nJe ne monterai pas dans la capsule. Qu'ils gardent mes rations.\n\nOn est quelques-uns, au nord, à dire non.\n\n— un ouvrier de l'atelier 12"},
 "en_us": {
  "airain.ruine.titre": "Torn Page",
  "airain.ruine.page1": "Workshop 12, night shift.\n\nThe foreman says the Transfer doesn't hurt. Then why has nobody from the first convoy answered our letters?\n\nI'm keeping the boiler warm, just in case.",
  "airain.ruine.page2": "Order of the Council, to be posted in every workshop:\n\nAfter departure, all machines shall remain under pressure.\n\nNobody told us for whom.",
  "airain.ruine.page3": "If anyone finds this: I refuse.\n\nI won't get into the capsule. They can keep my rations.\n\nA few of us, up north, are saying no.\n\n— a worker from Workshop 12"}}
for code, t in TX.items():
    f = os.path.join(L, code + ".json"); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("ok")
