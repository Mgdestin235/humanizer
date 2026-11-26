"""Construit MAOUSANG_FINANCIAL_MODEL.xlsx avec de vraies formules Excel.

Toutes les valeurs sont des HYPOTHÈSES prévisionnelles (montants en FCFA).
Les cellules bleues sont des hypothèses modifiables ; les cellules noires sont calculées.
"""
import re
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = sys.argv[1] if len(sys.argv) > 1 else "MAOUSANG_FINANCIAL_MODEL.xlsx"

TEAL = "0F766E"
DARK = "0B1B2B"
AMBER = "F59E0B"
LIGHT = "EEF6F5"
INPUT_FONT = Font(name="Arial", size=10, color="1D4ED8")
CALC_FONT = Font(name="Arial", size=10, color="000000")
BOLD = Font(name="Arial", size=10, bold=True)
HEAD = Font(name="Arial", size=11, bold=True, color="FFFFFF")
TITLE = Font(name="Arial", size=14, bold=True, color=DARK)
SEC_FILL = PatternFill("solid", fgColor=LIGHT)
HEAD_FILL = PatternFill("solid", fgColor=TEAL)
INPUT_FILL = PatternFill("solid", fgColor="FFF7E6")
thin = Side(style="thin", color="D0D7DE")
BORDER = Border(bottom=thin)

FMT_FCFA = '#,##0" FCFA";-#,##0" FCFA";"-"'
FMT_INT = '#,##0;-#,##0;"-"'
FMT_PCT = '0.0%'
FMT_DEC = '#,##0.0'

YEARS = ["Année 1", "Année 2", "Année 3"]
COLS = ["C", "D", "E"]

# ---------------------------------------------------------------- Équipe
# poste, effectifs (A1,A2,A3), salaire mensuel brut estimatif (A1,A2,A3), note
TEAM = [
    ("Directeur général (fondateur)", (1, 1, 1), (0, 350000, 500000),
     "A1 : non rémunéré (apport du fondateur), assure aussi la direction technique"),
    ("Responsable technique", (0, 1, 1), (0, 300000, 450000), "Recruté en A2"),
    ("Développeurs", (0, 1, 4), (0, 250000, 300000), "Équipe produit à partir de A2"),
    ("Responsable commercial et partenariats", (1, 1, 1), (150000, 250000, 400000), ""),
    ("Responsable marketing et communication", (1, 1, 1), (150000, 250000, 400000), ""),
    ("Responsable administratif et financier", (0, 1, 1), (0, 250000, 350000),
     "A1 : comptabilité externalisée (frais administratifs)"),
    ("Chargés de partenariats / commerciaux", (0, 1, 4), (0, 150000, 150000), ""),
    ("Agents de terrain", (4, 10, 25), (62500, 75000, 80000),
     "A1 : temps partiel + primes sur résultats"),
    ("Support client", (1, 4, 10), (75000, 90000, 100000), ""),
]

# ------------------------------------------------------------ Financement
FUNDING = [
    ("Marketing et communication", 3000000,
     "Agence de communication, identité, campagnes digitales, influenceurs, événements"),
    ("Recrutement et rémunération", 4500000,
     "Resp. commercial (150 000) + resp. marketing (150 000) + support (75 000) × 12 mois"),
    ("Agents de terrain", 3000000, "4 agents × 62 500 FCFA × 12 mois (temps partiel)"),
    ("Prospection commerciale", 1000000, "Supports imprimés, déplacements, kits de démonstration"),
    ("Frais administratifs et juridiques", 1000000,
     "Immatriculation, CGU / protection des données, comptabilité externalisée, marque"),
    ("Infrastructure technique et maintenance", 1200000,
     "Hébergement, base de données, SMS/OTP, cartographie, stores, 100 000 FCFA/mois"),
    ("Partenariats et développement commercial", 800000,
     "Intégration paiement mobile, conventions transporteurs, agences, universités"),
    ("Fonds de roulement", 500000, "Réserve de sécurité (imprévus, décalages de trésorerie)"),
]

