#!/usr/bin/env python3
"""Simule l'assemblage d'un avant-poste (blocs puzzle) sur terrain plat et dessine : plan, vue d'ensemble, planche des pièces.
usage : apercu_avant_poste.py <graine> <dossier de sortie>"""
import json, os, random, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "avant_poste_pieces.json")))
graine, OUT = int(sys.argv[1]), sys.argv[2]
CLIMAT = sys.argv[3] if len(sys.argv) > 3 else "tempere"
CITE = len(sys.argv) > 4 and sys.argv[4] == "cite"
NS = "kubejs:avant_poste/%s/" % CLIMAT
SOL_CLIMAT = {"desert": "minecraft:sand", "froid": "minecraft:snow_block"}.get(CLIMAT, "minecraft:grass_block")
NOMS_CLIMAT = {"tempere": "tempéré", "desert": "du désert", "froid": "du froid", "savane": "de la savane"}
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

POOLS = {  # mêmes poids que avant_poste_worldgen.py ; None = élément vide
 "centres": ([("centre_fontaine", 1)], None),
 "rues": ([("rue_rails", 4), ("rue_pavee", 3), ("rue_courte", 2), ("carrefour", 2), ("barricade", 1)], "fins"),
 "fins": ([("barricade", 1), (None, 1)], None),
 "marches": ([("marche", 1)], None),
 "batiments": ([("marche", 1), ("entrepot", 2), ("atelier", 2), ("dortoir", 3), ("kiosque", 1), (None, 1)], "petits"),
 "petits": ([("kiosque", 1), ("chateau_eau", 1)], None),
 "rues_cite": ([("avenue_c", 4), ("avenue_pavee_c", 3), ("carrefour_c", 3)], None),
 "batiments_cite": ([("marche_c", 2), ("grand_marche_c", 2), ("stand_tir_c", 2), ("laboratoire_c", 2), ("entrepot_c", 2), ("atelier_c", 2), ("dortoir_c", 2)], "petits_cite"),
 "petits_cite": ([("kiosque_c", 1), ("chateau_eau_c", 1)], None),
 "marches_cite": ([("grand_marche_c", 1), ("marche_c", 1)], None),
 "murs_cite": ([("tour", 1), ("kiosque_c", 2), ("chateau_eau_c", 1)], None),
 "machines_cite": ([("machine_" + c, 1) for c in ("batisseur", "matieres", "agriculture", "mecanique", "create", "expedition")], None),
 "machines": ([("machine_" + c, 1) for c in ("batisseur", "matieres", "agriculture", "mecanique", "create", "expedition")] + [(None, 2)], None),
 "salles_scellees": ([("salle_cuivre", 1), ("salle_laiton", 1), ("salle_ciel", 1)], None),
 "murs": ([("tour", 1), (None, 3)], None),
 "abords": ([("entrepot", 2), ("atelier", 2), ("dortoir", 2), ("tour", 1), ("chateau_eau", 1), ("depot_caisses", 2), ("ferraille", 1), ("abri", 2)], "abords_petits"),
 "abords_petits": ([("depot_caisses", 2), ("ferraille", 1), ("abri", 1), ("chateau_eau", 1), ("kiosque", 1)], None),
 "abords_cite": ([("entrepot_c", 2), ("atelier_c", 2), ("dortoir_c", 2), ("stand_tir_c", 2), ("laboratoire_c", 2), ("tour", 1), ("chateau_eau_c", 1), ("depot_caisses", 1), ("abri", 1)], "abords_petits"),
 "centres_cite": ([("centre_horloge", 1)], None),
 "salles_cuivre_c": ([("salle_cuivre_c", 1)], None), "salles_laiton_c": ([("salle_laiton_c", 1)], None), "salles_ciel_c": ([("salle_ciel_c", 1)], None),
}
VEC = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
ROT = ["north", "east", "south", "west"]
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}

