MAKKADEV - MONTAGE VIDÉO INSTITUTIONNEL
=======================================

CONTENU
- MakkaDev_Video_Finale.mp4   Vidéo finale : 1080x1920 (9:16), 30 i/s, H.264 High + AAC 48 kHz, 60,5 s, ~40 Mo.
- MakkaDev_SousTitres.srt     28 sous-titres français, texte exact de la voix off.
- MakkaDev_Timeline.json      15 plans, coupes, vitesses, transitions, textes, sous-titres.
- MakkaDev_Projet/            Projet réutilisable (voir plus bas).

TERMINÉ
- Voix off ElevenLabs intégrée (texte non modifié), calée avec les plans et les sous-titres.
- 15 plans choisis après analyse des vidéos : trajet en voiture, arrivée, marche de l'équipe,
  parking, couloir, ascenseur. Ordre réorganisé pour raconter le départ jusqu'à l'arrivée.
- Stabilisation légère, couleurs naturelles (contraste/saturation +4 à 6 %), fondus de 0,4 s.
- Ralenti léger (x0,9) sur le plan de l'équipe, ralenti x0,5 sur le plan final.
- Textes animés selon le plan demandé ; sous-titres dans la zone sûre (bas : 370 px, droite : 140 px).
- Audio des vidéos d'origine coupé (voix off présente presque tout le temps).
- Musique baissée automatiquement pendant la voix. Niveau final -16,3 LUFS, crête -1,3 dBFS.
- Vérifié : lecture complète sans erreur, aucune image noire sauf le fondu final voulu.

À FAIRE / À SAVOIR
1. LOGO : aucun logo MakkaDev n'était dans les fichiers fournis. Aucun logo n'a été créé.
   Le texte "MAKKADEV" sert de signature finale. Envoyez le logo pour l'ajouter.
2. MUSIQUE : vous n'avez pas fourni de musique. J'ai généré une musique instrumentale originale
   (scripts/music.py), donc sans droits d'auteur. Elle est simple. Pour la remplacer par votre
   musique libre de droits : python3 build.py --music votre_fichier.mp3
3. FICHIERS SOURCES : vous avez fourni 14 vidéos (WA0026 à WA0039), pas 9, et leurs noms
   (134126...) ne correspondent pas. Les plans ont été choisis d'après leur contenu réel.
   Le plan "134132" (équipe qui marche) est VID-...WA0030.mp4 (équipe face caméra) et WA0026 (de dos).
4. ENSEIGNE VISIBLE : sur certains plans, une enseigne "HÔTEL DE N'DJARI" apparaît en petit sur
   le bâtiment (surtout WA0034 et WA0035). J'ai évité ces passages quand c'était possible, mais
   le titre "Ministère des Finances" s'affiche sur des images de ce bâtiment. Vérifiez que cela vous convient.
5. Aucune réunion, signature ou attribution de marché n'est montrée ni écrite. La participation
   à l'appel d'offres est présentée comme une démarche.
6. Durée : 60,5 s (cible 60-75 s), calée sur la voix off (52 s) plus un plan final.
7. Test sur Android, WhatsApp, TikTok et Instagram : impossible ici. Le format est standard
   (H.264 High 4.1, yuv420p, AAC, faststart), compatible avec ces réseaux. Faites un essai
   d'envoi. Pour WhatsApp (limite ~16 Mo), réencodez : ffmpeg -i MakkaDev_Video_Finale.mp4 -crf 28 -c:a copy sortie.mp4

AJUSTER LE MONTAGE
Projet : MakkaDev_Projet/
  config.json   Plans (source, début, durée, vitesse), textes, sous-titres, durées, fondus.
  build.py      Relance tout le montage : python3 build.py  (nécessite ffmpeg avec vidstab/libass, Python 3, numpy, Pillow)
  scripts/music.py   Générateur de la musique.
  sources/ et audio/ Vidéos d'origine, voix off, musique générée.
Exemples : changer un plan = modifier "src"/"ss"/"dur" dans "shots" ; changer un texte = "titles" ;
corriger un sous-titre = "subtitles_voice_time" (temps de la voix). Un rendu complet prend ~6 minutes
(le plan en ralenti interpolé est le plus long) ; les plans inchangés sont ensuite réutilisés.

VERSION YOUTUBE HORIZONTALE (16:9)
- MakkaDev_Video_YouTube_Horizontale.mp4 : 1920x1080, vraie vidéo horizontale (image recadrée, sans bandes).
- Les vidéos d'origine sont verticales : chaque plan est recadré en 16:9 (fenêtre réglable par plan avec "cy"
  dans config.json) puis agrandi. L'image est donc moins nette et le haut/bas des plans est coupé.
- Pour la refaire : python3 build.py --landscape --work work_h
