# Génère les données des blocs d'airain et du haut-fourneau : blockstates, modèles, objets, butins, tags,
# data maps (patine, cire), recettes et noms. Modèles copiés de leurs équivalents « cuivre » de Minecraft.
import json, os, copy
R='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=R+'assets/airain/'; Dd=R+'data/'
MC='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/'
MD='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-data/data/minecraft/'
def w(chemin, d):
    os.makedirs(os.path.dirname(chemin), exist_ok=True); json.dump(d, open(chemin,'w'), indent=1, ensure_ascii=False)
def lire(chemin): return json.load(open(chemin))
PRE=['','exposed_','weathered_','oxidized_']
FAM=['airain_block','cut_airain','riveted_airain','chiseled_airain','airain_pillar','airain_stairs','cut_airain_stairs','airain_slab','cut_airain_slab',
     'airain_grate','airain_bars','airain_door','airain_trapdoor','airain_chain','airain_lantern']
def tex(stade, nom): return f'airain:block/{PRE[stade]}{nom}'
def remplacer(obj, table):
    s=json.dumps(obj)
    for a,b in table: s=s.replace(a,b)
    return json.loads(s)
TOUS=[]          # (id, famille, stade, ciré)
for f in FAM:
    for s in range(4):
        for c in (0,1): TOUS.append(((('waxed_' if c else '')+PRE[s]+f), f, s, c))
CUTOUT={'airain_grate','airain_bars','airain_door','airain_trapdoor','airain_chain','airain_lantern'}
# ------------------------------------------------------------------ modèles (un jeu par stade ; le ciré réutilise ceux du stade)
for s in range(4):
    p=PRE[s]
    for n in ('airain_block','cut_airain','riveted_airain','chiseled_airain','airain_grate'):
        d={"parent":"minecraft:block/cube_all","textures":{"all":tex(s,n)}}
        if n in CUTOUT: d["render_type"]="minecraft:cutout"
        w(AS+f'models/block/{p}{n}.json', d)
    w(AS+f'models/block/{p}airain_pillar.json',{"parent":"minecraft:block/cube_column","textures":{"end":tex(s,'airain_pillar_top'),"side":tex(s,'airain_pillar')}})
    w(AS+f'models/block/{p}airain_pillar_horizontal.json',{"parent":"minecraft:block/cube_column_horizontal","textures":{"end":tex(s,'airain_pillar_top'),"side":tex(s,'airain_pillar')}})
    for fam,base in (('airain_stairs','airain_block'),('cut_airain_stairs','cut_airain')):
        t={"bottom":tex(s,base),"side":tex(s,base),"top":tex(s,base)}
        for suf,par in (('','stairs'),('_inner','inner_stairs'),('_outer','outer_stairs')): w(AS+f'models/block/{p}{fam}{suf}.json',{"parent":"minecraft:block/"+par,"textures":t})
    for fam,base in (('airain_slab','airain_block'),('cut_airain_slab','cut_airain')):
        t={"bottom":tex(s,base),"side":tex(s,base),"top":tex(s,base)}
        w(AS+f'models/block/{p}{fam}.json',{"parent":"minecraft:block/slab","textures":t}); w(AS+f'models/block/{p}{fam}_top.json',{"parent":"minecraft:block/slab_top","textures":t})
    # barreaux : les six modèles des barreaux de fer, texture changée
    for m in ('iron_bars_cap','iron_bars_cap_alt','iron_bars_post','iron_bars_post_ends','iron_bars_side','iron_bars_side_alt'):
        d=remplacer(lire(MC+f'models/block/{m}.json'),[('"block/iron_bars"','"'+tex(s,'airain_bars')+'"'),('"minecraft:block/iron_bars"','"'+tex(s,'airain_bars')+'"')])
        d["render_type"]="minecraft:cutout_mipped"
        w(AS+f'models/block/{p}{m.replace("iron_bars","airain_bars")}.json',d)
    for m in ('door_bottom_left','door_bottom_left_open','door_bottom_right','door_bottom_right_open','door_top_left','door_top_left_open','door_top_right','door_top_right_open'):
        w(AS+f'models/block/{p}airain_{m}.json',{"parent":"minecraft:block/"+m,"render_type":"minecraft:cutout","textures":{"bottom":tex(s,'airain_door_bottom'),"top":tex(s,'airain_door_top')}})
    for m in ('bottom','open','top'):
        w(AS+f'models/block/{p}airain_trapdoor_{m}.json',{"parent":f"minecraft:block/template_orientable_trapdoor_{m}","render_type":"minecraft:cutout","textures":{"texture":tex(s,'airain_trapdoor')}})
    d=remplacer(lire(MC+'models/block/chain.json'),[('"block/chain"','"'+tex(s,'airain_chain')+'"')]); d["render_type"]="minecraft:cutout_mipped"
    w(AS+f'models/block/{p}airain_chain.json',d)
    w(AS+f'models/block/{p}airain_lantern.json',{"parent":"minecraft:block/template_lantern","render_type":"minecraft:cutout","textures":{"lantern":tex(s,'airain_lantern')}})
    w(AS+f'models/block/{p}airain_lantern_hanging.json',{"parent":"minecraft:block/template_hanging_lantern","render_type":"minecraft:cutout","textures":{"lantern":tex(s,'airain_lantern')}})
