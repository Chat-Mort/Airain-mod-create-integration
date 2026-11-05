from PIL import Image
D,M,C,L,H=(52,30,10,255),(120,74,24,255),(176,120,40,255),(222,170,74,255),(250,222,140,255)
R,RD=(200,40,40,255),(110,16,24,255)
V=(58,150,130,255)
ic=Image.new('RGBA',(16,16))
rows=[
"......DDDD......",
".....DHLLHD.....",
".DD..DLRLLD..DD.",
"DLLD.DLLRLD.DLLD",
"DLCCDDDLLDDDCCLD",
"DCCCCCCDDCCCCCCD",
"DHMMHMMMMMMHMMHD",
"DLLLLLLLLLLLLLLD",
"DCHCCVCCCCVCCHCD",
"DMMMMMMMMMMMMMMD",
".DDDDDDDDDDDDDD.",
]
P={'H':H,'L':L,'C':C,'M':M,'D':D,'R':R,'V':V}
for y,r in enumerate(rows):
  for x,ch in enumerate(r):
    if ch in P: ic.putpixel((x,y+3),P[ch])
ic.save('couronne_airain.png')
# couche d'armure : bande sur les 4 faces latérales de la tête (rangées 8..15 de l'UV), hauteur 4 + pointes
a=Image.new('RGBA',(64,32))
for fx in (0,8,16,24):
  for x in range(8):
    gx=fx+x
    if x in (1,2,5,6): a.putpixel((gx,8),L); a.putpixel((gx,9),C)
    a.putpixel((gx,10),H if x in (0,7) else L)
    a.putpixel((gx,11),(R if fx==8 and x in (3,4) else (V if x in (3,4) else C)))
    a.putpixel((gx,12),M)
a.save('couronne_layer_1.png')
ic.resize((256,256),Image.NEAREST).save('apercu_couronne.png')
