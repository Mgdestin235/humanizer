import { E, prog, lerp } from '../animations/easing.js';

/** Sous-titres cinétiques : groupe court de mots, mot-clé doré qui « pulse » au moment où il est prononcé. */
export function createSubtitles(parent, cues, { fmt, L }) {
  const box = document.createElement('div'); box.className = 'subs';
  box.style.bottom = `${fmt.h - L.subBottom}px`;
  if (fmt.key === '9x16') { box.style.left = `${L.sideL - 10}px`; box.style.right = `${L.sideR - 10}px`; }
  else { box.style.left = '8%'; box.style.right = '8%'; }
  parent.appendChild(box);
  let cur = -1, spans = [];
  return {
    el: box,
    update(t, enabled = true) {
      let idx = -1;
      if (enabled) for (let i = 0; i < cues.length; i++) { if (t >= cues[i].start && t < cues[i].end) { idx = i; break; } }
      if (idx !== cur) {
        cur = idx; box.innerHTML = ''; spans = [];
        if (idx >= 0) cues[idx].words.forEach((w) => {
          const s = document.createElement('span'); s.className = 'sw' + (w.hl ? ' hl' : '');
          s.textContent = w.hl ? w.w.toUpperCase() : w.w; box.appendChild(s); box.appendChild(document.createTextNode(' ')); spans.push(s);
        });
      }
      if (idx < 0) { box.style.opacity = '0'; return; }
      const c = cues[idx], lt = t - c.start, out = prog(t, c.end - 0.12, 0.12);
      const p = E.outBack(prog(lt, 0, 0.22));
      box.style.opacity = String(Math.min(1, lt / 0.1) * (1 - out));
      box.style.transform = `translateY(${(1 - p) * 22}px) scale(${lerp(0.96, 1, p)})`;
      c.words.forEach((w, i) => {
        if (!w.hl) return;
        const q = prog(t, w.start, 0.35), bump = Math.sin(q * Math.PI) * 0.14;
        spans[i].style.transform = `scale(${1 + bump})`;
      });
    },
  };
}
