#!/usr/bin/env python3
"""Livre de quêtes v2 de L'Empire d'Airain / The Airain Empire (FTB Quests 1.21.1, format v13).
Chaque texte est écrit en paire (français, anglais)."""
import hashlib, os, sys, json

OUT = sys.argv[1]
QDIR = os.path.join(OUT, "config/ftbquests/quests")

def hid(key):
    h = hashlib.md5(("airain2:" + key).encode()).hexdigest()[:16].upper()
    # FTB Quests lit les IDs avec Long.parseLong : premier chiffre entre 1 et 7 obligatoire.
    return "1234567"[int(h[0], 16) % 7] + h[1:]

def s(v):
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'

def item(i, c=1):
    return '{ count: %d, id: %s }' % (c, s(i))

# ---- tâches ----------------------------------------------------------------
def T_item(i, n=1, consume=False):
    d = {"item": item(i), "count": f"{n}L"}
    if consume: d["consume_items"] = "true"
    return ("item", d)
def T_kill(e, n=1): return ("kill", {"entity": s(e), "value": f"{n}L"})
def T_struct(st): return ("structure", {"structure": s(st)})
def T_dim(d): return ("dimension", {"dimension": s(d)})
def T_xp(n): return ("xp", {"value": f"{n}L", "points": "false"})
def T_check(): return ("checkmark", {})
def T_doc(doc):   # un écrit de l'Empire, reconnu à son marqueur (custom_data airain_doc), quel que soit son état
    return ("item", {"item": '{ components: { "minecraft:custom_data": { airain_doc: %s } }, count: 1, id: "minecraft:written_book" }' % s(doc),
                     "count": "1L", "match_components": '"fuzzy"'})
def T_loc(dim, y, h):   # n'importe où dans la dimension, entre y et y + h
    return ("location", {"dimension": s(dim), "ignore_dimension": "false",
                         "position": "[I; -30000000, %d, -30000000]" % y, "size": "[I; 60000000, %d, 60000000]" % h})
def T_stat(st, v): return ("stat", {"stat": s(st), "value": str(v)})
def T_custom(): return ("custom", {})
def T_stage(st): return ("gamestage", {"stage": s(st)})

# ---- récompenses -------------------------------------------------------------
def R_item(i, n=1): return ("item", {"item": item(i), "count": str(n)} if n > 1 else {"item": item(i)})
def R_xp(n): return ("xp", {"xp": str(n)})
def R_cmd(c): return ("command", {"command": s(c), "permission_level": "2", "silent": "true"})
def R_cmd_visible(c): return ("command", {"command": s(c), "permission_level": "2", "silent": "false"})
def R_tag(t): return R_cmd("tag @s add " + t)
def R_book(ench, lvl):
    stack = '{ components: { "minecraft:stored_enchantments": { levels: { %s: %d } } }, count: 1, id: "minecraft:enchanted_book" }' % (s(ench), lvl)
    return ("item", {"item": stack})
def R_carnet(n): return R_cmd("loot give @s loot kubejs:carnet/apprentie_%d" % n)   # une page du carnet de l'apprentie
lire = lambda: T_check()
def R_coin(kind, n=1): return R_item("numismatics:" + kind, n)   # spur 1, bevel 8, sprocket 16, cog 64, crown 512

LANG = {"fr": {}, "en": {}}
chapters = []
QUESTS = {}

def tr(key, pair):
    fr, en = pair
    LANG["fr"][key] = fr
    LANG["en"][key] = en

def chapter(key, filename, title, subtitle, icon, order, invisible=False):
    ch = {"key": key, "id": hid("ch:" + key), "filename": filename, "icon": icon,
          "order": order, "quests": [], "invisible": invisible}
    tr(f"chapter.{ch['id']}.title", title)
    tr(f"chapter.{ch['id']}.chapter_subtitle", ([subtitle[0]], [subtitle[1]]))
    chapters.append(ch)
    return ch

def quest(ch, key, title, x, y, tasks, rewards=(), deps=(), desc=None, subtitle=None,
          shape=None, size=None, optional=False, repeat=False, icon=None, dep_un=False):
    qid = hid("q:" + key)
    assert key not in QUESTS, key
    q = {"id": qid, "x": x, "y": y, "tasks": [], "rewards": [], "deps": [QUESTS[d] for d in deps],
         "shape": shape, "size": size, "optional": optional, "repeat": repeat, "icon": icon, "dep_un": dep_un}
    for n, (tt, data) in enumerate(tasks):
        q["tasks"].append((hid(f"t:{key}:{n}"), tt, data))
    for n, (rt, data) in enumerate(rewards):
        q["rewards"].append((hid(f"r:{key}:{n}"), rt, data))
    tr(f"quest.{qid}.title", title)
    if subtitle: tr(f"quest.{qid}.quest_subtitle", subtitle)
    if desc: tr(f"quest.{qid}.quest_desc", (list(desc[0]), list(desc[1])))
    QUESTS[key] = qid
    ch["quests"].append(q)
    return qid

def journal(fr_lines, en_lines):
    return (["", "&6&lJournal d'ingénieur&r"] + ["&o" + l + "&r" for l in fr_lines],
            ["", "&6&lEngineer's Journal&r"] + ["&o" + l + "&r" for l in en_lines])

def D(fr, en, extra=None):
    """Description : listes de lignes FR et EN, plus éventuellement une page de journal."""
    fr, en = list(fr), list(en)
    if extra:
        fr += extra[0]; en += extra[1]
    return (fr, en)

def titres_taches(key, titres):
    for n, t in enumerate(titres):
        if t: tr(f"task.{hid(f't:{key}:{n}')}.title", t)

# =============================================================================
# I · LE RÉVEIL
# =============================================================================
c1 = chapter("reveil", "01_le_reveil", ("&6I&r · Le Réveil", "&6I&r · The Awakening"),
             ("Un monde vide. Pas une tombe, pas un squelette.", "An empty world. Not a grave, not a skeleton."),
             "minecraft:clock", 1)

quest(c1, "comprendre", ("Comprendre ce qui s'est passé", "Understand What Happened"), 0, 0, [T_stage("airain_journal_lu")],
      [R_item("create:goggles"), R_item("create:wrench"), R_item("airain:codex"), R_item("airain:engineers_manual"), R_item("airain:chronicles"), R_item("minecraft:bread", 16), R_item("minecraft:torch", 32)],
      subtitle=("Lisez le journal de l'ingénieur", "Read the engineer's journal"), shape="gear", size=1.75,
      desc=D(["Vous vous réveillez dans une salle sans aucun souvenir. Cherchez des indices.",
              "", "&8La quête se valide en refermant le carnet, à la dernière page.&r"],
             ["You wake up in a room with no memory at all. Look for clues.",
              "", "&8The quest completes when you close the journal, on its last page.&r"]))

quest(c1, "bienvenue", ("Règles de survie", "Survival Rules"), 0, 2, [T_check()], [R_coin("bevel", 2)], deps=["comprendre"],
      desc=D(["&eÀ deux :&r rejoignez la même équipe (/ftbteams party create, puis invite) pour partager le livre.",
              "&eLes Schémas&r et &eles Sceaux&r débloquent les machines clés. Ils ne sont jamais consommés.",
              "&eChaque joueur&r doit réclamer lui-même les récompenses qui ouvrent un portail ou un chantier.",
              "&eLe comptoir&r du laboratoire échange vos pièces contre ce qu'on ne trouve nulle part. Payez avec les pièces exactes, ou par carte (quête « La banque de l'Empire »)."],
             ["&ePlaying together:&r join the same team (/ftbteams party create, then invite) to share the book.",
              "&eSchematics&r and &eSeals&r unlock the key machines. They are never consumed.",
              "&eEach player&r must claim the rewards that open a portal or a Great Work themselves.",
              "&eThe counter&r in the lab trades your coins for things you can't find anywhere. Pay with the exact coins, or by card (\"The Empire Bank\" quest)."]))

quest(c1, "outils", ("Des outils dignes de ce nom", "Proper Tools"), 2, 0, [T_item("minecraft:iron_pickaxe")],
      [R_item("minecraft:iron_ingot", 8)], deps=["comprendre"],
      desc=D(["Les outils et l'épée de fer se fabriquent toujours à la main. Les autres armes et les armures passeront par les machines."],
             ["Tools and the iron sword are always crafted by hand. Other weapons and armor will go through the machines."]))

quest(c1, "surface", ("Remonter à la surface", "Back to the Surface"), 4, -2, [T_check()], [R_coin("bevel", 2)], deps=["outils"],
      desc=D(["Le laboratoire reste votre base. Dehors, le monde est vide : pas une tombe, pas un squelette.",
              "Validez quand vous avez exploré les alentours."],
             ["The lab stays your base. Outside, the world is empty: not a grave, not a skeleton.",
              "Tick the box once you have explored the surroundings."]))

quest(c1, "alliage", ("L'alliage d'andésite", "Andesite Alloy"), 4, 0, [T_item("create:andesite_alloy", 16)],
      [R_xp(50)], deps=["outils"],
      desc=D(["La base de toute la mécanique d'Airain. Andésite + pépite de fer ou de zinc."],
             ["The basis of all Airain mechanics. Andesite + iron or zinc nugget."]))

quest(c1, "roue", ("La première roue", "The First Wheel"), 6, 0, [T_item("create:water_wheel"), T_item("create:shaft", 8)],
      [R_item("create:cogwheel", 4)], deps=["alliage"],
      desc=D(["Une roue à eau dans un courant : votre première source de force mécanique. Portez les lunettes pour lire vitesse et contrainte."],
             ["A water wheel in a stream: your first source of rotational force. Wear the goggles to read speed and stress."]))

quest(c1, "engrenages", ("Engrenages", "Cogwheels"), 8, 0, [T_item("create:cogwheel", 8), T_item("create:large_cogwheel", 4)],
      [R_xp(80)], deps=["roue"],
      desc=D(["Petit et grand engrenage : en les combinant, on change la vitesse. Plus vite = plus de contrainte."],
             ["Small and large cogwheels change rotation speed. Faster = more stress."]))

quest(c1, "boitiers1", ("Boîtiers d'andésite", "Andesite Casing"), 6, 2, [T_item("create:andesite_casing", 8)],
      [R_xp(80)], deps=["alliage"],
      desc=D(["Alliage d'andésite appliqué sur un tronc écorcé."], ["Andesite alloy applied to a stripped log."]))

quest(c1, "meule", ("La meule", "The Millstone"), 8, 2, [T_item("create:millstone")], [R_xp(100)],
      deps=["boitiers1", "engrenages"],
      desc=D(["La meule broie gravier, fleurs, céréales… Farine, silex et colorants sans effort."],
             ["The millstone grinds gravel, flowers, grain… Flour, flint and dyes without effort."]))

quest(c1, "tapis", ("Tapis et dépôt", "Belts and Depot"), 10, 2, [T_item("create:belt_connector", 8), T_item("create:depot", 2)],
      [R_xp(100)], deps=["meule"],
      desc=D(["Le tapis roulant (fait de varech séché) transporte les objets entre les machines."],
             ["The mechanical belt (made of dried kelp) carries items between machines."]))

quest(c1, "moulin", ("Le moulin", "The Mill"), 12, 1, [T_check()], [R_coin("bevel", 4), R_xp(150)],
      deps=["tapis"], shape="square",
      desc=D(["Construisez un moulin qui alimente en même temps une meule, un tapis roulant et un dépôt. Validez la coche quand tout tourne."],
             ["Build a mill that powers a millstone, a belt and a depot at the same time. Tick the box when it all runs."]))

quest(c1, "q_alliage", ("Réserve d'alliage", "Alloy Stockpile"), 10, 0, [T_item("create:andesite_alloy", 64)],
      [R_coin("bevel", 2)], deps=["engrenages"],
      desc=D(["Il en faudra beaucoup. Un mixeur saura bientôt le faire pour vous."], ["You will need a lot. A mixer will soon make it for you."]))

quest(c1, "cuir", ("Équipement de départ", "Starting Gear"), 2, 2,
      [T_item("minecraft:iron_sword")], [R_item("minecraft:bread", 8)], deps=["outils"],
      desc=D(["Une épée de fer, forgée à la main avec les lingots du laboratoire : avec la pioche, c'est tout ce qu'il faut pour sortir.",
              "L'armure de fer arrivera au chapitre II, avec la presse."],
             ["An iron sword, forged by hand with the ingots from the laboratory: together with the pickaxe, it's all you need to head out.",
              "Iron armor comes in chapter II, with the press."]))

quest(c1, "village", ("Signes de vie", "Signs of Life"), 4, 4, [T_struct("#kubejs:avant_postes")], [R_coin("bevel", 4)], deps=["cuir"],
      desc=D(["Trouvez un avant-poste de l'Empire. Personne ne vous y attend, mais ses machines fonctionnent encore : on y achète ce qui manque contre des pièces.",
              "Une salle y est restée scellée. Revenez quand vous aurez le bon Schéma."],
             ["Find an Empire outpost. Nobody is waiting for you there, but its machines still work: you can buy what you lack with coins.",
              "One room there is still sealed. Come back when you have the right Schematic."]))

quest(c1, "ruines_piste", ("Les ruines enfouies", "Buried Ruins"), 6, 4, [T_struct("minecraft:trail_ruins")],
      [R_item("minecraft:brush"), R_coin("bevel", 2)], deps=["village"], optional=True,
      desc=D(["&7Optionnel.&r Des ruines à moitié enterrées. Un pinceau révèle ce que la terre cache."],
             ["&7Optional.&r Half-buried ruins. A brush reveals what the earth hides."]))

quest(c1, "atelier", ("Grand Chantier : le premier atelier", "Great Work: The First Workshop"), 14, 1,
      [T_item("create:andesite_alloy", 128, consume=True), T_item("create:andesite_casing", 32, consume=True)],
      [R_item("minecraft:iron_block", 2), R_coin("sprocket", 2), R_xp(300)], deps=["moulin", "q_alliage"],
      shape="hexagon", size=1.5, subtitle=("Ouvre le chapitre II", "Opens chapter II"),
      desc=D(["Livrez les matériaux pour remettre en état un atelier impérial. Ils sont consommés.",
              "En échange : de quoi fabriquer votre première presse."],
             ["Deliver the materials to restore an imperial workshop. They are consumed.",
              "In return: enough to build your first press."]))

# =============================================================================
# II · L'ÂGE DE L'ANDÉSITE
# =============================================================================
c2 = chapter("andesite", "02_age_andesite", ("&6II&r · L'Âge de l'Andésite", "&6II&r · The Andesite Age"),
             ("Les premières machines. Et des ruines étrangement propres.", "The first machines. And ruins that are strangely clean."),
             "create:andesite_casing", 2)

quest(c2, "presse", ("La presse mécanique", "The Mechanical Press"), 0, 0, [T_item("create:mechanical_press")],
      [R_xp(150)], deps=["atelier"],
      desc=D(["Bloc de fer + boîtier d'andésite. La presse aplatit les lingots en plaques : tout le chapitre en dépend."],
             ["Iron block + andesite casing. The press flattens ingots into sheets: the whole chapter depends on it."]))

quest(c2, "bureau_etudes", ("Le bureau d'études", "The Design Office"), 0, -2,
      [T_item("create:schematic_table"), T_item("create:schematicannon")],
      [R_cmd('give @s airain:blueprint[minecraft:custom_data={plan:"moulin_vent"}]'), R_item("minecraft:gunpowder", 16)], deps=["presse"],
      desc=D(["Les ingénieurs de l'Empire ne montaient jamais une machine deux fois à la main : ils dessinaient un plan, et le canon le posait.",
              "Les &6bureaux d'études&r des avant-postes vendent des &6plans de l'Empire&r (moulin à vent, centrale à roues, meunerie…). Clic droit sur un plan : il devient un schéma.",
              "Posez le schéma au sol (clic droit pour le placer, il apparaît en fantôme), puis donnez-le au &6canon à schémas&r avec de la poudre à canon et un coffre de matériaux à côté : il construit tout seul.",
              "&8Le pack doit contenir son dossier « schematics » (voir le README).&r"],
             ["The Empire's engineers never built a machine twice by hand: they drew a plan, and the cannon placed it.",
              "Outpost &6design offices&r sell &6Empire plans&r (windmill, water wheel plant, mill…). Right-click a plan: it becomes a schematic.",
              "Deploy the schematic (right-click to place it, it shows as a ghost), then give it to the &6schematicannon&r with gunpowder and a chest of materials next to it: it builds by itself.",
              "&8The pack must include its \"schematics\" folder (see the README).&r"]))
titres_taches("bureau_etudes", [("La table à schémas", "The schematic table"), ("Le canon à schémas", "The schematicannon")])
quest(c2, "plaques", ("Plaques de fer", "Iron Sheets"), 2, 0, [T_item("create:iron_sheet", 32)], [R_coin("bevel", 3)],
      deps=["presse"])

quest(c2, "mixeur", ("Le mixeur et le bassin", "Mixer and Basin"), 2, -2,
      [T_item("create:mechanical_mixer"), T_item("create:basin")], [R_xp(150)], deps=["plaques"],
      desc=D(["Le mixeur au-dessus d'un bassin mélange les ingrédients. Automatisez l'alliage d'andésite avec."],
             ["A mixer above a basin combines ingredients. Use it to automate andesite alloy."]))

quest(c2, "ventilateur", ("Le ventilateur", "The Encased Fan"), 4, -2, [T_item("create:encased_fan")], [R_xp(150)],
      deps=["plaques"],
      desc=D(["Soufflé à travers l'eau : lavage. À travers le feu : cuisson ou fonte."],
             ["Blowing through water: washing. Through fire: smoking or smelting."]))

quest(c2, "outils_meca", ("Scie et perceuse", "Saw and Drill"), 4, 2,
      [T_item("create:mechanical_saw"), T_item("create:mechanical_drill")], [R_xp(150)], deps=["plaques"],
      desc=D(["Pour couper le bois et miner sans fatigue."], ["To cut wood and mine without tiring."]))

quest(c2, "goulottes", ("Goulottes et entonnoirs", "Chutes and Funnels"), 6, 2,
      [T_item("create:chute", 4), T_item("create:andesite_funnel", 4)], [R_xp(100)], deps=["outils_meca"])

quest(c2, "ferme", ("La ferme automatique", "The Automatic Farm"), 8, 2,
      [T_item("create:mechanical_harvester", 2), T_item("minecraft:bread", 32)], [R_coin("sprocket", 1), R_xp(200)],
      deps=["goulottes"],
      desc=D(["Une moissonneuse sur un engin qui va et vient récolte et replante. Le pain servira de provisions."],
             ["A harvester on a moving contraption harvests and replants. The bread will be your rations."]))

quest(c2, "minerai", ("La fonderie à ventilateur", "The Fan Smeltery"), 6, -2,
      [T_item("minecraft:iron_ingot", 64), T_check()], [R_coin("sprocket", 2), R_xp(300)],
      deps=["ventilateur", "mixeur"], shape="square",
      desc=D(["Le fer brut sur un tapis roulant, un ventilateur soufflant à travers la lave : des lingots à la chaîne, sans four. Validez quand la ligne tourne sans vous.",
              "&8Les roues de broyage, plus rentables, arriveront au chapitre IV.&r"],
             ["Raw iron on a belt, a fan blowing through lava: ingots in bulk, no furnace. Tick the box when the line runs without you.",
              "&8Crushing wheels, more profitable, arrive in chapter IV.&r"]))

quest(c2, "q_plaques", ("Laminoir", "Rolling Mill"), 8, -2, [T_item("create:iron_sheet", 256)], [R_coin("sprocket", 3)],
      deps=["minerai"],
      desc=D(["Elles serviront pour l'armure, les hélices, les goulottes et les commandes de l'Empire."],
             ["They will go into armor, propellers, chutes and the Empire's orders."]))

quest(c2, "armure_fer", ("L'armure de fer pressée", "Pressed Iron Armor"), 4, 0,
      [T_item("minecraft:iron_helmet"), T_item("minecraft:iron_chestplate"), T_item("minecraft:iron_leggings"), T_item("minecraft:iron_boots")],
      [R_xp(250)], deps=["plaques"],
      desc=D(["Les armures de fer se fabriquent avec des &6plaques de fer&r au lieu des lingots."],
             ["Iron armor is now made with &6iron sheets&r instead of ingots."]))

quest(c2, "arme_fer", ("Une vraie arme", "A Real Weapon"), 6, 0, [T_check()], [R_coin("bevel", 4)], deps=["armure_fer"],
      desc=D(["Forgez une arme de fer de Simply Swords (épée longue, katana, lance…). Elles demandent aussi des plaques. Validez quand c'est fait."],
             ["Forge an iron Simply Swords weapon (longsword, katana, spear…). They also need sheets. Tick the box when done."]))

quest(c2, "ruines_propres", ("Des ruines entretenues", "Well-Kept Ruins"), 8, 0, [T_check()], [R_item("minecraft:golden_carrot", 8)],
      deps=["arme_fer"],
      desc=D(["Certaines ruines sont &opropres&r. Les mécanismes sont huilés, les couloirs balayés. Les gardiens ne sont peut-être pas déréglés…",
              "&oMais pour qui font-ils la maintenance ?&r"],
             ["Some ruins are &oclean&r. Mechanisms oiled, corridors swept. Maybe the guardians are not malfunctioning…",
              "&oBut who are they maintaining it for?&r"],
             journal(["Les sentinelles de cuivre veilleront sur les salles d'épreuve."], ["The copper sentinels will watch over the trial chambers."])))

quest(c2, "salles", ("Les salles d'épreuve", "The Trial Chambers"), 10, 0, [T_struct("minecraft:trial_chambers"), T_item("minecraft:trial_key", 3)],
      [R_xp(300)], deps=["ruines_propres"],
      desc=D(["Sous terre, des salles de cuivre et de tuf. Videz quelques générateurs d'épreuve pour récupérer des clés."],
             ["Underground halls of copper and tuff. Clear some trial spawners to collect keys."]))

quest(c2, "prepa2", ("Préparatifs", "Preparations"), 10, 2, [T_item("minecraft:shield"), T_item("minecraft:arrow", 16), T_item("minecraft:bread", 32)],
      [R_item("minecraft:cooked_beef", 16)], deps=["salles", "ferme"],
      desc=D(["Bouclier, flèches et provisions avant l'épreuve funeste."], ["Shield, arrows and rations before the ominous trial."]))

quest(c2, "presage", ("Le présage funeste", "The Ominous Omen"), 12, 0, [T_item("minecraft:ominous_bottle")], [R_xp(200)],
      deps=["salles"],
      desc=D(["Les Réfractaires, ceux qui ont refusé le Transfert, vivent dans des camps de fortune. Environ un camp sur trois tient un étal qui vend la &6fiole funeste&r.",
              "Buvez-la avant d'entrer dans une salle d'épreuve : elle devient funeste."],
             ["The Refractories, those who refused the Transfer, live in makeshift camps. About one camp in three keeps a stall selling the &6ominous bottle&r.",
              "Drink it before entering a trial chamber: it turns ominous."]))

quest(c2, "gardien_vent", ("Le gardien du vent", "The Wind Guardian"), 14, 1,
      [T_item("minecraft:ominous_trial_key"), T_kill("minecraft:breeze", 10)],
      [R_item("kubejs:schema_cuivre"), R_item("kubejs:fragment_rouages"), R_coin("cog", 1), R_xp(800)],
      deps=["presage", "prepa2"], shape="hexagon", size=1.75,
      subtitle=("Débloque le Schéma du Cuivre", "Unlocks the Copper Schematic"),
      desc=D(["Obtenez une &6clé funeste&r et abattez 10 gardiens de vent.",
              "", "&eRécompense :&r le &6Schéma du Cuivre&r (pompe, bec verseur, égouttoir).",
              "&8En tombant, le dernier gardien laisse échapper un éclat de métal tiède. Un souvenir.&r"],
             ["Get an &6ominous trial key&r and bring down 10 wind guardians.",
              "", "&eReward:&r the &6Copper Schematic&r (pump, spout, item drain).",
              "&8As it falls, the last guardian drops a shard of warm metal. A memory.&r"]))

quest(c2, "masse", ("Bonus : la masse d'armes", "Bonus: The Mace"), 14, 3, [T_item("minecraft:heavy_core"), T_item("minecraft:mace")],
      [R_coin("cog", 1)], deps=["gardien_vent"], optional=True,
      desc=D(["&7Optionnel.&r Le noyau lourd tombe rarement des coffres funestes."], ["&7Optional.&r The heavy core rarely drops from ominous vaults."]))

quest(c2, "banque", ("La banque de l'Empire", "The Empire Bank"), 2, 2,
      [T_item("numismatics:white_card")], [R_coin("sprocket", 2)], deps=["plaques"], optional=True,
      subtitle=("Quête secondaire : payer par carte", "Side quest: pay by card"),
      desc=D(["&7Optionnel.&r Les distributeurs demandent les pièces exactes et ne rendent pas la monnaie. La banque règle ce problème.",
              "", "1. Fabriquez une &6carte bancaire&r : plaque de fer, plaque d'or et colorant blanc.",
              "2. Clic droit avec la carte en main : elle se lie à votre compte.",
              "3. Déposez vos pièces au &6terminal bancaire&r du comptoir.",
              "4. Achetez aux distributeurs en tenant la carte : la valeur totale est débitée, quelles que soient vos pièces."],
             ["&7Optional.&r Vendors ask for the exact coins and give no change. The bank solves that.",
              "", "1. Craft a &6bank card&r: iron sheet, gold sheet and white dye.",
              "2. Right-click with the card in hand: it binds to your account.",
              "3. Deposit your coins at the counter's &6bank terminal&r.",
              "4. Buy from vendors while holding the card: the total value is charged, whatever your coins."]))

