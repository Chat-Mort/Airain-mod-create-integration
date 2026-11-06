# Sauvegarde du pack « L'Empire d'Airain »

Branche à part du dépôt du mod : rien ici n'est compilé par la CI (elle ne tourne que sur `main`).
Dernière sauvegarde : 6 novembre 2026, mod 1.44.1.

## Contenu

| Dossier | Ce que c'est |
|---|---|
| `pack/` | Le pack complet tel qu'il est livré : `kubejs`, `config` (quêtes FTB), `defaultconfigs`, `mods` (jar du mod), `schematics`, `README.md`, `CHANGELOG.md` (notes de version, à compléter à chaque livraison ; README et CHANGELOG restent sur GitHub, hors des zips livrés). |
| `outils/` | Les scripts qui fabriquent le pack (générateurs de quêtes, structures, textures, modèles, aperçus) et leurs données. |

Le mod lui-même (code Java, ressources) est sur la branche `main`.

## Restaurer dans une nouvelle session

1. Cloner le dépôt, puis la branche : `git clone -b sauvegarde https://github.com/Chat-Mort/Airain-mod-create-integration sauvegarde`
2. Copier `pack/` vers `/home/claude/empire-airain-pack` et `outils/` vers le dossier de travail de la session.
3. Les scripts contiennent le chemin de l'ancien dossier de travail
   (`/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad`) : le remplacer par le nouveau
   dans tous les `*.py` (`grep -rl` puis `sed -i`).
4. Le mod : cloner `main` dans `/home/claude/airain-mod-create-integration`.

## Les outils principaux

| Script | Rôle |
|---|---|
| `gen_v2.py <pack>` | Génère tout le livre de quêtes (`config/ftbquests/quests`). Lit aussi `descriptions_revue.py`, `descriptions_revue2.py`, `passe_corrections.py` (corrections de la passe complète) et `mise_en_page.py` (positions, groupes de chapitres, titres de section). |
| `snbt_check.py <pack>/config/ftbquests/quests` | Vérifie les fichiers de quêtes générés. |
| `diag_gen.py <pack>` | Met à jour la liste d'identifiants du diagnostic au démarrage (`airain_diagnostic.js`). |
| `livre_audit/carte.py` | Dessine la carte de chaque chapitre (croisements, traits sur une quête). |
| `titres/plaques.py` | Plaques des titres de section (police du jeu). |
| `ecrits.py <pack>` | Écrits ajoutés le 5 novembre (Elias, Héléna, Ferrand, Morgana III, Ada) : textes dans `ecrits_textes.py`, quêtes dans `ecrits_quetes.py`. |
| `carnet.py <pack>` | Pages du carnet de l'apprentie (butins + textes). |
| `musique.py <pack>` | Musiques du pack (`kubejs/assets/minecraft/sounds.json`). |
| `musique_audio.sh <pack>` | Prépare les morceaux de `musique_in/` (sources) : volume -19 LUFS et fondu d'entrée de 2,5 s. |
| `echo_contenu.py`, `echo_structures.py`, `avant_poste.py`, `structures_plus.py`, `ruine.py`… | Contenu et structures (NBT) du pack. |
| `borne/`, `trone/`, `balise7/` | Modèles 3D en voxels et leurs aperçus ; `borne/integrer.py` écrit les modèles des bornes dans le mod. |
| `anglais/carte.py`, `anglais/appliquer.py` | Table français → anglais des identifiants et fichiers (passage en anglais du 4 novembre). |
| `retouches_liam/` | Textures retouchées par Liam : ne jamais les écraser. |

## Non sauvegardé (téléchargeable à nouveau)

- `mcmeta-assets`, `mcmeta-data`, `mcmeta-reg` partiellement : ressources et données de Minecraft 1.21.1 (dépôt GitHub misode/mcmeta, branches `assets`, `data`, `registries`). Seuls la police `ascii.png` et `sounds.json` sont gardés.
- Les sources d'autres mods décompressées pour étude (Create, Gunsmith, FTB, etc.).
- `avant_poste_pieces.json` : cache régénéré par `avant_poste.py`.
- Le zip livré (`empire-airain-pack.zip`, le même pour les joueurs et le serveur) : se refait depuis `pack/` avec
  `zip -qr ../empire-airain-pack.zip kubejs config defaultconfigs mods schematics`.

- Les clones de dépôts externes (`ars`, `cj`, `kjsc`, `kjsrc`, `mcmeta-reg`, `sb`, `simproj`, `ss`) : sources d'autres mods et registres de Minecraft, à recloner si besoin.