# ----------------------------------------------------------- Scénarios
# Valeurs (A1, A2, A3) par scénario : prudent, intermediaire, ambitieux
S = {
    "user_factor": ((0.5,) * 3, (1.0,) * 3, (1.2,) * 3),
    "mau_rate": ((0.30, 0.25, 0.20), (0.35, 0.30, 0.25), (0.40, 0.35, 0.30)),
    "pros_rate": ((0.02,) * 3, (0.02,) * 3, (0.02,) * 3),
    "mob_share": ((0.35,) * 3, (0.40,) * 3, (0.45,) * 3),
    "mob_freq": ((3,) * 3, (4,) * 3, (5,) * 3),
    "mob_aov": ((1000,) * 3, (1000,) * 3, (1200,) * 3),
    "mob_comm": ((0.08,) * 3, (0.10,) * 3, (0.12,) * 3),
    "bil_share": ((0.10,) * 3, (0.15,) * 3, (0.20,) * 3),
    "bil_trips": ((2,) * 3, (2,) * 3, (2,) * 3),
    "bil_price": ((15000,) * 3, (15000,) * 3, (15000,) * 3),
    "bil_comm": ((0.04,) * 3, (0.05,) * 3, (0.06,) * 3),
    "emp_comp": ((25, 150, 600), (50, 300, 1200), (80, 450, 1800)),
    "emp_posts": ((2,) * 3, (3,) * 3, (4,) * 3),
    "emp_price": ((10000,) * 3, (10000,) * 3, (10000,) * 3),
    "ats_subs": ((3, 15, 60), (5, 30, 120), (8, 45, 180)),
    "ats_price": ((25000,) * 3, (25000,) * 3, (25000,) * 3),
    "imm_spons": ((10, 60, 300), (20, 120, 600), (30, 180, 900)),
    "imm_spons_price": ((5000,) * 3, (5000,) * 3, (5000,) * 3),
    "imm_nights": ((100, 800, 5000), (200, 1500, 10000), (300, 2500, 15000)),
    "imm_stay": ((3,) * 3, (3,) * 3, (3,) * 3),
    "imm_night_price": ((20000,) * 3, (20000,) * 3, (20000,) * 3),
    "imm_comm": ((0.10,) * 3, (0.10,) * 3, (0.10,) * 3),
    "pro_paid_share": ((0.04,) * 3, (0.06,) * 3, (0.08,) * 3),
    "pro_price": ((5000,) * 3, (5000,) * 3, (5000,) * 3),
    "ads_n": ((1, 5, 20), (2, 10, 40), (3, 15, 60)),
    "ads_price": ((50000,) * 3, (50000,) * 3, (50000,) * 3),
    "ref_share": ((0.20,) * 3, (0.20,) * 3, (0.20,) * 3),
    "ref_reward": ((500,) * 3, (500,) * 3, (500,) * 3),
    "staff_factor": ((1.0, 0.7, 0.7), (1.0, 1.0, 1.0), (1.0, 1.5, 1.5)),
    "mkt_fixed": ((4800000, 20000000, 30000000), (4800000, 30000000, 90000000),
                  (4800000, 45000000, 200000000)),
    "tech": ((1200000, 4000000, 20000000), (1200000, 6000000, 45000000),
             (1200000, 8000000, 80000000)),
    "ops": ((1000000, 8000000, 30000000), (1000000, 12000000, 60000000),
            (1000000, 15000000, 100000000)),
    "pay_fee": ((0.03,) * 3, (0.03,) * 3, (0.03,) * 3),
}
SCEN = [("Prudent", 0), ("Intermediaire", 1), ("Ambitieux", 2)]
SCEN_LABEL = {"Prudent": "Prudent", "Intermediaire": "Intermédiaire", "Ambitieux": "Ambitieux"}

