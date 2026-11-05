import re
p = "gen_v2.py"
s = open(p, encoding="utf-8").read()
def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:60], s.count(old))
    s = s.replace(old, new)

# ---- commandes : les plaques de fer valent plus que l'alliage
rep('("o_alliage", "create:andesite_alloy", 128, "bevel", 6,', '("o_alliage", "create:andesite_alloy", 128, "bevel", 4,')
rep('("o_plaques", "create:iron_sheet", 128, "sprocket", 2,', '("o_plaques", "create:iron_sheet", 128, "sprocket", 4,')

# ---- banc d'entretien
i = s.index('quest(c3, "banc"'); j = s.index('quest(c3, "vapeur"')
s = s[:i] + '''quest(c3, "banc", ("Le banc d'entretien", "The Maintenance Bench"), 4, 4, [T_item("airain:maintenance_bench")],
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
              "A repaired tool or weapon comes out &6sharpened&r for a while (see \\"The Edge of the Blade\\").",
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
''' + s[j:]

# ---- désenchanteur : purge des malédictions
rep('''              "&8Clic droit avec l'objet, puis avec des livres ; main vide pour reprendre le livre enchanté. Entonnoirs et tapis fonctionnent aussi.&r"],''',
    '''              "&8Clic droit avec l'objet, puis avec des livres ; main vide pour reprendre le livre enchanté. Entonnoirs et tapis fonctionnent aussi. Les lunettes d'ingénieur montrent l'opération en cours.&r"],''')
rep('''              "&8Right-click with the item, then with books; empty-handed to take the enchanted book. Funnels and belts work too.&r"]))''',
    '''              "&8Right-click with the item, then with books; empty-handed to take the enchanted book. Funnels and belts work too. Engineer's goggles show the current operation.&r"]))
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
              "&8Modules show on the bench, and engineer's goggles list them.&r"]))''')

# ---- socle
rep('''              "• Œuf du Gardien des Cieux : plus de dégâts de chute ;", "• Écho primordial : vision nocturne.",
              "&8Deux trophées identiques ne cumulent pas. Clic droit main vide pour reprendre le trophée.&r"],''',
    '''              "• Œuf du Gardien des Cieux : aucun dégât de chute ;", "• Écho primordial : vision nocturne.",
              "&6Accroupi + clic droit main vide&r : les réglages du socle. Matériau, velours et capitonnage, garnitures, colonne haute, présentation du trophée (lévitation, posé, chevalet, sous cloche), éclairage, particules et plaque gravée. La plaque se grave seule, au nom du trophée et au jour de la victoire.",
              "&8Deux trophées identiques ne cumulent pas. Clic droit main vide pour reprendre le trophée. Un comparateur lit le socle : plus le trophée donne d'effets, plus le signal est fort. Un gabarit de bannière copie aussi l'apparence d'un socle.&r"],''')
rep('''              "• Sky Guardian's Egg: no more fall damage;", "• Primordial Echo: night vision.",
              "&8Two identical trophies do not stack. Right-click empty-handed to take the trophy back.&r"]))''',
    '''              "• Sky Guardian's Egg: no fall damage at all;", "• Primordial Echo: night vision.",
              "&6Sneak + right-click empty-handed&r: the pedestal settings. Material, velvet and tufting, trims, tall column, trophy display (levitating, resting, easel, under a glass dome), lighting, particles and engraved plaque. The plaque engraves itself with the trophy's name and the day of the victory.",
              "&8Two identical trophies do not stack. Right-click empty-handed to take the trophy back. A comparator reads the pedestal: the more effects the trophy gives, the stronger the signal. A banner template also copies a pedestal's look.&r"]))''')
rep('''      desc=D(["&7Optionnel.&r Exposez quatre trophées différents dans votre base. Validez quand c'est fait."],
             ["&7Optional.&r Display four different trophies in your base. Tick the box when done."]))''',
    '''      desc=D(["&7Optionnel.&r Les palais de l'Empire exposaient leurs trophées sous les bannières de leurs fondateurs. Exposez quatre trophées différents dans votre base. Validez quand c'est fait.",
              "&8Le registre des fondations a une page pour les trophées de chaque base, et les bannières réglées « selon trophées » se hissent quand un trophée est exposé dans leur zone.&r"],
             ["&7Optional.&r The Empire's palaces displayed their trophies under their founders' banners. Display four different trophies in your base. Tick the box when done.",
              "&8The foundation register has a page for each base's trophies, and banners set to \\"by trophies\\" are hoisted when a trophy is displayed in their area.&r"]))''')

