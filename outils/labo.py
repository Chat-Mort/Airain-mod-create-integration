#!/usr/bin/env python3
"""Laboratoire 7 : structure de départ de L'Empire d'Airain (Minecraft 1.21.1).
Écrit kubejs/data/kubejs/structure/laboratoire.nbt et un JSON de description pour les aperçus."""
import json, random, sys, os
import nbtlib
from nbtlib import Compound, List, Int, String, Byte

OUT = sys.argv[1]
random.seed(7)
SX, SY, SZ = 23, 6, 17          # x 0..22, y 0..5 (sol 0, plafond 5), z 0..16
B = {}                           # (x,y,z) -> (état, nbt|None)

def put(x, y, z, state, nbt=None):
    B[(x, y, z)] = (state, nbt)

def box(x1, y1, z1, x2, y2, z2, state):
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                put(x, y, z, state)

def ruine(state, choix, p):
    return random.choice(choix) if random.random() < p else state

# ---------------------------------------------------------------- coque
# style de l'Empire : murs de fonte et de cuivre (le socle de tuf est posé plus bas), plafond de roche
MUR = "create:industrial_iron_block"
MUR_ABIME = ["create:weathered_iron_block", "create:weathered_iron_block", "minecraft:weathered_copper", "minecraft:oxidized_copper"]
SOL = "minecraft:polished_tuff"
SOL_ABIME = ["minecraft:tuff", "minecraft:cobbled_deepslate", "minecraft:gravel"]
for x in range(SX):
    for z in range(SZ):
        for y in range(SY):
            if y == 0:
                put(x, y, z, ruine(SOL, SOL_ABIME, 0.12))
            elif y == SY - 1:
                put(x, y, z, ruine("minecraft:deepslate_bricks", ["minecraft:cracked_deepslate_bricks"], 0.15))
            elif x in (0, SX - 1) or z in (0, SZ - 1):
                put(x, y, z, ruine(MUR, MUR_ABIME, 0.18))
            else:
                put(x, y, z, "minecraft:air")

# murs intérieurs : x=9 et x=13 (couloir x 10..12), z=8 entre les pièces de chaque côté
for y in range(1, 5):
    for z in range(1, 16):
        put(9, y, z, ruine(MUR, MUR_ABIME, 0.15))
        put(13, y, z, ruine(MUR, MUR_ABIME, 0.15))
    for x in list(range(1, 9)) + list(range(14, 22)):
        put(x, y, 8, ruine(MUR, MUR_ABIME, 0.15))

# couloir : sol d'andésite polie, lanternes, échelle de sortie contre le mur sud
for z in range(1, 16):
    for x in range(10, 13):
        put(x, 0, z, ruine("minecraft:polished_andesite", ["minecraft:andesite", "minecraft:gravel"], 0.1))
for z in (4, 11):
    put(11, 4, z, "minecraft:lantern[hanging=true,waterlogged=false]")
for y in range(1, 5):
    put(11, y, 15, "minecraft:ladder[facing=north,waterlogged=false]")
put(11, 5, 15, "minecraft:ladder[facing=north,waterlogged=false]")   # trou de sortie dans le plafond

# portes
for y in (1, 2):
    for z in (4, 5):
        put(9, y, z, "minecraft:air")      # salle de réveil -> couloir
        put(13, y, z, "minecraft:air")     # bureau -> couloir
    for z in (12, 13):
        put(13, y, z, "minecraft:air")     # comptoir -> couloir
    put(9, y, 12, "minecraft:air")         # salle des capsules vides : porte entrouverte
    put(9, y, 13, "minecraft:iron_bars[east=false,north=true,south=true,west=false,waterlogged=false]")

# socle de tuf au pied de tous les murs, conduites sous le plafond du couloir et des salles
for (x, y, z), (st, nbt) in list(B.items()):
    if y == 1 and st in [MUR] + MUR_ABIME:
        put(x, y, z, "minecraft:tuff_bricks")
def _tuyau(axe):
    on = {"x": ("east", "west"), "z": ("north", "south")}[axe]
    return "create:fluid_pipe[%s,waterlogged=false]" % ",".join("%s=%s" % (f, "true" if f in on else "false") for f in ("down", "east", "north", "south", "up", "west"))
