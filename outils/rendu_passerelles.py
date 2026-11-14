# Maquette des passerelles d'airain : deux styles de rambarde (industriel, ferronnerie).
import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
import rendu_modele as rm
from rendu_modele import *
rm.RAC['t']='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_root/'
ALL=("north","south","east","west","up","down")
M='t:block/airain_block'; G='t:block/airain_catwalk'; L='t:block/airain_ladder'; MS='t:block/riveted_airain'
def boite(o,fr,to,tex=M,faces=ALL,rot=None,uvfull=False):
    x,y,z=o
    f={}
    for k in faces:
        if uvfull: uv=[0,0,16,16]
        else:
            a=[fr[0]%16,fr[1]%16,fr[2]%16]; uv={"north":[0,0,2,2],"south":[0,0,2,2]}.get(k,[0,0,2,2])
            # petites pièces : un morceau poli de la texture, à l'échelle
            w=max(1,min(16,abs(to[0]-fr[0]) if k in ("north","south","up","down") else abs(to[2]-fr[2])))
            h=max(1,min(16,abs(to[1]-fr[1]) if k not in ("up","down") else abs(to[2]-fr[2])))
            uv=[0,0,w,h]
        f[k]={"texture":tex,"uv":uv}
    e={"from":[fr[0]+x*16,fr[1]+y*16,fr[2]+z*16],"to":[to[0]+x*16,to[1]+y*16,to[2]+z*16],"faces":f}
    if rot: e["rotation"]={"origin":[rot[0][0]+x*16,rot[0][1]+y*16,rot[0][2]+z*16],"axis":rot[1],"angle":rot[2]}
    return e
SOL=3      # dessus du plancher (px)
def plancher(o, h=SOL):
    return [boite(o,[0,h-2,0],[16,h,16],G,uvfull=True)]
def rambarde(o, cote, style, h=SOL, poteaux=(0,), longueur=16):
    """Rambarde le long d'un côté (cote = 'n' z=0, 's' z=16, 'w' x=0, 'e' x=16)."""
    E=[]
    def seg(a0,a1,b0,b1,y0,y1,tex=M):     # a : le long du côté, b : épaisseur
        if cote in 'ns': z0,z1=(b0,b1) if cote=='n' else (16-b1,16-b0); return boite(o,[a0,y0,z0],[a1,y1,z1],tex)
        x0,x1=(b0,b1) if cote=='w' else (16-b1,16-b0); return boite(o,[x0,y0,a0],[x1,y1,a1],tex)
    haut=h+13
    E.append(seg(0,16,0,2,haut-2,haut))                    # main courante
    E.append(seg(0,16,0.5,1.5,h+6,h+7))                    # lisse intermédiaire
    E.append(seg(0,16,0,2,h,h+1))                          # plinthe
    for p in poteaux: E.append(seg(p,p+2,0,2,h,haut))      # poteaux
    if style=='fer':
        for p in poteaux: E.append(seg(p-0.5,p+2.5,-0.5,2.5,haut,haut+2))     # pommeau
        # volutes entre lisse et main courante : deux crosses par bloc
        for c in (5,11):
            E+= [seg(c,c+1,0.5,1.5,h+7,h+10), seg(c+1,c+2,0.5,1.5,h+9,h+10), seg(c-1,c,0.5,1.5,h+9,haut-2),
                 seg(c+1,c+2,0.5,1.5,h+3,h+6), seg(c,c+1,0.5,1.5,h+1,h+3)]
    return E
def escalier(o, style):
    """Monte vers +x : 4 marches de 4 px, du plancher (3) au plancher du bloc au-dessus (19)."""
    E=[]
    for i in range(4):
        top=SOL+4*(i+1)
        E.append(boite(o,[4*i,top-2,1],[4*i+4,top,15],G,uvfull=True))
    for z0 in (0,14):                                       # limons inclinés
        E.append(boite(o,[-2,8,z0],[18,11,z0+2],M,rot=([8,9.5,8],'z',45)))
    for z0 in (0,14):                                       # rampe inclinée + poteaux
        E.append(boite(o,[-2,22,z0],[18,24,z0+2],M,rot=([8,23,8],'z',45)))
        E.append(boite(o,[0,SOL,z0],[2,SOL+13,z0+2])); E.append(boite(o,[14,SOL+16,z0],[16,SOL+29,z0+2]))
        if style=='fer':
            E.append(boite(o,[-0.5,SOL+13,z0-0.5],[2.5,SOL+15,z0+2.5])); E.append(boite(o,[13.5,SOL+29,z0-0.5],[16.5,SOL+31,z0+2.5]))
    return E
