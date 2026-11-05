// L'Empire d'Airain / The Airain Empire — la balise de défense (chapitre VII, voir la Bible)
//
// Un bloc à poser dans la base. Elle n'est jamais consommée.
//   Accroupi + clic droit (balise au repos) : règle le rayon d'apparition (48, 64, 96, 128 ; 64 par défaut)
//                                             et montre pendant quelques secondes le cercle d'arrivée.
//   Clic droit : lance un assaut de 4 vagues après un compte à rebours (le cercle s'affiche).
//   Accroupi + clic droit pendant un assaut : l'abandonne.
// Les ennemis n'apparaissent que sur du sol naturel (terre, herbe, sable, neige, pierre, gravier…) à ciel ouvert,
// sur le cercle choisi : jamais sur vos sols, toits ou chemins. Le cercle vide sur vos murailles le montre.
// Entre deux vagues, 30 secondes de répit. Si tout le monde meurt ou s'éloigne, seule la vague en cours recommence
// quand quelqu'un revient. La 4e vague : un centurion à vapeur et son escorte. La première victoire valide la quête.
// Plus d'ennemis à deux, et un quart de plus à chaque victoire (jusqu'au double).

const BAL_TOUR = 'airain:defense_beacon'             // la tour-phare du mod (cœur, au centre du socle)
const BAL_PARTIE = 'airain:defense_beacon_part'            // les autres cases de la tour
const BAL_RAYONS = [48, 64, 96, 128]
const BAL_REPIT = 30
const BAL_COMPTE = 8               // secondes de compte à rebours avant la première vague
const BAL_LUEUR = 90               // secondes avant que les derniers ennemis ne brillent
const BAL_ATTENTE_MAX = 600        // sans personne pendant 10 minutes : l'assaut est abandonné
const BAL_SESSIONS = {}
const BAL_APERCUS = {}
let BAL_COMPTEUR = 0
const BalHauteur = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')

const BAL_ARAIGNEE = 'mebahelcreaturesdwarven:dwarven_spider'
const BAL_SPHERE = 'mebahelcreaturesdwarven:dwarven_sphere'
const BAL_GARDIENNE = 'mebahelcreaturesdwarven:dwarven_spider_guardian'
const BAL_CENTURION = 'mebahelcreaturesdwarven:dwarven_centurion'
// vagues de base : [ennemi, nombre, plafond] (le centurion reste toujours seul)
const BAL_VAGUES = [
  [[BAL_ARAIGNEE, 4, 10]],
  [[BAL_ARAIGNEE, 3, 8], [BAL_SPHERE, 3, 8]],
  [[BAL_ARAIGNEE, 3, 8], [BAL_SPHERE, 2, 6], [BAL_GARDIENNE, 1, 3]],
  [[BAL_CENTURION, 1, 1], [BAL_GARDIENNE, 1, 3], [BAL_ARAIGNEE, 4, 10]]
]
const BAL_RARES = [  // [objet, nombre, poids]
  ['minecraft:totem_of_undying', 1, 3], ['minecraft:golden_apple', 3, 4], ['minecraft:experience_bottle', 16, 4],
  ['minecraft:diamond', 4, 4], ['minecraft:netherite_scrap', 2, 2], ['kubejs:fragment_resonance', 3, 3],
  ['minecraft:enchanted_golden_apple', 1, 1]
]
const BAL_SOL_TAGS = ['minecraft:dirt', 'minecraft:sand', 'minecraft:base_stone_overworld', 'minecraft:terracotta',
  'minecraft:snow', 'minecraft:nylium', 'minecraft:base_stone_nether']
const BAL_SOL_IDS = ['minecraft:gravel', 'minecraft:snow_block', 'minecraft:powder_snow', 'minecraft:clay',
  'minecraft:soul_sand', 'minecraft:soul_soil', 'minecraft:end_stone', 'minecraft:calcite', 'minecraft:tuff']

