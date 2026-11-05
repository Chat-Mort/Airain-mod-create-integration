"""Sujets v7, lot D : machines du mod Create."""
import math
from kit import bez, quad, T, T2, T3, R
from sujets_b import sol

def carter(k, u0, v0, u1, v1, w=1.0):
    """Carter d'andésite : bloc à cornières et planches."""
    k.solid(k.rect(u0, v0, u1, v1), T, w)
    du, dv = (u1 - u0)*0.14, (v1 - v0)*0.14
    for (a, b) in ((u0, v0), (u1 - du, v0), (u0, v1 - dv), (u1 - du, v1 - dv)): k.solid(k.rect(a, b, a + du, b + dv), T2, 0.7)
    k.line([(u0 + du, (v0 + v1)/2), (u1 - du, (v0 + v1)/2)], T3, 0.5)
    k.line([((u0 + u1)/2, v0 + dv), ((u0 + u1)/2, v1 - dv)], T3, 0.5)

def cog(k, cu, cv, r, n=8):
    """Rouage de Create : disque d'andésite et dents en blocs de bois."""
    for i in range(n):
        a = 2*math.pi*i/n; ca, sa = math.cos(a), math.sin(a); w = r*0.2
        pts = [(cu + ca*r*0.75 - sa*w, cv + (sa*r*0.75 + ca*w)*k.k), (cu + ca*r*1.05 - sa*w, cv + (sa*r*1.05 + ca*w)*k.k),
               (cu + ca*r*1.05 + sa*w, cv + (sa*r*1.05 - ca*w)*k.k), (cu + ca*r*0.75 + sa*w, cv + (sa*r*0.75 - ca*w)*k.k)]
        k.solid(pts, T, 0.8)
    k.solid(k.cer(cu, cv, r*0.8)); k.closed(k.cer(cu, cv, r*0.55), T2, 0.6); k.solid(k.rect(cu - r*0.15, cv - r*0.15*k.k, cu + r*0.15, cv + r*0.15*k.k), T, 0.7)

def arbre(k, a, b, ep=0.035):
    (u0, v0), (u1, v1) = a, b
    if abs(v1 - v0) < abs(u1 - u0): k.solid(k.rect(min(u0, u1), v0 - ep, max(u0, u1), v0 + ep), T, 0.8)
    else: k.solid(k.rect(u0 - ep, min(v0, v1), u0 + ep, max(v0, v1)), T, 0.8)

# ---------------------------------------------------------------- 1 x 1
def manivelle(k):
    k.solid(k.rect(0.2, 0.84, 0.8, 0.96)); k.hatch(k.rect(0.2, 0.88, 0.8, 0.96))
    k.solid(k.rect(0.42, 0.5, 0.58, 0.84))
    k.solid(k.cer(0.5, 0.46, 0.1))
    k.solid([(0.46, 0.42), (0.54, 0.42), (0.84, 0.2), (0.8, 0.14)])
    k.solid(k.rrect(0.76, 0.04, 0.88, 0.2, 0.04)); k.dot((0.5, 0.46), 1.0, R)
    k.line(k.cer(0.5, 0.46, 0.38, 200, 300), T3, 0.6); k.line([(0.14, 0.32), (0.13, 0.4), (0.2, 0.37)], T3, 0.6)

