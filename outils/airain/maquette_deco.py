# Maquettes planche 1 : tuyauterie + manomètre, lampes d'atelier, garde-corps vitré, plancher technique, établi, réverbères.
import sys, math; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
_src=open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/passerelles_v2.py').read()
exec(_src[:_src.index('def scene():')])
_b=b
def b(o,fr,to,tex=M,faces=ALL,rot=None,full=False,rescale=False):
    # full='crop' : la texture est prise pixel pour pixel (centrée), jamais étirée ni tassée
    if full!='crop': return _b(o,fr,to,tex,faces,rot,full,rescale)
    e=_b(o,fr,to,tex,faces,rot,False,rescale)
    dx,dy,dz=[abs(to[i]-fr[i]) for i in range(3)]
    for k,f in e['faces'].items():
        w_,h_={"north":(dx,dy),"south":(dx,dy),"east":(dz,dy),"west":(dz,dy),"up":(dx,dz),"down":(dx,dz)}[k]
        w_=min(16,w_); h_=min(16,h_); u=(16-w_)/2; v=(16-h_)/2
        f['uv']=[u,v,u+w_,v+h_]
    return e
R_='t:block/riveted_airain'; OX='t:block/oxidized_airain_block'; BR='t:block/fire_bricks'
V='t:block/airain_glass'; FR='t:block/lamp_red_glass'; FC='t:block/lamp_warm'; SO='t:block/maq_sombre'; CA='t:block/gauge_face'
PN='t:block/airain_panel'; FZ='t:block/airain_frieze'; FL='t:block/airain_fluted'; TU='t:block/airain_pipe'; BD='t:block/airain_band'; GR='t:block/airain_grooves'; PV='t:block/airain_pipe_vertical'; RO='t:block/airain_rod'; CU='t:block/airain_chute'; CS='t:block/airain_chute_side'
def cube(o,t=BR): return [b(o,[0,0,0],[16,16,16],t,full=True)]
def sol(xs,zs): return [b((x,-1,z),[0,15,0],[16,16,16],BR,faces=("up",),full=True) for x in xs for z in zs]
def lum(e): 
    for f in e['faces'].values(): f['neoforge_data']={"block_light":15,"sky_light":15}
    return e
# ---------------------------------------------------------------- tuyauterie
def tuyau_x(o): return [b(o,[0,5,9],[16,11,15],TU,faces=("north","south","up","down"),full='crop'),b(o,[0,4,8],[1,12,16],BD,full='crop'),b(o,[15,4,8],[16,12,16],BD,full='crop')]
def coude_haut(o):
    return [b(o,[0,5,9],[11,11,15],TU,faces=("north","south","up","down","east"),full='crop'),b(o,[5,11,9],[11,16,15],PV,faces=("north","south","east","west"),full="crop"),
            b(o,[0,4,8],[1,12,16],BD,full='crop'),b(o,[4,15,8],[12,16,16],BD,full='crop')]
def tuyau_y(o): return [b(o,[5,0,9],[11,16,15],PV,faces=("north","south","east","west"),full='crop'),b(o,[4,0,8],[12,1,16],BD,full='crop'),b(o,[4,15,8],[12,16,16],BD,full='crop')]
def vanne(o):
    E=[b(o,[5.5,4.5,8.5],[10.5,11.5,9],BD,full='crop'),b(o,[7,7,5.5],[9,9,9])]
    for (a,c) in (([3,3,4.5],[13,4,5.5]),([3,12,4.5],[13,13,5.5]),([3,4,4.5],[4,12,5.5]),([12,4,4.5],[13,12,5.5]),([7.5,4,4.7],[8.5,12,5.3]),([4,7.5,4.7],[12,8.5,5.3])):
        E.append(b(o,a,c,OX))
    return E
def manometre(o):
    E=[b(o,[7.5,11,11.5],[8.5,13,12.5]),b(o,[5,13,10],[11,19,13]),b(o,[5,13,10],[11,19,13],rot=([8,16,11.5],'z',45))]
    E+=[b(o,[5.6,13.6,9.9],[10.4,18.4,10],CA,faces=("north",),full=True),b(o,[7.75,15.5,9.7],[8.25,18,9.8],SO,faces=("north",),rot=([8,16,9.75],'z',-22.5))]
    return E