# Lignes : (clé, libellé, unité, type, formule ou None, explication)
# type: 'sec' section, 'in' hypothèse, 'calc' calcul. Formule : [cle] = même année,
# [cle@prev] = année précédente, {TEAM} = masse salariale de l'onglet Equipe.
ROWS = [
    ("s_users", "UTILISATEURS", "", "sec", None, ""),
    ("users_target", "Objectif d'utilisateurs inscrits (fin d'année)", "pers.", "fixed",
     (10000, 100000, 1000000), "Objectifs de croissance du fondateur, pas des données acquises"),
    ("user_factor", "Coefficient de réalisation de l'objectif", "x", "in", None,
     "Prudent 0,5 ; intermédiaire 1,0 ; ambitieux 1,2"),
    ("users_end", "Utilisateurs inscrits (fin d'année)", "pers.", "calc",
     "=[users_target]*[user_factor]", "Objectif × coefficient"),
    ("users_avg", "Utilisateurs inscrits moyens sur l'année", "pers.", "calc",
     ("=[users_end]/2", "=([users_end@prev]+[users_end])/2", "=([users_end@prev]+[users_end])/2"),
     "(Inscrits début + inscrits fin) / 2 ; A1 démarre à 0"),
    ("new_users", "Nouveaux inscrits sur l'année", "pers.", "calc",
     ("=[users_end]", "=[users_end]-[users_end@prev]", "=[users_end]-[users_end@prev]"),
     "Inscrits fin − inscrits fin de l'année précédente"),
    ("mau_rate", "Taux d'utilisateurs actifs mensuels (MAU / inscrits)", "%", "in", None,
     "Baisse avec la taille : les nouveaux inscrits sont moins actifs"),
    ("mau", "Utilisateurs actifs mensuels moyens (MAU)", "pers.", "calc",
     "=[users_avg]*[mau_rate]", "Inscrits moyens × taux MAU"),
    ("pros_rate", "Prestataires professionnels / inscrits", "%", "in", None,
     "Conducteurs, livreurs, agences, recruteurs, transporteurs"),
    ("pros", "Prestataires professionnels inscrits (fin d'année)", "pers.", "calc",
     "=[users_end]*[pros_rate]", "Inscrits fin × ratio prestataires"),

    ("s_mob", "PÔLE MOBILITÉ – CLANDO ET LIVRAISON", "", "sec", None, ""),
    ("mob_share", "Part des MAU utilisant la mobilité", "%", "in", None, ""),
    ("mob_freq", "Courses ou livraisons par utilisateur et par mois", "nb", "in", None, ""),
    ("mob_aov", "Prix moyen d'une course ou livraison", "FCFA", "in", None,
     "Mix courses moto courtes et livraisons – hypothèse à tester"),
    ("mob_comm", "Commission Maousang", "%", "in", None, "Prélevée sur le prix payé"),
    ("mob_users", "Utilisateurs mobilité actifs", "pers.", "calc", "=[mau]*[mob_share]", "MAU × part"),
    ("mob_tx", "Courses et livraisons sur l'année", "nb", "calc",
     "=[mob_users]*[mob_freq]*12", "Utilisateurs × fréquence × 12 mois"),
    ("mob_gmv", "Volume d'affaires mobilité", "FCFA", "calc", "=[mob_tx]*[mob_aov]", "Transactions × prix moyen"),
    ("rev_mob", "CA mobilité", "FCFA", "calc", "=[mob_gmv]*[mob_comm]", "Volume × commission"),

    ("s_bil", "PÔLE BILLETTERIE", "", "sec", None, ""),
    ("bil_share", "Part des MAU achetant un billet", "%", "in", None, ""),
    ("bil_trips", "Billets par acheteur et par an", "nb", "in", None, ""),
    ("bil_price", "Prix moyen d'un billet interurbain", "FCFA", "in", None,
     "Ordre de grandeur constaté : N'Djaména–Moundou 12 500, –Sarh 17 500, –Abéché 25 000"),
    ("bil_comm", "Commission partenaire transporteur", "%", "in", None, "À négocier avec les compagnies"),
    ("bil_users", "Acheteurs de billets", "pers.", "calc", "=[mau]*[bil_share]", "MAU × part"),
    ("bil_tx", "Billets vendus", "nb", "calc", "=[bil_users]*[bil_trips]", "Acheteurs × billets/an"),
    ("bil_gmv", "Volume d'affaires billetterie", "FCFA", "calc", "=[bil_tx]*[bil_price]", ""),
    ("rev_bil", "CA billetterie", "FCFA", "calc", "=[bil_gmv]*[bil_comm]", "Volume × commission"),

    ("s_emp", "PÔLE EMPLOI ET ATS", "", "sec", None, ""),
    ("emp_comp", "Entreprises publiant des offres payantes", "nb", "in", None, ""),
    ("emp_posts", "Offres payantes par entreprise et par an", "nb", "in", None, ""),
    ("emp_price", "Prix d'une offre d'emploi", "FCFA", "in", None, "Candidats : gratuit"),
    ("ats_subs", "Recruteurs abonnés ATS premium (moyenne mensuelle)", "nb", "in", None, ""),
    ("ats_price", "Abonnement ATS premium mensuel", "FCFA", "in", None,
     "Analyse de CV, classement, présélection"),
    ("emp_tx", "Offres payantes publiées", "nb", "calc", "=[emp_comp]*[emp_posts]", ""),
    ("rev_emp_posts", "CA offres d'emploi", "FCFA", "calc", "=[emp_tx]*[emp_price]", ""),
    ("rev_ats", "CA ATS premium", "FCFA", "calc", "=[ats_subs]*[ats_price]*12", "Abonnés × prix × 12"),
    ("rev_emp", "CA emploi", "FCFA", "calc", "=[rev_emp_posts]+[rev_ats]", ""),

    ("s_imm", "PÔLE IMMOBILIER", "", "sec", None, ""),
    ("imm_spons", "Annonces sponsorisées actives (moyenne mensuelle)", "nb", "in", None, ""),
    ("imm_spons_price", "Prix d'une annonce sponsorisée par mois", "FCFA", "in", None, ""),
    ("imm_nights", "Nuitées réservées (location journalière)", "nb", "in", None, ""),
    ("imm_stay", "Durée moyenne d'un séjour", "nuits", "in", None, ""),
    ("imm_night_price", "Prix moyen d'une nuitée", "FCFA", "in", None, ""),
    ("imm_comm", "Commission sur réservation", "%", "in", None, ""),
    ("imm_bookings", "Réservations journalières", "nb", "calc", "=[imm_nights]/[imm_stay]", "Nuitées / durée"),
    ("rev_imm_spons", "CA annonces sponsorisées", "FCFA", "calc", "=[imm_spons]*[imm_spons_price]*12", ""),
    ("rev_imm_book", "CA réservations", "FCFA", "calc", "=[imm_nights]*[imm_night_price]*[imm_comm]", ""),
    ("rev_imm", "CA immobilier", "FCFA", "calc", "=[rev_imm_spons]+[rev_imm_book]", ""),

    ("s_trans", "REVENUS TRANSVERSAUX", "", "sec", None, ""),
    ("pro_paid_share", "Prestataires ayant un abonnement professionnel", "%", "in", None, ""),
    ("pro_price", "Abonnement professionnel mensuel", "FCFA", "in", None,
     "Visibilité, badge vérifié, statistiques"),
    ("ads_n", "Annonceurs actifs (moyenne mensuelle)", "nb", "in", None, ""),
    ("ads_price", "Forfait publicitaire mensuel", "FCFA", "in", None, ""),
    ("pro_paid", "Prestataires abonnés", "nb", "calc", "=[pros]*[pro_paid_share]", ""),
    ("rev_subs", "CA abonnements professionnels", "FCFA", "calc", "=[pro_paid]*[pro_price]*12", ""),
    ("rev_ads", "CA publicité", "FCFA", "calc", "=[ads_n]*[ads_price]*12", ""),

    ("s_tot", "SYNTHÈSE DES REVENUS ET INDICATEURS", "", "sec", None, ""),
    ("rev_total", "CHIFFRE D'AFFAIRES TOTAL", "FCFA", "calc",
     "=[rev_mob]+[rev_bil]+[rev_emp]+[rev_imm]+[rev_subs]+[rev_ads]", "Somme des pôles"),
    ("tx_total", "Transactions totales", "nb", "calc",
     "=[mob_tx]+[bil_tx]+[emp_tx]+[imm_bookings]", "Courses + billets + offres + réservations"),
    ("payers", "Clients payants (personnes et entreprises)", "nb", "calc",
     "=[mob_users]+[bil_users]+[imm_bookings]+[emp_comp]+[ats_subs]+[imm_spons]+[pro_paid]+[ads_n]",
     "Utilisateurs qui paient au moins une fois"),
    ("conv", "Taux de conversion payant", "%", "calc", "=[payers]/[users_avg]", "Clients payants / inscrits moyens"),
    ("arppu", "Revenu moyen par client payant (annuel)", "FCFA", "calc", "=[rev_total]/[payers]", "CA / clients payants"),

    ("s_cost", "DÉPENSES", "", "sec", None, ""),
    ("staff_factor", "Coefficient d'équipe (plan de l'onglet Equipe)", "x", "in", None,
     "A1 identique dans tous les scénarios (budget financé)"),
    ("mkt_fixed", "Marketing, prospection et partenariats (fixe)", "FCFA", "in", None,
     "A1 = 3,0 M marketing + 1,0 M prospection + 0,8 M partenariats"),
    ("ref_share", "Part des nouveaux inscrits venant du parrainage", "%", "in", None, ""),
    ("ref_reward", "Récompense par filleul actif", "FCFA", "in", None, "Crédit de course ou bon d'achat"),
    ("tech", "Coûts techniques et infrastructure", "FCFA", "in", None, ""),
    ("ops", "Dépenses opérationnelles (administratif, juridique, bureau)", "FCFA", "in", None, ""),
    ("pay_fee", "Frais de paiement mobile (en % du CA)", "%", "in", None, ""),
    ("cost_staff", "Masse salariale", "FCFA", "calc", "={TEAM}*[staff_factor]", "Plan Equipe × coefficient"),
    ("cost_ref", "Coût du parrainage", "FCFA", "calc", "=[new_users]*[ref_share]*[ref_reward]", ""),
    ("cost_mkt", "Dépenses marketing totales", "FCFA", "calc", "=[mkt_fixed]+[cost_ref]", ""),
    ("cost_pay", "Frais de paiement", "FCFA", "calc", "=[rev_total]*[pay_fee]", ""),
    ("cost_ops", "Dépenses opérationnelles totales", "FCFA", "calc", "=[ops]+[cost_pay]", ""),
    ("cost_total", "TOTAL DES DÉPENSES", "FCFA", "calc", "=[cost_staff]+[cost_mkt]+[tech]+[cost_ops]", ""),
    ("ebit", "RÉSULTAT OPÉRATIONNEL PRÉVISIONNEL", "FCFA", "calc", "=[rev_total]-[cost_total]", "CA − dépenses"),
    ("margin", "Marge opérationnelle", "%", "calc", "=IF([rev_total]=0,0,[ebit]/[rev_total])", ""),
    ("cash", "Trésorerie fin d'année (15 M FCFA levés, sans autre financement)", "FCFA", "calc",
     ("=15000000+[ebit]", "=[cash@prev]+[ebit]", "=[cash@prev]+[ebit]"),
     "Si négative : besoin de financement complémentaire"),
]

