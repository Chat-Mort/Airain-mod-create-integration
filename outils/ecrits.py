# Intègre les écrits de ecrits_textes.py dans le pack : lang kubejs, tables de butin, coffres, pupitre de la station.
import json, os, sys, gzip
P = sys.argv[1]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecrits_textes.py"), encoding="utf-8").read())
LT = f"{P}/kubejs/data/kubejs/loot_table"
def entree(doc, cle=None):
    cle = cle or doc
    t = DOCS[cle]
    return {"type": "minecraft:item", "name": "minecraft:written_book", "functions": [
        {"function": "minecraft:set_written_book_pages", "mode": "replace_all", "pages": [{"translate": f"airain.{cle}.p{i+1}"} for i in range(len(t[3]))]},
        {"function": "minecraft:set_name", "name": {"translate": f"airain.{cle}.titre", "italic": False}},
        {"function": "minecraft:set_custom_data", "tag": "{airain_doc:\"%s\"}" % doc}]}
# 1. lang
for lg, i in (("fr_fr", 3), ("en_us", 4)):
    f = f"{P}/kubejs/assets/kubejs/lang/{lg}.json"; j = json.load(open(f))
    for k, t in DOCS.items():
        j[f"airain.{k}.titre"] = t[0 if lg == "fr_fr" else 1]
        for n, p in enumerate(t[i]): j[f"airain.{k}.p{n+1}"] = p
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
# 2. tables données par les quêtes (loot give)
os.makedirs(f"{LT}/ecrits", exist_ok=True)
for k in DOCS:
    json.dump({"type": "minecraft:chest", "pools": [{"rolls": 1, "entries": [entree(k)]}]}, open(f"{LT}/ecrits/{k}.json", "w"), indent=1, ensure_ascii=False)
# 3. coffres : un pool de plus (retiré puis remis, pour rester idempotent)
COFFRES = {"station_capsules": ["elias1"], "vanilla_conseil": ["elias2"], "avant_poste_dortoir": ["elias3"], "station_collecteur": ["elias4"], "grand_relais": ["ada_fin"]}
for f, docs in COFFRES.items():
    path = f"{LT}/chests/{f}.json"; d = json.load(open(path))
    d["pools"] = [p for p in d["pools"] if not any(any('airain_doc:\\"%s\\"' % k in json.dumps(e) for k in DOCS) for e in p["entries"])]
    for doc in docs:
        d["pools"].append({"rolls": 1, "entries": [entree(doc)], **({"conditions": [{"condition": "minecraft:random_chance", "chance": 0.5}]} if len(docs) > 1 else {})})
    json.dump(d, open(path, "w"), indent=1, ensure_ascii=False)
print("ok")
# 4. pupitre de la station de capsules : le rapport de Vael retrouve ses propres pages (elles affichaient les relevés d'Octave)
import nbtlib, glob
for f in glob.glob(f"{P}/kubejs/data/**/station_capsules.nbt", recursive=True):
    n = nbtlib.load(f); ch = 0
    for b in n["blocks"]:
        bk = b.get("nbt", {}).get("Book")
        if bk is None: continue
        c = bk["components"]
        if c.get("minecraft:custom_data", {}).get("airain_doc") != "vael": continue
        c["minecraft:written_book_content"]["pages"] = nbtlib.List[nbtlib.String]([nbtlib.String(json.dumps({"translate": "airain.vael.p%d" % i})) for i in range(1, 7)])
        ch += 1
    n.save(); print(f, ch)
