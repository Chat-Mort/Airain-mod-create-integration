import json, sys
sys.path.insert(0, "butin")
import rendu_modele as R
from rendu_modele import *
M = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/"
fs = lambda p: (16 - p[0], p[1], 16 - p[2])
R.TEX["airain:entity/table_livre"] = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/entity/table_livre.png"
V = R.SC + "mcmeta-assets/assets/minecraft/textures/"
R.TEX["minecraft:entity/enchanting_table_book"] = V + "entity/enchanting_table_book.png"
def u(x0,y0,x1,y1): return [x0/4, y0/2, x1/4, y1/2]   # texture 64x32 -> uv 16
def livre(t):
    # couvertures ouvertes en V + pages, approximation du BookModel
    c = {"from":[2,0,5],"to":[8,0.4,15],"rotation":{"angle":-22.5,"axis":"z","origin":[8,0,10]},
         "faces":{"up":{"uv":u(0,0,6,10),"texture":"#t"},"down":{"uv":u(16,0,22,10),"texture":"#t"}}}
    c2 = {"from":[8,0,5],"to":[14,0.4,15],"rotation":{"angle":22.5,"axis":"z","origin":[8,0,10]},
         "faces":{"up":{"uv":u(16,0,22,10),"texture":"#t"},"down":{"uv":u(0,0,6,10),"texture":"#t"}}}
    p1 = {"from":[3,0.4,6],"to":[8,1.4,14],"rotation":{"angle":-22.5,"axis":"z","origin":[8,0,10]},
         "faces":{"up":{"uv":u(1,10,6,18),"texture":"#t"},"north":{"uv":u(0,10,5,11),"texture":"#t"}}}
    p2 = {"from":[8,0.4,6],"to":[13,1.4,14],"rotation":{"angle":22.5,"axis":"z","origin":[8,0,10]},
         "faces":{"up":{"uv":u(12,10,17,18),"texture":"#t"},"north":{"uv":u(0,10,5,11),"texture":"#t"}}}
    return {"textures":{"t":t},"elements":[c,c2,p1,p2]}
im = Image.new("RGBA",(1500,760),(44,46,52,255)); d = ImageDraw.Draw(im)
for i,(mod,t) in enumerate(((M+"table_enchantement.json","airain:entity/table_livre"),(None,"minecraft:entity/enchanting_table_book"))):
    if mod: m = json.load(open(mod))
    else:
        m = {"textures":{"d":"minecraft:block/enchanting_table_top","c":"minecraft:block/enchanting_table_side","b":"minecraft:block/enchanting_table_bottom"},
             "elements":[{"from":[0,0,0],"to":[16,12,16],"faces":{"up":{"uv":[0,0,16,16],"texture":"#d"},"down":{"uv":[0,0,16,16],"texture":"#b"},
               **{f:{"uv":[0,4,16,16],"texture":"#c"} for f in ("north","south","east","west")}}}]}
    L = quads(m, fs)
    dessiner(d, L, 20, 400 + i*720, 520)
im.save("hauts/table_apercu.png")
from PIL import ImageFont
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
im = Image.open("hauts/table_apercu.png"); d = ImageDraw.Draw(im)
for i,(f,n) in enumerate((("/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/entity/table_livre.png","Livre flottant (Empire)"),(V+"entity/enchanting_table_book.png","Livre vanilla"))):
    b = Image.open(f).convert("RGBA").resize((384,192), Image.NEAREST); im.paste(b,(210+i*720,60),b)
    d.text((210+i*720,260), n, fill=(235,225,200), font=F)
d.text((280,720),"Table de l'Empire",fill=(235,225,200),font=F); d.text((1010,720),"Table vanilla",fill=(235,225,200),font=F)
im.save("hauts/table_apercu.png")
