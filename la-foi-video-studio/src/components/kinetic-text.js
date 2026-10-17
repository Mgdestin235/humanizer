import { E, prog, lerp } from '../animations/easing.js';

const strip = (s) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

/** Découpe le texte en mots ; les mots appartenant à une expression de `highlight` passent en doré. */
export function tokens(text, highlight = []) {
  const ws = text.split(/\s+/).filter(Boolean).map((w) => ({ w, hl: false }));
  for (const h of highlight) {
    const ph = strip(h).split(/\s+/);
    for (let i = 0; i + ph.length <= ws.length; i++) {
      if (ph.every((k, j) => strip(ws[i + j].w).replace(/[^a-z0-9'’-]/g, '').replace(/^(l|d|qu)['’]/, '') === k.replace(/^(l|d|qu)['’]/, ''))) {
        for (let j = 0; j < ph.length; j++) ws[i + j].hl = true;
      }
    }
  }
  return ws;
}

/** Titre cinétique : chaque mot monte depuis un masque, en cascade. */
export function kineticTitle(parent, text, { highlight = [], className = 'title', stagger = 0.085 } = {}) {
  const box = document.createElement('div');
  box.className = className;
  const spans = tokens(text, highlight).map(({ w, hl }) => {
    const mask = document.createElement('span'); mask.className = 'wmask';
    const inner = document.createElement('span'); inner.className = 'w' + (hl ? ' hl' : '');
    inner.textContent = w; mask.appendChild(inner); box.appendChild(mask);
    box.appendChild(document.createTextNode(' '));
    return inner;
  });
  parent.appendChild(box);
  return {
    el: box,
    update(lt, t0 = 0.25) {
      spans.forEach((s, i) => {
        const p = prog(lt, t0 + i * stagger, 0.7);
        const e = E.outBack(p);
        s.style.transform = `translateY(${(1 - e) * 115}%)`;
        s.style.opacity = String(Math.min(1, p * 4));
      });
    },
  };
}

/** Pastille de rubrique (kicker) : trait doré qui s'ouvre puis texte. */
export function kicker(parent, text) {
  const k = document.createElement('div'); k.className = 'kicker';
  k.innerHTML = '<i class="bar"></i><span class="kt"></span>';
  k.querySelector('.kt').textContent = text;
  parent.appendChild(k);
  const bar = k.querySelector('.bar'), kt = k.querySelector('.kt');
  return {
    el: k,
    update(lt, t0 = 0.1) {
      bar.style.width = `${lerp(0, 64, E.outExpo(prog(lt, t0, 0.5)))}px`;
      const p = E.outCubic(prog(lt, t0 + 0.2, 0.5));
      kt.style.opacity = String(p); kt.style.transform = `translateX(${(1 - p) * -24}px)`;
    },
  };
}
