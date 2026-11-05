#!/usr/bin/env python3
"""Génère le livre de quêtes FTB Quests (1.21.1, format v13) de L'Empire d'Airain."""
import hashlib, os, sys, json

OUT = sys.argv[1]
QDIR = os.path.join(OUT, "config/ftbquests/quests")

def hid(key):
    h = hashlib.md5(("airain:" + key).encode()).hexdigest()[:16].upper()
    # FTB Quests lit les IDs avec Long.parseLong(hex) : le premier chiffre doit être entre 1 et 7,
    # sinon le nombre dépasse la limite d'un long signé et l'objet reçoit un ID aléatoire.
    h = "1234567"[int(h[0], 16) % 7] + h[1:]
    return h

def s(v):
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'

def item(i, c=1):
    return '{ count: %d, id: %s }' % (c, s(i))

# ---- tâches / récompenses -------------------------------------------------
def T_item(i, n=1, consume=False):
    return ("item", {"item": item(i), "count": f"{n}L"} | ({"consume_items": "TRUE"} if consume else {}))
def T_kill(e, n=1):
    return ("kill", {"entity": s(e), "value": f"{n}L"})
def T_struct(st):
    return ("structure", {"structure": s(st)})
def T_dim(d):
    return ("dimension", {"dimension": s(d)})
def T_check():
    return ("checkmark", {})

def R_item(i, n=1):
    return ("item", {"item": item(i), "count": str(n)} if n > 1 else {"item": item(i)})
def R_xp(n):
    return ("xp", {"xp": str(n)})
def R_cmd(c, msg):
    return ("command", {"command": s(c), "permission_level": "2", "silent": "false", "feedback_message": s(msg)})

lang = {}
LOGI = {}
chapters = []

def chapter(key, filename, title, subtitle, icon, order):
    ch = {"key": key, "id": hid("ch:" + key), "filename": filename, "icon": icon,
          "order": order, "quests": []}
    lang[f"chapter.{ch['id']}.title"] = title
    LOGI[f"chapter.{ch['id']}.title"] = f"ch:{key}.title"
    LOGI[f"chapter.{ch['id']}.chapter_subtitle"] = f"ch:{key}.subtitle"
    lang[f"chapter.{ch['id']}.chapter_subtitle"] = subtitle if isinstance(subtitle, list) else [subtitle]
    chapters.append(ch)
    return ch

QUESTS = {}

def quest(ch, key, title, x, y, tasks, rewards=(), deps=(), desc=(), subtitle=None,
          shape=None, size=None, optional=False, icon=None):
    qid = hid("q:" + key)
    q = {"id": qid, "x": x, "y": y, "tasks": [], "rewards": [], "deps": [QUESTS[d] for d in deps],
         "shape": shape, "size": size, "optional": optional, "icon": icon}
    for n, (tt, data) in enumerate(tasks):
        q["tasks"].append((hid(f"t:{key}:{n}"), tt, data))
    for n, (rt, data) in enumerate(rewards):
        q["rewards"].append((hid(f"r:{key}:{n}"), rt, data))
    lang[f"quest.{qid}.title"] = title
    LOGI[f"quest.{qid}.title"] = f"{key}.title"
    LOGI[f"quest.{qid}.quest_subtitle"] = f"{key}.subtitle"
    LOGI[f"quest.{qid}.quest_desc"] = f"{key}.desc"
    if subtitle:
        lang[f"quest.{qid}.quest_subtitle"] = subtitle
    if desc:
        lang[f"quest.{qid}.quest_desc"] = list(desc)
    QUESTS[key] = qid
    ch["quests"].append(q)
    return qid

def journal(*lines):
    """Une page du journal d'ingénieur, en italique doré."""
    return ["", "&6&lJournal d'ingénieur&r", *["&o" + l + "&r" for l in lines]]

# ========================================================================
# CHAPITRE 0 — LE RÉVEIL
# ========================================================================
c0 = chapter("reveil", "00_le_reveil", "&6I&r · Le Réveil",
             "Un monde vide. Pas une tombe, pas un squelette.", "minecraft:clock", 0)

quest(c0, "bienvenue", "Bienvenue dans l'Empire d'Airain", 0, 0, [T_check()],
      [R_item("minecraft:bread", 16), R_item("minecraft:torch", 32)],
      subtitle="Cliquez ici pour commencer",
      shape="gear", size=1.5,
      desc=["Il y a longtemps, l'&6Empire d'Airain&r maîtrisait une technologie mécanique sans égale.",
            "Puis il a disparu, du jour au lendemain.",
            "",
            "Ses ruines sont encore là, gardées par ses anciennes créations. Chaque gardien vaincu vous rendra un morceau de leur savoir.",
            "",
            "&eÀ deux :&r rejoignez la même équipe (/ftbteams) pour partager la progression du livre.",
            "&eLes Schémas&r débloquent les machines clés. Ils ne sont jamais consommés : gardez-les précieusement."])

