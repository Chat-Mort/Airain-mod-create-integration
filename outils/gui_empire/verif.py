import json, sys
from police import largeur
L = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/lang/"
LIM_VAL, LIM_LAB = 84, 74
for c in ("fr_fr", "en_us"):
    j = json.load(open(L + c + ".json"))
    print("==", c)
    for k, v in sorted(j.items()):
        if not k.startswith("airain.etendard."): continue
        parts = k.split(".")
        if k.startswith("airain.etendard.titre_page"): lim = 150
        elif k.startswith("airain.etendard.page"): lim = 66
        elif len(parts) == 3: lim = LIM_LAB
        elif k in ("airain.etendard.pas_de_place",): continue
        else: lim = LIM_VAL
        w = largeur(v)
        if w > lim: print(f"  TROP {w}>{lim}  {k} = {v}")
    for k in ("airain.fondation.devise", "airain.fondation.ecran", "block.airain.table_enchantement", "container.inventory"):
        if k in j: print("  ", k, largeur(j[k]), j[k])
