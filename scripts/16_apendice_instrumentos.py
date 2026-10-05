#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apéndice del paper — instrumentos: cada índice con sus preguntas VERBATIM
(español original del cuestionario) y su escala de respuesta, leídos de los
metadatos de los microdatos (etiquetas de variable y de valores). Cuando la
etiqueta no trae el enunciado (ítems de respuesta múltiple) o el instrumento
solo publica puntajes, la fila lo describe en inglés.

Salida: paper/tables/a*.tex (entornos {table} completos; macros definidos
        en paper/tablas.tex).
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
FEV = INT / "2024/Base evaluaciones Stata.dta"
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
    # quita prefijos tipo "d4_1. ", "g9:1.", "b55o_madre:", "CESD." repetidos
    lab = re.sub(r"^[a-z0-9_]+[.:]\s*", "", lab, flags=re.I)
    lab = re.sub(r"^[a-z0-9_]+[.:]\s*", "", lab, flags=re.I)
    lab = esc(lab)
    # Stata corta las etiquetas a 80 caracteres: se marca el truncado
    if 79 <= len(raw) <= 80 and not lab.rstrip().endswith(("?", ".", ")")):
        lab += "\\,\\dots"
    return lab


UNITS = {"g24": "kilograms", "g23": "centimeters", "g20": "weeks",
         "g25b1": "score 0--10", "a2": "days, 0--7", "a10_h": "days, 0--7",
         "a11": "portions per day", "b71": "number of children",
         "a8_a": "clock time", "a8_b": "clock time"}


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


def rows_for(m, code_vars, hspace=True, una_escala=False):
    rows = []
    primera = True
    for v in code_vars:
        if v not in m.column_names:
            continue
        pre = "\\hspace{1em}" if hspace else ""
        esc_v = scale(m, v) if (primera or not una_escala) else \
            "\\textit{Same scale}"
        primera = False
        rows.append(f"{pre}\\texttt{{{esc(v)}}} & {question(m, v)} & "
                    f"{esc_v} \\\\")
        rows.append("\\addlinespace[1pt]")
    if rows:
        rows = rows[:-1]
    return rows


def desc(var, texto, escala):
    return [f"\\hspace{{1em}}\\texttt{{{esc(var)}}} & {texto} & "
            f"{escala} \\\\"]


def table_env(fname, caption, label, header, body, notes, stretch="1.0"):
    lines = [f"% ---- begin paper/tables/{fname}.tex",
             "\\begin{table}[htbp]\\centering",
             f"\\caption{{{caption}}}",
             f"\\label{{{label}}}",
             f"\\footnotesize\\renewcommand{{\\arraystretch}}{{{stretch}}}",
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
PAN = "\\panel{3}"


def a1(m24):
    body = ([f"{PAN}{{Panel A. PHQ-4, answered by the adolescent in "
             "private (2024 wave)}"]
            + rows_for(m24, [f"d4_{i}" for i in (1, 2, 3, 4)])
            + ["\\addlinespace",
               f"{PAN}{{Panel B. Child Behavior Checklist, answered by the "
               "main caregiver about the adolescent}"]
            + desc("cbcl2", "Total problems scale. The survey releases the "
                   "computed scores, not the copyrighted items.",
                   "T score, standardized in the analysis")
            + desc("cbcl2\\_i", "Internalizing problems: the "
                   "anxious/depressed, withdrawn and somatic-complaints "
                   "syndrome scales.", "T score, standardized")
            + desc("cbcl2\\_e", "Externalizing problems: the rule-breaking "
                   "and aggressive-behavior syndrome scales.",
                   "T score, standardized")
            + desc("cbcl2\\_6", "Attention problems syndrome scale.",
                   "T score, standardized"))
    notes = (VERB + " The PHQ-4 score used in the paper is the sum of the "
             "four items rescaled to 0--3 each (0--12 in total) and "
             "standardized within age in years. The positive PHQ-2 "
             "(depression) and GAD-2 (anxiety) screens are the "
             "survey-provided indicators for a subscore of three or more "
             "on the corresponding pair of items.")
    table_env("a1_mh", "Mental-Health Instruments: Items and Scales",
              "tab:a_mh", HEAD, body, notes)


def a2(m24):
    body = ([f"{PAN}{{Panel A. Resilience: Brief Resilience Scale (all "
             "six items worded positively)}"]
            + rows_for(m24, [f"d2_{i}" for i in range(1, 7)], una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel B. Satisfaction, one item per domain, scale "
               "1 to 7}"]
            + rows_for(m24, [f"d3_{i}" for i in (6, 1, 2, 3, 4, 5, 7)],
                       una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel C. Self-rated health}}"]
            + rows_for(m24, ["d1"]))
    notes = (VERB + " The resilience score is the mean of the six items, "
             "standardized; the ELPI 2024 version words all six positively, "
             "unlike the original scale, so none is reverse-coded. Each "
             "satisfaction item is standardized on its own; life "
             "satisfaction is the item on life in general. Self-rated "
             "health is standardized with its sign reversed, so that "
             "higher values mean worse health.")
    table_env("a2_wellbeing", "Well-Being Outcomes: Items and Scales",
              "tab:a_wellbeing", HEAD, body, notes, stretch="0.95")


