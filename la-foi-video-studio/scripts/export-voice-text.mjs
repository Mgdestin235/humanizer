#!/usr/bin/env node
// Écrit le texte à donner à ElevenLabs : un paragraphe par unité du script (les pauses entre paragraphes servent à l'alignement).
import fs from 'node:fs';
import { p, readJson } from './lib/util.mjs';
const script = readJson(p('src/config/script.json'));
fs.writeFileSync(p('assets/audio/texte-voix-off.txt'), script.units.map((u) => u.text).join('\n\n') + '\n');
console.log(`assets/audio/texte-voix-off.txt (${script.units.length} paragraphes)`);