quest(c0, "outils", "Des outils dignes de ce nom", 2, 0,
      [T_item("minecraft:iron_pickaxe")], [R_item("minecraft:iron_ingot", 8)], deps=["bienvenue"],
      desc=["Le monde est dangereux. Commencez par vous équiper correctement."])

quest(c0, "journal1", "Le journal de l'ingénieur", 4, -1.5, [T_check()],
      [R_item("create:goggles"), R_item("create:wrench")], deps=["outils"],
      desc=["Dans une ruine effondrée, sous des pierres moussues, vous trouvez un carnet relié de cuivre.",
            "La plupart des pages sont illisibles. Pas les dernières.",
            *journal("Jour 412. Les ordres sont arrivés : tout le monde au Cœur.",
                     "Je laisse ce carnet pour ceux qui viendront après.",
                     "Nous ne partons pas. &lNous attendons.&r&o"),
            "",
            "&8Étrange : aucune tombe dans les environs. Aucun ossement.&r"])

quest(c0, "alliage", "L'alliage d'andésite", 4, 0,
      [T_item("create:andesite_alloy", 16)], [R_xp(50)], deps=["outils"],
      desc=["La base de toute la mécanique d'Airain : l'&6alliage d'andésite&r.",
            "Andésite + pépite de fer (ou de zinc) dans une table de craft."])

quest(c0, "roue", "La première roue", 6, 0,
      [T_item("create:water_wheel")], [R_item("create:shaft", 16)], deps=["alliage"],
      desc=["Placez une roue à eau dans un courant : votre première source de force mécanique.",
            "Mettez les lunettes d'ingénieur pour lire la vitesse et la contrainte."])

quest(c0, "engrenages", "Engrenages", 8, 0,
      [T_item("create:cogwheel", 8), T_item("create:large_cogwheel", 2)], [R_xp(80)], deps=["roue"],
      desc=["Petit engrenage et grand engrenage : en les combinant, vous changez la vitesse de rotation.",
            "Plus c'est rapide, plus ça consomme de contrainte."])

# ========================================================================
# CHAPITRE 1 — L'ÂGE DE L'ANDÉSITE
# ========================================================================
c1 = chapter("andesite", "01_age_andesite", "&6II&r · L'Âge de l'Andésite",
             "Les premières machines. Et des ruines étrangement propres.", "create:andesite_casing", 1)

quest(c1, "boitier_andesite", "Boîtier d'andésite", 0, 0,
      [T_item("create:andesite_casing", 8)], [R_xp(80)], deps=["engrenages"],
      desc=["Appliquez de l'alliage d'andésite sur un tronc écorcé pour obtenir un boîtier."])

quest(c1, "presse", "La presse mécanique", 2, -1,
      [T_item("create:mechanical_press")], [R_item("minecraft:iron_ingot", 16)], deps=["boitier_andesite"],
      desc=["La presse aplatit les lingots en plaques. Indispensable pour la suite."])

quest(c1, "mixeur", "Le mixeur et le bassin", 2, 1,
      [T_item("create:mechanical_mixer"), T_item("create:basin")], [R_xp(100)], deps=["boitier_andesite"],
      desc=["Un mixeur au-dessus d'un bassin mélange les ingrédients. Plus tard, avec de la chaleur, il fera des merveilles."])

quest(c1, "broyeur", "Broyer la pierre", 4, -1,
      [T_item("create:millstone")], [R_xp(100)], deps=["presse"],
      desc=["La meule broie minerais et graviers et double le rendement des minerais."])

quest(c1, "ventilateur", "Le ventilateur", 4, 1,
      [T_item("create:encased_fan")], [R_xp(100)], deps=["mixeur"],
      desc=["Un ventilateur qui souffle à travers l'eau lave les objets. À travers le feu, il les fume ou les fond."])

quest(c1, "ruines_propres", "Des ruines entretenues", 6, 0, [T_check()], [R_item("minecraft:golden_apple")],
      deps=["broyeur", "ventilateur"],
      desc=["Plus vous explorez, plus un détail vous dérange : certaines ruines sont &opropres&r.",
            "Les mécanismes sont huilés. Les couloirs, balayés.",
            "",
            "Les gardiens ne sont peut-être pas déréglés. Ils font de la maintenance.",
            "&oMais pour qui ?&r",
            *journal("Les sentinelles de cuivre veilleront sur les salles d'épreuve.",
                     "Elles savent ce qu'elles protègent.")])

