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

// Alignement automatique par pauses : les N unités du script sont lues à la suite, séparées par les N-1 plus longues pauses.
// À utiliser avec une voix générée à partir de assets/audio/texte-voix-off.txt (un paragraphe par unité).
if (arg('auto')) {
  const r = run('ffmpeg', ['-hide_banner', '-i', p(audio), '-af', 'silencedetect=noise=-38dB:d=0.12', '-f', 'null', '-'], {});
  const st = [...r.stderr.matchAll(/silence_start: ([\d.]+)/g)].map((m) => +m[1]);
  const en = [...r.stderr.matchAll(/silence_end: ([\d.]+)/g)].map((m) => +m[1]);
  let sil = st.map((s, i) => ({ start: s, end: en[i] ?? dur })).map((x) => ({ ...x, dur: x.end - x.start }));
  const speechStart = sil[0] && sil[0].start < 0.05 ? sil[0].end : 0;
  const last = sil.at(-1), speechEnd = last && last.end >= dur - 0.05 ? last.start : dur;
  sil = sil.filter((x) => x.start > speechStart + 0.05 && x.end < speechEnd - 0.05);
  const N = script.units.length;
  if (sil.length < N - 1) throw new Error(`Seulement ${sil.length} pauses détectées pour ${N} unités : la voix ne suit pas le script (ou les paragraphes ne sont pas séparés).`);
  // Choix des N-1 frontières par programmation dynamique : chaque unité doit durer à peu près
  // « longueur de son texte / longueur totale × durée de parole », et une pause longue est préférée à une courte.
  const cands = sil.filter((x) => x.dur >= 0.2);
  if (cands.length < N - 1) throw new Error(`Seulement ${cands.length} pauses nettes pour ${N} unités.`);
  const chars = script.units.map((u) => u.text.replace(/[^\p{L}\p{N}]/gu, '').length + 3 * (u.text.split(/\s+/).length));
  const totalChars = chars.reduce((a, b) => a + b, 0), speech = speechEnd - speechStart;
  const exp = chars.map((c) => (c / totalChars) * speech);
  const MU = 1.2, cost = (i, a, b) => { const d = Math.max(0.05, b - a); return Math.log(d / exp[i]) ** 2; };
  const M = cands.length, INF = 1e9;
  const best = Array.from({ length: N }, () => new Array(M).fill(INF)), from = Array.from({ length: N }, () => new Array(M).fill(-1));
  for (let j = 0; j < M; j++) best[0][j] = cost(0, speechStart, cands[j].start) - MU * Math.min(1, cands[j].dur);
  for (let k = 1; k < N - 1; k++) for (let j = 0; j < M; j++) for (let i = 0; i < j; i++) {
    if (best[k - 1][i] >= INF) continue;
    const c = best[k - 1][i] + cost(k, cands[i].end, cands[j].start) - MU * Math.min(1, cands[j].dur);
    if (c < best[k][j]) { best[k][j] = c; from[k][j] = i; }
  }
  let bj = -1, bc = INF;
  for (let j = 0; j < M; j++) { const c = best[N - 2][j] + cost(N - 1, cands[j].end, speechEnd); if (c < bc) { bc = c; bj = j; } }
  if (bj < 0) throw new Error('Aucun découpage cohérent trouvé.');
  const idx = []; for (let k = N - 2, j = bj; k >= 0; k--) { idx.unshift(j); j = from[k][j]; }
  const bounds = idx.map((j) => cands[j]);
  const margin = 0;
  const units = {};
  script.units.forEach((u, i) => {
    const a = i === 0 ? speechStart : bounds[i - 1].end, b = i === N - 1 ? speechEnd : bounds[i].start;
    const inner = sil.filter((x) => !bounds.includes(x) && x.start >= a && x.end <= b).map((x) => +((x.start + x.end) / 2).toFixed(3));
    units[u.id] = { start: +a.toFixed(3), end: +b.toFixed(3), pauses: inner };
  });
  writeJson(p('src/config/timing.json'), { source: 'pauses de la voix (automatique, à vérifier)', audio, duration: dur, units });
  console.table(script.units.map((u) => ({ unité: u.id, début: units[u.id].start, fin: units[u.id].end, pauses_internes: units[u.id].pauses.length })));
  console.table(script.units.map((u, i) => ({ unité: u.id, durée: +(units[u.id].end - units[u.id].start).toFixed(2), attendue: +exp[i].toFixed(2), rapport: +((units[u.id].end - units[u.id].start) / exp[i]).toFixed(2), pause_après: i < N - 1 ? +bounds[i].dur.toFixed(2) : '' })));
  const bad = script.units.filter((u, i) => { const r = (units[u.id].end - units[u.id].start) / exp[i]; return r < 0.6 || r > 1.6; });
  if (bad.length) console.log(`⚠ Durées peu plausibles pour ${bad.map((u) => u.id).join(', ')} : vérifiez à l'oreille.`);
  console.log('Alignement par pauses + longueur du texte : écoutez la voix avec la vidéo pour confirmer les transitions.');
  console.log('timing.json écrit. Lancez « npm run build ».'); process.exit(0);
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
console.log('Usage : align.mjs --auto | --silences | --from-phrases fichier | --elevenlabs reponse.json');
