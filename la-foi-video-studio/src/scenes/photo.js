import { E, prog, lerp, clamp } from '../animations/easing.js';
import { kineticTitle, kicker } from '../components/kinetic-text.js';
import { sparkles } from '../components/particles.js';
import { div, textBox, titleSize, cameraAt, placeImage } from './common.js';

export function buildPhoto(cfg, ctx) {
  const { fmt, L, brand } = ctx;
  const root = div('sc');
  const first = ctx.image(cfg.images[0].src);

  // Fond flou : sert quand la photo ne couvre pas tout le cadre (16:9, photos 4:5).
  const needsBg = fmt.key === '16x9' || cfg.images.some((i) => i.fit === 'width' && fmt.key === '9x16');
  if (needsBg) {
    const bg = div('bgblur', root); const im = first.cloneNode(); bg.appendChild(im);
    div('bgtint', root);
  }

  const layers = cfg.images.map((ic, i) => {
    const el = ctx.image(ic.src).cloneNode();
    const { w: nw, h: nh } = ctx.size(ic.src);
    const wide = fmt.key === '16x9';
    const fitWidth = ic.fit === 'width' && fmt.key === '9x16';
    const fx = wide ? Math.round(fmt.w * L.photoX) : 0;
    const frame = { x: fx, y: fitWidth ? (ic.top ?? 90) : 0, w: fmt.w - fx, h: fitWidth ? Math.round(fmt.w * nh / nw) : fmt.h };
    const sc = fitWidth ? frame.w / nw : Math.max(frame.w / nw, frame.h / nh);
    const fr = div('frame', root);
    Object.assign(fr.style, { left: `${frame.x}px`, top: `${frame.y}px`, width: `${frame.w}px`, height: `${frame.h}px` });
    Object.assign(el.style, { width: `${nw * sc}px`, height: `${nh * sc}px` });
    fr.appendChild(el);
    return { fr, el, frame, iw: nw * sc, ih: nh * sc, at: ic.at ?? (i === 0 ? 0 : i / cfg.images.length), cam: ic.camera, reveal: ic.reveal };
  });

  div('shade', root);
  const spark = cfg.sparkles ? Object.assign(document.createElement('canvas'), { width: fmt.w, height: fmt.h }) : null;
  if (spark) { spark.className = 'fxcanvas'; root.appendChild(spark); }

  // Pastilles numérotées (ex. les trois documents)
  const chips = (cfg.chips ?? []).map((c) => {
    const el = div('chip', root, `<b>${c.n}</b><span></span>`); el.querySelector('span').textContent = c.label; return { el, at: c.at };
  });
  if (chips.length) {
    const col = fmt.key === '16x9' ? { left: `${L.sideL}px`, top: `${L.top + 40}px` } : { left: `${L.sideL}px`, top: `${L.top + 140}px` };
    chips.forEach((c, i) => { Object.assign(c.el.style, col); c.el.style.marginTop = `${i * 112}px`; });
  }

  const pulse = cfg.pulse ? div('pulse', root, '<i></i><i></i>') : null;

  const box = textBox(root, ctx);
  const k = kicker(box, cfg.kicker);
  const t = kineticTitle(box, cfg.title, { highlight: cfg.highlight });
  t.el.style.fontSize = `${titleSize(cfg.title, fmt.key)}px`;
  const rule = div('rule', box);
  let pill = null;
  if (cfg.urlPill) pill = div('urlpill', box, `<span class="dot"></span>${brand.campaign.url}`);

  return {
    el: root,
    update(lt, dur, t0) {
      layers.forEach((l, i) => {
        const start = l.at * dur, end = (cfg.images[i + 1] ? cfg.images[i + 1].at ?? (i + 1) / cfg.images.length : 1) * dur;
        const vis = lt >= start - 1e-6;
        l.fr.style.display = vis ? 'block' : 'none';
        if (!vis) return;
        const rp = E.inOutCubic(prog(lt, start, 0.8));
        l.fr.style.clipPath = i === 0 || !l.reveal ? 'none' : l.reveal === 'wipe-left' ? `inset(0 ${(1 - rp) * 100}% 0 0)` : 'none';
        l.fr.style.opacity = i === 0 || l.reveal === 'wipe-left' ? '1' : String(rp);
        const cam = cameraAt(l.cam, (lt - start) / Math.max(0.01, end - start));
        l.cur = placeImage(l.el, l.frame, l.iw, l.ih, cam); l.camNow = cam;
      });
      const d0 = 0.35;
      k.update(lt, d0); t.update(lt, d0 + 0.12);
      rule.style.width = `${lerp(0, 220, E.outExpo(prog(lt, d0 + 0.6, 0.8)))}px`;
      if (pill) { const p = E.outBack(prog(lt, d0 + 1.0, 0.7)); pill.style.opacity = String(clamp(p * 3)); pill.style.transform = `translateY(${(1 - p) * 30}px) scale(${lerp(0.9, 1, p)})`; }
      chips.forEach((c) => {
        const q = prog(lt, c.at * dur, 0.6);
        c.el.style.opacity = String(clamp(E.outCubic(q) * 1.5)); c.el.style.transform = `translateX(${(1 - E.outBack(q)) * -120}px) scale(${lerp(0.9, 1, E.outCubic(q))})`;
      });
      if (pulse) {
        const l = layers[0];
        const px = l.frame.x + l.cur.tx + l.camNow.s * cfg.pulse.x * l.iw, py = l.frame.y + l.cur.ty + l.camNow.s * cfg.pulse.y * l.ih;
        pulse.style.left = `${px}px`; pulse.style.top = `${py}px`;
        pulse.style.opacity = String(E.outCubic(prog(lt, 1.2, 0.5)));
        pulse.querySelectorAll('i').forEach((r, i) => { const q = ((lt * 0.9 + i * 0.5) % 1); r.style.transform = `translate(-50%,-50%) scale(${0.4 + q * 1.6})`; r.style.opacity = String((1 - q) * 0.9); });
      }
      if (spark) {
        const W = fmt.w, H = fmt.h;
        sparkles(spark, lt, { from: 0.8, seed: 11, points: fmt.key === '16x9'
          ? [[0.06, 0.3], [0.3, 0.2], [0.36, 0.7], [0.1, 0.8], [0.22, 0.45]].map(([a, b]) => [a * W, b * H])
          : [[0.12, 0.62], [0.86, 0.55], [0.5, 0.6], [0.78, 0.7], [0.25, 0.7], [0.92, 0.66]].map(([a, b]) => [a * W, b * H]) });
      }
    },
  };
}