quest(c1, "salles_epreuve", "Les salles d'épreuve", 8, 0, [T_struct("minecraft:trial_chambers")], [R_xp(200)],
      deps=["ruines_propres"],
      desc=["Sous terre, des salles de cuivre et de tuf : des &6salles d'épreuve&r de l'Empire.",
            "Elles sont gardées. Préparez-vous."])

quest(c1, "gardien_vent", "Le gardien du vent", 10, 0, [T_kill("minecraft:breeze", 3)],
      [R_item("kubejs:schema_cuivre"), R_item("kubejs:fragment_rouages"), R_xp(500)],
      deps=["salles_epreuve"], shape="hexagon", size=1.5,
      subtitle="Débloque le Schéma du Cuivre",
      desc=["Les gardiens de vent protègent les salles d'épreuve. Abattez-en trois.",
            "",
            "&eRécompense :&r le &6Schéma du Cuivre&r, qui débloque la pompe mécanique, le bec verseur et l'égouttoir.",
            "",
            "&8En tombant, le dernier gardien laisse échapper un éclat de métal tiède. Un souvenir.&r"])

# ========================================================================
# CHAPITRE 2 — L'ÂGE DU CUIVRE
# ========================================================================
c2 = chapter("cuivre", "02_age_cuivre", "&6III&r · L'Âge du Cuivre",
             "Les fluides, les profondeurs, et les inscriptions.", "create:copper_casing", 2)

quest(c2, "boitier_cuivre", "Boîtier de cuivre", 0, 0,
      [T_item("create:copper_casing", 8)], [R_xp(100)], deps=["gardien_vent"],
      desc=["Le cuivre appliqué sur un tronc écorcé donne le boîtier des machines à fluides."])

quest(c2, "tuyaux", "Tuyauterie", 2, -1,
      [T_item("create:fluid_pipe", 16)], [R_item("minecraft:copper_ingot", 16)], deps=["boitier_cuivre"],
      desc=["Les tuyaux transportent eau, lave et tous les fluides de l'Empire."])

quest(c2, "pompe", "La pompe mécanique", 4, -1,
      [T_item("create:mechanical_pump")], [R_xp(150)], deps=["tuyaux"],
      desc=["Engrenage + tuyau + &6Schéma du Cuivre&r (non consommé).",
            "La pompe met les fluides en mouvement dans le sens de rotation."])

quest(c2, "reservoir", "Réservoirs", 2, 1,
      [T_item("create:fluid_tank", 4)], [R_xp(100)], deps=["boitier_cuivre"],
      desc=["Les réservoirs se combinent en grands volumes."])

quest(c2, "bec_verseur", "Bec verseur et égouttoir", 4, 1,
      [T_item("create:spout"), T_item("create:item_drain")], [R_xp(200)], deps=["reservoir", "pompe"],
      desc=["Le bec verseur remplit les objets, l'égouttoir les vide. Les deux demandent le &6Schéma du Cuivre&r."])

quest(c2, "vapeur", "La machine à vapeur", 6, -1,
      [T_item("create:steam_engine")], [R_xp(200)], deps=["bec_verseur"], optional=True,
      desc=["&7Optionnel.&r Une chaudière faite de réservoirs, de l'eau, du feu : beaucoup de puissance."])

quest(c2, "inscriptions", "Les inscriptions", 6, 1, [T_check()], [R_item("minecraft:conduit")],
      deps=["bec_verseur"],
      desc=["Sur les murs d'une ruine noyée, des inscriptions répétées des centaines de fois :",
            "",
            "&o« Nous dormons dans le métal. »&r",
            "&o« Le grand transfert approche. »&r",
            "",
            "Toujours pas de tombes. Où sont passés les habitants ?",
            *journal("Les gardiens des marées garderont le secret de l'alliage.",
                     "Personne ne doit le retrouver avant l'heure.")])

quest(c2, "monument", "Les ruines englouties", 8, 0, [T_struct("minecraft:monument")], [R_xp(250)],
      deps=["inscriptions"],
      desc=["Au fond de l'océan, un temple de prismarine. L'Empire y cachait le secret du laiton.",
            "&ePensez aux potions de respiration, et à la pompe pour vider des salles.&r"])

quest(c2, "gardien_marees", "Le gardien des marées", 10, 0, [T_kill("minecraft:elder_guardian")],
      [R_item("kubejs:schema_laiton"), R_item("kubejs:fragment_marees"), R_xp(800)],
      deps=["monument"], shape="hexagon", size=1.5,
      subtitle="Débloque le Schéma du Laiton",
      desc=["Un gardien ancien veille sur le temple.",
            "",
            "&eRécompense :&r le &6Schéma du Laiton&r, qui débloque le brûleur à blaze. Sans chaleur, pas de laiton."])

