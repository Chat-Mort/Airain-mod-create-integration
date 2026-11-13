# Maquette : escalier à palier (marche droite, palier mi-hauteur, marche à 90°)
_s=open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/maquette_quart.py').read()
exec(_s[:_s.index('def scene():')])
def palier(o, sens=1):
    E=[]
    def dalle(a,c,top):
        E.append(b(o,[a[0],top-1,a[1]],[c[0],top,c[1]],G,faces=("up","down"),full=False))
        E.append(b(o,[a[0],top-2,a[1]],[c[0],top-1,c[1]],faces=("north","south","east","west","down")))
    dalle((0,12),(12,16),SOL+4)          # marche 1 (entrée sud)
    dalle((0,0),(12,12),SOL+8)           # palier mi-hauteur
    dalle((12,0),(16,12),SOL+12)         # marche 2 (sortie est)
    E.append(b(o,[12,0,12],[16,SOL+16+13,16],R_,full=True))   # poteau d'angle
    y=SOL+8+11                                                 # rambardes ouest et nord au niveau du palier
    E+= [b(o,[0,y,0],[2,y+2,16]),b(o,[0.5,y-6,0],[1.5,y-5,16]),b(o,[0.5,y-11,0],[1,y-8,16])]
    E+= [b(o,[0,y,0],[16,y+2,2]),b(o,[0,y-6,0.5],[16,y-5,1.5]),b(o,[0,y-11,0.5],[16,y-8,1])]
    for (x,z) in ((0,14),(0,0),(14,0)):
        E.append(b(o,[x,SOL+4,z],[x+2,y+2,z+2]))
    if sens<0:
        for e in E:
            fr,to=e['from'],e['to']; ox=o[0]*16
            e['from'][0],e['to'][0]=2*ox+16-to[0],2*ox+16-fr[0]
            f=e['faces']; f['east'],f['west']=f.get('west'),f.get('east')
            e['faces']={k:v for k,v in f.items() if v}
    return E
fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
imgs=[]
for eye in ([-0.35,1.1,0.9],[1,0.6,0.9],[-0.9,0.7,0.6]):
    E=palier((0,0,0))+plancher((0,0,1))+plancher((1,1,0))+sol(range(-1,3),range(-1,3))
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(E,{},800); imgs.append(im.crop(im.getbbox()))
W=Image.new('RGBA',(sum(i.width for i in imgs)+80,max(i.height for i in imgs)+80),(34,30,38,255))
x=20
for i in imgs: W.alpha_composite(i,(x,60)); x+=i.width+20
ImageDraw.Draw(W).text((20,18),"Escalier à palier : marche → palier mi-hauteur → marche à 90°",font=fo,fill=(235,215,170))
W.save('rendu_fusion/palier.png')
