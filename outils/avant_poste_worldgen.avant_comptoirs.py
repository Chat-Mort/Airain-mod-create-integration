#!/usr/bin/env python3
"""Génération des avant-postes (4 climats) et des cités mécaniques, suppression des villages, butin et textes.
usage : avant_poste_worldgen.py <dossier du pack>"""
import json, os, sys
P = sys.argv[1]; D = os.path.join(P, "kubejs/data")
HERE = os.path.dirname(os.path.abspath(__file__))
VAN = os.path.join(HERE, "mcmeta-data/data/minecraft/worldgen/structure")
NS = "kubejs:avant_poste/tempere/"

def w(rel, obj):
    f = os.path.join(D, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)

CLIM = "tempere"            # climat en cours d'écriture (les pools sont dupliqués pour chaque climat)
def el(nom, poids, proj="rigid", proc="kubejs:avant_poste_usure"):
    return {"weight": poids, "element": {"element_type": "minecraft:single_pool_element",
                                         "location": "kubejs:avant_poste/%s/%s" % (CLIM, nom), "processors": proc, "projection": proj}}
VIDE = lambda poids: {"weight": poids, "element": {"element_type": "minecraft:empty_pool_element"}}
def pool(nom, elements, repli="minecraft:empty"):
    if repli.startswith("@"): repli = "kubejs:avant_poste/%s/%s" % (CLIM, repli[1:])
    w("kubejs/worldgen/template_pool/avant_poste/%s/%s.json" % (CLIM, nom), {"fallback": repli, "elements": elements})

# ---------------------------------------------------------------- usure
w("kubejs/tags/block/avant_poste_friable.json", {"values": ["minecraft:tuff_bricks", "minecraft:polished_tuff",
  "minecraft:cut_sandstone", "minecraft:smooth_sandstone", "minecraft:stone_bricks", "minecraft:polished_andesite",
  "minecraft:mud_bricks", "minecraft:packed_mud", "minecraft:jungle_planks", "minecraft:acacia_planks",
  "minecraft:spruce_planks", "minecraft:cobweb", "minecraft:moss_carpet", "minecraft:weathered_copper", "minecraft:oxidized_copper",
  "minecraft:weathered_cut_copper", "create:weathered_iron_block", "create:copper_bars", "create:industrial_iron_window",
  "create:weathered_copper_shingle_slab", "create:oxidized_copper_shingle_slab", "create:exposed_copper_shingle_slab"]})
w("kubejs/worldgen/processor_list/avant_poste_usure.json", {"processors": [
  {"processor_type": "minecraft:block_rot", "integrity": 0.94, "rottable_blocks": "#kubejs:avant_poste_friable"},
  {"processor_type": "minecraft:rule", "rules": [
    {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": "minecraft:tuff_bricks", "probability": 0.12},
     "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:mossy_cobblestone"}},
    {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": "minecraft:polished_tuff", "probability": 0.1},
     "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:tuff"}}]}]})
# les rues : jamais de trou au-dessus de l'eau
w("kubejs/worldgen/processor_list/avant_poste_rue.json", {"processors": [
  {"processor_type": "minecraft:rule", "rules": [
    {"input_predicate": {"predicate_type": "minecraft:always_true"},
     "location_predicate": {"predicate_type": "minecraft:block_match", "block": "minecraft:water"},
     "output_state": {"Name": "minecraft:spruce_planks"}}]}]})

# ---------------------------------------------------------------- pools
# l'enceinte (pièce de départ) épouse le terrain ; la place et tout le reste poussent à l'intérieur
w("kubejs/worldgen/processor_list/avant_poste_enceinte.json", {"processors": [
  {"processor_type": "minecraft:block_rot", "integrity": 0.9, "rottable_blocks": "#kubejs:avant_poste_friable"},
  {"processor_type": "minecraft:rule", "rules": [
    {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": "minecraft:tuff_bricks", "probability": 0.15},
     "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:mossy_cobblestone"}},
    {"input_predicate": {"predicate_type": "minecraft:always_true"},
     "location_predicate": {"predicate_type": "minecraft:block_match", "block": "minecraft:water"},
     "output_state": {"Name": "minecraft:tuff_bricks"}}]}]})
