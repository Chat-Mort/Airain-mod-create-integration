from PIL import Image
import colorsys, random, zlib
src=Image.open('../mcmeta-assets/assets/minecraft/textures/entity/iron_golem/iron_golem.png').convert('RGBA')
W,H=src.size
LAITON=[(28,16,8),(66,38,14),(112,68,22),(160,104,34),(198,146,56),(232,192,100)]
def grad(t):
    t=max(0,min(1,t))*(len(LAITON)-1); i=int(t); f=t-i
    if i>=len(LAITON)-1: return LAITON[-1]
    a,b=LAITON[i],LAITON[i+1]; return tuple(int(a[k]+(b[k]-a[k])*f) for k in range(3))
out=Image.new('RGBA',(W,H))
for y in range(H):
  for x in range(W):
    r,g,b,a=src.getpixel((x,y))
    if a==0: continue
    h,l,s=colorsys.rgb_to_hls(r/255,g/255,b/255)
    if g>r+20 and g>b+20:   # lierre -> vert-de-gris
        L=l*1.1; out.putpixel((x,y),(int(60*L+20),int(150*L+20),int(130*L+20),255)); continue
    if (r,g,b)==(255,213,0): out.putpixel((x,y),(255,190,60,255)); continue
    if r>120 and g<20: out.putpixel((x,y),(255,170,40,255)); continue     # yeux
    if r<40 and g<10: out.putpixel((x,y),(120,40,0,255)); continue
    out.putpixel((x,y),grad(max(0,(l-0.3)/0.65)**1.35)+(255,))
out.save('gardien.png')
# mousse / rouille : surcouche
rnd=random.Random(7)
m=Image.new('RGBA',(W,H))
TACHES=[(rnd.randrange(W),rnd.randrange(H),rnd.uniform(4,9)) for _ in range(45)]
for y in range(H):
  for x in range(W):
    if src.getpixel((x,y))[3]==0: continue
    d=min(((x-cx)**2+(y-cy)**2)**.5/rr for cx,cy,rr in TACHES)
    v=rnd.random()
    if d<1 and v<0.75-0.5*d: m.putpixel((x,y),rnd.choice([(74,98,40,255),(92,120,48,255),(60,82,34,255)]))
    elif v<0.05: m.putpixel((x,y),rnd.choice([(120,58,24,255),(98,44,20,255)]))
# yeux éteints en panne
for y in range(H):
  for x in range(W):
    r,g,b,a=src.getpixel((x,y))
    if a and ((r>120 and g<20) or (r<40 and g<10)): m.putpixel((x,y),(40,30,24,255))
m.save('gardien_mousse.png')
p=Image.new('RGBA',(W*2,H),(40,40,40,255)); p.paste(out,(0,0),out); 
o2=out.copy(); o2.alpha_composite(m); p.paste(o2,(W,0),o2)
p.resize((W*8,H*4),Image.NEAREST).save('apercu_tex.png')
