#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La comparación principal de la presentación: 6-11 meses frente a todas las
demás edades juntas.

Comparar con los de 2-3 años infla el efecto, porque en la zona de control
los de 2-3 años tienen un PHQ-4 alto (scripts/44_pga_niveles.py). Aquí, con
la misma especificación que el perfil (efectos fijos de comuna, año de
nacimiento y grupo de edad, controles, pesos ELPI, EE por comuna) y una sola
interacción, 6-11 meses x zona afectada:

  phq4      PHQ-4: todos, chicas, chicos y chicas con efectos fijos de mes
            de nacimiento (diapositiva 6)
  nivel     PHQ-4 medio por edad al terremoto y zona, chicas y chicos
            (diapositiva 6)
  entorno   los seis indicadores del entorno, chicas (diapositiva 7)
  pecho     el efecto de 6-11 meses en quienes tomaban pecho el 27-F y en
            quienes no; chicas, chicas con la educación y el empleo de la
            madre interactuados con el pecho y con la zona, y chicos
            (diapositiva 8)
  otros     PHQ-4, consumo, victimización y CBCL, chicas y chicos
            (diapositiva 9)

Salida: reports/contraste.csv y reports/contraste.md
Uso:    python3 scripts/45_contraste.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    s = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


p34 = modulo("p34", "34_estres_madre.py")
p33, p15 = p34.p33, p34.p15
SEXOS = (("chicas", 1), ("chicos", 0))
OTROS = ["z_phq4", "z_consumo", "z_bull", "cbcl_int", "cbcl_ext"]
OUT, FILAS = [], []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def guarda(tipo, resultado, grupo, b, se, p, n, **extra):
    FILAS.append({"tipo": tipo, "resultado": resultado, "grupo": grupo,
                  "b": b, "se": se, "p": p, "n": n, **extra})


def contraste(d, y, sx, **kw):
    b, n = p33.perfil(d, y, sx, "paper", solo="6-11", **kw)
    return b["6-11"][:3], n


def linea(lab, r, n):
    log(f"- {lab}: {r[0]:+.3f} (ee {r[1]:.3f}, p={r[2]:.3f}); N={n:,}")


def phq4():
    d, _, _ = p15.load_data()
    log("\n## PHQ-4")
    for g, sx, kw in (("todos", None, {}), ("chicas", 1, {}),
                      ("chicos", 0, {}), ("chicas, mes", 1, {"mes": True})):
        r, n = contraste(d, "z_phq4", sx, **kw)
        linea(g, r, n)
        guarda("phq4", "z_phq4", g, *r, n)
    p44 = modulo("p44", "44_pga_niveles.py")
    x = p44.carga()
    for g, sx in SEXOS:
        m = p44.medias(x[x.mujer == sx], p44.TRAMOS)
        for (t, e), (b, se, n) in m.items():
            guarda("nivel", "z_phq4", g, b, se, np.nan, n, tramo=t,
                   zona=int(e))


def entorno():
    p35 = modulo("p35", "35_canal_hogar.py")
    d = p35.carga()
    log("\n## Entorno, chicas")
    for i in p35.INDICES:
        r, n = contraste(d, i, 1)
        linea(i, r, n)
        guarda("entorno", i, "chicas", *r, n)


def otros():
    p36 = modulo("p36", "36_chicos.py")
    d = p36.p19.construye()
    c = d[["alcohol", "fuma", "cannabis", "otras_drogas"]]
    d["consumo"] = c.max(axis=1).where(c.notna().any(axis=1))
    d["z_consumo"] = (d.consumo - d.consumo.mean()) / d.consumo.std()
    log("\n## Otros resultados")
    for g, sx in SEXOS:
        for y in OTROS:
            r, n = contraste(d, y, sx)
            linea(f"{y}, {g}", r, n)
            guarda("otros", y, g, *r, n)


def pecho():
    """6-11 meses x zona, por separado para quienes tomaban pecho el 27-F y
    quienes no, frente a todas las demás edades; efectos fijos de grupo de
    edad x pecho."""
    p43 = modulo("p43", "43_triple_did.py")
    d = p34.carga()
    log("\n## El efecto de 6-11 meses según la lactancia")
    for g, sx, ses in (("chicas", 1, False), ("chicas, SES", 1, True),
                       ("chicos", 0, False)):
        x = p43.prepara(d, sx)
        extra = []
        if ses:
            x = x.dropna(subset=["educ_madre10", "trabaja10"]).copy()
            for v in ("educ_madre10", "trabaja10"):
                x[f"p_{v}"] = x.pecho * x[v]
                x[f"a_{v}"] = x.EQ * x[v]
                extra += [f"p_{v}", f"a_{v}"]
        x["S_bf"] = x.A6_11 * x.pecho
        x["S_no"] = x.A6_11 * (1 - x.pecho)
        ctr = p34.xt(x, p15.X_PRE) + p34.xt(x, p15.X_POST)
        rhs = (["S_bf", "S_no", "C(tramo)", "C(tramo):pecho", "pecho",
                "C(est)", "C(coh)"] + ctr + extra)
        r = smf.wls("z_phq4 ~ " + " + ".join(rhs), data=x, weights=x.w).fit(
            cov_type="cluster", cov_kwds={"groups": x.est})
        t = r.t_test("S_bf - S_no")
        dif = (float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]),
               float(np.ravel(t.pvalue)[0]))
        n = int(r.nobs)
        for k, lab in (("S_bf", "con pecho"), ("S_no", "sin pecho")):
            res = (float(r.params[k]), float(r.bse[k]), float(r.pvalues[k]))
            linea(f"{g}, {lab}", res, n)
            guarda("pecho", lab, g, *res, n)
        linea(f"{g}, diferencia", dif, n)
        guarda("pecho", "diferencia", g, *dif, n)


def main():
    log("# 6-11 meses frente a todas las demás edades "
        "(scripts/45_contraste.py)")
    log("Zona afectada menos no afectada; EF de comuna, año de nacimiento y "
        "grupo de edad; controles; pesos ELPI; EE por comuna.")
    phq4()
    entorno()
    pecho()
    otros()
    pd.DataFrame(FILAS).to_csv("reports/contraste.csv", index=False)
    Path("reports/contraste.md").write_text("\n".join(OUT) + "\n",
                                            encoding="utf-8")
    print("-> reports/contraste.csv, reports/contraste.md")


if __name__ == "__main__":
    main()
