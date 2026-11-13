import sys; sys.path.insert(0,'/tmp/claude-0/-home-claude/c0fedc50-c1fd-5e3d-b135-6ac1b8100b13/scratchpad')
src=open('rendu_vitrine.py').read().split('def vitrine')[0]
exec(src)
def objets(pre):
    b=lambda n:'t:block/'+pre+n
    L=b('airain_lantern'); C=b('airain_chain')
    return [
     ("Airain",[cube((0,0,0),b('airain_block'))]),
     ("Airain taillé",[cube((0,0,0),b('cut_airain'))]),
     ("Airain riveté",[cube((0,0,0),b('riveted_airain'))]),
     ("Airain ciselé",[cube((0,0,0),b('chiseled_airain'))]),
     ("Pilier",[cube((0,0,0),b('airain_pillar'),b('airain_pillar_top')),cube((0,1,0),b('airain_pillar'),b('airain_pillar_top'))]),
     ("Grille",[cube((0,0,0),b('airain_grate'))]),
     ("Escaliers",[el((0,0,0),[0,0,0],[16,8,16],b('airain_block')),el((0,0,0),[0,8,8],[16,16,16],b('airain_block'))]),
     ("Dalle taillée",[el((0,0,0),[0,0,0],[16,8,16],b('cut_airain'))]),
     ("Porte",[el((0,0,0),[0,0,0],[16,16,3],b("airain_door_bottom"),uvs=[0,0,16,16]),el((0,1,0),[0,0,0],[16,16,3],b("airain_door_top"),uvs=[0,0,16,16])]),
     ("Trappe",[el((0,0,0),[0,0,0],[16,3,16],b('airain_trapdoor'),uvs={"up":[0,0,16,16],"down":[0,0,16,16],"north":[0,0,16,3],"south":[0,0,16,3],"east":[0,0,16,3],"west":[0,0,16,3]})]),
     ("Barreaux",[el((0,y,0),[0,0,7],[16,16,9],b('airain_bars'),faces=("north","south"),uvs=[0,0,16,16]) for y in (0,1)]),
     ("Chaîne et lanterne",[el((0,1,0),[6.5,0,8],[9.5,16,8],C,faces=("north","south"),uvs=[0,0,3,16],rot=([8,8,8],'y',45)),
                            el((0,1,0),[8,0,6.5],[8,16,9.5],C,faces=("east","west"),uvs=[3,0,6,16],rot=([8,8,8],'y',45)),
                            el((0,0,0),[5,6,5],[11,13,11],L,uvs={"north":[0,2,6,9],"south":[0,2,6,9],"east":[0,2,6,9],"west":[0,2,6,9],"up":[0,9,6,15],"down":[0,9,6,15]}),
                            el((0,0,0),[6,13,6],[10,15,10],L,uvs={"north":[1,0,5,2],"south":[1,0,5,2],"east":[1,0,5,2],"west":[1,0,5,2],"up":[1,10,5,14],"down":[1,10,5,14]})]),
    ]
pre=sys.argv[2] if len(sys.argv)>2 else ''
rm.EYE=norm([-1,0.82,-1]); rm.F=-rm.EYE; rm.R=norm(np.cross(rm.F,[0,1,0])); rm.U=np.cross(rm.R,rm.F)
O=objets(pre); C=6; Tl=260
W=Image.new('RGBA',(C*Tl,2*(Tl+40)),(34,30,38,255)); d=ImageDraw.Draw(W); f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
for i,(n,E) in enumerate(O):
    # centrer verticalement les objets de 2 blocs : on les décale d'un demi-bloc
    haut=max(e['to'][1] for e in E)>16
    if haut:
        for e in E:
            e['from'][1]-=8; e['to'][1]-=8
            if 'rotation' in e: e['rotation']['origin'][1]-=8
    im=rendre(E,{},Tl,echelle=5.2 if haut else 7.5)
    x=(i%C)*Tl; y=(i//C)*(Tl+40)
    W.alpha_composite(im,(x,y+34)); d.text((x+Tl/2,y+16),n,font=f,fill=(235,215,170),anchor='mm')
W.save(sys.argv[1])
