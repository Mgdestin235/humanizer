# MAOUSANG — Dossier de levée de fonds

## Livrables (`livrables/`)

| Fichier | Contenu |
|---|---|
| `MAOUSANG_PITCH_DECK.pptx` | Présentation modifiable de 20 diapositives. Graphiques et tableaux natifs ; texte oral dans les notes de chaque diapositive |
| `MAOUSANG_PITCH_DECK.pdf` | Version PDF de la présentation |
| `MAOUSANG_BUSINESS_PLAN.pdf` | Business plan de 14 pages : marché, modèle économique, prévisions, expansion, financement, risques |
| `MAOUSANG_FINANCIAL_MODEL.xlsx` | Modèle financier sur 3 ans, 3 scénarios, avec formules. Cellules bleues = hypothèses modifiables |
| `MAOUSANG_SOURCES.md` | Sources, liens, dates, hypothèses et formules |
| `MAOUSANG_SPEAKER_NOTES.md` | Texte oral complet (environ 12 minutes) et questions probables du jury |

## À faire avant de présenter

1. **Insérer les vraies captures d'écran.** Le site n'a pas pu être consulté pendant la rédaction. Le deck contient donc 14 emplacements nommés, du démarrage jusqu'aux fonctionnalités. Sur votre ordinateur :

   ```bash
   cd maousang/outils
   npm install playwright && npx playwright install chromium
   node capture_maousang.js guide     # navigateur ouvert : allez sur chaque écran, puis Entrée
   pip install python-pptx pillow
   python3 insert_screenshots.py      # remplace les emplacements dans le deck
   python3 build_business_plan.py && node render_pdf.js business_plan.html ../livrables/MAOUSANG_BUSINESS_PLAN.pdf
   ```

   Vous pouvez aussi faire vos captures à la main et les enregistrer dans `assets/captures/` sous ces noms :
   `01_accueil`, `02_inscription`, `03_connexion`, `04_tableau_de_bord`, `05_billetterie_recherche`, `06_billetterie_resultats`, `07_clando_demande`, `08_livraison`, `09_emploi_offres`, `10_emploi_ats`, `11_immobilier_recherche`, `12_immobilier_annonce`, `13_annonces`, `14_assistant_ia` (format `.png`).

2. **Aligner les couleurs** du deck sur l'identité visuelle réelle de Maousang (actuellement : vert sarcelle `0F766E`, ambre `F59E0B`, bleu nuit `0B1B2B`).
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
