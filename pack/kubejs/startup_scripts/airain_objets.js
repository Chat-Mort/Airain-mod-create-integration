// L'Empire d'Airain / The Airain Empire — objets du pack
// Les noms sont traduits : voir kubejs/assets/kubejs/lang/fr_fr.json et en_us.json
// Schémas : clés de progression, jamais consommées dans les recettes (keepIngredient).
// Fragments de mémoire : récompenses des gardiens, consommés pour forger le Cœur d'Airain.

StartupEvents.registry('item', event => {
  const nom = id => Text.translate('item.kubejs.' + id)

  // --- Schémas (débloquent un palier) ---
  for (const id of ['schema_cuivre', 'schema_laiton', 'schema_ciel']) {
    event.create(id)
      .displayName(nom(id).gold())
      .unstackable()
      .rarity('rare')
      .fireResistant()
  }

  // --- Fragments de mémoire (un par gardien) ---
  for (const id of ['fragment_rouages', 'fragment_marees', 'fragment_forge', 'fragment_vide']) {
    event.create(id)
      .displayName(nom(id).aqua())
      .maxStackSize(16)
      .rarity('uncommon')
      .fireResistant()
  }

  // --- Grands Chantiers et équipement ---
  event.create('sceau_forge')
    .displayName(nom('sceau_forge').gold())
    .unstackable()
    .rarity('rare')
    .fireResistant()

  event.create('plaque_netherite')
    .displayName(nom('plaque_netherite'))
    .fireResistant()

  // Objet de transition de l'assemblage en séquence (comme le mécanisme de précision inachevé)
  event.create('plaque_netherite_inachevee')
    .displayName(nom('plaque_netherite_inachevee'))
    .maxStackSize(1)
    .fireResistant()

  // --- L'objet final ---
  event.create('coeur_d_airain')
    .displayName(nom('coeur_d_airain').gold().bold())
    .unstackable()
    .rarity('epic')
    .fireResistant()

  event.create('coeur_brise')                 // le premier Cœur, volé par Morgana : lâché une seule fois par le gardien du Vide
    .displayName(nom('coeur_brise').gold())
    .unstackable()
    .rarity('rare')
    .fireResistant()
  event.create('coeur_eteint')                // le Cœur d'Airain après la mort de l'Empereur : ne sert qu'au choix final
    .displayName(nom('coeur_eteint').gold().bold())
    .unstackable()
    .rarity('epic')
    .fireResistant()

  // --- La voie de l'Écho (annexe « Les Échos perdus ») ---
  event.create('fragment_resonance')          // lâché par les âmes sans repos, trouvé près des relais brisés
    .displayName(nom('fragment_resonance').lightPurple())
    .maxStackSize(64)
    .rarity('uncommon')
  event.create('diapason_echo')               // réveille le Chœur des Égarés au Grand Relais (consommé)
    .displayName(nom('diapason_echo').lightPurple())
    .unstackable()
    .rarity('rare')
  event.create('echo_primordial')             // récompense du boss : ingrédient des sorts les plus puissants
    .displayName(nom('echo_primordial').lightPurple().bold())
    .maxStackSize(16)
    .rarity('epic')
    .glow(true)
    .fireResistant()

})

// --- Butin des automates (les monstres de l'Empire sont des machines) ---
// Ferraille : se recycle au four (1 pépite) ou aux roues de concassage (davantage, avec une chance de zinc).
// Huile de machine : combustible (four, brûleur à blaze) — voir data/neoforge/data_maps/item/furnace_fuels.json
// Rouage brisé : la presse mécanique le remet en état.
StartupEvents.registry('item', event => {
  const nom = id => Text.translate('item.kubejs.' + id)
  event.create('ferraille').displayName(nom('ferraille'))
  event.create('huile_machine').displayName(nom('huile_machine')).maxStackSize(16)
  event.create('rouage_brise').displayName(nom('rouage_brise'))
})

// --- Banc d'entretien : répare comme une enclume, mais tourne à l'huile et à la force des rouages ---
// L'huile (fluide kubejs:huile) est définie ici ; la machine vient du mod airain (https://github.com/Chat-Mort/Airain-mod-create-integration).
StartupEvents.registry('fluid', event => {
  event.create('huile').tint(0x7A5226).displayName(Text.translate('fluid.kubejs.huile'))
})

// Le bloc lui-même est fourni par le mod « Airain : intégration Create » (airain:maintenance_bench).

// --- Onglet créatif : tous les objets du pack sont regroupés dans l'onglet « L'Empire d'Airain » du mod airain ---
StartupEvents.modifyCreativeTab('kubejs:tab', event => {
  try {
    event.remove('@kubejs')
  } catch (e) {
    console.warn('Onglet KubeJS : ' + e)
  }
})
