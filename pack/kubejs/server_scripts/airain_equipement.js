// L'Empire d'Airain / The Airain Empire — équipement par paliers
//
//   Fer (ch. II)       : armures et armes Simply Swords de fer/or demandent des PLAQUES (presse) au lieu des lingots.
//                        L'épée de fer reste à la main (lingots) : avec la pioche, c'est l'équipement de départ.
//   Diamant (ch. III)  : armures de diamant = diamants + plaques de cuivre + Sceau de la Forge (non consommé).
//                        Épée et armes Simply Swords de diamant : le manche devient une plaque de cuivre.
//   Netherite (ch. IV) : la table de forgeron demande une Plaque de netherite renforcée au lieu du lingot.
//                        Cette plaque se fabrique par assemblage en séquence (déployeur + presse),
//                        voir kubejs/data/kubejs/recipe/airain/plaque_netherite.json
//
// Les OUTILS (pioches, haches, pelles, houes) ne sont jamais touchés : on ne bloque pas le minage.

ServerEvents.recipes(event => {
  const SCEAU = 'kubejs:sceau_forge'

  // ---------- Palier du fer ----------
  const piecesFer = ['minecraft:iron_helmet', 'minecraft:iron_chestplate', 'minecraft:iron_leggings',
    'minecraft:iron_boots']
  piecesFer.forEach(id => {
    event.replaceInput({ output: id }, 'minecraft:iron_ingot', '#c:plates/iron')
  })
  event.replaceInput({ output: /^simplyswords:iron_.*/ }, 'minecraft:iron_ingot', '#c:plates/iron')
  event.replaceInput({ output: /^simplyswords:gold_.*/ }, 'minecraft:gold_ingot', '#c:plates/gold')

  // ---------- Palier du diamant ----------
  const D = 'minecraft:diamond'
  const C = '#c:plates/copper'
  const armuresDiamant = {
    'minecraft:diamond_helmet': ['DDD', 'DCD', ' K '],
    'minecraft:diamond_chestplate': ['DCD', 'DDD', 'DKD'],
    'minecraft:diamond_leggings': ['DDD', 'DCD', 'DKD'],
    'minecraft:diamond_boots': ['DCD', 'DKD']
  }
  Object.keys(armuresDiamant).forEach(id => {
    event.remove({ output: id, type: 'minecraft:crafting_shaped' })
    event.shaped(id, armuresDiamant[id], { D: D, C: C, K: SCEAU })
      .keepIngredient(SCEAU)
      .id('kubejs:airain/' + id.split(':')[1])
  })
  event.replaceInput({ output: 'minecraft:diamond_sword' }, 'minecraft:stick', C)
  event.replaceInput({ output: /^simplyswords:diamond_.*/ }, '#c:wood_sticks', C)
  event.replaceInput({ output: /^simplyswords:diamond_.*/ }, 'minecraft:stick', C)

  // ---------- Palier de la netherite ----------
  const NP = 'kubejs:plaque_netherite'
  const piecesNetherite = ['minecraft:netherite_helmet', 'minecraft:netherite_chestplate',
    'minecraft:netherite_leggings', 'minecraft:netherite_boots', 'minecraft:netherite_sword']
  piecesNetherite.forEach(id => {
    event.replaceInput({ output: id }, 'minecraft:netherite_ingot', NP)
    event.replaceInput({ output: id }, '#c:ingots/netherite', NP)
  })
  event.replaceInput({ output: /^simplyswords:netherite_.*/ }, 'minecraft:netherite_ingot', NP)
  event.replaceInput({ output: /^simplyswords:netherite_.*/ }, '#c:ingots/netherite', NP)
})
