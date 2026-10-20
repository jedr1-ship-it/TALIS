#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Y los que tenían 0-5 meses el 27-F?

La ELPI 2024 solo sigue a la muestra de 2010 (nacidos entre enero de 2006 y
agosto de 2009), así que el más pequeño tenía 6 meses el 27-F. Los nacidos
entre septiembre de 2009 y febrero de 2010 entraron en el refresco de 2012
(nacidos entre septiembre de 2009 y diciembre de 2011) y se vuelven a ver en
2017, no en 2024 (Informe metodológico ELPI 2024, sección 2.1.3).

Con la ronda de 2017 (7 a 11 años), nuestro diseño con un grupo más: zona
afectada menos no afectada para 0-5 y 6-11 meses, frente a todas las demás
edades (1-4 años) y frente a 2-3 años. Dos medidas de síntomas
internalizantes: el índice que reporta el niño (baja autoestima, no se
considera feliz, se siente solo en el curso) y el CBCL internalizante del
cuidador. La geografía y los pesos son los de 2017 (scripts/08), la misma
para la muestra de 2010 y la de refresco: la comuna del 27-F no se conoce
para el refresco.

Salida: reports/cero_cinco.md
Uso:    python3 scripts/46_cero_cinco.py
"""
import importlib.util
import warnings
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p40", HERE / "40_salud_mental_antes.py")
p40 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p40)
p08 = p40.p08
TRAMOS = ([0, 6, 12, 24, 36, 50], ["0-5", "6-11", "12-23", "24-35", "36-49"])
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def carga():
    df = p40.base()
    n17 = p40.ninos17()
    x = df[df.wave == 2017].copy()
    x["edadq"] = (2010 * 12 + 1) - x.birth_ym
    x = x[x.edadq.between(0, 49)].copy()
    x["g"] = pd.cut(x.edadq, TRAMOS[0], right=False,
                    labels=TRAMOS[1]).astype(str)
    x = x.merge(n17[["folio", "z_tae_baja", "no_feliz", "z_soledad"]],
                on="folio", how="left")
    zz = lambda s: (s - s.mean()) / s.std()                   # noqa: E731
    tres = pd.concat([zz(x.z_tae_baja), zz(x.no_feliz), zz(x.z_soledad)],
                     axis=1)
    x["malestar"] = zz(tres.mean(axis=1).where(tres.notna().all(axis=1)))
    return x


def ajusta(d, y, tramos):
    d = d.dropna(subset=[y, "geo", "w", "cohorte", "earthquake"]).copy()
    d = d[d.w > 0]
    d["com"] = d.geo.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    ii = []
    for t in tramos:
        k = "I" + t.replace("-", "_")
        d[k] = (d.g == t) * d.earthquake
        ii.append(k)
    xs = []
    for v in p08.XVARS:
        s = d[v]
        if s.notna().sum() == 0 or s.nunique() < 2:
            continue
        if s.isna().any():
            d[f"{v}_mi"] = s.isna().astype(float)
            d[v] = s.fillna(s.median())
            xs += [v, f"{v}_mi"]
        else:
            xs.append(v)
    r = smf.wls(f"{y} ~ {' + '.join(ii)} + C(g) + C(com) + C(coh) + "
                + " + ".join(xs), data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d.com})
    return {t: (float(r.params[k]), float(r.bse[k]), float(r.pvalues[k]))
            for t, k in zip(tramos, ii)}, int(r.nobs)


def main():
    x = carga()
    log("# Los que tenían 0-5 meses el 27-F (scripts/46_cero_cinco.py)")
    log("Ronda 2017; zona afectada menos no afectada; EF de comuna, año de "
        "nacimiento y grupo de edad; controles de scripts/08; pesos de "
        "2017; EE por comuna.")
    n = x[x.malestar.notna()].groupby(["mujer", "g", "earthquake"]).size()
    log("\nChicas con el índice del niño (no afectada / afectada): " + " | ".join(
        f"{t}: {n.get((1.0, t, 0.0), 0)} / {n.get((1.0, t, 1.0), 0)}"
        for t in TRAMOS[1]))
    for y, lab in (("malestar", "índice del niño (autoestima, felicidad y "
                                "soledad)"),
                   ("z_int", "CBCL internalizante, cuidador")):
        log(f"\n## {lab}")
        for g, sx in (("chicas", 1), ("chicos", 0)):
            d = x[x.mujer == sx]
            b, n_ = ajusta(d, y, ["0-5", "6-11"])
            log(f"- {g}, frente a 1-4 años: " + " | ".join(
                f"{t} {v[0]:+.3f} (ee {v[1]:.3f}, p={v[2]:.2f})"
                for t, v in b.items()) + f" | N={n_:,}")
            b, n_ = ajusta(d, y, ["0-5", "6-11", "12-23", "36-49"])
            log(f"- {g}, frente a 2-3 años: " + " | ".join(
                f"{t} {v[0]:+.3f} (ee {v[1]:.3f})" for t, v in b.items())
                + f" | N={n_:,}")
    Path("reports/cero_cinco.md").write_text("\n".join(OUT) + "\n",
                                             encoding="utf-8")
    print("-> reports/cero_cinco.md")


if __name__ == "__main__":
    main()
