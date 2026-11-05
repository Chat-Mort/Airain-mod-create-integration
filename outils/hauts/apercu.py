import json, sys
sys.path.insert(0, "butin")
import rendu_modele as R
from rendu_modele import *
from PIL import ImageFont
H="/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/hauts/"
M = "/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/models/block/"
inner = json.load(open("create-src/src/main/resources/assets/create/models/block/millstone/inner.json"))
fs = lambda p: (16 - p[0], p[1], 16 - p[2])
banc = json.load(open(M+"banc_entretien/block.json")); meule=json.load(open(M+"banc_entretien/meule.json"))
huile=json.load(open(M+"banc_entretien/huile.json")); des=json.load(open(M+"desenchanteur/block.json")); cri=json.load(open(M+"desenchanteur/cristal.json"))
try: F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
except: F = None
def vider():
    for k in list(R.TEX):
        if k.startswith("airain:block/banc_plan"): del R.TEX[k]
    if hasattr(R, "_cache"): R._cache.clear()
props = ["A_noyer","B_tole_laiton","C_pierre_gravee","D_cuivre_patine","E_ardoise_amethyste"]
noms = ["A · Noyer et équerres","B · Tôle striée laiton","C · Pierre gravée","D · Cuivre patiné","E · Ardoise et améthyste"]
W=420*len(props); im = Image.new("RGBA",(W,900),(44,46,52,255)); d=ImageDraw.Draw(im)
for i,p in enumerate(props):
    R.TEX["airain:block/banc_plan"] = H+f"plan_{p}.png"
    R._cache.pop("airain:block/banc_plan", None)
    L = quads(banc, fs)
    L += quads(inner, lambda q: fs(rot(q,{"angle":10,"axis":"y","origin":[8,8,8]})))
    L += quads(meule, lambda q: fs(rot(q,{"angle":15,"axis":"x","origin":[8,20.5,11]})))
    L += quads(huile, lambda q: fs((3.25+(q[0]-3.25)*0.6,q[1],q[2])))
    dessiner(d, L, 13, 210+i*420, 380)
    L = quads(des, fs)
    L += quads(inner, lambda q: fs(rot(q,{"angle":10,"axis":"y","origin":[8,8,8]})))
    L += quads(cri, lambda q: fs(rot(q,{"angle":20,"axis":"y","origin":[8,8,11]})))
    L += quads(huile, lambda q: fs((3.25+(q[0]-3.25)*0.6,q[1],q[2])))
    dessiner(d, L, 13, 210+i*420, 760)
    d.text((40+i*420, 20), noms[i], fill=(235,225,200), font=F)
    big = Image.open(H+f"plan_{p}.png").crop((2,2,14,14)).resize((96,96),Image.NEAREST)
    im.paste(big,(300+i*420,60))
im.save(H+"propositions_dessus.png")
