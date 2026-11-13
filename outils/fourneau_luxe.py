# Haut-fourneau v3 : briques pourpre impérial lisses, airain rouge impérial poli, filets dorés.
import math
from PIL import Image
exec(open('airain_luxe.py').read().split("STADES=['','exposed_'")[0])
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex'
TI=0.92                                   # teinte « rouge impérial »
def ai(v): a=int(max(0,min(6,v))); f=max(0,min(6,v))-a; return melange(teinte(a,TI),teinte(min(6,a+1),TI),f)
OR_=lambda v: melange(teinte(int(v),0.0),teinte(min(6,int(v)+1),0.0),v-int(v))   # filet doré (airain neuf)
BR=[(28,11,12),(50,19,20),(70,28,27),(88,37,33),(108,49,41),(132,66,54)]       # briques pourpres
def briques_lisses(seed=1):
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y in range(16):
        rang=y//4; ly=y%4
        dec=0 if rang%2==0 else 4
        for x in range(16):
            lx=(x+dec)%8
            if ly==3 or lx==7: c=BR[0]                                  # joint
            else:
                v=3 + (0.9 if ly==0 else 0) - (0.8 if ly==2 else 0) + (0.5 if lx==0 else 0) - (0.4 if lx==6 else 0)
                v+= ((x//8 + rang + seed)%3-1)*0.25                      # légère variation d'une brique à l'autre
                a=int(v); c=melange(BR[a],BR[min(5,a+1)],v-a)
            p[x,y]=c+(255,)
    return im
def suie(im, force=0.55):
    p=im.load()
    for y in range(16):
        for x in range(16):
            p[x,y]=melange(p[x,y][:3],(26,10,10),force*(1-y/16))+(255,)
    return im
def cornier(im, mir=False):
    p=im.load()
    cols=[(13,4.6),(14,3.4),(15,1.4)]
    for y in range(16):
        for x,v in cols: p[x,y]=ai(v)+(255,)
        p[12,y]=melange(p[12,y][:3],(20,8,8),0.5)+(255,)
    for y in (2,7,12): p[14,y]=OR_(5.6)+(255,); p[14,y+1]=ai(1.0)+(255,)       # rivets dorés
    return im
def bande(im, y0, y1, rivets=True):
    p=im.load()
    for x in range(16):
        for y in range(y0,y1+1):
            v=3.2+reflet(x,y-y0,0.5)
            if y==y0: v=5.0
            if y==y1: v=1.2
            p[x,y]=ai(v)+(255,)
        p[x,y0]=OR_(5.0)+(255,)                                          # filet doré sur l'arête
        if y0>0: p[x,y0-1]=melange(p[x,y0-1][:3],(20,8,8),0.45)+(255,)
    if rivets:
        ym=(y0+y1)//2
        for x in (2,7,12): p[x,ym]=OR_(5.8)+(255,); p[x+1,ym+1]=ai(1.0)+(255,)
    return im
def ecr(im,n): im.save(f'{OUT}/block/{n}.png')
ecr(briques_lisses(),'fire_bricks')
ecr(cornier(briques_lisses(2)),'fire_bricks_corner')
ecr(bande(briques_lisses(3),9,15),'blast_furnace_plinth')
ecr(cornier(bande(briques_lisses(4),9,15)),'blast_furnace_plinth_corner')
ecr(bande(briques_lisses(5),11,14),'blast_furnace_hopper_side')
ecr(cornier(bande(briques_lisses(6),11,14)),'blast_furnace_hopper_side_corner')
ecr(suie(briques_lisses(7)),'blast_furnace_top_sooty')
# pièces d'airain des modèles : rouge impérial poli
c=vide(); plaque(0,0,15,15,c,3.0,1.2); rendre_carte(c,TI).save(f'{OUT}/block/blast_furnace_airain.png')
# blason : l'engrenage ciselé, rouge impérial, cerclé d'or, dans les briques
def blason():
    im=briques_lisses(8); p=im.load()
    def dans(x,y):
        dx,dy=x-7.5,y-7.5; d=(dx*dx+dy*dy)**.5; a=math.atan2(dy,dx)
        return (d<=4.9 or (math.cos(a*8)>0.15 and d<=6.4)) and d>=2.0
    for y in range(16):
        for x in range(16):
            d=((x-7.5)**2+(y-7.5)**2)**.5
            if d<=7.4: p[x,y]=ai(2.2+((7.5-x)+(7.5-y))/15*0.8)+(255,)
            if 6.6<d<=7.4: p[x,y]=(OR_(5.2) if (x+y)<15 else OR_(2.2))+(255,)
            if dans(x,y):
                if not dans(x-1,y) or not dans(x,y-1): v=5.6
                elif not dans(x+1,y) or not dans(x,y+1): v=2.0
                else: v=4.2
                p[x,y]=OR_(v)+(255,)                                     # engrenage doré
    return im
ecr(blason(),'blast_furnace_emblem')
def tuyere():
    im=briques_lisses(13); p=im.load()
    for y in range(16):
        for x in range(16):
            d=((x-7.5)**2+(y-7.5)**2)**.5
            if d<6.4: p[x,y]=(OR_(5.0) if (x+y)<15 else ai(1.4))+(255,)
            if d<5.6: p[x,y]=ai(3.4+((7.5-x)+(7.5-y))/15)+(255,)
            if d<3.8: p[x,y]=(30,12,12,255)
            if d<2.2: p[x,y]=(16,6,6,255)
    return im
ecr(tuyere(),'blast_furnace_tuyere')
def coulee(allume):
    im=bande(briques_lisses(17),12,15); p=im.load()
    for y in range(16):
        for x in range(16):
            arche=(y>=4 and 4<=x<=11) and not (y==4 and x in (4,11))
            cadre=(y>=3 and 3<=x<=12) and not arche
            if y>=12: cadre = x in (3,12)
            if cadre: p[x,y]=(OR_(5.0) if x<8 and y<5 else ai(2.0 if x>=8 else 4.0))+(255,)
            if arche:
                if allume:
                    t=(y-4)/11; c=melange((255,226,150),(220,80,30),t)
                    if (x+2*y)%6==0: c=(255,240,190)
                else: c=(22,8,8) if y>8 else (36,14,12)
                p[x,y]=c+(255,)
    return im
ecr(coulee(False),'blast_furnace_taphole'); ecr(coulee(True),'blast_furnace_taphole_lit')
def gueulard(allume):
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            d=max(abs(x-7.5),abs(y-7.5))
            if d>6.5: c=OR_(5.0) if (x==0 or y==0) else ai(1.2)
            elif d>5.5: c=ai(3.6)
            elif d>4.5: c=ai(1.0)
            else:
                c=((255,190,90) if (x*3+y*5)%7 else (255,232,160)) if allume else (22,8,8)
            p[x,y]=c+(255,)
    return im
ecr(gueulard(False),'blast_furnace_hopper_top'); ecr(gueulard(True),'blast_furnace_hopper_top_lit')
print('ok')
