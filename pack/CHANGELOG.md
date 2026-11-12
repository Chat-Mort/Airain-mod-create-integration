# Notes de version — L'Empire d'Airain

Une entrée par jour, la plus récente en haut. Les numéros sont ceux du mod du pack (`airain-X.jar`).
À chaque mise à jour : supprimer `config/ftbquests/quests` avant de copier le nouveau `config`.

---

## 12 novembre 2026 — versions 1.47.0 à 1.47.3

**Ajouts**
- **Machines d'Écho**, le pont entre Create et Ars Nouveau, en milieu de partie :
  - **Turbine d'Écho** : un moteur de Create qui boit de l'Écho liquide amené par les tuyaux (20 mB par seconde) pour 64 tr/min et 1 024 de force. L'arbre sort à l'avant, et une cheminée à pales, creusée dans le dessus, évacue la vapeur d'Écho ;
  - **Sourcelink mécanique** : l'inverse, la rotation devient de l'Écho liquide, à pomper hors de sa cuve, avec un peu de perte. Son engrenage et sa gemme tournent avec l'axe ;
  - **Diffuseur d'Écho** : posé devant un ventilateur, il donne un nouveau traitement, l'imprégnation. Éclat d'améthyste ou lapis en gemme de source, bloc d'améthyste en bloc de gemme de source, sculk en éclat d'écho ;
  - **Condenseur d'Écho** : la source des jarres devient de l'**Écho liquide**, qui passe dans les tuyaux de Create (socle givré), et l'inverse à 90 % (socle chauffé au rouge, couvercle relevé, vapeur). Le liquide se voit dans la cuve à sa vraie hauteur. Au bec verseur, l'Écho liquide imprègne les objets un par un.
- **Glyphe de l'engrenage** (Ars Nouveau, niveau 2) : il accélère une machine de Create quelques secondes, grippe les automates (Rôdeur, Centurion nain, golems de l'End…) et soigne les gardiens d'airain.
- Livre de l'ingénieur : un cinquième sommaire, **Fusion**, avec une page par machine.
- Annexe Ingénierie : une ligne de cinq quêtes, « Les machines réfractaires ».

---

## 6 novembre 2026 — versions 1.44.0 à 1.46.1

**Ajouts**
- **Deux manuels d'armes** :
  - le *Règlement des armes de l'Empire* (livre, lingot de laiton, épée en fer) ;
  - le *Traité des armes de l'Écho* (livre, gemme d'Écho, éclat d'améthyste).

  Une page par arme, couronne, diadème et ensemble d'armure de fin : caractéristiques, pouvoirs, forge et une devise. Une page reste « ?????????? » tant que personne dans l'équipe n'a porté l'objet. Deux nouvelles quêtes dans l'annexe Arsenal.

- **Le choix final se fait dans le monde.**
  - À la mort de l'Empereur, sa machine reste à l'endroit où il est tombé, éteinte, et le Cœur d'Airain s'éteint.
  - Fin Empire : poser le Cœur éteint dans la machine, puis l'allumer avec un cœur du Gardien des enfers.
  - Fin Écho : poser le Cœur éteint sur le résonateur d'un Grand Relais, puis frapper avec le diapason d'Ada, un Écho primordial sur soi.

  La quête « Le choix final » se valide toute seule. Seule la fin choisie apparaît ensuite dans le livre.
- **Le Cœur brisé** : le premier Cœur, volé par Morgana. Le gardien du Vide le laisse une seule fois dans la partie, et il entre dans la recette du Cœur d'Airain. Le Cœur n'existe donc qu'en un seul exemplaire.
- Pages de Morgana III réécrites : le vol du premier Cœur.
- **Table d'enchantement de l'Empire** : un objet qui porte déjà l'enchantement paie moins. Pour un niveau normal, on paie seulement la différence (Protection III → IV : 3 niveaux au lieu de 14). Pour un niveau ouvert par un tome, la réduction est de 50 % au plus, soit 50 % divisés par le niveau maximum, pour chaque niveau déjà présent (Protection III → V : 25 niveaux au lieu de 40). Le prix réduit s'affiche comme chez les villageois : l'ancien prix barré, puis le nouveau.

**Changements**
- La reliure passe à neuf livres, avec les deux manuels.
- Commentaires du code plus clairs.
- Livre de quêtes : les plaques de titre de section sont retirées.

**Corrections**
- Plantage au lancement du jeu et du serveur depuis la 1.44.0 : le Traité des armes de l'Écho était enregistré deux fois.
- Textures retouchées : couronne d'airain sacrée, Chroniques, balise de défense, graisseur, et les trophées Œil du Gardien, Engrenage du Rôdeur, Cœur de magma et Sceau du Centurion.

---

## 5 novembre 2026 — versions 1.41.5 à 1.43.3

