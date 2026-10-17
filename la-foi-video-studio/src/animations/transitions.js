import { E, lerp } from './easing.js';

/** Entrée d'une scène. `el` = conteneur masqué, `inner` = contenu (contre-zoom). Retourne un anneau doré optionnel. */
export function applyEnter(el, inner, cfg, p, W, H) {
  const e = E.inOutCubic(p), o = E.outCubic(p);
  el.style.opacity = '1'; el.style.clipPath = 'none'; el.style.transform = 'none';
  inner.style.transform = 'none';
  let ring = null;
  switch (cfg.type) {
    case 'fade': el.style.opacity = String(o); break;
    case 'wipe-left': el.style.clipPath = `inset(0 ${(1 - e) * 100}% 0 0)`; inner.style.transform = `scale(${lerp(1.12, 1, o)})`; break;
    case 'wipe-right': el.style.clipPath = `inset(0 0 0 ${(1 - e) * 100}%)`; inner.style.transform = `scale(${lerp(1.12, 1, o)})`; break;
    case 'wipe-up': el.style.clipPath = `inset(${(1 - e) * 100}% 0 0 0)`; inner.style.transform = `translateY(${(1 - o) * -6}%) scale(${lerp(1.1, 1, o)})`; break;
    case 'slide-up': el.style.transform = `translateY(${(1 - E.outQuart(p)) * 100}%)`; break;
    case 'zoom': el.style.opacity = String(o); inner.style.transform = `scale(${lerp(1.35, 1, E.outQuart(p))})`; break;
    case 'circle': {
      const cx = (cfg.cx ?? 0.5) * W, cy = (cfg.cy ?? 0.5) * H;
      const R = Math.hypot(Math.max(cx, W - cx), Math.max(cy, H - cy)) * E.inOutCubic(p);
      el.style.clipPath = `circle(${R}px at ${cx}px ${cy}px)`;
      inner.style.transform = `scale(${lerp(1.15, 1, o)})`;
      if (cfg.ring && p > 0 && p < 1) ring = { cx, cy, r: R, alpha: 1 - p };
      break;
    }
    default: break;
  }
  return ring;
}

/** Sortie discrète : léger zoom et assombrissement, jamais de transparence (la scène suivante recouvre). */
export function applyExit(inner, p) {
  inner.style.filter = p > 0 ? `brightness(${lerp(1, 0.78, E.inOutCubic(p))})` : 'none';
  if (p > 0) inner.style.transform = `scale(${lerp(1, 1.035, E.inOutCubic(p))})`;
}
