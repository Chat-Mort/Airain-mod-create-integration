# 1.59 : modèles, blockstates, textures et données de la charpente d'airain et des marquages au sol.
import json, os, math, sys
S='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/'
os.chdir(S)
exec(open(S+'airain_luxe.py').read().split("STADES=['','exposed_'")[0])   # teinte(), rendre_carte()
from PIL import Image
R='/home/claude/airain-mod-create-integration/src/main/resources/'
AS=R+'assets/airain/'; Dd=R+'data/'
TB=AS+'textures/block/'; TI=AS+'textures/item/'
def w(c,d): os.makedirs(os.path.dirname(c),exist_ok=True); json.dump(d,open(c,'w'),indent=1,ensure_ascii=False)
PRE=['','exposed_','weathered_','oxidized_']; T_=[0.0,0.28,0.58,0.92]
ALL=("north","south","east","west","up","down")

# ================================================================ textures (cartes de teintes 0..6, rendues par stade)
def vide(): return [[3.2]*16 for _ in range(16)]
def rivet(c,x,y):
    c[y][x]=6; c[y][x+1]=4.6; c[y+1][x+1]=1.3; c[y+1][x]=3.9
def aile():
    """Aile de poutrelle : longueur le long de u ; biseau clair en haut (rang 3), sombre en bas (rang 12), rivets aux rangs 5 et 10."""
    c=[[3.5-0.5*abs(y-7.5)/5 for x in range(16)] for y in range(16)]
    for x in range(16): c[3][x]=5.0; c[4][x]=4.1; c[12][x]=1.3; c[11][x]=2.6
    for x in (3,11):
        for y in (5,9): rivet(c,x,y)
    return c
def ame():
    """Âme : aplat doux, ombre sous l'aile du haut (rang 3), reflet au-dessus de l'aile du bas."""
    c=[[3.3-0.4*(y-3)/9 for x in range(16)] for y in range(16)]
    for x in range(16): c[3][x]=1.6; c[4][x]=2.5; c[12][x]=3.4
    return c
def platine():
    c=[[3.4-0.6*(x+y)/30 for x in range(16)] for y in range(16)]
    for i in range(1,15): c[1][i]=5.0; c[i][1]=5.0; c[14][i]=1.3; c[i][14]=1.3
    c[1][14]=3.2; c[14][1]=3.2
    for x in (3,11):
        for y in (3,11): rivet(c,x,y)
    return c
def barre():
    c=[[3.3 for x in range(16)] for y in range(16)]
    for x in range(16): c[6][x]=5.0; c[9][x]=1.4
    for x in (1,13): rivet(c,x,7)
    return c
def transpose(c): return [[c[x][y] for x in range(16)] for y in range(16)]
CARTES={'airain_beam_flange':aile(),'airain_beam_web':ame(),'airain_beam_plate':platine(),'airain_lattice_bar':barre()}
for s,p in enumerate(PRE):
    for nom,c in CARTES.items():
        rendre_carte(c,T_[s]).save(f'{TB}{p}{nom}.png')
        if nom!='airain_beam_plate': rendre_carte(transpose(c),T_[s]).save(f'{TB}{p}{nom}_vertical.png')

