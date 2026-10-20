#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tablas del apéndice de la presentación (presentacion/advisor.tex), en el
formato de la AER: el outcome arriba en multicolumna, coeficiente con su
error estándar entre paréntesis (sin asteriscos, como pide la AER),
observaciones, una fila por efecto fijo y controles. Los outcomes están
estandarizados, así que no se reporta su media en el grupo de referencia.
Ancho fijo (\\anchotabla, lo fija la diapositiva). Una tabla por
diapositiva, con la misma especificación que el gráfico.

El resultado principal es el perfil por edad al terremoto en tramos de seis
meses, centrado (suma cero), con la prueba conjunta de perfil plano. La
comparación resumen, elegida después de ver el perfil (exploratoria), es la
de los primeros 18 meses (6-17) frente a todas las demás edades, con
efectos fijos de tramo de seis meses (scripts/45_contraste.py). Cada tabla
da el coeficiente de esa comparación y el p-valor de la prueba de perfil
plano:

  desc     descriptivas de la muestra, todos y por sexo (datos)
  balance  balance en lo fijado antes del terremoto, chicas, y el PHQ-4 con
           controles al nacer (especificación)
  atricion responder en 2024 y peso al nacer en la línea base de 2010
           (especificación; scripts/42_balance_atricion.py)
  perfil   PHQ-4, el perfil centrado (scripts/47_perfil_completo.py); todos,
           chicas y chicos (perfil)
  phq4     los primeros 18 meses frente al resto: todos, chicas, chicos,
           chicas con efectos fijos de mes de nacimiento y chicas con el PGA
  chicas, chicos  síntomas, CBCL, consumo y victimización (perfil;
           scripts/36_chicos.py)
  olas     la misma comparación en tres rondas, cuidador y autorreporte
           (tres rondas; scripts/48_tres_olas.py)
  entorno  los seis indicadores del entorno de 2010, chicas (entorno;
           scripts/35_canal_hogar.py)
  lactancia  los primeros 18 meses según la lactancia el 27-F, chicas y
           chicos (lactancia)
  diada    PHQ-4 de las hijas y estrés de la madre según la lactancia, con
           dos robusteces (lactancia; scripts/34_estres_madre.py)
  medias   madres con estrés y niños que tomaban pecho, por tramo de seis
           meses (lactancia; scripts/34_estres_madre.py)

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
SEIS = p33.CORTES["seis"][1]
VENT = "6-17"
ETVENT = "6--17 months $\\times$ Affected"


def coef(b):
    b = 0.0 if round(b, 3) == 0 else b          # sin "-0.000"
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


def panel(k, texto):
    return f"\\multicolumn{{{k + 1}}}{{@{{}}l}}{{\\emph{{{texto}}}}} \\\\"


def ventana(d, y, sx=None, **kw):
    """Los primeros 18 meses x zona frente a todas las demás edades, con
    efectos fijos de tramo de seis meses: (b, n, r, x) de p33.perfil."""
    return p33.perfil(d, y, sx, "seis", modelo=True, solo=p33.VENTANA, **kw)


def centrado(d, y, sx=None, **kw):
    """El perfil en tramos de seis meses centrado: la brecha de cada tramo
    menos la media de los siete (la de 24-29 meses, la omitida, vale cero);
    y el p-valor de la prueba conjunta de perfil plano."""
    _, n, r, _ = p33.perfil(d, y, sx, "seis_ref", modelo=True, **kw)
    nombres = list(r.params.index)
    ii = [k for k in nombres if k[:1] == "I" and k[1:2].isdigit()]
    res = {}
    for t in SEIS:
        c = np.zeros(len(nombres))
        for k in ii:
            c[nombres.index(k)] -= 1 / len(SEIS)
        k = "I" + t.replace("-", "_")
        if k in ii:
            c[nombres.index(k)] += 1
        tt = r.t_test(c)
        res[t] = (float(np.ravel(tt.effect)[0]), float(np.ravel(tt.sd)[0]))
    p = float(r.f_test(", ".join(f"{k} = 0" for k in ii)).pvalue)
    return res, p, n


def filas_ventana(res):
    return [fila(ETVENT, [coef(r[0][VENT][0]) for r in res]),
            fila("", [ee(r[0][VENT][1]) for r in res])]


