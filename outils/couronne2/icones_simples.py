from PIL import Image
K=(34,18,6,255); d=(110,66,20,255); m=(168,112,36,255); l=(214,162,62,255); h=(246,214,134,255)
r=(150,20,28,255); R=(230,78,70,255)
def couronne(dy=0):
    c=Image.new('RGBA',(16,16)); p=lambda x,y,col: c.putpixel((x,y+dy),col)
    # trois pointes
    for (x0,top) in ((2,4),(7,2),(12,4)):
        for y in range(top,9):
            for x in range(x0,x0+2): p(x,y,l if x==x0 else m)
        p(x0,top,h)
    # dents basses entre les pointes
    for x in (4,5,9,10):
        for y in (7,8): p(x,y,l if x in (4,9) else m)
    # bandeau
    for x in range(2,14):
        p(x,9,h); p(x,10,l); p(x,11,m); p(x,12,d)
    p(7,10,R); p(8,10,r); p(7,11,r); p(8,11,r)     # rubis
    src=c.copy()
    for y in range(16):
        for x in range(16):
            if src.getpixel((x,y))[3]==0 and any(0<=x+a<16 and 0<=y+b<16 and src.getpixel((x+a,y+b))[3] for a,b in ((1,0),(-1,0),(0,1),(0,-1))):
                c.putpixel((x,y),K)
    return c
seule=couronne(1); seule.save('couronne_simple.png')
casque=Image.open('../mcmeta-assets/assets/minecraft/textures/item/netherite_helmet.png').convert('RGBA')
cc=Image.new('RGBA',(16,16)); cc.paste(casque,(0,4),casque)
def petite():
    c=Image.new('RGBA',(16,16)); p=lambda x,y,col: c.putpixel((x,y),col)
    for (x,top) in ((4,3),(7,1),(8,1),(11,3)):
        for y in range(top,6): p(x,y,l if y>top else h)
    p(8,1,l); p(8,2,m); p(8,3,m); p(8,4,m); p(8,5,m)
    for x in (5,10): p(x,5,m)
    for x in range(4,12): p(x,6,h); p(x,7,l if x not in (7,8) else (R if x==7 else r))
    src=c.copy()
    for y in range(16):
        for x in range(16):
            if src.getpixel((x,y))[3]==0 and any(0<=x+a<16 and 0<=y+b<16 and src.getpixel((x+a,y+b))[3] for a,b in ((1,0),(-1,0),(0,1),(0,-1))):
                c.putpixel((x,y),K)
    return c
cr=petite()
# n'en garder que la partie haute (jusqu'au bandeau) pour la poser sur le casque
cc.alpha_composite(cr)
cc.save('casque_couronne_simple.png')
b=Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/registre_fondations.png').convert('RGBA')
o=Image.new('RGBA',(58,20),(60,60,66,255)); o.paste(seule,(2,2),seule); o.paste(cc,(21,2),cc); o.paste(b,(40,2),b)
o.resize((928,320),Image.NEAREST).save('/home/claude/apercus/icones_simples.png')
