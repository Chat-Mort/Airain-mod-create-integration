import json, os, copy
K = "/home/claude/empire-airain-pack/kubejs/data"
V = "mcmeta-data/data/minecraft/loot_table/entities"
def ecrire(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)

# ---- combustible : 8 objets cuits (une huile = 1600 ticks, comme le charbon)
ecrire(f"{K}/neoforge/data_maps/item/furnace_fuels.json", {"replace": False, "values": {"kubejs:huile_machine": {"burn_time": 1600}}})

# ---- recettes
R = f"{K}/kubejs/recipe/airain/butin"
for t in ("smelting", "blasting"):
    ecrire(f"{R}/ferraille_{t}.json", {"type": f"minecraft:{t}", "ingredient": {"item": "kubejs:ferraille"}, "result": {"id": "minecraft:iron_nugget", "count": 1},
                                         "experience": 0.1, "cookingtime": 200 if t == "smelting" else 100, "category": "misc"})
ecrire(f"{R}/ferraille_crushing.json", {"type": "create:crushing", "ingredients": [{"item": "kubejs:ferraille"}], "processing_time": 150,
    "results": [{"id": "minecraft:iron_nugget", "count": 2}, {"id": "minecraft:iron_nugget", "chance": 0.5}, {"id": "create:zinc_nugget", "chance": 0.15}]})
ecrire(f"{R}/rouage_brise_pressing.json", {"type": "create:pressing", "ingredients": [{"item": "kubejs:rouage_brise"}], "results": [{"id": "create:cogwheel"}]})

# ---- briques de tables de butin
def item(nom, mn, mx, looting=1.0, fonctions=None):
    f = [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": mn, "max": mx}, "add": False}]
    if looting: f.append({"function": "minecraft:enchanted_count_increase", "enchantment": "minecraft:looting", "count": {"type": "minecraft:uniform", "min": 0.0, "max": looting}})
    return {"type": "minecraft:item", "name": nom, "functions": f + (fonctions or [])}
def pool(*entrees, chance=None, joueur=False, rolls=1):
    c = []
    if joueur: c.append({"condition": "minecraft:killed_by_player"})
    if chance: c.append({"condition": "minecraft:random_chance_with_enchanted_bonus", "enchantment": "minecraft:looting",
                         "unenchanted_chance": chance, "enchanted_chance": {"type": "minecraft:linear", "base": chance + 0.02, "per_level_above_first": 0.02}})
    p = {"rolls": rolls, "bonus_rolls": 0.0, "entries": list(entrees)}
    if c: p["conditions"] = c
    return p
FERRAILLE = lambda mn=0.0, mx=2.0: pool(item("kubejs:ferraille", mn, mx))
PIECE = pool(item("numismatics:spur", 1.0, 2.0, 0), chance=0.05, joueur=True)
ROUAGE = lambda ch=0.05: pool(item("kubejs:rouage_brise", 1.0, 1.0, 0), chance=ch, joueur=True)
HUILE = lambda mn=0.0, mx=1.0: pool(item("kubejs:huile_machine", mn, mx))

def charge(nom):
    src = f"{K}/minecraft/loot_table/entities/{nom}.json"
    return json.load(open(src if os.path.exists(src) else f"{V}/{nom}.json"))
def sans(table, objets):
    """Retire les entrées d'objets donnés (et les groupes devenus vides)."""
    for p in table["pools"]:
        p["entries"] = [e for e in p["entries"] if e.get("name") not in objets]
    table["pools"] = [p for p in table["pools"] if p["entries"]]
    return table
def remplace_fruit(table, ancien, nouveau):
    """Les butins rares des zombies sont dans un groupe tiré au sort : on change un objet de ce groupe."""
    for p in table["pools"]:
        for e in p["entries"]:
            if e.get("name") == ancien: e["name"] = nouveau
    return table

T = {}
# Chauffeur (zombie) : chair -> ferraille + charbon ; garde fer, carotte, pomme de terre rares
T["zombie"] = sans(charge("zombie"), {"minecraft:rotten_flesh"}); T["zombie"]["pools"] += [FERRAILLE(), pool(item("minecraft:coal", 0.0, 1.0)), ROUAGE(), PIECE]
# Prospecteur (husk) : chair -> ferraille + minerai brut rare
T["husk"] = sans(charge("husk"), {"minecraft:rotten_flesh"})
T["husk"]["pools"] += [FERRAILLE(), pool(item("minecraft:raw_iron", 1.0, 1.0, 0), item("minecraft:raw_copper", 1.0, 1.0, 0), item("create:raw_zinc", 1.0, 1.0, 0), chance=0.1, joueur=True), ROUAGE(), PIECE]
# Scaphandrier (noyé) : chair -> ferraille + huile ; garde cuivre, nautile, harpon
T["drowned"] = sans(charge("drowned"), {"minecraft:rotten_flesh"}); T["drowned"]["pools"] += [FERRAILLE(), HUILE(), PIECE]
# Épave (zoglin) : chair -> ferraille + rouage brisé fréquent
T["zoglin"] = sans(charge("zoglin"), {"minecraft:rotten_flesh"}); T["zoglin"]["pools"] += [FERRAILLE(1.0, 3.0), ROUAGE(0.25), PIECE]
# Bélier-locomotive (hoglin) : porc -> ferraille + charbon ; garde le cuir
T["hoglin"] = sans(charge("hoglin"), {"minecraft:porkchop", "minecraft:cooked_porkchop"}); T["hoglin"]["pools"] += [FERRAILLE(1.0, 3.0), pool(item("minecraft:coal", 1.0, 2.0)), PIECE]
# Torpilleur (gardien) : poisson -> huile ; garde la prismarine
T["guardian"] = sans(charge("guardian"), {"minecraft:cod", "minecraft:cooked_cod"}); T["guardian"]["pools"] += [HUILE(0.0, 2.0), PIECE]
for p in T["guardian"]["pools"]:
    for e in p["entries"]:
        if e.get("type") == "minecraft:loot_table": pass
# Les autres automates gardent leur butin et gagnent de la ferraille
for nom, mx in (("skeleton", 2.0), ("stray", 2.0), ("bogged", 2.0), ("wither_skeleton", 2.0), ("creeper", 2.0), ("spider", 2.0), ("cave_spider", 1.0),
                ("enderman", 2.0), ("blaze", 2.0), ("breeze", 2.0), ("shulker", 1.0), ("elder_guardian", 4.0), ("phantom", 2.0)):
    t = charge(nom); t["pools"] += [FERRAILLE(0.0, mx), PIECE]
    if nom in ("elder_guardian",): t["pools"].append(HUILE(1.0, 3.0))
    T[nom] = t
for nom in ("silverfish", "endermite"):
    t = charge(nom); t.setdefault("pools", []); t["pools"].append(pool(item("kubejs:ferraille", 1.0, 1.0, 0), chance=0.3)); T[nom] = t
for nom, t in T.items(): ecrire(f"{K}/minecraft/loot_table/entities/{nom}.json", t)
print(len(T), "tables écrites")
