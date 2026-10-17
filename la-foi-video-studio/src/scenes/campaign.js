import { E, prog, lerp, clamp } from '../animations/easing.js';
import { kineticTitle, kicker } from '../components/kinetic-text.js';
import { confetti } from '../components/particles.js';
import { div, titleSize } from './common.js';

/** Scène « animation de la campagne » : logo, titre cinétique, confettis dorés. */
export function buildCampaign(cfg, ctx) {
  const { fmt, L, brand } = ctx;
  const root = div('sc campaign');
  const bg = div('bgblur', root); bg.appendChild(ctx.image(cfg.background).cloneNode());
  div('bgtint strong', root);
  const rays = div('rays', root);
  const wide = fmt.key === '16x9';
  const cx = wide ? fmt.w * 0.27 : fmt.w / 2, cy = wide ? fmt.h * 0.5 : fmt.h * 0.31;
  const logoSize = wide ? 520 : fmt.key === '1x1' ? 340 : 520;
  Object.assign(rays.style, { left: `${cx}px`, top: `${cy}px` });
  const halo = div('halo', root); Object.assign(halo.style, { left: `${cx}px`, top: `${cy}px`, width: `${logoSize * 1.35}px`, height: `${logoSize * 1.35}px` });
  const logo = div('medallion', root, `<img src="/${brand.logo}" alt="Logo Cabinet Médical LA FOI">`);
  Object.assign(logo.style, { left: `${cx}px`, top: `${cy}px`, width: `${logoSize}px`, height: `${logoSize}px` });
  const cv = Object.assign(document.createElement('canvas'), { width: fmt.w, height: fmt.h }); cv.className = 'fxcanvas'; root.appendChild(cv);

  const box = div('txt center', root);
  if (wide) Object.assign(box.style, { left: `${fmt.w * 0.5}px`, width: `${fmt.w * 0.44}px`, top: '0', bottom: '0', justifyContent: 'center' });
  else Object.assign(box.style, { left: `${L.sideL}px`, right: `${L.sideR}px`, top: `${cy + logoSize / 2 + 60}px` });
  const k = kicker(box, cfg.kicker);
  const t = kineticTitle(box, cfg.title, { highlight: cfg.highlight });
  t.el.style.fontSize = `${wide ? 104 : fmt.key === '1x1' ? 84 : 112}px`;
  const sub = div('sub', box); sub.textContent = cfg.subtitle;
  const seal = div('seal', root, `<span>${brand.campaign.date.toUpperCase()}</span>`);
  Object.assign(seal.style, wide ? { right: '90px', top: '60px' } : { right: `${L.sideR - 20}px`, top: `${L.top + 40}px` });

  return {
    el: root,
    update(lt) {
      const p = E.outBack(prog(lt, 0.25, 0.9));
      logo.style.transform = `translate(-50%,-50%) scale(${lerp(0.55, 1, p) * (1 + 0.012 * Math.sin(lt * 1.6))}) rotate(${lerp(-12, 0, E.outCubic(prog(lt, 0.25, 1.1)))}deg)`;
      logo.style.opacity = String(clamp(p * 2));
      halo.style.opacity = String(0.5 + 0.2 * Math.sin(lt * 2));
      rays.style.transform = `translate(-50%,-50%) rotate(${lt * 9}deg)`;
      rays.style.opacity = String(E.outCubic(prog(lt, 0.2, 1)) * 0.55);
      k.update(lt, 0.9); t.update(lt, 1.05);
      const sp = E.outCubic(prog(lt, 2.0, 0.7)); sub.style.opacity = String(sp); sub.style.transform = `translateY(${(1 - sp) * 24}px)`;
      const sl = E.outBack(prog(lt, 1.6, 0.7)); seal.style.opacity = String(clamp(sl * 2)); seal.style.transform = `scale(${lerp(0.6, 1, sl)}) rotate(${lerp(-18, -6, sl)}deg)`;
      confetti(cv, lt, { from: 0.9, count: 80, seed: 21 });
    },
  };
}
