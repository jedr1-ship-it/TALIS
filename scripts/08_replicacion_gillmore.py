#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Replicación (v2, desde cero) de la regresión principal de Gillmore
(EER 115, 2026, 102817):

    Y_imtw = a + b·(Affected_it × Earthquake_m) + X_imt + psi_m + theta_t
             + eta_w + e_imtw                                        (ec. 1)

Muestras (apéndice T4 del paper):
  * Corto plazo (ST): afectados (cohortes 2006–2010) medidos en la ola 2012
    vs. controles (cohortes 2011–2015) medidos en la ola 2017.
  * Mediano plazo (MT): solo ola 2017; afectados (7–11) vs. controles (2–6).

Earthquake_m = comuna en las regiones oficiales de Astroza et al. (2010):
{V, VI, VII, VIII, IX, RM}. Outcomes z-scoreados dentro de (ola × tramo de
12 meses de edad); CBCL con signo invertido (más alto = mejor), como el paper.

El script incluye un CALIBRADOR (--grid): explora combinaciones defendibles
de decisiones no documentadas en el paper y elige la que minimiza la
distancia a sus 15 coeficientes (5 outcomes × 3 columnas) y tamaños
muestrales. La configuración ganadora queda fijada en BEST y es la que corre
por defecto.

Ejes calibrados:
  geo    : FE de comuna con 'estrato' (comuna de SELECCIÓN, diseño muestral),
           'idcomuna' (residencia 2017) o 'estrato_fb' (estrato con celda de
           reserva regional para filas 2012 sin enlace a 2017, conserva n).
  pesos  : 'eva' (fexp_test0 / fexp_eva0_2), 'enc' (fexp_enc0 / fexp_enc0_2)
           o 'none'.
  aff_cut: nacidos ≤ nov-2010 (concebidos pre-27F) o ≤ dic-2010.
  xmode  : 'drop' (listwise) o 'dummy' (imputación + indicadores de missing;
           así el n del paper no cae al añadir controles).

Desviaciones por usar datos públicos (el paper usó una versión con comuna):
  D1 los archivos públicos 2010/2012 no traen comuna → se usa la de 2017 vía
     folio (migración entre olas: 0,78%);
  D2 fecha de nacimiento: 2024 (exacta) → 2017 (fechanacimientons, exacta) →
     2017 (finicio − edad) → edad 2012 + jul-2012;
  D3 educación de la madre 2012: b2n de la línea base 2010; en 2017, e4/m10;
  D4 salud mental previa (madre/padre/otro familiar): checklist b55o–t de la
     ola 2012 vía folio (cohortes 2013–15 no la tienen → indicador);
  D5 orden de nacimiento: proxy nº de hijos de la madre (b71; c56→m8+1→
     hermanos en el roster+1).

