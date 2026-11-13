# Style « ferronnerie impériale » : porte, trappe, barreaux, grille. Dessin au pixel + reflet poli diagonal.
import math
from PIL import Image, ImageDraw, ImageFont
exec(open('airain_luxe.py').read().split("STADES=['','exposed_'")[0])
V={'.':None,'D':0.9,'d':2.0,'s':2.7,'m':3.2,'p':3.7,'h':4.5,'H':5.2,'W':6.2}
def eclat(x,y):
    """Reflet poli continu en diagonale (comme les blocs d'airain), qui se prolonge d'une moitié de porte à l'autre."""
    d=(x+y)%24
    return 0.9*math.exp(-((d-8)/2.2)**2)+0.5*math.exp(-((d-17)/1.5)**2)
def carte(lignes, dy=0):
    assert len(lignes)==16, len(lignes)
    out=[]
    for y,l in enumerate(lignes):
        assert len(l)==16,(l,len(l))
        r=[]
        for x,ch in enumerate(l):
            v=V[ch]
            if v is not None and ch in 'smp': v+=eclat(x,y+dy)*1.6
            r.append(v)
        out.append(r)
    return out
PORTE_HAUT=[
"HHHHHHHHHHHHHHHD",
"HmmmmmmmmmmmmmmD",
"HmmmmDDDDDDmmmmD",
"HmmmD..dd..HmmmD",
"HmmD...hh...HmmD",
"HmD..hHWWHh..HmD",
"HmD.hH.hh.Hh.HmD",
"HmDdhWhDDhWhdHmD",
"HmD.hH.hh.Hh.HmD",
"HmD..hHWWHh..HmD",
"HmD...hhhh...HmD",
"HmD....hh....HmD",
"HmDHHHHHHHHHHHmD",
"HmmmmmmmmmmmmmmD",
"HmmWmmmmmmmmWmmD",
"HmmmmmmmmmmmmmmD"]
PORTE_BAS=[
"HmmmmmmmmmmmmmmD",
"HmDDDDDDDDDDDDmD",
"HmDsssssssssssHD",
"HWWWWWWWWhssssHD",
"HddddddddWhsssHD",
"HmDsssssdWHssWHD",
"HmDssssssdhhhdHD",
"HmDsssssssssssHD",
"HmDsssssssssWhHD",
"HmDsssssssssdWHD",
"HWWWWWWWWhssssHD",
"HddddddddWhsssHD",
"HmDsssssdWHsssHD",
"HmDssssssdhhhdHD",
"HmHHHHHHHHHHHHmD",
"DDDDDDDDDDDDDDDD"]
TRAPPE=[
"HHHHHHHHHHHHHHHD",
"HWmmmmmmmmmmmWmD",
"HmDDDDDDDDDDDHmD",
"HmD.hh.dd.hh.HmD",
"HmDh..hhhh..hHmD",
"HmDh.hHWWHh.hHmD",
"HmD.hH.hh.Hh.HmD",
"HmDdhWhDDhWhdHmD",
"HmD.hH.hh.Hh.HmD",
"HmDh.hHWWHh.hHmD",
"HmDh..hhhh..hHmD",
"HmD.hh.dd.hh.HmD",
"HmDHHHHHHHHHHHmD",
"HWmmmmmmmmmmmWmD",
"HmmmmmmmmmmmmmmD",
"DDDDDDDDDDDDDDDD"]
BARREAUX=[
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
"WHdW.WHdW.WHdW..",
"hHdh.hHdh.hHdh..",
".Hd.hHdHh.Hd.hHd"[:16],
".Hdh.hHdh.Hdh.hH"[:16],
".HdW.WHdW.HdW.WH"[:16],
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
".Hd...Hd...Hd...",
".Hd...Hd...Hd..."]
GRILLE=[
"HHHHHHHHHHHHHHHD",
"Hh.....Wh.....hD",
"H.h...h..h...h.D",
"H..h.h....h.h..D",
"H...W......W...D",
"H..h.h....h.h..D",
"H.h...h..h...h.D",
"HW.....Wh.....WD",
"Hh.....hW.....hD",
"H.h...h..h...h.D",
"H..h.h....h.h..D",
"H...W......W...D",
"H..h.h....h.h..D",
"H.h...h..h...h.D",
"Hh.....hW.....hD",
"HDDDDDDDDDDDDDDD"]
OUT='/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/portes'
def textures(t):
    return {'porte_haut':rendre_carte(carte(PORTE_HAUT,0),t),'porte_bas':rendre_carte(carte(PORTE_BAS,16),t),
            'trappe':rendre_carte(carte(TRAPPE),t),'barreaux':rendre_carte(carte(BARREAUX),t),'grille':rendre_carte(carte(GRILLE),t)}
if __name__=='__main__':
    f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
    mur=Image.open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/mcmeta-assets/assets/minecraft/textures/block/stone_bricks.png').convert('RGBA')
    bloc=Image.open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex/block/airain_block.png').convert('RGBA')
    W=Image.new('RGBA',(1040,560),(34,30,38,255)); d=ImageDraw.Draw(W)
    for j,(t,lab) in enumerate(((0.0,'neuf'),(0.92,'rouge impérial'))):
        T_=textures(t); y0=40+j*265
        d.text((10,y0+110),lab,font=f,fill=(235,215,170))
        # porte devant un mur, à côté d'un bloc d'airain pour comparer les teintes
        fond=Image.new('RGBA',(48,32)); 
        for (x,y) in ((0,0),(0,16),(16,0),(16,16),(32,0),(32,16)): fond.paste(mur,(x,y))
        fond.paste(bloc if t==0 else Image.open('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/airain_tex/block/oxidized_airain_block.png').convert('RGBA'),(0,16))
        fond.alpha_composite(T_['porte_haut'],(16,0)); fond.alpha_composite(T_['porte_bas'],(16,16))
        fond.alpha_composite(T_['barreaux'],(32,0)); fond.alpha_composite(T_['barreaux'],(32,16))
        W.alpha_composite(fond.resize((360,240),Image.NEAREST),(170,y0))
        f2=Image.new('RGBA',(16,16)); f2.paste(mur,(0,0)); f2.alpha_composite(T_['trappe']); W.alpha_composite(f2.resize((200,200),Image.NEAREST),(560,y0+20))
        f3=Image.new('RGBA',(16,16)); f3.paste(mur,(0,0)); f3.alpha_composite(T_['grille']); W.alpha_composite(f3.resize((200,200),Image.NEAREST),(800,y0+20))
    for x,n in ((260,'bloc · porte · barreaux'),(660,'trappe'),(900,'grille')): d.text((x+40,18),n,font=f,fill=(235,215,170),anchor='mm')
    W.save('/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/rendu_fusion/ferronnerie_v1.png')
    print('ok')
