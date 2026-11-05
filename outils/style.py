"""Vocabulaire steampunk commun à toutes les structures de l'Empire d'Airain.
Socle de pierre (tuf), murs en plaques de cuivre et de fer, toits en tôle de cuivre, verrières de fonte,
tuyaux, engrenages, ampoules de cuivre et vapeur. Le sapin ne sert qu'aux poutres et au mobilier."""
import random
_R = random.Random(0)
def style_graine(r):
    global _R
    _R = r
def _ch(*xs): return _R.choice(xs)

AIR = "minecraft:air"
SOL = lambda: _ch(*["minecraft:polished_tuff"] * 6, "minecraft:tuff", "minecraft:tuff_bricks", "minecraft:cobbled_deepslate", "minecraft:moss_block")
PAVE = lambda: _ch("minecraft:tuff", "minecraft:cobbled_deepslate", "minecraft:gravel", "minecraft:coarse_dirt",
                   "minecraft:dirt_path", "minecraft:dirt_path", "minecraft:polished_tuff")
MUR_SOCLE = lambda: _ch(*["minecraft:tuff_bricks"] * 6, "minecraft:polished_tuff", "minecraft:mossy_cobblestone")
PLAQUE = lambda: _ch("minecraft:weathered_copper", "minecraft:weathered_copper", "minecraft:oxidized_copper",
                     "minecraft:weathered_cut_copper", "create:weathered_iron_block", "create:weathered_iron_block")
PLANCHER = lambda: _ch(*["minecraft:spruce_planks"] * 4, "minecraft:polished_tuff", "create:weathered_copper_tiles")
CARREAU_CUIVRE = lambda: _ch("create:weathered_copper_tiles", "create:oxidized_copper_tiles", "create:exposed_copper_tiles")
TOLE_DALLE = lambda: _ch("create:weathered_copper_shingle_slab", "create:weathered_copper_shingle_slab",
                         "create:oxidized_copper_shingle_slab", "create:exposed_copper_shingle_slab") + "[type=bottom,waterlogged=false]"
GRILLE_CUIVRE = "minecraft:oxidized_copper_grate[waterlogged=false]"
FENETRE = "create:industrial_iron_window"
VAPEUR = "minecraft:campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]"     # filet de vapeur
AMPOULE_ETEINTE = "minecraft:waxed_oxidized_copper_bulb[lit=false,powered=false]"
AMPOULE = "minecraft:waxed_copper_bulb[lit=true,powered=false]"
TOILE = "minecraft:cobweb"
MOUSSE = "minecraft:moss_carpet"

def tuyau(axe):
    """Tuyau de Create droit selon l'axe x, y ou z."""
    on = {"x": ("east", "west"), "y": ("up", "down"), "z": ("north", "south")}[axe]
    props = ",".join("%s=%s" % (f, "true" if f in on else "false") for f in ("down", "east", "north", "south", "up", "west"))
    return "create:fluid_pipe[%s,waterlogged=false]" % props

def lampadaire(pc, x, z, h=3):
    """Réverbère : pied de pierre, mât de cuivre, ampoule éteinte, chapeau de tôle."""
    pc.put(x, 1, z, "minecraft:tuff_bricks")
    for y in range(2, h + 1):
        pc.put(x, y, z, "create:copper_bars")
    pc.put(x, h + 1, z, AMPOULE_ETEINTE)
    pc.put(x, h + 2, z, "create:weathered_copper_shingle_slab[type=bottom,waterlogged=false]")

# ------------------------------------------------------------------ détails de ruines (revue des structures)
def automate_abattu(put, x, y, z, axe="x", sens=1):
    """Carcasse d'automate couchée au sol : tête (ampoule éteinte), torse de fonte, bras en tiges, jambes en arbres."""
    def p(i, dz): return (x + i * sens, y, z + dz) if axe == "x" else (x + dz, y, z + i * sens)
    ax = axe
    trav = "z" if axe == "x" else "x"
    put(*p(0, 0), "minecraft:waxed_oxidized_copper_bulb[lit=false,powered=false]")
    put(*p(1, 0), "create:weathered_iron_block")
    put(*p(2, 0), "create:industrial_iron_block")
    face = {"x": ("north", "south"), "z": ("west", "east")}[axe]
    put(*p(1, -1), "minecraft:lightning_rod[facing=%s,powered=false,waterlogged=false]" % face[0])
    put(*p(1, 1), "minecraft:lightning_rod[facing=%s,powered=false,waterlogged=false]" % face[1])
    put(*p(3, 0), "create:shaft[axis=%s]" % ax)
    put(*p(4, 0), "create:cogwheel[axis=%s]" % ax)          # le genou, encore denté

PLEINS_LIERRE = ("tuff", "copper", "iron_block", "cobble", "deepslate", "brick", "stone", "mud")
def lierre(get, put, x, y, z, longueur=3):
    """Lierre qui pend d'un mur plein voisin (cherche la face d'accroche)."""
    for face, (dx, dz) in (("north", (0, -1)), ("south", (0, 1)), ("west", (-1, 0)), ("east", (1, 0))):
        mur = get(x + dx, y, z + dz) or ""
        if any(k in mur for k in PLEINS_LIERRE) and "slab" not in mur and "stairs" not in mur:
            props = ",".join("%s=%s" % (f, "true" if f == face else "false") for f in ("east", "north", "south", "up", "west"))
            for k in range(longueur):
                if get(x, y - k, z) not in ("minecraft:structure_void", "minecraft:air", None): break
                put(x, y - k, z, "minecraft:vine[%s]" % props)
            return True
    return False
