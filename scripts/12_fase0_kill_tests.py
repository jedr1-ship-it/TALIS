#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fase 0 del paper — kill-tests baratos de ideas candidatas.

Cada test responde una sola pregunta: ¿existe la variación y el n para que
la idea viva? Regresiones crudas, sin pulir. Resultados → docs/fase0_ideas.md.

KT-B  Dos terremotos más (Iquique 04-2014 M8.2, regiones XV+I; Illapel
      09-2015 M8.3, región IV): ¿hay n en la ELPI 2017 para replicar la
      ec. (1) de corto plazo de Gillmore en esos sismos?
KT-C  Postnatal de 12→24 semanas (Ley 20.545, oct-2011): ¿cuántos niños del
      refresco 2012 nacen alrededor del corte y llegan con tests a 2017?
KT-F  ¿Existen medidas de salud mental MATERNA en 2010/2012 (para la idea
      de transmisión intergeneracional)? — grep de etiquetas.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf
import warnings

warnings.simplefilter("ignore")
INT = Path("data/interim")


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


def zby(s, g):
    m, sd = s.groupby(g).transform("mean"), s.groupby(g).transform("std")
    return (s - m) / sd


def base17():
    ro = sav(INT / "2017/Base Cuidador Principal ELPI III (SPSS).sav",
             ["folio", "fechanacimientons", "idregion", "idcomuna"])
    # la fecha de nacimiento del niño seleccionado aparece UNA vez por folio
    # (en la fila de la entrevista, no en la fila h1==1): primer no-nulo.
    ni = ro.groupby("folio", as_index=False).first()
    print("KT-B/C base: filas roster", len(ro), "| folios:", len(ni))
    bd = pd.to_datetime(ni.fechanacimientons, errors="coerce")
    ni["birth_ym"] = bd.dt.year * 12 + (bd.dt.month - 1)
    ni["birth_y"], ni["birth_m"] = bd.dt.year, bd.dt.month
    ev = dta(INT / "2017/Base Evaluaciones ELPI III.dta",
             ["folio", "edad_mesesr", "tvip_ps", "battelle_pt_total",
              "cbcl1_pt_inter_t"]).drop_duplicates("folio")
    d = ni.merge(ev, on="folio", how="left")
    ed = num(d.edad_mesesr) // 12
    d["z_bat"] = zby(num(d.battelle_pt_total), ed)
    d["z_tvip"] = zby(num(d.tvip_ps), ed)
    d["reg"] = num(d.idregion).astype("Int64")
    print("  con fecha válida:", d.birth_ym.notna().sum(),
          "| nacidos por año:", d.birth_y.value_counts().sort_index().to_dict())
    return d


def ym(y, m):
    return y * 12 + m - 1


def crude_did(d, treat_regs, aff_lo, aff_hi, ctl_lo, ctl_hi, nombre, y):
    s = d[(d.birth_ym.between(aff_lo, aff_hi))
          | (d.birth_ym.between(ctl_lo, ctl_hi))].copy()
    s["aff"] = d.birth_ym.between(aff_lo, aff_hi).astype(float)
    s["tr"] = s.reg.isin(treat_regs).astype(float)
    s["AT"] = s.aff * s.tr
    s = s.dropna(subset=[y, "reg", "idcomuna"])
    s["reg"] = s.reg.astype(int).astype(str)
    s["coh"] = (s.birth_ym // 12).astype(int).astype(str)
    cel = s.groupby(["tr", "aff"]).size().to_dict()
    print(f"  {nombre}: celdas (trat,afect)->n {cel}")
    n_ta = cel.get((1.0, 1.0), 0)
    n_tc = cel.get((1.0, 0.0), 0)
    if min(n_ta, n_tc) < 60:
        print(f"  {nombre}: MUERE por n (afectados trat={n_ta}, "
              f"control trat={n_tc})")
        return
    r = smf.ols(f"{y} ~ AT + aff + C(reg) + C(coh)", data=s).fit(
        cov_type="cluster",
        cov_kwds={"groups": s.idcomuna.astype(int).astype(str)})
    print(f"  {nombre}: β(AT)={r.params['AT']:+.3f} "
          f"(EE {r.bse['AT']:.3f}, p={r.pvalues['AT']:.3f}) "
          f"n={int(r.nobs):,} | comunas={s.idcomuna.nunique()}")


def kt_b(d):
    print("\nKT-B — Iquique 2014 (reg. XV+I) e Illapel 2015 (reg. IV), "
          "outcome Battelle-z 2017 (crudo, sin pesos):")
    crude_did(d, {15, 1}, ym(2010, 4), ym(2014, 12), ym(2015, 1),
              ym(2016, 12), "Iquique-2014", "z_bat")
    crude_did(d, {4}, ym(2011, 9), ym(2016, 6), ym(2016, 7),
              ym(2017, 12), "Illapel-2015", "z_bat")
    for regs, nom in (({15, 1}, "XV+I"), ({4}, "IV")):
        n = (d.reg.isin(regs)).sum()
        print(f"  niños ELPI-2017 en regiones {nom}: {n:,} "
              f"| comunas: {d[d.reg.isin(regs)].idcomuna.nunique()}")


def kt_c(d):
    print("\nKT-C — Ley 20.545 (postnatal 12→24 sem., corte ~oct-2011):")
    f10 = set(dta(INT / "2010/Hogar_2010.dta", ["folio"]).folio)
    f12 = set(dta(INT / "2012/Entrevistada_2012.dta", ["folio"]).folio)
    refresh = f12 - f10
    print(f"  refresco 2012: {len(refresh):,} folios")
    r = d[d.folio.isin(refresh)].copy()
    print(f"  de ellos, en la ola 2017 con fecha: {r.birth_ym.notna().sum():,}")
    w = r[r.birth_y.eq(2011)]
    print("  nacidos 2011 por mes:",
          w.birth_m.value_counts().sort_index().to_dict())
    vent = r[r.birth_ym.between(ym(2011, 7), ym(2011, 12))]
    con_test = vent.z_bat.notna().sum()
    print(f"  ventana jul–dic 2011: n={len(vent)} | con Battelle 2017: "
          f"{con_test} | con TVIP: {vent.z_tvip.notna().sum()}")
    comp = r[r.birth_ym.between(ym(2010, 7), ym(2011, 6))]
    print(f"  cohorte comparación jul-2010–jun-2011: n={len(comp)} | "
          f"con Battelle: {comp.z_bat.notna().sum()}")


def kt_f():
    print("\nKT-F — ¿salud mental MATERNA medida en 2010/2012? "
          "(grep de etiquetas):")
    targets = ["depres", "ansie", "nervi", "estres", "estrés", "ánimo",
               "animo", "tranquil", "psicol", "epds", "salud mental"]
    for p in ["2010/Entrevistada_2010.dta", "2012/Entrevistada_2012.dta",
              "2010/Hogar_2010.dta", "2012/Hogar_2012.dta"]:
        try:
            _, meta = pyreadstat.read_dta(str(INT / p), metadataonly=True)
        except Exception as e:
            print(f"  {p}: no se pudo ({e})")
            continue
        hits = [(v, lab) for v, lab in meta.column_names_to_labels.items()
                if lab and any(t in lab.lower() for t in targets)]
        print(f"  {p}: {len(hits)} matches")
        for v, lab in hits[:12]:
            print(f"    {v}: {lab[:100]}")


def main():
    d = base17()
    kt_b(d)
    kt_c(d)
    kt_f()


if __name__ == "__main__":
    main()
