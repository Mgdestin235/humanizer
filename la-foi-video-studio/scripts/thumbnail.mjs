#!/usr/bin/env node
// Miniature publicitaire 1080×1920 (ou --format) : image de la scène choisie. Usage : node scripts/thumbnail.mjs [t=secondes] [format]
import { run, p, readJson } from './lib/util.mjs';
const tl = readJson(p('src/config/timeline.json'));
const t = process.argv[2] ?? (tl.scenes.find((s) => s.template === 'campaign').start + 3.2).toFixed(2);
const format = process.argv[3] ?? '9x16';
run('node', [p('scripts/still.mjs'), format, p('output/tmp/thumb'), t]);
import fs from 'node:fs';
const f = fs.readdirSync(p('output/tmp/thumb')).find((x) => x.startsWith(format));
fs.copyFileSync(p('output/tmp/thumb', f), p(`output/miniature_${format}.png`));
console.log(`output/miniature_${format}.png (t=${t}s)`);
