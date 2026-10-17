# Studio vidéo — Cabinet Médical LA FOI

Moteur local de montage publicitaire. Il produit un spot vertical 9:16 (1080×1920, 30 i/s, H.264 + AAC) à partir de photos, d'un logo, d'une voix off et d'un fichier de configuration. Il sait aussi produire un carré 1:1 et un horizontal 16:9 avec des mises en page adaptées.

## État actuel

| Élément | État |
|---|---|
| Spot final 9:16 | `output/la-foi_9x16.mp4` : 91 s, 1080×1920, 30 i/s, H.264 + AAC, −16,4 LUFS |
| Voix off | `assets/audio/voix-off.mp3` (ElevenLabs, masculine, 87,9 s) |
| Synchronisation | Scènes calées sur les pauses de la voix (`npm run align:auto`). **À vérifier à l'oreille**, surtout les groupes de mots dans chaque phrase (temps répartis, non mesurés mot à mot) |
| Sous-titres | `output/sous-titres.srt` (58) et incrustés dans la vidéo |
| Musique | Fond généré par `scripts/make-music.mjs` (sans droits à gérer), baisse automatique sous la voix |
| Logo | Découpé depuis la photo `05-carte-carnet.png`. Remplacez `assets/logos/logo-cmf.png` par le fichier officiel |
| Remotion / TypeScript | **Non utilisés** (registres npm bloqués à la création). Moteur : Chromium + FFmpeg |

Pour refaire la vidéo après un changement : `npm run align:auto && npm run render && npm run qc -- output/la-foi_9x16.mp4`. Pour un changement de son seul : `npm run render -- --reuse-frames`.

### Autre voix

Générez-la avec `assets/audio/texte-voix-off.txt` et `assets/audio/BRIEF-VOIX.md`, enregistrez-la sous `assets/audio/voix-off.mp3`, puis relancez la commande ci-dessus. L'alignement choisit les pauses entre paragraphes d'après la longueur du texte de chaque unité ; le tableau affiché signale toute durée peu plausible.

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
