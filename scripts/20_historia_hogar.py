#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La historia del hogar, puesta a prueba con predicciones fijadas antes de
mirar los datos:

  P1. En 2017 (siete años después del terremoto) los expuestos de bebés en
      zona afectada ya presenciaban más peleas o amenazas en el hogar que
      los expuestos a mayor edad (misma pregunta que en 2024).
  P2. En 2012 y 2017 recibían una disciplina más dura (gritos, amenazas,
      golpes).
  P3. Controlar por haber presenciado peleas reduce la brecha de síntomas
      entre los expuestos de bebés y los de dos años.
  P4. Entre los expuestos a 0-11 meses, el exceso de síntomas en zona
      afectada es mayor en los que tomaban pecho el 27-F (cuidado temprano
      interrumpido).

Mismos adolescentes de la ola 2024 y especificación de la columna 3 de la
Table 3; coeficientes relativos a los expuestos a 0-11 meses.

Salida: reports/historia_hogar.md
Uso:    python3 scripts/20_historia_hogar.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p15", HERE / "15_paper_estimaciones.py")
p15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p15)
num, fit, stars, zg = p15.num, p15.fit, p15.stars, p15.zg
OUT = []
EDADES = [("12-23m", "edad 1"), ("24-35m", "edad 2"), ("36-59m", "3-4")]


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def si(s):
    s = num(s)
    return pd.Series(np.where(s == 1, 1.0, np.where(s == 2, 0.0, np.nan)),
                     index=s.index)


def carga():
    d, _, _ = p15.load_data()
    f17 = "data/interim/2017/Base_Cuidador_Principal_ELPI_III(STATA)_241010.dta"
    c17 = ["folio", "pc29a"] + [f"pc27{c}" for c in "cdfghijkn"]
    r17, _ = pyreadstat.read_dta(f17, usecols=c17, encoding="latin1")
    r17["folio"] = num(r17.folio).astype("int64")
    r17 = r17.dropna(subset=["pc29a"])
    var = r17.groupby("folio").pc29a.nunique()
    log(f"2017: {len(r17)} filas, {r17.folio.nunique()} folios; folios con "
        f"respuestas distintas a pc29a: {(var > 1).sum()}")
    r17 = r17.drop_duplicates("folio").set_index("folio")
    x = pd.DataFrame(index=r17.index)
    x["peleas17"] = si(r17.pc29a)
    fis = pd.concat([si(r17[f"pc27{c}"]) for c in "cfgijk"], axis=1)
    psi = pd.concat([si(r17[f"pc27{c}"]) for c in "dhn"], axis=1)
    x["golpes17"] = fis.max(axis=1).where(fis.notna().any(axis=1))
    x["grito17"] = psi.max(axis=1).where(psi.notna().any(axis=1))

    e12, _ = pyreadstat.read_dta("data/interim/2012/Entrevistada_2012.dta",
                                 usecols=["folio", "f20c", "f20e", "f20h"])
    e12["folio"] = num(e12.folio).astype("int64")
    e12 = e12.drop_duplicates("folio").set_index("folio")
    y = pd.DataFrame(index=e12.index)
    for v, k in (("f20c", "grito12"), ("f20e", "amenaza12"),
                 ("f20h", "pega12")):
        s = num(e12[v])
        y[k] = np.where(s.between(1, 4), (s >= 2).astype(float), np.nan)

    lac, _ = pyreadstat.read_dta("data/interim/2012/Entrevistada_2012.dta",
                                 usecols=["folio", "b30", "b32"])
    lac["folio"] = num(lac.folio).astype("int64")
    lac = lac.drop_duplicates("folio").set_index("folio")
    b30, b32 = num(lac.b30), num(lac.b32)
    meses = pd.Series(np.nan, index=lac.index)
    meses[b30 == 3] = 0.0
    meses[b30.isin([1, 2])] = b32.where(~b32.isin([88, 99]))
    meses[b30 == 2] = 990.0
    y["meses_pecho"] = meses

    ev, _ = pyreadstat.read_dta("data/interim/2024/Base evaluaciones Stata.dta",
                                usecols=["folio", "aces_2"])
    ev["folio"] = num(ev.folio).astype("int64")
    ev = ev.drop_duplicates("folio").set_index("folio")
    z = pd.DataFrame({"peleas24": si(ev.aces_2)})
    return (d.merge(x.reset_index(), on="folio", how="left")
             .merge(y.reset_index(), on="folio", how="left")
             .merge(z.reset_index(), on="folio", how="left"))


