#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qué explica la brecha en salud mental por edad al terremoto: descomposición
de Gelbach (2016) con los cuatro índices de scripts/30.

Para cada edad a (frente a los expuestos con dos años), la brecha en PHQ-4
sin índices menos la brecha con los cuatro índices es, exactamente, la suma
de las contribuciones de cada índice:

    contribución_k(a) = gamma_k x delta_k(a)

  gamma_k   efecto del índice k sobre el PHQ-4 en la regresión completa
  delta_k   perfil por edad del índice k (zona afectada menos no afectada,
            edad a frente a dos años), con la misma especificación

Misma muestra (casos completos), mismos pesos y controles que el paper.
Intervalos por bootstrap de comunas (se remuestrean comunas completas).
Además de cada índice, el hogar (adversidad + familia + economía) y el
total explicado, cada uno con su intervalo.

Salida: reports/descomposicion.md y reports/descomposicion.csv
Uso:    python3 scripts/31_descomposicion.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import patsy

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p30", HERE / "30_indices_mediacion.py")
p30 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p30)
p15, p19 = p30.p15, p30.p19
INDICES = p30.INDICES
HOGAR = ["adversidad", "familia", "economia"]
EDADES = [("0-11m", "bebés"), ("12-23m", "1 año"), ("36-59m", "3-4 años")]
CONTR = {"0-11m": {"I_24": -1.0}, "12-23m": {"I_12": 1.0, "I_24": -1.0},
         "36-59m": {"I_36": 1.0, "I_24": -1.0}}
B = 500
RNG = np.random.default_rng(27)
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def matrices(d, sample):
    r = p15.fit(d, "z_phq4", 3, sample=sample, keep_model=True)
    dd, f, w = r["_d"], r["_f"], r["_w"]
    y, X = patsy.dmatrices(f, dd, return_type="dataframe")
    M = dd.loc[X.index, INDICES]
    return (y.to_numpy().ravel(), X, M.to_numpy(), w.loc[X.index].to_numpy(),
            dd.loc[X.index, "est"].to_numpy())


def descompone(y, X, M, w, filas=None):
    """Brecha sin índices, con índices y contribución de cada índice, para
    cada edad frente a dos años."""
    if filas is not None:
        y, X, M, w = y[filas], X[filas], M[filas], w[filas]
    sw = np.sqrt(w)
    Xw = X * sw[:, None]
    cols = COLS

    def ols(A, v):
        return np.linalg.lstsq(A, v * sw, rcond=None)[0]
    b0 = ols(Xw, y)
    b1 = ols(np.hstack([Xw, M * sw[:, None]]), y)
    gamma = b1[X.shape[1]:]
    deltas = np.column_stack([ols(Xw, M[:, k]) for k in range(M.shape[1])])

    def contraste(b, edad):
        return sum(c * b[cols.index(n)] for n, c in CONTR[edad].items())
    res = {}
    for edad, _ in EDADES:
        sin = contraste(b0, edad)
        con = contraste(b1, edad)
        contrib = [gamma[k] * contraste(deltas[:, k], edad)
                   for k in range(M.shape[1])]
        res[edad] = (sin, con, contrib)
    return res, gamma


def main():
    global COLS
    log("# Descomposición de la brecha en salud mental "
        "(scripts/31_descomposicion.py)")
    log("Gelbach (2016): brecha sin índices - brecha con índices = suma de "
        "gamma_k x delta_k. Edad frente a dos años, zona afectada menos no "
        f"afectada. Bootstrap de comunas, {B} réplicas.")
    d = p30.indices(p19.construye())
    filas_csv = []
    for grupo, sx in (("todos", None), ("chicas", 1.0)):
        def muestra(x, sx=sx):
            ok = x[INDICES].notna().all(axis=1)
            return ok if sx is None else ok & (x.mujer == sx)
        y, X, M, w, est = matrices(d, muestra)
        COLS = list(X.columns)
        Xn = X.to_numpy()
        res, gamma = descompone(y, Xn, M, w)
        comunas = np.unique(est)
        idx = {c: np.flatnonzero(est == c) for c in comunas}
        boot = []
        for _ in range(B):
            draw = RNG.choice(comunas, size=len(comunas), replace=True)
            filas = np.concatenate([idx[c] for c in draw])
            boot.append(descompone(y, Xn, M, w, filas)[0])
        log(f"\n## {grupo} (N={len(y)})")
        log("gamma, efecto de cada índice sobre el PHQ-4 en la regresión "
            "completa: " + "; ".join(f"{k} {g:+.3f}"
                                     for k, g in zip(INDICES, gamma)))
        for edad, lab in EDADES:
            sin, con, contrib = res[edad]
            bs = np.array([[b[edad][0], b[edad][1]] + list(b[edad][2])
                           for b in boot])
            lo, hi = np.percentile(bs, [2.5, 97.5], axis=0)
            expl = sin - con
            be = bs[:, 0] - bs[:, 1]
            elo, ehi = np.percentile(be, [2.5, 97.5])
            log(f"- {lab}: brecha {sin:+.3f} [{lo[0]:+.3f}, {hi[0]:+.3f}]; "
                f"con índices {con:+.3f} [{lo[1]:+.3f}, {hi[1]:+.3f}]; "
                f"explicado {expl:+.3f} [{elo:+.3f}, {ehi:+.3f}], "
                f"{100 * expl / sin:.0f}%")
            for k, nom in enumerate(INDICES):
                log(f"    {nom}: {contrib[k]:+.3f} [{lo[2 + k]:+.3f}, "
                    f"{hi[2 + k]:+.3f}]")
                filas_csv.append({"grupo": grupo, "edad": edad,
                                  "componente": nom, "valor": contrib[k],
                                  "lo": lo[2 + k], "hi": hi[2 + k]})
            # el hogar: todo lo que no es colegio
            kh = [2 + INDICES.index(i) for i in HOGAR]
            hog = sum(contrib[k - 2] for k in kh)
            hlo, hhi = np.percentile(bs[:, kh].sum(axis=1), [2.5, 97.5])
            log(f"    hogar ({' + '.join(HOGAR)}): {hog:+.3f} "
                f"[{hlo:+.3f}, {hhi:+.3f}]")
            filas_csv.append({"grupo": grupo, "edad": edad,
                              "componente": "hogar", "valor": hog,
                              "lo": hlo, "hi": hhi})
            filas_csv.append({"grupo": grupo, "edad": edad,
                              "componente": "explicado", "valor": expl,
                              "lo": elo, "hi": ehi})
            filas_csv.append({"grupo": grupo, "edad": edad,
                              "componente": "sin explicar", "valor": con,
                              "lo": lo[1], "hi": hi[1]})
            filas_csv.append({"grupo": grupo, "edad": edad,
                              "componente": "brecha", "valor": sin,
                              "lo": lo[0], "hi": hi[0]})
    pd.DataFrame(filas_csv).to_csv("reports/descomposicion.csv", index=False)
    Path("reports/descomposicion.md").write_text("\n".join(OUT) + "\n",
                                                 encoding="utf-8")
    print("-> reports/descomposicion.md, reports/descomposicion.csv")


COLS = []

if __name__ == "__main__":
    main()
