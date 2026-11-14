# Maquettes animées : monte-charge, pont-levis à bascule (1 à 4 segments), passerelle rétractable (1 à 4 segments).
import sys, math
_s=open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/maquette_nav.py').read()
exec(_s[:_s.index('f=ImageFont.truetype')])
def deplace(E,dx,dy,dz):
    for e in E:
        for k in ('from','to'):
            e[k]=[e[k][0]+dx,e[k][1]+dy,e[k][2]+dz]
        if 'rotation' in e: o=e['rotation']['origin']; e['rotation']['origin']=[o[0]+dx,o[1]+dy,o[2]+dz]
    return E
def roue(o,cx,cy,z0,z1,ang,r=5,t=OX):
    """Roue dentée vue de profil (plan xy) : jante et 8 dents, tournée de ang degrés."""
    E=[b(o,[cx-r,cy-1,z0],[cx+r,cy+1,z1],t,rot=([cx,cy,(z0+z1)/2],'z',ang)),b(o,[cx-1,cy-r,z0],[cx+1,cy+r,z1],t,rot=([cx,cy,(z0+z1)/2],'z',ang)),
       b(o,[cx-r+1,cy-1,z0],[cx+r-1,cy+1,z1],t,rot=([cx,cy,(z0+z1)/2],'z',ang+45)),b(o,[cx-1,cy-r+1,z0],[cx+1,cy+r-1,z1],t,rot=([cx,cy,(z0+z1)/2],'z',ang+45)),
       b(o,[cx-2.5,cy-2.5,z0-0.3],[cx+2.5,cy+2.5,z1+0.3],BD,full='crop',rot=([cx,cy,(z0+z1)/2],'z',ang))]
    return E
# ---------------------------------------------------------------- monte-charge
def treuil(o,ang):
    E=[b(o,[0,0,1],[16,12,15],PN,faces=("up","down"),full=True),b(o,[0,0,1],[16,12,15],BD,faces=("north","south","east","west"),full='crop')]
    E+=[b(o,[6,4,-2],[10,8,1],'t:block/airain_pipe',full='crop')]        # arbre de Create qui entre par l'avant
    E+=roue(o,8,6,15,16.5,ang)
    return E
def scene_monte(t):
    E=[]
    for y in range(4): E+=mat((0,y,0))
    E+=treuil((0,-1,1),t*360) if False else []
    E+=treuil((-1,0,0),t*720)
    h=t*3*16
    E+=deplace(cabine((1,0,0)),0,h,0)
    E+=plancher((2,0,0))+rambarde((2,0,0),'n')+rambarde((2,0,0),'s',poteau_fin=True)
    E+=plancher((2,3,0))+rambarde((2,3,0),'n')+rambarde((2,3,0),'s',poteau_fin=True)+poteau((2,2,0))+poteau((2,1,0))+poteau((2,0,0),haut=False)
    for y in (0,3): E+=[b((0,y,0),[16,6,0.5],[17,10,1.5],SO),lum(b((0,y,0),[16.5,8,0.3],[17,9,0.5],FR))]   # boîtiers d'appel
    return E+sol(range(-1,3),range(0,1))
# ---------------------------------------------------------------- pont-levis à bascule
def scene_pont(t, n=3):
    ang=80*(1-t)
    E=[]
    for z in range(2):
        E+=cube((0,0,z))+cube((n+1,0,z))
    for x in range(1,n+1):
        for z in range(2): E.append(b((x,-1,z),[0,0,0],[16,13,16],'t:block/maq_verre',faces=("up",),full=True))
    for z in range(2):
        # mécanisme : carter sur la rive, roue dentée qui tourne avec le tablier
        E+=[b((0,1,z),[0,0,1],[16,8,15],PN,faces=("up",),full=True),b((0,1,z),[0,0,1],[16,8,15],BD,faces=("north","south","east","west"),full='crop')]
        E+=roue((0,1,z),8,4,0.5 if z==0 else 14.5,1 if z==0 else 15.5,-ang*2)
        for k in range(n):        # tablier : un panneau par segment, tous pivotent autour de la charnière
            r=([16,16,z*16+8],'z',ang)
            E.append(b((1,0,z),[16*k-16+16,15,0],[16*k+16,17,16],PN,faces=("up","down"),full=True,rot=([0,16,8],'z',ang)) if False else
                     {'from':[16+16*k,15,z*16],'to':[32+16*k,17,z*16+16],'faces':{'up':{'texture':PN,'uv':[0,0,16,16]},'down':{'texture':PN,'uv':[0,0,16,16]}},'rotation':{'origin':[16,16,z*16+8],'axis':'z','angle':ang}})
            E.append({'from':[16+16*k,17,z*16+(0 if z==0 else 14)],'to':[32+16*k,20,z*16+(2 if z==0 else 16)],'faces':{f:{'texture':BD,'uv':[0,6.5,16,9.5]} for f in ('north','south','up')},'rotation':{'origin':[16,16,z*16+8],'axis':'z','angle':ang}})
    return E+sol(range(0,n+2),range(0,2))
# ---------------------------------------------------------------- passerelle rétractable
def segment(o):
    return plancher(o)+rambarde(o,'n')+rambarde(o,'s')