# ========================================================================
# CHAPITRE 3 — L'ÂGE DU LAITON
# ========================================================================
c3 = chapter("laiton", "03_age_laiton", "&6IV&r · L'Âge du Laiton",
             "Le cœur de la technologie d'Airain. Et une salle pleine de capsules vides.", "create:brass_casing", 3)

quest(c3, "bruleur", "Le brûleur à blaze", 0, 0,
      [T_item("create:blaze_burner")], [R_xp(200)], deps=["gardien_marees"],
      desc=["Fabriquez un brûleur vide (avec le &6Schéma du Laiton&r), puis capturez-y un blaze.",
            "Placé sous un bassin, il chauffe le mixeur."])

quest(c3, "laiton", "L'alliage d'Airain", 2, 0,
      [T_item("create:brass_ingot", 32)], [R_item("create:zinc_ingot", 16)], deps=["bruleur"],
      desc=["Cuivre + zinc dans un bassin chauffé : le &6laiton&r, métal sacré de l'Empire."])

quest(c3, "boitier_laiton", "Boîtier de laiton", 4, -1,
      [T_item("create:brass_casing", 16)], [R_xp(200)], deps=["laiton"])

quest(c3, "precision", "Mécanisme de précision", 4, 1,
      [T_item("create:precision_mechanism", 4)], [R_xp(300)], deps=["laiton"],
      desc=["L'assemblage en séquence : une chaîne de déployeurs et de presses qui construit pièce par pièce.",
            "&eAstuce :&r ouvrez la recette dans EMI et maintenez W sur une machine pour voir son tutoriel."])

quest(c3, "bras", "Le bras mécanique", 6, -1,
      [T_item("create:mechanical_arm"), T_item("create:deployer")], [R_xp(300)], deps=["boitier_laiton", "precision"],
      desc=["Le bras déplace les objets entre les machines. Le déployeur agit comme un joueur."])

quest(c3, "rails", "Poser les rails", 6, 1,
      [T_item("create:track", 64)], [R_item("create:railway_casing", 8)], deps=["precision"],
      desc=["Les ruines sont loin les unes des autres. Il est temps de relier le monde."])

quest(c3, "train", "Le premier train", 8, 1,
      [T_item("create:controls"), T_check()], [R_xp(500)], deps=["rails"],
      desc=["Commandes, bogies, assemblage en gare : construisez un train et faites-lui parcourir un trajet complet.",
            "Validez la coche quand votre train roule tout seul."])

quest(c3, "capsules", "La salle des capsules", 8, -1, [T_check()], [R_item("minecraft:ender_pearl", 8)],
      deps=["bras"],
      desc=["Au plus profond d'une ruine, une salle immense.",
            "Des milliers de capsules de laiton, alignées. &lToutes vides.&r",
            "",
            "Des câbles en sortent et partent tous dans la même direction, vers le bas.",
            *journal("Le transfert a commencé. Nous entrons dans le métal un par un.",
                     "Je serai le dernier. Je dois finir ce carnet.")])

quest(c3, "canons", "L'artillerie d'Airain", 10, 0,
      [T_item("createbigcannons:cannon_mount"),
       T_item("createbigcannons:cast_iron_cannon_barrel", 2),
       T_item("createbigcannons:cast_iron_sliding_breech"),
       T_item("createbigcannons:powder_charge", 8),
       T_item("createbigcannons:solid_shot", 8)],
      [R_xp(600)], deps=["capsules", "train"],
      desc=["Une forteresse du Nether garde le prochain secret. On ne la prend pas à l'épée.",
            "Construisez un canon complet : affût, tubes, culasse, charges et boulets.",
            "&eAstuce :&r les tubes se coulent dans des moules, puis s'alèsent à la foreuse."])

quest(c3, "nether", "Vers le Nether", 12, 0, [T_dim("minecraft:the_nether")], [R_xp(200)], deps=["canons"])

quest(c3, "forge_ames", "La forge des âmes", 14, 0, [T_kill("cataclysm:netherite_monstrosity")],
      [R_item("kubejs:schema_ciel"), R_item("kubejs:fragment_forge"), R_xp(1500)],
      deps=["nether"], shape="hexagon", size=1.5,
      subtitle="Débloque le Schéma du Ciel",
      desc=["Au fond d'une forge des âmes dort une &cmonstruosité de netherite&r. Elle se réveille quand on approche.",
            "Bombardez, puis finissez le travail.",
            "",
            "&eRécompense :&r le &6Schéma du Ciel&r, qui débloque l'assembleur physique et le roulement d'hélice : la clé des navires volants."])

