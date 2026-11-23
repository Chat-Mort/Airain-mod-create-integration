# Lot 5c : FTB Library (le thème « Nord » sert à tous les écrans FTB : livre de quêtes, réglages…).
# - Boutons Nord (200x20, coins de 4 px, le reste étiré) : plaque d'ardoise dans un cadre d'airain, rivets aux coins ;
#   or au repos, rouge au survol, gris désactivé (règle des états du pack). Bords et centre uniformes : ils sont étirés.
# - Icônes : objets dessinés en pixels ombrés -> pixels nets de 3x3, silhouette adoucie (règle du lot 3).
import os, sys, glob
from PIL import Image
sys.path.insert(0, '/home/claude/travail/lot5'); import ftbq
def hx(s): return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
SRC = '/tmp/src5/ftbl/common/src/main/resources/assets/ftblibrary/textures/'
OR = dict(trait=hx('704425'), hl=hx('fce9b7'), clair=hx('f3d694'), base=hx('e1ba6e'), mi=hx('b48242'), sombre=hx('a8763c'))
ROUGE = dict(trait=hx('520019'), hl=hx('f08a8a'), clair=hx('e06060'), base=hx('c04343'), mi=hx('af1d25'), sombre=hx('8a0018'))
GRIS = dict(trait=hx('2f2d27'), hl=hx('d8d4c6'), clair=hx('bdb8aa'), base=hx('a29d90'), mi=hx('87826f'), sombre=hx('6c6857'))
ARD = dict(haut=hx('434855'), base=hx('363a44'), bas=hx('2e323b'), ombre=hx('1b1e24'))

def bouton(P, gris_fond=False):
    W, H = 600, 60; im = Image.new('RGBA', (W, H)); px = im.load()
    def r(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): px[x, y] = c
    # cadre de 6 texels (dans les 12 du coin) : trait, arête claire, corps, pied sombre, trait ; coins arrondis d'un texel
    bandes = [P['trait'], P['hl'], P['clair'], P['base'], P['mi'], P['trait']]
    for k, c in enumerate(bandes): r(k, k, W - 1 - k, H - 1 - k, c)
    # ombre du cadre en bas et à droite (lumière en haut à gauche)
    r(1, H - 2, W - 2, H - 2, P['sombre']); r(W - 2, 1, W - 2, H - 2, P['sombre'])
    r(2, H - 3, W - 3, H - 3, P['mi']); r(W - 3, 2, W - 3, H - 3, P['mi'])
    # centre : ardoise, plus claire en haut (dégradé vertical, il s'étire sans dommage)
    for y in range(6, H - 6):
        t = (y - 6) / (H - 13); c = ARD['haut'] if t < 0.15 else ARD['base'] if t < 0.8 else ARD['bas']
        r(6, y, W - 7, y, c)
    r(6, 6, W - 7, 6, ARD['ombre'])                                     # ombre portée du cadre en haut
    for (x, y) in ((0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)): px[x, y] = (0, 0, 0, 0)
    # rivets aux quatre coins, dans le carré fixe de 12 texels
    for (cx, cy) in ((8, 8), (W - 9, 8), (8, H - 9), (W - 9, H - 9)):
        for dx, dy in ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            c = P['trait'] if abs(dx) + abs(dy) == 2 else P['hl'] if dx + dy < 0 else P['base'] if dx + dy == 0 else P['mi']
            px[cx + dx, cy + dy] = c
    return im

def icone(rel):
    im = Image.open(SRC + rel).convert('RGBA'); w, h = im.size; bb = im.getbbox()
    out = Image.new('RGBA', (w * 3, h * 3))
    if bb: out.alpha_composite(ftbq.hybride(im.crop(bb)), (bb[0] * 3, bb[1] * 3))
    return out

def sorties():
    s = {'gui/nord_button.png': bouton(OR), 'gui/nord_button_hovered.png': bouton(ROUGE), 'gui/nord_button_disabled.png': bouton(GRIS)}
    for p in sorted(glob.glob(SRC + 'icons/**/*.png', recursive=True)):
        rel = p[len(SRC):]; s[rel] = icone(rel)
    return s

if __name__ == '__main__':
    dest = sys.argv[1] if len(sys.argv) > 1 else '/tmp/l5c/apres/'
    for k, im in sorties().items():
        os.makedirs(os.path.dirname(dest + k), exist_ok=True); im.save(dest + k)
    print(len(sorties()), 'textures ->', dest)

# ---- Sophisticated (icônes des améliorations) et Numismatics (icônes) : planches entières, pixels nets (hybride)
import glob as _g
def planche_hybride(chemin):
    im = Image.open(chemin).convert('RGBA'); return ftbq.hybride(im)
AUTRES = {
    'sophisticatedcore/textures/gui/icons.png': _g.glob('/tmp/src5/sophcore/**/textures/gui/icons.png', recursive=True)[0],
    'numismatics/textures/gui/icons.png': _g.glob('/tmp/src5/numis/**/textures/gui/icons.png', recursive=True)[0],
}

def installer(hd='/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/'):
    n = 0
    for k, im in sorties().items():
        p = hd + 'ftblibrary/textures/' + k; os.makedirs(os.path.dirname(p), exist_ok=True); im.save(p); n += 1
    for k, src in AUTRES.items():
        p = hd + k; os.makedirs(os.path.dirname(p), exist_ok=True); planche_hybride(src).save(p); n += 1
    return n
