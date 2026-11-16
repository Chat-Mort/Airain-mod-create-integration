exec(open('base3d.py').read())
import nbtlib, glob
D='/home/claude/airain-mod-create-integration/src/main/resources/assets/airain/ponder/'
TEX={'smooth_stone':'minecraft:block/smooth_stone','fire_bricks':'airain:block/fire_bricks','blast_furnace_taphole':'airain:block/blast_furnace_taphole','airain_grate':'airain:block/airain_grate',
 'blast_furnace_tuyere':'airain:block/blast_furnace_tuyere','blast_furnace_hopper':'airain:block/blast_furnace_hopper_top','blaze_burner':'minecraft:block/orange_concrete','bricks':'minecraft:block/bricks'}
ims=[]
for n in ('haut_fourneau','telepherique','tableau_emaille','rayonnage','monte_charge'):
    f=nbtlib.load(D+n+'.nbt'); pal=[p['Name'].split(':')[1] for p in f['palette']]; E=[]
    for bl in f['blocks']:
        x,y,z=[int(v) for v in bl['pos']]; nm=pal[int(bl['state'])]
        t=TEX.get(nm,'minecraft:block/light_blue_concrete' if 'create' in str(f['palette'][int(bl['state'])]['Name']) else 'minecraft:block/yellow_concrete')
        E.append(b((x*16,y*16,z*16),(x*16+16,y*16+16,z*16+16),t))
    im=vue(E,[-0.5,0.6,-1],600); ims.append(im.crop(im.getbbox()))
W=sum(i.width for i in ims)+20*len(ims); H=max(i.height for i in ims)+20
o=Image.new('RGBA',(W,H),(34,30,38,255)); x=10
for i in ims: o.alpha_composite(i,(x,10)); x+=i.width+20
o.save('verif_schemas.png'); print(o.size)