# ========================================================================
# CHAPITRE 4 — L'ÂGE DU CIEL
# ========================================================================
c4 = chapter("ciel", "04_age_ciel", "&6V&r · L'Âge du Ciel",
             "L'Empire avait des cités volantes.", "minecraft:elytra", 4)

quest(c4, "envol", "Premier envol", 0, 0, [T_check()], [R_xp(500)], deps=["forge_ames"],
      desc=["Avec Create Aeronautics, construisez votre premier engin volant et faites-le décoller.",
            "L'&6assembleur physique&r (avec le Schéma du Ciel) transforme votre construction en véhicule.",
            "Validez la coche quand vous avez volé au-dessus des nuages."])

quest(c4, "navire_arme", "Le navire de guerre", 2, 0, [T_check()], [R_xp(800)], deps=["envol"],
      desc=["Montez au moins un canon sur votre engin volant.",
            "Le ciel n'est pas vide : la suite risque d'être mouvementée."])

quest(c4, "end", "Au-delà du portail", 4, -1, [T_dim("minecraft:the_end")], [R_xp(300)], deps=["navire_arme"])

quest(c4, "dragon", "Le gardien des portes", 6, -1, [T_kill("minecraft:ender_dragon")],
      [R_xp(1000)], deps=["end"],
      desc=["Le dragon garde l'accès aux îles extérieures."])

quest(c4, "cite_volante", "Les cités volantes", 6, 1, [T_struct("minecraft:end_city")],
      [R_item("minecraft:shulker_box", 2)], deps=["dragon"],
      desc=["Des tours suspendues dans le vide. L'architecture rappelle étrangement celle de l'Empire."])

quest(c4, "bientot", "Bientôt", 8, 0, [T_check()], [R_item("minecraft:totem_of_undying")],
      deps=["cite_volante"],
      desc=["Partout où vous passez, des machines s'allument seules. Des engrenages tournent sans force.",
            "",
            "Le dernier journal tient en une ligne, d'une écriture tremblante :",
            *journal("Il a répondu. Il sait que quelqu'un vient.")])

quest(c4, "citadelle", "La citadelle en ruine", 10, 0, [T_kill("cataclysm:ender_guardian")],
      [R_item("kubejs:fragment_vide"), R_xp(2000)], deps=["bientot"], shape="hexagon", size=1.5,
      subtitle="Le dernier fragment",
      desc=["Au troisième étage d'une citadelle en ruine de l'End, l'&5autel du vide&r. Approchez et le gardien s'éveille.",
            "",
            "&8Il ne meurt pas en hurlant. Il murmure : « Bientôt. »&r"])

# ========================================================================
# CHAPITRE 5 — LE CŒUR D'AIRAIN
# ========================================================================
c5 = chapter("coeur", "05_coeur_airain", "&6VI&r · Le Cœur d'Airain",
             "Rassembler les mémoires. Rallumer le Cœur.", "kubejs:coeur_d_airain", 5)

quest(c5, "assembleurs", "L'assembleur mécanique", 0, 0,
      [T_item("create:mechanical_crafter", 21)], [R_xp(500)], deps=["citadelle"],
      desc=["Le Cœur se forge sur une grille 5×5 d'assembleurs mécaniques : il en faut 21.",
            "Reliez-les avec la clé pour qu'ils travaillent ensemble."])

quest(c5, "memoires", "Les quatre mémoires", 2, 0,
      [T_item("kubejs:fragment_rouages"), T_item("kubejs:fragment_marees"),
       T_item("kubejs:fragment_forge"), T_item("kubejs:fragment_vide")],
      [R_xp(500)], deps=["assembleurs"],
      desc=["Rouages, Marées, Forge, Vide. Les quatre gardiens vous ont rendu chacun un souvenir.",
            "Mis côte à côte, les fragments se répondent : leurs inscriptions forment une seule phrase.",
            "",
            "&o« Rendez-nous notre Cœur. »&r"])

quest(c5, "forger", "Forger le Cœur", 4, 0, [T_item("kubejs:coeur_d_airain")], [R_xp(1500)],
      deps=["memoires"], shape="gear", size=1.5,
      desc=["Boîtiers de laiton, mécanismes de précision, un cœur de la mer et les quatre fragments.",
            "Consultez la recette dans EMI pour la disposition."])

