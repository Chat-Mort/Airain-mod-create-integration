from PIL import Image, ImageDraw, ImageFont
f=Image.open('fond.png'); d=Image.open('devant.png'); liq=Image.open('liquide.png')
def barre(rem, k=0, fond=(58,92,44,255)):
    im=Image.new('RGBA',(340,70),fond)
    L,Y=8,6   # Y = ligne écran de la toile (texel 0)
    im.alpha_composite(f.crop((0,0,324,54)),(L,Y))
    n=int(96*rem)*3
    if n: im.alpha_composite(liq.crop((0,18*k,n,18*k+18)),(L+27,Y+27))
    im.alpha_composite(d.crop((0,3,324,63)),(L,Y+3))
    return im
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
out=Image.new('RGB',(1060,560),(24,22,30)); dr=ImageDraw.Draw(out)
dr.text((10,6),"Taille réelle en jeu (interface 3)",font=F,fill=(230,230,230))
for j,(rem,fd) in enumerate(((1,(58,92,44,255)),(.55,(40,40,48,255)),(.12,(120,150,190,255)))):
    out.paste(barre(rem,0,fd),(10+j*350,30))
dr.text((10,112),"Agrandi x3",font=F,fill=(230,230,230))
out.paste(barre(.7,5,(40,40,48,255)).resize((1020,210),Image.NEAREST),(10,136))
out.paste(barre(1,12,(58,92,44,255)).crop((0,0,120,70)).resize((360,210),Image.NEAREST),(10,350))
out.paste(barre(1,12,(58,92,44,255)).crop((220,0,340,70)).resize((360,210),Image.NEAREST),(380,350))
out.save('apercu_hd.png')
# animation
fr=[barre(.7,k,(40,40,48,255)).resize((680,140),Image.NEAREST) for k in range(33)]
fr[0].save('anim.gif',save_all=True,append_images=fr[1:],duration=150,loop=0)
