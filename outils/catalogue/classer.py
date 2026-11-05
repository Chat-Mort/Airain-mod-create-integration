import json, re
S='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad'
items = [i if ':' in i else 'minecraft:' + i for i in json.load(open(S + '/mcmeta-reg/item/data.json'))]
EXCLU_MOTS = ['_sword', '_pickaxe', '_axe', '_shovel', '_hoe', '_helmet', '_chestplate', '_leggings', '_boots', 'horse_armor', 'wolf_armor',
 'spawn_egg', 'command_block', 'structure_', 'jigsaw', 'barrier', 'debug_stick', 'knowledge_book', 'light', 'bedrock', 'end_portal_frame',
 'spawner', 'trial_spawner', 'vault', 'music_disc', 'disc_fragment', 'smithing_template', 'pottery_sherd', 'banner_pattern', 'potion', 'tipped_arrow',
 'enchanted_book', 'written_book', 'writable_book', 'filled_map', 'map', 'bundle', 'shulker_box', 'minecart', '_boat', '_raft', 'elytra', 'trident',
 'totem', 'nether_star', 'dragon_egg', 'dragon_head', 'dragon_breath', 'heavy_core', 'trial_key', 'enchanted_golden_apple', 'end_crystal',
 'beacon', 'conduit', 'mace', 'bow', 'crossbow', 'shield', 'fishing_rod', 'carrot_on_a_stick', 'warped_fungus_on_a_stick', 'shears', 'flint_and_steel',
 'spyglass', 'brush', 'compass', 'clock', 'lead', 'name_tag', 'saddle', 'firework', 'experience_bottle', 'ominous', 'goat_horn', 'echo_shard',
 'recovery_compass', 'armor_stand', 'item_frame', 'painting', 'bucket', 'egg', 'player_head', 'skull', 'wither_rose', 'air', 'petrified_oak_slab',
 'budding_amethyst', 'reinforced_deepslate', 'frogspawn', 'turtle_scute', 'armadillo_scute', 'sniffer', 'suspicious_', 'infested_', 'chorus_flower',
 'enchanting_table', 'anvil', 'respawn_anchor', 'lodestone', 'crafter', 'jukebox', 'note_block', 'piston', 'observer', 'dispenser', 'dropper',
 'hopper', 'repeater', 'comparator', 'daylight', 'tnt', 'rail', 'redstone_torch', 'lever', 'tripwire', 'target', 'sculk_sensor', 'sculk_shrieker',
 'sculk_catalyst', 'calibrated', 'furnace', 'smoker', 'blast_furnace', 'brewing_stand', 'cauldron', 'cartography', 'fletching', 'smithing_table',
 'grindstone', 'stonecutter', 'loom', 'barrel', 'chest', 'bed', 'campfire', 'lectern', 'bell', 'ender_eye', 'end_rod', 'heart_of_the_sea',
 'nautilus_shell', 'shulker_shell', 'ghast_tear', 'phantom_membrane', 'rabbit_foot', 'netherite_ingot', 'netherite_block', 'ancient_debris',
 'netherite_scrap', 'golden_apple', 'glistering', 'golden_carrot', 'stew', 'soup', 'cake', 'pie', 'cookie', 'bread', 'cooked_', 'baked_potato',
 'dried_kelp', 'honey_bottle', 'milk', 'ominous', 'breeze_rod', 'wind_charge', 'trial', 'crying_obsidian', 'sponge', 'mob_', 'creaking']
DERIVES = ['_stairs', '_slab', '_wall', '_fence', '_fence_gate', '_door', '_trapdoor', '_button', '_pressure_plate', '_sign', '_pane',
 '_carpet', 'exposed_', 'weathered_', 'oxidized_', 'waxed_', 'polished_', 'chiseled_', 'cut_', 'smooth_', 'stripped_', 'torch', 'lantern', 'chain',
 'ladder', 'scaffolding', 'arrow', 'book', 'composter', 'crafting_table', '_head', 'fire_charge', 'banner', 'candle', 'glass_bottle', 'redstone_lamp', 'farmland', 'dirt_path', 'beehive', 'bee_nest', 'stick', 'paper', 'iron_bars', 'flower_pot', 'decorated_pot', 'armor', 'grate', 'bulb', 'heavy_weighted', 'pointed_dripstone', 'brick_', '_block_']
