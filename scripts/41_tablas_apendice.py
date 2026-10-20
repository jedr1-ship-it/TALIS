#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tablas del apéndice de la presentación (presentacion/advisor.tex), en el
formato de la AER: el outcome arriba en multicolumna, coeficiente con su
error estándar entre paréntesis (sin asteriscos, como pide la AER),
observaciones, una fila por efecto fijo y controles. Los outcomes están
estandarizados, así que no se reporta su media en el grupo de referencia.
Ancho fijo (\\anchotabla, lo fija la diapositiva). Una tabla por
diapositiva, con la misma especificación que el gráfico:

  desc     descriptivas de la muestra, todos y por sexo (diapositiva 4)
  balance  balance en lo fijado antes del terremoto, chicas, y el PHQ-4 con
           controles al nacer (diapositiva 5; scripts/33_ventanas.py)
  atricion responder en 2024 y peso al nacer en la línea base de 2010
           (diapositiva 5; scripts/42_balance_atricion.py)
  phq4     PHQ-4: panel A, 6-11 meses frente a todas las demás edades
           (scripts/45_contraste.py); panel B, perfil frente a 2-3 años;
           todos, chicas, chicos y chicas con efectos fijos de mes de
           nacimiento (diapositiva 6)
  entorno  los seis indicadores del entorno de 2010, chicas (diapositiva 7;
           scripts/35_canal_hogar.py)
  lactancia  el efecto de 6-11 meses según la lactancia el 27-F, chicas y
           chicos (diapositiva 8; scripts/45_contraste.py)
  diada    PHQ-4 de las hijas y estrés de la madre según la lactancia, con
           dos robusteces (diapositiva 8; scripts/34_estres_madre.py, 5)
  medias   las medias de la diapositiva 8: madres con estrés y niños que
           tomaban pecho, por edad al terremoto (reports/estres_madre.csv)
  chicas, chicos  síntomas, CBCL, consumo y victimización (diapositiva 9;
           scripts/36_chicos.py)

Comprueba que cada coeficiente coincide con el que dibuja el gráfico.

