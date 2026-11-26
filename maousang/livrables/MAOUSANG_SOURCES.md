# MAOUSANG — Sources, données et hypothèses

Recherche documentaire faite le 26 novembre 2026. Ce fichier liste chaque chiffre du pitch, sa source, sa date et son lien avec Maousang. Il sépare trois types d'information :

- **Donnée sourcée** : publiée par un organisme identifié.
- **Donnée relayée** : chiffre d'un organisme officiel, lu dans un média ou un blog. Il faut le confirmer dans la publication d'origine avant usage officiel.
- **Hypothèse** : choix de modélisation de Maousang, à tester sur le terrain.

## 1. Limite importante : le site de Maousang n'a pas pu être inspecté

L'environnement de travail n'avait pas accès à `maousang.vercel.app` : la politique réseau a bloqué l'hôte, et la demande d'accès a été refusée. En conséquence :

- Les fonctionnalités décrites viennent du cahier des charges du fondateur, pas d'une inspection du site.
- Les couleurs du deck (vert sarcelle `#0F766E`, ambre `#F59E0B`, bleu nuit `#0B1B2B`) sont une proposition. Il faut les aligner sur l'identité visuelle réelle du site.
- Les captures d'écran sont remplacées par des emplacements nommés. Le script `outils/capture_maousang.js` les capture, puis `outils/insert_screenshots.py` les insère (voir `LISEZ-MOI.md`).

## 2. Marché tchadien

| # | Indicateur | Chiffre | Année | Organisme | Lien | Rapport avec Maousang |
|---|---|---|---|---|---|---|
| 1 | Population totale | 21,1 millions | Oct. 2025 | Nations unies, via DataReportal *Digital 2026: Chad* | https://datareportal.com/reports/digital-2026-chad | Taille du pays ; ce n'est pas le nombre de clients |
| 2 | Population (série précédente) | 20,8 millions (déduit : 14,5 M connexions = 69,8 %) | Janv. 2025 | DataReportal *Digital 2025: Chad* | https://datareportal.com/reports/digital-2025-chad | Contrôle de cohérence |
| 3 | Part de population urbaine | 25,1 % | Fin 2025 | DataReportal *Digital 2026: Chad* (Nations unies) | https://datareportal.com/reports/digital-2026-chad | Base du SAM : ≈ 5,3 M de citadins |
| 4 | Population de N'Djaména (agglomération) | ≈ 1 656 000 | 2024 | Nations unies (World Urbanization Prospects), via Macrotrends | https://www.macrotrends.net/global-metrics/cities/20420/ndjamena/population | Premier marché de lancement. Chiffre officiel INSEED à confirmer (RGPH-3 en cours) |
| 5 | Connexions mobiles | 15,5 millions (73,3 % de la population) | Fin 2025 | GSMA Intelligence, via DataReportal | https://datareportal.com/reports/digital-2026-chad | Le téléphone est déjà là. Une personne peut avoir plusieurs SIM |
| 6 | Connexions mobiles (série précédente) | 14,5 millions, dont 57,3 % en haut débit (3G, 4G, 5G) | Janv. 2025 | GSMA Intelligence, via DataReportal | https://datareportal.com/reports/digital-2025-chad | Tendance : +1 M de connexions en un an |
| 7 | Utilisateurs d'Internet | 2,79 millions (≈ 13 %) | Oct. 2025 | Kepios, via DataReportal *Digital 2026* | https://datareportal.com/reports/digital-2026-chad | **TAM** de Maousang |
| 8 | Utilisateurs d'Internet (autre mesure) | 13 % de la population a utilisé Internet sur 3 mois | 2024-2025 | Internet Society Pulse | https://pulse.internetsociety.org/en/reports/td | Confirme l'ordre de grandeur |
| 9 | Identités actives sur les réseaux sociaux | 2,38 millions | Oct. 2025 | Kepios, via DataReportal | https://datareportal.com/reports/digital-2026-chad | Audience des campagnes digitales |
| 10 | Utilisateurs Facebook | 1 559 700 | Janv. 2026 | NapoleonCat (audience publicitaire) | https://stats.napoleoncat.com/facebook-users-in-chad/2026/01/ | Canal principal des campagnes et des pages influentes |
| 11 | Comptes de monnaie électronique ouverts | 6 254 862 | 31 déc. 2024 | BEAC, **chiffre relayé** par un blog | https://blog.iambeezy.app/fr/arnaques-mobile-money-tchad-2026/ | Paiement mobile disponible (Airtel Money, Moov Money). À confirmer dans le rapport BEAC |
| 12 | Coût des coupures d'Internet | ≈ 38 millions USD | 2024 | Top10VPN, relayé par Tchadinfos | https://tchadinfos.com/coupure-dinternet-au-tchad-en-2024-les-pertes-economiques-estimees-a-38-millions-usd-en-2024-selon-top10vpn/ | Illustration du « coût de la non-connectivité » |
| 13 | Croissance du PIB prévue | 3,9 % par an en moyenne (1,2 % par habitant) | 2026-2027 | Banque mondiale | https://www.banquemondiale.org/fr/country/chad/overview | Contexte macroéconomique |

