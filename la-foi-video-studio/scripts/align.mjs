#!/usr/bin/env node
// Alignement voix ↔ script. Trois sources possibles, du plus précis au plus manuel :
//   1. --elevenlabs fichier.json : réponse « with-timestamps » d'ElevenLabs (temps par caractère → par mot)
//   2. --silences                : détecte les phrases par les pauses et écrit un gabarit à compléter à la main
//   3. édition directe de src/config/timing.json
// Rien n'est simulé : si l'alignement manque, la vidéo reste marquée BROUILLON.
import fs from 'node:fs';
import { p, readJson, writeJson, run, probe } from './lib/util.mjs';

const arg = (k) => { const i = process.argv.indexOf(`--${k}`); return i < 0 ? null : (process.argv[i + 1] ?? true); };
const audioCfg = readJson(p('src/config/audio.json'));
const script = readJson(p('src/config/script.json'));
const audio = arg('audio') || audioCfg.voice;
const dur = +probe(p(audio)).format.duration;

if (arg('silences')) {
  const noise = arg('noise') && arg('noise') !== true ? arg('noise') : '-35dB', minPause = arg('pause') && arg('pause') !== true ? arg('pause') : '0.3';
  const r = run('ffmpeg', ['-hide_banner', '-i', p(audio), '-af', `silencedetect=noise=${noise}:d=${minPause}`, '-f', 'null', '-'], {});
  const log = r.stderr; const starts = [...log.matchAll(/silence_start: ([\d.]+)/g)].map((m) => +m[1]);
  const ends = [...log.matchAll(/silence_end: ([\d.]+)/g)].map((m) => +m[1]);
  const phrases = []; let cur = 0;
  starts.forEach((s, i) => { if (s - cur > 0.25) phrases.push({ start: +cur.toFixed(2), end: +s.toFixed(2) }); cur = ends[i] ?? s; });
  if (dur - cur > 0.25) phrases.push({ start: +cur.toFixed(2), end: +dur.toFixed(2) });
  writeJson(p('output/phrases-detectees.json'), {
    audio, duration: dur, phrases: phrases.map((x, i) => ({ n: i + 1, ...x, unit: '' })),
    aide: "Écoutez la voix et remplissez 'unit' (ex. u03) pour chaque phrase. Plusieurs phrases peuvent partager la même unité : le début est celui de la première, la fin celle de la dernière. Puis lancez : node scripts/align.mjs --from-phrases output/phrases-detectees.json",
  });
  console.log(`${phrases.length} phrases détectées pour ${script.units.length} unités du script, durée ${dur.toFixed(1)} s → output/phrases-detectees.json`);
  if (phrases.length > script.units.length * 1.5) console.log('⚠ La voix contient bien plus de phrases que le script : le texte lu est probablement différent. Vérifiez-le avant d\'aligner.');
  process.exit(0);
}

if (arg('from-phrases')) {
  const ph = readJson(p(arg('from-phrases'))).phrases.filter((x) => x.unit);
  const units = {};
  for (const x of ph) { const u = units[x.unit] ??= { start: x.start, end: x.end }; u.start = Math.min(u.start, x.start); u.end = Math.max(u.end, x.end); }
  const missing = script.units.filter((u) => !units[u.id]).map((u) => u.id);
  if (missing.length) throw new Error(`Unités sans phrase : ${missing.join(', ')}`);
  writeJson(p('src/config/timing.json'), { source: 'manuel (phrases-detectees.json)', audio, duration: dur, units });
  console.log('timing.json écrit (source manuelle). Lancez « npm run build ».'); process.exit(0);
}

if (arg('elevenlabs')) {
  const j = readJson(p(arg('elevenlabs')));
  const al = j.alignment ?? j.normalized_alignment;
  if (!al) throw new Error("Pas de champ 'alignment' dans ce fichier.");
  const chars = al.characters, st = al.character_start_times_seconds, en = al.character_end_times_seconds;
  const text = chars.join('');
  const norm = (s) => s.replace(/\s+/g, ' ');
  const units = {}; let pos = 0;
  for (const u of script.units) {
    const idx = text.indexOf(u.text.slice(0, 18), pos); if (idx < 0) throw new Error(`Texte de ${u.id} introuvable dans la voix générée (le script a-t-il changé ?)`);
    const endIdx = idx + u.text.length; pos = endIdx;
    const words = []; let i = idx;
    while (i < endIdx) {
      while (i < endIdx && /\s/.test(chars[i])) i++;
      let k = i; while (k < endIdx && !/\s/.test(chars[k])) k++;
      if (k > i) words.push({ w: chars.slice(i, k).join(''), start: +st[i].toFixed(3), end: +en[k - 1].toFixed(3) });
      i = k;
    }
    units[u.id] = { start: words[0].start, end: words.at(-1).end, words };
  }
  writeJson(p('src/config/timing.json'), { source: 'ElevenLabs (alignement par caractère)', audio, duration: dur, units });
  console.log('timing.json écrit avec horodatage mot à mot. Lancez « npm run build ».'); process.exit(0);
}
console.log('Usage : align.mjs --silences | --from-phrases fichier | --elevenlabs reponse.json');
