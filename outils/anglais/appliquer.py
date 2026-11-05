import os, re, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from carte import *
MOD = '/home/claude/airain-mod-create-integration/src/main'
R = MOD + '/resources'
A = R + '/assets/airain'
D = R + '/data/airain'

def mv(a, b):
    if os.path.exists(a) and a != b:
        assert not os.path.exists(b), b
        subprocess.run(['git', '-C', '/home/claude/airain-mod-create-integration', 'mv', a, b], check=True)

def renommer_dossier(dossier, carte, ext):
    if not os.path.isdir(dossier): return
    for f in sorted(os.listdir(dossier)):
        base, e = os.path.splitext(f)
        if e == ext and base in carte: mv(f'{dossier}/{f}', f'{dossier}/{carte[base]}{ext}')

# ---- 1. fichiers
renommer_dossier(A + '/textures/item', IDS, '.png')
renommer_dossier(A + '/textures/block', {**IDS, **TEX_BLOC}, '.png')
renommer_dossier(A + '/textures/entity', TEX_ENTITE, '.png')
renommer_dossier(A + '/textures/entity/etendard', TEX_ETENDARD, '.png')
mv(A + '/textures/entity/etendard', A + '/textures/entity/standard')
renommer_dossier(A + '/textures/gui', TEX_GUI, '.png')
renommer_dossier(A + '/textures/models/armor', TEX_ARMURE, '.png')
renommer_dossier(A + '/textures/painting', TEX_TABLEAU, '.png')
renommer_dossier(A + '/models/item', IDS, '.json')
for sous in ('banc_entretien', 'desenchanteur'):
    renommer_dossier(f'{A}/models/block/{sous}', MODELE_BLOC, '.json')
    mv(f'{A}/models/block/{sous}', f'{A}/models/block/{IDS[sous]}')
renommer_dossier(A + '/models/block', {**IDS, **MODELE_BLOC}, '.json')
renommer_dossier(A + '/blockstates', IDS, '.json')
renommer_dossier(D + '/loot_table/blocks', IDS, '.json')
renommer_dossier(D + '/loot_table/entities', IDS, '.json')
renommer_dossier(D + '/recipe', IDS, '.json')

# ---- 2. texte
SEG = {**IDS, **TEX_BLOC, **MODELE_BLOC}
def chemin_ressource(m):          # airain:item/x, airain:block/a/b
    gen, chemin = m.group(1), m.group(2)
    segs = chemin.split('/')
    carte = IDS if gen == 'item' else SEG
    return f'airain:{gen}/' + '/'.join(carte.get(s, s) for s in segs)
TEX = {'item': IDS, 'block': {**IDS, **TEX_BLOC}, 'entity': TEX_ENTITE, 'entity/etendard': TEX_ETENDARD, 'gui': TEX_GUI,
       'models/armor': TEX_ARMURE, 'painting': TEX_TABLEAU}
def chemin_texture(m):
    d, n = m.group(1), m.group(2)
    nd = 'entity/standard' if d == 'entity/etendard' else d
    return f'textures/{nd}/{TEX[d].get(n, n)}.png'
def ident(m):
    return 'airain:' + IDS.get(m.group(1), m.group(1))
def cle(m):
    return f'{m.group(1)}.airain.' + IDS.get(m.group(2), m.group(2))

def traduire(s, java=False):
    s = re.sub(r'airain:(item|block)/([a-z0-9_/]+)', chemin_ressource, s)
    s = re.sub(r'textures/(item|block|entity/etendard|entity|gui|models/armor|painting)/([a-z0-9_]+)\.png', chemin_texture, s)
    s = re.sub(r'(?<![#\w])airain:([a-z0-9_]+)(?![a-z0-9_/])', ident, s)
    s = re.sub(r'\b(item|block|entity)\.airain\.([a-z0-9_]+)', cle, s)
    s = re.sub(r'"asset_id": "airain:([a-z0-9_]+)"', lambda m: f'"asset_id": "airain:{TEX_TABLEAU.get(m.group(1), m.group(1))}"', s)
    if java:
        s = re.sub(r'\b(register|armure|arme|armeEcho|armeArcanique|armureEcho|armureArcanique|pioche|build)\("([a-z0-9_]+)"',
                   lambda m: f'{m.group(1)}("{IDS.get(m.group(2), m.group(2))}"', s)
        s = re.sub(r'(MATERIAUX\.register\(|materiau\(|materiauArmure\()"([a-z_]+)"', lambda m: f'{m.group(1)}"{MATERIAUX.get(m.group(2), m.group(2))}"', s)
    return s

def parcourir(racine, exts, java=False):
    n = 0
    for d, _, fs in os.walk(racine):
        if '/.git' in d or '/build' in d: continue
        for f in fs:
            if not f.endswith(exts): continue
            p = os.path.join(d, f)
            try: s = open(p, encoding='utf-8').read()
            except UnicodeDecodeError: continue
            t = traduire(s, java and f.endswith('.java'))
            if t != s: open(p, 'w', encoding='utf-8').write(t); n += 1
    return n

if __name__ == '__main__':
    print('mod :', parcourir(MOD, ('.java', '.json', '.mcmeta', '.toml'), java=True))
