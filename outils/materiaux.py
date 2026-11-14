# Nouveaux matériaux (maquette) : marbre blanc et noir veinés d'or, ardoise, bois laqué rouge.
# Motifs dessinés (veines périodiques sur 16 px, donc raccord parfait), relief éclairé en haut à gauche, contrastes doux.
import math, os
from PIL import Image
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/materiaux/'
os.makedirs(OUT,exist_ok=True)
def mix(a,b,t): return tuple(int(round(a[i]+(b[i]-a[i])*t)) for i in range(3))
def hexa(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
# palettes : (sombre, base, clair)
MARBRE={'blanc':(hexa('cfc8bb'),hexa('e9e4d9'),hexa('f7f4ee')),'noir':(hexa('17151b'),hexa('26232b'),hexa('3a3640'))}
OR=(hexa('8a6420'),hexa('c79a3e'),hexa('ecc874'))
def fond(pal,x,y,force=1.0):
    """Base du marbre : un léger nuage diagonal (pas de bruit), plus clair en haut à gauche."""
    t=0.5+0.18*math.sin((x+y)*math.pi/8)+0.10*math.sin((x-2*y)*math.pi/16)-0.12*((x+y)/30-0.5)
    t=max(0,min(1,t))
    return mix(pal[0],pal[2],0.25+0.6*t) if force else pal[1]
OR_PALE=(hexa('a88a4a'),hexa('d6b46a'),hexa('f0dca0'))
def veines():
    """Une veine principale en diagonale (raccord parfait : elle monte de 16 px sur 16 px) qui ondule doucement,
    une branche courte, et une veinule grise discrète dans l'autre sens. Renvoie {pixel: 'or' | 'gris'}."""
    v={}
    for x in range(16):
        w=int(round(1.6*math.sin(2*math.pi*x/16)+0.8*math.sin(4*math.pi*x/16+1)))
        y=(x+3+w)%16; v[(x,y)]='or'
        if x in (6,7): v[(x,(y+1)%16)]='or'          # la veine s'épaissit un peu
    for k in range(5):                                # branche
        v[((9+k)%16,(13-2*k//2+k%2)%16)]='or'
    for x in range(2,9):                              # veinule grise
        y=(14-x+int(round(0.7*math.sin(x))))%16
        v.setdefault((x,y),'gris')
    return v
def marbre_raccord(nom):
    pal=MARBRE[nom]; V=veines(); im=Image.new('RGB',(16,16)); p=im.load()
    o=OR_PALE if nom=='blanc' else OR
    for y in range(16):
        for x in range(16):
            col=fond(pal,x,y); k=V.get((x,y))
            if k=='or': col=o[2] if (x+y)%4==0 else o[1]
            elif k=='gris': col=mix(col,pal[0] if nom=='blanc' else pal[2],0.55)
            elif V.get(((x-1)%16,(y-1)%16))=='or': col=mix(col,o[0],0.3)
            p[x,y]=col
    return im
def biseau(p,x0,y0,x1,y1,pal,claire=0.55,sombre=0.55):
    for x in range(x0,x1+1):
        p[x,y0]=mix(p[x,y0],pal[2],claire); p[x,y1]=mix(p[x,y1],pal[0],sombre)
    for y in range(y0,y1+1):
        p[x0,y]=mix(p[x0,y],pal[2],claire); p[x1,y]=mix(p[x1,y],pal[0],sombre)
def dalles(nom):
    """Marbre poli en dalles de 8 : joints dorés fins, biseau léger."""
    im=marbre_raccord(nom); p=im.load(); pal=MARBRE[nom]
    for y in range(16):
        for x in range(16):
            if x%8==7 or y%8==7: p[x,y]=mix(pal[0],(0,0,0),0.08 if nom=='blanc' else 0.35)
    for ox in (0,8):
        for oy in (0,8): biseau(p,ox,oy,ox+6,oy+6,pal,0.5,0.3)
    return im
def briques(nom):
    im=marbre_raccord(nom); p=im.load(); pal=MARBRE[nom]
    for y in range(16):
        dec=0 if (y//4)%2==0 else 4
        for x in range(16):
            if y%4==3 or (x+dec)%8==7: p[x,y]=mix(pal[0],(0,0,0),0.15) if nom=='blanc' else mix(pal[0],(0,0,0),0.3)
    for r in range(4):
        dec=0 if r%2==0 else 4
        for k in range(2):
            x0=(k*8-dec)%16
            for x in range(x0,x0+7):
                xx=x%16; p[xx,r*4]=mix(p[xx,r*4],pal[2],0.45); p[xx,r*4+2]=mix(p[xx,r*4+2],pal[0],0.3)
    return im
def colonne(nom):
    """Pilier : cannelures verticales (creux ombré à droite), un filet d'or en haut et en bas."""
    im=Image.new('RGB',(16,16)); p=im.load(); pal=MARBRE[nom]
    for y in range(16):
        for x in range(16):
            k=x%4
            col=fond(pal,x,y)
            if k==0: col=mix(col,pal[2],0.5)
            if k==2: col=mix(col,pal[0],0.35)
            if k==3: col=mix(col,pal[0],0.15)
            if y in (0,15): col=OR[1] if y==0 else OR[0]
            if y in (1,14): col=OR[2] if y==1 else OR[1]
            p[x,y]=col
    return im
def cisele(nom):
    """Marbre ciselé : une étoile impériale d'or incrustée, dans un cadre biseauté."""
    im=marbre_raccord(nom); p=im.load(); pal=MARBRE[nom]
    for y in range(16):
        for x in range(16): p[x,y]=fond(pal,x,y)
    biseau(p,0,0,15,15,pal,0.6,0.6); biseau(p,2,2,13,13,pal,0.0,0.0)
    for x in range(2,14): p[x,2]=mix(p[x,2],pal[0],0.5); p[x,13]=mix(p[x,13],pal[2],0.5)
    for y in range(2,14): p[2,y]=mix(p[2,y],pal[0],0.5); p[13,y]=mix(p[13,y],pal[2],0.5)
    cx=cy=7.5      # premier motif (préféré) : étoile en croix incrustée d'or
    for y in range(16):
        for x in range(16):
            dx,dy=x-cx,y-cy; r=math.hypot(dx,dy); a=math.atan2(dy,dx)
            branche=abs(math.cos(4*a))
            if r<=1.2 or (r<=4.6 and branche>0.93-0.08*(4.6-r)) :
                p[x,y]=OR[2] if (dx+dy)<0 else OR[1]
            elif r<=5.3 and branche>0.9 : p[x,y]=OR[0]
    return im
# ---------------------------------------------------------------- ardoise
ARD=(hexa('22252c'),hexa('343843'),hexa('4c5260'))
def tuiles_ardoise():
    """Toiture : écailles arrondies (bas en demi-cercle), rangs décalés de 4, chaque écaille plus claire en haut."""
    im=Image.new('RGB',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            r=y//6 if False else None
            # écailles de 8 de large, 6 de haut ; rangées décalées de 4 ; périodique sur 16 (rangs de 8 : 2 rangs)
            rang=y//8; dec=0 if rang%2==0 else 4; yy=y%8; u=(x+dec)%8
            cx=3.5; prof=7.0-1.6*((u-cx)/cx)**2*2.2      # bord bas arrondi
            if yy>=prof-0.5: col=ARD[0]                        # ombre sous l'écaille (le rang du dessous dépasse)
            else:
                t=0.75-0.07*yy-0.05*abs(u-cx)
                col=mix(ARD[0],ARD[2],max(0.15,t))
                if u==0: col=mix(col,ARD[0],0.5)
                if yy==0: col=mix(col,ARD[2],0.4)
            p[x,y]=col
    return im
def ardoise_polie():
    im=Image.new('RGB',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            t=0.45+0.12*math.sin((x+y)*math.pi/8)
            p[x,y]=mix(ARD[0],ARD[2],t)
    biseau(p,0,0,15,15,ARD,0.5,0.6)
    for k in range(3,13,3): p[k,k+1 if k<15 else k]=mix(p[k,k],ARD[2],0.4)     # strates claires, à peine marquées
    return im
def carrelage():
    """Carrelage noir et blanc (damier de 8), joints fins."""
    im=Image.new('RGB',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            blanc=((x//8)+(y//8))%2==0
            p[x,y]=fond(MARBRE['blanc'] if blanc else MARBRE['noir'],x,y)
            if x%8==7 or y%8==7: p[x,y]=mix(p[x,y],(40,36,30),0.5)
    return im
# ---------------------------------------------------------------- bois laqué rouge
LAQ=(hexa('3f0c0c'),hexa('7a1a16'),hexa('a8322a'))
def laque():
    """Planches laquées rouge sombre : lames de 4 px, reflet laqué, filet d'or entre deux lames."""
    im=Image.new('RGB',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            yy=y%4
            t=0.45+0.25*math.exp(-((x+y*0.6)%16-5)**2/6)
            col=mix(LAQ[0],LAQ[2],t)
            if yy==0: col=mix(col,LAQ[2],0.35)
            if yy==3: col=mix(LAQ[0],(0,0,0),0.2)
            if y==7 or y==15: col=OR[1] if x%2==0 else OR[0]
            if yy==3 and (x+ (y//4)*5)%16==11: col=LAQ[0]
            p[x,y]=col
    return im
def panneau_laque():
    im=Image.new('RGB',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16):
            t=0.5+0.2*math.exp(-((x+y)%24-8)**2/10)
            p[x,y]=mix(LAQ[0],LAQ[2],t)
    for x in range(16): p[x,0]=OR[2]; p[x,15]=OR[0]
    for y in range(16): p[0,y]=OR[2]; p[15,y]=OR[0]
    biseau(p,3,3,12,12,LAQ,0.0,0.0)
    for x in range(3,13): p[x,3]=mix(LAQ[0],(0,0,0),0.2); p[x,12]=mix(p[x,12],LAQ[2],0.6)
    for y in range(3,13): p[3,y]=mix(LAQ[0],(0,0,0),0.2); p[12,y]=mix(p[12,y],LAQ[2],0.6)
    for (x,y) in ((1,1),(14,1),(1,14),(14,14)): p[x,y]=OR[2]
    return im
TEX={}
for n in ('blanc','noir'):
    TEX[f'marbre_{n}']=marbre_raccord(n); TEX[f'marbre_{n}_dalles']=dalles(n); TEX[f'marbre_{n}_briques']=briques(n)
    TEX[f'marbre_{n}_colonne']=colonne(n); TEX[f'marbre_{n}_cisele']=cisele(n)
TEX['ardoise_tuiles']=tuiles_ardoise(); TEX['ardoise_polie']=ardoise_polie(); TEX['carrelage']=carrelage()
TEX['laque']=laque(); TEX['laque_panneau']=panneau_laque()
for k,im in TEX.items(): im.save(OUT+k+'.png')
print(len(TEX))

def courbe(p0,p1,p2,n=40):
    pts=[]
    for k in range(n+1):
        t=k/n; x=(1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0]; y=(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]
        q=(int(round(x)),int(round(y)))
        if 0<=q[0]<16 and 0<=q[1]<16 and q not in pts: pts.append(q)
    return pts
VARIANTES=[   # (veine d'or, branche (inutilisée), veinule grise) ; None : pas de veine d'or (marbre presque uni)
    (((0,3),(8,4),(15,12)),None,((3,13),(6,10),(12,14))),
    (((1,15),(6,7),(15,1)),None,((1,3),(4,1),(8,2))),
    (((0,10),(9,14),(15,7)),None,((3,2),(7,5),(13,1))),
    (None,None,((2,12),(8,8),(14,10))),
    (None,None,((2,3),(6,6),(13,4))),
    (None,None,((4,14),(9,10),(12,2))),
]
def marbre(nom,v=0):
    pal=MARBRE[nom]; o=OR_PALE if nom=='blanc' else OR
    im=Image.new('RGB',(16,16)); p=im.load()
    for y in range(16):
        for x in range(16): p[x,y]=mix(pal[0],pal[2],0.55+0.05*math.sin((x+2*y)*math.pi/8)*math.sin((2*x-y)*math.pi/16))   # presque uni : pas de bord visible entre les blocs
    principale,branche,grise=VARIANTES[v]
    for q in courbe(*grise): p[q]=mix(p[q],pal[0] if nom=='blanc' else pal[2],0.5)
    for k,q in enumerate(courbe(*principale) if principale else []):
        p[q]=o[2] if k%4==0 else o[1]
        b=(q[0]+1,q[1]+1)
        if b[0]<16 and b[1]<16 and p[b]!=o[1] and p[b]!=o[2]: p[b]=mix(p[b],o[0],0.3)
    return im
for n in ('blanc','noir'):
    for v in range(6): marbre(n,v).save(OUT+f'marbre_{n}_{v}.png')
    cisele(n).save(OUT+f'marbre_{n}_cisele.png')
print('variantes ok')
