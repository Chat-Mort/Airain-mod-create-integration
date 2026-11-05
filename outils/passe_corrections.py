# Passe complète du pack (5 novembre) : corrections de textes, doublons retirés, noms clarifiés.
# Exécuté par gen_v2.py après les revues de descriptions, avant la mise en page.
def _desc(k, fr, en): tr(f"quest.{QUESTS[k]}.quest_desc", (fr, en))
def _titre(k, fr, en): tr(f"quest.{QUESTS[k]}.title", (fr, en))
def _rep(fr_a, fr_b, en_a, en_b):
    for lg, a, b in (("fr", fr_a, fr_b), ("en", en_a, en_b)):
        n = 0
        for k, v in LANG[lg].items():
            if isinstance(v, list):
                nv = [x.replace(a, b) for x in v]
                if nv != v: LANG[lg][k] = nv; n += 1
            elif a in v: LANG[lg][k] = v.replace(a, b); n += 1
        assert n, (lg, a)
# ---- l'appel de l'Écho : les textes écrasés par les anciennes revues
_desc("a_ars_source",
      ["Près des cristaux, l'air se refroidit, comme si quelqu'un passait. Les Réfractaires avaient appris à retenir ce froid dans l'améthyste. Ils l'appelaient l'&dÉcho&r.",
       "La chambre d'imprégnation fixe l'Écho dans l'améthyste : des gemmes de source. Posez-y de l'améthyste et laissez-la se charger ; sa recette est dans EMI.",
       "&8Récompense : la première page du carnet d'une apprentie réfractaire.&r"],
      ["Near the crystals the air turns cold, as if someone were passing by. The Refractories had learned to hold that chill in amethyst. They called it the &dEcho&r.",
       "The imbuement chamber binds the Echo into amethyst: source gems. Put amethyst in it and let it charge; its recipe is in EMI.",
       "&8Reward: the first page of a Refractory apprentice's notebook.&r"])
_desc("a_ars_livre",
      ["Un sort, c'est une volonté qu'on confie à l'Écho. Commencez petit : de la lumière dans la mine, une roche qui cède. Les égarés aiment se rendre utiles.",
       "Un grimoire de novice et le glyphe de lumière. Ouvrez le grimoire pour composer vos sorts à partir de glyphes ; ils puisent dans votre réserve d'Écho.",
       "&8Ouvre le chapitre &dLes Arcanes&8, la seconde voie de l'histoire.&r"],
      ["A spell is a will entrusted to the Echo. Start small: light in the mine, a rock that gives way. The lost like to be useful.",
       "A novice spell book and the light glyph. Open the book to compose spells from glyphs; they draw on your Echo reserve.",
       "&8Opens the &dThe Arcana&8 chapter, the story's second path.&r"])
_desc("l_relais",
      ["Le cycle 212, la ligne a cédé en pleine charge. Une partie du flux n'est jamais arrivée au Cœur. L'Empire a interdit le mot. Les cristaux, eux, ont continué de pousser.",
       "Trouvez un relais brisé et lisez le rapport d'incident sur le pupitre. C'est là que l'Écho s'est échappé."],
      ["On cycle 212 the line gave way under full load. Part of the flow never reached the Heart. The Empire banned the word. The crystals kept growing anyway.",
       "Find a broken relay and read the incident report on the lectern. This is where the Echo escaped."])
_desc("dragon",
      ["Le Gardien des Cieux n'est pas une machine, ni une bête de l'End. &dMorgana Dalmont&r l'a appelé de ses mains et l'a lié aux tours d'obsidienne, pour garder les portes des siens. Ses pages se trouvent encore dans les cités de l'End.",
       "Brisez d'abord les cristaux qui le nourrissent, sur les piliers. Il laisse un œuf : posé sur un socle de l'Empire, il protège toute l'équipe des chutes."],
      ["The Sky Guardian is neither a machine nor a beast of the End. &dMorgana Dalmont&r called it with her own hands and bound it to the obsidian towers, to guard her people's gates. Her pages can still be found in the End cities.",
       "First break the crystals that feed it, on the pillars. It leaves an egg: displayed on an Empire pedestal, it protects the whole team from falls."])
# ---- renvois vers des chapitres disparus
_rep("Le chapitre « Arsenal et Écho » détaille toutes les armes.", "L'annexe « Arsenal » détaille toutes les armes.",
     'The "Arsenal and Echo" chapter covers every weapon.', 'The "Arsenal" side chapter covers every weapon.')