def pie_ventana(res, plano, mes=None, controles=True):
    """mes: columnas con efectos fijos de mes de nacimiento, que reemplazan
    a los de año de nacimiento y tramo de seis meses."""
    k = len(res)
    mes = mes or [False] * k
    si = lambda v: "Yes" if v else "No"           # noqa: E731
    pie = [fila("Flat profile, joint test $p$-value",
                [f"{p:.3f}" for p in plano]),
           fila("Observations", [f"{r[1]:,}" for r in res]),
           fila("Municipality FE", ["Yes"] * k),
           fila("Birth-year FE", [si(not m) for m in mes]),
           fila("Six-month age-group FE", [si(not m) for m in mes])]
    if any(mes):
        pie.append(fila("Month-of-birth FE", [si(m) for m in mes]))
    return pie + [fila("Controls", [si(controles)] * k)]


def contrastes(tipo, grupo=None):
    c = pd.read_csv("reports/contraste.csv")
    c = c[c.tipo == tipo]
    return c if grupo is None else c[c.grupo == grupo]


def guarda(nombre, texto):
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / nombre).write_text(texto, encoding="utf-8")
    print(f"-> {OUTD / nombre}")


def igual(a, b, que):
    assert abs(a - b) < 1e-6, f"{que}: {a} != {b}"


# ------------------------------------------------------ phq4: el perfil

def a1():
    d, _, _ = p15.load_data()
    pga = d.assign(EQ=d.pga / 10)     # el PGA, por 10 puntos de % de g
    specs = ((d, None, {}), (d, 1, {}), (d, 0, {}), (d, 1, {"mes": True}),
             (pga, 1, {}))
    grupos = ("todos", "chicas", "chicos", "chicas, mes", "chicas, PGA")
    res = [ventana(x, "z_phq4", sx, **kw) for x, sx, kw in specs]
    perf = [centrado(x, "z_phq4", sx, **kw) for x, sx, kw in specs]
    c = contrastes("phq4").set_index("grupo")
    for g, r, pf in zip(grupos, res, perf):
        igual(r[0][VENT][0], c.loc[g, "b"], f"a1 ventana {g}")
        igual(pf[1], c.loc[g, "p_plano"], f"a1 plano {g}")
    pc = pd.read_csv("reports/perfil_completo.csv")
    pc = pc[pc.parte == "seis"].set_index(["grupo", "tramo"])
    for g, pf in (("chicas", perf[1]), ("chicos", perf[2])):
        for t in SEIS:
            igual(pf[0][t][0], pc.loc[(g, t), "b"], f"a1 perfil {g} {t}")
    k = len(res)
    mes = [False] * 3 + [True, False]
    exposicion = fila("Exposure", ["Zone"] * 4 + ["PGA"])
    # el perfil: todos, chicas y chicos (las columnas 4 y 5, con efectos
    # fijos de mes de nacimiento y con el PGA, solo dan la prueba conjunta,
    # que va en la nota)
    cuerpo = []
    for t in SEIS:
        cuerpo += [fila(t.replace("-", "--") + " months",
                        [coef(pf[0][t][0]) for pf in perf[:3]]),
                   fila("", [ee(pf[0][t][1]) for pf in perf[:3]])]
    guarda("perfil.tex", tabla(["All", "Girls", "Boys"], cuerpo,
                               pie_ventana(res[:3],
                                           [pf[1] for pf in perf[:3]]),
                               [("PHQ-4 (SD)", 3)]))
    print(f"   perfil plano, chicas, mes de nacimiento p={perf[3][1]:.3f}, "
          f"PGA p={perf[4][1]:.3f}")
    # la comparación resumen: sin la fila de perfil plano, que está arriba
    pie = pie_ventana(res, [pf[1] for pf in perf], mes=mes)[1:]
    pie[:0] = [fila("Wild bootstrap $p$-value",
                    [f"{c.loc[g, 'p_wild']:.3f}" for g in grupos])]
    pie[-1:-1] = [exposicion]
    guarda("phq4.tex", tabla(["All", "Girls", "Boys", "Girls", "Girls"],
                             filas_ventana(res), pie, [("PHQ-4 (SD)", k)]))


# ---------------------------------------- chicas y chicos: otros resultados

