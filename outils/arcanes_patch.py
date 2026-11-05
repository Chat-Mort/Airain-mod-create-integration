import re
f = 'gen_v2.py'; s = open(f).read()
def bloc(key):
    m = re.search(r'^quest\(c\w+, "' + key + r'",.*?(?=^\S)', s, re.S | re.M)
    assert m, key
    return m
def suppr(key):
    global s
    m = bloc(key); s = s[:m.start()] + s[m.end():]
for k in ("l_refractaires", "l_relais", "l_sanctuaire", "a_ars_livre", "a_ars_source", "a_ars_table", "a_ars_appareil", "a_ars_apprenti", "a_ars_archimage"):
    suppr(k)
# ---------------------------------------------------------------- chapitre IV : l'appel de l'Écho
C4 = '''# l'appel de l'Écho : la magie entre dans l'histoire principale
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
'''
s = s.replace('quest(c4, "prepa4",', C4 + 'quest(c4, "prepa4",', 1)
s = s.replace('''[T_item("minecraft:potion", 4), T_item("minecraft:golden_apple", 2)], [R_coin("sprocket", 2)], deps=["obus"],''',
              '''[T_item("minecraft:potion", 4), T_item("minecraft:golden_apple", 2)], [R_coin("sprocket", 2)], deps=["obus", "a_ars_livre"],''')
# ---------------------------------------------------------------- chapitre V
C5 = '''quest(c5, "l_relais", ("La ligne rompue", "The Broken Line"), 16, 2, [T_struct("kubejs:relais_brise"), lire()],
      [R_coin("sprocket", 1), R_item("kubejs:fragment_resonance", 2)], deps=["l_refractaires"], subtitle=("L'appel de l'Écho", "The Call of the Echo"),
      desc=D(["Le cycle 212, la ligne a cédé en pleine charge. Une partie du flux n'est jamais arrivée au Cœur. L'Empire a interdit le mot. Les cristaux, eux, ont continué de pousser.",
              "Trouvez un relais brisé et lisez le rapport d'incident sur le pupitre. C'est là que l'Écho s'est échappé."],
             ["On cycle 212 the line gave way under full load. Part of the flow never reached the Heart. The Empire banned the word. The crystals kept growing anyway.",
              "Find a broken relay and read the incident report on the lectern. This is where the Echo escaped."]))
'''
s = s.replace('quest(c5, "bientot",', C5 + 'quest(c5, "bientot",', 1)
s = s.replace('deps=["prepa5", "jetpack"],', 'deps=["prepa5", "jetpack", "l_relais"],', 1)
s = s.replace('''quest(c5, "dragon", ("Le Gardien des Cieux", "The Sky Guardian"), 10, 0, [T_kill("minecraft:ender_dragon")], [R_coin("crown", 1), R_xp(1500)],
      deps=["end"])''', '''quest(c5, "dragon", ("Le Gardien des Cieux", "The Sky Guardian"), 10, 0, [T_kill("minecraft:ender_dragon")], [R_coin("crown", 1), R_xp(1500)],
      deps=["end"],
      desc=D(["Ce n'est pas une bête de l'End. &dMorgana Dalmont&r l'a appelée de ses mains, pour garder les portes des siens.",
              "Ses pages se trouvent encore dans les cités de l'End."],
             ["It is no beast of the End. &dMorgana Dalmont&r called it with her own hands, to guard her people's gates.",
              "Her pages can still be found in the End cities."]))''')
# ---------------------------------------------------------------- chapitre VI
C6 = '''quest(c6, "l_sanctuaire", ("Le journal d'Ada", "Ada's Journal"), 4, 4, [T_struct("kubejs:sanctuaire_refractaire"), lire()],
      [R_coin("cog", 1), R_cmd_visible("locate structure kubejs:grand_relais")], deps=["l_relais"],
      subtitle=("L'appel de l'Écho", "The Call of the Echo"),
      desc=D(["Elle a signé les plans des capsules. Puis elle a pris ceux qui voulaient vivre, et elle est partie vers le nord. Avant de rallumer quoi que ce soit, lisez ce qu'elle a laissé.",
              "Quelque part dans le nord froid, le sanctuaire réfractaire garde le journal d'&dAda Vesper&r. Lisez-le jusqu'au bout : la récompense indique où se trouve le Grand Relais."],
             ["She signed the capsule blueprints. Then she took those who wanted to live, and went north. Before you rekindle anything, read what she left behind.",
              "Somewhere in the cold north, the Refractory sanctuary keeps &dAda Vesper&r's journal. Read it to the end: the reward tells you where the Great Relay is."]))
'''
s = s.replace('quest(c6, "forger",', C6 + 'quest(c6, "forger",', 1)
s = s.replace('[T_item("kubejs:coeur_d_airain")], [R_xp(2000)], deps=["memoires", "mer"],', '[T_item("kubejs:coeur_d_airain")], [R_xp(2000)], deps=["memoires", "mer", "l_sanctuaire"],', 1)
# ---------------------------------------------------------------- chapitre VII : les deux voix
C7 = '''quest(c7, "deux_voix", ("Les deux voix", "The Two Voices"), 14, -1, [T_check()], [R_xp(500)], deps=["coeur_eteint"],
      desc=D(["L'Empire dort dans le Cœur et promet l'éternité à ceux qui le servent.",
              "Ada, Morgana et Octave disent autre chose : le Transfert ne tue pas, il enferme, et des milliers de voix attendent encore.",
              "&6Rallumer le Cœur&r, c'est rendre l'Empire au monde. &3Le briser&r, c'est rendre les âmes à elles-mêmes.",
              "Il n'y a pas de bonne réponse. Seulement la vôtre."],
             ["The Empire sleeps in the Heart and promises eternity to those who serve it.",
              "Ada, Morgana and Octave say otherwise: the Transfer does not kill, it imprisons, and thousands of voices are still waiting.",
              "&6Rekindling the Heart&r gives the Empire back to the world. &3Breaking it&r gives the souls back to themselves.",
              "There is no right answer. Only yours."]))
'''
s = s.replace('quest(c7, "f_empire",', C7 + 'quest(c7, "f_empire",', 1)
s = s.replace('[R_cmd("airain fin empire"), R_item("airain:imperial_charter", 3)], deps=["coeur_eteint"],', '[R_cmd("airain fin empire"), R_item("airain:imperial_charter", 3)], deps=["coeur_eteint", "deux_voix"],', 1)
s = s.replace('[R_cmd("airain fin echo")], deps=["coeur_eteint"],', '[R_cmd("airain fin echo")], deps=["coeur_eteint", "deux_voix"],', 1)
# les Échos perdus : le rapport de Vael suit la ligne rompue (déjà le cas) ; la résonance suit le journal d'Ada (déjà le cas)
open(f, 'w').write(s)
print('ok')
