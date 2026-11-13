# Textures de détail (1.51) : motifs définis, pas de bruit — panneau à biseau, frise impériale, cannelures, tuyau,
# plaques émaillées, verre, cadran, verre de lanterne.
import math
exec(open('airain_luxe.py').read().split('def bloc():')[0])
from PIL import Image, ImageDraw
def ec(nom,im): im.save(OUT+'/block/'+nom+'.png')
# Contraste doux : deux pixels voisins ne s'écartent jamais de plus d'environ un cran (pas de blanc contre noir).
def panneau():
    """Plaque à cadre de 2 px légèrement en relief, champ poli en retrait, quatre boulons d'angle discrets."""
    c=vide()
    for y in range(16):
        for x in range(16):
            c[y][x]=3.2+0.5*reflet(x,y,0.8)
    for i in range(16):
        c[0][i]=c[i][0]=3.9; c[1][i]=c[i][1]=3.6          # cadre : arêtes éclairées en haut et à gauche
        c[15][i]=c[i][15]=2.6; c[14][i]=c[i][14]=2.9        # … ombrées en bas et à droite
    for i in range(2,14):
        c[2][i]=c[i][2]=2.8; c[13][i]=c[i][13]=3.5          # retrait du champ : ombre portée en haut à gauche
    c[0][15]=c[15][0]=3.2; c[1][14]=c[14][1]=3.2
    for (x,y) in ((1,1),(14,1),(1,14),(14,14)): c[y][x]=4.2 if (x,y)==(1,1) else 3.9
    return c
def frise():
    """Frise pour faces d'au moins 6 px : losanges sur les rangs 5 à 10, filets doux autour."""
    c=vide()
    for y in range(16):
        for x in range(16): c[y][x]=3.1+0.4*reflet(x,y,0.6)
    for x in range(16):
        c[3][x]=3.8; c[4][x]=2.8; c[11][x]=3.6; c[12][x]=2.6
    for x in range(16):
        for y in range(5,11):
            d=abs((x%6)-2.5)+abs(y-7.5)
            if d<=2.6:
                c[y][x]=4.2 if d<=0.8 else (3.8 if ((x%6)<3 and y<8) else (2.7 if ((x%6)>=3 and y>=8) else 3.3))
    return c
def bandeau():
    """Bandeau pour faces minces (2 à 4 px) : période 4, rivet discret tous les 4 px."""
    c=vide()
    for y in range(16):
        k=y%4
        for x in range(16):
            c[y][x]=[3.9,3.4,3.1,2.7][k]
            if k==2 and x%4==1: c[y][x]=3.9
            if k==2 and x%4==2: c[y][x]=2.6
    return c
def lignes():
    """Rainures horizontales douces (pièces longues ou inclinées : rien ne s'étire)."""
    c=vide()
    for y in range(16):
        for x in range(16): c[y][x]=[3.8,3.4,3.1,2.8][y%4]
    return c
def cannelures():
    """Cannelures verticales de 3 px : arête claire à gauche, creux, ombre à droite, sans écart brutal."""
    c=vide()
    for y in range(16):
        for x in range(16): c[y][x]=[3.9,3.3,2.8][x%3]
    return c
def tuyau():
    """Tuyau de 6 px : reflet doux en haut, ombre douce en bas (rangs 5 à 10)."""
    c=vide()
    g=[3.6,4.1,3.8,3.3,2.9,2.6]
    for y in range(16):
        for x in range(16): c[y][x]=g[y-5] if 5<=y<=10 else 3.2
    return c
for nom,f in (('airain_panel',panneau),('airain_frieze',frise),('airain_band',bandeau),('airain_grooves',lignes),('airain_fluted',cannelures),('airain_pipe',tuyau)):
    for s,p in enumerate(['','exposed_','weathered_','oxidized_']):
        ec(p+nom,rendre_carte(f(),T[s]))
