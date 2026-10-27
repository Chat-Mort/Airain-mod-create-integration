# Airain : intégration Create

Petit mod NeoForge 1.21.1 pour le modpack **L'Empire d'Airain**. Il dépend de Create 6.

## Contenu

- **Banc d'entretien** (`airain:banc_entretien`) : une vraie machine Create (consomme du stress, 8 su par tr/min).
  Elle répare l'équipement comme une enclume, mais avec de l'huile de machine (`kubejs:huile`) au lieu de l'expérience.
  - Matériau de réparation : chaque unité rend 25 % de la durabilité. Deux objets identiques : durabilités additionnées + 12 %.
  - 1 000 mB d'huile par unité (deux burettes `kubejs:huile_machine`). Réservoir de 8 000 mB.
  - Arbre de transmission sur l'axe horizontal ; 16 tr/min minimum. Une tranche de 25 % prend 30 s à 16 tr/min et 7,5 s à 256 tr/min (racine carrée de la vitesse), +20 % par niveau d'enchantement de l'objet.
  - Entonnoirs et tapis : l'objet abîmé puis le matériau entrent par toutes les faces, l'objet réparé ressort.

L'huile et la burette sont fournies par les scripts KubeJS du modpack.

## Compilation

La compilation se fait automatiquement sur GitHub à chaque envoi sur `main`.
Le `.jar` (ou le journal d'erreurs) est publié sur la branche `build`.
En local : `./gradlew build` (Java 21), le `.jar` est dans `build/libs/`.
