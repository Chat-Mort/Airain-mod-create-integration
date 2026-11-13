# Textures de l'airain (métal de l'Empire) : palette, quatre stades de patine, blocs, objets, haut-fourneau.
import random, os
from PIL import Image
OUT=os.environ.get('OUT','/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex')
MC='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/'
CR='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/create-src/src/main/resources/assets/create/textures/'
os.makedirs(OUT+'/block',exist_ok=True); os.makedirs(OUT+'/item',exist_ok=True)
# bronze sombre à reflets rouges : 0 = trait le plus sombre … 5 = reflet
A=[(62,36,22),(104,62,34),(146,96,50),(184,134,68),(216,172,94),(240,208,136)]
# vert-de-gris : 0 … 4
P=[(46,80,68),(64,106,90),(84,134,112),(108,162,136),(146,192,166)]
def melange(c,d,t): return tuple(int(c[i]*(1-t)+d[i]*t) for i in range(3))
def bruit(seed,w=16,h=16):
    r=random.Random(seed); return [[r.random() for x in range(w)] for y in range(h)]
def lisse(n,passes=2):
    h=len(n); w=len(n[0])
    for _ in range(passes):
        n=[[(n[y][x]*2+n[y][(x+1)%w]+n[y][(x-1)%w]+n[(y+1)%h][x]+n[(y-1)%h][x])/6 for x in range(w)] for y in range(h)]
    return n
def patiner(carte, stade, seed, relief=None):
    """carte : indices 0..5 (None = transparent). stade 0 neuf, 1 terni, 2 patiné, 3 vert-de-gris.
    Le vert-de-gris gagne d'abord les creux (indices bas), les reliefs (relief[y][x] vrai) restent bronze plus longtemps."""
    h=len(carte); w=len(carte[0])
    n=lisse(bruit(seed,w,h),2)
    seuil=[1.1,0.9,0.52,0.16][stade]
    im=Image.new('RGBA',(w,h)); p=im.load()
    for y in range(h):
        for x in range(w):
            i=carte[y][x]
            if i is None: p[x,y]=(0,0,0,0); continue
            c=A[i]
            if stade>=1: c=melange(c,(70,52,42),0.30 if stade==1 else 0.36)   # terni : plus brun, moins brillant
            haut=relief[y][x] if relief else (i>=5)
            v=n[y][x]+ (0.35 if haut else 0) - i*0.04
            if v>seuil-0.0 and stade>=1:
                pi=max(0,min(4,i-1+(1 if n[y][x]>0.6 else 0)))
                c=P[pi] if stade>=2 or n[y][x]>0.93 else melange(c,P[pi],0.5)
            p[x,y]=c+(255,)
    return im
