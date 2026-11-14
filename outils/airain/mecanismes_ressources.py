# Ressources 1.52 : passerelles mobiles (pièces-mécanismes), monte-charge (treuil, mât, cabine, boîtier d'appel).
import json, os
D=os.path.dirname(os.path.abspath(__file__))
_a=open(D+'/atelier_ressources.py').read()
exec(_a[:_a.index('# ---------------------------------------------------------------- textures')])
P={}; _p=open(D+'/passerelles_ressources.py').read()
exec(_p[:_p.index('# ---------------------------------------------------------------- modèles par teinte')],P)
ROT={'north':0,'east':90,'south':180,'west':270}
def mp(model,when=None,y=0,x=0):
    d={"apply":{"model":model}|({"y":y} if y else {})|({"x":x} if x else {})}
    if when is not None: d["when"]=when
    return d
def butin(i):
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
# ---------------------------------------------------------------- géométrie
def carter(h, pont):
    """1.56.3 : plus de carter sous le plancher. Un repère simple posé sur le sol (dessiné vers le nord = vers les segments) :
    pont-levis : une charnière épaisse au bord qui se relève ; passerelle rétractable : deux rails dans l'axe."""
    if pont:
        return [el([0.5,h-0.5,-0.25],[4.5,h+1,1.25],'#m'),el([11.5,h-0.5,-0.25],[15.5,h+1,1.25],'#m'),     # nœuds de charnière
                el([4.5,h-0.25,0],[11.5,h+0.75,1],'#rg'),el([4.5,h,1],[11.5,h+0.25,3],'#m'),                 # axe, et sa patte
                el([0.5,h,1.25],[4.5,h+0.25,3],'#m'),el([11.5,h,1.25],[15.5,h+0.25,3],'#m')]
    return [el([3.5,h,0],[4.5,h+0.5,16],'#rg'),el([11.5,h,0],[12.5,h+0.5,16],'#rg'),                       # rails
            el([3,h,0],[3.5,h+0.25,16],'#m'),el([12.5,h,0],[13,h+0.25,16],'#m')]                           # patins
def cote_rail(x0):   # rambarde le long d'un côté (x0 = 0 : ouest, 14 : est), sur toute la profondeur
    h=3; return [el([x0,h+11,0],[x0+2,h+13,16]),el([x0+0.5,h+6,0],[x0+1.5,h+7,16]),el([x0+0.5,h,0],[x0+1,h+3,16]),el([x0,h,0],[x0+2,h+13,2]),el([x0,h,14],[x0+2,h+13,16])]
def cabine():
    """Bas de la cabine (1.55) : plancher, poteaux d'angle, trois parois pleines ; le portail (nord) reste ouvert."""
    E=[el([0,1,0],[16,3,16],'#g',faces=("up","down"),uv='full'),el([0,1,0],[16,3,1]),el([0,1,15],[16,3,16]),el([0,1,1],[1,3,15]),el([15,1,1],[16,3,15])]
    for (x,z) in ((0,0),(14,0),(0,14),(14,14)): E.append(el([x,3,z],[x+2,16,z+2],'#m'))
    E+=[el([0,3,2],[1,16,14],'#pn',uv='crop'),el([15,3,2],[16,16,14],'#pn',uv='crop'),el([2,3,15],[14,16,16],'#pn',uv='crop'),
        el([1,9,2],[1.6,10,14],'#bd'),el([14.4,9,2],[15,10,14],'#bd'),el([2,9,14.4],[14,10,15],'#bd')]          # main courante
    return E