def rot_face(f, r): return ROT[(ROT.index(f) + r) % 4]
def rot_xz(x, z, sx, sz, r):
    for _ in range(r):
        x, z, sx, sz = sz - 1 - z, x, sz, sx
    return x, z
def taille(nom, r):
    sx, sy, sz = P[NS + nom]["size"]
    return (sz, sy, sx) if r % 2 else (sx, sy, sz)

class Inst:
    def __init__(s, nom, r, ox, oz):
        s.nom, s.r, s.ox, s.oz = nom, r, ox, oz
        s.sx, s.sy, s.sz = taille(nom, r)
    def boite(s): return (s.ox, s.oz, s.ox + s.sx - 1, s.oz + s.sz - 1)
    def jigs(s):
        sx, _, sz = P[NS + s.nom]["size"]
        for (x, y, z, face, nom, cible, pool, final) in P[NS + s.nom]["jigsaws"]:
            X, Z = rot_xz(x, z, sx, sz, s.r)
            yield (s.ox + X, y, s.oz + Z, rot_face(face, s.r), nom, cible, pool, final)

def chevauche(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

def assembler(seed):
    rnd = random.Random(seed)
    racine = Inst(("enceinte_cite_" + "ab"[seed % 2]) if CITE else ("enceinte_" + "abc"[seed % 3]), seed % 4, 0, 0)
    places, file = [racine], [(racine, 0)]
    R0 = racine.boite()
    while file:
        inst, prof = file.pop(0)
        for (jx, jy, jz, face, nom, cible, pool, final) in list(inst.jigs()):
            if pool == "minecraft:empty" or prof >= (10 if CITE else 6):
                continue
            pname = pool.split("/")[-1]
            essais = [pname]
            if POOLS[pname][1]: essais.append(POOLS[pname][1])
            fait = False
            for pn in essais:
                elems = POOLS[pn][0][:]
                ordre = []
                while elems:                                   # tirage pondéré sans remise
                    tot = sum(w for _, w in elems); t = rnd.uniform(0, tot)
                    for i, (e, wgt) in enumerate(elems):
                        t -= wgt
                        if t <= 0: ordre.append(e); elems.pop(i); break
                for e in ordre:
                    if e is None: fait = True; break
                    rots = [0, 1, 2, 3]; rnd.shuffle(rots)
                    for r in rots:
                        test = Inst(e, r, 0, 0)
                        for (kx, ky, kz, kf, knom, *_r) in test.jigs():
                            if knom != cible or kf != OPP[face]: continue
                            vx, vz = VEC[face]
                            c = Inst(e, r, jx + vx - kx, jz + vz - kz)
                            bx = c.boite()
                            if any(chevauche(bx, p.boite()) for p in places[1:]): continue
                            if bx[0] < R0[0] or bx[1] < R0[1] or bx[2] > R0[2] or bx[3] > R0[3]: continue   # dans l'enceinte
                            places.append(c); file.append((c, prof + 1)); fait = True; break
                        if fait: break
                    if fait: break
                if fait: break
    return places

TABLE = [("structure_void", None), ("air", None), ("jigsaw", None), ("campfire", (240, 240, 240)), ("redstone_lamp", (170, 120, 70)),
 ("fluid_pipe", (200, 130, 80)), ("copper_bars", (170, 110, 75)), ("copper_ladder", (170, 110, 75)), ("industrial_iron_window", (150, 190, 205)),
 ("framed_glass", (185, 220, 230)), ("industrial_iron_block", (88, 90, 96)), ("weathered_iron_block", (120, 98, 82)),
 ("copper_shingle", (95, 140, 115)), ("copper_tiles", (110, 150, 120)), ("weathered_cut_copper_slab", (100, 145, 110)),
 ("weathered_cut_copper", (100, 145, 110)), ("weathered_copper", (105, 150, 112)), ("minecraft:bricks", (150, 85, 70)), ("large_cogwheel", (150, 115, 70)), ("moss_carpet", (95, 125, 50)), ("cobweb", (225, 225, 225)),
 ("lootr_chest", (220, 170, 40)), ("creative_vendor", (240, 205, 60)), ("_bed", (150, 60, 50)), ("barrel", (140, 100, 55)),
 ("crafting_table", (150, 100, 55)), ("anvil", (70, 70, 75)), ("smithing", (60, 60, 70)), ("rail", (150, 130, 100)),
 ("iron_door", (200, 200, 205)), ("light_blue_glazed", (90, 170, 220)), ("brass_block", (215, 170, 70)), ("brass_casing", (190, 150, 70)),
 ("waxed_copper_block", (200, 110, 70)), ("copper_bulb[lit=true", (255, 200, 110)), ("copper_bulb", (80, 140, 120)),
 ("copper_casing", (180, 120, 80)), ("waxed_cut_copper", (190, 110, 75)), ("oxidized_cut_copper", (75, 150, 125)),
 ("oxidized_copper", (85, 165, 140)), ("lightning_rod", (90, 150, 130)), ("chain", (70, 75, 85)), ("iron_bars", (160, 160, 165)),
 ("glass", (190, 225, 235)), ("wall_sign", (200, 160, 100)), ("fence", (110, 80, 50)), ("ladder", (150, 110, 60)),
 ("stripped_spruce", (125, 92, 58)), ("spruce_log", (75, 52, 32)), ("spruce_slab", (105, 75, 45)), ("spruce_stairs", (105, 75, 45)),
 ("spruce_planks", (115, 85, 52)), ("spruce_trapdoor", (105, 75, 45)), ("stripped_spruce_wood", (125, 92, 58)),
 ("andesite_casing", (165, 160, 145)), ("mechanical_press", (150, 150, 145)), ("depot", (140, 140, 135)), ("cogwheel", (160, 125, 80)),
 ("shaft", (150, 150, 145)), ("dead_bush", (140, 110, 60)), ("mud", (70, 60, 55)), ("mossy_cobblestone", (100, 115, 90)),
 ("moss_block", (90, 115, 50)), ("polished_deepslate", (70, 70, 76)), ("deepslate_tile", (55, 55, 62)), ("cracked_deepslate", (60, 60, 66)),
 ("cobbled_deepslate", (75, 75, 80)), ("cut_sandstone", (215, 200, 150)), ("smooth_sandstone", (222, 208, 160)), ("sandstone", (210, 195, 145)), ("terracotta", (165, 90, 60)), ("minecraft:sand", (220, 205, 155)), ("jungle_", (160, 115, 80)), ("stone_bricks", (125, 125, 125)), ("polished_andesite", (135, 138, 135)), ("cobblestone", (115, 115, 115)), ("snow", (240, 245, 250)), ("packed_ice", (160, 190, 235)), ("mud_brick", (140, 105, 80)), ("packed_mud", (150, 115, 85)), ("acacia", (170, 90, 50)), ("bell", (230, 190, 60)), ("archwood_leaves", (70, 110, 200)), ("lodestone", (150, 150, 160)), ("reinforced_deepslate", (40, 50, 50)), ("chiseled_bookshelf", (140, 95, 50)), ("bookshelf", (140, 95, 50)), ("copper_block", (190, 110, 75)), ("purple_wool", (120, 50, 160)), ("purple_candle", (150, 80, 200)), ("calcite", (225, 225, 220)), ("soul_soil", (75, 58, 45)), ("soul_fire", (90, 210, 230)), ("soul_campfire", (90, 210, 230)), ("soul_lantern", (90, 210, 230)), ("amethyst", (155, 100, 210)), ("sourcestone", (110, 90, 140)), ("archwood", (60, 80, 150)), ("smooth_basalt", (70, 70, 75)), ("large_amethyst_bud", (170, 120, 220)), ("hay_block", (200, 170, 60)), ("target", (220, 200, 190)), ("blackstone", (45, 40, 45)), ("coal_block", (25, 25, 28)), ("millstone", (140, 140, 140)), ("encased_fan", (150, 150, 145)), ("lever", (120, 110, 100)), ("iron_trapdoor", (190, 190, 195)), ("exposed_cut_copper", (160, 120, 90)), ("red_wool", (165, 45, 40)), ("white_wool", (225, 225, 225)), ("brown_wool", (110, 75, 45)), ("white_carpet", (225, 225, 225)), ("red_banner", (165, 45, 40)), ("podzol", (95, 65, 35)), ("lantern", (250, 200, 100)), ("smoker", (90, 85, 80)), ("spruce_fence", (90, 65, 40)), ("ladder", (150, 110, 60)), ("spruce_log", (75, 52, 32)), ("lectern", (170, 120, 60)), ("glass", (190, 225, 235)), ("copper_grate", (80, 150, 125)), ("copper_block", (190, 110, 75)), ("tuff_brick", (108, 111, 100)), ("polished_tuff", (124, 128, 118)), ("tuff", (112, 114, 106)),
 ("coarse_dirt", (110, 80, 55)), ("dirt_path", (150, 122, 70)), ("gravel", (128, 120, 114)), ("grass", (105, 135, 65)), ("dirt", (120, 85, 60))]
def couleur(s):
    for k, c in TABLE:
        if k in s: return c
    return (200, 0, 200)
def plat(s): return any(k in s for k in ("carpet", "slab[type=bottom", "trapdoor", "rail", "_bed"))

def blocs_monde(places):
    W = {}
    for inst in places:
        d = P[NS + inst.nom]; sx, sy, sz = d["size"]
        finals = {(j[0], j[1], j[2]): j[7] for j in d["jigsaws"]}
        for k, s in d["blocks"].items():
            x, y, z = map(int, k.split(","))
            if (x, y, z) in finals: s = finals[(x, y, z)]
            if couleur(s) is None: continue
            X, Z = rot_xz(x, z, sx, sz, inst.r)
            W[(inst.ox + X, y, inst.oz + Z)] = s
    return W

def iso(W, T, sol=True, marge=2):
    pts = dict(W)
    xs = [p[0] for p in W]; zs = [p[2] for p in W]
    if sol:
        for x in range(min(xs) - marge, max(xs) + marge + 1):
            for z in range(min(zs) - marge, max(zs) + marge + 1):
                if (x, 0, z) not in pts: pts[(x, 0, z)] = SOL_CLIMAT
    proj = lambda x, y, z: ((x - z) * T, (x + z) * T / 2 - y * T * 1.15)
    co = [proj(*p) for p in pts]
    minx = min(a for a, _ in co) - T; maxx = max(a for a, _ in co) + T
    miny = min(b for _, b in co) - T; maxy = max(b for _, b in co) + 3 * T
    im = Image.new("RGB", (int(maxx - minx) + 20, int(maxy - miny) + 20), (30, 31, 36)); dr = ImageDraw.Draw(im)
    ox, oy = -minx + 10, -miny + 10
    f = lambda c, k: tuple(int(v * k) for v in c)
    for (x, y, z) in sorted(pts, key=lambda p: (p[0] + p[2], p[1])):
        s = pts[(x, y, z)]; c = couleur(s)
        px, py = proj(x, y, z); px += ox; py += oy
        h = T * 1.15 * (0.3 if plat(s) else 1); dy = T * 1.15 - h
        top = [(px, py + dy), (px + T, py + T / 2 + dy), (px, py + T + dy), (px - T, py + T / 2 + dy)]
        left = [(px - T, py + T / 2 + dy), (px, py + T + dy), (px, py + T + dy + h), (px - T, py + T / 2 + dy + h)]
        right = [(px, py + T + dy), (px + T, py + T / 2 + dy), (px + T, py + T / 2 + dy + h), (px, py + T + dy + h)]
        dr.polygon(left, fill=f(c, .62)); dr.polygon(right, fill=f(c, .8)); dr.polygon(top, fill=c)
    return im

NOMS = {"centre_horloge": "Horloge", "grand_marche_c": "Grand marché", "marche_c": "Marché", "stand_tir_c": "Tir", "laboratoire_c": "Labo", "entrepot_c": "Entrepôt", "atelier_c": "Atelier", "dortoir_c": "Dortoir", "kiosque_c": "·", "chateau_eau_c": "·", "kiosque": "·", "chateau_eau": "·", "centre_fontaine": "Place", "marche": "Marché", "entrepot": "Entrepôt", "atelier": "Atelier", "dortoir": "Dortoir",
        "porte": "Porte", "tour": "Tour", "depot_caisses": "Dépôt", "ferraille": "Ferraille", "abri": "Abri", "salle_cuivre": "Scellée cuivre", "salle_laiton": "Scellée laiton", "salle_ciel": "Scellée ciel"}
def plan(places, W, titre):
    xs = [p[0] for p in W]; zs = [p[2] for p in W]
    x0, z0 = min(xs) - 2, min(zs) - 2; C = 9
    w, h = (max(xs) - x0 + 3) * C, (max(zs) - z0 + 3) * C
    im = Image.new("RGB", (w + 40, h + 90), (30, 31, 36)); dr = ImageDraw.Draw(im)
    top = {}
    for (x, y, z), s in W.items():
        if (x, z) not in top or y >= top[(x, z)][0]: top[(x, z)] = (y, s)
    for x in range(x0, x0 + w // C):
        for z in range(z0, z0 + h // C):
            c = couleur(top[(x, z)][1]) if (x, z) in top else couleur(SOL_CLIMAT)
            dr.rectangle([20 + (x - x0) * C, 60 + (z - z0) * C, 20 + (x - x0) * C + C - 1, 60 + (z - z0) * C + C - 1], fill=c)
    fL = ImageFont.truetype(FB, 13)
    for inst in places:
        lab = NOMS.get(inst.nom) or ("Machine" if inst.nom.startswith("machine") else None)
        if not lab: continue
        b = inst.boite(); mx = 20 + ((b[0] + b[2]) / 2 - x0) * C; mz = 60 + ((b[1] + b[3]) / 2 - z0) * C
        tw = dr.textlength(lab, font=fL)
        dr.rectangle([mx - tw / 2 - 4, mz - 9, mx + tw / 2 + 4, mz + 9], fill=(20, 20, 24)); dr.text((mx - tw / 2, mz - 8), lab, font=fL, fill=(250, 220, 140))
    dr.text((20, 18), titre, font=ImageFont.truetype(FB, 20), fill=(240, 240, 240))
    return im

if __name__ == "__main__":
    places = assembler(graine)
    W = blocs_monde(places)
    titre = ("Cité mécanique" if CITE else "Avant-poste " + NOMS_CLIMAT[CLIMAT])
    tag = ("cite" if CITE else CLIMAT)
    plan(places, W, "%s · plan (assemblage n°%d, terrain plat)" % (titre, graine)).save(os.path.join(OUT, "%s_plan_%d.png" % (tag, graine)))
    im = iso(W, 5 if CITE else 7)
    dr = ImageDraw.Draw(im); dr.text((14, 10), "%s · vue d'ensemble (n°%d)" % (titre, graine), font=ImageFont.truetype(FB, 20), fill=(240, 240, 240))
    im.save(os.path.join(OUT, "%s_vue_%d.png" % (tag, graine)))
    from collections import Counter
    print(Counter(p.nom for p in places))

def couverture(places):
    """Part de l'intérieur de l'enceinte occupée par des pièces (hors enceinte)."""
    r = places[0].boite(); inner = set()
    for p in places[1:]:
        b = p.boite()
        for x in range(b[0], b[2] + 1):
            for z in range(b[1], b[3] + 1):
                inner.add((x, z))
    tot = (r[2] - r[0] - 5) * (r[3] - r[1] - 5)
    return len(inner) / tot
