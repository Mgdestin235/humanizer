import { E, prog, lerp, clamp } from '../animations/easing.js';
import { kineticTitle, kicker } from '../components/kinetic-text.js';
import { confetti } from '../components/particles.js';
import { div } from './common.js';

/** Appel à l'action final : logo officiel, date de lancement, adresse de réservation. */
export function buildFinale(cfg, ctx) {
  const { fmt, L, brand } = ctx;
  const root = div('sc finale');
  const bg = div('bgblur', root); bg.appendChild(ctx.image(cfg.background).cloneNode());
  div('bgtint strong', root);
  const wide = fmt.key === '16x9';
  const cx = wide ? fmt.w * 0.27 : fmt.w / 2, cy = wide ? fmt.h * 0.5 : fmt.h * 0.27;
  const size = wide ? 560 : fmt.key === '1x1' ? 330 : 500;
  const ring = div('goldring', root); Object.assign(ring.style, { left: `${cx}px`, top: `${cy}px`, width: `${size + 60}px`, height: `${size + 60}px` });
  const logo = div('medallion', root, `<img src="/${brand.logo}" alt="Logo Cabinet Médical LA FOI">`);
  Object.assign(logo.style, { left: `${cx}px`, top: `${cy}px`, width: `${size}px`, height: `${size}px` });
  const cv = Object.assign(document.createElement('canvas'), { width: fmt.w, height: fmt.h }); cv.className = 'fxcanvas'; root.appendChild(cv);

  const box = div('txt center', root);
  if (wide) Object.assign(box.style, { left: `${fmt.w * 0.5}px`, width: `${fmt.w * 0.44}px`, top: '0', bottom: '0', justifyContent: 'center' });
  else Object.assign(box.style, { left: `${L.sideL}px`, right: `${L.sideR}px`, top: `${cy + size / 2 + 50}px` });
  const k = kicker(box, cfg.kicker);
  const t = kineticTitle(box, cfg.title, { highlight: cfg.highlight });
  t.el.style.fontSize = `${wide ? 104 : fmt.key === '1x1' ? 80 : 104}px`;
  const cta = div('cta', box, `<span class="dot"></span><b>${cfg.subtitle}</b><em>${brand.campaign.url}</em>`);
  const tag = div('tagline', box); tag.textContent = cfg.perk ?? brand.campaign.tagline;
  if (brand.campaign.showPhone) tag.textContent += `  ·  ${brand.campaign.phone}`;

  return {
    el: root,
    update(lt, dur) {
      const p = E.outBack(prog(lt, 0.3, 0.9));
      logo.style.transform = `translate(-50%,-50%) scale(${lerp(0.6, 1, p)})`; logo.style.opacity = String(clamp(p * 2));
      ring.style.opacity = String(E.outCubic(prog(lt, 0.4, 0.8)) * 0.9); ring.style.transform = `translate(-50%,-50%) rotate(${lt * 22}deg) scale(${lerp(0.7, 1, E.outCubic(prog(lt, 0.3, 1)))})`;
      k.update(lt, 0.9); t.update(lt, 1.0);
      const c = E.outBack(prog(lt, 2.0, 0.8)); cta.style.opacity = String(clamp(c * 2)); cta.style.transform = `translateY(${(1 - c) * 40}px) scale(${lerp(0.92, 1, c)})`;
      cta.style.boxShadow = `0 0 ${24 + 14 * Math.sin(lt * 3)}px rgba(242,193,78,.55)`;
      const g = E.outCubic(prog(lt, 2.6, 0.7)); tag.style.opacity = String(g); tag.style.transform = `translateY(${(1 - g) * 20}px)`;
      confetti(cv, lt, { from: 0.8, count: 60, seed: 5 });
    },
  };
}