quest(c5, "reactiver", "Réactiver le Cœur", 6, 0, [T_check()],
      [R_cmd("locate structure cataclysm:ancient_factory",
             "Le Cœur tire vers une direction précise, sous terre."),
       R_item("minecraft:nether_star")],
      deps=["forger"], shape="hexagon", size=2.0,
      subtitle="&cLe retournement&r",
      desc=["Vous tenez le Cœur à deux mains. Il bat. Il chauffe.",
            "Et sous vos pieds, très loin, quelque chose répond.",
            "",
            "Le carnet s'ouvre tout seul à une page restée blanche jusqu'ici. Des lettres s'y gravent, comme brûlées de l'intérieur :",
            "",
            "&6&o« Merci.",
            "Ces pages, ces gardiens, ces schémas : c'est nous qui les avons placés sur votre route.",
            "Il nous fallait des mains vivantes pour rallumer le Cœur.",
            "Nous n'avons jamais disparu. Nous attendions dans le métal.",
            "Maintenant, nous revenons. Et ce monde redevient le nôtre. »&r",
            "",
            "&cL'Empire d'Airain se réveille.&r",
            "",
            "&8La récompense vous indique la direction de son berceau, et vous offre l'étincelle qui réveillera son maître.&r"])

# ========================================================================
# CHAPITRE 6 — LA RECONQUÊTE
# ========================================================================
c6 = chapter("reconquete", "06_reconquete", "&4VII&r · La Reconquête",
             "L'Empire est revenu. Il veut son monde.", "minecraft:nether_star", 6)

quest(c6, "eveil", "L'Empire s'éveille", 0, 0, [T_check()], [R_xp(500)], deps=["reactiver"],
      desc=["Les ruines ne dorment plus. Les mécanismes tournent, les sentinelles patrouillent.",
            "Vous avez rendu son cœur à l'Empire. À vous de l'arrêter.",
            "",
            "Tout ce que vous avez construit, l'usine, les trains, le navire de guerre, va servir maintenant."])

quest(c6, "rempart", "Fortifier la base", 2, -1, [T_item("createbigcannons:cannon_mount", 3)], [R_xp(800)],
      deps=["eveil"],
      desc=["Avant de frapper, protégez ce que vous avez bâti : trois affûts de canon autour de la base."])

quest(c6, "berceau", "Le berceau de l'Empire", 2, 1, [T_struct("cataclysm:ancient_factory")], [R_xp(800)],
      deps=["eveil"],
      desc=["Une &6usine ancienne&r enfouie vers Y -30. Le Cœur vous en a donné la direction.",
            "C'est ici que tout a commencé. C'est ici que tout doit finir."])

quest(c6, "sentinelle", "La sentinelle", 4, 1, [T_kill("cataclysm:the_prowler")], [R_xp(1500)],
      deps=["berceau"],
      desc=["Une sentinelle mécanique garde l'usine. Abattez-la pour ouvrir la voie."])

quest(c6, "etincelle", "L'étincelle", 4, -1, [T_item("minecraft:nether_star")], [R_xp(500)],
      deps=["rempart"],
      desc=["L'Empereur dort encore dans sa machine. Une étoile du Nether suffira à le réveiller.",
            "Le Cœur vous en a offert une. Si elle est perdue, il faudra vaincre un Wither."])

quest(c6, "empereur", "L'Empereur d'Airain", 6, 0, [T_kill("cataclysm:the_harbinger")],
      [R_xp(5000), R_item("minecraft:netherite_ingot", 4)],
      deps=["sentinelle", "etincelle"], shape="hexagon", size=2.5,
      subtitle="&4Boss final&r",
      desc=["Au centre de l'usine, une machine immense, immobile. L'Empereur, fusionné avec ce qu'il a construit.",
            "Clic droit avec l'étoile du Nether pour le réveiller.",
            "",
            "&cIl est extrêmement dangereux.&r Équipez-vous au mieux et combattez à deux."])

quest(c6, "epilogue", "Épilogue", 8, 0, [T_check()], [R_item("minecraft:beacon")],
      deps=["empereur"], shape="gear", size=1.5,
      desc=["Le silence revient. Les machines de l'Empire s'arrêtent une à une, pour de bon cette fois.",
            "",
            "Le Cœur d'Airain bat encore dans votre inventaire. Plus doucement.",
            "Il ne répond plus à personne. Il est à vous.",
            "",
            "&6Merci d'avoir joué à L'Empire d'Airain.&r"])

# ========================================================================
# ANNEXES
# ========================================================================
cA = chapter("arsenal", "10_arsenal", "&3Annexe&r · Arsenal et magie",
             "La technologie d'Airain si avancée qu'elle ressemble à des sorts.", "irons_spellbooks:iron_spell_book", 10)

quest(cA, "a_table", "La table d'inscription", 0, 0, [T_item("irons_spellbooks:inscription_table")],
      [R_item("irons_spellbooks:common_ink", 4)], deps=["gardien_vent"],
      desc=["Les &6parchemins&r de l'Empire sont des circuits miniaturisés. La table d'inscription permet de les graver dans un grimoire."])
