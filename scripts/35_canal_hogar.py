#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Cambió el entorno distinto según la edad del hijo? ¿Qué parte de la brecha
de cada grupo explica?

El entorno se mide justo después del terremoto, en la ronda de 2010 (entre
uno y nueve meses después del 27-F), con cuatro índices de lo que el
terremoto puede haber golpeado, orientados de forma que más alto = peor. El estrés de la madre no entra: es el segundo mecanismo y se estudia
aparte (scripts/34_estres_madre.py).

  conflicto en casa     durante la visita de 2010, la madre le grita,
                        muestra hostilidad o le pega (HOME, lo anota el
                        encuestador)
  falta de recursos     ingreso del hogar por persona el mes anterior a la
                        entrevista de 2010, suma de las fuentes de cada
                        integrante (signo cambiado), y vivienda
                        destruida o con daños mayores en el terremoto
                        (pregunta de 2012 sobre el 27-F)
  vivienda hacinada     personas por dormitorio en 2010
  vivienda precaria     en 2010, mediagua, o vivienda cedida o compartida
                        con otro hogar

  1. Perfil de cada índice por edad al terremoto (los grupos del paper:
     6-11 meses, 1 año y 3-4 años frente a 2 años), zona afectada menos no
     afectada. Si es plano, el golpe al entorno fue igual para todas las
     edades.
  2. Descomposición de Gelbach (2016) de la brecha en PHQ-4 de cada tramo
     en lo que explica cada índice y lo que queda, con bootstrap de
     comunas. Chicas y todos. Para no perder la muestra, un índice que falta
     entra como 0 (su media) junto a un indicador de dato faltante; su
     contribución suma la del índice y la del indicador.

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
INDICES = ["conflicto", "recursos", "hacinamiento", "precaria"]
TRAMOS = ["6-11", "12-23", "36-49"]
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
    ev = lee("data/interim/2010/Evaluaciones_2010.dta",
             ["folio", "hm1_9", "hm1_10", "hm1_11"]).drop_duplicates("folio")
    ev = ev.set_index("folio")
    x = {}
    for v, k in (("hm1_9", "grita10"), ("hm1_10", "hostil10"),
                 ("hm1_11", "pega10")):
        s_ = num(ev[v])
        x[k] = (1.0 - s_).where(s_.isin([0, 1]))
    fuentes = [f"d{k}m" for k in range(1, 9)]
    h = lee("data/interim/2010/Hogar_2010.dta", ["folio"] + fuentes)
    m = pd.concat([num(h[c]).where(lambda s_: (s_ >= 0) & (s_ != 99))
                   for c in fuentes], axis=1)
    h["y"] = m.sum(axis=1).where(m.notna().any(axis=1))
    h = h.groupby("folio").agg(y=("y", "sum"), n=("y", "size"),
                               validos=("y", "count"))
    x["log_ing10"] = np.log((h.y / h.n).where((h.validos > 0) & (h.y > 0)))
    e = lee("data/interim/2010/Entrevistada_2010.dta",
            ["folio", "f4", "f6_1", "f7"]).drop_duplicates("folio")
    e = e.set_index("folio")
    x["hacina10"] = h.n / num(e.f6_1).where(
        lambda s_: s_.between(0, 20)).clip(lower=1)
    f4, f7 = num(e.f4), num(e.f7)
    x["mediagua10"] = (f4 == 7).astype(float).where(f4.between(1, 7))
    x["cedida10"] = f7.isin([3, 6]).astype(float).where(f7.between(1, 6))
    x = pd.DataFrame(x)
    x.index.name = "folio"
    d = d.merge(x.reset_index(), on="folio", how="left")
    d["conflicto"] = indice([d.grita10, d.hostil10, d.pega10], 1)
    d["recursos"] = indice([-d.log_ing10, d.dano12], 1)
    d["hacinamiento"] = indice([d.hacina10], 1)
    d["precaria"] = indice([d.mediagua10, d.cedida10], 1)
    return d


def matrices(d, sx):
    """y, X y M de la especificación de scripts/33 (grupos del paper,
    frente a 2 años). M lleva cada índice, con 0 donde falta, y su
    indicador de dato faltante; grupo dice a qué índice pertenece cada
    columna de M."""
    x = d.dropna(subset=["z_phq4", "EQ", "estrato", "w", "cohorte",
                         "edadq_m"]).copy()
    x = x[(x.w > 0) & x.edadq_m.between(6, 49)]
    if sx is not None:
        x = x[x.mujer == sx]
    mcols, grupo = [], []
    for i in INDICES:
        x[i + "_f"] = x[i].fillna(0.0)
        x[i + "_m"] = x[i].isna().astype(float)
        mcols.append(i + "_f")
        grupo.append(i)
        if x[i + "_m"].std() > 0:
            mcols.append(i + "_m")
            grupo.append(i)
    bordes, tramos = p33.CORTES["paper"]
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
    return (y.to_numpy().ravel(), X.to_numpy(), x.loc[X.index, mcols]
            .to_numpy(), x.loc[X.index, "w"].to_numpy(),
            x.loc[X.index, "est"].to_numpy(), cols, np.array(grupo))


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


def agrega(r, grupo):
    """Suma por índice las contribuciones de su valor y de su indicador."""
    contr = np.stack([r[..., 2:][..., grupo == i].sum(axis=-1)
                      for i in INDICES], axis=-1)
    return np.concatenate([r[..., :2], contr], axis=-1)


def main():
    log("# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)")
    d = carga()
    log("Cobertura de los índices: " + "; ".join(
        f"{i} {d[i].notna().mean():.2f}" for i in INDICES))
    filas = []
    log("\n## 1. ¿Cambió el hogar distinto según la edad?")
    log("Zona afectada menos no afectada, frente a 2 años (DE del "
        "índice; más alto = peor).")
    for g, sx in GRUPOS:
        for i in INDICES:
            for ctr in (True, False):
                b, n = p33.perfil(d, i, sx, "paper", controles=ctr)
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
        y, X, M, w, est, cols, grupo = matrices(d, sx)
        r = agrega(descompone(y, X, M, w, cols), grupo)
        comunas = np.unique(est)
        idx = {c: np.flatnonzero(est == c) for c in comunas}
        boot = []
        for _ in range(B):
            f = np.concatenate([idx[c] for c in
                                RNG.choice(comunas, len(comunas))])
            boot.append(agrega(descompone(y[f], X[f], M[f], w[f], cols),
                               grupo))
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