def cabine_haut():
    """Haut de la cabine : fenêtres sur les côtés, paroi côté mât (boîtier), toit avec plafonnier ; ouvert côté passerelles."""
    E=[]
    for (x,z) in ((0,0),(14,0),(0,14),(14,14)): E.append(el([x,0,z],[x+2,16,z+2],'#m'))
    for a,b,c,d in (([0,0,2],[1,3,14],[0,13,2],[1,15,14]),([15,0,2],[16,3,14],[15,13,2],[16,15,14])):
        E+=[el(a,b,'#bd'),el(c,d,'#bd')]                                    # cadre des fenêtres latérales
    E+=[el([0.25,3,2],[0.75,13,14],'#gl',faces=("east","west"),uv='crop'),el([15.25,3,2],[15.75,13,14],'#gl',faces=("east","west"),uv='crop')]
    # côté passerelles : ouvert sur toute la hauteur (on entre debout), seul le toit le surplombe
    E+=[el([2,0,15],[14,15,16],'#pn',uv='crop'),                                            # paroi côté mât
        el([0,15,0],[16,16,16],'#pn',faces=("up","down","north","south","east","west"),uv='crop'),   # toit
        el([6,14.6,6],[10,15,10],'#lw',faces=("down",),uv='crop',lum=True),el([5.5,14.4,5.5],[10.5,15,6],'#bd'),el([5.5,14.4,10],[10.5,15,10.5],'#bd')]
    # boîtier du sélecteur d'étage (le panneau de Create se pose sur sa face)
    E+=[el([5,2,14],[11,9,15],'#bd'),el([5.6,7.4,13.8],[6.6,8.4,14],'#lr',faces=("north",),uv='crop',lum=True),el([9.4,7.4,13.8],[10.4,8.4,14],'#lw',faces=("north",),uv='crop',lum=True)]
    return E
def mat():
    E=[]
    for (x,z) in ((1,1),(13,1),(1,13),(13,13)): E.append(el([x,0,z],[x+2,16,z+2],'#ro',faces=("north","south","east","west"),uv={k:[7,0,9,16] for k in ("north","south","east","west")}))
    for y in (0,8):
        E+=[el([3,y,13],[13,y+1,15],'#bd'),el([1,y,3],[3,y+1,13],'#bd'),el([13,y,3],[15,y+1,13],'#bd')]
    E.append(el([6.5,0,1],[9.5,16,2.5],'#rg'))
    for y in range(0,16,2): E.append(el([6,y,0],[10,y+1,1],'#rg'))
    return E
def treuil():   # arbre dans l'axe nord-sud
    return [el([1,0,0],[15,12,16],'#pn',faces=("up",),uv='crop'),el([1,0,0],[15,12,16],'#bd',faces=("east","west","down")),
            el([1,0,0],[15,12,16],'#pn',faces=("north","south"),uv='crop'),el([3,12,4],[13,14,12],'#bd'),el([4,14,5],[12,15,11],'#rg')]
def appel():
    return [el([5,4,13],[11,12,16],'#bd'),el([6,9,12.6],[10,11,13],'#lr',faces=("north","east","west","up"),uv='crop',lum=True),el([6.5,5.5,12.6],[9.5,7.5,13],'#rg')]
# ---------------------------------------------------------------- modèles
tp=dict(tex(''),lw='airain:block/lamp_warm',lr='airain:block/lamp_red_glass')
for p in PRE:
    t=dict(tex(p),lw='airain:block/lamp_warm',lr='airain:block/lamp_red_glass')
    for pont,nom in ((True,'drawbridge'),(False,'telescopic')):
        for hh,h in (('bottom',3),('top',11)): modele(f'airain_catwalk_mechanism/{p}{nom}_{hh}',carter(h,pont),t)
        modele(f'{p}airain_catwalk_{nom}_item',[e for e in json.load(open(AS+f'models/block/{p}airain_catwalk_item.json'))['elements']]+carter(3,pont),dict(t,g=f'airain:block/{p}airain_catwalk',r=f'airain:block/{p}riveted_airain'))