def a6(m24):
    body = ([f"{PAN}{{Panel A. Cognition, assessed by the interviewer}}"]
            + desc("tvip", "Test de Vocabulario en Im\\'agenes Peabody "
                   "(TVIP), the Spanish adaptation of the Peabody Picture "
                   "Vocabulary Test: receptive vocabulary.",
                   "Standard score on Hispanic norms, standardized")
            + ["\\addlinespace",
               f"{PAN}{{Panel B. School, answered by the adolescent}}"]
            + rows_for(m24, ["e1", "e3_asiste", "e2_asiste", "e5", "e6",
                             "e7"]))
    notes = (VERB + " Attendance is one when the adolescent attends an "
             "educational establishment. The grade average converts each "
             "range to its midpoint on the Chilean 1--7 scale; the items on "
             "how school goes, liking school and liking the teachers are "
             "standardized. The expected degree is one for a university "
             "degree or postgraduate studies, among adolescents who name a "
             "level; not knowing is one for answer 88.")
    table_env("a6_escuela", "Cognition and School: Items and Scales",
              "tab:a_school", HEAD, body, notes)


def a3(m24):
    body = ([f"{PAN}{{Panel A. Peer victimization and class climate "
             "(frequency scale; standardized mean; item g1\\_3 "
             "reverse-coded)}"]
            + rows_for(m24, [f"g1_{i}" for i in range(1, 9)], una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel B. Cyber-victimization, last 12 months (any "
               "item)}"]
            + rows_for(m24, [f"g2_{i}" for i in range(1, 7)], una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel C. Dating violence, among adolescents who "
               "ever dated (any item)}"]
            + rows_for(m24, ["g9_1", "g9_2", "g9_3"], una_escala=True))
    notes = (VERB + " Cyber-victimization is one if any of the listed "
             "items is answered yes. The dating-violence items are the "
             "options of a multiple-response question on the forms of "
             "violence suffered in a relationship; the indicator is one if "
             "any is marked.")
    table_env("a3_conducta", "Peers and Victimization: Items and Scales",
              "tab:a_other", HEAD, body, notes, stretch="0.95")


def a7(m24):
    body = ([f"{PAN}{{Panel A. Substance use, last 12 months}}"]
            + rows_for(m24, ["g11"] + [f"g12_{i}" for i in (1, 2, 3, 4)]
                       + [f"g13_{i}" for i in range(1, 10)], una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel B. Sexual behavior}}"]
            + rows_for(m24, ["g6", "g8"]))
    notes = (VERB + " Drank alcohol is one if any of the four beverage "
             "items is answered yes; cannabis is item g13\\_a alone, and "
             "other drugs is one if any of items g13\\_b to g13\\_i is "
             "answered yes. No contraception is one when no method was used "
             "at the last voluntary sexual relation, among adolescents who "
             "report one.")
    table_env("a7_riesgo", "Risk Behaviors: Items and Scales",
              "tab:a_risk", HEAD, body, notes, stretch="0.95")


def a8(m24):
    body = (rows_for(m24, ["a8_a", "a8_b", "a8_e", "a4", "a2", "a7",
                           "a10_h", "a11"], hspace=False))
    notes = (VERB + " Hours of sleep on weekdays are the survey's own "
             "computation from the waking and sleeping times (variable "
             "tot\\_hrs\\_sueno\\_sem), kept between 3 and 14. Staying up "
             "on the phone, time on social media and time reading are "
             "standardized; the days of physical activity and of junk food "
             "and the daily portions of fruit enter in their own units.")
    table_env("a8_vida", "Daily Life: Items and Scales", "tab:a_daily",
              HEAD, body, notes)


