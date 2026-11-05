from PIL import Image
K=(30,16,6,255); d=(96,58,18,255); m=(150,98,32,255); l=(198,146,56,255); h=(240,208,128,255); w=(255,242,196,255)
r=(150,20,28,255); R=(225,70,64,255); v=(40,120,104,255); V=(96,196,166,255); O=(214,160,48,255); G=(225,248,252,255); g=(120,190,210,255)
casque=Image.open('../mcmeta-assets/assets/minecraft/textures/item/netherite_helmet.png').convert('RGBA')
im=Image.new('RGBA',(16,16)); im.paste(casque,(0,4),casque)
px=lambda x,y,c: im.putpixel((x,y),c) if 0<=x<16 and 0<=y<16 else None
cour=Image.new('RGBA',(16,16)); cp=lambda x,y,c: cour.putpixel((x,y),c)
# fleurons
for (x,top) in ((3,3),(12,3),(5,5),(10,5)):
    for y in range(top,7): cp(x,y,l if y>top else h)
for y in range(1,7):
    for x in (6,7,8,9):
        if y==1 and x in (6,9): continue
        if y<3 and x in (6,9): continue
        cp(x,y,l if x in (7,8) else m)
cp(7,1,w); cp(8,1,h); cp(7,3,R); cp(8,3,r); cp(7,4,r); cp(8,4,r)
for x in range(3,13):
    cp(x,6,h if x%3==1 else l); cp(x,7,m if x not in (5,10) else V); cp(x,8,d if x%2 else m)
cp(10,7,v)
# contour de la couronne
src=cour.copy()
for y in range(16):
    for x in range(16):
        if src.getpixel((x,y))[3]==0 and any(0<=x+a<16 and 0<=y+b<16 and src.getpixel((x+a,y+b))[3] for a,b in ((1,0),(-1,0),(0,1),(0,-1))):
            if not (y>=9): cour.putpixel((x,y),K)
im.alpha_composite(cour)
# loupe sur l'œil droit du porteur (à gauche vu de face)
for (x,y) in ((4,10),(5,10),(6,10),(4,11),(6,11),(4,12),(5,12),(6,12)): px(x,y,O)
px(5,11,G); px(4,10,h); px(7,11,d)
im.save('casque_icone.png')
b=Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/registre_fondations.png').convert('RGBA')
o_=Image.new('RGBA',(40,20),(60,60,66,255)); o_.paste(im,(2,2),im); o_.paste(b,(22,2),b); o_.resize((640,320),Image.NEAREST).save('/home/claude/apercus/casque_icone.png')