for z in range(1, 15):
    if z not in (4, 11):
        put(10, 4, z, _tuyau("z")); put(12, 4, z, _tuyau("z"))
for x in range(1, 9):
    if x != 5:
        put(x, 4, 4, _tuyau("x"))
for x in range(14, 21):
    put(x, 4, 7, _tuyau("x"))

# ---------------------------------------------------------------- capsules
def capsule(cx, cz, avant, allumee, cassee=False):
    """Capsule dont l'ouverture regarde vers +z (avant=1) ou -z (avant=-1)."""
    dos = cz - avant
    put(cx, 0, cz, "minecraft:waxed_oxidized_copper_grate[waterlogged=false]")
    for y in (1, 2):
        put(cx, y, dos, "minecraft:waxed_weathered_copper_grate[waterlogged=false]")
        for dx in (-1, 1):
            verre = "minecraft:air" if (cassee and random.random() < 0.5) else "minecraft:glass"
            put(cx + dx, y, cz, verre)
    put(cx, 3, cz, "minecraft:waxed_weathered_copper_bulb[lit=%s,powered=false]" % ("true" if allumee else "false"))
    for dx in (-1, 1):
        put(cx + dx, 3, cz, "minecraft:waxed_cut_copper")

# salle de réveil (x 1..8, z 1..7) : deux capsules contre le mur nord, ouvertes vers le sud
CAPSULES_REVEIL = [(3, 2), (6, 2)]
for cx, cz in CAPSULES_REVEIL:
    capsule(cx, cz, 1, True)
for p in [(1, 4, 1), (8, 4, 1), (1, 4, 7), (8, 3, 7), (2, 1, 7)]:
    put(*p, "minecraft:cobweb")
put(4, 1, 6, "minecraft:cobbled_deepslate")
put(5, 4, 5, "minecraft:chain[axis=y,waterlogged=false]")
put(5, 3, 5, "minecraft:waxed_exposed_copper_bulb[lit=true,powered=false]")

# salle des capsules vides (x 1..8, z 9..15) : deux rangées face à face, presque dans le noir
for cx in (2, 4, 6):
    capsule(cx, 10, 1, False, cassee=True)
    capsule(cx, 14, -1, False, cassee=True)
put(8, 1, 12, "minecraft:cobweb"); put(1, 4, 12, "minecraft:cobweb"); put(7, 4, 9, "minecraft:cobweb")
put(5, 4, 12, "minecraft:soul_lantern[hanging=true,waterlogged=false]")

# ---------------------------------------------------------------- bureau (x 14..21, z 1..7)
def page(*parts):
    return json.dumps(list(parts) if len(parts) > 1 else parts[0], ensure_ascii=False)
PAGES = [page({"translate": "airain.journal.p%d" % i}) for i in range(1, 6)]
PAGES.append(page("", {"translate": "airain.journal.p6"}, "\n\n",
                  {"translate": "airain.journal.fermer", "color": "dark_red", "underlined": True,
                   "clickEvent": {"action": "run_command", "value": "/trigger airain_journal"}}))
livre = Compound({
    "id": String("minecraft:written_book"), "count": Int(1),
    "components": Compound({"minecraft:written_book_content": Compound({
        "title": String("Journal"), "author": String("???"),
        "pages": List[String]([String(p) for p in PAGES])})})})
put(17, 1, 3, "minecraft:lectern[facing=west,has_book=true,powered=false]",
    Compound({"id": String("minecraft:lectern"), "Book": livre, "Page": Int(0)}))
put(19, 1, 1, "lootr:lootr_chest[facing=south,type=single,waterlogged=false]",
    Compound({"id": String("lootr:lootr_chest"), "LootTable": String("kubejs:chests/laboratoire")}))
put(15, 1, 1, "minecraft:crafting_table")
put(16, 1, 1, "minecraft:furnace[facing=south,lit=false]")
for z in range(2, 7):
    for y in (1, 2, 3):
        put(21, y, z, "minecraft:bookshelf" if random.random() > 0.25 else "minecraft:cobweb")
put(18, 4, 4, "minecraft:chain[axis=y,waterlogged=false]")
put(18, 3, 4, "minecraft:waxed_copper_bulb[lit=true,powered=false]")
for p in [(14, 4, 7), (20, 4, 1), (14, 1, 7)]:
    put(*p, "minecraft:cobweb")