**Remarque sur les séries DataReportal.** Le rapport 2024 indiquait 4,18 M d'internautes, le rapport 2025 en indique 2,74 M. La baisse vient d'une révision des sources, pas d'une chute réelle. Ce pitch retient la série la plus récente (2,79 M, oct. 2025). Une édition *Digital 2027* (oct. 2026) existe : elle indique environ 21,7 M d'habitants et 16,8 M de connexions mobiles. Il faut la vérifier en ligne avant de citer ces valeurs.

## 3. Secteurs de Maousang

| Secteur | Donnée | Année | Source | Lien | Usage dans le pitch |
|---|---|---|---|---|---|
| Billetterie | N'Djaména–Moundou 12 500 FCFA ; –Sarh 17 500 ; –Abéché 25 000 ; –Doba 14 000 ; –Bongor 8 000 | 2023-2024 | Association de défense des consommateurs (ADC), Alwihda Info, Tchadinfos | https://www.alwihdainfo.com/tchad-l-adc-denonce-l-augmentation-abusive-des-prix-des-transports-interurbains-a126913/ ; https://tchadinfos.com/2023/09/19/tchad-laugmentation-des-tarifs-du-transport-touche-egalement-les-destinations-du-sud/ | Prix moyen du billet dans le modèle : 15 000 FCFA (hypothèse) |
| Billetterie | Départs vers l'est et le nord depuis Diguel, vers le sud depuis Chagoua ; aucun tarif officiel publié | 2026 | Guide de voyage (blog) | https://blog.iambeezy.app/fr/voyager-villes-tchad-cout-trajet-2026/ | Problème : vente au guichet |
| Mobilité | Programme de réglementation et d'identification des moto-taxis à N'Djaména (200 conducteurs équipés au lancement) | 19 sept. 2026 | Tchadinfos | https://tchadinfos.com/2026/09/19/securite-lancement-du-programme-de-reglementation-et-didentification-des-motos-taxis-a-ndjamena/ | Besoin de traçabilité ; partenariat possible avec la mairie |
| Immobilier | Déficit estimé à 1,5 million de logements ; programme national d'habitat avec ONU-Habitat | Nov. 2026 | Tchadinfos | https://tchadinfos.com/2026/11/04/tchad-le-gouvernement-prepare-un-programme-national-dhabitat-resilient/ | Taille du besoin en logement |
| Immobilier | Rareté des logements à louer à N'Djaména ; salaire moyen cité entre 60 000 et 100 000 FCFA | 2023 | Tchadinfos | https://tchadinfos.com/2023/11/05/societe-vers-une-crise-de-logement-a-ndjamena/ | Calibrage des prix et des salaires |
| Emploi | Chômage des 15-24 ans : 1,45 % (définition BIT, emploi informel non compté) | 2024 | Banque mondiale (WDI), via FRED | https://fred.stlouisfed.org/series/SLUEM1524ZSTCD | **Non utilisé comme argument** : ce taux mesure mal le sous-emploi dans une économie informelle |

