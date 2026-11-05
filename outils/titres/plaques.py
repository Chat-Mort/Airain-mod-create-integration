"""Petits titres de section du livre de quêtes : plaques de laiton (Empire) ou d'obsidienne (Écho), police du jeu."""
import sys, unicodedata, random
from PIL import Image
SC = "/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad/"
A = Image.open(SC + "mcmeta-assets/assets/minecraft/textures/font/ascii.png").convert("RGBA")
ACC = {"́": "aigu", "̀": "grave", "̂": "circ", "̧": "cedille", "̈": "trema"}
def glyphe(ch):
    d = unicodedata.normalize("NFD", ch); base, marques = d[0], [ACC[m] for m in d[1:] if m in ACC]
    o = ord(base) if ord(base) < 256 else ord("?")
    g = A.crop(((o % 16) * 8, (o // 16) * 8, (o % 16) * 8 + 8, (o // 16) * 8 + 8))
    cols = [x for x in range(8) if any(g.getpixel((x, y))[3] for y in range(8))]
    w = (max(cols) + 1) if cols else 3
    return g, w, marques, base.isupper()
def largeur(t): return sum(glyphe(c)[1] + 1 for c in t) - 1
def ecrire(im, x, y, t, coul, ombre=None):
    for (dx, dy, c) in ((1, 1, ombre),) if ombre else ():
        _ecrire(im, x + dx, y + dy, t, c)
    _ecrire(im, x, y, t, coul)
def _ecrire(im, x, y, t, coul):
    for ch in t:
        g, w, marques, maj = glyphe(ch)
        m = Image.new("RGBA", g.size, coul + (255,)); m.putalpha(g.split()[3]); im.alpha_composite(m, (x, y))
        top = y - 2 if maj else y + 0          # rangées libres au-dessus des minuscules (rangée 0-1)
        cx = x + w // 2
        for mk in marques:
            pts = {"aigu": [(cx, top), (cx - 1, top + 1)], "grave": [(cx - 1, top), (cx, top + 1)],
                   "circ": [(cx - 1, top + 1), (cx, top), (cx + 1, top + 1)], "trema": [(cx - 2, top + 1), (cx + 1, top + 1)],
                   "cedille": [(cx, y + 7), (cx - 1, y + 8)]}[mk]
            for p in pts:
                if 0 <= p[0] < im.width and 0 <= p[1] < im.height: im.putpixel(p, coul + (255,))
        x += w + 1
STYLES = {
 "empire": dict(cadre=(58, 40, 22), face=(201, 152, 62), clair=(236, 196, 104), sombre=(150, 104, 40), rivet=(250, 226, 150), texte=(50, 30, 14), ombre=None),
 "echo":   dict(cadre=(18, 12, 28), face=(52, 36, 78), clair=(96, 68, 140), sombre=(34, 24, 52), rivet=(200, 170, 255), texte=(225, 210, 255), ombre=(20, 12, 34)),
}
def plaque(t, style="empire"):
    s = STYLES[style]; random.seed(t)
    w, h = largeur(t) + 14, 16
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for x in range(w):
        for y in range(h):
            bord = x in (0, w - 1) or y in (0, h - 1)
            coin = (x in (0, w - 1)) and (y in (0, h - 1))
            if coin: continue
            if bord: c = s["cadre"]
            elif y == 1 or x == 1: c = s["clair"]
            elif y == h - 2 or x == w - 2: c = s["sombre"]
            else:
                n = random.randint(-6, 6); c = tuple(max(0, min(255, v + n)) for v in s["face"])
            im.putpixel((x, y), c + (255,))
    for (rx, ry) in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
        im.putpixel((rx, ry), s["rivet"] + (255,)); im.putpixel((rx + 1, ry + 1), s["sombre"] + (255,))
    ecrire(im, 7, 5, t, s["texte"], s["ombre"])
    return im
if __name__ == "__main__":
    out = Image.new("RGBA", (420, 120), (30, 31, 36, 255)); y = 6
    for t, st in (("Le laiton", "empire"), ("L'appel de l'Écho", "empire"), ("Les Échos perdus", "echo"), ("La précision", "empire")):
        p = plaque(t, st); p = p.resize((p.width * 3, p.height * 3), Image.NEAREST); out.alpha_composite(p, (6, y)) if y < 100 else None; y += 0
    out.save("essai.png")