def fila(d, y, lab, sample=None, extra=None):
    r = fit(d, y, 3, sample=sample, extra_x=extra)
    dd = d if sample is None else d[sample(d)]
    cel = " | ".join(f"{e} {r['b'][k][0]:+.3f}{stars(r['b'][k][2])} "
                     f"(p={r['b'][k][2]:.3f})" for k, e in EDADES)
    log(f"- {lab}: media {dd[y].mean():.3f} | {cel} | N={r['n']}")
    return r


def main():
    d = carga()
    log("\n# La historia del hogar (scripts/20_historia_hogar.py)")
    log("Coeficientes relativos a los expuestos a 0-11 meses. Si la "
        "historia es cierta, los de mayor edad salen NEGATIVOS en peleas y "
        "disciplina dura (los bebés, más).")
    log("\n## P1. Presenció peleas o amenazas en el hogar")
    fila(d, "peleas17", "2017, a los 7-11 años")
    fila(d, "peleas24", "2024, a los 15-18 años")
    log("\n## P2. Disciplina dura")
    fila(d, "grito12", "2012, la madre le grita al menos a veces")
    fila(d, "amenaza12", "2012, la madre lo amenaza al menos a veces")
    fila(d, "pega12", "2012, la madre le pega al menos a veces")
    fila(d, "grito17", "2017, le gritó, insultó o amenazó")
    fila(d, "golpes17", "2017, lo sacudió o golpeó")
    log("\n## P3. Síntomas PHQ-4 con y sin controlar por las peleas")
    base = d.dropna(subset=["peleas17", "peleas24"])
    r0 = fila(base, "z_phq4", "PHQ-4, misma muestra, sin control")
    r1 = fila(base, "z_phq4", "PHQ-4, controlando peleas 2017 y 2024",
              extra=["peleas17", "peleas24"])
    b0, b1 = -r0["b"]["24-35m"][0], -r1["b"]["24-35m"][0]
    log(f"Brecha bebés frente a dos años: {b0:.3f} sin control y {b1:.3f} "
        f"con control ({100 * (1 - b1 / b0):.0f}% menos)")
    log("\n## P4. Bebés (0-11 meses): ¿más síntomas si tomaban pecho el 27-F?")
    b = d[(d.bin == "0-11m")].dropna(subset=["meses_pecho"]).copy()
    b["pecho"] = (b.meses_pecho >= b.edadq_m).astype(float)
    b["EQxpecho"] = b.EQ * b.pecho
    log(f"Tomaban pecho el 27-F: {b.pecho.mean():.3f} (N={len(b)})")
    for y, lab in (("z_phq4", "PHQ-4 (z)"), ("gad2_bin", "GAD-2 positivo")):
        for g, sel in (("todos", None), ("chicas", 1)):
            bb = b if sel is None else b[b.mujer == sel]
            bb = bb.dropna(subset=[y, "w", "estrato", "cohorte"])
            bb = bb[bb.w > 0].copy()
            bb["est"] = bb.estrato.astype(int).astype(str)
            bb["coh"] = bb.cohorte.astype(int).astype(str)
            rhs = " + ".join(["EQxpecho", "pecho", "C(est)", "C(coh)"]
                             + p15.xt(bb, p15.X_PRE) + p15.xt(bb, p15.X_POST))
            r = smf.wls(f"{y} ~ {rhs}", data=bb, weights=bb.w).fit(
                cov_type="cluster", cov_kwds={"groups": bb.est})
            log(f"- {lab}, {g}: zona afectada x pecho "
                f"{r.params['EQxpecho']:+.3f}{stars(r.pvalues['EQxpecho'])} "
                f"(ee {r.bse['EQxpecho']:.3f}, p={r.pvalues['EQxpecho']:.3f}); "
                f"N={int(r.nobs)}")
    log("\n## P4b. Placebos de la interacción zona afectada x pecho")
    def inter(bb, y):
        bb = bb.dropna(subset=[y, "w", "estrato", "cohorte"])
        bb = bb[bb.w > 0].copy()
        bb["est"] = bb.estrato.astype(int).astype(str)
        bb["coh"] = bb.cohorte.astype(int).astype(str)
        bb["pecho"] = (bb.meses_pecho >= bb.edadq_m).astype(float)
        bb["EQxpecho"] = bb.EQ * bb.pecho
        rhs = " + ".join(["EQxpecho", "pecho", "C(est)", "C(coh)"]
                         + p15.xt(bb, p15.X_PRE) + p15.xt(bb, p15.X_POST))
        r = smf.wls(f"{y} ~ {rhs}", data=bb, weights=bb.w).fit(
            cov_type="cluster", cov_kwds={"groups": bb.est})
        return r.params["EQxpecho"], r.bse["EQxpecho"], r.pvalues["EQxpecho"], int(r.nobs), bb.pecho.mean()
    bb = d[(d.bin == "0-11m")].dropna(subset=["meses_pecho"])
    for y, lab in (("z_peso", "peso al nacer (z)"), ("z_talla", "talla al nacer (z)"),
                   ("z_gest", "semanas de gestación (z)")):
        b_, se_, p_, n_, _ = inter(bb, y)
        log(f"- bebés, {lab}: {b_:+.3f}{stars(p_)} (ee {se_:.3f}, p={p_:.3f}); N={n_}")
    for y, lab in (("educ_madre10", "escolaridad de la madre 2010"),
                   ("edad_madre10", "edad de la madre 2010")):
        bb2 = bb.copy()
        bb2["pecho"] = (bb2.meses_pecho >= bb2.edadq_m).astype(float)
        bb2["EQxpecho"] = bb2.EQ * bb2.pecho
        bb2 = bb2.dropna(subset=[y, "w", "estrato"])
        bb2 = bb2[bb2.w > 0].copy()
        bb2["est"] = bb2.estrato.astype(int).astype(str)
        r = smf.wls(f"{y} ~ EQxpecho + pecho + C(est)", data=bb2, weights=bb2.w).fit(
            cov_type="cluster", cov_kwds={"groups": bb2.est})
        log(f"- bebés, {lab}: {r.params['EQxpecho']:+.3f}{stars(r.pvalues['EQxpecho'])} "
            f"(p={r.pvalues['EQxpecho']:.3f})")
    log("\n## P4c. La misma interacción a otras edades (PHQ-4)")
    for binl, lab in (("0-11m", "0-11 meses"), ("12-23m", "1 año"),
                      ("24-35m", "2 años")):
        bb = d[(d.bin == binl)].dropna(subset=["meses_pecho"])
        b_, se_, p_, n_, m_ = inter(bb, "z_phq4")
        log(f"- {lab}: tomaban pecho {m_:.2f} | zona afectada x pecho "
            f"{b_:+.3f}{stars(p_)} (ee {se_:.3f}, p={p_:.3f}); N={n_}")
    log("\n## Chicas")
    chicas = lambda x: x.mujer == 1
    fila(d, "peleas17", "2017, chicas", sample=chicas)
    fila(d, "peleas24", "2024, chicas", sample=chicas)
    log("\n## Chicos")
    chicos = lambda x: x.mujer == 0
    fila(d, "peleas17", "2017, chicos", sample=chicos)
    fila(d, "peleas24", "2024, chicos", sample=chicos)
    Path("reports/historia_hogar.md").write_text("\n".join(OUT) + "\n",
                                                 encoding="utf-8")
    log("\n-> reports/historia_hogar.md")


if __name__ == "__main__":
    main()
