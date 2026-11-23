# Installe les sprites génériques et regrave les empreintes des fonds (fourneaux, alambic).
import generiques
D = '/home/claude/airain-mod-create-integration/src/main/resources/resourcepacks/interface_hd/assets/minecraft/textures/gui/'
r = generiques.tout()
f = generiques.fonds(r)            # à partir des fonds actuels, avant d'écrire quoi que ce soit
for k, im in r.items(): im.save(D + 'sprites/' + k + '.png')
for k, im in f.items(): im.save(D + 'container/' + k + '.png')
print(len(r), 'sprites,', len(f), 'fonds')
