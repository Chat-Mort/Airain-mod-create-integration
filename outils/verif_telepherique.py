src=open('verif_atelier2.py').read(); exec(src[:src.index('# 1. tuyauterie')])
import math
rm.RAC['t']='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/'; rm._cache.clear()
def chargel(m,pos,r=0,dy=0):
    es=charge(m,(0,0,0),r)
    for e in es:
        (x1,y1,z1),(x2,y2,z2)=e['from'],e['to']
        D={'north':[16-x2,16-y2,16-x1,16-y1],'south':[x1,16-y2,x2,16-y1],'west':[z1,16-y2,z2,16-y1],'east':[16-z2,16-y2,16-z1,16-y1],'up':[x1,z1,x2,z2],'down':[x1,16-z2,x2,16-z1]}
        for k,f in e['faces'].items():
            f.setdefault('uv',D[k])
            u=f['uv']; f['uv']=[max(0,min(16,v)) for v in u]
        for i in range(3): e['from'][i]+=pos[i]*16; e['to'][i]+=pos[i]*16
        e['from'][1]+=dy; e['to'][1]+=dy
        if e.get('rotation'): e['rotation']['origin']=[e['rotation']['origin'][i]+pos[i]*16+(dy if i==1 else 0) for i in range(3)]
    return es
def bx(f,t,tex='t:block/airain_cable_strand'):
    return {'from':list(f),'to':list(t),'faces':{k:{'texture':tex,'uv':[7,0,9,16]} for k in ('north','south','east','west','up','down')}}
E=[]
# ligne le long de x : gare (0,0,0), pylône en x=10 (4 de haut + tête), gare (20,0,0) ; brin à z ± 1.5
E+=chargel('airain_cable_station',(0,0,0),90)+chargel('airain_cable_station_upper',(0,1,0),90)+chargel('airain_cable_station/wheel',(0,1,0),0)
E+=chargel('airain_cable_station',(20,0,0),270)+chargel('airain_cable_station_upper',(20,1,0),270)+chargel('airain_cable_station/wheel',(20,1,0),0)
for y in range(3): E+=chargel('airain_pylon',(10,y,0))
E+=chargel('airain_pylon_head',(10,3,0),90)
pts=[(0.5,1.9),(10.5,3.75),(20.5,1.9)]
for cote in (1.5,-1.5):
    for (xa,ya),(xb,yb) in zip(pts,pts[1:]):
        n=14
        for k in range(n):
            t0,t1=k/n,(k+1)/n
            f=lambda t:(xa+(xb-xa)*t, ya+(yb-ya)*t-0.035*abs(xb-xa)*4*t*(1-t))
            (x0,y0),(x1,y1)=f(t0),f(t1)
            y=(y0+y1)/2
            E.append(bx((x0*16,y*16-0.7,(0.5+cote)*16-0.7),(x1*16,y*16+0.7,(0.5+cote)*16+0.7)))
# nacelle à mi-chemin de la première travée, sur le brin droit (z + 1.5 vers le sud = droite en allant vers l'est ? on prend +1.5)
t=0.55; xc=0.5+10*t; yc=1.9+(3.75-1.9)*t-0.035*10*4*t*(1-t); zc=0.5+1.5
fy=yc-1.85
E+=chargel('airain_gondola/platform',(xc-0.5,0,zc-0.5),0,fy*16)
E+=chargel('airain_gondola/arm',(xc-0.5,0,zc-0.5),90,fy*16)
E+=chargel('airain_gondola/carriage',(xc-0.5,0,zc-0.5),90,yc*16)
for x in range(-1,22):
    for z in range(-2,4): E+=cube((x,-1,z),'t:block/fire_bricks')
A=vue(E,[-0.45,0.5,1],1400); A.save('rendu_fusion/telepherique_vrai.png')
B=vue(chargel('airain_cable_station',(0,0,0))+chargel('airain_cable_station_upper',(0,1,0))+chargel('airain_cable_station/wheel',(0,1,0))+
      chargel('airain_rolling_mill',(3,0,0))+chargel('airain_rolling_mill/roller_low',(3,0,0))+chargel('airain_rolling_mill/roller_high',(3,0,0))+
      chargel('airain_pylon_head',(6,0,0))+chargel('airain_gondola/platform',(9,0,0))+chargel('airain_gondola/arm',(9,0,0))+chargel('airain_gondola/carriage',(9,0,0),0,30),[-0.6,0.7,1],1000)
B.save('rendu_fusion/telepherique_pieces.png')
