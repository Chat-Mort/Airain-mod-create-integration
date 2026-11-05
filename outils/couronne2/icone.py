from PIL import Image
T=(0,0,0,0)
P={'.':T,
 'k':(40,22,10,255),   # contour
 'd':(96,58,18,255),'m':(150,98,32,255),'l':(198,146,56,255),'h':(240,208,128,255),'w':(255,240,190,255),
 'r':(150,20,28,255),'R':(220,60,60,255),'v':(40,120,104,255),'V':(90,190,160,255),
 'f':(56,58,64,255),'g':(130,200,215,255),'G':(220,245,250,255),'o':(176,120,36,255),'O':(226,176,70,255)}
A=[
"................",
".......kk.......",
"......khwk......",
"..k...klhk...k..",
".khk..kRRk..khk.",
".klk.kkrRkk.klk.",
".kmlkkhrrlkkmlk.",
".kmmlhlllllhmmk.",
"kkkkkkkkkkkkkkkk",
"kowhllllllllhwok",
"kOkmlVmmmmVmlkOk",
"kdkdkdkdkdkdkdkd",
"OkkGgkkkkkkkkkkO",
"kOkgkk....kfOkO.",
".kOkk......kOk..",
"..kk........kk..",
]
im=Image.new('RGBA',(16,16))
for y,row in enumerate(A):
    for x,ch in enumerate(row): im.putpixel((x,y),P[ch])
im.save('couronne_icone_brouillon.png')
