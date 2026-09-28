#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apéndice del paper — instrumentos: cada indicador con su pregunta VERBATIM
(español original del cuestionario) y su escala de respuesta, leídos de los
metadatos de los microdatos (etiquetas de variable y de valores).

Salida: paper/tables/a1_mh.tex … a5_birth.tex (entornos {table} completos,
        formato del WP de la Jornada; macros definidos en paper/tablas.tex).
Uso:    python3 scripts/16_apendice_instrumentos.py
"""
import re
import warnings
from pathlib import Path

import pyreadstat

warnings.simplefilter("ignore")
INT = Path("data/interim")
TAB = Path("paper/tables")

F24 = INT / "2024/Base adolescentes Stata.dta"
F10 = INT / "2010/Entrevistada_2010.dta"
F12 = INT / "2012/Entrevistada_2012.dta"


def esc(s):
    s = str(s)
    for a, b in [("\\", " "), ("&", "\\&"), ("%", "\\%"), ("#", "\\#"),
                 ("_", "\\_"), ("$", "\\$"), ("~", " "), ("^", " "),
                 ("¿", "?`"), ("¡", "!`")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def meta(path):
    _, m = pyreadstat.read_dta(str(path), metadataonly=True)
    return m


def question(m, var):
    raw = m.column_names_to_labels.get(var) or var
    lab = raw
    # quita prefijos tipo "d4_1. ", "g9:1.", "b55o_madre:" repetidos
    lab = re.sub(r"^[a-z0-9_]+[.:]\s*", "", lab, flags=re.I)
    lab = re.sub(r"^[a-z0-9_]+[.:]\s*", "", lab, flags=re.I)
    lab = esc(lab)
    # Stata corta las etiquetas a 80 caracteres: se marca el truncado
    if len(raw) >= 79 and not lab.rstrip().endswith(("?", ".", ")")):
        lab += "\\,\\dots"
    return lab


UNITS = {"g24": "kilograms", "g23": "centimeters", "g20": "weeks",
         "g25b1": "score 0--10"}


def scale(m, var, maxlev=8):
    vl = m.variable_value_labels.get(var)
    unit = UNITS.get(var)
    if not vl:
        return f"Open numeric answer ({unit})" if unit else \
            "Open numeric answer"
    items = sorted(vl.items(), key=lambda kv: kv[0])
    if unit is None and len(items) == 1:
        return "Marked = yes; not marked = no"
    out = []
    for k, v in items:
        v = esc(v)
        v = re.sub(r"^\d+\s*[=.]\s*", "", v)   # "1. Nunca" -> "Nunca"
        if len(v) > 34:
            v = v[:32] + "\\dots"
        kk = int(k) if float(k).is_integer() else k
        out.append(f"{kk} = {v}")
        if len(out) >= maxlev:
            out.append("\\dots")
            break
    s = "; ".join(out)
    if unit:
        s = f"Open numeric answer ({unit}); special codes: " + s
    return s


def rows_for(m, code_vars, hspace=True):
    rows = []
    for v in code_vars:
        if v not in m.column_names:
            continue
        pre = "\\hspace{1em}" if hspace else ""
        rows.append(f"{pre}\\texttt{{{esc(v)}}} & {question(m, v)} & "
                    f"{scale(m, v)} \\\\")
        rows.append("\\addlinespace[1pt]")
    if rows:
        rows = rows[:-1]
    return rows


def table_env(fname, caption, label, header, body, notes):
    lines = [f"% ---- begin paper/tables/{fname}.tex",
             "\\begin{table}[htbp]\\centering",
             f"\\caption{{{caption}}}",
             f"\\label{{{label}}}",
             "\\footnotesize\\renewcommand{\\arraystretch}{1.0}",
             "\\begin{threeparttable}",
             "\\begin{tabular}{@{}p{68pt}p{212pt}p{150pt}@{}}",
             "\\toprule"] + header + ["\\midrule"] + body + [
             "\\bottomrule", "\\end{tabular}",
             "\\begin{wpnotes}",
             "\\textit{Notes:} " + notes,
             "\\end{wpnotes}",
             "\\end{threeparttable}",
             "\\end{table}",
             f"% ---- end paper/tables/{fname}.tex"]
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / f"{fname}.tex").write_text("\n".join(lines) + "\n",
                                      encoding="utf-8")
    print(f"-> paper/tables/{fname}.tex ({len(body)} filas)")


HEAD = [" & Question, verbatim & Response scale \\\\",
        " & (1) & (2) \\\\"]
VERB = ("Question wording and response labels are reproduced verbatim in "
        "the original Spanish of the questionnaire, from the variable and "
        "value labels of the public microdata; wording the microdata "
        "truncates at 80 characters is marked with an ellipsis.")


def a1(m24):
    body = (["\\panel{3}{Panel A. PHQ-4, answered by the adolescent in "
             "private (2024 wave)}"]
            + rows_for(m24, [f"d4_{i}" for i in (1, 2, 3, 4)])
            + ["\\addlinespace",
               "\\panel{3}{Panel B. Caregiver-reported behavior}",
               "\\hspace{1em}\\texttt{cbcl2} & Child Behavior Checklist, "
               "internalizing scale, answered by the main caregiver about "
               "the adolescent; the survey releases the computed T score, "
               "not the copyrighted items. & T score, standardized in the "
               "analysis \\\\"])
    notes = (VERB + " The PHQ-4 score used in the paper is the sum of the "
             "four items rescaled to 0--3 each (0--12 in total) and "
             "standardized within age in years. The positive PHQ-2 "
             "(depression) and GAD-2 (anxiety) screens are the "
             "survey-provided indicators for a subscore of three or more "
             "on the corresponding pair of items.")
    table_env("a1_mh", "Mental-Health Instruments: Items and Scales",
              "tab:a_mh", HEAD, body, notes)


def a2(m24):
    body = (["\\panel{3}{Panel A. Resilience: Brief Resilience Scale "
             "(items 2, 4 and 6 reverse-coded)}"]
            + rows_for(m24, [f"d2_{i}" for i in range(1, 7)])
            + ["\\addlinespace",
               "\\panel{3}{Panel B. Life satisfaction and self-rated "
               "health}"]
            + rows_for(m24, ["d3_1", "d1"]))
    notes = (VERB + " The resilience score is the mean of the six items "
             "after reverse-coding items 2, 4 and 6, standardized; life "
             "satisfaction and self-rated health are standardized, the "
             "latter with its sign reversed in the analysis so that "
             "higher values mean worse health.")
    table_env("a2_wellbeing",
              "Well-Being Outcomes: Items and Scales", "tab:a_wellbeing",
              HEAD, body, notes)


def a3(m24):
    body = (["\\panel{3}{Panel A. School bullying (frequency scale; "
             "standardized mean; item g1\\_3 reverse-coded)}"]
            + rows_for(m24, [f"g1_{i}" for i in range(1, 9)])
            + ["\\addlinespace",
               "\\panel{3}{Panel B. Cyber-victimization, last 12 months "
               "(any item)}"]
            + rows_for(m24, [f"g2_{i}" for i in range(1, 9)])
            + ["\\addlinespace",
               "\\panel{3}{Panel C. Dating violence, among adolescents "
               "who ever dated (any item)}"]
            + rows_for(m24, ["g9_1", "g9_2", "g9_3"])
            + ["\\addlinespace",
               "\\panel{3}{Panel D. Substance use, last 12 months}"]
            + rows_for(m24, ["g11"] + [f"g12_{i}" for i in (1, 2, 3, 4)]
                       + ["g13_1"]))
    notes = (VERB + " Drank alcohol is one if any of the four beverage "
             "items is answered yes; cyber-victimization is one if any "
             "of the listed items is answered yes.")
    table_env("a3_conducta",
              "Victimization and Risk-Behavior Outcomes: Items and Scales",
              "tab:a_other", HEAD, body, notes)


def a4(m10, m12):
    body = (["\\panel{3}{Panel A. Reported by the mother in 2010, about "
             "the pregnancy and postpartum of the sampled child}"]
            + rows_for(m10, ["g4a_1", "g4a_3", "g4a_7", "g4b", "g19"])
            + ["\\addlinespace",
               "\\panel{3}{Panel B. Reported by the caregiver in 2012}"]
            + rows_for(m12, ["b64", "b55o_madre", "b55p_madre"]))
    notes = (VERB + " A mother is vulnerable in "
             "Table~\\ref{tab:mother} if any Panel A item is answered "
             "yes. The 2012 items enter the family mental-health "
             "controls of the main specification.")
    table_env("a4_madre",
              "Maternal Mental-Health Questions: Items and Scales",
              "tab:a_mother", HEAD, body, notes)


def a5(m10):
    body = rows_for(m10, ["g24", "g23", "g20", "g17_6", "g25b1"],
                    hspace=False)
    notes = (VERB + " Cleaning: birth weight kept between 0.5 and 6.5 "
             "kilograms, length between 30 and 65 centimeters, "
             "gestation between 24 and 45 weeks, Apgar between 0 and "
             "10; the survey codes 99 for a forgotten answer, treated "
             "as missing. All five outcomes are fixed at birth, one to "
             "four years before the earthquake for every cohort of the "
             "analysis sample.")
    table_env("a5_nacimiento",
              "Placebo Outcomes Fixed at Birth: Items and Scales",
              "tab:a_birth", HEAD, body, notes)


def main():
    m24, m10, m12 = meta(F24), meta(F10), meta(F12)
    a1(m24)
    a2(m24)
    a3(m24)
    a4(m10, m12)
    a5(m10)


if __name__ == "__main__":
    main()
