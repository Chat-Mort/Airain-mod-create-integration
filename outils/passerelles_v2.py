# Passerelles d'airain, style industriel, détaillées : plancher caillebotis avec cadre, rambarde (poteaux, main courante,
# lisse, plinthe), escalier à limons, rampe à tasseaux, poteau à contrefiche, échelle à crinoline, portillon.
import sys, math; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
rm.RAC['t']='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_root/'
ALL=("north","south","east","west","up","down")
M='t:block/airain_block'; G='t:block/airain_catwalk'; L='t:block/airain_ladder'
SOL=3
def b(o,fr,to,tex=M,faces=ALL,rot=None,full=False,rescale=False):
    x,y,z=o; f={}
    for k in faces:
        if full: uv=[0,0,16,16]
        else:
            dx,dy,dz=[abs(to[i]-fr[i]) for i in range(3)]
            w_,h_={"north":(dx,dy),"south":(dx,dy),"east":(dz,dy),"west":(dz,dy),"up":(dx,dz),"down":(dx,dz)}[k]
            uv=[2,2,2+max(0.5,min(12,w_)),2+max(0.5,min(12,h_))]
        f[k]={"texture":tex,"uv":uv}
    e={"from":[fr[0]+x*16,fr[1]+y*16,fr[2]+z*16],"to":[to[0]+x*16,to[1]+y*16,to[2]+z*16],"faces":f}
    if rot:
        e["rotation"]={"origin":[rot[0][0]+x*16,rot[0][1]+y*16,rot[0][2]+z*16],"axis":rot[1],"angle":rot[2]}
        if rescale:   # étire l'élément comme le fait Minecraft (rescale) pour qu'il couvre la diagonale
            c=1/math.cos(math.radians(abs(rot[2])))
            ax={'x':(1,2),'y':(0,2),'z':(0,1)}[rot[1]]
            for i in ax:
                o_=e["rotation"]["origin"][i]
                e["from"][i]=o_+(e["from"][i]-o_)*c; e["to"][i]=o_+(e["to"][i]-o_)*c
    return e
def plancher(o,h=SOL,cotes='nswe'):
    E=[b(o,[0,h-2,0],[16,h,16],G,full=True,faces=("up","down"))]
    # cadre : cornière d'1 px sur les bords, 2 px de haut
    if 'n' in cotes or True: E.append(b(o,[0,h-2,0],[16,h,1]))
    E.append(b(o,[0,h-2,15],[16,h,16]))
    E.append(b(o,[0,h-2,1],[1,h,15])); E.append(b(o,[15,h-2,1],[16,h,15]))
    return E
def rambarde(o,cote,h=SOL,poteau_debut=True,poteau_fin=False):
    """cote : n (z=0), s (z=16), w (x=0), e (x=16). Main courante à 13 px au-dessus du plancher."""
    E=[]
    def seg(a0,a1,c0,c1,y0,y1):
        if cote=='n': return b(o,[a0,y0,c0],[a1,y1,c1])
        if cote=='s': return b(o,[a0,y0,16-c1],[a1,y1,16-c0])
        if cote=='w': return b(o,[c0,y0,a0],[c1,y1,a1])
        return b(o,[16-c1,y0,a0],[16-c0,y1,a1])
    E.append(seg(0,16,0,2,h+11,h+13))          # main courante (2 × 2)
    E.append(seg(0,16,0.5,1.5,h+6,h+7))         # lisse intermédiaire
    E.append(seg(0,16,0.5,1,h,h+3))             # plinthe (garde-pied)
    if poteau_debut: E.append(seg(0,2,0,2,h,h+13))
    if poteau_fin: E.append(seg(14,16,0,2,h,h+13))
    return E
