#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Cambió el hogar distinto según la edad del hijo? ¿Qué parte de la brecha
de cada grupo explica?

El hogar se mide después del terremoto y antes de los síntomas, en 2012 y
2017, casi todo con lo que reporta la madre o el cuidador. Tres índices,
fijados antes de estimar y orientados de forma que más alto = peor:

  estrés de los padres  síntomas de la madre tras el terremoto, depresión
                        diagnosticada y angustia parental (PSI) en 2012;
                        depresión (CES-D) y angustia parental en 2017
  conflicto en casa     le grita, lo amenaza o le pega en 2012; presenció
                        peleas, lo zamarreó o golpeó, le gritó o insultó en
                        2017
  recursos              ingreso per cápita del hogar en 2012 y 2017 (signo
                        cambiado) y vivienda destruida o con daños mayores

  1. Perfil de cada índice por edad al terremoto (tramos de scripts/33:
     6-17, 36-41 y 42-49 meses frente a 18-35), zona afectada menos no
     afectada. Si es plano, el golpe al hogar fue igual para todas las
     edades.
  2. Descomposición de Gelbach (2016) de la brecha en PHQ-4 de cada tramo
     en lo que explica cada índice y lo que queda, con bootstrap de
     comunas. Chicas y todos.

Salida: reports/canal_hogar.md y reports/canal_hogar.csv
Uso:    python3 scripts/35_canal_hogar.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import pyreadstat

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p34", HERE / "34_estres_madre.py")
p34 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p34)
p33, p15 = p34.p33, p34.p15
num, stars, xt, si = p15.num, p15.stars, p15.xt, p34.si
INDICES = ["estres_padres", "conflicto", "recursos"]
TRAMOS = ["6-17", "36-41", "42-49"]
GRUPOS = (("chicas", 1), ("todos", None))
B = 300
RNG = np.random.default_rng(27)
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def z(s):
    s = pd.to_numeric(s, errors="coerce")
    return (s - s.mean()) / s.std()


def indice(cols, minimo):
    m = pd.concat([z(c) for c in cols], axis=1)
    return z(m.mean(axis=1).where(m.notna().sum(axis=1) >= minimo))


def lee(f, cols, sav=False):
    if sav:
        x, _ = pyreadstat.read_sav(f, usecols=cols)
    else:
        x, _ = pyreadstat.read_dta(f, usecols=cols, encoding="latin1")
    x["folio"] = num(x.folio).astype("int64")
    return x


def carga():
    d = p34.carga()
    e = lee("data/interim/2012/Entrevistada_2012.dta",
            ["folio", "f20c", "f20e", "f20h"]).drop_duplicates("folio")
    for v, k in (("f20c", "grito12"), ("f20e", "amenaza12"),
                 ("f20h", "pega12")):
        s = num(e[v])
        e[k] = np.where(s.between(1, 4), (s >= 2).astype(float), np.nan)
    h = lee("data/interim/2012/Hogar_2012.dta", ["folio", "l11_monto"])
    y12 = num(h.l11_monto).where(lambda s: (s > 0) & (s != 99))
    h = pd.DataFrame({"folio": h.folio, "y": y12})
    h = h.groupby("folio").agg(y=("y", "max"), n=("y", "size"))
    h["log_ing12"] = np.log(h.y / h.n)
    c = lee("data/interim/2017/Base Cuidador Principal ELPI III (SPSS).sav",
            ["folio", "ytotcorh", "pc29a"] + [f"pc27{k}" for k in "cdfghijkn"],
            sav=True)
    g = c.groupby("folio")
    c17 = pd.DataFrame({"y": g.ytotcorh.max(), "n": g.size()})
    c17["log_ing17"] = np.log(c17.y.where(c17.y > 0) / c17.n)
    c = c.dropna(subset=["pc29a"]).drop_duplicates("folio").set_index("folio")
    c17["peleas17"] = si(c.pc29a)
    fis = pd.concat([si(c[f"pc27{k}"]) for k in "cfgijk"], axis=1)
    psi = pd.concat([si(c[f"pc27{k}"]) for k in "dhn"], axis=1)
    c17["golpes17"] = fis.max(axis=1).where(fis.notna().any(axis=1))
    c17["grito17"] = psi.max(axis=1).where(psi.notna().any(axis=1))
    ev = lee("data/interim/2017/Base Evaluaciones ELPI III.sav",
             ["folio", "cesd10_pb", "psi_pb_pd"], sav=True)
    ev = ev.drop_duplicates("folio").set_index("folio")
    ev["cesd17"] = num(ev.cesd10_pb).where(lambda s: s >= 0)
    ev["psi_pd17"] = num(ev.psi_pb_pd).where(lambda s: s >= 0)
    d = (d.merge(e[["folio", "grito12", "amenaza12", "pega12"]], on="folio",
                 how="left")
          .merge(h[["log_ing12"]].reset_index(), on="folio", how="left")
          .merge(c17[["log_ing17", "peleas17", "golpes17", "grito17"]]
                 .reset_index(), on="folio", how="left")
          .merge(ev[["cesd17", "psi_pd17"]].reset_index(), on="folio",
                 how="left"))
    d["estres_padres"] = indice([d.n_sint12, d.depre12, d.psi_pd12,
                                 d.cesd17, d.psi_pd17], 2)
    d["conflicto"] = indice([d.grito12, d.amenaza12, d.pega12, d.peleas17,
                             d.golpes17, d.grito17], 3)
    d["recursos"] = indice([-d.log_ing12, -d.log_ing17, d.dano12], 2)
    return d