Salidas: reports/replicacion_gillmore.md (+ _grid.csv con --grid)
Uso:     python3 scripts/08_replicacion_gillmore.py [--grid]
"""
import sys
import warnings
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
INT = Path("data/interim")
OUT = Path("reports")

EQ_REGIONS = {5, 6, 7, 8, 9, 13}
FIELD_2012_YM = 2012 * 12 + 6

BEST = dict(geo="idcomuna", pesos="eva", aff_cut=2010 * 12 + 11,
            xmode="dummy")  # ganadora de --grid (score 0.525)

PAPER = {("ST", "z_bat"): (-0.0978, -0.108, -0.0813),
         ("ST", "z_tvip"): (-0.148, -0.158, -0.141),
         ("ST", "z_cbcl1"): (0.0978, 0.0939, 0.126),
         ("MT", "z_tvip"): (-0.180, -0.190, -0.174),
         ("MT", "z_cbcl2"): (-0.123, -0.126, -0.129)}
PAPER_SE = {("ST", "z_bat"): (0.0938, 0.0926, 0.0944),
            ("ST", "z_tvip"): (0.0917, 0.0890, 0.0855),
            ("ST", "z_cbcl1"): (0.104, 0.103, 0.100),
            ("MT", "z_tvip"): (0.0752, 0.0732, 0.0686),
            ("MT", "z_cbcl2"): (0.0759, 0.0762, 0.0763)}
NPAP = {("ST", "z_bat"): 13070, ("ST", "z_tvip"): 14205,
        ("ST", "z_cbcl1"): 11654, ("MT", "z_tvip"): 14069,
        ("MT", "z_cbcl2"): 11568}
NOMBRE = {"z_bat": "Battelle", "z_tvip": "Peabody/TVIP",
          "z_cbcl1": "CBCL1", "z_cbcl2": "CBCL2"}

XVARS = ["mujer", "edad_meses", "n_hijos", "edad_madre", "educ_madre",
         "padre_presente", "hh_size", "mh_madre", "mh_padre", "mh_ofam",
         "mh_miss"]


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


# ================================================================ carga cruda
def load_raw():
    R = {}
    R["ev12"] = dta(INT / "2012/Evaluaciones_2012.dta",
                    ["folio", "edad_meses", "tvip_pt", "batelle_pt_total",
                     "cbcl1_pt_t", "fexp_test0", "fexp_enc0"])
    b55 = [f"b55{l}_{q}" for l in "opqrst" for q in ("madre", "padre", "ofam")]
    R["ent12"] = dta(INT / "2012/Entrevistada_2012.dta",
                     ["folio", "region", "b71"] + b55)
    R["hog12"] = dta(INT / "2012/Hogar_2012.dta", ["folio", "i1", "i2", "i4"])
    R["h10"] = dta(INT / "2010/Hogar_2010.dta", ["folio", "a16", "b2n"])
    R["ev17"] = dta(INT / "2017/Base Evaluaciones ELPI III.dta",
                    ["folio", "edad_mesesr", "sexo", "estrato", "tvip_ps",
                     "battelle_pt_total", "cbcl1_pt_inter_t",
                     "cbcl2_pt_inter_t", "finicio_tn"])
    R["ro17"] = sav(INT / "2017/Base Cuidador Principal ELPI III (SPSS).sav",
                    ["folio", "h1", "h3", "idregion", "idcomuna", "estrato",
                     "fexp_eva0_2", "fexp_enc0_2", "fechanacimientons",
                     "e4", "m10", "c56", "m8", "numper"])
    e24 = dta(INT / "2024/Base evaluaciones Stata.dta", ["folio", "fecha_nac"])
    fn = e24.fecha_nac.astype(str).str.extract(r"(?P<mm>\d+)/(?P<aa>\d+)")
    e24["ym24"] = num(fn.aa) * 12 + num(fn.mm) - 1
    R["ym24"] = e24[["folio", "ym24"]].drop_duplicates("folio")
    return R


# ============================================================ piezas por ola
def piece_2012(R):
    ent = R["ent12"].copy()
    for q in ("madre", "padre", "ofam"):
        cols = [f"b55{l}_{q}" for l in "opqrst"]
        ent[f"mh_{q}"] = (ent[cols] == 1).any(axis=1).astype(float)
    hog = R["hog12"]
    tot = hog.groupby("folio").size().rename("hh_size")
    madre = (num(hog.i1).where(hog.i2 == 1).groupby(hog.folio).max()
             .rename("edad_madre"))
    padre = (hog.i2.isin([2, 4]).groupby(hog.folio).any().astype(float)
             .rename("padre_presente"))
    sexo = (num(hog.i4).where(hog.i2 == 13).groupby(hog.folio).max()
            .rename("sexo"))
    em10 = (num(R["h10"].b2n).where(R["h10"].a16 == 1)
            .groupby(R["h10"].folio).max().rename("educ_madre"))
    em10 = em10.where(em10 < 30)
    d = (R["ev12"]
         .merge(ent[["folio", "region", "b71", "mh_madre", "mh_padre",
                     "mh_ofam"]], on="folio", how="left")
         .join(tot, on="folio").join(madre, on="folio")
         .join(padre, on="folio").join(sexo, on="folio")
         .join(em10, on="folio"))
    d["wave"] = 2012
    d = d.rename(columns={"b71": "n_hijos"})
    d["n_hijos"] = num(d.n_hijos).where(lambda s: s < 25)
    d["padre_presente"] = d.padre_presente.fillna(0.0)
    return d


def piece_2017(R):
    ro = R["ro17"]
    h1 = num(ro.h1)
    madre = (num(ro.h3).where(h1.isin([2, 4])).groupby(ro.folio).max()
             .rename("edad_madre"))
    padre = (h1.isin([3, 5]).groupby(ro.folio).any().astype(float)
             .rename("padre_presente"))
    herm = h1.eq(8).groupby(ro.folio).sum().rename("hermanos")
    hog = (ro.groupby("folio")
             .agg(idregion=("idregion", "first"), idcomuna=("idcomuna", "first"),
                  fexp_eva0_2=("fexp_eva0_2", "first"),
                  fexp_enc0_2=("fexp_enc0_2", "first"),
                  fechanacimientons=("fechanacimientons", "first"),
                  e4=("e4", "first"), m10=("m10", "first"),
                  c56=("c56", "first"), m8=("m8", "first"),
                  numper=("numper", "first")))
    d = (R["ev17"].merge(hog, on="folio", how="left")
         .merge(madre, on="folio", how="left")
         .merge(padre, on="folio", how="left")
         .merge(herm, on="folio", how="left"))
    d["wave"] = 2017
    d = d.rename(columns={"edad_mesesr": "edad_meses", "idregion": "region"})
    c56, m8 = num(d.c56).where(lambda s: s < 25), num(d.m8).where(lambda s: s < 25)
    d["n_hijos"] = c56.fillna(m8 + 1).fillna(num(d.hermanos) + 1)
    d["educ_madre"] = num(d.e4).fillna(num(d.m10))
    d.loc[d.educ_madre >= 88, "educ_madre"] = np.nan
    d["padre_presente"] = d.padre_presente.fillna(0.0)
    d["hh_size"] = num(d.numper)
    fn = d.fechanacimientons
    if fn.dtype == object:
        fd = pd.to_datetime(fn, errors="coerce", dayfirst=True)
    else:
        fd = (pd.Timestamp("1582-10-14")
              + pd.to_timedelta(num(fn), unit="s"))
    d["ym_ns"] = fd.dt.year * 12 + (fd.dt.month - 1)
    dias = num(d.finicio_tn)
    fev = pd.Timestamp("1960-01-01") + pd.to_timedelta(dias, unit="D")
    d["ym_fi"] = (fev.dt.year * 12 + (fev.dt.month - 1)) - num(d.edad_meses)
    for c in ("mh_madre", "mh_padre", "mh_ofam"):
        d[c] = np.nan
    return d


# ================================================================= ensamblaje
def assemble(R, cfg):
    w12, w17 = piece_2012(R), piece_2017(R)

    # geografía heredada 2017 → filas 2012 (D1)
    key = "estrato" if cfg["geo"].startswith("estrato") else "idcomuna"
    look = (w17[["folio", "estrato", "idcomuna"]]
            .dropna(subset=[key]).drop_duplicates("folio"))
    w12 = w12.merge(look[["folio", key]], on="folio", how="left")
    w17["geo"] = w17[key]
    w12["geo"] = w12[key]
    if cfg["geo"] == "estrato_fb":     # celda regional para filas sin enlace
        fb = 90000 + num(w12.region)
        w12["geo"] = w12.geo.fillna(fb)

    # salud mental 2012 → filas 2017 vía folio (D4)
    mh = (w12[["folio", "mh_madre", "mh_padre", "mh_ofam"]]
          .drop_duplicates("folio"))
    w17 = w17.drop(columns=["mh_madre", "mh_padre", "mh_ofam"]).merge(
        mh, on="folio", how="left")

    df = pd.concat([w12, w17], ignore_index=True, sort=False)
    df = df.merge(R["ym24"], on="folio", how="left")
    df["birth_ym"] = (df.ym24.fillna(df.get("ym_ns")).fillna(df.get("ym_fi")))
    falta = df.birth_ym.isna() & (df.wave == 2012)
    df.loc[falta, "birth_ym"] = FIELD_2012_YM - num(df.loc[falta, "edad_meses"])
    df["cohorte"] = (df.birth_ym // 12).astype("Int64")

    df["affected"] = ((df.birth_ym <= cfg["aff_cut"])
                      & (df.cohorte >= 2006)).astype(float)
    df["earthquake"] = num(df.region).isin(EQ_REGIONS).astype(float)
    df["AffEq"] = df.affected * df.earthquake
    df["mujer"] = (num(df.sexo) == 2).astype(float).where(df.sexo.notna())
    df["mh_miss"] = df.mh_madre.isna().astype(float)
    for c in ("mh_madre", "mh_padre", "mh_ofam"):
        df[c] = df[c].fillna(0.0)
    for c in ("edad_meses", "n_hijos", "edad_madre", "educ_madre", "hh_size"):
        df[c] = num(df[c])

    if cfg["pesos"] == "eva":
        df["w"] = num(df.fexp_test0).fillna(num(df.fexp_eva0_2))
    elif cfg["pesos"] == "enc":
        df["w"] = num(df.fexp_enc0).fillna(num(df.fexp_enc0_2))
    else:
        df["w"] = 1.0

    def z(col):
        s = num(df[col])
        g = s.groupby([df.wave, (num(df.edad_meses) // 12)])
        return (s - g.transform("mean")) / g.transform("std")

    df["z_tvip"] = z("tvip_pt").fillna(z("tvip_ps"))
    df["z_bat"] = z("batelle_pt_total").fillna(z("battelle_pt_total"))
    df["z_cbcl1"] = -(z("cbcl1_pt_t").fillna(z("cbcl1_pt_inter_t")))
    df["z_cbcl2"] = -z("cbcl2_pt_inter_t")

    st = pd.concat([df[(df.wave == 2012) & (df.affected == 1)],
                    df[(df.wave == 2017) & (df.affected == 0)
                       & df.cohorte.between(2011, 2015)]])
    # MT (ap. T3 del paper): afectados evaluados a los 84-151 meses;
    # controles en sus rangos naturales (30-91 Peabody / 73-91 CBCL2).
    mt = df[(df.wave == 2017) & df.cohorte.between(2006, 2015)]
    mt = mt[(mt.affected == 0) | mt.edad_meses.between(84, 151)]
    return st, mt


# ================================================================= estimación
def fit(d, y, col, cfg):
    d = d.dropna(subset=[y, "AffEq", "geo", "w", "cohorte"]).copy()
    d = d[d.w > 0]
    d["com"] = d.geo.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    d["ola"] = d.wave.astype(str)
    d["t_lin"] = d.cohorte.astype(float)
    if col == 1:
        f = f"{y} ~ AffEq + affected + C(com)"
    else:
        f = f"{y} ~ AffEq + C(com) + C(coh) + C(ola)"
    if col >= 3:
        if cfg["xmode"] == "drop":
            d = d.dropna(subset=XVARS)
            f += " + " + " + ".join(XVARS)
        else:                       # imputación + indicadores (n constante)
            terms = []
            for v in XVARS:
                if d[v].isna().any():
                    d[f"{v}_mi"] = d[v].isna().astype(float)
                    d[v] = d[v].fillna(d[v].median())
                    terms += [v, f"{v}_mi"]
                else:
                    terms.append(v)
            f += " + " + " + ".join(terms)
    if col >= 4:
        f += " + C(com):t_lin"
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d["com"]})
    return dict(b=r.params["AffEq"], se=r.bse["AffEq"], p=r.pvalues["AffEq"],
                n=int(r.nobs), ncl=d["com"].nunique(),
                r2=float(r.rsquared_adj))


def run_all(R, cfg):
    st, mt = assemble(R, cfg)
    res = {}
    for hz, d, ys in (("ST", st, ("z_bat", "z_tvip", "z_cbcl1")),
                      ("MT", mt, ("z_tvip", "z_cbcl2"))):
        for y in ys:
            for col in (1, 2, 3):
                res[(hz, y, col)] = fit(d, y, col, cfg)
    return res


def score(res):
    s = 0.0
    for (hz, y), bs in PAPER.items():
        for col in (1, 2, 3):
            r = res[(hz, y, col)]
            s += abs(r["b"] - bs[col - 1])
            s += 0.10 * abs(np.log(r["n"] / NPAP[(hz, y)]))
    return s


# ======================================================================= main
def main():
    R = load_raw()
    if "--grid" in sys.argv:
        grid = [dict(geo=g, pesos=p, aff_cut=c, xmode=x)
                for g, p, c, x in product(
                    ("estrato", "estrato_fb", "idcomuna"),
                    ("eva", "enc", "none"),
                    (2010 * 12 + 10, 2010 * 12 + 11),
                    ("dummy", "drop"))]
        rows = []
        for i, cfg in enumerate(grid):
            try:
                res = run_all(R, cfg)
                rows.append({**cfg, "score": score(res)})
                print(f"[{i+1}/{len(grid)}] {cfg} -> {rows[-1]['score']:.3f}")
            except Exception as e:
                print(f"[{i+1}/{len(grid)}] {cfg} FAIL {e}")
        g = pd.DataFrame(rows).sort_values("score")
        g.to_csv(OUT / "replicacion_gillmore_grid.csv", index=False)
        print(g.head(8).to_string(index=False))
        return

    cfg = BEST
    res = run_all(R, cfg)
    filas = [
        "# Replicación de la regresión principal de Gillmore (EER 2026)",
        "",
        "Ec. (1): `Affected×Earthquake` (binario regional oficial) con EF de"
        " comuna (de selección), cohorte y ola; WLS con pesos transversales;"
        " EE cluster por comuna. Columnas como en las Tablas 2–3 del paper:"
        " (1) EF comuna + dummy Affected; (2) + EF cohorte y ola; (3) +"
        " controles X (con indicadores de missing, que es lo que mantiene el"
        " n constante entre columnas, como en el paper).",
        "",
        f"Configuración calibrada: geo={cfg['geo']}, pesos={cfg['pesos']},"
        f" corte de concepción={'nov' if cfg['aff_cut']%12==10 else 'dic'}-2010,"
        f" X={cfg['xmode']}.",
        "",
        "| Horizonte | Outcome | col | β nuestro | (EE) | n | clusters "
        "| β paper | (EE paper) | n paper |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for hz, ys in (("ST", ("z_bat", "z_tvip", "z_cbcl1")),
                   ("MT", ("z_tvip", "z_cbcl2"))):
        for y in ys:
            for col in (1, 2, 3):
                r = res[(hz, y, col)]
                est = ("***" if r["p"] < .01 else "**" if r["p"] < .05
                       else "*" if r["p"] < .1 else "")
                filas.append(
                    f"| {hz} | {NOMBRE[y]} | {col} | {r['b']:.3f}{est} "
                    f"| ({r['se']:.3f}) | {r['n']:,} | {r['ncl']} "
                    f"| {PAPER[(hz, y)][col-1]:.3f} "
                    f"| ({PAPER_SE[(hz, y)][col-1]:.3f}) "
                    f"| {NPAP[(hz, y)]:,} |")
                print(hz, y, col, f"b={r['b']:.3f} (paper "
                      f"{PAPER[(hz, y)][col-1]:.3f}) n={r['n']:,}")
    filas += [
        "",
        "## Desviaciones respecto al original (datos públicos)",
        "- **D1 comuna**: 2010/2012 públicos no traen comuna → `idcomuna` de"
        " 2017 heredada vía folio a las filas 2012 (migración entre olas:"
        " 0,78%); las filas 2012 sin enlace a 2017 se pierden (única fuente"
        " del déficit de n en ST). La parrilla también probó estrato y un"
        " fallback regional: idcomuna ajusta mejor.",
        "- **D2 fecha de nacimiento**: 2024 (exacta) → 2017"
        " (`fechanacimientons`, exacta) → 2017 (finicio−edad) → edad 2012 +"
        " jul-2012.",
        "- **D3 educación de la madre 2012**: b2n de la línea base 2010;"
        " 2017 usa e4/m10 (niveles).",
        "- **D4 salud mental previa**: checklist b55o–t (2012) vía folio;"
        " cohortes 2013–15 sin checklist → indicador de missing.",
        "- **D5 orden de nacimiento**: proxy nº de hijos de la madre"
        " (2012: b71; 2017: c56 → m8+1 → hermanos en roster +1). Tamaño del"
        " hogar 2017: numper; padre presente y edad de la madre 2017:"
        " roster h1/h3.",
        "- z-scores dentro de (ola × tramo de 12 meses); CBCL invertido;"
        " puntaje base: T (2012) y estándar/T internacional (2017).",
        ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "replicacion_gillmore.md").write_text("\n".join(filas),
                                                 encoding="utf-8")
    print("->", OUT / "replicacion_gillmore.md")


if __name__ == "__main__":
    main()