modele('airain_lift_cabin',cabine(),tp)
modele('airain_lift_cabin_top',cabine_haut(),dict(tp,gl='airain:block/airain_glass'),rt='translucent')
modele('airain_lift_cabin/gate',[dict(e) for e in P['portillon_nord'](3,False)],dict(tp,m='airain:block/airain_block'))
modele('airain_lift_mast',mat(),tp); modele('airain_lift_winch',treuil(),tp); modele('airain_lift_call_box',appel(),tp)
modele('airain_lift_item',mat()+[e for e in cabine()],tp)
# ---------------------------------------------------------------- blockstates
# 1. les passerelles ordinaires : invisibles quand elles sont relevées / rentrées
for p in PRE:
    for c in (0,1):
        i=('waxed_' if c else '')+p+'airain_catwalk'; cb=AS+f'blockstates/{i}.json'; bs=json.load(open(cb))
        for part in bs['multipart']: part.setdefault('when',{})['retracted']='false'
        w(cb,bs)
# 2. pièces-mécanismes : la passerelle (même teinte) + le carter tourné vers FACING
FAMS=['airain_catwalk_drawbridge','airain_catwalk_telescopic']; TOUS=[]
for f in FAMS:
    nom=f.split('_')[-1]
    for s,p in enumerate(PRE):
        base=json.load(open(AS+f'blockstates/{p}airain_catwalk.json'))
        for c in (0,1):
            i=('waxed_' if c else '')+p+f; TOUS.append(i)
            parts=[json.loads(json.dumps(x)) for x in base['multipart']]
            for part in parts: part['when'].pop('retracted',None)
            w(AS+f'blockstates/{i}.json',{"multipart":parts}); w(AS+f'models/item/{i}.json',{"parent":f'airain:block/{p}airain_catwalk_{nom}_item'}); butin(i)
# 3. monte-charge
w(AS+'blockstates/airain_lift_mast.json',{"variants":{f"facing={d}":{"model":"airain:block/airain_lift_mast"}|({"y":r} if r else {}) for d,r in ROT.items()}})
w(AS+'blockstates/airain_lift_cabin.json',{"variants":{f"facing={d},top={t}":{"model":"airain:block/airain_lift_cabin"+("_top" if t=="true" else "")}|({"y":r} if r else {}) for d,r in ROT.items() for t in ("false","true")}})
w(AS+'blockstates/airain_lift_winch.json',{"variants":{"axis=z":{"model":"airain:block/airain_lift_winch"},"axis=x":{"model":"airain:block/airain_lift_winch","y":90}}})
ap={}
for d,r in ROT.items():
    ap[f"face=wall,facing={d}"]={"model":"airain:block/airain_lift_call_box"}|({"y":r} if r else {})
    ap[f"face=floor,facing={d}"]={"model":"airain:block/airain_lift_call_box","x":270}|({"y":r} if r else {})
    ap[f"face=ceiling,facing={d}"]={"model":"airain:block/airain_lift_call_box","x":90}|({"y":r} if r else {})
w(AS+'blockstates/airain_lift_call_box.json',{"variants":ap})
for i,m in (('airain_lift_mast','airain_lift_item'),('airain_lift_winch','airain_lift_winch'),('airain_lift_call_box','airain_lift_call_box')):
    w(AS+f'models/item/{i}.json',{"parent":"airain:block/"+m}); butin(i)
