#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Se sostiene la historia de la lactancia? Batería de robustez de la
interacción zona afectada x tomaba pecho el 27-F, entre los bebés de
6-11 meses (especificación de la prueba P4 de scripts/20).

  A. Definiciones alternativas de lactancia (incluida "alguna vez", que
     no debería mostrar el efecto si lo que importa es el momento).
  B. Interacciones de la zona con la educación de la madre, la
     ruralidad y la cohorte, para absorber heterogeneidad correlacionada
     con la lactancia.
  C. Otros resultados: tamizajes, resiliencia, satisfacción, CBCL 2012,
     2017 y 2024, vocabulario.
  D. Dejando fuera una región afectada cada vez.
  E. Inferencia por aleatorización: se reasigna la condición de zona
     afectada entre comunas, 2.000 veces.
  F. Destete tras el 27-F frente a lactancia continuada, dentro de los que
     tomaban pecho en zona afectada.

Salida: reports/lactancia_robustez.md
Uso:    python3 scripts/25_lactancia_robustez.py
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
    "p22", HERE / "22_figuras_presentacion.py")
p22 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p22)
p15 = p22.p15
num, stars, xt, zg = p15.num, p15.stars, p15.xt, p15.zg
OUT = []
RNG = np.random.default_rng(27)


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(t):
    return f"{t[0]:+.3f}{stars(t[2])} (ee {t[1]:.3f}, p={t[2]:.3f})"


def carga():
    d = p22.carga()
    e12, _ = pyreadstat.read_dta("data/interim/2012/Evaluaciones_2012.dta",
                                 usecols=["folio", "cbcl1_pb_i",
                                          "cbcl1_pb_t", "edad_meses"])
    e12["folio"] = num(e12.folio).astype("int64")
    e12 = e12.drop_duplicates("folio")
    d = d.merge(e12.rename(columns={"edad_meses": "edad12"}), on="folio",
                how="left")
    for c in ("cbcl1_pb_i", "cbcl1_pb_t"):
        s = num(d[c])
        g = s.groupby(num(d.edad12) // 6)
        d[f"z_{c}"] = (s - g.transform("mean")) / g.transform("std")
    lac, _ = pyreadstat.read_dta("data/interim/2012/Entrevistada_2012.dta",
                                 usecols=["folio", "b30"])
    lac["folio"] = num(lac.folio).astype("int64")
    lac = lac.drop_duplicates("folio")
    d = d.merge(lac, on="folio", how="left")
    d["alguna_vez"] = np.where(num(d.b30).isin([1, 2]), 1.0,
                               np.where(num(d.b30) == 3, 0.0, np.nan))
    return d


def bebes(d):
    b = d[d.bin == "0-11m"].dropna(subset=["meses_pecho", "w", "estrato",
                                           "cohorte"]).copy()
    b = b[b.w > 0].copy()
    b["est"] = b.estrato.astype(int).astype(str)
    b["coh"] = b.cohorte.astype(int).astype(str)
    b["reg"] = b.region.astype(int).astype(str)
    b["pecho"] = (b.meses_pecho >= b.edadq_m).astype(float)
    return b


def inter(b, y, trat="pecho", extra=None, ctr=True, eq="EQ"):
    bb = b.dropna(subset=[y, trat]).copy()
    bb["T"] = bb[trat]
    bb["ExT"] = bb[eq] * bb["T"]
    rhs = ["ExT", "T", "C(est)", "C(coh)"]
    if ctr:
        rhs += xt(bb, p15.X_PRE) + xt(bb, p15.X_POST)
    if extra:
        rhs += extra
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=bb, weights=bb.w).fit(
        cov_type="cluster", cov_kwds={"groups": bb.est})
    return (float(r.params["ExT"]), float(r.bse["ExT"]),
            float(r.pvalues["ExT"])), int(r.nobs)


