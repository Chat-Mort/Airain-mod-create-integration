p='textes.py'; s=open(p).read()
s=s.replace(''' "airain.chronique.j.fin_echo":''',''' "airain.chronique.j.archiviste": ("Tous les écrits du monde sont rassemblés. Les archives sont complètes.", "Every writing in the world has been gathered. The archives are complete."),
 "airain.chronique.j.fin_echo":''')
s=s.replace('''"gardien_cieux": (''','''"station": ("La station d'observation", "The observation station",
 "Sur une île volante, la coupole où Octave Lanfrey regardait le ciel. Ses relevés disent qu'il a vu la lumière des Réfractaires monter vers le nord, la nuit où ils ont fui, et qu'il s'est tu. Ses dernières lignes : il redescendait préparer deux capsules qui ne mènent nulle part.",
 "On a floating island, the dome where Octave Lanfrey watched the sky. His readings say he saw the Refractories' light rise to the north the night they fled, and kept silent. His last lines: he was going down to prepare two capsules that lead nowhere.",
 "Passer le portail de l'End : la lumière violette menait là.",
 "Go through the End portal: the violet light led there."),
"gardien_cieux": (''')
open(p,'w').write(s)