// ---------- données conservées (rayon et victoires de chaque balise) ----------
function balCle(level, x, y, z) { return String(level.dimension) + '|' + x + '|' + y + '|' + z }
function balLire(server, cle, champ, defaut) {
  const k = 'airain_balise_' + champ + '|' + cle
  return server.persistentData.contains(k) ? server.persistentData.getInt(k) : defaut
}
function balEcrire(server, cle, champ, v) { server.persistentData.putInt('airain_balise_' + champ + '|' + cle, v) }

// ---------- sol naturel à ciel ouvert ----------
function balSol(level, x, z) {
  if (!level.hasChunk(x >> 4, z >> 4)) return null
  const h = level.getHeight(BalHauteur.MOTION_BLOCKING_NO_LEAVES, x, z)
  const bloc = level.getBlock(x, h - 1, z)
  const id = String(bloc.id)
  if (BAL_SOL_IDS.indexOf(id) >= 0) return h
  for (let i = 0; i < BAL_SOL_TAGS.length; i++) if (bloc.hasTag(BAL_SOL_TAGS[i])) return h
  return null
}

// une case de la tour renvoie à son cœur ; le cœur et l'ancienne balise renvoient à eux-mêmes
function balCoeur(block) {
  if (String(block.id) !== BAL_PARTIE) return { x: block.x, y: block.y, z: block.z }
  const p = block.properties
  return { x: block.x + 1 - parseInt(p.get('px')), y: block.y - parseInt(p.get('py')), z: block.z + 1 - parseInt(p.get('pz')) }
}
// la tour s'anime pendant l'assaut (sirène, phare, faisceaux) : son cœur garde l'état « alerte »
function balAlerte(server, s, on) {
  if (!s.tour) return
  server.runCommandSilent('execute in ' + s.dim + ' run data merge block ' + s.x + ' ' + s.y + ' ' + s.z + ' {alerte:' + (on ? '1b' : '0b') + '}')
}

// ---------- ambiance de l'assaut ----------
// Le ciel se couvre et l'orage gronde pendant les vagues (la météo d'avant revient à la fin) ;
// pendant le répit, la marche des machines se rapproche depuis le cercle, et le cœur bat les dix dernières secondes.
let BAL_ORAGES = 0, BAL_METEO = null
function balOrage(server, level, on) {
  if (on) {
    if (BAL_ORAGES++ === 0) BAL_METEO = { pluie: level.isRaining(), orage: level.isThundering() }
    server.runCommandSilent('weather thunder 1d')
  } else if (BAL_ORAGES > 0 && --BAL_ORAGES === 0 && BAL_METEO) {
    server.runCommandSilent(BAL_METEO.orage ? 'weather thunder' : BAL_METEO.pluie ? 'weather rain' : 'weather clear')
    BAL_METEO = null
  }
}
function balRumeur(server, s) {
  const a = Math.random() * 2 * Math.PI
  const x = (s.x + 0.5 + Math.cos(a) * s.rayon).toFixed(1), z = (s.z + 0.5 + Math.sin(a) * s.rayon).toFixed(1)
  const sons = ['minecraft:entity.iron_golem.step', 'minecraft:block.piston.extend', 'minecraft:block.anvil.land']
  server.runCommandSilent(balIci(s) + 'playsound ' + sons[Math.floor(Math.random() * sons.length)] + ' hostile ' + balQui(s) + ' ' + x + ' ' + s.y + ' ' + z + ' 5 0.5')
}

// la sirène des haut-parleurs : seulement pendant l'annonce d'une vague
function balSirene(server, s) {
  server.runCommandSilent(balIci(s) + 'playsound minecraft:item.goat_horn.sound.6 block ' + balQui(s) + ' ~ ~5 ~ 4 0.55')
}
// la corne de la vague coupe d'un coup les battements et la sirène
function balSilence(server, s) {
  const qui = balQui(s)
  for (const son of ['minecraft:item.goat_horn.sound.6', 'minecraft:entity.warden.heartbeat', 'minecraft:block.note_block.basedrum'])
    server.runCommandSilent(balIci(s) + 'stopsound ' + qui + ' * ' + son)
}
function balIci(s) { return 'execute in ' + s.dim + ' positioned ' + (s.x + 0.5) + ' ' + s.y + ' ' + (s.z + 0.5) + ' run ' }
function balQui(s) { return '@a[distance=..' + (s.rayon + 32) + ']' }

