"""Insère les captures (CAPTURE_<clé>, dossier assets/captures) et les illustrations 3D
(ILLU_<clé>, dossier assets/illustrations_3d) dans les emplacements du deck.

Usage :
    python3 insert_screenshots.py [deck.pptx] [dossier_captures] [sortie.pptx]
Par défaut : ../livrables/MAOUSANG_PITCH_DECK.pptx, ../assets/captures,
et la sortie remplace le deck d'origine.
Une capture absente laisse l'emplacement en place.
"""
import os
import sys

from PIL import Image
from pptx import Presentation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
deck = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "livrables", "MAOUSANG_PITCH_DECK.pptx")
caps = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "assets", "captures")
out = sys.argv[3] if len(sys.argv) > 3 else deck
ill = os.path.join(ROOT, "assets", "illustrations_3d")
PREFIX = {"CAPTURE_": caps, "ILLU_": ill}

prs = Presentation(deck)
done, missing = [], set()
for slide in prs.slides:
    for shp in list(slide.shapes):
        pre = next((x for x in PREFIX if shp.name.startswith(x)), None)
        if not pre:
            continue
        key, folder = shp.name[len(pre):], PREFIX[pre]
        img = next((os.path.join(folder, key + e) for e in (".png", ".jpg", ".jpeg")
                    if os.path.exists(os.path.join(folder, key + e))), None)
        if not img:
            missing.add(key)
            continue
        iw, ih = Image.open(img).size
        bw, bh = shp.width, shp.height
        scale = min(bw / iw, bh / ih)
        w, h = int(iw * scale), int(ih * scale)
        x, y = shp.left + (bw - w) // 2, shp.top + (bh - h) // 2
        pic = slide.shapes.add_picture(img, x, y, w, h)
        pic.name = f"SCREEN_{key}"
        shp._element.getparent().remove(shp._element)
        done.append(key)
prs.save(out)
print(f"{len(done)} capture(s) insérée(s) dans {out}")
if missing:
    print("Captures manquantes :", ", ".join(sorted(missing)))
