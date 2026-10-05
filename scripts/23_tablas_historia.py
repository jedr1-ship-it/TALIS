#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Las tres tablas que sostienen la historia del Overview, con el formato de
la Table 5 (heterogeneidad):

  t13_especificidad.tex  perfil por edad de los síntomas y del vocabulario
  t14_lactancia.tex      zona afectada x tomaba pecho el 27-F, con placebos
  t15_hogar.tex          peleas y disciplina dura en 2012, 2017 y 2024

Todas usan la ecuación (1) con los controles de la columna 3 de la
Table 3 y los bebés de 0-11 meses como grupo omitido, salvo la Table de
lactancia, que estima la interacción dentro de cada grupo de edad.

Salida: paper/tables/t13_especificidad.tex, t14_lactancia.tex, t15_hogar.tex
Uso:    python3 scripts/23_tablas_historia.py
"""
import importlib.util
import warnings
from pathlib import Path

import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p22", HERE / "22_figuras_presentacion.py")
p22 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p22)
p15 = p22.p15
fit, bcell, secell, stars, xt = (p15.fit, p15.bcell, p15.secell, p15.stars,
                                 p15.xt)
TAB = Path("paper/tables")
W = "460pt"
CHICAS = lambda x: x.mujer == 1
NOTA_FIN = ("Standard errors clustered by municipality of selection appear "
            "in parentheses. The estimates use sampling weights. "
            "* p $<$ 0.1, ** p $<$ 0.05, *** p $<$ 0.01.")


def escribe(fname, caption, label, colspec, header, body, notes):
    lines = (["% ---- begin paper/tables/" + fname + ".tex",
              "\\begin{table}[htbp]\\centering",
              f"\\begin{{minipage}}{{{W}}}",
              f"\\caption{{{caption}}}",
              f"\\label{{{label}}}",
              "{\\small",
              f"\\begin{{tabular*}}{{{W}}}{{{colspec}}}",
              "\\toprule"] + header + ["\\midrule"] + body + [
              "\\bottomrule",
              "\\end{tabular*}\\par}",
              "\\vspace{4pt}",
              "{\\footnotesize", "\\textit{Notes}: " + notes, "\\par}",
              "\\end{minipage}",
              "\\end{table}",
              "% ---- end paper/tables/" + fname + ".tex"])
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / f"{fname}.tex").write_text("\n".join(lines) + "\n",
                                      encoding="utf-8")
    print(f"-> paper/tables/{fname}.tex")


def panel(n, titulo):
    return (f"\\multicolumn{{{n}}}{{@{{}}l}}"
            f"{{\\textbf{{\\textit{{{titulo}}}}}}} \\\\")


def filas(lab, celdas):
    return [f"{lab} & " + " & ".join(bcell(b, p) for b, se, p in celdas)
            + " \\\\",
            " & " + " & ".join(secell(se) for b, se, p in celdas) + " \\\\"]


def bins(res):
    out = []
    for k, lab in p15.ROWLAB.items():
        out += filas(lab, [r["b"][k] for r in res])
        out.append("\\addlinespace[3pt]")
    return out


def t13_especificidad(d):
    cols = [(y, s) for s in (None, CHICAS)
            for y in ("z_phq4", "neg_tvip", "dif_dano")]
    res = [fit(d, y, 3, sample=s) for y, s in cols]
    for (y, s), r in zip(cols, res):
        print("T13", y, "chicas" if s else "todos",
              {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in r["b"].items()},
              f"contr {r['contr'][0]:+.3f}{stars(r['contr'][2])}")
    body = bins(res) + filas("Ages 3--4 $-$ age 2",
                             [r["contr"] for r in res])
    body += ["\\addlinespace[6pt]",
             "Observations & " + " & ".join(f"{r['n']:,}" for r in res)
             + " \\\\",
             "\\addlinespace[6pt]"]
    tick = " & ".join(["\\checkmark"] * 6) + " \\\\"
    body += ["Municipality FE & " + tick, "Birth Cohort FE & " + tick,
             "Pre-earthquake controls & " + tick, "2012 controls & " + tick]
    header = [" & \\multicolumn{3}{@{}l}{All adolescents} & "
              "\\multicolumn{3}{@{}l}{Girls} \\\\",
              "\\cmidrule(r){2-4}\\cmidrule(l){5-7}",
              " & PHQ-4 & Vocabulary & Difference & PHQ-4 & Vocabulary & "
              "Difference \\\\",
              " & index & deficit & & index & deficit & \\\\",
              " & (1) & (2) & (3) & (4) & (5) & (6) \\\\"]
    notes = (
        "Each column represents a separate regression of equation~(1) "
        "with the controls of column 3 of Table~\\ref{tab:main}. The "
        "PHQ-4 index is in standard deviations, so that higher values mean "
        "more symptoms. The vocabulary deficit is the 2024 TVIP score, the "
        "Spanish version of the Peabody picture vocabulary test, in "
        "standard deviations and with its sign reversed, so that higher "
        "values also mean more harm. The outcome of columns 3 and 6 is "
        "the PHQ-4 index minus the vocabulary deficit, and a coefficient "
        "different from zero in these columns means that the age profile "
        "of the earthquake differs between mental health and vocabulary. "
        "Coefficients compare each exposure-age group with the children "
        "exposed at 0--11 months, and the contrast row compares exposure "
        "at ages 3--4 with exposure at age 2. " + NOTA_FIN)
    escribe("t13_especificidad",
            "The age profile of the earthquake in mental health and in "
            "vocabulary at ages 15--18.",
            "tab:specific",
            "@{}l@{\\extracolsep{\\fill}}llllll@{}", header, body, notes)


def lactancia(d, binl, y, sexo=None, simple=False):
    """Zona afectada x tomaba pecho el 27-F dentro de un grupo de edad."""
    bb = d[d.bin == binl].dropna(subset=["meses_pecho", y, "w", "estrato",
                                         "cohorte"])
    if sexo is not None:
        bb = bb[bb.mujer == sexo]
    bb = bb[bb.w > 0].copy()
    bb["est"] = bb.estrato.astype(int).astype(str)
    bb["coh"] = bb.cohorte.astype(int).astype(str)
    bb["pecho"] = (bb.meses_pecho >= bb.edadq_m).astype(float)
    bb["EQxpecho"] = bb.EQ * bb.pecho
    rhs = ["EQxpecho", "pecho", "C(est)"]
    if not simple:
        rhs += ["C(coh)"] + xt(bb, p15.X_PRE) + xt(bb, p15.X_POST)
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=bb, weights=bb.w).fit(
        cov_type="cluster", cov_kwds={"groups": bb.est})
    g = lambda v: (float(r.params[v]), float(r.bse[v]), float(r.pvalues[v]))
    return {"int": g("EQxpecho"), "main": g("pecho"), "n": int(r.nobs),
            "share": float(bb.pecho.mean())}


def t14_lactancia(d):
    a = [lactancia(d, "0-11m", "z_phq4"),
         lactancia(d, "0-11m", "z_phq4", sexo=1),
         lactancia(d, "0-11m", "gad2_bin"),
         lactancia(d, "12-23m", "z_phq4"),
         lactancia(d, "24-35m", "z_phq4")]
    b = [lactancia(d, "0-11m", "z_peso"),
         lactancia(d, "0-11m", "z_talla"),
         lactancia(d, "0-11m", "z_gest"),
         lactancia(d, "0-11m", "z_educ_madre", simple=True),
         lactancia(d, "0-11m", "z_edad_madre", simple=True)]
    for lab, rr in (("A", a), ("B", b)):
        print("T14", lab, [f"{r['int'][0]:+.3f}{stars(r['int'][2])}"
                           for r in rr])
    body = [panel(6, "Panel A: Mental health at ages 15--18"),
            " & Infants & Infant girls & Infants & Age 1 & Age 2 \\\\",
            " & PHQ-4 & PHQ-4 & GAD-2 & PHQ-4 & PHQ-4 \\\\",
            "\\addlinespace[3pt]"]
    body += filas("Affected $\\times$ breastfed on 27-F",
                  [r["int"] for r in a])
    body += filas("Breastfed on 27-F", [r["main"] for r in a])
    body += ["\\addlinespace[3pt]",
             "Share breastfed on 27-F & "
             + " & ".join(f"{r['share']:.2f}" for r in a) + " \\\\",
             "Observations & " + " & ".join(f"{r['n']:,}" for r in a)
             + " \\\\",
             "\\addlinespace[9pt]",
             panel(6, "Panel B: Placebo, outcomes fixed before the "
                      "earthquake, infants"),
             " & Birth & Birth & Gestation & Mother's & Mother's \\\\",
             " & weight & length & weeks & schooling & age \\\\",
             "\\addlinespace[3pt]"]
    body += filas("Affected $\\times$ breastfed on 27-F",
                  [r["int"] for r in b])
    body += ["\\addlinespace[3pt]",
             "Observations & " + " & ".join(f"{r['n']:,}" for r in b)
             + " \\\\"]
    header = [" & (1) & (2) & (3) & (4) & (5) \\\\"]
    notes = (
        "Each column represents a separate regression on one exposure-age "
        "group, infants being the children exposed at 6--11 months. "
        "Breastfed on 27-F equals one if, according to the mother in 2012, "
        "the child was still breastfed in the month of the earthquake, and "
        "the coefficient of interest is its interaction with living in an "
        "affected municipality. Panel A and columns 1 to 3 of Panel B "
        "include municipality and birth-cohort fixed effects and the "
        "controls of column 3 of Table~\\ref{tab:main}; columns 4 and 5 of "
        "Panel B include only municipality fixed effects, since their "
        "outcome is itself a control. The PHQ-4 index and the Panel B "
        "outcomes are in standard deviations, and the GAD-2 screen is a "
        "probability. Among the children exposed at age 2, only 14 "
        "percent were still breastfed, a highly selected group. "
        + NOTA_FIN)
    escribe("t14_lactancia",
            "Breastfeeding on the day of the earthquake and mental health "
            "at ages 15--18.",
            "tab:breast",
            "@{}l@{\\extracolsep{\\fill}}lllll@{}", header, body, notes)


def t15_hogar(d):
    ys = ["peleas17", "grito12", "amenaza12", "pega12", "grito17",
          "golpes17", "peleas24"]
    body = []
    for titulo, s in (("Panel A: All adolescents", None),
                      ("Panel B: Girls", CHICAS)):
        res = [fit(d, y, 3, sample=s) for y in ys]
        for y, r in zip(ys, res):
            print("T15", titulo[:7], y,
                  {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in r["b"].items()})
        body += [panel(8, titulo)] + bins(res)
        body += ["Observations & " + " & ".join(f"{r['n']:,}" for r in res)
                 + " \\\\", "\\addlinespace[9pt]"]
    body = body[:-1]
    base = d.dropna(subset=["peleas17", "peleas24"])
    r0 = fit(base, "z_phq4", 3, sample=CHICAS)
    r1 = fit(base, "z_phq4", 3, sample=CHICAS,
             extra_x=["peleas17", "peleas24"])
    b0, b1 = r0["b"]["24-35m"][0], r1["b"]["24-35m"][0]
    print(f"T15 mediación chicas: {b0:+.3f} -> {b1:+.3f}")
    header = [" & \\multicolumn{6}{@{}l}{Mother or main caregiver} & "
              "Adolescent \\\\",
              "\\cmidrule(r){2-7}\\cmidrule(l){8-8}",
              " & Fights & Yells & Threatens & Hits & Yelled, & Shook & "
              "Fights \\\\",
              " & at home & & & & insulted & or hit & at home \\\\",
              " & 2017 & 2012 & 2012 & 2012 & 2017 & 2017 & 2024 \\\\",
              " & (1) & (2) & (3) & (4) & (5) & (6) & (7) \\\\"]
    notes = (
        "Each column represents a separate regression of equation~(1) "
        "with the controls of column 3 of Table~\\ref{tab:main}, and every "
        "outcome is a probability. Columns 1 and 7 equal one if the child "
        "witnessed fights or threats among household members, as reported "
        "by the main caregiver in 2017 and by the adolescent in 2024. "
        "Columns 2 to 4 come from the mother's report in 2012 of how she "
        "reacts when the child misbehaves, and equal one if she yells, "
        "threatens or hits the child at least sometimes. Columns 5 and 6 "
        "come from the main caregiver's report in 2017, and equal one if "
        "he or she yelled at, insulted or threatened the child (column 5) "
        "or shook, slapped or hit the child (column 6). In the sample of "
        "girls with both reports of fights, controlling for them moves the "
        f"PHQ-4 coefficient of exposure at age 2 from {b0:.3f} to "
        f"{b1:.3f}. " + NOTA_FIN).replace("from -", "from $-$").replace(
            "to -", "to $-$")
    escribe("t15_hogar",
            "Conflict and harsh discipline at home, by age at exposure to "
            "the earthquake.",
            "tab:home",
            "@{}l@{\\extracolsep{\\fill}}lllllll@{}", header, body, notes)


def main():
    d = p22.carga()
    t13_especificidad(d)
    t14_lactancia(d)
    t15_hogar(d)


if __name__ == "__main__":
    main()