def bruleur(k):
    k.solid([(0.12, 0.96), (0.88, 0.96), (0.82, 0.86), (0.18, 0.86)])
    for u in (0.2, 0.33, 0.5, 0.67, 0.8): k.line([(u, 0.86), (u, 0.34)], T, 1.0)          # cage
    k.line([(0.18, 0.36), (0.82, 0.36)], T, 1.2); k.line([(0.18, 0.6), (0.82, 0.6)], T2, 0.8)
    flamme = bez((0.3, 0.82), (0.22, 0.6), (0.36, 0.5), (0.4, 0.3)) + bez((0.4, 0.3), (0.46, 0.44), (0.5, 0.36), (0.52, 0.18))[1:] + bez((0.52, 0.18), (0.6, 0.36), (0.66, 0.42), (0.64, 0.28))[1:] + bez((0.64, 0.28), (0.8, 0.5), (0.76, 0.7), (0.7, 0.82))[1:]
    k.line(flamme + [flamme[0]], R, 1.0)
    for u in (0.42, 0.58): k.solid(k.rect(u - 0.04, 0.62, u + 0.04, 0.68), R, 0.8)
    k.line([(0.44, 0.75), (0.56, 0.75)], R, 0.8)

def boite_vitesses(k):
    arbre(k, (0.0, 0.5), (1.0, 0.5)); arbre(k, (0.5, 0.0), (0.5, 1.0))
    carter(k, 0.18, 0.18, 0.82, 0.82)
    k.dash(k.cer(0.5, 0.36, 0.1), T3); k.dash(k.cer(0.36, 0.5, 0.1), T3); k.dash(k.cer(0.64, 0.5, 0.1), T3); k.dash(k.cer(0.5, 0.64, 0.1), T3)

def cle_create(k):
    k.solid(k.rrect(0.36, 0.42, 0.64, 0.98, 0.1))                                            # manche
    for i in range(6): k.line([(0.36, 0.6 + i*0.06), (0.64, 0.6 + i*0.06)], T2, 0.6)
    k.solid([(0.3, 0.42), (0.7, 0.42), (0.7, 0.36), (0.3, 0.36)])
    cog(k, 0.5, 0.2, 0.34, 8)
    k.hole([(0.4, 0.0), (0.6, 0.0), (0.6, 0.14), (0.4, 0.14)], T2)                         # mâchoire

def ventilateur(k):
    arbre(k, (0.5, 0.82), (0.5, 1.0))
    carter(k, 0.1, 0.1, 0.9, 0.82)
    k.hole(k.cer(0.5, 0.46, 0.3), T)
    for i in range(4):
        a = math.radians(i*90 + 20)
        k.solid([(0.5, 0.46), (0.5 + 0.27*math.cos(a), 0.46 + 0.27*math.sin(a)), (0.5 + 0.24*math.cos(a + 0.6), 0.46 + 0.24*math.sin(a + 0.6))], T2, 0.7)
    k.solid(k.cer(0.5, 0.46, 0.06)); k.closed(k.rect(0.2, 0.2, 0.8, 0.72), T3, 0.5)

# ---------------------------------------------------------------- 2 x 1
def tapis(k):
    for u in (0.12, 0.88): k.solid(k.cer(u, 0.6, 0.08)); k.solid(k.rect(u - 0.02, 0.56, u + 0.02, 0.64), T, 0.7)
    k.line([(0.12, 0.6 - 0.08*k.k), (0.88, 0.6 - 0.08*k.k)], T, 1.6); k.line([(0.12, 0.6 + 0.08*k.k), (0.88, 0.6 + 0.08*k.k)], T, 1.6)
    for i in range(14): u = 0.16 + i*0.051; k.line([(u, 0.6 - 0.08*k.k - 0.02), (u, 0.6 - 0.08*k.k + 0.02)], T2, 0.6)
    for u in (0.3, 0.5, 0.7): k.closed(k.cer(u, 0.6, 0.02), T3, 0.5)
    for (u, w) in ((0.28, 0.1), (0.52, 0.08), (0.72, 0.1)):                                  # objets transportés
        v = 0.6 - 0.08*k.k - 0.02
        k.solid(k.rect(u - w/2, v - w*2, u + w/2, v))
    k.line([(0.4, 0.14), (0.6, 0.14)], R, 0.9); k.solid([(0.6, 0.1), (0.64, 0.14), (0.6, 0.18)], R, 0.8)
    for u in (0.12, 0.88): k.line([(u, 0.68 + 0.04), (u, 0.96)], T3, 0.6)

