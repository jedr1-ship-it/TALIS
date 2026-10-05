#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis exploratorio: ¿qué más difiere, según la edad al terremoto, entre
los adolescentes de las comunas afectadas y no afectadas? (ola 2024)

Cada resultado se estima con la especificación de la columna 3 de la
Table 3; los coeficientes comparan cada edad de exposición con los
expuestos a 0-11 meses. El diseño identifica diferencias entre edades de
exposición, no el nivel del efecto: un perfil plano es compatible con que
el terremoto no afecte al resultado o con que afecte por igual a todas las
edades.

Salidas: paper/tables/b1_explora_adolescente.tex,
         paper/tables/b2_explora_conducta.tex,
         paper/tables/b3_explora_familia.tex,
         reports/exploratorio_mapa.png, reports/exploratorio.md
Uso:     python3 scripts/19_exploratorio.py
"""
import importlib.util
import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pyreadstat

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p15", HERE / "15_paper_estimaciones.py")
p15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p15)
num, fit, stars, zg = p15.num, p15.fit, p15.stars, p15.zg
bcell, secell, fnum = p15.bcell, p15.secell, p15.fnum
TAB = Path("paper/tables")
OUT = []

NOTA_MEDIA = {1: 3.7, 2: 4.2, 3: 4.7, 4: 5.2, 5: 5.7, 6: 6.2, 7: 6.75}


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def rango(s, lo, hi):
    s = num(s)
    return s.where(s.between(lo, hi))


def si(s):
    """1 = sí, 2 = no -> 1/0; otros códigos, perdido."""
    s = num(s)
    return pd.Series(np.where(s == 1, 1.0, np.where(s == 2, 0.0, np.nan)),
                     index=s.index)


def construye():
    d, _, _ = p15.load_data()
    A, _ = pyreadstat.read_dta("data/interim/2024/Base adolescentes Stata.dta")
    A["folio"] = num(A.folio).astype("int64")
    A = A.drop_duplicates("folio").set_index("folio")
    x = pd.DataFrame(index=A.index)
    for k, v in enumerate(["familia", "amigos", "colegio", "si_mismo",
                           "barrio", "vida", "cuerpo"], start=1):
        x[f"sat_{v}"] = zg(rango(A[f"d3_{k}"], 1, 7))
    x["asiste"] = si(A.e1)
    x["nota"] = num(A.e3_asiste).map(NOTA_MEDIA)
    x["le_va"] = zg(rango(A.e2_asiste, 1, 5))
    x["gusta"] = zg(rango(A.e5, 1, 5))
    x["profes"] = zg(rango(A.e6, 1, 5))
    e7 = num(A.e7)
    x["univ"] = np.where(e7.between(1, 7), e7.isin([6, 7]).astype(float),
                         np.nan)
    x["no_sabe"] = np.where(e7.between(1, 7) | (e7 == 88),
                            (e7 == 88).astype(float), np.nan)
    otras = pd.concat([si(A[f"g13_{i}"]) for i in range(2, 10)], axis=1)
    x["otras_drogas"] = otras.max(axis=1, skipna=True).where(
        otras.notna().any(axis=1))
    g6, g8 = si(A.g6), si(A.g8)
    x["sin_anticonc"] = (1 - g8).where(g6 == 1)
    x["sueno"] = rango(A.tot_hrs_sueno_sem, 3, 14)
    x["celular_noche"] = zg(rango(A.a8_e, 1, 4))
    x["redes"] = zg(rango(A.a4, 1, 7))
    x["deporte"] = rango(A.a2, 0, 7)
    x["lectura"] = zg(rango(A.a7, 1, 7))
    x["chatarra"] = rango(A.a10_h, 0, 7)
    x["fruta"] = rango(A.a11, 0, 10)
    f2 = pd.concat([rango(A[f"f2_{i}"], 1, 5) for i in range(1, 9)], axis=1)
    x["supervision"] = zg(f2.mean(axis=1).where(f2.notna().sum(axis=1) >= 6))
    x["relacion_cuid"] = zg(rango(A.f5_1, 1, 5))
    x["confia_nadie"] = num(A.f1_9).where(num(A.f1_9).isin([0, 1]))
    ft = pd.concat([si(A[f"f{i}"]) for i in range(7, 12)], axis=1)
    x["tiempo_familia"] = ft.sum(axis=1).where(ft.notna().all(axis=1))
    a99 = num(A.a1a_99)
    x["participa"] = (1 - a99).where(a99.isin([0, 1]))

    E, _ = pyreadstat.read_dta("data/interim/2024/Base evaluaciones Stata.dta")
    E["folio"] = num(E.folio).astype("int64")
    E = E.drop_duplicates("folio").set_index("folio")
    x["cbcl_int"] = zg(num(E.cbcl2_pt_inter_i))
    x["cbcl_ext"] = zg(num(E.cbcl2_pt_inter_e))
    x["cbcl_aten"] = zg(num(E.cbcl2_pt_inter_6))
    x["tvip"] = zg(num(E.tvip_pst_hispano))
    aces = pd.concat([si(E[f"aces_{i}"]) for i in range(1, 11)], axis=1)
    x["aces"] = aces.sum(axis=1).where(aces.notna().sum(axis=1) >= 8)
    for i, k in ((2, "aces_peleas"), (3, "aces_separacion"),
                 (5, "aces_vivienda"), (7, "aces_hambre")):
        x[k] = si(E[f"aces_{i}"])
    x["cesd"] = zg(num(E.rs_cesd))
    x["psi_total"] = zg(num(E.psi_ts))
    x["psi_malestar"] = zg(num(E.psi_pd))
    x["psi_interaccion"] = zg(num(E.psi_p_cdi))
    x["pscs"] = zg(num(E.pscs_t))

    R, _ = pyreadstat.read_dta(
        "data/interim/2024/Base responsable principal Stata.dta",
        usecols=["folio", "ytotal_pc"])
    R["folio"] = num(R.folio).astype("int64")
    R = R.drop_duplicates("folio").set_index("folio")
    y = num(R.ytotal_pc)
    x["log_ingreso"] = np.log(y.where(y > 0))

    x = x.reset_index()
    return d.merge(x, on="folio", how="left")


# (variable, etiqueta, dirección: +1 si más alto es peor)
PANELES = {
    "b1": ("Exploratory outcomes I: mental health and well-being.",
           "tab:explora1",
           [("Panel A: Mental health", [
               ("z_phq4", "PHQ-4 symptoms (z)", 1),
               ("gad2_bin", "Positive anxiety screen, GAD-2 (0/1)", 1),
               ("phq2_bin", "Positive depression screen, PHQ-2 (0/1)", 1),
               ("cbcl_int", "Internalizing problems, CBCL (z)", 1),
               ("cbcl_ext", "Externalizing problems, CBCL (z)", 1),
               ("cbcl_aten", "Attention problems, CBCL (z)", 1)]),
            ("Panel B: Well-being", [
               ("z_resil", "Resilience (z)", -1),
               ("sat_vida", "Satisfaction with life in general (z)", -1),
               ("sat_familia", "Satisfaction with family life (z)", -1),
               ("sat_amigos", "Satisfaction with friends (z)", -1),
               ("sat_colegio", "Satisfaction with school (z)", -1),
               ("sat_si_mismo", "Satisfaction with oneself (z)", -1),
               ("sat_barrio", "Satisfaction with the neighborhood (z)", -1),
               ("sat_cuerpo", "Satisfaction with one's body (z)", -1),
               ("z_salud", "Poor self-rated health (z)", 1)]),
            ]),
    "b2": ("Exploratory outcomes II: cognition, school and peers.",
           "tab:explora2",
           [("Panel A: Cognition and school", [
               ("tvip", "Vocabulary, TVIP (z)", -1),
               ("asiste", "Attends school (0/1)", -1),
               ("nota", "Grade average last year (1--7)", -1),
               ("le_va", "Doing well at school (z)", -1),
               ("gusta", "Likes going to school (z)", -1),
               ("profes", "Likes the teachers (z)", -1),
               ("univ", "Expects a university degree (0/1)", -1),
               ("no_sabe", "Does not know how far they will study (0/1)",
                1)]),
            ("Panel B: Peers and victimization", [
               ("z_bull", "Peer victimization and class climate (z)", 1),
               ("ciber_any", "Cyber-victimization, last 12 months (0/1)", 1),
               ("viol_pareja", "Dating violence, ever dated (0/1)", 1)])]),
    "b3": ("Exploratory outcomes III: risk behaviors and daily life.",
           "tab:explora3",
           [("Panel A: Risk behaviors", [
               ("fuma", "Smoked tobacco, last 12 months (0/1)", 1),
               ("alcohol", "Drank alcohol, last 12 months (0/1)", 1),
               ("cannabis", "Used cannabis, last 12 months (0/1)", 1),
               ("otras_drogas", "Used other drugs, last 12 months (0/1)", 1),
               ("sin_anticonc", "No contraception at last sex (0/1)", 1)]),
            ("Panel B: Daily life", [
               ("sueno", "Hours of sleep on weekdays", -1),
               ("celular_noche", "Stays up on the phone in bed (z)", 1),
               ("redes", "Time on social media (z)", 1),
               ("deporte", "Days of physical activity, last week", -1),
               ("lectura", "Time reading (z)", -1),
               ("chatarra", "Days eating junk food, last week", 1),
               ("fruta", "Portions of fruit per day", -1)])]),
    "b4": ("Exploratory outcomes IV: family, adversity, caregiver and "
           "household.",
           "tab:explora4",
           [("Panel A: Family and social life", [
               ("supervision", "Parental knowledge of activities (z)", -1),
               ("relacion_cuid", "Relationship with main caregiver (z)", -1),
               ("confia_nadie", "Confides in nobody (0/1)", 1),
               ("tiempo_familia", "Activities with family, last week "
                                  "(0--5)", -1),
               ("participa", "Takes part in a group or organization (0/1)",
                -1)]),
            ("Panel B: Adverse experiences reported by the caregiver", [
               ("aces", "Number of adverse experiences (0--10)", 1),
               ("aces_peleas", "Witnessed fights at home (0/1)", 1),
               ("aces_separacion", "Abrupt separation from caregiver (0/1)",
                1),
               ("aces_vivienda", "Housing problems (0/1)", 1),
               ("aces_hambre", "Not enough to eat (0/1)", 1)]),
            ("Panel C: Caregiver and household", [
               ("cesd", "Caregiver depressive symptoms, CES-D (z)", 1),
               ("psi_total", "Parenting stress, PSI total (z)", 1),
               ("psi_malestar", "Parental distress, PSI (z)", 1),
               ("psi_interaccion", "Dysfunctional interaction, PSI (z)", 1),
               ("pscs", "Parenting sense of competence (z)", -1),
               ("log_ingreso", "Log household income per capita", -1)])]),
}
EDADES = [("12-23m", "Age 1"), ("24-35m", "Age 2"), ("36-59m", "Ages 3--4")]

ES = {
    "z_phq4": "Síntomas PHQ-4 (z)",
    "gad2_bin": "Tamizaje de ansiedad positivo, GAD-2",
    "phq2_bin": "Tamizaje de depresión positivo, PHQ-2",
    "cbcl_int": "Problemas internalizantes, CBCL (z)",
    "cbcl_ext": "Problemas externalizantes, CBCL (z)",
    "cbcl_aten": "Problemas de atención, CBCL (z)",
    "z_resil": "Resiliencia (z)",
    "sat_vida": "Satisfacción con la vida en general (z)",
    "sat_familia": "Satisfacción con la vida familiar (z)",
    "sat_amigos": "Satisfacción con los amigos (z)",
    "sat_colegio": "Satisfacción con el colegio (z)",
    "sat_si_mismo": "Satisfacción consigo mismo (z)",
    "sat_barrio": "Satisfacción con el barrio (z)",
    "sat_cuerpo": "Satisfacción con el propio cuerpo (z)",
    "z_salud": "Mala salud autopercibida (z)",
    "tvip": "Vocabulario, TVIP (z)",
    "asiste": "Asiste a un establecimiento",
    "nota": "Promedio de notas del año pasado (1–7)",
    "le_va": "Le va bien en el colegio (z)",
    "gusta": "Le gusta ir al colegio (z)",
    "profes": "Le agradan los profesores (z)",
    "univ": "Espera un título universitario",
    "no_sabe": "No sabe hasta dónde estudiará",
    "z_bull": "Victimización y clima del curso (z)",
    "ciber_any": "Ciberacoso, últimos 12 meses",
    "viol_pareja": "Violencia en el pololeo",
    "fuma": "Fumó tabaco, últimos 12 meses",
    "alcohol": "Bebió alcohol, últimos 12 meses",
    "cannabis": "Consumió marihuana, últimos 12 meses",
    "otras_drogas": "Consumió otras drogas, últimos 12 meses",
    "sin_anticonc": "Sin anticonceptivo en la última relación",
    "sueno": "Horas de sueño entre semana",
    "celular_noche": "Se queda con el celular en la cama (z)",
    "redes": "Tiempo en redes sociales (z)",
    "deporte": "Días de actividad física, última semana",
    "lectura": "Tiempo de lectura (z)",
    "chatarra": "Días con comida chatarra, última semana",
    "fruta": "Porciones de fruta al día",
    "supervision": "La familia sabe lo que hace (z)",
    "relacion_cuid": "Relación con el cuidador principal (z)",
    "confia_nadie": "No le cuenta sus problemas a nadie",
    "tiempo_familia": "Actividades con la familia (0–5)",
    "participa": "Participa en algún grupo u organización",
    "aces": "Número de experiencias adversas (0–10)",
    "aces_peleas": "Presenció peleas en el hogar",
    "aces_separacion": "Separación abrupta del cuidador",
    "aces_vivienda": "Problemas de vivienda",
    "aces_hambre": "No tuvo suficiente para comer",
    "cesd": "Síntomas depresivos del cuidador, CES-D (z)",
    "psi_total": "Estrés parental, PSI total (z)",
    "psi_malestar": "Malestar parental, PSI (z)",
    "psi_interaccion": "Interacción disfuncional, PSI (z)",
    "pscs": "Competencia parental percibida (z)",
    "log_ingreso": "Log del ingreso per cápita del hogar",
}
DOM_ES = {
    "Mental health": "SALUD MENTAL",
    "Well-being": "BIENESTAR",
    "Cognition and school": "COGNICIÓN Y COLEGIO",
    "Peers and victimization": "PARES Y VICTIMIZACIÓN",
    "Risk behaviors": "CONDUCTAS DE RIESGO",
    "Daily life": "VIDA COTIDIANA",
    "Family and social life": "FAMILIA Y VIDA SOCIAL",
    "Adverse experiences reported by the caregiver":
        "EXPERIENCIAS ADVERSAS (REPORTA EL CUIDADOR)",
    "Caregiver and household": "CUIDADOR Y HOGAR",
}


def estima(d):
    res = {}
    for clave, (_, _, paneles) in PANELES.items():
        for _, filas in paneles:
            for v, lab, sgn in filas:
                r = fit(d, v, 3)
                res[v] = {"r": r, "lab": lab, "sgn": sgn,
                          "media": d.loc[d[v].notna(), v].mean()}
                cel = " | ".join(
                    f"{e} {r['b'][k][0]:+.3f}{stars(r['b'][k][2])}"
                    for k, e in EDADES)
                log(f"- {v:16} media {res[v]['media']:8.3f} | {cel} | "
                    f"N={r['n']}")
    return res


def tabla(clave, res):
    titulo, etiqueta, paneles = PANELES[clave]
    L = []
    for ptit, filas in paneles:
        L.append(f"\\multicolumn{{6}}{{@{{}}l}}{{\\textbf{{\\textit{{{ptit}}}}}}}"
                 " \\\\")
        for v, lab, _ in filas:
            r, m = res[v]["r"], res[v]["media"]
            m = 0.0 if abs(m) < 0.0005 else m
            L.append(f"{lab} & "
                     + " & ".join(bcell(r["b"][k][0], r["b"][k][2])
                                  for k, _ in EDADES)
                     + f" & {fnum(m, 2 if abs(m) >= 1 else 3)} & "
                     f"{r['n']:,} \\\\")
            L.append(" & " + " & ".join(secell(r["b"][k][1])
                                        for k, _ in EDADES) + " & & \\\\")
        L.append("\\addlinespace[5pt]")
    L = L[:-1]
    notes = (
        "\\textit{Notes}: Each row is a separate regression of "
        "equation~(1) with the controls of column 3 of "
        "Table~\\ref{tab:main}. Columns 1 to 3 report the coefficient on "
        "exposure at the age named in the column interacted with the "
        "affected zone, relative to exposure at 0--11 months; column 4 "
        "reports the sample mean of the outcome. The design identifies "
        "differences across exposure ages, not the level of the effect, "
        "so a flat row is consistent both with no effect and with an "
        "effect common to all exposure ages. Variables marked (z) are "
        "standardized; Appendix Tables~\\ref{tab:a_mh} "
        "to~\\ref{tab:a_pscs} list the items behind every index. "
        "Standard errors clustered by "
        "municipality of selection appear in parentheses. The estimates "
        "use sampling weights. * p $<$ 0.1, ** p $<$ 0.05, "
        "*** p $<$ 0.01.")
    W = "460pt"
    nombre = {"b1": "b1_explora_salud", "b2": "b2_explora_escuela",
              "b3": "b3_explora_conducta", "b4": "b4_explora_familia"}[clave]
    lines = ([f"% ---- begin paper/tables/{nombre}.tex",
              "\\begin{table}[htbp]\\centering",
              f"\\begin{{minipage}}{{{W}}}",
              f"\\caption{{{titulo}}}",
              f"\\label{{{etiqueta}}}",
              "{\\footnotesize\\renewcommand{\\arraystretch}{0.92}",
              f"\\begin{{tabular*}}{{{W}}}"
              "{@{}p{200pt}@{\\extracolsep{\\fill}}lllll@{}}",
              "\\toprule",
              " & Age 1 & Age 2 & Ages 3--4 & Mean & Observations \\\\",
              " & (1) & (2) & (3) & (4) & (5) \\\\",
              "\\midrule"] + L + [
              "\\bottomrule",
              "\\end{tabular*}\\par}",
              "\\vspace{4pt}",
              "{\\footnotesize", notes, "\\par}",
              "\\end{minipage}",
              "\\end{table}",
              f"% ---- end paper/tables/{nombre}.tex"])
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / f"{nombre}.tex").write_text("\n".join(lines) + "\n",
                                       encoding="utf-8")
    print(f"-> paper/tables/{nombre}.tex")


def mapa(res, path):
    filas = []
    for clave in ("b1", "b2", "b3", "b4"):
        for ptit, fs in PANELES[clave][2]:
            filas.append(("panel", DOM_ES[ptit.split(": ", 1)[1]], None))
            for v, lab, sgn in fs:
                filas.append(("var", ES[v], v))
    n = len(filas)
    fig_h = 0.25 * n + 1.9
    fig, ax = plt.subplots(figsize=(9.6, fig_h), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    cmap = LinearSegmentedColormap.from_list(
        "dano", ["#2a78d6", "#f1f0ec", "#eb6834"])
    for i, (tipo, lab, v) in enumerate(filas):
        yy = n - 1 - i
        if tipo == "panel":
            ax.text(-0.08, yy, lab, ha="right", va="center",
                    fontsize=8.6, fontweight="bold", color="#52514e")
            continue
        ax.text(-0.08, yy, lab, ha="right", va="center", fontsize=8.6,
                color="#0b0b0b")
        r, sgn = res[v]["r"], res[v]["sgn"]
        for j, (k, _) in enumerate(EDADES):
            b, se, p = r["b"][k]
            t = np.clip(sgn * b / se, -3, 3)
            ax.add_patch(plt.Rectangle((j, yy - 0.42), 0.94, 0.84,
                                       color=cmap((t + 3) / 6)))
            st = stars(p)
            if st:
                ax.text(j + 0.47, yy, st, ha="center", va="center",
                        fontsize=9, color="#0b0b0b", fontweight="bold")
    for j, (_, e) in enumerate(EDADES):
        ax.text(j + 0.47, n - 0.2, e.replace("--", "–").replace(
            "Ages", "3–4 años").replace("Age 1", "1 año").replace(
            "Age 2", "2 años").replace(" 3–4", ""), ha="center",
            va="bottom", fontsize=9.5, fontweight="bold", color="#0b0b0b")
    ax.set_xlim(-0.1, 2.95)
    ax.set_ylim(-0.7, n + 0.4)
    ax.axis("off")
    fig.suptitle("Qué más difiere según la edad al terremoto",
                 x=0.02, ha="left", fontsize=13.5, fontweight="bold",
                 y=0.995)
    fig.text(0.02, 1 - 0.62 / fig_h,
             "Cada celda compara esa edad con los expuestos a 0–11 meses. "
             "Naranja = peor, azul = mejor\n(estadístico t orientado, "
             "saturado en ±3). Estrellas: * p<0,1, ** p<0,05, *** p<0,01.",
             fontsize=8.8, color="#52514e", ha="left", va="top")
    fig.subplots_adjust(left=0.47, right=0.99, top=1 - 1.25 / fig_h,
                        bottom=0.01)
    fig.savefig(path, dpi=160, facecolor="#fcfcfb")
    plt.close(fig)


def main():
    d = construye()
    log("# Análisis exploratorio, ola 2024 (scripts/19_exploratorio.py)")
    log("Coeficientes relativos a los expuestos a 0-11 meses; spec col. 3.")
    res = estima(d)
    ps = [res[v]["r"]["b"][k][2] for v in res for k, _ in EDADES]
    log(f"\nCoeficientes: {len(ps)}; p<0.10: {sum(p < .1 for p in ps)} "
        f"(esperados por azar {0.1 * len(ps):.0f}); p<0.05: "
        f"{sum(p < .05 for p in ps)} (esperados {0.05 * len(ps):.0f}); "
        f"p<0.01: {sum(p < .01 for p in ps)} (esperados "
        f"{0.01 * len(ps):.1f})")
    for clave in PANELES:
        tabla(clave, res)
    mapa(res, "reports/exploratorio_mapa.png")
    Path("reports/exploratorio.md").write_text("\n".join(OUT) + "\n",
                                               encoding="utf-8")
    print("-> reports/exploratorio_mapa.png, reports/exploratorio.md")


if __name__ == "__main__":
    main()
