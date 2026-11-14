# Version 3 : le mécanisme EST une pièce de passerelle (on marche dessus) ; il entraîne les passerelles ordinaires qui suivent.
src=open('maquette_meca.py').read()
exec(src[:src.index("gif('anim_monte_charge.gif'")])
def passerelle(o,cotes='ns'):
    E=plancher(o)
    for c in cotes: E+=rambarde(o,c)
    return E
def mecanisme(o,ang):
    """Passerelle-mécanisme : plancher et rambardes normaux, carter suspendu sous le plancher, roue dentée et arbre."""
    E=passerelle(o)
    E+=[b(o,[2,-9,2],[14,1,14],BD,faces=("north","south","east","west"),full='crop'),b(o,[2,-9,2],[14,1,14],PN,faces=("down",),full='crop')]
    E+=roue(o,8,-4,1.5,2,ang)
    E+=[b(o,[6.5,-16,6.5],[9.5,-9,9.5],'t:block/airain_pipe_vertical',full='crop')]     # arbre de Create qui monte dans le carter
    return E
def ligne(n):
    E=[]
    for x in (0,n+2): E+=poteau((x,0,0))
    return E
def scene_pont3(t,n=3):
    ang=80*(1-t); E=ligne(n)
    E+=passerelle((0,1,0),'nsw')+mecanisme((1,1,0),-ang*2)+passerelle((n+2,1,0),'nse')
    for k in range(n):
        seg=passerelle((2+k,1,0))
        for e in seg: e['rotation']={'origin':[32,16+1,8],'axis':'z','angle':ang}
        E+=seg
    return E+sol(range(0,n+3),range(0,1))
def scene_retract3(t,n=3):
    e=t*n; E=ligne(n)
    E+=passerelle((0,1,0),'nsw')+mecanisme((1,1,0),t*720)+passerelle((n+2,1,0),'nse')
    for k in range(n-1,-1,-1):
        fr_=max(0.0,min(1.0,e-k))
        if fr_<=0.02: continue
        E+=deplace(passerelle((1,1,0)),(fr_+k)*16,0,0)
    return E+sol(range(0,n+3),range(0,1))
gif('anim_pont_levis_v3.gif',scene_pont3,[-0.5,0.45,1],"Pont-levis de passerelle : la pièce-mécanisme fait partie de la passerelle")
gif('anim_passerelle_v3.gif',scene_retract3,[-0.5,0.45,1],"Passerelle rétractable : les segments sortent de la pièce-mécanisme")