function balCercle(server, level, s) {
  const n = Math.ceil(2 * Math.PI * s.rayon / 3)
  for (let i = 0; i < n; i++) {
    const a = i * 2 * Math.PI / n
    const x = Math.floor(s.x + Math.cos(a) * s.rayon), z = Math.floor(s.z + Math.sin(a) * s.rayon)
    const h = balSol(level, x, z)
    if (h === null) continue
    server.runCommandSilent(balIci(s) + 'particle minecraft:dust{color:[1.0,0.15,0.1],scale:3.0} ' + (x + 0.5) + ' ' + (h + 0.6) + ' ' +
      (z + 0.5) + ' 0 0.4 0 0 2 force ' + balQui(s))
  }
}

function balBarre(server, s, cle, arg, valeur, max) {
  server.runCommandSilent('bossbar set ' + s.barre + ' name {"translate":"' + cle + '","with":["' + arg + '"]}')
  server.runCommandSilent('bossbar set ' + s.barre + ' max ' + Math.max(1, max))
  server.runCommandSilent('bossbar set ' + s.barre + ' value ' + Math.max(0, Math.min(valeur, max)))
  server.runCommandSilent(balIci(s) + 'bossbar set ' + s.barre + ' players ' + balQui(s))
}

function balVider(server, s) {   // les ennemis restants repartent sous terre, sans rien laisser
  server.runCommandSilent('execute as @e[tag=' + s.tag + '] at @s run tp @s ~ -400 ~')
  server.runCommandSilent('kill @e[tag=' + s.tag + ']')
}

function balFin(server, cle, message) {
  const s = BAL_SESSIONS[cle]
  if (!s) return
  balVider(server, s)
  balAlerte(server, s, false)
  if (s.orage) { balOrage(server, s.level, false); s.orage = false }
  server.runCommandSilent('bossbar remove ' + s.barre)
  if (message) server.runCommandSilent(balIci(s) + 'tellraw ' + balQui(s) + ' {"translate":"' + message + '","color":"gold"}')
  delete BAL_SESSIONS[cle]
}

function balLancer(server, s) {
  const base = BAL_VAGUES[s.vague - 1]
  let total = 0
  base.forEach(e => {
    const nb = e[0] === BAL_CENTURION ? 1 : Math.min(e[2], Math.max(1, Math.round(e[1] * s.facteur)))
    for (let i = 0; i < nb; i++) {
      let pos = null
      for (let essai = 0; essai < 40 && pos === null; essai++) {
        const a = Math.random() * 2 * Math.PI, r = s.rayon + Math.random() * 8
        const x = Math.floor(s.x + Math.cos(a) * r), z = Math.floor(s.z + Math.sin(a) * r)
        const h = balSol(s.level, x, z)
        if (h !== null) pos = [x, h, z]
      }
      if (pos === null) continue
      server.runCommandSilent('execute in ' + s.dim + ' run summon ' + e[0] + ' ' + (pos[0] + 0.5) + ' ' + pos[1] + ' ' + (pos[2] + 0.5) +
        ' {Tags:["airain_vague","' + s.tag + '"],PersistenceRequired:1b}')
      total++
    }
  })
  s.total = total
  if (!s.orage) { balOrage(server, s.level, true); s.orage = true }
  s.etat = 'combat'
  s.duree = 0
  if (total === 0) {
    balFin(server, s.cle, 'airain.balise.pas_de_sol')
    return
  }
  balSilence(server, s)
  server.runCommandSilent(balIci(s) + 'playsound minecraft:event.raid.horn hostile ' + balQui(s) + ' ~ ~ ~ 64 0.8')
  server.runCommandSilent(balIci(s) + 'title ' + balQui(s) + ' actionbar {"translate":"airain.balise.vague","with":["' + s.vague + '"],"color":"red"}')
  balBarre(server, s, 'airain.balise.barre', s.vague, total, total)
}

