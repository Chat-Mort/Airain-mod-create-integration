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
    tmp=Image.new('RGBA',(largeur(t)+len(t)+4,12),(0,0,0,0)); ecrire(tmp,t,1,2,tuple(col[:3]),gras); return tmp.crop(tmp.getbbox() or (0,0,1,1)) if False else tmp
def poser(im,t,x,y,col,ech,gras=False,ancre='g'):
    s=txt_img(t,col,gras); s=s.resize((s.width*ech,s.height*ech),Image.NEAREST)
    w=(largeur(t)+(len(t) if gras else 0))*ech
    if ancre=='c': x-=w/2
    if ancre=='d': x-=w
    im.alpha_composite(s,(int(x),int(y)))
CR=(236,228,206,255); RO=(214,64,48,255); OR=(232,196,110,255); EM=(26,26,32,255)
A=dict(c=(252,233,183),l=(243,214,148),m=(201,154,81),d=(168,118,60),s=(112,68,37),ss=(87,51,29),rv=(255,240,196))
# =============================================================== 1. tableau émaillé
# panneau émaillé 42 × 26 px du modèle → texture 8 px par pixel
K=8
im=Image.new('RGBA',(42*K,26*K),EM); dd=ImageDraw.Draw(im)
for i in range(0,42*K,2): pass
dd.rectangle([0,0,42*K-1,1],fill=(60,60,70)); dd.rectangle([0,0,1,26*K-1],fill=(60,60,70))     # reflet de l'émail en haut à gauche
poser(im,'ATELIER DE LA FONDERIE',21*K,8,RO,2,True,'c')
dd.rectangle([12,32,42*K-13,33],fill=(110,90,60))
L=[("Lingots d'airain",'1 284',None),("Débit tapis nord",'312 /min',None),("Stress",'68 %',(10,7)),("Moulage du canon",'41 %',(8,3)),("Train pour Port-Impérial",'2 min',None)]
y=40
for nom,val,bar in L:
    poser(im,nom,12,y,CR,2)
    if bar:
        x=12+largeur(nom)*2+12
        for i in range(bar[0]): dd.rectangle([x+i*10,y+4,x+i*10+7,y+15],fill=OR if i<bar[1] else (62,58,52))
    poser(im,val,42*K-12,y,OR,2,False,'d'); y+=32
im.save(D+'tableau.png')
# plaque de gare : émail bleu, filet blanc, nom en grand (même texture des deux côtés)
pl=Image.new('RGBA',(44*K,12*K),(30,62,120,255)); dp=ImageDraw.Draw(pl)
dp.rectangle([6,6,44*K-7,12*K-7],outline=CR,width=4); poser(pl,'PORT-IMPERIAL',22*K,30,CR,3,True,'c')
pl.save(D+'plaque.png')
def tableau(ox,oy):
    """3 × 2 blocs au mur : contre-plaque, cadre riveté en saillie, émail en retrait, écusson ciselé, rosaces aux coins."""
    X,Y=ox*16,oy*16; E=[]
    E.append(b((X,Y,14),(X+48,Y+32,16),SOMBRE))                                   # contre-plaque
    E.append(b((X+3,Y+3,13),(X+45,Y+29,14),hd('tableau'),("north",),{'north':FULL}))   # émail
    E+=[b((X,Y+29,10.5),(X+48,Y+32,14),PL),b((X,Y,10.5),(X+48,Y+3,14),PL),b((X,Y+3,10.5),(X+3,Y+29,14),PL),b((X+45,Y+3,10.5),(X+48,Y+29,14),PL)]   # cadre
    E+=[b((X+3,Y+28,12.5),(X+45,Y+29,13),BD),b((X+3,Y+3,12.5),(X+4,Y+28,13),BD)]   # filet d'ombre intérieur
    for (cx,cy) in ((X+1,Y+1),(X+45,Y+1),(X+1,Y+29),(X+45,Y+29)):              # rosaces
        E+=[b((cx,cy,9.5),(cx+2,cy+2,10.5),CH)]
    E+=[b((X+19,Y+30,9),(X+29,Y+37,13),CH),b((X+21,Y+37,10),(X+27,Y+39,13),PL),b((X+22.5,Y+39,10.5),(X+25.5,Y+40,12.5),M)]   # écusson au fronton
    for k in range(4,46,6): E.append(b((X+k,Y+31,10),(X+k+1,Y+32,10.5),'airain:block/airain_rod'))   # têtes de rivets
    return E
