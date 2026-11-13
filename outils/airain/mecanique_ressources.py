# Ressources 1.53 : la mécanique impériale (allégeur, surcompresseur).
import json, os
D=os.path.dirname(os.path.abspath(__file__))
_a=open(D+'/atelier_ressources.py').read()
exec(_a[:_a.index('# ---------------------------------------------------------------- textures')])
ROT={'north':0,'east':90,'south':180,'west':270}
def butin(i):
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
TIGE_TRAVERS={"uv":[7,3,9,13],"rotation":90}
# ---------------------------------------------------------------- allégeur (arbre nord-sud)
def allegeur():
    """Flasques ciselés creusés au centre (on voit l'arbre et son palier), quatre colonnes, volant au milieu."""
    E=[]
    for z0 in (0,13):
        dehors="north" if z0==0 else "south"; dedans="south" if z0==0 else "north"
        for (a,b) in (([0,0],[16,5]),([0,11],[16,16]),([0,5],[5,11]),([11,5],[16,11])):
            E+=[el([a[0],a[1],z0],[b[0],b[1],z0+3],'#ci',faces=(dehors,)),el([a[0],a[1],z0],[b[0],b[1],z0+3],'#pn',faces=(dedans,))]
        E+=[el([0,0,z0],[16,16,z0+3],'#bd',faces=("east","west","up","down")),
            el([5,5,z0],[11,11,z0+3],'#bd',faces=("east","west","up","down"))]          # parois du trou (vues de l'intérieur)
        zc=z0+2 if z0==0 else z0
        for (a,b) in (([5,5],[11,6]),([5,10],[11,11]),([5,6],[6,10]),([10,6],[11,10])):  # palier en retrait, autour de l'arbre
            E.append(el([a[0],a[1],zc],[b[0],b[1],zc+1],'#rg'))
    for (x,y) in ((0,0),(14,0),(0,14),(14,14)):
        e=el([x,y,3],[x+2,y+2,13],'#ro',faces=("up","down"),uv=[7,3,9,13])
        e['faces'].update({k:{"texture":"#ro","uv":[7,3,9,13],"rotation":90} for k in ("east","west")}); E.append(e)
    return E
def volant():
    E=[]
    for k in (0,45):
        r=([8,8,8],'z',k) if k else None
        for a,b in (([3,13,6],[13,15,10]),([3,1,6],[13,3,10]),([1,3,6],[3,13,10]),([13,3,6],[15,13,10])):
            E.append(el(a,b,'#rg',rot=r))
    E+=[el([7.25,3,7],[8.75,13,9],'#m'),el([3,7.25,7],[13,8.75,9],'#m'),el([5.5,5.5,6.5],[10.5,10.5,9.5],'#bd')]
    return E
def lampes_allegeur():
    E=[]
    for (x,y) in ((2,2),(12,2),(2,12),(12,12)):
        E+=[el([x,y,-0.2],[x+2,y+2,0],'#lr',faces=("north",),uv=[3,6,5,8],lum=True),el([x,y,16],[x+2,y+2,16.2],'#lr',faces=("south",),uv=[3,6,5,8],lum=True)]
    return E
# ---------------------------------------------------------------- surcompresseur (le raccord vers le nord)
def surcomp():
    E=[el([0,0,0],[16,3,16],'#pn',faces=("up",),uv='full'),el([0,0,0],[16,3,16],'#bd',faces=("north","south","east","west")),el([0,0,0],[16,3,16],'#m',faces=("down",)),
       el([3,3,4],[13,12,12],'#fz',faces=("north","south","east","west"),uv='crop'),el([2,3,3],[14,4,13],'#bd'),el([2,11,3],[14,12,13],'#bd'),
       el([4,12,5],[12,13,11],'#pn',faces=("up",),uv='crop'),el([4,12,5],[12,13,11],'#bd',faces=("north","south","east","west")),
       el([5,4,0],[11,10,4],'#tu',faces=("east","west"),uv=[12,5,16,11]),el([5,4,0],[11,10,4],'#tv',faces=("up","down")),el([4,3,0],[12,11,1],'#bd'),
       el([7.5,13,11.5],[8.5,15,12.5]),el([5,15,12],[11,21,14]),el([5,15,12],[11,21,14],rot=([8,18,13],'z',45)),
       el([5.6,15.6,14],[10.4,20.4,14.1],'#cad',faces=("south",),uv='full'),
       el([11.5,12,10.5],[13.5,16,12.5],'#tv',faces=("north","south","east","west"),uv='crop'),el([11,16,10],[14,16.5,13],'#bd'),
       el([2,3,13.5],[4,5,15.5],'#rg'),el([4,13,7],[6,14,9],'#rg'),el([10,13,7],[12,14,9],'#rg')]
    return E
PISTON=[el([4.5,13,7.5],[5.5,17,8.5]),el([4,17,7],[6,18,9],'#bd')]
VOYANT=[el([1.9,2.9,13.4],[4.1,5.1,15.6],'#lr',uv=[3,6,5.2,8.2],lum=True)]
# ---------------------------------------------------------------- modèles
for p in PRE:
    t=dict(tex(p),ci=f'airain:block/{p}chiseled_airain',lr='airain:block/lamp_red_glass',cad='airain:block/gauge_face')
    modele(f'{p}airain_load_reliever',allegeur(),t); modele(f'{p}airain_load_reliever_item',allegeur()+volant(),t)
    modele(f'{p}airain_supercharger',surcomp(),t); modele(f'{p}airain_supercharger_item',surcomp()+PISTON+[dict(e,**{"from":[e['from'][0]+6,e['from'][1],e['from'][2]],"to":[e['to'][0]+6,e['to'][1],e['to'][2]]}) for e in PISTON],t)