def escalier(o):
    """Monte vers +x : 4 marches caillebotis de 4 px sur deux limons à 45°."""
    E=[]
    for i in range(4):
        top=SOL+4*(i+1)
        E.append(b(o,[4*i,top-1,2],[4*i+4,top,14],G,full=True,faces=("up","down")))
        E.append(b(o,[4*i+3,top-2,2],[4*i+4,top,14]))                    # nez de marche
    for z0 in (0,14):
        E.append(b(o,[0,SOL+5,z0+0.5],[16,SOL+8,z0+1.5],rot=([8,SOL+6.5,8],'z',45),rescale=True))   # limon
        E.append(b(o,[0,SOL+16+2.5,z0],[16,SOL+16+4.5,z0+2],rot=([8,SOL+19.5,8],'z',45),rescale=True))  # main courante
        E.append(b(o,[0,SOL+11.5,z0+0.5],[16,SOL+12.5,z0+1.5],rot=([8,SOL+12,8],'z',45),rescale=True))  # lisse
        E.append(b(o,[0,SOL,z0],[2,SOL+13,z0+2])); E.append(b(o,[14,SOL+16,z0],[16,SOL+29,z0+2]))     # poteaux
    return E
def rampe(o,h0):
    """Monte vers +x d'une dalle (8 px) : 8 tasseaux d'1 px."""
    E=[]
    for i in range(8):
        E.append(b(o,[2*i,h0-2+i,1],[2*i+2,h0+i,15],G,full=True,faces=("up","down")))
        E.append(b(o,[2*i+1,h0-1+i,1],[2*i+2,h0+i+0.5,15]))           # tasseau
    for z0 in (0,14):
        ang=math.degrees(math.atan(8/16))   # pour l'aperçu ; en jeu 22,5° (étiré)
        E.append(b(o,[0,h0+4+11,z0],[16,h0+4+13,z0+2],rot=([8,h0+4+12,8],'z',22.5),rescale=True))
        E.append(b(o,[0,h0+4+6,z0+0.5],[16,h0+4+7,z0+1.5],rot=([8,h0+4+6.5,8],'z',22.5),rescale=True))
        E.append(b(o,[0,h0+2,z0+0.5],[16,h0+4,z0+1],rot=([8,h0+3,8],'z',22.5),rescale=True))
        E.append(b(o,[0,h0,z0],[2,h0+13,z0+2])); E.append(b(o,[14,h0+8,z0],[16,h0+21,z0+2]))
    return E
def poteau(o, bas=True, haut=True):
    """Fût de 4 × 4 ; s'évase au contact du sol (platine + embase) et sous la passerelle (chapiteau + sommier)."""
    E=[b(o,[6,0,6],[10,16,10],'t:block/riveted_airain',full=True)]
    if bas: E+= [b(o,[2,0,2],[14,1,14]), b(o,[4,1,4],[12,2.5,12]), b(o,[5,2.5,5],[11,4,11])]
    if haut: E+= [b(o,[5,12,5],[11,13.5,11]), b(o,[4,13.5,4],[12,15,12]), b(o,[1,15,1],[15,16,15])]
    return E
def echelle(o,n):
    """Contre un mur au nord du bloc (z=0) ; crinoline vers le sud à partir du 3e bloc."""
    E=[]
    for k in range(n):
        p=(o[0],o[1]+k,o[2])
        E+= [b(p,[2,0,1],[4,16,3]),b(p,[12,0,1],[14,16,3])]                    # montants
        for yy in (2,6,10,14): E.append(b(p,[4,yy,1.5],[12,yy+1,2.5]))       # barreaux
        if k>=2:
            for yy in (4,12):
                E+= [b(p,[1,yy,1],[2,yy+1,13]),b(p,[14,yy,1],[15,yy+1,13]),b(p,[1,yy,13],[15,yy+1,14])]
            for xx in (1,7.5,14): E.append(b(p,[xx,0,13],[xx+1,16,14]))
    return E
