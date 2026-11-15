# Maquette : charpente métallique d'airain (poteaux/poutrelles en I, jambes de force, poutre treillis, chevrons,
# verrière, gouttière) et marquages au sol (lignes raccordées, hachures, flèches).
src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
import math, os
S='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/'
MQ=S+'charpente/'; os.makedirs(MQ+'textures/block',exist_ok=True)
rm.RAC['mq']=MQ; rm._cache.clear()
def hx(h): return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
CL,LI,MI,MD,SO,SOO,RV,RD=hx('fce9b7'),hx('f3d694'),hx('c08f4a'),hx('a9773d'),hx('704425'),hx('57331d'),hx('fff0c4'),hx('784b28')
def mid(t):  # dégradé doux clair→foncé (lumière en haut à gauche)
    a,b=hx('c99a51'),hx('a8763c'); return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))+(255,)
def sauve(nom,f):
    im=Image.new('RGBA',(16,16),(0,0,0,0))
    for y in range(16):
        for x in range(16):
            c=f(x,y)
            if c: im.putpixel((x,y),c)
    im.save(MQ+'textures/block/'+nom+'.png')
def rivet(x,y,px,py):
    if (x,y)==(px,py): return RV
    if (x,y)==(px+1,py): return hx('e1ba6e')
    if (x,y)==(px+1,py+1): return RD
    if (x,y)==(px,py+1): return hx('cb9c53')
# âme de la poutrelle : aplat légèrement dégradé, ombre portée sous l'aile du haut
sauve('beam_web',lambda x,y: SO if y==3 else (hx('b38141') if y==4 else mid((y-3)/10)))
# aile : biseau clair en haut/à gauche, sombre en bas/à droite, deux rivets par bloc et par rang
def aile(x,y):
    if y==3: return LI
    if y==12: return SO
    r=None
    for px in (3,11):
        for py in (5,9):
            r=r or rivet(x,y,px,py)
    return r or mid(abs(y-7.5)/9+x/60)
sauve('beam_flange',aile)
# platine (abouts, pied de poteau, chapiteau) : cadre biseauté et 4 rivets
def platine(x,y):
    if x==0 or y==0: return LI
    if x==15 or y==15: return SO
    r=None
    for px in (2,12):
        for py in (2,12): r=r or rivet(x,y,px,py)
    return r or mid((x+y)/40)