def scie(k):
    sol(k, 0.94)
    k.solid([(0.05, 0.72), (0.95, 0.72), (0.95, 0.94), (0.05, 0.94)])                        # bloc en bout de châssis
    k.hatch([(0.05, 0.86), (0.95, 0.86), (0.95, 0.94), (0.05, 0.94)])
    carter(k, 0.36, 0.42, 0.64, 0.72)
    k.solid(k.gear(0.5, 0.42, 0.26, 24, 0.12))                                                # lame circulaire
    k.closed(k.cer(0.5, 0.42, 0.18), T2, 0.6); k.solid(k.cer(0.5, 0.42, 0.04))
    k.solid(k.rect(0.36, 0.42, 0.64, 0.72), T, 1.0)
    k.solid(k.rrect(0.04, 0.5, 0.3, 0.7, 0.06)); k.closed(k.ell(0.04, 0.6, 0.02, 0.1), T2, 0.6)   # bûche
    for i in range(3): k.closed(k.ell(0.04, 0.6, 0.012*(3 - i), 0.025*(3 - i)), T3, 0.5)
    for i in range(6): k.dot((0.32 + i*0.01, 0.42 + (i % 2)*0.04), 0.6, R)

# ---------------------------------------------------------------- 2 x 2
def moteur_vapeur(k):
    sol(k, 0.96)
    bruleur_k = lambda u: (k.solid([(u - 0.12, 0.96), (u + 0.12, 0.96), (u + 0.1, 0.88), (u - 0.1, 0.88)]), [k.line([(x, 0.88), (x, 0.8)], T2, 0.7) for x in (u - 0.08, u, u + 0.08)])
    for u in (0.22, 0.48): bruleur_k(u)
    k.solid(k.rect(0.08, 0.2, 0.62, 0.8))                                                      # réservoir 2 x 2
    for v in (0.2, 0.5, 0.8): k.solid(k.rect(0.07, v - 0.02, 0.63, v + 0.02), T2, 0.8)
    k.line([(0.35, 0.22), (0.35, 0.78)], T2, 0.6)
    for (u, v) in ((0.2, 0.34), (0.48, 0.34), (0.2, 0.64), (0.48, 0.64)): k.hole(k.rrect(u - 0.06, v - 0.06, u + 0.06, v + 0.06, 0.02), T2)
    k.solid(k.cer(0.52, 0.12, 0.05)); k.line([(0.52, 0.12), (0.55, 0.09)], R, 0.8); k.line([(0.52, 0.17), (0.52, 0.2)], T, 0.9)
    k.solid(k.rect(0.62, 0.44, 0.78, 0.6))                                                     # moteur
    k.line([(0.78, 0.52), (0.86, 0.46)], T, 1.6)
    cog(k, 0.88, 0.42, 0.08)
    arbre(k, (0.88, 0.0), (0.88, 0.34))
    for j in range(3): k.line(k.ell(0.7 - j*0.04, 0.38 - j*0.07, 0.03, 0.02, 180, 360), T3, 0.6)

