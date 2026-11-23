import math
def norm(v):
    n=math.hypot(v[0],v[2]); return (1,0,0) if n<1e-6 else (v[0]/n,0,v[2]/n)
def droite(av,ic,ap):
    d=(0,0,0)
    if av: a=norm(sub(ic,av)); d=add(d,a)
    if ap: b=norm(sub(ap,ic)); d=add(d,b)
    d=norm(d); return (-d[2],0,d[0])
add=lambda a,b:tuple(x+y for x,y in zip(a,b)); sub=lambda a,b:tuple(x-y for x,y in zip(a,b)); sc=lambda a,k:tuple(x*k for x in a)
def cap(d): return math.degrees(math.atan2(-d[0],d[2]))
def wrap(a): return (a+180)%360-180
for C in ([(0.5,70,0.5),(20.5,72,0.5),(40.5,70,10.5)], [(0.5,70,0.5),(-30.5,70,0.5)]):
    n=len(C); r=1.5; dr=[droite(C[i-1] if i>0 else None,C[i],C[i+1] if i+1<n else None) for i in range(n)]
    ech=[]
    def portee(a,b,prem):
        m=max(4,int(math.dist(a,b)/1.5))
        for k in range(0 if prem else 1,m+1):
            t=k/m; p=add(sc(a,1-t),sc(b,t)); fl=0.035*math.hypot(b[0]-a[0],b[2]-a[2]); ech.append(sub(p,(0,fl*4*t*(1-t),0)))
    for i in range(n-1): portee(add(C[i],sc(dr[i],r)),add(C[i+1],sc(dr[i+1],r)),i==0)
    i1=len(ech)-1
    cB,rB=C[-1],dr[-1]; dB=norm(sub(cB,C[-2]))
    for j in range(1,13): t=math.pi*j/12; ech.append(add(add(cB,sc(rB,math.cos(t)*r)),sc(dB,math.sin(t)*r)))
    i2=len(ech)-1
    for i in range(n-1,0,-1): portee(sub(C[i],sc(dr[i],r)),sub(C[i-1],sc(dr[i-1],r)),False)
    i3=len(ech)-1
    cA,rA=C[0],dr[0]; dA=norm(sub(C[1],cA))
    for j in range(1,13): t=math.pi*j/12; ech.append(sub(sub(cA,sc(rA,math.cos(t)*r)),sc(dA,math.sin(t)*r)))
    print('fermeture', [round(x,3) for x in sub(ech[-1],ech[0])], 'jonction B', [round(x,3) for x in sub(ech[i2],ech[i2+1])][:1])
    # sauts max entre échantillons
    print('pas max', round(max(math.dist(ech[i],ech[i-1]) for i in range(1,len(ech))),2))
    capB=round(cap(dB)/90)*90; sensB=1 if wrap(cap(sc(rB,-1))-cap(dB))>=0 else -1
    capA=round(cap(sc(dA,-1))/90)*90; sensA=1 if wrap(cap(rA)-cap(sc(dA,-1)))>=0 else -1
    # caps de la plateforme : avant B (aller), fin du demi-tour B vs début du retour
    aller=round(cap(sub(ech[i1],ech[i1-1]))/90)*90; retour=round(cap(sub(ech[i2+1],ech[i2]))/90)*90
    print('B: aller',aller,'capB',capB,'fin',wrap(capB+sensB*180),'retour',retour, ' A: retour',round(cap(sub(ech[i3],ech[i3-1]))/90)*90,'capA',capA,'fin',wrap(capA+sensA*180),'aller',round(cap(sub(ech[1],ech[0]))/90)*90)
    # sens de rotation du chariot autour de B (doit être celui de la poulie : angle croissant = (z*vx - x*vz) > 0)
    p=sub(ech[i1+6],cB); v=sub(ech[i1+7],ech[i1+5]); print('rotation B', p[2]*v[0]-p[0]*v[2]>0, end=' ')
    p=sub(ech[i3+6],cA); v=sub(ech[i3+7],ech[i3+5]); print('rotation A', p[2]*v[0]-p[0]*v[2]>0)
