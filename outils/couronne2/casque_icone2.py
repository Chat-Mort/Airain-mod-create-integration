from PIL import Image
P={'.':(0,0,0,0),'K':(23,17,17,255),'h':(118,106,118,255),'H':(93,86,93,255),'l':(77,73,77,255),'m':(71,62,63,255),'d':(53,45,45,255),'D':(36,31,32,255),
   'i':(23,17,17,255),'r':(150,20,28,255),'R':(230,78,70,255)}
A=[
"................",
"................",
"..KK...KK...KK..",
".KHlK.KhlK.KmDK.",
".KllK.KllK.KmDK.",
".KllKKKllKKKmDK.",
".KHlllllllllmDK.",
".KllllllllllmDK.",
".KlddddRrdddDDK.",
".KlmmmmrrmmmmDK.",
".KlmKKKmmKKKmDK.",
".KlmKiKmmKiKmDK.",
".KllKiKmDKiKmDK.",
".KlmKiiKKiiKmDK.",
"..KKK.....KKKK..",
"................",
]
im=Image.new('RGBA',(16,16))
for y,row in enumerate(A):
    for x,c in enumerate(row): im.putpixel((x,y),P[c])
im.save('casque_couronne_icone.png')
seule=Image.open('couronne_simple.png')
b=Image.open('/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/registre_fondations.png').convert('RGBA')
n=Image.open('../mcmeta-assets/assets/minecraft/textures/item/netherite_helmet.png').convert('RGBA')
o=Image.new('RGBA',(77,20),(60,60,66,255))
for i,x in enumerate((seule,im,n,b)): o.paste(x,(2+i*19,2),x)
o.resize((1232,320),Image.NEAREST).save('/home/claude/apercus/icones_v2.png')
