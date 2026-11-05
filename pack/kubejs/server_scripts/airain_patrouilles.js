// ============================================================================
// Patrouilles de l'Empire (chapitre VII) : entre la réactivation du Cœur (tag airain_coeur_reveille, quête « Réactiver le Cœur »)
// et la chute de l'Empereur (tag airain_fin), une patrouille d'automates vient de temps en temps à la rencontre d'un joueur
// en surface. Parfois, elle est larguée du ciel par un dirigeable (le largage).
// Une seule patrouille à la fois ; elle repart si on s'éloigne ou au bout de cinq minutes.
// ============================================================================
const PAT_ARAIGNEE = 'mebahelcreaturesdwarven:dwarven_spider'
const PAT_SPHERE = 'mebahelcreaturesdwarven:dwarven_sphere'
const PAT_GARDIENNE = 'mebahelcreaturesdwarven:dwarven_spider_guardian'
const PAT_PREMIERE = 12000          // ticks avant la première patrouille après le réveil (10 min)
const PAT_ECART_MIN = 18000         // entre deux patrouilles pour un même joueur (15 à 25 min)
const PAT_ECART_MAX = 30000
const PAT_DUREE = 6000              // une patrouille repart au bout de 5 min
const PAT_LARGAGE = 0.35            // part des patrouilles larguées du ciel
const PatHauteur = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')
let PAT = null                      // la patrouille en cours : {tag, joueur, debut, total, largage}
let PAT_N = 0

function patSurface(level, x, z) {
  if (!level.hasChunk(x >> 4, z >> 4)) return null
  return level.getHeight(PatHauteur.MOTION_BLOCKING_NO_LEAVES, x, z)
}

function patDirection(dx, dz) {
  const a = Math.atan2(dz, dx) * 180 / Math.PI      // 0 = est, 90 = sud
  const noms = ['est', 'sud_est', 'sud', 'sud_ouest', 'ouest', 'nord_ouest', 'nord', 'nord_est']
  return noms[((Math.round(a / 45) % 8) + 8) % 8]
}

function patEligible(p) {
  if (!p.tags.contains('airain_coeur_reveille') || p.tags.contains('airain_fin')) return false
  if (p.isSpectator() || p.isCreative()) return false
  if (String(p.level.dimension) !== 'minecraft:overworld') return false
  const sol = patSurface(p.level, Math.floor(p.x), Math.floor(p.z))
  return sol !== null && p.y >= sol - 6
}

function patLancer(server, p) {
  const level = p.level
  const tag = 'airain_patrouille_' + (++PAT_N)
  const largage = Math.random() < PAT_LARGAGE
  const groupe = [PAT_ARAIGNEE, PAT_ARAIGNEE, PAT_SPHERE]
  if (Math.random() < 0.3) groupe.push(PAT_GARDIENNE)
  const a = Math.random() * 2 * Math.PI
  const r = largage ? 0 : 28
  const cx = Math.floor(p.x + Math.cos(a) * r), cz = Math.floor(p.z + Math.sin(a) * r)
  let n = 0
  groupe.forEach((id, i) => {
    const b = a + (i - 1.5) * 0.6
    const x = Math.floor(cx + Math.cos(b) * (largage ? 7 : 3)), z = Math.floor(cz + Math.sin(b) * (largage ? 7 : 3))
    const sol = patSurface(level, x, z)
    if (sol === null) return
    const y = largage ? Math.max(sol, Math.floor(p.y)) + 24 : sol
    const effets = largage ? ',active_effects:[{id:"minecraft:slow_falling",duration:300,amplifier:0,show_particles:1b}]' : ''
    server.runCommandSilent('execute in minecraft:overworld run summon ' + id + ' ' + (x + 0.5) + ' ' + y + ' ' + (z + 0.5) +
      ' {Tags:["airain_patrouille","' + tag + '"],PersistenceRequired:1b' + effets + '}')
    n++
  })
  if (n === 0) return false
  PAT = { tag: tag, joueur: String(p.username), debut: server.tickCount, total: n, largage: largage }
  const ici = 'execute in minecraft:overworld positioned ' + p.x + ' ' + p.y + ' ' + p.z + ' run '
  if (largage) {
    server.runCommandSilent(ici + 'playsound minecraft:item.elytra.flying hostile @a[distance=..64] ~ ~20 ~ 3 0.4')
    server.runCommandSilent(ici + 'playsound minecraft:entity.ender_dragon.flap hostile @a[distance=..64] ~ ~20 ~ 2 0.5')
    server.runCommandSilent(ici + 'particle minecraft:large_smoke ~ ~26 ~ 8 1 8 0.02 60 force')
    server.runCommandSilent(ici + 'title @a[distance=..64] actionbar {"translate":"airain.patrouille.largage","color":"red"}')
  } else {
    server.runCommandSilent(ici + 'playsound minecraft:event.raid.horn hostile @a[distance=..64] ~ ~ ~ 0.6 1.4')
    server.runCommandSilent(ici + 'title @a[distance=..64] actionbar {"translate":"airain.patrouille.approche","with":[{"translate":"airain.direction.' +
      patDirection(cx - p.x, cz - p.z) + '"}],"color":"red"}')
  }
  return true
}