quest(c2, "ars", ("L'Écho", "The Echo"), 0, 2,
      [T_item("minecraft:amethyst_shard", 8), T_item("minecraft:lapis_lazuli", 8)],
      [R_item("ars_nouveau:worn_notebook"), R_xp(150)], deps=["atelier"], optional=True,
      subtitle=("Quête secondaire : la magie de l'Écho", "Side quest: the magic of the Echo"),
      desc=D(["&7Optionnel.&r Pendant le Transfert, tous les esprits ne sont pas arrivés jusqu'au Cœur. Ceux qui se sont perdus flottent encore dans le monde : les Réfractaires appellent cela l'&dÉcho&r.",
              "L'Empire l'avait interdit. Les Réfractaires, eux, ont appris à s'en servir. L'améthyste résonne avec lui.",
              "Rapportez des éclats d'améthyste et du lapis-lazuli : un carnet réfractaire vous apprendra à capter l'Écho.",
              "&8Récompense : le carnet d'Ars Nouveau, le guide de toute la magie de l'Écho.&r"],
             ["&7Optional.&r During the Transfer, not every mind made it to the Core. The lost ones still drift through the world: the Refractories call it the &dEcho&r.",
              "The Empire had forbidden it. The Refractories learned to use it. Amethyst resonates with it.",
              "Bring amethyst shards and lapis lazuli: a Refractory notebook will teach you how to capture the Echo.",
              "&8Reward: the Ars Nouveau notebook, the guide to all Echo magic.&r"]))

# =============================================================================
# III · L'ÂGE DU CUIVRE
# =============================================================================
c3 = chapter("cuivre", "03_age_cuivre", ("&6III&r · L'Âge du Cuivre", "&6III&r · The Copper Age"),
             ("Les fluides, les profondeurs, et les inscriptions.", "Fluids, the depths, and the inscriptions."),
             "create:copper_casing", 3)

quest(c3, "boitier_cuivre", ("Boîtier de cuivre", "Copper Casing"), 0, 0, [T_item("create:copper_casing", 8)], [R_xp(150)],
      deps=["gardien_vent"])
quest(c3, "tuyaux", ("Tuyauterie", "Plumbing"), 2, -2, [T_item("create:fluid_pipe", 32)], [R_item("minecraft:copper_ingot", 16)],
      deps=["boitier_cuivre"])
quest(c3, "pompe", ("La pompe mécanique", "The Mechanical Pump"), 4, -2, [T_item("create:mechanical_pump", 2)], [R_xp(200)],
      deps=["tuyaux"],
      desc=D(["Engrenage + tuyau + &6Schéma du Cuivre&r (non consommé)."], ["Cogwheel + pipe + &6Copper Schematic&r (not consumed)."]))
quest(c3, "reservoirs", ("Réservoirs", "Fluid Tanks"), 2, 2, [T_item("create:fluid_tank", 16)], [R_xp(150)], deps=["boitier_cuivre"])
quest(c3, "bec", ("Bec verseur et égouttoir", "Spout and Item Drain"), 4, 2,
      [T_item("create:spout"), T_item("create:item_drain")], [R_xp(200)], deps=["reservoirs", "pompe"])
quest(c3, "banc", ("Le banc d'entretien", "The Maintenance Bench"), 4, 4, [T_item("airain:maintenance_bench")],
      [R_item("kubejs:huile_machine", 8), R_xp(200)], deps=["bec"], optional=True,
      subtitle=("Quête secondaire : réparer sans expérience", "Side quest: repair without experience"),
      desc=D(["&7Optionnel.&r Les automates ne saignent pas : ils fuient. Leur &6huile de machine&r fait tourner le banc d'entretien.",
              "Il répare comme une enclume (mêmes matériaux, mêmes quantités) mais brûle de l'huile au lieu de l'expérience : 1 000 mB, soit deux burettes, par lingot ou par fusion.",
              "C'est une vraie machine, montée comme la meule à farine : un rouage voisin ou un arbre par-dessous l'entraîne, et elle consomme du stress. Plus elle tourne vite (16 tr/min au moins), plus elle travaille vite ; les objets très enchantés prennent bien plus longtemps.",
              "&6Clic droit main vide&r : l'écran du banc. L'objet abîmé en haut, le matériau en dessous, l'objet réparé sort à droite. La cuve d'huile est à gauche, les trois emplacements de &6modules&r tout à droite.",
              "Un outil ou une arme réparé ressort &6affûté&r pour un temps (voir « Le fil de la lame »).",
              "&8Une burette ou un seau se verse d'un clic droit ; l'huile passe aussi au tuyau, après un égouttoir. Entonnoirs et tapis l'alimentent et récupèrent l'objet réparé. Les lunettes d'ingénieur montrent l'avancement et le temps restant.&r"],
             ["&7Optional.&r Automatons don't bleed: they leak. Their &6machine oil&r powers the maintenance bench.",
              "It repairs like an anvil (same materials, same amounts) but burns oil instead of experience: 1,000 mB, two oil cans, per ingot or per merge.",
              "It is a real machine, set up like the millstone: a neighbouring cogwheel or a shaft from below drives it, and it uses stress. The faster it turns (16 RPM at least), the faster it works; heavily enchanted items take much longer.",
              "&6Right-click empty-handed&r: the bench screen. The damaged item on top, the material below, the repaired item comes out on the right. The oil tank is on the left, the three &6module&r slots on the far right.",
              "A repaired tool or weapon comes out &6sharpened&r for a while (see \"The Edge of the Blade\").",
              "&8An oil can or a bucket pours in with a right-click; oil also flows through pipes, after an item drain. Funnels and belts feed it and collect the repaired item. Engineer's goggles show the progress and the time left.&r"]))
quest(c3, "affutage", ("Le fil de la lame", "The Edge of the Blade"), 6, 4, [T_check()], [R_coin("sprocket", 1), R_xp(150)],
      deps=["banc"], optional=True,
      desc=D(["&7Optionnel.&r Les ingénieurs de l'Empire ne rendaient jamais un outil sans l'avoir passé à la meule.",
              "Tout outil ou arme qui sort du banc d'entretien est &6affûté&r pendant 10 minutes : +10 % de vitesse de minage pour un outil, +10 % de dégâts pour une arme. Si la cuve d'huile est pleine aux trois quarts au moment de la réparation, l'effet dure 15 minutes.",
              "L'infobulle de l'objet affiche le temps qui reste. Validez après votre première réparation."],
             ["&7Optional.&r The Empire's engineers never handed a tool back without running it over the grindstone.",
              "Any tool or weapon that leaves the maintenance bench is &6sharpened&r for 10 minutes: +10% mining speed for a tool, +10% damage for a weapon. If the oil tank is at least three-quarters full when the repair is done, it lasts 15 minutes.",
              "The item's tooltip shows the time left. Tick the box after your first repair."]))
titres_taches("affutage", [("Réparer un outil ou une arme au banc", "Repair a tool or weapon at the bench")])
quest(c3, "vapeur", ("La machine à vapeur", "The Steam Engine"), 6, 2, [T_item("create:steam_engine"), T_check()],
      [R_coin("sprocket", 2)], deps=["bec"],
      desc=D(["Réservoirs + eau + un feu dessous : la chaleur passive fait tourner une petite machine à vapeur.",
              "&8Les brûleurs à blaze du chapitre IV la rendront bien plus puissante.&r"],
             ["Tanks + water + a fire underneath: passive heat runs a small steam engine.",
              "&8Chapter IV's blaze burners will make it far more powerful.&r"]))
quest(c3, "q_cuivre", ("Feuilles de cuivre", "Copper Sheets"), 6, -2, [T_item("create:copper_sheet", 256)], [R_coin("sprocket", 3)],
      deps=["pompe"],
      desc=D(["Pour les tuyaux, l'équipement de plongée et l'armure de diamant."], ["For pipes, diving gear and diamond armor."]))
quest(c3, "forge", ("Grand Chantier : la Forge impériale", "Great Work: The Imperial Forge"), 8, -2,
      [T_item("create:iron_sheet", 128, consume=True), T_item("create:copper_sheet", 128, consume=True), T_item("create:golden_sheet", 32, consume=True)],
      [R_item("kubejs:sceau_forge"), R_coin("cog", 1), R_xp(500)], deps=["q_cuivre"], shape="hexagon", size=1.5,
      subtitle=("Débloque l'armure de diamant", "Unlocks diamond armor"),
      desc=D(["Rallumez la forge de l'Empire. Les plaques sont consommées.", "&eRécompense :&r le &6Sceau de la Forge&r, exigé (sans être consommé) par l'armure de diamant."],
             ["Rekindle the Empire's forge. The sheets are consumed.", "&eReward:&r the &6Imperial Forge Seal&r, required (not consumed) for diamond armor."]))
quest(c3, "armure_diamant", ("L'armure de diamant", "Diamond Armor"), 10, -2,
      [T_item("minecraft:diamond_helmet"), T_item("minecraft:diamond_chestplate"), T_item("minecraft:diamond_leggings"), T_item("minecraft:diamond_boots")],
      [R_xp(500)], deps=["forge"],
      desc=D(["Diamants + plaques de cuivre + Sceau de la Forge."], ["Diamonds + copper sheets + Imperial Forge Seal."]))
quest(c3, "plongee", ("L'équipement de plongée", "Diving Gear"), 8, 2,
      [T_item("create:copper_diving_helmet"), T_item("create:copper_backtank"), T_item("create:copper_diving_boots")],
      [R_xp(300)], deps=["vapeur"],
      desc=D(["Le réservoir dorsal se recharge en air quand on le pose sur une source de rotation. Avec le casque, on respire sous l'eau."],
             ["The backtank refills with air when placed on a rotation source. With the helmet, you breathe underwater."]))
quest(c3, "inscriptions", ("Les inscriptions", "The Inscriptions"), 10, 0, [T_check()], [R_item("minecraft:conduit")],
      deps=["plongee", "armure_diamant"],
      desc=D(["Sur les murs d'une ruine noyée, répétées des centaines de fois :", "&o« Nous dormons dans le métal. »&r", "&o« Le grand transfert approche. »&r"],
             ["On the walls of a drowned ruin, repeated hundreds of times:", "&o\"We sleep in the metal.\"&r", "&o\"The great transfer approaches.\"&r"],
             journal(["Les gardiens des marées garderont le secret de l'alliage."], ["The tide guardians will keep the secret of the alloy."])))
quest(c3, "monument", ("Les ruines englouties", "The Sunken Ruins"), 12, 0, [T_struct("minecraft:monument")],
      [R_book("minecraft:respiration", 3), R_book("minecraft:aqua_affinity", 1), R_xp(300)], deps=["inscriptions"],
      desc=D(["Le temple de prismarine où l'Empire cachait le secret du laiton. Repérez-le avant de l'attaquer.",
              "&8Récompense : les livres Respiration III et Affinité aquatique, pour le casque de plongée.&r"],
             ["The prismarine temple where the Empire hid the secret of brass. Scout it before you attack.",
              "&8Reward: Respiration III and Aqua Affinity books, for the diving helmet.&r"]))
quest(c3, "prepa3", ("Préparatifs sous-marins", "Underwater Preparations"), 12, 2,
      [T_item("minecraft:milk_bucket", 3), T_item("create:copper_backtank")], [R_coin("sprocket", 1)], deps=["monument"],
      desc=D(["Le lait annule la fatigue de minage des gardiens. Un réservoir d'air chargé, et c'est parti."],
             ["Milk clears the guardians' mining fatigue. A charged backtank, and off you go."]))
quest(c3, "gardien_marees", ("Le gardien des marées", "The Tide Guardian"), 14, 1, [T_kill("minecraft:elder_guardian", 3)],
      [R_item("kubejs:schema_laiton"), R_item("kubejs:fragment_marees"), R_tag("airain_nether"), R_coin("cog", 2), R_xp(1000)],
      deps=["prepa3"], shape="hexagon", size=1.75,
      subtitle=("Schéma du Laiton, ouverture du Nether", "Brass Schematic, Nether opens"),
      desc=D(["Les trois gardiens anciens du monument.", "", "&eRécompenses :&r le &6Schéma du Laiton&r (brûleur à blaze), et le &cNether&r s'ouvre pour vous.",
              "&8Chaque joueur doit réclamer sa propre récompense pour pouvoir passer le portail.&r"],
             ["The monument's three elder guardians.", "", "&eRewards:&r the &6Brass Schematic&r (blaze burner), and the &cNether&r opens for you.",
              "&8Each player must claim their own reward to pass through the portal.&r"]))

# =============================================================================
# IV · L'ÂGE DU LAITON
# =============================================================================
c4 = chapter("laiton", "04_age_laiton", ("&6IV&r · L'Âge du Laiton", "&6IV&r · The Brass Age"),
             ("Le cœur de la technologie d'Airain. Et une salle pleine de capsules vides.", "The heart of Airain technology. And a hall full of empty capsules."),
             "create:brass_casing", 4)

quest(c4, "nether", ("Vers le Nether", "Into the Nether"), 0, 0, [T_dim("minecraft:the_nether")], [R_xp(200)], deps=["gardien_marees"])
quest(c4, "blaze", ("Capturer un blaze", "Catch a Blaze"), 2, -2, [T_item("create:blaze_burner")], [R_xp(300)], deps=["nether"],
      desc=D(["Brûleur vide (avec le Schéma du Laiton), puis clic droit sur une lanterne de forge (un blaze). Placé sous un bassin, il chauffe le mixeur."],
             ["Empty burner (with the Brass Schematic), then right-click a forge lantern (a blaze). Under a basin, it heats the mixer."]))
quest(c4, "quartz", ("Quartz et tubes", "Quartz and Tubes"), 2, 2, [T_item("create:polished_rose_quartz", 16), T_item("create:electron_tube", 8)],
      [R_xp(200)], deps=["nether"],
      desc=D(["Quartz du Nether + redstone = quartz rose. Poli, il devient le cœur des tubes électroniques."],
             ["Nether quartz + redstone = rose quartz. Polished, it becomes the core of electron tubes."]))
quest(c4, "laiton", ("L'alliage impérial", "The Imperial Alloy"), 4, -2, [T_item("create:brass_ingot", 32)], [R_item("create:zinc_ingot", 16)],
      deps=["blaze"])
quest(c4, "boitier_laiton", ("Boîtier de laiton", "Brass Casing"), 6, -2, [T_item("create:brass_casing", 16)], [R_xp(200)], deps=["laiton"])
quest(c4, "deployeur", ("Le déployeur", "The Deployer"), 6, 0, [T_item("create:deployer", 2)], [R_xp(250)], deps=["laiton", "quartz"],
      desc=D(["Il agit comme un joueur : il pose, utilise, assemble. Il rend possible l'assemblage en séquence."],
             ["It acts like a player: places, uses, assembles. It makes sequenced assembly possible."]))
quest(c4, "precision", ("Mécanisme de précision", "Precision Mechanism"), 8, 0, [T_item("create:precision_mechanism", 8)], [R_coin("sprocket", 3)],
      deps=["deployeur"],
      desc=D(["Une chaîne de déployeurs et de presses construit pièce par pièce. Maintenez W sur une machine pour son tutoriel."],
             ["A chain of deployers and presses builds it piece by piece. Hold W over a machine for its tutorial."]))
quest(c4, "crafter", ("L'assembleur mécanique", "The Mechanical Crafter"), 8, 2, [T_item("create:mechanical_crafter", 9)], [R_xp(300)],
      deps=["deployeur"])
quest(c4, "broyage", ("La ligne de minerai", "The Ore Line"), 10, 2,
      [T_item("create:crushing_wheel", 2), T_item("create:crushed_raw_iron", 64)], [R_coin("sprocket", 2), R_xp(300)],
      deps=["crafter"],
      desc=D(["Les roues de broyage se fabriquent à l'assembleur mécanique. Roues → lavage au ventilateur → fonte : de l'expérience et des sous-produits en plus (de la redstone avec le fer).",
              "&8Broyez des blocs de minerai minés avec Toucher de soie : près de deux fois plus de métal.&r"],
             ["Crushing wheels are made in the mechanical crafter. Wheels → fan washing → smelting: extra experience and by-products (redstone from iron).",
              "&8Crush ore blocks mined with Silk Touch: nearly twice the metal.&r"]))
quest(c4, "bras", ("Le bras mécanique", "The Mechanical Arm"), 10, 0, [T_item("create:mechanical_arm")], [R_xp(300)], deps=["precision"])
quest(c4, "q_laiton", ("Fonderie de laiton", "Brass Foundry"), 6, -4, [T_item("create:brass_ingot", 500)], [R_coin("cog", 2)], deps=["boitier_laiton"])
quest(c4, "table_empire", ("La bibliothèque impériale", "The Imperial Library"), 8, -4,
      [T_item("airain:imperial_enchanting_table"), T_item("minecraft:chiseled_bookshelf", 4)], [R_item("minecraft:book", 8), R_xp(300)],
      deps=["precision"], optional=True,
      subtitle=("Quête secondaire : enchanter sur mesure", "Side quest: enchanting to order"),
      desc=D(["&7Optionnel.&r La vieille table d'enchantement ne répond plus. Celle de l'Empire ne devine rien : elle lit.",
              "Rangez des &6livres enchantés&r dans des &6bibliothèques sculptées&r à moins de 3 blocs : la table propose ces enchantements, et vous choisissez le niveau, sans dépasser celui du livre. Les livres restent en place.",
              "Coût : de l'expérience (3 niveaux par niveau, plus selon la rareté, 30 au plus) et un lapis par niveau.",
              "&6Tomes anciens&r : rangé à côté d'un livre du même enchantement, un tome ancien ouvre le niveau suivant celui du livre (bouton doré), même au-delà du maximum. Le tome reste en place, mais appliquer ce niveau consomme une &6encre runique&r (troisième case). Un seul tome compte par enchantement. Au-delà du maximum, le coût passe à 40 niveaux et au double de lapis.",
              "&8Encre runique : au mélangeur chauffé, un éclat d'écho, un fragment de résonance, 4 lapis et 1 000 mB d'eau (un seau) donnent 2 encres.&r"],
             ["&7Optional.&r The old enchanting table no longer answers. The Empire's one guesses nothing: it reads.",
              "Shelve &6enchanted books&r in &6chiseled bookshelves&r within 3 blocks: the table offers those enchantments, and you pick the level, up to the book's. The books stay put.",
              "Cost: experience (3 levels per level, more for rarer ones, 30 at most) and one lapis per level.",
              "&6Ancient tomes&r: shelved next to a book of the same enchantment, an ancient tome unlocks the level after the book's (gold button), even beyond the maximum. The tome stays put, but applying that level consumes one &6rune ink&r (third slot). Only one tome counts per enchantment. Beyond the maximum, the cost rises to 40 levels and double lapis.",
              "&8Rune ink: in a heated mixer, an echo shard, a resonance fragment, 4 lapis and 1,000 mB of water (one bucket) make 2 inks.&r"]))
quest(c4, "desenchanteur", ("Le désenchanteur", "The Disenchanter"), 10, -4,
      [T_item("airain:disenchanter")], [R_item("kubejs:huile_machine", 8), R_item("minecraft:book", 4), R_xp(300)],
      deps=["table_empire"], optional=True,
      subtitle=("Quête secondaire : remplir la bibliothèque", "Side quest: filling the library"),
      desc=D(["&7Optionnel.&r Plus de marchands pour vendre des livres : il faut les arracher aux objets.",
              "Le désenchanteur détruit un objet enchanté et en tire &cun seul&r enchantement, au hasard, dans un livre vierge. Monté comme la meule à farine, il tourne au rouage et brûle 500 mB d'huile par niveau.",
              "&8Clic droit avec l'objet, puis avec des livres ; main vide pour reprendre le livre enchanté. Entonnoirs et tapis fonctionnent aussi. Les lunettes d'ingénieur montrent l'opération en cours.&r"],
             ["&7Optional.&r No more merchants to sell books: you have to tear them out of items.",
              "The disenchanter destroys an enchanted item and pulls &conly one&r enchantment out of it, at random, into a blank book. Built like the millstone, it runs on a cogwheel and burns 500 mB of oil per level.",
              "&8Right-click with the item, then with books; empty-handed to take the enchanted book. Funnels and belts work too. Engineer's goggles show the current operation.&r"]))
quest(c4, "purge", ("La purge", "The Purge"), 12, -4, [T_item("airain:runic_ink"), T_check()], [R_coin("cog", 1), R_xp(300)],
      deps=["desenchanteur"], optional=True,
      desc=D(["&7Optionnel.&r Certaines armes trouvées dans les ruines portent une malédiction. L'Empire savait la défaire sans briser l'objet.",
              "Donnez de l'&6encre runique&r au désenchanteur (clic droit). Un objet maudit qu'on lui confie n'est alors plus détruit : il perd &6une malédiction par passage&r, contre une encre et 500 mB d'huile, puis ressort avec ses autres enchantements intacts.",
              "&8Sans encre, un objet maudit est désenchanté comme les autres. Encre runique : au mélangeur chauffé, un éclat d'écho, un fragment de résonance, 4 lapis et un seau d'eau donnent 2 encres.&r"],
             ["&7Optional.&r Some weapons found in the ruins carry a curse. The Empire knew how to undo it without breaking the item.",
              "Give &6rune ink&r to the disenchanter (right-click). A cursed item fed to it is then no longer destroyed: it loses &6one curse per pass&r, for one ink and 500 mB of oil, and comes out with its other enchantments intact.",
              "&8Without ink, a cursed item is disenchanted like any other. Rune ink: in a heated mixer, an echo shard, a resonance fragment, 4 lapis and a bucket of water make 2 inks.&r"]))
titres_taches("purge", [None, ("Purger un objet maudit", "Purge a cursed item")])
quest(c4, "banc_modules", ("Les modules du banc", "Bench Modules"), 4, -4,
      [T_item("airain:fine_grindstone"), T_item("airain:reduction_gear"), T_item("airain:grease_gun")],
      [R_item("kubejs:huile_machine", 8), R_coin("sprocket", 3)], deps=["banc", "boitier_laiton"], optional=True,
      desc=D(["&7Optionnel.&r Avec le laiton, le banc d'entretien peut enfin être réglé comme ceux des ateliers de la capitale.",
              "Trois modules, à poser dans les emplacements à droite de son écran (un exemplaire de chaque compte) :",
              "• &6Meule fine&r : 30 % d'huile en moins par réparation ;",
              "• &6Démultiplicateur&r : 60 % plus rapide, mais demande deux fois plus de stress ;",
              "• &6Graisseur&r : pompe l'huile d'un réservoir voisin, 250 mB par seconde. Plus besoin de burettes.",
              "&8Les modules se voient sur le banc, et les lunettes d'ingénieur les listent.&r"],
             ["&7Optional.&r With brass, the maintenance bench can finally be tuned like the ones in the capital's workshops.",
              "Three modules, placed in the slots on the right of its screen (one of each counts):",
              "• &6Fine Grindstone&r: 30% less oil per repair;",
              "• &6Reduction Gear&r: 60% faster, but needs twice the stress;",
              "• &6Greaser&r: pumps oil from a neighbouring tank, 250 mB per second. No more oil cans.",
              "&8Modules show on the bench, and engineer's goggles list them.&r"]))
quest(c4, "q_precision", ("Chaîne de précision", "Precision Line"), 10, -2, [T_item("create:precision_mechanism", 64)], [R_coin("cog", 2)],
      deps=["precision"])
quest(c4, "bastion", ("Le bastion", "The Bastion"), 2, 4, [T_struct("minecraft:bastion_remnant")], [R_item("minecraft:netherite_upgrade_smithing_template")],
      deps=["nether"],
      desc=D(["Les bastions cachent les gabarits d'amélioration en netherite."], ["Bastions hide the netherite upgrade templates."]))
quest(c4, "netherite", ("Plaques de netherite", "Netherite Plates"), 12, -2, [T_item("kubejs:plaque_netherite", 4)], [R_xp(500)],
      deps=["q_precision"],
      desc=D(["Lingot de netherite → déployeur (mécanisme de précision) → presse. Ces plaques remplacent le lingot à la table de forgeron."],
             ["Netherite ingot → deployer (precision mechanism) → press. These plates replace the ingot at the smithing table."]))
quest(c4, "armure_netherite", ("L'armure de netherite", "Netherite Armor"), 14, -2,
      [T_item("minecraft:netherite_helmet"), T_item("minecraft:netherite_chestplate"), T_item("minecraft:netherite_leggings"), T_item("minecraft:netherite_boots")],
      [R_coin("cog", 2), R_xp(800)], deps=["netherite", "bastion"])
quest(c4, "rails", ("Poser les rails", "Laying Track"), 12, 2, [T_item("create:track", 128), T_item("create:railway_casing", 16)],
      [R_xp(300)], deps=["bras", "broyage"],
      desc=D(["Les rails se fabriquent par assemblage en séquence. Les ruines sont loin : reliez le monde."],
             ["Track is made by sequenced assembly. The ruins are far apart: connect the world."]))
quest(c4, "train", ("Le premier train", "The First Train"), 14, 2, [T_item("create:controls"), T_item("create:track_station", 2), T_check()],
      [R_coin("cog", 1)], deps=["rails"],
      desc=D(["Validez quand un train fait seul l'aller-retour entre deux gares."], ["Tick the box when a train runs a round trip between two stations on its own."]))
