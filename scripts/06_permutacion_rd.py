#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inferencia permutacional para el RD del corte escolar: estima el "salto" τ
con el mismo pipeline de scripts/05_rd_entrada_escolar.py situando el corte
en cada mes del año (1..12). Si |τ_abril| no destaca en esa distribución,
el diseño no distingue el corte legal de la estacionalidad mensual.

Salida: reports/rd_permutacion.md
Uso:    python3 scripts/06_permutacion_rd.py
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
INTERIM = Path("data/interim")
BOUNDS = [2006, 2007, 2008, 2009]
V = 4


def leer(r, c):
    try:
        df, _ = pyreadstat.read_dta(str(r), usecols=c)
    except Exception:
        df = pd.read_stata(str(r), columns=c, convert_categoricals=False)
    df["folio"] = pd.to_numeric(df.folio).astype("int64")
    return df


def base():
    e24, _ = pyreadstat.read_dta(INTERIM / "2024/Base evaluaciones Stata.dta",
                                 usecols=["folio", "fecha_nac", "tvip_pst_hispano"])
    e24["folio"] = e24.folio.astype("int64")
    fn = e24.fecha_nac.astype(str).str.extract(r"(?P<mm>\d+)/(?P<aa>\d+)")
    e24["ym"] = fn.aa.astype(float) * 12 + fn.mm.astype(float) - 1
    a24 = leer(INTERIM / "2024/Base adolescentes Stata.dta", ["folio", "phq2", "g11"])
    a24["fuma"] = (a24.g11 == 1).astype(float).where(a24.g11.notna())
    e17 = leer(INTERIM / "2017/Base Evaluaciones ELPI III.dta",
               ["folio", "nivel_edu_niño", "curso_edu_niño", "finicio_tn", "tvip_ps"])
    dias = pd.to_numeric(e17.finicio_tn, errors="coerce")
    fev = pd.Timestamp("1960-01-01") + pd.to_timedelta(dias, unit="D")
    e17["grado18"] = np.where(e17["nivel_edu_niño"] == 4, e17["curso_edu_niño"],
                              np.where(e17["nivel_edu_niño"].isin([0, 1, 2]), 0, np.nan))
    e17.loc[~fev.between("2018-03-01", "2018-07-31"), "grado18"] = np.nan
    h10 = leer(INTERIM / "2010/Hogar_2010.dta", ["folio", "a16", "tot_per"])
    hh = h10[h10.a16 == 1].drop_duplicates("folio")[["folio", "tot_per"]]
    hh.columns = ["folio", "totper"]
    return (e24.merge(a24, on="folio", how="left")
               .merge(e17[["folio", "grado18", "tvip_ps"]], on="folio", how="left")
               .merge(hh, on="folio", how="left"))


def tau(d, y, mes):
    m = np.full(len(d), np.nan)
    b = np.full(len(d), np.nan)
    for a in BOUNDS:
        c = a * 12 + (mes - 1)
        dd = d.ym - c
        mejor = np.abs(dd) < np.abs(np.where(np.isnan(m), np.inf, m))
        m = np.where(mejor, dd, m)
        b = np.where(mejor, a, b)
    t = d.assign(m=m, b=b).dropna(subset=[y, "m"])
    t = t[np.abs(t.m) <= V]
    t["D"] = (t.m >= 0).astype(int)
    t["mL"], t["mR"] = t.m * (1 - t.D), t.m * t.D
    t["cel"] = t.b.astype(int).astype(str) + ":" + t.m.astype(int).astype(str)
    r = smf.ols(f"{y}~D+mL+mR+C(b)", data=t).fit(
        cov_type="cluster", cov_kwds={"groups": t.cel})
    return r.params["D"]


def main():
    df = base()
    ys = {"grado18": "Primera etapa (curso 2018)",
          "tvip_ps": "TVIP estándar 2017",
          "tvip_pst_hispano": "TVIP estándar 2024",
          "phq2": "PHQ-2 (0/1)",
          "fuma": "Fumó 12m (0/1)",
          "totper": "Tamaño hogar 2010 (covariable)"}
    tab = pd.DataFrame({y: [tau(df, y, mes) for mes in range(1, 13)] for y in ys},
                       index=range(1, 13)).round(3)
    tab.index.name = "mes_corte"

    lineas = ["# Permutación del corte en los 12 meses (pipeline del script 05)",
              "", tab.to_markdown(), "",
              "| Variable | \\|τ_abril\\| | max \\|τ\\| (mes) | ranking abril | p permutacional |",
              "|---|---:|---:|---:|---:|"]
    for y, nom in ys.items():
        v = np.abs(tab[y].values)
        lineas.append(f"| {nom} | {v[3]:.3f} | {v.max():.3f} ({int(np.argmax(v)) + 1}) "
                      f"| {(v >= v[3]).sum()}/12 | {(v >= v[3]).mean():.2f} |")
    out = Path("reports/rd_permutacion.md")
    out.write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))
    print("->", out)


if __name__ == "__main__":
    main()
