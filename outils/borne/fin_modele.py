# Modèles de la machine de l'Empereur (éteinte, Cœur posé, rallumée), à partir de l'aperçu validé le 6 novembre.
exec(open('integrer.py').read().split('# ======================= Empire')[0])
DARK, RUST, IRON2, BRASS, GOLD, GOLD2 = (40, 40, 46), (96, 70, 52), (55, 56, 62), (200, 150, 60), (232, 192, 72), (180, 135, 40)
VOLET, CTERNE, CVIF, CLUM = (60, 70, 80), (110, 60, 40), (235, 120, 40), (255, 230, 150, 1)
def machine(nom, etat):
    metal, laiton = (DARK, RUST) if etat < 2 else (IRON2, BRASS)
    m = Modele(nom, [metal, laiton, GOLD if etat == 2 else GOLD2, VOLET, CTERNE, CVIF, CLUM])
    m.b(-2, 0, -2, 18, 3, 18, metal); m.b(-1, 3, -1, 17, 4, 17, laiton)            # socle
    m.cyl(8, 8, 4, 26, 7, metal)                                                     # chambre du Cœur
    for y in (6, 15, 24): m.anneau_xz(8, 8, y, y + 1.2, 6.9, 7.4, laiton)
    if etat == 0: m.b(3, 11, 0.4, 13, 21, 1.4, VOLET)                                # volet fermé (face nord = avant)
    else:
        m.b(3, 11, 0.6, 13, 11.6, 4, laiton); m.b(3, 20.4, 0.6, 13, 21, 4, laiton)   # niche ouverte
        m.b(4.8, 12.8, 0, 11.2, 19.2, 4, CVIF if etat == 2 else CTERNE, etat == 2)    # le Cœur
        m.anneau_xy(8, 16, 0.2, 1.2, 3.0, 4.0, GOLD if etat == 2 else GOLD2)
        if etat == 2: m.b(6.6, 14.6, -0.4, 9.4, 17.4, 0.2, CLUM, True)
    m.rouage_yz(15, 8, -2.5, 0, 5.5, laiton); m.rouage_yz(15, 8, 16, 18.5, 5.5, laiton)   # rouages latéraux
    for x in (2, 14): m.cyl(x, 12, 26, 32, 1.2, metal); m.cyl(x, 12, 31, 32, 1.6, laiton)  # cheminées
    for k in range(6):                                                               # fleurons
        a = k * math.pi / 3; cx, cz = 8 + 6 * math.cos(a), 8 + 6 * math.sin(a); m.b(cx - .6, 26, cz - .6, cx + .6, 29, cz + .6, GOLD if etat == 2 else GOLD2)
    m.texture(); m.modele(gui=0.4)
for nom, e in (("emperor_machine_off", 0), ("emperor_machine_heart", 1), ("emperor_machine_on", 2)): machine(nom, e)
FAC = (("north", 0), ("east", 90), ("south", 180), ("west", 270))
json.dump({"variants": {f"etat={e},facing={f}": {"model": "airain:block/" + n, "y": y} for e, n in enumerate(("emperor_machine_off", "emperor_machine_heart", "emperor_machine_on")) for f, y in FAC}},
          open(f'{A}/blockstates/emperor_machine.json', 'w'), indent=1)
