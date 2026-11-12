import sys, json, copy; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
from rendu_modele import *
CR='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/create-src/src/main/resources/assets/create/models/block/'
ALL=("north","south","east","west","up","down")
def box(fr,to,t,faces=ALL,lum=False,rot=None,uv=None):
    if t=="fenetre" and uv is None: uv={k:[0,0,16,16] for k in ALL}
    f={k:({"texture":t}|({"neoforge_data":{"block_light":15}} if lum else {})|({"uv":uv[k]} if uv and k in uv else {})) for k in faces}
    e={"from":fr,"to":to,"faces":f}
    if lum: e["shade"]=False
    if rot: e["rotation"]=rot
    return e
def deplace(els,dx,dy,dz):
    out=[]
    for e in copy.deepcopy(els):
        e['from']=[a+b for a,b in zip(e['from'],(dx,dy,dz))]; e['to']=[a+b for a,b in zip(e['to'],(dx,dy,dz))]
        if 'rotation' in e: e['rotation']['origin']=[a+b for a,b in zip(e['rotation']['origin'],(dx,dy,dz))]
        out.append(e)
    return out
COG=json.load(open(CR+'cogwheel_shaftless.json'))['elements']
SHAFT_N=box([6,6,-1],[10,10,8],"axis",faces=("east","west","up","down"))|{}
SHAFT_N["faces"]["north"]={"texture":"axis_top"}
T={"laiton":"create:block/brass_casing","andesite":"create:block/andesite_casing","cuivre":"create:block/copper_casing","bloc_laiton":"create:block/brass_block",
   "fenetre":"create:block/fluid_tank_window_single","cuve_haut":"create:block/fluid_tank_top","pales":"create:block/fan_blades","grille":"create:block/fan_casing",
   "source":"ars_nouveau:block/source_still","pierre":"ars_nouveau:block/smooth_sourcestone","dore":"ars_nouveau:block/gilded_sourcestone_small_bricks",
   "gemme":"ars_nouveau:block/source_gem_block","cristal":"minecraft:block/amethyst_cluster","axis":"create:block/axis","axis_top":"create:block/axis_top",
   "1_2":"create:block/cogwheel","tuyau":"create:block/glass_fluid_pipe","tuyau_cuivre":"create:block/encased_pipe","sombre":"create:block/andesite_casing","magma":"minecraft:block/magma","glace":"minecraft:block/packed_ice"}
G45=lambda o:{"origin":o,"axis":"y","angle":45}
# --- Turbine : à l'avant le rotor dans sa grille, à l'arrière la cuve de source qui l'alimente
turbine=[
 box([0,0,0],[16,4,3],"laiton"),box([0,12,0],[16,16,4],"laiton"),box([0,4,0],[4,12,3],"laiton"),box([12,4,0],[16,12,3],"laiton"),   # avant creusé autour de l'arbre
 box([0,0,3],[16,12,6],"laiton"),box([4,4,2.99],[12,12,3],"sombre",faces=("north",)),
 box([0,0,6],[16,2,16],"laiton"),                                                                                                       # cuve arrière
 box([0,2,15],[1,12,16],"laiton"),box([15,2,15],[16,12,16],"laiton"),
 box([1,2,7],[15,11,15],"source",lum=True),box([0.5,2,6.5],[15.5,12,15.5],"fenetre",faces=("east","west","south")),
 box([0,12,4],[4,16,16],"laiton"),box([12,12,4],[16,16,16],"laiton"),box([4,12,12],[12,16,16],"laiton"),                                # dessus, creusé pour la cheminée
 box([4,11.99,4],[12,12,12],"sombre",faces=("up",)),
 SHAFT_N]
ROTOR_TURBINE=[box([4,14.5,4],[12,14.51,12],"pales",faces=("up","down")),box([7,12,7],[9,15,9],"bloc_laiton")]
# --- Sourcelink mécanique : la rotation fait tourner un engrenage, qui fait tourner la gemme
sourcelink=[box([0,0,0],[16,8,16],"andesite"),box([0,0,0],[16,8,0.01],"laiton",faces=("north",)),
 *deplace(COG,0,3,0),
 box([5,12.5,5],[11,14,11],"pierre"),box([4,14,4],[12,15,12],"dore"),
 box([6,16,6],[10,20,10],"gemme",lum=True,rot=G45([8,18,8])),SHAFT_N]