# ---------------------------------------------------------------- émaux, verre, cadran (teintes fixes)
EM=(118,22,22); EM2=(150,34,30); ORf=(232,186,92); ORs=(150,96,40)
def plaque_emaillee(picto):
    im=Image.new('RGBA',(16,16),EM+(255,)); d=ImageDraw.Draw(im)
    for y in range(2,14):
        for x in range(2,14):
            if (x+y)<12: im.putpixel((x,y),EM2+(255,))
    d.rectangle([0,0,15,15],outline=ORs); d.rectangle([1,1,14,14],outline=ORf)
    for p in ((1,1),(14,1),(1,14),(14,14)): im.putpixel(p,(255,236,180,255))
    G=ORf+(255,)
    if picto=='fleche': d.polygon([(3,7),(8,7),(8,4),(12,8),(8,12),(8,9),(3,9)],fill=G)
    elif picto=='forge':
        d.rectangle([4,4,11,6],fill=G); d.rectangle([7,7,8,12],fill=G); d.point((11,7),fill=G)
    elif picto=='danger':
        d.polygon([(8,3),(13,12),(3,12)],outline=G); d.line([(8,6),(8,9)],fill=G); d.point((8,11),fill=G)
    elif picto=='sortie':
        d.rectangle([4,3,9,12],outline=G); d.line([(10,8),(13,8)],fill=G); d.point((12,7),fill=G); d.point((12,9),fill=G); d.point((7,8),fill=G)
    elif picto=='stock':
        d.rectangle([4,5,11,11],outline=G); d.line([(4,8),(11,8)],fill=G); d.line([(7,5),(7,8)],fill=G); d.line([(8,5),(8,8)],fill=G)
    elif picto=='engrenage':
        for a in range(8):
            x=8+4*math.cos(a*math.pi/4); y=8+4*math.sin(a*math.pi/4); d.rectangle([int(x)-1,int(y)-1,int(x),int(y)],fill=G)
        d.ellipse([5,5,10,10],outline=G)
    return im
for p in ('fleche','forge','danger','sortie','stock','engrenage'): ec('sign_'+p,plaque_emaillee(p))
def verre():
    im=Image.new('RGBA',(16,16),(196,214,212,90)); px=im.load()
    for y in range(16):
        for x in range(16):
            d=x+y
            if d in (5,6,20): px[x,y]=(240,248,246,150)
            if d==21: px[x,y]=(230,240,238,120)
    return im
ec('airain_glass',verre())
def cadran():
    im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([0,0,15,15],fill=(236,226,200,255),outline=(150,96,40,255))
    for a in range(-135,136,45):
        r=math.radians(a-90); x0=7.5+6*math.cos(r); y0=7.5+6*math.sin(r); x1=7.5+4.8*math.cos(r); y1=7.5+4.8*math.sin(r)
        d.line([(x0,y0),(x1,y1)],fill=(60,40,30,255))
    d.arc([2,2,13,13],20,60,fill=(170,40,30,255))
    return im
ec('gauge_face',cadran())
def lanterne_rouge():
    """Verre rouge : cœur clair au centre, bord sombre, croisillons d'airain."""
    im=Image.new('RGBA',(16,16)); px=im.load()
    for y in range(16):
        for x in range(16):
            d=math.hypot(x-7.5,(y-8.5)*0.8)/8
            v=max(0,1-d)
            px[x,y]=(int(150+105*v),int(30+150*v**2),int(20+90*v**3),255)
    for y in range(16): px[0,y]=px[15,y]=(150,96,40,255)
    for x in range(16): px[x,0]=px[x,15]=(150,96,40,255)
    for y in range(1,15): px[7,y]=px[8,y]=(184,134,68,255) if y%5 else (240,208,136,255)
    return im
ec('lamp_red_glass',lanterne_rouge())
def lampe_chaude():
    im=Image.new('RGBA',(16,16)); px=im.load()
    for y in range(16):
        for x in range(16):
            v=max(0,1-math.hypot(x-7.5,y-7.5)/9)
            px[x,y]=(255,int(190+60*v),int(110+120*v**2),255)
    return im
ec('lamp_warm',lampe_chaude())
print('ok')
