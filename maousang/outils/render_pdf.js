// Imprime une page HTML locale en PDF A4. Usage : node render_pdf.js in.html out.pdf
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [inp, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(inp), { waitUntil: 'load' });
  await page.pdf({
    path: out, format: 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;color:#64748B;width:100%;padding:0 16mm;display:flex;justify-content:space-between;font-family:Arial">'
      + '<span>MAOUSANG · Business plan · Données financières prévisionnelles</span>'
      + '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' },
  });
  await browser.close();
  console.log('pdf ok', out);
})();
