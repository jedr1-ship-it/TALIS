#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis RD del corte de entrada escolar (31 de marzo) con la cohorte ELPI.

Diseño: nacer el 1 de abril o después retrasa la entrada a 1º básica ~1 año.
Running variable: mes de nacimiento centrado en el corte de abril más cercano
(ventana +-4 meses, efectos fijos de corte/cohorte, tendencia lineal a cada
lado, errores agrupados por celda mes-de-nacimiento).

    y = a_b + tau*D + b1*m*(1-D) + b2*m*D + e,   D = 1(m >= 0), m = mes - abril

Salidas: reports/rd_resultados_ronda1.md (tablas para revisión adversarial).

Uso: python3 scripts/05_rd_entrada_escolar.py [--ventana 4] [--donut 0]
     [--placebo-mes 0]  (0 = corte real de abril; 7 = placebo en julio, etc.)
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")

INTERIM = Path("data/interim")
OUT = Path("reports")

BOUNDS = [2006, 2007, 2008, 2009]  # cortes: 1 de abril de cada año


def leer(ruta, cols):
    try:
        df, _ = pyreadstat.read_dta(str(ruta), usecols=cols)
    except Exception:
        df = pd.read_stata(str(ruta), columns=cols, convert_categoricals=False)
    df["folio"] = pd.to_numeric(df.folio).astype("int64")
    return df


def running_var(ym, mes_corte=4):
    """m = distancia en meses al corte (día 1 de `mes_corte`) más cercano."""
    m, b = np.full(len(ym), np.nan), np.full(len(ym), np.nan)
    for a in BOUNDS:
        corte = a * 12 + (mes_corte - 1)
        d = ym - corte
        mejor = np.abs(d) < np.abs(np.where(np.isnan(m), np.inf, m))
        m = np.where(mejor, d, m)
        b = np.where(mejor, a, b)
    return m, b


def rd(df, y, ventana, donut=0, pesos=None):
    d = df.dropna(subset=[y, "m"]).copy()
    d = d[np.abs(d.m) <= ventana]
    if donut:
        d = d[(d.m <= -1 - donut + 0) | (d.m >= donut)]  # quita m in [-donut, donut-1]
        d = d[~d.m.isin(range(-donut, donut))]
    d["D"] = (d.m >= 0).astype(int)
    d["mL"] = d.m * (1 - d.D)
    d["mR"] = d.m * d.D
    d["celda"] = d.b.astype(int).astype(str) + ":" + d.m.astype(int).astype(str)
    f = f"{y} ~ D + mL + mR + C(b)"
    kw = {}
    if pesos is not None:
        kw["weights"] = d[pesos]
        mod = smf.wls(f, data=d, **kw)
    else:
        mod = smf.ols(f, data=d)
    res = mod.fit(cov_type="cluster", cov_kwds={"groups": d["celda"]})
    return dict(tau=res.params["D"], se=res.bse["D"], p=res.pvalues["D"],
                n=int(res.nobs), media=float(d[y].mean()))


