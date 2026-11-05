#!/bin/bash
# Prépare les musiques : sources dans musique_in/, sortie dans le pack. Volume -19 LUFS, fondu d'entrée de 2,5 s.
# usage : musique_audio.sh <dossier du pack>
H=$(dirname "$(readlink -f "$0")"); O="$1/kubejs/assets/kubejs/sounds/music"; mkdir -p "$O"
for f in "$H"/musique_in/*.ogg; do
  n=$(basename "$f")
  ffmpeg -hide_banner -loglevel error -y -i "$f" -af "afade=t=in:st=0:d=2.5,loudnorm=I=-19:TP=-1.5:LRA=11" -ar 44100 -c:a libvorbis -q:a 6 "$O/$n" && echo "$n"
done
# thèmes de l'histoire (joués par le mod à des moments précis, pas dans les listes du jeu)
for f in "$H"/themes_in/*.ogg; do
  n=$(basename "$f")
  ffmpeg -hide_banner -loglevel error -y -i "$f" -af "afade=t=in:st=0:d=2.5,loudnorm=I=-19:TP=-1.5:LRA=11" -ar 44100 -c:a libvorbis -q:a 6 "$O/$n" && echo "$n (thème)"
done