def a5():
    c = contrastes("otros")
    ys = ["z_phq4", "z_consumo", "z_bull", "cbcl_int", "cbcl_ext"]
    cab = ["PHQ-4", "Substance use", "Victimization", "Internalizing",
           "Externalizing"]
    p36 = modulo("p36", "36_chicos.py")
    d = p36.p19.construye()
    u = d[["alcohol", "fuma", "cannabis", "otras_drogas"]]
    d["consumo"] = u.max(axis=1).where(u.notna().any(axis=1))
    d["z_consumo"] = (d.consumo - d.consumo.mean()) / d.consumo.std()
    for g, sx, nombre in (("chicas", 1, "chicas.tex"),
                          ("chicos", 0, "chicos.tex")):
        res = [ventana(d, y, sx) for y in ys]
        cg = c[c.grupo == g].set_index("resultado")
        for y, r in zip(ys, res):
            igual(r[0][VENT][0], cg.loc[y, "b"], f"a5 {g} {y}")
        guarda(nombre, tabla(cab, filas_ventana(res),
                             pie_ventana(res, [cg.loc[y, "p_plano"]
                                               for y in ys]),
                             [("Adolescent report (SD)", 3),
                              ("Caregiver report, CBCL (SD)", 2)]))


# ------------------------------------------------------ olas: tres rondas

def olas():
    """Los primeros 18 meses frente al resto en cinco medidas de los mismos
    adolescentes: el CBCL internalizante del cuidador en 2012, 2017 y 2024 y
    lo que reporta el propio niño en 2017 y 2024 (reports/tres_olas.csv)."""
    c = pd.read_csv("reports/tres_olas.csv").set_index(["medida", "grupo"])
    ms = ["z_int12", "z_int17", "z_cbcl", "malestar17", "z_phq4"]
    k = len(ms)
    cuerpo = []
    for g, nombre in (("chicas", "Panel A. Girls"),
                      ("chicos", "Panel B. Boys")):
        r = [c.loc[(m, g)] for m in ms]
        if cuerpo:
            cuerpo.append("\\addlinespace[3pt]")
        cuerpo += [panel(k, nombre),
                   fila(ETVENT, [coef(x.b_v) for x in r]),
                   fila("", [ee(x.se_v) for x in r]),
                   fila("Flat profile, joint test $p$-value",
                        [f"{x.p_conjunta:.3f}" for x in r]),
                   fila("Observations", [f"{int(x.n):,}" for x in r])]
    pie = [fila("Municipality FE", ["Yes"] * k),
           fila("Birth-year FE", ["Yes"] * k),
           fila("Six-month age-group FE", ["Yes"] * k),
           fila("Controls", ["Yes"] * k)]
    cab = ["\\shortstack{2012\\\\ages 2--6}", "\\shortstack{2017\\\\ages 8--12}",
           "\\shortstack{2024\\\\ages 14--18}",
           "\\shortstack{2017\\\\ages 8--12}",
           "\\shortstack{2024\\\\ages 14--18}"]
    guarda("olas.tex", tabla(cab, cuerpo, pie,
                             [("Caregiver, CBCL internalizing (SD)", 3),
                              ("Own report (SD)", 2)]))


# ------------------------------------------------------- entorno, chicas

def a2():
    p35 = modulo("p35", "35_canal_hogar.py")
    d = p35.carga()
    res = [ventana(d, i, 1) for i in p35.INDICES]
    c = contrastes("entorno").set_index("resultado")
    for i, r in zip(p35.INDICES, res):
        igual(r[0][VENT][0], c.loc[i, "b"], f"a2 {i}")
    cab = ["\\shortstack{Lower\\\\income}",
           "\\shortstack{Mother not\\\\employed}",
           "\\shortstack{Damaged\\\\housing}",
           "\\shortstack{Conflict\\\\at home}",
           "\\shortstack{Overcrowded\\\\housing}",
           "\\shortstack{Precarious\\\\housing}"]
    guarda("entorno.tex", tabla(cab, filas_ventana(res),
                                pie_ventana(res, [c.loc[i, "p_plano"]
                                                  for i in p35.INDICES]),
                                [("Mechanisms in Gillmore (2026), SD", 3),
                                 ("Other household conditions, SD", 3)]))


# --------------------------------------- lactancia: los primeros 18 meses

