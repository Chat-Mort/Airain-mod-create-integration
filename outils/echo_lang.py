#!/usr/bin/env python3
"""Ars Nouveau : la « Source » devient l'« Écho » (lore de l'Empire d'Airain). Écrit des traductions qui remplacent celles du mod.
usage : echo_lang.py <dossier du pack>"""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
en = json.load(open(os.path.join(H, "ars_lang/en_us.json")))
fr = json.load(open(os.path.join(H, "ars_lang/fr_fr.json")))
def en_echo(v):
    v = v.replace("Sourcestone", "Echostone").replace("sourcestone", "echostone")
    v = v.replace("Sourcelink", "Echolink").replace("sourcelink", "echolink")
    v = v.replace("Sourceberry", "Echoberry").replace("sourceberry", "echoberry")
    v = re.sub(r"\bSource\b", "Echo", v); v = re.sub(r"\bsource\b", "echo", v)
    return v
def fr_echo(v):
    v = re.sub(r"[Pp]ierre de source", "Pierre d'Écho", v)
    v = re.sub(r"\b(de la|de|du) [Ss]ource\b", "d'Écho", v)
    v = re.sub(r"\bla [Ss]ource\b", "l'Écho", v)
    v = re.sub(r"\ben [Ss]ource\b", "en Écho", v)
    v = re.sub(r"\b(Pot|Gemme|Relais|Lien|gemme|pot|relais|lien|baies|Baies) [Ss]ource\b", r"\1 d'Écho", v)
    v = re.sub(r"\b[Ss]ource\b", "Écho", v)
    v = re.sub(r"\b(une|la) Écho\b", "de l'Écho", v).replace("de de l'Écho", "de l'Écho")
    # textes restés en anglais dans la traduction d'Ars Nouveau
    v = v.replace("Sourcestone", "Pierre d'Écho").replace("Sourcelink", "Lien d'Écho").replace("Sourceberry", "Baie d'Écho")
    return v
out_en, out_fr = {}, {}
for k, v in en.items():
    if isinstance(v, str) and re.search(r"[Ss]ource", v):
        out_en[k] = en_echo(v)
        base = fr.get(k)
        out_fr[k] = fr_echo(base) if isinstance(base, str) else en_echo(v)
d = os.path.join(sys.argv[1], "kubejs/assets/ars_nouveau/lang"); os.makedirs(d, exist_ok=True)
json.dump(out_en, open(os.path.join(d, "en_us.json"), "w"), indent=1, ensure_ascii=False)
json.dump(out_fr, open(os.path.join(d, "fr_fr.json"), "w"), indent=1, ensure_ascii=False)
print(len(out_en), "textes renommés")
for k in ("item.ars_nouveau.source_gem", "block.ars_nouveau.source_jar", "block.ars_nouveau.sourcestone", "block.ars_nouveau.relay", "block.ars_nouveau.sourceberry_bush", "block.ars_nouveau.agronomic_sourcelink"):
    print(k, "|", out_en.get(k), "|", out_fr.get(k))
