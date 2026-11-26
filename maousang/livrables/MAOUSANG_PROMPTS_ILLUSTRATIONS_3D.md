# Illustrations 3D « Avant / Après Maousang »

Le fichier `MAOUSANG_AVANT_APRES_EDITABLE.pptx` contient la diapositive Avant/Après avec deux emplacements vides : `ILLU_avant` et `ILLU_apres`. La même diapositive (n° 4) existe dans le deck principal.

## Comment faire

1. Générez deux images avec un outil d'images IA (Midjourney, DALL·E / ChatGPT, Ideogram, Leonardo, Bing Image Creator) en copiant les prompts ci-dessous.
2. Format : paysage, rapport **8:3** (par exemple 1600 × 600 pixels), PNG.
3. Enregistrez-les sous `maousang/assets/illustrations_3d/avant.png` et `apres.png`.
4. Lancez `python3 outils/insert_screenshots.py` : les deux images remplacent les emplacements.
   Sinon, dans PowerPoint : clic droit sur l'emplacement → Modifier l'image, ou supprimez le cadre et insérez l'image.

## Prompt « AVANT »

```
3D illustration, Pixar-style stylized characters, warm cinematic lighting, wide 8:3 banner.
A busy street in N'Djamena, Chad, under a hot hazy sky. Frustrated Chadian people:
a young man waiting in a long queue at a dusty bus station ticket counter, a woman
arguing about the price with a moto-taxi (clando) driver, a graduate holding paper CVs
in front of a crowded notice board, a family following an informal real-estate broker.
Clocks and banknotes floating subtly to suggest lost time and money.
Muted, slightly desaturated colors (dusty beige, grey). Respectful, realistic
Central African features and clothing. No text, no logos.
```

## Prompt « APRÈS »

```
3D illustration, Pixar-style stylized characters, bright optimistic lighting, wide 8:3 banner.
The same street in N'Djamena, Chad, now calm and modern. Smiling Chadian people using a
smartphone app with an orange-and-black interface: a young woman booking a bus ticket,
a moto-taxi driver in an orange vest and helmet receiving a ride request, a graduate
getting a job notification, a family visiting a nice house found online.
Vivid palette dominated by orange (#EA580C), black and white, soft gold highlights.
Respectful, realistic Central African features and clothing. No text, no logos.
```

## Conseils

- Gardez le **même style** pour les deux images (même outil, même prompt de base) pour que la comparaison soit lisible.
- Vérifiez les mains, les visages et les plaques : refaites l'image si un détail est déformé.
- N'ajoutez pas de vrais logos de marques tierces.
- Vérifiez les droits d'usage commercial de l'outil choisi.
