#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dos ventanas: el perfil de la salud mental por edad al terremoto, en tramos
de seis meses.

Los cuatro tramos del paper (0-11 meses, 1 año, 2 años, 3-4 años) mezclan
edades que, según la teoría, deberían reaccionar distinto. Aquí el PHQ-4 se
estima en tramos de seis meses, frente a los expuestos con 24-35 meses, con
la especificación de la columna 3 de la Table 3:

  1. Tramos de seis meses (6-11, 12-17, 18-23, 36-41 y 42-49 meses; el más
     viejo de la muestra tenía 49 meses). Todos, chicas y chicos.
  2. Tramos agrupados según las dos ventanas: antes de los 18 meses, 36-41
     meses y desde los 42 meses.
  3. Robustez: sin controles y controlando por peso, talla y semanas de
     gestación al nacer.
  4. Placebos: las mismas diferencias en variables fijadas antes del
     terremoto (nacimiento y madre en 2010).

Salida: reports/ventanas.md y reports/ventanas.csv
Uso:    python3 scripts/33_ventanas.py
"""
import importlib.util
import warnings
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p15", HERE / "15_paper_estimaciones.py")
p15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p15)
stars, xt = p15.stars, p15.xt
CORTES = {"seis meses": ([6, 12, 18, 24, 36, 42, 50],
                         ["6-11", "12-17", "18-23", "ref", "36-41", "42-49"]),
          "ventanas": ([6, 18, 36, 42, 50],
                       ["6-17", "ref", "36-41", "42-49"]),
          # los grupos del paper, frente a 2 años; los usan scripts/34-36
          "paper": ([6, 12, 24, 36, 50],
                    ["6-11", "12-23", "ref", "36-49"])}
NACER = ["z_peso", "z_talla", "z_gest"]
GRUPOS = (("todos", None), ("chicas", 1), ("chicos", 0))
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def perfil(d, y, sx=None, corte="seis meses", controles=True, extra=(),
           modelo=False, mes=False):
    """Diferencia zona afectada menos no afectada de cada tramo de edad al
    terremoto, frente a los expuestos con 24-35 meses. Con modelo=True
    devuelve además el ajuste y la muestra (para las tablas del apéndice).
    Con mes=True, efectos fijos de mes de nacimiento en lugar de los de
    tramo y año de nacimiento y de la tendencia en la edad en meses: como
    la fecha del terremoto es la misma para todos, absorben cualquier
    función de la edad al terremoto y de la cohorte."""
    x = d.dropna(subset=[y, "EQ", "estrato", "w", "cohorte", "edadq_m",
                         *extra]).copy()
    x = x[(x.w > 0) & x.edadq_m.between(6, 49)]
    # muestra de análisis: quienes tienen PHQ-4 (9.996 de 10.003), para que
    # ningún resultado sume adolescentes que no están en la Table 3
    if "z_phq4" in x:
        x = x[x.z_phq4.notna()]
    if sx is not None:
        x = x[x.mujer == sx]
    bordes, tramos = CORTES[corte]
    x["tramo"] = pd.cut(x.edadq_m, bordes, right=False,
                        labels=tramos).astype(str)
    x["est"] = x.estrato.astype(int).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    cats = [t for t in tramos if t != "ref"]
    ii = ["I" + t.replace("-", "_") for t in cats]
    for t, i in zip(cats, ii):
        x[i] = (x.tramo == t).astype(float) * x.EQ
    rhs = ii + ["C(tramo)", "C(est)", "C(coh)"]
    pre = p15.X_PRE
    if mes:
        x["mob"] = x.birth_ym.astype(int).astype(str)
        rhs = ii + ["C(est)", "C(mob)"]
        pre = [v for v in pre if v != "edad_meses"]
    if controles:
        rhs += xt(x, pre) + xt(x, p15.X_POST)
    rhs += list(extra)
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x.est})
    b = {t: (float(r.params[i]), float(r.bse[i]), float(r.pvalues[i]),
             int((x.tramo == t).sum())) for t, i in zip(cats, ii)}
    if modelo:
        return b, int(r.nobs), r, x
    return b, int(r.nobs)


def linea(etiqueta, res):
    b, n = res
    log(f"- {etiqueta}: " + " | ".join(
        f"{t} {v[0]:+.3f}{stars(v[2])} (ee {v[1]:.3f}, p={v[2]:.3f})"
        for t, v in b.items()) + f" | N={n}")


def main():
    log("# Dos ventanas: PHQ-4 por edad al terremoto en tramos de seis meses "
        "(scripts/33_ventanas.py)")
    log("Zona afectada menos no afectada, frente a los expuestos con 24-35 "
        "meses; columna 3 de la Table 3.")
    d, _, _ = p15.load_data()
    filas = []
    log("\n## 1. Tramos de seis meses")
    for g, sx in GRUPOS:
        res = perfil(d, "z_phq4", sx)
        linea(g, res)
        for t, v in res[0].items():
            filas.append({"grupo": g, "tramo": t, "b": v[0], "se": v[1],
                          "p": v[2], "n_tramo": v[3]})
    log("\n## 2. Agrupados en las dos ventanas")
    for g, sx in GRUPOS:
        linea(g, perfil(d, "z_phq4", sx, "ventanas"))
    for y, lab in (("gad2_bin", "ansiedad, GAD-2"),
                   ("phq2_bin", "depresión, PHQ-2")):
        linea(f"chicas, {lab}", perfil(d, y, 1, "ventanas"))
    log("\n## 3. Robustez, chicas")
    linea("sin controles", perfil(d, "z_phq4", 1, controles=False))
    linea("con peso, talla y gestación al nacer",
          perfil(d, "z_phq4", 1, extra=NACER))
    linea("ventanas, con peso, talla y gestación al nacer",
          perfil(d, "z_phq4", 1, "ventanas", extra=NACER))
    log("\n## 4. Placebos: variables fijadas antes del terremoto, sin "
        "controles")
    for y in NACER + ["educ_madre10", "edad_madre10"]:
        for g, sx in GRUPOS[:2]:
            linea(f"{y}, {g}", perfil(d, y, sx, controles=False))
    pd.DataFrame(filas).to_csv("reports/ventanas.csv", index=False)
    Path("reports/ventanas.md").write_text("\n".join(OUT) + "\n",
                                           encoding="utf-8")
    print("-> reports/ventanas.md, reports/ventanas.csv")


if __name__ == "__main__":
    main()
