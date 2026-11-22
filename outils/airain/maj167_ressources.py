# 1.67 : marbre sans veines, colonnes raccordées, nouvelles ardoises, lanterne de réverbère élargie, montants de cloison.
import json, os, shutil, re
from PIL import Image
MOD = '/home/claude/airain-mod-create-integration/src/main/resources/'
AS = MOD + 'assets/airain/'; DA = MOD + 'data/'
TEX = '/home/claude/travail/materiaux2/tex/'
def w(c, d): os.makedirs(os.path.dirname(c), exist_ok=True); json.dump(d, open(c, 'w'), indent=1, ensure_ascii=False)
def B(n): return f'airain:block/{n}'
LIAM = {l.strip() for l in open('/home/claude/airain-mod-create-integration/outils/textures_liam.txt') if l.strip() and not l.startswith('#')}
def tex(nom, img):
    assert f'block/{nom}.png' not in LIAM, nom          # jamais une retouche de Liam
    img.save(AS + f'textures/block/{nom}.png')

# ---------------------------------------------------------------- textures
for t, f in (('white', 'blanc'), ('black', 'noir')):
    for v in range(6): tex(f'{t}_marble_{v}', Image.open(TEX + f'marbre_{f}_{v}.png'))
    tex(f'polished_{t}_marble', Image.open(TEX + f'marbre_{f}_poli.png'))
    for h in (1, 0):
        for b in (1, 0):
            suf = {(1, 1): '', (1, 0): '_top', (0, 1): '_bottom', (0, 0): '_middle'}[(h, b)]
            im = Image.open(TEX + f'pilier_{f}_{h}{b}.png')
            tex(f'{t}_marble_pillar{suf}', im); tex(f'{t}_marble_pillar{suf}_horizontal', im.transpose(Image.TRANSPOSE))
for a, b in (('slate_bricks', 'ardoise_briques'), ('small_slate_tiles', 'ardoise_dalles'), ('cut_slate', 'ardoise_taillee'),
             ('herringbone_slate', 'ardoise_chevrons'), ('chiseled_slate', 'ardoise_ciselee'), ('slate_pillar_end', 'ardoise_pilier_bout')):
    tex(a, Image.open(TEX + b + '.png'))
import importlib.util, sys
sp = importlib.util.spec_from_file_location('mt', '/home/claude/travail/materiaux2/textures.py'); mt = importlib.util.module_from_spec(sp)
sys.argv = ['x']; sp.loader.exec_module(mt)
for h in (1, 0):
    for b in (1, 0):
        suf = {(1, 1): '', (1, 0): '_top', (0, 1): '_bottom', (0, 0): '_middle'}[(h, b)]
        im = mt.pilier_ardoise(bool(h), bool(b)); tex(f'slate_pillar{suf}', im); tex(f'slate_pillar{suf}_horizontal', im.transpose(Image.TRANSPOSE))

