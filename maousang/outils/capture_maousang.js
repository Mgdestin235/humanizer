// Capture les écrans de Maousang au format smartphone, pour le pitch deck.
//
// Prérequis (sur votre ordinateur) : Node.js, puis
//   npm install playwright && npx playwright install chromium
//
// Mode guidé (recommandé, gère la connexion à un compte) :
//   node capture_maousang.js guide
//   Une fenêtre de navigateur s'ouvre. Pour chaque écran demandé, naviguez
//   jusqu'à lui, puis appuyez sur Entrée dans le terminal (s = passer).
//
// Mode automatique (pages publiques seulement) :
//   node capture_maousang.js auto
//   Capture l'accueil, puis chaque page liée dont l'adresse ou le texte
//   correspond à un écran attendu.
//
// Les images sont écrites dans ../assets/captures/<clé>.png.
const path = require('path');
const fs = require('fs');
const readline = require('readline');
const { chromium, devices } = require('playwright');

const BASE = process.env.MAOUSANG_URL || 'https://maousang.vercel.app';
const OUT = path.join(__dirname, '..', 'assets', 'captures');

// Clé (nom attendu par le deck) -> libellé et mots-clés pour le mode automatique
const SCREENS = [
  ['01_accueil', "Page d'accueil", []],
  ['02_inscription', 'Inscription', ['inscri', 'register', 'signup', 'sign-up']],
  ['03_connexion', 'Connexion', ['connex', 'login', 'signin', 'sign-in']],
  ['04_tableau_de_bord', 'Menu des services / tableau de bord', ['dashboard', 'tableau', 'services', 'accueil-user']],
  ['05_billetterie_recherche', 'Billetterie : recherche de voyages', ['billet', 'ticket', 'voyage']],
  ['06_billetterie_resultats', 'Billetterie : offres et réservation', ['reservation', 'offre']],
  ['07_clando_demande', 'Clando : demande de course', ['clando', 'moto', 'course', 'mobilit']],
  ['08_livraison', 'Livraison (repas, courses, colis)', ['livraison', 'delivery', 'colis']],
  ['09_emploi_offres', "Emploi : offres d'emploi", ['emploi', 'job', 'offres']],
  ['10_emploi_ats', 'Emploi : tableau ATS recruteur', ['ats', 'recrut', 'candidat']],
  ['11_immobilier_recherche', 'Immobilier : recherche', ['immobil', 'logement', 'house', 'location']],
  ['12_immobilier_annonce', "Immobilier : fiche d'annonce", ['bien', 'property', 'detail']],
  ['13_annonces', 'Annonces', ['annonce', 'ads', 'classified']],
  ['14_assistant_ia', 'Assistant IA', ['assistant', 'ia', 'ai', 'chat']],
];

async function shot(page, key) {
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(OUT, `${key}.png`) });
  console.log(`  ✔ ${key}.png`);
}

async function guided() {
  const browser = await chromium.launch({ headless: false });
  const ctx = await browser.newContext({ ...devices['iPhone 13'] });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: 'networkidle' });
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise((r) => rl.question(q, r));
  for (const [key, label] of SCREENS) {
    const a = await ask(`\nOuvrez l'écran « ${label} » puis Entrée (s = passer) : `);
    if (a.trim().toLowerCase() === 's') continue;
    await shot(page, key);
  }
  rl.close();
  await browser.close();
}

async function auto() {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ ...devices['iPhone 13'] });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await shot(page, '01_accueil');
  const links = await page.$$eval('a[href]', (as) => as.map((a) => ({ href: a.href, text: (a.innerText || '').toLowerCase() })));
  const origin = new URL(BASE).origin;
  const seen = new Set();
  for (const [key, , words] of SCREENS.slice(1)) {
    const hit = links.find((l) => l.href.startsWith(origin) && !seen.has(l.href) &&
      words.some((w) => l.href.toLowerCase().includes(w) || l.text.includes(w)));
    if (!hit) { console.log(`  – ${key} : aucun lien trouvé, utilisez le mode guidé`); continue; }
    seen.add(hit.href);
    await page.goto(hit.href, { waitUntil: 'networkidle' });
    await shot(page, key);
  }
  await browser.close();
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const mode = process.argv[2] || 'guide';
  console.log(`Captures de ${BASE} -> ${OUT}`);
  await (mode === 'auto' ? auto() : guided());
  console.log('\nÉtape suivante : python3 insert_screenshots.py');
})();
