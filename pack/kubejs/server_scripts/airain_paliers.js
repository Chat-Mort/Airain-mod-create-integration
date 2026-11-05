// L'Empire d'Airain — verrouillage des paliers
//
// Principe : certaines machines clés demandent un Schéma dans la grille de craft.
// Le Schéma n'est PAS consommé (keepIngredient) : une fois obtenu, le palier est ouvert pour de bon.
//
//   Schéma du Cuivre  (gardien du vent, chapitre 1)  -> pompe mécanique, bec verseur, égouttoir
//   Schéma du Laiton  (gardien des marées, chapitre 2) -> brûleur à blaze vide (donc mixage chauffé, donc laiton)
//   Schéma du Ciel    (la forge des âmes, chapitre 3)  -> assembleur physique et roulement d'hélice (Aeronautics)

ServerEvents.recipes(event => {
  const CUIVRE = 'kubejs:schema_cuivre'
  const LAITON = 'kubejs:schema_laiton'

  // ---------- Palier du Cuivre ----------
  event.remove({ id: 'create:crafting/kinetics/mechanical_pump' })
  event.shapeless('create:mechanical_pump', [
    'create:cogwheel',
    'create:fluid_pipe',
    CUIVRE
  ]).keepIngredient(CUIVRE).id('kubejs:airain/mechanical_pump')

  event.remove({ id: 'create:crafting/kinetics/spout' })
  event.shaped('create:spout', [
    'TK',
    'P '
  ], {
    T: 'create:copper_casing',
    P: 'minecraft:dried_kelp',
    K: CUIVRE
  }).keepIngredient(CUIVRE).id('kubejs:airain/spout')

  event.remove({ id: 'create:crafting/kinetics/item_drain' })
  event.shaped('create:item_drain', [
    'PK',
    'S '
  ], {
    P: 'minecraft:iron_bars',
    S: 'create:copper_casing',
    K: CUIVRE
  }).keepIngredient(CUIVRE).id('kubejs:airain/item_drain')

  // ---------- Palier du Laiton ----------
  // Sans brûleur, pas de mixage chauffé, donc pas de laiton ni de mécanisme de précision.
  event.remove({ id: 'create:crafting/kinetics/empty_blaze_burner' })
  event.shaped('create:empty_blaze_burner', [
    ' I ',
    'IAI',
    'KI '
  ], {
    I: '#c:plates/iron',
    A: '#c:netherracks',
    K: LAITON
  }).keepIngredient(LAITON).id('kubejs:airain/empty_blaze_burner')

  // ---------- Balise de défense : l'ancienne balise se change en tour-phare ----------

  // ---------- Banque : carte bancaire dès le chapitre II ----------
  // La recette d'origine demande un mécanisme de précision (chapitre IV) ; on ajoute celle-ci, plus simple.
  event.shaped('numismatics:white_card', ['IGD'], {
    I: '#c:plates/iron',
    G: '#c:plates/gold',
    D: '#c:dyes/white'
  }).id('kubejs:airain/carte_bancaire')

  // ---------- Le Cœur d'Airain ----------
  // Sa recette (assembleur mécanique 5x5) est un fichier de données classique :
  // kubejs/data/kubejs/recipe/airain/coeur_d_airain.json

  // ---------- Palier du Ciel (Create Aeronautics) ----------
  // L'assembleur physique (mod Simulated, livré avec Aeronautics) transforme une construction
  // en véhicule physique : sans lui, rien ne vole. On le verrouille, ainsi que le roulement d'hélice.
  const CIEL = 'kubejs:schema_ciel'

  event.remove({ id: 'simulated:physics_assembler' })
  event.shaped('simulated:physics_assembler', [
    ' K ',
    ' N ',
    'ARA'
  ], {
    A: 'create:andesite_alloy',
    N: 'minecraft:lever',
    R: 'create:andesite_casing',
    K: CIEL
  }).keepIngredient(CIEL).id('kubejs:airain/physics_assembler')

  event.remove({ id: 'aeronautics:propeller_bearing' })
  event.shaped('aeronautics:propeller_bearing', [
    ' A ',
    ' S ',
    'KB '
  ], {
    A: '#minecraft:wooden_slabs',
    S: '#c:plates/iron',
    B: 'create:brass_casing',
    K: CIEL
  }).keepIngredient(CIEL).id('kubejs:airain/propeller_bearing')
})

