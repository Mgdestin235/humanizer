#!/usr/bin/env node
// Génère un fond musical chaleureux (nappes + arpège doux) : aucune dette de droits, remplaçable.
// Usage : node scripts/make-music.mjs [durée_en_secondes]
// Pour utiliser votre propre musique : placez un fichier dans assets/audio/ et renseignez-le dans src/config/audio.json.
import { p } from './lib/util.mjs';
import { SR, writeWav, reverb } from './lib/wav.mjs';

const dur = Number(process.argv[2] ?? 100);
const n = Math.ceil(dur * SR);
const midi = (m) => 440 * 2 ** ((m - 69) / 12);
const chords = [[48, 55, 64, 67], [45, 57, 64, 72], [53, 57, 60, 69], [43, 55, 62, 71]]; // Do, La m, Fa, Sol (ouvert)
const beat = 60 / 84, chordLen = beat * 8;
const L = new Float32Array(n), R = new Float32Array(n);

for (let c = 0; c * chordLen < dur + chordLen; c++) {
  const ch = chords[c % chords.length], t0 = c * chordLen;
  ch.forEach((m, j) => {
    for (const det of [-0.12, 0.12]) {
      const f = midi(m) * 2 ** (det / 12);
      const i0 = Math.floor(t0 * SR), len = Math.floor((chordLen + 1.6) * SR);
      for (let i = 0; i < len && i0 + i < n; i++) {
        const t = i / SR, env = Math.min(1, t / 1.2) * Math.min(1, (chordLen + 1.6 - t) / 1.4);
        const s = (Math.sin(2 * Math.PI * f * t) + 0.35 * Math.sin(4 * Math.PI * f * t) + 0.12 * Math.sin(6 * Math.PI * f * t)) * env * 0.055;
        const pan = (j / 3 - 0.5) * 0.5;
        L[i0 + i] += s * (0.5 - pan); R[i0 + i] += s * (0.5 + pan);
      }
    }
  });
  // arpège de cloches douces
  const pat = [0, 2, 1, 3, 2, 1, 3, 2];
  pat.forEach((idx, k) => {
    const t = t0 + k * beat, f = midi(ch[idx] + 24), i0 = Math.floor(t * SR), len = Math.floor(1.4 * SR);
    for (let i = 0; i < len && i0 + i < n; i++) {
      const tt = i / SR, e = Math.exp(-tt * 3.2) * Math.min(1, tt / 0.004);
      const s = (Math.sin(2 * Math.PI * f * tt) + 0.3 * Math.sin(2 * Math.PI * f * 2.76 * tt) * Math.exp(-tt * 6)) * e * 0.05;
      const pan = ((k % 4) / 3 - 0.5) * 0.8; L[i0 + i] += s * (0.5 - pan); R[i0 + i] += s * (0.5 + pan);
    }
  });
}
const wl = reverb(L), wr = reverb(R);
let peak = 0; for (let i = 0; i < n; i++) peak = Math.max(peak, Math.abs(wl[i]), Math.abs(wr[i]));
const g = 0.7 / peak; for (let i = 0; i < n; i++) { wl[i] *= g; wr[i] *= g; }
writeWav(p('assets/audio/musique-fond.wav'), wl, wr);
console.log(`Musique générée : assets/audio/musique-fond.wav (${dur.toFixed(0)} s)`);