_rep("L'Écho primordial vient de l'annexe « Les Échos perdus ».", "L'Écho primordial s'obtient dans la voie de l'Écho, section « Les Échos perdus ».",
     'The Primordial Echo comes from the side chapter "The Lost Echoes".', 'The Primordial Echo is earned on the Echo path, in "The Lost Echoes" section.')
_rep("attend au Grand Relais (Échos perdus).", "attend au Grand Relais (section « Les Échos perdus », dans ce chapitre).",
     "waits at the Great Relay (Lost Echoes).", 'waits at the Great Relay ("The Lost Echoes" section of this chapter).')
tr(f"chapter.{hid('ch:arsenal')}.chapter_subtitle", (["Les armes de l'Empire : lames, artillerie et armes à feu."], ["The Empire's weapons: blades, artillery and firearms."]))
# ---- la balise : la sirène n'annonce plus que les vagues
_rep("Pendant l'assaut, sa sirène hurle et son phare balaie la base.", "Pendant l'assaut, son phare balaie la base, et sa sirène annonce chaque vague.",
     "During the assault, its siren wails and its light sweeps the base.", "During the assault, its light sweeps the base, and its siren announces each wave.")
# ---- le socle et ses neuf trophées
_desc("b_socle",
      ["&7Optionnel.&r Exposez un trophée de boss sur un socle : tant qu'il y reste, son effet profite à &6toute l'équipe&r, où que vous soyez.",
       "• Masque des enfers : résistance au feu ; Cœur du Gardien des enfers : régénération ; Œuf du Gardien des Cieux : aucun dégât de chute ; Écho primordial : vision nocturne ;",
       "• Visière du Colosse : force ; Cœur de magma : résistance ; Engrenage du Rôdeur : célérité ; Œil du Gardien : absorption ; Sceau du Centurion : satiété.",
       "&6Gravure&r : clic droit sur le socle avec &62 couronnes&r, et le trophée exposé gagne un second effet. Une plaque de netherite sacrée fait passer son effet au niveau II.",
       "&6Accroupi + clic droit main vide&r : les réglages du socle (matériau, velours, garnitures, colonne, présentation, éclairage, particules, plaque gravée au nom du trophée et au jour de la victoire).",
       "&8Deux trophées identiques ne cumulent pas. Clic droit main vide pour reprendre le trophée. Un comparateur lit le socle ; un gabarit de bannière copie son apparence.&r"],
      ["&7Optional.&r Display a boss trophy on a pedestal: as long as it stays there, its effect benefits &6the whole team&r, wherever you are.",
       "• Infernal Mask: fire resistance; Infernal Guardian Core: regeneration; Sky Guardian's Egg: no fall damage; Primordial Echo: night vision;",
       "• Colossus Visor: strength; Magma Heart: resistance; Prowler's Gear: haste; Guardian's Eye: absorption; Centurion's Seal: saturation.",
       "&6Engraving&r: right-click the pedestal with &62 crowns&r, and the displayed trophy gains a second effect. A sacred netherite plate raises its effect to level II.",
       "&6Sneak + right-click empty-handed&r: the pedestal settings (material, velvet, trims, column, display, lighting, particles, plaque engraved with the trophy's name and the day of the victory).",
       "&8Identical trophies don't stack. Right-click empty-handed to take the trophy back. A comparator reads the pedestal; a banner template copies its look.&r"])
# ---- les Réfractaires ont disparu
_rep("Les Réfractaires, ceux qui ont refusé le Transfert, vivent dans des camps de fortune. Environ un camp sur trois tient un étal qui vend la &6fiole funeste&r.",
     "Les Réfractaires, ceux qui ont refusé le Transfert, vivaient dans des camps de fortune. Ils ont disparu, mais dans environ un camp sur trois, un étal vend encore la &6fiole funeste&r.",
     "The Refractories, those who refused the Transfer, live in makeshift camps. About one camp in three keeps a stall selling the &6ominous bottle&r.",
     "The Refractories, those who refused the Transfer, lived in makeshift camps. They are gone, but in about one camp in three a stall still sells the &6ominous bottle&r.")
# ---- Octave Lanfrey : son journal, et le frère d'Ada
_rep("&6&lJournal d'ingénieur&r", "&6&lJournal d'Octave Lanfrey&r", "&6&lEngineer's Journal&r", "&6&lOctave Lanfrey's Journal&r")
_rep("&oIl a répondu. Il sait que quelqu'un vient.&r", "&oSi un jour le Cœur répond, c'est que quelqu'un vient. Ce sera vous.&r",
     "&oIt answered. It knows someone is coming.&r", "&oIf the Heart ever answers, it means someone is coming. It will be you.&r")