def ecrire(im,chemin): im.save(f'{OUT}/{chemin}.png')
STADES=['','exposed_','weathered_','oxidized_']
# ---------- bloc d'airain : plaque martelée, biseau ----------
def bloc():
    n=bruit(11); c=[[3]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if n[y][x]>0.93: c[y][x]=4
            elif n[y][x]<0.06: c[y][x]=2
    for i in range(16):
        c[0][i]=4; c[i][0]=4; c[15][i]=1; c[i][15]=1
    c[0][0]=5; c[15][15]=0
    for (x,y) in [(4,5),(10,9),(6,11),(11,3)]:   # bosses du martelage
        c[y][x]=5; c[y+1][x+1]=2
    return c
def riveted():
    c=bloc()
    for x in range(1,15): c[7][x]=1; c[8][x]=4        # joint entre deux plaques
    rel=[[False]*16 for _ in range(16)]
    for (x,y) in [(2,2),(11,2),(2,11),(11,11)]:
        m=[[4,5,3],[4,3,2],[2,1,1]]
        for dy in range(3):
            for dx in range(3): c[y+dy][x+dx]=m[dy][dx]; rel[y+dy][x+dx]=True
        c[y+3 if y+3<16 else y][x+1]=1
    return c,rel
def cut():
    n=bruit(23); c=[[3]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            lx,ly=x%8,y%8
            v=3
            if n[y][x]>0.85: v=4
            if n[y][x]<0.1: v=2
            if ly==0 or lx==0: v=4
            if ly==7 or lx==7: v=1
            if (lx,ly)==(0,0): v=5
            c[y][x]=v
    return c
def grate():
    c=[[None]*16 for _ in range(16)]; rel=[[False]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            bord = x in (0,15) or y in (0,15)
            barre = x in (5,10) or y in (5,10)
            if bord or barre:
                c[y][x]= 4 if (y==0 or x==0 or (barre and (x in (5,) or y in (5,)))) else (1 if (y==15 or x==15) else 2)
                if bord: c[y][x]= 4 if (y==0 or x==0) else 1
                if barre and not bord: c[y][x]= 3 if (x in (5,10) and y in (5,10)) else (4 if (x==5 or y==5) else 2)
                if x in (5,10) and y in (5,10): c[y][x]=5; rel[y][x]=True
    return c,rel
def pillar_side():
    n=bruit(31); c=[[3]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            f=x%4
            v=[4,3,2,1][f]
            if n[y][x]>0.9: v=min(5,v+1)
            c[y][x]=v
    for x in range(16):
        c[0][x]=4; c[1][x]=3; c[2][x]=1; c[13][x]=4; c[14][x]=3; c[15][x]=1
    return c
def pillar_top():
    c=[[3]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            d=((x-7.5)**2+(y-7.5)**2)**.5
            v=3
            if d>7.2: v=1
            elif d>6.2: v=4
            elif d>5.2: v=2
            elif d>3.2: v=3
            elif d>2.2: v=4
            else: v=2
            if (x+y)%7==0 and 3.2<d<5.2: v=4
            c[y][x]=v
    for i in range(16): c[0][i]=max(c[0][i],1); c[i][0]=c[i][0]
    return c
for s,pre in enumerate(STADES):
    ecrire(patiner(bloc(),s,101),f'block/{pre}airain_block')
    cr,rel=riveted(); ecrire(patiner(cr,s,102,rel),f'block/{pre}riveted_airain')
    ecrire(patiner(cut(),s,103),f'block/{pre}cut_airain')
    cg,rg=grate(); ecrire(patiner(cg,s,104,rg),f'block/{pre}airain_grate')
    ecrire(patiner(pillar_side(),s,105),f'block/{pre}airain_pillar')
    ecrire(patiner(pillar_top(),s,106),f'block/{pre}airain_pillar_top')
# ---------- recoloration par luminance (garde les formes de Minecraft / Create) ----------
def recolorer(src, rampe, seuil_alpha=10, crop=True):
    im=Image.open(src).convert('RGBA')
    if crop: im=im.crop((0,0,im.width,im.width))
    px=im.load(); vals=sorted({sum(px[x,y][:3]) for y in range(im.height) for x in range(im.width) if px[x,y][3]>seuil_alpha})
    out=Image.new('RGBA',im.size); q=out.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=px[x,y]
            if a<=seuil_alpha: q[x,y]=(0,0,0,0); continue
            k=vals.index(r+g+b)/max(1,len(vals)-1)
            q[x,y]=rampe[min(len(rampe)-1,int(k*len(rampe)))]+(a,)
    return out
ecrire(recolorer(MC+'item/iron_ingot.png',A),'item/airain_ingot')
ecrire(recolorer(MC+'item/iron_nugget.png',A),'item/airain_nugget')
def plaque():
    # plaque vue de biais, comme les plaques de Create : losange aplati, bord clair en haut, épaisseur sombre en bas
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            u=x+y*0.0; 
            haut = 3+ (x)*0.0
            if 2<=x<=13 and 4<=y<=11 and (x-2)+(11-y)>=2 and (13-x)+(y-4)>=2:
                c=A[3]
                if (x-2)+(11-y)==2 or y==4: c=A[5]
                elif (13-x)+(y-4)==2 or y==11: c=A[1]
                elif (x*7+y*3)%11==0: c=A[4]
                p[x,y]=c+(255,)
            if 3<=x<=14 and y==12 and (14-x)+(12-4)>=2 and x>=4: p[x,y]=A[0]+(255,)
    return im
ecrire(plaque(),'item/airain_sheet')
# lanterne : on garde la flamme, seul le fer devient airain
def lanterne():
    im=Image.open(MC+'block/lantern.png').convert('RGBA'); px=im.load()
    out=im.copy(); q=out.load()
    metal=lambda c: c[3]>0 and not (c[0]>c[2]+40)          # tout sauf la flamme (jaune-orange)
    gris=sorted({sum(px[x,y][:3]) for y in range(im.height) for x in range(im.width) if metal(px[x,y])})
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=px[x,y]
            if metal(px[x,y]):
                k=gris.index(r+g+b)/max(1,len(gris)-1); q[x,y]=A[min(5,int(k*6))]+(a,)
    return out
ecrire(lanterne(),'block/airain_lantern')
# engrenage d'airain : roue dentée, moyeu de cuivre rouge
def engrenage():
    im=Image.new('RGBA',(16,16)); p=im.load()
    import math
    for y in range(16):
        for x in range(16):
            dx,dy=x-7.5,y-7.5; d=(dx*dx+dy*dy)**.5; a=math.atan2(dy,dx)
            dent=(math.cos(a*8)>0.2)
            if d<=5.2 or (dent and d<=7.3):
                if d<1.6: c=(70,30,22)
                elif d<2.8: c=(176,82,54)                  # moyeu de cuivre rouge
                elif d<3.6: c=A[1]
                else:
                    lum=0.5+0.5*(-dx-dy)/max(1,d)*0.9
                    c=A[2+int(lum*3.2)]
                if d>6.6 or (d>4.6 and not dent and d<=5.2): c=A[0] if (dx+dy)>0 else A[1]
                p[x,y]=c+(255,)
    return im
ecrire(engrenage(),'item/airain_gear')
# laitier : scorie vitreuse sombre, une braise
def laitier():
    src=recolorer(MC+'item/coal.png',[(30,28,32),(48,44,50),(70,64,70),(98,88,92),(132,118,112)])
    p=src.load(); p[9,6]=(232,120,52,255); p[10,7]=(255,170,80,255)
    return src
ecrire(laitier(),'item/slag')
# ---------- haut-fourneau : briques réfractaires (chamotte), suie ----------
R=[(70,54,44),(118,96,76),(168,140,108),(196,170,132),(220,198,160),(238,222,188)]
ecrire(recolorer(MC+'item/brick.png',R),'item/fire_brick')
def briques(seed=7, suie=0.0):
    src=Image.open(MC+'block/bricks.png').convert('RGBA'); px=src.load()
    n=lisse(bruit(seed),1); out=Image.new('RGBA',(16,16)); q=out.load()
    for y in range(16):
        for x in range(16):
            r,g,b,a=px[x,y]; L=(r+g+b)/3
            if L<95: c=(92,80,72)                                           # joint de mortier
            else:
                k=min(5,max(0,int((L-95)/20)))
                c=R[min(5,2+k//2+(1 if n[y][x]>0.62 else 0))]
            if suie: c=melange(c,(40,34,30),max(0,suie-(y/16)*suie)*(0.6+0.4*n[y][x]))
            q[x,y]=c+(255,)
    return out
ecrire(briques(),'block/fire_bricks')
ecrire(briques(9,0.8),'block/blast_furnace_top_sooty')
def tuyere():
    im=briques(13).copy(); p=im.load()
    for y in range(16):
        for x in range(16):
            d=((x-7.5)**2+(y-7.5)**2)**.5
            if d<6.2: p[x,y]=(A[4] if (x+y)<15 else A[1])+(255,)
            if d<5.0: p[x,y]=A[3]+(255,)
            if d<3.6: p[x,y]=(36,24,20,255)
            if d<2.0: p[x,y]=(20,14,12,255)
    return im
ecrire(tuyere(),'block/blast_furnace_tuyere')
def coulee(allume):
    im=briques(17).copy(); p=im.load()
    for y in range(16):
        for x in range(16):
            # cadre d'airain en arc, ouverture en bas
            arche = (y>=5 and 3<=x<=12) and not (y==5 and x in (3,12))
            cadre = (y>=4 and 2<=x<=13) and not arche
            if cadre and y>=4: p[x,y]=(A[4] if x<8 else A[2])+(255,)
            if arche:
                if allume:
                    t=(y-5)/10
                    c=melange((255,214,120),(214,72,26),t) if (x+y)%5 else (255,236,170)
                else: c=(30,22,20) if y>9 else (44,32,28)
                p[x,y]=c+(255,)
    for x in range(2,14): p[x,15]=A[1]+(255,)
    return im
ecrire(coulee(False),'block/blast_furnace_taphole')
ecrire(coulee(True),'block/blast_furnace_taphole_lit')
def gueulard_dessus(allume):
    im=Image.new('RGBA',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            d=max(abs(x-7.5),abs(y-7.5))
            if d>6.5: c=A[1] if (x==15 or y==15) else A[4]
            elif d>5.5: c=A[2]
            elif d>4.5: c=(48,36,30)
            else:
                c=((250,150,60) if allume and (x*3+y*5)%7 else ((230,100,40) if allume else (26,18,16)))
            p[x,y]=c+(255,)
    for (x,y) in [(1,1),(14,1),(1,14),(14,14)]: p[x,y]=A[5]+(255,)
    return im
ecrire(gueulard_dessus(False),'block/blast_furnace_hopper_top')
ecrire(gueulard_dessus(True),'block/blast_furnace_hopper_top_lit')
def bande_airain():
    im=briques(19).copy(); p=im.load()
    for x in range(16):
        for y in (12,13,14): p[x,y]=(A[4] if y==12 else (A[3] if y==13 else A[1]))+(255,)
        if x in (2,7,12): p[x,13]=A[5]+(255,)
    return im
ecrire(bande_airain(),'block/blast_furnace_hopper_side')
# airain liquide : la lave recolorée en métal en fusion (animation conservée)
def liquide(nom):
    im=Image.open(MC+f'block/{nom}.png').convert('RGBA'); px=im.load()
    out=Image.new('RGBA',im.size); q=out.load()
    rampe=[(120,40,20),(170,70,30),(206,104,46),(232,140,64),(248,184,96),(255,226,150)]
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=px[x,y]; L=(r+g*2+b)/4
            q[x,y]=rampe[min(5,int(L/256*6.5))]+(255,)
    return out
ecrire(liquide('lava_still'),'block/molten_airain_still'); ecrire(liquide('lava_flow'),'block/molten_airain_flow')
import shutil
for n in ('lava_still','lava_flow'): shutil.copy(MC+f'block/{n}.png.mcmeta',f'{OUT}/block/molten_airain_{n.split("_")[1]}.png.mcmeta')
print('ok')
# ---------- haut-fourneau v2 : socle riveté, cornières d'airain, couronne ----------
def cornier(im):
    """Cornière d'airain sur le bord droit de la face (le coin du fourneau), rivetée."""
    p=im.load()
    for y in range(16):
        p[13,y]=A[4]+(255,); p[14,y]=A[3]+(255,); p[15,y]=A[1]+(255,)
        p[12,y]=melange(p[12,y][:3],(40,30,26),0.45)+(255,)          # ombre portée
    for y in (2,7,12): p[14,y]=A[5]+(255,); p[14,y+1]=A[1]+(255,)
    return im
def socle(seed):
    im=briques(seed).copy(); p=im.load()
    for x in range(16):
        for y in range(9,16):
            c=A[3]
            if y==9: c=A[5]
            elif y==10: c=A[4]
            elif y==15: c=A[0]
            elif (x*5+y*3)%13==0: c=A[2]
            p[x,y]=c+(255,)
        p[x,8]=melange(p[x,8][:3],(40,30,26),0.4)+(255,)
    for x in (2,7,12): p[x,12]=A[5]+(255,); p[x+1,13]=A[1]+(255,)
    return im
ecrire(cornier(briques(41)),'block/fire_bricks_corner')
ecrire(socle(43),'block/blast_furnace_plinth')
ecrire(cornier(socle(45)),'block/blast_furnace_plinth_corner')
ecrire(cornier(bande_airain()),'block/blast_furnace_hopper_side_corner')
# rigole de coulée et pièces d'airain des modèles
def airain_uni(seed):
    return patiner(bloc(),0,seed)
ecrire(airain_uni(201),'block/blast_furnace_airain')
