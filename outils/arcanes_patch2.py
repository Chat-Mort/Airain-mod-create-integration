f = 'gen_v2.py'; s = open(f).read()
s = s.replace('lire = lambda: T_check()\n', '', 1)
s = s.replace('def R_coin(kind, n=1):', '''def R_carnet(n): return R_cmd("loot give @s loot kubejs:carnet/apprentie_%d" % n)   # une page du carnet de l'apprentie
lire = lambda: T_check()
def R_coin(kind, n=1):''', 1)
AR = '''
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
             ["\\"The Echo is strongest where the trees change colour.\\" Find an archwood forest: blue, red, green or purple, each hue sings differently."]))
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
             ["\\"Our relays hold no one. They pass things on, then they let go.\\" The Empire's never gave back what they carried."]))
# III · le grimoire
quest(cR, "a_ars_table", ("La table du scribe", "The Scribe's Table"), 0, 4, [T_item("ars_nouveau:scribes_table")], [R_coin("cog", 1), R_carnet(3)],
      deps=["a_ars_livre"], subtitle=("III · Le grimoire", "III · The Spell Book"),
      desc=D(["Pour inscrire de nouveaux glyphes dans votre grimoire.", "&8Récompense : une page du carnet de l'apprentie.&r"],
             ["To inscribe new glyphs into your spell book.", "&8Reward: a page of the apprentice's notebook.&r"]))
quest(cR, "ar_glyphes", ("Trois volontés", "Three Wills"), 2, 4,
      [T_item("ars_nouveau:glyph_break"), T_item("ars_nouveau:glyph_heal"), T_item("ars_nouveau:glyph_light")], [R_coin("cog", 1)], deps=["a_ars_table"],
      desc=D(["Briser, soigner, éclairer. « Morgana disait qu'on juge un mage à son premier sort de soin. »"],
             ["Break, heal, light. \\"Morgana used to say you judge a mage by their first healing spell.\\""]))
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
             ["\\"Some of the lost were too small to keep a human shape. They took whatever shape they could.\\"",
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
              "\\"You don't wear the robe to protect yourself. You wear it so the lost recognise you.\\""]))
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
'''
s = s.replace('''
# =============================================================================
# EXPLORATION''', AR + '''
# =============================================================================
# EXPLORATION''', 1)
open(f, 'w').write(s); print('ok')