quest(c4, "reseau", ("Deux lignes", "Two Lines"), 16, 2, [T_item("create:track_signal", 4), T_check()], [R_coin("cog", 2)], deps=["train"],
      desc=D(["Un réseau d'au moins deux lignes, avec des signaux pour éviter les collisions."], ["A network of at least two lines, with signals to avoid collisions."]))
quest(c4, "waystones", ("Grand Chantier : le réseau des Waystones", "Great Work: The Waystone Network"), 16, 0,
      [T_item("create:brass_ingot", 64, consume=True), T_item("minecraft:ender_pearl", 16, consume=True)],
      [R_tag("airain_waystones"), R_coin("cog", 1)], deps=["bras"], shape="hexagon", size=1.5,
      subtitle=("Débloque la pose des Waystones", "Unlocks placing Waystones"),
      desc=D(["Remettez en marche le réseau de téléportation de l'Empire. Ensuite, vous pourrez poser vos propres Waystones."],
             ["Restart the Empire's teleport network. Then you can place your own Waystones."]))
quest(c4, "gare", ("Grand Chantier : la gare impériale", "Great Work: The Imperial Station"), 18, 2,
      [T_item("create:track", 256, consume=True), T_item("create:railway_casing", 64, consume=True)],
      [R_tag("airain_gare"), R_coin("cog", 2)], deps=["reseau"], shape="hexagon", size=1.5,
      subtitle=("Débloque les interfaces de stockage portables", "Unlocks portable storage interfaces"),
      desc=D(["Une gare digne de l'Empire. Elle débloque les interfaces portables, pour charger et décharger les trains."],
             ["A station worthy of the Empire. It unlocks portable interfaces to load and unload trains."]))
quest(c4, "capsules", ("La salle des capsules", "The Capsule Hall"), 12, 0, [T_check()], [R_item("minecraft:ender_pearl", 8)], deps=["bras"],
      desc=D(["Une salle immense. Des milliers de capsules de laiton, alignées. &lToutes vides.&r Des câbles en sortent, tous vers le bas."],
             ["A vast hall. Thousands of brass capsules, lined up. &lAll empty.&r Cables run out of them, all going down."],
             journal(["Le transfert a commencé. Nous entrons dans le métal un par un.", "Je serai le dernier."],
                     ["The transfer has begun. We enter the metal one by one.", "I will be the last."])))
quest(c4, "canons", ("Une batterie de canons", "A Cannon Battery"), 18, -2,
      [T_item("createbigcannons:cannon_mount", 4), T_item("createbigcannons:cast_iron_cannon_barrel", 8),
       T_item("createbigcannons:cast_iron_sliding_breech", 4), T_item("createbigcannons:powder_charge", 32)],
      [R_coin("cog", 2)], deps=["armure_netherite"],
      desc=D(["Quatre canons complets. Le fer devient de la fonte (presse sur bassin chauffé), la fonte fond dans un bassin chauffé et se coule dans un moule à canon, puis le fût se perce. Détails dans EMI."],
             ["Four complete cannons. Iron becomes cast iron (press over a heated basin), cast iron melts in a heated basin and is poured into a cannon cast, then the barrel is bored. Details in EMI."]))
quest(c4, "obus", ("Munitions", "Ammunition"), 20, -2, [T_item("createbigcannons:solid_shot", 32), T_item("createbigcannons:he_shell", 16)],
      [R_coin("cog", 1)], deps=["canons"])
# l'appel de l'Écho : la magie entre dans l'histoire principale
quest(c4, "l_refractaires", ("Ceux qui ont dit non", "Those Who Said No"), 16, 4, [T_struct("kubejs:avant_poste_refractaire"), lire()],
      [R_coin("bevel", 4)], deps=["nether"], subtitle=("L'appel de l'Écho", "The Call of the Echo"),
      desc=D(["Tous n'ont pas voulu du Transfert. Ils ont vu revenir les capsules vides, et ils sont partis la nuit même. Leurs camps tiennent encore, quelque part.",
              "Trouvez un camp réfractaire et lisez l'un de leurs écrits (dans leurs coffres). Validez quand c'est fait."],
             ["Not everyone wanted the Transfer. They saw the capsules come back empty, and they left that very night. Their camps still stand, somewhere.",
              "Find a Refractory camp and read one of their writings (in their chests). Tick when done."]))
quest(c4, "a_ars_source", ("Un froid dans l'améthyste", "A Chill in the Amethyst"), 18, 4,
      [T_item("ars_nouveau:imbuement_chamber"), T_item("ars_nouveau:source_gem", 4)], [R_coin("sprocket", 2), R_carnet(1)],
      deps=["l_refractaires"], subtitle=("L'appel de l'Écho", "The Call of the Echo"),
      desc=D(["Près des cristaux, l'air se refroidit, comme si quelqu'un passait. Les Réfractaires avaient appris à retenir ce froid dans l'améthyste. Ils l'appelaient l'&dÉcho&r.",
              "La chambre d'imprégnation fixe l'Écho dans l'améthyste : des gemmes de source. Consultez sa recette dans EMI.",
              "&8Récompense : la première page du carnet d'une apprentie réfractaire.&r"],
             ["Near the crystals the air turns cold, as if someone were passing by. The Refractories had learned to hold that chill in amethyst. They called it the &dEcho&r.",
              "The imbuement chamber binds the Echo into amethyst: source gems. Check its recipe in EMI.",
              "&8Reward: the first page of a Refractory apprentice's notebook.&r"]))
quest(c4, "a_ars_livre", ("Une volonté confiée", "An Entrusted Will"), 20, 4,
      [T_item("ars_nouveau:novice_spell_book"), T_item("ars_nouveau:glyph_light")], [R_coin("sprocket", 3)],
      deps=["a_ars_source"], subtitle=("L'appel de l'Écho", "The Call of the Echo"),
      desc=D(["Un sort, c'est une volonté qu'on confie à l'Écho. Commencez petit : de la lumière dans la mine, une roche qui cède. Les égarés aiment se rendre utiles.",
              "Un grimoire de novice et le glyphe de lumière. Ouvre le chapitre &dLes Arcanes&r, la seconde voie de l'histoire."],
             ["A spell is a will entrusted to the Echo. Start small: light in the mine, a rock that gives way. The lost like to be useful.",
              "A novice spell book and the light glyph. Opens the &dThe Arcana&r chapter, the story's second path."]))
quest(c4, "prepa4", ("Préparatifs infernaux", "Infernal Preparations"), 20, 0,
      [T_item("minecraft:potion", 4), T_item("minecraft:golden_apple", 2)], [R_coin("sprocket", 2)], deps=["obus", "a_ars_livre"],
      desc=D(["Des potions (résistance au feu conseillée) et des pommes dorées : la monstruosité frappe fort."],
             ["Potions (fire resistance recommended) and golden apples: the monstrosity hits hard."]))
# ---- gardiens et modules de garnison
quest(c4, "gardien_debout", ("Un gardien sur pied", "A Guardian on Its Feet"), 6, 4, [T_stage("airain_gardien_repare")],
      [R_item("kubejs:huile_machine", 4)], icon="airain:guardian_spawn_egg",
      desc=D(["Dans les ruines de l'Empire, des &6gardiens d'airain&r attendent, assis, couverts de mousse.",
              "Clé de Create en main, avec &616 ferrailles, 4 huiles et 2 rouages brisés&r sur vous : clic droit, et il se relève. Il garde la fondation la plus proche (4 par base).",
              "&8Le livre de l'ingénieur a tout le détail.&r"],
             ["In the Empire's ruins, &6brass guardians&r wait, seated, covered in moss.",
              "Create wrench in hand, with &616 scrap, 4 oils and 2 broken cogs&r on you: right-click, and it stands up. It guards the nearest foundation (4 per base).",
              "&8The engineer's book has all the details.&r"]))
quest(c4, "garnison", ("Les ateliers de garnison", "The Garrison Workshops"), 8, 4, [T_stage("airain_module_monte")],
      [R_xp(500), R_item("create:precision_mechanism", 2)], deps=["gardien_debout", "crafter"], icon="airain:lantern_module",
      desc=D(["Les ateliers de l'Empire équipaient leurs gardiens selon la garnison : lanternes pour les mines, canons pour les remparts, chaudières pour les postes isolés.",
              "Trois emplacements, un module chacun :",
              "&6Tête&r : tête-lanterne (lumière, monstres en surbrillance) ou longue-vue (dégâts, voit les invisibles).",
              "&6Épaules&r : canon d'épaule ou bobine Tesla.",
              "&6Torse&r : blindage riveté ou chaudière de secours (il se relève au lieu d'être détruit).",
              "Ils se fabriquent à l'&6assembleur mécanique&r. Clic droit sur un gardien en marche pour en monter un ; accroupi, main vide, pour tout démonter.",
              "&8La bobine et la chaudière demandent un fragment de résonance.&r"],
             ["The Empire's workshops fitted their guardians to the garrison: lanterns for the mines, cannons for the ramparts, boilers for remote posts.",
              "Three slots, one module each:",
              "&6Head&r: lantern head (light, glowing monsters) or spyglass lens (damage, sees the invisible).",
              "&6Shoulders&r: shoulder cannon or Tesla coil.",
              "&6Torso&r: riveted plating or emergency boiler (it gets back up instead of being destroyed).",
              "They are made at the &6mechanical crafter&r. Right-click a working guardian to mount one; sneak with an empty hand to remove them all.",
              "&8The coil and the boiler need a resonance fragment.&r"]))
quest(c4, "netherite_sacree", ("La netherite sacrée", "Sacred Netherite"), 10, 4, [T_item("airain:sacred_netherite_plate")],
      [R_xp(800)], deps=["garnison", "netherite"],
      desc=D(["Une plaque de netherite, et au centre, serti dans l'or, le cœur d'un Gardien des enfers.",
              "Posez la plaque sur un dépôt ou un tapis, et faites-y enfoncer le &6Cœur du Gardien des enfers&r par un &6déployeur&r."],
             ["A netherite plate and, set in gold at its centre, the core of an Infernal Guardian.",
              "Put the plate on a depot or a belt, and have a &6deployer&r press the &6Infernal Guardian Core&r into it."]))
quest(c4, "gardien_elite", ("Un gardien d'élite", "An Elite Guardian"), 12, 4, [T_stage("airain_module_2")],
      [R_coin("cog", 2), R_xp(1000)], deps=["netherite_sacree"], icon="airain:cannon_module_2",
      desc=D(["À la &6table de forgeron&r : un modèle d'amélioration en netherite, un module, une plaque sacrée. Le laiton noircit, l'or remonte dans les rivets, et tout ce que fait le module est doublé.",
              "Montez un module de niveau II sur un de vos gardiens."],
             ["At the &6smithing table&r: a netherite upgrade template, a module, a sacred plate. The brass blackens, gold rises in the rivets, and everything the module does is doubled.",
              "Mount a level II module on one of your guardians."]))

quest(c4, "forge_ames", ("La forge des âmes", "The Soul Forge"), 22, 0, [T_kill("cataclysm:netherite_monstrosity")],
      [R_item("kubejs:schema_ciel"), R_item("kubejs:fragment_forge"), R_tag("airain_end"), R_coin("crown", 1), R_xp(2000)],
      deps=["prepa4"], shape="hexagon", size=1.75,
      subtitle=("Schéma du Ciel, ouverture de l'End", "Sky Schematic, the End opens"),
      desc=D(["Au fond d'une forge des âmes dort une &cmonstruosité de netherite&r. Bombardez-la, puis finissez le travail.",
              "", "&eRécompenses :&r le &6Schéma du Ciel&r (assembleur physique, roulement d'hélice), et l'&5End&r s'ouvre pour vous."],
             ["Deep in a soul forge sleeps a &cNetherite Monstrosity&r. Bombard it, then finish the job.",
              "", "&eRewards:&r the &6Sky Schematic&r (physics assembler, propeller bearing), and the &5End&r opens for you."]))

# =============================================================================
# V · L'ÂGE DU CIEL
# =============================================================================
c5 = chapter("ciel", "05_age_ciel", ("&6V&r · L'Âge du Ciel", "&6V&r · The Sky Age"),
             ("L'Empire avait des cités volantes.", "The Empire had flying cities."), "minecraft:elytra", 5)

quest(c5, "assembleur", ("L'assembleur physique", "The Physics Assembler"), 0, 0, [T_item("simulated:physics_assembler")], [R_xp(300)],
      deps=["forge_ames"],
      desc=D(["Avec le Schéma du Ciel. Il transforme une construction en véhicule qui obéit à la physique."],
             ["With the Sky Schematic. It turns a build into a vehicle that follows physics."]))
quest(c5, "helices", ("Hélices", "Propellers"), 2, -2, [T_item("aeronautics:propeller_bearing", 2), T_item("aeronautics:andesite_propeller", 2)],
      [R_xp(300)], deps=["assembleur"])
quest(c5, "ballon", ("Le ballon", "The Balloon"), 2, 2, [T_item("aeronautics:white_envelope", 64), T_item("aeronautics:adjustable_burner")],
      [R_xp(300)], deps=["assembleur"],
      desc=D(["Des enveloppes au-dessus d'un brûleur à air chaud : la portance."], ["Envelopes above a hot air burner: lift."]))
quest(c5, "envol", ("Premier envol", "First Flight"), 4, 0, [T_check()], [R_coin("cog", 2), R_xp(500)], deps=["helices", "ballon"],
      desc=D(["Faites décoller votre premier engin et volez au-dessus des nuages."], ["Take off in your first craft and fly above the clouds."]))
quest(c5, "q_enveloppes", ("Chantier de toile", "Canvas Yard"), 4, 2, [T_item("aeronautics:white_envelope", 256)], [R_coin("cog", 1)], deps=["ballon"])
quest(c5, "navire", ("Le navire de guerre", "The Warship"), 6, 0, [T_item("createbigcannons:cannon_mount", 2), T_check()], [R_coin("cog", 3)],
      deps=["envol"],
      desc=D(["Montez au moins deux canons sur votre engin volant. Le ciel n'est pas vide."], ["Mount at least two cannons on your flying craft. The sky is not empty."]))
quest(c5, "station", ("La station d'observation", "The Observation Station"), 4, -2, [T_struct("kubejs:station_observation")],
      [R_coin("cog", 1), R_item("minecraft:spyglass")], deps=["envol"],
      desc=D(["Haut dans le ciel, au-dessus des plaines, une île flotte avec une coupole de cuivre. L'Empire y observait les étoiles.",
              "Le pupitre garde les relevés de l'ingénieur en chef Octave Lanfrey. &8Il faut voler pour l'atteindre : vers la hauteur 170.&r"],
             ["High in the sky above the plains, an island floats with a copper dome. The Empire watched the stars from there.",
              "The lectern keeps the readings of Engineer-in-Chief Octave Lanfrey. &8You need to fly to reach it: around height 170.&r"]))
quest(c5, "naval", ("Grand Chantier : le chantier naval", "Great Work: The Shipyard"), 6, -2,
      [T_item("create:brass_casing", 64, consume=True), T_item("aeronautics:white_envelope", 128, consume=True)],
      [R_item("kubejs:schema_ciel"), R_coin("cog", 1)], deps=["envol"], shape="hexagon", size=1.5,
      subtitle=("Un second Schéma du Ciel", "A second Sky Schematic"),
      desc=D(["Un second Schéma du Ciel, pour que chacun puisse construire de son côté."], ["A second Sky Schematic, so each of you can build on your own."]))
quest(c5, "end", ("Au-delà du portail", "Beyond the Portal"), 8, 0, [T_dim("minecraft:the_end")], [R_xp(300)], deps=["navire"])
quest(c5, "dragon", ("Le Gardien des Cieux", "The Sky Guardian"), 10, 0, [T_kill("minecraft:ender_dragon")], [R_coin("crown", 1), R_xp(1500)],
      deps=["end"],
      desc=D(["Ce n'est pas une bête de l'End. &dMorgana Dalmont&r l'a appelée de ses mains, pour garder les portes des siens.",
              "Ses pages se trouvent encore dans les cités de l'End."],
             ["It is no beast of the End. &dMorgana Dalmont&r called it with her own hands, to guard her people's gates.",
              "Her pages can still be found in the End cities."]))
quest(c5, "cites", ("Les cités volantes", "The Floating Cities"), 12, 0, [T_struct("minecraft:end_city"), T_item("minecraft:elytra")],
      [R_item("minecraft:shulker_box", 2)], deps=["dragon"],
      desc=D(["Des tours suspendues dans le vide. L'architecture rappelle étrangement celle de l'Empire."],
             ["Towers hanging over the void. The architecture is strangely like the Empire's."]))
quest(c5, "jetpack", ("Le jetpack", "The Jetpack"), 14, -2, [T_item("create_jetpack:jetpack")], [R_xp(800)], deps=["cites"],
      desc=D(["Votre réservoir d'air dorsal, des élytres et du laiton, assemblés à l'assembleur mécanique."],
             ["Your backtank, elytra and brass, assembled in the mechanical crafter."]))
quest(c5, "atelier_ench", ("Grand Chantier : l'atelier d'enchantement", "Great Work: The Enchanting Workshop"), 8, 2,
      [T_item("minecraft:book", 64, consume=True), T_item("minecraft:lapis_lazuli", 64, consume=True), T_xp(30)],
      [R_tag("airain_atelier"), R_coin("cog", 2)], deps=["envol"], shape="hexagon", size=1.5,
      subtitle=("Débloque les machines d'enchantement", "Unlocks the enchanting machines"),
      desc=D(["Rouvrez l'atelier : vous pourrez poser l'enchanteur à blaze, la forge à blaze et l'imprimante d'Enchantment Industry."],
             ["Reopen the workshop: you can then place Enchantment Industry's blaze enchanter, blaze forger and printer."]))
quest(c5, "mage", ("Robes d'Écho", "Echo Robes"), 10, 2, [T_check()], [R_xp(500)],
      deps=["atelier_ench"], optional=True,
      desc=D(["&7Optionnel.&r Pour celui de l'équipe qui suit la voie de l'Écho : une pièce d'armure d'Ars Nouveau (sorcier, arcaniste ou mage de bataille). Validez quand elle est portée."],
             ["&7Optional.&r For the one on the team who follows the Echo path: a piece of Ars Nouveau armor (sorcerer, arcanist or battlemage). Tick the box once it is worn."]))
quest(c5, "prepa5", ("Préparatifs célestes", "Celestial Preparations"), 14, 2, [T_item("minecraft:ender_pearl", 32), T_item("minecraft:potion", 4)],
      [R_coin("sprocket", 3)], deps=["cites"],
      desc=D(["Perles et potions (chute lente conseillée) pour la citadelle."], ["Pearls and potions (slow falling recommended) for the citadel."]))
quest(c5, "l_relais", ("La ligne rompue", "The Broken Line"), 16, 2, [T_struct("kubejs:relais_brise"), lire()],
      [R_coin("sprocket", 1), R_item("kubejs:fragment_resonance", 2)], deps=["l_refractaires"], subtitle=("L'appel de l'Écho", "The Call of the Echo"),
      desc=D(["Le cycle 212, la ligne a cédé en pleine charge. Une partie du flux n'est jamais arrivée au Cœur. L'Empire a interdit le mot. Les cristaux, eux, ont continué de pousser.",
              "Trouvez un relais brisé et lisez le rapport d'incident sur le pupitre. C'est là que l'Écho s'est échappé."],
             ["On cycle 212 the line gave way under full load. Part of the flow never reached the Heart. The Empire banned the word. The crystals kept growing anyway.",
              "Find a broken relay and read the incident report on the lectern. This is where the Echo escaped."]))
quest(c5, "bientot", ("Bientôt", "Soon"), 16, 0, [T_check()], [R_item("minecraft:totem_of_undying")], deps=["prepa5", "jetpack", "l_relais"],
      desc=D(["Partout où vous passez, des machines s'allument seules. Des engrenages tournent sans force."],
             ["Wherever you go, machines switch on by themselves. Gears turn with no power."],
             journal(["Il a répondu. Il sait que quelqu'un vient."], ["It answered. It knows someone is coming."])))
quest(c5, "citadelle", ("La citadelle en ruine", "The Ruined Citadel"), 18, 0, [T_kill("cataclysm:ender_guardian")],
      [R_item("kubejs:fragment_vide"), R_coin("crown", 2), R_xp(3000)], deps=["bientot"], shape="hexagon", size=1.75,
      subtitle=("Le dernier fragment", "The last fragment"),
      desc=D(["Au troisième étage d'une citadelle en ruine de l'End, l'&5autel du vide&r. Approchez et le gardien s'éveille.",
              "&8Il ne meurt pas en hurlant. Il murmure : « Bientôt. »&r"],
             ["On the third floor of a ruined citadel in the End stands the &5Altar of Void&r. Approach and the guardian awakens.",
              "&8It does not die screaming. It whispers: \"Soon.\"&r"]))

# =============================================================================
# VI · LE CŒUR D'AIRAIN
# =============================================================================
c6 = chapter("coeur", "06_coeur_airain", ("&6VI&r · Le Cœur d'Airain", "&6VI&r · Airain's Core"),
             ("Rassembler les mémoires. Rallumer le Cœur.", "Gather the memories. Rekindle the Core."), "kubejs:coeur_d_airain", 6)

quest(c6, "crafters21", ("La grille d'assemblage", "The Assembly Grid"), 0, 0, [T_item("create:mechanical_crafter", 21)], [R_xp(500)],
      deps=["citadelle"],
      desc=D(["Le Cœur se forge sur une grille 5 × 5 d'assembleurs : il en faut 21. Reliez-les à la clé."],
             ["The Core is forged on a 5 × 5 grid of crafters: you need 21. Connect them with the wrench."]))
quest(c6, "salle", ("La Salle du Cœur", "The Core Chamber"), 2, -2, [T_check()], [R_coin("cog", 2)], deps=["crafters21"],
      desc=D(["Construisez une salle d'au moins 9 × 9 avec la grille au centre. L'Empire mérite un écrin."],
             ["Build a hall of at least 9 × 9 with the grid at its center. The Empire deserves a proper setting."]))
quest(c6, "mat_coeur", ("Les matériaux du Cœur", "Core Materials"), 2, 2,
      [T_item("create:precision_mechanism", 32), T_item("create:brass_casing", 64)], [R_coin("cog", 1)], deps=["crafters21"])
quest(c6, "mer", ("Le cœur de la mer", "Heart of the Sea"), 4, 2, [T_item("minecraft:heart_of_the_sea")], [R_xp(300)], deps=["mat_coeur"],
      desc=D(["Dans les trésors enfouis (cartes au trésor des épaves), ou à la boutique."], ["In buried treasure (shipwreck treasure maps), or at the shop."]))
quest(c6, "memoires", ("Les quatre mémoires", "The Four Memories"), 4, -2,
      [T_item("kubejs:fragment_rouages"), T_item("kubejs:fragment_marees"), T_item("kubejs:fragment_forge"), T_item("kubejs:fragment_vide"), T_item("kubejs:coeur_brise")],
      [R_xp(500)], deps=["salle"],
      desc=D(["Côte à côte, les fragments se répondent. Leurs inscriptions forment une seule phrase :", "&o« Rendez-nous notre Cœur. »&r",
              "Au milieu d'eux, le &6Cœur brisé&r que le gardien du Vide a laissé en tombant : le premier Cœur, celui que Morgana avait volé. Il n'en existe qu'un seul."],
             ["Side by side, the fragments answer each other. Their inscriptions form a single sentence:", "&o\"Give us back our Core.\"&r",
              "Among them, the &6Broken Core&r the Void guardian left as it fell: the first Core, the one Morgana stole. There is only one."]))
quest(c6, "l_sanctuaire", ("Le journal d'Ada", "Ada's Journal"), 4, 4, [T_struct("kubejs:sanctuaire_refractaire"), lire()],
      [R_coin("cog", 1), R_cmd_visible("locate structure kubejs:grand_relais")], deps=["l_relais"],
      subtitle=("L'appel de l'Écho", "The Call of the Echo"),
      desc=D(["Elle a signé les plans des capsules. Puis elle a pris ceux qui voulaient vivre, et elle est partie vers le nord. Avant de rallumer quoi que ce soit, lisez ce qu'elle a laissé.",
              "Quelque part dans le nord froid, le sanctuaire réfractaire garde le journal d'&dAda Vesper&r. Lisez-le jusqu'au bout : la récompense indique où se trouve le Grand Relais."],
             ["She signed the capsule blueprints. Then she took those who wanted to live, and went north. Before you rekindle anything, read what she left behind.",
              "Somewhere in the cold north, the Refractory sanctuary keeps &dAda Vesper&r's journal. Read it to the end: the reward tells you where the Great Relay is."]))
quest(c6, "forger", ("Forger le Cœur", "Forge the Core"), 6, 0, [T_item("kubejs:coeur_d_airain")], [R_xp(2000)], deps=["memoires", "mer", "l_sanctuaire"],
      shape="gear", size=1.75,
      desc=D(["Consultez la recette dans EMI, catégorie assembleur mécanique.", "Le Cœur est fait d'airain : il demande des blocs et des engrenages d'airain (annexe « La fonderie impériale »)."],
             ["Check the recipe in EMI, mechanical crafting category.", "The Core is made of airain: it needs airain blocks and gears (side chapter \"The Imperial Foundry\")."]))
