#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
El estrés de la madre tras el terremoto: ¿cuánto la golpeó y en qué hijos
deja huella?

La ELPI 2012 pregunta a la madre si tuvo, con posterioridad al terremoto,
insomnio, estrés o angustia, llanto, miedo o pánico y recuerdos traumáticos.

  1. Cuánto la golpeó: proporción de madres con estrés o angustia y número
     de síntomas, zona afectada y no afectada, por edad del hijo al
     terremoto (tramos de scripts/33: 6-17, 18-35, 36-41 y 42-49 meses).
     Perfil frente a las madres de hijos de 18-35 meses.
  2. En qué hijos deja huella: PHQ-4 del adolescente en 2024 según el
     estrés de la madre, con una pendiente para cada tramo de edad del hijo,
     efectos fijos de comuna y cohorte y los controles del paper. Si el
     estrés de la madre se confunde con rasgos de la familia, la pendiente
     debería ser parecida a todas las edades.
  3. Qué parte de la brecha explica: perfil por edad del PHQ-4 con y sin el
     estrés de la madre (y su interacción con cada tramo), misma muestra.
  4. Otras medidas de la madre como contraste: daño de la vivienda,
     depresión diagnosticada y angustia parental (PSI) en 2012.

Salida: reports/estres_madre.md y reports/estres_madre.csv
Uso:    python3 scripts/34_estres_madre.py
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
spec = importlib.util.spec_from_file_location("p33", HERE / "33_ventanas.py")
p33 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p33)
p15 = p33.p15
num, stars, xt = p15.num, p15.stars, p15.xt
TRAMOS = [("6-17", 6, 17), ("18-35", 18, 35), ("36-41", 36, 41),
          ("42-49", 42, 49)]
GRUPOS = (("todos", None), ("chicas", 1), ("chicos", 0))
OUT = []


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
    e, _ = pyreadstat.read_dta(
        "data/interim/2012/Entrevistada_2012.dta", encoding="latin1",
        usecols=["folio", "h3", "b64"] + [f"h4_{i}" for i in range(1, 6)])
    e["folio"] = num(e.folio).astype("int64")
    e = e.drop_duplicates("folio").set_index("folio")
    x = pd.DataFrame(index=e.index)
    x["estres12"] = si(e.h4_2)
    sint = pd.concat([si(e[f"h4_{i}"]) for i in range(1, 6)], axis=1)
    x["n_sint12"] = sint.sum(axis=1).where(sint.notna().all(axis=1))
    h3 = num(e.h3)
    x["dano12"] = np.where(h3.isin([1, 2, 3]), 1.0,
                           np.where(h3.isin([4, 5, 6]), 0.0, np.nan))
    x["depre12"] = si(e.b64)
    ev, _ = pyreadstat.read_dta(
        "data/interim/2012/Evaluaciones_2012.dta", encoding="latin1",
        usecols=["folio", "psi_pb_pd"])
    ev["folio"] = num(ev.folio).astype("int64")
    ev = ev.drop_duplicates("folio").set_index("folio")
    s = num(ev.psi_pb_pd)
    x = x.join(((s - s.mean()) / s.std()).rename("psi_pd12"), how="outer")
    d = d.merge(x.rename_axis("folio").reset_index(), on="folio",
                how="left")
    d = d[d.edadq_m.between(6, 49)].copy()
    d["tramo"] = "18-35"
    for t, lo, hi in TRAMOS:
        d.loc[d.edadq_m.between(lo, hi), "tramo"] = t
    return d


def pendientes(d, y, dosis, sx=None):
    """Una pendiente del PHQ-4 en la dosis para cada tramo de edad del
    hijo, con efectos fijos de comuna y cohorte y los controles."""
    x = d.dropna(subset=[y, dosis, "estrato", "w", "cohorte"]).copy()
    x = x[x.w > 0]
    if sx is not None:
        x = x[x.mujer == sx]
    x["est"] = x.estrato.astype(int).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    ii = []
    for t, _, _ in TRAMOS:
        i = "D" + t.replace("-", "_")
        x[i] = (x.tramo == t).astype(float) * x[dosis]
        ii.append(i)
    rhs = ii + ["C(tramo)", "C(est)", "C(coh)"] + xt(x, p15.X_PRE) \
        + xt(x, p15.X_POST)
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x.est})
    dif = r.t_test(f"D6_17 - D18_35")
    out = {t: (float(r.params[i]), float(r.bse[i]), float(r.pvalues[i]))
           for (t, _, _), i in zip(TRAMOS, ii)}
    out["bebés menos 18-35"] = (float(np.ravel(dif.effect)[0]),
                                float(np.ravel(dif.sd)[0]),
                                float(np.ravel(dif.pvalue)[0]))
    return out, int(r.nobs)


