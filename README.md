# Airain : intégration Create

Petit mod NeoForge 1.21.1 pour le modpack **L'Empire d'Airain**. Il dépend de Create 6.

## Contenu

- **Banc d'entretien** (`airain:banc_entretien`) : une vraie machine Create (consomme du stress, 8 su par tr/min), avec une meule en pierre qui tourne sur le dessus et une jauge d'huile en façade.
  Elle répare l'équipement comme une enclume, mais avec de l'huile de machine (`kubejs:huile`) au lieu de l'expérience.
  - Matériau de réparation : chaque unité rend 25 % de la durabilité. Deux objets identiques : durabilités additionnées + 12 %.
  - 1 000 mB d'huile par unité (deux burettes `kubejs:huile_machine`). Réservoir de 8 000 mB.
  - Construit comme la meule de Create : rouage central (s'engrène avec les rouages voisins) ou arbre par le dessous ; 16 tr/min minimum. Pénalité de lenteur ×1 à 256 tr/min, ×1,5 à 128, ×2 à 64, ×2,5 à 32, ×3 à 16 :
    réparation complète en 2,5 s à 256 tr/min, 7,5 s à 128, 20 s à 64, 50 s à 32, 2 min à 16.
  - Chaque niveau d'enchantement de l'objet ajoute 25 % de temps (12 niveaux : ×4).
  - Entonnoirs et tapis : l'objet abîmé puis le matériau entrent par toutes les faces, l'objet réparé ressort.

- **Table d'enchantement de l'Empire** (`airain:table_enchantement`) : on choisit l'enchantement et son niveau, parmi ceux des livres
  enchantés rangés dans les bibliothèques sculptées à moins de 3 blocs, sans dépasser le niveau du livre. Coût : 3 niveaux d'XP par niveau
  + 2 × le coût d'enclume de l'enchantement (30 au plus), et un lapis par niveau. Les livres restent dans les bibliothèques.
  La table d'enchantement vanilla ne s'ouvre plus.
- **Désenchanteur** (`airain:desenchanteur`) : machine Create (8 su par tr/min, huile). Il détruit un objet enchanté et en tire,
  au hasard, un enchantement dans un livre vierge. 500 mB d'huile et 200 points de travail par niveau de l'enchantement tiré.

L'huile et la burette sont fournies par les scripts KubeJS du modpack.

## Compilation

La compilation se fait automatiquement sur GitHub à chaque envoi sur `main`.
Le `.jar` (ou le journal d'erreurs) est publié sur la branche `build`.
En local : `./gradlew build` (Java 21), le `.jar` est dans `build/libs/`.
