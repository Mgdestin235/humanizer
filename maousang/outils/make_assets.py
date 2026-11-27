"""Génère les illustrations vectorielles (SVG) de Maousang : icônes, cartes, couverture.

Les cartes sont SCHÉMATIQUES (contours simplifiés tracés à la main), pas des cartes officielles.
Le rendu PNG est fait par render_svg.js (Chromium).
"""
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/illustrations"
os.makedirs(OUT, exist_ok=True)

DARK = "#14213D"
TEAL = "#2A51A3"
MINT = "#6F8FD6"
AMBER = "#F78E20"
LIGHT = "#EEF2FA"
WHITE = "#FFFFFF"

ICONS = {
    "bus": '<rect x="3" y="3" width="18" height="15" rx="3"/><line x1="3" y1="11" x2="21" y2="11"/><line x1="12" y1="3" x2="12" y2="11"/><circle cx="7.5" cy="14.5" r="1"/><circle cx="16.5" cy="14.5" r="1"/><line x1="6" y1="18" x2="6" y2="21"/><line x1="18" y1="18" x2="18" y2="21"/>',
    "moto": '<circle cx="5" cy="17" r="3.5"/><circle cx="19" cy="17" r="3.5"/><path d="M5 17l4.5-7h5l4.5 7"/><path d="M14.5 10l1.5-4h3"/><path d="M8 10h3.5"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "home": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "cart": '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>',
    "plane": '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
    "ticket": '<path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z"/><line x1="15" y1="7" x2="15" y2="17" stroke-dasharray="2 2"/>',
    "megaphone": '<path d="M3 10v4h3l8 5V5l-8 5z"/><path d="M18 9a4 4 0 0 1 0 6"/><path d="M6 14l1 5h3l-1-4"/>',
    "bot": '<rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="9" cy="14" r="1.2"/><circle cx="15" cy="14" r="1.2"/><line x1="12" y1="4" x2="12" y2="8"/><circle cx="12" cy="3" r="1"/><line x1="2" y1="13" x2="2" y2="16"/><line x1="22" y1="13" x2="22" y2="16"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "money": '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "search": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "trend": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "phone": '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    "truck": '<rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "award": '<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>',
    "check": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "x": '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "card": '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
    "tv": '<rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/>',
    "gift": '<polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "building": '<rect x="4" y="2" width="16" height="20" rx="1"/><line x1="9" y1="22" x2="9" y2="17"/><line x1="15" y1="22" x2="15" y2="17"/><line x1="8" y1="6" x2="8" y2="6.01"/><line x1="12" y1="6" x2="12" y2="6.01"/><line x1="16" y1="6" x2="16" y2="6.01"/><line x1="8" y1="10" x2="8" y2="10.01"/><line x1="12" y1="10" x2="12" y2="10.01"/><line x1="16" y1="10" x2="16" y2="10.01"/><line x1="8" y1="14" x2="8" y2="14.01"/><line x1="12" y1="14" x2="12" y2="14.01"/><line x1="16" y1="14" x2="16" y2="14.01"/>',
    "bank": '<polygon points="12 2 2 7 22 7 12 2"/><line x1="5" y1="10" x2="5" y2="18"/><line x1="10" y1="10" x2="10" y2="18"/><line x1="14" y1="10" x2="14" y2="18"/><line x1="19" y1="10" x2="19" y2="18"/><line x1="2" y1="21" x2="22" y2="21"/>',
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "box": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
}
ICON_COLORS = {"w": WHITE, "t": TEAL, "a": AMBER, "d": DARK}


def icon_svg(name, color, size=256):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="-1 -1 26 26" '
            f'fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICONS[name]}</svg>')


# ------------------------------------------------------------------ Cartes
# Contour du Tchad (lon, lat) – simplifié
CHAD = [(15.99, 23.45), (24.0, 19.5), (24.0, 15.7), (22.9, 15.5), (22.4, 14.0), (22.5, 13.0),
        (21.9, 12.6), (22.5, 12.0), (22.86, 10.92), (21.7, 10.5), (21.0, 9.8), (20.1, 9.1),
        (19.0, 9.0), (18.8, 8.4), (17.6, 7.9), (16.6, 7.6), (15.5, 7.5), (15.2, 8.3),
        (14.5, 9.0), (13.95, 9.6), (14.5, 10.0), (15.0, 10.4), (15.1, 11.0), (15.05, 12.1),
        (14.6, 12.8), (14.2, 13.1), (13.5, 13.8), (13.6, 14.4), (15.0, 15.8), (15.5, 16.9),
        (15.7, 19.9), (15.99, 20.8)]
