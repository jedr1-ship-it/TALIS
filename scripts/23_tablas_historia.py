#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Las tres tablas que sostienen la historia del Overview, con el formato de
la Table 5 (heterogeneidad):

  t13_especificidad.tex  perfil por edad de los síntomas y del vocabulario
  t14_lactancia.tex      zona afectada x tomaba pecho el 27-F, con placebos
  t15_hogar.tex          peleas y disciplina dura en 2012, 2017 y 2024

Todas usan la ecuación (1) con los controles de la columna 3 de la
Table 3 y la comparación principal, 6-11 meses frente a todas las demás
edades (y, en la Table 13, también el perfil frente a los de 2-3 años). La
de lactancia es una triple diferencia en toda la muestra: zona afectada x
tomaba pecho el 27-F dentro de cada grupo de edad, con efectos fijos de
grupo de edad x pecho (la de scripts/43_triple_did.py).

Salida: paper/tables/t13_especificidad.tex, t14_lactancia.tex, t15_hogar.tex
Uso:    python3 scripts/23_tablas_historia.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
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
    """El perfil frente a los de 2-3 años."""
    out = []
    for k, lab in p15.ROWLAB2.items():
        out += filas(lab, [r["b2"][k] for r in res])
        out.append("\\addlinespace[3pt]")
    return out


def t13_especificidad(d):
    cols = [(y, s) for s in (None, CHICAS)
            for y in ("z_phq4", "neg_tvip", "dif_dano")]
    res = [fit(d, y, 3, sample=s) for y, s in cols]
    sol = [fit(d, y, 3, sample=s, solo=True) for y, s in cols]
    for (y, s), r, q in zip(cols, res, sol):
        print("T13", y, "chicas" if s else "todos",
              f"6-11 frente al resto {q['b']['0-11m'][0]:+.3f}"
              f"{stars(q['b']['0-11m'][2])}",
              {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in r["b2"].items()})
    body = ([panel(7, "Panel A: Relative to all other exposure ages")]
            + filas(p15.MAINLAB, [q["b"]["0-11m"] for q in sol])
            + ["\\addlinespace[6pt]",
               panel(7, "Panel B: Relative to exposure at 2--3 years")]
            + bins(res)[:-1])
    body += ["\\addlinespace[6pt]",
             "Observations & " + " & ".join(f"{r['n']:,}" for r in res)
             + " \\\\",
             "\\addlinespace[6pt]"]
    tick = " & ".join(["\\checkmark"] * 6) + " \\\\"
    body += ["Municipality FE & " + tick, "Birth-year FE & " + tick,
             "2010 baseline controls & " + tick, "2012 controls & " + tick]
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
        "Panel A compares the children exposed at 6--11 months with all "
        "other exposure ages, as in Panel A of Table~\\ref{tab:main}; Panel "
        "B compares each exposure-age group with the children exposed at "
        "2--3 years. " + NOTA_FIN)
    escribe("t13_especificidad",
            "The age profile of the earthquake in mental health and in "
            "vocabulary at ages 14--18.",
            "tab:specific",
            "@{}l@{\\extracolsep{\\fill}}llllll@{}", header, body, notes)


TRAMOS = {"0-11m": "6-11", "12-23m": "12-23", "24-35m": "24-35",
          "36-59m": "36-49"}