tp=dict(tex(''),lr='airain:block/lamp_red_glass')
for p in PRE:
    t=tex(p)
    modele(f'airain_load_reliever/{p}flywheel',volant(),t); modele(f'airain_supercharger/{p}piston',PISTON,t)
modele('airain_load_reliever/lamps',lampes_allegeur(),tp); modele('airain_supercharger/lamp',VOYANT,tp)
# ---------------------------------------------------------------- blockstates, objets, butin
FAMS=['airain_load_reliever','airain_supercharger']; TOUS=[]
for f in FAMS:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f; TOUS.append(i); M=f'airain:block/{p}{f}'
            if f=='airain_load_reliever': v={"axis=z":{"model":M},"axis=x":{"model":M,"y":90},"axis=y":{"model":M,"x":90}}
            else: v={f"facing={d}":{"model":M}|({"y":r} if r else {}) for d,r in ROT.items()}
            w(AS+f'blockstates/{i}.json',{"variants":v}); w(AS+f'models/item/{i}.json',{"parent":M+'_item'}); butin(i)
ox={}; wx={}
for f in FAMS:
    for s,p in enumerate(PRE):
        if s<3: ox['airain:'+p+f]={"next_oxidation_stage":'airain:'+PRE[s+1]+f}
        wx['airain:'+p+f]={"waxed":'airain:waxed_'+p+f}
for nm,aj in (('oxidizables',ox),('waxables',wx)):
    c=Dd+f'neoforge/data_maps/block/{nm}.json'; d=json.load(open(c)); d['values'].update(aj); w(c,d)
def tag(chemin, valeurs):
    c=Dd+chemin; old=json.load(open(c))['values'] if os.path.exists(c) else []
    w(c,{"replace":False,"values":list(dict.fromkeys(old+valeurs))})
ids=['airain:'+i for i in TOUS]
tag('minecraft/tags/block/mineable/pickaxe.json',ids); tag('minecraft/tags/block/needs_iron_tool.json',ids)
# ---------------------------------------------------------------- recettes : crafteur mécanique de Create, 5 × 5 entièrement rempli
RC=R+'data/airain/recipe/airain/'
it=lambda i:{"item":"airain:"+i}
def meca(n,pat,key,res):
    w(RC+n+'.json',{"type":"create:mechanical_crafting","accept_mirrored":False,"category":"misc","key":key,"pattern":pat,"result":{"count":1,"id":"airain:"+res},"show_notification":True})
P={"item":"create:precision_mechanism"}
meca('load_reliever',["BSSSB","SGIGS","SIPIS","SGIGS","BSSSB"],{"B":it('airain_block'),"S":it('airain_sheet'),"G":it('airain_gear'),"I":it('airain_ingot'),"P":P},'airain_load_reliever')
meca('supercharger',["BFFFB","FGSGF","FSPSF","FGSGF","BFFFB"],{"B":it('airain_block'),"F":it('fire_bricks'),"S":it('airain_sheet'),"G":it('airain_gear'),"P":P},'airain_supercharger')
for p in PRE:
    for f in FAMS:
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing",
          "ingredients":[it(p+f),{"item":"minecraft:honeycomb"}],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
# ---------------------------------------------------------------- noms
NFR={'airain_load_reliever':"Allégeur impérial",'airain_supercharger':"Surcompresseur impérial"}
NEN={'airain_load_reliever':"Imperial Load Reliever",'airain_supercharger':"Imperial Supercharger"}
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
fr={"airain.mecanique.double":"Un autre allégeur règle déjà ce réseau","airain.mecanique.repos":"Au repos (réseau immobile ou sans charge)",
    "airain.mecanique.allege":"Charge retirée : %s su","airain.mecanique.allege_part":"%s %% de la charge du réseau",
    "airain.mecanique.sans_generateur":"Aucun générateur à alimenter","airain.mecanique.alimente":"Alimente : %s","airain.mecanique.surcomp":"Capacité de stress : +%s %%"}
en={"airain.mecanique.double":"Another reliever already handles this network","airain.mecanique.repos":"Idle (network stopped or unloaded)",
    "airain.mecanique.allege":"Load removed: %s su","airain.mecanique.allege_part":"%s%% of the network's load",
    "airain.mecanique.sans_generateur":"No generator to feed","airain.mecanique.alimente":"Feeding: %s","airain.mecanique.surcomp":"Stress capacity: +%s%%"}
for f in FAMS:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f
            fr['block.airain.'+i]=NFR[f]+SFR[s]+(' (ciré)' if c else ''); en['block.airain.'+i]=('Waxed ' if c else '')+SEN[s]+NEN[f]
L=AS+'lang/'
for fn,d in (('fr_fr.json',fr),('en_us.json',en)):
    j=json.load(open(L+fn)); j.update(d); json.dump(j,open(L+fn,'w'),ensure_ascii=False,indent=1)
print('mécanique ok',len(TOUS))
