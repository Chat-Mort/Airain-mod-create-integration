# Écrits donnés par les quêtes (5 novembre) : journal d'Héléna, fragments d'Auguste, pages de Morgana III.
# Exécuté par gen_v2.py après passe_corrections.py.
_ECRITS = [("netherite_sacree", "helena1"), ("forge_ames", "helena2"), ("envol", "helena3"), ("station", "helena4"),
           ("cites", "helena5"), ("l_relais", "helena6"), ("sentinelle", "helena7"),
           ("salle", "ferrand1"), ("reactiver", "ferrand2"), ("berceau", "ferrand3"), ("citadelle", "morgana3")]
_PAR_ID = {q["id"]: q for c in chapters for q in c["quests"]}
for _k, _doc in _ECRITS:
    _q = _PAR_ID[QUESTS[_k]]
    _q["rewards"].append((hid(f"r:{_k}:ecrit"), *R_cmd("loot give @s loot kubejs:ecrits/" + _doc)))