RUE = "kubejs:avant_poste_rue"
# l'enceinte a une boîte de 64 de haut : on la descend de 28 sous le sol, pour qu'elle couvre de -28 à +35 autour du sol
# (ses blocs, eux, suivent le terrain quoi qu'il arrive). Les bâtiments posés plus bas ou plus haut que le centre y tiennent.
PROF = 28
BIOMES = {"tempere": ["plains", "sunflower_plains", "meadow"], "desert": ["desert"],
          "froid": ["snowy_plains", "snowy_taiga", "taiga"], "savane": ["savanna", "savanna_plateau"]}
for CLIM in BIOMES:
    pool("enceintes", [el("enceinte_" + v, 1, "terrain_matching", "kubejs:avant_poste_enceinte") for v in "abc"])
    pool("centres", [el("centre_fontaine", 1)])
    pool("rues", [el("rue_rails", 4, "terrain_matching", RUE), el("rue_pavee", 3, "terrain_matching", RUE),
                  el("rue_courte", 2, "terrain_matching", RUE), el("carrefour", 2, "terrain_matching", RUE),
                  el("barricade", 1, "terrain_matching", RUE)], "@fins")
    pool("fins", [el("barricade", 1, "terrain_matching", RUE), VIDE(1)])
    pool("marches", [el("marche", 1)])
    pool("batiments", [el("marche", 1), el("entrepot", 2), el("atelier", 2), el("dortoir", 3), el("kiosque", 1), VIDE(1)], "@petits")
    pool("petits", [el("kiosque", 1), el("chateau_eau", 1)])   # repli : bouche les trous où un grand bâtiment ne rentre pas
    pool("machines", [el("machine_" + c, 1, proc="minecraft:empty") for c in
                      ("batisseur", "matieres", "agriculture", "mecanique", "create", "expedition")] + [VIDE(2)])
    pool("salles_scellees", [el("salle_" + p, 1, proc="minecraft:empty") for p in ("cuivre", "laiton", "ciel")])
    pool("murs", [el("tour", 1), VIDE(3)])       # la muraille est l'enceinte ; il reste quelques pylônes de guet
    # abords : ce qui s'adosse à la muraille, porte vers la cour (jamais vide : c'est là que la cour se remplit)
    pool("abords", [el("entrepot", 2), el("atelier", 2), el("dortoir", 2), el("tour", 1), el("chateau_eau", 1),
                    el("depot_caisses", 2), el("ferraille", 1), el("abri", 2)], "@abords_petits")
    pool("abords_petits", [el("depot_caisses", 2), el("ferraille", 1), el("abri", 1), el("chateau_eau", 1), el("kiosque", 1)])
    w("kubejs/tags/worldgen/biome/avant_postes_%s.json" % CLIM, {"values": ["minecraft:" + b for b in BIOMES[CLIM]]})
    w("kubejs/worldgen/structure/avant_poste_%s.json" % CLIM, {"type": "minecraft:jigsaw",
      "biomes": "#kubejs:avant_postes_%s" % CLIM, "step": "surface_structures", "spawn_overrides": {},
      "terrain_adaptation": "beard_thin", "start_pool": "kubejs:avant_poste/%s/enceintes" % CLIM, "size": 6,
      "start_height": {"absolute": -PROF}, "project_start_to_heightmap": "WORLD_SURFACE_WG",
      "max_distance_from_center": 80, "use_expansion_hack": False})
w("kubejs/worldgen/structure_set/avant_postes.json", {"structures": [{"structure": "kubejs:avant_poste_" + c, "weight": 1} for c in BIOMES],
  "placement": {"type": "minecraft:random_spread", "spacing": 44, "separation": 14, "salt": 20251023}})
# tous les avant-postes de l'Empire (cités comprises) : utilisé par la quête « Signes de vie »
w("kubejs/tags/worldgen/structure/avant_postes.json", {"values": ["kubejs:avant_poste_" + c for c in BIOMES] + ["kubejs:cite_mecanique"]})

