# Trois styles de porte d'airain : A ferronnerie, B coffre-fort, C art déco. Rendus neuf et rouge impérial.
import math
from PIL import Image, ImageDraw, ImageFont
exec(open('airain_luxe.py').read().split("STADES=['','exposed_'")[0])
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/portes'
import os; os.makedirs(OUT,exist_ok=True)
def bord(c, base=3.2):
    plaque(0,0,15,15,c,base,0.7)
def creux_cadre(c,x0,y0,x1,y1):
    """Ouverture : biseau inversé autour (sombre en haut-gauche, clair en bas-droite), intérieur transparent."""
    for y in range(y0-1,y1+2):
        for x in range(x0-1,x1+2):
            if 0<=x<16 and 0<=y<16:
                if x0<=x<=x1 and y0<=y<=y1: c[y][x]=None
                elif y==y0-1 or x==x0-1: c[y][x]=1.2
                else: c[y][x]=5.0
# ---------- A : ferronnerie impériale ----------
def A_haut():
    c=vide(); bord(c)
    # fenêtre en arc
    for y in range(2,15):
        for x in range(2,14):
            dx=x-7.5; arc = y>=6 or (dx*dx+(y-6)**2)<=4.6**2+0.5
            if arc and 3<=x<=12 and 2<=y<=13: c[y][x]=None
    # contour de l'arc
    for y in range(1,15):
        for x in range(1,15):
            if c[y][x] is not None and any(0<=x+a<16 and 0<=y+b<16 and c[y+b][x+a] is None for a,b in ((1,0),(-1,0),(0,1),(0,-1))):
                c[y][x]=5.2 if (x>=8) else 1.6
    # engrenage ajouré au centre de la fenêtre
    def dent(x,y):
        dx,dy=x-7.5,y-8.5; d=(dx*dx+dy*dy)**.5; a=math.atan2(dy,dx)
        return (2.0<=d<=3.6) or (math.cos(a*6)>0.4 and 3.6<d<=4.6)
    for y in range(3,14):
        for x in range(3,13):
            if dent(x,y): c[y][x]=4.4 if (x+y)<16 else 2.6
    for y in range(13,16):
        for x in range(1,15): c[y][x]=c[y][x] if c[y][x] is not None else 3.0
    c[14]=[1.2]+[3.0]*14+[1.2]
    return c
def A_bas():
    c=vide(); bord(c); plaque(2,1,13,14,c,2.8,0.6)
    # pentures en volutes (bandes horizontales qui finissent en spirale)
    for yb in (3,11):
        for x in range(1,10): c[yb][x]=5.0; c[yb+1][x]=1.6
        for (dx,dy,v) in [(10,-1,5.0),(11,-1,5.0),(12,0,5.0),(12,1,1.6),(11,2,1.6),(10,1,5.0)]: c[yb+dy][dx]=v
    c[7][12]=6.0; c[8][12]=4.0; c[7][11]=4.6; c[8][11]=1.4          # poignée en anneau
    c[6][12]=4.6; c[9][12]=1.6
    return c
# ---------- B : coffre-fort ----------
def rivets_bord(c):
    for i in range(1,15,3):
        for (x,y) in ((1,i),(14,i),(i,1),(i,14)):
            c[y][x]=6.0
def B_haut():
    c=vide(); bord(c,3.0)
    for x in range(16):
        for y in (0,1,14,15): c[y][x]=5.0 if y==0 else (3.6 if y==1 else (2.0 if y==14 else 1.0))
    # hublot
    for y in range(16):
        for x in range(16):
            d=((x-7.5)**2+(y-7.5)**2)**.5
            if d<=5.6:
                c[y][x]=(5.4 if (x+y)<15 else 1.6) if d>4.4 else (4.2 if d>3.6 else None)
    for a in range(0,360,45):
        x=int(round(7.5+5.0*math.cos(math.radians(a)))); y=int(round(7.5+5.0*math.sin(math.radians(a))))
        c[y][x]=6.0
    rivets_bord(c)
    return c
