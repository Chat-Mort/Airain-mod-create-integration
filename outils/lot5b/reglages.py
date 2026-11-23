# Lot 5b : réglage de valeur de Create (la fenêtre qui s'ouvre en maintenant clic droit sur une valeur : vitesse, quantité…).
# Le cadre de laiton passe en baguette d'airain neuf ; le texte des étiquettes et du curseur reste brun sur airain (couleur imposée
# par Create, 0x442000), donc étiquettes et curseur restent des plaques claires, sans le damier d'origine.
from kit import *
def reglages():
    p = Planche(); S_ = S
    def R(x, y, w, h, c): p.r(x * S_, y * S_, (x + w) * S_ - 1, (y + h) * S_ - 1, c)
    # --- piste des valeurs (7,0 249x8, répétée tous les 248 px) : creux sombre, graduation fine tous les 2 px
    X0, X1 = 7 * S_, 256 * S_ - 1
    p.r(X0, 0, X1, 23, ARD['noir']); p.r(X0, 1, X1, 22, ARD['ombre'])
    for X in range(X0, X1 + 1):
        if (X - X0) % 6 == 0: p.r(X, 4, X, 19, ARD['ombre2'])
    p.r(X0, 1, X1, 2, ARD['noir'])                       # ombre portée du bord haut
    p.r(X0, 21, X1, 21, ARD['creux'])                    # reflet du fond de la piste
    # repères (0,0 7x8) et repère large (75,14 13x8) : cran d'airain sombre dans la piste
    def repere(x, y, w):
        Xa, Ya, Xb, Yb = x * S_, y * S_, (x + w) * S_ - 1, (y + 8) * S_ - 1
        p.r(Xa, Ya, Xb, Yb, ARD['noir']); p.r(Xa + 1, Ya + 1, Xb - 1, Yb - 1, ARD['ombre'])
        c = (Xa + Xb) // 2
        p.r(c - 2, Ya + 3, c + 2, Yb - 3, OR['trait']); p.r(c - 1, Ya + 4, c, Yb - 4, OR['mi']); p.r(c + 1, Ya + 4, c + 1, Yb - 4, OR['sombre'])
        p.r(c - 1, Ya + 4, c, Ya + 5, OR['base'])
    repere(0, 0, 7); repere(75, 14, 13)
    # fonds unis étirés (75,9) et (80,9)
    R(75, 9, 1, 1, ARD['noir'])                          # le fond extérieur (80,9) reste transparent, comme l'original
    # --- curseur (0,9 / 4,9 / 61,9) : plaque d'airain, le milieu est rogné à la largeur du texte (lignes uniformes)
    def rangees(X0, X1, Y0):
        for k, c in enumerate([OR['trait'], OR['hl'], OR['clair']] + [OR['base']] * 33 + [OR['mid'], OR['mi'], OR['sombre'], OR['trait']]):
            p.r(X0, Y0 + k, X1, Y0 + k, c)
    rangees(4 * S_, 60 * S_ - 1, 9 * S_)
    def embout(x, gauche):
        X = x * S_; Y = 9 * S_
        cols = [None, OR['trait'], OR['hl'] if gauche else OR['sombre']] if gauche else [OR['sombre'], OR['trait'], None]
        for k in range(3):
            for t in range(3):
                Xc = X + k * S_ + t
                if gauche:
                    if k == 0: c = OR['trait'] if t == 2 else None
                    elif k == 1: c = OR['trait'] if t == 0 else OR['hl'] if t == 1 else OR['clair']
                    else: c = 'rang'
                else:
                    if k == 2: c = OR['trait'] if t == 0 else None
                    elif k == 1: c = OR['sombre'] if t == 0 else OR['trait'] if t == 1 else None
                    else: c = 'rang'
                if c == 'rang':
                    for kk, cc in enumerate([OR['trait'], OR['hl'], OR['clair']] + [OR['base']] * 33 + [OR['mid'], OR['mi'], OR['sombre'], OR['trait']]):
                        p.im.putpixel((Xc, Y + kk), cc)
                elif c:
                    y0, y1 = (Y + 1, Y + 40) if (k == 1) else (Y + 15, Y + 26)     # l'ergot de côté, au milieu
                    p.r(Xc, y0, Xc, y1, c)
        # le haut et le bas des embouts suivent le tour de la plaque
    embout(0, True); embout(61, False)
    # --- icône du curseur (0,44 22x20) : plaque d'airain à ergots
    plaque_or(p, 1 * S_, 44 * S_, 21 * S_ - 1, 64 * S_ - 1)
    for X in (0, 21 * S_):
        p.r(X, 52 * S_, X + 2, 56 * S_ - 1, OR['trait']); p.r(X + (1 if X == 0 else 0), 52 * S_ + 1, X + (2 if X == 0 else 1), 56 * S_ - 2, OR['base'])
    # --- étiquette (0,31 161x11), rognée à droite : plaque claire, arête haute, pied ombré
    for k, c in enumerate([OR['hl'], OR['clair']] + [OR['base']] * 26 + [OR['mid'], OR['mi'], OR['sombre'], OR['trait']][:5]):
        p.r(0, 31 * S_ + k, 161 * S_ - 1, 31 * S_ + k, c)
    p.r(0, 31 * S_, 2, 42 * S_ - 1, OR['trait']); p.r(3, 31 * S_ + 1, 3, 42 * S_ - 3, OR['hl'])
    # --- cadre : coins 4x4, côtés étirés (3 px), haut et bas rognés
    B = bande_or()
    def horiz(y):
        for k, c in enumerate(B): p.r(0, y * S_ + k, 256 * S_ - 1, y * S_ + k, c)
    horiz(24); horiz(27)
    def vert(x, y):
        for k, c in enumerate(B): p.r(x * S_ + k, y * S_, x * S_ + k, (y + 4) * S_ - 1, c)
    vert(65, 14); vert(71, 14)
    def coin(x, y, dx, dy):
        # coin 4x4 : les deux baguettes se rejoignent en onglet (diagonale depuis l'angle extérieur), rivet dessus
        X, Y = x * S_, y * S_; ox = 3 * dx; oy = 3 * dy
        for j in range(12):
            for i in range(12):
                u, v = i - ox, j - oy
                hb = 0 <= v < 9 and ((dx == 0 and i >= ox) or (dx == 1 and i < ox + 9))
                vb = 0 <= u < 9 and ((dy == 0 and j >= oy) or (dy == 1 and j < oy + 9))
                if hb and vb:
                    horiz = {(0, 0): u > v, (1, 0): u + v < 8, (0, 1): u + v > 8, (1, 1): u < v}[(dx, dy)]
                    c = B[v] if horiz else B[u]
                elif hb: c = B[v]
                elif vb: c = B[u]
                else: continue
                p.im.putpixel((X + i, Y + j), c)
        p.rivet_or(X + ox + 4, Y + oy + 4)
    coin(65, 9, 0, 0); coin(70, 9, 1, 0); coin(65, 19, 0, 1); coin(70, 19, 1, 1)
    return p.im
