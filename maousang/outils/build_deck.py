"""Construit MAOUSANG_PITCH_DECK.pptx (python-pptx) et MAOUSANG_SPEAKER_NOTES.md.

Formes, tableaux et graphiques sont natifs et modifiables dans PowerPoint.
Les emplacements de captures d'écran sont des formes nommées CAPTURE_<clé> :
outils/insert_screenshots.py les remplace par les vraies captures.
"""
import json
import os
import sys

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ILL = os.path.join(ROOT, "assets", "illustrations")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "livrables", "MAOUSANG_PITCH_DECK.pptx")
NOTES_MD = os.path.join(ROOT, "livrables", "MAOUSANG_SPEAKER_NOTES.md")
M = json.load(open(os.path.join(ROOT, "outils", "model_values.json")))
I, P, A = M["Intermediaire"], M["Prudent"], M["Ambitieux"]


def rgb(h):
    return RGBColor.from_string(h)


DARK, TEAL, MINT, AMBER = "14213D", "2A51A3", "6F8FD6", "F78E20"
LIGHT, GRAY, MID, WHITE, NAVY2 = "EEF2FA", "4A5568", "D6E0F7", "FFFFFF", "1E2E52"
GREEN = "00A887"
FONT = "Montserrat"  # police du modèle SANIA


def fr(x, d=0):
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s


def mfcfa(x, d=1):
    return f"{fr(x / 1e6, d)} M"


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
NOTES = []


# ------------------------------------------------------------------ helpers
def bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = rgb(color)


