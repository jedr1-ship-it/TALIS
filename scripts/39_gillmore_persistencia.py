#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Persiste a los 15-18 años el efecto de Gillmore (2026) en el TVIP?

La ola 2024 solo trae a las cohortes 2006-2009, todas expuestas: el grupo de
control de Gillmore (concebidos después del 27-F) se toma de 2017, con 2-6
años (scripts/10_ec1_largo_plazo.py). Así, la ola y la edad al test van
juntas con el tratamiento. Tres pruebas de ese diseño, columna 3:

  1. Controles X interactuados con el grupo expuesto, que en 2024 coincide
     con la ola (la robustez de su nota 11, X por ola).
  2. Cola baja: estar en el 25 % (o el 10 %) inferior del TVIP de su edad y
     ola, menos sensible al techo del test a los 15-18 años.
  3. Geografía falsa (como su tabla C.17): sin las regiones afectadas,
     norte "tratado" frente a sur. Debería dar cero.

Las tres también en 2017 (expuestos a los 7-11 frente a concebidos después,
ambos en 2017), para comparar.

Salida: reports/gillmore_persistencia.md
Uso:    python3 scripts/39_gillmore_persistencia.py
"""
import importlib.util
import warnings
from pathlib import Path

import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p24", HERE / "24_niveles.py")
p24 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p24)
p10, num, fmt = p24.p10, p24.num, p24.fmt
NORTE = {1, 2, 3, 4, 15}
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def colas(df):
    s = num(df.tvip)
    g = s.groupby([df.wave, num(df.edad_meses) // 12])
    for q in (25, 10):
        corte = g.transform(lambda x, q=q: x.quantile(q / 100))
        df[f"cola{q}"] = (s <= corte).astype(float).where(s.notna())
    return df


def ajusta_x(df, y):
    """Columna 3 con cada control interactuado con el grupo expuesto."""
    d = df.dropna(subset=[y, "geo", "w", "cohorte"]).copy()
    d = d[d.w > 0]
    d["com"] = d.geo.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    xs = []
    for v in p10.XV:
        if d[v].isna().all() or d[v].nunique() < 2:
            continue
        if d[v].isna().any():
            d[f"{v}_mi"] = d[v].isna().astype(float)
            d[v] = d[v].fillna(d[v].median())
            xs += [v, f"{v}_mi"]
        else:
            xs.append(v)
    f = (f"{y} ~ AffEq + C(com) + C(coh) + " + " + ".join(xs) + " + "
         + " + ".join(f"{v}:affected" for v in xs))
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d["com"]})
    return (float(r.params["AffEq"]), float(r.bse["AffEq"]),
            float(r.pvalues["AffEq"])), int(r.nobs)


def falsa(base, y):
    d = base[base.EQ == 0].copy()
    d["Falso"] = d.affected * num(d.region).isin(NORTE).astype(float)
    r, n = p24.ajusta(d, y, ["Falso"])
    return r["Falso"], n, d.geo.nunique()


def main():
    log("# ¿Persiste el efecto de Gillmore en el TVIP? "
        "(scripts/39_gillmore_persistencia.py)")
    log("Zona afectada frente a no afectada, expuestos frente a concebidos "
        "después; columna 3 (EF de comuna y cohorte, controles X).")
    b24 = colas(p24.prepara(p24.base24()))
    b17 = colas(p24.prepara(p24.base17()))
    for etiqueta, base in (("2024: expuestos a los 15-18 frente a "
                            "concebidos después, medidos en 2017", b24),
                           ("2017: expuestos a los 7-11 frente a "
                            "concebidos después, ambos en 2017", b17)):
        log(f"\n## {etiqueta}")
        r, n = p24.ajusta(base, "z_tvip", ["AffEq"])
        log(f"- TVIP (z): {fmt(*r['AffEq'])}; N={n}")
        r, n = ajusta_x(base, "z_tvip")
        log(f"- controles interactuados con el grupo expuesto: {fmt(*r)}; "
            f"N={n}")
        for q in (25, 10):
            m = base.loc[base.affected == 1, f"cola{q}"].mean()
            r, n = p24.ajusta(base, f"cola{q}", ["AffEq"])
            log(f"- en el {q} % inferior del TVIP de su edad (media en "
                f"expuestos {m:.3f}): {fmt(*r['AffEq'])}; N={n}")
        r, n, k = falsa(base, "z_tvip")
        log(f"- geografía falsa, solo zona no afectada, norte frente a sur: "
            f"{fmt(*r)}; N={n}, comunas={k}")
    Path("reports/gillmore_persistencia.md").write_text(
        "\n".join(OUT) + "\n", encoding="utf-8")
    log("\n-> reports/gillmore_persistencia.md")


if __name__ == "__main__":
    main()