_rep("et une voix que vous connaissez : celle d'Elias Vael.", "et une voix que vous connaissez : celle d'Elias Vael, le frère d'Ada.",
     "and a voice you know: Elias Vael's.", "and a voice you know: Elias Vael's, Ada's brother.")
# ---- noms plus clairs
_titre("vague1", "Les araignées de bronze", "The Bronze Spiders")
_titre("vague2", "Les sphères", "The Spheres")
_titre("vague3", "Les forges rallumées", "The Rekindled Forges")
# ---- le grand étendard : bannière simple à gauche ou à droite
_rep("le fleuron du sommet (le rouage tourne), la double bannière et les lanternes.", "le fleuron du sommet (le rouage tourne), la bannière simple (à gauche ou à droite) ou double, et les lanternes.",
     "the finial (the gear turns), the double banner and the lanterns.", "the finial (the gear turns), a single banner (left or right) or a double one, and the lanterns.")
# ---- les commandes de l'Empire : une ligne d'ambiance chacune
_CMD = {
 "o_pain": ("Les cantines des avant-postes rallumés réclament du pain : les gardiens ne mangent pas, mais leurs ateliers se souviennent de ceux qui mangeaient.", "The rekindled outposts' canteens ask for bread: guardians don't eat, but their workshops remember those who did."),
 "o_alliage": ("Chaque réparation de l'Empire commence par de l'alliage d'andésite. Il n'y en a jamais assez.", "Every repair of the Empire starts with andesite alloy. There is never enough."),
 "o_plaques": ("Les ateliers de garnison réclament de la tôle pour rapiécer leurs gardiens.", "The garrison workshops want sheet metal to patch up their guardians."),
 "o_cuivre": ("Les chaudières des cités fuient. Il leur faut du cuivre, beaucoup de cuivre.", "The cities' boilers are leaking. They need copper, a lot of copper."),
 "o_tuyaux": ("Le second réseau, celui sous les rues, se répare tronçon par tronçon.", "The second network, the one beneath the streets, is being repaired section by section."),
 "o_laiton": ("Le métal de l'Empire, celui de ses insignes : ses entrepôts le paient au prix fort.", "The Empire's metal, the one of its insignia: its warehouses pay well for it."),
 "o_precision": ("Rien d'important ne fonctionne sans eux. L'Empire en commande sans compter.", "Nothing important works without them. The Empire orders them without counting."),
 "o_rails": ("La grande ligne doit rouvrir : chaque rail livré la rapproche d'une cité.", "The great line must reopen: every rail delivered brings it closer to a city."),
 "o_obus": ("Les batteries des remparts n'ont plus rien à tirer. Remplissez leurs soutes.", "The rampart batteries have nothing left to fire. Fill their magazines."),
 "o_enveloppes": ("La flotte du ciel a des trous dans ses ballons. Les chantiers de toile ne suffisent plus.", "The sky fleet's balloons are torn. The canvas yards can't keep up."),
 "o_tubes": ("Les machines qui pensent demandent des tubes neufs : les vieux ont grillé pendant le grand sommeil.", "The machines that think need new tubes: the old ones burned out during the long sleep."),
 "o_netherite": ("Les gardes de la forge des âmes veulent leur armure. Ils paient en couronnes.", "The Soul Forge guards want their armor. They pay in crowns."),
}
for _k, (_fr, _en) in _CMD.items():
    _a, _b = LANG["fr"][f"quest.{QUESTS[_k]}.quest_desc"], LANG["en"][f"quest.{QUESTS[_k]}.quest_desc"]
    _desc(_k, [_fr] + list(_a), [_en] + list(_b))
# ---- doublons retirés (leurs suites passent à la quête équivalente)
_RETIRE = {"e_avantposte": "l_refractaires", "e_manoir": "e_cite", "mage": None}
_rid = {QUESTS[k]: (QUESTS[v] if v else None) for k, v in _RETIRE.items()}
for _c in chapters:
    _c["quests"] = [q for q in _c["quests"] if q["id"] not in _rid]
    for _q in _c["quests"]:
        _n = []
        for _d in _q["deps"]:
            _d = _rid.get(_d, _d) if _d in _rid else _d
            if _d and _d not in _n: _n.append(_d)
        _q["deps"] = _n
