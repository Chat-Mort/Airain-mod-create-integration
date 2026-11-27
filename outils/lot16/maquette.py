# Armoire impériale : 4 rangées réservées (casque, plastron, jambières, bottes), un bouton d'échange sous chaque colonne
import sys; sys.path.insert(0, '/home/claude/travail/lot13')
from ecran import Ecran, S, OR, OR_S, BLANC, CREUX, ROUGE, ROUGE_S
from PIL import Image, ImageDraw
W, H = 176, 206
def silhouette(e, x, y, k):
    """Gabarit gris de pièce d'armure dans une case vide (comme les cases d'armure du jeu)."""
    g = (70, 74, 86)
    F = {0: ["..######..", ".########.", "##......##", "##......##", "#........#"],
         1: ["##.####.##", "##########", ".########.", ".########.", ".########.", ".########.", "..######.."],
         2: ["##########", "##########", "###....###", "###....###", "###....###", "###....###", "###....###"],
         3: ["###....###", "###....###", "###....###", "####..####", "####..####"]}[k]
    oy = (16 - len(F)) // 2
    for j, l in enumerate(F):
        for i, c in enumerate(l):
            if c == '#': e.R(x + 3 + i, y + oy + j, 1, 1, g)
def bouton(e, x, y, survol=False):
    e.R(x, y, 16, 10, OR_S); e.R(x, y, 15, 9, OR if survol else (190, 150, 90)); e.R(x + 1, y + 1, 13, 7, (240, 205, 130) if survol else (205, 170, 105))
    c = (60, 30, 10)
    # flèches d'échange : haut à gauche, bas à droite
    for (px, py) in ((5, 1), (4, 2), (5, 2), (6, 2), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (5, 4), (5, 5), (5, 6), (5, 7)): e.R(x + px, y + py, 1, 1, c)
    for (px, py) in ((10, 1), (10, 2), (10, 3), (10, 4), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5), (9, 6), (10, 6), (11, 6), (10, 7)): e.R(x + px, y + py, 1, 1, c)
def _maquette():
  pass
if __name__ == "__main__":
 e = Ecran(W, H)
 e.panneau(0, 0, W, H)
 e.texte('Imperial Wardrobe', 8, 5, OR, True)
 for r in range(4):
     for c in range(9):
         e.case(7 + c * 18, 17 + r * 18)
         if (c, r) not in ((0, 0), (0, 1), (0, 2), (0, 3), (2, 0), (2, 1), (3, 3)): silhouette(e, 7 + c * 18, 17 + r * 18, r)
 for c in range(9): bouton(e, 8 + c * 18, 91, survol=(c == 2))
 e.texte('Inventory', 8, 110, BLANC)
 e.inventaire(7, 121)
 im = e.im
 # objets d'exemple : un set complet en colonne 1, deux pièces en colonne 3, des bottes en colonne 4
 B = '/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/textures/item/'
 def it(n): return Image.open(B + n + '.png').convert('RGBA').crop((0, 0, 16, 16))
 for r, n in enumerate(('imperial_helmet', 'imperial_chestplate', 'imperial_leggings', 'imperial_boots')): e.objet(it(n), 8 + 0 * 18, 18 + r * 18)
 e.objet(it('runic_helmet'), 8 + 2 * 18, 18); e.objet(it('runic_chestplate'), 8 + 2 * 18, 36); e.objet(it('runic_boots'), 8 + 3 * 18, 18 + 54)
 # info-bulle du bouton survolé
 d = e.d; x0, y0 = 50, 103
 e.R(x0, y0, 70, 12, (16, 8, 16)); e.R(x0 + 1, y0 + 1, 68, 10, (40, 10, 60)); e.R(x0 + 2, y0 + 2, 66, 8, (16, 8, 16))
 e.texte('Swap armor', x0 + 4, y0 + 2, BLANC)
 fond = Image.new('RGBA', im.size, (139, 139, 139, 255)); fond.alpha_composite(im)
 fond.save('/tmp/mob/wardrobe_gui.png'); print(fond.size)
