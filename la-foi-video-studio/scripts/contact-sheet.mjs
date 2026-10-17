#!/usr/bin/env node
// Planche contact : une image par scène (à +offset s après son début) pour relire le montage d'un coup d'œil.
// Usage : node scripts/contact-sheet.mjs [format] [offset]
import fs from 'node:fs';
import { run, p, readJson } from './lib/util.mjs';

const format = process.argv[2] ?? '9x16', offset = Number(process.argv[3] ?? 2.6);
const tl = readJson(p('src/config/timeline.json'));
const ts = tl.scenes.map((s) => (s.start + Math.min(offset, (s.end - s.start) * 0.6)).toFixed(2));
const dir = p('output/verif/sheet'); fs.rmSync(dir, { recursive: true, force: true });
run('node', [p('scripts/still.mjs'), format, dir, ...ts]);
const files = fs.readdirSync(dir).filter((f) => f.endsWith('.png')).sort((a, b) => parseFloat(a.split('_t')[1].replace('_', '.')) - parseFloat(b.split('_t')[1].replace('_', '.')));
const cols = format === '16x9' ? 3 : 6, w = format === '16x9' ? 640 : 360;
const h = { '9x16': 640, '1x1': 360, '16x9': 360 }[format], rows = Math.ceil(files.length / cols);
const inputs = files.flatMap((f) => ['-i', `${dir}/${f}`]);
const filter = files.map((_, i) => `[${i}:v]scale=${w}:${h}[v${i}]`).join(';') + ';' + files.map((_, i) => `[v${i}]`).join('') +
  `xstack=inputs=${files.length}:layout=${files.map((_, i) => `${(i % cols) * w}_${Math.floor(i / cols) * h}`).join('|')}[o]`;
const out = p(`output/verif/planche_${format}.png`);
run('ffmpeg', ['-y', '-v', 'error', ...inputs, '-filter_complex', filter, '-map', '[o]', out]);
console.log(out, `${cols * w}x${rows * h}`);
