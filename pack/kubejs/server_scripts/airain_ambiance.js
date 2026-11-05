// L'Empire d'Airain / The Airain Empire — sons d'ambiance des structures
//
// Toutes les secondes, chaque joueur a une petite chance (au plus un son toutes les 25 s) d'entendre un son du lieu où il se trouve : vapeur, rouages et tôle
// dans les avant-postes, les cités et les ruines de l'Empire ; murmures de l'Écho aux relais et au sanctuaire ;
// feu et toile dans les camps réfractaires. Le son vient de quelques blocs autour, jamais sur le joueur.
// Les lieux sont des prédicats de données : kubejs/data/kubejs/predicate/ambiance/<lieu>.json

const AMB_LIEUX = {
  empire: {
    chance: 0.05,
    sons: [ // [son, volume, hauteur min, hauteur max]
      ['minecraft:block.lava.extinguish', 0.25, 0.6, 0.9],       // un jet de vapeur
      ['minecraft:block.fire.extinguish', 0.2, 0.5, 0.7],
      ['minecraft:block.grindstone.use', 0.18, 0.4, 0.6],        // des rouages qui grincent, loin
      ['minecraft:block.chain.step', 0.5, 0.5, 0.8],
      ['minecraft:block.iron_trapdoor.close', 0.3, 0.5, 0.7],    // une tôle qui claque
      ['minecraft:block.copper_door.close', 0.25, 0.6, 0.8],
      ['minecraft:block.piston.contract', 0.2, 0.5, 0.6],
      ['minecraft:block.copper_bulb.turn_on', 0.3, 0.5, 0.7],    // un relais qui claque dans le vide
      ['minecraft:entity.iron_golem.step', 0.4, 0.5, 0.6]        // quelque chose de lourd, quelque part
    ]
  },
  echo: {
    chance: 0.05,
    sons: [
      ['minecraft:block.sculk.spread', 0.5, 0.6, 0.9],
      ['minecraft:block.amethyst_block.chime', 0.6, 0.5, 0.8],
      ['minecraft:particle.soul_escape', 0.8, 0.5, 0.9],
      ['minecraft:ambient.soul_sand_valley.additions', 0.4, 0.8, 1.0],
      ['minecraft:block.respawn_anchor.ambient', 0.35, 0.6, 0.8],
      ['minecraft:entity.allay.ambient_without_item', 0.15, 0.4, 0.5]   // un murmure
    ]
  },
  refractaires: {
    chance: 0.05,
    sons: [
      ['minecraft:block.campfire.crackle', 0.7, 0.8, 1.1],
      ['minecraft:entity.phantom.flap', 0.25, 0.6, 0.8],         // le vent dans la toile des tentes
      ['minecraft:block.wool.step', 0.4, 0.6, 0.8],
      ['minecraft:block.barrel.open', 0.25, 0.8, 1.0],
      ['minecraft:block.ladder.step', 0.3, 0.7, 0.9]
    ]
  }
}
const AMB_ORDRE = ['echo', 'refractaires', 'empire']   // le premier lieu reconnu l'emporte
const AMB_ATTENTE = 25   // au moins 25 s entre deux sons pour un même joueur
const AMB_DERNIER = {}

ServerEvents.tick(event => {
  const server = event.server
  if (server.tickCount % 20 !== 7) return
  server.players.forEach(p => {
    if (p.isSpectator()) return
    const nom = String(p.username)
    const t = Math.floor(server.tickCount / 20)
    if (AMB_DERNIER[nom] !== undefined && t - AMB_DERNIER[nom] < AMB_ATTENTE) return
    for (let i = 0; i < AMB_ORDRE.length; i++) {
      const lieu = AMB_LIEUX[AMB_ORDRE[i]]
      if (Math.random() >= lieu.chance) continue
      const dedans = server.runCommandSilent('execute as ' + nom + ' at @s if predicate kubejs:ambiance/' + AMB_ORDRE[i])
      if (dedans <= 0) continue
      const s = lieu.sons[Math.floor(Math.random() * lieu.sons.length)]
      const a = Math.random() * 2 * Math.PI, d = 5 + Math.random() * 9
      const dx = (Math.cos(a) * d).toFixed(1), dz = (Math.sin(a) * d).toFixed(1), dy = (Math.random() * 4 - 1).toFixed(1)
      const h = (s[2] + Math.random() * (s[3] - s[2])).toFixed(2)
      AMB_DERNIER[nom] = t
      server.runCommandSilent('execute as ' + nom + ' at @s run playsound ' + s[0] + ' ambient ' + nom + ' ~' + dx + ' ~' + dy + ' ~' + dz + ' ' + s[1] + ' ' + h)
      return
    }
  })
})
