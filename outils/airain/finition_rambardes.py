# Finition des rambardes (1.56.1), à lancer après tous les générateurs (avant corriger_zfight et corriger_uv).
#  1. Variante « _x » des rambardes, portillons et vitres : chaque élément rentré de 0,03 px. Elle sert pour les côtés
#     est et ouest : là où deux rambardes se croisent (angles), leurs faces ne sont plus dans le même plan (plus de
#     scintillement), et la rambarde nord/sud passe devant.
#  2. Poteau d'angle extérieur : posé quand deux côtés voisins d'une même pièce ont une rambarde extérieure.
import json, os, glob, copy
AS='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
PRE=['','exposed_','weathered_','oxidized_']
RENTRE=0.03
def w(p,d): json.dump(d,open(p,'w'),indent=1,ensure_ascii=False)
# ---------------------------------------------------------------- 1. variantes _x
BASES=['airain_catwalk_railing','airain_catwalk_railing_inner','airain_catwalk_gate','airain_catwalk_gate_open','airain_catwalk_glass_frame','airain_catwalk_glass_pane']
VAR=set()
for p in PRE:
    for b in BASES:
        for hh in ('bottom','top'):
            n=f'{p}{b}_{hh}'; src=AS+f'models/block/{n}.json'
            if not os.path.exists(src): continue
            m=json.load(open(src)); m=copy.deepcopy(m)
            for e in m['elements']:
                f,t=e['from'],e['to']
                for i in range(3):
                    a,b2=min(f[i],t[i]),max(f[i],t[i])
                    if b2-a>2*RENTRE+0.05: f[i],t[i]=round(a+RENTRE,4),round(b2-RENTRE,4)
                    else: f[i],t[i]=a,b2
            w(AS+f'models/block/{n}_x.json',m); VAR.add(f'airain:block/{n}')
# ---------------------------------------------------------------- 2. poteau d'angle (dessiné au coin nord-ouest, dehors)
for p in PRE:
    for hh,h in (('bottom',3),('top',11)):
        tex={'m':f'airain:block/{p}airain_block','particle':f'airain:block/{p}airain_block'}
        el={"from":[-2,h,-2],"to":[0,h+13,0],"faces":{k:{"texture":"#m","uv":uv} for k,uv in
            (("north",[7,1.5,9,14.5]),("south",[7,1.5,9,14.5]),("east",[7,1.5,9,14.5]),("west",[7,1.5,9,14.5]),("up",[7,7,9,9]),("down",[7,7,9,9]))}}
        w(AS+f'models/block/{p}airain_catwalk_rail_corner_{hh}.json',{"parent":"minecraft:block/block","render_type":"minecraft:cutout","ambientocclusion":False,"textures":tex,"elements":[el]})
DEHORS="railing|glass|gate|gate_open"
COINS={('north','west'):0,('north','east'):90,('east','south'):180,('south','west'):270}
def coin(d1,d2):
    for k,r in COINS.items():
        if set(k)=={d1,d2}: return r
    return None
CW={'north':'east','east':'south','south':'west','west':'north'}; CCW={v:k for k,v in CW.items()}
# ---------------------------------------------------------------- 3. blockstates
n_bs=0
for bs_path in glob.glob(AS+'blockstates/*.json'):
    nom=os.path.basename(bs_path)[:-5]
    if not any(nom.endswith(x) for x in ('airain_catwalk','airain_catwalk_drawbridge','airain_catwalk_telescopic','airain_catwalk_landing')): continue
    bs=json.load(open(bs_path)); parts=bs['multipart']
    # tinte du bloc : celle de ses modèles de plancher
    p=next((x for x in PRE[1:] if x in nom), '')
    parts=[x for x in parts if 'rail_corner' not in x['apply']['model']]
    for x in parts:
        a=x['apply']
        if a['model'] in VAR and a.get('y',0) in (90,270): a['model']+='_x'
    if nom.endswith('airain_catwalk_landing'):
        for d in CW:
            for g in ('false','true'):
                flanc=CW[d] if g=='true' else CCW[d]
                parts.append({"apply":{"model":f'airain:block/{p}airain_catwalk_rail_corner_top'}|({"y":coin(d,flanc)} if coin(d,flanc) else {}),
                              "when":{"facing":d,"turn_left":g,"back":DEHORS,"side":DEHORS}})
    else:
        for (d1,d2),r in COINS.items():
            for hh,top in (('bottom','false'),('top','true')):
                when={d1:DEHORS,d2:DEHORS,"top":top}
                if 'retracted' in json.dumps(bs): when["retracted"]="false"
                parts.append({"apply":{"model":f'airain:block/{p}airain_catwalk_rail_corner_{hh}'}|({"y":r} if r else {}),"when":when})
    bs['multipart']=parts; w(bs_path,bs); n_bs+=1
print('finition rambardes : variantes',len(VAR),'blockstates',n_bs)