def fila(nombre, r):
    est = "***" if r["p"] < .01 else "**" if r["p"] < .05 else "*" if r["p"] < .1 else ""
    return (f"| {nombre} | {r['tau']:.3f}{est} | ({r['se']:.3f}) | {r['p']:.3f} "
            f"| {r['n']:,} | {r['media']:.3f} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ventana", type=int, default=4)
    ap.add_argument("--donut", type=int, default=0)
    ap.add_argument("--placebo-mes", type=int, default=0)
    args = ap.parse_args()
    mes_corte = args.placebo_mes or 4
    etiqueta = "" if mes_corte == 4 else f"_placebo_mes{mes_corte}"

    # ------------------------------------------------ armar base
    e24, _ = pyreadstat.read_dta(INTERIM / "2024/Base evaluaciones Stata.dta",
        usecols=["folio", "fecha_nac", "tvip_pst_hispano", "cbcl2_pt_inter_t"])
    e24["folio"] = e24.folio.astype("int64")
    fn = e24.fecha_nac.astype(str).str.extract(r"(?P<mm>\d+)/(?P<aa>\d+)")
    e24["ym"] = fn.aa.astype(float) * 12 + fn.mm.astype(float) - 1

    a24 = leer(INTERIM / "2024/Base adolescentes Stata.dta",
               ["folio", "phq2", "gad2", "phq4", "g11", "g12_1", "g12_2",
                "g12_3", "g12_4", "e3_asiste", "sg01"])
    a24["fuma"] = (a24.g11 == 1).astype(float).where(a24.g11.notna())
    alc = a24[["g12_1", "g12_2", "g12_3", "g12_4"]]
    a24["alcohol"] = (alc == 1).any(axis=1).astype(float).where(alc.notna().any(axis=1))
    a24["notas"] = pd.to_numeric(a24.e3_asiste, errors="coerce")
    a24.loc[(a24.notas < 1) | (a24.notas > 7), "notas"] = np.nan  # escala 1-7

    e17 = leer(INTERIM / "2017/Base Evaluaciones ELPI III.dta",
               ["folio", "nivel_edu_niño", "curso_edu_niño", "finicio_tn",
                "tvip_ps", "cbcl2_pt_inter_t"])
    e17 = e17.rename(columns={"cbcl2_pt_inter_t": "cbcl_t17",
                              "tvip_ps": "tvip17"})
    dias = pd.to_numeric(e17.finicio_tn, errors="coerce")
    e17["feval"] = pd.Timestamp("1960-01-01") + pd.to_timedelta(dias, unit="D")
    e17["grado18"] = np.where(e17["nivel_edu_niño"] == 4, e17["curso_edu_niño"],
                              np.where(e17["nivel_edu_niño"].isin([0, 1, 2]), 0, np.nan))
    e17.loc[~e17.feval.between("2018-03-01", "2018-07-31"), "grado18"] = np.nan

    # línea base 2010: madre y hogar
    h10 = leer(INTERIM / "2010/Hogar_2010.dta", ["folio", "a16", "a18", "a19", "b2n", "tot_per"])
    madre = h10[h10.a16 == 1].drop_duplicates("folio")[["folio", "a19", "b2n", "tot_per"]]
    madre.columns = ["folio", "edad_madre10", "educ_madre10", "tot_per10"]
    madre.loc[madre.edad_madre10 >= 99, "edad_madre10"] = np.nan
    nino = h10[h10.a16 == 13].drop_duplicates("folio")[["folio", "a18"]]
    nino.columns = ["folio", "sexo10"]
    ent10 = leer(INTERIM / "2010/Entrevistada_2010.dta", ["folio", "region", "area"])
    ent10["rm"] = (ent10.region == 13).astype(float)
    panel = pd.read_csv("data/processed/elpi_panel_ninos_ancho.csv",
                        usecols=["folio", "en_2010", "en_2024"])

    df = (e24.merge(a24, on="folio", how="left")
             .merge(e17, on="folio", how="left")
             .merge(madre, on="folio", how="left")
             .merge(nino, on="folio", how="left")
             .merge(ent10, on="folio", how="left"))
    df["m"], df["b"] = running_var(df.ym.values, mes_corte)
    df["mujer"] = (df.sexo10 == 2).astype(float).where(df.sexo10.notna())

    V, DON = args.ventana, args.donut

    lineas = [
        f"# RD corte escolar — resultados ronda 1{etiqueta}",
        "",
        f"Corte: día 1 del mes {mes_corte} (4=real abril). Ventana ±{V} meses; "
        f"donut={DON}; tendencia lineal a cada lado; EF de corte (cohorte); "
        "errores cluster por celda mes-de-nacimiento.",
        "",
        "| Variable | τ (salto en el corte) | (EE) | p | n | media |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    lineas.append("| **Primera etapa** |")
    lineas.append(fila("Curso alcanzado 2018 (grados)", rd(df, "grado18", V, DON)))

    lineas.append("| **Outcomes 2024 (14-18 años)** |")
    for y, nom in [("tvip_pst_hispano", "TVIP estándar 2024"),
                   ("notas", "Promedio de notas último año (1-7)"),
                   ("phq2", "Síntomas depresión (PHQ-2, 0/1)"),
                   ("gad2", "Síntomas ansiedad (GAD-2, 0/1)"),
                   ("fuma", "Fumó tabaco últimos 12m (0/1)"),
                   ("alcohol", "Tomó alcohol últimos 12m (0/1)"),
                   ("cbcl2_pt_inter_t", "CBCL total T 2024 (reporte cuidador)")]:
        lineas.append(fila(nom, rd(df, y, V, DON)))

    lineas.append("| **Outcomes 2017 (8-12 años)** |")
    for y, nom in [("tvip17", "TVIP estándar 2017"),
                   ("cbcl_t17", "CBCL total T 2017")]:
        lineas.append(fila(nom, rd(df, y, V, DON)))

    lineas.append("| **Balance en línea base 2010** |")
    for y, nom in [("mujer", "Niña (0/1)"), ("educ_madre10", "Educación madre (nivel)"),
                   ("edad_madre10", "Edad madre"), ("tot_per10", "Tamaño hogar"),
                   ("rm", "Región Metropolitana (0/1)"), ("area", "Área (1 urb/2 rur)")]:
        lineas.append(fila(nom, rd(df, y, V, DON)))

    # densidad: conteos por celda
    cel = df[np.abs(df.m) <= V].groupby(["b", "m"]).size().reset_index(name="n_cel")
    cel["log_n"] = np.log(cel.n_cel)
    cel["D"] = (cel.m >= 0).astype(int)
    cel["mL"], cel["mR"] = cel.m * (1 - cel.D), cel.m * cel.D
    res = smf.ols("log_n ~ D + mL + mR + C(b)", data=cel).fit(cov_type="HC1")
    lineas += ["", f"**Densidad** (log conteo por celda): salto = "
               f"{res.params['D']:.3f} (EE {res.bse['D']:.3f}, p={res.pvalues['D']:.3f}).",
               ""]

    # atrición diferencial: P(en 2024 | en 2010) — requiere fecha_nac, que solo
    # existe en 2024 => proxy: P(TVIP 2024 no nulo | evaluado 2017) por lado
    df["sigue24"] = df.tvip_pst_hispano.notna().astype(float)
    sub = df[df.tvip17.notna()]
    lineas.append("**Atrición diferencial** (P(TVIP 2024) | TVIP 2017): "
                  + fila("", rd(sub, "sigue24", V, DON)).replace("|  |", "|"))

    lineas += ["", f"n adolescentes 2024 con mes de nacimiento: {df.ym.notna().sum():,}",
               f"n en ventana ±{V}: {int((np.abs(df.m) <= V).sum()):,} "
               f"(izq {int(((df.m < 0) & (df.m >= -V)).sum()):,} / "
               f"der {int(((df.m >= 0) & (df.m <= V)).sum()):,})", ""]

    out = OUT / f"rd_resultados_ronda1{etiqueta}.md"
    out.write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))
    print("->", out)


if __name__ == "__main__":
    main()
