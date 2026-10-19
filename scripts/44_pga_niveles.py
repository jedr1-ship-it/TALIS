#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿El pico de las chicas de 6-11 meses es real o lo crea el grupo de
referencia?

El perfil de la presentación compara cada edad al terremoto con los que
tenían 2 años. Tres pruebas:

  1. Niveles: PHQ-4 medio (z) por edad al terremoto, zona afectada y no
     afectada por separado, chicas y chicos (y tramos de seis meses en
     chicas). Si el perfil en forma de U viene de un pico en la zona
     afectada o de un valor raro de los 2 años en la zona de control.
  2. PGA continuo (USGS ShakeMap, por 10 puntos de % de g) en lugar de la
     zona afectada; también solo dentro de la zona afectada.
  3. Otras referencias: 6-11 meses frente a todas las demás edades juntas
     (con la zona, con efectos fijos de mes de nacimiento y con el PGA), y
     frente a 1 año o a 3-4 años.

Salida: reports/pga_niveles.md y reports/niveles_zona.png
Uso:    python3 scripts/44_pga_niveles.py
"""
import importlib.util
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
import numpy as np                                   # noqa: E402
import pandas as pd                                  # noqa: E402
import statsmodels.formula.api as smf                # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    s = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


p33 = modulo("p33", "33_ventanas.py")
p28 = modulo("p28", "28_beamer_advisor.py")
p15 = p33.p15
TRAMOS = ([6, 12, 24, 36, 50], ["6-11", "12-23", "24-35", "36-49"])
SEIS = ([6, 12, 18, 24, 30, 36, 42, 50],
        ["6-11", "12-17", "18-23", "24-29", "30-35", "36-41", "42-49"])
GRUPOS = (("chicas", 1), ("chicos", 0), ("todos", None))
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def carga():
    d, _, _ = p15.load_data()
    d = d[d.z_phq4.notna() & d.edadq_m.between(6, 49) & (d.w > 0)].copy()
    d["pga10"] = d.pga / 10
    d["est"] = d.estrato.astype(int).astype(str)
    return d


def medias(x, cortes):
    """Media ponderada del PHQ-4 (z) en cada edad y zona, EE por comuna."""
    bordes, etiquetas = cortes
    x = x.copy()
    x["g"] = pd.cut(x.edadq_m, bordes, right=False,
                    labels=etiquetas).astype(str)
    x["cel"] = x.g + "_" + x.EQ.astype(int).astype(str)
    r = smf.wls("z_phq4 ~ 0 + C(cel)", data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x.est})
    return {(t, e): (float(r.params[f"C(cel)[{t}_{e}]"]),
                     float(r.bse[f"C(cel)[{t}_{e}]"]),
                     int(((x.g == t) & (x.EQ == e)).sum()))
            for t in etiquetas for e in (1, 0)}


def contraste(d, sx, dosis="EQ", mes=False):
    """6-11 meses frente a todas las demás edades juntas."""
    x = d if sx is None else d[d.mujer == sx]
    x = x.copy()
    x["tramo"] = pd.cut(x.edadq_m, TRAMOS[0], right=False,
                        labels=TRAMOS[1]).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    x["mob"] = x.birth_ym.astype(int).astype(str)
    x["I"] = (x.tramo == "6-11") * x[dosis]
    pre = [v for v in p15.X_PRE if not (mes and v == "edad_meses")]
    fe = ["C(est)", "C(mob)"] if mes else ["C(tramo)", "C(est)", "C(coh)"]
    rhs = ["I"] + fe + p15.xt(x, pre) + p15.xt(x, p15.X_POST)
    r = smf.wls("z_phq4 ~ " + " + ".join(rhs), data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x.est})
    return float(r.params["I"]), float(r.bse["I"]), float(r.pvalues["I"])


def referencia(d, ref):
    """Perfil de las chicas con otro grupo de referencia."""
    x = d[d.mujer == 1].copy()
    x["tramo"] = pd.cut(x.edadq_m, TRAMOS[0], right=False,
                        labels=TRAMOS[1]).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    ii = []
    for t in TRAMOS[1]:
        if t != ref:
            x["I" + t.replace("-", "_")] = (x.tramo == t) * x.EQ
            ii.append("I" + t.replace("-", "_"))
    rhs = (ii + ["C(tramo)", "C(est)", "C(coh)"] + p15.xt(x, p15.X_PRE)
           + p15.xt(x, p15.X_POST))
    r = smf.wls("z_phq4 ~ " + " + ".join(rhs), data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x.est})
    return {i: (float(r.params[i]), float(r.bse[i])) for i in ii}


def figura(niv):
    etiq = ["6–11\nmonths", "1–2\nyears", "2–3\nyears", "3–4\nyears"]
    with plt.rc_context(p28.PAPER):
        f = plt.figure(figsize=(144 * p28.MM, 58 * p28.MM))
        hs = []
        for i, (g, nombre) in enumerate((("chicas", "Girls"),
                                         ("chicos", "Boys"))):
            a = f.add_axes([0.1 + i * 0.47, 0.24, 0.39, 0.62])
            for lado in ("top", "right"):
                a.spines[lado].set_visible(False)
            m = niv[g]
            hs = []
            for e, col, marca, hueco, dx in ((1, p28.OCRE, "^", False, -0.07),
                                             (0, p28.GRISR, "o", True, 0.07)):
                xs = np.arange(4) + dx
                ys = [m[(t, e)][0] for t in TRAMOS[1]]
                se = [m[(t, e)][1] for t in TRAMOS[1]]
                a.plot(xs, ys, color=col, lw=0.9, zorder=2)
                h = a.errorbar(xs, ys, yerr=1.96 * np.array(se), fmt=marca,
                               color=col, mfc="white" if hueco else col,
                               mec=col, mew=1.0,
                               ms=6.0 if marca == "^" else 5.5, capsize=2.6,
                               elinewidth=1.0, capthick=1.0, zorder=3)
                hs.append(h)
            a.set_xticks(range(4))
            a.set_xticklabels(etiq, fontsize=7.5)
            a.set_xlim(-0.4, 3.4)
            a.set_ylim(-0.5, 0.6)
            p28.formato_eje(a, 0.2)
            a.set_title(nombre, fontsize=9, pad=4)
            if i == 0:
                a.set_ylabel("PHQ-4 in 2024 (SD)", fontsize=8)
        f.text(0.53, 0.01, "Age at the earthquake", ha="center",
               va="bottom", fontsize=8)
        f.legend(hs, ["Affected zone", "Unaffected"], loc="upper center",
                 bbox_to_anchor=(0.53, 1.0), ncol=2, frameon=False,
                 fontsize=7.5, handletextpad=0.3, columnspacing=1.2)
        f.savefig("reports/niveles_zona.png", dpi=220)
        plt.close(f)
    print("-> reports/niveles_zona.png")


def main():
    d = carga()
    log("# ¿Pico real o efecto del grupo de referencia? "
        "(scripts/44_pga_niveles.py)")
    log("PHQ-4 en DE; pesos ELPI; EE por comuna.")
    log("\n## 1. Niveles por edad al terremoto y zona")
    niv = {}
    for g, sx in GRUPOS[:2]:
        niv[g] = m = medias(d[d.mujer == sx], TRAMOS)
        log(f"- {g}: " + " | ".join(
            f"{t}: afectada {m[(t, 1)][0]:+.2f} ({m[(t, 1)][1]:.2f}), "
            f"no afectada {m[(t, 0)][0]:+.2f} ({m[(t, 0)][1]:.2f}), brecha "
            f"{m[(t, 1)][0] - m[(t, 0)][0]:+.2f}" for t in TRAMOS[1]))
    m = medias(d[d.mujer == 1], SEIS)
    log("- chicas, tramos de seis meses: " + " | ".join(
        f"{t}: {m[(t, 1)][0]:+.2f} / {m[(t, 0)][0]:+.2f} (n {m[(t, 0)][2]})"
        for t in SEIS[1]) + "  [afectada / no afectada (n no afectada)]")
    figura(niv)
    log("\n## 2. PGA continuo (por 10 puntos de % de g), frente a 2 años")
    log(f"PGA medio: zona afectada {d[d.EQ == 1].pga.mean():.1f}, "
        f"no afectada {d[d.EQ == 0].pga.mean():.1f}.")
    for g, sx in GRUPOS:
        p33.linea(f"{g}", p33.perfil(d.assign(EQ=d.pga10), "z_phq4", sx,
                                     "paper"))
        OUT.append(p33.OUT.pop())
    for g, sx in GRUPOS[::2]:
        p33.linea(f"{g}, solo zona afectada",
                  p33.perfil(d[d.EQ == 1].assign(EQ=d.pga10), "z_phq4", sx,
                             "paper"))
        OUT.append(p33.OUT.pop())
    log("\n## 3. 6-11 meses frente a todas las demás edades juntas")
    for g, sx in GRUPOS:
        for lab, kw in (("zona afectada", {}),
                        ("zona afectada, EF de mes de nacimiento",
                         {"mes": True}),
                        ("PGA por 10 puntos", {"dosis": "pga10"})):
            b, se, p = contraste(d, sx, **kw)
            log(f"- {g}, {lab}: {b:+.3f} (ee {se:.3f}, p={p:.3f})")
    for ref in ("12-23", "36-49"):
        r = referencia(d, ref)
        log(f"- chicas, referencia {ref}: " + " | ".join(
            f"{k[1:]} {v[0]:+.3f} (ee {v[1]:.3f})" for k, v in r.items()))
    Path("reports/pga_niveles.md").write_text("\n".join(OUT) + "\n",
                                              encoding="utf-8")
    print("-> reports/pga_niveles.md")


if __name__ == "__main__":
    main()