CITIES = [("N'Djaména", 15.05, 12.11, True), ("Moundou", 16.08, 8.57, True), ("Sarh", 18.39, 9.15, True),
          ("Abéché", 20.83, 13.83, True), ("Bongor", 15.37, 10.28, False),
          ("Mongo", 18.69, 12.18, False), ("Am Timan", 20.28, 10.98, False), ("Ati", 18.33, 13.21, False),
          ("Faya-Largeau", 19.11, 17.93, False)]

AFRICA = [(-5.9, 35.8), (-1.0, 35.2), (3.0, 36.8), (10.0, 37.2), (11.0, 35.0), (10.2, 33.8), (11.5, 33.0),
          (15.2, 32.3), (19.0, 30.4), (20.0, 32.0), (25.0, 31.6), (29.0, 30.9), (32.3, 31.3), (34.2, 27.9),
          (35.5, 23.9), (37.2, 21.0), (38.5, 18.0), (39.5, 15.5), (42.5, 12.5), (43.3, 11.8), (44.9, 10.4),
          (51.2, 11.8), (51.0, 10.4), (48.0, 4.5), (45.3, 2.0), (41.5, -1.8), (39.7, -4.0), (39.2, -6.8),
          (40.5, -10.5), (40.6, -14.5), (37.0, -18.0), (35.5, -22.0), (35.4, -24.0), (32.9, -26.0),
          (32.4, -28.5), (30.9, -30.5), (27.9, -33.0), (25.6, -34.0), (20.0, -34.8), (18.4, -34.0),
          (17.8, -32.0), (16.5, -28.6), (15.2, -27.0), (14.5, -22.9), (11.8, -17.2), (12.3, -13.5),
          (13.3, -9.0), (12.2, -6.0), (11.8, -3.5), (9.4, -0.5), (9.6, 1.0), (9.8, 3.0), (8.5, 4.5),
          (6.0, 4.3), (4.0, 6.4), (1.2, 6.1), (-2.0, 4.7), (-4.0, 5.2), (-7.5, 4.4), (-9.5, 5.7),
          (-11.5, 6.9), (-13.3, 8.5), (-15.0, 10.9), (-16.8, 12.4), (-17.2, 14.7), (-16.5, 16.5),
          (-16.1, 19.0), (-17.1, 21.0), (-15.0, 24.5), (-13.2, 27.0), (-9.8, 29.8), (-9.6, 30.4),
          (-8.4, 33.4), (-6.8, 34.0)]
MADAGASCAR = [(49.3, -12.0), (50.5, -15.5), (49.0, -24.0), (47.0, -25.2), (43.5, -21.5), (44.3, -16.2),
              (47.0, -14.5)]


def proj(lon, lat, x0, x1, y0, y1, W, H, pad=20):
    sx = (W - 2 * pad) / (x1 - x0)
    sy = (H - 2 * pad) / (y1 - y0)
    s = min(sx, sy)
    ox = pad + ((W - 2 * pad) - s * (x1 - x0)) / 2
    oy = pad + ((H - 2 * pad) - s * (y1 - y0)) / 2
    return ox + (lon - x0) * s, oy + (y1 - lat) * s


