# Maquettes planche 2 : monte-charge, toboggan, plaques, borne de carrefour, pont-levis et passerelle rétractable.
import sys, math; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
_s=open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/maquette_deco.py').read()
exec(_s[:_s.index('# ---------------------------------------------------------------- planche')])
PA='t:block/sign_fleche'; PI='t:block/sign_forge'; DA='t:block/sign_danger'; CH='t:block/airain_chain'
# ---------------------------------------------------------------- monte-charge
def mat(o):
    E=[]
    for (x,z) in ((1,1),(13,1),(1,13),(13,13)): E.append(b(o,[x,0,z],[x+2,16,z+2],FL,full='crop'))
    for y in (0,8): E+=[b(o,[1,y,1],[15,y+1,3]),b(o,[1,y,13],[15,y+1,15])]
    for y in range(0,16,2): E.append(b(o,[15,y,6],[16.5,y+1,10],OX))          # crémaillère sur la face est
    E.append(b(o,[7,0,7],[9,16,9],OX))
    return E
def cabine(o):
    E=plancher(o)+rambarde(o,'n')+rambarde(o,'s',poteau_fin=True)
    E+=[b(o,[14,0,0],[16,16,2]),b(o,[14,0,14],[16,16,16]),b(o,[14,14,0],[16,16,16])]   # cadre du portail côté est
    E+=[b(o,[-3,2,4],[1,12,12],PN,full='crop'),b(o,[-2,4,5],[0.5,10,11],OX),b(o,[0,14,6],[14,16,10])]   # carter et pignon contre le mât, traverse haute
    E+=[b(o,[1,6,0.5],[3,10,1.5],SO),lum(b(o,[1.5,8.5,0.3],[2.5,9.5,0.5],FR))]           # boîte à boutons
    return E
def p_monte():
    E=[]
    for y in range(4): E+=mat((0,y,0))
    E+=cabine((1,1,0))
    E+=plancher((2,3,0))+rambarde((2,3,0),'n')+rambarde((2,3,0),'s',poteau_fin=True)+poteau((2,2,0))+poteau((2,1,0))+poteau((2,0,0))
    return E+sol(range(0,3),range(0,1))
# ---------------------------------------------------------------- toboggan
def tob(o):
    a=-45
    return [b(o,[-3,7,2],[19,8,14],M,rot=([8,8,8],'z',a)),b(o,[-3,7,1],[19,13,2],M,rot=([8,8,8],'z',a)),b(o,[-3,7,14],[19,13,15],M,rot=([8,8,8],'z',a))]
def p_tob():
    E=plancher((0,2,0))+rambarde((0,2,0),'n')+rambarde((0,2,0),'s')+rambarde((0,2,0),'w')+poteau((0,1,0))+poteau((0,0,0))
    E+=tob((1,1,0))+tob((2,0,0))
    E+=[b((3,0,0),[0,0,2],[10,1,14]),b((3,0,0),[0,1,1],[10,4,2]),b((3,0,0),[0,1,14],[10,4,15]),b((3,0,0),[9,1,2],[10,4,14])]
    return E+sol(range(0,4),range(0,1))
# ---------------------------------------------------------------- plaques
def plaque_rambarde(o,t):
    return [b(o,[3,SOL+4,2],[13,SOL+10,2.5],t,faces=("south",),full=True),b(o,[3,SOL+4,2],[13,SOL+10,2.5],M,faces=("north","east","west","up","down"))]
def plaque_mur(o,t):
    return [b(o,[2,4,15.5],[14,12,16],t,faces=("north",),full="crop"),b(o,[2,4,15.5],[14,12,16],M,faces=("east","west","up","down"))]
def p_plaques():
    E=[]
    for x,t in ((0,PA),(1,PI),(2,DA),(3,'t:block/sign_sortie')): E+=plancher((x,0,0))+rambarde((x,0,0),'n',poteau_fin=x==3)+plaque_rambarde((x,0,0),t)
    return E+sol(range(0,4),range(0,1))
# ---------------------------------------------------------------- borne de carrefour
def fleche(o,y,ang,t=PA):
    return [b(o,[8,y,7.5],[19,y+4,8.5],t,faces=("north","south"),full=True,rot=([8,y+2,8],'y',ang)),
            b(o,[8,y,7.5],[19,y+4,8.5],M,faces=("east","up","down"),rot=([8,y+2,8],'y',ang))]