def portillon(o,cote='n',h=SOL):
    """Portillon : cadre, traverse au milieu, deux petites écharpes (bas → milieu, milieu → haut), loquet."""
    z0,z1=(0,1) if cote=='n' else (15,16)
    zc=(z0+z1)/2
    E=[b(o,[2,h+1,z0],[3,h+12,z1]),b(o,[13,h+1,z0],[14,h+12,z1]),b(o,[2,h+11,z0],[14,h+12,z1]),b(o,[2,h+1,z0],[14,h+2,z1]),
       b(o,[3,h+6,z0+0.2],[13,h+7,z1-0.2]),
       b(o,[3,h+3.5,z0+0.3],[13,h+4.5,z1-0.3],rot=([8,h+4,zc],'z',22.5),rescale=True),
       b(o,[3,h+8.5,z0+0.3],[13,h+9.5,z1-0.3],rot=([8,h+9,zc],'z',22.5),rescale=True),
       b(o,[14,h+7,z0-0.5],[15,h+9,z1+0.5]),
       b(o,[0,h,0 if cote=='n' else 14],[2,h+13,2 if cote=='n' else 16]),b(o,[14,h,0 if cote=='n' else 14],[16,h+13,2 if cote=='n' else 16])]
    return E
def mur(o,n):
    return [b((o[0],o[1]+k,o[2]),[0,0,0],[16,16,16],'t:block/fire_bricks',full=True) for k in range(n)]
def scene():
    E=[]
    # 1 · passerelle en L au sol, avec portillon
    E+=plancher((0,0,0))+rambarde((0,0,0),'n')+rambarde((0,0,0),'w',poteau_fin=True)
    E+=plancher((1,0,0))+portillon((1,0,0),'n')+rambarde((1,0,0),'e',poteau_fin=True)
    E+=plancher((0,0,1))+rambarde((0,0,1),'w')+rambarde((0,0,1),'s')+rambarde((0,0,1),'e',poteau_fin=True)
    # 2 · escalier vers un palier sur poteau
    E+=plancher((3,0,0))+rambarde((3,0,0),'n')+rambarde((3,0,0),'s')+rambarde((3,0,0),'w',poteau_fin=True)
    E+=escalier((4,0,0))
    E+=plancher((5,1,0))+poteau((5,0,0))+rambarde((5,1,0),'n')+rambarde((5,1,0),'s')+rambarde((5,1,0),'e',poteau_fin=True)
    # 3 · rampe, mi-hauteur, rampe
    z=3
    E+=plancher((0,0,z))+rambarde((0,0,z),'w')+rambarde((0,0,z),'n')+rambarde((0,0,z),'s')
    E+=rampe((1,0,z),SOL)
    E+=plancher((2,0,z),SOL+8)+rambarde((2,0,z),'n',h=SOL+8)+rambarde((2,0,z),'s',h=SOL+8)
    E+=rampe((3,0,z),SOL+8)
    E+=plancher((4,1,z))+poteau((4,0,z))+rambarde((4,1,z),'n')+rambarde((4,1,z),'s')+rambarde((4,1,z),'e',poteau_fin=True)
    # 4 · échelle à crinoline contre un mur
    E+=mur((7,0,2),5)+echelle((7,0,3),5)
    for x in range(-1,9):
        for zz in range(-1,5): E.append(b((x,-1,zz),[0,15,0],[16,16,16],'t:block/fire_bricks',faces=("up",),full=True))
    return E
def gros_plan():
    E=plancher((0,0,0))+portillon((0,0,0),'s')+rambarde((0,0,0),'n')+rambarde((0,0,0),'w',poteau_fin=True)+escalier((1,0,0))+plancher((2,1,0))+rambarde((2,1,0),'n')+rambarde((2,1,0),'e',poteau_fin=True)+poteau((2,0,0))
    for x in range(-1,4):
        for zz in range(-1,2): E.append(b((x,-1,zz),[0,15,0],[16,16,16],'t:block/fire_bricks',faces=("up",),full=True))
    return E
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",26)
for nom,E,eye,taille in (('vue',scene(),[-0.6,0.85,1],1700),('gros_plan',gros_plan(),[-0.5,0.6,1],1300)):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(E,{},taille); im=im.crop(im.getbbox())
    fond=Image.new('RGBA',(im.width+40,im.height+40),(34,30,38,255)); fond.alpha_composite(im,(20,20))
    fond.save(sys.argv[1].replace('.png','_'+nom+'.png'))