quest(c6, "reactiver", ("Réactiver le Cœur", "Reawaken the Core"), 8, 0, [T_check()],
      [R_cmd_visible("locate structure cataclysm:ancient_factory"), R_item("minecraft:nether_star"), R_coin("crown", 2), R_tag("airain_coeur_reveille")],
      deps=["forger"], shape="hexagon", size=2.0, subtitle=("&cLe retournement&r", "&cThe twist&r"),
      desc=D(["Vous tenez le Cœur à deux mains. Il bat. Il chauffe. Et très loin sous vos pieds, quelque chose répond.",
              "", "Le carnet s'ouvre tout seul à une page restée blanche. Des lettres s'y gravent, comme brûlées de l'intérieur :",
              "", "&6&o« Merci.", "Ces pages, ces gardiens, ces schémas : c'est nous qui les avons placés sur votre route.",
              "Il nous fallait des mains vivantes pour rallumer le Cœur.", "Nous n'avons jamais disparu. Nous attendions dans le métal.",
              "Maintenant, nous revenons. Et ce monde redevient le nôtre. »&r",
              "", "En dessous, d'une autre main, plus petite, à l'encre ordinaire :",
              "&7&o« Ne les crois pas. Ils ne dorment pas : ils brûlent. Je vous ai gardés à part pour ce jour-là. Quand tout sera fini, c'est vous qui choisirez. — O. L. »&r",
              "", "&cL'Empire d'Airain se réveille.&r"],
             ["You hold the Core in both hands. It pulses. It grows warm. And far beneath your feet, something answers.",
              "", "The journal opens by itself to a page that had stayed blank. Letters carve themselves into it, as if burned from within:",
              "", "&6&o\"Thank you.", "These pages, these guardians, these schematics: we placed them on your path.",
              "We needed living hands to rekindle the Core.", "We never vanished. We were waiting in the metal.",
              "Now we return. And this world becomes ours again.\"&r",
              "", "Below, in another hand, smaller, in ordinary ink:",
              "&7&o\"Do not believe them. They are not sleeping: they are burning. I kept you apart for this day. When it is all over, you will be the ones to choose. — O. L.\"&r",
              "", "&cThe Airain Empire awakens.&r"]))
quest(c6, "siege", ("Préparer le siège", "Prepare for the Siege"), 10, -1,
      [T_item("createbigcannons:solid_shot", 128), T_item("createbigcannons:he_shell", 64)], [R_coin("cog", 2)], deps=["reactiver"])
quest(c6, "soins", ("La réserve de soins", "The Healing Stock"), 10, 1, [T_item("minecraft:potion", 16), T_item("minecraft:golden_apple", 8)],
      [R_coin("cog", 1)], deps=["reactiver"],
      desc=D(["Des potions de soin, de force, de résistance au feu. L'Empire ne fera pas de quartier."],
             ["Healing, strength and fire resistance potions. The Empire will show no mercy."]))
quest(c6, "remparts", ("Renforcer la base", "Fortify the Base"), 12, 0, [T_item("createbigcannons:cannon_mount", 3), T_check()],
      [R_coin("cog", 2)], deps=["siege", "soins"],
      desc=D(["Trois affûts de canon autour de la base. Validez quand ils sont en place."], ["Three cannon mounts around the base. Tick the box when they are in place."]))

# =============================================================================
# VII · LA RECONQUÊTE
# =============================================================================
c7 = chapter("reconquete", "07_reconquete", ("&4VII&r · La Reconquête", "&4VII&r · The Reconquest"),
             ("L'Empire est revenu. Il veut son monde.", "The Empire is back. It wants its world."), "minecraft:nether_star", 7)

quest(c7, "eveil", ("L'Empire s'éveille", "The Empire Awakens"), 0, 0, [T_check()], [R_item("airain:defense_beacon"), R_xp(500)], deps=["remparts"],
      desc=D(["Les ruines ne dorment plus. Vous avez rendu son Cœur à l'Empire. À vous de l'arrêter.",
              "", "&eRécompense :&r la &cBalise de défense&r, une tour-phare à sirène. Posez-la dans votre base (3 × 3 blocs au sol, 8 de haut) : c'est vous qui choisissez quand l'Empire attaque. Pendant l'assaut, sa sirène hurle et son phare balaie la base.",
              "&8Chaque joueur réclame sa propre balise.&r",
              "", "&cDésormais, des patrouilles d'automates viennent à votre rencontre en surface, et certaines tombent du ciel.&r Elles cessent quand l'Empereur tombe."],
             ["The ruins no longer sleep. You gave the Empire back its Core. Now you must stop it.",
              "", "&eReward:&r the &cDefense Beacon&r, a siren lighthouse tower. Place it in your base (3 × 3 blocks of ground, 8 high): you choose when the Empire attacks. During the assault, its siren wails and its light sweeps the base.",
              "&8Each player claims their own beacon.&r",
              "", "&cFrom now on, automaton patrols come for you on the surface, and some drop from the sky.&r They stop when the Emperor falls."]))
quest(c7, "assaut", ("Tenir la position", "Hold the Line"), 0, -2, [T_stage("airain_assaut")], [R_coin("cog", 3), R_xp(1000)], deps=["eveil"],
      desc=D(["Posez la balise de défense dans votre base et repoussez un assaut complet de l'Empire : quatre vagues, la dernière menée par un centurion à vapeur.",
              "", "&eClic droit&r sur la balise : l'assaut commence après un compte à rebours.",
              "&eAccroupi + clic droit&r (balise au repos) : règle le rayon d'arrivée (48, 64, 96 ou 128 blocs) et montre le cercle rouge où ils apparaîtront. Placez-le au-delà de vos murailles.",
              "Les ennemis n'apparaissent que sur du sol naturel à ciel ouvert : jamais sur vos sols, toits ou chemins.",
              "Entre deux vagues, 30 secondes de répit. Si vous tombez tous les deux, seule la vague en cours recommence à votre retour.",
              "", "La balise ne s'use jamais. Chaque assaut repoussé rapporte des engrenages et un objet rare, et le suivant sera un peu plus fort."],
             ["Place the defense beacon in your base and repel a full Empire assault: four waves, the last one led by a steam centurion.",
              "", "&eRight-click&r the beacon: the assault starts after a countdown.",
              "&eSneak + right-click&r (beacon idle): sets the arrival radius (48, 64, 96 or 128 blocks) and shows the red circle where they will appear. Put it beyond your walls.",
              "Enemies only appear on natural ground under open sky: never on your floors, roofs or paths.",
              "Between waves, 30 seconds of respite. If you both fall, only the current wave starts again when you come back.",
              "", "The beacon never wears out. Every assault repelled pays cogs and a rare item, and the next one will be a little stronger."]))
quest(c7, "vague1", ("Première vague", "First Wave"), 2, -2, [T_kill("mebahelcreaturesdwarven:dwarven_spider", 20)],
      [R_coin("cog", 2)], deps=["eveil"],
      desc=D(["Les vieilles usines de bronze de l'Empire se sont rallumées. Leurs araignées mécaniques patrouillent de nouveau.",
              "Abattez-en vingt (le compteur avance à chaque machine détruite)."],
             ["The Empire's old bronze works have lit up again. Their mechanical spiders are back on patrol.",
              "Destroy twenty of them (the counter goes up with each machine destroyed)."]))
quest(c7, "vague2", ("Deuxième vague", "Second Wave"), 4, -2, [T_kill("mebahelcreaturesdwarven:dwarven_sphere", 12)],
      [R_coin("cog", 3)], deps=["vague1"],
      desc=D(["Repliées, elles roulent comme des boulets. Déployées, ce sont des soldats. Détruisez douze sphères."],
             ["Folded, they roll like cannonballs. Unfolded, they are soldiers. Destroy twelve spheres."]))
quest(c7, "vague3", ("Troisième vague", "Third Wave"), 6, -2, [T_kill("minecraft:wither_skeleton", 30), T_kill("minecraft:blaze", 30)],
      [R_coin("crown", 1)], deps=["vague2"],
      desc=D(["Dans le Nether aussi, les forges de l'Empire se sont rallumées."], ["In the Nether too, the Empire's forges have lit up again."]))
quest(c7, "flotte", ("La flotte du ciel", "The Sky Fleet"), 2, 0, [T_struct("kubejs:dirigeable")], [R_coin("crown", 1), R_xp(800)], deps=["eveil"],
      desc=D(["Des croiseurs de l'Empire n'ont jamais atterri. Ils tournent encore au-dessus des nuages, vers la hauteur 150, tenus par leur équipage d'automates.",
              "Abordez-en un avec votre propre engin volant. Le livre de bord du capitaine est dans sa cabine, à la poupe ; la soute est sous le pont.",
              "&8C'est d'eux que tombent parfois des automates, quand une patrouille est larguée.&r"],
             ["Some Empire cruisers never landed. They still circle above the clouds, around height 150, held by their automaton crews.",
              "Board one with your own flying machine. The captain's log is in his cabin at the stern; the hold is under the deck.",
              "&8They are where automatons sometimes drop from, when a patrol is airdropped.&r"]))
quest(c7, "cite1", ("La cité de bronze", "The Bronze City"), 2, 2, [T_kill("mebahelcreaturesdwarven:dwarven_spider_guardian", 3)], [R_coin("cog", 3)], deps=["eveil"],
      desc=D(["Une cité de l'Empire bâtie dans le bronze, bien avant l'âge du laiton. Ses grandes araignées gardiennes veillent encore. Abattez-en trois."],
             ["An Empire city built in bronze, long before the brass age. Its great guardian spiders still keep watch. Destroy three."]))
quest(c7, "cite2", ("Les profondeurs", "The Depths"), 4, 2, [T_kill("mebahelcreaturesdwarven:dwarven_centurion")], [R_coin("cog", 3)], deps=["cite1"],
      desc=D(["Sous terre, une ville entière éclairée par des lampes qui n'ont jamais faibli. Au fond, un centurion de bronze, haut comme une maison, à vapeur. Abattez-le."],
             ["Underground, a whole city lit by lamps that never dimmed. At its heart, a steam-powered bronze centurion as tall as a house. Destroy it."]))
quest(c7, "cite3", ("Le colosse de fer", "The Iron Colossus"), 6, 2, [T_kill("mowziesmobs:ferrous_wroughtnaut")], [R_coin("crown", 1)], deps=["cite2"],
      desc=D(["Dans une salle souterraine fermée, une armure vide, plus grande qu'un homme, tient encore sa hache. Elle attend un ordre depuis des siècles.",
              "&8Frappez-la dans le dos, quand elle se fige après un coup.&r"],
             ["In a sealed underground hall, an empty suit of armor, taller than a man, still holds its axe. It has waited centuries for an order.",
              "&8Strike its back when it freezes after a blow.&r"]))
quest(c7, "wither", ("L'étincelle de secours", "The Spare Spark"), 8, 3, [T_kill("minecraft:wither")], [R_coin("crown", 1)], deps=["eveil"],
      optional=True,
      desc=D(["&7Optionnel.&r Si le cœur du Gardien des enfers offert par le Cœur d'Airain est perdu, le Gardien des enfers (le Wither) en donne un autre."],
             ["&7Optional.&r If the Infernal Guardian Core given by the Airain Core is lost, the Infernal Guardian (the Wither) drops another."]))
quest(c7, "berceau", ("Le berceau de l'Empire", "Cradle of the Empire"), 8, 0, [T_struct("cataclysm:ancient_factory")], [R_xp(800)],
      deps=["vague3", "cite3"],
      desc=D(["Une usine ancienne enfouie vers Y -30. Le Cœur vous en a donné la direction."], ["An ancient factory buried around Y -30. The Core showed you the way."]))
quest(c7, "sentinelle", ("La sentinelle", "The Sentinel"), 10, 0, [T_kill("cataclysm:the_prowler")], [R_coin("crown", 1)], deps=["berceau"])
quest(c7, "etincelle", ("L'étincelle", "The Spark"), 10, 2, [T_item("minecraft:nether_star")], [R_xp(500)], deps=["berceau"],
      desc=D(["Un cœur du Gardien des enfers réveillera l'Empereur endormi dans sa machine."], ["An Infernal Guardian Core will wake the Emperor sleeping inside his machine."]))
quest(c7, "empereur", ("L'Empereur d'Airain", "The Airain Emperor"), 12, 1, [T_kill("cataclysm:the_harbinger")],
      [R_coin("sun", 1), R_item("minecraft:netherite_ingot", 4), R_xp(5000), R_tag("airain_fin")], deps=["sentinelle", "etincelle"],
      shape="hexagon", size=2.5, subtitle=("&4Boss final&r", "&4Final boss&r"),
      desc=D(["Au centre de l'usine, une machine immense, immobile. L'Empereur, fusionné avec ce qu'il a construit : Auguste Ferrand, le fondateur, transféré dans sa propre usine bien avant tous les autres.",
              "Clic droit avec le cœur du Gardien des enfers pour le réveiller. &cIl est extrêmement dangereux.&r"],
             ["At the center of the factory, a huge motionless machine. The Emperor, fused with what he built: Auguste Ferrand, the founder, transferred into his own factory long before everyone else.",
              "Right-click it with the Infernal Guardian Core to wake him. &cHe is extremely dangerous.&r"]))
quest(c7, "coeur_eteint", ("Le Cœur éteint", "The Dark Heart"), 14, 1, [T_item("kubejs:coeur_eteint")], [R_xp(1000)], deps=["empereur"],
      shape="gear", size=1.5,
      desc=D(["L'Empereur est tombé. Sa machine est restée là, éteinte, et dans votre sac le Cœur d'Airain ne bat plus. Il contient encore toutes les âmes que l'Empire a fait brûler, et une voix que vous connaissez : celle d'Elias Vael.",
              "&o« Il fait froid… Ramène-moi, ou laisse-moi partir. »&r",
              "&8Le Cœur s'éteint dès qu'on le porte sur soi. Il n'en existe qu'un seul : ne le perdez pas.&r"],
             ["The Emperor has fallen. His machine stayed behind, dark, and in your pack Airain's Core no longer beats. It still holds every soul the Empire burned, and a voice you know: Elias Vael's.",
              "&o\"It's cold… Bring me back, or let me go.\"&r",
              "&8The Core goes dark as soon as someone carries it. There is only one: do not lose it.&r"]))
quest(c7, "deux_voix", ("Les deux voix", "The Two Voices"), 14, -1, [T_check()], [R_xp(500)], deps=["coeur_eteint"],
      desc=D(["L'Empire dort dans le Cœur et promet l'éternité à ceux qui le servent.",
              "Ada, Morgana et Octave disent autre chose : le Transfert ne tue pas, il enferme, et des milliers de voix attendent encore.",
              "&6Rallumer le Cœur&r, c'est rendre l'Empire au monde. &3Le briser&r, c'est rendre les âmes à elles-mêmes.",
              "Il n'y a pas de bonne réponse. Seulement la vôtre."],
             ["The Empire sleeps in the Heart and promises eternity to those who serve it.",
              "Ada, Morgana and Octave say otherwise: the Transfer does not kill, it imprisons, and thousands of voices are still waiting.",
              "&6Rekindling the Heart&r gives the Empire back to the world. &3Breaking it&r gives the souls back to themselves.",
              "There is no right answer. Only yours."]))
quest(c7, "choix_final", ("Le choix final", "The Final Choice"), 16, 1, [T_stage("airain_fin")], [R_xp(2000)], deps=["deux_voix"],
      shape="hexagon", size=2.0, icon="kubejs:coeur_eteint", subtitle=("&6Un seul choix, pour tout le monde&r", "&6One choice, for everyone&r"),
      desc=D(["Deux lieux, deux gestes. Le choix se fait dans le monde, et vaut pour toute l'équipe. Il n'y a pas de retour.",
              "&6Rallumer le Cœur&r : au berceau, posez le Cœur éteint dans la &6machine de l'Empereur&r, puis allumez-le d'un &6cœur du Gardien des enfers&r. L'Empire repart, et il vous obéit.",
              "&3Libérer les âmes&r : au centre d'un &3Grand Relais&r, posez le Cœur éteint sur le résonateur, puis frappez avec le &3diapason d'Ada&r, un &3Écho primordial&r sur vous. Le Cœur se brise, et tout s'arrête.",
              "&8Tant que le geste n'est pas fait, un clic droit à main nue reprend le Cœur. Le diapason se fabrique : refaites-en un s'il a servi contre le Chœur.&r"],
             ["Two places, two gestures. The choice is made in the world, and holds for the whole team. There is no going back.",
              "&6Rekindle the Heart&r: at the cradle, set the dark Core into the &6Emperor's machine&r, then light it with an &6Infernal Guardian Core&r. The Empire starts again, and obeys you.",
              "&3Free the souls&r: at the center of a &3Great Relay&r, set the dark Core on the resonator, then strike it with &3Ada's tuning fork&r, a &3Primordial Echo&r on you. The Core breaks, and everything stops.",
              "&8Until the gesture is made, right-clicking bare-handed takes the Core back. The tuning fork can be crafted: make another if it was spent against the Choir.&r"]))
titres_taches("choix_final", [("Rallumer le Cœur ou libérer les âmes", "Rekindle the Heart or free the souls")])
quest(c7, "f_empire", ("Rallumer le Cœur", "Rekindle the Heart"), 18, 0, [T_stage("airain_fin_empire")],
      [R_item("airain:imperial_charter", 3)], deps=["choix_final"], shape="hexagon", size=1.5, icon="airain:airain_crown",
      subtitle=("&6Fin de l'Empire&r", "&6Empire ending&r"),
      desc=D(["Le Cœur bat de nouveau. Les automates se sont tus, puis ils vous ont obéi : vous êtes les nouveaux souverains.",
              "Récompenses : la &6couronne d'airain&r (les automates ne vous attaquent plus d'eux-mêmes, vos gardiens proches sont plus forts), le testament d'Auguste Ferrand, des gardiens réparés plus robustes, et le livre « L'Empire renaissant »."],
             ["The Heart beats again. The automatons fell silent, then obeyed you: you are the new sovereigns.",
              "Rewards: the &6Airain Crown&r (automatons no longer attack you on their own, your nearby guardians grow stronger), Auguste Ferrand's testament, sturdier repaired guardians, and the book \"The Empire Reborn\"."]))
quest(c7, "f_echo", ("Libérer les âmes", "Free the Souls"), 18, 2, [T_stage("airain_fin_echo")],
      [], deps=["choix_final"], shape="hexagon", size=1.5, icon="kubejs:echo_primordial",
      subtitle=("&3Fin de l'Écho&r", "&3Echo ending&r"),
      desc=D(["Le diapason a sonné contre le Cœur. Il s'est fendu, et les âmes s'en sont allées, Elias et Ada les derniers. Les automates se sont arrêtés pour de bon.",
              "Récompenses : la &3bénédiction de l'Écho&r (vision dans le noir, moitié plus d'expérience, le sculk ne vous entend plus, et accroupi immobile un instant, une onde révèle les créatures à 24 blocs), le diadème et la note de Morgana, les âmes sans repos ne reviennent plus, et le livre « Le dernier chant »."],
             ["The tuning fork rang against the Core. It cracked, and the souls went away, Elias and Ada last of all. The automatons stopped for good.",
              "Rewards: the &3Echo's blessing&r (sight in the dark, half again as much experience, the sculk no longer hears you, and crouching still for a moment sends a wave revealing creatures within 24 blocks), Morgana's diadem and note, restless souls never return, and the book \"The Last Song\"."]))
for _c in chapters:                       # la fin non choisie ne s'affiche jamais
    for _q in _c["quests"]:
        if _q["id"] in (QUESTS["f_empire"], QUESTS["f_echo"]): _q["invisible"] = True
quest(c7, "capitaine", ("Le Capitaine impérial", "The Imperial Captain"), 18, -1, [T_stage("airain_gardien_elite")],
      [R_coin("crown", 1), R_xp(2000)], deps=["f_empire"], icon="airain:imperial_plate", optional=True,
      desc=D(["L'Empire rallumé a de nouveau besoin d'officiers. Une plaque impériale, rivée sur le torse d'un gardien, en fait un capitaine.",
              "Clic droit avec une &6plaque impériale&r sur un gardien rattaché à une base. Un seul capitaine par base.",
              "Plus grand et plus robuste, il porte &6deux modules par emplacement&r, et les gardiens à 16 blocs gagnent Force et Résistance."],
             ["The rekindled Empire needs officers again. An imperial plate, riveted onto a guardian's chest, makes it a captain.",
              "Right-click a guardian bound to a base with an &6imperial plate&r. One captain per base.",
              "Taller and sturdier, it carries &6two modules per slot&r, and guardians within 16 blocks gain Strength and Resistance."]))
quest(c7, "gardien_echo", ("Le Gardien d'Écho", "The Echo Guardian"), 18, 3, [T_stage("airain_gardien_elite")],
      [R_item("kubejs:echo_primordial", 2), R_xp(2000)], deps=["f_echo"], icon="airain:primordial_echo_block", optional=True,
      desc=D(["Les âmes sont parties, mais l'Écho reste dans le laiton. Un bloc d'écho primordial suffit à le réveiller dans un gardien.",
              "Clic droit avec un &3bloc d'écho primordial&r sur un gardien rattaché à une base. Un seul gardien d'Écho par base.",
              "Il frappe ses cibles d'une &3onde sonique&r jusqu'à 16 blocs et soigne les gardiens qui l'entourent."],
             ["The souls are gone, but the Echo lingers in the brass. A primordial echo block is enough to wake it inside a guardian.",
              "Right-click a guardian bound to a base with a &3primordial echo block&r. One Echo guardian per base.",
              "It strikes its targets with a &3sonic wave&r up to 16 blocks away and heals the guardians around it."]))
quest(c7, "trone", ("Le Trône impérial", "The Imperial Throne"), 20, -1, [T_item("airain:imperial_throne")],
      [R_coin("crown", 2), R_xp(3000)], deps=["f_empire"], icon="airain:imperial_throne", optional=True,
      desc=D(["Un Empire a besoin d'un trône. Un seul, dressé dans la &6capitale impériale&r : un étendard de fondation sur lequel on a posé une plaque impériale.",
              "Assis, l'Empereur promulgue un &6décret&r pour une heure : &6guerre&r (gardiens renforcés, et au lieu de mourir on est ramené au trône), &6forge&r (concasseurs, meule, lavage et cuisson au ventilateur rendent le double dans les bases) ou &6prospérité&r (commandes +50 %). On peut en changer au bout de 15 minutes.",
              "Dans sa base, la couronne commande tous les gardiens, et l'on réapparaît devant le trône."],
             ["An Empire needs a throne. Only one, raised in the &6imperial capital&r: a foundation banner given an imperial plate.",
              "Seated, the Emperor issues a &6decree&r for an hour: &6war&r (stronger guardians, and instead of dying you are brought back to the throne), &6forge&r (crushers, millstones, fan washing and cooking yield double in bases) or &6prosperity&r (orders +50%). It can be changed after 15 minutes.",
              "In its base, the crown commands every guardian, and you respawn before the throne."]))
quest(c7, "solium", ("Le Solium de la Prêtresse", "The Priestess's Solium"), 20, 3, [T_item("airain:solium")],
      [R_item("kubejs:echo_primordial", 2), R_xp(3000)], deps=["f_echo"], icon="airain:solium", optional=True,
      desc=D(["Morgana chantait assise. Son siège, rebâti à l'appareil d'enchantement, se dresse dans une &3capitale arcanique&r (un étendard de fondation sur lequel on a posé un bloc d'écho primordial), et il n'y en a qu'un.",
              "Assise, la Prêtresse entonne un &3chant&r pour une heure : &3âmes&r (expérience doublée), &3croissance&r (plantes trois fois plus rapides dans les bases) ou &3résonance&r (sourcelinks doublés). On peut en changer au bout de 15 minutes.",
              "Dans sa base, le mana se régénère bien plus vite, et l'on réapparaît devant le solium."],
             ["Morgana sang seated. Her seat, rebuilt at the enchanting apparatus, stands in an &3arcane capital&r (a foundation banner given a primordial echo block), and there is only one.",
              "Seated, the Priestess intones a &3chant&r for an hour: &3souls&r (double experience), &3growth&r (plants three times faster in bases) or &3resonance&r (double sourcelinks). It can be changed after 15 minutes.",
              "In its base, mana regenerates much faster, and you respawn before the solium."]))
quest(c7, "borne_empire", ("La Machine différentielle", "The Difference Engine"), 22, -1, [T_item("airain:difference_engine")],
      [R_coin("crown", 2), R_xp(2000)], deps=["f_empire"], icon="airain:difference_engine", optional=True,
      desc=D(["Les entrepôts de l'Empire n'ont jamais été vides ; il suffisait de savoir compter. Une &6machine différentielle&r, montée à l'établi mécanique autour d'une plaque impériale, les rouvre.",
              "Elle se pose avec ses décors et une &6zone d'arrivage&r de 3 x 3 devant elle. Clic droit : choisissez des matières premières par lots de 1, 32 ou 64, payées en pièces.",
              "Une minute plus tard, la caisse descend en &6parachute&r sur la zone. Clic droit dessus pour la vider."],
             ["The Empire's warehouses were never empty; you only had to know how to count. A &6difference engine&r, built at the mechanical crafter around an imperial plate, opens them again.",
              "It is placed with its decorations and a 3 x 3 &6arrival pad&r in front. Right-click: pick raw materials in lots of 1, 32 or 64, paid in coins.",
              "One minute later, the crate &6parachutes&r onto the pad. Right-click it to empty it."]))