PCT_KEYS = {"mau_rate", "pros_rate", "mob_share", "mob_comm", "bil_share", "bil_comm",
            "imm_comm", "pro_paid_share", "ref_share", "pay_fee", "conv", "margin"}


def fmt_for(unit, key):
    if key in PCT_KEYS or unit == "%":
        return FMT_PCT
    if unit == "FCFA":
        return FMT_FCFA
    if unit == "x":
        return '0.00'
    return FMT_INT


def build():
    wb = Workbook()

    # ------------------------------------------------------------- Lisez-moi
    ws = wb.active
    ws.title = "Lisez-moi"
    lines = [
        ("MAOUSANG – Modèle financier prévisionnel sur 3 ans", TITLE),
        ("Tous les montants sont en FCFA. Tous les chiffres sont des HYPOTHÈSES et des objectifs, pas des résultats acquis.", BOLD),
        ("", None),
        ("Comment lire ce fichier :", BOLD),
        ("• Cellules bleues sur fond crème : hypothèses modifiables. Cellules noires : calculs automatiques.", None),
        ("• Onglets Prudent, Intermediaire, Ambitieux : même structure, hypothèses différentes.", None),
        ("• La colonne F de chaque scénario explique la formule en langage clair.", None),
        ("• Onglet Equipe : plan de recrutement et masse salariale (A1 = budget financé).", None),
        ("• Onglet Financement : ventilation indicative des 15 000 000 FCFA, à affiner selon devis.", None),
        ("• Onglet Marche : calcul TAM / SAM / SOM à partir de sources publiques (voir MAOUSANG_SOURCES.md).", None),
        ("• Onglet Synthese : comparaison des trois scénarios.", None),
        ("", None),
        ("Les tarifs (commissions, abonnements, forfaits) sont des hypothèses de travail non validées par le marché.", None),
        ("Ils doivent être testés auprès des utilisateurs et des partenaires avant toute communication commerciale.", None),
    ]
    for i, (t, f) in enumerate(lines, 1):
        c = ws.cell(row=i, column=1, value=t)
        if f:
            c.font = f
        else:
            c.font = Font(name="Arial", size=10)
    ws.column_dimensions["A"].width = 120

    # ---------------------------------------------------------------- Equipe
    we = wb.create_sheet("Equipe")
    we["A1"] = "Plan d'équipe et masse salariale (scénario de référence)"
    we["A1"].font = TITLE
    hdr = ["Poste", "Effectif A1", "Effectif A2", "Effectif A3",
           "Salaire mensuel A1", "Salaire mensuel A2", "Salaire mensuel A3",
           "Coût annuel A1", "Coût annuel A2", "Coût annuel A3", "Note"]
    for j, h in enumerate(hdr, 1):
        c = we.cell(row=3, column=j, value=h)
        c.font = HEAD
        c.fill = HEAD_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
    r0 = 4
    for i, (poste, hc, sal, note) in enumerate(TEAM):
        r = r0 + i
        we.cell(row=r, column=1, value=poste).font = CALC_FONT
        for k in range(3):
            c = we.cell(row=r, column=2 + k, value=hc[k])
            c.font, c.fill, c.number_format = INPUT_FONT, INPUT_FILL, FMT_INT
            c = we.cell(row=r, column=5 + k, value=sal[k])
            c.font, c.fill, c.number_format = INPUT_FONT, INPUT_FILL, FMT_FCFA
            hcl, sl = get_column_letter(2 + k), get_column_letter(5 + k)
            c = we.cell(row=r, column=8 + k, value=f"={hcl}{r}*{sl}{r}*12")
            c.font, c.number_format = CALC_FONT, FMT_FCFA
        we.cell(row=r, column=11, value=note).font = Font(name="Arial", size=9, italic=True)
    rt = r0 + len(TEAM)
    we.cell(row=rt, column=1, value="TOTAL").font = BOLD
    for k in range(3):
        for base in (2, 8):
            col = get_column_letter(base + k)
            c = we.cell(row=rt, column=base + k, value=f"=SUM({col}{r0}:{col}{rt-1})")
            c.font = BOLD
            c.number_format = FMT_INT if base == 2 else FMT_FCFA
    we.cell(row=rt + 2, column=1,
            value="Les salaires sont des estimations pour N'Djaména, à valider avec un cabinet RH et le Code du travail.").font = Font(name="Arial", size=9, italic=True)
    widths = [42, 11, 11, 11, 17, 17, 17, 17, 17, 17, 60]
    for j, w in enumerate(widths, 1):
        we.column_dimensions[get_column_letter(j)].width = w
    team_total_ref = {0: f"Equipe!H{rt}", 1: f"Equipe!I{rt}", 2: f"Equipe!J{rt}"}

    # ---------------------------------------------------------- Scénarios
    rowmap = {}
    for name, si in SCEN:
        ws = wb.create_sheet(name)
        ws["A1"] = f"Scénario {SCEN_LABEL[name]} – compte de résultat prévisionnel (FCFA)"
        ws["A1"].font = TITLE
        for j, h in enumerate(["Indicateur", "Unité"] + YEARS + ["Formule / justification"], 1):
            c = ws.cell(row=3, column=j, value=h)
            c.font = HEAD
            c.fill = HEAD_FILL
        r = 4
        local = {}
        for key, *_ in ROWS:
            local[key] = r
            r += 1
        rowmap = local
        for key, label, unit, typ, formula, note in ROWS:
            rr = local[key]
            if typ == "sec":
                c = ws.cell(row=rr, column=1, value=label)
                c.font = Font(name="Arial", size=10, bold=True, color=TEAL)
                for j in range(1, 7):
                    ws.cell(row=rr, column=j).fill = SEC_FILL
                continue
            lab = ws.cell(row=rr, column=1, value=label)
            lab.font = BOLD if key in ("rev_total", "cost_total", "ebit", "cash") else CALC_FONT
            ws.cell(row=rr, column=2, value=unit).font = CALC_FONT
            for k, col in enumerate(COLS):
                if typ == "in":
                    val = S[key][si][k]
                    c = ws.cell(row=rr, column=3 + k, value=val)
                    c.font, c.fill = INPUT_FONT, INPUT_FILL
                elif typ == "fixed":
                    c = ws.cell(row=rr, column=3 + k, value=formula[k])
                    c.font, c.fill = INPUT_FONT, INPUT_FILL
                else:
                    f = formula[k] if isinstance(formula, tuple) else formula
                    f = f.replace("{TEAM}", team_total_ref[k])

                    def sub(m):
                        ref = m.group(1)
                        if ref.endswith("@prev"):
                            return f"{COLS[k-1]}{local[ref[:-5]]}"
                        return f"{col}{local[ref]}"
                    f = re.sub(r"\[([a-z_@]+)\]", sub, f)
                    c = ws.cell(row=rr, column=3 + k, value=f)
                    c.font = BOLD if key in ("rev_total", "cost_total", "ebit", "cash") else CALC_FONT
                c.number_format = fmt_for(unit, key)
            ws.cell(row=rr, column=6, value=note).font = Font(name="Arial", size=9, italic=True, color="475569")
            if key in ("rev_total", "ebit"):
                for j in range(1, 6):
                    ws.cell(row=rr, column=j).border = Border(top=thin, bottom=thin)
        ws.column_dimensions["A"].width = 58
        ws.column_dimensions["B"].width = 8
        for col in COLS:
            ws.column_dimensions[col].width = 20
        ws.column_dimensions["F"].width = 70
        ws.freeze_panes = "C4"

    # ------------------------------------------------------------ Synthèse
    wsy = wb.create_sheet("Synthese", 1)
    wsy["A1"] = "Synthèse des trois scénarios (FCFA, prévisionnel)"
    wsy["A1"].font = TITLE
    KEYS = [("users_end", "Utilisateurs inscrits (fin d'année)"), ("mau", "Utilisateurs actifs mensuels moyens"),
            ("pros", "Prestataires professionnels"), ("tx_total", "Transactions"),
            ("conv", "Taux de conversion payant"), ("arppu", "Revenu moyen par client payant"),
            ("rev_mob", "CA mobilité"), ("rev_bil", "CA billetterie"), ("rev_emp", "CA emploi"),
            ("rev_imm", "CA immobilier"), ("rev_subs", "CA abonnements pros"), ("rev_ads", "CA publicité"),
            ("rev_total", "CHIFFRE D'AFFAIRES TOTAL"), ("cost_ops", "Dépenses opérationnelles"),
            ("cost_mkt", "Dépenses marketing"), ("cost_staff", "Masse salariale"),
            ("tech", "Coûts techniques et infrastructure"), ("cost_total", "Total des dépenses"),
            ("ebit", "RÉSULTAT OPÉRATIONNEL"), ("cash", "Trésorerie fin d'année")]
    r = 3
    for name, si in SCEN:
        c = wsy.cell(row=r, column=1, value=f"Scénario {SCEN_LABEL[name]}")
        c.font = HEAD
        for j in range(1, 6):
            wsy.cell(row=r, column=j).fill = HEAD_FILL
        for k, y in enumerate(YEARS):
            cc = wsy.cell(row=r, column=3 + k, value=y)
            cc.font = HEAD
        r += 1
        for key, lab in KEYS:
            unit = next(u for kk, _, u, *_ in ROWS if kk == key)
            wsy.cell(row=r, column=1, value=lab).font = BOLD if key in ("rev_total", "ebit") else CALC_FONT
            for k, col in enumerate(COLS):
                c = wsy.cell(row=r, column=3 + k, value=f"={name}!{col}{rowmap[key]}")
                c.number_format = fmt_for(unit, key)
                c.font = BOLD if key in ("rev_total", "ebit") else CALC_FONT
            r += 1
        r += 1
    wsy.column_dimensions["A"].width = 44
    for col in COLS:
        wsy.column_dimensions[col].width = 20

    # ---------------------------------------------------------- Financement
    wf = wb.create_sheet("Financement")
    wf["A1"] = "Besoin de financement : 15 000 000 FCFA (ventilation indicative, à affiner selon devis)"
    wf["A1"].font = TITLE
    for j, h in enumerate(["Poste", "Montant", "Part", "Contenu"], 1):
        c = wf.cell(row=3, column=j, value=h)
        c.font, c.fill = HEAD, HEAD_FILL
    for i, (p, m, d) in enumerate(FUNDING):
        r = 4 + i
        wf.cell(row=r, column=1, value=p).font = CALC_FONT
        c = wf.cell(row=r, column=2, value=m)
        c.font, c.fill, c.number_format = INPUT_FONT, INPUT_FILL, FMT_FCFA
        c = wf.cell(row=r, column=3, value=f"=B{r}/$B${4+len(FUNDING)}")
        c.number_format = FMT_PCT
        wf.cell(row=r, column=4, value=d).font = Font(name="Arial", size=9)
    rt = 4 + len(FUNDING)
    wf.cell(row=rt, column=1, value="TOTAL").font = BOLD
    c = wf.cell(row=rt, column=2, value=f"=SUM(B4:B{rt-1})")
    c.font, c.number_format = BOLD, FMT_FCFA
    wf.cell(row=rt + 1, column=1, value="Contrôle : écart avec 15 000 000").font = CALC_FONT
    c = wf.cell(row=rt + 1, column=2, value=f"=B{rt}-15000000")
    c.number_format = FMT_FCFA
    wf.cell(row=rt + 3, column=1, value="Distinction des ressources").font = BOLD
    rows = [
        ("Dépenses déjà réalisées par le fondateur", "Conception, développement et mise en production de la plateforme",
         "Apport en temps et en compétences (non décaissé par le financement demandé)"),
        ("Apport du fondateur", "Travail non rémunéré en A1 (direction générale et technique)",
         "Valorisation à renseigner par le fondateur si nécessaire"),
        ("Besoin financier restant", "15 000 000 FCFA", "Lancement commercial et structuration sur 12 mois"),
        ("Dépenses futures (A2, A3)", "Financées par le CA et, si besoin, un tour complémentaire",
         "Voir la trésorerie des onglets de scénario"),
    ]
    for i, (a, b, c3) in enumerate(rows):
        r = rt + 4 + i
        wf.cell(row=r, column=1, value=a).font = BOLD
        wf.cell(row=r, column=2, value=b).font = CALC_FONT
        wf.cell(row=r, column=4, value=c3).font = Font(name="Arial", size=9, italic=True)
    wf.column_dimensions["A"].width = 44
    wf.column_dimensions["B"].width = 26
    wf.column_dimensions["C"].width = 9
    wf.column_dimensions["D"].width = 80

    # --------------------------------------------------------------- Marché
    wm = wb.create_sheet("Marche")
    wm["A1"] = "TAM / SAM / SOM – Tchad (base : données publiques, hypothèses signalées)"
    wm["A1"].font = TITLE
    data = [
        ("Population du Tchad (oct. 2025)", 21100000, "DataReportal Digital 2026 (ONU)", "src"),
        ("Part urbaine de la population", 0.251, "DataReportal Digital 2026", "src"),
        ("Utilisateurs d'Internet (oct. 2025)", 2790000, "DataReportal Digital 2026 (Kepios)", "src"),
        ("Connexions mobiles (fin 2025)", 15500000, "DataReportal Digital 2026 (GSMA Intelligence)", "src"),
        ("Hypothèse : taux d'usage d'Internet en ville", 0.30, "HYPOTHÈSE (moyenne nationale ≈ 13 %)", "hyp"),
        ("Population urbaine", "=B4*B5", "Calcul", "calc"),
        ("TAM – internautes au Tchad", "=B6", "Toute personne en ligne peut utiliser Maousang", "calc"),
        ("SAM – internautes urbains (N'Djaména et grandes villes)", "=B9*B8", "Population urbaine × usage urbain", "calc"),
        ("SOM prudent (5 % du SAM, utilisateurs actifs)", "=B11*0.05", "Part conquise à 3 ans", "calc"),
        ("SOM intermédiaire (10 % du SAM)", "=B11*0.10", "", "calc"),
        ("SOM ambitieux (20 % du SAM)", "=B11*0.20", "", "calc"),
        ("MAU fin A3 implicite – objectif 1 M inscrits", "=Intermediaire!E%d*Intermediaire!E%d" % (rowmap["users_end"], rowmap["mau_rate"]), "Inscrits fin A3 × taux MAU", "calc"),
        ("Part du SAM correspondante", "=B15/B11", "Lecture : objectif très ambitieux", "calc"),
        ("Revenu annuel par MAU (intermédiaire A3)", "=Intermediaire!E%d/Intermediaire!E%d" % (rowmap["rev_total"], rowmap["mau"]), "CA A3 / MAU A3", "calc"),
        ("TAM en valeur (revenu plateforme potentiel)", "=B10*B17", "TAM × revenu par MAU", "calc"),
        ("SAM en valeur", "=B11*B17", "SAM × revenu par MAU", "calc"),
        ("SOM intermédiaire en valeur", "=B13*B17", "SOM × revenu par MAU", "calc"),
    ]
    for j, h in enumerate(["Indicateur", "Valeur", "Source / méthode"], 1):
        c = wm.cell(row=3, column=j, value=h)
        c.font, c.fill = HEAD, HEAD_FILL
    for i, (lab, val, src, kind) in enumerate(data):
        r = 4 + i
        wm.cell(row=r, column=1, value=lab).font = CALC_FONT
        c = wm.cell(row=r, column=2, value=val)
        if kind in ("src", "hyp"):
            c.font, c.fill = INPUT_FONT, INPUT_FILL
        is_pct = "Part" in lab or "taux" in lab
        c.number_format = FMT_PCT if is_pct else (FMT_FCFA if "valeur" in lab or "Revenu" in lab else FMT_INT)
        wm.cell(row=r, column=3, value=src).font = Font(name="Arial", size=9, italic=True)
    wm.column_dimensions["A"].width = 58
    wm.column_dimensions["B"].width = 24
    wm.column_dimensions["C"].width = 60

    wb.save(OUT)
    return rowmap


if __name__ == "__main__":
    rm = build()
    import json
    with open(OUT + ".rows.json", "w") as f:
        json.dump(rm, f)
    print("ok", OUT)