def plaque_suspendue(ox,oy,oz):
    """Plaque de gare double face, pendue sous une poutrelle par deux chaînes."""
    X,Y,Z=ox*16,oy*16,oz*16; E=[]
    E+=[b((X-6,Y+20,Z+5),(X+54,Y+22,Z+11),FL),b((X-6,Y+30,Z+5),(X+54,Y+32,Z+11),FL),b((X-6,Y+22,Z+7),(X+54,Y+30,Z+9),WB,("north","south"))]   # poutrelle
    for cx in (X+6,X+38):
        E+=[b((cx,Y+12,Z+7.5),(cx+1,Y+20,Z+8.5),'airain:block/airain_rod'),b((cx+3,Y+12,Z+7.5),(cx+4,Y+20,Z+8.5),'airain:block/airain_rod'),b((cx,Y+11,Z+7),(cx+4,Y+12,Z+9),PL)]
    E+=[b((X+2,Y,Z+6.5),(X+46,Y+12,Z+9.5),PL),
        b((X+3,Y+1,Z+6.3),(X+45,Y+11,Z+6.5),hd('plaque'),("north",),{'north':FULL}),b((X+3,Y+1,Z+9.5),(X+45,Y+11,Z+9.7),hd('plaque'),("south",),{'south':FULL})]
    return E
E=mur(-1,5,0,4)+sol(-1,5,-3,1)+tableau(0,1)
TA=vue(E,[-0.3,0.18,-1],1000)
E=plaque_suspendue(0,0,0)
PS=vue(E,[-0.45,0.2,-1],700)
# =============================================================== 2. cadran
R0,RI=14,11      # rayon extérieur de la lunette, rayon de la glace
cad=Image.new('RGBA',(22*K*2,22*K*2),(0,0,0,0)); dc=ImageDraw.Draw(cad); C=22*K; Rr=22*K-4
dc.ellipse([C-Rr,C-Rr,C+Rr,C+Rr],fill=(238,228,200,255))
for a0,a1,c in ((135,270,(120,160,90)),(270,342,(225,190,80)),(342,405,(200,70,50))):
    dc.arc([C-Rr+26,C-Rr+26,C+Rr-26,C+Rr-26],a0,a1,fill=c,width=20)
for k in range(21):
    a=math.radians(135+k*13.5); r0=Rr-50 if k%5 else Rr-70
    dc.line([C+math.cos(a)*r0,C+math.sin(a)*r0,C+math.cos(a)*(Rr-26),C+math.sin(a)*(Rr-26)],fill=(40,30,25),width=6 if k%5==0 else 3)
for k,t in ((0,'0'),(1,'25'),(2,'50'),(3,'75'),(4,'100')):
    a=math.radians(135+k*67.5); poser(cad,t,C+math.cos(a)*(Rr-95),C+math.sin(a)*(Rr-95)-12,(60,45,35,255),3,True,'c')
poser(cad,'STRESS  %',C,C+100,(60,45,35,255),3,True,'c')
cad.save(D+'cadran.png')
def cadran(ox,oy):
    X,Y=ox*16,oy*16; cx,cy=X+16,Y+16; E=[]
    E.append(b((X+1,Y+1,14),(X+31,Y+31,16),PL))                                  # platine carrée rivetée
    for (rx,ry) in ((X+2,Y+2),(X+28,Y+2),(X+2,Y+28),(X+28,Y+28)): E.append(b((rx,ry,13),(rx+2,ry+2,14),CH))   # boulons
    for yy in range(-R0,R0):                                                     # lunette en relief, rangée par rangée
        yc=yy+0.5; w0=math.sqrt(max(0,R0*R0-yc*yc)); w1=math.sqrt(max(0,RI*RI-yc*yc)) if abs(yc)<RI else 0
        prof=10 if abs(yc)<R0-1.5 else 11.5
        if w1==0: E.append(b((cx-w0,cy+yy,prof),(cx+w0,cy+yy+1,14),M))
        else: E+=[b((cx-w0,cy+yy,prof),(cx-w1,cy+yy+1,14),M),b((cx+w1,cy+yy,prof),(cx+w0,cy+yy+1,14),M)]
    E.append(b((cx-RI,cy-RI,12.5),(cx+RI,cy+RI,13),hd('cadran'),("north",),{'north':FULL}))   # cadran en retrait
    a=180-(360-(135+0.68*270))                                                     # aiguille (68 %) ; vue de face, x inversé
    E.append(b((cx-1,cy-0.6,11.4),(cx+9,cy+0.6,11.8),'minecraft:block/red_concrete',rot={'origin':[cx,cy,11.6],'axis':'z','angle':a}))
    E+=[b((cx-1.5,cy-1.5,10.6),(cx+1.5,cy+1.5,12.5),CH),b((cx-0.5,cy-0.5,10.2),(cx+0.5,cy+0.5,10.6),M)]          # moyeu
    E+=[b((cx-3,Y-2,12),(cx+3,Y+1,15),M),b((cx-2,Y-8,12.5),(cx+2,Y-2,14.5),'airain:block/airain_pipe_vertical')]   # raccord du capillaire, dessous
    return E