quest(c7, "borne_echo", ("L'Archive résonante", "The Resonant Archive"), 22, 3, [T_item("airain:resonant_archive")],
      [R_coin("crown", 2), R_xp(2000)], deps=["f_echo"], icon="airain:resonant_archive", optional=True,
      desc=D(["L'Écho se souvient de tout ce qui a existé. Une &3archive résonante&r, éveillée à l'appareil d'enchantement autour d'un bloc d'écho primordial, le lui fait rendre.",
              "Elle se pose avec ses obélisques et un &3cercle d'arrivée&r de 3 x 3 devant elle. Clic droit : choisissez des matières premières par lots de 1, 32 ou 64, payées en pièces.",
              "Une minute plus tard, un passage s'ouvre et la caisse &3apparaît&r sur le cercle. Clic droit dessus pour la vider."],
             ["The Echo remembers everything that ever existed. A &3resonant archive&r, awakened at the enchanting apparatus around a primordial echo block, makes it give things back.",
              "It is placed with its obelisks and a 3 x 3 &3arrival circle&r in front. Right-click: pick raw materials in lots of 1, 32 or 64, paid in coins.",
              "One minute later, a passage opens and the crate &3appears&r on the circle. Right-click it to empty it."]))
quest(c7, "epilogue", ("Épilogue", "Epilogue"), 18, 1, [T_check()], [R_item("minecraft:beacon")], deps=["f_empire", "f_echo"], shape="gear", size=1.5,
      dep_un=True,
      desc=D(["Le choix est fait. Lisez le livre qu'il vous a laissé : c'est la fin de l'histoire, la vôtre.",
              "", "&6Merci d'avoir joué à L'Empire d'Airain.&r"],
             ["The choice is made. Read the book it left you: this is the end of the story, yours.",
              "", "&6Thank you for playing The Airain Empire.&r"]))
# l'après-fin : rebâtir l'Empire ou apaiser l'Écho
for _k, _n, _x in (("r1", 1, 18), ("r3", 3, 20), ("r5", 5, 22), ("r10", 10, 24)):
    quest(c7, _k, (("Rebâtir l'Empire" if _n == 1 else "Rebâtir : %d avant-postes" % _n), ("Rebuild the Empire" if _n == 1 else "Rebuild: %d outposts" % _n)),
          _x, -2.5, [T_stage("airain_poste_%d" % _n)],
          [R_coin("crown", 1)] + ([R_item("airain:imperial_charter", 2)] if _n < 10 else [R_coin("sun", 1)]),
          deps=["f_empire"] if _n == 1 else ["r%d" % {3: 1, 5: 3, 10: 5}[_n]], optional=True, shape="gear" if _n == 10 else None,
          desc=D(["&7Après la fin de l'Empire.&r Couronne sur la tête, entrez dans un avant-poste (ou une cité mécanique) et utilisez une &6charte impériale&r (clic droit).",
                  "L'avant-poste se rallume : ses bannières prennent les couleurs de votre base la plus proche, plus aucun monstre n'y apparaît, ses comptoirs baissent leurs prix d'un quart, et un gardien réparé y monte la garde.",
                  "&8Charte : 6 lingots de laiton, 2 mécanismes de précision, 1 papier.&r"] if _n == 1 else ["Rallumez %d avant-postes en tout." % _n],
                 ["&7After the Empire ending.&r Crown on your head, enter an outpost (or a mechanical city) and use an &6imperial charter&r (right-click).",
                  "The outpost comes back to life: its banners take your nearest base's colors, no more monsters spawn there, its counters lower their prices by a quarter, and a repaired guardian stands watch.",
                  "&8Charter: 6 brass ingots, 2 precision mechanisms, 1 paper.&r"] if _n == 1 else ["Rekindle %d outposts in all." % _n]))
    quest(c7, "a%d" % _n, (("Apaiser l'Écho" if _n == 1 else "Apaiser : %d relais" % _n), ("Soothe the Echo" if _n == 1 else "Soothe: %d relays" % _n)),
          _x, 4.5, [T_stage("airain_relais_%d" % _n)],
          [R_coin("crown", 1)] + ([R_item("kubejs:fragment_resonance", 8)] if _n < 10 else [R_coin("sun", 1)]),
          deps=["f_echo"] if _n == 1 else ["a%d" % {3: 1, 5: 3, 10: 5}[_n]], optional=True, shape="gear" if _n == 10 else None,
          desc=D(["&7Après la fin de l'Écho.&r Dans un relais brisé (ou au Grand Relais), accroupi, frappez le diapason d'Ada (clic droit) avec &d8 fragments de résonance&r sur vous.",
                  "Le relais s'apaise : plus aucun monstre n'apparaît à moins de 64 blocs, et un Écho tranquille flotte autour.",
                  "&8Les âmes sans repos ne venant plus, les fragments se trouvent dans les relais, le sanctuaire et les cités antiques.&r"] if _n == 1 else ["Apaisez %d relais en tout." % _n],
                 ["&7After the Echo ending.&r In a broken relay (or the Great Relay), sneak and strike Ada's tuning fork (right-click) with &d8 resonance fragments&r on you.",
                  "The relay grows calm: no more monsters spawn within 64 blocks, and a quiet Echo drifts around it.",
                  "&8With the restless souls gone, fragments are found in relays, the sanctuary and ancient cities.&r"] if _n == 1 else ["Soothe %d relays in all." % _n]))
quest(c7, "defi", ("Défi final : la garde de bronze", "Final Challenge: The Bronze Guard"), 20, 1,
      [T_kill("mebahelcreaturesdwarven:dwarven_centurion", 3)],
      [R_coin("sun", 2)], deps=["epilogue"], optional=True,
      desc=D(["&7Optionnel.&r Pour ceux qui en veulent encore : trois centurions de plus. Ils ne se sont pas tous arrêtés."],
             ["&7Optional.&r For those who want more: three more centurions. Not all of them stopped."]))

# =============================================================================
# SACS ET STOCKAGE
# =============================================================================
cS = chapter("sacs", "10_sacs_stockage", ("&3Annexe&r · Sacs et stockage", "&3Side&r · Backpacks and Storage"),
             ("Avant chaque expédition, un sac plus grand.", "Before each expedition, a bigger backpack."), "sophisticatedbackpacks:backpack", 10)
SB, SS = "sophisticatedbackpacks:", "sophisticatedstorage:"
quest(cS, "sac1", ("Le premier sac", "The First Backpack"), 0, 0, [T_item(SB + "backpack")], [R_item("minecraft:leather", 8)], deps=["outils"],
      desc=D(["Cuir, ficelle et un coffre. Clic droit pour l'ouvrir, et il peut se poser au sol."], ["Leather, string and a chest. Right-click to open; it can also be placed down."]))
quest(cS, "sac_cuivre", ("Sac de cuivre", "Copper Backpack"), 2, 0, [T_item(SB + "copper_backpack"), T_item(SB + "tool_swapper_upgrade")],
      [R_coin("bevel", 3)], deps=["sac1"],
      desc=D(["L'échangeur d'outils prend tout seul le bon outil dans le sac."], ["The tool swapper picks the right tool from the backpack on its own."]))
quest(cS, "stock1", ("Tonneaux de l'Empire", "Empire Barrels"), 2, 2, [T_item(SS + "barrel", 4), T_item(SS + "chest", 2)], [R_coin("bevel", 3)],
      deps=["sac1"])
quest(cS, "sac_fer", ("Sac de fer", "Iron Backpack"), 4, 0, [T_item(SB + "iron_backpack"), T_item(SB + "pickup_upgrade"), T_item(SB + "stack_upgrade_tier_1")],
      [R_coin("sprocket", 1)], deps=["sac_cuivre", "plaques"],
      desc=D(["Avant les salles d'épreuve : un sac plus grand qui ramasse tout seul."], ["Before the trial chambers: a bigger backpack that picks things up on its own."]))
quest(cS, "stock2", ("Le stockage s'organise", "Storage Gets Organized"), 4, 2, [T_item(SS + "iron_barrel", 4), T_item(SS + "storage_tool")],
      [R_coin("sprocket", 1)], deps=["stock1"])
quest(cS, "sac_or", ("Sac d'or", "Gold Backpack"), 6, 0,
      [T_item(SB + "gold_backpack"), T_item(SB + "magnet_upgrade"), T_item(SB + "feeding_upgrade"), T_item(SB + "refill_upgrade")],
      [R_coin("sprocket", 2)], deps=["sac_fer", "boitier_cuivre"],
      desc=D(["Avant le monument : aimant, nourriture et réapprovisionnement automatiques."], ["Before the monument: automatic magnet, feeding and refill."]))
quest(cS, "stock3", ("Liens de stockage", "Storage Links"), 6, 2, [T_item(SS + "gold_chest", 2), T_item(SS + "storage_link", 4)],
      [R_coin("sprocket", 2)], deps=["stock2"])
quest(cS, "sac_diamant", ("Sac de diamant", "Diamond Backpack"), 8, 0, [T_item(SB + "diamond_backpack"), T_item(SB + "auto_smelting_upgrade")],
      [R_coin("cog", 1)], deps=["sac_or", "nether"],
      desc=D(["Avant le Nether : un sac qui fond le minerai pendant que vous marchez."], ["Before the Nether: a backpack that smelts ore while you walk."]))
quest(cS, "controleur", ("Le contrôleur de stockage", "The Storage Controller"), 8, 2, [T_item(SS + "controller")], [R_coin("cog", 1)],
      deps=["stock3", "quartz"],
      desc=D(["Il relie tous vos coffres et tonneaux en un seul inventaire. Demande un comparateur, donc du quartz du Nether."],
             ["It links all your chests and barrels into one inventory. Needs a comparator, so Nether quartz."]))
quest(cS, "sac_netherite", ("Sac de netherite", "Netherite Backpack"), 10, 0, [T_item(SB + "netherite_backpack"), T_item(SB + "tank_upgrade")],
      [R_coin("cog", 2)], deps=["sac_diamant", "bastion"])
quest(cS, "sac_eternel", ("Bonus : le sac éternel", "Bonus: The Everlasting Backpack"), 12, 0,
      [T_item(SB + "everlasting_upgrade"), T_item(SB + "inception_upgrade")], [R_coin("crown", 1)], deps=["sac_netherite", "reactiver"],
      optional=True,
      desc=D(["&7Optionnel.&r Demande des cœurs du Gardien des enfers (étoiles du Nether) : le sac ne disparaît plus jamais, et peut contenir d'autres sacs."],
             ["&7Optional.&r Needs Infernal Guardian Cores (Nether Stars): the backpack never despawns, and can hold other backpacks."]))

# =============================================================================
# COMMANDES DE L'EMPIRE (répétables)
# =============================================================================
cC = chapter("commandes", "11_commandes", ("&3Annexe&r · Commandes de l'Empire", "&3Side&r · Empire Orders"),
             ("La production se paie en pièces. Les pièces achètent ce qu'on ne trouve nulle part.", "Production pays in coins. Coins buy what you can't find anywhere."),
             "numismatics:cog", 11)
ORD = [  # (clé, objet, quantité, pièce, nombre, dépendance, (titre fr, en))
    ("o_pain", "minecraft:bread", 64, "bevel", 4, "ferme", ("Commande : pain", "Order: Bread")),
    ("o_alliage", "create:andesite_alloy", 128, "bevel", 4, "q_alliage", ("Commande : alliage", "Order: Alloy")),
    ("o_plaques", "create:iron_sheet", 128, "sprocket", 4, "q_plaques", ("Commande : plaques de fer", "Order: Iron Sheets")),
    ("o_cuivre", "create:copper_sheet", 128, "sprocket", 3, "q_cuivre", ("Commande : plaques de cuivre", "Order: Copper Sheets")),
    ("o_tuyaux", "create:fluid_pipe", 64, "sprocket", 2, "tuyaux", ("Commande : tuyaux", "Order: Pipes")),
    ("o_laiton", "create:brass_ingot", 128, "cog", 1, "q_laiton", ("Commande : laiton", "Order: Brass")),
    ("o_precision", "create:precision_mechanism", 32, "cog", 2, "q_precision", ("Commande : mécanismes", "Order: Mechanisms")),
    ("o_rails", "create:track", 256, "cog", 2, "rails", ("Commande : rails", "Order: Track")),
    ("o_obus", "createbigcannons:solid_shot", 32, "cog", 2, "obus", ("Commande : boulets", "Order: Shot")),
    ("o_enveloppes", "aeronautics:white_envelope", 128, "cog", 2, "q_enveloppes", ("Commande : enveloppes", "Order: Envelopes")),
    ("o_tubes", "create:electron_tube", 64, "cog", 2, "quartz", ("Commande : tubes électroniques", "Order: Electron Tubes")),
    ("o_netherite", "kubejs:plaque_netherite", 4, "crown", 1, "netherite", ("Commande : plaques de netherite", "Order: Netherite Plates")),
]
quest(cC, "boutique", ("La boutique de l'Empire", "The Empire Shop"), 0, 0, [T_check()], [R_coin("bevel", 4)], deps=["bienvenue"],
      desc=D(["Les commandes se répètent : livrez, encaissez, recommencez.",
              "Valeurs : éperon 1, biseau 8, pignon 16, engrenage 64, couronne 512, soleil 4096.",
              "Le comptoir du laboratoire vend bois, fer brut, lapis, netherrack, perles de l'Ender et cœurs de la mer. Les avant-postes ont leurs propres machines, et leurs salles scellées vendent livres d'enchantement, totems et bien plus."],
             ["Orders repeat: deliver, get paid, start again.",
              "Values: spur 1, bevel 8, sprocket 16, cog 64, crown 512, sun 4096.",
              "The lab counter sells logs, raw iron, lapis, netherrack, ender pearls and hearts of the sea. Outposts have their own machines, and their sealed rooms sell enchanted books, totems and more."]))
