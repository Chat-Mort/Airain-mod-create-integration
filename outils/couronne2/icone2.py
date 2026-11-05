from PIL import Image
K=(38,20,8,255); d=(96,58,18,255); m=(150,98,32,255); l=(198,146,56,255); h=(240,208,128,255); w=(255,242,196,255)
r=(150,20,28,255); R=(225,70,64,255); v=(40,120,104,255); V=(96,196,166,255)
O=(214,160,48,255); o=(150,104,30,255); f=(60,62,68,255); g=(120,190,210,255); G=(225,248,252,255)
im=Image.new('RGBA',(16,16)); px=lambda x,y,c: im.putpixel((x,y),c) if 0<=x<16 and 0<=y<16 else None
def rouage(cx,cy):
    pat=["..o.o..",
         ".oOOOo.",
         "oOdddOo",
         ".OdfdO.",
         "oOdddOo",
         ".oOOOo.",
         "..o.o.."]
    for j,row in enumerate(pat):
        for i,ch in enumerate(row):
            if ch!='.': px(cx-3+i,cy-3+j,{'O':O,'o':o,'f':f,'d':d}[ch])

# fleurons
def fleuron(x,top,larg=1):
    for y in range(top,9): px(x,y,l if y>top else h)
fleuron(3,4); fleuron(12,4)
for x in (4,11): fleuron(x,7)
for x in (5,10): fleuron(x,6)
for y in range(2,9):        # fleuron central (3 de large), rubis
    for x in (6,7,8,9):
        if y==2 and x in (6,9): continue
        px(x,y,l if x in (7,8) else m)
px(7,2,w); px(8,2,h)
px(7,4,R); px(8,4,r); px(7,5,r); px(8,5,r); px(7,3,h); px(8,3,l)
# bandeau
for x in range(3,13):
    px(x,8,h if x%3==1 else l); px(x,9,l); px(x,10,m if x not in (5,10) else V); px(x,11,m); px(x,12,d if x%2 else o)
for x in (3,12):
    for y in (9,10,11): px(x,y,w if y==9 else O)
px(5,10,V); px(10,10,v)
# loupe sous le bandeau, côté gauche (œil droit du porteur)
# loupe accrochée au bandeau par une chaînette, à gauche
px(2,11,o); px(1,12,o)
for (x,y) in ((0,13),(1,13),(2,13),(0,14),(2,14),(0,15),(1,15),(2,15)): px(x,y,O)
px(1,14,G); px(0,13,h)
# contour automatique
src=im.copy()
for y in range(16):
    for x in range(16):
        if src.getpixel((x,y))[3]==0 and any(0<=x+a<16 and 0<=y+b<16 and src.getpixel((x+a,y+b))[3] and src.getpixel((x+a,y+b))!=K for a,b in ((1,0),(-1,0),(0,1),(0,-1))):
            im.putpixel((x,y),K)
im.save('couronne_icone.png')
a=im; b=Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/registre_fondations.png').convert('RGBA')
o_=Image.new('RGBA',(40,20),(60,60,66,255)); o_.paste(a,(2,2),a); o_.paste(b,(22,2),b); o_.resize((640,320),Image.NEAREST).save('ic.png')
