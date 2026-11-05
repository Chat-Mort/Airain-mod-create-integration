import json, sys, collections, random
sys.path.insert(0, '../armure')
from PIL import Image
exec(open('icones_echo.py').read().split("if __name__")[0])
import gen_armures as GA   # boite_uv, bruit
M = '/home/claude/airain-mod-create-integration/src/main/resources/'
A = M + 'assets/airain/'
# ---- icônes
for n, fn in AUTRES:
    if n == 'bloc_echo_primordial': fn().save(A + 'textures/block/' + n + '.png')
    else: fn().save(A + 'textures/item/' + n + '.png')
for n, fn in ARMURE: fn().save(A + 'textures/item/' + n + '.png')
for n, fn in ARMES: fn(R).save(A + 'textures/item/' + n + '.png')
GRAND = json.load(open(A + 'models/item/katana_sacre.json'))['display']
def modele(n, parent='minecraft:item/generated', grand=False):
    m = {"parent": parent, "textures": {"layer0": "airain:item/" + n}}
    if grand: m["display"] = GRAND
    json.dump(m, open(A + 'models/item/' + n + '.json', 'w'))
for n in ('diademe_echo', 'lingot_arcanium', 'casque_runique', 'plastron_runique', 'jambieres_runiques', 'bottes_runiques'): modele(n)
for n in ('epee_runique', 'pioche_runique'): modele(n, 'minecraft:item/handheld')
for n in ('katana_runique', 'espadon_runique', 'twinblade_runique'): modele(n, 'minecraft:item/handheld', True)
json.dump({"parent": "minecraft:block/cube_all", "textures": {"all": "airain:block/bloc_echo_primordial"}}, open(A + 'models/block/bloc_echo_primordial.json', 'w'))
json.dump({"parent": "airain:block/bloc_echo_primordial"}, open(A + 'models/item/bloc_echo_primordial.json', 'w'))
json.dump({"variants": {"": {"model": "airain:block/bloc_echo_primordial"}}}, open(A + 'blockstates/bloc_echo_primordial.json', 'w'))
D = M + 'data/'
json.dump({"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "airain:bloc_echo_primordial"}],
           "conditions": [{"condition": "minecraft:survives_explosion"}]}]}, open(D + 'airain/loot_table/blocks/bloc_echo_primordial.json', 'w'), indent=1)
for t in ('mineable/pickaxe', 'needs_diamond_tool'):
    f = D + 'minecraft/tags/block/' + t + '.json'; j = json.load(open(f))
    if "airain:bloc_echo_primordial" not in j["values"]: j["values"].append("airain:bloc_echo_primordial")
    json.dump(j, open(f, 'w'), indent=1)

# ---- textures portées : armure runique (64x32, deux couches), diadème (64x64, tuiles)
NE = lambda x, y: NE2 if (x * 3 + y) % 5 else NE3
l1 = Image.new('RGBA', (64, 32), (0,0,0,0)); l2 = Image.new('RGBA', (64, 32), (0,0,0,0))
def tete(face, x, y, w, h):
    if face == 'dessous': return None
    if y == 2 and face != 'dessus': return AR2 if x % 2 else AR3                 # le diadème, autour du front
    if face == 'avant' and y == 1 and x in (3, 4): return LV2
    if y == 4 and face in ('droite', 'gauche', 'arriere') and x % 3 == 1: return LV
    return NE(x, y)
GA.boite_uv(l1, 0, 0, 8, 8, 8, tete)
def corps(face, x, y, w, h):
    if face in ('dessus', 'dessous'): return NE1
    if face == 'avant':
        if y in (0, h-1): return AR2
        if y in (9, 10): return V2 if (x + y) % 3 else V3                         # ceinture de tissu
        if x - (7 - y) in (0, 1) and 1 <= y <= 8: return V3 if x % 2 else V2      # écharpe
        if (x, y) in ((2, 3), (5, 5), (1, 7), (6, 7), (3, 1)): return LV
        return NE(x, y)
    if face == 'arriere': return V1 if y >= 9 else NE(x, y)
    return NE2 if y % 4 else NE3
GA.boite_uv(l1, 16, 16, 8, 12, 4, corps)
def bras(face, x, y, w, h):
    if face == 'dessus': return AR2
    if face == 'dessous': return NE1
    if y == 0: return AR3
    if y == 6 and x % 2 == 0: return LV
    return V1 if y >= 8 else NE2