for i, (k, it, n, coin, nb, dep, title) in enumerate(ORD):
    quest(cC, k, title, 2 + (i % 4) * 2, -3 + (i // 4) * 2, [T_item(it, n, consume=True)], [R_coin(coin, nb), R_cmd("pouvoir prime %s %d" % (coin, nb))],
          deps=["boutique", dep], repeat=True,
          desc=D(["&7Répétable.&r Les objets livrés sont consommés."], ["&7Repeatable.&r Delivered items are consumed."]))

# =============================================================================
# INGÉNIERIE
# =============================================================================
cI = chapter("ingenierie", "12_ingenierie", ("&3Annexe&r · Ingénierie", "&3Side&r · Engineering"),
             ("Faire travailler les machines à votre place.", "Make the machines work for you."), "create:mechanical_harvester", 12)
quest(cI, "i_scierie", ("La scierie", "The Sawmill"), 0, 0, [T_item("minecraft:oak_planks", 512)], [R_coin("sprocket", 2)], deps=["outils_meca"],
      desc=D(["Une scie mécanique sur un tapis : des planches à l'infini."], ["A mechanical saw over a belt: endless planks."]))
quest(cI, "i_cuisine", ("Cuisine au ventilateur", "Fan Cooking"), 2, 0, [T_item("minecraft:cooked_beef", 64)], [R_coin("sprocket", 1)],
      deps=["ventilateur"], desc=D(["Un ventilateur soufflant à travers un feu de camp cuit la viande à la chaîne."], ["A fan blowing through a campfire cooks meat in bulk."]))
quest(cI, "i_tri", ("Le tri", "Sorting"), 4, 0, [T_item("create:filter", 4), T_check()], [R_coin("sprocket", 2)], deps=["goulottes"],
      desc=D(["Des filtres dans des entonnoirs : chaque objet dans le bon coffre."], ["Filters in funnels: every item in the right chest."]))
quest(cI, "i_canne", ("Ferme à canne à sucre", "Sugar Cane Farm"), 0, 2, [T_item("minecraft:sugar_cane", 256)], [R_coin("sprocket", 1)], deps=["ferme"])
quest(cI, "i_arbres", ("Ferme à arbres", "Tree Farm"), 2, 2, [T_item("minecraft:oak_log", 256)], [R_coin("sprocket", 2)], deps=["i_scierie"])
quest(cI, "i_pierre", ("Générateur de pierre", "Cobblestone Generator"), 4, 2, [T_item("minecraft:cobblestone", 1024)], [R_coin("sprocket", 2)],
      deps=["outils_meca"])
quest(cI, "i_vapeur", ("La grande chaudière", "The Great Boiler"), 6, 0, [T_item("create:blaze_burner", 4), T_check()], [R_coin("cog", 2)],
      deps=["blaze", "vapeur"],
      desc=D(["Une machine à vapeur chauffée par au moins quatre brûleurs à blaze."], ["A steam engine heated by at least four blaze burners."]))
quest(cI, "i_entonnoirs", ("Entonnoirs de laiton", "Brass Funnels"), 6, 2, [T_item("create:brass_funnel", 8)], [R_coin("sprocket", 2)], deps=["laiton", "quartz"])
quest(cI, "i_coffres", ("Coffres-forts", "Item Vaults"), 8, 0, [T_item("create:item_vault", 8)], [R_coin("cog", 1)], deps=["q_plaques"])
quest(cI, "i_gisement", ("Les gisements infinis", "Infinite Veins"), 8, 2, [T_item("createoreexcavation:vein_finder"), T_item("createoreexcavation:drilling_machine")],
      [R_coin("cog", 2)], deps=["precision", "broyage"],
      desc=D(["Trouvez un filon caché avec le détecteur, puis forez-le à l'infini.",
              "&8Le détecteur demande un bloc de minerai de redstone intact (pioche Toucher de soie) ; la foreuse, des plaques renforcées (obsidienne broyée aux roues).&r"],
             ["Find a hidden vein with the finder, then drill it forever.",
              "&8The finder needs an intact redstone ore block (Silk Touch pickaxe); the drilling machine needs sturdy sheets (obsidian crushed by the wheels).&r"]))

# Les machines réfractaires : Create et Ars Nouveau ensemble (mod Airain, package fusion)
quest(cI, "f_condenseur", ("L'Écho liquide", "Liquid Echo"), 0, 0, [T_item("airain:echo_condenser"), T_item("airain:liquid_echo_bucket")], [R_coin("cog", 1)],
      deps=["laiton", "a_ars_source"], subtitle=("Les machines réfractaires", "The Refractory Machines"),
      desc=D(["Le condenseur change la source des jarres en Écho liquide, qui coule dans les tuyaux, et l'inverse. C'est lui qui nourrit la turbine depuis vos jarres. Un bec verseur s'en sert aussi pour imprégner les objets un par un."],
             ["The condenser turns the source of jars into liquid Echo, which flows through pipes, and back. It feeds the turbine from your jars. A spout also uses it to imbue items one by one."]))
quest(cI, "f_turbine", ("La turbine d'Écho", "The Echo Turbine"), 2, 0, [T_item("airain:echo_turbine")], [R_coin("cog", 1)],
      deps=["f_condenseur"],
      desc=D(["Les ingénieurs réfractaires faisaient tourner leurs ateliers à la source. Une turbine d'Écho boit de l'Écho liquide, amené par les tuyaux, et rend 64 tr/min.",
              "&8Établi mécanique. Tout est dans le livre de l'ingénieur, onglet Fusion.&r"],
             ["The Refractory engineers ran their workshops on source. An Echo Turbine drinks piped liquid Echo and gives 64 RPM.",
              "&8Mechanical crafter. Everything is in the engineer's manual, Fusion tab.&r"]))
quest(cI, "f_sourcelink", ("Le sourcelink mécanique", "The Mechanical Sourcelink"), 2, 0, [T_item("airain:mechanical_sourcelink")], [R_coin("sprocket", 3)],
      deps=["f_turbine"],
      desc=D(["L'inverse de la turbine : la rotation devient de l'Écho liquide, à pomper hors de sa cuve. On y perd toujours un peu."],
             ["The turbine's opposite: rotation becomes liquid Echo, to pump out of its tank. Something is always lost."]))
quest(cI, "f_diffuseur", ("La brume d'Écho", "The Echo Mist"), 4, 0, [T_item("airain:echo_diffuser"), T_item("ars_nouveau:source_gem", 32)], [R_coin("cog", 1)],
      deps=["f_condenseur", "ventilateur"],
      desc=D(["Un diffuseur d'Écho devant un ventilateur : le souffle imprègne d'Écho tout ce qu'il touche. Les éclats d'améthyste deviennent des gemmes de source, le sculk des éclats d'écho."],
             ["An Echo Diffuser in front of a fan: the airflow imbues everything it touches. Amethyst shards become source gems, sculk becomes echo shards."]))
quest(cI, "f_glyphe", ("Le glyphe de l'engrenage", "The Glyph of the Gear"), 8, 0, [T_item("airain:glyph_gear")], [R_coin("cog", 2)],
      deps=["f_turbine"],
      desc=D(["Le seul sort que les deux camps ont appris l'un de l'autre. Lancé sur une machine de Create, il la fait tourner plus vite. Lancé sur un automate, il grippe ses rouages."],
             ["The only spell both sides learned from each other. Cast on a Create machine, it makes it run faster. Cast on an automaton, it jams its gears."]))

# =============================================================================
# LA FONDERIE IMPÉRIALE (mod Airain, paquet fonderie)
# =============================================================================
cF = chapter("fonderie", "16_fonderie", ("&3Annexe&r · La fonderie impériale", "&3Side&r · The Imperial Foundry"),
             ("L'airain, l'alliage secret de l'Empire, et le haut-fourneau qui le fond.", "Airain, the Empire's secret alloy, and the blast furnace that melts it."),
             "airain:blast_furnace_taphole", 16)
quest(cF, "fo_briques", ("Les briques réfractaires", "Fire Bricks"), 0, 0, [T_item("airain:fire_bricks", 32)], [R_coin("sprocket", 2)],
      deps=["laiton"], subtitle=("La fonderie impériale", "The Imperial Foundry"),
      desc=D(["L'airain ne se fond pas dans un four ordinaire. Les fondeurs de l'Empire montaient leurs hauts-fourneaux en briques réfractaires, qui tiennent là où la pierre éclate.",
              "&8Mélangeur chauffé : deux briques et une brique du Nether donnent deux briques réfractaires.&r"],
             ["Airain cannot be melted in an ordinary furnace. The Empire's founders built their blast furnaces from fire bricks, which hold where stone cracks.",
              "&8Heated mixer: two bricks and a nether brick make two fire bricks.&r"]))
quest(cF, "fo_fourneau", ("Le haut-fourneau impérial", "The Imperial Blast Furnace"), 2, 0,
      [T_item("airain:blast_furnace_taphole"), T_item("airain:blast_furnace_tuyere"), T_item("airain:blast_furnace_hopper"), T_check()], [R_coin("cog", 2)],
      deps=["fo_briques", "blaze"],
      desc=D(["Une tour de 3 × 3, haute de 4. Le trou de coulée au milieu de la face avant, en bas ; une grille au centre du sol, un brûleur à blaze dessous ; le gueulard au centre du sommet ; une tuyère sur un côté, avec un ventilateur de Create qui souffle dedans.",
              "Clic droit main nue sur le trou de coulée : il dit ce qui manque, et les places à remplir brillent. Une fois monté, le fourneau prend son habillage d'airain. Validez quand c'est fait.",
              "&8Tout est dans le livre de l'ingénieur.&r"],
             ["A 3 × 3 tower, 4 high. The taphole in the middle of the front face, at the bottom; a grate in the middle of the floor, a blaze burner below; the throat in the middle of the top; a tuyere on one side, with a Create fan blowing into it.",
              "Right-click the taphole bare-handed: it tells what is missing, and the spots to fill glow. Once assembled, the furnace takes on its airain trim. Tick the box when it's done.",
              "&8Everything is in the engineer's manual.&r"]))
quest(cF, "fo_refonte", ("Refondre l'Empire", "Remelting the Empire"), 4, -1, [T_item("airain:airain_ingot", 4)], [R_coin("sprocket", 3)],
      deps=["fo_fourneau"],
      desc=D(["Les automates sont faits d'airain. Leur ferraille et leurs rouages brisés, versés au gueulard, redeviennent de l'airain en fusion : il suffit d'un brûleur chauffé.",
              "Le métal sort par le trou de coulée : un tuyau, un bassin et une presse en font des lingots."],
             ["The automatons are made of airain. Their scrap and broken cogs, poured into the throat, turn back into molten airain: a heated burner is enough.",
              "The metal comes out of the taphole: a pipe, a basin and a press turn it into ingots."]))
quest(cF, "fo_alliage", ("L'alliage secret", "The Secret Alloy"), 4, 1, [T_item("airain:airain_block", 4)], [R_coin("cog", 2)],
      deps=["fo_fourneau"],
      desc=D(["Trois de cuivre, un de zinc, un fondant (calcite, poudre de cendres ou laitier) : la recette que l'Empire gardait sous scellés. Il faut un brûleur surchauffé.",
              "Plus le ventilateur tourne vite, plus le fourneau produit."],
             ["Three copper, one zinc, one flux (calcite, cinder flour or slag): the recipe the Empire kept under seal. It needs a superheated burner.",
              "The faster the fan spins, the more the furnace produces."]))
quest(cF, "fo_engrenage", ("L'engrenage d'airain", "The Airain Gear"), 6, 1, [T_item("airain:airain_gear", 4)], [R_coin("cog", 2)],
      deps=["fo_alliage", "precision"],
      desc=D(["La pièce maîtresse des machines impériales : un engrenage, une plaque d'airain, une coulée d'airain en fusion, un coup de presse. Assemblage séquencé.",
              "Les bornes, le trône, la charte et le Cœur d'Airain en demandent."],
             ["The centrepiece of imperial machines: a cogwheel, an airain sheet, a pour of molten airain, a press stroke. Sequenced assembly.",
              "Terminals, the throne, the charter and Airain's Core require it."]))
quest(cF, "fo_style", ("Le style impérial", "The Imperial Style"), 6, -1, [T_item("airain:chiseled_airain", 4), T_item("airain:airain_pillar", 4), T_item("airain:airain_lantern", 4)],
      [R_coin("sprocket", 4)], deps=["fo_refonte"],
      desc=D(["Airain taillé, riveté, ciselé, piliers, grilles, portes ferronnées, lanternes à flamme rouge : de quoi bâtir une capitale digne de l'Empire. Au tailleur de pierre depuis un bloc d'airain."],
             ["Cut, riveted and chiseled airain, pillars, grates, wrought doors, red-flame lanterns: enough to build a capital worthy of the Empire. At the stonecutter, from a block of airain."]))
quest(cF, "fo_patine", ("Rouge impérial", "Imperial Red"), 8, -1, [T_item("airain:oxidized_airain_block")], [R_coin("cog", 1)],
      deps=["fo_style"], optional=True,
      desc=D(["&7Optionnel.&r Avec le temps, l'airain vire doucement du doré au rouge profond de l'Empire. Une couche de cire (rayon de miel) fige la teinte ; la hache la fait revenir en arrière."],
             ["&7Optional.&r Over time, airain slowly turns from gold to the Empire's deep red. A coat of wax (honeycomb) freezes the colour; an axe takes it back."]))
quest(cF, "fo_laitier", ("Rien ne se perd", "Nothing Is Wasted"), 2, 2, [T_item("airain:slag", 16)], [R_coin("sprocket", 1)],
      deps=["fo_fourneau"], optional=True,
      desc=D(["&7Optionnel.&r Le laitier sort par le trou de coulée (entonnoir). Broyé, il donne de la poudre de cendres ; remis au gueulard, il sert de fondant."],
             ["&7Optional.&r Slag comes out of the taphole (funnel). Crushed, it gives cinder flour; put back into the throat, it serves as flux."]))

quest(cF, "fo_passerelle", ("Au-dessus des machines", "Above the Machines"), 8, 1,
      [T_item("airain:airain_catwalk", 16), T_item("airain:airain_catwalk_stairs", 2)], [R_coin("cog", 1)], deps=["fo_style"],
      desc=D(["Dans les usines de l'Empire, on circulait au-dessus des machines. Passerelles, escaliers, rampes, poteaux et échelles d'airain : les rambardes se posent seules, la clé de Create les retire ou les remet."],
             ["In the Empire's factories people moved above the machines. Airain catwalks, stairs, ramps, supports and ladders: railings appear on their own, the Create wrench removes or restores them."]))
quest(cF, "fo_atelier", ("L'usine suspendue", "The Hanging Factory"), 10, 1,
      [T_item("airain:airain_catwalk_landing"), T_item("airain:airain_hanger", 2), T_item("airain:airain_railing", 4)], [R_coin("sprocket", 2)],
      deps=["fo_passerelle"], optional=True,
      desc=D(["&7Optionnel.&r L'escalier à palier tourne d'un quart de tour en montant d'un bloc, avec un palier à mi-hauteur qui se raccorde aux passerelles hautes. Les suspentes pendent les passerelles au plafond ; la rambarde seule borde n'importe quel bloc."],
             ["&7Optional.&r Landing stairs turn a quarter in climbing one block, with a half-height landing that joins high catwalks. Hangers hang catwalks from the ceiling; the standalone railing edges any block."]))
quest(cF, "fo_conduit", ("Le souffle de l'Empire", "The Empire's Breath"), 8, 2,
      [T_item("airain:airain_air_duct", 8), T_item("airain:airain_air_vent")], [R_coin("cog", 2)],
      deps=["fo_engrenage"],
      desc=D(["Un ventilateur de Create souffle dans un conduit d'air ; à l'autre bout, la bouche d'air rend exactement le même courant : même force, même portée, mêmes traitements, quelle que soit la longueur (64 conduits au plus).",
              "&8Les lunettes d'ingénieur montrent le courant transmis.&r"],
             ["A Create fan blows into an air duct; at the far end, the air vent gives back exactly the same current: same force, same range, same processing, whatever the length (64 ducts at most).",
              "&8Engineer's goggles show the transmitted current.&r"]))
quest(cF, "fo_tuyaux", ("La tuyauterie impériale", "Imperial Pipework"), 10, 2,
      [T_item("airain:airain_pipe", 8), T_item("airain:airain_pipe_valve"), T_item("airain:airain_gauge")], [R_coin("sprocket", 2)],
      deps=["fo_conduit"], optional=True,
      desc=D(["&7Optionnel.&r Des tuyaux d'airain qui se raccordent tout seuls, des vannes à volant (clic droit), et le manomètre : posé sur une machine de Create, une bouche d'air ou un réservoir, son aiguille suit la vitesse, le courant ou le remplissage.",
              "Le plancher technique cache tuyaux et conduits : la clé relève la dalle, on y loge l'objet ; un conduit logé reste dans le réseau d'air."],
             ["&7Optional.&r Airain pipes that connect by themselves, handwheel valves (right-click), and the gauge: placed on a Create machine, an air vent or a tank, its needle follows the speed, the current or the fill level.",
              "The raised floor hides pipes and ducts: the wrench lifts the plate, you lodge the item in; a lodged duct stays part of the air network."]))
quest(cF, "fo_lumieres", ("Les lumières de la capitale", "Lights of the Capital"), 10, -1,
      [T_item("airain:airain_lamppost", 3), T_item("airain:airain_pendant_lamp", 2), T_item("airain:airain_wall_lamp", 2)], [R_coin("sprocket", 2)],
      deps=["fo_style"], optional=True,
      desc=D(["&7Optionnel.&r Réverbères impériaux (empilez-les ; la clé sur la tête donne une ou deux lanternes), suspensions d'atelier, appliques à flamme rouge. Et le gyrophare, qui tourne sur un signal de redstone."],
             ["&7Optional.&r Imperial lampposts (stack them; the wrench on the head gives one or two lanterns), workshop pendant lamps, red-flame wall lamps. And the beacon light, which spins on a redstone signal."]))
quest(cF, "fo_rues", ("Les rues de l'Empire", "Streets of the Empire"), 12, 1,
      [T_item("airain:airain_signpost"), T_item("airain:airain_sign_plate", 3), T_item("airain:airain_workbench")], [R_coin("cog", 1)],
      deps=["fo_atelier"], optional=True,
      desc=D(["&7Optionnel.&r Bornes de carrefour (une étiquette renommée écrit sur la flèche, la clé la tourne), plaques émaillées (la clé change le pictogramme), toboggan, garde-corps vitré (la clé sur une rambarde), et l'établi d'atelier, dont la grille garde ses objets."],
             ["&7Optional.&r Crossroads signposts (a renamed name tag writes on the arrow, the wrench turns it), enamel signs (the wrench changes the pictogram), chutes, glass railings (the wrench on a railing), and the workshop bench, whose grid keeps its items."]))
# le Cœur demande de l'airain : « Forger le Cœur » dépend aussi de l'engrenage d'airain
[q for q in c6["quests"] if q["id"] == QUESTS["forger"]][0]["deps"].append(QUESTS["fo_engrenage"])

# =============================================================================
# TRAINS ET LOGISTIQUE
# =============================================================================
cT = chapter("trains", "13_trains", ("&3Annexe&r · Trains et logistique", "&3Side&r · Trains and Logistics"),
             ("Relier les ruines, transporter la production.", "Connect the ruins, haul the production."), "create:controls", 13)
quest(cT, "t_horaire", ("Les horaires", "Schedules"), 0, 0, [T_item("create:schedule")], [R_coin("sprocket", 2)], deps=["train"])
quest(cT, "t_portes", ("Portes de train", "Train Doors"), 2, -1, [T_item("create:train_door", 4)], [R_coin("sprocket", 1)], deps=["t_horaire"])
quest(cT, "t_observateur", ("Observateurs de voie", "Track Observers"), 2, 1, [T_item("create:track_observer", 2)], [R_coin("sprocket", 2)],
      deps=["t_horaire"])
quest(cT, "t_fret", ("Le train de marchandises", "The Freight Train"), 4, 0,
      [T_item("create:portable_storage_interface", 2), T_check()], [R_coin("cog", 2)], deps=["gare"],
      desc=D(["Un train qui charge et décharge seul à deux gares, grâce aux interfaces portables."], ["A train that loads and unloads by itself at two stations, using portable interfaces."]))
quest(cT, "t_fluides", ("Le train-citerne", "The Tanker Train"), 6, -1, [T_item("create:portable_fluid_interface", 2)], [R_coin("cog", 1)], deps=["t_fret"])
quest(cT, "t_triage", ("La gare de triage", "The Rail Yard"), 6, 1, [T_check()], [R_coin("cog", 3)], deps=["t_fret"],
      desc=D(["Au moins trois trains qui partagent les mêmes voies sans collision."], ["At least three trains sharing the same tracks without collisions."]))
quest(cT, "t_long", ("La grande ligne", "The Main Line"), 8, 0, [T_item("create:track", 1024)], [R_coin("crown", 1)], deps=["t_triage"])

# =============================================================================
# ARSENAL
# =============================================================================
cA = chapter("arsenal", "14_arsenal", ("&3Annexe&r · Arsenal et Écho", "&3Side&r · Arsenal and Echo"),
             ("Les armes de l'Empire, et sa technologie qui ressemble à des sorts.", "The Empire's weapons, and its technology that looks like spells."),
             "simplyswords:iron_longsword", 14)
quest(cA, "a_lance", ("La lance", "The Spear"), 0, -2, [T_item("simplyswords:iron_spear")], [R_coin("bevel", 4)], deps=["arme_fer"])
quest(cA, "a_katana", ("Le katana", "The Katana"), 2, -2, [T_item("simplyswords:iron_katana")], [R_coin("bevel", 4)], deps=["arme_fer"])
quest(cA, "a_claymore", ("La claymore de diamant", "The Diamond Claymore"), 4, -2, [T_item("simplyswords:diamond_claymore")], [R_coin("sprocket", 3)],
      deps=["armure_diamant"], desc=D(["Le manche est désormais une plaque de cuivre."], ["The grip is now a copper sheet."]))
quest(cA, "a_netherite", ("Une arme de netherite", "A Netherite Weapon"), 6, -2, [T_item("simplyswords:netherite_longsword")], [R_coin("cog", 2)],
      deps=["netherite", "bastion"])
quest(cA, "a_unique", ("Une arme unique", "A Unique Weapon"), 8, -2, [T_check()], [R_coin("cog", 3)], deps=["a_netherite"],
      desc=D(["Certaines armes n'ont jamais été fabriquées en série : on les trouve dans les coffres des donjons et des forteresses. Mettez la main sur une arme unique de Simply Swords, puis validez."],
             ["Some weapons were never mass-produced: they are found in the chests of dungeons and fortresses. Get your hands on a unique Simply Swords weapon, then tick the box."]))
quest(cA, "a_reglement", ("Le règlement des armes", "The Arms Regulations"), 0, -4, [T_item("airain:imperial_arms_regulations")], [R_coin("sprocket", 2)],
      deps=["laiton"], optional=True,
      desc=D(["&7Optionnel.&r Les officiers de l'Empire apprenaient leurs armes dans un règlement. Il décrit, page par page, les armes et les armures de fin de l'Empire : caractéristiques, pouvoirs, forge.",
              "Une page se remplit dès que quelqu'un de l'équipe porte l'arme. Le livre tient dans la reliure."],
             ["&7Optional.&r The Empire's officers learned their weapons from a book of regulations. Page by page, it describes the Empire's end-game weapons and armour: characteristics, powers, forging.",
              "A page fills in as soon as someone on the team carries the weapon. The book fits in the binder."]))
quest(cA, "a_traite", ("Le traité des armes de l'Écho", "The Treatise on the Echo Arms"), 2, -4, [T_item("airain:echo_arms_treatise")], [R_coin("sprocket", 2)],
      deps=["a_ars_source"], optional=True,
      desc=D(["&7Optionnel.&r Les Réfractaires ont recueilli tout ce qu'ils savaient des armes qu'on éveille avec l'Écho. Le traité les décrit une par une, avec leurs atours.",
              "Une page se remplit dès que quelqu'un de l'équipe porte l'arme. Le livre tient dans la reliure."],
             ["&7Optional.&r The Refractories gathered everything they knew about the weapons awakened with the Echo. The treatise describes them one by one, with their attire.",
              "A page fills in as soon as someone on the team carries the weapon. The book fits in the binder."]))
quest(cA, "a_obus", ("Obus spéciaux", "Special Shells"), 0, 1,
      [T_item("createbigcannons:ap_shot", 8), T_item("createbigcannons:shrapnel_shell", 8), T_item("createbigcannons:smoke_shell", 4)],
      [R_coin("cog", 2)], deps=["obus"])
quest(cA, "a_mortier", ("Le mortier", "The Mortar"), 2, 1, [T_item("createbigcannons:drop_mortar_shell", 8)], [R_coin("cog", 1)], deps=["a_obus"])
# =============================================================================
# LES ARCANES : la seconde voie (Ars Nouveau)
# =============================================================================
cR = chapter("arcanes", "08_arcanes", ("&dVoie de l'Écho&r · Les Arcanes", "&dEcho Path&r · The Arcana"),
             ("Ce que les Réfractaires ont appris, à l'écart de l'Empire.", "What the Refractories learned, far from the Empire."),
             "ars_nouveau:archmage_spell_book", 8)
SR = lambda fr, en: (fr, en)
# I · les premiers murmures
quest(cR, "ar_archebois", ("Les premiers murmures", "The First Whispers"), 0, 0, [T_item("ars_nouveau:archwood_planks", 16)], [R_coin("bevel", 4)],
      deps=["a_ars_livre"], subtitle=("I · Les premiers murmures", "I · The First Whispers"),
      desc=D(["« L'Écho est plus fort là où les arbres changent de couleur. » Trouvez une forêt d'archebois : bleu, rouge, vert ou violet, chaque teinte chante autrement."],
             ["\"The Echo is strongest where the trees change colour.\" Find an archwood forest: blue, red, green or purple, each hue sings differently."]))
quest(cR, "ar_bocal", ("Un bocal de source", "A Source Jar"), 2, 0, [T_item("ars_nouveau:source_jar")], [R_coin("bevel", 4)], deps=["ar_archebois"],
      desc=D(["L'Écho qu'on capte doit bien aller quelque part. Les Réfractaires le gardaient dans des bocaux, comme on garde une braise."],
             ["The Echo you capture has to go somewhere. The Refractories kept it in jars, the way you keep an ember."]))
quest(cR, "ar_magebloom", ("La fleur des mages", "The Mage's Flower"), 4, 0, [T_item("ars_nouveau:magebloom", 4)], [R_coin("bevel", 4)], deps=["ar_archebois"],
      desc=D(["La magebloom ne pousse que sur une terre imprégnée. Ses fibres tissent les robes des Arcanes."],
             ["Magebloom only grows on imbued soil. Its fibres weave the robes of the Arcana."]))
# II · nourrir l'Écho
quest(cR, "ar_sourcelinks", ("Nourrir l'Écho", "Feeding the Echo"), 2, 2,
      [T_item("ars_nouveau:agronomic_sourcelink"), T_item("ars_nouveau:volcanic_sourcelink")], [R_coin("sprocket", 2), R_carnet(2)], deps=["ar_bocal"],
      subtitle=("II · Nourrir l'Écho", "II · Feeding the Echo"),
      desc=D(["On ne prend pas l'Écho, on le nourrit : les plantes qui poussent, la lave qui brûle. Ce qui vit lui rend un peu de ce que l'Empire lui a volé.",
              "&8Récompense : une page du carnet de l'apprentie.&r"],
             ["You don't take the Echo, you feed it: growing plants, burning lava. What lives gives back a little of what the Empire stole from it.",
              "&8Reward: a page of the apprentice's notebook.&r"]))
quest(cR, "ar_relais", ("Des relais qui laissent partir", "Relays That Let Go"), 4, 2, [T_item("ars_nouveau:relay", 2)], [R_coin("sprocket", 2)], deps=["ar_sourcelinks"],
      desc=D(["« Nos relais ne retiennent personne. Ils transmettent, puis ils laissent partir. » Ceux de l'Empire, eux, n'ont jamais rendu ce qu'ils portaient."],
             ["\"Our relays hold no one. They pass things on, then they let go.\" The Empire's never gave back what they carried."]))
# III · le grimoire
quest(cR, "a_ars_table", ("La table du scribe", "The Scribe's Table"), 0, 4, [T_item("ars_nouveau:scribes_table")], [R_coin("cog", 1), R_carnet(3)],
      deps=["a_ars_livre"], subtitle=("III · Le grimoire", "III · The Spell Book"),
      desc=D(["Pour inscrire de nouveaux glyphes dans votre grimoire.", "&8Récompense : une page du carnet de l'apprentie.&r"],
             ["To inscribe new glyphs into your spell book.", "&8Reward: a page of the apprentice's notebook.&r"]))
quest(cR, "ar_glyphes", ("Trois volontés", "Three Wills"), 2, 4,
      [T_item("ars_nouveau:glyph_break"), T_item("ars_nouveau:glyph_heal"), T_item("ars_nouveau:glyph_light")], [R_coin("cog", 1)], deps=["a_ars_table"],
      desc=D(["Briser, soigner, éclairer. « Morgana disait qu'on juge un mage à son premier sort de soin. »"],
             ["Break, heal, light. \"Morgana used to say you judge a mage by their first healing spell.\""]))
# IV · l'atelier réfractaire
quest(cR, "a_ars_appareil", ("L'appareil d'enchantement", "The Enchanting Apparatus"), 0, 6,
      [T_item("ars_nouveau:enchanting_apparatus"), T_item("ars_nouveau:arcane_core")], [R_coin("cog", 1)], deps=["a_ars_table"],
      subtitle=("IV · L'atelier réfractaire", "IV · The Refractory Workshop"),
      desc=D(["Le cœur de tout atelier réfractaire : il lie l'Écho aux objets."], ["The heart of every Refractory workshop: it binds the Echo to objects."]))
quest(cR, "ar_brasero", ("Le brasero rituel", "The Ritual Brazier"), 2, 6, [T_item("ars_nouveau:ritual_brazier")], [R_coin("cog", 1)], deps=["a_ars_appareil"],
      desc=D(["Certaines volontés sont trop grandes pour un grimoire. On les confie au feu."], ["Some wills are too great for a spell book. They are entrusted to the fire."]))
quest(cR, "ar_rituel", ("Ouvrir le ciel", "Opening the Sky"), 4, 6, [T_item("ars_nouveau:ritual_cloudshaping"), T_check()], [R_coin("cog", 2), R_carnet(4)],
      deps=["ar_brasero"],
      desc=D(["Un rituel des nuages, posé sur le brasero. Validez une fois le ciel changé.",
              "&8Récompense : une page du carnet de l'apprentie.&r"],
             ["A cloudshaping ritual, placed on the brazier. Tick once the sky has changed.",
              "&8Reward: a page of the apprentice's notebook.&r"]))
# V · les petits Échos
quest(cR, "ar_starbuncle", ("Le petit être jaune", "The Little Yellow One"), 2, 8, [T_item("ars_nouveau:starbuncle_charm")], [R_coin("cog", 1), R_carnet(5)],
      deps=["a_ars_appareil"], subtitle=("V · Les petits Échos", "V · The Little Echoes"),
      desc=D(["« Certains égarés étaient trop petits pour garder une forme humaine. Ils ont pris celle qu'ils ont pu. »",
              "Le Starbuncle porte les objets d'un coffre à l'autre. Il fera ça très bien pour vos machines.",
              "&8Récompense : une page du carnet de l'apprentie.&r"],
             ["\"Some of the lost were too small to keep a human shape. They took whatever shape they could.\"",
              "The Starbuncle carries items from one chest to another. It will do that very well for your machines.",
              "&8Reward: a page of the apprentice's notebook.&r"]))
quest(cR, "ar_drygmy", ("Le Drygmy", "The Drygmy"), 4, 8, [T_item("ars_nouveau:drygmy_charm")], [R_coin("cog", 1)], deps=["ar_starbuncle"],
      desc=D(["Il récolte ce que laissent les bêtes, sans leur faire de mal. Les Réfractaires ne tuaient pas pour manger quand ils pouvaient l'éviter."],
             ["It gathers what animals leave behind, without harming them. The Refractories did not kill to eat when they could avoid it."]))
quest(cR, "ar_whirlisprig", ("Le Whirlisprig", "The Whirlisprig"), 6, 8, [T_item("ars_nouveau:whirlisprig_charm")], [R_coin("cog", 1)], deps=["ar_starbuncle"],
      desc=D(["Là où il danse, les plantes poussent. Il nourrit l'Écho en retour."], ["Where it dances, plants grow. It feeds the Echo in return."]))
quest(cR, "ar_wixie", ("Le Wixie", "The Wixie"), 8, 8, [T_item("ars_nouveau:wixie_charm")], [R_coin("cog", 1)], deps=["ar_starbuncle"],
      desc=D(["Un petit alchimiste au chaudron. Il se souvient de recettes que personne ne lui a apprises."], ["A small alchemist at the cauldron. It remembers recipes no one ever taught it."]))
quest(cR, "ar_golem", ("Le golem d'améthyste", "The Amethyst Golem"), 10, 8, [T_item("ars_nouveau:amethyst_golem_charm")], [R_coin("cog", 1)], deps=["ar_starbuncle"],
      desc=D(["Un gardien de cristal qui fait pousser l'améthyste. Le seul golem que l'Empire n'a jamais construit."],
             ["A crystal guardian that grows amethyst. The only golem the Empire never built."]))
# VI · la robe des Arcanes
quest(cR, "a_ars_apprenti", ("Le grimoire d'apprenti", "The Apprentice Spell Book"), 2, 10, [T_item("ars_nouveau:apprentice_spell_book")],
      [R_coin("cog", 2), R_carnet(6)], deps=["a_ars_appareil"], subtitle=("VI · La robe des Arcanes", "VI · The Robe of the Arcana"),
      desc=D(["Plus de place, plus de puissance.", "&8Récompense : une page du carnet de l'apprentie.&r"],
             ["More room, more power.", "&8Reward: a page of the apprentice's notebook.&r"]))
quest(cR, "ar_robe", ("La robe des Arcanes", "The Robe of the Arcana"), 4, 10, [T_check()], [R_coin("cog", 2)], deps=["a_ars_apprenti"],
      desc=D(["Une armure de mage complète (sorcier, arcaniste ou mage de bataille). Validez une fois vêtu.",
              "« On ne porte pas la robe pour se protéger. On la porte pour que les égarés nous reconnaissent. »"],
             ["A full set of mage armor (sorcerer, arcanist or battlemage). Tick once you wear it.",
              "\"You don't wear the robe to protect yourself. You wear it so the lost recognise you.\""]))
quest(cR, "ar_fil", ("Un fil d'Écho", "A Thread of Echo"), 6, 10, [T_check()], [R_coin("cog", 1)], deps=["ar_robe"],
      desc=D(["Glissez un fil d'amélioration dans une pièce de votre robe (à l'appareil d'enchantement). Validez quand c'est fait."],
             ["Slip an upgrade thread into a piece of your robe (at the enchanting apparatus). Tick when done."]))
quest(cR, "a_ars_archimage", ("Le grimoire d'archimage", "The Archmage Spell Book"), 8, 10, [T_item("ars_nouveau:archmage_spell_book")],
      [R_coin("crown", 1)], deps=["a_ars_apprenti"],
      desc=D(["Les chefs réfractaires en portaient un. Avec lui, on parle presque aux esprits perdus."],
             ["Refractory leaders carried one. With it, you can almost speak to the lost minds."]))
# VII · les bêtes de l'Écho
quest(cR, "ar_chasseur", ("Le chasseur", "The Hunter"), 2, 12, [T_kill("ars_nouveau:wilden_hunter")], [R_coin("cog", 1)], deps=["ar_glyphes"],
      subtitle=("VII · Les bêtes de l'Écho", "VII · The Beasts of the Echo"),
      desc=D(["Les Wildens sont des égarés qui ont trop longtemps erré dans la nature. Ils ne reconnaissent plus personne."],
             ["Wildens are lost minds that wandered the wild for too long. They no longer recognise anyone."]))
quest(cR, "ar_rodeur", ("Le rôdeur", "The Stalker"), 4, 12, [T_kill("ars_nouveau:wilden_stalker")], [R_coin("cog", 1)], deps=["ar_chasseur"],
      desc=D(["Il attaque en piqué, depuis les hauteurs. Gardez un sort prêt."], ["It dives from above. Keep a spell ready."]))
quest(cR, "ar_gardien", ("Le gardien wilden", "The Wilden Guardian"), 6, 12, [T_kill("ars_nouveau:wilden_guardian")], [R_coin("cog", 2), R_carnet(7)],
      deps=["ar_rodeur"],
      desc=D(["Couvert d'épines, il les lance en se roulant en boule. Le plus grand d'entre eux, le &5Chœur des Égarés&r, attend au Grand Relais (Échos perdus).",
              "&8Récompense : la dernière page du carnet de l'apprentie.&r"],
             ["Covered in spines, it hurls them as it curls up. The greatest of them, the &5Choir of the Lost&r, waits at the Great Relay (Lost Echoes).",
              "&8Reward: the last page of the apprentice's notebook.&r"]))

# =============================================================================
# EXPLORATION
# =============================================================================
cE = chapter("exploration", "15_exploration", ("&3Annexe&r · Exploration", "&3Side&r · Exploration"),
             ("Cartographier ce que l'Empire a laissé derrière lui.", "Mapping what the Empire left behind."), "minecraft:filled_map", 15)
quest(cE, "e_avantposte", ("Le camp réfractaire", "The Refractory Camp"), 0, 0, [T_struct("kubejs:avant_poste_refractaire")], [R_coin("bevel", 4)], deps=["outils"],
      desc=D(["Une palissade, des tentes rouges, un automate abattu exposé comme un trophée. Ici, on n'aime pas l'Empire."],
             ["A palisade, red tents, a felled automaton displayed like a trophy. Nobody here loves the Empire."]))
quest(cE, "e_pyramide", ("Le temple du désert", "The Desert Temple"), 2, -1, [T_struct("minecraft:desert_pyramid")], [R_coin("bevel", 4)], deps=["outils"])
quest(cE, "e_epave", ("L'épave", "The Shipwreck"), 2, 1, [T_struct("minecraft:shipwreck")], [R_coin("bevel", 4)], deps=["outils"],
      desc=D(["Les épaves cachent des cartes au trésor : le cœur de la mer est au bout."], ["Shipwrecks hide treasure maps: the heart of the sea is at the end."]))
quest(cE, "e_fortin", ("Le fort souterrain", "The Stronghold"), 4, -1, [T_struct("minecraft:stronghold")], [R_coin("sprocket", 2)], deps=["e_pyramide"])
quest(cE, "e_cite", ("La cité antique", "The Ancient City"), 4, 1, [T_struct("minecraft:ancient_city")], [R_coin("cog", 1)], deps=["e_epave"],
      desc=D(["Une cité engloutie dans les ténèbres. &cSilence absolu recommandé.&r"], ["A city swallowed by darkness. &cTotal silence recommended.&r"]))
quest(cE, "e_forteresse", ("La forteresse du Nether", "The Nether Fortress"), 6, -1, [T_struct("minecraft:fortress")], [R_coin("sprocket", 3)], deps=["nether"])
quest(cE, "e_manoir", ("La station de capsules", "The Capsule Station"), 6, 1, [T_struct("kubejs:station_capsules")], [R_coin("cog", 2)], deps=["e_cite"],
      optional=True,
      desc=D(["Un hall plein de capsules vides, et des câbles qui plongent dans un puits. Descendez lire le rapport de l'ingénieur."],
             ["A hall full of empty capsules, and cables plunging into a shaft. Go down and read the engineer's report."]))
quest(cE, "e_cite_meca", ("La cité mécanique", "The Mechanical City"), 8, 2, [T_struct("kubejs:cite_mecanique")], [R_coin("cog", 3)], deps=["e_manoir"],
      optional=True,
      desc=D(["Rare et immense : une ville entière de l'Empire, sa tour d'horloge, plusieurs marchés et les trois salles scellées."],
             ["Rare and huge: a whole Empire town, its clock tower, several markets and all three sealed rooms."]))
quest(cE, "e_donjons", ("Les donjons surgis", "The Risen Dungeons"), 8, 0, [T_check()], [R_coin("cog", 3)], deps=["e_forteresse", "e_manoir"],
      desc=D(["Explorez trois grandes structures de When Dungeons Arise (forteresses volantes, cités en ruine…). Validez à la troisième."],
             ["Explore three large When Dungeons Arise structures (floating fortresses, ruined cities…). Tick at the third."]))

# --- armes à feu de Create: Gunsmithing (la progression de Create les place déjà : silex au ch. II, le reste au laiton)
quest(cA, "a_silex", ("Le pistolet à silex", "The Flintlock"), 0, 5, [T_item("cgs:flintlock")], [R_coin("sprocket", 2)], deps=["plaques"],
      desc=D(["La première arme à feu de l'Empire : plaques de fer, alliage d'andésite, un briquet. Elle tire des cartouches de papier (balles de plomb, poudre, papier)."],
             ["The Empire's first firearm: iron sheets, andesite alloy, a flint and steel. It fires paper shots (lead balls, gunpowder, paper)."]))
quest(cA, "a_revolver", ("Le revolver", "The Revolver"), 2, 5, [T_item("cgs:revolver")], [R_coin("cog", 1)], deps=["a_silex", "crafter"],
      desc=D(["Se fabrique à l'assembleur mécanique avec des plaques de laiton et de l'acier.",
              "L'acier se mélange au malaxeur sur un brûleur surchauffé (gâteau de blaze) : fer et poussière de charbon de bois."],
             ["Made in the mechanical crafter with brass sheets and steel.",
              "Steel is mixed on a superheated blaze burner (blaze cake): iron and charcoal dust."]))
quest(cA, "a_fusil", ("Le fusil à pompe", "The Shotgun"), 4, 5, [T_item("cgs:shotgun")], [R_coin("cog", 1)], deps=["a_revolver"])
quest(cA, "a_gatling", ("La gatling", "The Gatling"), 6, 5, [T_item("cgs:gatling")], [R_coin("cog", 2)], deps=["a_fusil", "precision"],
      desc=D(["Un mécanisme de précision, un tambour, et l'Empire n'a plus besoin de soldats."],
             ["A precision mechanism, a drum, and the Empire no longer needs soldiers."]))
quest(cA, "a_blazegun", ("Le lance-flammes à blaze", "The Blazegun"), 8, 5, [T_item("cgs:blazegun")], [R_coin("cog", 2)], deps=["a_revolver", "blaze"],
      desc=D(["Un brûleur à blaze dans une crosse de bois. Ce n'est pas prudent. C'est très efficace."],
             ["A blaze burner in a wooden stock. It isn't safe. It is very effective."]))

# --- Hypertubes : les tubes se fabriquent librement, poser une entrée demande le Grand Chantier pneumatique
quest(cT, "t_pneumatique", ("Grand Chantier : le réseau pneumatique", "Great Work: The Pneumatic Network"), 4, 3,
      [T_item("create:brass_sheet", 64, consume=True), T_item("create:smart_chute", 8, consume=True), T_item("create:precision_mechanism", 4, consume=True)],
      [R_tag("airain_pneumatique"), R_coin("cog", 2)], deps=["reseau"], shape="hexagon", size=1.5,
      subtitle=("Débloque les entrées d'Hypertubes", "Unlocks Hypertube entrances"),
      desc=D(["Sous les cités, l'Empire envoyait ses ingénieurs d'un atelier à l'autre par des tubes de verre et de laiton. Rouvrez le réseau.",
              "Les tubes se fabriquent dès maintenant ; seules les entrées attendent ce chantier."],
             ["Beneath its cities, the Empire sent its engineers from one workshop to the next through tubes of glass and brass. Reopen the network.",
              "Tubes can be crafted already; only the entrances wait for this work."]))
quest(cT, "t_tube", ("Le premier tube", "The First Tube"), 6, 3, [T_item("create_hypertube:hypertube_entrance", 2), T_check()], [R_coin("cog", 1)],
      deps=["t_pneumatique"],
      desc=D(["Deux entrées alimentées par un engrenage, reliées par des tubes. Validez quand vous avez fait le trajet."],
             ["Two entrances powered by a cogwheel, linked by tubes. Tick the box once you've made the trip."]))
# Ender Transmission : transmetteurs entre dimensions, recettes verrouillées derrière le dragon (carapaces de shulker)
quest(cT, "t_ender", ("Par-delà les dimensions", "Beyond the Dimensions"), 0, 7,
      [T_item("createendertransmission:item_transmitter")], [R_coin("cog", 2)], deps=["dragon"],
      desc=D(["Les ingénieurs de l'Empire savaient faire passer la matière d'un monde à l'autre : un transmetteur envoie objets, fluides ou rotation à tous ceux réglés sur la même fréquence, quelle que soit la dimension.",
              "&8Assembleur mécanique. Il faut des carapaces de shulker, qu'on ne trouve qu'au-delà de la passerelle ouverte par la mort du dragon.&r"],
             ["The Empire's engineers knew how to send matter from one world to another: a transmitter sends items, fluids or rotation to every transmitter tuned to the same frequency, whatever the dimension.",
              "&8Mechanical crafter. It needs shulker shells, found only beyond the gateway opened by the dragon's death.&r"]))

# =============================================================================
# BESTIAIRE
# =============================================================================
cB = chapter("bestiaire", "16_bestiaire", ("&3Annexe&r · Bestiaire", "&3Side&r · Bestiary"),
             ("Les machines de l'Empire, en défi facultatif.", "The Empire's machines, as optional challenges."), "create:brass_casing", 16)
for i, (k, ent, title, desc) in enumerate([
        ("b_araignee", "mebahelcreaturesdwarven:dwarven_spider", ("L'araignée de bronze", "The Bronze Spider"),
         ("Le modèle le plus répandu des vieilles usines de bronze.", "The most common model in the old bronze works.")),
        ("b_sphere", "mebahelcreaturesdwarven:dwarven_sphere", ("La sphère", "The Sphere"),
         ("Repliée, elle roule. Déployée, elle se bat.", "Folded, it rolls. Unfolded, it fights.")),
        ("b_gardienne", "mebahelcreaturesdwarven:dwarven_spider_guardian", ("L'araignée gardienne", "The Guardian Spider"),
         ("Elle garde les portes des cités de bronze.", "It guards the gates of the bronze cities.")),
        ("b_centurion", "mebahelcreaturesdwarven:dwarven_centurion", ("Le centurion", "The Centurion"),
         ("Un colosse à vapeur. Il crache de la vapeur brûlante avant de frapper.", "A steam colossus. It spits scalding steam before it strikes.")),
        ("b_wroughtnaut", "mowziesmobs:ferrous_wroughtnaut", ("Le colosse de fer", "The Iron Colossus"),
         ("Une armure vide qui attend un ordre.", "An empty suit of armor awaiting an order.")),
        ("b_golem", "cataclysm:ender_golem", ("Le golem de l'End", "The Ender Golem"),
         ("Un gardien de pierre et de vide, qui ne dort jamais.", "A guardian of stone and void that never sleeps.")),
        ("b_rodeur", "cataclysm:the_prowler", ("Le rôdeur", "The Prowler"),
         ("Une machine de guerre de l'usine ancienne.", "A war machine from the ancient factory.")),
        ("b_veilleur", "cataclysm:the_watcher", ("Le veilleur", "The Watcher"),
         ("Un drone de surveillance. Il ne vient jamais seul.", "A surveillance drone. It never comes alone."))]):
    quest(cB, k, title, (i % 4) * 2, (i // 4) * 2, [T_kill(ent)], [R_coin("cog" if i < 5 else "crown", 2 if i < 5 else 1)],
          deps=["nether"], optional=True, desc=D(["&7Optionnel.&r " + desc[0]], ["&7Optional.&r " + desc[1]]))

# trophées de l'Empire (mod Airain 1.5) : un trophée exposé = un effet permanent pour toute l'équipe
quest(cB, "b_socle", ("Le socle de l'Empire", "The Empire Pedestal"), 0, 4, [T_item("airain:trophy_pedestal")], [R_coin("cog", 1)],
      deps=["nether"], optional=True,
      desc=D(["&7Optionnel.&r Exposez un trophée de boss sur un socle : tant qu'il y reste, son effet profite à &6toute l'équipe&r, où que vous soyez.",
              "• Masque des enfers : résistance au feu ;", "• Cœur du Gardien des enfers : régénération ;",
              "• Œuf du Gardien des Cieux : aucun dégât de chute ;", "• Écho primordial : vision nocturne.",
              "&6Accroupi + clic droit main vide&r : les réglages du socle. Matériau, velours et capitonnage, garnitures, colonne haute, présentation du trophée (lévitation, posé, chevalet, sous cloche), éclairage, particules et plaque gravée. La plaque se grave seule, au nom du trophée et au jour de la victoire.",
              "&8Deux trophées identiques ne cumulent pas. Clic droit main vide pour reprendre le trophée. Un comparateur lit le socle : plus le trophée donne d'effets, plus le signal est fort. Un gabarit de bannière copie aussi l'apparence d'un socle.&r"],
             ["&7Optional.&r Display a boss trophy on a pedestal: as long as it stays there, its effect benefits &6the whole team&r, wherever you are.",
              "• Infernal Mask: fire resistance;", "• Infernal Guardian Core: regeneration;",
              "• Sky Guardian's Egg: no fall damage at all;", "• Primordial Echo: night vision.",
              "&6Sneak + right-click empty-handed&r: the pedestal settings. Material, velvet and tufting, trims, tall column, trophy display (levitating, resting, easel, under a glass dome), lighting, particles and engraved plaque. The plaque engraves itself with the trophy's name and the day of the victory.",
              "&8Two identical trophies do not stack. Right-click empty-handed to take the trophy back. A comparator reads the pedestal: the more effects the trophy gives, the stronger the signal. A banner template also copies a pedestal's look.&r"]))
quest(cB, "b_trophees", ("La salle des trophées", "The Trophy Room"), 2, 4, [T_check()], [R_coin("crown", 1), R_xp(1000)],
      deps=["b_socle"], optional=True,
      desc=D(["&7Optionnel.&r Les palais de l'Empire exposaient leurs trophées sous les bannières de leurs fondateurs. Exposez quatre trophées différents dans votre base. Validez quand c'est fait.",
              "&8Le registre des fondations recense aussi vos trophées exposés, et les bannières réglées « selon trophées » se hissent quand un trophée est exposé dans leur zone.&r"],
             ["&7Optional.&r The Empire's palaces displayed their trophies under their founders' banners. Display four different trophies in your base. Tick the box when done.",
              "&8The foundation register also lists your displayed trophies, and banners set to \"by trophies\" are hoisted when a trophy is displayed in their area.&r"]))

# améliorations de capitale (après la fin, l'une ou l'autre)
_CAP_FR = "&7Optionnel, après la fin.&r Posez les plans sur l'étendard de votre &6capitale&r (impériale ou arcanique) : le prix en &6soleils&r est prélevé dans votre inventaire, la monnaie est rendue. Un plan par niveau."
_CAP_EN = "&7Optional, after the ending.&r Use the plans on your &6capital&r's standard (imperial or arcane): the price in &6suns&r is taken from your inventory, change is given back. One plan per level."
for _k, _it, _t, _x, _fr, _en in [
    ("c_agrandissement", "expansion_plans", ("Repousser les murs", "Pushing the Walls"), 1,
     ["Une capitale ne tient jamais dans ses premières limites.", "&6Agrandissement&r, 3 niveaux (4, 8 puis 16 soleils) : zone de 224, 256 puis 320 blocs, et un gardien de plus à chaque niveau (jusqu'à 9)."],
     ["A capital never fits within its first bounds.", "&6Expansion&r, 3 levels (4, 8 then 16 suns): 224, 256 then 320-block zone, and one more guardian per level (up to 9)."]),
    ("c_infirmerie", "infirmary_plans", ("L'infirmerie", "The Infirmary"), 3,
     ["Les médecins de l'Empire soignaient les ouvriers comme on huile une machine : souvent, et avant la panne.", "&6Infirmerie&r, 2 niveaux (3 puis 8 soleils) : Régénération I dans toute la zone et soin des gardiens, puis Régénération II qui chasse aussi poison et flétrissure."],
     ["The Empire's physicians tended workers the way one oils a machine: often, and before it breaks.", "&6Infirmary&r, 2 levels (3 then 8 suns): Regeneration I across the zone and guardian healing, then Regeneration II that also clears poison and wither."]),
    ("c_meteo", "weather_station_plans", ("La station météo", "The Weather Station"), 5,
     ["Paratonnerres, girouettes et baromètres : la capitale ne subit plus le ciel, elle le règle.", "&6Station météo&r, 2 niveaux (2 puis 6 soleils) : &6accroupi + clic droit main vide&r sur l'étendard pour le beau temps ou la pluie, une fois par jour ; puis l'orage aussi, toutes les 5 minutes. Surface seulement."],
     ["Lightning rods, weathervanes and barometers: the capital no longer suffers the sky, it sets it.", "&6Weather station&r, 2 levels (2 then 6 suns): &6sneak + right-click empty-handed&r on the standard for clear weather or rain, once a day; then thunder too, every 5 minutes. Overworld only."]),
    ("c_forge", "garrison_forge_plans", ("La forge de garnison", "The Garrison Forge"), 7,
     ["Une garnison qui rentre ébréchée repart affûtée.", "&6Forge de garnison&r, 2 niveaux (3 puis 8 soleils) : l'équipement porté se répare lentement dans la zone, puis trois fois plus vite, barre d'action comprise."],
     ["A garrison that comes home chipped leaves sharpened.", "&6Garrison forge&r, 2 levels (3 then 8 suns): worn gear slowly repairs in the zone, then three times faster, hotbar included."]),
]:
    quest(cB, _k, _t, _x, 6, [T_item("airain:" + _it)], [R_xp(1500)], deps=["f_empire", "f_echo"], dep_un=True, optional=True,
          icon="airain:" + _it, desc=D(_fr + [_CAP_FR], _en + [_CAP_EN]))

# =============================================================================
# LES ÉCHOS PERDUS (la voie de l'Écho : le lore, puis le boss)
# =============================================================================
cL = chapter("echos", "17_echos_perdus", ("&dAnnexe&r · Les Échos perdus", "&dSide&r · The Lost Echoes"),
             ("Ce que l'Empire a voulu taire. Et ceux qui attendent encore d'être libérés.",
              "What the Empire tried to silence. And those still waiting to be freed."), "kubejs:echo_primordial", 17)
quest(cL, "l_vael", ("Le rapport de Vael", "Vael's Report"), 4, 0, [T_struct("kubejs:station_capsules"), lire()],
      [R_coin("sprocket", 2)], deps=["l_relais"],
      desc=D(["Descendez au fond d'une station de capsules et lisez le rapport de l'ingénieur Elias Vael.",
              "Dans le coffre du collecteur, une lettre attend toujours d'être ouverte."],
             ["Go down to the bottom of a capsule station and read engineer Elias Vael's report.",
              "In the collector's chest, a letter is still waiting to be opened."]))
quest(cL, "l_essai", ("L'essai 41", "Trial 41"), 6, 0, [T_struct("kubejs:cite_mecanique"), lire()],
      [R_coin("cog", 1)], deps=["l_vael"],
      desc=D(["Dans une cité mécanique, trouvez un laboratoire d'essais et lisez le journal de sa salle souterraine."],
             ["In a mechanical city, find a test laboratory and read the journal in its underground room."]))
quest(cL, "l_resonance", ("Résonance", "Resonance"), 8, 2, [T_item("kubejs:fragment_resonance", 4)],
      [R_xp(300)], deps=["l_sanctuaire"],
      desc=D(["Les âmes sans repos (les fantômes des nuits sans sommeil) laissent parfois un &dfragment de résonance&r. Les relais brisés et le sanctuaire en cachent aussi."],
             ["Restless souls (the phantoms of sleepless nights) sometimes drop a &dresonance fragment&r. Broken relays and the sanctuary hide some too."]))
quest(cL, "l_diapason", ("Le diapason", "The Tuning Fork"), 6, 2, [T_item("kubejs:diapason_echo")],
      [R_xp(300)], deps=["l_resonance"],
      desc=D(["La recette d'Ada : quatre fragments de résonance, une gemme d'Écho et un lingot d'or."],
             ["Ada's recipe: four resonance fragments, an echo gem and a gold ingot."]))
quest(cL, "l_grand_relais", ("Le Grand Relais", "The Great Relay"), 4, 2, [T_struct("kubejs:grand_relais")],
      [R_coin("cog", 2)], deps=["l_diapason"],
      desc=D(["Là où la ligne principale du Transfert a cédé. Le résonateur, une pierre d'aimant posée sur de l'ardoise renforcée, se dresse près du pylône effondré.",
              "&cPréparez-vous avant de frapper le diapason : le Chœur est redoutable. Équipement du chapitre V conseillé, à deux.&r"],
             ["Where the Transfer's main line gave way. The resonator, a lodestone set on reinforced deepslate, stands near the collapsed pylon.",
              "&cPrepare before striking the fork: the Choir is formidable. Chapter V gear recommended, as a pair.&r"]))
quest(cL, "l_choeur", ("Le Chœur des Égarés", "The Choir of the Lost"), 2, 2, [T_kill("ars_nouveau:wilden_boss")],
      [R_xp(2000), R_coin("crown", 1)], deps=["l_grand_relais"], shape="hexagon", size=2.0,
      subtitle=("&5Boss de l'Écho&r", "&5Echo boss&r"),
      desc=D(["Frappez le diapason sur le résonateur (clic droit). Des milliers d'esprits fusionnés dans la douleur se réveillent.",
              "Les vaincre, c'est les libérer."],
             ["Strike the fork on the resonator (right-click). Thousands of minds, fused in pain, awaken.",
              "Defeating them is freeing them."]))
quest(cL, "l_primordial", ("L'Écho primordial", "The Primordial Echo"), 0, 2, [T_item("kubejs:echo_primordial")],
      [R_xp(1000)], deps=["l_choeur"], shape="gear", size=1.5,
      desc=D(["Ils vous ont confié ce qu'ils étaient.",
              "&dL'Écho primordial&r entre dans la fabrication des sorts les plus puissants : explosion, foudre, maléfice, flétrissement, persistance, mur et rafale.",
              "Et les machines ne le sentent pas : vos sorts infligent &650 % de dégâts en plus&r aux machines de l'Empire, même les plus grandes."],
             ["They entrusted you with what they were.",
              "&dThe Primordial Echo&r is needed to craft the most powerful spells: explosion, lightning, hex, wither, linger, wall and burst.",
              "And machines cannot feel it: your spells deal &650% more damage&r to the Empire's machines, even the greatest."]))

# =============================================================================
# NOUVELLES QUÊTES : archives, ligne impériale, fret aérien, records
# =============================================================================

DOCS = [("vael", ("Le rapport de l'ingénieur Vael", "Engineer Vael's report")),
        ("lettre", ("La lettre d'Ada", "Ada's letter")),
        ("incident", ("Le rapport d'incident", "The incident report")),
        ("essais", ("Le journal d'essais", "The trial log")),
        ("ada", ("Le journal d'Ada Vesper", "Ada Vesper's journal")),
        ("refractaire", ("Un écrit réfractaire", "A Refractory writing")),
        ("cache", ("L'inventaire d'une cache", "A cache inventory"))]
quest(cE, "e_archives", ("Les archives de l'Empire", "The Empire's Archives"), 10, 1, [T_doc(d) for d, _ in DOCS],
      [R_coin("crown", 1), R_xp(1000)], deps=["e_avantposte"], optional=True,
      subtitle=("Rassembler tous les écrits", "Gather every writing"),
      desc=D(["&7Optionnel.&r Ceux qui ont vécu la fin de l'Empire ont laissé des écrits. Rassemblez-les tous dans votre inventaire (ils ne sont pas consommés) :",
              "• le rapport de Vael, sur le pupitre d'une station de capsules ;",
              "• la lettre d'Ada, dans le coffre du collecteur de la même station ;",
              "• le rapport d'incident, sur le pupitre d'un relais brisé ;",
              "• le journal d'essais, dans le laboratoire d'une cité mécanique ;",
              "• le journal d'Ada Vesper, dans le sanctuaire réfractaire ;",
              "• un écrit réfractaire, dans les coffres des camps ;",
              "• l'inventaire d'une cache, enterrée sous la croix d'une carte réfractaire (cartes trouvées dans les camps).",
              "&8Les structures générées avant cette mise à jour gardent d'anciens exemplaires, non reconnus : cherchez-en de nouvelles.&r"],
             ["&7Optional.&r Those who lived through the end of the Empire left writings behind. Gather them all in your inventory (they are not consumed):",
              "• Vael's report, on the lectern of a capsule station;",
              "• Ada's letter, in the collector's chest of the same station;",
              "• the incident report, on the lectern of a broken relay;",
              "• the trial log, in the laboratory of a mechanical city;",
              "• Ada Vesper's journal, in the Refractory sanctuary;",
              "• a Refractory writing, in the camps' chests;",
              "• a cache inventory, buried under the cross of a Refractory map (maps found in the camps).",
              "&8Structures generated before this update keep older copies that are not recognized: look for new ones.&r"]))
titres_taches("e_archives", [t for _, t in DOCS])

TRACES = [("mine", ("Le carnet de mineur", "The miner's notebook"), ("puits de mine abandonnés et donjons", "abandoned mineshafts and dungeons")),
          ("prospecteur", ("La lettre d'un prospecteur", "A prospector's letter"), ("temples du désert et de la jungle, igloos", "desert and jungle temples, igloos")),
          ("cargaison", ("Le manifeste de cargaison", "The cargo manifest"), ("épaves, trésors enfouis, ruines sous-marines", "shipwrecks, buried treasure, ocean ruins")),
          ("conseil", ("Le registre du Conseil", "The Council register"), ("forts souterrains", "strongholds")),
          ("profondeurs", ("Le rapport des profondeurs", "The deep expedition report"), ("cités antiques", "ancient cities")),
          ("nether", ("Le journal du Nether", "The Nether log"), ("forteresses du Nether et bastions", "Nether fortresses and bastions")),
          ("ciel", ("Le dernier message", "The last message"), ("cités de l'End", "End cities"))]
quest(cE, "e_traces", ("Les traces du monde ancien", "Traces of the Old World"), 10, -1, [T_doc(d) for d, _, _ in TRACES],
      [R_coin("crown", 1), R_xp(1500)], deps=["e_fortin"], optional=True,
      subtitle=("Les écrits cachés dans les ruines d'avant", "The writings hidden in older ruins"),
      desc=D(["&7Optionnel.&r L'Empire est passé partout, même dans les ruines plus anciennes que lui. Ses écrits dorment au fond de leurs coffres. Rassemblez-les dans votre inventaire (ils ne sont pas consommés) :"]
             + ["• %s : %s%s" % (t[0].lower()[0] + t[0][1:], o[0], "." if d == "ciel" else " ;") for d, t, o in TRACES]
             + ["&8Le dernier ne se trouve qu'au bout du voyage.&r"],
             ["&7Optional.&r The Empire went everywhere, even into ruins older than itself. Its writings sleep at the bottom of their chests. Gather them in your inventory (they are not consumed):"]
             + ["• %s: %s%s" % (t[1].lower()[0] + t[1][1:], o[1], "." if d == "ciel" else ";") for d, t, o in TRACES]
             + ["&8The last one is only found at the end of the journey.&r"]))
titres_taches("e_traces", [t for _, t, _ in TRACES])

quest(cE, "e_archiviste", ("L'Archiviste", "The Archivist"), 12, 0,
      [T_doc("station"), T_doc("abri_nether"), T_doc("champ_bataille"), T_doc("dirigeable")],
      [R_coin("crown", 2), R_xp(2000), R_cmd("airain chronique note archiviste")], deps=["e_archives", "e_traces"], optional=True,
      shape="gear", size=1.5, subtitle=("Tous les écrits du monde", "Every writing in the world"),
      desc=D(["&7Optionnel.&r Il ne manque que les écrits les plus difficiles à atteindre :",
              "• les relevés de la station d'observation, sur une île volante ;",
              "• le carnet de route d'un abri réfractaire, sur un îlot du lac de lave du Nether ;",
              "• la lettre jamais envoyée, dans la caisse d'une barricade du champ de bataille ;",
              "• le livre de bord d'un dirigeable de la flotte du ciel.",
              "Tous ces écrits se relisent dans les archives des Chroniques oubliées."],
             ["&7Optional.&r Only the hardest writings to reach are missing:",
              "• the readings of the observation station, on a floating island;",
              "• the road notebook of a Refractory shelter, on an islet in the Nether's lava lake;",
              "• the letter never sent, in the crate of a battlefield barricade;",
              "• the log of a sky fleet airship.",
              "All these writings can be read again in the Forgotten Chronicles' archives."]))
titres_taches("e_archiviste", [("Les relevés de la station n°2", "Station no. 2 readings"), ("Le carnet de route", "The road notebook"), ("La lettre jamais envoyée", "The letter never sent"), ("Le livre de bord", "The ship's log")])

# le monde en trois fronts (lore du 30 octobre)
quest(cE, "e_front", ("Le front", "The Front"), 2, 3, [T_struct("kubejs:champ_bataille")], [R_coin("sprocket", 2)], deps=["e_avantposte"], optional=True,
      desc=D(["&7Optionnel.&r Dans les savanes brûlées et les collines battues, la guerre s'est arrêtée net. Un marcheur de l'Empire gît encore devant une barricade réfractaire, au milieu d'un cratère où l'Écho a fait pousser du cristal.",
              "&8La caisse de la barricade garde parfois une lettre jamais envoyée.&r"],
             ["&7Optional.&r In the burned savannas and battered hills, the war stopped dead. An Empire walker still lies before a Refractory barricade, in a crater where the Echo grew crystal.",
              "&8The barricade's crate sometimes holds a letter never sent.&r"]))
quest(cE, "e_fuite", ("La route de la fuite", "The Road of Escape"), 4, 3, [T_struct("kubejs:abri_nether")], [R_coin("sprocket", 3)], deps=["nether"], optional=True,
      desc=D(["&7Optionnel.&r Sur un îlot du lac de lave, une palissade de bois de l'Écho et un feu d'âmes. Des Réfractaires se sont arrêtés ici, sur la route de leur fuite.",
              "&8Leur carnet de route dit où ils allaient.&r"],
             ["&7Optional.&r On an islet of the lava lake, a palisade of Echo wood and a soul fire. Refractories stopped here, on the road of their escape.",
              "&8Their road notebook tells where they were going.&r"]))

# pierres de fondation (mod Airain 1.6)
quest(cE, "e_fondation", ("La première fondation", "The First Foundation"), 0, -2, [T_item("airain:foundation_stone"), T_item("airain:foundation_registry")],
      [R_coin("bevel", 4)], deps=["outils"], optional=True,
      desc=D(["&7Optionnel.&r Plantez un &6étendard de fondation&r au cœur de votre base et donnez-lui un nom et une devise : chaque fois qu'un de vous deux entrera dans sa zone, ils s'afficheront à l'écran, encadrés de sa bannière.",
              "Clic droit pour tout régler. Page « Général » : nom, devise, style du mât (potence, vexillum, cérémonie). Page « Toile » : couleurs, partition et seconde couleur, motif et sa couleur, forme du bas, usure (neuve, usée, déchirée), broderie lumineuse.",
              "Clic droit avec une clé de Create pour agrandir la zone (16 à 128 blocs, accroupi pour réduire). Un comparateur contre l'étendard donne un signal plein tant que l'un de vous est dans la zone.",
              "Le &6registre des fondations&r liste toutes vos bases (nom, coordonnées, dimension, distance), puis vos trophées exposés.",
              "&8L'étendard de fondation est le maître de sa zone : les grands étendards et bannières qui s'y trouvent peuvent suivre sa présence (voir « Hisser les couleurs »).&r"],
             ["&7Optional.&r Plant a &6foundation standard&r at the heart of your base and give it a name and a motto: each time one of you enters its area, they show on screen, framed by its banner.",
              "Right-click to set it all. \"General\" page: name, motto, mast style (gallows, vexillum, ceremonial). \"Cloth\" page: colours, division and second colour, emblem and its colour, bottom shape, wear (new, worn, torn), glowing embroidery.",
              "Right-click with a Create wrench to enlarge the area (16 to 128 blocks, sneak to shrink). A comparator against the standard gives a full signal while one of you is in the area.",
              "The &6foundation register&r lists all your bases (name, coordinates, dimension, distance), then your displayed trophies.",
              "&8The foundation standard is the master of its area: the great standards and banners in it can follow its presence (see \"Raise the Colours\").&r"]))

# --- l'héraldique de l'Empire (mod Airain 1.10 à 1.17)
quest(cE, "h_grand", ("Le grand étendard", "The Great Standard"), 2, -3, [T_item("airain:great_standard")], [R_coin("cog", 1)],
      deps=["e_fondation", "laiton"], optional=True,
      desc=D(["&7Optionnel.&r Les places de l'Empire se reconnaissaient de loin : un mât de cinq à huit blocs, et une toile qui claquait au vent.",
              "Le &6grand étendard&r fait tout ce que fait l'étendard de fondation, en plus grand. Une troisième page, « Mât », règle la hauteur, la longueur et la largeur de la toile, le vent, les franges, le fleuron du sommet (le rouage tourne), la double bannière et les lanternes.",
              "Mode &6décoratif&r (page « Général ») : pas de titre à l'écran, pas de place dans le registre. Parfait pour orner une base qui a déjà sa fondation.",
              "&8Un signal de redstone le met en berne. La météo fait claquer la toile ; l'option « Vent commun » fait onduler ensemble toutes les bannières qui l'ont.&r"],
             ["&7Optional.&r The Empire's squares could be recognised from afar: a mast five to eight blocks tall, and a cloth snapping in the wind.",
              "The &6great standard&r does everything the foundation standard does, only bigger. A third page, \"Mast\", sets the height, the cloth's length and width, the wind, fringes, the finial (the gear turns), the double banner and the lanterns.",
              "&6Decorative&r mode (\"General\" page): no title on screen, no entry in the register. Ideal to adorn a base that already has its foundation.",
              "&8A redstone signal lowers it to half-mast. Weather makes the cloth snap; the \"Shared wind\" option makes every banner that has it wave together.&r"]))
quest(cE, "h_murale", ("La bannière murale", "The Wall Banner"), 4, -3, [T_item("airain:foundation_wall_banner", 2)], [R_coin("sprocket", 2)],
      deps=["h_grand"], optional=True,
      desc=D(["&7Optionnel.&r Dans les halls de l'Empire, les couleurs tombaient des murs jusqu'au sol.",
              "La &6bannière murale&r se pose contre un mur, sur sa tringle. Mêmes réglages de toile que les étendards ; sa page « Taille » choisit la longueur (2 à 4 blocs) et la largeur.",
              "&8Un signal de redstone l'enroule. Les camps réfractaires ont aussi les leurs, à leurs propres couleurs.&r"],
             ["&7Optional.&r In the Empire's halls, the colours fell from the walls to the floor.",
              "The &6wall banner&r is placed against a wall, on its rod. Same cloth settings as the standards; its \"Size\" page picks the length (2 to 4 blocks) and the width.",
              "&8A redstone signal rolls it up. The Refractory camps have their own too, in their own colours.&r"]))
quest(cE, "h_gabarit", ("Le gabarit", "The Template"), 6, -3, [T_item("airain:banner_template")], [R_coin("sprocket", 1)],
      deps=["h_murale"], optional=True,
      desc=D(["&7Optionnel.&r Les drapiers de l'Empire travaillaient sur patron : toutes les bannières d'une cité se ressemblaient au fil près.",
              "Accroupi + clic droit avec le &6gabarit&r sur un étendard ou une bannière : il en copie l'apparence (couleurs, motif, mât, mode décoratif). Clic droit sur une autre : il l'applique. Le nom et la devise restent.",
              "&8Il copie aussi l'apparence d'un socle de l'Empire, pour l'appliquer à un autre socle.&r"],
             ["&7Optional.&r The Empire's drapers worked from patterns: every banner in a city matched to the thread.",
              "Sneak + right-click with the &6template&r on a standard or banner: it copies its look (colours, emblem, mast, decorative mode). Right-click another: it applies it. Name and motto are kept.",
              "&8It also copies the look of an Empire pedestal, to apply it to another pedestal.&r"]))
quest(cE, "h_hissage", ("Hisser les couleurs", "Raise the Colours"), 8, -3, [T_check()], [R_coin("cog", 1), R_xp(300)],
      deps=["h_murale"], optional=True,
      desc=D(["&7Optionnel.&r Quand l'Empereur entrait dans une cité, toutes ses bannières montaient ensemble.",
              "Grands étendards et bannières murales ont un réglage « Hissage » :",
              "• &6Manuel&r : un arbre de Create qui tourne contre le pied du mât, ou contre la bannière, la hisse ou l'abaisse selon le sens ;",
              "• &6Selon présence&r : les bannières montent dès que l'un de vous entre dans la zone de l'étendard de fondation, et redescendent quand le dernier la quitte. Toutes celles de la zone bougent ensemble ;",
              "• &6Selon trophées&r : elles montent tant qu'un trophée est exposé dans la zone.",
              "Réglez une bannière « selon présence » dans votre base, sortez de la zone puis revenez. Validez quand vous l'avez vue se hisser."],
             ["&7Optional.&r When the Emperor entered a city, all its banners rose together.",
              "Great standards and wall banners have a \"Hoisting\" setting:",
              "• &6Manual&r: a Create shaft turning against the foot of the mast, or against the banner, raises or lowers it depending on the direction;",
              "• &6By presence&r: banners rise as soon as one of you enters the foundation standard's area, and come down when the last one leaves. All those in the area move together;",
              "• &6By trophies&r: they stay up while a trophy is displayed in the area.",
              "Set a banner to \"by presence\" in your base, leave the area and come back. Tick the box once you have seen it rise."]))
titres_taches("h_hissage", [("Voir une bannière se hisser à votre retour", "See a banner rise when you return")])
quest(cE, "h_pavoise", ("Une base pavoisée", "A Bedecked Base"), 10, -3, [T_check()], [R_coin("cog", 2), R_xp(500)],
      deps=["h_hissage", "h_gabarit"], optional=True,
      desc=D(["&7Optionnel.&r Une fondation digne de l'Empire : au moins quatre grands étendards ou bannières murales dans la zone d'un même étendard de fondation, aux mêmes couleurs, qui se hissent tous ensemble à votre arrivée.",
              "Validez quand c'est fait."],
             ["&7Optional.&r A foundation worthy of the Empire: at least four great standards or wall banners within the area of a single foundation standard, in the same colours, all rising together when you arrive.",
              "Tick the box when done."]))
titres_taches("h_pavoise", [("Quatre bannières hissées ensemble", "Four banners raised together")])

quest(cT, "t_ligne", ("La ligne impériale", "The Imperial Line"), 0, 3, [T_struct("kubejs:cite_mecanique"), T_check()],
      [R_coin("cog", 3), R_xp(500)], deps=["train"],
      desc=D(["Les cités de l'Empire étaient reliées par le rail. Rétablissez une ligne : un train qui relie votre base à une cité mécanique, avec une gare à chaque bout.",
              "Validez après le premier aller-retour."],
             ["The Empire's cities were linked by rail. Restore a line: a train linking your base to a mechanical city, with a station at each end.",
              "Tick the box after the first round trip."]))
titres_taches("t_ligne", [None, ("Un aller-retour base ↔ cité", "A base ↔ city round trip")])

quest(c5, "fret", ("Le fret aérien", "Air Freight"), 6, 2, [T_check()], [R_coin("cog", 3), R_xp(500)], deps=["envol"],
      desc=D(["Les cités volantes de l'Empire ne vivaient que du fret. Construisez un engin volant avec une cale (coffres, tonneaux ou coffres-forts), chargez-le dans une de vos bases et livrez la cargaison dans une autre.",
              "Validez après une livraison complète."],
             ["The Empire's flying cities lived on freight. Build a flying craft with a hold (chests, barrels or item vaults), load it at one of your bases and deliver the cargo to another.",
              "Tick the box after a complete delivery."]))

REC = [("r_ciel", ("Au-dessus de tout", "Above Everything"), [T_loc("minecraft:overworld", 330, 4000)], ["outils"], R_coin("sprocket", 2),
        ("Montez au-dessus de Y 330, plus haut que tout ce qu'on peut construire. En élytres ou en engin volant.",
         "Climb above Y 330, higher than anything can be built. With elytra or a flying craft.")),
       ("r_abysses", ("Au fond du monde", "The Bottom of the World"), [T_loc("minecraft:overworld", -64, 5)], ["outils"], R_coin("bevel", 4),
        ("Descendez sous Y -59, tout contre la bedrock.", "Go below Y -59, right against the bedrock.")),
       ("r_toit", ("Le toit du Nether", "The Nether Roof"), [T_loc("minecraft:the_nether", 128, 4000)], ["nether"], R_coin("cog", 1),
        ("Passez au-dessus du plafond de bedrock du Nether. Une perle de l'Ender bien lancée peut aider.",
         "Get above the Nether's bedrock ceiling. A well-thrown ender pearl can help.")),
       ("r_vitesse", ("Pleine puissance", "Full Power"), [T_check()], ["engrenages"], R_coin("sprocket", 2),
        ("Faites tourner une machine à 256 tours/minute, la vitesse maximale. Les lunettes affichent la vitesse. Validez quand c'est fait.",
         "Run a machine at 256 RPM, the maximum speed. The goggles show the speed. Tick the box when done.")),
       ("r_voyage", ("Le grand voyageur", "The Great Traveller"), [T_stat("minecraft:aviate_one_cm", 1000000)], ["cites"], R_coin("cog", 2),
        ("Parcourez 10 km en élytres.", "Fly 10 km with elytra."))]
for i, (k, t, taches, deps, r, (fr, en)) in enumerate(REC):
    quest(cE, k, t, i * 2, 4, taches, [r], deps=deps, optional=True,
          desc=D(["&7Record d'ingénieur, optionnel.&r " + fr], ["&7Engineer's record, optional.&r " + en]))

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions_revue.py"), encoding="utf-8").read())
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions_revue2.py"), encoding="utf-8").read())

# =============================================================================
# CHRONIQUES OUBLIÉES : chaque étape du récit se débloque avec sa quête
# =============================================================================
CHRONIQUE = {"comprendre": "reveil", "surface": "surface", "village": "avant_poste", "atelier": "atelier",
             "ruines_propres": "entretien", "presage": "refractaires", "gardien_vent": "gardien_vent", "inscriptions": "inscriptions",
             "gardien_marees": "marees", "bastion": "bastion", "capsules": "capsules", "forge_ames": "forge_ames",
             "station": "station", "dragon": "gardien_cieux", "cites": "cites", "citadelle": "citadelle", "memoires": "memoires", "reactiver": "coeur",
             "eveil": "eveil", "cite3": "colosse", "berceau": "berceau", "empereur": "empereur",
             "l_refractaires": "echo_refus", "l_vael": "echo_vael", "l_sanctuaire": "echo_ada", "l_choeur": "echo_choeur"}
for _ch in chapters:
    for _q in _ch["quests"]:
        for _k, _r in CHRONIQUE.items():
            if _q["id"] == QUESTS[_k]:
                _q["rewards"].append((hid(f"r:{_k}:chronique"), "command",
                    {"command": s("airain chronique recit " + _r), "permission_level": "2", "silent": "true"}))

exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "passe_corrections.py"), encoding="utf-8").read())
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecrits_quetes.py"), encoding="utf-8").read())
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mise_en_page.py"), encoding="utf-8").read())