sauve('plate',platine)
# barre de treillis / chevron : plat biseauté, rivet aux deux bouts
sauve('bar',lambda x,y: LI if y==6 else (SO if y==9 else (rivet(x,y,2,7) or rivet(x,y,13,7) or mid(0.4))))
# --- marquages ---
JA,JA2,BL,BL2,NO,RO_=hx('e3b021'),hx('c99a17'),hx('e8e4d8'),hx('c9c4b6'),hx('262626'),hx('b8322a')
sauve('line_yellow',lambda x,y: JA if 7<=x<=8 else None)
sauve('line_white',lambda x,y: BL if 7<=x<=8 else None)
sauve('hatch_yellow',lambda x,y: JA if ((x+y)//4)%2==0 else NO)
sauve('hatch_red',lambda x,y: RO_ if ((x+y)//4)%2==0 else BL)
def fleche(x,y):  # flèche pleine : hampe large et tête triangulaire
    if 6<=x<=9 and 8<=y<=14: return BL
    d=abs(x-7.5)
    if 2<=y<=8 and d<=(y-2)+0.5: return BL
sauve('arrow_white',fleche)
def zebra(x,y): return BL if (x//4)%2==0 and 1<=y<=14 else None
sauve('crossing_white',zebra)

T={k:'mq:block/'+k for k in ('beam_web','beam_flange','plate','bar','line_yellow','line_white','hatch_yellow','hatch_red','arrow_white','crossing_white')}
GL='t:block/airain_glass'; PI='t:block/airain_pipe'
def b(f,t,tex,faces=("north","south","east","west","up","down"),rot=None,uvs=None):
    fc={}
    for k in faces:
        x0,y0,z0=f; x1,y1,z1=t
        dims={'north':(x1-x0,y1-y0),'south':(x1-x0,y1-y0),'east':(z1-z0,y1-y0),'west':(z1-z0,y1-y0),'up':(x1-x0,z1-z0),'down':(x1-x0,z1-z0)}[k]
        a,h=min(16,dims[0]),min(16,dims[1]); u=(16-a)/2; v=(16-h)/2
        fc[k]={'texture':tex,'uv':(uvs or {}).get(k,[u,v,u+a,v+h])}
    e={'from':list(f),'to':list(t),'faces':fc}
    if rot: e['rotation']=rot
    return e
# ---------- pièces ----------
def poutre(p0,axe,n):
    """Poutrelle en I de n blocs le long de axe ('x','y','z'), section 10 (ailes) × 14 (hauteur), âme de 2."""
    X,Y,Z=[c*16 for c in p0]; E=[]
    for k in range(n):
        if axe=='x':
            x=X+k*16
            E+=[b((x,Y+1,Z+3),(x+16,Y+3,Z+13),T['beam_flange']),b((x,Y+13,Z+3),(x+16,Y+15,Z+13),T['beam_flange']),
                b((x,Y+3,Z+7),(x+16,Y+13,Z+9),T['beam_web'],uvs={'north':[0,3,16,13],'south':[0,3,16,13]})]
        if axe=='z':
            z=Z+k*16
            E+=[b((X+3,Y+1,z),(X+13,Y+3,z+16),T['beam_flange'],uvs={'up':[3,0,13,16],'down':[3,0,13,16]}),b((X+3,Y+13,z),(X+13,Y+15,z+16),T['beam_flange'],uvs={'up':[3,0,13,16],'down':[3,0,13,16]}),
                b((X+7,Y+3,z),(X+9,Y+13,z+16),T['beam_web'],uvs={'east':[0,3,16,13],'west':[0,3,16,13]})]
        if axe=='y':
            y=Y+k*16   # poteau : ailes face nord/sud, âme est-ouest
            E+=[b((X+3,y,Z+1),(X+13,y+16,Z+3),T['beam_flange'],uvs={'north':[3,0,13,16],'south':[3,0,13,16]}),b((X+3,y,Z+13),(X+13,y+16,Z+15),T['beam_flange'],uvs={'north':[3,0,13,16],'south':[3,0,13,16]}),
                b((X+7,y,Z+3),(X+9,y+16,Z+13),T['beam_web'],uvs={'east':[3,0,13,16],'west':[3,0,13,16]})]
    return E
def platine_y(x,y,z,haut=False):   # pied (posé au sol) ou chapiteau
    X,Y,Z=x*16,y*16,z*16
    return [b((X+1,Y+(15 if haut else 0),Z+1),(X+15,Y+(16 if haut else 1),Z+15),T['plate'])]
def about(x,y,z,face):            # platine d'about contre un poteau
    X,Y,Z=x*16,y*16,z*16
    if face=='north': return [b((X+2,Y+1,Z),(X+14,Y+15,Z+1),T['plate'])]
    if face=='south': return [b((X+2,Y+1,Z+15),(X+14,Y+15,Z+16),T['plate'])]
def jambe(x,y,z,sens):
    """Jambe de force : poutrelle courte à 45° entre poteau et poutre (sens +1 : monte vers +z)."""
    X,Y,Z=x*16,y*16,z*16; L=16*math.sqrt(2)
    if sens>0: o=[X+8,Y,Z+1]; ang=45
    else: o=[X+8,Y,Z+15]; ang=-45
    E=[]
    for (a0,a1,dz) in ((7,9,0),):
        pass
    if sens>0:
        E+=[b((X+5,Y,Z+1),(X+11,Y+2,Z+1+L),T['beam_flange'],rot={'origin':[X+8,Y,Z+1],'axis':'x','angle':-45},uvs={'up':[5,0,11,16],'down':[5,0,11,16]}),
            b((X+7,Y+2,Z+1),(X+9,Y+6,Z+1+L),T['beam_web'],rot={'origin':[X+8,Y,Z+1],'axis':'x','angle':-45})]
    else:
        E+=[b((X+5,Y,Z+15-L),(X+11,Y+2,Z+15),T['beam_flange'],rot={'origin':[X+8,Y,Z+15],'axis':'x','angle':45},uvs={'up':[5,0,11,16],'down':[5,0,11,16]}),
            b((X+7,Y+2,Z+15-L),(X+9,Y+6,Z+15),T['beam_web'],rot={'origin':[X+8,Y,Z+15],'axis':'x','angle':45})]
    return E
def treillis(x0,y,z,n):
    """Poutre treillis le long de x : membrures haute et basse, diagonales alternées (Warren) d'un bloc à l'autre."""
    Y,Z=y*16,z*16; E=[]; L=14*math.sqrt(2)
    for k in range(n):
        X=(x0+k)*16
        E+=[b((X,Y,Z+4),(X+16,Y+2,Z+12),T['beam_flange'],uvs={'up':[0,4,16,12],'down':[0,4,16,12]}),b((X,Y+14,Z+4),(X+16,Y+16,Z+12),T['beam_flange'],uvs={'up':[0,4,16,12],'down':[0,4,16,12]})]
        E+=[b((X,Y+2,Z+6),(X+1,Y+14,Z+10),T['bar'])]   # montant
        if k%2==0: E.append(b((X+1,Y+2,Z+6.5),(X+1+L,Y+4,Z+9.5),T['bar'],rot={'origin':[X+1,Y+2,Z+8],'axis':'z','angle':45}))
        else: E.append(b((X+1,Y+12,Z+6.5),(X+1+L,Y+14,Z+9.5),T['bar'],rot={'origin':[X+1,Y+14,Z+8],'axis':'z','angle':-45}))
    E+=[b(((x0+n)*16-1,Y+2,Z+6),((x0+n)*16,Y+14,Z+10),T['bar'])]
    return E
def chevron(xa,ya,z,n,sens):
    """Chevron en I incliné à 45° sur n blocs (sens +1 : monte vers +x)."""
    X,Y,Z=xa*16,ya*16,z*16; L=16*math.sqrt(2)*n
    if sens>0: return [b((X,Y,Z+5),(X+L,Y+2,Z+11),T['beam_flange'],rot={'origin':[X,Y,Z+8],'axis':'z','angle':45},uvs={'up':[0,5,16,11],'down':[0,5,16,11]}),
                       b((X,Y+2,Z+7),(X+L,Y+6,Z+9),T['beam_web'],rot={'origin':[X,Y,Z+8],'axis':'z','angle':45})]
    return [b((X-L,Y,Z+5),(X,Y+2,Z+11),T['beam_flange'],rot={'origin':[X,Y,Z+8],'axis':'z','angle':-45},uvs={'up':[0,5,16,11],'down':[0,5,16,11]}),
            b((X-L,Y+2,Z+7),(X,Y+6,Z+9),T['beam_web'],rot={'origin':[X,Y,Z+8],'axis':'z','angle':-45})]
def verriere(xa,ya,z0,z1,n):
    """Verrière inclinée à 45° (monte vers +x) : verre d'airain, petits-bois tous les blocs."""
    X,Y=xa*16,ya*16; L=16*math.sqrt(2)*n; E=[]; r={'origin':[X,Y+6,0],'axis':'z','angle':45}
    E.append(b((X,Y+6,z0*16),(X+L,Y+6.6,z1*16),GL,faces=("up","down"),rot=r))
    for z in range(z0,z1+1):
        E.append(b((X,Y+6,z*16-1),(X+L,Y+8,z*16+1),T['bar'],rot=r))
    for k in range(n+1):
        E.append(b((X+k*16*math.sqrt(2)-1,Y+6,z0*16),(X+k*16*math.sqrt(2)+1,Y+7.5,z1*16),T['bar'],faces=("up","north","south","east","west"),rot=r))
    return E
def gouttiere(x,y,z0,z1):
    X,Y=x*16,y*16; E=[]
    for z in range(z0,z1):
        E+=[b((X+3,Y+10,z*16),(X+13,Y+11,z*16+16),PI),b((X+3,Y+11,z*16),(X+4,Y+15,z*16+16),PI),b((X+12,Y+11,z*16),(X+13,Y+15,z*16+16),PI),
            b((X+2,Y+11,z*16+7),(X+14,Y+15.5,z*16+9),T['bar'],faces=("north","south","up"))]
    return E
def descente(x,y0,y1,z):
    X,Z=x*16,z*16; E=[b((X+6,y0*16,Z+6),(X+10,y1*16+11,Z+10),PI)]
    for y in range(y0,y1+1): E.append(b((X+5,y*16+6,Z+5),(X+11,y*16+7,Z+11),T['bar']))
    return E
def ardoise(x,y,z0,z1):   # escalier d'ardoise (toiture opaque), escalier vanilla
    E=[]
    for z in range(z0,z1):
        X,Y,Z=x*16,y*16,z*16
        E+=[b((X,Y,Z),(X+16,Y+8,Z+16),'t:block/slate_shingles'),b((X+8,Y+8,Z),(X+16,Y+16,Z+16),'t:block/slate_shingles')]
    return E
def ardoise_d(x,y,z0,z1):
    E=[]
    for z in range(z0,z1):
        X,Y,Z=x*16,y*16,z*16
        E+=[b((X,Y,Z),(X+16,Y+8,Z+16),'t:block/slate_shingles'),b((X,Y+8,Z),(X+8,Y+16,Z+16),'t:block/slate_shingles')]
    return E
def marque(x,z,tex,bras=None,rot=0):
    """Marquage : une fine couche peinte posée sur le sol (y≈0)."""
    X,Z=x*16,z*16; E=[]
    if bras is None:
        uv=[0,0,16,16]
        e=b((X,0.05,Z),(X+16,0.1,Z+16),tex,faces=("up",));
        if rot: e['faces']['up']['rotation']=rot
        # rotation des uv simulée
        if rot==90: e['faces']['up']['uv']=[0,0,16,16]; e['faces']['up']['texture']=tex+'_r90'
        return [e]
    E.append(b((X+7,0.05,Z+7),(X+9,0.1,Z+9),tex,faces=("up",),uvs={'up':[7,7,9,9]}))
    for d in bras:
        if d=='n': E.append(b((X+7,0.05,Z),(X+9,0.1,Z+7),tex,faces=("up",),uvs={'up':[7,0,9,7]}))
        if d=='s': E.append(b((X+7,0.05,Z+9),(X+9,0.1,Z+16),tex,faces=("up",),uvs={'up':[7,9,9,16]}))
        if d=='w': E.append(b((X,0.05,Z+7),(X+7,0.1,Z+9),tex,faces=("up",),uvs={'up':[7,0,9,7]}))
        if d=='e': E.append(b((X+9,0.05,Z+7),(X+16,0.1,Z+9),tex,faces=("up",),uvs={'up':[7,9,9,16]}))
    return E
# textures tournées pour flèches et passages
for nom in ('arrow_white','crossing_white'):
    im=Image.open(MQ+'textures/block/'+nom+'.png')
    im.rotate(-90).save(MQ+'textures/block/'+nom+'_r90.png'); im.rotate(90).save(MQ+'textures/block/'+nom+'_r270.png'); im.rotate(180).save(MQ+'textures/block/'+nom+'_r180.png')
def mq(t,suf=''): return 'mq:block/'+t+suf
# ---------- scène : une travée de halle ----------
E=[]
P=[(0,0),(0,4),(6,0),(6,4)]
for (x,z) in P:
    E+=poutre((x,0,z),'y',4)+platine_y(x,0,z)+platine_y(x,3,z,True)
for x in (0,6):
    E+=poutre((x,3,1),'z',3)+about(x,3,1,'north')+about(x,3,3,'south')
    E+=jambe(x,2,1,1)+jambe(x,2,3,-1)
for z in (0,4):
    E+=treillis(0,4,z,7)
# toiture : chevrons à 45°, verrière côté ouest, ardoise côté est
for z in (0,4):
    E+=chevron(0,5,z,3,1)+chevron(7,5,z,3,-1)
E+=verriere(0,5,0,5,3)
for k in range(3): E+=ardoise_d(4+k,7-k,0,5)
E+=poutre((3,8,0),'z',5)   # faîtage
E+=gouttiere(-1,5,0,5)+descente(-1,0,4,0)
# sol et machine
FL='minecraft:block/polished_andesite'
for x in range(-3,10):
    for z in range(-4,8): E+=[b((x*16,-1,z*16),(x*16+16,0,z*16+16),FL,faces=("up",))]
MA='create:block/andesite_casing'
E+=[b((48,0,32),(64,16,48),MA)]
# hachures autour de la machine
for x in (2,3,4):
    for z in (1,2,3):
        if (x,z)!=(3,2): E+=marque(x,z,mq('hatch_yellow'))
# allée : lignes jaunes le long de x à z=-2 et z=6, avec angles et un T
for x in range(-2,9):
    E+=marque(x,-2,mq('line_yellow'),'we' if x not in (-2,8) else ('es' if x==-2 else 'ws'))
    E+=marque(x,6,mq('line_yellow'),'we' if x not in (-2,8) else ('en' if x==-2 else 'wn'))
for z in range(-1,6):
    E+=marque(-2,z,mq('line_yellow'),'ns'); E+=marque(8,z,mq('line_yellow'),'ns' if z!=2 else 'nse')
E+=marque(9,2,mq('line_yellow'),'w')
for x in (0,3,6): E+=[b((x*16,0.05,-3*16),(x*16+16,0.1,-3*16+16),mq('arrow_white','_r90'),faces=("up",))]
for z in (-1,): pass
for x in (-1,): pass
E+=[b((7*16,0.05,-3*16),(7*16+16,0.1,-3*16+16),mq('crossing_white'),faces=("up",))]
A=vue(E,[-0.75,0.55,-1],1500)
# ---------- planche des pièces ----------
def place(EL,dx,dz):
    out=copy.deepcopy(EL)
    for e in out:
        e['from'][0]+=dx*16; e['to'][0]+=dx*16; e['from'][2]+=dz*16; e['to'][2]+=dz*16
        if 'rotation' in e: e['rotation']['origin'][0]+=dx*16; e['rotation']['origin'][2]+=dz*16
    return out
Q=[]
# 1. poteau + poutre + jambe de force (détail)
Q+=poutre((0,0,0),'y',2)+platine_y(0,0,0)+poutre((0,1,1),'z',2)+about(0,1,1,'north')+jambe(0,0,1,1)
# 2. poutre treillis 3 blocs
Q+=place(treillis(0,0,0,3),3,0)
# 3. marquages : ligne (droite, angle, T, croix), hachures jaune/noir et rouge/blanc, flèche, passage
M=[]
M+=marque(0,0,mq('line_yellow'),'ns')+marque(1,0,mq('line_yellow'),'es')+marque(2,0,mq('line_white'),'nse')+marque(3,0,mq('line_white'),'nsew')
M+=marque(0,1,mq('hatch_yellow'))+marque(1,1,mq('hatch_red'))+[b((32,0.05,16),(48,0.1,32),mq('arrow_white'),faces=("up",))]+[b((48,0.05,16),(64,0.1,32),mq('crossing_white'),faces=("up",))]
for x in range(4):
    for z in range(2): M+=[b((x*16,-1,z*16),(x*16+16,0,z*16+16),FL,faces=("up",))]
B=vue(Q+[b((x*16,-1,z*16),(x*16+16,0,z*16+16),FL,faces=("up",)) for x in range(-1,7) for z in range(-1,3)],[-0.8,0.5,-1],800)
C=vue(M,[-0.3,1.2,-0.6],560)
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
W=Image.new("RGBA",(max(A.width,B.width+C.width+60)+160,A.height+max(B.height,C.height)+150),(34,30,38,255)); d=ImageDraw.Draw(W)
d.text((20,10),"Halle : poteaux/poutrelles en I, jambes de force, treillis, chevrons, verrière, faîtage, gouttière",font=fo,fill=(235,215,170))
W.alpha_composite(A,(20,50))
y=A.height+70
d.text((20,y),"Détail : treillis ; poteau, platine d'about, jambe de force",font=fo,fill=(235,215,170))
d.text((B.width+80,y),"Marquages : lignes raccordées, hachures, flèche, passage",font=fo,fill=(235,215,170))
W.alpha_composite(B,(20,y+40)); W.alpha_composite(C,(B.width+80,y+40))
W.save(S+'rendu_fusion/charpente.png'); print(W.size)
