"""Produit deux decks à partir du deck généré par build_deck.py :
- MAOUSANG_PITCH_DECK.pptx : version complète (20 diapositives) ;
- MAOUSANG_PITCH_5MIN.pptx : version courte (10 diapositives, texte oral de 5 minutes maximum).
"""
import json
import os
import re

from pptx import Presentation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIV = os.path.join(ROOT, "livrables")
FULL = os.path.join(LIV, "MAOUSANG_PITCH_DECK.pptx")
SHORT = os.path.join(LIV, "MAOUSANG_PITCH_5MIN.pptx")
I = json.load(open(os.path.join(ROOT, "outils", "model_values.json")))["Intermediaire"]


def fr(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


# Ordre de la version courte : numéros des diapositives du deck généré (21 = « L'application en action »)
ORDER = [1, 3, 4, 5, 21, 11, 14, 16, 18, 20]
NOTES = [
    "Bonjour. Je suis Giscard Destin, ingénieur en intelligence artificielle et data scientist, fondateur de "
    "Maousang. Maousang réunit dans une seule application les services du quotidien au Tchad : se déplacer, "
    "voyager, trouver un emploi et un logement. La plateforme est déjà développée et en ligne.",
    "Aujourd'hui, à N'Djaména, chaque besoin demande un déplacement, un intermédiaire ou du bouche-à-oreille : "
    "héler un clando, faire la queue au guichet pour un billet, payer un démarcheur pour un logement, chercher "
    "des offres d'emploi dispersées. Résultat : du temps et de l'argent perdus, et des entreprises invisibles.",
    "Avant Maousang, l'utilisateur jongle entre l'immobilier, la mobilité, l'emploi, le commerce et les services, "
    "sans solution unique. Avec Maousang, tout est dans son téléphone, en quelques minutes.",
    "Maousang compte quatre pôles déjà développés : la billetterie de bus, la mobilité Clando avec la livraison, "
    "l'emploi avec un ATS intelligent qui trie les CV, et l'immobilier. Le commerce et la billetterie "
    "internationale arriveront en phase deux. Un assistant IA guide chaque utilisateur vers le bon service.",
    "Voici l'application réelle. La page IA demande : « Que cherchez-vous aujourd'hui ? ». En un geste, "
    "l'utilisateur commande un clando ou une livraison, recherche un bus, consulte des offres d'emploi ou trouve "
    "un logement, en longue ou en courte durée.",
    "Le Tchad compte 21 millions d'habitants, dont 5 millions en ville, et 15,5 millions de connexions mobiles, "
    "mais seulement 2,8 millions d'internautes. Le téléphone est déjà là ; l'usage reste à conquérir. Notre cible "
    "de départ : les internautes urbains, environ 1,6 million de personnes, à commencer par N'Djaména.",
    "Chercher est gratuit. Nous gagnons de l'argent sur les transactions et la visibilité : commissions sur les "
    "courses et les billets, abonnements des professionnels, offres d'emploi payantes, ATS premium, annonces "
    "sponsorisées et publicité. Huit sources de revenus, avec des tarifs que nous testerons sur le terrain.",
    f"Nos objectifs : 10 000 inscrits la première année, 100 000 la deuxième, un million la troisième. Dans le "
    f"scénario intermédiaire, le chiffre d'affaires atteint {fr(I['rev_total'][2] / 1e6)} millions de FCFA en "
    f"année trois, avec un résultat positif de {fr(I['ebit'][2] / 1e6)} millions. Ce sont des prévisions : "
    "toutes les hypothèses sont dans notre modèle Excel.",
    "Le développement est déjà fait, à mes frais. Nous demandons 10 millions de FCFA, au lieu des 15 prévus au "
    "départ, pour douze mois de lancement commercial : 3 millions pour l'équipe, 2 pour le marketing, 1,8 pour "
    "les agents de terrain, le reste pour l'infrastructure, le juridique et les partenariats.",
    "Un problème réel, une solution déjà en ligne, un marché qui s'ouvre et un fondateur engagé. Investissez "
    "10 millions de FCFA dans Maousang et ouvrez-nous vos réseaux. Maousang : connecter les services, rapprocher "
    "les opportunités et construire l'économie numérique de demain. Merci.",
]


def keep(path_in, path_out, order, notes=None):
    prs = Presentation(path_in)
    lst = prs.slides._sldIdLst
    ids = list(lst)
    for el in ids:
        lst.remove(el)
    for n in order:
        lst.append(ids[n - 1])
    for el in ids:
        if el not in list(lst):
            prs.part.drop_rel(el.rId)
    for i, slide in enumerate(prs.slides, 1):
        for shp in slide.shapes:  # renumérote le pied de page « MAOUSANG · n »
            if shp.has_text_frame and shp.text_frame.text.startswith("MAOUSANG  ·  "):
                runs = shp.text_frame.paragraphs[0].runs
                runs[0].text = f"MAOUSANG  ·  {i}"
                for r in runs[1:]:
                    r.text = ""
        if notes:
            slide.notes_slide.notes_text_frame.text = notes[i - 1]
    prs.save(path_out)


keep(FULL, SHORT, ORDER, NOTES)
keep(FULL, FULL, list(range(1, 21)))

words = sum(len(n.split()) for n in NOTES)
titles = ["Couverture", "Le problème", "Avant / Après", "La solution", "L'application en action", "Le marché",
          "Le modèle économique", "Les projections", "Le financement : 10 M FCFA", "Appel à l'action"]
with open(os.path.join(LIV, "MAOUSANG_SPEAKER_NOTES_5MIN.md"), "w") as f:
    f.write(f"# MAOUSANG — Pitch de 5 minutes\n\n{len(NOTES)} diapositives, environ {words} mots, soit environ "
            f"{round(words / 130, 1)} minutes à 130 mots par minute. Il reste environ 30 secondes de marge.\n\n"
            "Règle : environ 30 secondes par diapositive. Ne lisez pas les chiffres affichés : dites seulement le message.\n\n")
    for i, (t, n) in enumerate(zip(titles, NOTES), 1):
        f.write(f"## {i}. {t}\n\n{n}\n\n")
print("versions ok | mots 5 min :", words)