function balVictoire(server, s) {
  const ici = balIci(s), qui = balQui(s)
  const victoires = balLire(server, s.cle, 'victoires', 0) + 1
  balEcrire(server, s.cle, 'victoires', victoires)
  server.runCommandSilent(ici + 'tag ' + qui + ' add airain_assaut')
  server.runCommandSilent('airain chronique note assaut ' + victoires)   // Chroniques oubliées : journal de bord
  server.runCommandSilent(ici + 'give ' + qui + ' numismatics:cog ' + Math.min(1 + victoires, 6))
  // un objet rare garanti, et une chance d'en avoir un second
  const tirages = Math.random() < 0.5 ? 2 : 1
  for (let t = 0; t < tirages; t++) {
    let total = 0
    BAL_RARES.forEach(r => { total += r[2] })
    let v = Math.random() * total
    for (let i = 0; i < BAL_RARES.length; i++) {
      v -= BAL_RARES[i][2]
      if (v <= 0) { server.runCommandSilent(ici + 'give ' + qui + ' ' + BAL_RARES[i][0] + ' ' + BAL_RARES[i][1]); break }
    }
  }
  server.runCommandSilent(ici + 'playsound minecraft:ui.toast.challenge_complete player ' + qui + ' ~ ~ ~ 64 1')
  balFin(server, s.cle, 'airain.balise.victoire')
}

// ---------- clic droit sur la balise ----------
function balAction(event) {
  if (String(event.hand) !== 'MAIN_HAND') return false
  const player = event.player, level = event.level, server = event.server
  const block = balCoeur(event.block)
  const tour = true
  const cle = balCle(level, block.x, block.y, block.z)
  const accroupi = player.isShiftKeyDown()

  if (BAL_SESSIONS[cle]) {
    if (accroupi) balFin(server, cle, 'airain.balise.abandon')
    else player.setStatusMessage(Text.translate('airain.balise.en_cours').gold())
    return true
  }
  let rayon = balLire(server, cle, 'rayon', 64)
  if (accroupi) {
    rayon = BAL_RAYONS[(BAL_RAYONS.indexOf(rayon) + 1) % BAL_RAYONS.length]
    balEcrire(server, cle, 'rayon', rayon)
    player.setStatusMessage(Text.translate('airain.balise.rayon', String(rayon)).gold())
    BAL_APERCUS[cle] = { level: level, dim: String(level.dimension), x: block.x, y: block.y, z: block.z, rayon: rayon, reste: 6 }
    return true
  }

  const victoires = balLire(server, cle, 'victoires', 0)
  const joueurs = server.runCommandSilent('execute in ' + String(level.dimension) + ' positioned ' + (block.x + 0.5) + ' ' + block.y + ' ' +
    (block.z + 0.5) + ' if entity @a[distance=..' + (rayon + 32) + ']')
  BAL_COMPTEUR++
  const s = {
    cle: cle, level: level, dim: String(level.dimension), x: block.x, y: block.y, z: block.z, rayon: rayon,
    facteur: (1 + 0.25 * Math.min(victoires, 4)) * (joueurs >= 2 ? 1.5 : 1),
    vague: 1, etat: 'compte', attente: BAL_COMPTE, duree: 0, total: 0, absence: 0,
    tag: 'airain_balise_' + BAL_COMPTEUR, barre: 'kubejs:balise_' + BAL_COMPTEUR, tour: tour
  }
  BAL_SESSIONS[cle] = s
  delete BAL_APERCUS[cle]
  server.runCommandSilent('bossbar add ' + s.barre + ' ""')
  server.runCommandSilent('bossbar set ' + s.barre + ' color red')
  server.runCommandSilent('bossbar set ' + s.barre + ' style notched_10')
  server.runCommandSilent(balIci(s) + 'tellraw ' + balQui(s) + ' {"translate":"airain.balise.appel","color":"red","italic":true}')
  balAlerte(server, s, true)
  balBarre(server, s, 'airain.balise.compte', s.attente, 0, BAL_COMPTE)
  return true
}
// event.cancel() arrête aussitôt le script : on ne l'appelle qu'après avoir tout fait
function balClic(event) { if (balAction(event)) event.cancel() }
BlockEvents.rightClicked(BAL_TOUR, balClic)
BlockEvents.rightClicked(BAL_PARTIE, balClic)

