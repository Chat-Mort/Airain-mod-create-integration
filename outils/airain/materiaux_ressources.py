# Ressources 1.57 : marbres veinés d'or, ardoise, carrelage (textures, modèles, blockstates, butin, étiquettes, recettes, noms).
import json, os, shutil
SCR='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/'
MOD='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=MOD+'assets/airain/'; DA=MOD+'data/'
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
M=SCR+'materiaux/'
# ---------------------------------------------------------------- textures (noms anglais)
TX={}
for t,fr in (('white','blanc'),('black','noir')):
    for v in range(6): TX[f'{t}_marble_{v}']=f'marbre_{fr}_{v}'
    TX[f'polished_{t}_marble']=f'marbre_{fr}_dalles'; TX[f'{t}_marble_bricks']=f'marbre_{fr}_briques'
    TX[f'{t}_marble_pillar']=f'marbre_{fr}_colonne'; TX[f'chiseled_{t}_marble']=f'marbre_{fr}_cisele'
TX['slate']='ardoise_polie'; TX['slate_shingles']='ardoise_tuiles'; TX['marble_tiles']='carrelage'
LIAM={l.strip() for l in open('/home/claude/airain-mod-create-integration/outils/textures_liam.txt') if l.strip() and not l.startswith('#')}   # retouches de Liam : jamais écrasées
for a,b in TX.items():
    if f'block/{a}.png' not in LIAM: shutil.copyfile(M+b+'.png',AS+f'textures/block/{a}.png')
