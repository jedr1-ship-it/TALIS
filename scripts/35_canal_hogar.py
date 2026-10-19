#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Cambió el hogar distinto según la edad del hijo? ¿Qué parte de la brecha
de cada grupo explica?

El hogar se mide después del terremoto y antes de los síntomas, en 2012 y
2017, casi todo con lo que reporta la madre o el cuidador. Siete índices,
fijados antes de estimar y orientados de forma que más alto = peor. El
estrés de la madre no entra: es el segundo mecanismo y se estudia aparte
(scripts/34_estres_madre.py).

  conflicto en casa     le grita, lo amenaza o le pega en 2012; presenció
                        peleas, lo zamarreó o golpeó, le gritó o insultó en
                        2017
  falta de recursos     ingreso per cápita del hogar en 2012 y 2017 (signo
                        cambiado) y vivienda destruida o con daños mayores
  padre fuera del hogar el padre no vive en el hogar, 2012 y 2017
  madre sin empleo      la madre no trabajó la semana anterior, 2012 y 2017
  hacinamiento          personas por dormitorio en 2012; categoría de
                        hacinamiento en 2017
  poca estimulación     la madre le lee y le canta (2012), el cuidador le
                        lee y le cuenta cuentos (2017) y libros infantiles
                        en casa (2012 y 2017), con signo cambiado
  barrio inseguro       cuánto de inseguro ve el niño su barrio y la calle
                        (2017)

  1. Perfil de cada índice por edad al terremoto (los grupos del paper:
     6-11 meses, 1 año y 3-4 años frente a 2 años), zona afectada menos no
     afectada. Si es plano, el golpe al hogar fue igual para todas las
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
INDICES = ["conflicto", "recursos", "padre_fuera", "sin_empleo",
           "hacinamiento", "estimulacion", "barrio"]
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
    hg = lee("data/interim/2012/Hogar_2012.dta",
             ["folio", "i2", "k1", "k2", "k3"])
    i2 = num(hg.i2)
    h["padre_fuera12"] = 1.0 - hg.assign(p=i2.isin([2, 4])).groupby(
        "folio").p.max().astype(float)
    madre = hg[i2.isin([1, 3])].drop_duplicates("folio").set_index("folio")
    k1, k2, k3 = num(madre.k1), num(madre.k2), num(madre.k3)
    trabaja = (k1 == 1) | k2.between(1, 6) | (k3 == 1)
    h["sin_empleo12"] = (1.0 - trabaja.astype(float)).where(k1.isin([1, 2]))
    e2 = lee("data/interim/2012/Entrevistada_2012.dta",
             ["folio", "m5a", "f21a_m_t", "f21c_m_t"])
    e2 = e2.drop_duplicates("folio").set_index("folio")
    h["hacina12"] = h.n / num(e2.m5a).where(lambda s: s.between(0, 20)).clip(
        lower=1)
    h["lee12"] = num(e2.f21a_m_t).where(lambda s: s.between(1, 4))
    h["canta12"] = num(e2.f21c_m_t).where(lambda s: s.between(1, 4))
    ev = lee("data/interim/2012/Evaluaciones_2012.dta",
             ["folio", "hm1_13", "hm2_15"]).drop_duplicates("folio")
    ev = ev.set_index("folio")
    h["libros12"] = num(ev.hm1_13).where(lambda s: s >= 0).fillna(
        num(ev.hm2_15).where(lambda s: s >= 0))
    c = lee("data/interim/2017/Base Cuidador Principal ELPI III (SPSS).sav",
            ["folio", "ytotcorh", "pc29a", "h1", "o1", "o2", "o3",
             "hacinamiento", "cn4f_cp", "cn4g_cp", "pc35"]
            + [f"pc27{k}" for k in "cdfghijkn"], sav=True)
    g = c.groupby("folio")
    c17 = pd.DataFrame({"y": g.ytotcorh.max(), "n": g.size()})
    c17["log_ing17"] = np.log(c17.y.where(c17.y > 0) / c17.n)
    h1 = num(c.h1)
    c17["padre_fuera17"] = 1.0 - c.assign(p=h1.isin([3, 5])).groupby(
        "folio").p.max().astype(float)
    m17 = c[h1.isin([2, 4])].drop_duplicates("folio").set_index("folio")
    o1 = num(m17.o1)
    tr = (o1 == 1) | (num(m17.o2) == 1) | (num(m17.o3) == 1)
    c17["sin_empleo17"] = (1.0 - tr.astype(float)).where(o1.isin([1, 2]))
    c17["hacina17"] = g.hacinamiento.max().where(lambda s: s.between(1, 4))
    for v, k in (("cn4f_cp", "lee17"), ("cn4g_cp", "cuentos17")):
        c17[k] = g[v].max().where(lambda s: s.between(1, 4))
    c17["libros17"] = g.pc35.max().where(lambda s: s.between(1, 3))
    c = c.dropna(subset=["pc29a"]).drop_duplicates("folio").set_index("folio")
    c17["peleas17"] = si(c.pc29a)
    fis = pd.concat([si(c[f"pc27{k}"]) for k in "cfgijk"], axis=1)
    psi = pd.concat([si(c[f"pc27{k}"]) for k in "dhn"], axis=1)
    c17["golpes17"] = fis.max(axis=1).where(fis.notna().any(axis=1))
    c17["grito17"] = psi.max(axis=1).where(psi.notna().any(axis=1))
    n = lee("data/interim/2017/Base Niños y Niñas ELPI III (SPSS).sav",
            ["folio", "a22", "a23"], sav=True).drop_duplicates("folio")
    n = n.set_index("folio")
    c17["barrio17"] = num(n.a22).where(lambda s: s.between(1, 5))
    c17["calle17"] = num(n.a23).where(lambda s: s.between(1, 5))
    d = (d.merge(e[["folio", "grito12", "amenaza12", "pega12"]], on="folio",
                 how="left")
          .merge(h.drop(columns=["y", "n"]).reset_index(), on="folio",
                 how="left")
          .merge(c17.drop(columns=["y", "n"]).reset_index(), on="folio",
                 how="left"))
    d["conflicto"] = indice([d.grito12, d.amenaza12, d.pega12, d.peleas17,
                             d.golpes17, d.grito17], 3)
    d["recursos"] = indice([-d.log_ing12, -d.log_ing17, d.dano12], 2)
    d["padre_fuera"] = indice([d.padre_fuera12, d.padre_fuera17], 1)
    d["sin_empleo"] = indice([d.sin_empleo12, d.sin_empleo17], 1)
    d["hacinamiento"] = indice([d.hacina12, d.hacina17], 1)
    d["estimulacion"] = indice([-d.lee12, -d.canta12, -d.libros12,
                                -d.lee17, -d.cuentos17, -d.libros17], 3)
    d["barrio"] = indice([d.barrio17, d.calle17], 1)
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