def coucou(k):
    k.axe((0.5, 0.0), (0.5, 1.0))
    maison = [(0.18, 0.28), (0.82, 0.28), (0.82, 0.7), (0.18, 0.7)]
    k.solid(maison)
    k.solid([(0.06, 0.32), (0.5, 0.02), (0.94, 0.32), (0.88, 0.34), (0.5, 0.08), (0.12, 0.34)])  # toit
    k.solid(k.rect(0.44, 0.14, 0.56, 0.24)); k.hole(k.rect(0.46, 0.16, 0.54, 0.24), T2)       # porte de l'oiseau
    k.solid(k.ell(0.5, 0.2, 0.025, 0.02), R, 0.7)
    k.solid(k.cer(0.5, 0.48, 0.17)); k.closed(k.cer(0.5, 0.48, 0.14), T2, 0.6)
    for i in range(12): a = math.radians(i*30); k.line([(0.5 + math.cos(a)*0.11, 0.48 + math.sin(a)*0.11), (0.5 + math.cos(a)*0.14, 0.48 + math.sin(a)*0.14)], T, 0.7)
    k.line([(0.5, 0.48), (0.5, 0.39)], R, 1.0); k.line([(0.5, 0.48), (0.57, 0.5)], R, 1.0)
    for s in (-1, 1): k.line(bez((0.5 + s*0.3, 0.7), (0.5 + s*0.34, 0.6), (0.5 + s*0.36, 0.44), (0.5 + s*0.3, 0.3)), T2, 0.9)   # sculptures
    k.line([(0.5, 0.7), (0.5, 0.88)], T, 0.8); k.solid(k.cer(0.5, 0.9, 0.04))                  # balancier
    for u in (0.36, 0.64):                                                                      # poids en pomme de pin
        k.line([(u, 0.7), (u, 0.82)], T2, 0.6)
        k.solid(bez((u, 0.82), (u - 0.05, 0.86), (u - 0.04, 0.96), (u, 0.98)) + bez((u, 0.98), (u + 0.04, 0.96), (u + 0.05, 0.86), (u, 0.82))[1:])
        for j in range(3): k.line([(u - 0.03, 0.86 + j*0.03), (u + 0.03, 0.88 + j*0.03)], T2, 0.5)

def meule(k):
    arbre(k, (0.5, 0.7), (0.5, 1.0))
    carter(k, 0.14, 0.62, 0.86, 0.9)
    cog(k, 0.5, 0.96, 0.08)
    for (v, h) in ((0.44, 0.18), (0.24, 0.18)):                                                  # deux meules de pierre
        k.solid(k.rect(0.16, v, 0.84, v + h))
        k.solid(k.ell(0.5, v, 0.34, 0.05))
        for i in range(7): k.line([(0.2 + i*0.1, v + 0.04), (0.2 + i*0.1, v + h - 0.02)], T2, 0.5)
    k.line([(0.16, 0.44), (0.84, 0.44)], T, 1.0)
    k.solid(k.ell(0.5, 0.24, 0.1, 0.02), T2, 0.7)
    k.line([(0.5, 0.0), (0.5, 0.16)], R, 0.9); k.solid([(0.47, 0.13), (0.5, 0.18), (0.53, 0.13)], R, 0.7)
    for i in range(5): k.dot((0.86 + i*0.025, 0.56 + i*0.02), 0.7, T2)

# ---------------------------------------------------------------- 3 x 3
def mixeur(k):
    arbre(k, (0.5, 0.0), (0.5, 0.08)); cog(k, 0.5, 0.08, 0.1)
    carter(k, 0.3, 0.14, 0.7, 0.36)
    k.solid(k.rect(0.46, 0.36, 0.54, 0.62))                                                    # axe télescopique
    for v in (0.42, 0.5): k.line([(0.46, v), (0.54, v)], T2, 0.5)
    for s in (-1, 1): k.line(bez((0.5, 0.6), (0.5 + s*0.26, 0.62), (0.5 + s*0.24, 0.86), (0.5, 0.88)), T, 1.6)
    for s in (-1, 1): k.line(bez((0.5, 0.6), (0.5 + s*0.13, 0.64), (0.5 + s*0.12, 0.84), (0.5, 0.88)), T2, 1.0)
    k.line([(0.16, 0.66), (0.16, 0.96), (0.84, 0.96), (0.84, 0.66)], T, 1.6)                     # bassin (coupe)
    k.line(bez((0.22, 0.8), (0.36, 0.78), (0.64, 0.82), (0.78, 0.8)), R, 0.8)
    for s in (-1, 1): k.solid([(0.5 + s*0.32, 0.7), (0.5 + s*0.34, 0.7), (0.5 + s*0.34, 0.96), (0.5 + s*0.32, 0.96)], T2, 0.6)
    for s in (-1, 1): k.line(k.ell(0.5, 0.71, 0.24, 0.04, 200 if s < 0 else 20, 250 if s < 0 else 70), R, 0.8)
    k.solid(k.rect(0.12, 0.96, 0.88, 1.0), T, 0.8)

