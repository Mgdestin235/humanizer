# Brief de voix off — Cabinet Médical LA FOI

À donner à ElevenLabs (ou à un comédien). Texte exact : `texte-voix-off.txt` (un paragraphe par unité, ne pas fusionner les paragraphes).

## Voix demandée
- Voix **masculine**, française, professionnelle, **chaleureuse et dynamique**.
- Ton **rassurant**, avec une **touche d'émotion** sur la phrase « chaque patient mérite écoute, attention et dignité ».
- Sourire audible, énergie maîtrisée, sans cris ni emphase publicitaire excessive.
- Rythme : environ 150 mots par minute. Durée attendue : 1 min 30 à 1 min 45.

## Réglages ElevenLabs à essayer (points de départ, à ajuster à l'oreille)
- Modèle : Multilingual v2 (respecte bien les pauses entre paragraphes).
- Stabilité 40–50 % ; similarité 70–80 % ; style 25–35 % ; « Speaker boost » activé ; vitesse 1.0.
- Dans la bibliothèque de voix : filtrez langue « français », genre « masculin », usage « publicité » ou « narration ». Écoutez 2 ou 3 voix sur la première phrase avant de choisir.

## Points à vérifier à l'écoute
- « LA FOI » se prononce « la foi ». « 20 octobre 2026 » est lu en entier, deux fois (début et rendez-vous).
- Une pause nette (plus de 0,5 s) entre chaque paragraphe. Les pauses internes (virgules) restent courtes.
- Aucune phrase ajoutée, supprimée ou reformulée par la voix.

## Après l'export
1. Enregistrez le MP3 sous `assets/audio/voix-off.mp3` et renseignez-le dans `src/config/audio.json` (`voice`).
2. `npm run align:auto` puis `npm run build` ; vérifiez le tableau affiché.
3. `npm run render` puis `npm run qc -- output/la-foi_9x16.mp4`.