def scene_retract(t, n=3):
    e=t*n
    E=[]
    for x in (0,n+1): E+=cube((x,0,0))
    E+=segment((n+1,1,0))
    # carter sur la rive : coffre plein, ouvert du côté du vide
    E+=[b((0,1,0),[0,0,0],[16,16,16],PN,faces=("up",),full=True),b((0,1,0),[0,0,0],[16,16,16],BD,faces=("north","south","west"),full='crop'),
        b((0,1,0),[15,0,0],[16,16,2],BD,full='crop'),b((0,1,0),[15,0,14],[16,16,16],BD,full='crop'),b((0,1,0),[15,13,0],[16,16,16],BD,full='crop')]
    for k in range(n-1,-1,-1):
        fr_=max(0.0,min(1.0,e-k))           # le segment k sort quand le k-1 est sorti
        if fr_<=0.02: continue
        x=fr_+k
        E+=deplace(segment((0,1,0)),x*16,0,0)
    return E+sol(range(0,n+2),range(0,1))
# ---------------------------------------------------------------- animation
def vue(E,eye,taille=640):
    rm.EYE=norm(eye); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
    return rendre(E,{},taille)
def gif(nom,fn,eye,titre,n=14):
    ts=[i/(n-1) for i in range(n)]; seq=ts+[1]*4+ts[::-1]+[0]*4
    cache={}
    frames=[]
    for t in seq:
        if t not in cache: cache[t]=vue(fn(t),eye)
        frames.append(cache[t])
    bb=None
    for im in cache.values():
        g=im.getbbox(); bb=g if bb is None else (min(bb[0],g[0]),min(bb[1],g[1]),max(bb[2],g[2]),max(bb[3],g[3]))
    fo=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
    out=[]
    for im in frames:
        c=im.crop(bb); W=Image.new('RGBA',(max(c.width+40,fo.getbbox(titre)[2]+40),c.height+70),(34,30,38,255)); W.alpha_composite(c,((max(c.width+40,fo.getbbox(titre)[2]+40)-c.width)//2,55))
        ImageDraw.Draw(W).text((20,15),titre,font=fo,fill=(235,215,170)); out.append(W.convert('P',palette=Image.ADAPTIVE,colors=255))
    out[0].save('rendu_fusion/'+nom,save_all=True,append_images=out[1:],duration=90,loop=0,disposal=2)
gif('anim_monte_charge.gif',scene_monte,[-0.6,0.4,1],"Monte-charge : treuil (rotation de Create), mât à crémaillère, cabine")
gif('anim_pont_levis.gif',scene_pont,[-0.5,0.55,1],"Pont-levis à bascule : mécanisme + 3 segments")
gif('anim_passerelle.gif',scene_retract,[-0.5,0.6,1],"Passerelle rétractable : carter + 3 segments")

# ---------------------------------------------------------------- version 2 : le mécanisme est SOUS le chemin (encastré dans la rive)
def chemin(x,z): return [b((x,0,z),[0,13,0],[16,16,16],PN,faces=("up",),full=True)]
def scene_pont2(t, n=3):
    ang=80*(1-t); E=[]
    for z in range(2):
        E+=cube((-1,0,z))+cube((n+1,0,z))+cube((-1,-1,z))+cube((n+1,-1,z))+cube((0,-1,z))
        # mécanisme encastré : bloc plein à hauteur du sol, dessus praticable, roue dentée visible sur le flanc
        E+=[b((0,0,z),[0,0,0],[16,16,16],PN,faces=("up",),full=True),b((0,0,z),[0,0,0],[16,16,16],BD,faces=("north","south","east","west"),full='crop')]
        if z==0: E+=roue((0,0,z),8,8,-0.5,0,-ang*2)
        for k in range(n):
            E.append({'from':[16+16*k,13,z*16],'to':[32+16*k,16,z*16+16],'faces':{'up':{'texture':PN,'uv':[0,0,16,16]},'down':{'texture':PN,'uv':[0,0,16,16]},'north':{'texture':BD,'uv':[0,6.5,16,9.5]},'south':{'texture':BD,'uv':[0,6.5,16,9.5]}},'rotation':{'origin':[16,16,z*16+8],'axis':'z','angle':ang}})
    for x in range(1,n+1):
        for z in range(2): E.append(b((x,-1,z),[0,0,0],[16,13,16],'t:block/maq_verre',faces=("up",),full=True))
    return E+[b((x,-2,z),[0,15,0],[16,16,16],BR,faces=("up",),full=True) for x in range(-1,n+2) for z in range(2)]
def scene_retract2(t, n=3):
    e=t*n; E=[]
    for x in (-1,n+1): E+=cube((x,-1,0))+cube((x,0,0))
    E+=cube((0,-1,0))
    E+=[b((0,0,0),[0,0,0],[16,16,16],PN,faces=("up",),full=True),b((0,0,0),[0,0,0],[16,16,16],BD,faces=("north","south","west","east"),full='crop'),
        b((0,0,0),[15.9,11,1],[16.1,16,15],SO,faces=("east",))]                 # fente par où sortent les segments
    for k in range(n-1,-1,-1):
        fr_=max(0.0,min(1.0,e-k))
        if fr_<=0.02: continue
        E+=deplace(plancher((0,0,0),h=16)+rambarde((0,0,0),'n',h=16)+rambarde((0,0,0),'s',h=16),(fr_+k)*16,0,0)
    return E+[b((x,-2,0),[0,15,0],[16,16,16],BR,faces=("up",),full=True) for x in range(-1,n+2)]
gif('anim_pont_levis_v2.gif',scene_pont2,[-0.5,0.55,1],"Pont-levis : mécanisme encastré dans la rive, sous le chemin")
gif('anim_passerelle_v2.gif',scene_retract2,[-0.5,0.6,1],"Passerelle rétractable : carter encastré, les segments sortent au ras du sol")