def a9(m24):
    body = ([f"{PAN}{{Panel A. Parental knowledge of the adolescent's "
             "activities (standardized mean of eight items)}"]
            + rows_for(m24, [f"f2_{i}" for i in range(1, 9)], una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel B. Relationships and time with the family}}"]
            + rows_for(m24, ["f5_1"])
            + rows_for(m24, [f"f{i}" for i in range(7, 12)], una_escala=True)
            + desc("f1\\_9", "Option ``Nadie'' (nobody) of a "
                   "multiple-response question on whom the adolescent tells "
                   "about their problems.", "Marked = 1; not marked = 0")
            + ["\\addlinespace",
               f"{PAN}{{Panel C. Social participation}}"]
            + desc("a1a\\_99", "Option ``No participa en ninguna "
                   "organizaci\\'on o grupo'' of a multiple-response "
                   "question listing sports clubs, religious, artistic, "
                   "civic and student groups.",
                   "Takes part = 1 when not marked"))
    notes = (VERB + " Parental knowledge is the mean of items f2\\_1 to "
             "f2\\_8 when at least six are answered. Activities with the "
             "family count the yes answers to items f7 to f11. The "
             "relationship with the main caregiver is standardized.")
    table_env("a9_familia", "Family and Social Life: Items and Scales",
              "tab:a_family", HEAD, body, notes, stretch="0.95")


def a10(mev):
    body = rows_for(mev, [f"aces_{i}" for i in range(1, 11)], hspace=False,
                    una_escala=True)
    notes = (VERB + " The main caregiver answers each item about the "
             "adolescent's whole life. The count adds the yes answers when "
             "at least eight items are answered.")
    table_env("a10_aces", "Adverse Experiences Reported by the Caregiver: "
              "Items and Scales", "tab:a_aces", HEAD, body, notes)


def a11(mev):
    body = ([f"{PAN}{{Panel A. Caregiver depressive symptoms, CES-D, ten "
             "items on the last week}"]
            + rows_for(mev, [f"cesd_p1{c}" for c in "abcdefghij"], una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel B. Parenting stress and household income}}"]
            + desc("psi", "Parenting Stress Index, short form, answered by "
                   "the caregiver: parental distress, dysfunctional "
                   "parent--child interaction and difficult child, twelve "
                   "items each. The survey releases the scores, not the "
                   "items.", "Total 36--180 and subscales 12--60, "
                   "standardized")
            + desc("ytotal\\_pc", "Total household income per capita in "
                   "the month before the interview, computed by the survey "
                   "from the income module.", "Chilean pesos; enters in "
                   "logs"))
    notes = (VERB + " The CES-D score is the survey's raw score (0--30, "
             "positive items reversed), standardized.")
    table_env("a11_cuidador", "Caregiver Measures I: Items and Scales",
              "tab:a_caregiver", HEAD, body, notes)


def a12(mev):
    body = rows_for(mev, [f"pscs_p{i}" for i in range(1, 18)],
                    hspace=False, una_escala=True)
    notes = (VERB + " Parenting Sense of Competence Scale, answered by the "
             "main caregiver; the analysis uses the survey's total score, "
             "standardized, with higher values meaning more competence.")
    table_env("a12_pscs", "Caregiver Measures II: Parenting Sense of "
              "Competence", "tab:a_pscs", HEAD, body, notes,
              stretch="0.92")


def a4(m12):
    body = ([f"{PAN}{{Panel A. Family history of mental illness, asked "
             "about the mother (2012)}"]
            + rows_for(m12, [f"b55{c}_madre" for c in "opqrst"], una_escala=True)
            + ["\\addlinespace",
               f"{PAN}{{Panel B. Number of children of the mother (2012)}}"]
            + rows_for(m12, ["b71"]))
    notes = (VERB + " The same six items are asked about the father "
             "(b55o\\_padre to b55t\\_padre) and about another relative "
             "(b55o\\_ofam to b55t\\_ofam). Each of the three indicators "
             "of family mental illness is one if any of the six "
             "conditions is reported, and the three enter the 2012 "
             "controls of the main specification together with the number "
             "of children.")
    table_env("a4_madre", "Family Mental-Health Controls: Items and Scales",
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
    m24, mev = meta(F24), meta(FEV)
    m10, m12 = meta(F10), meta(F12)
    a1(m24)
    a2(m24)
    a6(m24)
    a3(m24)
    a7(m24)
    a8(m24)
    a9(m24)
    a10(mev)
    a11(mev)
    a12(mev)
    a4(m12)
    a5(m10)


if __name__ == "__main__":
    main()
