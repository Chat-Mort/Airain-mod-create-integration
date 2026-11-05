from PIL import Image, ImageDraw, ImageFont
C = {'K':(42,30,22),'B':(244,214,128),'b':(214,170,80),'d':(150,104,40),'I':(12,34,46),'i':(20,64,80),'j':(30,96,108),
     'G':(110,250,230),'g':(46,170,168),'W':(238,234,222),'w':(176,170,160),'L':(190,226,236),'R':(150,40,40),'r':(110,26,30),'.':None}
def img(rows):
    im = Image.new('RGBA',(16,16),(0,0,0,0)); px = im.load()
    for y,l in enumerate(rows):
        for x,c in enumerate(l):
            if C[c]: px[x,y] = C[c]+(255,)
    return im
# A : encrier de laiton et plume
A = ["............WW..",
     "...........WWwW.",
     "..........WWwWW.",
     ".........WWwWWw.",
     "........WWwWWw..",
     "........WwWWw...",
     ".......KwWw.....",
     ".....KKKwKK.....",
     "....KbBbibbK....",
     "...KKdddddddKK..",
     "..KiiijGjiiiiiK.",
     "..KijGGGGjiiiiK.",
     "..KiijGjiiiiiiK.",
     "..KbBbbbbbbbbdK.",
     "...KddddddddKK..",
     "....KKKKKKKK...."]
# B : cartouche d'encre en diagonale (embouts de laiton, verre)
B = ["................",
     "..........KKKK..",
     ".........KBBbdK.",
     "........KBbbbdK.",
     ".......KKdddKK..",
     "......KLGgjiK...",
     ".....KLGGjiiK...",
     "....KLgGjGiK....",
     "...KLjjiiiK.....",
     "..KKdddKKK......",
     ".KBbbbdK........",
     ".KBbbddK........",
     "..KdddK.........",
     "...KdK..........",
     "....K...........",
     "................"]
# C : ampoule d'encre dans une cage de laiton
Cc = [".......KK.......",
      "......KbbK......",
      ".....KKddKK.....",
      "....KBbbbbdK....",
      "....KK.KK.KK....",
      "....bKLiiKb.....",
      "....bLjGGiKb....",
      "....bLGGGjib....",
      "....bKjGgiib....",
      "....bKijiiKb....",
      "....bKiiiiKb....",
      "....KKKiiKKK....",
      "....KBbbbbdK....",
      "...KbBbbbbddK...",
      "...KddddddddK...",
      "....KKKKKKKK...."]
props = {"A_encrier": A, "B_cartouche": B, "C_ampoule": Cc}
for k,v in props.items():
    assert all(len(l)==16 for l in v) and len(v)==16, k
    img(v).save(k+".png")
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
noms = ["A · Encrier et plume","B · Cartouche d'encre","C · Ampoule en cage"]
W = 300*3; out = Image.new('RGBA',(W,330),(44,46,52,255)); d = ImageDraw.Draw(out)
for i,k in enumerate(props):
    big = img(props[k]).resize((224,224),Image.NEAREST); out.paste(big,(38+i*300,50),big)
    small = img(props[k]).resize((32,32),Image.NEAREST); out.paste(small,(250+i*300,280),small)
    d.text((30+i*300,12),noms[i],fill=(235,225,200),font=F)
out.save("propositions_encre.png")