def exclu(i):
    n = i.split(':')[1]
    return any(m in n for m in EXCLU_MOTS) or any(m in n for m in DERIVES)
# paliers : (quantité, prix en éperons)
P = {"commun": (64, 8), "courant": (64, 16), "travaille": (64, 32), "minerai": (16, 32), "precieux": (16, 64), "rare": (4, 64), "tres_rare": (1, 128)}
def palier(n):
    if re.search(r'diamond|emerald', n): return 'rare' if 'ore' in n or n in ('diamond', 'emerald') else 'tres_rare'
    if re.search(r'gold|amethyst|prismarine|blaze|slime|magma_cream|ender_pearl|glowstone|obsidian|quartz', n): return 'precieux'
    if re.search(r'iron|copper|coal|redstone|lapis|raw_', n): return 'minerai'
    if re.search(r'(^|_)(dirt|grass_block|stone|cobblestone|sand|gravel|netherrack|deepslate|cobbled_deepslate|andesite|diorite|granite|tuff|calcite|clay|mud|end_stone|basalt|blackstone|snow|ice)$', n) or n in ('dirt', 'sand', 'gravel'):
        return 'commun'
    if re.search(r'_log$|_wood$|_stem$|_hyphae$|planks|sapling|leaves|seeds|wheat|carrot|potato|beetroot|melon|pumpkin|sugar_cane|bamboo|cactus|kelp|vine|flower|tulip|poppy|dandelion|orchid|allium|azure|daisy|cornflower|lily|rose|peony|lilac|sunflower|fern|grass|bush|mushroom|moss|string|bone|feather|leather|rotten|spider_eye|gunpowder|ink_sac|dye|wool|carpet|terracotta|glass|concrete|brick', n):
        return 'courant'
    return 'travaille'
def categorie(n):
    for c, r in (("Minerais et métaux", r'ore|ingot|nugget|raw_|diamond|emerald|lapis|redstone|coal|quartz|amethyst|copper|iron|gold'),
                 ("Bois et plantes", r'_log|_wood|planks|stem|hyphae|sapling|leaves|seeds|wheat|carrot|potato|beetroot|melon|pumpkin|sugar_cane|bamboo|cactus|kelp|vine|flower|tulip|poppy|dandelion|orchid|allium|azure|daisy|cornflower|lily|rose|peony|lilac|sunflower|fern|grass|bush|mushroom|moss|wart|fungus|roots|cocoa|berries|apple|petals|dripleaf|azalea|spore|lichen|hanging|propagule|pitcher|torchflower'),
                 ("Butin de créatures", r'string|bone|feather|leather|rotten|spider_eye|gunpowder|ink_sac|slime|blaze|ender_pearl|magma_cream|honeycomb|rabbit_hide|prismarine|scute|beef|porkchop|chicken|mutton|rabbit|cod|salmon|tropical|pufferfish'),
                 ("Couleurs et décoration", r'dye|wool|carpet|terracotta|glass|concrete|candle|banner|glazed'),
                 ("Pierres et terrains", r'.*')):
        if re.search(r, n): return c
items_ok = []
for i in sorted(items):
    if exclu(i): continue
    n = i.split(':')[1]
    t = palier(n); q, p = P[t]
    items_ok.append({"id": i, "cat": categorie(n), "palier": t, "qte": q, "prix": p})
# Create : matières premières et pierres décoratives
for n in ['raw_zinc', 'zinc_ingot', 'zinc_nugget', 'zinc_ore', 'deepslate_zinc_ore']:
    t = 'minerai'; items_ok.append({"id": "create:" + n, "cat": "Minerais et métaux", "palier": t, "qte": P[t][0], "prix": P[t][1]})
for n in ['limestone', 'scoria', 'scorchia', 'ochrum', 'veridium', 'crimsite', 'asurine', 'cut_granite']:
    items_ok.append({"id": "create:" + n, "cat": "Pierres et terrains", "palier": "commun", "qte": 64, "prix": 8})
json.dump({"paliers": P, "items": items_ok}, open(S + '/catalogue/catalogue.json', 'w'), ensure_ascii=False, indent=0)
from collections import Counter
print(len(items_ok), Counter(x['cat'] for x in items_ok), Counter(x['palier'] for x in items_ok))
