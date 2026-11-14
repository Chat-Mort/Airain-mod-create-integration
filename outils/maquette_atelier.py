# Maquettes : escalier en colimaçon, rambarde seule, passerelle suspendue, conduit d'air.
import sys, math; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
_src=open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/passerelles_v2.py').read()
exec(_src[:_src.index('def scene():')])
R_='t:block/riveted_airain'
def colimacon(o, ouverts=()):
    """4 marches en quart de cercle autour d'un fût, du plancher (3) au plancher du bloc au-dessus (19) ; main courante en pente."""
    E=[b(o,[6,0,6],[10,16,10],R_,full=True)]
    quarts=[((0,8),(8,16)),((0,8),(0,8)),((8,16),(0,8)),((8,16),(8,16))]      # SO, NO, NE, SE
    for i,((x0,x1),(z0,z1)) in enumerate(quarts):
        top=SOL+4*(i+1)
        E.append(b(o,[x0,top-1,z0],[x1,top,z1],G,full=True,faces=("up","down")))
        E.append(b(o,[x0,top-2,z0],[x1,top-1,z1]))
    # pourtour : 8 demi-côtés dans l'ordre de la montée ; main courante plate qui monte de 2 px à chaque demi-côté
    seg=[('w',16,8),('w',8,0),('n',0,8),('n',8,16),('e',0,8),('e',8,16),('s',16,8),('s',8,0)]
    for k,(c,a0,a1) in enumerate(seg):
        if c in ouverts: continue
        y=SOL+2*k+12
        lo,hi=min(a0,a1),max(a0,a1)
        dep=a0 if a0<a1 else a0-2                    # départ du demi-côté
        epais=2 if k%2==0 else 1                     # gros poteau aux coins, barreau entre les deux
        if c in 'we':
            xx=0 if c=='w' else 14
            E.append(b(o,[xx,y,lo],[xx+2,y+2,hi]))
            E.append(b(o,[xx+0.5,y-6,lo],[xx+1.5,y-5,hi]))
            E.append(b(o,[xx+(0 if epais==2 else 0.5),y-12,dep],[xx+(2 if epais==2 else 1.5),y+2,dep+epais]))
        else:
            zz=0 if c=='n' else 14
            E.append(b(o,[lo,y,zz],[hi,y+2,zz+2]))
            E.append(b(o,[lo,y-6,zz+0.5],[hi,y-5,zz+1.5]))
            E.append(b(o,[dep,y-12,zz+(0 if epais==2 else 0.5)],[dep+epais,y+2,zz+(2 if epais==2 else 1.5)]))
    return E
def rambarde_seule(o, cotes):
    E=[]
    for c in cotes: E+=rambarde(o,c,h=0,poteau_debut=True,poteau_fin=True)
    return E
def suspente(o, plafond=True):
    """Deux tirants, plaque au plafond, étrier et traverse sous le plancher du bloc du dessous."""
    E=[]
    for x0 in (1,14):
        E.append(b(o,[x0,-16,7.5],[x0+1,16,8.5]))
        E.append(b(o,[x0-0.5,-16,6.5],[x0+1.5,-15,9.5]))
    E.append(b(o,[1,-16.5,7],[15,-15.5,9]))
    if plafond:
        for x0 in (1,14): E.append(b(o,[x0-1.5,15,5.5],[x0+2.5,16,10.5]))
    return E
def gaine(o, axe):
    if axe=='x': return [b(o,[0,3,3],[16,13,13],'t:block/airain_block',faces=("north","south","up","down"),full=True),b(o,[0,2,2],[2,14,14]),b(o,[14,2,2],[16,14,14])]
    return [b(o,[3,3,0],[13,13,16],'t:block/airain_block',faces=("east","west","up","down"),full=True),b(o,[2,2,0],[14,14,2]),b(o,[2,2,14],[14,14,16])]
def coude(o):
    return [b(o,[3,3,3],[13,13,13],'t:block/airain_block',full=True),b(o,[0,3,3],[3,13,13],'t:block/airain_block',faces=("north","south","up","down"),full=True),
            b(o,[3,3,13],[13,13,16],'t:block/airain_block',faces=("east","west","up","down"),full=True),b(o,[0,2,2],[2,14,14]),b(o,[2,2,14],[14,14,16])]
def bouche_sud(o):
    """Bouche de soufflage tournée vers le sud : bride, cône, cadre et lames inclinées."""
    E=[b(o,[2,2,0],[14,14,2]),b(o,[3,3,2],[13,13,10],R_,faces=("east","west","up","down"),full=True),
       b(o,[1,1,10],[15,15,16],'t:block/airain_block',faces=("east","west","up","down"),full=True)]
    for yy in (3,6,9,12): E.append(b(o,[2,yy,11],[14,yy+1,16],rot=([8,yy+0.5,13.5],'x',22.5)))
    return E
def ventilo(o): return [b(o,[0,0,0],[16,16,16],"create:block/fan_side",full=True)]
def sol(xs,zs): return [b((x,-1,z),[0,15,0],[16,16,16],'t:block/fire_bricks',faces=("up",),full=True) for x in xs for z in zs]
def p_colimacon():
    E=colimacon((0,0,0),ouverts=('s',))+colimacon((0,1,0))+colimacon((0,2,0),ouverts=('e',))
    E+=plancher((0,0,1))+rambarde((0,0,1),'w')+rambarde((0,0,1),'s')+rambarde((0,0,1),'e',poteau_fin=True)
    E+=plancher((1,3,0))+rambarde((1,3,0),'n')+rambarde((1,3,0),'s')+rambarde((1,3,0),'e',poteau_fin=True)+poteau((1,2,0))
    return E+sol(range(-1,3),range(-1,3))
def p_rambarde():
    E=[]
    for x in range(0,3):
        E.append(b((x,0,0),[0,0,0],[16,16,16],'t:block/fire_bricks',full=True)); E+=rambarde_seule((x,1,0),'s')
    E.append(b((2,0,1),[0,0,0],[16,16,16],'t:block/fire_bricks',full=True)); E+=rambarde_seule((2,1,1),'e')+rambarde_seule((2,1,0),'e')
    return E+sol(range(-1,4),range(-1,3))
def p_suspente():
    E=[]
    for x in (0,1,2):
        E+=plancher((x,0,0))+rambarde((x,0,0),'n')+rambarde((x,0,0),'s')
        E.append(b((x,2,0),[0,0,0],[16,16,16],'t:block/fire_bricks',full=True))
    E+=suspente((0,1,0))+suspente((2,1,0))+rambarde((2,0,0),'e',poteau_fin=True)+rambarde((0,0,0),'w',poteau_fin=True)
    return E
def p_conduit():
    E=ventilo((0,0,0))+gaine((1,0,0),'x')+coude((2,0,0))+gaine((2,0,1),'z')
    for e in bouche_sud((2,0,2)): E.append(e)
    return E+sol(range(-1,4),range(-1,5))
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
for nom,fn,eye in (("Escalier en colimaçon",p_colimacon,[-0.55,0.85,1]),("Rambarde seule",p_rambarde,[-0.6,0.7,1]),("Passerelle suspendue",p_suspente,[-0.6,0.45,1]),("Conduit d'air",p_conduit,[-0.6,0.8,1])):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(fn(),{},1300); im=im.crop(im.getbbox())
    W=Image.new('RGBA',(im.width+40,im.height+80),(34,30,38,255)); W.alpha_composite(im,(20,60)); ImageDraw.Draw(W).text((20,18),nom,font=f,fill=(235,215,170))
    W.save(sys.argv[1].replace('.png','_'+fn.__name__+'.png'))
