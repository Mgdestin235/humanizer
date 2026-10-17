#!/usr/bin/env node
// Effets sonores discrets synchronisés sur les transitions (whoosh) et les moments clés (cloche).
import { p, readJson } from './lib/util.mjs';
import { SR, writeWav, reverb } from './lib/wav.mjs';

const tl = readJson(p('src/config/timeline.json'));
const n = Math.ceil((tl.duration + 1) * SR);
const L = new Float32Array(n), R = new Float32Array(n);
let seed = 12345; const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296) * 2 - 1;

function whoosh(t0) {
  const len = Math.floor(0.75 * SR), i0 = Math.floor(t0 * SR); let y = 0, y2 = 0;
  for (let i = 0; i < len && i0 + i < n; i++) {
    const u = i / len, env = Math.sin(Math.PI * u) ** 2 * 0.22, a = 0.02 + 0.3 * u * u;
    y += a * (rnd() - y); y2 += a * (y - y2);
    const s = (y - y2) * 3 * env, pan = (u - 0.5) * 0.7;
    L[i0 + i] += s * (0.5 - pan); R[i0 + i] += s * (0.5 + pan);
  }
}
function bell(t0, f = 880) {
  const len = Math.floor(2.2 * SR), i0 = Math.floor(t0 * SR);
  for (let i = 0; i < len && i0 + i < n; i++) {
    const t = i / SR, e = Math.exp(-t * 2.4);
    const s = (Math.sin(2 * Math.PI * f * t) + 0.5 * Math.sin(2 * Math.PI * f * 2.01 * t) * Math.exp(-t * 3) + 0.25 * Math.sin(2 * Math.PI * f * 3.97 * t) * Math.exp(-t * 5)) * e * 0.16;
    L[i0 + i] += s; R[i0 + i] += s;
  }
}
for (const s of tl.scenes) {
  const t = s.start + (s.enter?.dur ?? 0.6) * 0.15;
  if (s.sfx === 'whoosh') whoosh(Math.max(0, s.start - 0.05));
  if (s.sfx === 'bell') { bell(t + 0.2); bell(t + 0.45, 1318.5); }
}
writeWav(p('output/tmp/sfx.wav'), reverb(L, 0.2), reverb(R, 0.2));
console.log('Effets sonores générés.');