GA.boite_uv(l1, 40, 16, 4, 12, 4, bras)
def bottes(face, x, y, w, h):
    if face == 'dessus' or y < 7: return None
    if face == 'dessous' or y == h-1: return NE1
    if y == 7: return AR2
    if face == 'avant' and y == 9 and x == 1: return LV
    return NE2
GA.boite_uv(l1, 0, 16, 4, 12, 4, bottes)
def ceinture(face, x, y, w, h):
    if face == 'dessus' or y < 8: return None
    if face == 'dessous': return NE1
    return V2 if y in (8, 9) else NE2
GA.boite_uv(l2, 16, 16, 8, 12, 4, ceinture)
def jambes(face, x, y, w, h):
    if face == 'dessus': return None
    if face == 'dessous': return NE1
    if face == 'avant' and y <= 5: return V2 if (x + y) % 3 else V1             # pan de tissu
    if face == 'avant' and y == 8 and x in (1, 2): return LV
    return NE(x, y)
GA.boite_uv(l2, 0, 16, 4, 12, 4, jambes)
l1.save(A + 'textures/models/armor/runique_layer_1.png'); l2.save(A + 'textures/models/armor/runique_layer_2.png')
dia = Image.new('RGBA', (64, 64), (0,0,0,0))
for i, c in enumerate((AR2, (110, 112, 132), LV, V2)):
    u, v = (i % 2) * 32, (i // 2) * 16
    for x in range(32):
        for y in range(16): dia.putpixel((u + x, v + y), GA.bruit(c, 3) if i != 2 else c + (255,))
dia.save(A + 'textures/models/armor/diademe_layer_1.png')

# ---- recettes (appareil d'enchantement et chambre d'imprégnation d'Ars Nouveau)
RC = D + 'airain/recipe/'
def it(i): return {"item": i}
def appareil(nom, reactif, piedestaux, resultat, source, garder=False):
    json.dump({"type": "ars_nouveau:enchanting_apparatus", "keepNbtOfReagent": garder, "pedestalItems": [it(p) for p in piedestaux],
               "reagent": it(reactif), "result": {"count": 1, "id": resultat}, "sourceCost": source}, open(RC + nom + '.json', 'w'), indent=1)
FR, EC, EP = 'kubejs:fragment_resonance', 'minecraft:echo_shard', 'kubejs:echo_primordial'
appareil('lingot_arcanium', 'minecraft:diamond', [FR, FR, EC, EC] + ['minecraft:lapis_lazuli'] * 4, 'airain:lingot_arcanium', 1000)
appareil('bloc_echo_primordial', EP, [EP] * 5 + ['airain:lingot_arcanium'] * 4, 'airain:bloc_echo_primordial', 3000)
base = [EP, FR, FR, FR, EC, EC, EC, 'minecraft:diamond_block']
for nom, piece in (('plastron_runique', 'netherite_chestplate'), ('jambieres_runiques', 'netherite_leggings'), ('bottes_runiques', 'netherite_boots')):
    appareil(nom, 'minecraft:' + piece, base, 'airain:' + nom, 2500, True)
appareil('casque_runique', 'minecraft:netherite_helmet', base + ['airain:diademe_echo'], 'airain:casque_runique', 2500, True)
for nom, b in (('epee_runique', 'minecraft:netherite_sword'), ('katana_runique', 'simplyswords:netherite_katana'), ('espadon_runique', 'simplyswords:netherite_claymore'),
               ('twinblade_runique', 'simplyswords:netherite_twinblade'), ('pioche_runique', 'minecraft:netherite_pickaxe')):
    appareil(nom, b, base, 'airain:' + nom, 2500, True)

# ---- langues
L = A + 'lang/'
FRL = {"item.airain.diademe_echo": "Diadème d'Écho", "item.airain.lingot_arcanium": "Lingot d'arcanium", "block.airain.bloc_echo_primordial": "Bloc d'écho primordial",
 "item.airain.casque_runique": "Casque runique", "item.airain.plastron_runique": "Plastron runique", "item.airain.jambieres_runiques": "Jambières runiques",
 "item.airain.bottes_runiques": "Bottes runiques", "item.airain.epee_runique": "Épée runique", "item.airain.katana_runique": "Katana runique",
 "item.airain.espadon_runique": "Espadon runique", "item.airain.twinblade_runique": "Twinblade runique", "item.airain.pioche_runique": "Pioche runique",
 "airain.lignee.echo": "Lignée de l'Écho : ne sert qu'avec la fin Écho.",
 "airain.lignee.refus_echo": "Les arcanes ne répondent qu'à ceux qui ont libéré l'Écho.",
 "airain.diademe.l1": "Porté par Morgana Dalmont, Haute-Prêtresse des Arcanes.",
 "airain.diademe.effet": "Diadème : le Warden vous ignore, le sonar porte à 40 blocs (recharge moitié), mana régénéré.",
 "airain.armure.runique.ensemble": "Armure runique (avec le casque runique)",
 "airain.armure.runique.bonus": "Ensemble complet : mana +200, régénération +3, sorts plus puissants ; ni cécité ni obscurité.",
 "airain.arme.epee_echo.nom": "Onde sonique", "airain.arme.epee_echo.effet1": "Le 5e coup sur une même cible déclenche une onde qui traverse les armures.",
 "airain.arme.katana_echo.nom": "Écho de lame", "airain.arme.katana_echo.effet1": "Clic droit : ruée ; une seconde plus tard, l'écho refrappe ce qu'elle a tranché (50 %).",
 "airain.arme.espadon_echo.nom": "Résonance", "airain.arme.espadon_echo.effet1": "Maintenir puis relâcher : onde de choc, et une zone de sculk qui ralentit.",
 "airain.arme.twinblade_echo.nom": "Double tranchant", "airain.arme.twinblade_echo.effet1": "Chaque coup frappe une seconde fois (25 %) et fait luire la cible.",
 "airain.arme.pioche_echo.nom": "Écholocation", "airain.arme.pioche_echo.effet": "Accroupi, clic droit : les minerais à %s blocs luisent à travers la roche.",
 "airain.arme.pioche_echo.trouve": "L'écho revient : %s minerai(s)."}
ENL = {"item.airain.diademe_echo": "Echo Diadem", "item.airain.lingot_arcanium": "Arcanium Ingot", "block.airain.bloc_echo_primordial": "Primordial Echo Block",
 "item.airain.casque_runique": "Runic Helmet", "item.airain.plastron_runique": "Runic Chestplate", "item.airain.jambieres_runiques": "Runic Leggings",
 "item.airain.bottes_runiques": "Runic Boots", "item.airain.epee_runique": "Runic Sword", "item.airain.katana_runique": "Runic Katana",
 "item.airain.espadon_runique": "Runic Claymore", "item.airain.twinblade_runique": "Runic Twinblade", "item.airain.pioche_runique": "Runic Pickaxe",
 "airain.lignee.echo": "Echo line: only works with the Echo ending.",
 "airain.lignee.refus_echo": "The arcana answer only to those who freed the Echo.",
 "airain.diademe.l1": "Worn by Morgana Dalmont, High Priestess of the Arcana.",
 "airain.diademe.effet": "Diadem: the Warden ignores you, sonar reaches 40 blocks (half cooldown), mana regenerated.",
 "airain.armure.runique.ensemble": "Runic armor (with the runic helmet)",
 "airain.armure.runique.bonus": "Full set: mana +200, regeneration +3, stronger spells; no blindness or darkness.",
 "airain.arme.epee_echo.nom": "Sonic Wave", "airain.arme.epee_echo.effet1": "The 5th hit on the same target releases a wave that pierces armor.",
 "airain.arme.katana_echo.nom": "Blade Echo", "airain.arme.katana_echo.effet1": "Right-click: dash; a second later, its echo strikes what it cut again (50%).",
 "airain.arme.espadon_echo.nom": "Resonance", "airain.arme.espadon_echo.effet1": "Hold then release: shockwave, and a sculk zone that slows.",
 "airain.arme.twinblade_echo.nom": "Double Edge", "airain.arme.twinblade_echo.effet1": "Each hit strikes a second time (25%) and makes the target glow.",
 "airain.arme.pioche_echo.nom": "Echolocation", "airain.arme.pioche_echo.effet": "Sneak, right-click: ores within %s blocks glow through the rock.",
 "airain.arme.pioche_echo.trouve": "The echo returns: %s ore(s)."}
for f, d in (('fr_fr.json', FRL), ('en_us.json', ENL)):
    j = json.load(open(L + f), object_pairs_hook=collections.OrderedDict); j.update(d); json.dump(j, open(L + f, 'w'), ensure_ascii=False, indent=1)
print('ok')