function balCasse(event) {
  const b = balCoeur(event.block)
  const cle = balCle(event.level, b.x, b.y, b.z)
  delete BAL_APERCUS[cle]
  if (BAL_SESSIONS[cle]) balFin(event.server, cle, 'airain.balise.abandon')
}
BlockEvents.broken(BAL_TOUR, balCasse)
BlockEvents.broken(BAL_PARTIE, balCasse)

// ---------- chaque seconde ----------
ServerEvents.tick(event => {
  const server = event.server
  if (server.tickCount % 20 !== 0) return

  Object.keys(BAL_APERCUS).forEach(cle => {
    const a = BAL_APERCUS[cle]
    balCercle(server, a.level, a)
    if (--a.reste <= 0) delete BAL_APERCUS[cle]
  })

  Object.keys(BAL_SESSIONS).forEach(cle => {
    const s = BAL_SESSIONS[cle]
    const presents = server.runCommandSilent(balIci(s) + 'execute if entity ' + balQui(s))

    // tout le monde est mort ou parti : la vague en cours est retirée, elle recommencera
    if (presents <= 0) {
      if (s.etat === 'combat') balVider(server, s)
      if (s.etat !== 'absence') { s.etat = 'absence'; s.absence = 0 }
      if (++s.absence >= BAL_ATTENTE_MAX) balFin(server, cle, null)
      return
    }
    if (s.etat === 'absence') {
      s.etat = 'repit'
      s.attente = BAL_REPIT
      server.runCommandSilent(balIci(s) + 'tellraw ' + balQui(s) + ' {"translate":"airain.balise.reprise","with":["' + s.vague + '"],"color":"gold"}')
    }

    if (s.etat === 'compte' || s.etat === 'repit') {
      if (s.etat === 'compte') balCercle(server, s.level, s)
      s.attente--
      if (s.etat === 'compte') server.runCommandSilent(balIci(s) + 'playsound minecraft:block.note_block.basedrum block ' + balQui(s) + ' ~ ~ ~ 2 0.6')
      if ((s.etat === 'compte' || s.attente <= 10) && s.attente > 0 && s.attente % 4 === 0) balSirene(server, s)
      else {
        if (s.attente % 6 === 0) balRumeur(server, s)
        if (s.attente <= 10 && s.attente > 0) server.runCommandSilent(balIci(s) + 'playsound minecraft:entity.warden.heartbeat ambient ' + balQui(s) + ' ~ ~ ~ ' + (0.6 + (10 - s.attente) * 0.08).toFixed(2) + ' 1')
      }
      balBarre(server, s, s.etat === 'compte' ? 'airain.balise.compte' : 'airain.balise.repit', s.vague,
        (s.etat === 'compte' ? BAL_COMPTE : BAL_REPIT) - s.attente, s.etat === 'compte' ? BAL_COMPTE : BAL_REPIT)
      if (s.attente <= 0) balLancer(server, s)
      return
    }

    // combat
    s.duree++
    const restants = server.runCommandSilent('execute if entity @e[tag=' + s.tag + ']')
    balBarre(server, s, 'airain.balise.barre', s.vague, restants, s.total)
    if (s.duree === BAL_LUEUR) server.runCommandSilent('effect give @e[tag=' + s.tag + '] minecraft:glowing infinite 0 true')
    if (restants > 0) return
    if (s.vague >= BAL_VAGUES.length) { balVictoire(server, s); return }
    server.runCommandSilent(balIci(s) + 'give ' + balQui(s) + ' numismatics:sprocket ' + s.vague)
    server.runCommandSilent(balIci(s) + 'tellraw ' + balQui(s) + ' {"translate":"airain.balise.vague_ok","with":["' + s.vague + '","' + BAL_REPIT + '"],"color":"gold"}')
    s.vague++
    s.etat = 'repit'
    s.attente = BAL_REPIT
  })
})
