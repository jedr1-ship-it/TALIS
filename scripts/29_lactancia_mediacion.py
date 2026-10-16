#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La lactancia como canal, en dos pasos.

  1. Primera etapa: ¿adelantó el terremoto el destete? Entre los que mamaban
     el 27-F, destete en los tres meses siguientes, zona afectada frente a no
     afectada, con efectos fijos de edad al terremoto y controles previos
     (la especificación de scripts/17, sección D). Placebo: destete en los
     cuatro meses anteriores. Se estima para 1-18 meses, como en scripts/17,
     y para los bebés de 6-11 meses del paper.
  2. Mediación: entre los bebés de 6-11 meses que tomaban pecho en la zona
     afectada, PHQ-4 de los destetados en esos tres meses frente a los que
     siguieron (scripts/25, sección F, ahora con su error estándar), junto a
     la interacción zona afectada x tomaba pecho (scripts/25, base). El
     efecto indirecto por el destete es el producto de la primera etapa y de
     esa diferencia.
  3. Lo mismo para los expuestos con un año: primera etapa para 12-18 y
     12-23 meses, interacción zona afectada x tomaba pecho y destetados
     frente a los que siguieron.

Salida: reports/lactancia_mediacion.md
Uso:    python3 scripts/29_lactancia_mediacion.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p17 = modulo("p17", "17_mecanismos.py")
p25 = modulo("p25", "25_lactancia_robustez.py")
p15 = p25.p15
xt, stars = p15.xt, p15.stars
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(t):
    return f"{t[0]:+.3f}{stars(t[2])} (ee {t[1]:.3f}, p={t[2]:.3f})"


def destete(d, edades):
    """Primera etapa y placebo para las edades al terremoto en `edades`."""
    lo, hi = edades
    out = {}
    tt = d.dropna(subset=["mamando"]).copy()
    tt = tt[tt.edadq_m.between(lo, hi) & (tt.mamando >= tt.edadq_m)]
    tt["destete"] = (tt.mamando <= tt.edadq_m + 3).astype(float)
    pre = d.dropna(subset=["mamando"]).copy()
    pre = pre[pre.edadq_m.between(max(lo, 5), hi)
              & (pre.mamando >= pre.edadq_m - 4)]
    pre["destete"] = pre.mamando.between(pre.edadq_m - 4,
                                         pre.edadq_m - 1).astype(float)
    for k, base in (("post", tt), ("pre", pre)):
        base = base.dropna(subset=["w", "estrato"])
        base = base[base.w > 0].copy()
        base["est"] = base.estrato.astype(int).astype(str)
        rhs = " + ".join(["EQ", "C(edadq_m)"] + xt(base, p15.X_PRE))
        r = smf.wls(f"destete ~ {rhs}", data=base, weights=base.w).fit(
            cov_type="cluster", cov_kwds={"groups": base.est})
        out[k] = (float(r.params["EQ"]), float(r.bse["EQ"]),
                  float(r.pvalues["EQ"]), float(base.destete.mean()),
                  int(r.nobs))
    return out


