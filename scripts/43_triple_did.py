#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Triple diferencia: ¿el terremoto golpea más a quienes tomaban pecho el 27-F?

La Table A5 de la presentación relaciona el PHQ-4 de la hija con el estrés
que la madre reporta en 2012, según tomara pecho o no: es una correlación,
no usa el terremoto. Aquí se usa el terremoto. Para cada grupo de edad al
27-F, la diferencia zona afectada menos no afectada entre quienes tomaban
pecho, menos la misma diferencia entre quienes no:

  PHQ-4 = sum_a kappa_a (Age_a x Affected x Breastfed)
          + sum_{a != 2} beta_a (Age_a x Affected)
          + EF de grupo de edad x pecho, de comuna y de año de nacimiento
          + controles de la Table 3

Si la vía fuera el estrés que la madre reporta, kappa debería ser
aproximadamente la pendiente de la Table A5 (0,29) por el aumento del
estrés en la zona afectada (13 puntos): unas 0,04 DE. Con cientos de
lactantes por grupo, el error estándar es diez veces eso.

Instrumentar el estrés con el terremoto no es posible: la zona afectada
se absorbe en los efectos fijos de comuna (el nivel no está identificado
porque en 2024 todos estuvieron expuestos), y el terremoto llega al niño
por más vías que el estrés de la madre.

Salida: reports/triple_did.md, reports/triple_did.csv y
        reports/triple_did.png
Uso:    python3 scripts/43_triple_did.py
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


p34 = modulo("p34", "34_estres_madre.py")
p28 = modulo("p28", "28_beamer_advisor.py")
p15 = p34.p15
TRAMOS = ["6-11", "12-23", "24-35", "36-49"]
ETIQ = ["6–11\nmonths", "1–2\nyears", "2–3\nyears", "3–4\nyears"]
GRUPOS = (("chicas", 1), ("chicos", 0), ("todos", None))
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def prepara(d, sx):
    x = d.dropna(subset=["z_phq4", "pecho", "estrato", "w", "cohorte"]).copy()
    x = x[x.w > 0]
    if sx is not None:
        x = x[x.mujer == sx]
    x["est"] = x.estrato.astype(int).astype(str)
    x["coh"] = x.cohorte.astype(int).astype(str)
    for t in TRAMOS:
        k = t.replace("-", "_")
        x[f"A{k}"] = (x.tramo == t) * x.EQ
        x[f"K{k}"] = (x.tramo == t) * x.EQ * x.pecho
    x["AB"] = x.EQ * x.pecho
    return x


def ajusta(x, triple, extra=()):
    ctr = p34.xt(x, p15.X_PRE) + p34.xt(x, p15.X_POST)
    rhs = (triple + ["A6_11", "A12_23", "A36_49", "C(tramo)",
                     "C(tramo):pecho", "pecho", "C(est)", "C(coh)"]
           + ctr + list(extra))
    return smf.wls("z_phq4 ~ " + " + ".join(rhs), data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x.est})


