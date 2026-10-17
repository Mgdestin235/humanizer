#!/usr/bin/env node
// Importe les médias : inventaire, agrandissement des photos, logo détouré.
// Les originaux ne sont jamais modifiés. Les copies agrandies vont dans assets/images/_hd/.
import fs from 'node:fs';
import path from 'node:path';
import { p, run, probe, writeJson } from './lib/util.mjs';

const imgDir = p('assets/images');
const hdDir = p('assets/images/_hd');
fs.mkdirSync(hdDir, { recursive: true });

const inventory = { images: [], audio: [], logos: [] };

for (const f of fs.readdirSync(imgDir).filter((n) => /\.(png|jpe?g)$/i.test(n)).sort()) {
  const src = path.join(imgDir, f);
  const s = probe(src).streams[0];
  const target = 1.5; // agrandissement doux pour que les zooms restent nets
  const out = path.join(hdDir, f.replace(/\.[^.]+$/, '.png'));
  run('ffmpeg', ['-y', '-v', 'error', '-i', src,
    '-vf', `scale=iw*${target}:ih*${target}:flags=lanczos,unsharp=5:5:0.6:5:5:0.0`, out]);
  inventory.images.push({
    file: `assets/images/${f}`, hd: `assets/images/_hd/${path.basename(out)}`,
    width: s.width, height: s.height, ratio: +(s.width / s.height).toFixed(3),
    note: s.width < 1080 ? 'plus petite que la cible 1080 px : agrandie 1,5× (rendu légèrement adouci)' : 'ok',
  });
}

// Logo : aucun fichier source isolé n'a été fourni. On le découpe depuis la photo 05 (logo mural entier, vu de face).
// Remplacez assets/logos/logo-cmf.png par le fichier officiel dès que vous l'avez : le projet l'utilisera tel quel.
const logo = p('assets/logos/logo-cmf.png');
if (!fs.existsSync(logo) || process.argv.includes('--force-logo')) {
  const src = p('assets/images/05-carte-carnet.png');
  // cercle mesuré : centre (302,262), rayon ~204 sur l'image 941x1672
  const cx = 302, cy = 262, r = 204;
  run('ffmpeg', ['-y', '-v', 'error', '-i', src, '-vf',
    `crop=${2 * r + 4}:${2 * r + 4}:${cx - r - 2}:${cy - r - 2},scale=iw*2:ih*2:flags=lanczos,format=rgba,` +
    `geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*lt(hypot(X-W/2,Y-H/2),${r * 2 - 4})'`, logo]);
}
const ls = probe(logo).streams[0];
inventory.logos.push({ file: 'assets/logos/logo-cmf.png', width: ls.width, height: ls.height,
  note: 'découpé depuis la photo 05 (pas de fichier officiel fourni)' });

for (const f of fs.readdirSync(p('assets/audio')).filter((n) => /\.(mp3|wav|m4a)$/i.test(n))) {
  const pr = probe(p('assets/audio', f));
  inventory.audio.push({ file: `assets/audio/${f}`, duration: +(+pr.format.duration).toFixed(2),
    codec: pr.streams[0].codec_name, sampleRate: +pr.streams[0].sample_rate, channels: pr.streams[0].channels });
}

writeJson(p('output/inventaire.json'), inventory);
console.table(inventory.images.map(({ file, width, height, note }) => ({ file, width, height, note })));
console.log('logos :', inventory.logos.map((l) => `${l.file} ${l.width}x${l.height}`).join(', '));
console.log('audio :', inventory.audio.map((a) => `${a.file} ${a.duration}s`).join(', '));
