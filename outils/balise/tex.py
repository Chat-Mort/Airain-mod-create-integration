from PIL import Image
P = {'.':None,
 'k':(40,26,18),   # contour sombre
 'B':(224,170,72), 'b':(170,118,44), 'h':(255,222,140),   # laiton
 'C':(196,104,64), 'c':(140,68,40),                        # cuivre
 'R':(232,48,40), 'r':(150,24,24), 'w':(255,190,150),      # lampe rouge
 'g':(90,90,96)}
A = [
"......kkkk......",
".....kRwRRk.....",
"....kRwRRRrk....",
"....kRRRRRrk....",
".....kRRRrk.....",
"......kCCk......",
"......kCck......",
"......kCck......",
".....kbhBBk.....",
"....kbhBBBbk....",
"...kBBkbbkBBk...",
"...kbBBggBBbk...",
"..kbhBBBBBBBbk..",
"..kbBBBBBBBbbk..",
"..kkbbbbbbbbkk..",
"...kkkkkkkkkk...",
]
im = Image.new("RGBA",(16,16),(0,0,0,0))
for y,row in enumerate(A):
    assert len(row)==16,(y,len(row))
    for x,ch in enumerate(row):
        if P[ch]: im.putpixel((x,y),P[ch]+(255,))
im.save("/home/claude/empire-airain-pack/kubejs/assets/kubejs/textures/item/balise_defense.png")
im.resize((128,128),Image.NEAREST).save("apercu.png")