# --- Diffuseur : un brasero de laiton, plein de source qui fume ; éteint, le bassin est vide
def diffuseur(on):
    e=[box([2,0,2],[4,3,4],"bloc_laiton"),box([12,0,2],[14,3,4],"bloc_laiton"),box([2,0,12],[4,3,14],"bloc_laiton"),box([12,0,12],[14,3,14],"bloc_laiton"),
       box([1,3,1],[15,4,15],"laiton"),
       box([1,4,1],[15,9,2],"laiton"),box([1,4,14],[15,9,15],"laiton"),box([1,4,2],[2,9,14],"laiton"),box([14,4,2],[15,9,14],"laiton")]
    if on:
        e+=[box([2,4,2],[14,7.5,14],"source",lum=True),
            box([3,7,4],[7,12,4.01],"cristal",faces=("north","south"),rot=G45([5,9,4])),box([10,7,11],[13,11,11.01],"cristal",faces=("north","south"),rot=G45([11.5,9,11])),
            box([9,7,3],[12,10,3.01],"cristal",faces=("north","south"),rot={"origin":[10.5,8.5,3],"axis":"y","angle":-45})]
    else:
        e+=[box([2,4,2],[14,4.5,14],"pierre"),box([4,4.5,5],[7,8,5.01],"cristal",faces=("north","south"),rot=G45([5.5,6,5]))]
    return e
# --- Condenseur : une cuve de Create (fenêtres) pleine d'Écho liquide, des raccords de tuyau, l'arrivée de source au-dessus
def condenseur(evap):
    # condense : socle givré (serpentin froid), cuve pleine, la source descend par le tuyau
    # évapore : socle chauffé au rouge (évents de magma), cuve presque vide, couvercle doré relevé et vapeur
    niveau=5 if evap else 12
    socle="magma" if evap else "glace"
    e=[box([0,0,0],[16,3,16],"cuivre",faces=("down",)),box([0,0,0],[16,3,16],socle,faces=("north","south","east","west","up"),lum=evap),
       box([0,14,0],[16,16,16],"cuivre",faces=("north","south","east","west","down")),box([0,14,0],[16,16,16],"cuve_haut",faces=("up",)),
       box([0,3,0],[2,14,2],"cuivre"),box([14,3,0],[16,14,2],"cuivre"),box([0,3,14],[2,14,16],"cuivre"),box([14,3,14],[16,14,16],"cuivre"),
       box([0.5,3,0.5],[15.5,14,15.5],"fenetre",faces=("north","south","east","west")),
       box([-1,5,5],[0.5,11,11],"tuyau_cuivre",faces=("north","south","up","down","west")),box([15.5,5,5],[17,11,11],"tuyau_cuivre",faces=("north","south","up","down","east")),
       box([6,16,6],[10,19,10],"tuyau",faces=("north","south","east","west"))]
    if evap:
        e+=[box([5,19,5],[11,20.5,11],"pierre"),box([4,22.5,4],[12,23.5,12],"dore"),box([7,20.5,7],[9,22.5,9],"bloc_laiton"),
            box([6.5,20.5,6.5],[9.5,22.5,9.5],"gemme",lum=True,rot=G45([8,21.5,8]))]
    else:
        e+=[box([5,19,5],[11,20.5,11],"pierre"),box([6.5,20.5,6.5],[9.5,23,9.5],"gemme",lum=True,rot=G45([8,21.75,8]))]
    return e
cases=[("Turbine d'Écho",turbine),("Sourcelink mécanique",sourcelink),("Diffuseur d'Écho (éteint)",diffuseur(False)),("Diffuseur d'Écho (allumé)",diffuseur(True)),
       ("Condenseur (condense)",condenseur(False)),("Condenseur (évapore)",condenseur(True))]
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
Tl=360; W=Image.new('RGBA',(Tl*3,(Tl+40)*2),(34,30,38,255)); d=ImageDraw.Draw(W); f=ImageFont.truetype(FB,20)
for i,(nom,e) in enumerate(cases):
    im=rendre(e,T,Tl,echelle=12.5)
    x=(i%3)*Tl; y=(i//3)*(Tl+40)
    W.alpha_composite(im,(x,y+30)); d.text((x+Tl/2,y+14),nom,font=f,fill=(235,215,170),anchor='mm')
W.save(sys.argv[1])
json.dump({n:e for n,e in cases},open('design_v2.json','w'))
