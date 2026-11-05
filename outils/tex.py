from PIL import Image
import sys
out=sys.argv[1]
def img(): return Image.new("RGBA",(16,16),(0,0,0,0))
def schema(name, border):
    im=img(); p=im.load()
    paper=(46,86,150,255); light=(70,120,190,255); line=(210,230,255,255); dark=(25,50,95,255)
    for y in range(2,14):
        for x in range(1,15):
            p[x,y]=paper
    for y in range(2,14):
        p[1,y]=border; p[14,y]=border
    for x in range(1,15):
        p[x,2]=border; p[x,13]=border
    # rolled edges
    for y in range(1,15): p[0,y]=tuple(max(0,c-40) for c in border[:3])+(255,); p[15,y]=p[0,y]
    # gear sketch
    pts=[(6,5),(7,5),(8,5),(9,5),(5,6),(10,6),(5,7),(10,7),(5,8),(10,8),(5,9),(10,9),(6,10),(7,10),(8,10),(9,10),(7,4),(8,4),(7,11),(8,11),(4,7),(4,8),(11,7),(11,8)]
    for q in pts: p[q]=line
    p[7,7]=line;p[8,8]=line;p[7,8]=light;p[8,7]=light
    for x in range(3,13,2): p[x,12]=light
    im.save(f"{out}/{name}.png")
def shard(name, base):
    im=img(); p=im.load()
    hi=tuple(min(255,int(c*1.45)+30) for c in base)+(255,)
    mid=tuple(base)+(255,)
    lo=tuple(int(c*0.55) for c in base)+(255,)
    shape=["      ##      ","     ####     ","    ######    ","   ########   ","   #########  ","  ##########  ","  ##########  ","   #########  ","   ########   ","    ######    ","    #####     ","     ###      ","      #       "]
    for j,row in enumerate(shape):
        for i,ch in enumerate(row):
            if ch=="#":
                x,y=i+1,j+2
                c = hi if i<6 and j<6 else (lo if i>8 or j>9 else mid)
                p[x,y]=c
    # outline
    pts=[(x,y) for x in range(16) for y in range(16) if p[x,y][3]>0]
    for x,y in pts:
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<16 and 0<=ny<16 and p[nx,ny][3]==0: p[nx,ny]=(30,22,18,255)
    p[5,5]=(255,255,255,255); p[6,4]=(255,255,255,200)
    im.save(f"{out}/{name}.png")
def coeur():
    im=img(); p=im.load()
    shape=["  ###   ###  ","  ##### #####  "]
    heart=["   ###  ###   ","  ##### #####  "," ############# "," ############# "," ############# ","  ###########  ","   #########   ","    #######    ","     #####     ","      ###      ","       #       "]
    brass=(214,163,72,255); hi=(250,214,130,255); lo=(140,95,35,255)
    for j,row in enumerate(heart):
        for i,ch in enumerate(row):
            if ch=="#":
                x,y=i,j+3
                if x<16: p[x,y]= hi if (j<3 and i<7) else (lo if j>7 or i>11 else brass)
    for x,y in [(x,y) for x in range(16) for y in range(16) if p[x,y][3]>0]:
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<16 and 0<=ny<16 and p[nx,ny][3]==0: p[nx,ny]=(45,28,12,255)
    gear=(90,30,20,255); core=(255,90,40,255)
    for q in [(6,6),(7,6),(8,6),(5,7),(9,7),(5,8),(9,8),(6,9),(7,9),(8,9),(7,5),(4,8),(10,7),(7,10)]: p[q]=gear
    p[6,7]=core;p[7,7]=core;p[8,7]=core;p[6,8]=core;p[7,8]=(255,200,120,255);p[8,8]=core
    im.save(f"{out}/coeur_d_airain.png")
schema("schema_cuivre",(196,108,64,255))
schema("schema_laiton",(222,176,74,255))
schema("schema_ciel",(150,210,240,255))
shard("fragment_rouages",(184,120,60))
shard("fragment_marees",(50,170,170))
shard("fragment_forge",(210,80,40))
shard("fragment_vide",(130,70,190))
coeur()
