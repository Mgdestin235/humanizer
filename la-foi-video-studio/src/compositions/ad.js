import { E, prog, clamp, lerp } from '../animations/easing.js';
import { applyEnter, applyExit } from '../animations/transitions.js';
import { TEMPLATES } from '../scenes/index.js';
import { createSubtitles } from '../subtitles/layer.js';
import { div } from '../scenes/common.js';

const q = new URLSearchParams(location.search);

export async function mount() {
  const tl = await (await fetch(`/src/config/timeline.json?${Date.now()}`)).json();
  const brand = tl.brand;
  const key = q.get('format') ?? '9x16';
  const L = brand.layout[key];
  const fmt = { key, w: L.w, h: L.h };
  const stage = document.getElementById('stage');
  Object.assign(document.getElementById('viewport').style, { width: `${fmt.w}px`, height: `${fmt.h}px` });
  stage.className = `fmt-${key}`;
  Object.assign(stage.style, { width: `${fmt.w}px`, height: `${fmt.h}px` });
  const css = document.documentElement.style;
  const c = brand.colors;
  css.setProperty('--green', c.green); css.setProperty('--greenDark', c.greenDark); css.setProperty('--greenDeep', c.greenDeep);
  css.setProperty('--gold', c.gold); css.setProperty('--goldLight', c.goldLight); css.setProperty('--ink', c.ink); css.setProperty('--blue', c.blue);
  css.setProperty('--font', `'${brand.font}', system-ui, sans-serif`);
  css.setProperty('--subSize', `${brand.subtitles.fontSize * (key === '16x9' ? 0.9 : key === '1x1' ? 0.85 : 1)}px`);

  // Chargement des images (versions agrandies _hd)
  const dims = new Map(), loaded = new Map();
  const hd = (src) => '/' + src.replace('assets/images/', 'assets/images/_hd/').replace(/\.[a-z]+$/i, '.png');
  const srcs = new Set();
  tl.scenes.forEach((s) => { (s.images ?? []).forEach((i) => srcs.add(i.src)); if (s.background) srcs.add(s.background); });
  await Promise.all([...srcs].map(async (s) => {
    const im = new Image(); im.src = hd(s); await im.decode(); loaded.set(s, im); dims.set(s, { w: im.naturalWidth, h: im.naturalHeight });
  }));
  await Promise.all(['500', '600', '700', '800', '900'].map((w) => document.fonts.load(`${w} 40px Inter`)));
  await document.fonts.ready;

  const ctx = { fmt, L, brand, image: (s) => loaded.get(s).cloneNode(), size: (s) => dims.get(s) };
  const scenesEl = div('scenes', stage);
  const fx = Object.assign(document.createElement('canvas'), { width: fmt.w, height: fmt.h });
  const built = tl.scenes.map((s, i) => {
    const holder = div('scene', scenesEl); holder.style.zIndex = String(i + 1);
    const inner = div('scene-inner', holder);
    const inst = TEMPLATES[s.template](s, ctx);
    inner.appendChild(inst.el);
    return { cfg: s, holder, inner, inst };
  });
  const ringEl = div('ringfx', stage);
  const badge = div('badge', stage, `<img src="/${brand.logo}" alt=""><span>ANNIVERSAIRE · ${brand.campaign.date.replace('octobre', 'OCT.').toUpperCase()}</span>`);
  Object.assign(badge.style, { left: `${L.sideL}px`, top: `${L.top}px` });
  const subs = createSubtitles(stage, tl.cues, ctx);
  const showSubs = q.get('subs') !== '0';
  await Promise.all([...document.images].map((i) => i.decode().catch(() => {})));

  function setTime(t, opts = {}) {
    let ring = null;
    built.forEach((b, i) => {
      const { cfg, holder, inner, inst } = b;
      const nextStart = tl.scenes[i + 1]?.start ?? Infinity;
      const visible = t >= cfg.start && t < cfg.end;
      holder.style.display = visible ? 'block' : 'none';
      if (!visible) return;
      const lt = t - cfg.start, dur = cfg.end - cfg.start;
      const r = applyEnter(holder, inner, cfg.enter, prog(lt, 0, cfg.enter.dur), fmt.w, fmt.h);
      if (r) ring = r;
      inst.update(lt, dur);
      if (t > nextStart) applyExit(inner, prog(t, nextStart, tl.scenes[i + 1].enter.dur));
      else inner.style.filter = 'none';
    });
    if (ring) { Object.assign(ringEl.style, { display: 'block', left: `${ring.cx - ring.r}px`, top: `${ring.cy - ring.r}px`, width: `${ring.r * 2}px`, height: `${ring.r * 2}px`, opacity: String(ring.alpha) }); }
    else ringEl.style.display = 'none';
    // pastille de marque : discrète, absente des scènes qui montrent déjà le grand logo
    const cur = [...tl.scenes].reverse().find((s) => t >= s.start);
    const on = cur && cur.brandBadge !== false && !['campaign', 'finale'].includes(cur.template) && t > 1.0;
    badge.style.opacity = String(on ? clamp((t - Math.max(1.0, cur.start)) / 0.4) : 0);
    subs.update(t, showSubs && opts.subs !== false);
    // fondu d'entrée / sortie global
    stage.style.setProperty('--fade', String(clamp(Math.min(t / 0.5, (tl.duration - t) / 0.8))));
    document.getElementById('fadeout').style.opacity = String(1 - clamp(Math.min(t / 0.4, (tl.duration - t) / 0.9)));
  }
  return { tl, fmt, setTime, duration: tl.duration, fps: tl.fps };
}