def B_bas():
    c=vide(); bord(c,3.0)
    for yb in (3,8,13):
        for x in range(16): c[yb][x]=5.0; c[yb+1][x]=1.4
        for x in (2,6,9,13): c[yb][x]=6.0
    # volant à droite
    for y in range(4,12):
        for x in range(8,16):
            d=((x-11.5)**2+(y-7.5)**2)**.5
            if 2.6<=d<=3.4: c[y][x]=5.6 if (x+y)<19 else 1.8
            if d<1.0: c[y][x]=6.0
            if abs(x-11.5)<0.6 and d<3 or abs(y-7.5)<0.6 and d<3: c[y][x]=4.6
    return c
# ---------- C : art déco ----------
def C_haut():
    c=vide(); bord(c)
    # soleil levant : demi-disque en bas de la fenêtre, rayons de métal sur fond ajouré
    for y in range(2,14):
        for x in range(2,14):
            c[y][x]=None
    cx,cy=7.5,13.5
    for y in range(2,14):
        for x in range(2,14):
            dx,dy=x-cx,y-cy; d=(dx*dx+dy*dy)**.5; a=math.degrees(math.atan2(-dy,dx))
            if d<=3.2: c[y][x]=5.2 if dx<0 else 3.6                                   # soleil
            elif 0<a<180 and (round(a)%30<8): c[y][x]=4.6 if dx<0 else 2.8            # rayons
    for x in range(1,15): c[1][x]=1.4; c[14][x]=5.0
    for y in range(1,15): c[y][1]=1.4; c[y][14]=5.0
    # gradins aux coins supérieurs
    for (x,y) in [(2,2),(3,2),(2,3),(13,2),(12,2),(13,3)]: c[y][x]=4.0
    return c
def C_bas():
    c=vide(); bord(c)
    for y in range(2,14):
        for x in range(2,14):
            c[y][x]=[4.6,3.6,2.4,1.6][(x-2)%4]
    for x in range(2,14): c[2][x]=5.2; c[13][x]=1.2
    # chevron central
    for i in range(6):
        c[7+ (i if i<3 else 5-i)][2+i*2]=6.0
    c[1][1]=5.8
    c[7][13]=6.0; c[8][13]=1.6
    return c
STY={'A':(A_haut,A_bas),'B':(B_haut,B_bas),'C':(C_haut,C_bas)}
for k,(h,b) in STY.items():
    for t,n in ((0.0,'neuf'),(0.92,'rouge')):
        rendre_carte(h(),t).save(f'{OUT}/{k}_{n}_top.png'); rendre_carte(b(),t).save(f'{OUT}/{k}_{n}_bottom.png')
# planche : les trois portes, neuves et rouge impérial, en grand (fond = mur pour voir les ajours)
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
noms={'A':'A · Ferronnerie impériale','B':'B · Coffre-fort','C':'C · Art déco'}
W=Image.new('RGBA',(3*330,560),(34,30,38,255)); d=ImageDraw.Draw(W)
mur=Image.open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/block/stone_bricks.png').convert('RGBA')
for i,k in enumerate('ABC'):
    d.text((i*330+165,20),noms[k],font=f,fill=(235,215,170),anchor='mm')
    for j,n in enumerate(('neuf','rouge')):
        x=i*330+20+j*150; y=50
        fond=Image.new('RGBA',(16,32)); fond.paste(mur,(0,0)); fond.paste(mur,(0,16))
        porte=Image.new('RGBA',(16,32)); porte.paste(Image.open(f'{OUT}/{k}_{n}_top.png'),(0,0)); porte.paste(Image.open(f'{OUT}/{k}_{n}_bottom.png'),(0,16))
        fond.alpha_composite(porte); W.alpha_composite(fond.resize((140,280),Image.NEAREST),(x,y))
        W.alpha_composite(porte.resize((140,280),Image.NEAREST),(x,y+290)) if False else None
W.save('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/rendu_fusion/portes_styles.png')
print('ok')