def main():
    log("# La lactancia como canal: primera etapa y mediación "
        "(scripts/29_lactancia_mediacion.py)")
    d17 = p17.carga()
    log("\n## 1. Primera etapa: destete entre los que mamaban el 27-F")
    fe = {}
    for edades, lab in (((1, 18), "1-18 meses"), ((6, 11), "6-11 meses")):
        fe[lab] = destete(d17, edades)
        for k, txt in (("post", "en los 3 meses tras el 27-F"),
                       ("pre", "en los 4 meses antes, placebo")):
            t = fe[lab][k]
            log(f"- {lab}, destete {txt}: zona afectada {fmt(t)}; media "
                f"{t[3]:.3f}; N={t[4]}")

    log("\n## 2. Mediación, bebés de 6-11 meses")
    d = p25.carga()
    b = p25.bebes(d)
    t, n = p25.inter(b, "z_phq4")
    log(f"- PHQ-4, zona afectada x tomaba pecho el 27-F: {fmt(t)}; N={n}")
    a = b[(b.pecho == 1) & (b.EQ == 1)].copy()
    a["destete3"] = (a.meses_pecho <= a.edadq_m + 3).astype(float)
    a = a.dropna(subset=["z_phq4", "w", "estrato", "cohorte"])
    a = a[a.w > 0]
    r = smf.wls("z_phq4 ~ destete3 + C(est) + C(coh) + "
                + " + ".join(xt(a, p15.X_PRE)), data=a,
                weights=a.w).fit(cov_type="cluster",
                                 cov_kwds={"groups": a.est})
    m = (float(r.params["destete3"]), float(r.bse["destete3"]),
         float(r.pvalues["destete3"]))
    log(f"- PHQ-4, destetados en los 3 meses tras el 27-F frente a los que "
        f"siguieron, tomaban pecho en zona afectada: {fmt(m)}; N="
        f"{int(r.nobs)}; destetados {a.destete3.mean():.2f}")
    fs = fe["6-11 meses"]["post"]
    ind = fs[0] * m[0]
    se_ind = np.sqrt((fs[0] * m[1]) ** 2 + (m[0] * fs[1]) ** 2)
    se_exacto = np.sqrt(se_ind ** 2 + (fs[1] * m[1]) ** 2)
    log(f"- efecto indirecto por el destete, 6-11 meses: {fs[0]:+.3f} x "
        f"{m[0]:+.3f} = {ind:+.4f} DE (ee delta {se_ind:.4f}; ee exacto "
        f"del producto {se_exacto:.4f})")
    log("\n## 3. Los expuestos con un año (12-23 meses)")
    for edades, lab in (((12, 18), "12-18 meses"), ((12, 23), "12-23 meses")):
        r1 = destete(d17, edades)
        for k, txt in (("post", "en los 3 meses tras el 27-F"),
                       ("pre", "en los 4 meses antes, placebo")):
            t1 = r1[k]
            log(f"- {lab}, destete {txt}: zona afectada {fmt(t1)}; media "
                f"{t1[3]:.3f}; N={t1[4]}")
    for (lo, hi), lab in (((12, 23), "12-23 meses"), ((12, 18), "12-18 meses")):
        u = d[d.edadq_m.between(lo, hi)].dropna(
            subset=["meses_pecho", "w", "estrato", "cohorte"]).copy()
        u = u[u.w > 0].copy()
        u["est"] = u.estrato.astype(int).astype(str)
        u["coh"] = u.cohorte.astype(int).astype(str)
        u["reg"] = u.region.astype(int).astype(str)
        u["pecho"] = (u.meses_pecho >= u.edadq_m).astype(float)
        t1, n1 = p25.inter(u, "z_phq4")
        log(f"- {lab}, PHQ-4, zona afectada x tomaba pecho el 27-F: "
            f"{fmt(t1)}; N={n1}; tomaban pecho {u.pecho.mean():.2f}")
        a1 = u[(u.pecho == 1) & (u.EQ == 1)].copy()
        a1["destete3"] = (a1.meses_pecho <= a1.edadq_m + 3).astype(float)
        a1 = a1.dropna(subset=["z_phq4"])
        r = smf.wls("z_phq4 ~ destete3 + C(est) + C(coh) + "
                    + " + ".join(xt(a1, p15.X_PRE)), data=a1,
                    weights=a1.w).fit(cov_type="cluster",
                                      cov_kwds={"groups": a1.est})
        t2 = (float(r.params["destete3"]), float(r.bse["destete3"]),
              float(r.pvalues["destete3"]))
        log(f"- {lab}, PHQ-4, destetados en los 3 meses frente a los que "
            f"siguieron, zona afectada: {fmt(t2)}; N={int(r.nobs)}; "
            f"destetados {a1.destete3.mean():.2f}")
    Path("reports/lactancia_mediacion.md").write_text(
        "\n".join(OUT) + "\n", encoding="utf-8")
    print("-> reports/lactancia_mediacion.md")


if __name__ == "__main__":
    main()
