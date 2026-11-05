// L'Empire d'Airain / The Airain Empire — salles scellées des avant-postes, distributeurs, règles du monde
//
// Une salle scellée est fermée par une porte de fer surmontée d'une « marque » qui donne son palier :
//   bloc de cuivre ciré -> Schéma du Cuivre, bloc de laiton -> Schéma du Laiton, terre cuite émaillée bleu clair -> Schéma du Ciel.
// Clic droit sur la porte avec le bon Schéma en main : la porte disparaît pour de bon (pour les deux joueurs).
// Tant que la porte est là, les blocs de la salle ne peuvent pas être cassés en survie.
// Les distributeurs créatifs (laboratoire, avant-postes) ne peuvent jamais être cassés en survie.

const AIRAIN_SCEAUX = {
  'minecraft:waxed_copper_block': 'kubejs:schema_cuivre',
  'create:brass_block': 'kubejs:schema_laiton',
  'minecraft:light_blue_glazed_terracotta': 'kubejs:schema_ciel'
}
// blocs dont sont faites les salles : seuls ceux-là déclenchent la recherche d'un sceau proche
const AIRAIN_MATERIAUX_SALLE = ['create:industrial_iron_block', 'minecraft:tuff_bricks', 'minecraft:iron_door',
  'minecraft:cut_sandstone', 'minecraft:stone_bricks', 'minecraft:mud_bricks',
  'minecraft:waxed_copper_block', 'create:brass_block', 'minecraft:light_blue_glazed_terracotta',
  'minecraft:waxed_cut_copper', 'create:brass_casing', 'minecraft:waxed_copper_bulb', 'minecraft:spruce_wall_sign',
  'create:large_cogwheel', 'create:fluid_pipe', 'create:weathered_iron_block', 'minecraft:campfire']

// (x, y, z) est un bloc de porte de fer : renvoie {bas, schema} si c'est une porte scellée
function airainSceau(level, x, y, z) {
  const b = level.getBlock(x, y, z)
  if (String(b.id) !== 'minecraft:iron_door') return null
  const haut = String(b.properties.get('half')) === 'upper' ? y : y + 1
  const schema = AIRAIN_SCEAUX[String(level.getBlock(x, haut + 1, z).id)]
  return schema ? { bas: haut - 1, schema: schema } : null
}

function airainSceauProche(level, x, y, z) {
  for (let dx = -4; dx <= 4; dx++)
    for (let dz = -4; dz <= 4; dz++)
      for (let dy = -4; dy <= 4; dy++)
        if (String(level.getBlock(x + dx, y + dy, z + dz).id) === 'minecraft:iron_door' &&
            airainSceau(level, x + dx, y + dy, z + dz)) return true
  return false
}

// event.cancel() arrête aussitôt le script : on ne l'appelle qu'après avoir tout fait
function airainPorteScellee(event) {
  if (String(event.hand) !== 'MAIN_HAND') return false
  const block = event.block, player = event.player, level = event.level
  const s = airainSceau(level, block.x, block.y, block.z)
  if (!s) return false
  if (String(player.mainHandItem.id) !== s.schema) {
    player.setStatusMessage(Text.translate('airain.sceau.refus',
      Text.translate('item.kubejs.' + s.schema.split(':')[1])).gold())
    return true
  }
  // 2 (mise à jour des clients) + 16 (pas de réaction des voisins) + 32 (pas d'objet lâché)
  level.getBlock(block.x, s.bas + 1, block.z).set('minecraft:air', {}, 50)
  level.getBlock(block.x, s.bas, block.z).set('minecraft:air', {}, 50)
  const dim = String(level.dimension)
  const pos = block.x + ' ' + (s.bas + 1) + ' ' + block.z
  event.server.runCommandSilent('execute in ' + dim + ' run playsound minecraft:block.vault.open_shutter block @a ' + pos + ' 1 0.7')
  event.server.runCommandSilent('execute in ' + dim + ' run particle minecraft:wax_off ' + pos + ' 0.4 0.8 0.4 0 40')
  player.tell(Text.translate('airain.sceau.ouvert').green())
  return true
}
BlockEvents.rightClicked('minecraft:iron_door', event => { if (airainPorteScellee(event)) event.cancel() })

BlockEvents.broken(event => {
  const player = event.entity
  if (!player || !player.isPlayer() || player.isCreative()) return
  const id = String(event.block.id)
  if (id === 'numismatics:creative_vendor') {
    player.setStatusMessage(Text.translate('airain.distributeur.protege').gold())
    event.cancel(); return
  }
  if (AIRAIN_MATERIAUX_SALLE.indexOf(id) < 0) return
  if (airainSceauProche(event.level, event.block.x, event.block.y, event.block.z)) {
    player.setStatusMessage(Text.translate('airain.sceau.protege').gold())
    event.cancel()
  }
})

// ---------- Règles du monde : plus de marchand ambulant, de patrouilles ni de raids ----------
ServerEvents.loaded(event => {
  const s = event.server
  s.runCommandSilent('gamerule doTraderSpawning false')
  s.runCommandSilent('gamerule doPatrolSpawning false')
  s.runCommandSilent('gamerule disableRaids true')
})

// ---------- Aucun humain dans le monde de l'Empire ----------
// Filet de sécurité général : quelle que soit la structure ou le mod qui les fait apparaître
// (îles volantes, donjons d'autres mods, œufs…), ces créatures sont retirées dès leur arrivée dans le monde.
const AIRAIN_BANNIS = ['minecraft:villager', 'minecraft:wandering_trader', 'minecraft:trader_llama', 'minecraft:zombie_villager',
  'minecraft:witch', 'minecraft:pillager', 'minecraft:vindicator', 'minecraft:evoker', 'minecraft:illusioner', 'minecraft:ravager']

EntityEvents.spawned(event => {
  if (AIRAIN_BANNIS.indexOf(String(event.entity.type)) >= 0) event.cancel()
})
