// L'Empire d'Airain / The Airain Empire — la voie de l'Écho
//
// 1. Le Chœur des Égarés : au cœur du Grand Relais, un résonateur (pierre de magnétite posée sur de l'ardoise
//    renforcée, introuvable ailleurs). Clic droit avec le diapason d'Écho : il est consommé et le boss s'éveille.
//    C'est la Chimère sauvage d'Ars Nouveau, renommée et renforcée.
// 2. À sa mort, chaque joueur proche reçoit de l'Écho primordial (ingrédient des sorts les plus puissants).
// 3. « Les machines ne sentent pas l'Écho » : les sorts font 50 % de dégâts en plus aux créatures de l'Empire.

const AIRAIN_CHOEUR = 'ars_nouveau:wilden_boss'
const AIRAIN_CHOEUR_VIE = 600               // la Chimère d'origine en a beaucoup moins : à ajuster après essai
const AIRAIN_ECHO_PAR_JOUEUR = 8
const AIRAIN_DEGATS_ECHO = ['ars_nouveau:spell', 'ars_nouveau:frost', 'ars_nouveau:flare', 'ars_nouveau:crush', 'ars_nouveau:windshear']
const AIRAIN_MACHINES = ['cataclysm:the_harbinger', 'cataclysm:the_prowler', 'cataclysm:the_watcher', 'cataclysm:netherite_monstrosity',
  'cataclysm:ender_golem', 'cataclysm:ender_guardian', 'mowziesmobs:ferrous_wroughtnaut',
  'minecraft:skeleton', 'minecraft:stray', 'minecraft:wither_skeleton', 'minecraft:creeper', 'minecraft:spider', 'minecraft:cave_spider']

function airainEstMachine(type) {
  // les automates de Dwarven Automatons, quel que soit leur identifiant exact
  return AIRAIN_MACHINES.indexOf(type) >= 0 || type.indexOf('dwarven') >= 0
}

// event.cancel() arrête aussitôt le script : on ne l'appelle qu'après avoir tout fait
function airainDiapason(event) {
  if (String(event.hand) !== 'MAIN_HAND') return false
  const player = event.player, block = event.block, level = event.level
  if (String(player.mainHandItem.id) !== 'kubejs:diapason_echo') return false
  if (String(level.getBlock(block.x, block.y - 1, block.z).id) !== 'minecraft:reinforced_deepslate') {
    player.setStatusMessage(Text.translate('airain.boss.pas_ici').lightPurple()); return true
  }
  const dim = String(level.dimension)
  const x = block.x + 0.5, y = block.y + 2, z = block.z + 0.5
  const ici = 'execute in ' + dim + ' positioned ' + x + ' ' + y + ' ' + z + ' run '
  // le Cœur éteint est posé sur le résonateur : le diapason sert au choix final (géré par le mod), pas au boss
  if (event.server.runCommandSilent(ici + 'execute if entity @e[tag=airain_coeur_pose,distance=..3]') > 0) return false
  // un seul Chœur à la fois autour du résonateur
  if (event.server.runCommandSilent(ici + 'execute if entity @e[tag=airain_choeur,distance=..96]') > 0) {
    player.setStatusMessage(Text.translate('airain.boss.deja').lightPurple()); return true
  }
  if (!player.isCreative()) player.mainHandItem.shrink(1)
  event.server.runCommandSilent(ici + 'summon ' + AIRAIN_CHOEUR + ' ~ ~ ~ {Tags:["airain_choeur"],PersistenceRequired:1b,CustomName:\'{"translate":"airain.boss.choeur","color":"light_purple"}\'}')
  event.server.runCommandSilent(ici + 'attribute @e[tag=airain_choeur,limit=1,sort=nearest] minecraft:generic.max_health base set ' + AIRAIN_CHOEUR_VIE)
  event.server.runCommandSilent(ici + 'data merge entity @e[tag=airain_choeur,limit=1,sort=nearest] {Health:' + AIRAIN_CHOEUR_VIE + 'f}')
  event.server.runCommandSilent(ici + 'playsound minecraft:block.amethyst_block.resonate hostile @a ~ ~ ~ 4 0.5')
  event.server.runCommandSilent(ici + 'particle minecraft:soul ~ ~ ~ 4 3 4 0.02 300')
  event.server.runCommandSilent(ici + 'tellraw @a[distance=..64] {"translate":"airain.boss.reveil","color":"light_purple","italic":true}')
  return true
}
BlockEvents.rightClicked('minecraft:lodestone', event => { if (airainDiapason(event)) event.cancel() })

EntityEvents.death(event => {
  const e = event.entity
  if (!e.tags || !e.tags.contains('airain_choeur')) return
  const dim = String(e.level.dimension)
  const ici = 'execute in ' + dim + ' positioned ' + e.x + ' ' + e.y + ' ' + e.z + ' run '
  event.server.runCommandSilent(ici + 'give @a[distance=..64] kubejs:echo_primordial ' + AIRAIN_ECHO_PAR_JOUEUR)
  event.server.runCommandSilent(ici + 'tellraw @a[distance=..64] {"translate":"airain.boss.libere","color":"light_purple","italic":true}')
  event.server.runCommandSilent(ici + 'particle minecraft:soul ~ ~1 ~ 5 4 5 0.05 500')
  event.server.runCommandSilent(ici + 'playsound minecraft:block.amethyst_block.chime hostile @a ~ ~ ~ 4 0.6')
})

// « Les machines ne sentent pas l'Écho » : +50 % de dégâts de sorts contre l'Empire
EntityEvents.beforeHurt(event => {
  const type = String(event.entity.type)
  if (!airainEstMachine(type)) return
  let dmg = ''
  try { dmg = String(event.source.typeHolder().unwrapKey().get().location()) } catch (err) { return }
  if (AIRAIN_DEGATS_ECHO.indexOf(dmg) >= 0) event.setDamage(event.damage * 1.5)
})

// Le Wither, comme le Chœur : un Cœur du Gardien des enfers pour chaque joueur à 64 blocs (au moins un, au sol, s'il n'y a personne).
EntityEvents.death('minecraft:wither', event => {
  const e = event.entity
  const ici = 'execute in ' + String(e.level.dimension) + ' positioned ' + e.x + ' ' + e.y + ' ' + e.z + ' run '
  const n = event.server.runCommandSilent(ici + 'give @a[distance=..64] minecraft:nether_star 1')
  if (n <= 0) event.server.runCommandSilent(ici + 'summon minecraft:item ~ ~1 ~ {Item:{id:"minecraft:nether_star",count:1}}')
})

// Le gardien du Vide (citadelle de l'End) : Morgana l'a éveillé avec le premier Cœur, qu'elle avait volé.
// La première fois qu'il tombe dans la partie, il laisse le Cœur brisé ; ensuite, plus jamais (il n'en existe qu'un).
EntityEvents.death('cataclysm:ender_guardian', event => {
  const data = event.server.persistentData
  if (data.getBoolean('airain_coeur_brise')) return
  data.putBoolean('airain_coeur_brise', true)
  const e = event.entity
  const ici = 'execute in ' + String(e.level.dimension) + ' positioned ' + e.x + ' ' + (e.y + 0.5) + ' ' + e.z + ' run '
  event.server.runCommandSilent(ici + 'summon minecraft:item ~ ~ ~ {Item:{id:"kubejs:coeur_brise",count:1},Invulnerable:1b,Glowing:1b,Age:-32768s}')
  event.server.runCommandSilent(ici + 'playsound minecraft:block.anvil.land hostile @a[distance=..64] ~ ~ ~ 1 0.5')
})
