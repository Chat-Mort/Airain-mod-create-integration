import json, os, random
from PIL import Image
R = "/home/claude/airain-mod-create-integration/src/main/resources/"
A = R + "assets/airain/"; D = R + "data/"
C = "create-src/src/main/resources/assets/create/models/block/millstone/"
inner = json.load(open(C + "inner.json"))
banc = json.load(open(A + "models/block/banc_entretien/block.json"))
def boite(f, t, tex, uv=None, faces="nsewud", rot=None):
    noms = {"n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down"}
    e = {"from": f, "to": t, "faces": {noms[c]: {"uv": uv or [0, 0, 16, 16], "texture": tex} for c in faces}}
    if rot: e["rotation"] = rot
    return e
os.makedirs(A + "models/block/desenchanteur", exist_ok=True)
# ---- désenchanteur : socle et jauge du banc, sans les montants de la meule, plus un petit pupitre
corps = [e for e in banc["elements"] if not (e["from"][1] == 16 and e["to"][1] == 21.5)]
pupitre = [boite([6, 16, 9], [10, 17, 13], "#laiton", [0, 0, 4, 1]), boite([7, 17, 10], [9, 18, 12], "#laiton", [0, 0, 2, 1])]
tex = dict(banc["textures"]); tex["particle"] = "airain:block/banc_cuivre"
desench = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout", "textures": tex, "elements": corps + pupitre}
cristal_el = [boite([7, 18, 10], [9, 23, 12], "#cristal", [7, 4, 9, 9]),
              boite([7, 18, 10], [9, 23, 12], "#cristal", [7, 4, 9, 9], rot={"angle": 45, "axis": "y", "origin": [8, 20, 11]}),
              boite([7.5, 23, 10.5], [8.5, 24, 11.5], "#cristal", [7, 3, 8, 4])]
cristal = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout",
           "textures": {"particle": "minecraft:block/amethyst_block", "cristal": "minecraft:block/amethyst_block"}, "elements": cristal_el}
json.dump(desench, open(A + "models/block/desenchanteur/block.json", "w"), indent=1)
json.dump(cristal, open(A + "models/block/desenchanteur/cristal.json", "w"), indent=1)
objet = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout",
         "textures": dict(tex, **{k: v for k, v in inner["textures"].items() if k != "particle"}, cristal="minecraft:block/amethyst_block"),
         "elements": corps + pupitre + inner["elements"] + cristal_el,
         "display": json.load(open(A + "models/item/banc_entretien.json"))["display"]}
json.dump(objet, open(A + "models/item/desenchanteur.json", "w"), indent=1)
json.dump({"variants": {f"facing={f}": {"model": "airain:block/desenchanteur/block", **({"y": y} if y else {})}
                        for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}}, open(A + "blockstates/desenchanteur.json", "w"), indent=1)
# ---- table de l'Empire
table = {"parent": "minecraft:block/block", "render_type": "minecraft:cutout",
         "textures": {"particle": "airain:block/table_cote", "cote": "airain:block/table_cote", "dessus": "airain:block/table_dessus",
                      "dessous": "airain:block/banc_cuivre", "page": "airain:block/table_page", "laiton": "airain:block/banc_laiton"},
         "elements": [
             {"from": [0, 0, 0], "to": [16, 12, 16], "faces": {
                 "north": {"uv": [0, 4, 16, 16], "texture": "#cote"}, "south": {"uv": [0, 4, 16, 16], "texture": "#cote"},
                 "east": {"uv": [0, 4, 16, 16], "texture": "#cote"}, "west": {"uv": [0, 4, 16, 16], "texture": "#cote"},
                 "up": {"uv": [0, 0, 16, 16], "texture": "#dessus"}, "down": {"uv": [0, 0, 16, 16], "texture": "#dessous"}}},
             boite([7.5, 12, 7], [8.5, 13, 9], "#laiton", [0, 0, 1, 2]),
             boite([3, 12.5, 5], [8, 13, 11], "#page", [0, 0, 5, 6], rot={"angle": 22.5, "axis": "z", "origin": [8, 12.5, 8]}),
             boite([8, 12.5, 5], [13, 13, 11], "#page", [5, 0, 10, 6], rot={"angle": -22.5, "axis": "z", "origin": [8, 12.5, 8]}),
         ]}
