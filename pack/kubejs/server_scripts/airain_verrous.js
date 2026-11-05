// L'Empire d'Airain / The Airain Empire — portails et Grands Chantiers
//
// Chaque déblocage est une ÉTIQUETTE posée sur le joueur par une récompense de quête
// (commande « tag @s add ... »). Chaque joueur reçoit la sienne en réclamant la récompense.
//
//   airain_nether     : Gardien des marées (fin du chapitre III)  -> portail du Nether
//   airain_end        : La forge des âmes (fin du chapitre IV)    -> portail de l'End
//   airain_waystones  : Grand Chantier « Le réseau des Waystones » -> poser des Waystones
//   airain_gare       : Grand Chantier « La gare impériale »       -> interfaces de stockage portables
//   airain_atelier    : Grand Chantier « L'atelier d'enchantement » -> machines d'Enchantment Industry
//   airain_pneumatique: Grand Chantier « Le réseau pneumatique »   -> entrées d'Hypertubes
//
// En cas de souci, un administrateur peut poser une étiquette à la main :
//   /tag <joueur> add airain_nether

function airainA(player, etiquette) {
  return player.tags.contains(etiquette)
}

function airainMessage(player, cle) {
  player.displayClientMessage(Text.translate(cle).gold(), true)
}

// ---------- Allumage des portails ----------
BlockEvents.rightClicked(event => {
  const player = event.player
  if (!player) return
  const bloc = String(event.block.id)
  const objet = String(event.item.id)

  if (bloc === 'minecraft:obsidian' && (objet === 'minecraft:flint_and_steel' || objet === 'minecraft:fire_charge')) {
    if (!airainA(player, 'airain_nether')) {
      airainMessage(player, 'airain.portail.nether')
      event.cancel()
    }
  }

  if (bloc === 'minecraft:end_portal_frame' && objet === 'minecraft:ender_eye') {
    if (!airainA(player, 'airain_end')) {
      airainMessage(player, 'airain.portail.end')
      event.cancel()
    }
  }
})

// ---------- Filet de sécurité : un joueur arrivé dans une dimension fermée est renvoyé ----------
PlayerEvents.tick(event => {
  const player = event.player
  if (!player.server || player.tickCount % 40 !== 0) return
  const dim = String(player.level.dimension)
  const ferme = (dim === 'minecraft:the_nether' && !airainA(player, 'airain_nether')) ||
    (dim === 'minecraft:the_end' && !airainA(player, 'airain_end'))
  if (!ferme) return

  const spawn = player.server.overworld().getSharedSpawnPos()
  player.server.runCommandSilent('execute in minecraft:overworld run tp ' + player.username + ' ' +
    spawn.x + ' ' + spawn.y + ' ' + spawn.z)
  airainMessage(player, 'airain.renvoi')
})

// ---------- Blocs réservés aux Grands Chantiers ----------
function airainChantier(bloc) {
  if (bloc.indexOf('waystones:') === 0) return ['airain_waystones', 'airain.chantier.waystones']
  if (bloc === 'create:portable_storage_interface' || bloc === 'create:portable_fluid_interface') {
    return ['airain_gare', 'airain.chantier.gare']
  }
  if (bloc === 'create_enchantment_industry:blaze_enchanter' ||
    bloc === 'create_enchantment_industry:blaze_forger' ||
    bloc === 'create_enchantment_industry:printer') {
    return ['airain_atelier', 'airain.chantier.atelier']
  }
  if (bloc === 'create_hypertube:hypertube_entrance') return ['airain_pneumatique', 'airain.chantier.pneumatique']
  return null
}

BlockEvents.placed(event => {
  const player = event.entity
  if (!player || !player.isPlayer()) return
  const regle = airainChantier(String(event.block.id))
  if (regle && !airainA(player, regle[0])) {
    airainMessage(player, regle[1])
    event.cancel()
  }
})