# ---------------------------------------------------------------- comptoir (x 14..21, z 9..15)
def prix(spur=0, bevel=0, sprocket=0, cog=0, crown=0, sun=0):
    return Compound({k: Int(v) for k, v in
                     dict(spur=spur, bevel=bevel, sprocket=sprocket, cog=cog, crown=crown, sun=sun).items()})
VENTES = [  # (objet, quantité, prix) — début de partie + secours (Bible : « un mélange »)
    ("minecraft:oak_log", 16, prix(bevel=1)),
    ("minecraft:torch", 16, prix(bevel=1)),
    ("minecraft:raw_iron", 8, prix(sprocket=1)),
    ("minecraft:bread", 16, prix(bevel=1)),
    ("minecraft:lapis_lazuli", 16, prix(sprocket=1)),
    ("minecraft:netherrack", 16, prix(bevel=1)),
    ("minecraft:ender_pearl", 4, prix(cog=1)),
    ("minecraft:heart_of_the_sea", 1, prix(crown=1)),
]
for i, (obj, n, p) in enumerate(VENTES):
    put(14 + i, 1, 15, "numismatics:creative_vendor[facing=north]",
        Compound({"id": String("numismatics:vendor"), "Mode": Int(0), "Prices": p,
                  "Selling": Compound({"id": String(obj), "count": Int(n)})}))
    put(14 + i, 2, 15, "minecraft:waxed_cut_copper")
sign = lambda ligne: Compound({"messages": List[String]([String('""'), String(ligne), String('""'), String('""')]),
                               "color": String("black"), "has_glowing_text": Byte(1)})
put(17, 3, 14, "minecraft:spruce_wall_sign[facing=north,waterlogged=false]",
    Compound({"id": String("minecraft:sign"), "is_waxed": Byte(1),
              "front_text": sign(json.dumps({"translate": "airain.comptoir"})), "back_text": sign('""')}))
put(18, 3, 14, "minecraft:spruce_wall_sign[facing=north,waterlogged=false]",
    Compound({"id": String("minecraft:sign"), "is_waxed": Byte(1),
              "front_text": sign(json.dumps({"translate": "airain.comptoir2"})), "back_text": sign('""')}))
put(21, 1, 11, "numismatics:bank_terminal[facing=west]")
put(21, 2, 11, "minecraft:waxed_cut_copper")
put(17, 4, 11, "minecraft:chain[axis=y,waterlogged=false]")
put(17, 3, 11, "minecraft:waxed_copper_bulb[lit=true,powered=false]")
put(14, 4, 9, "minecraft:cobweb"); put(21, 4, 9, "minecraft:cobweb")

# ---------------------------------------------------------------- écriture
palette, pidx, blocks = [], {}, []
def parse(state):
    if "[" in state:
        name, props = state[:-1].split("[")
        return name, dict(kv.split("=") for kv in props.split(","))
    return state, {}
for (x, y, z), (state, nbt) in sorted(B.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
    if state not in pidx:
        name, props = parse(state)
        e = Compound({"Name": String(name)})
        if props:
            e["Properties"] = Compound({k: String(v) for k, v in props.items()})
        pidx[state] = len(palette); palette.append(e)
    b = Compound({"pos": List[Int]([Int(x), Int(y), Int(z)]), "state": Int(pidx[state])})
    if nbt is not None:
        b["nbt"] = nbt
    blocks.append(b)
root = Compound({"DataVersion": Int(3955), "size": List[Int]([Int(SX), Int(SY), Int(SZ)]),
                 "palette": List[Compound](palette), "blocks": List[Compound](blocks), "entities": List[Compound]([])})
dest = os.path.join(OUT, "kubejs/data/kubejs/structure")
os.makedirs(dest, exist_ok=True)
nbtlib.File(root, root_name="").save(os.path.join(dest, "laboratoire.nbt"), gzipped=True)

here = os.path.dirname(os.path.abspath(__file__))
json.dump({"size": [SX, SY, SZ], "capsules": CAPSULES_REVEIL, "sortie": [11, 15],
           "blocks": {f"{x},{y},{z}": s for (x, y, z), (s, n) in B.items()}},
          open(os.path.join(here, "labo_blocks.json"), "w"))
print("blocs:", len(blocks), "palette:", len(palette), "ventes:", len(VENTES))
