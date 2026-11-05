#!/usr/bin/env python3
"""Retouches des structures vanilla assemblées en pièces, selon leur faction (lore du 30 octobre) :
on ajoute une règle de remplacement aux listes de traitements que leurs pièces utilisent déjà.
- salles d'épreuve (Empire) : renforts de fonte et de cuivre dans le tuf ;
- cité antique (premier essai de Transfert) : des machines de l'Empire cachées dans l'ardoise ;
- bastions (peuple asservi) : fonte de l'Empire dans les murs, chaînes et barreaux des forges ;
- ruines de piste (avant l'Empire) : quelques piquets d'arpenteur impériaux.
usage : vanilla_retouches.py <pack>"""
import json, os, sys
P = sys.argv[1]
H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(H, "mcmeta-data/data/minecraft/worldgen/processor_list")
DST = os.path.join(P, "kubejs/data/minecraft/worldgen/processor_list")
def regle(bloc, proba, sortie):
    return {"input_predicate": {"predicate_type": "minecraft:random_block_match", "block": bloc, "probability": proba},
            "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": sortie}}
EMPIRE_TUF = [regle("minecraft:tuff_bricks", 0.08, "create:industrial_iron_block"), regle("minecraft:polished_tuff", 0.06, "create:weathered_iron_block"),
              regle("minecraft:chiseled_tuff", 0.25, "create:copper_casing"), regle("minecraft:tuff", 0.05, "create:andesite_casing")]
TRANSFERT = [regle("minecraft:deepslate_tiles", 0.05, "minecraft:waxed_oxidized_cut_copper"), regle("minecraft:polished_deepslate", 0.04, "create:industrial_iron_block"),
             regle("minecraft:deepslate_bricks", 0.03, "create:weathered_iron_block"), regle("minecraft:cracked_deepslate_tiles", 0.08, "minecraft:waxed_oxidized_copper_grate")]
ASSERVIS = [regle("minecraft:polished_blackstone_bricks", 0.06, "create:industrial_iron_block"), regle("minecraft:blackstone", 0.03, "create:weathered_iron_block"),
            regle("minecraft:polished_blackstone_brick_wall", 0.3, "minecraft:iron_bars"), regle("minecraft:cracked_polished_blackstone_bricks", 0.1, "minecraft:chain")]
ARPENTEURS = [regle("minecraft:mud_bricks", 0.02, "minecraft:weathered_copper"), regle("minecraft:packed_mud", 0.02, "create:weathered_iron_block")]
LISTES = {"trial_chambers_copper_bulb_degradation": EMPIRE_TUF,
          "ancient_city_generic_degradation": TRANSFERT, "ancient_city_walls_degradation": TRANSFERT, "ancient_city_start_degradation": TRANSFERT,
          "bastion_generic_degradation": ASSERVIS, "rampart_degradation": ASSERVIS, "high_wall": ASSERVIS, "side_wall_degradation": ASSERVIS,
          "housing": ASSERVIS, "stable_degradation": ASSERVIS, "treasure_rooms": ASSERVIS, "bridge": ASSERVIS, "high_rampart": ASSERVIS, "bottom_rampart": ASSERVIS,
          "trail_ruins_houses_archaeology": ARPENTEURS, "trail_ruins_roads_archaeology": ARPENTEURS, "trail_ruins_tower_top_archaeology": ARPENTEURS}
os.makedirs(DST, exist_ok=True)
for nom, regles in LISTES.items():
    d = json.load(open(os.path.join(SRC, nom + ".json")))
    d["processors"] = [p for p in d["processors"] if p.get("airain") is None]
    d["processors"].insert(0, {"processor_type": "minecraft:rule", "rules": regles})   # avant les traitements d'origine (usure, archéologie)
    json.dump(d, open(os.path.join(DST, nom + ".json"), "w"), indent=2)
print("structures vanilla retouchées :", len(LISTES), "listes")