quest(cA, "a_journal", "Premier grimoire", 2, 0, [T_item("irons_spellbooks:copper_spell_book")],
      [R_xp(150)], deps=["a_table"])
quest(cA, "a_essence", "Essence arcanique", 2, 1.5, [T_item("irons_spellbooks:arcane_essence", 16)],
      [R_xp(200)], deps=["a_table"])
quest(cA, "a_forge", "La forge à parchemins", 4, 0, [T_item("irons_spellbooks:scroll_forge")],
      [R_xp(300)], deps=["a_journal", "a_essence"],
      desc=["Fabriquez vos propres parchemins de sorts."])
quest(cA, "a_tome", "Le tome de fer", 6, 0, [T_item("irons_spellbooks:iron_spell_book")],
      [R_xp(400)], deps=["a_forge"])
quest(cA, "a_mithril", "Mithril", 6, 1.5, [T_item("irons_spellbooks:mithril_ingot", 4)],
      [R_xp(500)], deps=["a_forge"], optional=True)
quest(cA, "a_codex", "Le codex ancien", 8, 0, [T_item("irons_spellbooks:netherite_spell_book")],
      [R_xp(1500)], deps=["a_tome"], optional=True,
      desc=["Le grimoire ultime. Un vrai mage de l'Empire."])

cB = chapter("production", "11_production", "&3Annexe&r · Défis de production",
             "L'Empire produisait sans relâche. Faites mieux.", "create:precision_mechanism", 11)

quest(cB, "p_alliage", "Mille alliages", 0, 0, [T_item("create:andesite_alloy", 1000)], [R_xp(500)],
      deps=["boitier_andesite"],
      desc=["Automatisez entièrement l'alliage d'andésite."])
quest(cB, "p_plaques", "Laminoir", 2, 0, [T_item("create:iron_sheet", 512)], [R_xp(500)], deps=["p_alliage"])
quest(cB, "p_laiton", "Fonderie de laiton", 4, 0, [T_item("create:brass_ingot", 500)], [R_xp(1000)],
      deps=["p_plaques", "laiton"])
quest(cB, "p_precision", "Chaîne de précision", 6, 0, [T_item("create:precision_mechanism", 64)], [R_xp(1500)],
      deps=["p_laiton", "precision"])
quest(cB, "p_rails", "Le grand réseau", 8, 0, [T_item("create:track", 1024)], [R_xp(2000)],
      deps=["p_precision", "train"])

cC = chapter("exploration", "12_exploration", "&3Annexe&r · Exploration",
             "Cartographier ce que l'Empire a laissé derrière lui.", "minecraft:filled_map", 12)

quest(cC, "e_cite", "La cité antique", 0, 0, [T_struct("minecraft:ancient_city")], [R_xp(800)],
      deps=["outils"], desc=["Une cité engloutie dans les ténèbres. &cSilence absolu recommandé.&r"])
quest(cC, "e_bastion", "Le bastion", 2, 0, [T_struct("minecraft:bastion_remnant")], [R_xp(800)],
      deps=["nether"])
quest(cC, "e_fortin", "Le fort souterrain", 0, 1.5, [T_struct("minecraft:stronghold")], [R_xp(800)],
      deps=["outils"])
quest(cC, "e_pyramide", "Le temple du désert", 2, 1.5, [T_struct("minecraft:desert_pyramid")], [R_xp(300)],
      deps=["outils"])
quest(cC, "e_manoir", "Le manoir des bois", 4, 0.75, [T_struct("minecraft:mansion")], [R_xp(1500)],
      deps=["outils"], optional=True)

# ---- écriture ---------------------------------------------------------------
def kv(d, indent):
    pad = "\t" * indent
    return "".join(f"{pad}{k}: {v}\n" for k, v in d.items())

