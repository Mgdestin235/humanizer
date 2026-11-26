// Convertit chaque .svg d'un dossier en .png (fond transparent) avec Chromium.
// Usage : node render_svg.js <dossier>
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const w = parseInt(/width="(\d+)"/.exec(svg)[1], 10);
    const h = parseInt(/height="(\d+)"/.exec(svg)[1], 10);
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await page.screenshot({ path: path.join(dir, f.replace('.svg', '.png')), omitBackground: true,
      clip: { x: 0, y: 0, width: w, height: h } });
  }
  await browser.close();
  console.log('png ok');
})();
