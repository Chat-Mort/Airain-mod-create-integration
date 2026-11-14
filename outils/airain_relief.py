# Relief creusé : à partir d'un masque 16×16 par face (1 = creusé d'un pixel), construit le modèle du bloc.
# Les zones à fleur sont des plaques d'un pixel d'épaisseur, fusionnées en rectangles ; un noyau en retrait d'un pixel
# forme le fond des creux. Rien ne dépasse du bloc.
import math, json
def masque_cisele():
    def dans(x,y):
        dx,dy=x-7.5,y-7.5; d=(dx*dx+dy*dy)**.5; a=math.atan2(dy,dx)
        return (d<=4.7 or (math.cos(a*8)>0.15 and d<=6.3)) and d>=1.9
    return [[1 if (2<=x<=13 and 2<=y<=13 and not dans(x,y)) else 0 for x in range(16)] for y in range(16)]
def masque_taille(): return [[1 if (1<=x<=14 and 1<=y<=14 and (x in (7,8) or y in (7,8))) else 0 for x in range(16)] for y in range(16)]
def masque_rivete(): return [[1 if (1<=x<=14 and y in (7,8)) else 0 for x in range(16)] for y in range(16)]
def masque_cannelures(): return [[1 if (3<=y<=12 and x%4 in (2,3) and 1<=x<=14) else 0 for x in range(16)] for y in range(16)]
def masque_pilier_dessus():
    return [[1 if 5.6<((x-7.5)**2+(y-7.5)**2)**.5<=6.6 or ((x-7.5)**2+(y-7.5)**2)**.5<=1.6 else 0 for x in range(16)] for y in range(16)]
def plat(): return [[0]*16 for _ in range(16)]
def rectangles(m, val=0):
    """Fusion gloutonne des pixels m==val en rectangles (x0,y0,x1,y1) inclus."""
    vu=[[False]*16 for _ in range(16)]; out=[]
    for y in range(16):
        for x in range(16):
            if m[y][x]!=val or vu[y][x]: continue
            w=1
            while x+w<16 and m[y][x+w]==val and not vu[y][x+w]: w+=1
            h=1
            while y+h<16 and all(m[y+h][x+i]==val and not vu[y+h][x+i] for i in range(w)): h+=1
            for yy in range(y,y+h):
                for xx in range(x,x+w): vu[yy][xx]=True
            out.append((x,y,x+w-1,y+h-1))
    return out
# Pour chaque face : passage des coordonnées texture (u à droite, v vers le bas) aux coordonnées du bloc.
def plaque_face(face, x0,y0,x1,y1, tex, m):
    """Plaque d'un pixel d'épaisseur sur la face, pour le rectangle texture (x0..x1, y0..y1)."""
    u0,u1,v0,v1=x0,x1+1,y0,y1+1
    if face=='north': fr,to=[16-u1,16-v1,0],[16-u0,16-v0,1]
    if face=='south': fr,to=[u0,16-v1,15],[u1,16-v0,16]
    if face=='west':  fr,to=[0,16-v1,u0],[1,16-v0,u1]
    if face=='east':  fr,to=[15,16-v1,16-u1],[16,16-v0,16-u0]
    if face=='up':    fr,to=[u0,15,v0],[u1,16,v1]
    if face=='down':  fr,to=[u0,0,16-v1],[u1,1,16-v0]
    faces={face:{"texture":tex,"uv":[u0,v0,u1,v1],"cullface":face}}
    # parois des creux : seulement là où le pixel voisin (dans la même face) est creusé
    def creux(x,y): return 0<=x<16 and 0<=y<16 and m[y][x]==1
    cotes={}
    # côté gauche (u0), droit (u1), haut (v0), bas (v1) de la plaque, exprimés en directions du bloc
    dirs={'north':('east','west','up','down'),'south':('west','east','up','down'),'west':('north','south','up','down'),
          'east':('south','north','up','down'),'up':('west','east','north','south'),'down':('west','east','south','north')}[face]
    g,d,h,b=dirs
    if any(creux(x0-1,y) for y in range(y0,y1+1)): cotes[g]=[u0,v0,u0+1,v1+1] if False else [max(0,u0-1),v0,u0,v1+1]
    if any(creux(x1+1,y) for y in range(y0,y1+1)): cotes[d]=[u1,v0,min(16,u1+1),v1+1]
    if any(creux(x,y0-1) for x in range(x0,x1+1)): cotes[h]=[u0,max(0,v0-1),u1,v0]
    if any(creux(x,y1+1) for x in range(x0,x1+1)): cotes[b]=[u0,v1+1,u1,min(16,v1+2)]
    for k,uv in cotes.items(): faces[k]={"texture":tex,"uv":uv}
    return {"from":fr,"to":to,"faces":faces}
def modele(masques, textures):
    """masques / textures : dict face → masque, face → '#clé'. Retourne la liste d'éléments."""
    E=[]
    creuse=any(any(any(r) for r in m) for m in masques.values())
    if not creuse:
        return [{"from":[0,0,0],"to":[16,16,16],"faces":{f:{"texture":textures[f],"cullface":f} for f in masques}}]
    # noyau : le fond des creux, en retrait d'un pixel
    E.append({"from":[1,1,1],"to":[15,15,15],"faces":{f:{"texture":textures[f],"uv":[1,1,15,15]} for f in masques}})
    for f,m in masques.items():
        for (x0,y0,x1,y1) in rectangles(m,0): E.append(plaque_face(f,x0,y0,x1,y1,textures[f],m))
    return E