def main():
    d = carga()
    b = bebes(d)
    log("# Robustez de la historia de la lactancia "
        "(scripts/25_lactancia_robustez.py)")
    t, n = inter(b, "z_phq4")
    log(f"\nBase: PHQ-4, zona afectada x tomaba pecho {fmt(t)}; N={n}; "
        f"tomaban pecho {b.pecho.mean():.2f}")

    log("\n## A. Definiciones de lactancia")
    b["pecho_mas1"] = (b.meses_pecho >= b.edadq_m + 1).astype(float)
    b["pecho_mas3"] = (b.meses_pecho >= b.edadq_m + 3).astype(float)
    for trat, lab in (("pecho_mas1", "seguía al menos un mes después"),
                      ("pecho_mas3", "seguía al menos tres meses después"),
                      ("alguna_vez", "alguna vez tomó pecho (no debería)")):
        t, n = inter(b, "z_phq4", trat=trat)
        log(f"- {lab}: {fmt(t)}; N={n}; media {b[trat].mean():.2f}")

    log("\n## B. Heterogeneidad de la zona correlacionada con la lactancia")
    b["EQ_educ"] = b.EQ * num(b.educ_madre10).fillna(
        num(b.educ_madre10).median())
    b["EQ_rural"] = b.EQ * num(b.rural10).fillna(0)
    b["EQ_mujer"] = b.EQ * b.mujer
    for extra, lab in ((["EQ_educ"], "zona x educación de la madre"),
                       (["EQ_rural"], "zona x ruralidad"),
                       (["EQ_mujer"], "zona x sexo"),
                       (["EQ_educ", "EQ_rural", "EQ_mujer",
                         "EQ:C(coh)"], "todas, más zona x cohorte")):
        t, n = inter(b, "z_phq4", extra=extra)
        log(f"- con {lab}: {fmt(t)}; N={n}")

    log("\n## C. Otros resultados (signo: + = peor)")
    b["neg_resil"] = -b.z_resil
    b["neg_sat"] = -b.sat_vida if "sat_vida" in b else np.nan
    for y, lab in (("gad2_bin", "ansiedad, GAD-2 positivo"),
                   ("phq2_bin", "depresión, PHQ-2 positivo"),
                   ("neg_resil", "baja resiliencia (z)"),
                   ("z_cbcl1_pb_i", "CBCL internalizante 2012, a los 2-3 "
                                    "años (z)"),
                   ("z_cbcl1_pb_t", "CBCL total 2012 (z)"),
                   ("z_cbcl17", "CBCL 2017 (z)"),
                   ("z_cbcl", "CBCL 2024 (z)"),
                   ("neg_tvip", "déficit de vocabulario 2024 (z)")):
        if y not in b or b[y].isna().all():
            log(f"- {lab}: no disponible")
            continue
        t, n = inter(b, y)
        log(f"- {lab}: {fmt(t)}; N={n}")

    log("\n## D. Dejando fuera una región afectada")
    for r in (5, 6, 7, 8, 9, 13):
        t, n = inter(b[b.region != r], "z_phq4")
        log(f"- sin la región {r}: {fmt(t)}; N={n}")

    log("\n## E. Inferencia por aleatorización (zona afectada reasignada "
        "entre comunas)")
    obs, _ = inter(b, "z_phq4", ctr=True)
    com = b.estrato.astype(int)
    comunas = np.sort(com.unique())
    zona = b.groupby(com).EQ.first().reindex(comunas).to_numpy()
    sims = []
    for _ in range(2000):
        perm = dict(zip(comunas, RNG.permutation(zona)))
        b["EQp"] = com.map(perm).astype(float)
        t, _ = inter(b, "z_phq4", eq="EQp", ctr=False)
        sims.append(t[0])
    obs_nc, _ = inter(b, "z_phq4", ctr=False)
    sims = np.array(sims)
    p_ri = float(np.mean(np.abs(sims) >= abs(obs_nc[0])))
    log(f"- coeficiente sin controles {obs_nc[0]:+.3f}; p por "
        f"aleatorización {p_ri:.3f} (2.000 permutaciones)")

    log("\n## F. Dentro de los que tomaban pecho en zona afectada")
    a = b[(b.pecho == 1) & (b.EQ == 1)].copy()
    a["destete3"] = (a.meses_pecho <= a.edadq_m + 3).astype(float)
    a = a.dropna(subset=["z_phq4"])
    r = smf.wls("z_phq4 ~ destete3 + C(est) + C(coh) + "
                + " + ".join(xt(a, p15.X_PRE)),
                data=a, weights=a.w).fit(cov_type="cluster",
                                         cov_kwds={"groups": a.est})
    log(f"- destetados en los 3 meses siguientes frente a los que "
        f"siguieron: {r.params['destete3']:+.3f}{stars(r.pvalues['destete3'])}"
        f" (p={r.pvalues['destete3']:.3f}); N={int(r.nobs)}; destetados "
        f"{a.destete3.mean():.2f}")
    Path("reports/lactancia_robustez.md").write_text("\n".join(OUT) + "\n",
                                                     encoding="utf-8")
    log("\n-> reports/lactancia_robustez.md")


if __name__ == "__main__":
    main()