# ---------------------------------------------------------------- outils de modèles (repris de materiaux_ressources.py)
def modele(nom, parent, t): w(AS + f'models/block/{nom}.json', {"parent": parent, "textures": t})
def item(nom, m=None): w(AS + f'models/item/{nom}.json', {"parent": B(m or nom)})
def butin(nom, dalle=False):
    e = {"type": "minecraft:item", "name": "airain:" + nom}
    if dalle: e["functions"] = [{"function": "minecraft:set_count", "count": 2, "conditions": [{"condition": "minecraft:block_state_property", "block": "airain:" + nom, "properties": {"type": "double"}}]}]
    w(DA + f'airain/loot_table/blocks/{nom}.json', {"type": "minecraft:block", "pools": [{"rolls": 1, "bonus_rolls": 0, "entries": [e], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
TOUS = []; ESC = []; DAL = []; MUR = []
def plein(nom, t):
    modele(nom, "minecraft:block/cube_all", {"all": B(t)}); w(AS + f'blockstates/{nom}.json', {"variants": {"": {"model": B(nom)}}}); item(nom); butin(nom); TOUS.append(nom)
def escaliers(nom, t):
    tt = {"bottom": B(t), "top": B(t), "side": B(t)}
    modele(nom, "minecraft:block/stairs", tt); modele(nom + '_inner', "minecraft:block/inner_stairs", tt); modele(nom + '_outer', "minecraft:block/outer_stairs", tt)
    v = json.loads(open(AS + 'blockstates/slate_stairs.json').read().replace('airain:block/slate_stairs', B(nom)))
    w(AS + f'blockstates/{nom}.json', v); item(nom); butin(nom); TOUS.append(nom); ESC.append(nom)
def dalle(nom, t, double):
    tt = {"bottom": B(t), "top": B(t), "side": B(t)}
    modele(nom, "minecraft:block/slab", tt); modele(nom + '_top', "minecraft:block/slab_top", tt)
    w(AS + f'blockstates/{nom}.json', {"variants": {"type=bottom": {"model": B(nom)}, "type=top": {"model": B(nom + '_top')}, "type=double": {"model": B(double)}}})
    item(nom); butin(nom, True); TOUS.append(nom); DAL.append(nom)
def muret(nom, t):
    for s, p in (('_post', 'template_wall_post'), ('_side', 'template_wall_side'), ('_side_tall', 'template_wall_side_tall'), ('_inventory', 'wall_inventory')):
        modele(nom + s, "minecraft:block/" + p, {"wall": B(t)})
    v = json.loads(open(AS + 'blockstates/slate_wall.json').read().replace('airain:block/slate_wall', B(nom)))
    w(AS + f'blockstates/{nom}.json', v); item(nom, nom + '_inventory'); butin(nom); TOUS.append(nom); MUR.append(nom)

# ---------------------------------------------------------------- colonnes raccordées
def face(t, uv): return {"texture": t, "uv": uv}
D, I = [0, 0, 16, 16], [16, 0, 0, 16]        # droit, et retourné en largeur
def colonne(nom, fin):
    """Douze états (axe x bouts). Modèles explicites, sans rotation de blockstate : la bande « positive » tombe toujours
    du côté +axe. Côtés verticaux : texture en lignes (rangée 0 = haut) ; axes x/z : texture transposée (colonne 0 = bout +)."""
    var = {}
    for (fp, fn), suf in (((True, True), ''), ((True, False), '_top'), ((False, True), '_bottom'), ((False, False), '_middle')):
        s, h, e = B(f'{nom}{suf}'), B(f'{nom}{suf}_horizontal'), B(fin)
        el = lambda faces: {"from": [0, 0, 0], "to": [16, 16, 16], "faces": faces}
        mY = el({"north": face("#s", D), "south": face("#s", D), "east": face("#s", D), "west": face("#s", D), "up": face("#e", D), "down": face("#e", D)})
        mX = el({"north": face("#h", D), "south": face("#h", I), "up": face("#h", I), "down": face("#h", I), "east": face("#e", D), "west": face("#e", D)})
        mZ = el({"west": face("#h", I), "east": face("#h", D), "up": face("#s", [0, 16, 16, 0]), "down": face("#s", D), "north": face("#e", D), "south": face("#e", D)})
        for ax, m in (('y', mY), ('x', mX), ('z', mZ)):
            n = f'{nom}{suf}_{ax}'
            w(AS + f'models/block/{n}.json', {"parent": "minecraft:block/block", "textures": {"particle": s, "s": s, "h": h, "e": e}, "elements": [m]})
            var[f'axis={ax},negative_end={str(fn).lower()},positive_end={str(fp).lower()}'] = {"model": B(n)}
    w(AS + f'blockstates/{nom}.json', {"variants": var})
    item(nom, nom + '_y')
    for v in ('', '_horizontal'):                  # anciens modèles, plus utilisés
        p = AS + f'models/block/{nom}{v}.json'
        if os.path.exists(p): os.remove(p)
for t in ('white', 'black'): colonne(f'{t}_marble_pillar', f'polished_{t}_marble')
colonne('slate_pillar', 'slate_pillar_end'); butin('slate_pillar'); TOUS.append('slate_pillar')

# ---------------------------------------------------------------- nouvelles ardoises
plein('slate_bricks', 'slate_bricks'); escaliers('slate_brick_stairs', 'slate_bricks'); dalle('slate_brick_slab', 'slate_bricks', 'slate_bricks'); muret('slate_brick_wall', 'slate_bricks')
plein('small_slate_tiles', 'small_slate_tiles'); escaliers('small_slate_tile_stairs', 'small_slate_tiles'); dalle('small_slate_tile_slab', 'small_slate_tiles', 'small_slate_tiles'); muret('small_slate_tile_wall', 'small_slate_tiles')
plein('cut_slate', 'cut_slate'); escaliers('cut_slate_stairs', 'cut_slate'); dalle('cut_slate_slab', 'cut_slate', 'cut_slate'); muret('cut_slate_wall', 'cut_slate')
plein('herringbone_slate', 'herringbone_slate'); plein('chiseled_slate', 'chiseled_slate')

def ajoute(chemin, vals):
    p = DA + chemin; d = json.load(open(p)) if os.path.exists(p) else {"replace": False, "values": []}
    for v in vals:
        if v not in d["values"]: d["values"].append(v)
    w(p, d)
ajoute('minecraft/tags/block/mineable/pickaxe.json', ['airain:' + n for n in TOUS])
for k, L in (('stairs', ESC), ('slabs', DAL), ('walls', MUR)):
    ajoute(f'minecraft/tags/block/{k}.json', ['airain:' + n for n in L]); ajoute(f'minecraft/tags/item/{k}.json', ['airain:' + n for n in L])
R = DA + 'airain/recipe/materiaux/'
def taille(src, dst, n=1):
    w(R + f'{dst}_from_{src}_stonecutting.json', {"type": "minecraft:stonecutting", "ingredient": {"item": "airain:" + src}, "result": {"id": "airain:" + dst, "count": n}})
for racine, plein_ in (('slate_brick', 'slate_bricks'), ('small_slate_tile', 'small_slate_tiles'), ('cut_slate', 'cut_slate')):
    for dst, n in ((plein_, 1), (racine + '_stairs', 1), (racine + '_slab', 2), (racine + '_wall', 1)): taille('slate', dst, n)
    for dst, n in ((racine + '_stairs', 1), (racine + '_slab', 2), (racine + '_wall', 1)): taille(plein_, dst, n)
for dst in ('herringbone_slate', 'chiseled_slate', 'slate_pillar'): taille('slate', dst)

FR = {'slate_bricks': "Briques d'ardoise", 'slate_brick_stairs': "Escalier en briques d'ardoise", 'slate_brick_slab': "Dalle en briques d'ardoise", 'slate_brick_wall': "Muret en briques d'ardoise",
      'small_slate_tiles': "Petites dalles d'ardoise", 'small_slate_tile_stairs': "Escalier en petites dalles d'ardoise", 'small_slate_tile_slab': "Dalle en petites dalles d'ardoise", 'small_slate_tile_wall': "Muret en petites dalles d'ardoise",
      'cut_slate': "Ardoise taillée", 'cut_slate_stairs': "Escalier d'ardoise taillée", 'cut_slate_slab': "Dalle d'ardoise taillée", 'cut_slate_wall': "Muret d'ardoise taillée",
      'herringbone_slate': "Ardoise en chevrons", 'chiseled_slate': "Ardoise ciselée", 'slate_pillar': "Colonne d'ardoise"}
EN = {'slate_bricks': "Slate Bricks", 'slate_brick_stairs': "Slate Brick Stairs", 'slate_brick_slab': "Slate Brick Slab", 'slate_brick_wall': "Slate Brick Wall",
      'small_slate_tiles': "Small Slate Tiles", 'small_slate_tile_stairs': "Small Slate Tile Stairs", 'small_slate_tile_slab': "Small Slate Tile Slab", 'small_slate_tile_wall': "Small Slate Tile Wall",
      'cut_slate': "Cut Slate", 'cut_slate_stairs': "Cut Slate Stairs", 'cut_slate_slab': "Cut Slate Slab", 'cut_slate_wall': "Cut Slate Wall",
      'herringbone_slate': "Herringbone Slate", 'chiseled_slate': "Chiseled Slate", 'slate_pillar': "Slate Pillar"}
for f, Dd in (('fr_fr.json', FR), ('en_us.json', EN)):
    p = AS + 'lang/' + f; d = json.load(open(p))
    for k, v in Dd.items(): d['block.airain.' + k] = v
    w(p, d)
assert set(FR) == set(TOUS), set(TOUS) ^ set(FR)

# ---------------------------------------------------------------- réverbère : lanterne élargie
LUM = {"block_light": 15, "sky_light": 15}
def boite(a, b, t, lum=False):
    f = {}
    for k in ('north', 'south', 'east', 'west', 'up', 'down'):
        # uv : rectangle de la taille de la face, centré dans la texture (les boîtes peuvent sortir du bloc)
        if k in ('up', 'down'): du, dv = b[0] - a[0], b[2] - a[2]
        elif k in ('north', 'south'): du, dv = b[0] - a[0], b[1] - a[1]
        else: du, dv = b[2] - a[2], b[1] - a[1]
        u0, v0 = 8 - du / 2, 8 - dv / 2
        f[k] = {"texture": t, "uv": [round(u0, 3), round(v0, 3), round(u0 + du, 3), round(v0 + dv, 3)]}
        if lum: f[k]["neoforge_data"] = LUM
    return {"from": list(a), "to": list(b), "faces": f}
def lanterne(cx, cz, y0, lv, coins):
    """Lanterne vitrée centrée en (cx, cz), du socle (y0) au fleuron ; lv = demi-largeur du vitrage."""
    e = [boite((cx - lv - .5, y0, cz - lv - .5), (cx + lv + .5, y0 + 1, cz + lv + .5), '#m'),
         boite((cx - lv, y0 + 1, cz - lv), (cx + lv, y0 + 8, cz + lv), '#lw', True)]
    if coins: e += [boite((x, y0 + 1, z), (x + 1, y0 + 8, z + 1), '#m') for x in (cx - lv - .5, cx + lv - .5) for z in (cz - lv - .5, cz + lv - .5)]
    e += [boite((cx - lv - 1, y0 + 8, cz - lv - 1), (cx + lv + 1, y0 + 9, cz + lv + 1), '#m'),
          boite((cx - lv + .5, y0 + 9, cz - lv + .5), (cx + lv - .5, y0 + 10, cz + lv - .5), '#m'),
          boite((cx - 2, y0 + 10, cz - 2), (cx + 2, y0 + 11, cz + 2), '#m')]
    return e
for st in ('', 'exposed_', 'weathered_', 'oxidized_'):
    p = AS + f'models/block/{st}airain_lamppost_head.json'; d = json.load(open(p))
    d['elements'] = [boite((6.5, 0, 6.5), (9.5, 3, 9.5), '#fl'), boite((5, 3, 5), (11, 4, 11), '#m')] + lanterne(8, 8, 4, 3.5, True) \
        + [boite((7.5, 15, 7.5), (8.5, 17.5, 8.5), '#m')]
    w(p, d)
    # double : deux lanternes suspendues aux bouts du bras, plus larges elles aussi
    p = AS + f'models/block/{st}airain_lamppost_head_double.json'; d = json.load(open(p))
    garde = d['elements'][:3]                        # fût, bras, chapeau du fût
    els = list(garde)
    for cx in (0, 16):
        els += [boite((cx - .5, 7.5, 7.5), (cx + .5, 9, 8.5), '#m')]          # crochet sous le bras
        l = lanterne(cx, 8, -3.5, 2.5, True)
        els += [e for e in l if e['to'][1] <= 7.5]                            # sans le dernier gradin (le crochet le remplace)
    d['elements'] = els
    w(p, d)

# ---------------------------------------------------------------- cloison : montants au bord d'un portail
def montant(nom, x0, x1, pre):
    w(AS + f'models/block/{nom}.json', {"parent": "minecraft:block/block", "render_type": "minecraft:cutout", "ambientocclusion": False,
       "textures": {"bd": B(pre + 'airain_band'), "particle": B(pre + 'airain_band')}, "elements": [boite((x0, 0, 0), (x1, 16, 1.5), '#bd')]})
for st in ('', 'exposed_', 'weathered_', 'oxidized_'):
    # le vantail du portail est décalé du côté + de son axe : le montant couvre la cloison et le vantail
    montant(f'{st}airain_mesh_fence_frame', 7, 11, st); montant(f'{st}airain_mesh_fence_frame_mirror', 5, 9, st)
for f in os.listdir(AS + 'blockstates'):
    if not f.endswith('airain_mesh_fence.json'): continue
    p = AS + 'blockstates/' + f; d = json.load(open(p))
    side = next(x['apply']['model'] for x in d['multipart'] if x['apply']['model'].endswith('_mesh_fence_side'))
    cadre = side.replace('_side', '_frame')
    d['multipart'] = [x for x in d['multipart'] if '_frame' not in x['apply']['model']]
    for dirn, y, m in (('north', 0, cadre), ('east', 90, cadre), ('south', 180, cadre + '_mirror'), ('west', 270, cadre + '_mirror')):
        a = {"model": m}
        if y: a["y"] = y
        d['multipart'].append({"apply": a, "when": {"frame_" + dirn: "true"}})
    w(p, d)
# 1.67.1 : marbre brut sans rotation aléatoire (une texture tournée ne se raccorde plus à ses voisines) ; 6 variantes au hasard
for t in ('white', 'black'):
    w(AS + f'blockstates/{t}_marble.json', {"variants": {"": [{"model": B(f'{t}_marble_{v}'), "weight": 1 if v < 3 else 2} for v in range(6)]}})
print('1.67 ok', len(TOUS))