def poly(points, **kw):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def chad_map():
    W, H = 900, 1100
    P = lambda lo, la: proj(lo, la, 13.3, 24.2, 7.2, 23.7, W, H, 60)
    pts = poly([P(*p) for p in CHAD])
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3E3C3"/>'
         f'<stop offset="1" stop-color="{LIGHT}"/></linearGradient></defs>',
         f'<polygon points="{pts}" fill="url(#g)" stroke="{TEAL}" stroke-width="5" stroke-linejoin="round"/>']
    # Lac Tchad
    lx, ly = P(14.0, 13.3)
    s.append(f'<ellipse cx="{lx:.0f}" cy="{ly:.0f}" rx="26" ry="20" fill="#9ED8DB" opacity="0.9"/>')
    nd = P(15.05, 12.11)
    for name, lo, la, main in CITIES:
        x, y = P(lo, la)
        if main and name != "N'Djaména":
            s.append(f'<line x1="{nd[0]:.0f}" y1="{nd[1]:.0f}" x2="{x:.0f}" y2="{y:.0f}" stroke="{AMBER}" '
                     'stroke-width="4" stroke-dasharray="10 8" opacity="0.9"/>')
    for name, lo, la, main in CITIES:
        x, y = P(lo, la)
        if name == "N'Djaména":
            s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="34" fill="{AMBER}" opacity="0.25"/>')
            s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="16" fill="{AMBER}" stroke="#fff" stroke-width="4"/>')
            s.append(f'<text x="{x+26:.0f}" y="{y+52:.0f}" font-family="Arial" font-weight="700" font-size="36" fill="{DARK}">N\'Djaména</text>')
        else:
            r = 11 if main else 7
            col = TEAL if main else "#64748B"
            s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{col}" stroke="#fff" stroke-width="3"/>')
            fs = 30 if main else 24
            fw = 700 if main else 400
            s.append(f'<text x="{x+16:.0f}" y="{y+9:.0f}" font-family="Arial" font-weight="{fw}" font-size="{fs}" fill="{DARK}">{name}</text>')
    s.append(f'<text x="{W-40}" y="{H-24}" text-anchor="end" font-family="Arial" font-size="20" fill="#64748B">Carte schématique – contours simplifiés</text>')
    s.append("</svg>")
    return "\n".join(s)


def africa_map():
    W, H = 1300, 1200
    P = lambda lo, la: proj(lo, la, -27, 56, -37, 38, W, H, 40)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<polygon points="{poly([P(*p) for p in AFRICA])}" fill="{LIGHT}" stroke="#9DB4E8" stroke-width="3" stroke-linejoin="round"/>',
         f'<polygon points="{poly([P(*p) for p in MADAGASCAR])}" fill="{LIGHT}" stroke="#9DB4E8" stroke-width="3"/>',
         f'<polygon points="{poly([P(*p) for p in CHAD])}" fill="{TEAL}" stroke="#fff" stroke-width="3"/>']
    nd = P(15.05, 12.11)
    targets = [("Cameroun", 11.5, 3.87, 1, "L", 0), ("Centrafrique", 18.56, 4.36, 1, "R", 18),
               ("Sénégal", -17.45, 14.7, 2, "L", 0), ("Côte d'Ivoire", -4.0, 5.36, 2, "L", 0),
               ("Guinée", -13.7, 9.5, 2, "L", 0), ("Gabon", 9.45, 0.4, 3, "L", 0),
               ("Congo", 15.28, -4.27, 3, "R", 0), ("Niger", 2.11, 13.51, 3, "L", -26)]
    colors = {1: AMBER, 2: MINT, 3: "#94A3B8"}
    for name, lo, la, w, side, dyl in targets:
        x, y = P(lo, la)
        dx, dy = x - nd[0], y - nd[1]
        cx, cy = nd[0] + dx / 2 - dy * 0.18, nd[1] + dy / 2 + dx * 0.18
        s.append(f'<path d="M{nd[0]:.0f},{nd[1]:.0f} Q{cx:.0f},{cy:.0f} {x:.0f},{y:.0f}" fill="none" stroke="{colors[w]}" '
                 f'stroke-width="{5 if w == 1 else 4}" stroke-dasharray="{"0" if w == 1 else "12 8"}"/>')
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{colors[w]}" stroke="#fff" stroke-width="4"/>')
        anchor = "end" if side == "L" else "start"
        tx = x - 20 if side == "L" else x + 20
        s.append(f'<text x="{tx:.0f}" y="{y+10+dyl:.0f}" text-anchor="{anchor}" font-family="Arial" font-weight="700" font-size="32" fill="{DARK}">{name}</text>')
    # destinations internationales (flèches vers le bord)
    intl = [("Europe", 4, 37.5), ("Turquie", 34, 37.5), ("Russie", 46, 37.5), ("Émirats", 48.5, 25), ("Chine", 48.5, 14)]
    for name, lo, la in intl:
        x, y = P(lo, la)
        s.append(f'<path d="M{nd[0]:.0f},{nd[1]:.0f} L{x:.0f},{y:.0f}" stroke="{DARK}" stroke-width="3" stroke-dasharray="4 8" opacity="0.55"/>')
        s.append(f'<rect x="{x-80:.0f}" y="{y-24:.0f}" width="160" height="48" rx="24" fill="{DARK}"/>')
        s.append(f'<text x="{x:.0f}" y="{y+10:.0f}" text-anchor="middle" font-family="Arial" font-weight="700" font-size="26" fill="#fff">✈ {name}</text>')
    s.append(f'<circle cx="{nd[0]:.0f}" cy="{nd[1]:.0f}" r="22" fill="{AMBER}" stroke="#fff" stroke-width="5"/>')
    s.append(f'<text x="{nd[0]+30:.0f}" y="{nd[1]-24:.0f}" font-family="Arial" font-weight="700" font-size="34" fill="{DARK}">Tchad</text>')
    s.append(f'<text x="{W-30}" y="{H-20}" text-anchor="end" font-family="Arial" font-size="22" fill="#64748B">Carte schématique – contours simplifiés</text>')
    s.append("</svg>")
    return "\n".join(s)


