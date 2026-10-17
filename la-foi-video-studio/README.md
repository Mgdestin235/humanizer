# Studio vidéo — Cabinet Médical LA FOI

Moteur local de montage publicitaire. Il produit un spot vertical 9:16 (1080×1920, 30 i/s, H.264 + AAC) à partir de photos, d'un logo, d'une voix off et d'un fichier de configuration. Il sait aussi produire un carré 1:1 et un horizontal 16:9 avec des mises en page adaptées.

## État actuel — à lire en premier

| Élément | État |
|---|---|
| Moteur, 12 scènes, sous-titres, mixage, rendu, contrôle qualité | Fonctionnent |
| Rendu 9:16 | Fonctionne. Fichier : `output/la-foi_9x16_BROUILLON.mp4` |
| **Voix off** | **Non ajoutée.** L'ancien MP3 (282 s) ne correspond pas au script ; la nouvelle voix reste à générer (voir ci-dessous) |
| Synchronisation voix ↔ images | **Non faite.** Les temps du brouillon sont estimés |
| Musique | Fond généré par `scripts/make-music.mjs` (aucun droit à gérer). Remplaçable |
| Logo | Découpé depuis la photo `05-carte-carnet.png`. Remplacez `assets/logos/logo-cmf.png` par le fichier officiel |
| Remotion / TypeScript | **Non utilisés.** Les registres npm et PyPI étaient bloqués dans l'environnement de création |

### Pourquoi la voix n'est pas dans la vidéo

La voix dure 4 min 42 s et contient 53 phrases séparées par des pauses. Le script de ce projet fait 13 unités et se lit en 1 min 30 environ. Le texte lu est donc différent. Aucun outil de transcription n'était disponible pour l'écouter. Le moteur refuse d'ajouter une voix non alignée, car les sous-titres seraient faux.

**Voix choisie :** masculine, professionnelle, chaleureuse et dynamique, ton rassurant avec une touche d'émotion. Le brief complet est dans `assets/audio/BRIEF-VOIX.md`. Cette voix n'a pas pu être générée dans l'environnement de création (pas de clé ElevenLabs, API inaccessible, aucun moteur de voix local). Je n'ai pas utilisé de voix de synthèse de substitution.

Procédure pour finaliser le spot :

1. `npm run voice-text` écrit `assets/audio/texte-voix-off.txt` (un paragraphe par unité du script).
2. Générez la voix dans ElevenLabs avec ce texte et le brief, puis enregistrez `assets/audio/voix-off.mp3` et renseignez-la dans `src/config/audio.json`.
3. `npm run align:auto`, puis `npm run build`, puis `npm run render`.

L'alignement automatique repère les pauses entre paragraphes et cale les scènes et les sous-titres dessus. Il a été testé uniquement sur un audio synthétique aux pauses connues (erreur de 4 ms), pas sur une vraie voix : écoutez le résultat. Pour un alignement mot à mot, utilisez plutôt `npm run voice` (API ElevenLabs avec horodatage).

Si vous préférez garder la voix actuelle de 4 min 42 s, collez son texte exact dans `src/config/script.json` et alignez à la main (section « Mode A »).

## Démarrage

Prérequis : Node 20 ou plus, FFmpeg, Chromium (ou Chrome) et Playwright.

```bash
npm install                 # installe Playwright (si absent)
npm run prepare-media       # inventaire, agrandissement des photos, logo
npm run studio              # prévisualisation : http://localhost:3000/src/compositions/index.html?studio=1
npm run render              # MP4 9:16 final dans output/
npm run qc -- output/la-foi_9x16_BROUILLON.mp4
```

Si Chromium n'est pas dans `/opt/pw-browsers/chromium`, définissez `CHROMIUM_PATH`.

## Où modifier quoi

Tout se règle dans `src/config/`. Après un changement, relancez `npm run build` (ou simplement le rendu) puis rechargez le studio.

| Je veux changer… | Fichier | Champ |
|---|---|---|
| Ordre des scènes | `storyboard.json` | ordre du tableau `scenes` |
| Photo d'une scène | `storyboard.json` | `images[].src` |
| Titre, rubrique, message | `storyboard.json` | `title`, `kicker`, `subtitle` |
| Mots en doré | `storyboard.json` / `script.json` | `highlight` / `highlights` |
| Cadrage et zoom | `storyboard.json` | `camera` : `s` = zoom, `x`,`y` = point de la photo au centre |
| Animation d'entrée | `storyboard.json` | `enter.type` : `fade`, `wipe-left`, `wipe-right`, `wipe-up`, `slide-up`, `zoom`, `circle` |
| Durée d'une scène | `script.json` + `timing.json` | la voix décide (voir plus bas) |
| Texte de la voix | `script.json` | `units[].text` |
| Couleurs, police, URL, date | `brand.json` | `colors`, `font`, `campaign` |
| Logo | `assets/logos/logo-cmf.png` | remplacer le fichier |
| Sous-titres (taille, mots par ligne) | `brand.json` | `subtitles` |
| Volume musique, voix, effets | `audio.json` | `musicVolume`, `voiceVolume`, `sfxVolume` |
| Position du texte, marges Reels | `brand.json` | `layout` (par format) |
| Afficher le téléphone du cabinet | `brand.json` | `campaign.showPhone` |
| Sans sous-titres incrustés | commande | `npm run render -- --no-subs` |

