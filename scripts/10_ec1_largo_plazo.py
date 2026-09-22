#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ec. (1) de Gillmore LITERAL, extendida al LARGO PLAZO (14 años) con la ola
2024:

    Y_imtw = a + b·(Affected_it × Earthquake_m) + X_imt + psi_m + theta_t
             + eta_w + e_imtw

  * Afectados : cohortes 2006–2009 (in utero–4 años el 27-F), medidos en la
                OLA 2024 (14–18 años).
  * Controles : concebidos DESPUÉS del 27-F (cohortes 2011+), medidos en la
                OLA 2017 — el mismo grupo de control del paper; eta_w
                absorbe la ola, como cuando él pool-ea 2012+2017.
  * psi_m     : comuna de SELECCIÓN en CUT (2024: estrato→CUT vía crosswalk;
                2017: estrato, que ya es CUT) — misma unidad en ambas olas.
  * Outcomes con el mismo test en ambos lados: Peabody/TVIP (Panel A) y
    CBCL2 T internacional (Panel B, INVERTIDO como el paper: más alto =
    mejor). PHQ-4/PHQ-2/GAD-2 solo se midieron en 2024 (solo expuestos):
    sin filas de control, la ec. (1) no es estimable para ellos.
  * Columnas como sus Tablas 2–3: (1) FE comuna + dummy Affected;
    (2) + FE cohorte y ola; (3) + controles X; (4) + tendencias lineales
    por comuna. z dentro de (ola × tramo de 12 meses); WLS con pesos
    transversales; EE cluster por comuna.

Salida: reports/ec1_largo_plazo.md
Uso:    python3 scripts/10_ec1_largo_plazo.py
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
INT = Path("data/interim")
OUT = Path("reports")
EQ_REGIONS = {5, 6, 7, 8, 9, 13}


def dta(path, cols=None):
    kw = {"usecols": cols} if cols else {}
    df, _ = pyreadstat.read_dta(str(path), **kw)
    df["folio"] = pd.to_numeric(df.folio).astype("int64")
    return df


def sav(path, cols=None):
    kw = {"usecols": cols} if cols else {}
    df, _ = pyreadstat.read_sav(str(path), **kw)
    df["folio"] = pd.to_numeric(df.folio).astype("int64")
    return df


def num(s):
    return pd.to_numeric(s, errors="coerce")


