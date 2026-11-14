# Portes dessinées au pixel (16×16 par moitié). Légende : . vide, D trait, d ombre, s fond de panneau, m métal, p clair, h reflet, H arête claire, W éclat.
from PIL import Image, ImageDraw, ImageFont
exec(open('airain_luxe.py').read().split("STADES=['','exposed_'")[0])
V={'.':None,'D':0.9,'d':2.0,'s':2.7,'m':3.2,'p':3.7,'h':4.5,'H':5.2,'W':6.2}
def carte(lignes):
    assert len(lignes)==16, len(lignes)
    for l in lignes: assert len(l)==16, (l,len(l))
    return [[V[ch] for ch in l] for l in lignes]
A_HAUT=[
"HHHHHHHHHHHHHHHD",
"HmmmmmmmmmmmmmmD",
"HmmmmmDDDDhmmmmD",
"HmmmDD.hh..HmmmD",
"HmmD...hh...HmmD",
"HmD..hhhhhh..HmD",
"HmD.hh.WW.hh.HmD",
"HmDhhhWdDWhhhHmD",
"HmD.hh.WW.hh.HmD",
"HmD..hhhhhh..HmD",
"HmD....hh....HmD",
"HmD....hh....HmD",
"HmDHHHHHHHHHHHmD",
"HmmmmmmmmmmmmmmD",
"HmmWmmmmmmmmWmmD",
"HmmmmmmmmmmmmmmD"]
A_BAS=[
"HmmmmmmmmmmmmmmD",
"HmDDDDDDDDDDDDmD",
"HmDssssssssssHmD",
"WWWWWWWWWWhsssHD",
"dddddddddWHhssHD",
"HmDsssssshdWssHD",
"HmDsssssssWdssHD",
"HmDssssssssssWhD",
"HmDssssssssssdWD",
"HmDssssssssssHmD",
"WWWWWWWWWWhsssHD",
"dddddddddWHhssHD",
"HmDsssssshdWssHD",
"HmDsssssssWdssHD",
"HmHHHHHHHHHHHHmD",
"DDDDDDDDDDDDDDDD"]
B_HAUT=[
"WHHWHHWHHWHHWHHD",
"HppppppppppppppD",
"WpmmmmDDDDmmmmpD",
"HpmmDDhHHhDDmmpD",
"HpmDhH....HdDmpD",
"WpDhH......HdDpD",
"HpDH........HDpD",
"HpDH........HDpD",
"WpDH........HDpD",
"HpDh........dDpD",
"HpmDh......ddDpD",
"WpmDDhh..ddDDmpD",
"HpmmmDDDDDDmmmpD",
"HppppppppppppppD",
"WddddddddddddddD",
"HHHHHHHHHHHHHHHD"]
B_BAS=[
"HmmmmmmmmmmmmmmD",
"HmmmmmmmmmmmmmmD",
"WHHWHHWHHWHHWHHD",
"DddDddDddDddDddD",
"HmmmmmmmmmmmmmmD",
"HmmmmmmmHHHHmmmD",
"HmmmmmmHdmmWHmmD",
"HmmmmmmHmWWmHmmD",
"WHHWHHWHmWWmHHHD",
"DddDddDdmmmmdddD",
"HmmmmmmmdddDmmmD",
"HmmmmmmmmmmmmmmD",
"HmmmmmmmmmmmmmmD",
"WHHWHHWHHWHHWHHD",
"DddDddDddDddDddD",
"DDDDDDDDDDDDDDDD"]
C_HAUT=[
"HHHHHHHHHHHHHHHD",
"HpppppppppppppdD",
"HpDDDDDDDDDDDHdD",
"HpD.h..h..h.hHdD",
"HpD..h.h.h.h.HdD",
"HpDh..hhh.h..HdD",
"HpD.h..h.h..hHdD",
"HpD..h.h.h.h.HdD",
"HpD...hhhhh..HdD",
"HpDhh.hWWWh.hHdD",
"HpD..hWHHHWh.HdD",
"HpD.hWHhhhHWhHdD",
"HpDHHHHHHHHHHHdD",
"HpppppppppppppdD",
"HdhhhhhhhhhhhhdD",
"HpddddddddddddpD"]
C_BAS=[
"HpppppppppppppdD",
"HHHHHHHHHHHHHHdD",
"HhmdDhmdDhmdDhdD",
"HhmdDhmdDhmdDhdD",
"HhmdDhmdDhmdDhdD",
"HhmdDhmdDhmdDhdD",
"HWWWWWWWWWWWWWdD",
"HdhdhdhdhdhdhdWD",
"HDDDDDDDDDDDDDdD",
"HhmdDhmdDhmdDhdD",
"HhmdDhmdDhmdDhdD",
"HhmdDhmdDhmdDhdD",
"HhmdDhmdDhmdDhdD",
"HhmdDhmdDhmdDhdD",
"HHHHHHHHHHHHHHdD",
"DDDDDDDDDDDDDDDD"]
STY={'A':(A_HAUT,A_BAS),'B':(B_HAUT,B_BAS),'C':(C_HAUT,C_BAS)}
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/portes'
f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
noms={'A':'A · Ferronnerie impériale','B':'B · Coffre-fort','C':'C · Art déco'}
W=Image.new('RGBA',(3*330,350),(34,30,38,255)); d=ImageDraw.Draw(W)
mur=Image.open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/block/stone_bricks.png').convert('RGBA')
for i,k in enumerate('ABC'):
    d.text((i*330+165,20),noms[k],font=f,fill=(235,215,170),anchor='mm')
    h,b=STY[k]
    for j,t in enumerate((0.0,0.92)):
        hi=rendre_carte(carte(h),t); bi=rendre_carte(carte(b),t)
        hi.save(f'{OUT}/{k}_{j}_top.png'); bi.save(f'{OUT}/{k}_{j}_bottom.png')
        fond=Image.new('RGBA',(16,32)); fond.paste(mur,(0,0)); fond.paste(mur,(0,16))
        porte=Image.new('RGBA',(16,32)); porte.alpha_composite(hi,(0,0)); porte.alpha_composite(bi,(0,16))
        fond.alpha_composite(porte); W.alpha_composite(fond.resize((140,280),Image.NEAREST),(i*330+20+j*150,50))
W.save('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/rendu_fusion/portes_styles.png')
print('ok')