Les modèles de scène sont dans `src/scenes/` : `photo`, `campaign`, `benefits`, `finale`. Pour en créer un, ajoutez un fichier et inscrivez-le dans `src/scenes/index.js`.

## Voix off et synchronisation

Le moteur calcule les scènes à partir des temps de chaque unité du script. Sans `src/config/timing.json`, il estime ces temps : la vidéo est alors marquée `BROUILLON`.

### Mode A — voix fournie, alignement manuel

```bash
npm run align                                  # détecte les phrases par les pauses
# ouvrez output/phrases-detectees.json, écoutez la voix, remplissez "unit" (u01…u13)
node scripts/align.mjs --from-phrases output/phrases-detectees.json
npm run build                                  # recalcule scènes et sous-titres
```

Le fichier `src/config/timing.json` est lisible et modifiable : ajustez un début ou une fin à la main si besoin.

### Mode B — génération ElevenLabs (facultatif)

```bash
export ELEVENLABS_API_KEY=...      # jamais dans le navigateur ni dans le dépôt
export ELEVENLABS_VOICE_ID=...
npm run voice
node scripts/align.mjs --audio assets/audio/voix-generee.mp3 --elevenlabs output/elevenlabs-alignement.json
npm run render
```

Le script appelle l'API `with-timestamps`, qui donne l'heure de chaque caractère. Ce mode n'a pas pu être testé ici (pas d'accès réseau). Vérifiez le premier essai.

### Mixage

La musique baisse automatiquement quand la voix parle (compression « sidechain »). Des effets discrets (souffle, cloche) accompagnent les transitions. Le son entier est fondu à l'entrée et à la sortie, sans coupure entre les scènes.

## Sorties (`output/`)

| Fichier | Contenu |
|---|---|
| `la-foi_9x16_BROUILLON.mp4` | Spot vertical (le suffixe disparaît quand la voix est alignée) |
| `la-foi_9x16_apercu.mp4` | Aperçu léger |
| `sous-titres.srt` | Sous-titres, générés avec la timeline |
| `miniature_9x16.png` | Miniature (`npm run thumbnail`) |
| `rapport-qc.txt` | Résultat du contrôle qualité |
| `verif/` | Images de contrôle et planches contact (`npm run sheet`) |

Autres formats : `npm run render:square` (1:1), `npm run render:wide` (16:9).

## Contrôle qualité

`npm run qc -- fichier.mp4` vérifie : médias présents, logo non déformé, absence de prix, de pourcentage et de durée inventés, « gratuit » toujours accompagné de sa condition, orthographe courante, sous-titres (chevauchements, vitesse de lecture), textes dans la zone visible des Reels, photos non déformées, codecs, images par seconde, durée, silences, lisibilité du fichier.

Limites : le contrôle d'orthographe n'est qu'une liste de fautes fréquentes, et la zone visible est estimée (haut 200 px, bas 330 px, droite 110 px). Relisez la vidéo avant publication.

## Points d'attention sur les médias

- Les 9 photos font 941×1672 px (ou 1122×1402) : sous la définition de rendu. Elles sont agrandies de 1,5 fois (`assets/images/_hd/`), donc légèrement douces. Fournissez les originaux haute définition si vous les avez.
- Plusieurs photos ressemblent à des images générées par IA (par exemple une marque visible sur des lunettes). Si ce sont bien des images illustratives, indiquez-le dans la publication. Le brief demande de distinguer ces images des photos documentaires.
- Le site officiel n'était pas joignable depuis l'environnement de création : l'adresse affichée vient de votre brief.

## Structure

```
assets/        images, logos, audio, polices (Inter, licence OFL)
src/config/    brand.json, script.json, storyboard.json, audio.json, timing.json, timeline.json (généré)
src/scenes/    modèles de scènes          src/animations/  easings et transitions
src/components/ texte cinétique, particules, icônes      src/subtitles/  sous-titres animés
src/compositions/  page de rendu, studio, styles
scripts/       import, timeline, alignement, rendu, mixage, contrôle qualité
output/        vidéos, SRT, miniature, rapports
```

## Réutilisation

La structure (configuration, modèles de scènes, rendu) peut servir à d'autres spots : changez `brand.json`, `script.json`, `storyboard.json` et les médias. Une bibliothèque de modèles de montage (institutionnel, émotionnel, commercial, motion design) n'est pas encore écrite : elle vient après la validation de ce spot.
