import nbtlib, sys
from collections import Counter
TERRAIN=("grass_block","dirt","stone","deepslate","sand","water","short_grass","tall_grass","_log","leaves","andesite","diorite","granite","poppy","dandelion","flower")
def lire(f):
    n=nbtlib.load(f); pal=n["palette"]; B={}; J={}; E={}
    for b in n["blocks"]:
        st=pal[int(b["state"])]; nm=str(st["Name"]).replace("minecraft:",""); p=tuple(int(v) for v in b["pos"]); B[p]=nm
        if nm=="jigsaw": J[p]=str(b["nbt"]["pool"]).split("/")[-1]
        elif "nbt" in b: E[p]=b["nbt"]
    return n,B,J,E
for sien,mien in zip(sys.argv[1::2],sys.argv[2::2]):
    n1,L,JL,EL=lire(sien); n0,M,JM,EM=lire(mien)
    s1=[int(v) for v in n1["size"]]; s0=[int(v) for v in n0["size"]]
    print("==",sien.split("/")[-1],"taille",s1,"vs",s0)
    N=s0[0]
    TR={"0":lambda x,z:(x,z),"CCW":lambda x,z:(z,N-1-x),"180":lambda x,z:(N-1-x,N-1-z),"CW":lambda x,z:(N-1-z,x)}
    res={k:sum(1 for (x,y,z),s in M.items() if s!="air" and L.get((f(x,z)[0],y,f(x,z)[1]))==s) for k,f in TR.items()}
    k=max(res,key=res.get); f=TR[k]; print("  rotation",k,"identiques",res[k],"/",sum(1 for s in M.values() if s!="air"))
    JMr={(f(x,z)[0],y,f(x,z)[1]):j for (x,y,z),j in JM.items()}
    print("  puzzle",len(JM),"->",len(JL),"manquants",[(p,j) for p,j in JMr.items() if JL.get(p)!=j],"en plus",[(p,j) for p,j in JL.items() if p not in JMr])
    R={(f(x,z)[0],y,f(x,z)[1]):s for (x,y,z),s in M.items()}
    d=Counter((R.get(p,"vide"),L.get(p,"vide")) for p in set(R)|set(L) if R.get(p,"vide")!=L.get(p,"vide") and not (L.get(p)=="air" and R.get(p,"vide") in("vide","air")))
    print("  changements",sum(d.values()),d.most_common(14))
    print("  terrain:",Counter(s for p,s in L.items() if any(x in s for x in TERRAIN) and R.get(p)!=s).most_common(5))
    for p,t in EL.items():
        i=str(t.get("id",""))
        if any(x in i for x in ("chest","lectern","vendor")): print("   ",i,p,{kk:str(t[kk])[:50] for kk in ("LootTable","Book","Items","Selling") if kk in t})