**Ajouts**
- **Améliorations de capitale**, après la fin. On pose des plans sur l'étendard de la capitale et on paie en soleils :
  - agrandissement : zone jusqu'à 320 blocs et 9 gardiens ;
  - infirmerie : régénération dans la zone et soin des gardiens ;
  - station météo : beau temps, pluie ou orage à volonté ;
  - forge de garnison : réparation de l'équipement porté.

  Quatre nouvelles quêtes dans l'annexe Bases et capitales, et une page dans le livre de l'ingénieur.
- **Nouveaux écrits**, pour que chaque camp ait son personnage clé, son dirigeant et son personnage secondaire :
  - Carnets d'Elias Vael (I à IV) ;
  - Journal d'Héléna Strass (7 pages déchirées) ;
  - Fragments brûlés d'Auguste Ferrand (I à III) ;
  - Pages de Morgana III, qui explique le gardien du Vide et son « Bientôt » ;
  - Dernière page d'Ada, au Grand Relais.
- **Fins complétées** :
  - Empire : le testament d'Auguste, donné avec la couronne ;
  - Écho : la voix d'Ada répond à Elias.

  Les épilogues passent à 5 pages.
- **Chroniques, archives** : un index complet des 51 écrits, rangé par camp puis par auteur. Les écrits pas encore trouvés apparaissent en « ?????????? », avec un compteur.

- **Musique** :
  - nouveau morceau de surface, Alone, en alternance avec le thème principal ;
  - deux nouveaux morceaux pour l'End, Almost Safe et Echoing Voices ;
  - tous les morceaux commencent par un court fondu d'entrée.
- **Thème d'Ada et d'Elias**, Mechanical Love : il joue la première fois qu'on trouve la lettre jamais ouverte, puis la première fois qu'on trouve la dernière page d'Ada.
- **Thème de la fin**, Epilogue : il joue au choix final, quelle que soit la fin.

**Changements**
- L'apprentie de Morgana a un nom : **Sybille Arden**. Ses carnets s'appellent maintenant « Carnet de Sybille Arden ».
- Balise de défense : les battements et la sirène ne jouent plus qu'au lancement et aux annonces de vague. La corne coupe tout.
- Livre de l'ingénieur à jour : balise, grand étendard, fragments de résonance.

**Corrections**
- Le rapport d'Elias Vael, sur le pupitre de la station de capsules, affichait les relevés d'Octave. Il a retrouvé ses 6 pages.
- Les écrits trouvés dans les coffres n'avaient pas de titre dans les archives des Chroniques.
- Épilogue Écho : il ne parle plus de Réfractaires vivants dans l'End.

---

## 4 novembre 2026 — versions 1.40.0 à 1.41.4

**Ajouts**
- **Bornes de commande**, après la fin : la Machine différentielle (Empire) et l'Archive résonante (Écho). On choisit des matières premières dans un catalogue, on paie en pièces, et la livraison arrive une minute plus tard sur la zone d'arrivage. Recettes à l'établi mécanique de Create et à l'appareil d'enchantement d'Ars Nouveau.
- Grand étendard : la bannière simple peut être placée à gauche ou à droite.
- **La voie de l'Écho étoffée** : nouveau chapitre « La voie de l'Écho », avec les carnets de l'apprentie de Morgana en récompense des quêtes.
- **Musique** : le thème principal au menu et en surface, Hells Guards dans le Nether.

**Changements**
- **Tous les identifiants et fichiers du mod passent en anglais.** Les mondes existants sont convertis automatiquement.
- Livre de quêtes réorganisé :
  - groupes de chapitres (L'Empire, La voie de l'Écho, Annexes) ;
  - chapitres centrés ;
  - titres de section en plaques de laiton.
- Textures retouchées : épées, plaques de fondation (rouage et cristal arcanique), motifs d'étendard (avec leur relief).

**Corrections**
- L'ancienne petite balise a été retirée.
- Faux avertissements du diagnostic au démarrage.

---

## 3 novembre 2026 — versions 1.24.1 à 1.39.0

**Ajouts**
- **Modules de gardien** : 6 modules (tête, épaules, torse), passage au niveau II à la table de forgeron.
- **Netherite sacrée**, qui améliore :
  - la couronne ;
  - la fondation : zone ×1,5 et 6 gardiens ;
  - la balise : elle foudroie les assaillants ;
  - le socle : effet de niveau II.
