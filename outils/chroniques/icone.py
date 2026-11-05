from PIL import Image
P={'.':(0,0,0,0),'K':(22,18,16,255),
 's':(38,60,58,255),'S':(52,80,76,255),   # dos
 'c':(66,98,90,255),'C':(84,118,106,255),'d':(52,78,72,255),'u':(110,136,120,255),  # cuir délavé
 'p':(226,214,186,255),'P':(196,182,150,255),   # tranche des pages
 'o':(214,160,48,255),'O':(246,214,134,255),'b':(140,94,30,255),  # laiton
 'r':(150,30,30,255),'R':(190,52,44,255)}  # signet
A=[
"..KKKKKKKKKKKK..",
"..KsSOcCccucOpK.",
"..KsScbbbbbbcPK.",
"..KsScbOOOOObpK.",
"..KsScbcpppcbPK.",
"..KsScbccpccbpK.",
"..KsScbccOccbPK.",
"..KsScbccpccbpK.",
"..KsScbcpppcbPK.",
"..KsScbOOOOObpK.",
"..KsScbbbbbbcPK.",
"..KsScdcCcdccpK.",
"..KsSCccccccdPK.",
"..KsSObcRccOcpK.",
"..KsSocdRcdcopK.",
"...KKKKKRKKKKK..",
]
im=Image.new('RGBA',(16,16))
for y,row in enumerate(A):
    for x,c in enumerate(row): im.putpixel((x,y),P[c])
im.save('chroniques.png')
T='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
o=Image.new('RGBA',(78,20),(60,60,66,255))
for i,f in enumerate(('chroniques.png',T+'registre_fondations.png',T+'codex.png',T+'livre_ingenieur.png')):
    x=Image.open(f).convert('RGBA'); o.paste(x,(2+i*19,2),x)
o.resize((1248,320),Image.NEAREST).save('/home/claude/apercus/chroniques_icone.png')