# =============================================================================
# SOUPAPE DE SECOURS (invisible pour les joueurs, visible en mode édition)
# =============================================================================
cX = chapter("secours", "99_secours", ("&cSecours administrateur&r", "&cAdmin rescue&r"),
             ("Ne pas montrer aux joueurs.", "Do not show to players."), "minecraft:command_block", 99, invisible=True)
RESC = [
    ("x_cuivre", ("Secours : chapitre II", "Rescue: chapter II"), [R_item("kubejs:schema_cuivre"), R_item("kubejs:fragment_rouages")]),
    ("x_laiton", ("Secours : chapitre III", "Rescue: chapter III"), [R_item("kubejs:schema_laiton"), R_item("kubejs:fragment_marees"), R_item("kubejs:sceau_forge"), R_tag("airain_nether")]),
    ("x_ciel", ("Secours : chapitre IV", "Rescue: chapter IV"), [R_item("kubejs:schema_ciel"), R_item("kubejs:fragment_forge"), R_tag("airain_end"), R_tag("airain_waystones"), R_tag("airain_gare"), R_tag("airain_pneumatique")]),
    ("x_vide", ("Secours : chapitre V", "Rescue: chapter V"), [R_item("kubejs:fragment_vide"), R_tag("airain_atelier")]),
    ("x_coeur", ("Secours : chapitre VI", "Rescue: chapter VI"), [R_item("kubejs:coeur_d_airain"), R_item("minecraft:nether_star"), R_item("airain:defense_beacon")]),
    ("x_echo", ("Secours : l'Écho", "Rescue: the Echo"), [R_item("kubejs:diapason_echo"), R_item("kubejs:echo_primordial", 8)]),
]
for i, (k, title, rewards) in enumerate(RESC):
    quest(cX, k, title, i * 2, 0, [T_check()], rewards,
          desc=D(["Complétez cette quête en mode édition pour débloquer un joueur coincé par un bug."],
                 ["Complete this quest in edit mode to unblock a player stuck because of a bug."]))