## 4. Concurrents (aucun chiffre d'affaires, d'utilisateurs ou de part de marché n'est cité)

| Acteur | Ce qui a été vérifié | Source | Lien |
|---|---|---|---|
| Chadito | Application de petites annonces (voitures, location, emploi, électronique) ; vérification des vendeurs (KYC) | App Store, Google Play | https://apps.apple.com/us/app/chadito/id6757854742 ; https://play.google.com/store/apps/details?id=com.chadito.app |
| Blyt | Taxi à N'Djaména ; prix affiché avant la course ; chauffeurs identifiés ; applications passager et chauffeur | Google Play, App Store | https://play.google.com/store/apps/details?id=blyt.chad.taxi.passenger ; https://apps.apple.com/us/app/blyt-chad-local-taxi/id6760299644 |
| SafeClando | Application de moto-taxi à N'Djaména | Fiche Liners | https://liners.com/safeclando |
| Allons-y Taxi Privé Tchad | Réservation de taxi ; français, anglais, arabe (fiche tierce, non vérifiée) | Softonic | https://allons-y-taxi-prive-tchad.en.softonic.com/android |
| emploi.td | Site d'offres d'emploi et de recrutement | Site | https://www.emploi.td/ |
| JobRapide, consult.africa | Agrégateurs d'offres d'emploi et d'appels d'offres incluant le Tchad | Sites | https://www.jobrapide.org/region/tchad/ ; https://consult.africa/pays/td/ |
| Alwihda Info (rubrique annonces) | Annonces immobilières gratuites, par web et SMS | Site | https://www.alwihdainfo.com/annonces-immobilieres-au-tchad-a3559/ |
| GoAfrica Online | Annuaire de professionnels de l'immobilier | Site | https://www.goafricaonline.com/td/annuaire/immobilier |
| Agences de bus interurbaines | Vente au guichet ; tarifs non publiés officiellement | Presse et guide | voir section 3 |
| **Wadini** | Aucune présence publique trouvée sous ce nom | Recherche web | — À vérifier par le fondateur |
| **Annoncena** | Aucune présence publique trouvée sous ce nom | Recherche web | — À vérifier par le fondateur |
| **Tchad Emploi** | Pas de site exact trouvé ; les plus proches sont emploi.td et le blog JobTchad | Recherche web | https://tchademploisetcarrieres.blogspot.com/ |

La matrice de positionnement du deck est **qualitative** : elle place les acteurs selon le nombre de domaines couverts et la présence d'outils intelligents décrits publiquement.

## 5. Marchés d'expansion

| Pays | Population | Internautes | Pénétration | Date | Source |
|---|---|---|---|---|---|
| Cameroun | 29,5 M | 12,4 M | 41,9 % | Janv. 2025 | https://datareportal.com/reports/digital-2025-cameroon |
| Centrafrique | 5,42 M | 839 000 | 15,5 % | Janv. 2025 | https://datareportal.com/reports/digital-2025-central-african-republic |
| Sénégal | 18,7 M | 11,3 M | 60,6 % | Janv. 2025 | https://datareportal.com/reports/digital-2025-senegal |
| Côte d'Ivoire | 32,3 M | 12,8 M | 39,6 % | Janv. 2025 | https://datareportal.com/reports/digital-2025-cote-divoire |
| Guinée | 14,9 M | 3,96 M | 26,5 % | Janv. 2025 | https://datareportal.com/reports/digital-2025-guinea |