w(Dd+'airain/loot_table/blocks/airain_lift_cabin.json',{"type":"minecraft:block","pools":[]})
# ---------------------------------------------------------------- patine, étiquettes, recettes, noms
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
ids=['airain:'+i for i in TOUS]+['airain:airain_lift_winch','airain:airain_lift_mast','airain:airain_lift_call_box']
tag('minecraft/tags/block/mineable/pickaxe.json',ids); tag('minecraft/tags/block/needs_stone_tool.json',ids)
RC=R+'data/airain/recipe/airain/'
it=lambda i:{"item":"airain:"+i}; mc=lambda i:{"item":"minecraft:"+i}
def sh(n,pat,key,res,cnt=1): w(RC+n+'.json',{"type":"minecraft:crafting_shaped","category":"misc","pattern":pat,"key":key,"result":{"id":"airain:"+res,"count":cnt}})
def sl(n,ing,res,cnt=1): w(RC+n+'.json',{"type":"minecraft:crafting_shapeless","category":"misc","ingredients":ing,"result":{"id":"airain:"+res,"count":cnt}})
sl('catwalk_drawbridge',[it('airain_catwalk'),it('airain_gear'),it('airain_sheet')],'airain_catwalk_drawbridge')
sl('catwalk_telescopic',[it('airain_catwalk'),it('airain_catwalk'),it('airain_gear')],'airain_catwalk_telescopic')
sh('lift_winch',["SGS","ICI"],{"S":it('airain_sheet'),"G":it('airain_gear'),"I":it('airain_ingot'),"C":{"item":"create:shaft"}},'airain_lift_winch')
sh('lift_mast',["I","B","I"],{"I":it('airain_ingot'),"B":it('airain_bars')},'airain_lift_mast',2)
sl('lift_call_box',[it('airain_sheet'),mc('stone_button'),mc('redstone')],'airain_lift_call_box')
for p in PRE:
    for f in FAMS:
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing",
          "ingredients":[it(p+f),{"item":"minecraft:honeycomb"}],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
NFR={'airain_catwalk_drawbridge':"Mécanisme de pont-levis",'airain_catwalk_telescopic':"Mécanisme de passerelle rétractable"}
NEN={'airain_catwalk_drawbridge':"Drawbridge Mechanism",'airain_catwalk_telescopic':"Telescopic Catwalk Mechanism"}
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
fr={"block.airain.airain_lift_winch":"Treuil de monte-charge","block.airain.airain_lift_mast":"Mât de monte-charge","block.airain.airain_lift_cabin":"Cabine de monte-charge",
    "block.airain.airain_lift_call_box":"Boîtier d'appel",
    "airain.mobile.longueur":"Longueur : %s segment(s)","airain.mobile.deploye":"Déployée","airain.mobile.releve":"Relevé","airain.mobile.rentre":"Rentrée","airain.mobile.mouvement":"En mouvement",
    "airain.ascenseur.etage":"Étage","airain.ascenseur.rdc":"RdC","airain.ascenseur.nb_etages":"Étages détectés : %s","airain.ascenseur.aucun":"Aucun monte-charge à portée",
    "airain.ascenseur.bloque":"Le passage de la cabine est obstrué","airain.ascenseur.immobile":"Le treuil ne tourne pas"}
en={"block.airain.airain_lift_winch":"Lift Winch","block.airain.airain_lift_mast":"Lift Mast","block.airain.airain_lift_cabin":"Lift Cabin","block.airain.airain_lift_call_box":"Call Box",
    "airain.mobile.longueur":"Length: %s segment(s)","airain.mobile.deploye":"Deployed","airain.mobile.releve":"Raised","airain.mobile.rentre":"Retracted","airain.mobile.mouvement":"Moving",
    "airain.ascenseur.etage":"Floor","airain.ascenseur.rdc":"GF","airain.ascenseur.nb_etages":"Floors detected: %s","airain.ascenseur.aucun":"No lift within reach",
    "airain.ascenseur.bloque":"The cabin's path is blocked","airain.ascenseur.immobile":"The winch is not turning"}
for f in FAMS:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f
            fr['block.airain.'+i]=NFR[f]+SFR[s]+(' (ciré)' if c else ''); en['block.airain.'+i]=('Waxed ' if c else '')+SEN[s]+NEN[f]
L=AS+'lang/'
for fn,d in (('fr_fr.json',fr),('en_us.json',en)):
    j=json.load(open(L+fn)); j.update(d); json.dump(j,open(L+fn,'w'),ensure_ascii=False,indent=1)
print('mécanismes ok',len(TOUS)+4)
