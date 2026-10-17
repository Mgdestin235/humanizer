#!/usr/bin/env node
// Rendu vidéo : timeline → images (Chromium) → MP4 H.264 + AAC (FFmpeg).
// Options : --format 9x16|1x1|16x9   --preview (540 px, rapide)   --range 0:10   --voice (force la voix même non alignée)
//           --out chemin.mp4   --workers 4   --no-subs (sans sous-titres incrustés)
import fs from 'node:fs';
import path from 'node:path';
import { serve } from './lib/server.mjs';
import { loadPlaywright, chromiumPath, p, run, readJson } from './lib/util.mjs';
import { mixAudio } from './mix-audio.mjs';

const arg = (k, d) => { const i = process.argv.indexOf(`--${k}`); return i < 0 ? d : (process.argv[i + 1]?.startsWith('--') || i + 1 >= process.argv.length ? true : process.argv[i + 1]); };
const format = arg('format', '9x16'), preview = !!arg('preview', false), noSubs = !!arg('no-subs', false);
const workers = Number(arg('workers', 4));
run('node', [p('scripts/build-timeline.mjs')]);
const tl = readJson(p('src/config/timeline.json'));
const dims = { '9x16': [1080, 1920], '1x1': [1080, 1080], '16x9': [1920, 1080] }[format];
const [r0, r1] = String(arg('range', `0:${tl.duration}`)).split(':').map(Number);
const fps = tl.fps, f0 = Math.floor(r0 * fps), f1 = Math.min(Math.ceil(r1 * fps), Math.floor(tl.duration * fps));
const nameBase = `la-foi_${format}${preview ? '_apercu' : ''}${tl.estimated ? '_BROUILLON' : ''}`;
const outFile = arg('out', p('output', `${nameBase}.mp4`));
const frameDir = p('output/tmp/frames'); fs.rmSync(frameDir, { recursive: true, force: true }); fs.mkdirSync(frameDir, { recursive: true });

// Audio
if (!fs.existsSync(p('assets/audio/musique-fond.wav'))) run('node', [p('scripts/make-music.mjs'), String(Math.ceil(tl.duration + 4))]);
run('node', [p('scripts/make-sfx.mjs')]);
const voiceOk = !tl.estimated || !!arg('voice', false);
if (!voiceOk) console.log('ℹ Voix off non ajoutée : les temps sont estimés (voir README). Utilisez --voice pour forcer.');
mixAudio({ duration: tl.duration, useVoice: voiceOk });

// Images
const { chromium } = await loadPlaywright();
const { server, port } = await serve(0);
const browser = await chromium.launch({ executablePath: chromiumPath(), args: ['--no-sandbox', '--font-render-hinting=none'] });
const total = f1 - f0; let done = 0; const t0 = Date.now();
await Promise.all(Array.from({ length: workers }, async (_, w) => {
  const page = await browser.newPage({ viewport: { width: dims[0], height: dims[1] } });
  page.on('pageerror', (e) => console.error('[erreur page]', e.message));
  await page.goto(`http://127.0.0.1:${port}/src/compositions/index.html?format=${format}${noSubs ? '&subs=0' : ''}`);
  await page.waitForFunction('window.__ready === true', null, { timeout: 120000 });
  for (let f = f0 + w; f < f1; f += workers) {
    await page.evaluate((t) => window.__comp.setTime(t), f / fps);
    await page.screenshot({ path: path.join(frameDir, `${String(f - f0).padStart(6, '0')}.jpg`), type: 'jpeg', quality: 94 });
    if (++done % 150 === 0) process.stdout.write(`\r  images ${done}/${total}  (${Math.round(done / ((Date.now() - t0) / 1000))} i/s)`);
  }
  await page.close();
}));
await browser.close(); server.close();
console.log(`\r  images ${done}/${total} en ${((Date.now() - t0) / 1000).toFixed(0)} s`);

// Encodage
const scale = preview ? ['-vf', `scale=${Math.round(dims[0] / 2)}:-2`] : [];
const aStart = r0, aDur = (f1 - f0) / fps;
run('ffmpeg', ['-y', '-v', 'error', '-framerate', String(fps), '-i', path.join(frameDir, '%06d.jpg'), '-ss', String(aStart), '-t', String(aDur), '-i', p('output/mix.m4a'),
  ...scale, '-c:v', 'libx264', '-preset', preview ? 'veryfast' : 'slow', '-crf', preview ? '26' : '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(fps),
  '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', outFile]);
console.log(`✔ ${outFile}`);
