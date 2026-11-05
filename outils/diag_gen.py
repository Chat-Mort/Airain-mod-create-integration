#!/usr/bin/env python3
"""Met à jour la liste d'identifiants du diagnostic (kubejs/server_scripts/airain_diagnostic.js). usage : diag_gen.py <pack>"""
import re, glob, json, sys, os, nbtlib
P = sys.argv[1]; os.chdir(P)
items, ent, struct = set(), set(), set()
for f in glob.glob("config/ftbquests/quests/chapters/*.snbt") + glob.glob("config/ftbquests/quests/reward_tables/*.snbt"):
    s = open(f).read()
    for m in re.finditer(r'(entity|structure)\s*:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"', s):
        (ent if m.group(1) == "entity" else struct).add(m.group(2))
    for m in re.finditer(r'\bid:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"', s):
        items.add(m.group(1))
for f in glob.glob("kubejs/data/**/*.json", recursive=True):
    if "/worldgen/" in f or "/tags/" in f: continue
    def marcher(x):   # seuls les vrais objets : pas les étiquettes de butin, les potions ni les fluides
        if isinstance(x, dict):
            if x.get("type") in ("minecraft:tag", "minecraft:loot_table") or "function" in x or "amount" in x: pass
            else:
                for k in ("item", "id", "name"):
                    v = x.get(k)
                    if isinstance(v, str) and re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_/.-]+", v) and not v.startswith("kubejs:chests"): items.add(v)
            for k, v in x.items():
                if k not in ("fluid", "fluids"): marcher(v)
        elif isinstance(x, list):
            for v in x: marcher(v)
    try: marcher(json.load(open(f)))
    except Exception: pass
for f in glob.glob("kubejs/data/kubejs/structure/**/*.nbt", recursive=True):
    for b in nbtlib.load(f)["blocks"]:
        if "nbt" in b and "Selling" in b["nbt"]: items.add(str(b["nbt"]["Selling"]["id"]))
for f in glob.glob("kubejs/server_scripts/*.js"):
    if "diagnostic" in f: continue
    for m in re.finditer(r"'([a-z0-9_]+:[a-z0-9_/]+)'", open(f).read()):
        i = m.group(1)
        if i.split(":")[0] in ("cataclysm", "mowziesmobs", "mebahelcreaturesdwarven"): ent.add(i)
NON = ("sequenced_assembly", "deploying", "pressing", "mechanical_crafting", "crafting_shaped", "glyph", "shaped", "shapeless",
       "item", "chest", "empty", "set_count", "uniform", "random_chance", "set_name", "set_written_book_pages", "killed_by_player")
items = {i for i in items if i.split(":")[1] not in NON and not i.startswith("ftbquests:")}
f = "kubejs/server_scripts/airain_diagnostic.js"; s = open(f).read()
nouveau = "const AIRAIN_DIAG = {\n  items: %s,\n  entites: %s,\n  structures: %s\n}" % (
    json.dumps(sorted(items)), json.dumps(sorted(ent)), json.dumps(sorted(struct)))
s = re.sub(r"const AIRAIN_DIAG = \{.*?\n\}", lambda m: nouveau, s, count=1, flags=re.S)
open(f, "w").write(s)
print("diagnostic :", len(items), "objets,", len(ent), "créatures,", len(struct), "structures")