# marquages : peinture franche, légèrement plus sombre sur le bord (pas de bruit)
def hx(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
JA,JA_B,BL,BL_B,RO,RO_B,NO=hx('e3b021'),hx('c99a17'),hx('e8e4d8'),hx('cfcabb'),hx('b8322a'),hx('9a2822'),hx('2a2a2a')
def peindre(nom,f,dossier=TB):
    im=Image.new('RGBA',(16,16),(0,0,0,0))
    for y in range(16):
        for x in range(16):
            c=f(x,y)
            if c: im.putpixel((x,y),c)
    im.save(dossier+nom+'.png')
for nom,(c,cb) in (('yellow',(JA,JA_B)),('white',(BL,BL_B)),('red',(RO,RO_B))):
    # croix de 2 px : les bras du modèle y prennent leur morceau (uv à la position)
    peindre(f'{nom}_floor_line',lambda x,y,c=c: c if (7<=x<=8 or 7<=y<=8) else None)
    peindre(f'{nom}_floor_line',lambda x,y,c=c,cb=cb: (cb if x in (6,9) else c) if 6<=x<=9 and 1<=y<=14 else None,TI)
peindre('yellow_hazard_stripes',lambda x,y: JA if ((x+y)//4)%2==0 else NO)
peindre('red_hazard_stripes',lambda x,y: RO if ((x+y)//4)%2==0 else BL)
def fleche(c):
    def f(x,y):
        if 6<=x<=9 and 8<=y<=14: return c
        if 2<=y<=8 and abs(x-7.5)<=(y-2)+0.5 and abs(x-7.5)<=6.5: return c
    return f
peindre('white_floor_arrow',fleche(BL)); peindre('yellow_floor_arrow',fleche(JA))
peindre('white_floor_crossing',lambda x,y: BL if (x%8)<4 and 1<=y<=14 else None)

# ================================================================ modèles
def el(fr,to,t,faces=ALL,rot=None,uv=None):
    """Élément ; uv pixel pour pixel, centré (jamais étiré). Les textures orientables prennent leur version verticale
    quand la face est plus haute que large."""
    f={}
    for k in faces:
        dx,dy,dz=[abs(to[i]-fr[i]) for i in range(3)]
        a,b={"north":(dx,dy),"south":(dx,dy),"east":(dz,dy),"west":(dz,dy),"up":(dx,dz),"down":(dx,dz)}[k]
        tt=t
        if t in ('#f','#w','#b') and b>a+0.01: tt=t+'v'
        if uv and k in uv: u=uv[k]
        else:
            a=max(0.5,min(16,a)); b=max(0.5,min(16,b)); u0=(16-a)/2; v0=(16-b)/2
            u=[round(u0,3),round(v0,3),round(u0+a,3),round(v0+b,3)]
        f[k]={"texture":tt,"uv":u}
    e={"from":[round(v,3) for v in fr],"to":[round(v,3) for v in to],"faces":f}
    if rot: e["rotation"]={"origin":rot[0],"axis":rot[1],"angle":rot[2]}
    return e
def modele(nom,E,tex,rt='cutout',parent='minecraft:block/block'):
    w(AS+f'models/block/{nom}.json',{"parent":parent,"render_type":"minecraft:"+rt,"ambientocclusion":False,
       "textures":dict(tex,particle=tex.get('f',tex.get('pi',tex.get('b')))),"elements":E})
# --- poutrelle (couchée le long de x ; platine de début à l'ouest)
def poutre(tourne):
    if not tourne: return [el([0,1,3],[16,3,13],'#f'),el([0,13,3],[16,15,13],'#f'),el([0,3,7],[16,13,9],'#w',faces=("north","south"))]
    return [el([0,3,1],[16,13,3],'#f'),el([0,3,13],[16,13,15],'#f'),el([0,7,3],[16,9,13],'#w',faces=("up","down"))]
def poutre_platine(tourne,fin):
    x0,x1=(15,16) if fin else (0,1)
    return [el([x0,0.5,2],[x1,15.5,14],'#p')] if not tourne else [el([x0,2,0.5],[x1,14,15.5],'#p')]
def poteau(tourne):   # debout ; ailes au nord et au sud (tourné : à l'est et à l'ouest)
    if not tourne: return [el([3,0,1],[13,16,3],'#f'),el([3,0,13],[13,16,15],'#f'),el([7,0,3],[9,16,13],'#w',faces=("east","west"))]
    return [el([1,0,3],[3,16,13],'#f'),el([13,0,3],[15,16,13],'#f'),el([3,0,7],[13,16,9],'#w',faces=("north","south"))]
def poteau_platine(fin): y0,y1=(15,16) if fin else (0,1); return [el([1,y0,1],[15,y1,15],'#p')]
# --- pièces à 45° (montent vers l'est ; le blockstate tourne vers FACING), coupées en deux moitiés ≤ 16 px pour ne rien étirer
L=16*math.sqrt(2); H=L/2
def incline(y0,y1,z0,z1,t,faces=ALL):
    E=[]
    for a,b in ((8-H,8),(8,8+H)):
        E.append(el([a,y0,z0],[b,y1,z1],t,faces=faces,rot=([8,8,8],'z',45)))
    return E
def profil_incline(h,lg):   # h : hauteur du profil, lg : largeur des ailes
    c=8; e=1.5 if h>6 else 1
    return incline(c-h/2,c-h/2+e,8-lg/2,8+lg/2,'#f')+incline(c+h/2-e,c+h/2,8-lg/2,8+lg/2,'#f')+incline(c-h/2+e,c+h/2-e,7,9,'#w',faces=("north","south"))
def verriere_cadre():
    E=incline(8,9.5,0,1,'#b')+incline(8,9.5,15,16,'#b')
    E.append(el([8-H,8,1],[8-H+1.5,9.5,15],'#b',rot=([8,8,8],'z',45)))     # traverse au bas de chaque bloc
    return E
def verriere_verre():
    return [el([8-H,7.6,0],[8,8.4,16],'#g',faces=("up","down"),rot=([8,8,8],'z',45),uv={'up':[0,0,H,16],'down':[0,0,H,16]}),
            el([8,7.6,0],[8+H,8.4,16],'#g',faces=("up","down"),rot=([8,8,8],'z',45),uv={'up':[16-H,0,16,16],'down':[16-H,0,16,16]})]
# --- treillis (le long de x)
def treillis(alt):
    D=8.0
    return [el([0,0,4],[16,2,12],'#f'),el([0,14,4],[16,16,12],'#f'),el([0,2,6],[1,14,10],'#b'),el([15,2,6],[16,14,10],'#b'),
            el([8-D,7,6.5],[8+D,9,9.5],'#b',rot=([8,8,8],'z',-45 if alt else 45))]
def tourne_z(E):
    """Quart de tour autour de z (pour la colonne) : x' = 16 - y, y' = x ; la diagonale change de sens."""
    out=[]
    for e in E:
        (x0,y0,z0),(x1,y1,z1)=e['from'],e['to']
        t=next(iter(e['faces'].values()))['texture'].rstrip('v')
        r=e.get('rotation')
        if r:   # barre diagonale : on garde la boîte, l'angle s'inverse
            out.append(el([x0,y0,z0],[x1,y1,z1],t,rot=(r['origin'],'z',-r['angle'])))
        else: out.append(el([16-y1,x0,z0],[16-y0,x1,z1],t))
    return out
# --- lanterneau
def lanterneau_cadre(): return [el([0,0,0],[16,2,1],'#b'),el([0,0,15],[16,2,16],'#b'),el([0,0,1],[1,2,15],'#b'),el([15,0,1],[16,2,15],'#b')]
def lanterneau_verre(): return [el([1,0.8,1],[15,1.2,15],'#g',faces=("up","down"))]
# --- gouttière (le long de x) et descente
def gouttiere():
    E=[el([0,10,3],[16,11,13],'#pi'),el([0,11,3],[16,15,4],'#pi'),el([0,11,12],[16,15,13],'#pi'),
       el([0,14.5,2.5],[16,15.5,3.5],'#pi'),el([0,14.5,12.5],[16,15.5,13.5],'#pi')]          # bourrelets
    E+=[el([7,9.5,2.5],[9,10,13.5],'#b'),el([7,10,2.5],[9,15,3],'#b'),el([7,10,13],[9,15,13.5],'#b')]   # crochet
    return E
def gouttiere_bout(fin): x0,x1=(15.5,16) if fin else (0,0.5); return [el([x0,10,3],[x1,15,13],'#pi')]
def gouttiere_sortie(): return [el([6,0,6],[10,10,10],'#piv',faces=("north","south","east","west","down"))]
def descente(): return [el([6,0,6],[10,16,10],'#piv',faces=("north","south","east","west")),el([5,6,5],[11,7.5,11],'#b')]
def descente_sabot(): return [el([5,0,5],[11,2,11],'#pi'),el([6,2,6],[10,3,10],'#pi',faces=("north","south","east","west","up"))]

for p in PRE:
    tex={'f':f'airain:block/{p}airain_beam_flange','fv':f'airain:block/{p}airain_beam_flange_vertical','w':f'airain:block/{p}airain_beam_web',
         'wv':f'airain:block/{p}airain_beam_web_vertical','p':f'airain:block/{p}airain_beam_plate','b':f'airain:block/{p}airain_lattice_bar',
         'bv':f'airain:block/{p}airain_lattice_bar_vertical','g':'airain:block/airain_glass','pi':f'airain:block/{p}airain_pipe','piv':f'airain:block/{p}airain_pipe_vertical'}
    for t,suf in ((False,''),(True,'_turned')):
        modele(f'{p}airain_beam{suf}',poutre(t),tex); modele(f'{p}airain_beam_start{suf}',poutre_platine(t,False),tex); modele(f'{p}airain_beam_end{suf}',poutre_platine(t,True),tex)
        modele(f'{p}airain_beam_post{suf}',poteau(t),tex)
    modele(f'{p}airain_beam_post_base',poteau_platine(False),tex); modele(f'{p}airain_beam_post_cap',poteau_platine(True),tex)
    modele(f'{p}airain_beam_item',poteau(False)+poteau_platine(False)+poteau_platine(True),tex)
    modele(f'{p}airain_knee_brace',profil_incline(6,6),tex)
    modele(f'{p}airain_rafter',profil_incline(10,10),tex)
    modele(f'{p}airain_glass_roof_frame',verriere_cadre(),tex); modele(f'{p}airain_glass_roof_glass',verriere_verre(),tex,'translucent')
    modele(f'{p}airain_glass_roof_item',verriere_cadre()+verriere_verre(),tex,'translucent')
    for alt in (False,True):
        s='_alt' if alt else ''
        modele(f'{p}airain_lattice_girder{s}',treillis(alt),tex); modele(f'{p}airain_lattice_girder_column{s}',tourne_z(treillis(alt)),tex)
    modele(f'{p}airain_skylight_frame',lanterneau_cadre(),tex); modele(f'{p}airain_skylight_glass',lanterneau_verre(),tex,'translucent')
    modele(f'{p}airain_skylight_item',lanterneau_cadre()+lanterneau_verre(),tex,'translucent')
    modele(f'{p}airain_gutter',gouttiere(),tex); modele(f'{p}airain_gutter_start',gouttiere_bout(False),tex); modele(f'{p}airain_gutter_end',gouttiere_bout(True),tex)
    modele(f'{p}airain_gutter_outlet',gouttiere_sortie(),tex)
    modele(f'{p}airain_gutter_item',gouttiere()+gouttiere_bout(False)+gouttiere_bout(True),tex)
    modele(f'{p}airain_downpipe',descente(),tex); modele(f'{p}airain_downpipe_shoe',descente_sabot(),tex)
    modele(f'{p}airain_downpipe_item',descente()+descente_sabot(),tex)

# marquages : une seule face, à peine au-dessus du sol
def couche(x0,z0,x1,z1,t='#t'): return el([x0,0,z0],[x1,0.1,z1],t,faces=("up",),uv={'up':[x0,z0,x1,z1]})
def marquage(nom,E,tex): w(AS+f'models/block/{nom}.json',{"parent":"minecraft:block/block","render_type":"minecraft:cutout","ambientocclusion":False,"textures":dict(tex,particle=tex['t']),"elements":E})
for c in ('yellow','white','red'):
    tex={'t':f'airain:block/{c}_floor_line'}
    marquage(f'{c}_floor_line_dot',[couche(7,7,9,9)],tex)
    for d,(a,b,cc,dd) in {'north':(7,0,9,7),'south':(7,9,9,16),'east':(9,7,16,9),'west':(0,7,7,9)}.items(): marquage(f'{c}_floor_line_{d}',[couche(a,b,cc,dd)],tex)
for n in ('yellow_hazard_stripes','red_hazard_stripes','white_floor_arrow','yellow_floor_arrow','white_floor_crossing'):
    marquage(n,[couche(0,0,16,16)],{'t':f'airain:block/{n}'})

# ================================================================ blockstates
def mp(model,when=None,x=0,y=0):
    d={"apply":{"model":model}|({"x":x} if x else {})|({"y":y} if y else {})}
    if when: d["when"]=when
    return d
FACE={'north':270,'east':0,'south':90,'west':180}     # pièces dessinées montant vers l'est
FAM=['airain_beam','airain_knee_brace','airain_rafter','airain_lattice_girder','airain_glass_roof','airain_skylight','airain_gutter','airain_downpipe']
TOUS=[]
for f in FAM:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f; TOUS.append(i); M=lambda n: f'airain:block/{p}{n}'
            if f=='airain_beam':
                parts=[]
                for tr in ('false','true'):
                    suf='_turned' if tr=='true' else ''
                    for ax,yr in (('x',0),('z',90)):
                        parts+=[mp(M('airain_beam'+suf),{"axis":ax,"turned":tr},y=yr),mp(M('airain_beam_start'+suf),{"axis":ax,"turned":tr,"start":"true"},y=yr),
                                mp(M('airain_beam_end'+suf),{"axis":ax,"turned":tr,"end":"true"},y=yr)]
                    parts.append(mp(M('airain_beam_post'+suf),{"axis":"y","turned":tr}))
                parts+=[mp(M('airain_beam_post_base'),{"axis":"y","start":"true"}),mp(M('airain_beam_post_cap'),{"axis":"y","end":"true"})]
                bs={"multipart":parts}
            elif f in ('airain_knee_brace','airain_rafter'):
                bs={"variants":{f"facing={d}":{"model":M(f)}|({"y":r} if r else {}) for d,r in FACE.items()}}
            elif f=='airain_glass_roof':
                bs={"multipart":[mp(M('airain_glass_roof_frame'),{"facing":d},y=r) for d,r in FACE.items()]+[mp(M('airain_glass_roof_glass'),{"facing":d},y=r) for d,r in FACE.items()]}
            elif f=='airain_lattice_girder':
                v={}
                for alt in ('false','true'):
                    s_='_alt' if alt=='true' else ''
                    v[f'alt={alt},axis=x']={"model":M('airain_lattice_girder'+s_)}
                    v[f'alt={alt},axis=z']={"model":M('airain_lattice_girder'+s_),"y":90}
                    v[f'alt={alt},axis=y']={"model":M('airain_lattice_girder_column'+s_)}
                bs={"variants":v}
            elif f=='airain_skylight':
                bs={"multipart":[mp(M('airain_skylight_frame')),mp(M('airain_skylight_glass'))]}
            elif f=='airain_gutter':
                parts=[]
                for ax,yr in (('x',0),('z',90)):
                    parts+=[mp(M('airain_gutter'),{"axis":ax},y=yr),mp(M('airain_gutter_start'),{"axis":ax,"start":"true"},y=yr),mp(M('airain_gutter_end'),{"axis":ax,"end":"true"},y=yr)]
                parts.append(mp(M('airain_gutter_outlet'),{"outlet":"true"}))
                bs={"multipart":parts}
            else:
                bs={"multipart":[mp(M('airain_downpipe')),mp(M('airain_downpipe_shoe'),{"outlet":"true"})]}
            w(AS+f'blockstates/{i}.json',bs)
            item={'airain_beam':'airain_beam_item','airain_glass_roof':'airain_glass_roof_item','airain_skylight':'airain_skylight_item','airain_gutter':'airain_gutter_item','airain_downpipe':'airain_downpipe_item'}.get(f,f)
            w(AS+f'models/item/{i}.json',{"parent":M(item)})
            w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})
MARQ=['yellow_floor_line','white_floor_line','red_floor_line','yellow_hazard_stripes','red_hazard_stripes','white_floor_arrow','yellow_floor_arrow','white_floor_crossing']
for i in MARQ:
    if i.endswith('_line'):
        c=i.split('_')[0]
        bs={"multipart":[mp(f'airain:block/{c}_floor_line_dot')]+[mp(f'airain:block/{c}_floor_line_{d}',{d:"true"}) for d in ('north','south','east','west')]}
        w(AS+f'models/item/{i}.json',{"parent":"minecraft:item/generated","textures":{"layer0":f"airain:item/{i}"}})
    elif 'stripes' in i:
        bs={"variants":{"":{"model":f'airain:block/{i}'}}}
        w(AS+f'models/item/{i}.json',{"parent":"minecraft:item/generated","textures":{"layer0":f"airain:block/{i}"}})
    else:
        bs={"variants":{f"facing={d}":{"model":f'airain:block/{i}'}|({"y":r} if r else {}) for d,r in {'north':0,'east':90,'south':180,'west':270}.items()}}
        w(AS+f'models/item/{i}.json',{"parent":"minecraft:item/generated","textures":{"layer0":f"airain:block/{i}"}})
    w(AS+f'blockstates/{i}.json',bs)
    w(Dd+f'airain/loot_table/blocks/{i}.json',{"type":"minecraft:block","pools":[{"rolls":1,"bonus_rolls":0,"entries":[{"type":"minecraft:item","name":"airain:"+i}],"conditions":[{"condition":"minecraft:survives_explosion"}]}]})

# ================================================================ data maps, tags
ox={}; wx={}
for f in FAM:
    for s,p in enumerate(PRE):
        if s<3: ox['airain:'+p+f]={"next_oxidation_stage":'airain:'+PRE[s+1]+f}
        wx['airain:'+p+f]={"waxed":'airain:waxed_'+p+f}
for nom,ajout in (('oxidizables',ox),('waxables',wx)):
    c=Dd+f'neoforge/data_maps/block/{nom}.json'; d=json.load(open(c)); d['values'].update(ajout); w(c,d)
def tag(chemin, valeurs):
    c=Dd+chemin; old=json.load(open(c))['values'] if os.path.exists(c) else []
    w(c,{"replace":False,"values":list(dict.fromkeys(old+valeurs))})
ids=['airain:'+i for i in TOUS]
tag('minecraft/tags/block/mineable/pickaxe.json',ids); tag('minecraft/tags/block/needs_stone_tool.json',ids)

# ================================================================ recettes
RC=Dd+'airain/recipe/charpente/'
def it(i): return {"item":i if ':' in i else 'airain:'+i}
w(RC+'beam.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["III"," I ","III"],"key":{"I":it('airain_ingot')},"result":{"id":"airain:airain_beam","count":12}})
def scie(nom,src,res,n=1): w(RC+nom+'.json',{"type":"minecraft:stonecutting","ingredient":it(src),"result":{"id":"airain:"+res,"count":n}})
scie('knee_brace','airain_beam','airain_knee_brace',2); scie('rafter','airain_beam','airain_rafter'); scie('lattice_girder','airain_beam','airain_lattice_girder',2)
w(RC+'glass_roof.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":[it('airain_beam'),it('minecraft:glass'),it('minecraft:glass'),it('minecraft:glass')],"result":{"id":"airain:airain_glass_roof","count":4}})
scie('skylight','airain_glass_roof','airain_skylight')
w(RC+'gutter.json',{"type":"minecraft:crafting_shaped","category":"building","pattern":["P P"," P "],"key":{"P":it('airain_sheet')},"result":{"id":"airain:airain_gutter","count":4}})
scie('downpipe','airain_gutter','airain_downpipe')
for p in PRE:
    for f in FAM:
        w(RC+f'waxing/waxed_{p}{f}.json',{"type":"minecraft:crafting_shapeless","category":"building","group":"airain_waxing",
          "ingredients":[it(p+f),it('minecraft:honeycomb')],"result":{"id":f"airain:waxed_{p}{f}","count":1}})
for c in ('yellow','white','red'):
    w(RC+f'{c}_floor_line.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":[it(f'minecraft:{c}_dye'),it('minecraft:stone')],"result":{"id":f"airain:{c}_floor_line","count":16}})
w(RC+'yellow_hazard_stripes.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":[it('minecraft:yellow_dye'),it('minecraft:black_dye'),it('minecraft:stone')],"result":{"id":"airain:yellow_hazard_stripes","count":16}})
w(RC+'red_hazard_stripes.json',{"type":"minecraft:crafting_shapeless","category":"building","ingredients":[it('minecraft:red_dye'),it('minecraft:white_dye'),it('minecraft:stone')],"result":{"id":"airain:red_hazard_stripes","count":16}})
scie('white_floor_arrow','white_floor_line','white_floor_arrow'); scie('yellow_floor_arrow','yellow_floor_line','yellow_floor_arrow'); scie('white_floor_crossing','white_floor_line','white_floor_crossing')

# ================================================================ noms et livre
NFR={'airain_beam':"Poutrelle d'airain",'airain_knee_brace':"Jambe de force d'airain",'airain_rafter':"Chevron d'airain",'airain_lattice_girder':"Poutre treillis d'airain",
     'airain_glass_roof':"Verrière d'airain",'airain_skylight':"Lanterneau d'airain",'airain_gutter':"Gouttière d'airain",'airain_downpipe':"Descente d'airain"}
NEN={'airain_beam':"Airain I-Beam",'airain_knee_brace':"Airain Knee Brace",'airain_rafter':"Airain Rafter",'airain_lattice_girder':"Airain Lattice Girder",
     'airain_glass_roof':"Airain Glass Roof",'airain_skylight':"Airain Skylight",'airain_gutter':"Airain Gutter",'airain_downpipe':"Airain Downpipe"}
SFR=['',' terni',' vieilli',' rouge impérial']; SEN=['','Tarnished ','Aged ','Imperial Red ']
fr={}; en={}
for f in FAM:
    for s,p in enumerate(PRE):
        for c in (0,1):
            i=('waxed_' if c else '')+p+f
            fr['block.airain.'+i]=NFR[f]+SFR[s]+(' (ciré)' if c else ''); en['block.airain.'+i]=('Waxed ' if c else '')+SEN[s]+NEN[f]
fr.update({'block.airain.yellow_floor_line':"Ligne au sol jaune",'block.airain.white_floor_line':"Ligne au sol blanche",'block.airain.red_floor_line':"Ligne au sol rouge",
    'block.airain.yellow_hazard_stripes':"Hachures jaunes et noires",'block.airain.red_hazard_stripes':"Hachures rouges et blanches",
    'block.airain.white_floor_arrow':"Flèche au sol blanche",'block.airain.yellow_floor_arrow':"Flèche au sol jaune",'block.airain.white_floor_crossing':"Passage piéton"})
en.update({'block.airain.yellow_floor_line':"Yellow Floor Line",'block.airain.white_floor_line':"White Floor Line",'block.airain.red_floor_line':"Red Floor Line",
    'block.airain.yellow_hazard_stripes':"Yellow Hazard Stripes",'block.airain.red_hazard_stripes':"Red Hazard Stripes",
    'block.airain.white_floor_arrow':"White Floor Arrow",'block.airain.yellow_floor_arrow':"Yellow Floor Arrow",'block.airain.white_floor_crossing':"Pedestrian Crossing"})
# livre de l'ingénieur : nouveau sommaire « Bâtir », deux chapitres
fr.update({"airain.ingenieur.sommaire.batir":"Bâtir l'Empire","airain.ingenieur.onglet.batir":"Bâtir",
  "airain.ingenieur.charpente.titre":"La charpente d'airain","airain.ingenieur.charpente.court":"Charpente",
  "airain.ingenieur.charpente.histoire":"Les halles de l'Empire tenaient sur l'airain.",
  "airain.ingenieur.charpente.usage":"@airain:airain_beam Poutrelle : poteau ou poutre\n- Platines seules ; clé : profil tourné\n@airain:airain_knee_brace Jambe de force à 45°\n@airain:airain_lattice_girder Treillis ; accroupi : colonne\n@airain:airain_rafter Chevron de toit\n@airain:airain_glass_roof Verrière entre chevrons\n@airain:airain_skylight Lanterneau, à plat\n@airain:airain_gutter Gouttière, descente\n- Inclinés : le haut devant soi\n- Tailleur : depuis la poutrelle",
  "airain.ingenieur.marquages.titre":"Les marquages au sol","airain.ingenieur.marquages.court":"Marquages",
  "airain.ingenieur.marquages.histoire":"Chaque allée avait sa ligne, chaque danger ses hachures.",
  "airain.ingenieur.marquages.usage":"@airain:yellow_floor_line Lignes : se raccordent seules\n- Jaune, blanche, rouge\n- Colorant + pierre : 16\n@airain:yellow_hazard_stripes Hachures : 2 colorants + pierre\n@airain:white_floor_arrow Flèche : vers où l'on regarde\n@airain:white_floor_crossing Passage piéton\n- Tailleur de pierre depuis une ligne\n- Sur tout sol plein, sans collision"})
en.update({"airain.ingenieur.sommaire.batir":"Building the Empire","airain.ingenieur.onglet.batir":"Build",
  "airain.ingenieur.charpente.titre":"Airain Framework","airain.ingenieur.charpente.court":"Framework",
  "airain.ingenieur.charpente.histoire":"The Empire's halls stood on airain.",
  "airain.ingenieur.charpente.usage":"@airain:airain_beam I-beam: post or beam\n- Plates on their own; wrench: turns\n@airain:airain_knee_brace Knee brace at 45°\n@airain:airain_lattice_girder Lattice; sneak: column\n@airain:airain_rafter Roof rafter\n@airain:airain_glass_roof Glass roof between rafters\n@airain:airain_skylight Skylight, flat\n@airain:airain_gutter Gutter, downpipe\n- Sloped: the top goes ahead of you\n- Stonecutter: from the I-beam",
  "airain.ingenieur.marquages.titre":"Floor Markings","airain.ingenieur.marquages.court":"Markings",
  "airain.ingenieur.marquages.histoire":"Every aisle had its line, every hazard its stripes.",
  "airain.ingenieur.marquages.usage":"@airain:yellow_floor_line Lines: connect on their own\n- Yellow, white, red\n- Dye + stone: 16\n@airain:yellow_hazard_stripes Stripes: 2 dyes + stone\n@airain:white_floor_arrow Arrow: points where you look\n@airain:white_floor_crossing Pedestrian crossing\n- Stonecutter, from a line\n- On any solid floor, no collision"})
L_=AS+'lang/'
for fn,d in (('fr_fr.json',fr),('en_us.json',en)):
    j=json.load(open(L_+fn)); j.update(d); json.dump(j,open(L_+fn,'w'),ensure_ascii=False,indent=1)
print('charpente ok', len(TOUS)+len(MARQ))
