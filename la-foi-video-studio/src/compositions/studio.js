// Prévisualisation interactive : lecture, défilement, changement de format, sous-titres.
export function initStudio(comp) {
  const $ = (id) => document.getElementById(id);
  const stage = $('stage'), bar = $('studio'); bar.hidden = false;
  document.body.classList.add('studio');
  const params = new URLSearchParams(location.search);
  $('fmt').value = params.get('format') ?? '9x16';
  $('fmt').onchange = () => { params.set('format', $('fmt').value); location.search = params.toString(); };
  $('subs').checked = params.get('subs') !== '0';
  $('subs').onchange = () => { params.set('subs', $('subs').checked ? '1' : '0'); location.search = params.toString(); };
  const fit = () => { const k = Math.min(innerWidth / comp.fmt.w, (innerHeight - 70) / comp.fmt.h); stage.style.transform = `scale(${k})`; stage.style.transformOrigin = 'top left'; $('viewport').style.width = `${comp.fmt.w * k}px`; $('viewport').style.height = `${comp.fmt.h * k}px`; };
  addEventListener('resize', fit); fit();
  const audio = new Audio('/output/mix.m4a'); audio.preload = 'auto';
  let t = Number(params.get('t') ?? 0), playing = false, last = 0;
  const fmtT = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  const draw = () => { comp.setTime(t); $('scrub').value = String((t / comp.duration) * 1000); $('clock').textContent = `${fmtT(t)} / ${fmtT(comp.duration)}${comp.tl.estimated ? '  (temps estimés)' : ''}`; };
  const tick = (now) => { if (playing) { t = Math.min(comp.duration, t + (now - last) / 1000); last = now; if (t >= comp.duration) toggle(); draw(); requestAnimationFrame(tick); } };
  function toggle() { playing = !playing; $('play').textContent = playing ? '❚❚' : '▶'; if (playing) { last = performance.now(); audio.currentTime = t; audio.play().catch(() => {}); requestAnimationFrame(tick); } else audio.pause(); }
  $('play').onclick = toggle; addEventListener('keydown', (e) => { if (e.code === 'Space') { e.preventDefault(); toggle(); } });
  $('scrub').oninput = () => { t = ($('scrub').value / 1000) * comp.duration; if (playing) audio.currentTime = t; draw(); };
  comp.tl.scenes.forEach((s, i) => { const b = document.createElement('button'); b.textContent = String(i + 1); b.title = s.id; b.onclick = () => { t = s.start + 1.5; draw(); }; $('scenes').appendChild(b); });
  draw(); window.__ready = true;
}