def _rivet_or(self, cx, cy):
    for dx, dy in ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1)):
        c = OR['hl'] if dx + dy < 0 else OR['base'] if dx + dy == 0 else OR['mi']
        self.im.putpixel((cx + dx, cy + dy), c)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)): self.im.putpixel((cx + dx, cy + dy), OR['mid'])
Planche.rivet_or = _rivet_or

# ---------------- version habillée (retour de Liam : la glissière ne doit pas être « qu'un rectangle ») ----------------
def reglages():
    p = Planche(); s = S
    def ligne(X0, X1, Y, c): p.r(X0, Y, X1, Y, c)
    # --- piste (7,0 249x8, répétée tous les 248) : règle à calcul. Rails d'airain en haut et en bas, fond gravé,
    #     petite graduation tous les 2 px, grande tous les 8 px (744 texels = 31 grands pas : la répétition tombe juste)
    X0, X1 = 7 * s, 256 * s - 1
    ligne(X0, X1, 0, OR['trait']); ligne(X0, X1, 1, OR['clair']); ligne(X0, X1, 2, OR['mi']); ligne(X0, X1, 3, OR['trait'])
    p.r(X0, 4, X1, 19, ARD['ombre']); ligne(X0, X1, 4, ARD['noir']); ligne(X0, X1, 5, ARD['noir'])
    ligne(X0, X1, 12, ARD['ombre2'])                                     # rainure centrale
    for X in range(X0, X1 + 1):
        k = X - X0
        if k % 24 == 0: p.r(X, 13, X, 19, OR['sombre']); p.r(X + 1, 14, X + 1, 19, OR['trait'])
        elif k % 6 == 0: p.r(X, 16, X, 19, hx('4b5160'))
    ligne(X0, X1, 20, OR['trait']); ligne(X0, X1, 21, OR['base']); ligne(X0, X1, 22, OR['mi']); ligne(X0, X1, 23, OR['trait'])
    # --- repères : index d'airain (pointe vers le bas, tige) sur la piste
    def repere(x, y, w):
        # index d'airain : une bride qui enserre les deux rails (raccord en haut et en bas, sur toute la hauteur de la piste),
        # montant entre les deux, bouton en losange sur la rainure. Aux deux bouts de la règle (valeur 0 et maximum),
        # cette bride ferme la piste (retour de Liam : la règle finissait ouverte).
        Xa, Ya, Xb = x * s, y * s, (x + w) * s - 1; c = (Xa + Xb) // 2
        for (y0, y1) in ((Ya, Ya + 4), (Ya + 19, Ya + 23)):            # colliers sur les rails
            p.r(c - 3, y0, c + 3, y1, OR['trait']); p.r(c - 2, y0 + 1, c + 2, y1 - 1, OR['base'])
            p.r(c - 2, y0 + 1, c + 2, y0 + 1, OR['hl']); p.r(c - 2, y1 - 1, c + 2, y1 - 1, OR['mi'])
        p.r(c - 1, Ya + 5, c + 1, Ya + 18, OR['trait']); p.r(c, Ya + 5, c, Ya + 18, OR['base'])
        for k in range(4):
            p.r(c - 3 + k, Ya + 12 - k, c + 3 - k, Ya + 12 - k, OR['trait']); p.r(c - 3 + k, Ya + 12 + k, c + 3 - k, Ya + 12 + k, OR['trait'])
        for k in range(3):
            p.r(c - 2 + k, Ya + 12 - k, c + 2 - k, Ya + 12 - k, OR['clair'] if k else OR['base']); p.r(c - 2 + k, Ya + 12 + k, c + 2 - k, Ya + 12 + k, OR['mi'] if k else OR['base'])
        p.im.putpixel((c - 1, Ya + 11), OR['hl'])
    repere(0, 0, 7); repere(75, 14, 13)
    R = lambda x, y, w, h, c: p.r(x * s, y * s, (x + w) * s - 1, (y + h) * s - 1, c)
    R(75, 9, 1, 1, ARD['noir'])
    # --- curseur : chariot d'airain. Milieu rogné à la largeur du texte (rangées uniformes) ; les embouts portent le décor :
    #     molettes striées et rivet, ergot pointé vers la piste
    rang = ([OR['trait'], OR['hl'], OR['clair'], OR['mi']] + [OR['base']] * 30 + [OR['mid'], OR['mid'], OR['mi'], OR['hl'], OR['sombre'], OR['trait']])
    def colonne(X, Y0, rr):
        for k, c in enumerate(rr): p.im.putpixel((X, Y0 + k), c)
    for X in range(4 * s, 60 * s): colonne(X, 9 * s, rang)
    def embout(x, gauche):
        X0 = x * s; Y0 = 9 * s
        for t in range(9):
            X = X0 + t; i = t if gauche else 8 - t          # i : distance au bord extérieur
            if i == 0:
                p.r(X, Y0 + 14, X, Y0 + 27, OR['trait'])       # ergot
            elif i == 1:
                p.r(X, Y0 + 1, X, Y0 + 40, OR['trait']); p.r(X, Y0 + 15, X, Y0 + 26, OR['mi'])
            else:
                colonne(X, Y0, rang)
                if i in (3, 5, 7): p.r(X, Y0 + 6, X, Y0 + 35, OR['mi'] if gauche else OR['sombre'])     # stries de prise
                if i == 2: p.r(X, Y0 + 2, X, Y0 + 39, OR['hl'] if gauche else OR['sombre'])
        p.im.putpixel((X0 + (0 if gauche else 8), Y0), (0, 0, 0, 0))
    embout(0, True); embout(61, False)
    # --- encadré de l'icône du curseur (0,44 22x20) : lunette d'airain, quatre rivets, filet gravé dedans, ergots
    plaque_or(p, 1 * s, 44 * s, 21 * s - 1, 64 * s - 1)
    p.r(1 * s + 5, 44 * s + 5, 21 * s - 6, 64 * s - 6, OR['mi']); p.r(1 * s + 6, 44 * s + 6, 21 * s - 6, 64 * s - 6, OR['hl'])
    p.r(1 * s + 6, 44 * s + 6, 21 * s - 7, 64 * s - 7, OR['base'])
    for (X, Y) in ((1 * s + 3, 44 * s + 3), (21 * s - 4, 44 * s + 3), (1 * s + 3, 64 * s - 4), (21 * s - 4, 64 * s - 4)): p.rivet_or(X, Y)
    for X in (0, 21 * s):
        p.r(X, 52 * s, X + 2, 56 * s - 1, OR['trait']); p.r(X + (1 if X == 0 else 0), 52 * s + 1, X + (2 if X == 0 else 1), 56 * s - 2, OR['base'])
    # --- étiquette (0,31 161x11, rognée à droite) : plaque nominative, embout gauche riveté, filet gravé sous le texte
    # étiquette (0,31 161x11, rognée à droite) : plaque nominative aux bouts arrondis. Rangées : trait, arête claire, corps,
    #   pied ombré, trait. L'embout gauche (les 4 px avant le texte) porte une vis ; l'embout droit arrondi (162,31 3x11)
    #   est posé par le mod sur le bout de la plaque rognée (ReglageValeurMixin).
    rangs = [OR['trait'], OR['hl'], OR['clair']] + [OR['base']] * 26 + [OR['mid'], OR['mi'], OR['sombre'], OR['trait']]   # 33 texels = 11 px
    def plaque_rangs(X0, X1):
        for k, c in enumerate(rangs): p.r(X0, 31 * s + k, X1, 31 * s + k, c)
    plaque_rangs(0, 161 * s - 1)
    Y0 = 31 * s; Y1 = 42 * s - 1
    def arrondi(X, droite):
        # quart de cercle de 5 texels aux deux coins de l'embout ; bord : trait, puis arête (claire à gauche, sombre à droite)
        R = 5
        for j in range(R):
            for i in range(R):
                d = ((R - 0.5 - i) ** 2 + (R - 0.5 - j) ** 2) ** 0.5
                for (yy, haut) in ((Y0 + j, True), (Y1 - j, False)):
                    xx = X + i if not droite else X + 8 - i
                    if d > R: p.im.putpixel((xx, yy), (0, 0, 0, 0))
                    elif d > R - 1: p.im.putpixel((xx, yy), OR['trait'])
                    elif d > R - 2: p.im.putpixel((xx, yy), (OR['hl'] if haut else OR['mi']) if not droite else (OR['clair'] if haut else OR['sombre']))
        xb = X if not droite else X + 8
        p.r(xb, Y0 + R, xb, Y1 - R, OR['trait'])
        p.r(xb + (1 if not droite else -1), Y0 + R, xb + (1 if not droite else -1), Y1 - R, OR['hl'] if not droite else OR['sombre'])
    arrondi(0, False)
    p.rivet_or(8, (Y0 + Y1) // 2)
    plaque_rangs(162 * s, 165 * s - 1); arrondi(162 * s, True)
    # (le texte commence 4 px après le bord : l'embout reste libre ; pas de rivet, le texte d'une ligne courte pourrait le toucher)
    # --- cadre : baguettes de 3 px, rivets réguliers sur le haut et le bas (rognés depuis la gauche : le rythme se garde)
    B = bande_or()
    for y in (24, 27):
        for k, c in enumerate(B): p.r(0, y * s + k, 256 * s - 1, y * s + k, c)
        for X in range(18, 256 * s - 4, 30): p.rivet_or(X, y * s + 4)
    for x in (65, 71):
        for k, c in enumerate(B): p.r(x * s + k, 14 * s, x * s + k, 18 * s - 1, c)
    def coin(x, y, dx, dy):
        # coin en rosace : carré d'airain à pans coupés, rivet central (4x4 px)
        X, Y = x * s, y * s
        p.r(X, Y, X + 11, Y + 11, (0, 0, 0, 0))
        for j in range(12):
            for i in range(12):
                if min(i, 11 - i) + min(j, 11 - j) < 2: continue          # pans coupés
                bord = i in (0, 11) or j in (0, 11) or min(i, 11 - i) + min(j, 11 - j) == 2
                c = OR['trait'] if bord else OR['hl'] if (i == 1 or j == 1) else OR['mi'] if (i == 10 or j == 10) else OR['base']
                p.im.putpixel((X + i, Y + j), c)
        for k in range(3, 9): p.im.putpixel((X + k, Y + 3), OR['mi']); p.im.putpixel((X + 3, Y + k), OR['mi'])
        for k in range(3, 9): p.im.putpixel((X + k, Y + 8), OR['clair']); p.im.putpixel((X + 8, Y + k), OR['clair'])
        p.rivet_or(X + 5, Y + 5); p.im.putpixel((X + 6, Y + 6), OR['mi'])
    coin(65, 9, 0, 0); coin(70, 9, 1, 0); coin(65, 19, 0, 1); coin(70, 19, 1, 1)
    return p.im
