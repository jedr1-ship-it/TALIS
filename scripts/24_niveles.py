#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Qué deja el terremoto EN NIVELES, no solo entre edades?

El diseño del paper (efectos fijos de comuna, comparación entre edades de
exposición) identifica perfiles por edad, no si el terremoto dejó un daño
duradero. Este script prueba los dos diseños en niveles posibles:

  1. Intensidad sísmica dentro de la región, solo expuestos (ola 2024):
     todos los resultados, pero con placebos de nivel socioeconómico.
  2. Comparación con los concebidos después del 27-F (Gillmore 2026):
     cohortes 2006-2009 frente a cohortes 2011+, zona afectada frente a no
     afectada, con efectos fijos de comuna, cohorte y ola. Solo para los
     tests medidos en ambos grupos: TVIP y CBCL.
     a) total, por edad al terremoto y por sexo;
     b) dosis: exposición x PGA, dentro de la comuna;
     c) 2017 frente a 2024 en los mismos niños.

Salida: reports/niveles.md
Uso:    python3 scripts/24_niveles.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p10 = modulo("p10", "10_ec1_largo_plazo.py")
p19 = modulo("p19", "19_exploratorio.py")
p15 = p19.p15
num, stars = p15.num, p15.stars
OUT = []
BINS = [(0, 11, "0-11m"), (12, 23, "12-23m"), (24, 35, "24-35m"),
        (36, 59, "36-59m")]


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(b, se, p):
    return f"{b:+.3f}{stars(p)} (ee {se:.3f}, p={p:.3f})"


# ------------------- 1. intensidad dentro de la región --------------------

def intensidad():
    d = p19.construye()
    d["dosis"] = d.pga / 10.0

    def est(y, ctr=True):
        dd = d.dropna(subset=[y, "dosis", "region", "w", "estrato",
                              "cohorte"])
        dd = dd[dd.w > 0].copy()
        dd["reg"] = dd.region.astype(int).astype(str)
        dd["coh"] = dd.cohorte.astype(int).astype(str)
        dd["est"] = dd.estrato.astype(int).astype(str)
        rhs = ["dosis", "C(reg)", "C(coh)"]
        if ctr:
            rhs += p15.xt(dd, p15.X_PRE) + p15.xt(dd, p15.X_POST)
        r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=dd,
                    weights=dd.w).fit(cov_type="cluster",
                                      cov_kwds={"groups": dd.est})
        return r.params["dosis"], r.bse["dosis"], r.pvalues["dosis"]

    log("\n## 1. Intensidad sísmica dentro de la región (PGA/10, expuestos "
        "2024)")
    log("Placebos, características fijadas antes del terremoto:")
    for y, ctr in (("z_peso", True), ("z_gest", True),
                   ("educ_madre10", False), ("edad_madre10", False),
                   ("rural10", False)):
        log(f"- {y}: {fmt(*est(y, ctr))}")
    log("Dentro de cada región, las comunas más sacudidas tenían madres más "
        "educadas y eran más urbanas: el diseño confunde intensidad con "
        "nivel socioeconómico y no sirve para niveles.")


# ------------- 2. comparación con los concebidos después ------------------

def base24():
    df = p10.build()
    return df