# ---- fondation
i = s.index('quest(cE, "e_fondation"'); j = s.index('quest(cT, "t_ligne"')
s = s[:i] + '''quest(cE, "e_fondation", ("La première fondation", "The First Foundation"), 0, -2, [T_item("airain:foundation_stone"), T_item("airain:foundation_registry")],
      [R_coin("bevel", 4)], deps=["outils"], optional=True,
      desc=D(["&7Optionnel.&r Plantez un &6étendard de fondation&r au cœur de votre base et donnez-lui un nom et une devise : chaque fois qu'un de vous deux entrera dans sa zone, ils s'afficheront à l'écran, encadrés de sa bannière.",
              "Clic droit pour tout régler. Page « Général » : nom, devise, style du mât (potence, vexillum, cérémonie). Page « Toile » : couleurs, partition et seconde couleur, motif et sa couleur, forme du bas, usure (neuve, usée, déchirée), broderie lumineuse.",
              "Clic droit avec une clé de Create pour agrandir la zone (16 à 128 blocs, accroupi pour réduire). Un comparateur contre l'étendard donne un signal plein tant que l'un de vous est dans la zone.",
              "Le &6registre des fondations&r liste toutes vos bases : nom, coordonnées, dimension, distance et trophées exposés.",
              "&8L'étendard de fondation est le maître de sa zone : les grands étendards et bannières qui s'y trouvent peuvent suivre sa présence (voir « Hisser les couleurs »).&r"],
             ["&7Optional.&r Plant a &6foundation standard&r at the heart of your base and give it a name and a motto: each time one of you enters its area, they show on screen, framed by its banner.",
              "Right-click to set it all. \\"General\\" page: name, motto, mast style (gallows, vexillum, ceremonial). \\"Cloth\\" page: colours, division and second colour, emblem and its colour, bottom shape, wear (new, worn, torn), glowing embroidery.",
              "Right-click with a Create wrench to enlarge the area (16 to 128 blocks, sneak to shrink). A comparator against the standard gives a full signal while one of you is in the area.",
              "The &6foundation register&r lists all your bases: name, coordinates, dimension, distance and displayed trophies.",
              "&8The foundation standard is the master of its area: the great standards and banners in it can follow its presence (see \\"Raise the Colours\\").&r"]))

# --- l'héraldique de l'Empire (mod Airain 1.10 à 1.17)
quest(cE, "h_grand", ("Le grand étendard", "The Great Standard"), 2, -3, [T_item("airain:great_standard")], [R_coin("cog", 1)],
      deps=["e_fondation", "laiton"], optional=True,
      desc=D(["&7Optionnel.&r Les places de l'Empire se reconnaissaient de loin : un mât de cinq à huit blocs, et une toile qui claquait au vent.",
              "Le &6grand étendard&r fait tout ce que fait l'étendard de fondation, en plus grand. Une troisième page, « Mât », règle la hauteur, la longueur et la largeur de la toile, le vent, les franges, le fleuron du sommet (le rouage tourne), la double bannière et les lanternes.",
              "Mode &6décoratif&r (page « Général ») : pas de titre à l'écran, pas de place dans le registre. Parfait pour orner une base qui a déjà sa fondation.",
              "&8Un signal de redstone le met en berne. La météo fait claquer la toile ; l'option « Vent commun » fait onduler ensemble toutes les bannières qui l'ont.&r"],
             ["&7Optional.&r The Empire's squares could be recognised from afar: a mast five to eight blocks tall, and a cloth snapping in the wind.",
              "The &6great standard&r does everything the foundation standard does, only bigger. A third page, \\"Mast\\", sets the height, the cloth's length and width, the wind, fringes, the finial (the gear turns), the double banner and the lanterns.",
              "&6Decorative&r mode (\\"General\\" page): no title on screen, no entry in the register. Ideal to adorn a base that already has its foundation.",
              "&8A redstone signal lowers it to half-mast. Weather makes the cloth snap; the \\"Shared wind\\" option makes every banner that has it wave together.&r"]))
quest(cE, "h_murale", ("La bannière murale", "The Wall Banner"), 4, -3, [T_item("airain:foundation_wall_banner", 2)], [R_coin("sprocket", 2)],
      deps=["h_grand"], optional=True,
      desc=D(["&7Optionnel.&r Dans les halls de l'Empire, les couleurs tombaient des murs jusqu'au sol.",
              "La &6bannière murale&r se pose contre un mur, sur sa tringle. Mêmes réglages de toile que les étendards ; sa page « Taille » choisit la longueur (2 à 4 blocs) et la largeur.",
              "&8Un signal de redstone l'enroule. Les camps réfractaires ont les leurs, en toile ignifugée.&r"],
             ["&7Optional.&r In the Empire's halls, the colours fell from the walls to the floor.",
              "The &6wall banner&r is placed against a wall, on its rod. Same cloth settings as the standards; its \\"Size\\" page picks the length (2 to 4 blocks) and the width.",
              "&8A redstone signal rolls it up. The Refractory camps have their own, in fireproof cloth.&r"]))
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
              "Great standards and wall banners have a \\"Hoisting\\" setting:",
              "• &6Manual&r: a Create shaft turning against the foot of the mast, or against the banner, raises or lowers it depending on the direction;",
              "• &6By presence&r: banners rise as soon as one of you enters the foundation standard's area, and come down when the last one leaves. All those in the area move together;",
              "• &6By trophies&r: they stay up while a trophy is displayed in the area.",
              "Set a banner to \\"by presence\\" in your base, leave the area and come back. Tick the box once you have seen it rise."]))
titres_taches("h_hissage", [("Voir une bannière se hisser à votre retour", "See a banner rise when you return")])
quest(cE, "h_pavoise", ("Une base pavoisée", "A Bedecked Base"), 10, -3, [T_check()], [R_coin("cog", 2), R_xp(500)],
      deps=["h_hissage", "h_gabarit"], optional=True,
      desc=D(["&7Optionnel.&r Une fondation digne de l'Empire : au moins quatre grands étendards ou bannières murales dans la zone d'un même étendard de fondation, aux mêmes couleurs, qui se hissent tous ensemble à votre arrivée.",
              "Validez quand c'est fait."],
             ["&7Optional.&r A foundation worthy of the Empire: at least four great standards or wall banners within the area of a single foundation standard, in the same colours, all rising together when you arrive.",
              "Tick the box when done."]))
titres_taches("h_pavoise", [("Quatre bannières hissées ensemble", "Four banners raised together")])

''' + s[j:]
open(p, "w", encoding="utf-8").write(s)
print("ok")
