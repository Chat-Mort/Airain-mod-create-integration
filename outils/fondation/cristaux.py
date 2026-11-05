import math
def dedans(p, poly):
    x,y=p; ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: ins=not ins
    return ins
def raster(facettes, w=10, h=12, ss=6, seuil=0.45):
    g=[]
    for j in range(h):
        l=""
        for i in range(w):
            compte={}
            for a in range(ss):
                for b in range(ss):
                    p=(i+(a+0.5)/ss, j+(b+0.5)/ss)
                    for ton,poly in facettes:
                        if dedans(p,poly): compte[ton]=compte.get(ton,0)+1; break
            tot=sum(compte.values())
            l+= max(compte,key=compte.get) if tot/(ss*ss)>=seuil else "."
        g.append(l)
    return g
def rot(p,c,a):
    x,y=p[0]-c[0],p[1]-c[1]; return (c[0]+x*math.cos(a)-y*math.sin(a), c[1]+x*math.sin(a)+y*math.cos(a))
# ---- A : trois branches qui partent de la base
def branche(base, ang, long, larg, coupe):
    # rectangle vertical centré sur base, de hauteur long, puis rotation ; sommet biseauté
    x=base[0]; y=base[1]
    g=[(x-larg/2,y),(x,y),(x,y-long+coupe),(x-larg/2,y-long)]
    d=[(x,y),(x+larg/2,y),(x+larg/2,y-long+coupe*2),(x,y-long+coupe)]
    return [rot(p,base,ang) for p in g],[rot(p,base,ang) for p in d]
def A():
    f=[]
    # centre : prisme pointu
    f.append(("M",[(5,0),(5,2.4),(3.1,2.4)]));   f.append(("L",[(5,0),(6.9,2.4),(5,2.4)]))
    f.append(("L",[(3.1,2.4),(5,2.4),(5,12),(3.1,12)])); f.append(("D",[(5,2.4),(6.9,2.4),(6.9,12),(5,12)]))
    gl,dl=branche((2.3,12.2),-0.62,7.6,2.6,0.9); f.append(("L",gl)); f.append(("M",dl))
    gr,dr=branche((7.7,12.2),0.62,7.6,2.6,0.9)
    # miroir : à droite la face extérieure est sombre
    f.append(("M",gr)); f.append(("D",dr))
    return raster(f)
def B():
    T,Lp,Rp,Bp=(5,0),(0.2,5.0),(9.8,5.0),(5,12)
    P1,P2=(3.6,4.3),(6.6,5.6)
    f=[("M",[T,Lp,P1]),("L",[T,P1,P2]),("M",[T,P2,Rp]),
       ("D",[Lp,P1,Bp]),("M",[P1,P2,Bp]),("L",[P2,Rp,Bp])]
    return raster(f)
if __name__=="__main__":
    for n,g in (("A",A()),("B",B())): print(n); print("\n".join(g))
