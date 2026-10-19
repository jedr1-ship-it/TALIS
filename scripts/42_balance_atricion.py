#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿El desequilibrio de la tabla de balance viene de la atrición?

La tabla de balance del apéndice (scripts/41_tablas_apendice.py) usa a
quienes respondieron en 2024. Entre 2010 y 2024 se perdió un 34 % de la
muestra, así que el desequilibrio puede venir de quién se quedó. Aquí, con
los 14.855 niños de la línea base de 2010:

  1. Atrición diferencial: responder en 2024 frente a los grupos de edad al
     terremoto por zona afectada (6-11 meses, 1 año y 3-4 años frente a 2
     años).
  2. Balance en lo fijado antes del terremoto (peso, talla y gestación al
     nacer, educación y edad de la madre) en toda la muestra de 2010 y,
     con la misma especificación, solo en quienes respondieron en 2024.

Los archivos públicos de 2010 no traen comuna, así que los efectos fijos son
de región (la zona afectada se define por región), cohorte y grupo de edad,
sin pesos y con errores robustos (HC1). Chicas y todos.

Salida: reports/balance_atricion.md
Uso:    python3 scripts/42_balance_atricion.py
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
INT = Path("data/interim")
TRAMOS = ([6, 12, 24, 36, 50], ["6-11", "12-23", "ref", "36-49"])
NOMBRE = {"6-11": "6-11 meses", "12-23": "1 año", "36-49": "3-4 años"}
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def num(s):
    return pd.to_numeric(s, errors="coerce")


def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""


def carga():
    a = pd.read_pickle("data/processed/paper_atricion.pkl")
    h, _ = pyreadstat.read_dta(INT / "2010/Hogar_2010.dta",
                               usecols=["folio", "a16", "a18"])
    h["folio"] = num(h.folio).astype("int64")
    nino = h[num(h.a16) == 13].drop_duplicates("folio")
    e, _ = pyreadstat.read_dta(INT / "2010/Entrevistada_2010.dta",
                               usecols=["folio", "g24", "g23", "g20"])
    e["folio"] = num(e.folio).astype("int64")
    e = e.drop_duplicates("folio")
    d = (a.merge(nino[["folio", "a18"]], on="folio", how="left")
          .merge(e, on="folio", how="left"))
    d["mujer"] = (num(d.a18) == 2).astype(float).where(d.a18.notna())
    d["peso"] = num(d.g24).where(lambda s: s.between(0.5, 6.5))
    d["talla"] = num(d.g23).where(lambda s: s.between(30, 65))
    d["gest"] = num(d.g20).where(lambda s: s.between(24, 45))
    d["educ"] = num(d.b2n).where(lambda s: s < 30)
    d["edad_madre"] = num(d.a19).where(lambda s: s < 99)
    for v in ("peso", "talla", "gest"):
        d[f"z_{v}"] = (d[v] - d[v].mean()) / d[v].std()
    d = d[num(d.edadq_m).between(6, 49)].copy()
    d["tramo"] = pd.cut(num(d.edadq_m), TRAMOS[0], right=False,
                        labels=TRAMOS[1]).astype(str)
    d["cohorte"] = (num(d.birth_ym) // 12).astype("Int64").astype(str)
    d["reg"] = num(d.region).astype("Int64").astype(str)
    for t in ("6-11", "12-23", "36-49"):
        d["I" + t.replace("-", "_")] = (d.tramo == t) * num(d.EQ)
    return d


def ajusta(d, y):
    x = d.dropna(subset=[y, "EQ", "reg", "cohorte"])
    ii = ["I6_11", "I12_23", "I36_49"]
    r = smf.ols(f"{y} ~ {' + '.join(ii)} + C(tramo) + C(reg) + C(cohorte)",
                data=x).fit(cov_type="HC1")
    return {t: (r.params[i], r.bse[i], r.pvalues[i])
            for t, i in zip(("6-11", "12-23", "36-49"), ii)}, int(r.nobs)


def linea(lab, res):
    b, n = res
    log(f"- {lab}: " + " | ".join(
        f"{NOMBRE[t]} {v[0]:+.3f}{stars(v[2])} (ee {v[1]:.3f})"
        for t, v in b.items()) + f" | N={n:,}")


def main():
    d = carga()
    log("# ¿El desequilibrio viene de la atrición? "
        "(scripts/42_balance_atricion.py)")
    log("Zona afectada menos no afectada, frente a quienes tenían 2 años; "
        "EF de región, cohorte y grupo de edad; sin pesos; EE robustos.")
    log(f"\nLínea base 2010: {len(d):,} niños con 6-49 meses el 27-F; "
        f"responden en 2024: {d.in2024.mean():.1%}.")
    for g, sel in (("chicas", d.mujer == 1), ("todos", d.mujer.notna())):
        x = d[sel]
        log(f"\n## {g}")
        log("Atrición diferencial (responde en 2024, 0/1):")
        linea("responde en 2024", ajusta(x, "in2024"))
        for nombre, sub in (("toda la muestra de 2010", x),
                            ("solo quienes responden en 2024",
                             x[x.in2024 == 1])):
            log(f"Balance, {nombre}:")
            for y, lab in (("z_peso", "peso al nacer (DE)"),
                           ("z_talla", "talla al nacer (DE)"),
                           ("z_gest", "semanas de gestación (DE)"),
                           ("educ", "educación de la madre (años)"),
                           ("edad_madre", "edad de la madre (años)")):
                linea(lab, ajusta(sub, y))
    Path("reports/balance_atricion.md").write_text("\n".join(OUT) + "\n",
                                                   encoding="utf-8")
    print("-> reports/balance_atricion.md")


if __name__ == "__main__":
    main()
