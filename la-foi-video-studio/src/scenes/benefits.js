import { E, prog, lerp, clamp } from '../animations/easing.js';
import { kineticTitle, kicker } from '../components/kinetic-text.js';
import { icon } from '../components/icons.js';
import { div, titleSize } from './common.js';

/** Cartes d'avantages animées (icônes dorées, entrée en cascade). */
export function buildBenefits(cfg, ctx) {
  const { fmt, L } = ctx;
  const root = div('sc benefits');
  const bg = div('bgblur', root); bg.appendChild(ctx.image(cfg.background).cloneNode());
  div('bgtint strong', root);
  const wide = fmt.key === '16x9';
  const head = div('head', root);
  Object.assign(head.style, wide ? { left: `${L.sideL}px`, top: '0', bottom: '0', width: '640px', justifyContent: 'center' } : { left: `${L.sideL}px`, right: `${L.sideR}px`, top: `${L.top + 130}px` });
  const k = kicker(head, cfg.kicker);
  const t = kineticTitle(head, cfg.title, { highlight: cfg.highlight });
  t.el.style.fontSize = `${titleSize(cfg.title, fmt.key) * (wide ? 0.95 : fmt.key === '1x1' ? 0.8 : 0.95)}px`;

  const list = div('cards', root);
  Object.assign(list.style, wide ? { left: `${fmt.w * 0.5}px`, right: '100px', top: '0', bottom: '0', justifyContent: 'center' }
    : { left: `${L.sideL}px`, right: `${L.sideR}px`, top: `${L.top + (fmt.key === '1x1' ? 390 : 600)}px` });
  const cards = cfg.cards.map((c) => {
    const el = div('card', list, `<span class="ic">${icon(c.icon, 56, '#06210F')}</span><span class="lb"></span>`);
    el.querySelector('.lb').textContent = c.label; return { el, at: c.at };
  });
  if (fmt.key === '1x1') list.style.gap = '12px';
  return {
    el: root,
    update(lt, dur) {
      k.update(lt, 0.3); t.update(lt, 0.45);
      cards.forEach((c, i) => {
        const q = prog(lt, c.at * dur, 0.75), e = E.outBack(q);
        c.el.style.opacity = String(clamp(E.outCubic(q) * 1.6));
        c.el.style.transform = `translateX(${(1 - e) * 140}px) scale(${lerp(0.94, 1, E.outCubic(q))})`;
        c.el.querySelector('.ic').style.transform = `rotate(${(1 - E.outCubic(prog(lt, c.at * dur + 0.15, 0.8))) * -90}deg) scale(${lerp(0.6, 1, E.outBack(prog(lt, c.at * dur + 0.1, 0.6)))})`;
      });
    },
  };
}