function patEntites(server) {
  const l = []
  try { server.getLevel('minecraft:overworld').getEntities().forEach(e => { if (e.tags.contains(PAT.tag)) l.push(e) }) } catch (err) {}
  return l
}

function patRetirer(server) {
  server.runCommandSilent('execute in minecraft:overworld as @e[tag=' + PAT.tag + '] at @s run tp @s ~ -400 ~')
  server.runCommandSilent('execute in minecraft:overworld run kill @e[tag=' + PAT.tag + ']')
  PAT = null
}

ServerEvents.tick(event => {
  const server = event.server
  if (server.tickCount % 20 !== 7) return
  // la patrouille en cours : elle marche vers son joueur, repart si elle le perd, est notée si elle tombe
  if (PAT) {
    const p = server.getPlayer(PAT.joueur) ? server.getPlayer(PAT.joueur) : null
    const restes = patEntites(server)
    if (server.runCommandSilent('execute in minecraft:overworld if entity @e[tag=' + PAT.tag + ']') <= 0) {
      if (p) {
        server.runCommandSilent('airain chronique note patrouille ' + p.username)
        p.tell(Text.translate('airain.patrouille.repoussee').gold())
        server.runCommandSilent('execute as ' + p.username + ' at @s run give @s numismatics:sprocket 1')
      }
      PAT = null
      return
    }
    if (!p || server.tickCount - PAT.debut > PAT_DUREE || String(p.level.dimension) !== 'minecraft:overworld') { patRetirer(server); return }
    restes.forEach(e => {
      try { if (e.getTarget() === null) { e.setTarget(p); e.getNavigation().moveTo(p.x, p.y, p.z, 1.0) } } catch (err) {}
    })
    const proches = server.runCommandSilent('execute as ' + p.username + ' at @s if entity @e[tag=' + PAT.tag + ',distance=..96]')
    if (proches <= 0) patRetirer(server)
    return
  }
  // sinon : une chance qu'un joueur éligible voie arriver une patrouille
  if (server.tickCount % 200 !== 7) return
  // compteur de temps de jeu par joueur (en ticks, avance de 200 à chaque vérification), gardé dans ses données
  server.players.forEach(p => {
    if (!patEligible(p)) return
    const d = p.persistentData
    const t = (d.contains('airain_patrouille_temps') ? d.getLong('airain_patrouille_temps') : 0) + 200
    d.putLong('airain_patrouille_temps', t)
    if (PAT) return
    if (!d.contains('airain_patrouille_prochaine')) { d.putLong('airain_patrouille_prochaine', t + PAT_PREMIERE); return }
    if (t < d.getLong('airain_patrouille_prochaine')) return
    if (patLancer(server, p))
      d.putLong('airain_patrouille_prochaine', t + PAT_ECART_MIN + Math.floor(Math.random() * (PAT_ECART_MAX - PAT_ECART_MIN)))
  })
})
