#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Venía de antes? Las mismas preguntas en 2017 y en 2024.

Si el hogar o el colegio causaran la brecha en salud mental, la diferencia
por edad al terremoto en esas variables tendría que verse antes que los
síntomas. La ELPI hace en 2017, a los 7-11 años, las mismas preguntas que
en 2024, a los mismos niños:

  colegio   ¿Cómo te va en el colegio? y ¿Cuánto te gusta ir al colegio?
            (lo responde el niño; promedio de z, más alto = peor)
  peleas    ¿Ha presenciado peleas o amenazas entre los integrantes del
            hogar? (lo responde el cuidador; 0/1)
  síntomas  CBCL en 2017 (lo responde el cuidador) y PHQ-4 en 2024 (lo
            responde el adolescente); no es la misma escala

  1. Perfil por edad frente a los expuestos con dos años, zona afectada
     menos no afectada, en 2017 y en 2024, con los mismos niños en las dos
     olas. Todos y chicas.
  2. Mediación: brecha en PHQ-4 con y sin controlar por colegio y peleas,
     medidos en 2017 y, aparte, en 2024. Misma muestra.

Salida: reports/orden_temporal.md y reports/orden_temporal.csv
Uso:    python3 scripts/32_orden_temporal.py
"""
import importlib.util
import warnings
from pathlib import Path

import pandas as pd
import pyreadstat

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p30", HERE / "30_indices_mediacion.py")
p30 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p30)
p15, p19 = p30.p15, p30.p19
num, stars, z, fmt = p15.num, p15.stars, p30.z, p30.fmt
EDADES = p30.EDADES
GRUPOS = (("todos", None), ("chicas", lambda x: x.mujer == 1))
MEDIDAS = (("colegio", "colegio17", "colegio24"),
           ("peleas", "peleas17", "peleas24"),
           ("síntomas", "z_cbcl17", "z_phq4"))
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def rango(s, lo, hi):
    s = num(s)
    return s.where(s.between(lo, hi))


def carga():
    d = p19.construye()
    n17, _ = pyreadstat.read_sav(
        "data/interim/2017/Base Niños y Niñas ELPI III (SPSS).sav",
        usecols=["folio", "c2_a", "c5"])
    n17["folio"] = num(n17.folio).astype("int64")
    n17 = n17.drop_duplicates("folio")
    c17 = pd.concat([z(rango(n17.c2_a, 1, 5)), z(rango(n17.c5, 1, 5))],
                    axis=1)
    n17["colegio17"] = c17.mean(axis=1).where(c17.notna().all(axis=1))
    r17, _ = pyreadstat.read_sav(
        "data/interim/2017/Base Cuidador Principal ELPI III (SPSS).sav",
        usecols=["folio", "pc29a"])
    r17["folio"] = num(r17.folio).astype("int64")
    r17 = r17.dropna(subset=["pc29a"]).drop_duplicates("folio")
    r17["peleas17"] = p19.si(r17.pc29a)
    d = (d.merge(n17[["folio", "colegio17"]], on="folio", how="left")
          .merge(r17[["folio", "peleas17"]], on="folio", how="left"))
    d["colegio17"] = z(d.colegio17)
    c24 = pd.concat([z(d.le_va), z(d.gusta)], axis=1)
    d["colegio24"] = z(-c24.mean(axis=1).where(c24.notna().all(axis=1)))
    d["peleas24"] = d.aces_peleas
    return d


def perfil(d, y, sample=None, extra=None):
    r = p15.fit(d, y, 3, sample=sample, extra_x=extra, keep_model=True)
    return p19.frente_a_dos(r), r["n"]


def main():
    log("# ¿Venía de antes? Mismas preguntas en 2017 y 2024 "
        "(scripts/32_orden_temporal.py)")
    d = carga()
    filas = []
    log("\n## 1. Perfil por edad frente a los expuestos con dos años")
    log("Zona afectada menos no afectada; los mismos niños en las dos olas. "
        "Colegio y síntomas en DE, peleas en proporción; más alto = peor.")
    for grupo, sx in GRUPOS:
        log(f"\n{grupo}")
        for medida, v17, v24 in MEDIDAS:
            def muestra(x, sx=sx, v17=v17, v24=v24):
                ok = x[v17].notna() & x[v24].notna()
                return ok if sx is None else ok & sx(x)
            for ola, v in (("2017", v17), ("2024", v24)):
                b, n = perfil(d, v, muestra)
                log(f"- {medida} {ola} ({v}): " + " | ".join(
                    f"{lab} {fmt(b[k])}" for k, lab in EDADES) + f" | N={n}")
                for k, _ in EDADES:
                    filas.append({"grupo": grupo, "medida": medida,
                                  "ola": ola, "edad": k, "b": b[k][0],
                                  "se": b[k][1], "p": b[k][2], "n": n})

    log("\n## 2. Mediación: PHQ-4 con y sin colegio y peleas")
    for grupo, sx in GRUPOS:
        cols = ["colegio17", "peleas17", "colegio24", "peleas24"]

        def muestra(x, sx=sx):
            ok = x[cols].notna().all(axis=1)
            return ok if sx is None else ok & sx(x)
        sin, n = perfil(d, "z_phq4", muestra)
        log(f"\n{grupo} (misma muestra, N={n})")
        log("- sin controles: " + " | ".join(
            f"{lab} {fmt(sin[k])}" for k, lab in EDADES))
        for ola, extra in (("2017", cols[:2]), ("2024", cols[2:])):
            con, _ = perfil(d, "z_phq4", muestra, extra=extra)
            log(f"- con colegio y peleas de {ola}: " + " | ".join(
                f"{lab} {fmt(con[k])} ({100 * (1 - con[k][0] / sin[k][0]):.0f}"
                f"% explicado)" for k, lab in EDADES))
    pd.DataFrame(filas).to_csv("reports/orden_temporal.csv", index=False)
    Path("reports/orden_temporal.md").write_text("\n".join(OUT) + "\n",
                                                 encoding="utf-8")
    print("-> reports/orden_temporal.md, reports/orden_temporal.csv")


if __name__ == "__main__":
    main()
