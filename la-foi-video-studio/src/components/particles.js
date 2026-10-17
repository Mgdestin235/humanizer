import { rng } from '../animations/easing.js';

/** Confettis dorés déterministes : même position pour un même instant. */
export function confetti(canvas, t, { count = 70, seed = 7, colors = ['#F2C14E', '#FFE39A', '#FFFFFF', '#0B8A44'], from = 0, fade = 1.2 } = {}) {
  const ctx = canvas.getContext('2d'); const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  const lt = t - from; if (lt < 0) return;
  const r = rng(seed);
  for (let i = 0; i < count; i++) {
    const x0 = r() * W, vx = (r() - 0.5) * 220, vy = -300 - r() * 520, rot0 = r() * 6.28, vr = (r() - 0.5) * 9;
    const w = 10 + r() * 16, h = 6 + r() * 10, color = colors[Math.floor(r() * colors.length)], delay = r() * 0.7;
    const tt = lt - delay; if (tt < 0) continue;
    const g = 640, y = H * 0.62 + vy * tt + 0.5 * g * tt * tt, x = x0 + vx * tt;
    if (y > H + 40) continue;
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot0 + vr * tt); ctx.scale(1, Math.cos(tt * 6 + i));
    ctx.globalAlpha = Math.min(1, Math.max(0, (3.4 - tt) / fade));
    ctx.fillStyle = color; ctx.fillRect(-w / 2, -h / 2, w, h); ctx.restore();
  }
}

/** Étincelles à quatre branches qui scintillent autour d'un point. */
export function sparkles(canvas, t, { points, seed = 3, from = 0, size = 26 }) {
  const ctx = canvas.getContext('2d'); ctx.clearRect(0, 0, canvas.width, canvas.height);
  const r = rng(seed);
  points.forEach(([px, py], i) => {
    const ph = r() * 6.28, sp = 2 + r() * 2;
    const a = Math.max(0, Math.sin((t - from) * sp + ph)) * Math.min(1, Math.max(0, (t - from) * 2));
    if (a <= 0.02) return;
    const s = size * (0.5 + r() * 0.8) * a;
    ctx.save(); ctx.translate(px, py); ctx.globalAlpha = a; ctx.fillStyle = '#FFE39A';
    ctx.beginPath();
    for (let k = 0; k < 4; k++) { const ang = k * Math.PI / 2; ctx.lineTo(Math.cos(ang) * s, Math.sin(ang) * s); ctx.lineTo(Math.cos(ang + Math.PI / 4) * s * 0.22, Math.sin(ang + Math.PI / 4) * s * 0.22); }
    ctx.closePath(); ctx.fill(); ctx.restore();
  });
}