def main():
    d = p34.carga()
    log("# Triple diferencia: edad x zona afectada x pecho el 27-F "
        "(scripts/43_triple_did.py)")
    log("Diferencia zona afectada menos no afectada entre quienes tomaban "
        "pecho, menos la misma entre quienes no, en cada grupo de edad; EF "
        "de grupo de edad x pecho, comuna y año de nacimiento; controles de "
        "la Table 3; pesos ELPI; EE por comuna.")
    filas = []
    for g, sx in GRUPOS:
        x = prepara(d, sx)
        ks = ["K" + t.replace("-", "_") for t in TRAMOS]
        r = ajusta(x, ks)
        rp = ajusta(x, ["AB"])
        y = x.dropna(subset=["estres12"])
        fs = smf.wls("estres12 ~ EQ + C(tramo) + C(coh)", data=y,
                     weights=y.w).fit(cov_type="cluster",
                                      cov_kwds={"groups": y.est})
        z = x.dropna(subset=["educ_madre10", "trabaja10"]).copy()
        for v in ("educ_madre10", "trabaja10"):
            z[f"p_{v}"] = z.pecho * z[v]
            z[f"a_{v}"] = z.EQ * z[v]
        rs = ajusta(z, ks, [f"{p}_{v}" for p in ("p", "a")
                            for v in ("educ_madre10", "trabaja10")])
        dif = r.t_test("K6_11 - K24_35")
        log(f"\n## {g} (N={int(r.nobs):,})")
        log(f"- estrés de la madre, zona afectada menos no afectada (sin EF "
            f"de comuna): {fs.params['EQ']:+.3f} (ee {fs.bse['EQ']:.3f})")
        log(f"- todas las edades juntas: {rp.params['AB']:+.3f} "
            f"(ee {rp.bse['AB']:.3f}, p={rp.pvalues['AB']:.3f})")
        for t, k in zip(TRAMOS, ks):
            n = int(((x.tramo == t) & (x.pecho == 1)).sum())
            log(f"- {t}: {r.params[k]:+.3f} (ee {r.bse[k]:.3f}, "
                f"p={r.pvalues[k]:.3f}); con educación y empleo de la madre "
                f"x pecho y x zona: {rs.params[k]:+.3f} (ee {rs.bse[k]:.3f})"
                f"; tomaban pecho {n}")
            filas.append({"grupo": g, "tramo": t, "b": r.params[k],
                          "se": r.bse[k], "p": r.pvalues[k], "n_pecho": n,
                          "b_ses": rs.params[k], "se_ses": rs.bse[k]})
        log(f"- 6-11 meses menos 2 años: {float(np.ravel(dif.effect)[0]):+.3f}"
            f" (ee {float(np.ravel(dif.sd)[0]):.3f}, "
            f"p={float(np.ravel(dif.pvalue)[0]):.3f})")
        filas.append({"grupo": g, "tramo": "todas", "b": rp.params["AB"],
                      "se": rp.bse["AB"], "p": rp.pvalues["AB"],
                      "n_pecho": int(x.pecho.sum()),
                      "primera_etapa": fs.params["EQ"]})
    c = pd.DataFrame(filas)
    c.to_csv("reports/triple_did.csv", index=False)
    comprobaciones(d)
    figura(c)
    Path("reports/triple_did.md").write_text("\n".join(OUT) + "\n",
                                             encoding="utf-8")
    print("-> reports/triple_did.md, reports/triple_did.csv")


def comprobaciones(d):
    """El efecto de 6-11 meses según la lactancia, el grupo de referencia,
    la lactancia en los menores de 2 años y si el terremoto cortó la
    lactancia."""
    log("\n## Comprobaciones")
    for g, sx in GRUPOS[:2]:
        x = prepara(d, sx)
        ctr = p34.xt(x, p15.X_PRE) + p34.xt(x, p15.X_POST)
        fe = ["C(tramo)", "C(tramo):pecho", "pecho", "C(est)", "C(coh)"] + ctr

        def fit(datos, rhs):
            return smf.wls("z_phq4 ~ " + " + ".join(rhs), data=datos,
                           weights=datos.w).fit(
                cov_type="cluster", cov_kwds={"groups": datos.est})
        x["S_bf"] = x.A6_11 * x.pecho
        x["S_no"] = x.A6_11 * (1 - x.pecho)
        r = fit(x, ["S_bf", "S_no", "A12_23", "A36_49"] + fe)
        log(f"- {g}, 6-11 meses frente a 2 años: tomaba pecho "
            f"{r.params['S_bf']:+.3f} (ee {r.bse['S_bf']:.3f}), no tomaba "
            f"{r.params['S_no']:+.3f} (ee {r.bse['S_no']:.3f})")
        x["U2"] = x.tramo.isin(["6-11", "12-23"]) * x.EQ * x.pecho
        x["O2"] = x.tramo.isin(["24-35", "36-49"]) * x.EQ * x.pecho
        r = fit(x, ["U2", "O2", "A6_11", "A12_23", "A36_49"] + fe)
        log(f"- {g}, pecho x zona, menores de 2 años: {r.params['U2']:+.3f} "
            f"(ee {r.bse['U2']:.3f}, p={r.pvalues['U2']:.3f}); 2 años o más: "
            f"{r.params['O2']:+.3f} (ee {r.bse['O2']:.3f})")
        base = ["A6_11", "A12_23", "A36_49", "C(tramo)", "C(est)",
                "C(coh)"] + ctr
        y = x[~((x.tramo == "24-35") & (x.pecho == 1))]
        r0, r1 = fit(x, base), fit(y, base)
        log(f"- {g}, perfil principal, 6-11 meses: {r0.params['A6_11']:+.3f}"
            f" (ee {r0.bse['A6_11']:.3f}); sin los de 2 años que tomaban "
            f"pecho en la referencia: {r1.params['A6_11']:+.3f} "
            f"(ee {r1.bse['A6_11']:.3f})")
    x = d[(d.pecho == 1) & d.tramo.isin(["6-11", "12-23"])].dropna(
        subset=["meses_pecho", "estrato", "w"]).copy()
    x["corta3"] = ((x.meses_pecho < x.edadq_m + 3)
                   & (x.meses_pecho < 900)).astype(float)
    for t in ("6-11", "12-23"):
        z = x[x.tramo == t]
        log(f"- tomaban pecho el 27-F con {t} meses, destetados en los tres "
            f"meses siguientes: zona afectada {z[z.EQ == 1].corta3.mean():.3f}"
            f", no afectada {z[z.EQ == 0].corta3.mean():.3f}")
    z = d[d.tramo == "6-11"].dropna(subset=["estres12", "pecho"])
    log("- estrés de la madre (2012), hijos de 6-11 meses: " + " | ".join(
        f"{'afectada' if e else 'no afectada'}, "
        f"{'con pecho' if b else 'sin pecho'} "
        f"{z[(z.EQ == e) & (z.pecho == b)].estres12.mean():.3f}"
        for e in (1, 0) for b in (1, 0)))


