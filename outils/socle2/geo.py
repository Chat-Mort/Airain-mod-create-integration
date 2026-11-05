"""Géométrie du piédestal v2 (pixels, devant = nord). Partagée entre l'aperçu Python et le code Java (généré)."""
import json
BASE = json.load(open("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/item/socle_trophee.json"))
# m = matériau, c = colonne, o = garniture, v = velours
ELEMENTS = [(e["from"], e["to"], list(e["faces"].values())[0]["texture"][1]) for e in BASE["elements"]]
MATERIAUX = [("airain:block/socle_marbre", "airain:block/socle_colonne"),
             ("minecraft:block/polished_tuff", "minecraft:block/tuff_bricks"),
             ("minecraft:block/polished_blackstone", "minecraft:block/polished_blackstone_bricks"),
             ("minecraft:block/weathered_cut_copper", "minecraft:block/weathered_copper"),
             ("minecraft:block/dark_oak_planks", "minecraft:block/stripped_dark_oak_log")]
def haut(elements, grand):
    """Colonne haute : la colonne et ses piliers s'allongent de 16 px, tout ce qui est au-dessus monte d'autant."""
    if not grand: return elements
    out = []
    for f, t, k in elements:
        f, t = list(f), list(t)
        if f[1] >= 4.6 and t[1] <= 10: t[1] += 16
        elif f[1] >= 9.4: f[1] += 16; t[1] += 16
        out.append((f, t, k))
    return out
def java():
    lignes = []
    for f, t, k in ELEMENTS:
        lignes.append("\t\t{%s, %s, %s, %s, %s, %s, '%s'}" % (*(repr(float(v)) + "f" for v in f + t), k))
    return ",\n".join(lignes).replace("'m'", "0").replace("'c'", "1").replace("'o'", "2").replace("'v'", "3")
if __name__ == "__main__":
    print(java())