E=mur(-1,3,-1,3)+cadran(0,0)+sol(-1,3,-3,1)
for e in E:
    for k in ('from','to'): e[k][1]+=0
CA=vue(E,[-0.5,0.3,-1],900)
# =============================================================== 3. totaliseur (bloc plein, fenêtre en retrait, rouleaux)
def rouleau(ch,suivant=None,dec=0.0):
    r=Image.new('RGBA',(40,64),(28,24,22,255)); dr=ImageDraw.Draw(r)
    for yy in range(64):
        t=abs((yy-31.5)/32)
        if t>0.55: dr.line([0,yy,39,yy],fill=(int(28-14*t),int(24-12*t),int(22-11*t),255))
    if suivant is None: poser(r,ch,20,10,CR,4,True,'c')
    else: poser(r,ch,20,-22,CR,4,True,'c'); poser(r,suivant,20,40,CR,4,True,'c')
    dr.rectangle([0,0,39,2],fill=(10,8,8,255)); dr.rectangle([0,61,39,63],fill=(10,8,8,255))
    return r
for i,c in enumerate('0012'): rouleau(c).save(D+f'rouleau_{5-i}.png')
rouleau('8').save(D+'rouleau_1.png'); rouleau('4','5').save(D+'rouleau_0.png')
gr=Image.new('RGBA',(24*K,4*K),(0,0,0,0)); poser(gr,'LINGOTS D\'AIRAIN',12*K,6,(87,51,29,255),2,True,'c'); gr.save(D+'gravure.png')
def totaliseur(ox,oy,oz,n=2):
    """n blocs côte à côte (3 rouleaux chacun) : boîtier d'airain riveté, fenêtre en retrait, plaque gravée, bouton de remise à zéro."""
    X,Y,Z=ox*16,oy*16,oz*16; E=[]; Lg=16*n
    E+=[b((X,Y,Z+3),(X+Lg,Y+16,Z+16),RIV,("up","east","west","south","down"))]
    # façade : cadre autour de la fenêtre (en saillie), fenêtre creusée de 3 px
    E+=[b((X,Y+13,Z),(X+Lg,Y+16,Z+3),PL),b((X,Y,Z),(X+Lg,Y+7,Z+3),PL),b((X,Y+7,Z),(X+2,Y+13,Z+3),PL),b((X+Lg-2,Y+7,Z),(X+Lg,Y+13,Z+3),PL)]
    for k in range(1,n): E.append(b((X+16*k-1,Y+7,Z+0.5),(X+16*k+1,Y+13,Z+3),PL))   # montant entre deux blocs
    zr=Z+3
    pos=[X+2+i*4.6 for i in range(3)]+[X+16+1+i*4.6 for i in range(3)] if n==2 else [X+2+i*4 for i in range(3)]
    for i,px in enumerate(pos):
        E+=[b((px,Y+7.5,zr-0.8),(px+4,Y+12.5,zr),hd(f'rouleau_{i}'),("north",),{'north':FULL}),
            b((px,Y+7,zr-0.4),(px+4,Y+7.5,zr),SOMBRE,("north","up")),b((px,Y+12.5,zr-0.4),(px+4,Y+13,zr),SOMBRE,("north","down"))]
    E+=[b((X+2,Y+12.8,Z+0.5),(X+Lg-2,Y+13,Z+3),BD,("down",))]                      # ombre du linteau
    E+=[b((X+4,Y+2,Z-0.5),(X+Lg-4,Y+5.5,Z),hd('gravure'),("north",),{'north':FULL}),b((X+4,Y+2,Z-0.5),(X+Lg-4,Y+5.5,Z),PL,("up","east","west","down"))]   # plaque gravée
    E+=[b((X+Lg-6,Y+16,Z+6),(X+Lg-3,Y+17,Z+9),M),b((X+Lg-5.5,Y+17,Z+6.5),(X+Lg-3.5,Y+18,Z+8.5),'minecraft:block/red_concrete')]   # bouton
    E+=[b((X+Lg,Y+6,Z+6),(X+Lg+2,Y+10,Z+10),M),b((X+Lg+2,Y+7,Z+7),(X+Lg+3,Y+9,Z+9),CH)]   # arbre d'entraînement sur le côté
    return E
