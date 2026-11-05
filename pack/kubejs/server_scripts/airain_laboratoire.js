// L'Empire d'Airain / The Airain Empire — Laboratoire 7 (point de départ)
//
// 1. Au premier démarrage du monde, le laboratoire (kubejs/data/kubejs/structure/laboratoire.nbt)
//    est posé sous le point d'apparition, avec un puits à échelle qui remonte jusqu'à la surface.
// 2. À sa première connexion, chaque joueur se réveille dans une des deux capsules,
//    qui devient son point de réapparition.
// 3. Le journal posé sur le pupitre se termine par « Refermer le carnet » : un clic lance
//    /trigger airain_journal ; le script donne alors l'étape airain_journal_lu au joueur,
//    et la tâche « étape » de la quête « Comprendre ce qui s'est passé » se valide d'elle-même.
//    (On ne passe plus par /ftbquests change_progress : la commande est réservée aux joueurs
//    opérateurs et refusait de s'exécuter depuis le serveur.)

const AIRAIN_ETAPE_JOURNAL = 'airain_journal_lu'
const AIRAIN_SORTIE = [11, 15]                 // position du puits dans la structure
const AIRAIN_CAPSULES = [[3, 2], [6, 2]]       // positions des capsules de réveil

let airainCompteur = 0

function airainOrigine(server) {
  const d = server.persistentData
  return [d.getInt('airain_x0'), d.getInt('airain_y0'), d.getInt('airain_z0')]
}

function airainPoser(server) {
  const d = server.persistentData
  if (d.getBoolean('airain_labo')) return true

  const spawn = server.overworld().getSharedSpawnPos()
  const sx = spawn.x, sy = spawn.y, sz = spawn.z
  const x0 = sx - AIRAIN_SORTIE[0], z0 = sz - AIRAIN_SORTIE[1]
  const y0 = Math.max(sy - 13, -56)
  const cmd = c => server.runCommandSilent('execute in minecraft:overworld run ' + c)

  cmd('place template kubejs:laboratoire ' + x0 + ' ' + y0 + ' ' + z0)
  // vérification : le pupitre doit être là, sinon on réessaiera plus tard (zone pas encore chargée)
  const pupitre = server.overworld().getBlock(x0 + 17, y0 + 1, z0 + 3)
  if (String(pupitre.id) !== 'minecraft:lectern') return false

  // puits vers la surface : parois, vide, échelle, margelle
  const hx = sx, hz = sz, bas = y0 + 6, haut = sy
  if (haut > bas) {
    cmd('fill ' + (hx - 1) + ' ' + bas + ' ' + (hz - 1) + ' ' + (hx + 1) + ' ' + haut + ' ' + (hz + 1) + ' minecraft:cobbled_deepslate')
    cmd('fill ' + hx + ' ' + bas + ' ' + hz + ' ' + hx + ' ' + (haut + 2) + ' ' + hz + ' minecraft:air')
    cmd('fill ' + hx + ' ' + bas + ' ' + hz + ' ' + hx + ' ' + haut + ' ' + hz + ' minecraft:ladder[facing=north]')
  }
  cmd('fill ' + (hx - 1) + ' ' + (haut + 1) + ' ' + (hz - 1) + ' ' + (hx + 1) + ' ' + (haut + 1) + ' ' + (hz + 1) + ' minecraft:mossy_cobblestone_wall')
  cmd('fill ' + hx + ' ' + (haut + 1) + ' ' + (hz - 1) + ' ' + hx + ' ' + (haut + 2) + ' ' + hz + ' minecraft:air')

  d.putBoolean('airain_labo', true)
  d.putInt('airain_x0', x0); d.putInt('airain_y0', y0); d.putInt('airain_z0', z0)
  console.info('[Airain] Laboratoire 7 posé en ' + x0 + ' ' + y0 + ' ' + z0)
  return true
}

function airainReveiller(server, player) {
  if (player.stages.has('airain_reveil')) return
  const d = server.persistentData
  const n = d.getInt('airain_reveils')
  const cap = AIRAIN_CAPSULES[n % AIRAIN_CAPSULES.length]
  const o = airainOrigine(server)
  const x = o[0] + cap[0], y = o[1] + 1, z = o[2] + cap[1]
  server.runCommandSilent('execute in minecraft:overworld run tp ' + player.username + ' ' + (x + 0.5) + ' ' + y + ' ' + (z + 0.5) + ' 0 0')
  server.runCommandSilent('execute in minecraft:overworld run spawnpoint ' + player.username + ' ' + x + ' ' + y + ' ' + z)
  d.putInt('airain_reveils', n + 1)
  player.stages.add('airain_reveil')
}

ServerEvents.loaded(event => {
  const server = event.server
  server.runCommandSilent('scoreboard objectives add airain_journal trigger')
  // nom affiché dans le message « Triggered [...] » qui confirme le clic
  server.runCommandSilent('scoreboard objectives modify airain_journal displayname {"translate":"airain.journal.lu"}')
  airainPoser(server)
})

PlayerEvents.loggedIn(event => {
  const server = event.server
  server.runCommandSilent('scoreboard players enable ' + event.player.username + ' airain_journal')
  if (server.persistentData.getBoolean('airain_labo')) airainReveiller(server, event.player)
})

ServerEvents.tick(event => {
  airainCompteur++
  if (airainCompteur % 20 !== 0) return
  const server = event.server

  // laboratoire pas encore posé (zone pas chargée au démarrage) : on réessaie
  if (!server.persistentData.getBoolean('airain_labo')) {
    if (!airainPoser(server)) return
  }
  server.players.forEach(p => airainReveiller(server, p))

  // lecture du journal
  server.runCommandSilent('tag @a[scores={airain_journal=1..}] add ' + AIRAIN_ETAPE_JOURNAL)
  server.players.forEach(p => {
    if (p.tags.contains(AIRAIN_ETAPE_JOURNAL) && !p.stages.has(AIRAIN_ETAPE_JOURNAL)) p.stages.add(AIRAIN_ETAPE_JOURNAL)
  })
  server.runCommandSilent('scoreboard players set @a[scores={airain_journal=1..}] airain_journal 0')
  server.runCommandSilent('scoreboard players enable @a airain_journal')
})