json.dump(table, open(A + "models/block/table_enchantement.json", "w"), indent=1)
json.dump({"parent": "airain:block/table_enchantement"}, open(A + "models/item/table_enchantement.json", "w"))
json.dump({"variants": {"": {"model": "airain:block/table_enchantement"}}}, open(A + "blockstates/table_enchantement.json", "w"))
# ---- textures
TX = A + "textures/block/"
LA = [(110, 80, 30), (170, 128, 50), (214, 172, 80), (240, 210, 130)]
VI = [(70, 30, 110), (130, 70, 200), (200, 150, 255)]
def tex(f, nom):
    im = Image.new("RGBA", (16, 16)); px = im.load()
    for y in range(16):
        for x in range(16): px[x, y] = f(x, y) + (255,)
    im.save(TX + nom + ".png")
def cote(x, y):
    if y in (0, 15) or x in (0, 15): return LA[0]
    if y in (1, 14) or x in (1, 14): return LA[3] if (x + y) % 2 else LA[2]
    if 4 <= y <= 11 and 3 <= x <= 12:                                  # runes de l'Écho gravées
        motif = ["0110011001", "1001100110", "0110011001", "0000000000", "1011011010", "0101101101", "1011011010", "0000000000"]
        return VI[1] if motif[y - 4][x - 3] == "1" else LA[1]
    return LA[2] if (x * 7 + y * 3) % 5 else LA[1]
tex(cote, "table_cote")
def dessus(x, y):
    if x in (0, 15) or y in (0, 15): return LA[0]
    if x in (1, 14) or y in (1, 14): return LA[3]
    return (52, 22, 34) if (x + y) % 4 else (66, 30, 44)
tex(dessus, "table_dessus")
tex(lambda x, y: (236, 226, 200) if (y % 2 or x in (0, 4, 5, 9)) else (180, 168, 140), "table_page")
# ---- lang, données
for code, d in (("fr_fr", {"block.airain.table_enchantement": "Table d'enchantement de l'Empire", "block.airain.desenchanteur": "Désenchanteur",
    "airain.table.vide": "Aucun livre enchanté dans les bibliothèques sculptées autour de la table (3 blocs).",
    "airain.table.cout": "Coût : %s niveaux, %s lapis-lazuli", "airain.table.sans_objet": "Posez un objet à enchanter.",
    "airain.table.incompatible": "Impossible sur cet objet.", "airain.table.vanilla_bloquee": "Cette vieille table ne répond plus. Utilisez la table d'enchantement de l'Empire.",
    "airain.desench.lunettes.titre": "Désenchanteur :", "airain.desench.enchantements": " enchantement(s)"}),
    ("en_us", {"block.airain.table_enchantement": "Empire Enchanting Table", "block.airain.desenchanteur": "Disenchanter",
    "airain.table.vide": "No enchanted book in the chiseled bookshelves around the table (3 blocks).",
    "airain.table.cout": "Cost: %s levels, %s lapis lazuli", "airain.table.sans_objet": "Place an item to enchant.",
    "airain.table.incompatible": "Not possible on this item.", "airain.table.vanilla_bloquee": "This old table no longer answers. Use the Empire Enchanting Table.",
    "airain.desench.lunettes.titre": "Disenchanter:", "airain.desench.enchantements": " enchantment(s)"})):
    p = A + f"lang/{code}.json"; j = json.load(open(p)); j.update(d); json.dump(j, open(p, "w"), ensure_ascii=False, indent=2)
def recette(nom, motif, cle):
    json.dump({"type": "minecraft:crafting_shaped", "category": "misc", "pattern": motif, "key": {k: {"item": v} for k, v in cle.items()},
               "result": {"id": f"airain:{nom}", "count": 1}}, open(D + f"airain/recipe/{nom}.json", "w"), indent=1)
recette("table_enchantement", [" P ", "CEC", "SSS"], {"P": "create:precision_mechanism", "C": "create:brass_casing", "E": "minecraft:enchanting_table", "S": "create:brass_sheet"})
recette("desenchanteur", ["PAP", "CGC", "SKS"], {"P": "create:brass_sheet", "A": "minecraft:amethyst_shard", "C": "create:brass_casing", "G": "minecraft:grindstone", "S": "create:iron_sheet", "K": "create:cogwheel"})
for nom in ("table_enchantement", "desenchanteur"):
    json.dump({"type": "minecraft:block", "pools": [{"rolls": 1, "bonus_rolls": 0, "entries": [{"type": "minecraft:item", "name": f"airain:{nom}"}],
               "conditions": [{"condition": "minecraft:survives_explosion"}]}]}, open(D + f"airain/loot_table/blocks/{nom}.json", "w"), indent=1)
json.dump({"values": ["airain:banc_entretien", "airain:table_enchantement", "airain:desenchanteur"]}, open(D + "minecraft/tags/block/mineable/pickaxe.json", "w"))
print("ok")
