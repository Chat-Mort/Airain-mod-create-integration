# Rendus 3D des quatre afficheurs impériaux : tableau émaillé (et plaque de gare suspendue), cadran, totaliseur, enseigne.
import math, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import rendu3d as rm
from rendu3d import norm, rendre
exec(open('livre_maquette.py').read().split('def couper')[0])
D='/home/claude/maquettes/tex/'; os.makedirs(D,exist_ok=True)
M='airain:block/airain_block'; RIV='airain:block/riveted_airain'; BD='airain:block/airain_band'; PL='airain:block/airain_beam_plate'
CH='airain:block/chiseled_airain'; FL='airain:block/airain_beam_flange'; WB='airain:block/airain_beam_web'; BAR='airain:block/airain_lattice_bar'
MUR='minecraft:block/bricks'; SOMBRE='airain:block/oxidized_airain_block'
ALL=("north","south","east","west","up","down")
def b(f,t,tex,faces=ALL,uv=None,rot=None):
    fc={}
    for k in faces:
        x0,y0,z0=f; x1,y1,z1=t
        a,h={'north':(x1-x0,y1-y0),'south':(x1-x0,y1-y0),'east':(z1-z0,y1-y0),'west':(z1-z0,y1-y0),'up':(x1-x0,z1-z0),'down':(x1-x0,z1-z0)}[k]
        a,h=min(16,a),min(16,h); u=(16-a)/2; v=(16-h)/2
        fc[k]={'texture':tex,'uv':(uv or {}).get(k,[u,v,u+a,v+h])}
    e={'from':list(f),'to':list(t),'faces':fc}
    if rot: e['rotation']=rot
    return e
def hd(nom): return 'hd:'+D+nom+'.png'
FULL=[0,0,16,16]
def vue(E,eye,taille=1000,echelle=None,cache=None):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    return rendre(E,{},taille,echelle)
def mur(x0,x1,y0,y1,z=16,ep=16):
    return [b((x*16,y*16,z),(x*16+16,y*16+16,z+ep),MUR,("north","up","west","east")) for x in range(x0,x1) for y in range(y0,y1)]
def sol(x0,x1,z0,z1,t='minecraft:block/polished_andesite'):
    return [b((x*16,-1,z*16),(x*16+16,0,z*16+16),t,("up",)) for x in range(x0,x1) for z in range(z0,z1)]
# ---------------------------------------------------------------- écriture haute définition
def txt_img(t,col,gras=False):
    tmp=Image.new('RGBA',(largeur(t)+len(t)+4,16),(0,0,0,0)); ecrire(tmp,t,1,5,tuple(col[:3]),gras); return tmp.crop(tmp.getbbox() or (0,0,1,1)) if False else tmp
def poser(im,t,x,y,col,ech,gras=False,ancre='g'):
    s=txt_img(t,col,gras); s=s.resize((s.width*ech,s.height*ech),Image.NEAREST)
    w=(largeur(t)+(len(t) if gras else 0))*ech
    y-=3*ech
    if ancre=='c': x-=w/2
    if ancre=='d': x-=w
    im.alpha_composite(s,(int(x),int(y)))
CR=(236,228,206,255); RO=(214,64,48,255); OR=(232,196,110,255); EM=(26,26,32,255)
A=dict(c=(252,233,183),l=(243,214,148),m=(201,154,81),d=(168,118,60),s=(112,68,37),ss=(87,51,29),rv=(255,240,196))