Le Cameroun et la Centrafrique sont prioritaires parce qu'ils partagent avec le Tchad le franc CFA (XAF) et la Banque des États de l'Afrique centrale (BEAC). Le Sénégal et la Côte d'Ivoire utilisent le franc CFA d'Afrique de l'Ouest (XOF), et la Guinée le franc guinéen.

## 6. Hypothèses de Maousang (non validées par le marché)

Toutes ces valeurs sont modifiables dans `MAOUSANG_FINANCIAL_MODEL.xlsx` (cellules bleues).

| Hypothèse | Prudent | Intermédiaire | Ambitieux | Justification |
|---|---|---|---|---|
| Réalisation de l'objectif d'inscrits (10 k, 100 k, 1 M) | 50 % | 100 % | 120 % | Objectifs du fondateur |
| Actifs mensuels / inscrits (A1 → A3) | 30 → 20 % | 35 → 25 % | 40 → 30 % | L'activité baisse quand la base grandit |
| Part des actifs utilisant la mobilité | 35 % | 40 % | 45 % | Usage le plus fréquent en ville |
| Courses ou livraisons par mois et par utilisateur | 3 | 4 | 5 | Usage hebdomadaire |
| Prix moyen d'une course ou livraison | 1 000 FCFA | 1 000 FCFA | 1 200 FCFA | Mélange de courses courtes et de livraisons |
| Commission mobilité | 8 % | 10 % | 12 % | En dessous des commissions VTC habituelles |
| Part des actifs achetant un billet ; billets par an | 10 % ; 2 | 15 % ; 2 | 20 % ; 2 | Voyages familiaux et d'études |
| Prix moyen du billet ; commission | 15 000 ; 4 % | 15 000 ; 5 % | 15 000 ; 6 % | Prix observés en section 3 |
| Offre d'emploi ; ATS premium | 10 000 FCFA ; 25 000 FCFA/mois | idem | idem | Tarifs d'entrée pour les PME |
| Annonce immobilière sponsorisée | 5 000 FCFA/mois | idem | idem | Accessible aux particuliers |
| Nuitée réservée ; commission | 20 000 FCFA ; 10 % | idem | idem | Résidences meublées |
| Prestataires / inscrits ; part abonnée ; prix | 2 % ; 4 % ; 5 000 | 2 % ; 6 % ; 5 000 | 2 % ; 8 % ; 5 000 | Conducteurs, agences, recruteurs |
| Forfait publicitaire mensuel | 50 000 FCFA | idem | idem | PME locales |
| Parrainage | 20 % des nouveaux inscrits, 500 FCFA par filleul | idem | idem | Crédit de course ou bon d'achat |
| Frais de paiement mobile | 3 % du CA | idem | idem | Ordre de grandeur, à négocier |
| Usage d'Internet en ville (pour le SAM) | 30 % | 30 % | 30 % | Supérieur à la moyenne nationale (13 %) |

Les salaires (onglet Equipe) sont des estimations pour N'Djaména. Il faut les valider avec un cabinet RH et le Code du travail tchadien.

## 7. Formules principales

- Inscrits moyens = (inscrits début d'année + inscrits fin d'année) / 2
- Actifs mensuels (MAU) = inscrits moyens × taux d'activité
- CA mobilité = MAU × part mobilité × courses par mois × 12 × prix moyen × commission
- CA billetterie = MAU × part billetterie × billets par an × prix du billet × commission
- CA emploi = entreprises × offres × prix de l'offre + abonnés ATS × prix × 12
- CA immobilier = annonces sponsorisées × prix × 12 + nuitées × prix de la nuitée × commission
- CA abonnements = inscrits fin × 2 % × part abonnée × prix × 12
- CA publicité = annonceurs × forfait × 12
- Taux de conversion payant = clients payants / inscrits moyens
- Revenu moyen par client payant = CA total / clients payants
- Résultat opérationnel = CA total − (masse salariale + marketing + technique + opérations + frais de paiement)
- TAM = internautes ; SAM = population urbaine × usage urbain ; SOM = 5 %, 10 % ou 20 % du SAM