def cover_art():
    """Silhouette du Tchad traversée par un réseau de services."""
    W, H = 1100, 1200
    P = lambda lo, la: proj(lo, la, 13.3, 24.2, 7.2, 23.7, W, H, 80)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<polygon points="{poly([P(*p) for p in CHAD])}" fill="#1E2E52" stroke="{MINT}" stroke-width="4" stroke-linejoin="round" opacity="0.95"/>']
    nodes = [P(lo, la) for _, lo, la, _ in CITIES]
    nd = nodes[0]
    for (x, y) in nodes[1:]:
        s.append(f'<line x1="{nd[0]:.0f}" y1="{nd[1]:.0f}" x2="{x:.0f}" y2="{y:.0f}" stroke="{MINT}" stroke-width="2.5" opacity="0.7"/>')
    for i, (x, y) in enumerate(nodes[1:]):
        x2, y2 = nodes[1 + (i + 1) % (len(nodes) - 1)]
        s.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{MINT}" stroke-width="1.5" opacity="0.35"/>')
    for (x, y) in nodes[1:]:
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{MINT}"/>')
    s.append(f'<circle cx="{nd[0]:.0f}" cy="{nd[1]:.0f}" r="60" fill="{AMBER}" opacity="0.18"/>')
    s.append(f'<circle cx="{nd[0]:.0f}" cy="{nd[1]:.0f}" r="22" fill="{AMBER}" stroke="#fff" stroke-width="5"/>')
    # badges d'icônes
    badges = [("bus", 19.5, 19.5), ("moto", 22.6, 15.0), ("briefcase", 21.5, 10.6), ("home", 17.6, 8.6),
              ("cart", 16.5, 15.5), ("plane", 18.2, 21.8)]
    for name, lo, la in badges:
        x, y = P(lo, la)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="58" fill="{TEAL}" stroke="{MINT}" stroke-width="3"/>')
        s.append(f'<g transform="translate({x-32:.0f},{y-32:.0f}) scale(2.6)" fill="none" stroke="#fff" stroke-width="1.8" '
                 f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')
    s.append("</svg>")
    return "\n".join(s)


def pixel_chad():
    """Carte du Tchad en carrés de couleur, dans le style du modèle SANIA."""
    import random
    random.seed(7)
    W, H, step = 900, 1100, 34
    P = lambda lo, la: proj(lo, la, 13.3, 24.2, 7.2, 23.7, W, H, 30)
    poly_pts = [P(*p) for p in CHAD]

    def inside(x, y):
        n, c = len(poly_pts), False
        for i in range(n):
            x1, y1 = poly_pts[i]
            x2, y2 = poly_pts[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
        return c
    pal = ["#2A51A3", "#2A51A3", "#6F8FD6", "#9DB4E8", "#00A887", "#F78E20"]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    for y in range(0, H, step):
        for x in range(0, W, step):
            if inside(x + step / 2, y + step / 2):
                s.append(f'<rect x="{x+3}" y="{y+3}" width="{step-6}" height="{step-6}" fill="{random.choice(pal)}"/>')
    s.append("</svg>")
    return "\n".join(s)


def write(name, svg):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    for n in ICONS:
        for ck, col in ICON_COLORS.items():
            write(f"icon_{n}_{ck}", icon_svg(n, col))
    write("map_chad", chad_map())
    write("map_africa", africa_map())
    write("cover_art", cover_art())
    write("pixel_chad", pixel_chad())
    print("svg ok", len(os.listdir(OUT)))