def write_chapter(ch):
    L = ["{\n"]
    L.append(f'\tdefault_hide_dependency_lines: false\n')
    L.append(f'\tdefault_quest_shape: ""\n')
    L.append(f'\tfilename: {s(ch["filename"])}\n')
    L.append(f'\tgroup: ""\n')
    L.append('\thide_quest_details_until_startable: true\n')
    L.append(f'\ticon: {item(ch["icon"])}\n')
    L.append(f'\tid: {s(ch["id"])}\n')
    L.append(f'\torder_index: {ch["order"]}\n')
    L.append("\tquests: [\n")
    for q in ch["quests"]:
        L.append("\t\t{\n")
        if q["deps"]:
            L.append("\t\t\tdependencies: [" + ", ".join(s(d) for d in q["deps"]) + "]\n")
        if q["icon"]:
            L.append(f'\t\t\ticon: {item(q["icon"])}\n')
        L.append(f'\t\t\tid: {s(q["id"])}\n')
        if q["optional"]:
            L.append("\t\t\toptional: true\n")
        if q["rewards"]:
            L.append("\t\t\trewards: [\n")
            for rid, rt, data in q["rewards"]:
                L.append("\t\t\t\t{\n" + kv(data, 5) + f'\t\t\t\t\tid: {s(rid)}\n\t\t\t\t\ttype: {s(rt)}\n\t\t\t\t}}\n')
            L.append("\t\t\t]\n")
        if q["shape"]:
            L.append(f'\t\t\tshape: {s(q["shape"])}\n')
        if q["size"]:
            L.append(f'\t\t\tsize: {q["size"]}d\n')
        L.append("\t\t\ttasks: [\n")
        for tid, tt, data in q["tasks"]:
            L.append("\t\t\t\t{\n" + kv(data, 5) + f'\t\t\t\t\tid: {s(tid)}\n\t\t\t\t\ttype: {s(tt)}\n\t\t\t\t}}\n')
        L.append("\t\t\t]\n")
        L.append(f'\t\t\tx: {float(q["x"])}d\n\t\t\ty: {float(q["y"])}d\n')
        L.append("\t\t}\n")
    L.append("\t]\n}\n")
    return "".join(L)

os.makedirs(os.path.join(QDIR, "chapters"), exist_ok=True)
os.makedirs(os.path.join(QDIR, "lang"), exist_ok=True)
os.makedirs(os.path.join(QDIR, "reward_tables"), exist_ok=True)

for ch in chapters:
    with open(os.path.join(QDIR, "chapters", ch["filename"] + ".snbt"), "w", encoding="utf-8") as f:
        f.write(write_chapter(ch))

with open(os.path.join(QDIR, "data.snbt"), "w", encoding="utf-8") as f:
    f.write("{\n"
            "\tdefault_consume_items: false\n"
            "\tdefault_quest_shape: \"circle\"\n"
            "\tdefault_reward_team: false\n"
            "\tfallback_locale: \"en_us\"\n"
            "\tversion: 13\n"
            "}\n")

with open(os.path.join(QDIR, "chapter_groups.snbt"), "w", encoding="utf-8") as f:
    f.write("{\n\tchapter_groups: [ ]\n}\n")

lang["file.0000000000000001.title"] = "L'Empire d'Airain"
LOGI["file.0000000000000001.title"] = "file.title"

def lang_snbt(d):
    out = ["{\n"]
    for k in sorted(d):
        v = d[k]
        if isinstance(v, list):
            if not v:
                continue
            out.append(f"\t{s(k)}: [\n" + "".join(f"\t\t{s(x)}\n" for x in v) + "\t]\n")
        else:
            out.append(f"\t{s(k)}: {s(v)}\n")
    out.append("}\n")
    return "".join(out)

fr_logical = {LOGI[k]: v for k, v in lang.items()}
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "fr_logical.json"), "w", encoding="utf-8") as f:
    json.dump(fr_logical, f, ensure_ascii=False, indent=1)
en_path = os.path.join(here, "en_logical.json")
en_lang = None
if os.path.exists(en_path):
    en_logical = json.load(open(en_path, encoding="utf-8"))
    missing = sorted(set(fr_logical) - set(en_logical)); extra = sorted(set(en_logical) - set(fr_logical))
    if missing or extra:
        print("TRADUCTION INCOMPLETE", "manquantes:", missing, "en trop:", extra); sys.exit(1)
    for k in fr_logical:
        if isinstance(fr_logical[k], list) != isinstance(en_logical[k], list):
            print("TYPE DIFFERENT", k); sys.exit(1)
    en_lang = {k: en_logical[LOGI[k]] for k in lang}
with open(os.path.join(QDIR, "lang", "fr_fr.snbt"), "w", encoding="utf-8") as f:
    f.write(lang_snbt(lang))
with open(os.path.join(QDIR, "lang", "en_us.snbt"), "w", encoding="utf-8") as f:
    f.write(lang_snbt(en_lang if en_lang else lang))

# résumé pour la vérification
summary = {"chapters": len(chapters), "quests": sum(len(c["quests"]) for c in chapters),
           "items": sorted({d["item"] for c in chapters for q in c["quests"] for _, tt, d in q["tasks"] if tt == "item"}
                           | {d["item"] for c in chapters for q in c["quests"] for _, rt, d in q["rewards"] if rt == "item"}),
           "entities": sorted({d["entity"] for c in chapters for q in c["quests"] for _, tt, d in q["tasks"] if tt == "kill"}),
           "structures": sorted({d["structure"] for c in chapters for q in c["quests"] for _, tt, d in q["tasks"] if tt == "structure"})}
print(json.dumps(summary, ensure_ascii=False, indent=1))
