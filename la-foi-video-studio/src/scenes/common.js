import { clamp } from '../animations/easing.js';

export const div = (cls, parent, html) => {
  const d = document.createElement('div'); if (cls) d.className = cls;
  if (html != null) d.innerHTML = html; if (parent) parent.appendChild(d); return d;
};

/** Taille du titre selon sa longueur et le format, pour rester lisible sans déborder. */
export function titleSize(text, fmtKey) {
  const n = text.length;
  const base = n <= 16 ? 112 : n <= 24 ? 104 : n <= 34 ? 92 : 80;
  return Math.round(base * (fmtKey === '16x9' ? 0.8 : fmtKey === '1x1' ? 0.82 : 1));
}

/** Bloc de texte (rubrique + titre + sous-titre) placé selon le format. */
export function textBox(root, ctx) {
  const { L, fmt } = ctx;
  const box = div('txt', root);
  box.style.left = `${L.sideL}px`;
  if (fmt.key === '16x9') { box.style.width = `${L.textWidth}px`; }
  else { box.style.right = `${L.sideR}px`; box.style.bottom = `${fmt.h - L.titleBottom}px`; }
  return box;
}

/** Applique une caméra à clés : s = zoom, (x,y) = point de l'image placé au centre du cadre. */
export function cameraAt(keys, p) {
  p = clamp(p);
  let i = 0; while (i < keys.length - 2 && p > keys[i + 1].at) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const span = Math.max(1e-6, b.at - a.at);
  const u = clamp((p - a.at) / span);
  const e = 0.5 * u + 0.5 * (u < 0.5 ? 4 * u ** 3 : 1 - (-2 * u + 2) ** 3 / 2);
  return { s: a.s + (b.s - a.s) * e, x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e };
}

/** Place l'image dans son cadre sans jamais déformer ni laisser de bord vide. */
export function placeImage(img, frame, iw, ih, cam) {
  const tx = clamp(frame.w / 2 - cam.s * cam.x * iw, frame.w - cam.s * iw, 0);
  const ty = clamp(frame.h / 2 - cam.s * cam.y * ih, frame.h - cam.s * ih, 0);
  img.style.transform = `translate(${tx}px,${ty}px) scale(${cam.s})`;
  return { tx, ty };
}
