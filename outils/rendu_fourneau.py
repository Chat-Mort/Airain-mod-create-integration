import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
rm.RAC['t']='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_root/'
FULL=[0,0,16,16]; MIR=[16,0,0,16]
def boite(fr,to,tex,lum=False,uvs=None,faces=("north","south","east","west","up","down")):
    f={}
    for k in faces:
        t=tex[k] if isinstance(tex,dict) else tex
        if t is None: continue
        f[k]={"texture":t}|({"uv":uvs[k]} if uvs and k in uvs else {"uv":[0,0,16,16]})|({"neoforge_data":{}} if lum and (lum is True or k in lum) else {})
    return {"from":fr,"to":to,"faces":f}
def cube(pos, faces, uvs=None, lum=()):
    x,y,z=[v*16 for v in pos]
    u={k:FULL for k in ("north","south","east","west","up","down")}; u.update(uvs or {})
    return boite([x,y,z],[x+16,y+16,z+16],faces,lum=lum,uvs=u)
def fourneau(allume):
    E=[]
    for yy in range(4):
        cote={0:'t:block/blast_furnace_plinth',1:'t:block/fire_bricks',2:'t:block/fire_bricks',3:'t:block/blast_furnace_hopper_side'}[yy]
        coin={0:'t:block/blast_furnace_plinth_corner',1:'t:block/fire_bricks_corner',2:'t:block/fire_bricks_corner',3:'t:block/blast_furnace_hopper_side_corner'}[yy]
        for xx in range(3):
            for zz in range(3):
                if (xx,zz)==(1,1) or (xx,yy,zz)==(1,0,0): continue
                f={k:cote for k in ("north","south","east","west")}; f["up"]='t:block/blast_furnace_top_sooty' if yy==3 else None; f["down"]=None
                uv={}
                # cornières : la face qui touche le coin porte la cornière, côté coin
                if xx in (0,2) and zz in (0,2):
                    for k in ("north","south","east","west"):
                        f[k]=coin
                    # orienter la cornière vers l'arête extérieure
                    uv["north"]= FULL if xx==0 else MIR
                    uv["south"]= MIR if xx==0 else FULL
                    uv["west"] = MIR if zz==0 else FULL
                    uv["east"] = FULL if zz==0 else MIR
                if (xx,yy,zz)==(1,2,0): f["north"]='t:block/blast_furnace_emblem'
                E.append(cube((xx,yy,zz),f,uv))
    # trou de coulée : capot d'airain en saillie et rigole
    lit=allume
    E.append(cube((1,0,0),{"north":'t:block/blast_furnace_taphole'+('_lit' if lit else ''),"up":None,"down":None,"south":None,"east":'t:block/blast_furnace_plinth',"west":'t:block/blast_furnace_plinth'},lum=("north",) if lit else ()))
    A='t:block/blast_furnace_airain'
    E+= [boite([17,9,-2],[31,11,0],A),                                        # linteau en saillie
         boite([21,2,-6],[27,3,0],A), boite([21,3,-6],[22,5,0],A), boite([26,3,-6],[27,5,0],A)]   # rigole
    if lit: E.append(boite([22,3,-6],[26,3.6,0],'t:block/molten_airain_still',lum=True))
    # tuyère : buse cylindrique d'airain vers le ventilateur
    E+= [boite([-3,21,20],[0,27,28],A), boite([-1,20,19],[0,28,29],A)]
    E.append(cube((-1,1,1),{"east":"create:block/fan_casing","west":"create:block/fan_casing","north":"create:block/fan_side","south":"create:block/fan_side","up":"create:block/fan_side","down":"create:block/fan_side"}))
    E[-1]["from"][0]-=4; E[-1]["to"][0]-=4
    # gueulard : entonnoir d'airain riveté qui dépasse du sommet
    E+= [boite([17,64,17],[31,70,19],A), boite([17,64,29],[31,70,31],A), boite([17,64,19],[19,70,29],A), boite([29,64,19],[31,70,29],A),
         boite([16,70,16],[32,71,32],A,faces=("north","south","east","west","down")),
         boite([19,63.9,19],[29,64,29],{"up":'t:block/blast_furnace_hopper_top'+('_lit' if allume else '')},lum=allume, uvs={"up":FULL},faces=("up",))]
    if allume: E.append(boite([19,64,19],[29,66,29],'t:block/molten_airain_still',lum=True,faces=("up",)))
    return E
W=Image.new('RGBA',(1200,600),(34,30,38,255)); d=ImageDraw.Draw(W); f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
for i,(n,eye,al) in enumerate((("Haut-fourneau à froid",[-1,0.62,-1.15],False),("En marche",[-1,0.62,-1.15],True))):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    W.alpha_composite(rendre(fourneau(al),{},560),(i*600+20,36)); d.text((i*600+300,18),n,font=f,fill=(235,215,170),anchor='mm')
W.save(sys.argv[1])