def fmt(t):
    return f"{t[0]:+.3f}{stars(t[2])} (ee {t[1]:.3f}, p={t[2]:.3f})"


def main():
    log("# El estrés de la madre tras el terremoto (scripts/34_estres_madre.py)")
    d = carga()
    filas = []
    log("\n## 1. Cuánto golpeó a las madres, por edad del hijo")
    for t, _, _ in TRAMOS:
        g = d[d.tramo == t].dropna(subset=["estres12", "EQ"])
        a = g[g.EQ == 1]
        n = g[g.EQ == 0]
        log(f"- {t} meses: estrés o angustia {a.estres12.mean():.3f} en zona "
            f"afectada y {n.estres12.mean():.3f} fuera; síntomas "
            f"{a.n_sint12.mean():.2f} y {n.n_sint12.mean():.2f}; N={len(g)}")
        for zona, z in (("afectada", a), ("no afectada", n)):
            filas.append({"panel": "nivel", "grupo": "todos", "tramo": t,
                          "zona": zona, "b": z.estres12.mean(),
                          "se": z.estres12.std() / np.sqrt(len(z)),
                          "p": np.nan, "n": len(z)})
    log("Perfil frente a las madres de hijos de 18-35 meses, zona afectada "
        "menos no afectada (EF de comuna y cohorte, sin controles):")
    for v in ("estres12", "n_sint12", "dano12"):
        b, n = p33.perfil(d, v, None, "ventanas", controles=False)
        log(f"- {v}: " + " | ".join(f"{k} {fmt(t)}" for k, t in b.items())
            + f" | N={n}")

    log("\n## 2. En qué hijos deja huella: PHQ-4 según el estrés de la madre")
    for dosis in ("estres12", "n_sint12"):
        for g, sx in GRUPOS:
            b, n = pendientes(d, "z_phq4", dosis, sx)
            log(f"- {dosis}, {g}: " + " | ".join(
                f"{k} {fmt(t)}" for k, t in b.items()) + f" | N={n}")
            if dosis == "estres12":
                for t, _, _ in TRAMOS:
                    filas.append({"panel": "pendiente", "grupo": g,
                                  "tramo": t, "zona": "", "b": b[t][0],
                                  "se": b[t][1], "p": b[t][2], "n": n})
    log("Contraste con otras medidas de 2012 (todos):")
    for dosis in ("dano12", "depre12", "psi_pd12"):
        b, n = pendientes(d, "z_phq4", dosis)
        log(f"- {dosis}: " + " | ".join(f"{k} {fmt(t)}" for k, t in b.items())
            + f" | N={n}")

    log("\n## 3. Qué parte de la brecha explica")
    base = d[d.estres12.notna()].copy()
    extra = ["estres12"]
    for t, lo, hi in TRAMOS:
        if t != "18-35":
            c = "e_" + t.replace("-", "_")
            base[c] = base.estres12 * base.edadq_m.between(lo, hi)
            extra.append(c)
    for g, sx in GRUPOS[:2]:
        sin = p33.perfil(base, "z_phq4", sx, "ventanas")
        con = p33.perfil(base, "z_phq4", sx, "ventanas", extra=tuple(extra))
        log(f"- {g}, sin el estrés de la madre: " + " | ".join(
            f"{k} {fmt(t)}" for k, t in sin[0].items()) + f" | N={sin[1]}")
        log(f"- {g}, con el estrés de la madre por tramo: " + " | ".join(
            f"{k} {fmt(t)} ({100 * (1 - t[0] / sin[0][k][0]):.0f}% "
            f"explicado)" for k, t in con[0].items()))
    pd.DataFrame(filas).to_csv("reports/estres_madre.csv", index=False)
    Path("reports/estres_madre.md").write_text("\n".join(OUT) + "\n",
                                               encoding="utf-8")
    print("-> reports/estres_madre.md, reports/estres_madre.csv")


if __name__ == "__main__":
    main()
