#!/usr/bin/env node
// Capture des images fixes pour vérification : node scripts/still.mjs <format> <sortie.png> <t1> <t2> ...
import path from 'node:path';
import fs from 'node:fs';
import { serve } from './lib/server.mjs';
import { loadPlaywright, chromiumPath, p } from './lib/util.mjs';

const [format = '9x16', outDir = p('output/verif'), ...ts] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const { chromium } = await loadPlaywright();
const { server, port } = await serve(0);
const dims = { '9x16': [1080, 1920], '1x1': [1080, 1080], '16x9': [1920, 1080] }[format];
const browser = await chromium.launch({ executablePath: chromiumPath(), args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: dims[0], height: dims[1] } });
page.on('console', (m) => ['error', 'warning'].includes(m.type()) && console.log('[page]', m.text()));
page.on('response', (r) => r.status() >= 400 && console.log('[404]', r.url()));
page.on('pageerror', (e) => console.log('[erreur page]', e.message));
await page.goto(`http://127.0.0.1:${port}/src/compositions/index.html?format=${format}`);
await page.waitForFunction('window.__ready === true', null, { timeout: 60000 });
for (const t of ts) {
  await page.evaluate((x) => window.__comp.setTime(x), Number(t));
  const f = path.join(outDir, `${format}_t${String(t).replace('.', '_')}.png`);
  await page.screenshot({ path: f }); console.log(f);
}
await browser.close(); server.close();
