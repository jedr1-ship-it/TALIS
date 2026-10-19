#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tablas del apéndice de la presentación (presentacion/advisor.tex), en el
formato de la AER: el outcome arriba en multicolumna, coeficiente con su
error estándar entre paréntesis (sin asteriscos, como pide la AER),
observaciones, efectos fijos y controles. Los outcomes están estandarizados,
así que no se reporta su media en el grupo de referencia. Ancho fijo
(\anchotabla, lo fija la diapositiva). Una tabla por
diapositiva con gráfico de coeficientes, con la misma especificación que el
gráfico:

  a1  PHQ-4 por edad al terremoto, todos, chicas y chicos (diapositiva 6;
      scripts/33_ventanas.py, grupos del paper)
  a2  los seis indicadores del entorno de 2010, chicas (diapositiva 7;
      scripts/35_canal_hogar.py)
  a3  PHQ-4 de las hijas y estrés de la madre según la lactancia, con dos
      robusteces (diapositiva 8; scripts/34_estres_madre.py, sección 5)
  a4  las medias de la diapositiva 8: madres con estrés y niños que tomaban
      pecho, por edad al terremoto (reports/estres_madre.csv)
  a5  síntomas, CBCL, consumo y victimización, chicas (diapositiva 9;
      scripts/36_chicos.py); a6, lo mismo para los chicos

Comprueba que cada coeficiente coincide con el que dibuja el gráfico.

Salida: presentacion/tablas/a1.tex ... a6.tex
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
          ("12-23", "1 year $\\times$ Affected"),
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


def bloque_edades(res):
    """Filas de coeficientes por grupo de edad; res: lista de (b, n, r, x)."""
    lineas = []
    for t, lab in EDADES:
        lineas.append(fila(lab, [coef(r[0][t][0]) for r in res]))
        lineas.append(fila("", [ee(r[0][t][1]) for r in res]))
        lineas.append("\\addlinespace[2pt]")
    return lineas[:-1]


def pie_perfil(res):
    k = len(res)
    return [fila("Observations", [f"{r[1]:,}" for r in res]),
            fila("Municipality FE", ["Yes"] * k),
            fila("Birth-cohort FE", ["Yes"] * k),
            fila("Age-group FE", ["Yes"] * k),
            fila("Controls", ["Yes"] * k)]


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
    guarda("a1.tex", tabla(["All", "Girls", "Boys"], bloque_edades(res),
                           pie_perfil(res), [("PHQ-4 (SD)", 3)]))


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
    guarda("a2.tex", tabla(cab, bloque_edades(res), pie_perfil(res),
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
           fila("Birth-cohort FE", ["Yes"] * 3),
           fila("Age-group FE", ["Yes"] * 3),
           fila("Age group $\\times$ breastfed FE", ["Yes"] * 3),
           fila("Controls", ["Yes"] * 3),
           fila("Stress and breastfed $\\times$ mother's education and "
                "employment", ["No", "Yes", "Yes"]),
           fila("Stress $\\times$ 6--11 months", ["No", "No", "Yes"])]
    guarda("a3.tex", tabla(["Baseline", "\\shortstack{Mother's\\\\SES}",
                            "\\shortstack{Mother's SES\\\\and infancy}"],
                           cuerpo, pie, [("Daughters' PHQ-4 (SD)", 3)]))


# ------------------------------------------- a4: medias de la diapositiva 8

def a4():
    c = pd.read_csv("reports/estres_madre.csv")
    niv = c[c.panel == "nivel"].set_index(["tramo", "zona"])
    pec = c[c.panel == "pecho"].set_index("tramo")
    nombres = {"6-11": "6--11 months", "12-23": "1 year", "24-35": "2 years",
               "36-49": "3--4 years"}
    cuerpo = []
    for t, lab in nombres.items():
        a, n = niv.loc[(t, "afectada")], niv.loc[(t, "no afectada")]
        cuerpo += [fila(lab, [f"{100 * a.b:.1f}", f"{100 * n.b:.1f}",
                              f"{100 * pec.loc[t, 'b']:.1f}"]),
                   fila("", [f"({100 * a.se:.1f})", f"({100 * n.se:.1f})",
                             ""]),
                   "\\addlinespace[2pt]"]
    pie = [fila("Children", [f"{int(niv.xs('afectada', level='zona').n.sum()):,}",
                             f"{int(niv.xs('no afectada', level='zona').n.sum()):,}",
                             f"{int(pec.n.sum()):,}"])]
    guarda("a4.tex", tabla(["Affected", "Unaffected", "On 27-F"],
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
    for g, sx, nombre in (("chicas", 1, "a5.tex"), ("chicos", 0, "a6.tex")):
        res = [p33.perfil(d, y, sx, "paper", modelo=True) for y in ys]
        for y, r in zip(ys, res):
            igual(r[0]["6-11"][0], ch[(ch.resultado == y) & (ch.grupo == g)
                                      & (ch.tramo == "6-11")].b.iloc[0],
                  f"a5 {g} {y}")
        guarda(nombre, tabla(cab, bloque_edades(res), pie_perfil(res),
                             [("Adolescent report (SD)", 3),
                              ("Caregiver report, CBCL (SD)", 2)]))


def main():
    a1()
    a2()
    a3()
    a4()
    a5()


if __name__ == "__main__":
    main()