# ---------------------------------------------------------------- les cités mécaniques (tempérées, rares, très grandes)
CLIM = "tempere"
pool("enceintes_cite", [el("enceinte_cite_" + v, 1, "terrain_matching", "kubejs:avant_poste_enceinte") for v in "ab"])
# la cité est remplie au maximum : aucun tirage « vide », et de petites pièces en repli partout
pool("rues_cite", [el("avenue_c", 4, "terrain_matching", RUE), el("avenue_pavee_c", 3, "terrain_matching", RUE),
                   el("carrefour_c", 3, "terrain_matching", RUE)])
pool("batiments_cite", [el("marche_c", 2), el("grand_marche_c", 2), el("stand_tir_c", 2), el("laboratoire_c", 2),
                        el("entrepot_c", 2), el("atelier_c", 2), el("dortoir_c", 2)], "@petits_cite")
pool("petits_cite", [el("kiosque_c", 1), el("chateau_eau_c", 1)])
pool("marches_cite", [el("grand_marche_c", 1), el("marche_c", 1)])
pool("murs_cite", [el("tour", 1), el("kiosque_c", 2), el("chateau_eau_c", 1)])
pool("machines_cite", [el("machine_" + c, 1, proc="minecraft:empty") for c in
                       ("batisseur", "matieres", "agriculture", "mecanique", "create", "expedition")])
pool("centres_cite", [el("centre_horloge", 1)])
pool("abords_cite", [el("entrepot_c", 2), el("atelier_c", 2), el("dortoir_c", 2), el("stand_tir_c", 2), el("laboratoire_c", 2),
                     el("tour", 1), el("chateau_eau_c", 1), el("depot_caisses", 1), el("abri", 1)], "@abords_petits")
for p_ in ("cuivre", "laiton", "ciel"):
    pool("salles_%s_c" % p_, [el("salle_%s_c" % p_, 1, proc="minecraft:empty")])
w("kubejs/worldgen/structure/cite_mecanique.json", {"type": "minecraft:jigsaw",
  "biomes": "#kubejs:avant_postes_tempere", "step": "surface_structures", "spawn_overrides": {},
  "terrain_adaptation": "beard_thin", "start_pool": "kubejs:avant_poste/tempere/enceintes_cite", "size": 10,
  "start_height": {"absolute": -PROF}, "project_start_to_heightmap": "WORLD_SURFACE_WG",
  "max_distance_from_center": 80, "use_expansion_hack": False})
w("kubejs/worldgen/structure_set/cites_mecaniques.json", {"structures": [{"structure": "kubejs:cite_mecanique", "weight": 1}],
  "placement": {"type": "minecraft:random_spread", "spacing": 80, "separation": 30, "salt": 77123401,
                "exclusion_zone": {"other_set": "kubejs:avant_postes", "chunk_count": 6}}})

# ---------------------------------------------------------------- ce qui disparaît : villages, cabane de sorcière, igloo
w("kubejs/tags/worldgen/biome/aucun.json", {"values": []})
for s in ("village_plains", "village_desert", "village_savanna", "village_snowy", "village_taiga", "swamp_hut", "igloo"):
    j = json.load(open(os.path.join(VAN, s + ".json")))
    j["biomes"] = "#kubejs:aucun"
    w("minecraft/worldgen/structure/%s.json" % s, j)
w("kubejs/neoforge/biome_modifier/sans_villageois_zombies.json",
  {"type": "neoforge:remove_spawns", "biomes": "#minecraft:is_overworld", "entity_types": "minecraft:zombie_villager"})

# ---------------------------------------------------------------- butin
def n(item, a, b, poids=1):
    return {"type": "minecraft:item", "name": item, "weight": poids,
            "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": a, "max": b}}]}
def page(k):
    return {"type": "minecraft:item", "name": "minecraft:written_book", "functions": [
        {"function": "minecraft:set_written_book_pages", "mode": "replace_all", "pages": [{"translate": k}]},
        {"function": "minecraft:set_name", "name": {"translate": "airain.ruine.titre", "italic": False}}]}