def B(n): return f'airain:block/{n}'
def modele(nom,parent,tex): w(AS+f'models/block/{nom}.json',{"parent":parent,"textures":tex})
def item(nom,modele_=None): w(AS+f'models/item/{nom}.json',{"parent":B(modele_ or nom)})
def butin(nom,dalle=False):
    e={"type":"minecraft:item","name":"airain:"+nom}
    if dalle: e["functions"]=[{"function":"minecraft:set_count","count":2,"conditions":[{"condition":"minecraft:block_state_property","block":"airain:"+nom,"properties":{"type":"double"}}]}]
    w(DA+f'airain/loot_table/blocks/{nom}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[e],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
TOUS=[]; ESC=[]; DAL=[]; MUR=[]
def plein(nom,tex):
    modele(nom,"minecraft:block/cube_all",{"all":B(tex)}); w(AS+f'blockstates/{nom}.json',{"variants":{"":{"model":B(nom)}}}); item(nom); butin(nom); TOUS.append(nom)
def escaliers(nom,tex):
    t={"bottom":B(tex),"top":B(tex),"side":B(tex)}
    modele(nom,"minecraft:block/stairs",t); modele(nom+'_inner',"minecraft:block/inner_stairs",t); modele(nom+'_outer',"minecraft:block/outer_stairs",t)
    v=json.loads(open(SCR+'mcmeta-assets/assets/minecraft/blockstates/stone_brick_stairs.json').read().replace('minecraft:block/stone_brick_stairs',B(nom)))['variants']
    w(AS+f'blockstates/{nom}.json',{"variants":v}); item(nom); butin(nom); TOUS.append(nom); ESC.append(nom)
def dalle(nom,tex,double):
    t={"bottom":B(tex),"top":B(tex),"side":B(tex)}
    modele(nom,"minecraft:block/slab",t); modele(nom+'_top',"minecraft:block/slab_top",t)
    w(AS+f'blockstates/{nom}.json',{"variants":{"type=bottom":{"model":B(nom)},"type=top":{"model":B(nom+'_top')},"type=double":{"model":B(double)}}})
    item(nom); butin(nom,True); TOUS.append(nom); DAL.append(nom)
def muret(nom,tex):
    modele(nom+'_post',"minecraft:block/template_wall_post",{"wall":B(tex)})
    modele(nom+'_side',"minecraft:block/template_wall_side",{"wall":B(tex)})
    modele(nom+'_side_tall',"minecraft:block/template_wall_side_tall",{"wall":B(tex)})
    modele(nom+'_inventory',"minecraft:block/wall_inventory",{"wall":B(tex)})
    parts=json.loads(open(SCR+'mcmeta-assets/assets/minecraft/blockstates/stone_brick_wall.json').read().replace('minecraft:block/stone_brick_wall',B(nom)))['multipart']
    w(AS+f'blockstates/{nom}.json',{"multipart":parts}); item(nom,nom+'_inventory'); butin(nom); TOUS.append(nom); MUR.append(nom)
# ---------------------------------------------------------------- les blocs
for t in ('white','black'):
    # marbre brut : 6 textures tirées au hasard, et une rotation ; les 3 presque unies sortent deux fois plus souvent
    for v in range(6): modele(f'{t}_marble_{v}',"minecraft:block/cube_all",{"all":B(f'{t}_marble_{v}')})
    var=[]
    for v in range(6):
        for (x,y) in ((0,0),(90,0),(180,0),(270,0),(90,90),(270,90)):
            d={"model":B(f'{t}_marble_{v}'),"weight":1 if v<3 else 2}
            if x: d["x"]=x
            if y: d["y"]=y
            var.append(d)
    w(AS+f'blockstates/{t}_marble.json',{"variants":{"":var}}); item(f'{t}_marble',f'{t}_marble_0'); butin(f'{t}_marble'); TOUS.append(f'{t}_marble')
    escaliers(f'{t}_marble_stairs',f'{t}_marble_3'); dalle(f'{t}_marble_slab',f'{t}_marble_3',f'{t}_marble_3'); muret(f'{t}_marble_wall',f'{t}_marble_3')
    plein(f'polished_{t}_marble',f'polished_{t}_marble'); escaliers(f'polished_{t}_marble_stairs',f'polished_{t}_marble'); dalle(f'polished_{t}_marble_slab',f'polished_{t}_marble',f'polished_{t}_marble')
    plein(f'{t}_marble_bricks',f'{t}_marble_bricks'); escaliers(f'{t}_marble_brick_stairs',f'{t}_marble_bricks'); dalle(f'{t}_marble_brick_slab',f'{t}_marble_bricks',f'{t}_marble_bricks'); muret(f'{t}_marble_brick_wall',f'{t}_marble_bricks')
    plein(f'chiseled_{t}_marble',f'chiseled_{t}_marble')
    # colonne : cannelures sur les côtés, dalle polie aux extrémités
    p=f'{t}_marble_pillar'
    modele(p,"minecraft:block/cube_column",{"side":B(p),"end":B(f'polished_{t}_marble')})
    modele(p+'_horizontal',"minecraft:block/cube_column_horizontal",{"side":B(p),"end":B(f'polished_{t}_marble')})
    w(AS+f'blockstates/{p}.json',{"variants":{"axis=y":{"model":B(p)},"axis=z":{"model":B(p+'_horizontal'),"x":90},"axis=x":{"model":B(p+'_horizontal'),"x":90,"y":90}}})
    item(p); butin(p); TOUS.append(p)
plein('slate','slate'); escaliers('slate_stairs','slate'); dalle('slate_slab','slate','slate'); muret('slate_wall','slate')
plein('slate_shingles','slate_shingles'); escaliers('slate_shingle_stairs','slate_shingles'); dalle('slate_shingle_slab','slate_shingles','slate_shingles')
plein('marble_tiles','marble_tiles'); dalle('marble_tile_slab','marble_tiles','marble_tiles')
# ---------------------------------------------------------------- étiquettes (pioche, escaliers, dalles, murets)
def ajoute(chemin,vals):
    p=DA+chemin; d=json.load(open(p)) if os.path.exists(p) else {"replace":False,"values":[]}
    for v in vals:
        if v not in d["values"]: d["values"].append(v)
    w(p,d)
ajoute('minecraft/tags/block/mineable/pickaxe.json',['airain:'+n for n in TOUS])
ajoute('minecraft/tags/block/stairs.json',['airain:'+n for n in ESC]); ajoute('minecraft/tags/item/stairs.json',['airain:'+n for n in ESC])
ajoute('minecraft/tags/block/slabs.json',['airain:'+n for n in DAL]); ajoute('minecraft/tags/item/slabs.json',['airain:'+n for n in DAL])
ajoute('minecraft/tags/block/walls.json',['airain:'+n for n in MUR]); ajoute('minecraft/tags/item/walls.json',['airain:'+n for n in MUR])
# pierres qui deviennent du marbre
w(DA+'airain/tags/item/white_marble_stones.json',{"replace":False,"values":["minecraft:calcite","minecraft:diorite",{"id":"create:limestone","required":False}]})
w(DA+'airain/tags/item/black_marble_stones.json',{"replace":False,"values":["minecraft:blackstone","minecraft:cobbled_deepslate","minecraft:basalt"]})
# ---------------------------------------------------------------- recettes
R=DA+'airain/recipe/materiaux/'
for t in ('white','black'):
    w(R+f'{t}_marble_mixing.json',{"type":"create:mixing","ingredients":[{"tag":f"airain:{t}_marble_stones"}]*8+[{"item":"minecraft:gold_nugget"}],
                                   "results":[{"id":f"airain:{t}_marble","count":8}]})
w(R+'black_marble_gilded.json',{"type":"create:pressing","ingredients":[{"item":"minecraft:gilded_blackstone"}],"results":[{"id":"airain:black_marble"}]})
w(R+'slate_pressing.json',{"type":"create:pressing","ingredients":[{"item":"minecraft:cobbled_deepslate"}],"results":[{"id":"airain:slate"}]})
w(R+'marble_tiles.json',{"type":"minecraft:crafting_shaped","pattern":["WB","BW"],"key":{"W":{"item":"airain:white_marble"},"B":{"item":"airain:black_marble"}},
                         "result":{"id":"airain:marble_tiles","count":4},"category":"building"})
def taille(src,dst,n=1):
    w(R+f'{dst}_from_{src}_stonecutting.json',{"type":"minecraft:stonecutting","ingredient":{"item":"airain:"+src},"result":{"id":"airain:"+dst,"count":n}})
for t in ('white','black'):
    base=f'{t}_marble'
    for dst,n in ((f'polished_{t}_marble',1),(f'{t}_marble_bricks',1),(f'{t}_marble_pillar',1),(f'chiseled_{t}_marble',1),(f'{t}_marble_stairs',1),(f'{t}_marble_slab',2),(f'{t}_marble_wall',1),
                  (f'polished_{t}_marble_stairs',1),(f'polished_{t}_marble_slab',2),(f'{t}_marble_brick_stairs',1),(f'{t}_marble_brick_slab',2),(f'{t}_marble_brick_wall',1)):
        taille(base,dst,n)
    for src,dst,n in ((f'polished_{t}_marble',f'polished_{t}_marble_stairs',1),(f'polished_{t}_marble',f'polished_{t}_marble_slab',2),
                      (f'{t}_marble_bricks',f'{t}_marble_brick_stairs',1),(f'{t}_marble_bricks',f'{t}_marble_brick_slab',2),(f'{t}_marble_bricks',f'{t}_marble_brick_wall',1)):
        taille(src,dst,n)
for dst,n in (('slate_shingles',1),('slate_stairs',1),('slate_slab',2),('slate_wall',1),('slate_shingle_stairs',1),('slate_shingle_slab',2)): taille('slate',dst,n)
for dst,n in (('slate_shingle_stairs',1),('slate_shingle_slab',2)): taille('slate_shingles',dst,n)
taille('marble_tiles','marble_tile_slab',2)
# ---------------------------------------------------------------- noms
FR={}; EN={}
for t,f,e in (('white','blanc','White'),('black','noir','Black')):
    FR.update({f'{t}_marble':f"Marbre {f}",f'polished_{t}_marble':f"Marbre {f} poli",f'{t}_marble_bricks':f"Briques de marbre {f}",
               f'{t}_marble_pillar':f"Colonne de marbre {f}",f'chiseled_{t}_marble':f"Marbre {f} ciselé",
               f'{t}_marble_stairs':f"Escalier de marbre {f}",f'{t}_marble_slab':f"Dalle de marbre {f}",f'{t}_marble_wall':f"Muret de marbre {f}",
               f'polished_{t}_marble_stairs':f"Escalier de marbre {f} poli",f'polished_{t}_marble_slab':f"Dalle de marbre {f} poli",
               f'{t}_marble_brick_stairs':f"Escalier en briques de marbre {f}",f'{t}_marble_brick_slab':f"Dalle en briques de marbre {f}",f'{t}_marble_brick_wall':f"Muret en briques de marbre {f}"})
    EN.update({f'{t}_marble':f"{e} Marble",f'polished_{t}_marble':f"Polished {e} Marble",f'{t}_marble_bricks':f"{e} Marble Bricks",
               f'{t}_marble_pillar':f"{e} Marble Pillar",f'chiseled_{t}_marble':f"Chiseled {e} Marble",
               f'{t}_marble_stairs':f"{e} Marble Stairs",f'{t}_marble_slab':f"{e} Marble Slab",f'{t}_marble_wall':f"{e} Marble Wall",
               f'polished_{t}_marble_stairs':f"Polished {e} Marble Stairs",f'polished_{t}_marble_slab':f"Polished {e} Marble Slab",
               f'{t}_marble_brick_stairs':f"{e} Marble Brick Stairs",f'{t}_marble_brick_slab':f"{e} Marble Brick Slab",f'{t}_marble_brick_wall':f"{e} Marble Brick Wall"})
FR.update({'slate':"Ardoise",'slate_stairs':"Escalier d'ardoise",'slate_slab':"Dalle d'ardoise",'slate_wall':"Muret d'ardoise",
           'slate_shingles':"Tuiles d'ardoise",'slate_shingle_stairs':"Escalier en tuiles d'ardoise",'slate_shingle_slab':"Dalle en tuiles d'ardoise",
           'marble_tiles':"Carrelage de marbre",'marble_tile_slab':"Dalle de carrelage"})
EN.update({'slate':"Slate",'slate_stairs':"Slate Stairs",'slate_slab':"Slate Slab",'slate_wall':"Slate Wall",
           'slate_shingles':"Slate Shingles",'slate_shingle_stairs':"Slate Shingle Stairs",'slate_shingle_slab':"Slate Shingle Slab",
           'marble_tiles':"Marble Tiles",'marble_tile_slab':"Marble Tile Slab"})
for f,D in (('fr_fr.json',FR),('en_us.json',EN)):
    p=AS+'lang/'+f; d=json.load(open(p))
    for k,v in D.items(): d['block.airain.'+k]=v
    w(p,d)
assert set(FR)==set(TOUS), set(TOUS)^set(FR)
print('matériaux ok',len(TOUS))