def triple(d, y, sexo=None, simple=False):
    """Triple diferencia en toda la muestra: para cada grupo de edad, zona
    afectada x tomaba pecho el 27-F (K) y tomaba pecho (P), con las
    interacciones de edad x zona, efectos fijos de grupo de edad, comuna y
    año de nacimiento y, salvo simple=True, los controles de la columna 3."""
    x = d.dropna(subset=["meses_pecho", y, "w", "estrato", "cohorte", "bin"])
    if sexo is not None:
        x = x[x.mujer == sexo]
    x = x[x.w > 0].copy()
    x["est"] = x.estrato.astype(int).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    x["pecho"] = (x.meses_pecho >= x.edadq_m).astype(float)
    rhs = []
    for b, t in TRAMOS.items():
        k = t.replace("-", "_")
        g = (x.bin == b).astype(float)
        x[f"K{k}"], x[f"P{k}"] = g * x.EQ * x.pecho, g * x.pecho
        rhs += [f"K{k}", f"P{k}"]
        if b != "24-35m":
            x[f"A{k}"] = g * x.EQ
            rhs.append(f"A{k}")
    rhs += ["C(bin)", "C(est)", "C(coh)"]
    if not simple:
        rhs += xt(x, p15.X_PRE) + xt(x, p15.X_POST)
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x.est})
    g = lambda v: (float(r.params[v]), float(r.bse[v]), float(r.pvalues[v]))
    return {b: {"int": g(f"K{t.replace('-', '_')}"),
                "main": g(f"P{t.replace('-', '_')}"),
                "share": float(x[x.bin == b].pecho.mean()),
                "nbf": int(x[x.bin == b].pecho.sum())}
            for b, t in TRAMOS.items()} | {"n": int(r.nobs)}


def solo_bebes(d, y, sexo=None):
    """La misma interacción estimada solo con los de 6-11 meses."""
    bb = d[d.bin == "0-11m"].dropna(subset=["meses_pecho", y, "w", "estrato",
                                            "cohorte"])
    if sexo is not None:
        bb = bb[bb.mujer == sexo]
    bb = bb[bb.w > 0].copy()
    bb["est"] = bb.estrato.astype(int).astype(str)
    bb["coh"] = bb.cohorte.astype(int).astype(str)
    bb["pecho"] = (bb.meses_pecho >= bb.edadq_m).astype(float)
    bb["EQxpecho"] = bb.EQ * bb.pecho
    rhs = (["EQxpecho", "pecho", "C(est)", "C(coh)"] + xt(bb, p15.X_PRE)
           + xt(bb, p15.X_POST))
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=bb, weights=bb.w).fit(
        cov_type="cluster", cov_kwds={"groups": bb.est})
    return float(r.params["EQxpecho"])


def t14_lactancia(d):
    todos, chicas = triple(d, "z_phq4"), triple(d, "z_phq4", sexo=1)
    gad = triple(d, "gad2_bin")
    a = [(todos, "0-11m"), (chicas, "0-11m"), (gad, "0-11m"),
         (todos, "12-23m"), (todos, "24-35m")]
    b = [triple(d, "z_peso"), triple(d, "z_talla"), triple(d, "z_gest"),
         triple(d, "z_educ_madre", simple=True),
         triple(d, "z_edad_madre", simple=True)]
    print("T14 A", [f"{r[k]['int'][0]:+.3f}{stars(r[k]['int'][2])}"
                    for r, k in a])
    print("T14 B", [f"{r['0-11m']['int'][0]:+.3f}"
                    f"{stars(r['0-11m']['int'][2])}" for r in b])
    s0, s1 = solo_bebes(d, "z_phq4"), solo_bebes(d, "z_phq4", sexo=1)
    body = [panel(6, "Panel A: Mental health at ages 14--18"),
            " & 6--11 months & 6--11 months & 6--11 months & 1--2 years & "
            "2--3 years \\\\",
            " & PHQ-4 & PHQ-4, girls & GAD-2 & PHQ-4 & PHQ-4 \\\\",
            "\\addlinespace[3pt]"]
    body += filas("Affected $\\times$ breastfed on 27-F",
                  [r[k]["int"] for r, k in a])
    body += filas("Breastfed on 27-F", [r[k]["main"] for r, k in a])
    body += ["\\addlinespace[3pt]",
             "Share breastfed on 27-F & "
             + " & ".join(f"{r[k]['share']:.2f}" for r, k in a) + " \\\\",
             "Observations & " + " & ".join(f"{r['n']:,}" for r, _ in a)
             + " \\\\",
             "\\addlinespace[9pt]",
             panel(6, "Panel B: Placebo, outcomes fixed before the "
                      "earthquake, exposed at 6--11 months"),
             " & Birth & Birth & Gestation & Mother's & Mother's \\\\",
             " & weight & length & weeks & schooling & age \\\\",
             "\\addlinespace[3pt]"]
    body += filas("Affected $\\times$ breastfed on 27-F",
                  [r["0-11m"]["int"] for r in b])
    body += ["\\addlinespace[3pt]",
             "Observations & " + " & ".join(f"{r['n']:,}" for r in b)
             + " \\\\"]
    header = [" & (1) & (2) & (3) & (4) & (5) \\\\"]
    notes = (
        "Triple-difference estimates on the full sample. For each "
        "exposure-age group, the coefficient of interest is the "
        "interaction of living in an affected municipality with being "
        "breastfed on 27-F, which compares the gap between affected and "
        "unaffected municipalities among the breastfed with the same gap "
        "among the children who were not; the column heading names the "
        "group reported. Breastfed on 27-F equals one if, according to the "
        "mother in 2012, the child was still breastfed in the month of the "
        "earthquake, and the regressions include its interaction with each "
        "exposure-age group, the exposure-age interactions of "
        "equation~(1), and exposure-age, municipality and birth-year fixed "
        "effects. Panel A and columns 1 to 3 of Panel B add the controls of "
        "column 3 of Table~\\ref{tab:main}; columns 4 and 5 of Panel B do "
        "not, since their outcome is itself a control. The PHQ-4 index and "
        "the Panel B outcomes are in standard deviations, and the GAD-2 "
        "screen is a probability. Estimated on the children exposed at "
        f"6--11 months alone, the interaction for the PHQ-4 is {s0:.3f} "
        f"(column 1) and {s1:.3f} (column 2). Among the children exposed "
        "at 2--3 years, only 14 percent were still breastfed, a highly "
        "selected group. " + NOTA_FIN)
    escribe("t14_lactancia",
            "Breastfeeding on the day of the earthquake and mental health "
            "at ages 14--18.",
            "tab:breast",
            "@{}l@{\\extracolsep{\\fill}}lllll@{}", header, body, notes)


