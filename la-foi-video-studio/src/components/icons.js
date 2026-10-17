// Icônes vectorielles simples (trait), dessinées pour ce projet.
const P = {
  tag: '<path d="M4 12.5V5a1 1 0 0 1 1-1h7.5a1 1 0 0 1 .7.3l7 7a1 1 0 0 1 0 1.4l-7.5 7.5a1 1 0 0 1-1.4 0l-7-7a1 1 0 0 1-.3-.7z"/><circle cx="8.5" cy="8.5" r="1.6"/>',
  pulse: '<path d="M3 12h4l2.5-6 4 12 2.5-6H21"/>',
  star: '<path d="M12 3.2l2.6 5.5 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6L3.4 9.5l6-.8z"/>',
  gift: '<rect x="3.5" y="9" width="17" height="11" rx="1.5"/><path d="M12 9v11M3.5 13.5h17M12 9c-2.5 0-4.5-1-4.5-3a2 2 0 0 1 4-.3c.3-1.4 1.4-2.2 2.700-2.200A2.300 2.300 0 0 1 16.500 6c0 2-2 3-4.500 3z"/>',
  calendar: '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
  check: '<path d="M5 12.5l4.500 4.500L19 7.500"/>',
};
export const icon = (name, size = 56, color = 'currentColor') =>
  `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="${color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${P[name] ?? ''}</svg>`;