def matrices(d, sx):
    """y, X y M de la especificación de scripts/33 (tramos agrupados,
    frente a 18-35 meses), en la muestra con los tres índices."""
    x = d.dropna(subset=["z_phq4", "EQ", "estrato", "w", "cohorte",
                         "edadq_m"] + INDICES).copy()
    x = x[(x.w > 0) & x.edadq_m.between(6, 49)]
    if sx is not None:
        x = x[x.mujer == sx]
    bordes, tramos = p33.CORTES["ventanas"]
    x["tramo"] = pd.cut(x.edadq_m, bordes, right=False,
                        labels=tramos).astype(str)
    x["est"] = x.estrato.astype(int).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    ii = ["I" + t.replace("-", "_") for t in TRAMOS]
    for t, i in zip(TRAMOS, ii):
        x[i] = (x.tramo == t).astype(float) * x.EQ
    rhs = ii + ["C(tramo)", "C(est)", "C(coh)"] + xt(x, p15.X_PRE) \
        + xt(x, p15.X_POST)
    y, X = patsy.dmatrices(f"z_phq4 ~ {' + '.join(rhs)}", x,
                           return_type="dataframe")
    cols = [list(X.columns).index(i) for i in ii]
    return (y.to_numpy().ravel(), X.to_numpy(), x.loc[X.index, INDICES]
            .to_numpy(), x.loc[X.index, "w"].to_numpy(),
            x.loc[X.index, "est"].to_numpy(), cols)


def descompone(y, X, M, w, cols):
    sw = np.sqrt(w)
    Xw = X * sw[:, None]

    def ols(A, v):
        return np.linalg.lstsq(A, v * sw, rcond=None)[0]
    b0 = ols(Xw, y)
    b1 = ols(np.hstack([Xw, M * sw[:, None]]), y)
    gamma = b1[X.shape[1]:]
    delta = np.column_stack([ols(Xw, M[:, k]) for k in range(M.shape[1])])
    return np.array([[b0[c], b1[c]] + [gamma[k] * delta[c, k]
                                        for k in range(M.shape[1])]
                     for c in cols])


def main():
    log("# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)")
    d = carga()
    log("Cobertura de los índices: " + "; ".join(
        f"{i} {d[i].notna().mean():.2f}" for i in INDICES))
    filas = []
    log("\n## 1. ¿Cambió el hogar distinto según la edad?")
    log("Zona afectada menos no afectada, frente a 18-35 meses (DE del "
        "índice; más alto = peor).")
    for g, sx in GRUPOS:
        for i in INDICES:
            for ctr in (True, False):
                b, n = p33.perfil(d, i, sx, "ventanas", controles=ctr)
                log(f"- {g}, {i}{'' if ctr else ', sin controles'}: "
                    + " | ".join(f"{t} {v[0]:+.3f}{stars(v[2])} "
                                 f"(ee {v[1]:.3f}, p={v[2]:.3f})"
                                 for t, v in b.items()) + f" | N={n}")
                if ctr:
                    for t, v in b.items():
                        filas.append({"tipo": "perfil", "grupo": g,
                                      "componente": i, "tramo": t,
                                      "valor": v[0], "lo": v[0] - 1.96 * v[1],
                                      "hi": v[0] + 1.96 * v[1], "p": v[2]})
    log(f"\n## 2. Qué parte de la brecha explica el hogar (Gelbach, "
        f"bootstrap de comunas, {B} réplicas)")
    for g, sx in GRUPOS:
        y, X, M, w, est, cols = matrices(d, sx)
        r = descompone(y, X, M, w, cols)
        comunas = np.unique(est)
        idx = {c: np.flatnonzero(est == c) for c in comunas}
        boot = []
        for _ in range(B):
            f = np.concatenate([idx[c] for c in
                                RNG.choice(comunas, len(comunas))])
            boot.append(descompone(y[f], X[f], M[f], w[f], cols))
        boot = np.array(boot)
        log(f"\n{g} (N={len(y)})")
        for j, t in enumerate(TRAMOS):
            sin, con = r[j, 0], r[j, 1]
            bs = boot[:, j, :]
            lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
            ex = bs[:, 0] - bs[:, 1]
            elo, ehi = np.percentile(ex, [2.5, 97.5])
            log(f"- {t}: brecha {sin:+.3f} [{lo[0]:+.3f}, {hi[0]:+.3f}]; "
                f"con el hogar {con:+.3f}; explicado {sin - con:+.3f} "
                f"[{elo:+.3f}, {ehi:+.3f}], {100 * (sin - con) / sin:.0f}%")
            for k, i in enumerate(INDICES):
                log(f"    {i}: {r[j, 2 + k]:+.3f} [{lo[2 + k]:+.3f}, "
                    f"{hi[2 + k]:+.3f}]")
                filas.append({"tipo": "descomp", "grupo": g,
                              "componente": i, "tramo": t,
                              "valor": r[j, 2 + k], "lo": lo[2 + k],
                              "hi": hi[2 + k], "p": np.nan})
            for comp, v, a, b_ in (("brecha", sin, lo[0], hi[0]),
                                   ("sin explicar", con, lo[1], hi[1]),
                                   ("explicado", sin - con, elo, ehi)):
                filas.append({"tipo": "descomp", "grupo": g,
                              "componente": comp, "tramo": t, "valor": v,
                              "lo": a, "hi": b_, "p": np.nan})
    pd.DataFrame(filas).to_csv("reports/canal_hogar.csv", index=False)
    Path("reports/canal_hogar.md").write_text("\n".join(OUT) + "\n",
                                              encoding="utf-8")
    print("-> reports/canal_hogar.md, reports/canal_hogar.csv")


if __name__ == "__main__":
    main()