def lactancia():
    """Los primeros 18 meses frente a todas las demás edades, por separado
    para quienes tomaban pecho el 27-F y quienes no (los números de
    reports/contraste.csv, que calcula scripts/45_contraste.py)."""
    c = contrastes("pecho")
    cols = ["chicas", "chicas, SES", "chicos"]
    cuerpo = []
    for clave, lab in (("con pecho", "6--17 months $\\times$ Affected "
                        "$\\times$ breastfed"),
                       ("sin pecho", "6--17 months $\\times$ Affected "
                        "$\\times$ not breastfed"),
                       ("diferencia", "Difference, breastfed $-$ not "
                        "breastfed")):
        r = c[c.resultado == clave].set_index("grupo").loc[cols]
        cuerpo += [fila(lab, [coef(b) for b in r.b]),
                   fila("", [ee(se) for se in r.se]), "\\addlinespace[2pt]"]
    dif = c[c.resultado == "diferencia"].set_index("grupo").loc[cols]
    pie = [fila("Wild bootstrap $p$-value, difference",
                [f"{v:.3f}" for v in dif.p_wild]),
           fila("Breastfed, share at 6--17 months",
                [f"{v:.2f}" for v in dif.cuota]),
           fila("Observations", [f"{int(v):,}" for v in dif.n]),
           fila("Municipality FE", ["Yes"] * 3),
           fila("Birth-year FE", ["Yes"] * 3),
           fila("Six-month age-group FE", ["Yes"] * 3),
           fila("Six-month age group $\\times$ breastfed FE", ["Yes"] * 3),
           fila("Controls", ["Yes"] * 3),
           fila("Mother's education and employment $\\times$ breastfed "
                "and $\\times$ affected", ["No", "Yes", "No"])]
    guarda("lactancia.tex", tabla(["Girls", "Girls", "Boys"], cuerpo[:-1],
                                  pie, [("PHQ-4 (SD)", 3)]))


# -------------------------------------- diada: estrés de la madre y pecho

def a3():
    p34 = modulo("p34", "34_estres_madre.py")
    d = p34.carga()
    x = d.dropna(subset=["z_phq4", "estres12", "pecho", "estrato", "w",
                         "cohorte"]).copy()
    x = x[(x.w > 0) & (x.mujer == 1)]
    x["est"] = x.estrato.astype(int).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    bordes, et = p33.CORTES["seis"]
    x["b6"] = pd.cut(x.edadq_m, bordes, right=False, labels=et).astype(str)
    x["e_pecho"] = x.estres12 * x.pecho
    x["e_sin"] = x.estres12 * (1 - x.pecho)
    x["e_bebe"] = x.estres12 * (x.edadq_m < 18)
    fe = ["C(b6)", "C(b6):pecho", "pecho", "C(est)", "C(coh)"] \
        + p34.xt(x, p15.X_PRE) + p34.xt(x, p15.X_POST)

    def ajusta(datos, extra):
        r = smf.wls("z_phq4 ~ " + " + ".join(["e_sin", "e_pecho"] + extra
                                             + fe), data=datos,
                    weights=datos.w).fit(cov_type="cluster",
                                         cov_kwds={"groups": datos.est})
        t = r.t_test("e_pecho - e_sin")
        dif = (float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]),
               float(np.ravel(t.pvalue)[0]))
        return r, dif

    y = x.dropna(subset=["educ_madre10", "trabaja10"]).copy()
    y["e_educ"] = y.estres12 * (y.educ_madre10 - y.educ_madre10.mean())
    y["e_trab"] = y.estres12 * y.trabaja10
    y["p_educ"] = y.pecho * (y.educ_madre10 - y.educ_madre10.mean())
    y["p_trab"] = y.pecho * y.trabaja10
    res = [ajusta(x, []),
           ajusta(y, ["e_educ", "e_trab", "p_educ", "p_trab"]),
           ajusta(y, ["e_educ", "e_trab", "e_bebe", "p_educ", "p_trab"])]
    cuerpo = []
    for k, lab in (("e_sin", "Maternal stress $\\times$ not breastfed"),
                   ("e_pecho", "Maternal stress $\\times$ breastfed")):
        cuerpo += [fila(lab, [coef(r.params[k]) for r, _ in res]),
                   fila("", [ee(r.bse[k]) for r, _ in res]),
                   "\\addlinespace[2pt]"]
    cuerpo += [fila("Difference, breastfed $-$ not breastfed",
                    [coef(dif[0]) for _, dif in res]),
               fila("", [ee(dif[1]) for _, dif in res])]
    pie = [fila("Observations", [f"{int(r.nobs):,}" for r, _ in res]),
           fila("Municipality FE", ["Yes"] * 3),
           fila("Birth-year FE", ["Yes"] * 3),
           fila("Six-month age-group FE", ["Yes"] * 3),
           fila("Six-month age group $\\times$ breastfed FE", ["Yes"] * 3),
           fila("Controls", ["Yes"] * 3),
           fila("Stress and breastfed $\\times$ mother's education and "
                "employment", ["No", "Yes", "Yes"]),
           fila("Stress $\\times$ 6--17 months", ["No", "No", "Yes"])]
    guarda("diada.tex", tabla(["Baseline", "\\shortstack{Mother's\\\\SES}",
                               "\\shortstack{Mother's SES\\\\and 6--17 "
                               "months}"],
                              cuerpo, pie, [("Daughters' PHQ-4 (SD)", 3)]))