def figura(c):
    """Coeficientes kappa por edad, chicas y chicos, con la magnitud que
    implicaría la vía del estrés reportado."""
    esperado = 0.29 * float(c[(c.grupo == "chicas") & (c.tramo == "todas")]
                            .primera_etapa.iloc[0])
    with plt.rc_context(p28.PAPER):
        f = plt.figure(figsize=(130 * p28.MM, 68 * p28.MM))
        a = f.add_axes([0.14, 0.3, 0.83, 0.57])
        p28.ejes_paper(a)
        hs = []
        for g, col, marca, hueco, dx in (("chicas", p28.OCRE, "^", False,
                                          -0.12),
                                         ("chicos", p28.GRISR, "o", True,
                                          0.12)):
            s = c[c.grupo == g].set_index("tramo")
            for x, t in enumerate(TRAMOS):
                h = p28.barra(a, x + dx, (s.loc[t, "b"], s.loc[t, "se"]),
                              col, marca, hueco)
            hs.append(h)
        a.axhline(esperado, color=p28.ACC, lw=0.8, ls=":", zorder=1)
        a.text(1.5, esperado + 0.05, "Implied by reported\nmaternal stress",
               ha="center", va="bottom", fontsize=6.5, color=p28.ACC,
               linespacing=1.0)
        ch = c[c.grupo == "chicas"].set_index("tramo")
        cv = c[c.grupo == "chicos"].set_index("tramo")
        a.set_xticks(range(4))
        a.set_xticklabels(ETIQ, fontsize=7.5)
        a.set_xlim(-0.5, 3.5)
        a.set_ylim(-1.2, 1.2)
        p28.formato_eje(a, 0.4)
        a.set_ylabel("Breastfed minus not breastfed,\n"
                     "affected minus unaffected (SD)", fontsize=8)
        a.set_xlabel("Age at the earthquake", fontsize=8, labelpad=3)
        eje_x = a.get_xaxis_transform()
        for x, t in enumerate(TRAMOS):
            a.text(x, -0.42, f"{int(ch.loc[t, 'n_pecho'])} / "
                   f"{int(cv.loc[t, 'n_pecho'])}", ha="center", va="center",
                   fontsize=7, color=p28.MUTED, transform=eje_x)
        a.text(-0.53, -0.42, "Breastfed,\ngirls / boys", ha="right",
               va="center", fontsize=7, color=p28.MUTED, linespacing=1.0,
               transform=eje_x)
        a.legend(hs, ["Girls", "Boys"], loc="lower center",
                 bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False,
                 fontsize=7.5, handletextpad=0.3, columnspacing=1.2,
                 borderaxespad=0.1)
        f.savefig("reports/triple_did.png", dpi=220)
        plt.close(f)
    print("-> reports/triple_did.png")


if __name__ == "__main__":
    main()