def t15_hogar(d):
    ys = ["peleas17", "grito12", "amenaza12", "pega12", "grito17",
          "golpes17", "peleas24"]
    body = []
    for titulo, s in (("Panel A: All adolescents", None),
                      ("Panel B: Girls", CHICAS)):
        res = [fit(d, y, 3, sample=s, solo=True) for y in ys]
        for y, r in zip(ys, res):
            v = r["b"]["0-11m"]
            print("T15", titulo[:7], y, f"{v[0]:+.3f}{stars(v[2])}")
        body += ([panel(8, titulo)]
                 + filas(p15.MAINLAB, [r["b"]["0-11m"] for r in res])
                 + ["\\addlinespace[3pt]"])
        body += ["Observations & " + " & ".join(f"{r['n']:,}" for r in res)
                 + " \\\\", "\\addlinespace[9pt]"]
    body = body[:-1]
    base = d.dropna(subset=["peleas17", "peleas24"])
    r0 = fit(base, "z_phq4", 3, sample=CHICAS, solo=True)
    r1 = fit(base, "z_phq4", 3, sample=CHICAS, solo=True,
             extra_x=["peleas17", "peleas24"])
    b0, b1 = r0["b"]["0-11m"][0], r1["b"]["0-11m"][0]
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
        "Each column represents a separate regression with the "
        "specification of Panel A of Table~\\ref{tab:main}, which compares "
        "the children exposed at 6--11 months with all other exposure "
        "ages, and every outcome is a probability. Columns 1 and 7 equal one if the child "
        "witnessed fights or threats among household members, as reported "
        "by the main caregiver in 2017 and by the adolescent in 2024. "
        "Columns 2 to 4 come from the mother's report in 2012 of how she "
        "reacts when the child misbehaves, and equal one if she yells, "
        "threatens or hits the child at least sometimes. Columns 5 and 6 "
        "come from the main caregiver's report in 2017, and equal one if "
        "he or she yelled at, insulted or threatened the child (column 5) "
        "or shook, slapped or hit the child (column 6). In the sample of "
        "girls with both reports of fights, controlling for them moves the "
        f"PHQ-4 coefficient of exposure at 6--11 months from {b0:.3f} to "
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