def concasseur(k):
    for (u, sens) in ((0.28, 1), (0.72, -1)):
        k.solid(k.cer(u, 0.56, 0.22)); k.closed(k.cer(u, 0.56, 0.16), T2, 0.6)
        for i in range(20):                                                                     # stries de la jante
            a = 2*math.pi*i/20
            k.line([(u + math.cos(a)*0.17, 0.56 + math.sin(a)*0.17*k.k), (u + math.cos(a)*0.215, 0.56 + math.sin(a)*0.215*k.k)], T2, 0.6)
        k.solid(k.rect(u - 0.04, 0.56 - 0.04*k.k, u + 0.04, 0.56 + 0.04*k.k))
        k.line(k.ell(u, 0.56, 0.27, 0.27, 210 if sens > 0 else 270, 300 if sens > 0 else 330), R, 0.9)
    for i in range(4):                                                                          # minerai entrant et sortant
        k.solid(k.rect(0.47 + (i % 2)*0.02, 0.08 + i*0.06, 0.53 + (i % 2)*0.02, 0.12 + i*0.06), T, 0.7)
    for i in range(6): k.dot((0.46 + (i % 3)*0.04, 0.86 + (i // 3)*0.05), 0.9, T2)
    k.line([(0.5, 0.36), (0.5, 0.42)], R, 0.8); k.solid([(0.48, 0.41), (0.5, 0.45), (0.52, 0.41)], R, 0.6)

def presse_create(k):
    sol(k, 0.96)
    arbre(k, (0.0, 0.2), (1.0, 0.2))
    carter(k, 0.26, 0.06, 0.74, 0.36)
    cog(k, 0.86, 0.2, 0.09)
    k.solid(k.rect(0.45, 0.36, 0.55, 0.58)); k.line([(0.5, 0.36), (0.5, 0.58)], T3, 0.5)
    k.solid(k.rect(0.3, 0.58, 0.7, 0.66)); k.hatch(k.rect(0.31, 0.6, 0.69, 0.66))
    k.solid(k.rect(0.32, 0.7, 0.68, 0.73), R, 0.9)
    k.solid(k.rect(0.24, 0.73, 0.76, 0.96)); k.line([(0.24, 0.78), (0.76, 0.78)], T2, 0.6)     # dépôt
    for u in (0.28, 0.72): k.line([(u, 0.8), (u, 0.92)], T3, 0.5)

def foreuse_create(k):
    k.axe((0.0, 0.5), (1.0, 0.5))
    arbre(k, (0.0, 0.5), (0.16, 0.5))
    carter(k, 0.14, 0.24, 0.46, 0.76)
    cone = [(0.46, 0.28), (0.46, 0.72), (0.96, 0.5)]
    k.solid(cone)
    for i in range(7):                                                                          # spirale de la mèche
        u0 = 0.48 + i*0.068; h0 = 0.22*(1 - (u0 - 0.46)/0.5); h1 = 0.22*(1 - (u0 + 0.06 - 0.46)/0.5)
        k.line(bez((u0, 0.5 - h0), (u0 + 0.03, 0.5 - h0*0.3), (u0 + 0.03, 0.5 + h1*0.3), (u0 + 0.06, 0.5 + h1)), T2, 0.8)
    k.solid(k.rect(0.44, 0.26, 0.5, 0.74), T, 0.8)
    for i in range(6): k.dot((0.98 - (i % 2)*0.01, 0.42 + i*0.03), 0.7, R)
