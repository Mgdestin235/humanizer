#!/usr/bin/env node
// Contrôle qualité. Usage : node scripts/qc.mjs [video.mp4] [--format 9x16]
// Vérifie médias, textes interdits, orthographe courante, zones visibles, déformation, sous-titres, fichier final.
import fs from 'node:fs';
import path from 'node:path';
import { serve } from './lib/server.mjs';
import { loadPlaywright, chromiumPath, p, readJson, run, probe } from './lib/util.mjs';

const args = process.argv.slice(2);
const video = args.find((a) => a.endsWith('.mp4'));
const fi = args.indexOf('--format'); const format = fi >= 0 ? args[fi + 1] : '9x16';
const tl = readJson(p('src/config/timeline.json')), script = readJson(p('src/config/script.json'));
const results = []; const add = (ok, name, detail = '') => { results.push({ ok, name, detail }); console.log(`${ok === true ? '✔' : ok === 'warn' ? '⚠' : '✘'} ${name}${detail ? ' — ' + detail : ''}`); };

// 1. Médias chargés
const files = new Set(); tl.scenes.forEach((s) => { (s.images ?? []).forEach((i) => files.add(i.src)); if (s.background) files.add(s.background); });
files.add(tl.brand.logo);
const missing = [...files].filter((f) => !fs.existsSync(p(f)) || fs.statSync(p(f)).size < 1000);
add(!missing.length, `Médias présents (${files.size})`, missing.join(', '));
const lg = probe(p(tl.brand.logo)).streams[0]; add(Math.abs(lg.width - lg.height) <= 2, 'Logo carré, non déformé', `${lg.width}x${lg.height}`);

// 2. Contenu interdit par le brief
const allText = [...script.units.map((u) => u.text), ...tl.scenes.flatMap((s) => [s.title, s.subtitle, s.kicker, ...(s.cards ?? []).map((c) => c.label), ...(s.chips ?? []).map((c) => c.label)])].filter(Boolean).join('\n');
const banned = [/%/, /€|\bFCFA\b|\bXAF\b|\bCFA\b|\$/, /\bprix\b|\btarif|\bcoût|\bpayant/i];
const hits = banned.map((r) => allText.match(r)?.[0]).filter(Boolean);
// « gratuit » doit toujours rester accompagné de sa condition dans la même scène (ou la même phrase du script).
const sceneTxt = (s) => [s.title, s.subtitle, ...(s.cards ?? []).map((c) => c.label)].filter(Boolean).join(' ');
tl.scenes.filter((s) => /gratuit/i.test(sceneTxt(s)) && !/condition|adhésion|adhérent/i.test(sceneTxt(s))).forEach((s) => hits.push(`« gratuit » sans condition (${s.id})`));
script.units.filter((u) => /gratuit/i.test(u.text) && !/condition|adhésion/i.test(u.text)).forEach((u) => hits.push(`« gratuit » sans condition (${u.id})`));
add(!hits.length, 'Aucun prix, pourcentage ni promesse sans condition', hits.join(', '));
add(!/\b\d+\s*(jours|mois|semaines|ans)\b/i.test(allText), 'Aucune durée de validité inventée');
add(['carte d\'adhésion', 'carnet médical', 'bilan médical', 'consultations médicales gratuites', '20 octobre 2026'].every((k) => allText.toLowerCase().includes(k)), 'Informations essentielles du brief présentes');

