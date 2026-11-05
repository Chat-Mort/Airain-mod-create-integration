#!/usr/bin/env python3
"""La voie de l'Écho : sorts verrouillés, diapason, butin des âmes sans repos, textes.
usage : echo_contenu.py <dossier du pack>"""
import json, os, sys, glob
P = sys.argv[1]; D = os.path.join(P, "kubejs/data"); H = os.path.dirname(os.path.abspath(__file__))
def w(rel, obj):
    f = os.path.join(D, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    json.dump(obj, open(f, "w"), indent=2, ensure_ascii=False)
# --- les sorts les plus puissants demandent l'Écho primordial (même identifiant que la recette d'Ars : elle la remplace)
for f in sorted(glob.glob(os.path.join(H, "ars_glyphs/glyph_*.json"))):
    j = json.load(open(f)); j["inputs"].append({"item": "kubejs:echo_primordial"})
    w("ars_nouveau/recipe/" + os.path.basename(f), j)
# --- le diapason d'Écho
w("kubejs/recipe/airain/diapason_echo.json", {"type": "minecraft:crafting_shaped", "category": "misc",
  "pattern": ["F F", "FSF", " G "],
  "key": {"F": {"item": "kubejs:fragment_resonance"}, "S": {"item": "ars_nouveau:source_gem"}, "G": {"tag": "c:ingots/gold"}},
  "result": {"count": 1, "id": "kubejs:diapason_echo"}})
# --- les âmes sans repos (phantoms) lâchent des fragments de résonance
ph = json.load(open(os.path.join(H, "mcmeta-data/data/minecraft/loot_table/entities/phantom.json")))
ph["pools"].append({"rolls": 1, "bonus_rolls": 0, "conditions": [{"condition": "minecraft:killed_by_player"},
  {"condition": "minecraft:random_chance_with_enchanted_bonus", "enchantment": "minecraft:looting",
   "unenchanted_chance": 0.5, "enchanted_chance": {"type": "minecraft:linear", "base": 0.6, "per_level_above_first": 0.1}}],
  "entries": [{"type": "minecraft:item", "name": "kubejs:fragment_resonance"}]})
w("minecraft/loot_table/entities/phantom.json", ph)
# --- textes
TX = {"fr_fr": {
  "item.kubejs.fragment_resonance": "Fragment de résonance", "item.kubejs.diapason_echo": "Diapason d'Écho",
  "item.kubejs.echo_primordial": "Écho primordial",
  "tooltip.kubejs.fragment_resonance.1": "Un peu de ce que furent les égarés. Il vibre encore.",
  "tooltip.kubejs.diapason_echo.1": "Frappé au cœur du Grand Relais, il fait chanter l'Écho.",
  "tooltip.kubejs.diapason_echo.2": "Clic droit sur le résonateur du Grand Relais.",
  "tooltip.kubejs.echo_primordial.1": "Ce qu'ils étaient, confié librement. Les machines ne le sentent pas.",
  "tooltip.kubejs.echo_primordial.2": "Ingrédient des sorts les plus puissants de l'Écho.",
  "airain.boss.choeur": "Le Chœur des Égarés",
  "airain.boss.reveil": "L'Écho se met à chanter. Des milliers de voix répondent.",
  "airain.boss.deja": "Le Chœur est déjà éveillé.",
  "airain.boss.pas_ici": "Le diapason ne résonne qu'au cœur du Grand Relais.",
  "airain.boss.libere": "Les voix se taisent, une à une. Elles vous laissent ce qu'elles étaient.",
  "airain.ada.titre": "Journal d'Ada Vesper",
  "airain.ada.p1": "Je m'appelle Ada Vesper. Je suis née Ada Vael.\n\nJ'étais ingénieure à la station n°4, avec mon frère Elias. J'ai signé les plans des capsules. Je sais ce qu'elles font.",
  "airain.ada.p2": "Elias est resté. Pour lui, j'ai trahi l'Empire : il ne dit plus « ma sœur », seulement « Ada ».\n\nJe lui ai laissé une lettre. Il n'est jamais venu.\n\nJ'ai pris ceux qui voulaient vivre, et nous sommes partis vers le nord. Nous sommes les Réfractaires.",
  "airain.ada.p3": "L'Écho est plus fort autour des relais brisés. Le plus fort de tous, c'est le Grand Relais, là où la ligne principale a cédé.\n\nDes milliers d'esprits y sont restés coincés. Ils hurlent sans bruit.",
  "airain.ada.p4": "J'ai fabriqué un diapason : des fragments de résonance, une gemme d'Écho, un peu d'or.\n\nFrappé sur le résonateur du Grand Relais, il les réveillera. Ils seront fous de douleur.",
  "airain.ada.p5": "Si quelqu'un les libère, ils lui confieront ce qu'ils sont. Un Écho pur, que les machines ne peuvent pas sentir.\n\nC'est la seule arme qui atteindra ceux qui dorment dans le métal, si un jour ils se réveillent.",
  "airain.ada.p6": "Elias est entré dans une capsule. Je le sais.\n\nS'il est arrivé jusqu'au Cœur, il dort avec l'Empire. S'il s'est perdu en route, il chante avec le Chœur.\n\nJe ne sais pas ce que je souhaite le plus.\n\n— A. V."},
 "en_us": {
  "item.kubejs.fragment_resonance": "Resonance Fragment", "item.kubejs.diapason_echo": "Echo Tuning Fork",
  "item.kubejs.echo_primordial": "Primordial Echo",
  "tooltip.kubejs.fragment_resonance.1": "A little of what the lost once were. It still hums.",
  "tooltip.kubejs.diapason_echo.1": "Struck at the heart of the Great Relay, it makes the Echo sing.",
  "tooltip.kubejs.diapason_echo.2": "Right-click the Great Relay's resonator.",
  "tooltip.kubejs.echo_primordial.1": "What they were, freely given. Machines cannot feel it.",
  "tooltip.kubejs.echo_primordial.2": "Ingredient of the most powerful Echo spells.",
  "airain.boss.choeur": "The Choir of the Lost",
  "airain.boss.reveil": "The Echo starts to sing. Thousands of voices answer.",
  "airain.boss.deja": "The Choir is already awake.",
  "airain.boss.pas_ici": "The tuning fork only resonates at the heart of the Great Relay.",
  "airain.boss.libere": "The voices fall silent, one by one. They leave you what they were.",
  "airain.ada.titre": "Ada Vesper's Journal",
  "airain.ada.p1": "My name is Ada Vesper. I was born Ada Vael.\n\nI was an engineer at station no. 4, with my brother Elias. I signed the capsule blueprints. I know what they do.",
  "airain.ada.p2": "Elias stayed. To him, I betrayed the Empire: he no longer says \"my sister\", only \"Ada\".\n\nI left him a letter. He never came.\n\nI took those who wanted to live, and we went north. We are the Refractories.",
  "airain.ada.p3": "The Echo is stronger around broken relays. Strongest of all is the Great Relay, where the main line gave way.\n\nThousands of minds are stuck there. They scream without a sound.",
  "airain.ada.p4": "I made a tuning fork: resonance fragments, an echo gem, a little gold.\n\nStruck on the Great Relay's resonator, it will wake them. They will be mad with pain.",
  "airain.ada.p5": "If someone frees them, they will entrust that person with what they are. A pure Echo, which machines cannot feel.\n\nIt is the only weapon that will reach those who sleep in the metal, if they ever wake.",
  "airain.ada.p6": "Elias went into a capsule. I know it.\n\nIf he reached the Core, he sleeps with the Empire. If he got lost on the way, he sings with the Choir.\n\nI don't know which I wish for more.\n\n— A. V."}}
L = os.path.join(P, "kubejs/assets/kubejs/lang")
for code, t in TX.items():
    f = os.path.join(L, code + ".json"); j = json.load(open(f)); j.update(t)
    json.dump(j, open(f, "w"), indent=2, ensure_ascii=False)
print("ok")