# ---------------------------------- medias: estrés y pecho por tramo

def a4():
    p34 = modulo("p34", "34_estres_madre.py")
    m = p34.medias_seis(p34.carga())
    est = m[m.que == "estres"].set_index(["tramo", "zona"])
    pec = m[m.que == "pecho"].set_index("tramo")
    cuerpo = []
    for t in SEIS:
        a, n = est.loc[(t, "afectada")], est.loc[(t, "no afectada")]
        cuerpo += [fila(t.replace("-", "--") + " months",
                        [f"{100 * a.b:.1f}", f"{100 * n.b:.1f}",
                         f"{100 * pec.loc[t, 'b']:.1f}"]),
                   fila("", [f"({100 * a.se:.1f})", f"({100 * n.se:.1f})",
                             f"({100 * pec.loc[t, 'se']:.1f})"])]
    pie = [fila("Observations",
                [f"{int(est.xs('afectada', level='zona').n.sum()):,}",
                 f"{int(est.xs('no afectada', level='zona').n.sum()):,}",
                 f"{int(pec.n.sum()):,}"])]
    guarda("medias.tex", tabla(["Affected", "Unaffected", "On 27-F"],
                               cuerpo, pie,
                               [("Mothers with stress (\\%)", 2),
                                ("Breastfed (\\%)", 1)]))


# ------------------------------------- descriptivas de la muestra

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
            cuerpo.append(panel(4, lab))
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


# ------------------------------------------------------------ balance

def balance():
    d, _, _ = p15.load_data()
    ys = ["z_peso", "z_talla", "z_gest", "educ_madre10", "edad_madre10"]
    res = [ventana(d, y, 1, controles=False) for y in ys]
    plano = [centrado(d, y, 1, controles=False)[1] for y in ys]
    guarda("balance.tex", tabla(["Weight", "Length", "Gestation",
                                 "Education", "Age"],
                                filas_ventana(res),
                                pie_ventana(res, plano, controles=False),
                                [("At birth (SD)", 3),
                                 ("Mother, 2010 (years)", 2)]))
    # la misma muestra con y sin los controles al nacer: las chicas sin
    # registro de nacimiento cambian el coeficiente, los controles no
    nacer = ("z_peso", "z_talla", "z_gest")
    sin = ventana(d.dropna(subset=list(nacer)), "z_phq4", 1)[0][VENT]
    con = ventana(d, "z_phq4", 1, extra=nacer)
    b, n = con[0][VENT], con[1]
    (OUTD / "balance_nota.tex").write_text(
        f"Among the {n:,} girls with birth records, the PHQ-4 coefficient "
        "for those exposed at 6--17 months, relative to all other ages, is "
        f"{sin[0]:.3f} ({sin[1]:.3f}) without and {b[0]:.3f} ({b[1]:.3f}) "
        "with the three birth outcomes as controls.\n", encoding="utf-8")
    print(f"-> {OUTD / 'balance_nota.tex'}")


# ------------------------------------------------------------ atrición

def atricion():
    """Responder en 2024 por edad al terremoto y zona, y el peso al nacer de
    las chicas en toda la línea base y en quienes responden."""
    p42 = modulo("p42", "42_balance_atricion.py")
    res, _ = p42.resultados(ventana=True)
    pie = [fila("Flat profile, joint test $p$-value",
                [f"{r[2]:.3f}" for r in res]),
           fila("Mean of dependent variable",
                [f"{r[3]:.2f}" for r in res[:3]] + ["", ""]),
           fila("Observations", [f"{r[1]:,}" for r in res]),
           fila("Region FE", ["Yes"] * 5),
           fila("Birth-year FE", ["Yes"] * 5),
           fila("Six-month age-group FE", ["Yes"] * 5)]
    guarda("atricion.tex", tabla(
        ["Girls", "Boys", "All", "\\shortstack{2010\\\\baseline}",
         "\\shortstack{Interviewed\\\\in 2024}"],
        filas_ventana(res), pie,
        [("Interviewed in 2024", 3), ("Birth weight, girls (SD)", 2)]))


def main():
    desc()
    balance()
    atricion()
    a1()
    a5()
    olas()
    a2()
    lactancia()
    a3()
    a4()


if __name__ == "__main__":
    main()