def rampe(o, h0, style):
    """Monte vers +x d'un demi-bloc : 8 tasseaux d'1 px (rampe antidérapante)."""
    E=[]
    for i in range(8):
        top=h0+1+i
        E.append(boite(o,[2*i,h0-2,1],[2*i+2,top,15],G,uvfull=True))
    for z0 in (0,14):
        E.append(boite(o,[0,h0,z0],[16,h0+1,z0+2]))
        E.append(boite(o,[0,h0+12,z0],[16,h0+13,z0+2],rot=([8,h0+16.5,8],'z',22.5)))
        E.append(boite(o,[0,h0,z0],[2,h0+13,z0+2])); E.append(boite(o,[14,h0+8,z0],[16,h0+21,z0+2]))
        if style=='fer': E.append(boite(o,[-0.5,h0+13,z0-0.5],[2.5,h0+15,z0+2.5]))
    return E
def poteau(o, style):
    E=[boite(o,[6,0,6],[10,16,10],MS),boite(o,[5,15,5],[11,16,11])]
    E.append(boite(o,[7,4,7],[9,20,9],M,rot=([8,12,8],'x',45)))           # contrefiche
    return E
def echelle(o, n, style):
    E=[]
    for k in range(n):
        E.append(boite((o[0],o[1]+k,o[2]),[0,0,14],[16,16,15],L,faces=("north","south"),uvfull=True))
        if k>=2:                                                           # crinoline
            for yy in (2,10):
                E+= [boite((o[0],o[1]+k,o[2]),[0,yy,0],[1,yy+1,14]),boite((o[0],o[1]+k,o[2]),[15,yy,0],[16,yy+1,14]),boite((o[0],o[1]+k,o[2]),[0,yy,0],[16,yy+1,1])]
            for xx in (0,7.5,15): E.append(boite((o[0],o[1]+k,o[2]),[xx,0,0],[xx+1,16,1]))
    return E
def portillon(o, style):
    E=[boite(o,[2,SOL,15],[3,SOL+12,16]),boite(o,[13,SOL,15],[14,SOL+12,16]),boite(o,[2,SOL+11,15],[14,SOL+12,16]),boite(o,[2,SOL+1,15],[14,SOL+2,16]),
       boite(o,[2,SOL+2,15],[14,SOL+11,15.01],G,faces=("north","south"),uvfull=True)]
    return E
def scene(style):
    E=[]
    # rangée 1 : passerelle, passerelle (avec portillon), escalier, palier haut sur poteau, échelle
    E+=plancher((0,0,0))+rambarde((0,0,0),'n',style)+rambarde((0,0,0),'w',style,poteaux=(0,14))+rambarde((0,0,0),'s',style)
    E+=plancher((1,0,0))+rambarde((1,0,0),'n',style)+portillon((1,0,0),style)
    E+=escalier((2,0,0),style)
    E+=plancher((3,1,0))+rambarde((3,1,0),'n',style)+rambarde((3,1,0),'s',style)+rambarde((3,1,0),'e',style,poteaux=(0,14))+poteau((3,0,0),style)
    E+=echelle((4,0,0),4,style)
    # rangée 2 : passerelle, rampe, passerelle à mi-hauteur, rampe, passerelle du bloc au-dessus
    z=2
    E+=plancher((0,0,z))+rambarde((0,0,z),'n',style)+rambarde((0,0,z),'s',style)+rambarde((0,0,z),'w',style,poteaux=(0,14))
    E+=rampe((1,0,z),SOL,style)
    E+=plancher((2,0,z),SOL+8)+rambarde((2,0,z),'n',style,h=SOL+8)+rambarde((2,0,z),'s',style,h=SOL+8)
    E+=rampe((3,0,z),SOL+8,style)
    E+=plancher((4,1,z))+rambarde((4,1,z),'n',style)+rambarde((4,1,z),'s',style)+rambarde((4,1,z),'e',style,poteaux=(0,14))+poteau((4,0,z),style)
    # sol de repère
    for x in range(-1,6):
        for zz in range(-1,4): E.append(boite((x,-1,zz),[0,15,0],[16,16,16],'t:block/fire_bricks',faces=("up",),uvfull=True))
    return E
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",26)
imgs=[]
for st,n in (('indus','Style industriel'),('fer','Style ferronnerie')):
    rm.EYE=norm([-0.55,0.75,1]); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(scene(st),{},1600)
    bb=im.getbbox(); im=im.crop(bb)
    fond=Image.new('RGBA',(im.width+40,im.height+70),(34,30,38,255)); fond.alpha_composite(im,(20,55))
    ImageDraw.Draw(fond).text((20,15),n,font=f,fill=(235,215,170))
    fond.save(sys.argv[1].replace('.png','_'+st+'.png'))
