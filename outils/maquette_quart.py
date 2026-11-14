# Quart tournant : entrée par le sud (plancher 3), sortie par l'est (19, le plancher du bloc voisin un cran plus haut).
# 4 marches en éventail autour du coin sud-est (secteurs de 22,5°), main courante extérieure sur les faces ouest et nord.
import sys, math; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
_src=open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/maquette_tournant.py').read()
exec(_src[:_src.index('def tournant(')])
def marche_de(x,z):
    """Indice de la marche (0 à 3) d'une case : selon l'angle vu du coin sud-est, de l'ouest (0°) au nord (90°)."""
    dx,dz=16-x,16-z
    t=math.degrees(math.atan2(dz,dx))
    return min(3,int(t//22.5))
def quart(o, sens=1):
    E=[]
    cases={}
    for z in range(0,16,2):
        for x in range(0,16,2):
            if x>=13 and z>=13: continue                       # le noyau du coin
            cases[(x,z)]=marche_de(x+1,z+1)
    # fusion des cases d'une même marche ligne par ligne
    for z in range(0,16,2):
        x=0
        while x<16:
            if (x,z) not in cases: x+=2; continue
            i=cases[(x,z)]; x1=x
            while (x1+2,z) in cases and cases[(x1+2,z)]==i: x1+=2
            top=SOL+4*(i+1)
            E.append(b(o,[x,top-1,z],[x1+2,top,z+2],G,faces=("up","down"),full=False))
            E.append(b(o,[x,top-2,z],[x1+2,top-1,z+2],faces=("north","south","east","west","down")))
            x=x1+2
    # nez de marche (bordure claire) : le long des limites entre marches, visuel seulement → on garde simple
    E.append(b(o,[13,0,13],[16,SOL+16+13,16],R_,full=True))      # noyau (poteau d'angle intérieur)
    # main courante extérieure : ouest (marches 0 puis 1), nord (marches 2 puis 3)
    for (c,lo,hi,i) in (('w',8,16,0),('w',0,8,1),('n',0,8,2),('n',8,16,3)):
        y=SOL+4*(i+1)+11
        if c=='w': E+= [b(o,[0,y,lo],[2,y+2,hi]),b(o,[0.5,y-6,lo],[1.5,y-5,hi]),b(o,[0.5,y-11,lo],[1,y-8,hi])]
        else:      E+= [b(o,[lo,y,0],[hi,y+2,2]),b(o,[lo,y-6,0.5],[hi,y-5,1.5]),b(o,[lo,y-11,0.5],[hi,y-8,1])]
    for (x,z,i0) in ((0,14,0),(0,0,1),(14,0,3)):                 # poteaux : sud-ouest (bas), nord-ouest, nord-est (haut)
        y=SOL+4*(i0+1)
        E.append(b(o,[x,y-4 if i0 else SOL,z],[x+2,y+13,z+2]))
    if sens<0:                                                    # tourne à gauche : miroir est-ouest
        for e in E:
            fr,to=e['from'],e['to']; ox=o[0]*16
            e['from'][0],e['to'][0]=2*ox+16-to[0],2*ox+16-fr[0]
            f=e['faces']; f['east'],f['west']=f.get('west'),f.get('east')
            e['faces']={k:v for k,v in f.items() if v}
    return E
def scene():
    E=plancher((0,0,2))+rambarde((0,0,2),'w')+rambarde((0,0,2),'s')+rambarde((0,0,2),'e',poteau_fin=True)
    E+=quart((0,0,1))
    E+=plancher((1,1,1))+rambarde((1,1,1),'n')+rambarde((1,1,1),'s')+rambarde((1,1,1),'e',poteau_fin=True)+poteau((1,0,1))
    # deuxième exemple : quart tournant à gauche
    E+=plancher((4,0,2))+rambarde((4,0,2),'w')+rambarde((4,0,2),'s')+rambarde((4,0,2),'e',poteau_fin=True)
    E+=quart((4,0,1),sens=-1)
    E+=plancher((3,1,1))+rambarde((3,1,1),'n')+rambarde((3,1,1),'s')+rambarde((3,1,1),'w',poteau_fin=True)+poteau((3,0,1))
    return E+sol(range(-1,6),range(-1,4))
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
for nom,eye,suf in (("Quart tournant : à droite et à gauche",[-0.5,0.95,1],'a'),("Vu de plus bas",[-0.9,0.45,1],'b')):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(scene(),{},1500); im=im.crop(im.getbbox())
    W=Image.new('RGBA',(im.width+40,im.height+80),(34,30,38,255)); W.alpha_composite(im,(20,60)); ImageDraw.Draw(W).text((20,18),nom,font=f,fill=(235,215,170))
    W.save(sys.argv[1].replace('.png','_'+suf+'.png'))