def build():
    # ---------- filas AFECTADAS: ola 2024 (cohortes 2006-2009) ----------
    e24 = dta(INT / "2024/Base evaluaciones Stata.dta",
              ["folio", "fecha_nac", "estrato", "tvip_pst_hispano",
               "cbcl2_pt_inter_t", "f_exp"])
    xw = pd.read_csv("data/processed/crosswalk_estrato24_comuna.csv")
    a = e24.merge(xw, left_on="estrato", right_on="estrato24", how="left")
    fn = a.fecha_nac.astype(str).str.extract(r"(?P<mm>\d+)/(?P<aa>\d+)")
    a["birth_ym"] = num(fn.aa) * 12 + num(fn.mm) - 1
    a = a[a.birth_ym <= 2010 * 12 + 1]            # nacidos antes del 27-F
    a["geo"] = num(a.cut_comuna_seleccion)        # comuna de selección (CUT)
    a["edad_meses"] = (2024 * 12 + 7) - a.birth_ym
    a["tvip"] = num(a.tvip_pst_hispano)
    a["cbcl"] = num(a.cbcl2_pt_inter_t)
    a["w"] = num(a.f_exp)
    a["wave"] = 2024
    a["affected"] = 1.0

    # controles X de los afectados: línea base 2010 + 2012 (como script 09)
    h10 = dta(INT / "2010/Hogar_2010.dta",
              ["folio", "a16", "a18", "a19", "b2n", "tot_per"])
    madre = h10[h10.a16 == 1].drop_duplicates("folio").set_index("folio")
    nino = h10[h10.a16 == 13].drop_duplicates("folio").set_index("folio")
    b55 = [f"b55{l}_{q}" for l in "opqrst" for q in ("madre", "padre", "ofam")]
    e12 = dta(INT / "2012/Entrevistada_2012.dta", ["folio", "b71"] + b55)
    for q in ("madre", "padre", "ofam"):
        cols = [f"b55{l}_{q}" for l in "opqrst"]
        e12[f"mh_{q}"] = (e12[cols] == 1).any(axis=1).astype(float)
    h12 = dta(INT / "2012/Hogar_2012.dta", ["folio", "i2"])
    pp12 = h12.i2.isin([2, 4]).groupby(h12.folio).any().astype(float)
    a = (a.join(madre[["a19", "b2n", "tot_per"]], on="folio")
          .join(nino[["a18"]], on="folio")
          .merge(e12[["folio", "b71", "mh_madre", "mh_padre", "mh_ofam"]],
                 on="folio", how="left")
          .join(pp12.rename("padre_presente"), on="folio"))
    a["sexo"] = num(a.a18)
    a["edad_madre"] = num(a.a19).where(lambda s: s < 99)
    a["educ_madre"] = num(a.b2n).where(lambda s: s < 30)
    a["hh_size"] = num(a.tot_per)
    a["n_hijos"] = num(a.b71).where(lambda s: s < 25)

    # ---------- filas de CONTROL: ola 2017, concebidos post-27F ----------
    e17 = dta(INT / "2017/Base Evaluaciones ELPI III.dta",
              ["folio", "edad_mesesr", "sexo", "estrato", "tvip_ps",
               "cbcl2_pt_inter_t", "finicio_tn"])
    ro = sav(INT / "2017/Base Cuidador Principal ELPI III (SPSS).sav",
             ["folio", "h1", "h3", "fexp_eva0_2", "fechanacimientons",
              "e4", "m10", "c56", "m8", "numper"])
    h1 = num(ro.h1)
    em = (num(ro.h3).where(h1.isin([2, 4])).groupby(ro.folio).max()
          .rename("edad_madre"))
    pp = (h1.isin([3, 5]).groupby(ro.folio).any().astype(float)
          .rename("padre_presente"))
    herm = h1.eq(8).groupby(ro.folio).sum().rename("hermanos")
    hog = (ro.groupby("folio")
             .agg(fexp_eva0_2=("fexp_eva0_2", "first"),
                  fechanacimientons=("fechanacimientons", "first"),
                  e4=("e4", "first"), m10=("m10", "first"),
                  c56=("c56", "first"), m8=("m8", "first"),
                  numper=("numper", "first")))
    c = (e17.merge(hog, on="folio", how="left")
            .merge(em, on="folio", how="left")
            .merge(pp, on="folio", how="left")
            .merge(herm, on="folio", how="left"))
    fnc = c.fechanacimientons
    if fnc.dtype == object:
        fd = pd.to_datetime(fnc, errors="coerce", dayfirst=True)
    else:
        fd = (pd.Timestamp("1582-10-14")
              + pd.to_timedelta(num(fnc), unit="s"))
    ym_ns = fd.dt.year * 12 + (fd.dt.month - 1)
    dias = num(c.finicio_tn)
    fev = pd.Timestamp("1960-01-01") + pd.to_timedelta(dias, unit="D")
    ym_fi = (fev.dt.year * 12 + (fev.dt.month - 1)) - num(c.edad_mesesr)
    c["birth_ym"] = ym_ns.fillna(ym_fi)
    c = c[c.birth_ym >= 2011 * 12]                # concebidos post-27F
    c["geo"] = num(c.estrato)                     # comuna selección (CUT)
    c["edad_meses"] = num(c.edad_mesesr)
    c["tvip"] = num(c.tvip_ps)
    c["cbcl"] = num(c.cbcl2_pt_inter_t)
    c["w"] = num(c.fexp_eva0_2)
    c["wave"] = 2017
    c["affected"] = 0.0
    c56v = num(c.c56).where(lambda s: s < 25)
    m8v = num(c.m8).where(lambda s: s < 25)
    c["n_hijos"] = c56v.fillna(m8v + 1).fillna(num(c.hermanos) + 1)
    c["educ_madre"] = num(c.e4).fillna(num(c.m10))
    c.loc[c.educ_madre >= 88, "educ_madre"] = np.nan
    c["hh_size"] = num(c.numper)
    for v in ("mh_madre", "mh_padre", "mh_ofam"):
        c[v] = np.nan

    keep = ["folio", "geo", "birth_ym", "edad_meses", "sexo", "tvip", "cbcl",
            "w", "wave", "affected", "edad_madre", "educ_madre", "hh_size",
            "n_hijos", "padre_presente", "mh_madre", "mh_padre", "mh_ofam"]
    df = pd.concat([a[keep], c[keep]], ignore_index=True)
    df["cohorte"] = (df.birth_ym // 12).astype("Int64")
    df["region"] = (df.geo // 1000).astype("Int64")
    df["EQ"] = num(df.region).isin(EQ_REGIONS).astype(float)
    df["AffEq"] = df.affected * df.EQ
    df["mujer"] = (num(df.sexo) == 2).astype(float).where(df.sexo.notna())
    df["mh_miss"] = df.mh_madre.isna().astype(float)
    for v in ("mh_madre", "mh_padre", "mh_ofam"):
        df[v] = df[v].fillna(0.0)
    df["padre_presente"] = df.padre_presente.fillna(0.0)

    def z(col):
        s = num(df[col])
        g = s.groupby([df.wave, (num(df.edad_meses) // 12)])
        return (s - g.transform("mean")) / g.transform("std")

    df["z_tvip"] = z("tvip")
    df["z_cbcl"] = -z("cbcl")        # invertido, como el paper
    return df


XV = ["mujer", "edad_meses", "n_hijos", "edad_madre", "educ_madre",
      "padre_presente", "hh_size", "mh_madre", "mh_padre", "mh_ofam",
      "mh_miss"]


def fit(df, y, col):
    d = df.dropna(subset=[y, "AffEq", "geo", "w", "cohorte"]).copy()
    d = d[d.w > 0]
    d["com"] = d.geo.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    d["ola"] = d.wave.astype(str)
    d["t"] = num(d.cohorte)
    if col == 1:
        f = f"{y} ~ AffEq + affected + C(com)"
    else:
        f = f"{y} ~ AffEq + C(com) + C(coh) + C(ola)"
    if col >= 3:
        terms = []
        for v in XV:
            if d[v].isna().any():
                d[f"{v}_mi"] = d[v].isna().astype(float)
                d[v] = d[v].fillna(d[v].median())
                terms += [v, f"{v}_mi"]
            else:
                terms.append(v)
        f += " + " + " + ".join(terms)
    if col >= 4:
        f += " + C(com):t"
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d["com"]})
    return dict(b=r.params["AffEq"], se=r.bse["AffEq"], p=r.pvalues["AffEq"],
                n=int(r.nobs), ncl=d["com"].nunique(),
                r2=float(r.rsquared_adj))


def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""


def main():
    df = build()
    na = int((df.affected == 1).sum())
    nc = int((df.affected == 0).sum())
    print(f"afectados 2024: {na:,} | controles 2017 (concebidos post): {nc:,}")

    filas = [
        "# Ec. (1) de Gillmore en el LARGO PLAZO (14 anos) — ola 2024",
        "",
        "Afectados: cohortes 2006-2009 medidos en 2024 (14-18). Controles:"
        " concebidos post-27F (2011+) medidos en 2017 — el grupo de control"
        " del paper, con eta_w absorbiendo la ola. CBCL2 invertido (mas alto"
        " = mejor), z por ola x tramo de edad. EE cluster por comuna de"
        " seleccion. Columnas (1)-(4) como las Tablas 2-3 del paper.",
        "",
        "|  | (1) | (2) | (3) | (4) |",
        "|---|---:|---:|---:|---:|"]
    for panel, y in (("Panel A: Peabody", "z_tvip"),
                     ("Panel B: CBCL2", "z_cbcl")):
        filas.append(f"| **{panel}** | | | | |")
        rs = [fit(df, y, c) for c in (1, 2, 3, 4)]
        filas.append("| Affected*Earthquake | " + " | ".join(
            f"{r['b']:.3f}{stars(r['p'])}" for r in rs) + " |")
        filas.append("|  | " + " | ".join(f"({r['se']:.3f})" for r in rs)
                     + " |")
        filas.append("| Observations | " + " | ".join(f"{r['n']:,}"
                                                      for r in rs) + " |")
        filas.append("| Adj-R2 | " + " | ".join(f"{r['r2']:.3f}"
                                                for r in rs) + " |")
        for r, cnum in zip(rs, (1, 2, 3, 4)):
            print(panel, f"col{cnum}: b={r['b']:.3f}{stars(r['p'])} "
                  f"(se {r['se']:.3f}) n={r['n']:,} ncl={r['ncl']}")
    filas += [
        "| Municipality FE | Si | Si | Si | Si |",
        "| Birth Cohort FE | No | Si | Si | Si |",
        "| Survey wave FE | No | Si | Si | Si |",
        "| Child-Mother-HH control | No | No | Si | Si |",
        "| Municipality linear trends | No | No | No | Si |",
        "",
        "Nota: PHQ-4, PHQ-2 y GAD-2 solo se midieron en 2024 y solo a la"
        " cohorte expuesta; sin filas de control, b no es estimable en la"
        " ec. (1) para esos outcomes (el CBCL2 es el outcome de salud"
        " mental con el mismo instrumento en ambos lados).",
        ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "ec1_largo_plazo.md").write_text("\n".join(filas),
                                            encoding="utf-8")
    print("->", OUT / "ec1_largo_plazo.md")


if __name__ == "__main__":
    main()
