# MAOUSANG — Dossier de levée de fonds

## Livrables (`livrables/`)

| Fichier | Contenu |
|---|---|
| `MAOUSANG_PITCH_DECK.pptx` | Présentation modifiable de 20 diapositives. Graphiques et tableaux natifs ; texte oral dans les notes de chaque diapositive |
| `MAOUSANG_PITCH_DECK.pdf` | Version PDF de la présentation |
| `MAOUSANG_PITCH_5MIN.pptx` et `.pdf` | Version courte : 10 diapositives pour un pitch de 5 minutes |
| `MAOUSANG_SPEAKER_NOTES_5MIN.md` | Texte oral de la version 5 minutes (environ 450 mots) |
| `MAOUSANG_BUSINESS_PLAN.pdf` | Business plan de 14 pages : marché, modèle économique, prévisions, expansion, financement, risques |
| `MAOUSANG_FINANCIAL_MODEL.xlsx` | Modèle financier sur 3 ans, 3 scénarios, avec formules. Cellules bleues = hypothèses modifiables |
| `MAOUSANG_SOURCES.md` | Sources, liens, dates, hypothèses et formules |
| `MAOUSANG_AVANT_APRES_EDITABLE.pptx` | Diapositive Avant/Après modifiable, avec 2 emplacements d'illustrations 3D |
| `MAOUSANG_PROMPTS_ILLUSTRATIONS_3D.md` | Prompts pour générer les illustrations 3D |
| `MAOUSANG_SPEAKER_NOTES.md` | Texte oral complet (environ 12 minutes) et questions probables du jury |

## À faire avant de présenter

1. **Illustrations 3D Avant/Après.** Suivez `livrables/MAOUSANG_PROMPTS_ILLUSTRATIONS_3D.md`, enregistrez `avant.png` et `apres.png` dans `assets/illustrations_3d/`, puis lancez `python3 outils/insert_screenshots.py` (deck principal) et `python3 outils/insert_screenshots.py livrables/MAOUSANG_AVANT_APRES_EDITABLE.pptx`. Les 8 captures de l'application sont déjà insérées (`assets/captures/`).

2. **Couleurs :** orange `EA580C`, noir et blanc, repris des captures de l'application.
3. **Vérifier les points signalés** dans `MAOUSANG_SOURCES.md` : chiffre BEAC du paiement mobile, population de N'Djaména selon l'INSEED, concurrents Wadini et Annoncena.
4. **Ajouter vos coordonnées** (e-mail, téléphone) sur la dernière diapositive. Elles n'ont pas été ajoutées parce qu'elles n'ont pas pu être vérifiées.
5. **Ajouter des photographies** de N'Djaména (clandos, gare routière, quartiers) si vous en avez les droits. Le deck utilise des illustrations vectorielles et des cartes schématiques.

## Régénérer les fichiers (`outils/`)

| Script | Rôle |
|---|---|
| `build_model.py` | Crée le modèle Excel. Ensuite, LibreOffice recalcule et `model_values.json` reprend les résultats |
| `make_assets.py` + `render_svg.js` | Icônes, cartes et illustration de couverture |
| `build_deck.py` | Deck PowerPoint et notes orales |
| `build_business_plan.py` + `render_pdf.js` | Business plan HTML puis PDF |
| `capture_maousang.js`, `insert_screenshots.py` | Captures d'écran réelles |
