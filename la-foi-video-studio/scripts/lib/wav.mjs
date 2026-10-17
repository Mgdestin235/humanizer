import fs from 'node:fs';
export const SR = 44100;
/** Écrit un WAV 16 bits stéréo à partir de deux Float32Array. */
export function writeWav(file, L, R) {
  const n = L.length, buf = Buffer.alloc(44 + n * 4);
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22); buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28);
  buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(n * 4, 40);
  const c = (x) => Math.max(-32768, Math.min(32767, Math.round(x * 32767)));
  for (let i = 0; i < n; i++) { buf.writeInt16LE(c(L[i]), 44 + i * 4); buf.writeInt16LE(c(R[i]), 46 + i * 4); }
  fs.writeFileSync(file, buf);
}
/** Réverbération douce (peignes en parallèle). */
export function reverb(x, mix = 0.28) {
  const out = new Float32Array(x.length);
  for (const [d, g] of [[1557, 0.78], [1617, 0.76], [1491, 0.77], [1422, 0.75], [1277, 0.74]]) {
    const buf = new Float32Array(d); let k = 0;
    for (let i = 0; i < x.length; i++) { const y = buf[k]; buf[k] = x[i] + y * g; k = (k + 1) % d; out[i] += y * 0.2; }
  }
  for (let i = 0; i < x.length; i++) out[i] = x[i] * (1 - mix) + out[i] * mix * 2;
  return out;
}