- **Plaque impériale** (bloc d'étoile du Nether, assemblage au déployeur).
- **Lignée de l'Empire**, réservée à la fin Empire : armures sacrée et impériale, armes (épée, katana, espadon, twinblade), pioche Filon, sceptre impérial.
- **Lignée de l'Écho**, réservée à la fin Écho :
  - diadème, arcanium, bloc d'écho primordial ;
  - armures et armes runiques puis arcaniques ;
  - sceptre arcanique.
- **Coiffes de fin** :
  - Empire : couronne, casque couronné, couronne sacrée, Couronne de l'Empereur ;
  - Écho : casque au diadème, tiare runique, Nimbe.

  Les coiffes finales permettent de voler.
- **Gardiens d'élite** : Capitaine impérial et Gardien d'Écho, un par base.
- **Trône impérial et Solium de la Prêtresse** :
  - Trône : décrets de guerre, de forge et de prospérité ;
  - Solium : chants des âmes, de la croissance et de la résonance.
- **Capitales impériale et arcanique**, avec les couleurs de leur camp.
- **Trophées des boss avancés** : force, résistance, célérité, absorption, satiété.
- **Gravure des trophées** (2 couronnes) : un second effet par trophée.
- Livre de l'ingénieur : quatre sommaires (blocs, objets, Empire, Écho), un chapitre par set.

**Changements**
- Nouvelles icônes d'armes, nouvelles textures des katanas et du lingot d'arcanium.
- Livres : signet de ruban pour revenir au sommaire, et touches Début / Retour arrière.

**Corrections**
- Plantage « Not building! » dans l'aperçu de l'écran du socle.
- Mise en page des livres : sommaire, numéros de page, trophées, Chroniques, atlas.
- Coiffes sans cube, zone de l'espadon, tourbillon de la twinblade, recettes d'Ars Nouveau.

---

## 2 novembre 2026 — versions 1.21.0 à 1.24.0

**Ajouts**
- **Gardiens d'airain** : automates réparés à la clé qui défendent les bases.
- **Choix final** entre la fin Empire et la fin Écho, avec livres d'épilogue, récompenses et bénédiction de l'Écho (sonar, moisson d'âmes).
- **Couronne d'airain** : modèle 3D, loupe d'ingénieur avec zoom, casque couronné.
- **Chroniques oubliées** : le récit, le journal de bord et les archives des écrits.
- **Reliure de l'ingénieur** : huit livres rangés ensemble, ouverts par onglets depuis un sac.
- **Livre de l'ingénieur**, le manuel des machines de l'Empire.
- Tableau de service, atlas impérial, presse à affiches (affiches impériales et réfractaires).
- **Suites de fin** : rebâtir l'Empire (charte impériale) ou apaiser les relais.
- Comptoirs : cartes de l'Empire et plans de construction.

**Changements**
- Touches : la Reliure sur K (B ouvre les sacs), la loupe sur H.

---

## 30 octobre 2026 — versions 1.18.0 à 1.20.0

**Ajouts**
- **Balise de défense** : tour-phare à sirène (3 × 3 × 8), qui déclenche un assaut en vagues.
- **Codex de l'Empire** : une page par créature, notes d'ingénieur, pages de boss.

**Corrections**
- Le registre des fondations s'ouvre dans son propre écran, et sa mise en page ne déborde plus.

---

## 29 octobre 2026 — versions 1.9.0 à 1.17.1

**Ajouts**
- **Grand étendard**, avec une bannière réglable :
  - mât de 5 à 8 blocs ;
  - franges, fleurons, bannière double, lanternes ;
  - mode décoratif.
- **Bannières** :
  - gabarit pour copier et coller une apparence ;
  - partitions, mise en berne, vent selon la météo ;
  - hissage par rotation Create ou selon la présence de joueurs ;
  - bannière murale.
- **Piédestal de l'Empire v2** : matériaux, velours, présentations (cloche, chevalet), plaque gravée, éclairage.
- **Banc d'entretien v2** (modules, affûtage). Le désenchanteur peut purger les malédictions.
- Interfaces au style de l'Empire (laiton, rivets, touches de machine à écrire).

---

## 28 octobre 2026 — versions 1.4.0 à 1.8.3

**Ajouts**
- **Table d'enchantement de l'Empire**, qui lit les bibliothèques sculptées et utilise les tomes anciens avec l'encre runique, et **désenchanteur**.
- **Socle de l'Empire** : un trophée de boss exposé donne son effet à toute l'équipe.
- **Pierres de fondation** et **registre des fondations** : bases nommées, zone réglable, titre à l'entrée.
- **Étendard de fondation** : trois styles de mât, bannière animée, motifs de l'Empire et des Réfractaires.
- Gardien des Cieux translucide, avec des ailes en vitrail.

---

## 27 octobre 2026 — versions 1.0.0 à 1.3.2

**Ajouts**
- **Banc d'entretien** : une machine de Create qui répare l'équipement à l'huile. Le temps dépend de la vitesse de rotation et des enchantements.

---

*Avant le 27 octobre : quêtes, structures, textes et réglages du pack (KubeJS), sans le mod. Ces changements n'ont pas été notés au jour le jour.*
