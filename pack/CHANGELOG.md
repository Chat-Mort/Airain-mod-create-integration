# Notes de version — L'Empire d'Airain

Une entrée par jour, la plus récente en haut. Les numéros sont ceux du mod du pack (`airain-X.jar`).
À chaque mise à jour : supprimer `config/ftbquests/quests` avant de copier le nouveau `config`.

---

## 14 novembre 2026 — version 1.56.0

**Changements**
- Livre de l'ingénieur refait :
  - chaque chapitre tient en général sur une double page : icône et titre, une phrase d'histoire, puis le mode d'emploi en intertitres, puces et lignes avec l'icône de l'objet ;
  - le texte commence sous l'histoire, sur la page de gauche, et continue sur la droite ;
  - tous les textes sont raccourcis (environ 77 pages au lieu de 124) ; l'airain affiche ses ingrédients avec leurs icônes ;
  - nouvel onglet « Industrie » (airain, récupération, haut-fourneau, style impérial, passerelles, conduite d'air, atelier, mécanismes, mécanique, machines d'Écho) à la place de « Fusion » ; les sommaires ne débordent plus de la page.

## 14 novembre 2026 — versions 1.55.1 à 1.55.3

**Corrections (1.55.3)**
- Mémoire : les passerelles occupaient beaucoup trop de RAM (plus de 5 millions d'états de blocs en mémoire). On revient à environ 250 000 :
  - pont-levis et passerelle rétractable : leur sens et leur longueur sont gardés dans le bloc lui-même, plus dans son état ;
  - escalier à palier : il ne garde que ses deux côtés extérieurs ;
  - la clé de Create passe de rambarde à vitrée, puis à rien : un côté vidé reprend sa rambarde si un bloc voisin change.
- Les pièces de pont-levis et de passerelle rétractable déjà posées reviennent à leur sens et leur longueur par défaut : les casser et les reposer. Les côtés des paliers déjà posés se recalculent au prochain changement voisin (ou en les reposant).


**Corrections (1.55.2)**
- Rambardes à côté de la cage du monte-charge (la cabine, ou la case vide contre le mât) : elles restent à l'intérieur de la passerelle et ne gênent plus la cabine ni le joueur dedans.
- Passerelles mobiles relevées ou rentrées : le mécanisme et le bloc d'en face remettent leur rambarde à l'intérieur de leur bloc, au bout du passage, au lieu de la faire dépasser dans le vide.
- Sourcelink mécanique et turbine d'Écho posés contre un arbre de Create : ils se tournent maintenant vers l'arbre et s'y raccordent. Un bloc déjà posé à l'envers se recasse et se repose.


**Changements**
- Haut-fourneau impérial, plus imposant : 5 de haut et 54 briques réfractaires.
  - En bas, le creuset : 5 × 5 aux coins coupés, sur deux rangs. Le trou de coulée est au milieu de la face avant, la grille au centre du sol (brûleur à blaze dessous), et l'intérieur reste vide au deuxième rang.
  - Dessus, la cuve : 3 × 3 sur trois rangs, creuse, avec le gueulard au centre du sommet.
  - L'habillage d'airain suit la nouvelle forme : socle riveté, corniche sur l'épaulement, ceinture rivetée au pied de la cuve, blason, cornières sur tous les angles.
  - Un fourneau 3 × 3 déjà construit n'est plus reconnu : il faut le reconstruire.
- Une à trois tuyères, au milieu des côtés ou de l'arrière du creuset. Chaque ventilateur ajoute son débit.
- Construction du haut-fourneau : clic droit main nue sur le trou de coulée, et les blocs manquants apparaissent en hologramme pendant 30 secondes (les mauvais blocs sont entourés de rouge). Un clic droit avec le bon bloc le pose dans la case visée, même en l'air. Les particules orange et le texte dans le chat disparaissent ; les lunettes d'ingénieur comptent ce qui manque.
- Monte-charge : la cabine fait deux blocs de haut. Elle est fermée sur trois côtés (fenêtres vitrées en haut, toit avec plafonnier) et reste ouverte côté passerelles, avec le portail en bas. Le panneau de sélection d'étage passe en haut, contre la paroi du mât.
- La quête « Les briques réfractaires » demande 54 briques.

---

## 14 novembre 2026 — versions 1.54.0 et 1.54.1

**Corrections (1.54.1)**
- Le dessus de la main courante des rambardes s'affiche de nouveau.
- Plus de taches de couleur étrangères (vertes, bleues) sous les passerelles mobiles, sur le trou de coulée, la tuyère et le gueulard du haut-fourneau, ni sur les autres pièces qui dépassent de leur bloc.
- Passerelles mobiles : quand les segments se relèvent ou rentrent, le mécanisme et le bloc d'en face remettent leurs rambardes ; elles s'effacent de nouveau au redéploiement.

**Changements (1.54.1)**
- Allégeur impérial : flasques lisses sans motif d'engrenage, creusées en retrait, avec une bague qui ressort autour de l'arbre ; les voyants passent dans les coins du cadre.

**Changements**
- Passerelles d'airain : le sol (passerelle, escalier, rampe, palier) prend toute la largeur du bloc et les rambardes se dressent juste à l'extérieur, sur les blocs voisins. Elles n'apparaissent que du côté du vide et s'effacent dès qu'un bloc ou une autre passerelle est posé à côté.
- La clé de Create, sur un côté de passerelle ou de palier, passe de rambarde à garde-corps vitré, puis à côté ouvert (sans rambarde), puis de nouveau à rambarde. Un côté ouvert à la clé le reste.
- Les suspentes, garde-corps vitrés et plaques émaillées suivent la nouvelle position des rambardes.

**Ajouts**
- Pose assistée : clic droit avec une pièce de passerelle sur le bord ou la rambarde d'une passerelle posée, et la pièce se pose de l'autre côté, dans le prolongement et à la bonne hauteur (passerelle, escalier qui monte, rampe, palier). Accroupi, l'escalier et la rampe descendent.

---

## 13 novembre 2026 — versions 1.48.0 à 1.53.1

**Ajouts**
- **L'airain**, l'alliage secret de l'Empire : lingot, pépite, plaque, engrenage d'airain et airain en fusion. Il ne sort que du haut-fourneau.
- **Le haut-fourneau impérial**, une tour de 3 × 3 sur 4 en briques réfractaires, qui prend son habillage d'airain une fois montée (socle riveté, cornières, blason) :
  - le trou de coulée en façade, une grille au centre du sol avec un brûleur à blaze dessous, le gueulard au sommet, une tuyère sur un côté avec un ventilateur de Create ;
  - clic droit main nue sur le trou de coulée : il dit ce qui manque, et les places vides brillent ;
  - brûleur chauffé : refonte de la ferraille et des rouages brisés des automates ; surchauffé : alliage (3 cuivres, 1 zinc, 1 fondant donnent 4 lingots) ;
  - la vitesse du ventilateur règle le débit ; l'airain en fusion sort au tuyau, le laitier à l'entonnoir ; les lunettes d'ingénieur montrent la chaleur, le souffle et la cuve.
- **Le style impérial** : bloc d'airain, airain taillé, riveté, ciselé, pilier, escaliers, dalles, grille, barreaux, porte et trappe ferronnées, chaîne, et une lanterne à flamme rouge. Avec le temps, l'airain vire du doré au rouge impérial en quatre teintes ; la cire fige la teinte, la hache la ramène.
- **Engrenage d'airain** (assemblage séquencé) : il entre dans le Cœur d'Airain (avec des blocs d'airain), la Machine différentielle, le trône impérial et la charte impériale.
- **Passerelles d'airain** (style industriel) : passerelle en caillebotis, à hauteur basse ou à mi-hauteur, avec des rambardes qui se posent seules sur les côtés libres (la clé de Create en retire ou en remet une) ; escalier qui monte d'un bloc ; rampe qui monte d'une demi-hauteur ; portillon à poser sur une rambarde ; poteau de soutien évasé ; échelle d'airain à crinoline. La clé de Create passe le sol d'une passerelle, d'un escalier ou d'une rampe du caillebotis à l'airain plein, et l'entourage de l'échelle de rien à la crinoline puis au tunnel plein. Tout se patine comme l'airain.
- **Escalier à palier** : une marche, un palier à mi-hauteur, puis une marche à 90° qui ressort un bloc plus haut (virage à gauche ou à droite selon la moitié du bloc visée). Les côtés extérieurs du palier se raccordent aux passerelles à mi-hauteur et au haut des rampes, sinon ils portent une rambarde (portillon possible).
- **Suspente d'airain** : pend une passerelle au plafond ; ses deux tirants longent les rambardes et son étrier se cale sous le plancher, bas ou à mi-hauteur.
- **Rambarde d'airain seule** : se pose au bord de n'importe quel bloc ; on ajoute un côté avec une autre rambarde, la clé de Create en retire un.
- **Conduite d'air** : un ventilateur de Create souffle dans un réseau de conduits d'air (raccords automatiques, jusqu'à 64 conduits) ; la bouche d'air au bout rend exactement le même courant (même force, même portée, mêmes traitements). Aspiration comprise. Les lunettes d'ingénieur affichent le courant transmis.
- **L'atelier impérial** :
  - tuyau d'airain décoratif qui se raccorde tout seul, vanne à volant (clic droit), manomètre dont l'aiguille suit la vitesse d'une machine de Create, le courant d'une bouche d'air ou le remplissage d'un réservoir ;
  - plancher technique sur plots : la clé relève la dalle, on y loge un tuyau ou un conduit d'air (le conduit reste dans le réseau d'air) ;
  - suspension d'atelier, applique à flamme rouge, gyrophare qui tourne sur un signal de redstone ;
  - réverbère impérial à empiler, à une ou deux lanternes ;
  - toboggan d'airain (on y glisse) et son bac de réception ;
  - garde-corps vitré : la clé fait passer une rambarde de passerelle ou de palier de pleine à vitrée, puis à rien ;
  - plaques émaillées à huit pictogrammes, contre un mur ou une rambarde ;
  - borne de carrefour à flèches orientables (huit directions), sur lesquelles on écrit avec une étiquette renommée ;
  - établi d'atelier dont la grille garde ses objets.
- **Passerelles mobiles** : deux pièces-mécanismes à glisser dans une ligne de passerelles, qui entraînent les 1 à 4 passerelles suivantes : pont-levis (elles se relèvent) et passerelle rétractable (elles rentrent en télescope). Commandes par arbre de Create (sens et vitesse) ou par redstone ; des rambardes ferment les deux bouts quand le passage est ouvert.
- **Monte-charge** : treuil (rotation de Create), mât à crémaillère jusqu'à 32 blocs, cabine. Les étages sont détectés tout seuls (chaque passerelle en face du mât) ; dans la cabine, clic droit pour monter, accroupi pour descendre, clic maintenu sur le panneau pour choisir l'étage dans le tableau de Create ; boîtier d'appel sur les paliers. Les paliers gardent leur rambarde tant que la cabine n'y est pas.
- **La mécanique impériale**, deux pièces qui s'emboîtent dans Create, au crafteur mécanique (5 × 5) :
  - **allégeur impérial** : dans une ligne d'arbres, son volant d'inertie retire 25 % de la charge de tout le réseau ;
  - **surcompresseur impérial** : contre une roue à eau, un moulin ou un moteur à vapeur, +50 % de capacité de stress pour ce générateur ; pistons, manomètre et vapeur suivent le générateur.
- Nouvelles textures de détail pour ces pièces : panneau à pointe de diamant, frise, bandeau à perles, cannelures, tuyau, tige.
- Nouvelle annexe de quêtes « La fonderie impériale » (17 quêtes) et huit pages dans le livre de l'ingénieur.

**Changements**
- « Forger le Cœur » demande aussi l'engrenage d'airain.
- Le sol des passerelles, escaliers, rampes, paliers et pièces-mécanismes passe en croisillons épais, comme la grille d'airain ; chaque marche d'escalier montre une rangée de croix entières. Plus aucune texture de passerelle n'est tassée.
- Nez des marches d'escalier en bandeau à rivets ; allégeur aux flasques creusés (on voit l'arbre tourner dans son palier) ; carter des pièces-mécanismes affiché seulement s'il a la place dessous ; étau de l'établi recentré.

**Corrections**
- Textures manquantes (touches rouges) sur les pièces ternies et vieillies : volant de l'allégeur, vanne, lampes, monte-charge, mécanismes.

---

## 12 novembre 2026 — versions 1.47.0 à 1.47.7

**Ajouts**
- **Machines d'Écho**, le pont entre Create et Ars Nouveau, en milieu de partie :
  - **Turbine d'Écho** : un moteur de Create qui boit de l'Écho liquide amené par les tuyaux (20 mB par seconde) pour 64 tr/min et 1 024 de force. L'arbre sort d'un logement creusé dans la face avant, et une cheminée à pales, creusée dans le dessus, évacue la vapeur d'Écho ;
  - **Sourcelink mécanique** : l'inverse, la rotation devient de l'Écho liquide, à pomper hors de sa cuve, avec un peu de perte. Son engrenage et sa gemme tournent avec l'axe ;
  - **Diffuseur d'Écho** : posé devant un ventilateur, il donne un nouveau traitement, l'imprégnation. Éclat d'améthyste ou lapis en gemme de source, bloc d'améthyste en bloc de gemme de source, sculk en éclat d'écho ;
  - **Condenseur d'Écho** : la source des jarres devient de l'**Écho liquide**, qui passe dans les tuyaux de Create (socle givré), et l'inverse à 90 % (socle chauffé au rouge, couvercle relevé, vapeur). Le liquide se voit dans la cuve à sa vraie hauteur. Au bec verseur, l'Écho liquide imprègne les objets un par un.
- **Glyphe de l'engrenage** (Ars Nouveau, niveau 2) : il accélère une machine de Create quelques secondes, grippe les automates (Rôdeur, Centurion nain, golems de l'End…) et soigne les gardiens d'airain.
- Les cuves des machines d'Écho ont des vitres en retrait d'un pixel, avec un bord bleu pâle et quelques reflets.
- **Ender Transmission** (mod à ajouter dans `mods/`, clients et serveur) : transmetteurs d'objets, de fluides et de rotation entre dimensions, et chargeur de chunks. Leurs recettes demandent des carapaces de shulker, donc l'accès au-delà de la passerelle ouverte par la mort du dragon. Nouvelle quête « Par-delà les dimensions » dans l'annexe Ingénierie et logistique.
- Livre de l'ingénieur : un cinquième sommaire, **Fusion**, avec une page par machine.
- Annexe Ingénierie : une ligne de cinq quêtes, « Les machines réfractaires », en haut du chapitre.

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
