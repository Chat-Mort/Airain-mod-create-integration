# Maquette du livre de l'ingénieur : police bitmap de Minecraft, fond du registre, icônes d'objets.
import json, os, numpy as np
from PIL import Image
S='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/'
MC=S+'mcmeta-assets/assets/minecraft/'
AIR='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'
# ---------------------------------------------------------------- police
GL={}
for p in json.load(open(MC+'font/include/default.json'))['providers']:
    im=Image.open(MC+'textures/'+p['file'].split(':')[1]).convert('RGBA'); a=np.asarray(im)[...,3]
    rows=p['chars']; cw=im.width//len(rows[0]); ch=im.height//len(rows); h=p.get('height',8); asc=p['ascent']
    for r,row in enumerate(rows):
        for c,car in enumerate(row):
            if car in GL or car=='\u0000': continue
            cell=a[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
            cols=np.where(cell.max(0)>0)[0]
            w=(cols.max()+1) if len(cols) else 0
            GL[car]=(cell>0, w, asc)
def adv(car,gras=False):
    if car==' ': return 4
    g=GL.get(car); return (g[1]+1 if g else 6)+(1 if gras else 0)
def largeur(t):
    w=0; gras=False; i=0
    while i<len(t):
        if t[i]=='§' and i+1<len(t): gras = (t[i+1]=='l') or (gras and t[i+1] not in 'r0123456789abcdef'); i+=2; continue
        w+=adv(t[i],gras); i+=1
    return w
COUL={'0':(0,0,0),'4':(0x8A,0x1A,0x14),'6':(0x9A,0x60,0x10),'8':(0x6E,0x50,0x34),'9':(0x28,0x50,0x7A)}
def ecrire(img,t,x,y,col,gras=False,ital=False):
    px=img.load(); c0=col; i=0
    while i<len(t):
        if t[i]=='§' and i+1<len(t):
            k=t[i+1]
            if k=='l': gras=True
            elif k=='o': ital=True
            elif k=='r': gras=False; ital=False; col=c0
            elif k in COUL: col=COUL[k]
            i+=2; continue
        car=t[i]; g=GL.get(car)
        if g and car!=' ':
            m,w,asc=g; top=y+7-asc
            for yy in range(m.shape[0]):
                dec=int(round((7-yy)*0.25)) if ital else 0
                for xx in range(m.shape[1]):
                    if m[yy,xx]:
                        for b in ((0,1) if gras else (0,)):
                            X,Y=x+xx+b+dec,top+yy
                            if 0<=X<img.width and 0<=Y<img.height: px[X,Y]=col+(255,)
        x+=adv(car,gras); i+=1
    return x
def couper(t,maxw):
    mots=t.split(' '); L=[]; cur=''
    for m in mots:
        essai=(cur+' '+m) if cur else m
        if largeur(essai)<=maxw: cur=essai
        else:
            if cur: L.append(cur)
            cur=m
    if cur: L.append(cur)
    # le gras continue d'une ligne à l'autre
    out=[]; actif=''
    for l in L:
        out.append(actif+l)
        for j in range(len(l)-1):
            if l[j]=='§': actif = '§l' if l[j+1]=='l' else ('' if l[j+1]=='r' else actif)
    return out
# ---------------------------------------------------------------- icônes
import rendu_modele as rm
_ic={}
def icone(id_):
    if id_ in _ic: return _ic[id_]
    if id_=='create:zinc_ingot':      # pas de textures de Create ici : un lingot de fer bleuté pour la maquette
        im=Image.open(MC+'textures/item/iron_ingot.png').convert('RGBA'); a=np.asarray(im).astype(float); a[...,0]*=0.8; a[...,1]*=0.95; _ic[id_]=Image.fromarray(a.clip(0,255).astype('uint8')); return _ic[id_]
    ns,n=id_.split(':')
    racines={'airain':AIR,'minecraft':MC,'create':S+'create-src/src/main/resources/assets/create/'}
    kj='/home/claude/empire-airain-pack/kubejs/assets/kubejs/'
    im=None
    if ns=='kubejs':
        p=kj+'textures/item/'+n+'.png'
        if os.path.exists(p): im=Image.open(p).convert('RGBA').crop((0,0,16,16))
    else:
        R=racines[ns]; mi=R+'models/item/'+n+'.json'
        if os.path.exists(mi):
            d=json.load(open(mi)); par=d.get('parent','')
            if 'generated' in par or 'handheld' in par:
                t=d['textures']['layer0'].split(':')[-1]; im=Image.open(R+'textures/'+t+'.png').convert('RGBA').crop((0,0,16,16))
            else:
                try:
                    src=open(S+'verif_atelier2.py').read(); g={}
                    exec(src[:src.index('# 1. tuyauterie')],g)
                    E=g['charge'](par.split('block/')[-1] if 'block/' in par else n,(0,0,0))
                    g['rm'].RAC['t']=AIR
                    big=g['vue'](E,[-1,0.82,-1],128); im=big.resize((16,16),Image.LANCZOS)
                except Exception as e:
                    print('icône',id_,e)
        for t in ('item','block'):
            if im is None and os.path.exists(R+f'textures/{t}/'+n+'.png'): im=Image.open(R+f'textures/{t}/'+n+'.png').convert('RGBA').crop((0,0,16,16))
    if im is None: im=Image.new('RGBA',(16,16),(200,0,200,255))
    _ic[id_]=im; return im
def coller(img,id_,x,y,ech=1.0):
    ic=icone(id_)
    if ech!=1.0: ic=ic.resize((max(1,int(16*ech)),max(1,int(16*ech))),Image.NEAREST if ech>=1 else Image.LANCZOS)
    img.alpha_composite(ic,(int(x),int(y)))
# ---------------------------------------------------------------- mise en page (règles du futur écran)
ENCRE=(0x3A,0x1A,0x0A); SEPIA=(0x6E,0x50,0x34); ROUGE=(0x8A,0x1A,0x14); BLEU=(0x28,0x50,0x7A); FILET=(0x9A,0x70,0x46)
W=300; LARGE=118
def fond():
    reg=Image.open(AIR+'textures/gui/registry.png').convert('RGBA')
    im=Image.new('RGBA',(W+40,196+40),(40,32,30,255)); im.alpha_composite(reg.crop((0,0,W,196)),(20,20)); return im
def blocs(texte, maxw=LARGE):
    """Le texte balisé → lignes affichables : (type, données, hauteur)."""
    out=[]
    for par in texte.split('\n'):
        if par.startswith('## '):
            out.append(('titre',par[3:],13))
        elif par.startswith('- '):
            for j,l in enumerate(couper(par[2:],maxw-8)): out.append(('puce',(l,j==0),10))
        elif par.startswith('@'):
            id_,reste=par[1:].split(' ',1)
            for j,l in enumerate(couper(reste,maxw-13)): out.append(('objet',(id_ if j==0 else None,l),11 if j==0 else 10))
        elif par=='':
            out.append(('vide','',5))
        else:
            for l in couper(par,maxw): out.append(('texte',l,10))
    return out
def dessiner(img,L,x,y):
    for typ,d,h in L:
        if typ=='titre':
            ecrire(img,d,x,y+2,ROUGE,gras=True)
            img.paste(Image.new('RGBA',(LARGE,1),FILET+(255,)),(x,y+11))
        elif typ=='puce':
            l,prem=d
            if prem: ecrire(img,'•',x+1,y,ROUGE)
            ecrire(img,l,x+8,y,ENCRE)
        elif typ=='objet':
            id_,l=d
            if id_: coller(img,id_,x,y-1,0.625)
            ecrire(img,l,x+13,y+(1 if id_ else 0),ENCRE)
        elif typ=='texte': ecrire(img,d,x,y,ENCRE)
        y+=h
    return y
BAS=136   # bas utile des deux pages (y relatif au haut du texte, avant les flèches et le numéro)
def groupe(L,i):
    """Une entrée entière (ses lignes de suite) ; un titre reste avec la ligne qui le suit."""
    j=i+1
    while j<len(L) and ((L[j][0]=='puce' and not L[j][1][1]) or (L[j][0]=='objet' and L[j][1][0] is None)): j+=1
    if L[i][0]=='titre' and j<len(L): return groupe(L,j)[0:0] or L[i:groupe_fin(L,j)]
    return L[i:j]
def groupe_fin(L,j):
    k=j+1
    while k<len(L) and ((L[k][0]=='puce' and not L[k][1][1]) or (L[k][0]=='objet' and L[k][1][0] is None)): k+=1
    return k
def couler(L, colonnes):
    """Répartit les lignes dans les colonnes [(x, y0, bas)] sans couper une entrée. Renvoie [[lignes]], reste."""
    out=[]; i=0
    for (x,y0,bas) in colonnes:
        col=[]; h=y0
        while i<len(L):
            if not col and L[i][0]=='vide': i+=1; continue
            g=groupe(L,i); hg=sum(b[2] for b in g)
            if h+hg>bas: break
            col+=g; h+=hg; i+=len(g)
        out.append(col)
    return out, L[i:]
def chapitre(icone_id,titre,histoire,usage,num,tot,tete="Mode d'emploi"):
    """Gauche : icône et titre, histoire en italique, puis le mode d'emploi coule sur la gauche puis la droite."""
    res=[]; L=blocs(usage); k=0
    while True:
        im=fond(); bx,by=20,20; gx=bx+20; dx=bx+162; y=by+22
        if k==0:
            coller(im,icone_id,gx,y,1.5)
            T=couper('§l'+titre,LARGE-28)
            for j,l in enumerate(T[:2]): ecrire(im,l,gx+28,y+(8 if len(T)==1 else 3)+j*10,ENCRE)
            yy=y+28
            for l in couper(histoire,LARGE)[:4]: ecrire(im,l,gx,yy,SEPIA,ital=True); yy+=10
            im.paste(Image.new('RGBA',(LARGE,1),FILET+(255,)),(gx,yy+2))
            g0=yy+7-y
        else:
            coller(im,icone_id,gx,y,0.75); ecrire(im,titre+' (suite)',gx+15,y+2,SEPIA,ital=True)
            im.paste(Image.new('RGBA',(LARGE,1),FILET+(255,)),(gx,y+14)); g0=19
        cols,L=couler(L,[(gx,g0,136),(dx,0,128)])
        dessiner(im,cols[0],gx,y+g0); dessiner(im,cols[1],dx,y)
        n=f'{num+k} / {tot}'; ecrire(im,n,dx+LARGE//2-largeur(n)//2,by+162,SEPIA)
        res.append(im); k+=1
        if not L: return res
def sommaire(titre_livre,sous,onglets,ici,entrees,num,tot):
    im=fond(); bx,by=20,20; gx=bx+20; dx=bx+162; y=by+22
    ecrire(im,titre_livre,gx,y+2,ROUGE,gras=True); ecrire(im,sous,gx,y+14,SEPIA,ital=True)
    x=gx; row=0
    for i,o in enumerate(onglets):
        if i and i%3==0: row+=1; x=gx
        ecrire(im,o,x,y+26+row*11,ROUGE if i==ici else SEPIA)
        if i==ici: im.paste(Image.new('RGBA',(largeur(o),1),ROUGE+(255,)),(x,y+26+row*11+9))
        x+=largeur(o)+10
    im.paste(Image.new('RGBA',(LARGE,1),FILET+(255,)),(gx,y+49))
    for i,(ic,t) in enumerate(entrees):
        if i<5: X,Y=gx,y+56+i*14
        else: X,Y=dx,y+2+(i-5)*14
        coller(im,ic,X,Y-3,0.8); ecrire(im,t,X+16,Y,ENCRE)
    n=f'{num} / {tot}'; ecrire(im,n,dx+LARGE//2-largeur(n)//2,by+162,SEPIA)
    return im
def planche(ims,nom,echelle=3):
    W2=max(i.width for i in ims); H=sum(i.height for i in ims)
    out=Image.new('RGBA',(W2,H),(40,32,30,255)); y=0
    for i in ims: out.alpha_composite(i,(0,y)); y+=i.height
    out=out.resize((out.width*echelle,out.height*echelle),Image.NEAREST); out.save(S+'rendu_fusion/'+nom); return out