// Infobulles (texte d'ambiance, traduit dans kubejs/assets/kubejs/lang/)
// Chaque objet reçoit sa propre liste de lignes, construite dans une fonction :
// Rhino ne recrée pas toujours les variables d'une boucle, ce qui faisait s'additionner les infobulles.
function airainLignes(id, n) {
  var texte = []
  for (var i = 1; i <= n; i++) {
    texte.push(Text.translate('tooltip.kubejs.' + id + '.' + i).gray().italic())
  }
  return texte
}

ItemEvents.modifyTooltips(event => {
  event.add('kubejs:schema_cuivre', airainLignes('schema_cuivre', 2))
  event.add('kubejs:schema_laiton', airainLignes('schema_laiton', 2))
  event.add('kubejs:schema_ciel', airainLignes('schema_ciel', 2))
  event.add('kubejs:fragment_rouages', airainLignes('fragment_rouages', 5))
  event.add('kubejs:fragment_marees', airainLignes('fragment_marees', 5))
  event.add('kubejs:fragment_forge', airainLignes('fragment_forge', 5))
  event.add('kubejs:fragment_vide', airainLignes('fragment_vide', 5))
  event.add('kubejs:coeur_d_airain', airainLignes('coeur_d_airain', 2))
  event.add('kubejs:sceau_forge', airainLignes('sceau_forge', 2))
  event.add('kubejs:plaque_netherite', airainLignes('plaque_netherite', 1))
  event.add('kubejs:fragment_resonance', airainLignes('fragment_resonance', 1))
  event.add('kubejs:diapason_echo', airainLignes('diapason_echo', 2))
  event.add('kubejs:echo_primordial', airainLignes('echo_primordial', 2))
  event.add('airain:defense_beacon', airainLignes('balise_defense', 2))
  event.add('kubejs:ferraille', airainLignes('ferraille', 1))
  event.add('kubejs:huile_machine', airainLignes('huile_machine', 1))
  event.add('kubejs:rouage_brise', airainLignes('rouage_brise', 1))
  event.add('airain:maintenance_bench', airainLignes('banc_entretien', 2))
  event.add('airain:fine_grindstone', airainLignes('meule_fine', 1))
  event.add('airain:reduction_gear', airainLignes('demultiplicateur', 1))
  event.add('airain:grease_gun', airainLignes('graisseur', 1))
  event.add('airain:imperial_enchanting_table', airainLignes('table_enchantement', 3))
  event.add('airain:runic_ink', airainLignes('encre_runique', 2))
  event.add('airain:trophy_pedestal', airainLignes('socle_trophee', 2))
  event.add('airain:foundation_stone', airainLignes('pierre_fondation', 2))
  event.add('airain:great_standard', airainLignes('grand_etendard', 2))
  event.add('airain:foundation_wall_banner', airainLignes('banniere_murale', 2))
  event.add('airain:banner_template', airainLignes('gabarit_banniere', 2))
  event.add('airain:foundation_registry', airainLignes('registre_fondations', 1))
  event.add('airain:disenchanter', airainLignes('desenchanteur', 2))
})

// Butins renommés : le nom vanilla reste affiché en gris, pour les reconnaître dans les recettes et sur les wikis
ItemEvents.modifyTooltips(event => {
  const vanilla = {
    'minecraft:phantom_membrane': 'phantom_membrane', 'minecraft:ghast_tear': 'ghast_tear', 'minecraft:magma_cream': 'magma_cream',
    'minecraft:wither_skeleton_skull': 'wither_skeleton_skull', 'minecraft:nether_star': 'nether_star', 'minecraft:dragon_egg': 'dragon_egg'
  }
  Object.keys(vanilla).forEach(id => {
    event.add(id, [Text.translate('tooltip.kubejs.vanilla.' + vanilla[id]).darkGray().italic()])
  })
})