def table(nom, rolls, entrees, pages=None, chance=0.5):
    pools = [{"rolls": {"type": "minecraft:uniform", "min": rolls[0], "max": rolls[1]}, "entries": entrees}]
    if pages:
        pools.append({"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": chance}],
                      "entries": [page(k) for k in pages]})
    w("kubejs/loot_table/chests/%s.json" % nom, {"type": "minecraft:chest", "pools": pools})
table("avant_poste_entrepot", (4, 7), [
    n("minecraft:spruce_log", 4, 12, 3), n("minecraft:oak_planks", 8, 24, 2), n("minecraft:coal", 4, 12, 3),
    n("minecraft:iron_nugget", 6, 18, 3), n("minecraft:copper_ingot", 3, 9, 3), n("create:zinc_nugget", 4, 12, 2),
    n("minecraft:wheat", 4, 12, 2), n("minecraft:string", 2, 6, 1), n("minecraft:leather", 1, 4, 1),
    n("numismatics:spur", 4, 12, 2), n("numismatics:bevel", 1, 3, 1)])
table("avant_poste_atelier", (3, 6), [
    n("create:andesite_alloy", 2, 8, 3), n("create:cogwheel", 1, 4, 2), n("create:shaft", 2, 8, 2),
    n("create:iron_sheet", 1, 3, 2), n("minecraft:iron_ingot", 1, 4, 2), n("create:zinc_ingot", 1, 3, 1),
    n("minecraft:stone_pickaxe", 1, 1, 1), n("minecraft:iron_pickaxe", 1, 1, 1), n("create:wrench", 1, 1, 1),
    n("numismatics:bevel", 1, 3, 1)])
table("avant_poste_dortoir", (3, 5), [
    n("minecraft:bread", 2, 6, 3), n("minecraft:white_wool", 1, 4, 2), n("minecraft:candle", 1, 3, 1),
    n("minecraft:book", 1, 2, 1), n("minecraft:paper", 2, 6, 2), n("numismatics:spur", 3, 10, 3),
    n("numismatics:bevel", 1, 2, 1)], pages=["airain.dortoir.page1", "airain.dortoir.page2", "airain.dortoir.page3"], chance=0.6)

table("stand_tir", (3, 5), [
    n("minecraft:arrow", 8, 24, 3), n("minecraft:gunpowder", 2, 6, 3), n("minecraft:iron_nugget", 6, 16, 2),
    n("minecraft:crossbow", 1, 1, 1), n("minecraft:bow", 1, 1, 1), n("minecraft:copper_ingot", 2, 6, 2), n("numismatics:bevel", 1, 3, 2)])
table("laboratoire_essais", (3, 6), [
    n("minecraft:redstone", 4, 12, 3), n("create:iron_sheet", 2, 6, 2), n("create:copper_sheet", 2, 6, 2),
    n("create:cogwheel", 2, 6, 2), n("create:andesite_alloy", 4, 10, 2), n("minecraft:experience_bottle", 2, 6, 2),
    n("minecraft:glass", 4, 8, 1), n("numismatics:sprocket", 1, 2, 1)])