// 3. Orthographe courante (liste de fautes fréquentes, sans accent ni apostrophe)
const typos = { 'medical ': 'médical', 'medecin': 'médecin', 'prevention': 'prévention', 'adhesion': 'adhésion', 'sante': 'santé', 'accueil ': 'accueil', 'a cette occasion': 'À cette occasion', "d'avantage\\b": 'davantage ?' };
const found = Object.keys(typos).filter((k) => new RegExp(k.replace(/ $/, '\\b'), 'i').test(allText.replace(/LA FOI/g, '')) && !(k === 'accueil ' )).map((k) => `${k.trim()} → ${typos[k]}`);
add(!found.length, 'Orthographe française (accents courants)', found.join('; '));
add(!/ {2,}| ,| \.|\bl ' |’ /.test(allText), 'Typographie : espaces et apostrophes');

// 4. Sous-titres
let bad = [];
tl.cues.forEach((c, i) => {
  const n = tl.cues[i + 1];
  if (n && c.end > n.start + 1e-3) bad.push(`chevauchement #${i + 1}`);
  if (c.end - c.start < 0.25) bad.push(`trop court #${i + 1}`);
  const cps = c.text.length / (c.end - c.start); if (cps > 22) bad.push(`lecture trop rapide #${i + 1} (${cps.toFixed(0)} car/s)`);
  if (c.end > tl.duration + 0.01) bad.push(`hors durée #${i + 1}`);
});
add(!bad.length, `Sous-titres cohérents (${tl.cues.length})`, bad.slice(0, 5).join('; '));
const srt = fs.existsSync(p('output/sous-titres.srt')); add(srt, 'Fichier SRT présent');
add(tl.estimated ? 'warn' : true, 'Synchronisation voix ↔ sous-titres', tl.estimated ? 'ESTIMÉE (aucun alignement de la voix off) : le spot est un brouillon' : tl.timingSource);

// 5. Rendu navigateur : zones visibles, déformation
const { chromium } = await loadPlaywright(); const { server, port } = await serve(0);
const dims = { '9x16': [1080, 1920], '1x1': [1080, 1080], '16x9': [1920, 1080] }[format];
const browser = await chromium.launch({ executablePath: chromiumPath(), args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: dims[0], height: dims[1] } });
await page.goto(`http://127.0.0.1:${port}/src/compositions/index.html?format=${format}`);
await page.waitForFunction('window.__ready === true');
const L = tl.brand.layout[format], safe = format === '9x16' ? { l: 40, r: dims[0] - 110, t: 200, b: dims[1] - 330 } : { l: 40, r: dims[0] - 40, t: 30, b: dims[1] - 30 };
const outside = [], distorted = [];
for (const s of tl.scenes) {
  for (const f of [0.55, 0.9]) {
    const t = s.start + (s.end - s.start - 0.5) * f;
    const r = await page.evaluate((t) => {
      window.__comp.setTime(t); const out = [], dist = [];
      for (const el of document.querySelectorAll('.txt, .subs, .chip, .card, .seal, .badge, .urlpill, .cta, .head')) {
        const cs = getComputedStyle(el); const sc = el.closest('.scene'); if (sc && getComputedStyle(sc).display === 'none') continue;
        if (+cs.opacity < 0.9 || el.offsetParent === null) continue;
        let b = el.getBoundingClientRect();
        if (el.matches('.txt, .head') && el.children.length) { // le conteneur peut être plus grand que son texte : on mesure les enfants
          const rs = [...el.children].map((c) => c.getBoundingClientRect()).filter((r) => r.width > 0);
          b = { left: Math.min(...rs.map((r) => r.left)), right: Math.max(...rs.map((r) => r.right)), top: Math.min(...rs.map((r) => r.top)), bottom: Math.max(...rs.map((r) => r.bottom)) };
        }
        out.push({ c: el.className, l: b.left, r: b.right, t: b.top, b: b.bottom });
      }
      for (const im of document.querySelectorAll('.frame img')) { const sc = im.closest('.scene'); if (getComputedStyle(sc).display === 'none') continue; const w = parseFloat(im.style.width), h = parseFloat(im.style.height); dist.push({ src: im.src.split('/').pop(), ratio: w / h, nat: im.naturalWidth / im.naturalHeight }); }
      return { out, dist };
    }, t);
    for (const e of r.out) if (e.l < safe.l - 1 || e.r > safe.r + 1 || e.t < safe.t - 1 || e.b > safe.b + 1) outside.push(`${s.id}@${t.toFixed(1)} .${e.c.split(' ')[0]} [${Math.round(e.l)},${Math.round(e.t)} → ${Math.round(e.r)},${Math.round(e.b)}]`);
    for (const d of r.dist) if (Math.abs(d.ratio / d.nat - 1) > 0.004) distorted.push(`${s.id} ${d.src}`);
  }
}
add(!outside.length, `Textes dans la zone visible (${format})`, outside.slice(0, 4).join(' | '));
add(!distorted.length, 'Photos non déformées (rapport largeur/hauteur conservé)', distorted.join(', '));
await browser.close(); server.close();

// 6. Fichier vidéo
if (video) {
  const pr = probe(video), v = pr.streams.find((s) => s.codec_type === 'video'), a = pr.streams.find((s) => s.codec_type === 'audio');
  const d = +pr.format.duration;
  add(v?.codec_name === 'h264' && a?.codec_name === 'aac', 'Codecs H.264 + AAC', `${v?.codec_name}/${a?.codec_name}`);
  add(v && +v.width === dims[0] && +v.height === dims[1] || /apercu/.test(video), `Dimensions ${dims.join('×')}`, `${v?.width}x${v?.height}`);
  add(v?.r_frame_rate === '30/1', '30 images par seconde', v?.r_frame_rate);
  add(Math.abs(d - tl.duration) < 0.25 || /proto/.test(video), 'Durée conforme à la timeline', `${d.toFixed(2)} s`);
  const sil = run('ffmpeg', ['-hide_banner', '-i', video, '-af', 'silencedetect=noise=-55dB:d=0.8', '-f', 'null', '-']).stderr;
  const sl = [...sil.matchAll(/silence_start: ([\d.]+)/g)].map((m) => m[1]);
  add(!sl.length, 'Aucun silence involontaire (> 0,8 s)', sl.join(', '));
  const vd = run('ffmpeg', ['-hide_banner', '-v', 'error', '-i', video, '-f', 'null', '-']).stderr.trim(); add(!vd, 'Fichier lisible, flux sans erreur', vd.slice(0, 120));
  fs.mkdirSync(p('output/verif'), { recursive: true });
  run('ffmpeg', ['-y', '-v', 'error', '-i', video, '-vf', 'select=eq(n\\,0)', '-frames:v', '1', p('output/verif/premiere-image.png')]);
  run('ffmpeg', ['-y', '-v', 'error', '-sseof', '-0.1', '-i', video, '-frames:v', '1', '-update', '1', p('output/verif/derniere-image.png')]);
  console.log('Images de contrôle : output/verif/premiere-image.png, derniere-image.png');
}
const fail = results.filter((r) => r.ok === false).length, warn = results.filter((r) => r.ok === 'warn').length;
fs.writeFileSync(p('output/rapport-qc.txt'), results.map((r) => `${r.ok === true ? 'OK   ' : r.ok === 'warn' ? 'AVERT' : 'ÉCHEC'} ${r.name} ${r.detail}`).join('\n') + '\n');
console.log(`\n${fail ? '✘' : '✔'} ${results.length - fail - warn} réussis, ${warn} avertissement(s), ${fail} échec(s) → output/rapport-qc.txt`);
process.exit(fail ? 1 : 0);
