p='textes.py'; s=open(p).read()
rep=[
("Nous nous sommes réveillés au Laboratoire 7, sans un souvenir. Une lampe grésillait, une horloge s'était arrêtée. Sur la table, le carnet d'un ingénieur racontait ce qui s'était passé ici, à moitié.",
 "Nous nous sommes réveillés au Laboratoire 7, sans un souvenir. Une lampe grésillait, une horloge s'était arrêtée. Sur la table, le carnet d'Octave Lanfrey, l'ingénieur en chef : nous étions ses apprentis, endormis à part, trois siècles plus tôt. Il voulait que nous nous réveillions sans rien devoir à l'Empire."),
("We woke in Laboratory 7 with no memory. A lamp crackled, a clock had stopped. On the table, an engineer's notebook told half of what had happened here.",
 "We woke in Laboratory 7 with no memory. A lamp crackled, a clock had stopped. On the table lay the journal of Octave Lanfrey, the Engineer-in-Chief: we were his apprentices, put to sleep apart, three centuries ago. He wanted us to wake owing the Empire nothing."),
("Le Cœur bat de nouveau entre nos mains. Il chauffe. Très loin sous nos pieds, quelque chose a répondu. Le carnet s'est ouvert tout seul à une page blanche, et des lettres s'y sont gravées.",
 "Le Cœur bat de nouveau entre nos mains. Très loin sous nos pieds, quelque chose a répondu. Le carnet s'est ouvert à une page blanche : l'Empire nous remerciait d'avoir été ses mains. Dessous, de l'écriture d'Octave : « Ils ne dorment pas : ils brûlent. Quand tout sera fini, c'est vous qui choisirez. »"),
("The Heart beats again in our hands. It is warm. Far beneath our feet, something answered. The notebook opened by itself to a blank page, and letters burned into it.",
 'The Heart beats again in our hands. Far beneath our feet, something answered. The journal opened to a blank page: the Empire thanked us for being its hands. Below, in Octave\'s handwriting: \\"They are not sleeping: they are burning. When it is all over, you will be the ones to choose.\\"'),
("L'usine ancienne, là où les premières machines ont été forgées. Au centre, une machine immense dort encore. Il lui faut une étincelle.",
 "L'usine ancienne, là où Auguste Ferrand, le fondateur, a forgé ses premières machines. Le Conseil l'avait caché : il s'y est transféré seul, bien avant tout le monde. Au centre, sa machine dort encore. Il lui faut une étincelle."),
("The ancient factory, where the first machines were forged. At its center, a huge machine still sleeps. It needs a spark.",
 "The ancient factory, where Auguste Ferrand, the founder, forged his first machines. The Council had hidden it: he transferred himself there, alone, long before anyone else. At its center, his machine still sleeps. It needs a spark."),
("L'Empereur, fusionné avec ce qu'il avait construit, est tombé.","Auguste Ferrand, l'Empereur, fusionné avec ce qu'il avait construit, est tombé."),
("The Emperor, fused with what he had built, has fallen.","Auguste Ferrand, the Emperor, fused with what he had built, has fallen."),
]
for a,b in rep:
    assert a in s, a[:40]; s=s.replace(a,b)
open(p,'w').write(s)
