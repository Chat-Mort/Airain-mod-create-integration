# 1.63 : ressources des cloisons grillagées et du portail coulissant (4 teintes + cirées).
import json, os
R='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=R+'assets/airain/'; Dd=R+'data/'
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
PRE=['','exposed_','weathered_','oxidized_']; ALL=("north","south","east","west","up","down")
def el(fr,to,t,faces=ALL):
    f={}
    for k in faces:
        dx,dy,dz=[abs(to[i]-fr[i]) for i in range(3)]
        a,b={"north":(dx,dy),"south":(dx,dy),"east":(dz,dy),"west":(dz,dy),"up":(dx,dz),"down":(dx,dz)}[k]
        tt=t+'v' if t=='#f' and b>a+0.01 else t
        a=min(16,a); b=min(16,b); u0=(16-a)/2; v0=(16-b)/2
        f[k]={"texture":tt,"uv":[round(u0,3),round(v0,3),round(u0+a,3),round(v0+b,3)]}
    return {"from":fr,"to":to,"faces":f}
def modele(nom,E,tex): w(AS+f'models/block/{nom}.json',{"parent":"minecraft:block/block","render_type":"minecraft:cutout","ambientocclusion":False,"textures":tex,"elements":E})
poteau=[el([7,0,7],[9,16,9],'#f')]
chapeau=[el([6.5,15,6.5],[9.5,16,9.5],'#bd')]
def bras(): return [el([7.5,0,0],[8.5,16,7],'#g',("east","west")),el([7.25,7.4,0],[8.75,8.6,7],'#bd')]
bras_haut=[el([7,14.5,0],[9,16,7],'#bd')]; bras_bas=[el([7,0,0],[9,1.5,7],'#bd')]
def tourne(E,ang):   # quart(s) de tour autour du centre, pour l'objet (bras est et ouest)
    out=[]
    for e in E:
        (x0,y0,z0),(x1,y1,z1)=e['from'],e['to']
        for _ in range(ang//90): x0,z0,x1,z1=16-z1,x0,16-z0,x1
        t=next(iter(e['faces'].values()))['texture'].rstrip('v')
        out.append(el([x0,y0,z0],[x1,y1,z1],t if t!='#g' else '#g',("north","south") if t=='#g' else ALL))
    return out
# vantail (dessiné le long de x) pour l'objet du portail
vantail=[el([0,0,9.75],[16,16,10.25],'#g',("north","south")),el([0,14.5,9.4],[16,16,10.6],'#bd'),el([0,0,9.4],[16,1.5,10.6],'#bd'),
         el([0,7.4,9.5],[16,8.6,10.5],'#bd'),el([0,0,9.3],[1.5,16,10.7],'#bd'),el([14.5,0,9.3],[16,16,10.7],'#bd'),el([1.8,9.5,8.6],[3.8,13.5,11.4],'#ci')]
ROT={'north':0,'east':90,'south':180,'west':270}
def mp(m,when=None,y=0):
    d={"apply":{"model":m}|({"y":y} if y else {})}
    if when: d["when"]=when
    return d
TOUS=[]
for s,p in enumerate(PRE):
    tex={'f':f'airain:block/{p}airain_beam_flange','fv':f'airain:block/{p}airain_beam_flange_vertical','bd':f'airain:block/{p}airain_band','g':f'airain:block/{p}airain_grate',
         'ci':f'airain:block/{p}chiseled_airain','particle':f'airain:block/{p}airain_grate'}
    modele(f'{p}airain_mesh_fence_post',poteau,tex); modele(f'{p}airain_mesh_fence_cap',chapeau,tex)
    modele(f'{p}airain_mesh_fence_side',bras(),tex); modele(f'{p}airain_mesh_fence_side_top',bras_haut,tex); modele(f'{p}airain_mesh_fence_side_bottom',bras_bas,tex)
    item=poteau+chapeau
    for a in (90,270): item+=tourne(bras()+bras_haut+bras_bas,a)
    modele(f'{p}airain_mesh_fence_item',item,tex)
    modele(f'{p}airain_sliding_gate',[],{'particle':tex['g']})
    modele(f'{p}airain_sliding_gate_item',vantail,tex)
    for c in (0,1):
        for f in ('airain_mesh_fence','airain_sliding_gate'):
            i=('waxed_' if c else '')+p+f; TOUS.append((i,f,p))
for i,f,p in TOUS:
    M=lambda n: f'airain:block/{p}{n}'
    if f=='airain_mesh_fence':
        parts=[mp(M('airain_mesh_fence_post')),mp(M('airain_mesh_fence_cap'),{"top":"true"})]
        for d,y in ROT.items():
            parts+=[mp(M('airain_mesh_fence_side'),{d:"true"},y),mp(M('airain_mesh_fence_side_top'),{d:"true","top":"true"},y),mp(M('airain_mesh_fence_side_bottom'),{d:"true","bottom":"true"},y)]
        bs={"multipart":parts}
    else: bs={"variants":{"":{"model":M('airain_sliding_gate')}}}
    w(AS+f'blockstates/{i}.json',bs)
    w(AS+f'models/item/{i}.json',{"parent":M(f+'_item')})
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
ox={}; wx={}
for f in ('airain_mesh_fence','airain_sliding_gate'):
    for s,p in enumerate(PRE):
        if s<3: ox['airain:'+p+f]={"next_oxidation_stage":'airain:'+PRE[s+1]+f}
        wx['airain:'+p+f]={"waxed":'airain:waxed_'+p+f}
for nom,aj in (('oxidizables',ox),('waxables',wx)):
    c=Dd+f'neoforge/data_maps/block/{nom}.json'; d=json.load(open(c)); d['values'].update(aj); w(c,d)
for tg in ('minecraft/tags/block/mineable/pickaxe.json','minecraft/tags/block/needs_stone_tool.json'):
    c=Dd+tg; d=json.load(open(c))
    for i,_,_ in TOUS:
        if 'airain:'+i not in d['values']: d['values'].append('airain:'+i)
    w(c,d)
RC=Dd+'airain/recipe/cloisons/'
it=lambda i:{"item":i if ':' in i else 'airain:'+i}
w(RC+'mesh_fence.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["NGN","NGN"],"key":{"N":it('airain_nugget'),"G":it('airain_grate')},"result":{"id":"airain:airain_mesh_fence","count":6}})
w(RC+'sliding_gate.json',{"type":"minecraft:crafting_shapeless","category":"redstone","ingredients":[it('airain_mesh_fence'),it('airain_mesh_fence'),it('airain_ingot')],"result":{"id":"airain:airain_sliding_gate","count":1}})
for p in PRE:
    for f in ('airain_mesh_fence','airain_sliding_gate'):
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing","ingredients":[it(p+f),it('minecraft:honeycomb')],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
NFR={'airain_mesh_fence':"Cloison grillagée d'airain",'airain_sliding_gate':"Portail coulissant d'airain"}
NEN={'airain_mesh_fence':"Airain Mesh Fence",'airain_sliding_gate':"Airain Sliding Gate"}
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
fr={}; en={}
for i,f,p in TOUS:
    s=PRE.index(p); c=i.startswith('waxed_')
    fr['block.airain.'+i]=NFR[f]+SFR[s]+(' (ciré)' if c else ''); en['block.airain.'+i]=('Waxed ' if c else '')+SEN[s]+NEN[f]
fr.update({"airain.ingenieur.cloisons.titre":"Cloisons et portails","airain.ingenieur.cloisons.court":"Cloisons",
  "airain.ingenieur.cloisons.histoire":"Chaque atelier avait sa cage, chaque cage sa porte.",
  "airain.ingenieur.cloisons.usage":"@airain:airain_mesh_fence Cloison : se raccorde, s'empile\n@airain:airain_sliding_gate Portail coulissant\n- Clic droit main nue : ouvrir, fermer\n- Ou un signal de redstone\n- Les portails voisins bougent ensemble\n- Clé : changer le côté où il glisse"})
en.update({"airain.ingenieur.cloisons.titre":"Fences and Gates","airain.ingenieur.cloisons.court":"Fences",
  "airain.ingenieur.cloisons.histoire":"Every workshop had its cage, every cage its gate.",
  "airain.ingenieur.cloisons.usage":"@airain:airain_mesh_fence Fence: connects, stacks\n@airain:airain_sliding_gate Sliding gate\n- Bare-hand right-click: open, close\n- Or a redstone signal\n- Neighbouring gates move together\n- Wrench: change the sliding side"})
for f,D in (('fr_fr.json',fr),('en_us.json',en)):
    pth=AS+'lang/'+f; d=json.load(open(pth)); d.update(D); json.dump(d,open(pth,'w'),ensure_ascii=False,indent=1)
print('cloisons ok', len(TOUS))
