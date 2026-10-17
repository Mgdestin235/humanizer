#!/usr/bin/env node
// Calcule la timeline finale : débuts/fins des scènes, sous-titres, fichier SRT.
// Source des temps (par priorité) :
//   1. src/config/timing.json  (alignement ElevenLabs ou saisie manuelle)
//   2. estimation d'après le nombre de mots (BROUILLON : non synchronisé avec une vraie voix)
import fs from 'node:fs';
import { p, readJson, writeJson, fmtTime } from './lib/util.mjs';

const brand = readJson(p('src/config/brand.json'));
const script = readJson(p('src/config/script.json'));
const story = readJson(p('src/config/storyboard.json'));
const timingFile = p('src/config/timing.json');
const timing = fs.existsSync(timingFile) ? readJson(timingFile) : null;

const WPS = 2.55; // mots par seconde pour l'estimation
// Ponctuation haute française (« mot : ») : espace insécable pour que « : » ne devienne jamais un mot seul.
const words = (t) => t.replace(/ ([:;!?»])/g, '\u00A0$1').split(/[ \t\n]+/).filter(Boolean);

// ---- 1. Temps de chaque unité ------------------------------------------------
const units = {};
let estimated = false;
if (timing) {
  for (const u of script.units) {
    const t = timing.units?.[u.id];
    if (!t) throw new Error(`timing.json : unité ${u.id} absente. Complétez-la ou supprimez timing.json.`);
    units[u.id] = { ...u, start: t.start, end: t.end, words: t.words };
  }
} else {
  estimated = true;
  let cur = 0.6;
  for (const u of script.units) {
    const dur = words(u.text).length / WPS;
    units[u.id] = { ...u, start: +cur.toFixed(2), end: +(cur + dur).toFixed(2) };
    cur += dur + 0.45;
  }
}
const order = script.units.map((u) => u.id);
const lastEnd = units[order.at(-1)].end;

// ---- 2. Scènes ------------------------------------------------------------------
const overlap = brand.transitionOverlap ?? 0.5;
const scenes = story.scenes.map((s, i) => {
  const from = units[s.sync.from], to = units[s.sync.to];
  if (!from || !to) throw new Error(`Scène ${s.id} : unité inconnue (${s.sync.from} → ${s.sync.to})`);
  return { ...s, _start: i === 0 ? 0 : from.start, _unitEnd: to.end };
});
scenes.forEach((s, i) => {
  const next = scenes[i + 1];
  s.start = +s._start.toFixed(3);
  s.end = +(next ? next._start + overlap : Math.max(s._unitEnd + (s.tail ?? 2.5), lastEnd + (s.tail ?? 2.5))).toFixed(3);
  delete s._start; delete s._unitEnd;
  if (next && next._start <= s.start + 1.2) console.warn(`⚠ Scène ${s.id} très courte (${(next._start - s.start).toFixed(2)} s).`);
});
const duration = scenes.at(-1).end;

// ---- 3. Sous-titres ---------------------------------------------------------------
const strip = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const hlPhrases = script.highlights.map((h) => strip(h).split(/\s+/));
function tokenize(text) {
  const toks = words(text).map((w) => ({ w, key: strip(w).replace(/[^a-z0-9'’-]/g, ''), hl: false, hlId: -1 }));
  hlPhrases.forEach((ph, id) => {
    for (let i = 0; i + ph.length <= toks.length; i++) {
      if (ph.every((k, j) => toks[i + j].key.replace(/^l'|^d'|^qu'/, '') === k.replace(/^l'|^d'|^qu'/, '') || toks[i + j].key === k)) {
        for (let j = 0; j < ph.length; j++) { toks[i + j].hl = true; toks[i + j].hlId = id * 1000 + i; }
      }
    }
  });
  return toks;
}
function group(toks) {
  const { maxWords, maxChars } = brand.subtitles;
  const out = []; let cur = [];
  const flush = () => { if (cur.length) out.push(cur); cur = []; };
  toks.forEach((t, i) => {
    cur.push(t);
    const chars = cur.map((x) => x.w).join(' ').length;
    const next = toks[i + 1];
    const endsClause = /[,:;.!?]$/.test(t.w);
    const joinsHl = next && t.hl && next.hl && next.hlId === t.hlId;
    if (joinsHl) return;
    if (endsClause || cur.length >= maxWords || (next && chars + next.w.length + 1 > maxChars)) flush();
  });
  flush();
  // évite un groupe orphelin d'un seul mot court
  for (let i = out.length - 1; i > 0; i--) {
    if (out[i].length === 1 && out[i][0].w.length <= 4 && out[i - 1].length < brand.subtitles.maxWords) {
      out[i - 1].push(...out[i]); out.splice(i, 1);
    }
  }
  return out;
}
const cues = [];
for (const id of order) {
  const u = units[id];
  const groups = group(tokenize(u.text));
  const flat = groups.flat();
  // temps par mot : réels si fournis, sinon répartis selon la longueur des mots
  let wt;
  if (u.words && u.words.length === flat.length) {
    wt = u.words.map((x) => ({ start: x.start, end: x.end }));
  } else {
    const weights = flat.map((t) => t.w.replace(/[^\p{L}\p{N}]/gu, '').length + 1.5);
    const total = weights.reduce((a, b) => a + b, 0);
    let c = u.start; wt = weights.map((w) => { const d = (w / total) * (u.end - u.start); const r = { start: c, end: c + d }; c += d; return r; });
  }
  let k = 0;
  for (const g of groups) {
    const ws = g.map((t) => ({ w: t.w, hl: t.hl, start: +wt[k].start.toFixed(3), end: +wt[k++].end.toFixed(3) }));
    cues.push({ unit: id, start: ws[0].start, end: ws.at(-1).end, words: ws, text: ws.map((x) => x.w).join(' ') });
  }
}
// Un sous-titre reste affiché jusqu'au suivant (≤ 0,45 s), sans chevauchement.
cues.forEach((c, i) => {
  const next = cues[i + 1];
  const hold = c.end + 0.45;
  c.end = +Math.min(hold, next ? next.start - 0.02 : hold).toFixed(3);
  if (c.end < c.start + 0.25) c.end = +(c.start + 0.25).toFixed(3);
});

const timeline = {
  version: 1, estimated, timingSource: timing?.source ?? 'estimation (brouillon)',
  audio: timing?.audio ?? null, duration: +duration.toFixed(3), fps: 30, brand,
  scenes, cues, units: order.map((id) => ({ id, text: units[id].text, start: units[id].start, end: units[id].end })),
};
writeJson(p('src/config/timeline.json'), timeline);

const srt = cues.map((c, i) => `${i + 1}\n${fmtTime(c.start)} --> ${fmtTime(c.end)}\n${c.text}\n`).join('\n');
fs.mkdirSync(p('output'), { recursive: true });
fs.writeFileSync(p('output/sous-titres.srt'), srt);

console.log(`Timeline : ${scenes.length} scènes, ${cues.length} sous-titres, ${duration.toFixed(1)} s (${timeline.timingSource}).`);
if (estimated) console.log('⚠ Temps ESTIMÉS : aucune voix off alignée. Voir README (alignement ElevenLabs ou manuel).');
console.table(scenes.map((s) => ({ scène: s.id, début: s.start, fin: s.end, durée: +(s.end - s.start).toFixed(2) })));
