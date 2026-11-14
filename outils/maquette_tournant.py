# Escalier tournant (quart tournant 90°) : monte d'un bloc comme l'escalier droit, en tournant autour d'un coin.
import sys, math; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
_src=open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/maquette_atelier.py').read()
exec(_src[:_src.index('f=ImageFont.truetype')])
def tournant(o, rot=0, rambarde_ext=True):
    """Décrit pour : entrée par le sud (plancher 3), sortie par l'est (19), coin intérieur au nord-est.
    4 marches en éventail autour du coin nord-est ; limon extérieur le long des faces ouest et nord."""
    E=[b(o,[13,0,0],[16,16+16,3],R_,full=True)]                 # noyau au coin intérieur (monte jusqu'au palier)
    # marches : secteurs de 22,5° autour du coin (16,0), du sud vers l'est ; approchées par des boîtes
    pas=[(0,16,8,16),(0,8,0,16),(0,16,0,8),(8,16,0,8)]
    zones=[((0,16),(10,16)),((0,9),(4,16)),((0,12),(0,6)),((7,16),(0,6))]
    zones=[((0,13),(11,16)),((0,8),(4,11)),((3,13),(0,4)),((9,13),(0,4))]
    # version lisible : chaque marche est un quart de l'éventail (boîtes en L)
    marches=[ [((0,13),(12,16))], [((0,7),(6,12)),((0,4),(0,6))], [((4,13),(0,4)),((7,13),(4,6))], [((7,13),(6,12))] ]
    for i,parts in enumerate(marches):
        top=SOL+4*(i+1)
        for (x0,x1),(z0,z1) in parts:
            E.append(b(o,[x0,top-1,z0],[x1,top,z1],G,full=True,faces=("up","down")))
            E.append(b(o,[x0,top-2,z0],[x1,top-1,z1]))
    if rambarde_ext:
        # rambarde extérieure : face ouest (marches 1-2) puis face nord (marches 2-3), en paliers
        for (c,a0,a1,i) in (('w',16,8,0),('w',8,0,1),('n',0,8,2),('n',8,13,3)):
            y=SOL+4*(i+1)+11; lo,hi=min(a0,a1),max(a0,a1)
            if c=='w': E+= [b(o,[0,y,lo],[2,y+2,hi]),b(o,[0.5,y-6,lo],[1.5,y-5,hi]),b(o,[0,y-11,lo],[2,y+2,lo+2])]
            else:      E+= [b(o,[lo,y,0],[hi,y+2,2]),b(o,[lo,y-6,0.5],[hi,y-5,1.5]),b(o,[lo,y-11,0],[lo+2,y+2,2])]
    # rotation du bloc (pas de 90°)
    for _ in range(rot//90):
        for e in E:
            fr,to=e['from'],e['to']; ox=o[0]*16; oz=o[2]*16
            nf=[ox+16-(to[2]-oz), fr[1], oz+(fr[0]-ox)]; nt=[ox+16-(fr[2]-oz), to[1], oz+(to[0]-ox)]
            e['from'],e['to']=nf,nt
            fc={}; m={'north':'east','east':'south','south':'west','west':'north','up':'up','down':'down'}
            for k,v in e['faces'].items(): fc[m[k]]=v
            e['faces']=fc
    return E
def p_tournant():
    """Escalier droit → quart tournant → escalier droit (demi-tour en deux quarts)."""
    E=plancher((0,0,2))+rambarde((0,0,2),'w')+rambarde((0,0,2),'s')+rambarde((0,0,2),'e',poteau_fin=True)
    E+=escalier_n((0,0,1))
    E+=tournant((0,1,0))
    E+=sol(range(-1,4),range(-2,4))
    return E
def escalier_n(o):
    """Escalier droit montant vers le nord (le modèle de la maquette tourné)."""
    E=escalier((0,0,0))
    for e in E:
        fr,to=e['from'],e['to']; e['from']=[fr[2],fr[1],16-to[0]]; e['to']=[to[2],to[1],16-fr[0]]
        if 'rotation' in e: oo=e['rotation']['origin']; e['rotation']['origin']=[oo[2],oo[1],16-oo[0]]; e['rotation']['axis']='x'
        fc={}; m={'north':'west','east':'north','south':'east','west':'south','up':'up','down':'down'}
        for k,v in e['faces'].items(): fc[m[k]]=v
        e['faces']=fc
        for i,v in enumerate(o): e['from'][i]+=v*16; e['to'][i]+=v*16
        if 'rotation' in e: e['rotation']['origin']=[e['rotation']['origin'][i]+o[i]*16 for i in range(3)]
    return E
def p_spirale():
    """Colimaçon 2 × 2 fait de quarts tournants autour du centre commun : un tour = 4 blocs de haut."""
    E=[]
    pos=[((0,0,1),0),((1,1,1),270),((1,2,0),180),((0,3,0),90)]
    for (o,r) in pos: E+=tournant(o,r)
    E+=sol(range(-1,3),range(-1,3))
    return E
def suspente2(o):
    """Suspente corrigée : tirants le long des deux côtés (juste à l'intérieur des rambardes)."""
    E=[]
    for z0 in (2.5,12.5):
        E.append(b(o,[7.5,-16,z0],[8.5,16,z0+1]))
        E.append(b(o,[6.5,-16,z0-0.5],[9.5,-15,z0+1.5]))
    E.append(b(o,[7,-16.5,1],[9,-15.5,15]))
    for z0 in (2.5,12.5): E.append(b(o,[5.5,15,z0-1.5],[10.5,16,z0+2.5]))
    return E
def p_suspente2():
    E=[]
    for x in (0,1,2):
        E+=plancher((x,0,0))+rambarde((x,0,0),'n')+rambarde((x,0,0),'s')
        E.append(b((x,2,0),[0,0,0],[16,16,16],'t:block/fire_bricks',full=True))
    E+=suspente2((0,1,0))+suspente2((2,1,0))+rambarde((2,0,0),'e',poteau_fin=True)+rambarde((0,0,0),'w',poteau_fin=True)
    return E
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
for nom,fn,eye in (("Quart tournant (escalier droit puis quart tournant)",p_tournant,[-0.6,0.8,1]),("Colimaçon 2 × 2 en quarts tournants",p_spirale,[-0.6,0.6,1]),("Suspente corrigée",p_suspente2,[-0.6,0.45,1])):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(fn(),{},1300); im=im.crop(im.getbbox())
    W=Image.new('RGBA',(im.width+40,im.height+80),(34,30,38,255)); W.alpha_composite(im,(20,60)); ImageDraw.Draw(W).text((20,18),nom,font=f,fill=(235,215,170))
    W.save(sys.argv[1].replace('.png','_'+fn.__name__+'.png'))