def p_tuyaux():
    E=[]
    for x in range(3):
        for y in range(2): E+=cube((x,y,1))
    E+=tuyau_x((0,0,0))+manometre((0,0,0))+tuyau_x((1,0,0))+vanne((1,0,0))+coude_haut((2,0,0))+tuyau_y((2,1,0))
    return E+sol(range(0,3),range(0,2))
# ---------------------------------------------------------------- lampes
def suspension(o):
    E=[b(o,[7.5,12,7.5],[8.5,16,8.5]),b(o,[6,11,6],[10,12,10],BD,full='crop'),b(o,[5,10,5],[11,11,11]),b(o,[4,8,4],[12,10,12]),b(o,[3,6,3],[13,8,13],BD,full='crop'),b(o,[2,5,2],[14,6,14])]
    E.append(lum(b(o,[5.5,3.5,5.5],[10.5,6,10.5],FC)))
    return E
def applique(o):
    E=[b(o,[4,3,15],[12,13,16],PN,full='crop'),b(o,[5,4,10],[11,5,15]),b(o,[5,11,10],[11,12,15]),lum(b(o,[6.5,5,11.5],[9.5,11,14.5],FR))]
    for x in (5,7.25,8.75,10.5): E.append(b(o,[x,5,10],[x+0.5,11,10.5]))
    E.append(b(o,[5,7.75,10],[11,8.25,10.5]))
    return E
def gyrophare(o):
    E=[b(o,[4,0,4],[12,2,12],BD,full='crop'),lum(b(o,[5,2,5],[11,8,11],FR)),b(o,[5,8,5],[11,9,11])]
    for (a,c) in (([5,2,5],[5.5,8,5.5]),([10.5,2,5],[11,8,5.5]),([5,2,10.5],[5.5,8,11]),([10.5,2,10.5],[11,8,11])): E.append(b(o,a,c))
    return E
def p_lampes():
    E=cube((0,2,0))+cube((1,2,0))+suspension((0,1,0))
    E+=cube((2,1,1))+cube((2,0,1))+applique((2,1,0))
    E+=cube((4,0,0),M)+gyrophare((4,1,0))
    return E+sol(range(0,5),range(0,2))
# ---------------------------------------------------------------- garde-corps vitré
def vitre_nord(o,h=SOL,fin=False):
    E=[b(o,[0,h,0],[2,h+13,2]),b(o,[0,h+11,0],[16,h+13,2]),b(o,[0,h,0.5],[16,h+1.5,1.5]),b(o,[2,h+1.5,0.75],[16,h+11,1.25],V,full='crop')]
    if fin: E.append(b(o,[14,h,0],[16,h+13,2]))
    return E
def p_vitre():
    E=[]
    for x in range(2): E+=plancher((x,0,0))+vitre_nord((x,0,0),fin=x==1)+rambarde((x,0,0),'s',poteau_fin=x==1)
    return E+sol(range(0,2),range(0,1))
# ---------------------------------------------------------------- plancher technique
def plancher_tech(o,ouvert=False):
    E=[]
    for (x,z) in ((1,1),(13,1),(1,13),(13,13)): E+=[b(o,[x,0,z],[x+2,13,z+2],RO,full='crop'),b(o,[x-0.5,0,z-0.5],[x+2.5,1,z+2.5])]
    if not ouvert:
        E+=[b(o,[0,13,0],[16,16,16],PN,faces=("up","down"),full=True),b(o,[0,13,0],[16,16,16],BD,faces=("north","south","east","west"),full='crop'),b(o,[2,16,7],[3,16.5,9],SO)]
    else:
        # dalle entière relevée sur sa charnière nord : panneau 16 × 16 pixel pour pixel, chants en bandeau
        E+=[b(o,[0,13,-3],[16,29,0],PN,faces=("north","south"),full=True),b(o,[0,13,-3],[16,29,0],BD,faces=("east","west","up","down"),full='crop')]
    return E
def p_tech():
    E=plancher_tech((0,0,0))+plancher_tech((1,0,0),ouvert=True)+plancher_tech((2,0,0))
    for x in range(3): E+=[b((x,0,0),[0,4,5],[16,10,11],OX,faces=("north","south","up","down"))]
    return E+sol(range(0,3),range(0,1))