# =============================================================================
# ÉCRITURE
# =============================================================================
def kv(d, indent):
    pad = "\t" * indent
    return "".join(f"{pad}{k}: {v}\n" for k, v in d.items())

def write_chapter(ch):
    L = ["{\n"]
    if ch["invisible"]: L.append("\talways_invisible: true\n")
    L.append('\tdefault_hide_dependency_lines: false\n')
    L.append('\tdefault_quest_shape: ""\n')
    L.append(f'\tfilename: {s(ch["filename"])}\n')
    L.append(f'\tgroup: {s(ch.get("group", ""))}\n')
    L.append('\thide_quest_details_until_startable: true\n')
    L.append(f'\ticon: {item(ch["icon"])}\n')
    if ch.get("images"):
        L.append("\timages: [\n")
        for im in ch["images"]:
            L.append("\t\t{\n\t\t\theight: %sd\n\t\t\timage: %s\n\t\t\trotation: 0.0d\n\t\t\twidth: %sd\n\t\t\tx: %sd\n\t\t\ty: %sd\n\t\t}\n"
                     % (float(im["h"]), s(im["image"]), float(im["w"]), float(im["x"]), float(im["y"])))
        L.append("\t]\n")
    L.append(f'\tid: {s(ch["id"])}\n')
    L.append(f'\torder_index: {ch["order"]}\n')
    L.append("\tquests: [\n")
    for q in ch["quests"]:
        L.append("\t\t{\n")
        if q["repeat"]: L.append("\t\t\tcan_repeat: true\n")
        if q["deps"]: L.append("\t\t\tdependencies: [" + ", ".join(s(d) for d in q["deps"]) + "]\n")
        if q.get("dep_un"): L.append('\t\t\tdependency_requirement: "one_completed"\n')
        if q.get("hide_lines"): L.append("\t\t\thide_dependency_lines: true\n")
        if q["icon"]: L.append(f'\t\t\ticon: {item(q["icon"])}\n')
        L.append(f'\t\t\tid: {s(q["id"])}\n')
        if q.get("invisible"): L.append("\t\t\tinvisible: true\n\t\t\tinvisible_until_tasks: 1\n")   # cachée tant que sa tâche n'est pas faite
        if q["optional"]: L.append("\t\t\toptional: true\n")
        if q["rewards"]:
            L.append("\t\t\trewards: [\n")
            for rid, rt, data in q["rewards"]:
                L.append("\t\t\t\t{\n" + kv(data, 5) + f'\t\t\t\t\tid: {s(rid)}\n\t\t\t\t\ttype: {s(rt)}\n\t\t\t\t}}\n')
            L.append("\t\t\t]\n")
        if q["shape"]: L.append(f'\t\t\tshape: {s(q["shape"])}\n')
        if q["size"]: L.append(f'\t\t\tsize: {q["size"]}d\n')
        L.append("\t\t\ttasks: [\n")
        for tid, tt, data in q["tasks"]:
            L.append("\t\t\t\t{\n" + kv(data, 5) + f'\t\t\t\t\tid: {s(tid)}\n\t\t\t\t\ttype: {s(tt)}\n\t\t\t\t}}\n')
        L.append("\t\t\t]\n")
        L.append(f'\t\t\tx: {float(q["x"])}d\n\t\t\ty: {float(q["y"])}d\n')
        L.append("\t\t}\n")
    L.append("\t]\n}\n")
    return "".join(L)

def lang_snbt(d):
    out = ["{\n"]
    for k in sorted(d):
        v = d[k]
        if isinstance(v, list):
            if not v: continue
            out.append(f"\t{s(k)}: [\n" + "".join(f"\t\t{s(x)}\n" for x in v) + "\t]\n")
        else:
            out.append(f"\t{s(k)}: {s(v)}\n")
    out.append("}\n")
    return "".join(out)

os.makedirs(os.path.join(QDIR, "chapters"), exist_ok=True)
os.makedirs(os.path.join(QDIR, "lang"), exist_ok=True)
os.makedirs(os.path.join(QDIR, "reward_tables"), exist_ok=True)
for ch in chapters:
    with open(os.path.join(QDIR, "chapters", ch["filename"] + ".snbt"), "w", encoding="utf-8") as f:
        f.write(write_chapter(ch))
with open(os.path.join(QDIR, "data.snbt"), "w", encoding="utf-8") as f:
    f.write('{\n\tdefault_consume_items: false\n\tdefault_quest_shape: "circle"\n\tdefault_reward_team: false\n\tfallback_locale: "en_us"\n\tversion: 13\n}\n')
with open(os.path.join(QDIR, "chapter_groups.snbt"), "w", encoding="utf-8") as f:
    f.write("{\n\tchapter_groups: [\n" + "".join("\t\t{ id: %s }\n" % s(hid("grp:" + g)) for g, _, _ in GROUPES) + "\t]\n}\n")
for _f in os.listdir(os.path.join(QDIR, "chapters")):   # chapitres disparus (fusionnés)
    if _f.endswith(".snbt") and _f[:-5] not in {c["filename"] for c in chapters}: os.remove(os.path.join(QDIR, "chapters", _f))
tr("file.0000000000000001.title", ("L'Empire d'Airain", "The Airain Empire"))
with open(os.path.join(QDIR, "lang", "fr_fr.snbt"), "w", encoding="utf-8") as f: f.write(lang_snbt(LANG["fr"]))
with open(os.path.join(QDIR, "lang", "en_us.snbt"), "w", encoding="utf-8") as f: f.write(lang_snbt(LANG["en"]))

summary = {"chapters": len(chapters),
           "quests": {c["key"]: len(c["quests"]) for c in chapters},
           "total": sum(len(c["quests"]) for c in chapters),
           "items": sorted({d["item"].split('id: "')[-1].split('"')[0] for c in chapters for q in c["quests"]
                            for _, t, d in q["tasks"] + q["rewards"] if t == "item"}),
           "entities": sorted({d["entity"].strip('"') for c in chapters for q in c["quests"] for _, t, d in q["tasks"] if t == "kill"}),
           "structures": sorted({d["structure"].strip('"') for c in chapters for q in c["quests"] for _, t, d in q["tasks"] if t == "structure"})}
json.dump(summary, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary_v2.json"), "w"), indent=1)
print(json.dumps({k: summary[k] for k in ("quests", "total")}, indent=1))