# ---------------------------------------------------------------- textes
TX = {"fr_fr": {
  "airain.avant_poste.place": "Place du Relais",
  "airain.machine.batisseur": "Bâtisseur", "airain.machine.matieres": "Matières", "airain.machine.agriculture": "Agriculture",
  "airain.machine.mecanique": "Mécanique", "airain.machine.create": "Ateliers", "airain.machine.expedition": "Expédition",
  "airain.sceau.cuivre": "Sceau de cuivre", "airain.sceau.laiton": "Sceau de laiton", "airain.sceau.ciel": "Sceau du ciel",
  "airain.sceau.requis.cuivre": "Schéma du Cuivre", "airain.sceau.requis.laiton": "Schéma du Laiton", "airain.sceau.requis.ciel": "Schéma du Ciel",
  "airain.sceau.ouvert": "Le sceau cède. La salle s'ouvre.",
  "airain.sceau.refus": "Ce sceau ne répond qu'au %s.",
  "airain.sceau.protege": "Un sceau protège encore cette salle.",
  "airain.dortoir.page1": "Dortoir 3.\n\nOn nous a dit de laisser nos affaires : « là où vous allez, vous n'en aurez pas besoin ».\n\nJ'ai quand même gardé la photo de ma sœur.",
  "airain.dortoir.page2": "Les capsules sont prêtes. Le contremaître a l'air soulagé.\n\nMoi, je n'arrive pas à dormir. Les machines font un bruit, la nuit. Comme une respiration.",
  "airain.dortoir.page3": "Dernière nuit ici.\n\nSi le Transfert marche, on se réveillera dans le Cœur, tous ensemble, pour toujours.\n\nSi ça ne marche pas… personne ne viendra lire ceci.",
  "airain.distributeur.protege": "Les machines de l'Empire sont scellées au sol.",
  "airain.cite.stand_tir": "Stand de tir",
  "airain.essais.p1": "Laboratoire d'essais n°3.\n\nEssai 41 : transfert d'un esprit d'ouvrier vers un automate de patrouille.\n\nL'automate s'est mis en marche. Il a appelé sa fille.",
  "airain.essais.p2": "Essai 42 : même protocole.\n\nL'automate a refusé tout ordre pendant trois jours. Puis il a obéi. Il n'a plus jamais parlé.\n\nLe Conseil juge l'essai réussi.",
  "airain.essais.p3": "Conclusion transmise au Conseil :\n\nun corps de métal ne suffit pas. Il faut un réceptacle plus grand, qui ne s'use pas.\n\nLe projet « Cœur » est approuvé."},
 "en_us": {
  "airain.avant_poste.place": "Relay Square",
  "airain.machine.batisseur": "Builder", "airain.machine.matieres": "Materials", "airain.machine.agriculture": "Farming",
  "airain.machine.mecanique": "Mechanics", "airain.machine.create": "Workshops", "airain.machine.expedition": "Expedition",
  "airain.sceau.cuivre": "Copper Seal", "airain.sceau.laiton": "Brass Seal", "airain.sceau.ciel": "Sky Seal",
  "airain.sceau.requis.cuivre": "Copper Schematic", "airain.sceau.requis.laiton": "Brass Schematic", "airain.sceau.requis.ciel": "Sky Schematic",
  "airain.sceau.ouvert": "The seal gives way. The room opens.",
  "airain.sceau.refus": "This seal only answers to the %s.",
  "airain.sceau.protege": "A seal still protects this room.",
  "airain.dortoir.page1": "Dormitory 3.\n\nThey told us to leave our belongings behind: \"where you're going, you won't need them\".\n\nI kept my sister's photograph anyway.",
  "airain.dortoir.page2": "The capsules are ready. The foreman looks relieved.\n\nI can't sleep. The machines make a sound at night. Like breathing.",
  "airain.dortoir.page3": "Last night here.\n\nIf the Transfer works, we'll wake up inside the Core, all together, forever.\n\nIf it doesn't… nobody will come to read this.",
  "airain.distributeur.protege": "The Empire's machines are sealed to the ground.",
  "airain.cite.stand_tir": "Shooting Range",
  "airain.essais.p1": "Test laboratory no. 3.\n\nTrial 41: transfer of a worker's mind into a patrol automaton.\n\nThe automaton started up. It called for its daughter.",
  "airain.essais.p2": "Trial 42: same protocol.\n\nThe automaton refused every order for three days. Then it obeyed. It never spoke again.\n\nThe Council deems the trial a success.",
  "airain.essais.p3": "Conclusion sent to the Council:\n\na metal body is not enough. A larger vessel is needed, one that does not wear out.\n\nProject \"Core\" is approved."}}
L = os.path.join(P, "kubejs/assets/kubejs/lang")
for code, t in TX.items():
    f = os.path.join(L, code + ".json"); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("ok")
