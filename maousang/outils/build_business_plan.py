"""Génère le business plan en HTML (outils/business_plan.html). render_pdf.js l'imprime en PDF."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "outils", "model_values.json")))
P, I, A = M["Prudent"], M["Intermediaire"], M["Ambitieux"]
MK, EQ = M["Marche"], M["Equipe"]
ILL = "../assets/illustrations"

DARK, TEAL, MINT, AMBER, GRAY = "#0B1B2B", "#0F766E", "#14B8A6", "#F59E0B", "#94A3B8"


def fr(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


def mf(x, d=1):
    return f"{fr(x / 1e6, d)} M"


def bars(series, cats, colors, title, unit="", w=520, h=260, labels=True):
    """Histogramme groupé en SVG."""
    vmax = max(max(v) for _, v in series) * 1.15
    pad_l, pad_b, pad_t = 50, 40, 36
    cw = (w - pad_l - 10) / len(cats)
    bw = cw * 0.7 / len(series)
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, Arial" font-size="11">',
           f'<text x="0" y="16" font-weight="700" font-size="13" fill="{DARK}">{title}</text>']
    for k in range(5):
        y = pad_t + (h - pad_t - pad_b) * k / 4
        val = vmax * (1 - k / 4)
        out.append(f'<line x1="{pad_l}" y1="{y:.0f}" x2="{w-10}" y2="{y:.0f}" stroke="#E2E8F0"/>')
        out.append(f'<text x="{pad_l-6}" y="{y+4:.0f}" text-anchor="end" fill="#64748B">{fr(val)}</text>')
    for j, c in enumerate(cats):
        x0 = pad_l + j * cw + cw * 0.15
        for i, (name, vals) in enumerate(series):
            v = vals[j]
            bh = (h - pad_t - pad_b) * v / vmax
            x = x0 + i * bw
            y = h - pad_b - bh
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-3:.1f}" height="{bh:.1f}" rx="2" fill="{colors[i]}"/>')
            if labels:
                out.append(f'<text x="{x+bw/2-1.5:.1f}" y="{y-4:.1f}" text-anchor="middle" font-size="9.5" fill="{DARK}">{fr(v, 1 if v < 100 else 0)}</text>')
        out.append(f'<text x="{pad_l + j*cw + cw/2:.0f}" y="{h-pad_b+16}" text-anchor="middle" fill="#334155" font-weight="600">{c}</text>')
    lx = pad_l
    for i, (name, _) in enumerate(series):
        out.append(f'<rect x="{lx}" y="{h-14}" width="10" height="10" fill="{colors[i]}"/>'
                   f'<text x="{lx+14}" y="{h-5}" fill="#334155">{name}</text>')
        lx += 22 + 7 * len(name)
    out.append("</svg>")
    return "".join(out)


def donut(items, colors, title, size=240):
    import math
    tot = sum(v for _, v in items)
    cx = cy = size / 2
    r1, r2 = size * 0.42, size * 0.25
    out = [f'<svg viewBox="0 0 {size+230} {size+20}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, Arial" font-size="11">',
           f'<text x="0" y="14" font-weight="700" font-size="13" fill="{DARK}">{title}</text>']
    a0 = -math.pi / 2
    for (lab, v), col in zip(items, colors):
        a1 = a0 + 2 * math.pi * v / tot
        large = 1 if a1 - a0 > math.pi else 0
        p = [(cx + r1 * math.cos(a0), 20 + cy + r1 * math.sin(a0)), (cx + r1 * math.cos(a1), 20 + cy + r1 * math.sin(a1)),
             (cx + r2 * math.cos(a1), 20 + cy + r2 * math.sin(a1)), (cx + r2 * math.cos(a0), 20 + cy + r2 * math.sin(a0))]
        out.append(f'<path d="M{p[0][0]:.1f},{p[0][1]:.1f} A{r1},{r1} 0 {large} 1 {p[1][0]:.1f},{p[1][1]:.1f} '
                   f'L{p[2][0]:.1f},{p[2][1]:.1f} A{r2},{r2} 0 {large} 0 {p[3][0]:.1f},{p[3][1]:.1f} Z" fill="{col}" stroke="#fff" stroke-width="2"/>')
        a0 = a1
    for i, ((lab, v), col) in enumerate(zip(items, colors)):
        y = 40 + i * 22
        out.append(f'<rect x="{size+10}" y="{y-10}" width="12" height="12" rx="2" fill="{col}"/>'
                   f'<text x="{size+28}" y="{y}" fill="#334155">{lab} : <tspan font-weight="700">{fr(100*v/tot)} %</tspan></text>')
    out.append("</svg>")
    return "".join(out)


def tbl(rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in rows[0])
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows[1:])
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def pl_table(sc, name):
    keys = [("users_end", "Utilisateurs inscrits (fin)", "n"), ("mau", "Actifs mensuels moyens", "n"),
            ("pros", "Prestataires professionnels", "n"), ("tx_total", "Transactions", "n"),
            ("conv", "Taux de conversion payant", "p"), ("arppu", "Revenu moyen par client payant (FCFA)", "n"),
            ("rev_mob", "CA mobilité", "m"), ("rev_bil", "CA billetterie", "m"), ("rev_emp", "CA emploi", "m"),
            ("rev_imm", "CA immobilier", "m"), ("rev_subs", "CA abonnements pros", "m"), ("rev_ads", "CA publicité", "m"),
            ("rev_total", "<b>Chiffre d'affaires total</b>", "m"), ("cost_ops", "Dépenses opérationnelles", "m"),
            ("cost_mkt", "Dépenses marketing", "m"), ("cost_staff", "Masse salariale", "m"),
            ("tech", "Coûts techniques et infrastructure", "m"), ("cost_total", "<b>Total des dépenses</b>", "m"),
            ("ebit", "<b>Résultat opérationnel</b>", "m"), ("cash", "Trésorerie fin d'année (avec 15 M levés)", "m")]
    rows = [[f"Scénario {name}", "A1", "A2", "A3"]]
    for k, lab, t in keys:
        f = {"n": lambda v: fr(v), "p": lambda v: f"{fr(v*100,1)} %", "m": lambda v: mf(v)}[t]
        rows.append([lab] + [f(v) for v in sc[k]])
    return tbl(rows, "num")


tam = MK["TAM – internautes au Tchad"]
sam = MK["SAM – internautes urbains (N'Djaména et grandes villes)"]
rpm = MK["Revenu annuel par MAU (intermédiaire A3)"]
somp, somi, soma = (MK["SOM prudent (5 % du SAM, utilisateurs actifs)"], MK["SOM intermédiaire (10 % du SAM)"],
                    MK["SOM ambitieux (20 % du SAM)"])

rev_chart = bars([("Prudent", [v / 1e6 for v in P["rev_total"]]), ("Intermédiaire", [v / 1e6 for v in I["rev_total"]]),
                  ("Ambitieux", [v / 1e6 for v in A["rev_total"]])], ["Année 1", "Année 2", "Année 3"],
                 [GRAY, TEAL, AMBER], "Chiffre d'affaires par scénario (M FCFA)")
users_chart = bars([("Inscrits fin d'année", [v / 1e3 for v in I["users_end"]]), ("Actifs mensuels", [v / 1e3 for v in I["mau"]])],
                   ["Année 1", "Année 2", "Année 3"], [TEAL, AMBER], "Utilisateurs, scénario intermédiaire (milliers)")
mix = [("Mobilité", I["rev_mob"][2]), ("Abonnements", I["rev_subs"][2]), ("Emploi", I["rev_emp"][2]),
       ("Immobilier", I["rev_imm"][2]), ("Billetterie", I["rev_bil"][2]), ("Publicité", I["rev_ads"][2])]
mix_chart = donut(mix, [TEAL, MINT, AMBER, "#0EA5E9", GRAY, DARK], "Répartition du CA, A3 (intermédiaire)")
FUND = [("Recrutement et rémunération", 4500000), ("Marketing et communication", 3000000), ("Agents de terrain", 3000000),
        ("Infrastructure technique", 1200000), ("Prospection commerciale", 1000000), ("Administratif et juridique", 1000000),
        ("Partenariats", 800000), ("Fonds de roulement", 500000)]
fund_chart = donut(FUND, [TEAL, AMBER, MINT, DARK, "#0EA5E9", GRAY, "#B45309", "#475569"], "Répartition des 15 000 000 FCFA", size=230)

team_rows = [["Poste", "Effectif A1", "Effectif A2", "Effectif A3", "Salaire mensuel A1", "Salaire mensuel A3", "Coût annuel A1", "Coût annuel A3"]]
for r in EQ[:-1]:
    team_rows.append([r[0], r[1], r[2], r[3], fr(r[4]), fr(r[6]), fr(r[7]), fr(r[9])])
t = EQ[-1]
team_rows.append(["<b>Total</b>", t[1], t[2], t[3], "", "", f"<b>{fr(t[7])}</b>", f"<b>{fr(t[9])}</b>"])

CAPS = [("01_accueil", "Accueil"), ("02_inscription", "Inscription"), ("03_connexion", "Connexion"),
        ("04_tableau_de_bord", "Menu des services"), ("05_billetterie_recherche", "Billetterie : recherche"),
        ("06_billetterie_resultats", "Billetterie : offres"), ("07_clando_demande", "Clando : demande"),
        ("08_livraison", "Livraison"), ("09_emploi_offres", "Emploi : offres"), ("10_emploi_ats", "Emploi : ATS"),
        ("11_immobilier_recherche", "Immobilier : recherche"), ("12_immobilier_annonce", "Immobilier : annonce"),
        ("13_annonces", "Annonces"), ("14_assistant_ia", "Assistant IA")]
cap_html = ""
for k, lab in CAPS:
    pth = os.path.join(ROOT, "assets", "captures", k + ".png")
    inner = f'<img src="../assets/captures/{k}.png">' if os.path.exists(pth) else f'<div class="ph"><div>Capture à insérer<br><b>{lab}</b></div></div>'
    cap_html += f'<figure class="cap">{inner}<figcaption>{lab}</figcaption></figure>'

css = f"""
@page {{ size: A4; margin: 18mm 16mm 18mm 16mm; }}
body {{ font-family: Inter, Arial, sans-serif; color: {DARK}; font-size: 10.5pt; line-height: 1.5; }}
h1 {{ font-size: 22pt; margin: 0 0 6px; }} h2 {{ font-size: 16pt; color: {TEAL}; margin: 22px 0 8px; break-after: avoid; }}
h3 {{ font-size: 12pt; margin: 14px 0 6px; break-after: avoid; }}
p {{ margin: 0 0 8px; }} ul {{ margin: 0 0 8px; padding-left: 18px; }} li {{ margin-bottom: 3px; }}
table {{ width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 9pt; break-inside: avoid; }}
th {{ background: {TEAL}; color: #fff; text-align: left; padding: 5px 6px; }}
td {{ padding: 4px 6px; border-bottom: 1px solid #E2E8F0; vertical-align: top; }}
table.num td:not(:first-child), table.num th:not(:first-child) {{ text-align: right; white-space: nowrap; }}
.cover {{ height: 255mm; background: {DARK}; color: #fff; padding: 22mm 18mm; box-sizing: border-box; position: relative;
  margin: -18mm -16mm 0; break-after: page; }}
.cover h1 {{ font-size: 46pt; color: #fff; margin-top: 30mm; }} .cover .k {{ color: {AMBER}; font-weight: 700; letter-spacing: 1px; }}
.cover img {{ position: absolute; right: 10mm; bottom: 18mm; width: 95mm; }}
.cover .sub {{ font-size: 15pt; color: #CDE7E3; max-width: 105mm; }}
.box {{ background: #E6F4F1; border-radius: 8px; padding: 10px 14px; margin: 10px 0; break-inside: avoid; }}
.warn {{ background: #FFF7E6; border-left: 0; border-radius: 8px; padding: 10px 14px; margin: 10px 0; break-inside: avoid; }}
.kpis {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 10px 0; }}
.kpi {{ background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px; }}
.kpi b {{ display: block; font-size: 17pt; color: {TEAL}; }} .kpi span {{ font-size: 8.5pt; color: #475569; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: start; }}
.fig {{ break-inside: avoid; margin: 8px 0; }}
.src {{ font-size: 8pt; color: #64748B; }}
.caps {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }}
.cap {{ margin: 0; text-align: center; font-size: 7.5pt; }} .cap img {{ width: 100%; border-radius: 6px; border: 1px solid #CBD5E1; }}
.ph {{ height: 46mm; border: 1px dashed #94A3B8; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #64748B; font-size: 7pt; padding: 3px; }}
.pb {{ break-before: page; }}
"""

html = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>MAOUSANG – Business plan</title><style>{css}</style></head><body>
<section class="cover">
<div class="k">BUSINESS PLAN · 2026</div>
<h1>MAOUSANG</h1>
<p class="sub">La plateforme numérique multiservices du Tchad : billetterie, mobilité, emploi et immobilier dans un seul environnement digital.</p>
<p style="margin-top:20mm;font-size:11pt"><b>Giscard Destin</b><br><span style="color:#94A3B8">Fondateur, ingénieur en intelligence artificielle et data scientist</span></p>
<p style="color:{MINT};font-weight:700">maousang.vercel.app</p>
<p style="font-size:9pt;color:#94A3B8;max-width:100mm;margin-top:14mm">Document confidentiel. Les données financières sont prévisionnelles. Les tarifs sont des hypothèses non validées par le marché.</p>
<img src="{ILL}/cover_art.png">
</section>

<h2>1. Résumé</h2>
<p><b>Maousang</b> réunit dans une seule plateforme les services dont les Tchadiens ont besoin chaque jour : acheter un billet de bus, commander un clando ou une livraison, trouver un emploi et trouver un logement. La plateforme est déjà développée et en production. Le fondateur, ingénieur en IA, a financé la conception et le développement.</p>
<div class="kpis">
<div class="kpi"><b>2,79 M</b><span>internautes au Tchad (oct. 2025), notre marché total</span></div>
<div class="kpi"><b>{fr(sam/1e6,2)} M</b><span>internautes urbains estimés, notre marché accessible</span></div>
<div class="kpi"><b>15 M FCFA</b><span>besoin de financement pour 12 mois de lancement</span></div>
<div class="kpi"><b>{mf(I['rev_total'][2])} FCFA</b><span>CA prévisionnel A3, scénario intermédiaire</span></div>
<div class="kpi"><b>8 → 48</b><span>emplois directs prévus de A1 à A3</span></div>
<div class="kpi"><b>8</b><span>sources de revenus</span></div>
</div>
<p>Nous demandons <b>15 000 000 FCFA</b> et un accompagnement stratégique. Ils financent l'équipe de lancement, le marketing, les agents de terrain et la structuration juridique, pour atteindre 10 000 inscrits en année 1. Dans le scénario intermédiaire, Maousang devient rentable en année 3. La trésorerie peut être légèrement négative en année 2 ({mf(I['cash'][1])} FCFA). Nous prévoyons donc un relais : revenus, prêt d'honneur ou tour d'amorçage.</p>

<h2>2. Présentation de Maousang</h2>
<p><b>Mission :</b> connecter les populations, les entreprises, les prestataires et les organisations grâce à des solutions numériques simples, accessibles et intelligentes.</p>
<p><b>Vision :</b> « Devenir une plateforme de référence pour l'accès aux services numériques au Tchad, avec une expansion en Afrique centrale, en rapprochant les populations des opportunités, des services et des acteurs économiques. »</p>
<div class="warn"><b>Note de méthode.</b> Le site maousang.vercel.app n'était pas accessible depuis l'environnement de rédaction. Les fonctionnalités décrites ici viennent du fondateur. Les captures d'écran de l'annexe sont à insérer avec les scripts fournis.</div>

<h2>3. Le problème</h2>
<ul>
<li>Trouver un transport fiable : le clando se hèle dans la rue et le prix se négocie.</li>
<li>Rechercher et réserver un logement : démarcheurs informels, visites inutiles. Le pays affiche un déficit estimé à 1,5 million de logements.</li>
<li>Trouver un emploi : offres dispersées entre sites, réseaux sociaux et affichages.</li>
<li>Acheter un billet : vente au guichet, prix peu lisibles (12 500 à 25 000 FCFA selon la destination).</li>
<li>Trouver des prestataires, accéder à une information centralisée, toucher ses clients quand on est une petite entreprise.</li>
<li>Dépendre des déplacements, des démarches physiques et des intermédiaires informels.</li>
</ul>
<p><b>Conséquences :</b> perte de temps, perte d'argent, prestataires invisibles, ventes manquées, accès difficile à l'information, services peu digitalisés. Pour illustrer le coût de la non-connectivité : les coupures d'Internet de 2024 auraient coûté environ 38 millions USD à l'économie tchadienne (estimation Top10VPN).</p>

<h2>4. La solution : l'écosystème Maousang</h2>
{tbl([["Pôle", "Statut", "Fonctionnalités", "Utilisateurs", "Valeur ajoutée"],
      ["1. Billetterie", "Développé", "Recherche de voyages, consultation des offres, services de billetterie", "Voyageurs, étudiants, compagnies de bus", "Moins d'attente ; meilleur remplissage des bus"],
      ["2. Mobilité – Clando", "Développé", "Moto-taxis, livraison de repas, de courses et de colis, autres prestataires de mobilité", "Citadins, restaurants, commerces, conducteurs, livreurs", "Revenus pour les conducteurs ; traçabilité"],
      ["3. Emploi et ATS", "Développé", "Offres ; ATS : réception des candidatures, analyse automatisée des CV, classement, présélection, mise en relation", "Candidats, PME, ONG, cabinets RH", "Tri plus rapide ; candidats visibles"],
      ["4. Immobilier", "Développé", "Recherche, location, réservation journalière, annonces, mise en relation", "Locataires, voyageurs, propriétaires, agences", "Moins de visites inutiles ; biens visibles"],
      ["Annonces, assistant IA", "Développé", "Publication et promotion ; orientation de l'utilisateur", "Tous", "Rétention et monétisation"],
      ["5. Commerce", "Phase 2", "Boutiques, catalogue, commandes, paiement, livraison", "Commerçants, acheteurs", "Vente en ligne pour les PME"],
      ["6. Billetterie internationale", "Phase 2", "Recherche et réservation de vols (Afrique, Turquie, Chine, Russie, Émirats, Europe)", "Voyageurs, diaspora, entreprises", "Partenariats à signer"]])}

<h2 class="pb">5. Étude de marché</h2>
<div class="two"><div>
{tbl([["Indicateur", "Valeur", "Source"],
      ["Population", "21,1 M (oct. 2025)", "ONU via DataReportal"],
      ["Population urbaine", "25,1 %, ≈ 5,3 M", "DataReportal 2026"],
      ["N'Djaména", "≈ 1,66 M (2024)", "ONU WUP via Macrotrends"],
      ["Connexions mobiles", "15,5 M (fin 2025)", "GSMA Intelligence"],
      ["Internautes", "2,79 M (oct. 2025)", "Kepios via DataReportal"],
      ["Réseaux sociaux", "2,38 M identités", "Kepios via DataReportal"],
      ["Monnaie électronique", "6,25 M comptes (2024)", "BEAC, relayé, à confirmer"],
      ["Déficit de logements", "≈ 1,5 M", "Gouvernement, nov. 2026"]])}
</div><div class="fig"><img src="{ILL}/map_chad.png" style="width:100%"></div></div>
<p><b>Emploi.</b> Le taux de chômage officiel des jeunes (≈ 1,5 %, Banque mondiale) mesure mal la réalité, car l'emploi informel domine. Nous ne l'utilisons pas comme argument. Le besoin se lit plutôt dans la dispersion des offres et la demande des recruteurs pour un tri plus rapide.</p>
<p><b>Transport et mobilité.</b> Le clando est le transport urbain dominant. La ville a lancé en septembre 2026 un programme d'identification des moto-taxis : la traçabilité devient une attente.</p>
<p><b>Billetterie.</b> Les liaisons N'Djaména–Moundou, –Sarh et –Abéché coûtent de 12 500 à 25 000 FCFA. Les billets se vendent au guichet, sans grille officielle publiée.</p>

<h3>TAM, SAM, SOM</h3>
<p>Nous mesurons le marché en <b>utilisateurs actifs</b>, pas en population. La valeur est estimée avec le revenu annuel par utilisateur actif du modèle intermédiaire en A3 ({fr(rpm)} FCFA).</p>
{tbl([["Niveau", "Méthode", "Utilisateurs", "Valeur annuelle"],
      ["TAM", "Internautes au Tchad", fr(tam), f"{fr(tam*rpm/1e9,1)} Md FCFA"],
      ["SAM", "5,3 M de citadins × 30 % d'usage d'Internet (hypothèse)", fr(sam), f"{fr(sam*rpm/1e9,1)} Md FCFA"],
      ["SOM prudent", "5 % du SAM à 3 ans", fr(somp), f"{fr(somp*rpm/1e6)} M FCFA"],
      ["SOM intermédiaire", "10 % du SAM à 3 ans", fr(somi), f"{fr(somi*rpm/1e6)} M FCFA"],
      ["SOM ambitieux", "20 % du SAM à 3 ans", fr(soma), f"{fr(soma*rpm/1e6)} M FCFA"]], "num")}
<div class="warn">L'objectif d'un million d'inscrits en A3 implique environ {fr(MK['MAU fin A3 implicite – objectif 1 M inscrits'])} utilisateurs actifs, soit {fr(MK['Part du SAM correspondante']*100)} % du SAM actuel. C'est ambitieux. Il faut la croissance d'Internet, l'extension aux grandes villes et les premiers marchés étrangers.</div>

<h2>6. Concurrence et positionnement</h2>
{tbl([["Acteur", "Secteur", "Offre observée", "Limite identifiable", "Différenciation Maousang"],
      ["Chadito", "Annonces", "Annonces : voitures, location, emploi, électronique ; KYC vendeurs", "Pas de mobilité, de billetterie ni d'ATS", "Transactions et ATS intégrés"],
      ["Blyt", "Mobilité (taxi)", "Prix affiché avant la course, chauffeurs identifiés", "Mobilité seule", "Moto-taxi, livraison et autres pôles"],
      ["SafeClando", "Moto-taxi", "Réservation de clando à N'Djaména", "Mobilité seule", "Écosystème multiservices"],
      ["Allons-y Taxi Privé", "Mobilité", "Réservation de taxi, trilingue", "Mobilité seule", "Écosystème multiservices"],
      ["emploi.td", "Emploi", "Offres et recrutement", "Pas d'ATS mentionné publiquement", "ATS intelligent"],
      ["Alwihda Info", "Annonces", "Annonces immobilières gratuites (web, SMS)", "Annonces non structurées", "Recherche filtrée, réservation"],
      ["Agences de bus", "Billetterie", "Vente au guichet", "Peu de vente en ligne publiée", "Recherche et comparaison en ligne"]])}
<p class="src">Aucun chiffre d'affaires, nombre d'utilisateurs ou part de marché n'est cité. Wadini et Annoncena : aucune présence publique trouvée sous ces noms (à vérifier).</p>
<p><b>Avantage stratégique.</b> Contrairement aux plateformes spécialisées dans un seul domaine, Maousang réunit plusieurs services dans un même écosystème. Un utilisateur acquis pour un service en découvre d'autres : cela réduit le coût d'acquisition et augmente la valeur de chaque client.</p>

<h2 class="pb">7. Modèle économique</h2>
{tbl([["Source de revenus", "Fonctionnement", "Tarif (hypothèse)", "Potentiel"],
      ["1. Commissions sur transactions", "% des courses, livraisons et réservations", "8 à 12 % (mobilité), 10 % (réservations)", "Élevé"],
      ["2. Abonnements professionnels", "Visibilité, badge vérifié, statistiques", "5 000 FCFA/mois", "Élevé"],
      ["3. Immobilier sponsorisé", "Mise en avant d'une annonce", "5 000 FCFA/mois", "Moyen"],
      ["4. Offres d'emploi payantes", "Publication par l'entreprise", "10 000 FCFA/offre", "Moyen"],
      ["5. Services premium recruteurs", "ATS : analyse et classement des CV", "25 000 FCFA/mois", "Moyen"],
      ["6. Publicité", "Bannières, annonces commerciales", "50 000 FCFA/mois", "Moyen"],
      ["7. Partenariats transporteurs", "Commission sur billets", "4 à 6 % du billet", "Moyen"],
      ["8. Frais de réservation", "Mise en relation, si applicable", "À définir par pôle", "Appoint"]])}
<p class="src">Ces tarifs sont des hypothèses de travail. Ils n'ont pas été validés par le marché et seront testés pendant les six premiers mois.</p>

<h2>8. Stratégie de communication et d'acquisition</h2>
<ul>
<li><b>A. Agence de communication</b> (sous-traitance) : identité visuelle, campagnes, contenus, community management, publicité digitale, relations publiques.</li>
<li><b>B. Web médias et influence</b> : médias numériques tchadiens, pages Facebook influentes, créateurs de contenus, médias économiques et technologiques.</li>
<li><b>C. Parrainage</b> : le parrain reçoit un crédit (hypothèse : 500 FCFA par filleul actif) ; les utilisateurs actifs deviennent ambassadeurs.</li>
<li><b>D. « Le coût de la non-connectivité »</b> : campagne éducative sur les pertes de temps, les déplacements inutiles et les opportunités manquées. Message : la transformation numérique est un levier de développement, pas un luxe.</li>
<li><b>E. Terrain</b> : agents, démonstrations publiques, universités, visites d'entreprises, partenariats avec les transporteurs, campagnes de quartier.</li>
</ul>
{tbl([["Mois", "Actions principales"],
      ["M1–M2", "Identité et kit de communication ; recrutement des agents ; démonstrations à l'université"],
      ["M3", "Lancement public ; ouverture du parrainage ; première campagne de l'agence"],
      ["M4–M5", "Campagne « Le coût de la non-connectivité » ; partenariats transporteurs"],
      ["M6", "Campagne sur l'emploi et l'ATS ; visites d'entreprises"],
      ["M7–M8", "Campagnes de quartier ; recrutement de restaurants et de commerces pour la livraison"],
      ["M9–M10", "Rentrée universitaire ; seconde vague de sensibilisation"],
      ["M11–M12", "Campagne de fin d'année (voyages des fêtes) ; bilan et plan A2"]])}
{tbl([["Poste du budget A1", "Montant (FCFA)"], ["Agence de communication", "1 200 000"], ["Web médias et influenceurs", "800 000"],
      ["Publicité digitale", "600 000"], ["Universités et démonstrations", "400 000"], ["Prospection terrain", "1 000 000"],
      ["Partenariats", "800 000"], ["<b>Total (dans les 15 M)</b>", "<b>4 800 000</b>"],
      ["Parrainage (payé sur les revenus)", f"{fr(I['cost_ref'][0])}"]], "num")}

<h2 class="pb">9. Projections financières sur trois ans</h2>
<p>Les objectifs de croissance sont <b>10 000</b>, <b>100 000</b> puis <b>1 000 000</b> d'inscrits. Ce sont des objectifs, pas des données acquises. Le modèle Excel (MAOUSANG_FINANCIAL_MODEL.xlsx) contient toutes les formules ; chaque hypothèse est en bleu et modifiable.</p>
<div class="two"><div class="fig">{rev_chart}</div><div class="fig">{users_chart}</div></div>
<div class="fig" style="width:75%">{mix_chart}</div>
<h3>Formules</h3>
<ul>
<li>Inscrits moyens = (inscrits début + inscrits fin) / 2 ; actifs mensuels = inscrits moyens × taux d'activité.</li>
<li>CA mobilité = actifs × part mobilité × courses/mois × 12 × prix moyen × commission. Exemple A1 intermédiaire : {fr(I['mau'][0])} × 40 % × 4 × 12 × 1 000 × 10 % = {fr(I['rev_mob'][0])} FCFA.</li>
<li>CA billetterie = actifs × part billetterie × 2 billets × 15 000 FCFA × commission.</li>
<li>CA emploi = entreprises × offres × 10 000 + abonnés ATS × 25 000 × 12.</li>
<li>CA immobilier = annonces sponsorisées × 5 000 × 12 + nuitées × 20 000 × 10 %.</li>
<li>Résultat opérationnel = CA − (masse salariale + marketing + technique + opérations + frais de paiement à 3 % du CA).</li>
</ul>
{pl_table(I, "intermédiaire")}
<div class="two"><div>{pl_table(P, "prudent")}</div><div>{pl_table(A, "ambitieux")}</div></div>
<div class="warn"><b>Lecture.</b> Le scénario prudent reste déficitaire sur trois ans : il faudrait réduire les dépenses ou lever davantage. Le scénario intermédiaire devient rentable en A3, avec un creux de trésorerie en A2. Le scénario ambitieux est rentable dès l'A1. Les écarts viennent surtout du taux d'activité, de la fréquence d'usage de la mobilité et des commissions.</div>

<h2 class="pb">10. Plan d'expansion</h2>
<div class="two"><div>
<h3>Phase 1 : consolidation au Tchad (A1–A2)</h3>
<p>Déploiement à N'Djaména ; premiers utilisateurs ; réseau de prestataires ; extension à Moundou, Abéché et Sarh ; amélioration de l'expérience utilisateur.</p>
<h3>Phase 2 : deux nouveaux pôles (A2–A3)</h3>
<p><b>Commerce :</b> boutiques numériques, catalogue, commandes, paiements, mise en relation vendeurs-acheteurs, livraison.<br>
<b>Billetterie internationale :</b> vols vers l'Afrique, la Turquie, la Chine, la Russie, les Émirats et l'Europe. Partenariats nécessaires : compagnies aériennes, agences de voyages, fournisseurs de réservation (systèmes de distribution, consolidateurs). <b>Aucun n'est signé à ce jour.</b></p>
<h3>Phase 3 : expansion africaine (A3 et après)</h3>
<p>Ordre proposé : Cameroun et Centrafrique (même monnaie et même banque centrale, corridor Douala–N'Djaména), puis Sénégal, Côte d'Ivoire et Guinée.</p>
</div><div class="fig"><img src="{ILL}/map_africa.png" style="width:100%"></div></div>
{tbl([["Pays", "Population", "Internautes", "Pénétration", "Atout", "Accessibilité"],
      ["Cameroun", "29,5 M", "12,4 M", "41,9 %", "Grand marché, corridor commercial", "CEMAC, XAF, francophone"],
      ["Centrafrique", "5,42 M", "0,84 M", "15,5 %", "Voisin, peu de concurrence", "CEMAC, XAF ; marché petit"],
      ["Sénégal", "18,7 M", "11,3 M", "60,6 %", "Forte adoption numérique", "UEMOA, XOF ; concurrence forte"],
      ["Côte d'Ivoire", "32,3 M", "12,8 M", "39,6 %", "Grand marché, paiement mobile mûr", "UEMOA, XOF"],
      ["Guinée", "14,9 M", "3,96 M", "26,5 %", "Croissance du mobile", "Franc guinéen"]])}
<p class="src">Source : DataReportal Digital 2025 (janvier 2025).</p>

<h2>11. Besoin de financement : 15 000 000 FCFA</h2>
<div class="two"><div>
{tbl([["Poste", "Montant (FCFA)", "Contenu"]] + [[n, f'<span style="white-space:nowrap">{fr(v)}</span>', c] for (n, v), c in zip(FUND, [
    "Resp. commercial, resp. marketing (150 000/mois) et support (75 000/mois), 12 mois",
    "Agence, campagnes, influenceurs, événements", "4 agents à temps partiel (62 500/mois) + primes",
    "Hébergement, base de données, SMS, cartes, stores", "Supports, déplacements, démonstrations",
    "Immatriculation, CGU, protection des données, comptabilité", "Paiement mobile, transporteurs, universités",
    "Réserve de sécurité"])] + [["<b>Total</b>", '<b style="white-space:nowrap">15 000 000</b>', ""]], "")}
</div><div class="fig">{fund_chart}</div></div>
{tbl([["Catégorie", "Contenu", "Financement"],
      ["Dépenses déjà réalisées", "Conception, développement et mise en production de la plateforme", "Fondateur (non couvert par la levée)"],
      ["Apport du fondateur", "Temps et compétences ; travail non rémunéré en A1 (direction générale et technique)", "Apport en industrie, valorisation à préciser"],
      ["Besoin financier restant", "Lancement commercial sur 12 mois", "15 000 000 FCFA demandés"],
      ["Dépenses futures", "A2–A3 : équipe élargie, marketing, infrastructure", "Chiffre d'affaires et, si besoin, tour d'amorçage"]])}
<p class="src">Ventilation indicative, à affiner selon les devis réels.</p>

<h2 class="pb">12. Impact économique et social, équipe et partenaires</h2>
{tbl(team_rows, "num")}
<p class="src">Salaires mensuels bruts estimatifs en FCFA, à valider avec un cabinet RH et le Code du travail. Recrutement progressif selon la croissance et les moyens disponibles.</p>
<ul>
<li><b>Emplois directs :</b> {EQ[-1][1]} en A1, {EQ[-1][2]} en A2, {EQ[-1][3]} en A3 (scénario intermédiaire), surtout des jeunes (agents, support, développeurs).</li>
<li><b>Emplois indirects et opportunités :</b> {fr(I['pros'][2])} prestataires inscrits en A3 (conducteurs, livreurs, agences, commerçants). Ce sont des sources de revenus, pas des emplois salariés.</li>
<li><b>Effets économiques :</b> accès aux offres d'emploi, visibilité des petites entreprises, digitalisation des services, baisse des coûts de recherche et de mise en relation.</li>
</ul>
{tbl([["Partenaire", "Ce que Maousang attend", "Ce que le partenaire gagne"],
      ["Ministères et institutions", "Reconnaissance, accès aux programmes numériques et d'emploi", "Un canal de digitalisation des services"],
      ["Banques et établissements financiers", "Financement, comptes professionnels", "Nouveaux clients (prestataires, PME)"],
      ["Opérateurs de paiement mobile", "Intégration du paiement", "Volume de transactions"],
      ["Compagnies de transport", "Accès aux horaires et à la vente", "Remplissage, vente en ligne"],
      ["Agences de voyages", "Offres nationales et internationales", "Nouveaux clients"],
      ["Agences immobilières", "Annonces vérifiées", "Visibilité, clients qualifiés"],
      ["Entreprises de livraison", "Capacité logistique", "Commandes supplémentaires"],
      ["Universités et écoles", "Accès aux étudiants, stages", "Insertion des diplômés"],
      ["Entreprises privées", "Offres d'emploi, publicité", "Recrutement plus rapide"],
      ["Médias et agences de communication", "Visibilité, campagnes", "Contenus, budgets publicitaires"],
      ["Incubateurs", "Accompagnement, réseau", "Une startup déjà en production"]])}
<p class="src">Aucun partenariat n'est signé à la date de ce document.</p>

<h2>13. Risques et réponses</h2>
{tbl([["Risque", "Réponse"],
      ["Faible usage d'Internet (≈ 13 %)", "Cibler d'abord les internautes urbains ; interface légère ; assistance par agents de terrain"],
      ["Coupures d'Internet", "Fonctions hors ligne simples, SMS de confirmation, relais par les agents"],
      ["Adoption lente du paiement en ligne", "Paiement mobile et espèces au démarrage"],
      ["Confiance et sécurité (clando, annonces)", "Vérification des prestataires, notation, signalement"],
      ["Dispersion sur trop de pôles", "Priorité à la mobilité et à l'emploi ; pôles suivants selon la traction"],
      ["Trésorerie en A2", "Recrutement indexé sur le CA ; relais de financement préparé dès le M9"],
      ["Réglementation (données, transport)", "Conseil juridique dès l'A1 ; dialogue avec la mairie et les ministères"]])}

<h2>14. Appel à l'action</h2>
<div class="box"><p>Un problème réel. Une solution déjà en production. Un marché jeune où le mobile progresse. Huit sources de revenus. Une expansion par étapes. Des emplois. Un fondateur engagé.</p>
<p><b>Nous demandons 15 000 000 FCFA et un accompagnement stratégique pour lancer la croissance de Maousang.</b></p>
<p style="font-size:12pt"><b style="color:{AMBER}">MAOUSANG</b> — <i>Connecter les services, rapprocher les opportunités et construire l'économie numérique de demain.</i></p>
<p>Giscard Destin, fondateur · maousang.vercel.app</p></div>

<h2 class="pb">Annexe : parcours en captures d'écran</h2>
<p>Du démarrage aux fonctionnalités. Les emplacements vides sont remplis automatiquement lorsque les captures existent dans <code>assets/captures/</code> (voir LISEZ-MOI.md).</p>
<div class="caps">{cap_html}</div>
<p class="src" style="margin-top:12px">Sources détaillées, dates et liens : MAOUSANG_SOURCES.md.</p>
</body></html>"""

with open(os.path.join(ROOT, "outils", "business_plan.html"), "w") as f:
    f.write(html)
print("html ok")
