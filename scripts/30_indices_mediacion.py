#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Qué hay detrás del perfil por edad de la salud mental? Índices por dominio
y mediación.

Los índices se fijan antes de estimar y usan TODAS las variables de cada
dominio, no solo las que salieron significativas en el análisis
exploratorio (un índice hecho solo con esas saldría significativo por
construcción). Todos orientados: más alto = peor.

  adversidad  número de experiencias adversas que reporta el cuidador (z)
  familia     relación con el cuidador, supervisión y actividades en
              familia, que reporta el adolescente (promedio de z, signo
              cambiado)
  colegio     le va bien, le gusta ir, le agradan los profesores y
              satisfacción con el colegio (promedio de z, signo cambiado)
  economia    ingreso per cápita (signo cambiado), problemas de vivienda y
              no tener suficiente para comer (promedio de z)

  1. Asociación: PHQ-4 contra cada índice, con efectos fijos de comuna y
     cohorte y los controles del paper: ¿los que tienen más adversidad
     tienen más síntomas?
  2. Qué pinta el terremoto: perfil por edad de cada índice frente a los
     expuestos con dos años, zona afectada menos no afectada.
  3. Mediación: perfil por edad del PHQ-4 con y sin controlar por los
     índices, en la misma muestra; qué parte de la brecha explican. Todos y
     chicas.

Salida: reports/indices_mediacion.md
Uso:    python3 scripts/30_indices_mediacion.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p19", HERE / "19_exploratorio.py")
p19 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p19)
p15 = p19.p15
fit, xt, stars = p15.fit, p15.xt, p15.stars
EDADES = [("0-11m", "bebés"), ("12-23m", "1 año"), ("36-59m", "3-4 años")]
INDICES = ["adversidad", "familia", "colegio", "economia"]
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(t):
    return f"{t[0]:+.3f}{stars(t[2])} (ee {t[1]:.3f}, p={t[2]:.3f})"


def z(s):
    s = pd.to_numeric(s, errors="coerce")
    return (s - s.mean()) / s.std()


def indices(d):
    d["adversidad"] = z(d.aces)
    fam = pd.concat([z(d.relacion_cuid), z(d.supervision),
                     z(d.tiempo_familia)], axis=1)
    d["familia"] = z(-fam.mean(axis=1).where(fam.notna().sum(axis=1) >= 2))
    col = pd.concat([z(d.le_va), z(d.gusta), z(d.profes),
                     z(d.sat_colegio)], axis=1)
    d["colegio"] = z(-col.mean(axis=1).where(col.notna().sum(axis=1) >= 3))
    eco = pd.concat([z(-d.log_ingreso), z(d.aces_vivienda),
                     z(d.aces_hambre)], axis=1)
    d["economia"] = z(eco.mean(axis=1).where(eco.notna().sum(axis=1) >= 2))
    return d


def perfil(d, y, sample=None, extra=None):
    r = fit(d, y, 3, sample=sample, extra_x=extra, keep_model=True)
    return p19.frente_a_dos(r), r["n"]


def main():
    log("# Índices por dominio y mediación (scripts/30_indices_mediacion.py)")
    d = indices(p19.construye())
    log("Correlaciones entre índices:")
    log(d[INDICES].corr().round(2).to_string())

    log("\n## 1. ¿Los que tienen más adversidad tienen más síntomas?")
    log("PHQ-4 (DE) por cada DE del índice, EF de comuna y cohorte y "
        "controles; cada índice por separado y todos juntos.")
    base = d.dropna(subset=["z_phq4", "w", "estrato", "cohorte"])
    base = base[base.w > 0].copy()
    base["est"] = base.estrato.astype(int).astype(str)
    base["coh"] = base.cohorte.astype(int).astype(str)
    ctr = xt(base, p15.X_PRE) + xt(base, p15.X_POST)
    for ys in ([[i] for i in INDICES] + [INDICES]):
        bb = base.dropna(subset=ys)
        r = smf.wls(f"z_phq4 ~ {' + '.join(ys + ['C(est)', 'C(coh)'] + ctr)}",
                    data=bb, weights=bb.w).fit(
            cov_type="cluster", cov_kwds={"groups": bb.est})
        log(f"- {' + '.join(ys)}: " + "; ".join(
            f"{i} {fmt((r.params[i], r.bse[i], r.pvalues[i]))}" for i in ys)
            + f"; N={int(r.nobs)}")

    log("\n## 2. Qué pinta el terremoto: perfil por edad de cada índice")
    log("Diferencia con los expuestos con dos años, zona afectada menos no "
        "afectada (DE del índice; más alto = peor).")
    for grupo, sample in (("todos", None),
                          ("chicas", lambda x: x.mujer == 1)):
        for i in INDICES:
            b, n = perfil(d, i, sample)
            log(f"- {grupo}, {i}: " + " | ".join(
                f"{lab} {fmt(b[k])}" for k, lab in EDADES) + f" | N={n}")

    log("\n## 3. Mediación: PHQ-4 con y sin los índices")
    for grupo, sx in (("todos", None), ("chicas", 1.0)):
        def muestra(x, sx=sx):
            ok = x[INDICES].notna().all(axis=1)
            return ok if sx is None else ok & (x.mujer == sx)
        sin, n = perfil(d, "z_phq4", muestra)
        log(f"\n{grupo} (misma muestra, N={n})")
        log("- sin índices: " + " | ".join(
            f"{lab} {fmt(sin[k])}" for k, lab in EDADES))
        for extra, nombre in ([([i], i) for i in INDICES]
                              + [(INDICES, "los cuatro")]):
            con, _ = perfil(d, "z_phq4", muestra, extra=list(extra))
            log(f"- con {nombre}: " + " | ".join(
                f"{lab} {fmt(con[k])} ({100 * (1 - con[k][0] / sin[k][0]):.0f}% "
                f"explicado)" for k, lab in EDADES))
    Path("reports/indices_mediacion.md").write_text("\n".join(OUT) + "\n",
                                                    encoding="utf-8")
    print("-> reports/indices_mediacion.md")


if __name__ == "__main__":
    main()
