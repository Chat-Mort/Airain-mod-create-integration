# Maquettes : allégeur impérial (dans une ligne d'arbres) et surcompresseur impérial (contre un générateur).
src=open('maquette_meca.py').read(); exec(src[:src.index("gif('anim_monte_charge.gif'")])
CI='t:block/chiseled_airain'; SH='create:block/axis'; WH='create:block/water_wheel'
def arbre(o,x0,x1):   # arbre de Create le long de x
    return [b(o,[x0,6,6],[x1,10,10],'create:block/axis',faces=("north","south","up","down"),full=True)]
def allegeur(o,ang):
    """Cadre ouvert : deux flasques ciselés aux bouts de l'arbre, quatre colonnes cannelées, un grand volant d'inertie au milieu."""
    E=[]
    for x0 in (0,13):
        E+=[b(o,[x0,0,0],[x0+3,16,16],CI,faces=("east","west"),full=True),b(o,[x0,0,0],[x0+3,16,16],BD,faces=("north","south","up","down"),full='crop')]
    for (y,z) in ((0,0),(0,14),(14,0),(14,14)):
        E.append(b(o,[3,y,z],[13,y+2,z+2],'t:block/airain_fluted',full='crop'))
    # volant : jante octogonale rouge impérial, moyeu, rayons
    for k in (0,45):
        E.append(b(o,[6,1.5,1.5],[10,14.5,14.5],OX,faces=("east","west"),full='crop',rot=([8,8,8],'x',ang+k)))
        E.append(b(o,[6,1.5,1.5],[10,14.5,14.5],BD,faces=("north","south","up","down"),full='crop',rot=([8,8,8],'x',ang+k)))
    E.append(b(o,[5.5,5,5],[10.5,11,11],PN,full='crop',rot=([8,8,8],'x',ang)))
    E+=arbre(o,-4,0)+arbre(o,16,20)
    return E
def surcomp(o,ang):
    E=[b(o,[0,0,2],[16,4,14],PN,faces=("up",),full='crop'),b(o,[0,0,2],[16,4,14],BD,faces=("north","south","east","west"),full='crop')]
    # cylindre de compression, couronné de frises, avec 4 ailettes
    E+=[b(o,[3,4,4],[13,13,12],'t:block/airain_frieze',faces=("north","south","east","west"),full='crop'),b(o,[3,13,4],[13,14,12],PN,faces=("up",),full='crop'),
        b(o,[2,12,3],[14,13,13],BD,full='crop'),b(o,[2,4,3],[14,5,13],BD,full='crop')]
    for z in (2.5,13): E.append(b(o,[4,6,z],[12,11,z+0.5],OX))
    # manomètre et tuyau de raccord vers le générateur (face ouest)
    E+=[b(o,[6,14,6],[10,17,10],'t:block/airain_pipe_vertical',full='crop'),b(o,[5,17,7.5],[11,22,8.5],M),b(o,[5.6,17.6,8.5],[10.4,21.4,8.6],'t:block/gauge_face',faces=("south",),full=True)]
    E+=[b(o,[-2,6,6],[3,10,10],'t:block/airain_pipe',full='crop'),b(o,[-2.5,5.5,5.5],[-1.5,10.5,10.5],BD,full='crop')]
    E.append(b(o,[7.75,19.5,8.65],[8.25,21,8.7],SO,faces=("south",),rot=([8,19.5,8.65],'z',-60+120*ang/360)))
    return E
def roue(o):    # roue à eau de Create (évoquée)
    return [b(o,[0,0,0],[16,16,16],'create:block/water_wheel',full=True)] if False else [b(o,[6,0,0],[10,16,16],'t:block/maq_sombre',faces=("east","west"),full=True),b(o,[6,0,0],[10,16,16],M,faces=("north","south","up","down"))]
def scene(t):
    ang=t*360
    E=allegeur((1,0,0),ang)+arbre((0,0,0),0,16)+arbre((2,0,0),0,16)
    E+=surcomp((5,0,0),ang)+roue((4,0,0))
    return E+sol(range(0,6),range(0,1))
def vue(E,eye,taille=640):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    return rendre(E,{},taille)
im=vue(scene(0.1),[-0.45,0.55,1],1100); im=im.crop(im.getbbox())
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
W=Image.new('RGBA',(max(im.width+40,1240),im.height+80),(34,30,38,255)); W.alpha_composite(im,(20,60))
ImageDraw.Draw(W).text((20,15),"Allégeur impérial (dans la ligne d'arbres)  ·  Surcompresseur impérial (contre un générateur)",font=fo,fill=(235,215,170))
W.save('rendu_fusion/boost.png')
