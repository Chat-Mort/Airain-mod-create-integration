# Textures de détail v3 : chaque texture part d'une carte de hauteurs (relief réel), éclairée par une seule lumière
# venant d'en haut à gauche. Les pentes donnent des dégradés, jamais un pixel blanc collé à un noir.
import math
exec(open('airain_luxe.py').read().split('def bloc():')[0])
from PIL import Image
LUM=(-0.55,-0.65,0.52); n_=math.sqrt(sum(c*c for c in LUM)); LUM=tuple(c/n_ for c in LUM)
def ombrer(H, base=3.5, force=3.4, ao=0.45, poli=0.6, boucle=True, mini=1.3, maxi=5.4):
    """Hauteurs H[y][x] (en px) → carte de teintes (valeurs fractionnaires 0..6)."""
    def h(x,y):
        if boucle: return H[y%16][x%16]
        return H[max(0,min(15,y))][max(0,min(15,x))]
    C=vide(); plat=LUM[2]
    for y in range(16):
        for x in range(16):
            dx=(h(x+1,y)-h(x-1,y))/2; dy=(h(x,y+1)-h(x,y-1))/2
            nx,ny,nz=-dx,-dy,1.0; l=math.sqrt(nx*nx+ny*ny+nz*nz)
            d=(nx*LUM[0]+ny*LUM[1]+nz*LUM[2])/l
            moy=sum(h(x+i,y+j) for i in (-1,0,1) for j in (-1,0,1))/9
            creux=max(0.0,moy-h(x,y))                       # occlusion : les fonds de creux s'assombrissent
            v=base+force*(d-plat)-ao*creux+poli*reflet(x,y,0.8)
            C[y][x]=max(mini,min(maxi,v))
    return C
def biseau(t, larg):
    """Rampe douce sur `larg` px (0 → 1)."""
    return max(0.0,min(1.0,t/larg))
# ---------------------------------------------------------------- panneau à cadre (symétrique, centré)
def panneau():
    H=[[0.0]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            d=min(x,y,15-x,15-y)                          # distance au bord, symétrique
            H[y][x]={0:1.4,1:2.0,2:1.0}.get(d,0.0)          # cadre bombé, biseau, champ en retrait
    for y in range(16):                                    # losange central à quatre facettes (pointe de diamant)
        for x in range(16):
            dd=abs(x-7.5)+abs(y-7.5)
            if dd<=4: H[y][x]=max(H[y][x],1.6*(1-dd/5))
    for (cx,cy) in ((1,1),(14,1),(1,14),(14,14)): H[cy][cx]=2.6
    return ombrer(H,boucle=False)
# ---------------------------------------------------------------- frise : filets et pointes de diamant (faces ≥ 6 px), période 8, centrée
def frise():
    H=[[0.0]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if y in (3,12): H[y][x]=1.2
            elif y in (2,13): H[y][x]=0.6
            if 5<=y<=10:
                dd=abs((x%8)-3.5)+abs(y-7.5)
                if dd<=3.2: H[y][x]=1.5*(1-dd/4)
    return ombrer(H)
# ---------------------------------------------------------------- bandeau (faces minces 2–4 px) : boudin et perle tous les 8 px
def bandeau():
    H=[[0.0]*16 for _ in range(16)]
    for y in range(16):
        k=(y%4)+0.5
        for x in range(16):
            hh=1.0*math.sin(math.pi*k/4)
            if y%4 in (1,2):
                r=math.hypot((x%8)-3.5,(y%4)-1.5)
                if r<=1.6: hh+=0.9*(1-r/2)
            H[y][x]=hh
    return ombrer(H,force=3.0)
# ---------------------------------------------------------------- rainures douces (pièces longues/inclinées)
def rainures():
    H=[[0.9*math.cos(2*math.pi*(y+0.5)/4) for x in range(16)] for y in range(16)]
    return ombrer(H,force=2.6)
# ---------------------------------------------------------------- cannelures de 3 px
def cannelures():
    H=[[(-1.2*math.sin(math.pi*((x%3)+0.5)/3)) for x in range(16)] for y in range(16)]
    return ombrer(H,force=3.0)
# ---------------------------------------------------------------- tuyau : cylindre de 6 px (rangs 5 à 10) et soudure au milieu
def tuyau():
    C=vide()
    for y in range(16):
        for x in range(16):
            if 5<=y<=10:
                t=(y-4.5)/6*2-1                             # -1 (haut) → 1 (bas)
                nz=math.sqrt(max(0,1-t*t)); ny=t
                d=ny*LUM[1]+nz*LUM[2]
                v=2.2+3.3*d+0.3*reflet(x,y,0.8)
                if x in (7,8): v+=0.35 if x==7 else -0.25   # cordon de soudure
            else: v=3.4+0.6*reflet(x,y,0.8)
            C[y][x]=max(1.7,min(5.0,v))
    return C
def tuyau_v():
    """Tuyau vertical de 6 px (colonnes 5 à 10), reflet à gauche, soudure horizontale au milieu."""
    C=vide()
    for y in range(16):
        for x in range(16):
            if 5<=x<=10:
                t=(x-4.5)/6*2-1; nz=math.sqrt(max(0,1-t*t))
                v=2.2+3.3*(t*LUM[0]+nz*LUM[2])+0.3*reflet(x,y,0.8)
                if y in (7,8): v+=0.35 if y==7 else -0.25
            else: v=3.4+0.6*reflet(x,y,0.8)
            C[y][x]=max(1.7,min(5.0,v))
    return C
def tige():
    """Tige ronde pour pieds et montants fins (2 à 4 px), centrée : clair à gauche, ombre douce à droite."""
    prof={5:3.4,6:4.0,7:4.4,8:3.5,9:2.8,10:2.5}
    return [[prof.get(x,3.3) for x in range(16)] for y in range(16)]
def goulotte():
    """Fond du toboggan : gouttière concave en travers, lisse dans le sens de la glisse."""
    C=vide()
    for y in range(16):
        t=(y-7.5)/8
        v=3.6+1.0*t-0.6*(1-t*t)           # le bord bas reçoit la lumière, le fond s'assombrit doucement
        for x in range(16): C[y][x]=v
    return C
def rebord():
    """Flanc du toboggan : rebord arrondi en haut, champ poli, filet d'ombre en bas — rien ne varie en longueur."""
    C=vide()
    prof=[3.4]*5+[4.6,4.1,3.6,3.4,3.1,2.7]+[3.3]*5     # profil centré sur les rangs 5 à 10 (flanc de 6 px)
    for y in range(16):
        for x in range(16): C[y][x]=prof[y]
    return C
OUTB=OUT+'/block/'
for nom,f in (('airain_panel',panneau),('airain_frieze',frise),('airain_band',bandeau),('airain_grooves',rainures),('airain_fluted',cannelures),('airain_pipe',tuyau),('airain_pipe_vertical',tuyau_v),('airain_rod',tige),('airain_chute',goulotte),('airain_chute_side',rebord)):
    c=f()
    for s,p in enumerate(['','exposed_','weathered_','oxidized_']): rendre_carte(c,T[s]).save(OUTB+p+nom+'.png')
print('ok')