def text(slide, x, y, w, h, content, size=14, bold=False, color=DARK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, italic=False, name=None, spacing=None):
    """content : str, ou liste de paragraphes ; un paragraphe = str ou liste de (texte, {opts})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0)
    tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing:
            p.space_after = Pt(spacing)
        runs = para if isinstance(para, list) else [(para, {})]
        for item in runs:
            t, o = (item, {}) if isinstance(item, str) else item
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = FONT
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = rgb(o.get("color", color))
            if o.get("spc"):
                f._rPr.set("spc", str(o["spc"]))
            if o.get("strike"):
                f._rPr.set("strike", "sngStrike")
    return tb


def shape(slide, kind, x, y, w, h, fill=None, line=None, lw=1, name=None, radius=None, dash=False):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = rgb(line)
        s.line.width = Pt(lw)
        if dash:
            s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    return s


def card(slide, x, y, w, h, fill=WHITE, line=MID, radius=0.08):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, line=line, lw=0.75, radius=radius)


def icon(slide, name, x, y, d, circle=TEAL, col="w", ring=None):
    """Icône dans un cercle coloré (motif visuel du deck)."""
    if circle:
        shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill=circle, line=ring, lw=1.5)
        pad = d * 0.24
        slide.shapes.add_picture(os.path.join(ILL, f"icon_{name}_{col}.png"),
                                 Inches(x + pad), Inches(y + pad), Inches(d - 2 * pad), Inches(d - 2 * pad))
    else:
        slide.shapes.add_picture(os.path.join(ILL, f"icon_{name}_{col}.png"), Inches(x), Inches(y), Inches(d), Inches(d))


def picture(slide, file, x, y, w=None, h=None):
    return slide.shapes.add_picture(os.path.join(ILL, file), Inches(x), Inches(y),
                                    Inches(w) if w else None, Inches(h) if h else None)


def line(slide, x1, y1, x2, y2, color=MID, w=1.5, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(w)
    if dash:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return c


def phone(slide, key, label, x, y, w=1.75, h=3.5):
    """Cadre de smartphone + emplacement nommé pour une capture réelle."""
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=DARK, radius=0.12)
    inner = shape(slide, MSO_SHAPE.RECTANGLE, x + 0.09, y + 0.22, w - 0.18, h - 0.4, fill="F8FAFC",
                  line="94A3B8", lw=1, dash=True, name=f"CAPTURE_{key}")
    tf = inner.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.06)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Capture à insérer"
    r.font.size, r.font.bold, r.font.name = Pt(10), True, FONT
    r.font.color.rgb = rgb(GRAY)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = label
    r2.font.size, r2.font.name = Pt(10), FONT
    r2.font.color.rgb = rgb(TEAL)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x + w / 2 - 0.25, y + 0.08, 0.5, 0.06, fill="334155", radius=0.5)


def header(slide, title, msg=None, dark=False):
    text(slide, 0.6, 0.38, 12.1, 0.7, title, size=34, bold=True, color=WHITE if dark else DARK)
    if msg:
        text(slide, 0.6, 1.08, 12.1, 0.45, msg, size=15, color=MINT if dark else TEAL)


def footer(slide, n, source=None, dark=False):
    col = "94A3B8" if dark else GRAY
    if source:
        text(slide, 0.6, 6.98, 10.6, 0.35, source, size=9, color=col)
    text(slide, 11.4, 7.0, 1.33, 0.3, f"MAOUSANG  ·  {n}", size=9, color=col, align=PP_ALIGN.RIGHT, bold=True)


def new_slide(color=WHITE):
    s = prs.slides.add_slide(BLANK)
    bg(s, color)
    return s


def notes(slide, title, txt):
    slide.notes_slide.notes_text_frame.text = txt
    NOTES.append((title, txt))


def chart_style(ch, legend=True, size=10):
    ch.font.name = FONT
    ch.font.size = Pt(size)
    ch.font.color.rgb = rgb(GRAY)
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(size)


def table(slide, x, y, w, h, data, colw, head=TEAL, size=11, first_bold=True, zebra=True):
    rows, cols = len(data), len(data[0])
    gt = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    t = gt.table
    for j, cw in enumerate(colw):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = str(val)
            r.font.name = FONT
            r.font.size = Pt(size)
            if i == 0:
                r.font.bold = True
                r.font.color.rgb = rgb(WHITE)
                c.fill.solid()
                c.fill.fore_color.rgb = rgb(head)
            else:
                r.font.color.rgb = rgb(DARK)
                r.font.bold = first_bold and j == 0
                c.fill.solid()
                c.fill.fore_color.rgb = rgb("F1F5F9" if (zebra and i % 2 == 0) else WHITE)
    return t


# =================================================================== SLIDES
# 1 — Couverture (mise en page du modèle SANIA) ---------------------------
s = new_slide(DARK)
picture(s, "pixel_chad.png", 8.6, 0.55, h=4.9)
text(s, 0.89, 1.8, 8.23, 0.3, "PITCH INVESTISSEURS · MAOUSANG · NOVEMBRE 2026", size=14, bold=True, color="9DB4E8",
     **{})
s.shapes[-1].text_frame.paragraphs[0].runs[0].font._rPr.set("spc", "200")
text(s, 0.76, 2.64, 8.0, 2.3, ["Tous vos services", "dans une seule app"], size=56, bold=True, color=WHITE)
for i, col in enumerate(["6F8FD6", GREEN, AMBER]):
    shape(s, MSO_SHAPE.RECTANGLE, 0.89 + i * 0.67, 4.97, 0.67, 0.08, fill=col)
text(s, 0.89, 5.33, 8.23, 0.45, "Mobilité, billetterie, immobilier et aide à l'emploi au Tchad", size=20, color="D6E0F7")
text(s, 0.89, 6.46, 6.44, 0.32, "Giscard Destin · Fondateur de Maousang", size=16, bold=True, color=WHITE)
card(s, 8.95, 5.9, 3.75, 1.05, fill=WHITE, line=None, radius=0.12)
picture(s, "maousang_logo.png", 9.15, 6.08, w=3.35)
notes(s, "1. Couverture",
      "Bonjour à toutes et à tous. Je m'appelle Giscard Destin. Je suis ingénieur en intelligence artificielle et "
      "data scientist, et je suis le fondateur de Maousang. Maousang est une plateforme numérique multiservices, "
      "déjà développée et en ligne sur maousang.vercel.app. En une phrase : nous réunissons dans une seule "
      "application les services dont les Tchadiens ont besoin chaque jour : se déplacer, voyager, trouver un "
      "emploi et trouver un logement. Dans les dix prochaines minutes, je vais vous montrer le problème, notre "
      "solution, notre marché, notre modèle économique et ce que nous attendons de vous.")

# 2 — Maousang en bref -----------------------------------------------------
s = new_slide()
header(s, "Maousang en bref", "Un seul environnement digital pour plusieurs services essentiels")
card(s, 0.6, 1.75, 6.0, 1.55, fill=LIGHT, line=None)
text(s, 0.85, 1.9, 5.5, 1.3, [[("Mission  ", {"bold": True, "color": TEAL})],
                              "Connecter les populations, les entreprises, les prestataires et les organisations "
                              "grâce à des solutions numériques simples, accessibles et intelligentes."], size=14, spacing=4)
card(s, 0.6, 3.45, 6.0, 1.75, fill=DARK, line=None)
text(s, 0.85, 3.6, 5.5, 1.5, [[("Vision  ", {"bold": True, "color": AMBER})],
                              [("« Devenir une plateforme de référence pour l'accès aux services numériques au Tchad, "
                                "avec une expansion en Afrique centrale, en rapprochant les populations des opportunités, "
                                "des services et des acteurs économiques. »", {"italic": True, "color": WHITE})]], size=14, spacing=4)
facts = [("Fondateur", "Giscard Destin, ingénieur IA et data scientist"),
         ("Statut", "Plateforme développée et mise en production"),
         ("Marché de départ", "N'Djaména, puis grandes villes du Tchad")]
for i, (k, v) in enumerate(facts):
    y = 5.4 + i * 0.47
    text(s, 0.6, y, 1.9, 0.4, k, size=13, bold=True, color=TEAL)
    text(s, 2.5, y, 4.1, 0.4, v, size=13)
# Écosystème (moyeu)
cx, cy, R = 9.9, 4.25, 2.05
poles = [("ticket", "Billetterie", TEAL), ("moto", "Mobilité – Clando", TEAL), ("briefcase", "Emploi et ATS", TEAL),
         ("home", "Immobilier", TEAL), ("cart", "Commerce", "94A3B8"), ("plane", "Billetterie internationale", "94A3B8")]
import math
for i, (ic, lab, col) in enumerate(poles):
    ang = math.radians(-90 + i * 60)
    px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
    line(s, cx, cy, px, py, color=MID, w=1.5, dash=(col != TEAL))
for i, (ic, lab, col) in enumerate(poles):
    ang = math.radians(-90 + i * 60)
    px, py = cx + R * math.cos(ang), cy + R * math.sin(ang)
    icon(s, ic, px - 0.42, py - 0.42, 0.84, circle=col)
    ly = py + 0.47 if math.sin(ang) >= -0.1 else py - 0.78
    text(s, px - 1.1, ly, 2.2, 0.32, lab, size=12, bold=True, align=PP_ALIGN.CENTER, color=DARK if col == TEAL else GRAY)
shape(s, MSO_SHAPE.OVAL, cx - 0.85, cy - 0.85, 1.7, 1.7, fill=DARK)
text(s, cx - 0.85, cy - 0.32, 1.7, 0.4, "MAOUSANG", size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
text(s, cx - 0.85, cy + 0.05, 1.7, 0.4, "Annonces · Assistant IA", size=9, color=MINT, align=PP_ALIGN.CENTER)
footer(s, 2, "Schéma : cercles verts = pôles développés ; cercles gris et traits pointillés = pôles de la phase 2.")
notes(s, "2. Maousang en bref",
      "Notre mission est simple : connecter les populations, les entreprises, les prestataires et les organisations "
      "grâce à des outils numériques simples et accessibles. Notre vision : devenir la plateforme de référence pour "
      "l'accès aux services numériques au Tchad, puis en Afrique centrale. Le schéma de droite montre l'écosystème : "
      "quatre pôles déjà développés, la billetterie, la mobilité, l'emploi et l'immobilier, plus deux pôles prévus en "
      "phase deux, le commerce et la billetterie internationale. Les annonces et l'assistant IA servent tous les pôles.")

# 3 — Problème ---------------------------------------------------------------
s = new_slide()
header(s, "Le problème : une économie peu connectée",
       "Au Tchad, accéder à un service demande souvent un déplacement, un intermédiaire ou du bouche-à-oreille")
pains = [("moto", "Trouver un transport fiable"), ("home", "Chercher et réserver un logement"),
         ("briefcase", "Trouver des offres d'emploi"), ("ticket", "Acheter un billet de transport"),
         ("search", "Trouver des prestataires"), ("layers", "Informations dispersées"),
         ("megaphone", "Entreprises peu visibles"), ("pin", "Démarches physiques et informelles")]
for i, (ic, lab) in enumerate(pains):
    col, row = i % 4, i // 4
    x, y = 0.6 + col * 2.05, 1.75 + row * 1.6
    card(s, x, y, 1.9, 1.5, fill="F8FAFC")
    icon(s, ic, x + 0.15, y + 0.15, 0.55, circle=TEAL)
    text(s, x + 0.15, y + 0.8, 1.65, 0.55, lab, size=12, bold=True)
card(s, 8.95, 1.8, 3.8, 4.85, fill=DARK, line=None)
text(s, 9.2, 1.98, 3.4, 0.4, "Ce que cela coûte", size=16, bold=True, color=AMBER)
cons = [("clock", "Perte de temps"), ("money", "Perte d'argent"), ("x", "Prestataires invisibles"),
        ("trend", "Ventes manquées"), ("search", "Accès difficile à l'information"), ("phone", "Services peu digitalisés")]
for i, (ic, lab) in enumerate(cons):
    y = 2.55 + i * 0.66
    icon(s, ic, 9.2, y, 0.45, circle=None, col="a")
    text(s, 9.8, y + 0.06, 2.8, 0.4, lab, size=14, color=WHITE)
text(s, 0.6, 5.1, 8.1, 1.6, [[("Un exemple chiffré du coût de la non-connectivité : ", {"bold": True}),
                               ("les coupures d'Internet de 2024 auraient coûté environ 38 millions USD à l'économie "
                                "tchadienne (estimation Top10VPN, relayée par Tchadinfos).", {})],
                              [("Seuls 2,79 millions de Tchadiens utilisent Internet (oct. 2025), soit environ 13 % "
                                "de la population : la marge de progression est considérable.", {"color": TEAL})]],
     size=13, spacing=6)
footer(s, 3, "Sources : Top10VPN via Tchadinfos (2024) ; DataReportal Digital 2026 Chad (Kepios). Détails dans MAOUSANG_SOURCES.md")
notes(s, "3. Le problème",
      "Partons du quotidien. À N'Djaména, trouver un clando fiable, réserver un logement, repérer une offre d'emploi "
      "ou acheter un billet de bus demande souvent de se déplacer, de passer par un intermédiaire ou de compter sur "
      "le bouche-à-oreille. L'information est dispersée et les petites entreprises restent invisibles. Le résultat, "
      "c'est du temps perdu, de l'argent perdu et des ventes manquées. Un exemple chiffré : selon Top10VPN, les "
      "coupures d'Internet de 2024 auraient coûté environ 38 millions de dollars à l'économie tchadienne. Quand la "
      "connexion disparaît, l'économie ralentit. Et aujourd'hui, seuls 13 % des Tchadiens utilisent Internet : "
      "la marge de progression est énorme.")

# 4 — Avant / Après -----------------------------------------------------------
s = new_slide()
header(s, "Avant Maousang, après Maousang", "Plusieurs démarches dispersées → une seule application")
rows = [("Billet de bus", "Aller au guichet de la gare, faire la queue", "Rechercher et comparer les voyages en ligne"),
        ("Course ou livraison", "Héler un clando dans la rue, négocier le prix", "Commander une course ou une livraison"),
        ("Emploi", "Parcourir les panneaux, groupes et sites dispersés", "Postuler en ligne ; le recruteur trie avec l'ATS"),
        ("Logement", "Payer un démarcheur, multiplier les visites", "Filtrer les annonces, contacter le propriétaire"),
        ("Visibilité", "Bouche-à-oreille limité au quartier", "Profil, annonces et publicité ciblée")]

AA_ROWS = rows


def ill_slot(slide, key, label, x, y, w, h):
    """Emplacement nommé ILLU_<clé> pour une illustration 3D (remplacé par insert_screenshots.py)."""
    r = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=WHITE, line="94A3B8", lw=1, dash=True,
              name=f"ILLU_{key}", radius=0.06)
    tf = r.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = "Illustration 3D à insérer : " + label
    run.font.size, run.font.name, run.font.bold = Pt(11), FONT, True
    run.font.color.rgb = rgb(GRAY)


def avant_apres(s):
    img = os.path.join(ROOT, "assets", "illustrations_3d", "avant_apres.png")
    x, y, h = 1.95, 1.65, 5.25
    w = h * 1672 / 941
    if os.path.exists(img):
        pic = s.shapes.add_picture(img, Inches(x), Inches(y), Inches(w), Inches(h))
        pic.name = "IMG_avant_apres"
    else:
        ill_slot(s, "avant_apres", "image Avant / Après (16:9)", x, y, w, h)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.2, y + h - 0.6, 1.3, 0.42, fill="B91C1C", radius=0.5)
    text(s, x + 0.2, y + h - 0.53, 1.3, 0.3, "AVANT", size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + w - 2.6, y + h - 0.6, 2.4, 0.42, fill=TEAL, radius=0.5)
    text(s, x + w - 2.6, y + h - 0.53, 2.4, 0.3, "APRÈS MAOUSANG", size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

avant_apres(s)
footer(s, 4)
notes(s, "4. Avant / Après",
      "Cette image résume la promesse. Avant : on va au guichet de la gare pour un billet, on hèle un clando et on "
      "négocie, on parcourt des panneaux pour trouver un emploi, on paie un démarcheur pour un logement. Après : "
      "tout se fait depuis le téléphone. Le voyageur compare les trajets, le passager demande une course, le "
      "candidat postule en ligne et le recruteur trie les CV avec notre ATS, le locataire filtre les annonces. "
      "Pour les prestataires, c'est une vitrine qu'ils n'avaient pas.")

# 5 — Écosystème -----------------------------------------------------------------
s = new_slide()
header(s, "La solution : l'écosystème Maousang", "Quatre pôles développés, deux pôles en phase 2, deux services transversaux")
grid = [("ticket", "Billetterie", "Rechercher des voyages et accéder aux offres de billetterie", True),
        ("moto", "Mobilité – Clando", "Moto-taxis, livraison de repas, courses et colis", True),
        ("briefcase", "Emploi et ATS", "Offres d'emploi et tri intelligent des candidatures", True),
        ("home", "Immobilier", "Recherche, location, réservation journalière, annonces", True),
        ("cart", "Commerce", "Boutiques en ligne, catalogue, commandes, paiement, livraison", False),
        ("plane", "Billetterie internationale", "Vols vers l'Afrique, la Turquie, la Chine, les Émirats, l'Europe", False)]
for i, (ic, t, d, live) in enumerate(grid):
    col, row = i % 3, i // 3
    x, y = 0.6 + col * 4.1, 1.75 + row * 2.05
    card(s, x, y, 3.9, 1.85, fill=WHITE if live else "F8FAFC", line=MID)
    icon(s, ic, x + 0.2, y + 0.22, 0.7, circle=TEAL if live else "94A3B8")
    text(s, x + 1.05, y + 0.25, 2.7, 0.4, t, size=15, bold=True)
    badge = "Développé" if live else "Phase 2"
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 1.05, y + 0.68, 1.15 if live else 0.95, 0.28,
          fill=LIGHT if live else "E2E8F0", radius=0.5)
    text(s, x + 1.05, y + 0.7, 1.15 if live else 0.95, 0.25, badge, size=10, bold=True,
         color=TEAL if live else GRAY, align=PP_ALIGN.CENTER)
    text(s, x + 0.2, y + 1.1, 3.5, 0.7, d, size=12, color="334155")
card(s, 0.6, 5.9, 12.1, 0.85, fill=DARK, line=None)
icon(s, "megaphone", 0.85, 6.05, 0.55, circle=AMBER)
text(s, 1.55, 6.12, 4.6, 0.5, [[("Annonces : ", {"bold": True, "color": AMBER}),
                                ("publication et promotion pour tous les pôles", {"color": WHITE})]], size=13)
icon(s, "bot", 6.7, 6.05, 0.55, circle=AMBER)
text(s, 7.4, 6.12, 5.2, 0.5, [[("Assistant IA : ", {"bold": True, "color": AMBER}),
                               ("guide l'utilisateur vers le bon service", {"color": WHITE})]], size=13)
footer(s, 5)
notes(s, "5. L'écosystème",
      "Maousang n'est pas une application de plus. C'est un écosystème. Quatre pôles sont déjà développés : la "
      "billetterie, la mobilité Clando avec la livraison, l'emploi avec un ATS intelligent, et l'immobilier. Deux "
      "pôles sont prévus en phase deux : le commerce et la billetterie internationale ; ils sont clairement indiqués "
      "comme des évolutions futures. Deux services transversaux relient le tout : les annonces et l'assistant IA, "
      "qui oriente l'utilisateur vers le bon service. Un seul compte, une seule application, plusieurs usages : "
      "c'est ce qui crée la fidélité.")

# 6 — Parcours en captures -------------------------------------------------------
s = new_slide()
header(s, "Le parcours utilisateur, du démarrage aux services",
       "Parcours sur la plateforme en production (maousang.vercel.app)")
steps = [("01_demarrage", "Démarrage animé (≈ 1,5 s)"), ("02_logo", "Logo Maousang (≈ 1,5 s)"),
         ("03_video_intro", "Vidéo d'introduction (≈ 30 s)"), ("04_page_ia", "Page IA : choix du service")]
for i, (k, lab) in enumerate(steps):
    x = 1.0 + i * 3.0
    phone(s, k, lab, x, 1.65, w=2.1, h=4.1)
    shape(s, MSO_SHAPE.OVAL, x + 0.82, 5.9, 0.45, 0.45, fill=TEAL)
    text(s, x + 0.82, 5.96, 0.45, 0.35, str(i + 1), size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    text(s, x - 0.35, 6.42, 2.8, 0.35, lab, size=13, bold=True, align=PP_ALIGN.CENTER)
    if i < 3:
        shape(s, MSO_SHAPE.RIGHT_ARROW, x + 2.3, 3.55, 0.4, 0.4, fill=MID)
footer(s, 6, "Captures d'écran de l'application fournies par le fondateur (novembre 2026). Les pôles détaillés suivent.")
notes(s, "6. Parcours en captures",
      "Voici le parcours réel dans l'application. Un démarrage animé, puis le logo Maousang, puis une courte vidéo "
      "d'introduction de trente secondes, que l'on peut passer. L'utilisateur arrive ensuite sur la page IA : "
      "« Que cherchez-vous aujourd'hui ? ». Il choisit Clando, Immobilier, Bus ou Emploi. Je vous montre "
      "maintenant chaque pôle en détail.")

# 7-10 — Pôles -----------------------------------------------------------------------
POLES = [
    ("ticket", "Pôle 1 · Billetterie", "Acheter son billet sans passer par le guichet",
     "Les billets interurbains se vendent surtout au guichet des agences. Les prix varient : N'Djaména–Moundou 12 500 FCFA, "
     "–Sarh 17 500 FCFA, –Abéché 25 000 FCFA (presse, 2023-2024).",
     "Rechercher un bus par ville de départ, ville d'arrivée et date de voyage, puis réserver et acheter son billet.",
     "Voyageurs interurbains, étudiants, familles, compagnies de bus et agences de voyage.",
     "Moins de déplacements et d'attente pour le voyageur, meilleur remplissage pour le transporteur. "
     "Revenu : commission sur billet (hypothèse 5 %).",
     [("07_bus", "Bus : rechercher un bus")],
     "Prix des billets : ADC Tchad et Tchadinfos (2023-2024). Commission : hypothèse à négocier avec les transporteurs."),
    ("moto", "Pôle 2 · Mobilité – Clando", "Une course ou une livraison en quelques clics",
     "Le clando se hèle dans la rue, le prix se négocie et la livraison reste informelle. En septembre 2026, la ville a "
     "lancé un programme d'identification des moto-taxis : la demande de traçabilité existe.",
     "« Commander un Clando » ou « Commander une Livraison » : moto-taxi, repas, courses, colis, documents, "
     "et autres prestataires de mobilité.",
     "Citadins, restaurants, commerces, conducteurs de moto-taxi et livreurs.",
     "Des revenus en plus pour les conducteurs, de la traçabilité pour les passagers. "
     "Revenu : commission par course ou livraison (hypothèse 10 %).",
     [("05_clando", "Clando : course et livraison")],
     "Programme d'identification des moto-taxis : Tchadinfos, 19/09/2026. Commission : hypothèse."),
    ("briefcase", "Pôle 3 · Emploi et ATS intelligent", "Le bon candidat, plus vite",
     "Les offres sont dispersées entre sites, réseaux sociaux et affichages. Les recruteurs trient des piles de CV à la main.",
     "Offres d'emploi, publication d'offres, profil, offres recommandées ; ATS : réception des candidatures, analyse automatisée des CV, "
     "classement des profils, aide à la présélection, mise en relation.",
     "Chercheurs d'emploi, jeunes diplômés, PME, ONG, cabinets RH.",
     "Tri des candidatures plus rapide, candidats plus visibles. Revenu : offre payante (hyp. 10 000 FCFA) "
     "et ATS premium (hyp. 25 000 FCFA/mois). Gratuit pour les candidats.",
     [("08_emploi", "Emploi")],
     "Tarifs : hypothèses de travail non validées par le marché."),
    ("home", "Pôle 4 · Immobilier", "Trouver un logement sans démarcheur",
     "La recherche passe par le bouche-à-oreille et des démarcheurs informels. Le Tchad affiche un déficit estimé "
     "à 1,5 million de logements (gouvernement, nov. 2026).",
     "Location longue durée, location courte durée, agences partenaires, favoris, publication d'annonces, mise en relation "
     "entre propriétaires, agences et locataires.",
     "Locataires, étudiants, voyageurs, expatriés, propriétaires et agences immobilières.",
     "Moins de visites inutiles, plus de visibilité pour les biens. Revenu : annonces sponsorisées "
     "(hyp. 5 000 FCFA/mois) et commission sur réservation journalière (hyp. 10 %).",
     [("06_immobilier", "Immobilier")],
     "Déficit de logements : Tchadinfos, 04/11/2026 (programme national d'habitat). Tarifs : hypothèses."),
]
pole_notes = [
    "Premier pôle, la billetterie. Aujourd'hui, pour voyager de N'Djaména à Moundou, Sarh ou Abéché, on achète son "
    "billet au guichet. Les prix vont de 12 500 à 25 000 FCFA selon la destination. Avec Maousang, le voyageur "
    "recherche les voyages et consulte les offres depuis son téléphone. Le transporteur remplit mieux ses bus. "
    "Notre revenu : une commission sur chaque billet, que nous estimons à 5 % et que nous négocierons avec les compagnies.",
    "Deuxième pôle, la mobilité. Le clando est le moyen de transport le plus courant à N'Djaména, mais tout se fait "
    "dans la rue : on hèle, on négocie, sans traçabilité. La mairie a d'ailleurs lancé en septembre un programme "
    "d'identification des moto-taxis. Maousang met en relation passagers, conducteurs et livreurs, pour les courses, "
    "les repas, les achats et les colis. Le conducteur gagne des clients, le passager gagne en sécurité. Nous "
    "prenons une commission, estimée à 10 %.",
    "Troisième pôle, l'emploi. C'est là que mon expertise en IA fait la différence. En plus des offres, nous proposons "
    "un ATS intelligent : il reçoit les candidatures, analyse les CV automatiquement, classe les profils et aide à "
    "la présélection. Le recruteur gagne des heures, le candidat est vu. C'est gratuit pour les candidats ; les "
    "entreprises paient l'offre et l'ATS premium.",
    "Quatrième pôle, l'immobilier. Le pays manque d'environ 1,5 million de logements, et la recherche passe encore "
    "par des démarcheurs. Maousang permet de rechercher, louer, réserver à la nuit et publier des annonces. "
    "Propriétaires et agences paient pour mettre leurs biens en avant, et nous prenons une commission sur les "
    "réservations journalières.",
]
for k, (ic, title, msg, prob, feat, users, value, caps, src) in enumerate(POLES):
    s = new_slide()
    header(s, title, msg)
    icon(s, ic, 0.6, 1.8, 0.95, circle=TEAL)
    blocks = [("Le problème", prob, "x"), ("La fonctionnalité", feat, "zap"),
              ("Les utilisateurs", users, "users"), ("La valeur ajoutée", value, "money")]
    for j, (bt, bd, bi) in enumerate(blocks):
        col, row = j % 2, j // 2
        x, y = 1.8 + col * 4.0, 1.8 + row * 2.5
        card(s, x, y, 3.8, 2.3, fill="F8FAFC" if j != 3 else LIGHT)
        icon(s, bi, x + 0.18, y + 0.18, 0.38, circle=None, col="t")
        text(s, x + 0.65, y + 0.2, 3.0, 0.4, bt, size=14, bold=True, color=TEAL)
        text(s, x + 0.18, y + 0.7, 3.45, 1.55, bd, size=12, color="1F2937")
    for j, (key, lab) in enumerate(caps):
        phone(s, key, lab, 10.05, 1.75, w=2.5, h=4.85)
    footer(s, 7 + k, src)
    notes(s, f"{7 + k}. {title}", pole_notes[k])

# 11 — Marché -------------------------------------------------------------------------
s = new_slide()
header(s, "Le marché : mobile, mais peu connecté",
       "Le téléphone est déjà là ; l'usage d'Internet reste à conquérir")
picture(s, "map_chad.png", 0.4, 1.55, h=5.35)
stats = [("21,1 M", "habitants (oct. 2025)", "ONU, via DataReportal 2026"),
         ("25,1 %", "de population urbaine, soit ≈ 5,3 M de citadins", "DataReportal 2026"),
         ("≈ 1,66 M", "habitants à N'Djaména (2024)", "ONU WUP, via Macrotrends"),
         ("15,5 M", "connexions mobiles (fin 2025), 73 % de la population", "GSMA Intelligence, via DataReportal"),
         ("2,79 M", "internautes (oct. 2025), ≈ 13 % de la population", "Kepios, via DataReportal 2026"),
         ("6,25 M", "comptes de monnaie électronique (déc. 2024)", "BEAC, chiffre relayé, à confirmer")]
for i, (v, l, src) in enumerate(stats):
    col, row = i % 2, i // 2
    x, y = 4.95 + col * 3.95, 1.75 + row * 1.42
    card(s, x, y, 3.75, 1.28, fill="F8FAFC")
    text(s, x + 0.2, y + 0.1, 3.4, 0.55, v, size=26, bold=True, color=TEAL)
    text(s, x + 0.2, y + 0.62, 3.4, 0.4, l, size=11, color=DARK)
    text(s, x + 0.2, y + 0.98, 3.4, 0.25, src, size=9, color=GRAY, italic=True)
text(s, 4.95, 6.05, 7.75, 0.75, [[("Lecture : ", {"bold": True}),
                                  ("le marché adressable n'est pas la population totale. Maousang vise d'abord les "
                                   "internautes urbains, puis profite de la croissance du mobile et du paiement mobile.", {})]],
     size=12)
footer(s, 11, "Liens, dates et méthodes : MAOUSANG_SOURCES.md. Carte schématique, contours simplifiés.")
notes(s, "11. Le marché",
      "Regardons les chiffres, tous sourcés. Le Tchad compte environ 21 millions d'habitants, dont un quart en ville, "
      "soit 5,3 millions de citadins. N'Djaména compte environ 1,7 million d'habitants. Il y a 15,5 millions de "
      "connexions mobiles, mais seulement 2,8 millions d'internautes. Autrement dit, le téléphone est déjà dans les "
      "poches ; l'usage d'Internet, lui, reste à conquérir. La BEAC recense aussi plus de 6 millions de comptes de "
      "monnaie électronique : le paiement mobile est en place. Attention : je ne confonds pas population et clients. "
      "Notre cible de départ, ce sont les internautes urbains.")

# 12 — TAM SAM SOM ----------------------------------------------------------------------
Mk = M["Marche"]
tam, sam = Mk["TAM – internautes au Tchad"], Mk["SAM – internautes urbains (N'Djaména et grandes villes)"]
somp, somi, soma = Mk["SOM prudent (5 % du SAM, utilisateurs actifs)"], Mk["SOM intermédiaire (10 % du SAM)"], Mk["SOM ambitieux (20 % du SAM)"]
rev_mau = Mk["Revenu annuel par MAU (intermédiaire A3)"]
s = new_slide()
header(s, "TAM, SAM, SOM : un potentiel mesuré avec prudence",
       "Unité : utilisateurs actifs. Valeur : revenu plateforme annuel potentiel en FCFA")
shape(s, MSO_SHAPE.OVAL, 0.7, 1.75, 5.0, 5.0, fill=LIGHT, line=MINT, lw=1.5)
shape(s, MSO_SHAPE.OVAL, 1.55, 3.0, 3.3, 3.3, fill="9DB4E8")
shape(s, MSO_SHAPE.OVAL, 2.35, 4.25, 1.7, 1.7, fill=TEAL)
text(s, 0.7, 2.05, 5.0, 0.6, [[("TAM  ", {"bold": True}), (f"{fr(tam / 1e6, 2)} M", {"bold": True, "color": TEAL})]], size=18, align=PP_ALIGN.CENTER)
text(s, 1.55, 3.3, 3.3, 0.6, [[("SAM  ", {"bold": True}), (f"{fr(sam / 1e6, 2)} M", {"bold": True, "color": DARK})]], size=17, align=PP_ALIGN.CENTER)
text(s, 2.35, 4.75, 1.7, 0.7, [["SOM"], [f"{fr(somi / 1e3)} k"]], size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
data = [["Niveau", "Définition", "Utilisateurs", "Valeur / an*"],
        ["TAM", "Internautes au Tchad (oct. 2025)", f"{fr(tam)}", f"{fr(tam * rev_mau / 1e9, 1)} Md FCFA"],
        ["SAM", "Internautes urbains : 5,3 M de citadins × 30 % d'usage (hyp.)", f"{fr(sam)}", f"{fr(sam * rev_mau / 1e9, 1)} Md FCFA"],
        ["SOM prudent", "5 % du SAM à 3 ans", f"{fr(somp)}", f"{fr(somp * rev_mau / 1e6)} M FCFA"],
        ["SOM intermédiaire", "10 % du SAM à 3 ans", f"{fr(somi)}", f"{fr(somi * rev_mau / 1e6)} M FCFA"],
        ["SOM ambitieux", "20 % du SAM à 3 ans", f"{fr(soma)}", f"{fr(soma * rev_mau / 1e6)} M FCFA"]]
table(s, 6.1, 1.8, 6.6, 3.0, data, [1.55, 2.75, 1.05, 1.25], size=11)
card(s, 6.1, 5.05, 6.6, 1.65, fill=DARK, line=None)
text(s, 6.35, 5.17, 6.1, 1.45, [[("Point de vigilance. ", {"bold": True, "color": AMBER}),
                                 (f"L'objectif d'1 million d'inscrits en A3 correspond à ≈ {fr(Mk['MAU fin A3 implicite – objectif 1 M inscrits'] / 1e3)} k "
                                  f"utilisateurs actifs, soit {fr(Mk['Part du SAM correspondante'] * 100)} % du SAM actuel. "
                                  "C'est ambitieux : il faut la croissance d'Internet, l'extension aux grandes villes "
                                  "et les premiers pas à l'étranger.", {"color": WHITE})]], size=12)
footer(s, 12, f"* Valeur = utilisateurs × {fr(rev_mau)} FCFA de revenu annuel par utilisateur actif (modèle intermédiaire, A3). "
       "Sources : DataReportal 2026 ; hypothèse d'usage urbain à 30 %.")
notes(s, "12. TAM, SAM, SOM",
      f"Pour mesurer le potentiel, je raisonne en utilisateurs actifs, pas en population. Le TAM, ce sont les "
      f"{fr(tam / 1e6, 2)} millions d'internautes du pays. Le SAM, ce sont les internautes urbains : nous l'estimons "
      f"à {fr(sam / 1e6, 2)} million, avec une hypothèse d'usage d'Internet de 30 % en ville. Le SOM, la part que nous "
      f"pouvons conquérir en trois ans, va de {fr(somp / 1e3)} mille à {fr(soma / 1e3)} mille utilisateurs actifs. "
      f"En valeur, le SAM représente environ {fr(sam * rev_mau / 1e9, 1)} milliards de FCFA de revenus de plateforme par an. "
      "Je suis transparent : notre objectif d'un million d'inscrits est ambitieux. Il suppose la croissance "
      "d'Internet et l'extension à d'autres villes et pays.")

# 13 — Concurrence ---------------------------------------------------------------------
s = new_slide()
header(s, "La concurrence : des spécialistes, pas d'écosystème",
       "Chaque acteur observé couvre un seul domaine ; Maousang les réunit")
data = [["Acteur", "Secteur", "Offre observée (descriptions publiques)", "Limite identifiable"],
        ["Chadito", "Annonces", "Petites annonces : voitures, location, emploi, électronique ; vendeurs vérifiés (KYC)", "Pas de mobilité, de billetterie ni d'ATS"],
        ["Blyt", "Mobilité (VTC)", "Taxi à N'Djaména, prix affiché avant la course, chauffeurs identifiés", "Mobilité seule"],
        ["SafeClando", "Moto-taxi", "Réservation de clando à N'Djaména", "Mobilité seule"],
        ["Allons-y Taxi Privé", "Mobilité", "Réservation de taxi, en français, anglais et arabe", "Mobilité seule"],
        ["emploi.td", "Emploi", "Offres d'emploi et recrutement", "Pas d'ATS mentionné publiquement"],
        ["Alwihda Info", "Annonces", "Annonces immobilières gratuites, par web et SMS", "Annonces non structurées"],
        ["Agences de bus", "Billetterie", "Vente au guichet (gares de Diguel et Chagoua)", "Peu de vente en ligne publiée"]]
table(s, 0.6, 1.75, 8.1, 4.3, data, [1.55, 1.2, 3.3, 2.05], size=10)
# Matrice
mx, my, mw, mh = 9.1, 1.85, 3.6, 3.6
shape(s, MSO_SHAPE.RECTANGLE, mx, my, mw, mh, fill="F8FAFC", line=MID)
line(s, mx + mw / 2, my, mx + mw / 2, my + mh, color=MID, w=1, dash=True)
line(s, mx, my + mh / 2, mx + mw, my + mh / 2, color=MID, w=1, dash=True)
text(s, mx, my + mh + 0.05, mw, 0.3, "Nombre de services couverts →", size=10, color=GRAY, align=PP_ALIGN.CENTER)
text(s, mx - 0.05, my - 0.32, mw, 0.3, "↑ Outils intelligents (IA, ATS, réservation)", size=10, color=GRAY)
pts = [("Chadito", 0.42, 0.42, GRAY), ("Blyt", 0.12, 0.62, GRAY), ("SafeClando", 0.1, 0.45, GRAY),
       ("emploi.td", 0.12, 0.22, GRAY), ("Alwihda", 0.33, 0.12, GRAY), ("Guichets", 0.1, 0.06, GRAY),
       ("MAOUSANG", 0.82, 0.84, AMBER)]
for lab, px, py, col in pts:
    d = 0.32 if lab == "MAOUSANG" else 0.18
    x, y = mx + px * mw - d / 2, my + (1 - py) * mh - d / 2
    shape(s, MSO_SHAPE.OVAL, x, y, d, d, fill=col)
    if lab == "MAOUSANG":
        text(s, x - 1.25, y + 0.38, 1.9, 0.3, lab, size=11, bold=True, color=DARK, align=PP_ALIGN.RIGHT)
    else:
        text(s, x + d + 0.05, y - 0.05, 1.3, 0.3, lab, size=10, color=DARK)
text(s, 9.1, 5.85, 3.6, 0.3, "Positionnement qualitatif", size=9, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
text(s, 0.6, 6.2, 8.1, 0.6, [[("Notre différence : ", {"bold": True, "color": TEAL}),
                              ("un seul compte pour la billetterie, la mobilité, l'emploi avec ATS et l'immobilier.", {})]],
     size=13)
footer(s, 13, "Sources : fiches App Store et Google Play, sites des acteurs (nov. 2026). Wadini, Annoncena : aucune présence publique trouvée. Aucun chiffre inventé.")
notes(s, "13. La concurrence",
      "Il existe des acteurs sérieux, et je les respecte. Chadito fait de la petite annonce, Blyt, SafeClando et "
      "Allons-y font de la mobilité, emploi.td publie des offres d'emploi, Alwihda Info diffuse des annonces "
      "immobilières, et les agences de bus vendent au guichet. Chacun couvre un seul domaine. Je ne cite aucun "
      "chiffre sur eux, car je n'en ai pas de fiable. Notre avantage stratégique est l'écosystème : un utilisateur "
      "qui vient pour un clando revient pour un billet, un emploi ou un logement. Cela réduit le coût "
      "d'acquisition et augmente la valeur de chaque client.")

# 14 — Modèle économique ----------------------------------------------------------------
s = new_slide()
header(s, "Le modèle économique : huit sources de revenus",
       "Gratuit pour l'utilisateur qui cherche ; payant pour la transaction et la visibilité")
data = [["Source de revenus", "Fonctionnement", "Tarif (hypothèse à tester)", "Potentiel"],
        ["1. Commissions sur transactions", "% prélevé sur les courses, livraisons et réservations", "10 % (mobilité, réservations)", "Élevé"],
        ["2. Abonnements professionnels", "Visibilité, badge vérifié, statistiques", "5 000 FCFA / mois", "Élevé"],
        ["3. Immobilier sponsorisé", "Annonce mise en avant", "5 000 FCFA / mois", "Moyen"],
        ["4. Offres d'emploi payantes", "Publication par l'entreprise", "10 000 FCFA / offre", "Moyen"],
        ["5. Services premium recruteurs", "ATS : analyse et classement des CV", "25 000 FCFA / mois", "Moyen"],
        ["6. Publicité", "Bannières et annonces commerciales", "50 000 FCFA / mois", "Moyen"],
        ["7. Partenariats transporteurs", "Commission sur billets vendus", "5 % du billet", "Moyen"],
        ["8. Frais de réservation", "Mise en relation, si applicable", "À définir par pôle", "Appoint"]]
table(s, 0.6, 1.75, 8.3, 4.5, data, [2.55, 2.85, 1.95, 0.95], size=11)
# répartition des revenus (A3, intermédiaire)
cd = CategoryChartData()
cats = ["Mobilité", "Abonnements", "Emploi", "Immobilier", "Billetterie", "Publicité"]
keys = ["rev_mob", "rev_subs", "rev_emp", "rev_imm", "rev_bil", "rev_ads"]
cd.categories = cats
cd.add_series("CA A3", [round(I[k][2] / 1e6, 1) for k in keys])
gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(9.1), Inches(1.6), Inches(3.7), Inches(4.4), cd)
ch = gf.chart
chart_style(ch, legend=True, size=10)
ch.has_title = True
ch.chart_title.text_frame.text = "Répartition du CA, A3 (intermédiaire)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
pal = [TEAL, MINT, AMBER, "0EA5E9", "94A3B8", DARK]
plot = ch.plots[0]
plot.has_data_labels = True
plot.data_labels.number_format = '0%'
plot.data_labels.show_percentage = True
plot.data_labels.show_value = False
plot.data_labels.font.size = Pt(9)
plot.data_labels.font.color.rgb = rgb(WHITE)
for i, pt in enumerate(plot.series[0].points):
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = rgb(pal[i])
text(s, 0.6, 6.4, 12.1, 0.4, "Aucun tarif n'est encore validé par le marché : ils seront testés auprès des utilisateurs "
     "et des partenaires pendant les six premiers mois.", size=12, italic=True, color=GRAY)
footer(s, 14)
notes(s, "14. Le modèle économique",
      "Comment gagnons-nous de l'argent ? Le principe : chercher est gratuit, la transaction et la visibilité sont "
      "payantes. Nous avons huit sources de revenus : les commissions sur courses et réservations, les abonnements "
      "des professionnels, l'immobilier sponsorisé, les offres d'emploi payantes, l'ATS premium pour les "
      "recruteurs, la publicité, les partenariats avec les transporteurs et des frais de réservation. Les tarifs "
      "affichés sont des hypothèses, pas des prix validés : nous les testerons pendant les six premiers mois. "
      "En année trois, la mobilité et les abonnements pèseraient environ deux tiers du chiffre d'affaires.")

# 15 — Acquisition --------------------------------------------------------------------
s = new_slide()
header(s, "Acquisition : cinq leviers sur douze mois",
       "Faire connaître, faire essayer, faire recommander")
levers = [("megaphone", "A. Agence de communication", "Identité, campagnes, contenus, community management, RP"),
          ("tv", "B. Web médias et influence", "Médias tchadiens, pages Facebook, créateurs de contenus"),
          ("gift", "C. Parrainage", "Le parrain gagne un crédit ; les actifs deviennent ambassadeurs"),
          ("zap", "D. « Le coût de la non-connectivité »", "Campagne éducative : temps, argent, opportunités perdus"),
          ("users", "E. Terrain", "Agents, démonstrations, universités, entreprises, transporteurs, quartiers")]
for i, (ic, t, d) in enumerate(levers):
    y = 1.75 + i * 0.97
    icon(s, ic, 0.6, y, 0.6, circle=TEAL if i != 3 else AMBER)
    text(s, 1.35, y - 0.02, 3.7, 0.35, t, size=13, bold=True)
    text(s, 1.35, y + 0.32, 3.7, 0.6, d, size=11, color="334155")
# calendrier
gx, gy, cw, rh = 5.5, 1.85, 0.47, 0.5
months = [f"M{i}" for i in range(1, 13)]
for j, m in enumerate(months):
    text(s, gx + 1.55 + j * cw, gy - 0.05, cw, 0.3, m, size=10, bold=True, color=GRAY, align=PP_ALIGN.CENTER)
plan = [("Agence", [(1, 2, DARK), (3, 3, TEAL), (6, 6, TEAL), (9, 9, TEAL), (12, 12, TEAL)]),
        ("Web médias", [(2, 12, MINT)]),
        ("Parrainage", [(3, 12, TEAL)]),
        ("Sensibilisation", [(4, 5, AMBER), (10, 11, AMBER)]),
        ("Universités", [(1, 3, "0EA5E9"), (9, 10, "0EA5E9")]),
        ("Terrain", [(1, 12, "94A3B8")])]
for i, (lab, spans) in enumerate(plan):
    y = gy + 0.35 + i * rh
    text(s, gx, y + 0.08, 1.5, 0.3, lab, size=11, bold=True)
    shape(s, MSO_SHAPE.RECTANGLE, gx + 1.55, y + 0.05, 12 * cw, rh - 0.1, fill="F1F5F9")
    for a, b, col in spans:
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, gx + 1.55 + (a - 1) * cw + 0.03, y + 0.1, (b - a + 1) * cw - 0.06, rh - 0.2, fill=col, radius=0.3)
text(s, gx, 5.15, 7.2, 0.3, "Budget A1 (dans les 10 M FCFA) – indicatif, à affiner selon devis", size=12, bold=True, color=TEAL)
budget = [("Agence de communication", 0.8), ("Web médias et influenceurs", 0.5), ("Publicité digitale", 0.4),
          ("Universités et démonstrations", 0.3), ("Prospection terrain", 0.7), ("Partenariats", 0.4)]
for i, (b, v) in enumerate(budget):
    col, row = i % 2, i // 2
    text(s, gx + col * 3.65, 5.5 + row * 0.38, 2.6, 0.35, b, size=11)
    text(s, gx + col * 3.65 + 2.55, 5.5 + row * 0.38, 0.9, 0.35, f"{fr(v, 1)} M", size=11, bold=True, align=PP_ALIGN.RIGHT)
footer(s, 15, "Total A1 : 3,1 M FCFA (2,0 M marketing + 0,7 M prospection + 0,4 M partenariats). Parrainage : ≈ 1,0 M FCFA en A1, payé sur les revenus.")
notes(s, "15. Acquisition",
      "Pour acquérir nos utilisateurs, nous combinons cinq leviers. Une agence de communication pour l'identité, les "
      "campagnes et les relations presse. Les médias numériques et les influenceurs tchadiens. Un programme de "
      "parrainage : chaque utilisateur qui fait venir un ami gagne un crédit. Une campagne éducative, « le coût de "
      "la non-connectivité », qui montre le temps et l'argent perdus sans accès à l'information. Et surtout le "
      "terrain : agents, démonstrations, universités, entreprises, transporteurs et quartiers. Le calendrier "
      "s'étale sur douze mois, pour 3,1 millions de FCFA en année un.")

# 16 — Finances --------------------------------------------------------------------------
s = new_slide()
header(s, "Projections financières sur trois ans (prévisionnel)",
       "Objectifs : 10 000, 100 000, puis 1 000 000 d'inscrits. Trois scénarios, toutes formules dans le modèle Excel")
cd = CategoryChartData()
cd.categories = ["A1", "A2", "A3"]
for nm, sc in (("Prudent", P), ("Intermédiaire", I), ("Ambitieux", A)):
    cd.add_series(nm, [round(v / 1e6, 1) for v in sc["rev_total"]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(1.65), Inches(4.3), Inches(3.3), cd)
ch = gf.chart
chart_style(ch)
ch.has_title = True
ch.chart_title.text_frame.text = "Chiffre d'affaires (M FCFA)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
ch.value_axis.has_major_gridlines = True
ch.value_axis.major_gridlines.format.line.color.rgb = rgb("E2E8F0")
ch.value_axis.tick_labels.font.size = Pt(9)
ch.value_axis.format.line.fill.background()
for i, col in enumerate(["94A3B8", TEAL, AMBER]):
    ser = ch.plots[0].series[i]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
ch.plots[0].gap_width = 60
cd = CategoryChartData()
cd.categories = ["A1", "A2", "A3"]
cd.add_series("Inscrits (fin d'année)", [round(v / 1e3, 1) for v in I["users_end"]])
cd.add_series("Actifs mensuels (moyenne)", [round(v / 1e3, 1) for v in I["mau"]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(4.75), Inches(1.65), Inches(4.0), Inches(3.3), cd)
ch = gf.chart
chart_style(ch)
ch.has_title = True
ch.chart_title.text_frame.text = "Utilisateurs, intermédiaire (milliers)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
ch.value_axis.major_gridlines.format.line.color.rgb = rgb("E2E8F0")
ch.value_axis.tick_labels.font.size = Pt(9)
pl = ch.plots[0]
pl.gap_width = 60
pl.has_data_labels = True
pl.data_labels.font.size = Pt(9)
pl.data_labels.number_format = '#,##0'
pl.data_labels.number_format_is_linked = False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
for i, col in enumerate([TEAL, AMBER]):
    pl.series[i].format.fill.solid()
    pl.series[i].format.fill.fore_color.rgb = rgb(col)
# tableau synthèse intermédiaire
data = [["Intermédiaire (FCFA)", "A1", "A2", "A3"],
        ["Chiffre d'affaires"] + [mfcfa(v) for v in I["rev_total"]],
        ["Dépenses totales"] + [mfcfa(v) for v in I["cost_total"]],
        ["Résultat opérationnel"] + [mfcfa(v) for v in I["ebit"]],
        ["Transactions"] + [fr(v) for v in I["tx_total"]],
        ["Conversion payante"] + [f"{fr(v * 100, 1)} %" for v in I["conv"]],
        ["Revenu / client payant"] + [fr(v) for v in I["arppu"]],
        ["Équipe (personnes)"] + [str(int(x)) for x in M["Equipe"][-1][1:4]]]
table(s, 8.95, 1.75, 3.85, 3.2, data, [1.6, 0.75, 0.75, 0.75], size=10)
# scénarios résultat
card(s, 0.6, 5.15, 12.1, 1.65, fill="F8FAFC")
text(s, 0.85, 5.25, 3.5, 0.35, "Résultat opérationnel (M FCFA)", size=12, bold=True, color=TEAL)
for i, (nm, sc, col) in enumerate((("Prudent", P, GRAY), ("Intermédiaire", I, TEAL), ("Ambitieux", A, "B45309"))):
    y = 5.62 + i * 0.36
    text(s, 0.85, y, 1.6, 0.3, nm, size=11, bold=True, color=col)
    text(s, 2.45, y, 3.3, 0.3, "   ".join(f"A{k + 1} : {fr(v / 1e6, 1)}" for k, v in enumerate(sc["ebit"])), size=11)
text(s, 6.2, 5.25, 6.3, 1.5, [[("Formule clé : ", {"bold": True}),
                               ("CA = Σ pôles. Ex. mobilité = MAU × 40 % × 4 courses/mois × 12 × 1 000 FCFA × 10 %.", {})],
                              [("Hypothèses : ", {"bold": True}),
                               ("MAU = inscrits moyens × 35 % → 25 % ; dépenses A1 = budget financé de 10 M.", {})],
                              [("Trésorerie A2 (intermédiaire) : ", {"bold": True, "color": "B45309"}),
                               (f"{mfcfa(I['cash'][1])} FCFA → prévoir un relais (revenus, prêt ou tour d'amorçage).", {})]],
     size=11, spacing=3)
footer(s, 16, "Toutes les données sont prévisionnelles. Détail des hypothèses et formules : MAOUSANG_FINANCIAL_MODEL.xlsx.")
notes(s, "16. Projections financières",
      f"Voici nos projections, construites dans un modèle Excel où chaque chiffre a une formule. Nos objectifs sont "
      f"10 000 inscrits en année un, 100 000 en année deux et un million en année trois. Ce sont des objectifs, pas "
      f"des résultats. Dans le scénario intermédiaire, le chiffre d'affaires passe de {mfcfa(I['rev_total'][0])} FCFA "
      f"en année un à {mfcfa(I['rev_total'][1])} en année deux, puis {mfcfa(I['rev_total'][2])} en année trois. Le "
      f"résultat opérationnel est négatif les deux premières années, puis atteint {mfcfa(I['ebit'][2])} en année trois. "
      f"Le scénario prudent reste déficitaire sur trois ans ; le scénario ambitieux est rentable dès l'année un. Je "
      "signale un point : en année deux, la trésorerie du scénario intermédiaire passe légèrement sous zéro. Nous "
      "prévoyons donc un relais, par les revenus, un prêt ou un tour d'amorçage.")

# 17 — Expansion ----------------------------------------------------------------------------
s = new_slide()
header(s, "Expansion : du Tchad vers l'Afrique centrale et au-delà",
       "Trois phases, déclenchées par la traction, pas par le calendrier")
picture(s, "map_africa.png", 6.75, 1.45, h=5.45)
phases = [("1", "Consolidation au Tchad", "A1–A2", TEAL,
           "N'Djaména, puis Moundou, Abéché, Sarh. Réseau de prestataires, expérience utilisateur."),
          ("2", "Deux nouveaux pôles", "A2–A3", AMBER,
           "Commerce : boutiques, catalogue, commandes, paiement, livraison. Billetterie internationale : Afrique, "
           "Turquie, Chine, Russie, Émirats, Europe, via compagnies, agences et fournisseurs de réservation à signer."),
          ("3", "Expansion africaine", "A3+", DARK,
           "D'abord la CEMAC : Cameroun (29,5 M hab., 41,9 % en ligne), Centrafrique (5,4 M ; 15,5 %). "
           "Ensuite Sénégal (60,6 %), Côte d'Ivoire (39,6 %), Guinée (26,5 %).")]
y = 1.75
for n, t, when, col, d in phases:
    h = 1.25 if n == "1" else 1.65
    shape(s, MSO_SHAPE.OVAL, 0.6, y, 0.6, 0.6, fill=col)
    text(s, 0.6, y + 0.12, 0.6, 0.4, n, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    text(s, 1.4, y, 3.8, 0.35, t, size=15, bold=True)
    text(s, 5.2, y + 0.02, 1.3, 0.3, when, size=12, bold=True, color=col, align=PP_ALIGN.RIGHT)
    text(s, 1.4, y + 0.4, 5.1, h - 0.4, d, size=12, color="334155")
    y += h + 0.15
text(s, 0.6, 6.4, 6.0, 0.5, [[("Pourquoi la CEMAC d'abord : ", {"bold": True, "color": TEAL}),
                              ("même monnaie (FCFA), même banque centrale (BEAC), corridor Douala–N'Djaména.", {})]], size=11)
footer(s, 17, "Sources : DataReportal Digital 2025 (Cameroun, Centrafrique, Sénégal, Côte d'Ivoire, Guinée). Aucun partenariat international n'est encore signé.")
notes(s, "17. Expansion",
      "Notre expansion se fait en trois phases. Phase un : consolider le Tchad, d'abord N'Djaména, puis Moundou, "
      "Abéché et Sarh. Phase deux : ouvrir deux nouveaux pôles, le commerce et la billetterie internationale vers "
      "l'Afrique, la Turquie, la Chine, la Russie, les Émirats et l'Europe. Pour cela, nous devrons signer avec des "
      "compagnies aériennes, des agences et des fournisseurs de réservation ; ces partenariats restent à construire. "
      "Phase trois : l'Afrique, en commençant par la CEMAC. Le Cameroun et la Centrafrique partagent notre monnaie et "
      "notre banque centrale, et le corridor Douala–N'Djaména nous relie déjà. Viendront ensuite le Sénégal, la "
      "Côte d'Ivoire et la Guinée, des marchés plus connectés.")

# 18 — Financement ---------------------------------------------------------------------------
s = new_slide()
header(s, [[("Notre besoin : ", {}), ("15 000 000", {"strike": True, "color": GRAY}), (" 10 000 000 FCFA", {})]],
       "Le produit est financé par le fondateur ; l'argent levé sert au lancement commercial")
FUND = [("Recrutement et rémunération", 3.0), ("Marketing et communication", 2.0), ("Agents de terrain", 1.8),
        ("Infrastructure technique", 1.0), ("Administratif et juridique", 0.8), ("Prospection commerciale", 0.7),
        ("Partenariats", 0.4), ("Fonds de roulement", 0.3)]
cd = CategoryChartData()
cd.categories = [f for f, _ in FUND]
cd.add_series("M FCFA", [v for _, v in FUND])
gf = s.shapes.add_chart(XL_CHART_TYPE.PIE, Inches(4.55), Inches(1.6), Inches(4.4), Inches(5.2), cd)
ch = gf.chart
chart_style(ch, legend=True, size=10)
ch.has_title = False
pl = ch.plots[0]
pl.has_data_labels = True
pl.data_labels.show_value = True
pl.data_labels.show_percentage = False
pl.data_labels.number_format = '0.0" M"'
pl.data_labels.number_format_is_linked = False
pl.data_labels.font.size = Pt(10)
pl.data_labels.font.bold = True
pl.data_labels.font.color.rgb = rgb(WHITE)
pal = [TEAL, AMBER, MINT, DARK, "0EA5E9", "94A3B8", "B45309", "475569"]
for i, pt in enumerate(pl.series[0].points):
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = rgb(pal[i])
card(s, 0.6, 1.75, 3.75, 2.45, fill=LIGHT, line=None)
text(s, 0.8, 1.88, 3.4, 0.35, "Déjà réalisé par le fondateur", size=14, bold=True, color=TEAL)
text(s, 0.8, 2.3, 3.4, 1.85, ["Conception du projet", "Développement de la plateforme", "Mise en production",
                              "Apport en temps et en compétences, non rémunéré en A1"], size=12, spacing=4)
card(s, 0.6, 4.35, 3.75, 2.4, fill=DARK, line=None)
text(s, 0.8, 4.48, 3.4, 0.35, "Ce que finance la levée", size=14, bold=True, color=AMBER)
text(s, 0.8, 4.9, 3.4, 1.8, ["12 mois de lancement commercial", "Équipe de 5 personnes autour du fondateur",
                             "Acquisition des 10 000 premiers inscrits", "Structuration juridique et partenariats"],
     size=12, color=WHITE, spacing=4)
card(s, 9.2, 1.75, 3.5, 5.0, fill="F8FAFC")
text(s, 9.4, 1.88, 3.1, 0.35, "Calendrier des ressources", size=14, bold=True, color=TEAL)
rows = [("Dépenses déjà réalisées", "Développement et mise en production, payés par le fondateur"),
        ("Apport du fondateur", "Travail non rémunéré en A1 ; valorisation à préciser"),
        ("Besoin restant", "10 000 000 FCFA (A1), au lieu de 15 000 000"),
        ("Dépenses futures", "A2–A3 : financées par le CA et, si besoin, un tour d'amorçage")]
for i, (k, v) in enumerate(rows):
    yy = 2.35 + i * 1.08
    text(s, 9.4, yy, 3.1, 0.3, k, size=12, bold=True)
    text(s, 9.4, yy + 0.32, 3.1, 0.7, v, size=11, color="334155")
footer(s, 18, "Ventilation indicative, à affiner selon les devis réels. Détail : onglet Financement du modèle Excel.")
notes(s, "18. Le besoin de financement",
      "Je vous demande 10 millions de FCFA, et non plus 15. Je veux être précis sur ce que couvre cet argent. La conception, le "
      "développement et la mise en production de la plateforme sont déjà faits, à mes frais et sur mon temps : "
      "c'est mon apport. L'argent levé ne paie pas le développement passé ; il finance douze mois de lancement "
      "commercial. 3 millions pour l'équipe, 2 millions pour le marketing, 1,8 million pour les agents de terrain, "
      "1 million pour l'infrastructure, le reste pour la prospection, le juridique, les partenariats et une petite "
      "réserve. Cette ventilation sera affinée avec des devis réels.")

# 19 — Impact, équipe, partenaires ------------------------------------------------------------
s = new_slide()
header(s, "Impact : des emplois et des revenus pour les Tchadiens",
       "Emplois directs, revenus pour les prestataires, PME plus visibles")
# organigramme
ox, oy = 0.6, 1.8
def node(x, y, w, t, fill=WHITE, col=DARK, line=MID):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, 0.5, fill=fill, line=line, radius=0.2)
    text(s, x, y + 0.08, w, 0.35, t, size=10, bold=True, color=col, align=PP_ALIGN.CENTER)
node(1.9, oy, 2.4, "Direction générale", fill=DARK, col=WHITE, line=None)
subs = ["Technique", "Commercial", "Marketing", "Admin. et finances"]
line(s, 3.1, oy + 0.5, 3.1, oy + 0.75)
line(s, 1.25, oy + 0.75, 5.6, oy + 0.75)
for i, t in enumerate(subs):
    x = 0.6 + i * 1.45
    line(s, x + 0.65, oy + 0.75, x + 0.65, oy + 0.95)
    node(x, oy + 0.95, 1.3, t, fill=LIGHT, col=TEAL, line=None)
for i, t in enumerate(["Développeurs", "Agents de terrain", "Support client"]):
    x = 0.6 + [0, 1, 2][i] * 1.45
    line(s, x + 0.65, oy + 1.45, x + 0.65, oy + 1.7, dash=True)
    node(x, oy + 1.7, 1.3, t)
text(s, 0.6, 4.1, 5.5, 0.3, "Organisation cible ; recrutement progressif selon la croissance", size=10, italic=True, color=GRAY)
E = M["Equipe"]
data = [["Emplois et revenus", "A1", "A2", "A3"],
        ["Emplois directs"] + [str(int(x)) for x in E[-1][1:4]],
        ["Masse salariale (M FCFA)"] + [fr(x / 1e6, 1) for x in E[-1][7:10]],
        ["Prestataires inscrits*"] + [fr(x) for x in I["pros"]],
        ["Courses et livraisons / an"] + [fr(x) for x in I["mob_tx"]]]
table(s, 6.6, 1.8, 6.1, 2.2, data, [2.8, 1.1, 1.1, 1.1], size=11)
text(s, 6.6, 4.05, 6.1, 0.35, "* Prestataires qui gagnent des revenus via Maousang : opportunités, pas des emplois salariés.",
     size=10, italic=True, color=GRAY)
imp = [("users", "Emploi des jeunes"), ("moto", "Revenus des conducteurs"), ("cart", "Commerçants visibles"),
       ("briefcase", "Accès aux offres"), ("building", "PME digitalisées"), ("money", "Moins de frais de recherche")]
for i, (ic, t) in enumerate(imp):
    x = 0.6 + i * 2.03
    icon(s, ic, x, 4.6, 0.5, circle=TEAL)
    text(s, x + 0.58, 4.68, 1.4, 0.45, t, size=11, bold=True)
text(s, 0.6, 5.35, 12.1, 0.3, "Partenaires recherchés (aucun n'est encore signé)", size=13, bold=True, color=TEAL)
partners = ["Ministères", "Banques", "Paiement mobile", "Transporteurs", "Agences de voyage", "Agences immobilières",
            "Livraison", "Universités", "Entreprises", "Médias et agences", "Incubateurs"]
x, y = 0.6, 5.75
for pname in partners:
    w = 0.22 + 0.085 * len(pname)
    if x + w > 12.7:
        x, y = 0.6, y + 0.48
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, 0.38, fill="F1F5F9", line=MID, radius=0.5)
    text(s, x, y + 0.07, w, 0.28, pname, size=10, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    x += w + 0.12
footer(s, 19, "Salaires : estimations à valider (onglet Equipe). Rôle de chaque partenaire : voir le business plan, section 12.")
notes(s, "19. Impact, équipe et partenaires",
      "Maousang crée de l'emploi. En année un, six personnes, moi compris ; vingt et une en année deux ; quarante-huit "
      "en année trois, si la croissance suit. Au-delà des salariés, des milliers de conducteurs, de livreurs, de "
      "commerçants et d'agences pourront gagner des revenus grâce à la plateforme. Je les compte comme des "
      "opportunités, pas comme des emplois. Pour réussir, nous cherchons des partenaires : ministères, banques, "
      "opérateurs de paiement mobile, transporteurs, agences, universités, médias et incubateurs. Aucun n'est "
      "encore signé, et c'est précisément pour cela que je suis devant vous.")

# 20 — Appel à l'action ----------------------------------------------------------------------------
s = new_slide(DARK)
text(s, 0.8, 0.55, 11.5, 0.7, "Investir dans Maousang, maintenant", size=34, bold=True, color=WHITE)
reasons = ["Un problème réel, vécu chaque jour", "Une solution déjà développée et en production",
           "Un marché jeune où le mobile progresse", "Huit sources de revenus",
           "Une stratégie d'expansion par étapes", "Des emplois directs et des revenus pour les prestataires",
           "Un fondateur ingénieur IA, engagé à plein temps"]
for i, r in enumerate(reasons):
    y = 1.6 + i * 0.52
    icon(s, "check", 0.8, y, 0.36, circle=None, col="a")
    text(s, 1.3, y + 0.02, 5.6, 0.4, r, size=15, color=WHITE)
card(s, 7.35, 1.55, 5.2, 3.5, fill=TEAL, line=None)
text(s, 7.65, 1.75, 4.6, 0.35, "NOTRE DEMANDE", size=13, bold=True, color="D6E0F7")
text(s, 7.65, 2.05, 4.6, 1.1, [[("15 000 000 FCFA", {"strike": True, "size": 18, "color": "FFEDD5", "bold": False})], [("10 000 000 FCFA", {})]], size=36, bold=True, color=WHITE)
text(s, 7.65, 3.25, 4.6, 1.75, ["un accompagnement financier et stratégique pour 12 mois de lancement commercial,",
                              "et vos réseaux : paiement mobile, transporteurs, entreprises, institutions."],
     size=14, color=WHITE, spacing=6)
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.8, 5.45, 11.75, 1.15, fill=NAVY2, line=MINT, lw=1, radius=0.15)
text(s, 1.0, 5.55, 11.35, 0.95, [[("MAOUSANG", {"bold": True, "color": AMBER}),
                                  (" — Connecter les services, rapprocher les opportunités et construire "
                                   "l'économie numérique de demain.", {"color": WHITE, "italic": True})]],
     size=19, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.8, 6.8, 6.0, 0.35, [[("Giscard Destin", {"bold": True, "color": WHITE}),
                               ("  ·  Fondateur", {"color": "94A3B8"})]], size=13)
text(s, 7.0, 6.8, 5.55, 0.35, "maousang.vercel.app", size=13, bold=True, color=MINT, align=PP_ALIGN.RIGHT)
notes(s, "20. Appel à l'action",
      "Pour conclure : le problème est réel et vécu chaque jour. La solution est déjà développée et en ligne. Le "
      "marché est jeune et le mobile progresse. Nous avons huit sources de revenus, une expansion par étapes, un "
      "impact sur l'emploi, et un fondateur engagé à plein temps. Je vous demande donc 10 millions de FCFA, ainsi "
      "qu'un accompagnement stratégique et l'accès à vos réseaux. Maousang : connecter les services, rapprocher "
      "les opportunités et construire l'économie numérique de demain. Merci. Je suis prêt à répondre à vos questions, "
      "et à vous faire une démonstration en direct sur maousang.vercel.app.")

# 21 — Diapositive réservée à la version 5 minutes (retirée du deck complet par make_versions.py)
s = new_slide()
header(s, "L'application en action", "Une page IA, quatre services, en quelques secondes")
for i, (k, lab) in enumerate([("04_page_ia", "Page IA"), ("05_clando", "Clando"), ("07_bus", "Bus"),
                              ("08_emploi", "Emploi"), ("06_immobilier", "Immobilier")]):
    x = 0.75 + i * 2.45
    phone(s, k, lab, x, 1.65, w=2.15, h=4.45)
    text(s, x, 6.25, 2.15, 0.35, lab, size=14, bold=True, align=PP_ALIGN.CENTER, color=TEAL if i == 0 else DARK)
footer(s, 5, "Captures de l'application fournies par le fondateur (novembre 2026).")

# 22 — Version 5 minutes : les 4 services de lancement
s = new_slide()
header(s, "Nos 4 services de lancement", "Commencer simple : quatre besoins quotidiens, une seule application")
SERV = [("moto", "Mobilité", "Commander un moto-taxi (clando) depuis son téléphone.",
         "Citadins, conducteurs de moto-taxi", "Commission par course"),
        ("ticket", "Billetterie", "Acheter son billet de bus pour les voyages interurbains.",
         "Voyageurs, étudiants, compagnies de bus", "Commission par billet"),
        ("home", "Immobilier", "Rechercher et réserver un appartement à la journée.",
         "Expatriés, étrangers de passage, Tchadiens", "Commission par réservation"),
        ("briefcase", "Aide à l'emploi", "L'ATS fait la synthèse des CV et envoie les meilleurs profils aux recruteurs.",
         "Chercheurs d'emploi, entreprises, ONG", "Abonnement recruteur")]
for i, (ic, t, d, u, r) in enumerate(SERV):
    col, row = i % 2, i // 2
    x, y = 0.6 + col * 6.15, 1.75 + row * 2.45
    card(s, x, y, 5.95, 2.25, fill="F8FAFC")
    icon(s, ic, x + 0.25, y + 0.3, 0.95, circle=TEAL)
    text(s, x + 1.45, y + 0.25, 4.3, 0.45, t, size=20, bold=True)
    text(s, x + 1.45, y + 0.75, 4.3, 0.7, d, size=14)
    text(s, x + 1.45, y + 1.45, 4.3, 0.35, [[("Pour : ", {"bold": True, "color": TEAL}), (u, {})]], size=12)
    text(s, x + 1.45, y + 1.78, 4.3, 0.35, [[("Revenu : ", {"bold": True, "color": TEAL}), (r, {})]], size=12)
text(s, 0.6, 6.68, 12.1, 0.3, "Ensuite : commerce et billetterie internationale, selon la traction.", size=12, italic=True, color=GRAY)

# 23 — Version 5 minutes : appel à l'action avec trois packs
s = new_slide(DARK)
text(s, 0.8, 0.45, 11.7, 0.6, "Investir dans Maousang : trois packs au choix", size=32, bold=True, color=WHITE)
text(s, 0.8, 1.1, 11.7, 0.7, "Pour ce besoin de financement de 10 millions de FCFA, notre startup propose un panier "
     "de trois packs de retour sur investissement.", size=15, color="D6E0F7")
PACKS = [("users", "Pack 1 · Devenir associé", "Vous entrez au capital de la startup et contribuez aux décisions "
          "stratégiques, économiques et à la vision d'avenir."),
         ("money", "Pack 2 · Dividendes", "Vous percevez des dividendes dès que l'entreprise atteint son seuil "
          "de rentabilité."),
         ("trend", "Pack 3 · Part des revenus", "Vous recevez une rémunération calculée sur le chiffre d'affaires, "
          "selon le pourcentage négocié.")]
for i, (ic, t, d) in enumerate(PACKS):
    x = 0.8 + i * 3.95
    card(s, x, 2.05, 3.7, 3.05, fill=NAVY2, line=TEAL)
    icon(s, ic, x + 0.3, 2.3, 0.8, circle=TEAL)
    text(s, x + 0.3, 3.25, 3.15, 0.45, t, size=17, bold=True, color=AMBER)
    text(s, x + 0.3, 3.75, 3.15, 1.3, d, size=13, color=WHITE)
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.8, 5.4, 11.75, 0.95, fill=TEAL, radius=0.15)
text(s, 1.0, 5.47, 11.35, 0.8, [[("MAOUSANG", {"bold": True, "color": AMBER}),
                                 (" — Connecter les services, rapprocher les opportunités et construire "
                                  "l'économie numérique de demain.", {"color": WHITE, "italic": True})]],
     size=17, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.8, 6.55, 6.0, 0.35, [[("Giscard Destin", {"bold": True, "color": WHITE}),
                                ("  ·  Fondateur", {"color": "94A3B8"})]], size=13)
text(s, 7.0, 6.55, 5.55, 0.35, "maousang.vercel.app", size=13, bold=True, color=MINT, align=PP_ALIGN.RIGHT)
text(s, 0.8, 6.98, 11.7, 0.3, "Part au capital, seuil, pourcentage et durée : à négocier, puis à formaliser par contrat "
     "ou pacte d'associés.", size=9, color="94A3B8")

prs.save(OUT)

# ---------------------------------------------- Version éditable Avant / Après
prs2 = Presentation()
prs2.slide_width, prs2.slide_height = Inches(13.333), Inches(7.5)
s = prs2.slides.add_slide(prs2.slide_layouts[6])
bg(s, WHITE)
header(s, "Avant Maousang, après Maousang", "Plusieurs démarches dispersées → une seule application")
avant_apres(s)
s.notes_slide.notes_text_frame.text = open(os.path.join(ROOT, "livrables", "MAOUSANG_PROMPTS_ILLUSTRATIONS_3D.md")).read()
prs2.save(os.path.join(ROOT, "livrables", "MAOUSANG_AVANT_APRES_EDITABLE.pptx"))

# ------------------------------------------------------------------ Notes MD
words = sum(len(t.split()) for _, t in NOTES)
with open(NOTES_MD, "w") as f:
    f.write("# MAOUSANG — Texte oral du pitch\n\n")
    f.write(f"Durée visée : 8 à 12 minutes. Le texte compte environ {words} mots, soit environ "
            f"{round(words / 150)} minutes à un débit de 150 mots par minute. Le reste du temps sert à la "
            "démonstration et aux transitions.\n\n")
    f.write("Conseils : parler lentement, regarder le jury, montrer la plateforme en direct sur la diapositive 6 si "
            "la connexion le permet. Les chiffres cités sont sourcés (MAOUSANG_SOURCES.md) ou prévisionnels "
            "(MAOUSANG_FINANCIAL_MODEL.xlsx) : toujours dire « prévisionnel » ou « objectif » pour les seconds.\n\n")
    for t, n in NOTES:
        f.write(f"## Diapositive {t}\n\n{n}\n\n")
    f.write("## Questions probables du jury\n\n")
    qa = [("Pourquoi plusieurs pôles au lieu d'un seul ?",
           "Un compte unique réduit le coût d'acquisition : l'utilisateur qui vient pour un clando revient pour un billet ou un logement. Nous lançons les pôles progressivement selon la traction."),
          ("Un million d'inscrits en trois ans, est-ce réaliste ?",
           "C'est un objectif ambitieux, que je ne présente pas comme acquis. Le scénario prudent retient la moitié. Le modèle montre l'impact de chaque hypothèse."),
          ("Comment les paiements seront-ils encaissés ?",
           "Par paiement mobile (Airtel Money, Moov Money) et en espèces au démarrage. L'intégration fait partie du budget partenariats."),
          ("Qui sont vos concurrents ?",
           "Des acteurs spécialisés : Chadito, Blyt, SafeClando, Allons-y, emploi.td, Alwihda Info. Aucun ne combine les quatre pôles."),
          ("Que se passe-t-il si la trésorerie manque en année deux ?",
           "Nous ajustons les recrutements au chiffre d'affaires réel et préparons un relais : prêt d'honneur, banque ou tour d'amorçage.")]
    for q, a in qa:
        f.write(f"**{q}**\n\n{a}\n\n")
print("deck ok", OUT, "| mots de notes :", words)