Salida: presentacion/tablas/*.tex
Uso:    python3 scripts/41_tablas_apendice.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
OUTD = Path("presentacion/tablas")


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p33 = modulo("p33", "33_ventanas.py")
p15 = p33.p15
EDADES = [("6-11", "6--11 months $\\times$ Affected"),
          ("12-23", "1--2 years $\\times$ Affected"),
          ("36-49", "3--4 years $\\times$ Affected")]


def coef(b):
    return f"{b:.3f}".replace("-", "$-$")


def ee(se):
    return f"({se:.3f})"


def fila(etiqueta, celdas):
    return f"{etiqueta} & " + " & ".join(celdas) + " \\\\"


def tabla(cabecera, cuerpo, pie, arriba):
    """cabecera: nombres de columna; arriba: (outcome, nº de columnas) para la
    fila de multicolumna; cuerpo y pie: líneas ya armadas. El ancho lo da
    \\anchotabla."""
    k = len(cabecera)
    celdas, reglas, j = [], [], 2
    for etiqueta, n in arriba:
        celdas.append(f"\\multicolumn{{{n}}}{{c}}{{{etiqueta}}}")
        reglas.append(f"\\cmidrule(lr){{{j}-{j + n - 1}}}")
        j += n
    return "\n".join(
        ["\\begin{tabular*}{\\anchotabla}{@{\\extracolsep{\\fill}}l"
         f"*{{{k}}}{{c}}@{{}}}}", "\\toprule",
         " & " + " & ".join(celdas) + " \\\\", " ".join(reglas),
         fila("", [f"({i + 1})" for i in range(k)]),
         fila("", cabecera), "\\midrule", *cuerpo, "\\midrule", *pie,
         "\\bottomrule", "\\end{tabular*}"]) + "\n"


def bloque_edades(res, edades=EDADES):
    """Filas de coeficientes por grupo de edad; res: lista de (b, n, r, x)."""
    lineas = []
    for t, lab in edades:
        lineas.append(fila(lab, [coef(r[0][t][0]) for r in res]))
        lineas.append(fila("", [ee(r[0][t][1]) for r in res]))
        lineas.append("\\addlinespace[2pt]")
    return lineas[:-1]


def paneles(res_a, res_b):
    """Panel A: 6-11 meses frente a todas las demás edades; panel B: el
    perfil frente a 2-3 años. Misma muestra y especificación."""
    k = len(res_a) + 1
    return ([f"\\multicolumn{{{k}}}{{@{{}}l}}{{\\emph{{Panel A. Relative "
             "to all other ages}} \\\\"]
            + bloque_edades(res_a, EDADES[:1])
            + ["\\addlinespace[3pt]",
               f"\\multicolumn{{{k}}}{{@{{}}l}}{{\\emph{{Panel B. Relative "
               "to ages 2--3}} \\\\"]
            + bloque_edades(res_b))


def contrastes(tipo, grupo=None):
    c = pd.read_csv("reports/contraste.csv")
    c = c[c.tipo == tipo]
    return c if grupo is None else c[c.grupo == grupo]


def pie_perfil(res, mes=None):
    """mes: columnas con efectos fijos de mes de nacimiento, que reemplazan
    a los de año de nacimiento y grupo de edad."""
    k = len(res)
    mes = mes or [False] * k
    si = lambda v: "Yes" if v else "No"           # noqa: E731
    pie = [fila("Observations", [f"{r[1]:,}" for r in res]),
           fila("Municipality FE", ["Yes"] * k),
           fila("Birth-year FE", [si(not m) for m in mes]),
           fila("Age-group FE", [si(not m) for m in mes])]
    if any(mes):
        pie.append(fila("Month-of-birth FE", [si(m) for m in mes]))
    return pie + [fila("Controls", ["Yes"] * k)]


def guarda(nombre, texto):
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / nombre).write_text(texto, encoding="utf-8")
    print(f"-> {OUTD / nombre}")


def igual(a, b, que):
    assert abs(a - b) < 1e-6, f"{que}: {a} != {b}"


# ------------------------------------------------- a1: PHQ-4, diapositiva 6

def a1():
    d, _, _ = p15.load_data()
    res = [p33.perfil(d, "z_phq4", sx, "paper", modelo=True)
           for sx in (None, 1, 0)]
    ch = pd.read_csv("reports/chicos.csv")
    for (g, r) in (("chicas", res[1]), ("chicos", res[2])):
        for t, _ in EDADES:
            igual(r[0][t][0], ch[(ch.resultado == "z_phq4") & (ch.grupo == g)
                                  & (ch.tramo == t)].b.iloc[0], f"a1 {g} {t}")
    res.append(p33.perfil(d, "z_phq4", 1, "paper", modelo=True, mes=True))
    # columna 5: el PGA (por 10 puntos de % de g) en lugar de la zona
    pga = d.assign(EQ=d.pga / 10)
    res.append(p33.perfil(pga, "z_phq4", 1, "paper", modelo=True))
    res_a = [p33.perfil(datos, "z_phq4", sx, "paper", modelo=True,
                        solo="6-11", **kw)
             for datos, sx, kw in ((d, None, {}), (d, 1, {}), (d, 0, {}),
                                   (d, 1, {"mes": True}), (pga, 1, {}))]
    grupos = ("todos", "chicas", "chicos", "chicas, mes", "chicas, PGA")
    c = contrastes("phq4").set_index("grupo")
    for g, r in zip(grupos, res_a):
        igual(r[0]["6-11"][0], c.loc[g, "b"], f"a1 contraste {g}")
    mes = [False] * 3 + [True, False]
    pie = pie_perfil(res, mes)
    pie[-1:-1] = [fila("Exposure", ["Zone"] * 4 + ["PGA"])]
    pie.append(fila("Wild bootstrap $p$-value, panel A",
                    [f"{c.loc[g, 'p_wild']:.3f}" for g in grupos]))
    guarda("phq4.tex", tabla(["All", "Girls", "Boys", "Girls", "Girls"],
                             paneles(res_a, res), pie,
                             [("PHQ-4 (SD)", 5)]))


# ---------------------------------------------- a2: entorno, diapositiva 7

def a2():
    p35 = modulo("p35", "35_canal_hogar.py")
    d = p35.carga()
    res = [p33.perfil(d, i, 1, "paper", modelo=True) for i in p35.INDICES]
    c = pd.read_csv("reports/canal_hogar.csv")
    c = c[(c.tipo == "perfil") & (c.grupo == "chicas")]
    for i, r in zip(p35.INDICES, res):
        for t, _ in EDADES:
            igual(r[0][t][0], c[(c.componente == i) & (c.tramo == t)]
                  .valor.iloc[0], f"a2 {i} {t}")
    cab = ["\\shortstack{Lower\\\\income}", "\\shortstack{Mother not\\\\employed}",
           "\\shortstack{Damaged\\\\housing}", "\\shortstack{Conflict\\\\at home}",
           "\\shortstack{Overcrowded\\\\housing}",
           "\\shortstack{Precarious\\\\housing}"]
    res_a = [p33.perfil(d, i, 1, "paper", modelo=True, solo="6-11")
             for i in p35.INDICES]
    c = contrastes("entorno").set_index("resultado")
    for i, r in zip(p35.INDICES, res_a):
        igual(r[0]["6-11"][0], c.loc[i, "b"], f"a2 contraste {i}")
    guarda("entorno.tex", tabla(cab, paneles(res_a, res), pie_perfil(res),
                           [("Mechanisms in Gillmore (2026), SD", 3),
                            ("Other household conditions, SD", 3)]))


# --------------------------------- a3: estrés y lactancia, diapositiva 8

def a3():
    p34 = modulo("p34", "34_estres_madre.py")
    d = p34.carga()
    x = d.dropna(subset=["z_phq4", "estres12", "pecho", "estrato", "w",
                         "cohorte"]).copy()
    x = x[(x.w > 0) & (x.mujer == 1)]
    x["est"] = x.estrato.astype(int).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    x["e_pecho"] = x.estres12 * x.pecho
    x["e_sin"] = x.estres12 * (1 - x.pecho)
    x["e_bebe"] = x.estres12 * (x.tramo == "6-11")
    fe = ["C(tramo)", "C(tramo):pecho", "pecho", "C(est)", "C(coh)"] \
        + p34.xt(x, p15.X_PRE) + p34.xt(x, p15.X_POST)

    def ajusta(datos, extra):
        r = smf.wls("z_phq4 ~ " + " + ".join(["e_sin", "e_pecho"] + extra
                                             + fe), data=datos,
                    weights=datos.w).fit(cov_type="cluster",
                                         cov_kwds={"groups": datos.est})
        t = r.t_test("e_pecho - e_sin")
        dif = (float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]),
               float(np.ravel(t.pvalue)[0]))
        return r, dif, datos.estrato.nunique()

    y = x.dropna(subset=["educ_madre10", "trabaja10"]).copy()
    y["e_educ"] = y.estres12 * (y.educ_madre10 - y.educ_madre10.mean())
    y["e_trab"] = y.estres12 * y.trabaja10
    y["p_educ"] = y.pecho * (y.educ_madre10 - y.educ_madre10.mean())
    y["p_trab"] = y.pecho * y.trabaja10
    res = [ajusta(x, []),
           ajusta(y, ["e_educ", "e_trab", "p_educ", "p_trab"]),
           ajusta(y, ["e_educ", "e_trab", "e_bebe", "p_educ", "p_trab"])]
    c = pd.read_csv("reports/estres_madre.csv")
    c = c[(c.panel == "lactancia") & (c.grupo == "chicas")].set_index("tramo")
    igual(res[0][0].params["e_sin"], c.loc["sin pecho", "b"], "a3 sin")
    igual(res[0][0].params["e_pecho"], c.loc["con pecho", "b"], "a3 con")
    cuerpo = []
    for k, lab in (("e_sin", "Maternal stress $\\times$ not breastfed"),
                   ("e_pecho", "Maternal stress $\\times$ breastfed")):
        cuerpo += [fila(lab, [coef(r.params[k])
                              for r, _, _ in res]),
                   fila("", [ee(r.bse[k]) for r, _, _ in res]),
                   "\\addlinespace[2pt]"]
    cuerpo += [fila("Difference, breastfed $-$ not breastfed",
                    [coef(dif[0]) for _, dif, _ in res]),
               fila("", [ee(dif[1]) for _, dif, _ in res])]
    pie = [fila("Observations", [f"{int(r.nobs):,}" for r, _, _ in res]),
           fila("Municipality FE", ["Yes"] * 3),
           fila("Birth-year FE", ["Yes"] * 3),
           fila("Age-group FE", ["Yes"] * 3),
           fila("Age group $\\times$ breastfed FE", ["Yes"] * 3),
           fila("Controls", ["Yes"] * 3),
           fila("Stress and breastfed $\\times$ mother's education and "
                "employment", ["No", "Yes", "Yes"]),
           fila("Stress $\\times$ 6--11 months", ["No", "No", "Yes"])]
    guarda("diada.tex", tabla(["Baseline", "\\shortstack{Mother's\\\\SES}",
                            "\\shortstack{Mother's SES\\\\and infancy}"],
                           cuerpo, pie, [("Daughters' PHQ-4 (SD)", 3)]))


# ------------------------- lactancia: el efecto de 6-11 meses, diapositiva 8

def lactancia():
    """El efecto de 6-11 meses frente a todas las demás edades, por
    separado para quienes tomaban pecho el 27-F y quienes no (los números
    de reports/contraste.csv, que calcula scripts/45_contraste.py)."""
    c = contrastes("pecho")
    cols = ["chicas", "chicas, SES", "chicos"]
    cuerpo = []
    for clave, lab in (("con pecho", "6--11 months $\\times$ Affected "
                        "$\\times$ breastfed"),
                       ("sin pecho", "6--11 months $\\times$ Affected "
                        "$\\times$ not breastfed"),
                       ("diferencia", "Difference, breastfed $-$ not "
                        "breastfed")):
        r = c[c.resultado == clave].set_index("grupo").loc[cols]
        cuerpo += [fila(lab, [coef(b) for b in r.b]),
                   fila("", [ee(se) for se in r.se]), "\\addlinespace[2pt]"]
    n = c[c.resultado == "diferencia"].set_index("grupo").loc[cols].n
    pw = c[c.resultado == "diferencia"].set_index("grupo").loc[cols].p_wild
    pie = [fila("Wild bootstrap $p$-value, difference",
                [f"{v:.3f}" for v in pw]),
           fila("Observations", [f"{int(v):,}" for v in n]),
           fila("Municipality FE", ["Yes"] * 3),
           fila("Birth-year FE", ["Yes"] * 3),
           fila("Age-group FE", ["Yes"] * 3),
           fila("Age group $\\times$ breastfed FE", ["Yes"] * 3),
           fila("Controls", ["Yes"] * 3),
           fila("Mother's education and employment $\\times$ breastfed "
                "and $\\times$ affected", ["No", "Yes", "No"])]
    guarda("lactancia.tex", tabla(["Girls", "Girls", "Boys"], cuerpo[:-1],
                                  pie, [("PHQ-4 (SD)", 3)]))


# ------------------------------------------- a4: medias de la diapositiva 8

def a4():
    c = pd.read_csv("reports/estres_madre.csv")
    niv = c[c.panel == "nivel"].set_index(["tramo", "zona"])
    pec = c[c.panel == "pecho"].set_index("tramo")
    nombres = {"6-11": "6--11 months", "12-23": "1--2 years", "24-35": "2--3 years",
               "36-49": "3--4 years"}
    cuerpo = []
    for t, lab in nombres.items():
        a, n = niv.loc[(t, "afectada")], niv.loc[(t, "no afectada")]
        cuerpo += [fila(lab, [f"{100 * a.b:.1f}", f"{100 * n.b:.1f}",
                              f"{100 * pec.loc[t, 'b']:.1f}"]),
                   fila("", [f"({100 * a.se:.1f})", f"({100 * n.se:.1f})",
                             ""]),
                   "\\addlinespace[2pt]"]
    pie = [fila("Observations", [f"{int(niv.xs('afectada', level='zona').n.sum()):,}",
                             f"{int(niv.xs('no afectada', level='zona').n.sum()):,}",
                             f"{int(pec.n.sum()):,}"])]
    guarda("medias.tex", tabla(["Affected", "Unaffected", "On 27-F"],
                           cuerpo[:-1], pie,
                           [("Mothers with stress (\\%)", 2),
                            ("Breastfed (\\%)", 1)]))


# ------------------------------------ a5 y a6: chicas y chicos, diapositiva 9

def a5():
    p36 = modulo("p36", "36_chicos.py")
    d = p36.p19.construye()
    c = d[["alcohol", "fuma", "cannabis", "otras_drogas"]]
    d["consumo"] = c.max(axis=1).where(c.notna().any(axis=1))
    d["z_consumo"] = (d.consumo - d.consumo.mean()) / d.consumo.std()
    ys = ["z_phq4", "z_consumo", "z_bull", "cbcl_int", "cbcl_ext"]
    cab = ["PHQ-4", "Substance use", "Victimization", "Internalizing",
           "Externalizing"]
    ch = pd.read_csv("reports/chicos.csv")
    for g, sx, nombre in (("chicas", 1, "chicas.tex"), ("chicos", 0, "chicos.tex")):
        res = [p33.perfil(d, y, sx, "paper", modelo=True) for y in ys]
        for y, r in zip(ys, res):
            igual(r[0]["6-11"][0], ch[(ch.resultado == y) & (ch.grupo == g)
                                      & (ch.tramo == "6-11")].b.iloc[0],
                  f"a5 {g} {y}")
        res_a = [p33.perfil(d, y, sx, "paper", modelo=True, solo="6-11")
                 for y in ys]
        c = contrastes("otros", g).set_index("resultado")
        for y, r in zip(ys, res_a):
            igual(r[0]["6-11"][0], c.loc[y, "b"], f"a5 contraste {g} {y}")
        guarda(nombre, tabla(cab, paneles(res_a, res), pie_perfil(res),
                             [("Adolescent report (SD)", 3),
                              ("Caregiver report, CBCL (SD)", 2)]))


# ------------------------------------- descriptivas de la muestra, diapo 4

def desc():
    """Media y DE de toda la muestra y medias por sexo, ponderadas; sin
    comparar zonas, que no es la comparación del diseño."""
    p34 = modulo("p34", "34_estres_madre.py")
    d = p34.carga()
    d = d[d.w > 0].copy()
    d["phq4_alto"] = (d.phq4_score >= 6).astype(float).where(
        d.phq4_score.notna())
    d["edad_ent"] = d.edad_meses / 12
    filas = [("Panel A. Adolescent, 2024", None),
             ("PHQ-4 score (0--12)", "phq4_score"),
             ("PHQ-4 of 6 or more (share)", "phq4_alto"),
             ("Age in August 2024 (years)", "edad_ent"),
             ("Age at the earthquake (months)", "edadq_m"),
             ("Affected municipality (share)", "EQ"),
             ("Panel B. Birth and household, 2010", None),
             ("Birth weight (kg)", "peso_nacer"),
             ("Gestation (weeks)", "sem_gest"),
             ("Mother's age (years)", "edad_madre10"),
             ("Mother's education (years)", "educ_madre10"),
             ("Household size", "tot_per10"),
             ("Rural (share)", "rural10"),
             ("Panel C. After the earthquake, 2012", None),
             ("Breastfed on 27-F (share)", "pecho"),
             ("Mother reported stress (share)", "estres12")]

    def media(x, v):
        x = x.dropna(subset=[v])
        return np.average(x[v], weights=x.w)

    cuerpo = []
    for lab, v in filas:
        if v is None:
            if cuerpo:
                cuerpo.append("\\addlinespace[3pt]")
            cuerpo.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{lab}}}}} \\\\")
            continue
        x = d.dropna(subset=[v])
        m = media(x, v)
        sd = np.sqrt(np.average((x[v] - m) ** 2, weights=x.w))
        cuerpo.append(fila(lab, [f"{m:.2f}", f"{sd:.2f}",
                                 f"{media(d[d.mujer == 1], v):.2f}",
                                 f"{media(d[d.mujer == 0], v):.2f}"]))
    pie = [fila("Adolescents", [f"{len(d):,}", "",
                                f"{int((d.mujer == 1).sum()):,}",
                                f"{int((d.mujer == 0).sum()):,}"])]
    guarda("desc.tex", tabla(["Mean", "SD", "Girls", "Boys"], cuerpo, pie,
                             [("All", 2), ("Mean by sex", 2)]))


# ------------------------------------------ balance, diapositiva 5

def balance():
    d, _, _ = p15.load_data()
    ys = ["z_peso", "z_talla", "z_gest", "educ_madre10", "edad_madre10"]
    res = [p33.perfil(d, y, 1, "paper", controles=False, modelo=True)
           for y in ys]
    res_a = [p33.perfil(d, y, 1, "paper", controles=False, modelo=True,
                        solo="6-11") for y in ys]
    pie = [fila("Observations", [f"{r[1]:,}" for r in res]),
           fila("Municipality FE", ["Yes"] * 5),
           fila("Birth-year FE", ["Yes"] * 5),
           fila("Age-group FE", ["Yes"] * 5),
           fila("Controls", ["No"] * 5)]
    guarda("balance.tex", tabla(["Weight", "Length", "Gestation",
                                 "Education", "Age"],
                                paneles(res_a, res), pie,
                                [("At birth (SD)", 3),
                                 ("Mother, 2010 (years)", 2)]))
    # la misma muestra con y sin los controles al nacer: las chicas sin
    # registro de nacimiento cambian el coeficiente, los controles no
    nacer = ("z_peso", "z_talla", "z_gest")
    sin = p33.perfil(d.dropna(subset=list(nacer)), "z_phq4", 1, "paper",
                     solo="6-11")[0]["6-11"]
    con = p33.perfil(d, "z_phq4", 1, "paper", solo="6-11", extra=nacer)
    b, n = con[0]["6-11"], con[1]
    (OUTD / "balance_nota.tex").write_text(
        f"Among the {n:,} girls with birth records, the PHQ-4 coefficient "
        "for those exposed at 6--11 months, relative to all other ages, is "
        f"{sin[0]:.3f} ({sin[1]:.3f}) without and {b[0]:.3f} ({b[1]:.3f}) "
        "with the three birth outcomes as controls.\n", encoding="utf-8")
    print(f"-> {OUTD / 'balance_nota.tex'}")


# ------------------------------------------- atrición, diapositiva 5

def atricion():
    """Responder en 2024 por edad al terremoto y zona, y el peso al nacer de
    las chicas en toda la línea base y en quienes responden."""
    p42 = modulo("p42", "42_balance_atricion.py")
    res, x = p42.resultados()
    res_a, _ = p42.resultados(x.drop(columns=["tramo", "cohorte", "region"]
                                     + p42.II), solo=True)
    pie = [fila("Joint test, panel B, $p$-value",
                [f"{r[2]:.2f}" for r in res]),
           fila("Mean of dependent variable",
                [f"{r[3]:.2f}" for r in res[:3]] + ["", ""]),
           fila("Observations", [f"{r[1]:,}" for r in res]),
           fila("Region FE", ["Yes"] * 5),
           fila("Birth-year FE", ["Yes"] * 5),
           fila("Age-group FE", ["Yes"] * 5)]
    guarda("atricion.tex", tabla(
        ["Girls", "Boys", "All", "\\shortstack{2010\\\\baseline}",
         "\\shortstack{Interviewed\\\\in 2024}"],
        paneles(res_a, res), pie,
        [("Interviewed in 2024", 3), ("Birth weight, girls (SD)", 2)]))


def main():
    desc()
    balance()
    atricion()
    a1()
    lactancia()
    a2()
    a3()
    a4()
    a5()


if __name__ == "__main__":
    main()
