# Airain v2 : métal poli, luxueux, sans pixels d'usure. Le temps le fait virer doucement au rouge impérial.
import os, math
from PIL import Image
exec(open('airain_textures.py').read().split('# ---------- bloc d')[0])   # reprend les outils (bruit, melange, ecrire…)
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex'
# 0 = trait sombre … 6 = reflet blanc doré
OR=[(62,36,22),(104,62,34),(146,96,50),(184,134,68),(216,172,94),(240,208,136),(255,240,196)]
ROUGE=[(52,14,16),(92,26,26),(134,42,36),(170,66,48),(202,100,68),(230,148,110),(250,206,180)]
def teinte(i,t):
    i=max(0,min(6,i)); return melange(OR[i],ROUGE[i],t)
T=[0.0,0.28,0.58,0.92]       # neuf → doré-rouge → rouge brun → rouge impérial
def rendre_carte(carte,t):
    h=len(carte); w=len(carte[0]); im=Image.new('RGBA',(w,h)); p=im.load()
    for y in range(h):
        for x in range(w):
            v=carte[y][x]
            if v is None: p[x,y]=(0,0,0,0); continue
            # valeurs fractionnaires : dégradés doux entre deux teintes
            a=int(v); f=v-a
            p[x,y]=melange(teinte(a,t),teinte(a+1,t),f)+(255,)
    return im
def reflet(x,y,force=1.0):
    """Reflet de métal poli : bandes diagonales douces (comme le bloc d'or)."""
    d=(x+y)
    return force*(0.9*math.exp(-((d-9)/2.2)**2)+0.5*math.exp(-((d-20)/1.6)**2))
def plaque(x0,y0,x1,y1,carte,base=3.0,force=1.0):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            v=base+reflet(x-x0,y-y0,force)*1.6-((y-y0)/(y1-y0+1))*0.5
            if y==y0 or x==x0: v=5.2
            if y==y1 or x==x1: v=1.2
            if (x,y)==(x0,y0): v=5.8
            if (x,y)==(x1,y1): v=0.6
            if y==y0+1 and x0<x<x1: v=max(v,4.4)
            carte[y][x]=v
def vide(): return [[3.0]*16 for _ in range(16)]
def bloc():
    c=vide(); plaque(0,0,15,15,c,3.0,1.2); return c
def riveted():
    c=vide(); plaque(0,0,15,7,c,3.0); plaque(0,8,15,15,c,3.0)
    for (x,y) in [(2,3),(12,3),(2,11),(12,11)]:
        c[y][x]=6; c[y][x+1]=4.4; c[y+1][x]=3.6; c[y+1][x+1]=1.4
    return c
def cut():
    c=vide()
    for (x,y) in [(0,0),(8,0),(0,8),(8,8)]: plaque(x,y,x+7,y+7,c,3.0,0.8)
    return c
def chiseled():
    """Airain ciselé : l'engrenage de l'Empire en relief, éclairé en haut à gauche."""
    c=vide(); plaque(0,0,15,15,c,2.4,0.5)
    def dans(x,y):
        dx,dy=x-7.5,y-7.5; d=(dx*dx+dy*dy)**.5; a=math.atan2(dy,dx)
        return (d<=4.7 or (math.cos(a*8)>0.15 and d<=6.3)) and d>=1.9
    for y in range(2,14):
        for x in range(2,14):
            if dans(x,y):
                if not dans(x-1,y) or not dans(x,y-1): c[y][x]=5.6
                elif not dans(x+1,y) or not dans(x,y+1): c[y][x]=2.0
                else: c[y][x]=4.0
            elif dans(x-1,y-1): c[y][x]=1.2                 # ombre portée
    return c
def grate():
    c=[[None]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            bord = x in (0,15) or y in (0,15)
            barre = x in (5,10) or y in (5,10)
            if bord: c[y][x]=5.2 if (x==0 or y==0) else 1.2
            elif barre: c[y][x]=(4.6 if (x==5 or y==5) else 2.6)+reflet(x,y,0.3)
    for (x,y) in [(5,5),(10,5),(5,10),(10,10)]:            # boutons aux croisements
        c[y][x]=6.0
    c[0][0]=5.8; c[15][15]=0.6
    return c
def pillar_side():
    c=vide()
    for y in range(16):
        for x in range(16):
            f=x%4
            c[y][x]=[4.6,3.6,2.4,1.6][f]+reflet(0,y,0.3)*0.4
    for x in range(16):
        c[0][x]=5.2; c[1][x]=3.8; c[2][x]=1.4; c[13][x]=5.0; c[14][x]=3.6; c[15][x]=1.2
    return c
def pillar_top():
    c=vide()
    for y in range(16):
        for x in range(16):
            d=((x-7.5)**2+(y-7.5)**2)**.5
            lum=((7.5-x)+(7.5-y))/15
            if d>7.0: v=1.6+lum
            elif d>6.0: v=4.8+lum*0.6
            elif d>3.0: v=3.0+lum*1.2
            elif d>2.0: v=5.2
            else: v=2.0
            c[y][x]=v
    return c
STADES=['','exposed_','weathered_','oxidized_']
for s,pre in enumerate(STADES):
    t=T[s]
    for nom,f in (('airain_block',bloc),('riveted_airain',riveted),('cut_airain',cut),('chiseled_airain',chiseled),
                  ('airain_grate',grate),('airain_pillar',pillar_side),('airain_pillar_top',pillar_top)):
        rendre_carte(f(),t).save(f'{OUT}/block/{pre}{nom}.png')
# objets et lanterne, à la nouvelle teinte (neuf)
A=[teinte(i,0) for i in (0,1,2,3,4,5)]
exec(open('airain_textures.py').read().split('# ---------- recoloration')[1].split('# laitier')[0].replace('ecrire(','ecrire(') if False else '')