# la chaîne utilise sa propre texture de bloc (copiée de la vanilla recolorée) : on la crée depuis la chaîne vanilla
# ------------------------------------------------------------------ blockstates
def bs_copie(vanilla, table): return remplacer(lire(MC+f'blockstates/{vanilla}.json'), table)
for (i,f,s,c) in TOUS:
    p=PRE[s]; m=lambda n: f'airain:block/{p}{n}'
    if f in ('airain_block','cut_airain','riveted_airain','chiseled_airain','airain_grate'):
        d={"variants":{"":{"model":m(f)}}}
    elif f=='airain_pillar':
        d={"variants":{"axis=x":{"model":m('airain_pillar_horizontal'),"x":90,"y":90},"axis=y":{"model":m('airain_pillar')},"axis=z":{"model":m('airain_pillar_horizontal'),"x":90}}}
    elif f.endswith('_stairs'):
        d=bs_copie('cut_copper_stairs',[('minecraft:block/cut_copper_stairs',m(f))])
    elif f.endswith('_slab'):
        base='airain_block' if f=='airain_slab' else 'cut_airain'
        d=bs_copie('cut_copper_slab',[('minecraft:block/cut_copper_slab_top',m(f+'_top')),('minecraft:block/cut_copper_slab',m(f)),('minecraft:block/cut_copper',m(base))])
    elif f=='airain_bars':
        d=bs_copie('iron_bars',[('minecraft:block/iron_bars',m('airain_bars'))])
    elif f=='airain_door':
        d=bs_copie('copper_door',[('minecraft:block/copper_door',m('airain_door'))])
    elif f=='airain_trapdoor':
        d=bs_copie('copper_trapdoor',[('minecraft:block/copper_trapdoor',m('airain_trapdoor'))])
    elif f=='airain_chain':
        d=bs_copie('chain',[('minecraft:block/chain',m('airain_chain'))])
    elif f=='airain_lantern':
        d=bs_copie('lantern',[('minecraft:block/lantern_hanging',m('airain_lantern_hanging')),('minecraft:block/lantern',m('airain_lantern'))])
    w(AS+f'blockstates/{i}.json',d)
    # objet
    if f in ('airain_door','airain_bars','airain_chain','airain_lantern'):
        couche={'airain_door':f'airain:item/{p}airain_door','airain_bars':tex(s,'airain_bars'),'airain_chain':f'airain:item/{p}airain_chain','airain_lantern':f'airain:item/{p}airain_lantern'}[f]
        w(AS+f'models/item/{i}.json',{"parent":"minecraft:item/generated","textures":{"layer0":couche}})
    elif f=='airain_trapdoor': w(AS+f'models/item/{i}.json',{"parent":m('airain_trapdoor_bottom')})
    else: w(AS+f'models/item/{i}.json',{"parent":m(f)})
    # butin
    if f=='airain_door': lt=remplacer(lire(MD+'loot_table/blocks/copper_door.json'),[('minecraft:copper_door','airain:'+i)])
    elif f.endswith('_slab'): lt=remplacer(lire(MD+'loot_table/blocks/cut_copper_slab.json'),[('minecraft:cut_copper_slab','airain:'+i)])
    else: lt={"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]}
    lt.pop('random_sequence',None)
    w(Dd+f'airain/loot_table/blocks/{i}.json',lt)
# textures de chaîne côté bloc : la vanilla recolorée (même méthode que l'objet)
from PIL import Image
import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
exec(open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_luxe.py').read().split("STADES=['','exposed_'")[0])
MC='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/'
for s in range(4):
    im=Image.open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/block/chain.png').convert('RGBA'); px=im.load(); out=im.copy(); q=out.load()
    vals=sorted({sum(px[x,y][:3]) for y in range(im.height) for x in range(im.width) if px[x,y][3]>0})
    for y in range(im.height):
        for x in range(im.width):
            if px[x,y][3]>0: q[x,y]=teinte(1+int(vals.index(sum(px[x,y][:3]))/max(1,len(vals)-1)*4.99),[0.0,0.28,0.58,0.92][s])+(px[x,y][3],)
    out.save(AS+f'textures/block/{PRE[s]}airain_chain.png')
# ------------------------------------------------------------------ data maps : patine et cire
ox={}; wx={}
for f in FAM:
    for s in range(4):
        if s<3: ox['airain:'+PRE[s]+f]={"next_oxidation_stage":'airain:'+PRE[s+1]+f}
        wx['airain:'+PRE[s]+f]={"waxed":'airain:waxed_'+PRE[s]+f}
w(Dd+'neoforge/data_maps/block/oxidizables.json',{"values":ox})
w(Dd+'neoforge/data_maps/block/waxables.json',{"values":wx})
# ------------------------------------------------------------------ tags
def tag(chemin, valeurs):
    c=Dd+chemin
    old=lire(c)['values'] if os.path.exists(c) else []
    w(c,{"replace":False,"values":list(dict.fromkeys(old+valeurs))})
ids=['airain:'+i for (i,_,_,_) in TOUS]
FOUR=['airain:fire_bricks','airain:blast_furnace_tuyere','airain:blast_furnace_hopper','airain:blast_furnace_taphole']
tag('minecraft/tags/block/mineable/pickaxe.json', ids+FOUR)
tag('minecraft/tags/block/needs_stone_tool.json', ids)
tag('minecraft/tags/block/doors.json',[x for x in ids if 'door' in x and 'trap' not in x]); tag('minecraft/tags/item/doors.json',[x for x in ids if 'door' in x and 'trap' not in x])
tag('minecraft/tags/block/trapdoors.json',[x for x in ids if 'trapdoor' in x]); tag('minecraft/tags/item/trapdoors.json',[x for x in ids if 'trapdoor' in x])
tag('minecraft/tags/block/stairs.json',[x for x in ids if 'stairs' in x]); tag('minecraft/tags/item/stairs.json',[x for x in ids if 'stairs' in x])
tag('minecraft/tags/block/slabs.json',[x for x in ids if 'slab' in x]); tag('minecraft/tags/item/slabs.json',[x for x in ids if 'slab' in x])
tag('airain/tags/block/airain_grates.json',[x for x in ids if 'grate' in x])
tag('c/tags/item/ingots/airain.json',['airain:airain_ingot']); tag('c/tags/item/ingots.json',['airain:airain_ingot'])
tag('c/tags/item/nuggets/airain.json',['airain:airain_nugget']); tag('c/tags/item/plates/airain.json',['airain:airain_sheet'])
tag('c/tags/block/storage_blocks/airain.json',['airain:airain_block']); tag('c/tags/item/storage_blocks/airain.json',['airain:airain_block'])
tag('c/tags/fluid/molten_airain.json',['airain:molten_airain','airain:flowing_molten_airain'])
# ------------------------------------------------------------------ haut-fourneau : modèles et blockstates
F=lambda n: 'airain:block/'+n
def cube(nom, t, render=None, extra=None):
    d={"parent":"minecraft:block/block","textures":dict(t,particle=t.get('north',t.get('all'))),"elements":[{"from":[0,0,0],"to":[16,16,16],"faces":{k:{"texture":"#"+(k if k in t else 'all'),"cullface":k} for k in ("north","south","east","west","up","down")}}]}
    if extra: d["elements"]+=extra
    if render: d["render_type"]=render
    w(AS+f'models/block/{nom}.json',d)
B='fire_bricks'
PARTS={'none':('fire_bricks','fire_bricks','fire_bricks'),'body':('fire_bricks','fire_bricks','fire_bricks'),
       'base':('blast_furnace_plinth','fire_bricks','fire_bricks'),'crown':('blast_furnace_hopper_side','blast_furnace_top_sooty','fire_bricks')}
COIN={'base':'blast_furnace_plinth_corner','body':'fire_bricks_corner','crown':'blast_furnace_hopper_side_corner'}
for part,(cote,haut,bas) in PARTS.items():
    cube(f'fire_bricks_{part}',{"all":F(B),"north":F(cote),"south":F(cote),"east":F(cote),"west":F(cote),"up":F(haut),"down":F(bas)})
for part,coin in COIN.items():
    cote,haut,bas=PARTS[part]
    # coin dessiné pour le nord-ouest : cornière sur l'arête ouest de la face nord et l'arête nord de la face ouest
    d={"parent":"minecraft:block/block","textures":{"particle":F(B),"coin":F(coin),"cote":F(cote),"haut":F(haut),"bas":F(bas)},
       "elements":[{"from":[0,0,0],"to":[16,16,16],"faces":{"north":{"texture":"#coin","uv":[0,0,16,16],"cullface":"north"},"west":{"texture":"#coin","uv":[16,0,0,16],"cullface":"west"},
                    "south":{"texture":"#cote","cullface":"south"},"east":{"texture":"#cote","cullface":"east"},"up":{"texture":"#haut","cullface":"up"},"down":{"texture":"#bas","cullface":"down"}}}]}
    w(AS+f'models/block/fire_bricks_{part}_corner.json',d)
cube('fire_bricks_emblem',{"all":F(B),"north":F('blast_furnace_emblem')})
ROT={'north':0,'east':90,'south':180,'west':270}
v={}
for part in ('none','base','base_corner','body','body_corner','crown','crown_corner','emblem'):
    for fa,r in ROT.items():
        e={"model":F('fire_bricks_'+part)}
        if part.endswith('corner') or part=='emblem':
            if r: e["y"]=r
        v[f'facing={fa},part={part}']=e
w(AS+'blockstates/fire_bricks.json',{"variants":v})
w(AS+'models/item/fire_bricks.json',{"parent":F('fire_bricks_none')})
AIR=F('blast_furnace_airain')
def b(fr,to,t="#airain",faces=("north","south","east","west","up","down"),lum=False):
    f={k:{"texture":t}|({"neoforge_data":{"block_light":15,"sky_light":15}} if lum else {}) for k in faces}
    return {"from":fr,"to":to,"faces":f}|({"shade":False} if lum else {})
# tuyère : buse d'airain cerclée, vers le nord
cube('blast_furnace_tuyere',{"all":F(B),"north":F('blast_furnace_tuyere'),"airain":AIR},
     extra=[b([5,5,-3],[11,11,0],faces=("north","east","west","up","down")),b([4,4,-1],[12,12,0],faces=("east","west","up","down"))])
w(AS+'blockstates/blast_furnace_tuyere.json',{"variants":{f'facing={fa}':({"model":F('blast_furnace_tuyere')}|({"y":r} if r else {})) for fa,r in ROT.items()}})
w(AS+'models/item/blast_furnace_tuyere.json',{"parent":F('blast_furnace_tuyere')})
# trou de coulée : linteau et rigole en saillie ; allumé, le métal coule
for lit in (False,True):
    ex=[b([1,9,-2],[15,11,0],faces=("north","east","west","up","down")),b([5,2,-6],[11,3,0],faces=("north","east","west","up","down")),
        b([5,3,-6],[6,5,0],faces=("north","east","west","up")),b([10,3,-6],[11,5,0],faces=("north","east","west","up"))]
    if lit: ex.append(b([6,3,-6],[10,3.6,0],"#metal",faces=("up","north"),lum=True))
    t={"all":F(B),"north":F('blast_furnace_taphole'+('_lit' if lit else '')),"airain":AIR,"metal":F('molten_airain_still')}
    cube('blast_furnace_taphole'+('_lit' if lit else ''),t,extra=ex)
    # face avant lumineuse quand il coule
    if lit:
        m=lire(AS+'models/block/blast_furnace_taphole_lit.json'); m["elements"][0]["faces"]["north"]["neoforge_data"]={"block_light":15,"sky_light":15}; w(AS+'models/block/blast_furnace_taphole_lit.json',m)
w(AS+'blockstates/blast_furnace_taphole.json',{"variants":{f'facing={fa},lit={str(l).lower()}':({"model":F('blast_furnace_taphole'+('_lit' if l else ''))}|({"y":r} if r else {})) for fa,r in ROT.items() for l in (False,True)}})
w(AS+'models/item/blast_furnace_taphole.json',{"parent":F('blast_furnace_taphole')})
# gueulard : entonnoir riveté qui dépasse du sommet
for lit in (False,True):
    ex=[b([1,16,1],[15,22,3]),b([1,16,13],[15,22,15]),b([1,16,3],[3,22,13]),b([13,16,3],[15,22,13]),
        b([0,22,0],[16,23,2]),b([0,22,14],[16,23,16]),b([0,22,2],[2,23,14]),b([14,22,2],[16,23,14])]
    t={"all":F('blast_furnace_hopper_side'),"up":F('blast_furnace_hopper_top'+('_lit' if lit else '')),"down":F(B),"airain":AIR,"metal":F('molten_airain_still')}
    if lit: ex.append(b([3,16,3],[13,17.5,13],"#metal",faces=("up",),lum=True))
    cube('blast_furnace_hopper'+('_lit' if lit else ''),t,render="minecraft:cutout",extra=ex)
    if lit:
        m=lire(AS+'models/block/blast_furnace_hopper_lit.json'); m["elements"][0]["faces"]["up"]["neoforge_data"]={"block_light":15,"sky_light":15}; w(AS+'models/block/blast_furnace_hopper_lit.json',m)
w(AS+'blockstates/blast_furnace_hopper.json',{"variants":{"lit=false":{"model":F('blast_furnace_hopper')},"lit=true":{"model":F('blast_furnace_hopper_lit')}}})
w(AS+'models/item/blast_furnace_hopper.json',{"parent":F('blast_furnace_hopper')})
for n in FOUR:
    i=n.split(':')[1]
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":n}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
# airain en fusion : bloc liquide et objets
w(AS+'blockstates/molten_airain.json',{"variants":{"":{"model":F('molten_airain')}}})
w(AS+'models/block/molten_airain.json',{"textures":{"particle":F('molten_airain_still')}})
for it in ('airain_ingot','airain_nugget','airain_sheet','airain_gear','incomplete_airain_gear','slag','fire_brick','molten_airain_bucket'):
    w(AS+f'models/item/{it}.json',{"parent":"minecraft:item/generated","textures":{"layer0":'airain:item/'+it}})
print('ressources ok', len(TOUS), 'blocs patinables')