# ---------------------------------------------------------------- établi
def etabli(o):
    E=[b(o,[0,13,0],[16,16,16],PN,faces=("up","down"),full=True),b(o,[0,13,0],[16,16,16],BD,faces=("north","south","east","west"),full='crop')]
    for (x,z) in ((0.5,0.5),(13.5,0.5),(0.5,13.5),(13.5,13.5)): E.append(b(o,[x,0,z],[x+2,13,z+2]))
    E+=[b(o,[1,3,1],[15,4,15],OX),b(o,[2,9,0],[14,12.5,1],BD,full='crop'),b(o,[7,10,-0.5],[9,11,0]),
        b(o,[1,16,1],[6,19,4],BD,full='crop'),b(o,[1.5,16,-1],[5.5,19,0.5],BD,full='crop'),b(o,[3,17,-3],[4,18,-1]),b(o,[0,17.5,-2.5],[7,18,-2]),
        b(o,[9,16,6],[13,17.5,7.5],SO),b(o,[10.5,16,7.5],[11.5,17,13])]
    return E
def p_etabli(): return etabli((0,0,0))+sol(range(0,1),range(0,1))
# ---------------------------------------------------------------- réverbères
def lanterne(o,x,y,z):
    return [b(o,[x-2,y+6,z-2],[x+2,y+7,z+2]),b(o,[x-1,y+7,z-1],[x+1,y+8,z+1]),lum(b(o,[x-1.5,y+1,z-1.5],[x+1.5,y+6,z+1.5],FR)),b(o,[x-2,y,z-2],[x+2,y+1,z+2])]
def reverbere(o,double=False):
    x,y,z=o; E=[b(o,[3,0,3],[13,2,13],BD,full='crop'),b(o,[4.5,2,4.5],[11.5,5,11.5],BD,full='crop'),b(o,[6.5,5,6.5],[9.5,16,9.5],FL,full='crop')]
    E+=[b((x,y+1,z),[6.5,0,6.5],[9.5,16,9.5],FL,full='crop'),b((x,y+1,z),[6,8,6],[10,9,10])]
    t=(x,y+2,z)
    E+=[b(t,[7,0,7],[9,10,9])]
    if double:
        E+=[b(t,[-1,9,7],[17,10.5,9]),b(t,[6,10.5,7.5],[10,12,8.5])]
        E+=[b(t,[-0.5,6,7.5],[0.5,9,8.5]),b(t,[15.5,6,7.5],[16.5,9,8.5])]
        E+=lanterne(t,0,-1,8)+lanterne(t,16,-1,8)
    else:
        E+=lanterne(t,8,10,8)
    return E
def p_reverberes(): return reverbere((0,0,0))+reverbere((2,0,0),double=True)+sol(range(-1,4),range(0,1))
# ---------------------------------------------------------------- planche
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",26)
def vue(E,eye,taille=900):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    im=rendre(E,{},taille); return im.crop(im.getbbox())
V1=[("Tuyauterie : vanne, coude, manomètre",p_tuyaux,[-0.6,0.5,-1]),("Lampes : suspension, applique, gyrophare",p_lampes,[-0.6,0.3,-1]),
    ("Garde-corps vitré",p_vitre,[-0.6,0.6,1]),("Plancher technique (trappe ouverte au milieu)",p_tech,[-0.6,0.7,1]),
    ("Établi d'atelier",p_etabli,[-0.7,0.7,-1]),("Réverbères : simple, double",p_reverberes,[-0.6,0.35,1])]
ims=[(t,vue(fn(),eye)) for t,fn,eye in V1]
cw=max(i.width for _,i in ims); ch=max(i.height for _,i in ims)
for k in range(len(ims)):
    t,i=ims[k]; s=min(1,700/i.width,520/i.height); ims[k]=(t,i.resize((int(i.width*s),int(i.height*s))))
W=Image.new('RGBA',(2*760,3*600),(34,30,38,255)); d=ImageDraw.Draw(W)
for k,(t,i) in enumerate(ims):
    x0=(k%2)*760; y0=(k//2)*600
    d.text((x0+20,y0+15),t,font=f,fill=(235,215,170)); W.alpha_composite(i,(x0+30+(700-i.width)//2,y0+60+(520-i.height)//2))
W.save('rendu_fusion/planche_deco.png')