def p_borne():
    E=[b((0,0,0),[4,0,4],[12,2,12],BD,full='crop'),b((0,0,0),[6.5,2,6.5],[9.5,16,9.5],FL,full='crop'),b((0,1,0),[6.5,0,6.5],[9.5,14,9.5],FL,full='crop'),b((0,1,0),[5.5,14,5.5],[10.5,15,10.5]),b((0,1,0),[6.5,15,6.5],[9.5,16,9.5],BD,full='crop')]
    E+=fleche((0,1,0),9,0)+fleche((0,1,0),4,45,PI)+fleche((0,0,0),13,-45)
    return E+sol(range(-1,2),range(-1,2))
# ---------------------------------------------------------------- pont-levis et passerelle rétractable
def p_pont():
    E=[]
    for x in (0,4):
        for z in range(2):
            E+=cube((x,0,z))+cube((x,-1,z))
    for x in (1,2,3):
        for z in range(2): E.append(b((x,-1,z),[0,0,0],[16,13,16],'t:block/maq_verre',faces=("up",),full=True))
    # tablier relevé à 60° depuis la rive ouest (3 blocs, 2 de large), portique et chaînes
    ang=60
    for z in range(2):
        for k in range(3):            # un panneau par bloc : rien ne s'étire
            E.append(b((1,1,z),[16*k,-1,0],[16*k+16,1,16],PN,faces=("up","down"),rot=([0,0,8],'z',ang),full=True))
            E.append(b((1,1,z),[16*k,1,0 if z==0 else 14],[16*k+16,3,2 if z==0 else 16],BD,rot=([0,0,8],'z',ang),full='crop'))
    for z0 in (0,30):
        E.append(b((0,1,0),[6,0,z0],[8,48,z0+2],FL,full='crop'))
    E.append(b((0,1,0),[6,46,0],[8,48,32],BD,full='crop'))
    c=math.radians(ang); tx=16+48*math.cos(c)*0.9; ty=16+48*math.sin(c)*0.9
    for z0 in (1,31):
        dx,dy=tx-7,ty-47; L_=math.hypot(dx,dy); a=math.degrees(math.atan2(dy,dx))
        E.append(b((0,0,0),[7,62.5,z0-0.5],[7+L_,63.5,z0+0.5],CH,rot=([7,63,z0],'z',a)))
    return E+sol(range(0,5),range(0,2))
def p_retract():
    E=[]
    for x in (0,3): E+=cube((x,0,0))+plancher((x,1,0))+rambarde((x,1,0),'n')+rambarde((x,1,0),'s')
    E+=[b((1,0,0),[0,10,0],[16,16,16],PN,faces=("up","down"),full=True),b((1,0,0),[0,10,0],[16,16,16],FZ,faces=("north","south","east","west"),full='crop')]                       # carter (le pont rentre dedans)
    E+=plancher((1,1,0))+rambarde((1,1,0),'n')+rambarde((1,1,0),'s')
    E+=[b((2,1,0),[0,1,0],[8,3,16]),b((2,1,0),[0,3,0],[8,16,2]),b((2,1,0),[0,3,14],[8,16,16])]   # à moitié sorti
    return E+sol(range(0,4),range(0,1))
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",26)
def vue(E,eye,taille=900):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(E,{},taille); return im.crop(im.getbbox())
V1=[("Monte-charge à crémaillère",p_monte,[-0.6,0.45,1]),("Toboggan de descente",p_tob,[-0.4,0.5,1]),
    ("Plaques émaillées",p_plaques,[-0.4,0.4,1]),("Borne de carrefour",p_borne,[-0.6,0.4,1]),
    ("Pont-levis (relevé)",p_pont,[-0.5,0.55,1]),("Passerelle rétractable (à moitié sortie)",p_retract,[-0.5,0.6,1])]
ims=[(t,vue(fn(),eye)) for t,fn,eye in V1]
for k in range(len(ims)):
    t,i=ims[k]; s=min(1,700/i.width,520/i.height); ims[k]=(t,i.resize((int(i.width*s),int(i.height*s))))
W=Image.new('RGBA',(2*760,3*600),(34,30,38,255)); d=ImageDraw.Draw(W)
for k,(t,i) in enumerate(ims):
    x0=(k%2)*760; y0=(k//2)*600
    d.text((x0+20,y0+15),t,font=f,fill=(235,215,170)); W.alpha_composite(i,(x0+30+(700-i.width)//2,y0+60+(520-i.height)//2))
W.save('rendu_fusion/planche_nav.png')