E=sol(-1,3,-2,1)+totaliseur(0,1,0)+[b((x*16,y*16,0),(x*16+16,y*16+16,16),MUR,('north','up','west','east')) for x in range(-1,3) for y in range(0,3) if not (y==1 and x in (0,1))]
TO=vue(E,[-0.35,0.25,-1],900)
# =============================================================== 4. enseigne : lettres extrudées sur entretoises, halo rouge
def lettres(mot,ox,oy,ech=2,cache=False):
    E=[]; x=ox*16; tx='hd:'+D+'transparent.png' if cache else M
    for car in mot:
        m,wd,asc=GL[car]
        rows=m.shape[0]
        for yy in range(rows):
            xx=0
            while xx<m.shape[1]:
                if m[yy,xx]:
                    x2=xx
                    while x2+1<m.shape[1] and m[yy,x2+1]: x2+=1
                    # gras : un pixel de plus à droite
                    y0=oy*16+(asc-yy)*ech
                    E.append(b((x+xx*ech,y0,11),(x+(x2+2)*ech,y0+ech,14),tx))
                    xx=x2+1
                else: xx+=1
        E.append(b((x+wd*ech/2-1,oy*16+3*ech,14),(x+wd*ech/2+1,oy*16+5*ech,16),tx))    # entretoise
        x+=(wd+2)*ech
    return E
Image.new('RGBA',(4,4),(0,0,0,0)).save(D+'transparent.png')
def miroir(E,c):
    for e in E:
        x0,x1=e['from'][0],e['to'][0]; e['from'][0],e['to'][0]=c-x1,c-x0
        f=e['faces']; f['east'],f['west']=f.get('west'),f.get('east')
        e['faces']={k:v for k,v in f.items() if v}
    return E
MOT='FONDERIE'; ech=2
fond=mur(-1,11,0,3)+sol(-1,11,-2,1)
EN=vue(fond+miroir(lettres(MOT,0,1,ech),9*16),[-0.35,0.2,-1],1300)
# halo : même cadrage, lettres seules ; puis lueur rouge floue sous les lettres
seul=vue([dict(e,faces={k:dict(v,texture='hd:'+D+'transparent.png') for k,v in e['faces'].items()}) for e in fond]+miroir(lettres(MOT,0,1,ech),9*16),[-0.35,0.2,-1],1300)
a=np.asarray(seul)[...,3]
glow=Image.fromarray((a>0).astype('uint8')*255).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(18))
g=np.asarray(glow).astype(float)/255
base=np.asarray(EN).astype(float)
base[...,0]=np.minimum(255,base[...,0]+g*150); base[...,1]=np.minimum(255,base[...,1]+g*25); base[...,2]=np.minimum(255,base[...,2]+g*10)
EN=Image.fromarray(base.astype('uint8'),'RGBA'); EN.alpha_composite(seul)
EN=EN.crop(EN.getbbox())
TA=TA.crop(TA.getbbox()); PS=PS.crop(PS.getbbox()); CA=CA.crop(CA.getbbox()); TO=TO.crop(TO.getbbox())
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",22)
W=max(TA.width+PS.width,CA.width+TO.width,EN.width)+80
H=max(TA.height,PS.height)+max(CA.height,TO.height)+EN.height+200
out=Image.new('RGBA',(W,H),(34,30,38,255)); dd=ImageDraw.Draw(out)
y=10
dd.text((20,y),"1. Tableau émaillé (3 × 2), cadre en saillie",font=fo,fill=(235,215,170)); dd.text((TA.width+50,y),"   Même bloc : plaque de gare pendue",font=fo,fill=(235,215,170))
out.alpha_composite(TA,(20,y+36)); out.alpha_composite(PS,(TA.width+60,y+36)); y+=max(TA.height,PS.height)+50
dd.text((20,y),"2. Cadran (2 × 2) : lunette en relief, glace en retrait",font=fo,fill=(235,215,170)); dd.text((CA.width+60,y),"3. Totaliseur : un vrai bloc, 3 rouleaux par bloc",font=fo,fill=(235,215,170))
out.alpha_composite(CA,(20,y+36)); out.alpha_composite(TO,(CA.width+60,y+36)); y+=max(CA.height,TO.height)+50
dd.text((20,y),"4. Enseigne : lettres d'airain extrudées sur entretoises, éclairées",font=fo,fill=(235,215,170)); out.alpha_composite(EN,(20,y+36))
out.save('afficheurs3d.png'); print(out.size)
