# L'Empire d'Airain / The Airain Empire

Modpack Create pour Minecraft **1.21.1 / NeoForge**, à jouer à deux, environ 60 heures.

Ce dossier contient :

- le livre de quêtes (environ 290 quêtes, en français et en anglais) ;
- les scripts de progression ;
- les structures du monde ;
- les objets du pack et leurs textures.

Les mods eux-mêmes sont à télécharger à part : voir la liste des mods.

Ce qui change à chaque version : voir `CHANGELOG.md`.

---

## 1. Installer

> **Mods à retirer** par rapport aux versions précédentes :
>
> - **Iron's Spells 'n Spellbooks** (remplacé par la magie de l'Écho d'Ars Nouveau) ;
> - **SimplySwords Create Lines** (incompatible avec Create 6) ;
> - **Mowzie's Cataclysm**.
>
> Leurs bibliothèques peuvent rester.

1. Dans Prism Launcher, crée une instance **Minecraft 1.21.1 + NeoForge** et installe les mods de la liste.

2. Copie `config`, `defaultconfigs`, `kubejs` et `schematics` à la racine de l'instance (le dossier qui contient `mods`),
   et mets `mods/airain-1.45.1.jar` (le mod du pack : banc d'entretien) dans le dossier `mods`. Supprime l'ancienne version du `.jar` s'il y en a une.
   Si une ancienne version du pack y est déjà, **supprime d'abord** `config/ftbquests/quests` et `kubejs`.

3. Serveur : mêmes mods sauf ceux marqués « Client », plus `airain-1.45.1.jar`, et la même copie de `config`, `defaultconfigs`, `kubejs` et `schematics` (les plans de l'Empire, lus par le canon à schémas).

4. Mémoire du serveur (`user_jvm_args.txt`) :
   - `-Xmx8G` sur une machine de 16 Go ;
   - `-Xmx12G` sur 32 Go ;
   - un peu moins si ton ami joue sur la même machine.

5. Pas de prégénération : Chunky est retiré, car il plante à la création du monde avec Distant Horizons. Distant Horizons génère lui-même le paysage lointain, en tâche de fond.

6. Écran d'accueil et interface (chez chaque joueur) :
   - Le logo, l'écran de chargement, les phrases d'accueil, les boutons et les fenêtres en laiton sont déjà dans `kubejs` : rien à activer.
   - Pour l'image de fond de l'accueil, installe **FancyMenu** (client). L'image est fournie dans `config/fancymenu/assets/fond_accueil.png`.
   - Dans Options › Accessibility, active **Monochrome Logo** : sans ça, l'écran de chargement garde son fond rouge et le logo paraît délavé.

**Tectonic et tous les mods qui touchent au monde doivent être installés avant de créer le monde.**

---

## 2. Le Laboratoire 7 (point de départ)

Au premier démarrage d'un **monde neuf**, le laboratoire est construit tout seul sous le point d'apparition, avec un puits à échelle qui remonte à la surface. Chaque joueur se réveille dans une capsule, qui devient son point de réapparition.

**Le bureau**
Le journal de l'ingénieur est sur le pupitre : le refermer valide la première quête.
Le coffre Lootr donne à chacun son livre de quêtes, 5 ou 6 lingots de fer et quelques toiles d'araignée.

**Le comptoir**
8 distributeurs déjà réglés, qui vendent contre des pièces :
- de quoi démarrer : bûches de chêne, torches, fer brut, pain, lapis-lazuli ;
- des secours : netherrack, perles d'Ender, cœur de la mer.

Prix et objets se modifient en créatif (clic droit sur un distributeur).

**Le terminal bancaire**
Les distributeurs exigent les pièces exactes et ne rendent pas la monnaie.
Avec une carte bancaire (quête optionnelle « La banque de l'Empire », chapitre II : plaque de fer, plaque d'or, colorant blanc), on dépose ses pièces au terminal et on paie la valeur totale, quelles que soient les pièces.

**Ars Nouveau**
Le carnet n'est plus donné à la connexion : il s'obtient avec la quête optionnelle « L'Écho » (chapitre II).
Le réglage est dans `defaultconfigs/ars_nouveau-server.toml`, à copier aussi à la racine du serveur. Il ne s'applique qu'aux mondes créés ensuite ; pour un monde existant, mets `spawnBook = false` dans `world/serverconfig/ars_nouveau-server.toml`.

---

## 3. Comment fonctionne la progression

| Chapitre | Gardien | Débloque |
|---|---|---|
| I · Le Réveil | Grand Chantier « le premier atelier » | la presse (2 blocs de fer offerts) |
| II · Andésite | 10 Breezes + clé funeste | Schéma du Cuivre : pompe, bec verseur, égouttoir |
| III · Cuivre | les 3 gardiens anciens | Schéma du Laiton : brûleur à blaze ; **le Nether** |
| IV · Laiton | Monstruosité de netherite | Schéma du Ciel : assembleur physique, roulement d'hélice ; **l'End** |
| V · Ciel | Ender Guardian | le dernier Fragment |
| VI · Le Cœur | (forger et réactiver le Cœur) | le retournement, l'usine ancienne |
| VII · Reconquête | The Harbinger | la fin |

**Équipement**
- Armure de fer : plaques de fer (presse).
- Armure de diamant : diamants + plaques de cuivre + Sceau de la Forge.
- Netherite : plaque de netherite renforcée (déployeur + presse).
- Les outils ne sont jamais verrouillés.

**Grands Chantiers**
Des livraisons consommées qui débloquent la Forge (armure de diamant), les Waystones, les interfaces portables des trains, les entrées d'Hypertubes (« le réseau pneumatique », annexe Trains) et les machines d'Enchantment Industry.

**Armes à feu (Create: Gunsmithing)**
Pas de verrou ajouté : leurs recettes suivent déjà Create. Le pistolet à silex arrive au chapitre II (plaques de fer), les autres armes au chapitre IV (laiton, assembleur mécanique, acier au brûleur surchauffé). Quêtes dans l'annexe Arsenal.

**Déblocages par joueur**
Les portails et les chantiers se débloquent pour chaque joueur : chacun doit réclamer sa propre récompense. Un administrateur peut aussi le faire à la main :

```
/tag <joueur> add airain_nether
```

(ou `airain_end`, `airain_waystones`, `airain_gare`, `airain_atelier`)

**La voie de l'Écho (facultative)**
L'annexe « Les Échos perdus » raconte l'histoire cachée de l'Empire et mène à un boss, le Chœur des Égarés. Sa récompense, l'Écho primordial, débloque les sorts les plus puissants d'Ars Nouveau. On peut finir le jeu sans elle.

---

## 4. Tests à faire en créatif avant la vraie partie

Coche au fur et à mesure. **Repars d'un monde neuf pour la vraie partie.**

### Démarrage

- [ ] **Diagnostic** : en entrant dans le monde, aucun message rouge « [Airain] … identifiant(s) manquant(s) ».
  S'il y en a un, il liste les objets, créatures ou structures que le pack utilise mais qui n'existent pas dans ton installation (mod absent ou retiré). Envoie-moi la liste.
  Si tout va bien, `logs/kubejs/server.log` contient « [Airain] Diagnostic : les … identifiants du pack existent tous ».

- [ ] **Bannières** : aux portails des avant-postes et des cités, sur les places, dans les marchés et sous les cadrans de l'horloge, la Roue couronnée (laiton sur noir, bordure cuivre).
  Dans les camps réfractaires et au sanctuaire, l'Éclat d'Écho (violet sur noir). Les quatre motifs se tissent aussi au métier à tisser, sans objet de motif.

- [ ] **Recettes de Create dans EMI** : la recette du Cœur (assembleur mécanique) et celle des plaques de netherite (assemblage en séquence) doivent apparaître.
  Si elles manquent, installe aussi **JEI** : EMI s'en sert pour afficher les recettes spéciales de Create.

- [ ] **Laboratoire** : sur un monde neuf, tu te réveilles dans une capsule.
  Le coffre du bureau contient le livre de quêtes.
  Refermer le journal du pupitre valide « Comprendre ce qui s'est passé ».
  L'échelle mène à la surface.

- [ ] **Comptoir** : avec des pièces (`/give @s numismatics:cog 4`), un achat fonctionne.
  Une carte bancaire se fabrique avec plaques de fer et d'or, se lie au clic droit, et paie au distributeur après un dépôt au terminal.
  Si un distributeur est tourné vers le mur, tourne-le avec la clé de Create.

### Le monde

- [ ] **Musique** : le thème principal joue sur l'écran titre. En jeu, à la surface, il revient environ une fois sur trois parmi les musiques de Minecraft (qui laissent toujours de longs silences entre deux morceaux).

- [ ] **Couleurs** : le ciel est plus terne et ambré, l'herbe olive, l'eau vert-de-gris.

- [ ] **Noms** : un zombie s'appelle « Ouvrier déchu » (`/summon minecraft:zombie ~ ~ ~` puis le viser avec Jade), un creeper « Chaudière instable ».
  F3 affiche toujours `minecraft:plains`, mais le nom traduit des biomes apparaît dans les mods qui l'affichent.

- [ ] **Tectonic** : le relief est plus haut et plus varié (montagnes, vallées, falaises).

- [ ] **Plus aucun humain** :
  - `/locate structure minecraft:village_plains`, `minecraft:pillager_outpost` et `minecraft:mansion` ne trouvent rien ;
  - pas de villageois zombie, de marchand ambulant ni de patrouille ;
  - `/summon minecraft:villager` ne fait rien apparaître (villageois, sorcières et illageois sont retirés dès leur arrivée, même depuis une structure d'un autre mod).

### Les structures de l'Empire

- [ ] **Ruines isolées** (très fréquentes) :
  `/place structure kubejs:ruine_atelier`, `kubejs:ruine_reservoir` (château d'eau effondré), `kubejs:ruine_conduite` (conduite rompue).
  L'atelier et le réservoir ont parfois un coffre, avec une page arrachée une fois sur deux environ.

- [ ] **Avant-postes** :
  `/locate structure kubejs:avant_poste_tempere` (plaines, prairies), `kubejs:avant_poste_desert`, `kubejs:avant_poste_froid` (plaines enneigées, taïgas), `kubejs:avant_poste_savane`.
  - Une enceinte carrée de 71 blocs qui suit le relief : muraille de tôle sur socle de pierre, tronçons intacts, abîmés ou effondrés.
  - Aux angles : deux châteaux d'eau, une cheminée d'usine qui fume et une tour en ruine. 3 ou 4 portails à grandes roues dentées.
  - À l'intérieur : la place à la fontaine à vapeur, un marché garanti (0 à 3 machines), des entrepôts, ateliers, dortoirs, kiosques, et une salle scellée.
  - Le long des murs, porte vers la cour : bâtiments, tours de guet, dépôts de caisses avec leur grue, tas de ferraille, appentis de réparation.
  - Sur une pente, rien ne doit manquer : la cour se remplit aussi là où le sol est plus haut ou plus bas que la place.
  - Mêmes plans dans les 4 climats ; seuls le socle, les sols et le bois changent.

- [ ] **Cité mécanique** (rare, plaines et prairies) : `/locate structure kubejs:cite_mecanique`.
  - Enceinte de 111 blocs, remplie au maximum, avec stands de tir, laboratoires et ateliers adossés aux murs.
  - Place de la tour d'horloge (cloche en haut, quatre cadrans à roues dentées).
  - Plusieurs marchés, dont des grands marchés à 6 machines.
  - Stands de tir, laboratoires d'essais (journal d'essais dans la salle souterraine).
  - Les 3 salles scellées : cuivre, laiton, ciel.

- [ ] **Salles scellées** : clic droit sur la porte de fer avec le bon Schéma (la couleur au-dessus de la porte donne le palier : cuivre, laiton, bleu ciel).
  La porte disparaît ; avec un autre objet, un message indique le Schéma demandé.
  Tant qu'elle est fermée, les murs ne se cassent pas en survie.
  La salle du ciel vend un totem d'immortalité (1 couronne).

- [ ] **Distributeurs** : impossible de les casser en survie (laboratoire et avant-postes).

- [ ] **Station de capsules** (forêts, taïgas, plaines) : `/locate structure kubejs:station_capsules`.
  Deux rangées de capsules vides, des câbles qui plongent dans un puits.
  En bas : le rapport d'Elias Vael sur le pupitre, et dans le coffre du collecteur, la lettre jamais ouverte d'Ada.

### Les Réfractaires et l'Écho

- [ ] **Camp réfractaire** : `/locate structure kubejs:avant_poste_refractaire`.
  - Palissade rapiécée, tentes, feu de camp, automate abattu en trophée, coffres avec des écrits réfractaires.
  - Un cercle d'Écho (feu d'âmes, améthyste, bougies) et un étal d'Écho (améthyste, pousses d'archebois, baies d'Écho).
  - Un camp sur trois a aussi un étal de fiole funeste (2 pignons) : en créatif, `/place structure` plusieurs fois pour le voir apparaître.

- [ ] **Relais brisé** : `/locate structure kubejs:relais_brise`.
  Pylône tombé, sol brûlé couvert d'améthyste, feux d'âmes, rapport d'incident sur le pupitre et un coffre.

- [ ] **Sanctuaire réfractaire** (taïgas, plaines enneigées, prairies) : `/locate structure kubejs:sanctuaire_refractaire`.
  Le journal d'Ada Vesper est sur le pupitre de la grande tente violette.

- [ ] **Grand Relais** : `/locate structure kubejs:grand_relais`.
  - Au sud du pylône effondré, le résonateur (pierre de magnétite).
  - En créatif : `/give @s kubejs:diapason_echo`, puis clic droit sur le résonateur : le Chœur des Égarés apparaît. Vérifie qu'il a bien 600 points de vie et son nom.
  - À sa mort, chaque joueur proche reçoit 8 Échos primordiaux.
  - Si rien n'apparaît, tape `/summon ars_nouveau:` pour vérifier l'identifiant de la Chimère.

- [ ] **Noms de l'Écho** : dans EMI, les objets d'Ars Nouveau s'appellent « Gemme d'Écho », « Pot d'Écho », « Pierre d'Écho »… (en anglais « Echo Gem », « Echo Jar »). Aucune machine de l'Empire ne vend de magie.

- [ ] **Fragments et diapason** : les âmes sans repos (phantoms) lâchent parfois un fragment de résonance. Le diapason se fabrique avec 5 fragments, une gemme d'Écho et un lingot d'or.

- [ ] **Sorts verrouillés** : dans EMI, les glyphes explosion, foudre, maléfice, flétrissement, persistance, mur et rafale demandent un Écho primordial.

- [ ] **Bonus contre les machines** : un sort sur un automate de patrouille (squelette) doit faire nettement plus mal qu'avant.

### La progression

- [ ] **Objets** : `/give @s kubejs:schema_cuivre`, `kubejs:sceau_forge`, `kubejs:coeur_d_airain` ont un nom et une texture.

- [ ] **Chapitre II** : la presse et le ventilateur se fabriquent sans Schéma ; l'armure de fer demande des plaques.

- [ ] **Chapitre III** : pompe, bec verseur, égouttoir demandent le Schéma du Cuivre ; l'armure de diamant demande plaques de cuivre et Sceau.

- [ ] **Portail du Nether** : refuse de s'allumer sans `airain_nether`, s'allume après `/tag @s add airain_nether`.

- [ ] **Chapitre IV** : le brûleur demande le Schéma du Laiton ; la plaque de netherite apparaît dans EMI (assemblage en séquence).

- [ ] **Portail de l'End** : même test avec `airain_end`.

- [ ] **Chapitre V** : assembleur physique et roulement d'hélice demandent le Schéma du Ciel.

- [ ] **Chantiers** : impossible de poser une Waystone sans `airain_waystones`, ni une entrée d'Hypertube sans `airain_pneumatique`.

- [ ] **Chapitre VI** : la recette du Cœur apparaît dans EMI, catégorie assembleur mécanique.

- [ ] **Chapitre VII et Bestiaire** : ils utilisent les automates nains de Mebahel (araignée, sphère, araignée gardienne, centurion), le colosse de fer de Mowzie's, et le golem, le rôdeur et le veilleur de Cataclysm.
  Le diagnostic au démarrage signale tout identifiant absent. Les automates n'apparaissent que dans leurs ruines : celles-ci doivent rester actives.

- [ ] **Gardiens d'airain** : un golem de laiton assis et moussu dans la tour, les places et la grande enceinte des avant-postes, et sur le champ de bataille.
  Clé de Create avec 16 ferrailles, 4 huiles et 2 rouages brisés : il se lève. Dans la zone d'un étendard, il s'y rattache (4 par base, compte visible dans le registre).
  Accroupi + clé : il vous suit ; clé sur un étendard : il y prend son poste. Une huile le soigne.

- [ ] **Chroniques oubliées** : le livre arrive avec la première quête (ou livre + horloge à l'établi). Il contient « Où en étions-nous ? », le récit (un passage par grande quête), le journal de bord (fondations, boss, premiers pas dans le Nether et l'End, écrits trouvés, assauts, gardiens, choix final) et les archives (les écrits portés sur soi y sont recopiés ; un clic pour les relire).
  Partie déjà commencée : `/airain chronique jusqua <étape>` (opérateur) débloque le récit jusqu'à une étape, par exemple `jusqua atelier` pour la fin du chapitre I. Les étapes se complètent avec la touche Tab.

- [ ] **Reliure de l'ingénieur** (livre + cuir + plaque de laiton + pépite de fer) : 9 livres (Chroniques, registre, codex, atlas, livre de l'ingénieur, les deux manuels d'armes, livre de quêtes, carnet d'Ars Nouveau). Clic droit : onglets pour lire ; accroupi + clic droit : ranger ; touche K : l’ouvre même rangée dans un sac porté.
  Rangée dans un sac (ou un coffre), ses livres apparaissent en onglets à gauche de l'écran ; Échap après lecture ramène au sac. À vérifier livre par livre : le livre de quêtes et le carnet d'Ars Nouveau. Liste des livres autorisés : tag `airain:reliure`.

- [ ] **Fin du lore** : la station d'observation n°2 flotte vers la hauteur 170 au-dessus des plaines (`/locate structure kubejs:station_observation`), avec un gardien en panne et les relevés d'Octave. Les affiches de propagande pendent aux murs des avant-postes et des cités (vérifier qu'elles tiennent au mur). Les fragments de mémoire ont un texte complet dans leur infobulle.

- [ ] **Tableau de service** (planches, papier, plaques de laiton) : à accrocher au mur d'une base ; 6 notes, punaises rouge / jaune / verte ; clic : fait, clic droit : retirer. À la connexion, message pour les notes non lues ; elles apparaissent aussi dans « Où en étions-nous ? ». Casser le tableau efface ses notes.
- [ ] **Atlas impérial** (livre + carte + boussole, rangeable dans la Reliure) : chunks parcourus en clair, bases, lieux visités, morts ; glisser, molette, filtres. Il ne note que ce qui est parcouru après la mise à jour.
- [ ] **Affiches** : affiche vierge (3 papiers + colorant noir, ×2) au déployeur avec colorant rouge, rouage, éclat d'améthyste, pépite d'or ou pépite de laiton ; réfractaires : fragment de résonance, éclat d'écho, diapason (gardé).

- [ ] **Patrouilles (chapitre VII)** : après « Réactiver le Cœur » (tag `airain_coeur_reveille`) et jusqu'à l'Empereur (tag `airain_fin`), une patrouille de 3-4 automates vient vers un joueur en surface toutes les 15 à 25 minutes (première 10 min après le réveil) ; 35 % sont larguées du ciel. Pour tester : `/tag @s add airain_coeur_reveille`, puis rester 10 minutes en surface.
- [ ] **Dirigeables** : croiseurs de la flotte du ciel vers la hauteur 150 (`/locate structure kubejs:dirigeable`), équipage d'automates sur le pont, cabine (livre de bord, coffre) et soute (deux coffres).

- [ ] **Après la fin** : fin Empire → 3 chartes impériales (puis laiton ×6 + mécanismes ×2 + papier) ; couronne sur la tête, clic droit dans un avant-poste : bannières aux couleurs de la base, plus de monstres, prix −25 %, un gardien. Fin Écho → accroupi + diapason dans un relais brisé avec 8 fragments de résonance : plus de monstres à 64 blocs. Quêtes de paliers 1 / 3 / 5 / 10 au chapitre VII.

- [ ] **Comptoirs des avant-postes** : les halles ont maintenant deux comptoirs, « Pièces détachées » (pièces de Create par lots) et « Cartographe » (cartes de l'Empire : clic droit, la carte se dessine vers le lieu le plus proche). Les salles scellées vendent les pièces et les cartes du palier suivant. Les avant-postes déjà générés gardent leurs anciennes machines : il faut en découvrir de nouveaux.

- [ ] **Bureau d'études et plans** : quête « Le bureau d'études » (chapitre II) ; les halles peuvent avoir un comptoir « Bureau d'études » (plans, poudre, schémas vierges). Plans à tester : moulin à vent, centrale à roues, meunerie. Clic droit sur le plan → schéma de Create → canon à schémas. Si un plan ne fonctionne pas, noter ce qui coince.

- [ ] **Choix final** : après l'Empereur, `/airain fin empire` ou `/airain fin echo` (opérateur) fixe la fin du monde ; `/airain fin aucun` l'efface pour tester l'autre.
  Empire : couronne d'airain, à porter seule (2 d'armure, incassable) ou à monter à l'enclume sur un casque de netherite pour obtenir le casque couronné (protection de netherite, enchantements gardés ; accroupi + clic droit pour la détacher) (les zombies, squelettes et automates ne vous ciblent plus sauf si vous frappez ; gardiens à 16 blocs renforcés ; la loupe sert de lunettes d’ingénieur et zoome en maintenant H). Écho : vision de nuit, +50 % d'expérience, le sculk ne réagit plus, plus de phantoms ; accroupi immobile 1,5 s, les créatures à 24 blocs brillent (recharge 15 s).

---

## 5. Retoucher une structure en jeu

1. En créatif, `/give @s minecraft:structure_block`, pose-le, passe-le en mode **Load**.

2. Tape le nom de la pièce (voir le tableau ci-dessous) et clique **Load** deux fois : la pièce apparaît, sans usure.

3. Modifie-la librement, puis repasse **le même bloc** en mode **Save**, sans toucher à la position relative ni à la taille (le Load les a remplies), et clique **Save**.
   - Si tu poses un nouveau bloc pour sauvegarder, la zone sera décalée et le fichier contiendra autre chose que la pièce.
   - Ne casse pas les blocs puzzle (blocs gris à flèche) : ce sont eux qui accrochent les pièces entre elles. Sans eux, la pièce n'apparaît plus ou n'a plus rien autour.
   - Une pièce déjà sauvegardée dans le monde (`saves/<monde>/generated/`) est rechargée à la place de celle du pack : en cas de doute, supprime-la ou utilise un monde neuf.
   - Charge une seule pièce à la fois, loin des autres : le cadre d'une enceinte est très grand et englobe ce qui est autour.
   - Envoie-moi les fichiers retouchés : je les branche dans le générateur, et les variantes de climat et de cité suivent toutes seules.

4. Le fichier modifié se trouve dans `saves/<ton monde>/generated/kubejs/structures/...` : copie-le au même endroit dans `kubejs/data/kubejs/structure/` (et sur le serveur).

| Structure | Nom à charger |
|---|---|
| Laboratoire 7 | `kubejs:laboratoire` |
| Ruines | `kubejs:ruines/atelier_effondre`, `kubejs:ruines/reservoir_tombe`, `kubejs:ruines/conduite_rompue`, `kubejs:ruines/relais_brise`, `kubejs:ruines/grand_relais` |
| Avant-poste (une pièce) | `kubejs:avant_poste/tempere/marche`, `.../entrepot`, `.../tour`, `.../depot_caisses`, `.../ferraille`, `.../abri`, `.../salle_cuivre`… (climats : `tempere`, `desert`, `froid`, `savane`) |
| Enceinte entière | `kubejs:avant_poste/tempere/enceinte_a` (71 × 20 × 71) |
| Cité mécanique | `kubejs:avant_poste/tempere/centre_horloge`, `.../enceinte_cite_a`, `.../laboratoire_c`, `.../stand_tir_c`, `.../grand_marche_c` |
| Réfractaires | `kubejs:refractaires/camp_a`, `kubejs:refractaires/camp_b`, `kubejs:refractaires/sanctuaire` |
| Station de capsules | `kubejs:station/station_capsules` |

**À garder intacts**
- **Les blocs puzzle (jigsaw)** : ce sont les points d'accroche entre les pièces. Ne les déplace pas et ne les supprime pas.
- **Dans les salles scellées** : la porte de fer et le bloc coloré au-dessus. Le script s'en sert.
- **Dans le Grand Relais** : la pierre de magnétite et l'ardoise renforcée en dessous. C'est le résonateur.

Les blocs laissés vides (structure void) ne touchent pas au terrain : c'est ce qui permet à l'herbe et aux fleurs de rester autour des murs.

---

## 6. Le chapitre de secours

Un chapitre « Secours administrateur » est caché aux joueurs. Il apparaît en mode édition (`/ftbquests editing_mode`).

Une quête par chapitre redonne le Schéma, les Fragments et les déblocages correspondants, et une quête redonne le diapason et les Échos primordiaux.

À utiliser seulement si un bug bloque la partie.

---

## 7. Langues

Le pack suit la langue de Minecraft : *The Airain Empire* en anglais, *L'Empire d'Airain* en français.

- Textes des quêtes : `config/ftbquests/quests/lang/`
- Objets et messages : `kubejs/assets/kubejs/lang/`
- Noms des biomes et des monstres : `kubejs/assets/minecraft/lang/`
- Noms de l'Écho (Ars Nouveau) : `kubejs/assets/ars_nouveau/lang/`

---

## 8. Contenu du dossier

```
config/ftbquests/quests/            le livre de quêtes (7 chapitres, 8 annexes, 1 chapitre de secours caché)

kubejs/startup_scripts/             les objets du pack (Schémas, Fragments, Sceau, plaques, Cœur, objets de l'Écho)

kubejs/server_scripts/
    airain_paliers.js               Schémas : pompe, bec verseur, égouttoir, brûleur, assembleur physique, hélices
    airain_equipement.js            armures et armes par paliers (plaques de fer, cuivre, netherite)
    airain_verrous.js               portails du Nether et de l'End, blocs des Grands Chantiers
    airain_laboratoire.js           construction du Laboratoire 7, réveil dans les capsules, journal
    airain_sceaux.js                salles scellées, distributeurs incassables, plus aucun humain
    airain_echo.js                  le Chœur des Égarés, l'Écho primordial, bonus des sorts contre les machines

kubejs/data/kubejs/structure/       toutes les structures (.nbt)
kubejs/data/kubejs/worldgen/        leur génération (fréquence, biomes, assemblage, usure)
kubejs/data/kubejs/recipe/airain/   recettes (Cœur d'Airain, plaque de netherite, diapason)
kubejs/data/kubejs/loot_table/      le contenu des coffres
kubejs/data/ars_nouveau/recipe/     les sorts verrouillés par l'Écho primordial
kubejs/data/minecraft/              couleurs des biomes, structures vanilla désactivées, butin des âmes sans repos

kubejs/assets/                      textures, traductions et musiques (kubejs/assets/kubejs/sounds/music/)

defaultconfigs/                     réglage d'Ars Nouveau (pas de carnet au spawn)
```