def base17():
    """Expuestos y concebidos después, ambos medidos en 2017."""
    import pyreadstat
    INT = Path("data/interim")
    e17, _ = pyreadstat.read_dta(
        str(INT / "2017/Base Evaluaciones ELPI III.dta"),
        usecols=["folio", "edad_mesesr", "sexo", "estrato", "tvip_ps",
                 "cbcl2_pt_inter_t", "finicio_tn"])
    e17["folio"] = num(e17.folio).astype("int64")
    ro, _ = pyreadstat.read_sav(
        str(INT / "2017/Base Cuidador Principal ELPI III (SPSS).sav"),
        usecols=["folio", "h1", "h3", "fexp_eva0_2", "fechanacimientons",
                 "e4", "m10", "c56", "m8", "numper"])
    ro["folio"] = num(ro.folio).astype("int64")
    h1 = num(ro.h1)
    em = (num(ro.h3).where(h1.isin([2, 4])).groupby(ro.folio).max()
          .rename("edad_madre"))
    pp = (h1.isin([3, 5]).groupby(ro.folio).any().astype(float)
          .rename("padre_presente"))
    herm = h1.eq(8).groupby(ro.folio).sum().rename("hermanos")
    hog = ro.groupby("folio").first()[["fexp_eva0_2", "fechanacimientons",
                                       "e4", "m10", "c56", "m8", "numper"]]
    c = (e17.merge(hog, on="folio", how="left")
            .merge(em, on="folio", how="left")
            .merge(pp, on="folio", how="left")
            .merge(herm, on="folio", how="left"))
    fnc = c.fechanacimientons
    if fnc.dtype == object:
        fd = pd.to_datetime(fnc, errors="coerce", dayfirst=True)
    else:
        fd = pd.Timestamp("1582-10-14") + pd.to_timedelta(num(fnc),
                                                          unit="s")
    ym_ns = fd.dt.year * 12 + (fd.dt.month - 1)
    fev = pd.Timestamp("1960-01-01") + pd.to_timedelta(num(c.finicio_tn),
                                                       unit="D")
    ym_fi = (fev.dt.year * 12 + (fev.dt.month - 1)) - num(c.edad_mesesr)
    c["birth_ym"] = ym_ns.fillna(ym_fi)
    expu = c.birth_ym.between(2006 * 12, 2010 * 12 + 1)
    ctrl = c.birth_ym >= 2011 * 12
    c = c[expu | ctrl].copy()
    c["affected"] = expu[expu | ctrl].astype(float).values
    c["geo"] = num(c.estrato)
    c["edad_meses"] = num(c.edad_mesesr)
    c["tvip"] = num(c.tvip_ps)
    c["cbcl"] = num(c.cbcl2_pt_inter_t)
    c["w"] = num(c.fexp_eva0_2)
    c["wave"] = 2017
    c56v = num(c.c56).where(lambda s: s < 25)
    m8v = num(c.m8).where(lambda s: s < 25)
    c["n_hijos"] = c56v.fillna(m8v + 1).fillna(num(c.hermanos) + 1)
    c["educ_madre"] = num(c.e4).fillna(num(c.m10))
    c.loc[c.educ_madre >= 88, "educ_madre"] = np.nan
    c["hh_size"] = num(c.numper)
    for v in ("mh_madre", "mh_padre", "mh_ofam"):
        c[v] = np.nan
    c["cohorte"] = (c.birth_ym // 12).astype("Int64")
    c["region"] = (c.geo // 1000).astype("Int64")
    c["EQ"] = num(c.region).isin(p10.EQ_REGIONS).astype(float)
    c["AffEq"] = c.affected * c.EQ
    c["mujer"] = (num(c.sexo) == 2).astype(float).where(c.sexo.notna())
    c["mh_miss"] = 1.0
    for v in ("mh_madre", "mh_padre", "mh_ofam"):
        c[v] = 0.0
    c["padre_presente"] = c.padre_presente.fillna(0.0)
    s = num(c.tvip)
    g = s.groupby(num(c.edad_meses) // 12)
    c["z_tvip"] = (s - g.transform("mean")) / g.transform("std")
    s = num(c.cbcl)
    g = s.groupby(num(c.edad_meses) // 12)
    c["z_cbcl"] = -(s - g.transform("mean")) / g.transform("std")
    return c


def prepara(df):
    df = df.copy()
    pga = pd.read_csv("data/processed/pga_comuna.csv")[["cut", "pga"]]
    df = df.merge(pga, left_on="geo", right_on="cut", how="left")
    df["edadq"] = (2010 * 12 + 1) - df.birth_ym
    for lo, hi, lab in BINS:
        df[f"A{lo}"] = (df.affected * df.EQ
                        * df.edadq.between(lo, hi).astype(float))
    df["AffDosis"] = df.affected * df.pga / 10.0
    return df


def ajusta(df, y, terminos, sample=None, tendencias=False):
    d = df if sample is None else df[sample(df)]
    d = d.dropna(subset=[y, "geo", "w", "cohorte"]).copy()
    d = d[d.w > 0]
    d["com"] = d.geo.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    d["ola"] = d.wave.astype(str)
    d["t"] = num(d.cohorte)
    f = f"{y} ~ {' + '.join(terminos)} + C(com) + C(coh)"
    if d.ola.nunique() > 1:
        f += " + C(ola)"
    xs = []
    for v in p10.XV:
        if d[v].isna().all():
            continue
        if d[v].isna().any():
            d[f"{v}_mi"] = d[v].isna().astype(float)
            d[v] = d[v].fillna(d[v].median())
            xs += [v, f"{v}_mi"]
        else:
            xs.append(v)
    f += " + " + " + ".join(xs)
    if tendencias:
        f += " + C(com):t"
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d["com"]})
    return {k: (float(r.params[k]), float(r.bse[k]), float(r.pvalues[k]))
            for k in terminos}, int(r.nobs)


def cohortes():
    b24 = prepara(base24())
    b17 = prepara(base17())
    folios24 = set(b24.loc[b24.affected == 1, "folio"])
    for etiqueta, base in (("2024 (expuestos a los 15-18 frente a "
                            "concebidos después, medidos en 2017)", b24),
                           ("2017 (expuestos a los 7-11 frente a "
                            "concebidos después, ambos en 2017)", b17)):
        log(f"\n## 2. Concebidos después como comparación: {etiqueta}")
        for y in ("z_tvip", "z_cbcl"):
            tot, n = ajusta(base, y, ["AffEq"])
            log(f"- {y}, efecto total: {fmt(*tot['AffEq'])}; N={n}")
            if base is b17:
                bal, nb = ajusta(base, y, ["AffEq"], sample=lambda x: (
                    (x.affected == 0) | x.folio.isin(folios24)))
                log(f"  mismos niños que en 2024: {fmt(*bal['AffEq'])}; "
                    f"N={nb}")
            por, n = ajusta(base, y, [f"A{lo}" for lo, _, _ in BINS])
            log(f"  por edad al terremoto: " + "; ".join(
                f"{lab} {fmt(*por[f'A{lo}'])}" for lo, _, lab in BINS))
            for sx, sel in (("chicas", 1.0), ("chicos", 0.0)):
                r, n = ajusta(base, y, ["AffEq"],
                              sample=lambda x, s=sel: x.mujer == s)
                log(f"  {sx}: {fmt(*r['AffEq'])}; N={n}")
            r, n = ajusta(base, y, ["AffDosis"])
            log(f"  dosis, exposición x PGA/10 dentro de la comuna: "
                f"{fmt(*r['AffDosis'])}; N={n}")
            r, n = ajusta(base, y, ["AffEq"], tendencias=True)
            log(f"  con tendencias lineales por comuna: "
                f"{fmt(*r['AffEq'])}; N={n}")


def main():
    log("# Efectos en niveles (scripts/24_niveles.py)")
    intensidad()
    cohortes()
    Path("reports/niveles.md").write_text("\n".join(OUT) + "\n",
                                          encoding="utf-8")
    log("\n-> reports/niveles.md")


if __name__ == "__main__":
    main()
