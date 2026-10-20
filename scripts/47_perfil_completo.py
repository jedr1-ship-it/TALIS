#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Se separa el pico de 6-11 meses de sus vecinos? El perfil completo.

Comentarios tipo referee (punto 1 y los baratos: 2, 4, 5 y 7). Mismo
diseño que la presentación (EF de comuna de selección, año de nacimiento y
grupo de edad; controles; pesos ELPI; EE por comuna), en las chicas y los
chicos de 2024:

  1. Perfil en tramos de seis meses (6-11, 12-17, ..., 42-49) por zona
     afectada, normalizado para que sume cero (ningún tramo hace de
     referencia), y una curva suave (B-spline de la edad en meses x zona).
     Prueba conjunta de perfil plano; 6-11 frente a 12-17 y frente a 12-23.
  2. 6-11 frente al resto sin el tramo de 2-3 años.
  4. Celdas sexo x tramo x zona y comunas por zona. Inferencia con la zona
     asignada por región: inferencia por aleatorización permutando cuáles
     6 de las 15 regiones son "afectadas" (las 5.005 combinaciones), y EE
     por región. PGA en terciles; sin Biobío y Maule; sin Santiago.
  5. Diferencia chicas menos chicos con su p-valor (modelo interactuado).
  7. Sin los controles de 2012 (posteriores al terremoto) y solo con
     efectos fijos.

Salida: reports/perfil_completo.md, reports/perfil_completo.csv y
        reports/perfil_completo.png
Uso:    python3 scripts/47_perfil_completo.py
"""
import importlib.util
import itertools
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
import numpy as np                                   # noqa: E402
import pandas as pd                                  # noqa: E402
import patsy                                         # noqa: E402
import statsmodels.formula.api as smf                # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    s = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


p28 = modulo("p28", "28_beamer_advisor.py")
p15 = modulo("p15", "15_paper_estimaciones.py")
SEIS = ([6, 12, 18, 24, 30, 36, 42, 50],
        ["6-11", "12-17", "18-23", "24-29", "30-35", "36-41", "42-49"])
CUATRO = ([6, 12, 24, 36, 50], ["6-11", "12-23", "24-35", "36-49"])
SEXOS = (("chicas", 1), ("chicos", 0))
OUT, FILAS = [], []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(b, se, p):
    st = "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""
    return f"{b:+.3f}{st} (ee {se:.3f}, p={p:.3f})"


def carga():
    d, _, _ = p15.load_data()
    d = d[d.z_phq4.notna() & (d.w > 0) & d.edadq_m.between(6, 49)].copy()
    d["est"] = d.estrato.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    d["reg"] = (pd.to_numeric(d.cut_comuna_seleccion) // 1000).astype(int)
    d["pga10"] = d.pga / 10
    for (bordes, et), col in ((SEIS, "b6"), (CUATRO, "b4")):
        d[col] = pd.cut(d.edadq_m, bordes, right=False,
                        labels=et).astype(str)
    return d


def controles(x, post=True, tendencia=True):
    pre = [v for v in p15.X_PRE if tendencia or v != "edad_meses"]
    return p15.xt(x, pre) + (p15.xt(x, p15.X_POST) if post else [])


def wls(x, rhs, grupos="est", y="z_phq4"):
    x = x.dropna(subset=[y])
    return smf.wls(f"{y} ~ " + " + ".join(rhs), data=x, weights=x.w).fit(
        cov_type="cluster", cov_kwds={"groups": x[grupos]})


def prueba(r, c):
    t = r.t_test(c)
    return (float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]),
            float(np.ravel(t.pvalue)[0]))


# ------------------------------------------------------------- 1. perfil

def tramos_seis(x, y="z_phq4"):
    """Brecha zona afectada menos no afectada en cada tramo de seis meses,
    centrada en la media de los tramos."""
    x = x.dropna(subset=[y]).copy()
    et = SEIS[1]
    ii = []
    for t in et[1:]:
        k = "S" + t.replace("-", "_")
        x[k] = (x.b6 == t) * x.EQ
        ii.append(k)
    r = wls(x, ii + ["C(b6)", "C(est)", "C(coh)"] + controles(x), y=y)
    nombres = list(r.params.index)
    K = len(et)
    res = {}
    for j, t in enumerate(et):
        c = np.zeros(len(nombres))
        for i, k in enumerate(ii):            # delta_ref = 0
            c[nombres.index(k)] -= 1.0 / K
        if j > 0:
            c[nombres.index(ii[j - 1])] += 1.0
        res[t] = prueba(r, c)
    conj = float(r.f_test(", ".join(f"{k} = 0" for k in ii)).pvalue)
    vec = prueba(r, f"{ii[0]} = 0")           # 12-17 menos 6-11
    vec = (-vec[0], vec[1], vec[2])
    return res, conj, vec, int(r.nobs)


def curva(x, df=5):
    """Brecha suave: B-spline de la edad en meses x zona, centrada en la
    media ponderada de la muestra; IC punto a punto por el método delta."""
    x = x.copy()
    base = patsy.dmatrix(f"bs(edadq_m, df={df}) - 1", x,
                         return_type="dataframe")
    ks = []
    for j in range(base.shape[1]):
        x[f"B{j}"], x[f"E{j}"] = base.iloc[:, j], base.iloc[:, j] * x.EQ
        ks.append(f"E{j}")
    r = wls(x, ks + [f"B{j}" for j in range(base.shape[1])]
            + ["C(est)", "C(coh)"] + controles(x, tendencia=False))
    g = r.params[ks].values
    V = r.cov_params().loc[ks, ks].values
    malla = np.arange(6, 50)
    Bm = patsy.build_design_matrices([base.design_info],
                                     pd.DataFrame({"edadq_m": malla}))[0]
    Bm = np.asarray(Bm)
    media = np.average(np.asarray(base), axis=0, weights=x.w)
    C = Bm - media
    f = C @ g
    se = np.sqrt(np.einsum("ij,jk,ik->i", C, V, C))
    return malla, f, se


# --------------------------------------------------------- 4. inferencia

def aleatorizacion(x):
    """Coeficiente de 6-11 meses x zona para cada forma de elegir 6 de las
    15 regiones como zona afectada (Frisch-Waugh: una QR, luego cada
    permutación es una proyección)."""
    x = x.copy()
    x["D"] = (x.b4 == "6-11") * x.EQ
    r = wls(x, ["D", "C(b4)", "C(est)", "C(coh)"] + controles(x))
    nombres = list(r.model.exog_names)
    j = nombres.index("D")
    X = np.asarray(r.model.exog)
    raiz = np.sqrt(np.asarray(r.model.weights))
    W = np.delete(X, j, axis=1) * raiz[:, None]
    Q, _ = np.linalg.qr(W)
    y = np.asarray(r.model.endog) * raiz
    yr = y - Q @ (Q.T @ y)
    bebe = (x.b4.values == "6-11").astype(float)
    regiones = sorted(x.reg.unique())
    reg = x.reg.values

    def beta(conj):
        dd = bebe * np.isin(reg, conj) * raiz
        dd = dd - Q @ (Q.T @ dd)
        return float(dd @ yr / (dd @ dd))
    b0 = beta([5, 6, 7, 8, 9, 13])
    bs = np.array([beta(list(c)) for c in
                   itertools.combinations(regiones, 6)])
    p = float((np.abs(bs) >= abs(b0) - 1e-12).mean())
    rr = wls(x, ["D", "C(b4)", "C(est)", "C(coh)"] + controles(x),
             grupos="reg")
    return b0, p, len(bs), float((bs >= b0 - 1e-12).mean()), \
        (float(rr.params["D"]), float(rr.bse["D"]), float(rr.pvalues["D"]))


def contraste(x, rhs_extra=(), dosis="EQ", post=True, tendencia=True,
              solo_ef=False, y="z_phq4"):
    x = x.dropna(subset=[y]).copy()
    x["D"] = (x.b4 == "6-11") * x[dosis]
    rhs = ["D", "C(b4)", "C(est)", "C(coh)"]
    if not solo_ef:
        rhs += controles(x, post, tendencia)
    r = wls(x, rhs + list(rhs_extra), y=y)
    return (float(r.params["D"]), float(r.bse["D"]),
            float(r.pvalues["D"])), int(r.nobs)


def figura(perfiles, curvas):
    with plt.rc_context(p28.PAPER):
        f = plt.figure(figsize=(144 * p28.MM, 60 * p28.MM))
        for i, (g, nombre) in enumerate((("chicas", "Girls"),
                                         ("chicos", "Boys"))):
            a = f.add_axes([0.11 + i * 0.46, 0.2, 0.38, 0.66])
            p28.ejes_paper(a)
            malla, fc, se = curvas[g]
            a.fill_between(malla, fc - 1.96 * se, fc + 1.96 * se,
                           color=p28.ACC, alpha=0.15, lw=0)
            a.plot(malla, fc, color=p28.ACC, lw=1.2)
            centros = [8.5, 14.5, 20.5, 26.5, 32.5, 38.5, 45.5]
            res = perfiles[g]
            for c, t in zip(centros, SEIS[1]):
                b, se_, _ = res[t]
                a.errorbar(c, b, yerr=1.96 * se_, fmt="o", color=p28.INK,
                           ms=4, capsize=2, elinewidth=0.9, zorder=3)
            for corte in (12, 24, 36):
                a.axvline(corte, color=p28.GRID, lw=0.6, zorder=0)
            a.set_xlim(5, 50)
            a.set_ylim(-0.8, 0.8)
            p28.formato_eje(a, 0.4)
            a.set_xticks([6, 12, 18, 24, 30, 36, 42, 49])
            a.set_title(nombre, fontsize=9, pad=4)
            if i == 0:
                a.set_ylabel("Affected minus unaffected,\n"
                             "centered (SD)", fontsize=8)
        f.text(0.53, 0.02, "Age at the earthquake (months)", ha="center",
               fontsize=8.5)
        f.savefig("reports/perfil_completo.png", dpi=220)
        plt.close(f)
    print("-> reports/perfil_completo.png")


def main():
    d = carga()
    log("# El perfil completo por edad al terremoto "
        "(scripts/47_perfil_completo.py)")
    log("PHQ-4 (DE), zona afectada menos no afectada; EF de comuna, año de "
        "nacimiento y tramo; controles; pesos ELPI; EE por comuna salvo "
        "donde se indica.")
    log("\n## Celdas: adolescentes por sexo, tramo y zona (no afectada / "
        "afectada) y comunas")
    for g, sx in SEXOS:
        x = d[d.mujer == sx]
        n = x.groupby(["b6", "EQ"]).size()
        log(f"- {g}: " + " | ".join(
            f"{t}: {n.get((t, 0.0), 0)} / {n.get((t, 1.0), 0)}"
            for t in SEIS[1]))
    log(f"- comunas de selección: afectada {d[d.EQ == 1].est.nunique()}, "
        f"no afectada {d[d.EQ == 0].est.nunique()}; regiones: afectada 6, "
        f"no afectada {d[d.EQ == 0].reg.nunique()}")

    log("\n## 1. Tramos de seis meses, centrados (suman cero)")
    perfiles, curvas = {}, {}
    for g, sx in SEXOS:
        x = d[d.mujer == sx]
        res, conj, vec, n = tramos_seis(x)
        perfiles[g] = res
        curvas[g] = curva(x)
        log(f"- {g}: " + " | ".join(f"{t} {fmt(*v)}" for t, v in res.items())
            + f" | N={n:,}")
        log(f"  perfil plano, prueba conjunta: p={conj:.3f}; 6-11 menos "
            f"12-17: {fmt(*vec)}")
        for t, v in res.items():
            FILAS.append({"parte": "seis", "grupo": g, "tramo": t, "b": v[0],
                          "se": v[1], "p": v[2]})
        x4 = x.copy()
        for t in ("6-11", "24-35", "36-49"):
            x4["V" + t.replace("-", "_")] = (x4.b4 == t) * x4.EQ
        r = wls(x4, ["V6_11", "V24_35", "V36_49", "C(b4)", "C(est)",
                     "C(coh)"] + controles(x4))
        log(f"  6-11 frente a 12-23: {fmt(*prueba(r, 'V6_11 = 0'))}")
    figura(perfiles, curvas)

    log("\n## 2. 6-11 meses frente al resto, sin el tramo de 2-3 años")
    for g, sx in SEXOS:
        x = d[(d.mujer == sx) & (d.b4 != "24-35")]
        r, n = contraste(x)
        log(f"- {g}: {fmt(*r)}; N={n:,}")

    log("\n## 5. Chicas menos chicos (modelo interactuado)")
    x = d.copy()
    x["D"] = (x.b4 == "6-11") * x.EQ
    ctr = controles(x)
    base = ["D", "C(b4)", "C(est)", "C(coh)"] + [c for c in ctr
                                                  if c != "mujer"]
    r = wls(x, base + [f"{v}:mujer" for v in base] + ["mujer"])
    log(f"- chicos {fmt(r.params['D'], r.bse['D'], r.pvalues['D'])}; "
        f"chicas menos chicos {fmt(r.params['D:mujer'], r.bse['D:mujer'], r.pvalues['D:mujer'])}")

    log("\n## 7. Controles (chicas)")
    ch = d[d.mujer == 1]
    for lab, kw in (("solo efectos fijos", {"solo_ef": True}),
                    ("con los de 2010, sin los de 2012", {"post": False}),
                    ("con los de 2010 y 2012 (principal)", {})):
        r, n = contraste(ch, **kw)
        log(f"- {lab}: {fmt(*r)}; N={n:,}")
    sub = ch.dropna(subset=["z_peso", "z_talla", "z_gest"])
    r, n = contraste(sub)
    log(f"- chicas con registro de nacimiento, sin controles al nacer: "
        f"{fmt(*r)}; N={n:,}")

    log("\n## 4. Inferencia con la zona asignada por región, y dosis")
    for g, sx in SEXOS:
        x = d[d.mujer == sx]
        b0, p, k, p1, rr = aleatorizacion(x)
        log(f"- {g}: coeficiente {b0:+.3f}; aleatorización por región, "
            f"p bilateral={p:.3f}, unilateral={p1:.3f} ({k:,} asignaciones)"
            f"; EE por región (15): {fmt(*rr)}")
    for g, sx in SEXOS:
        x = d[d.mujer == sx].copy()
        cortes = x[x.EQ == 1].pga.quantile([1 / 3, 2 / 3]).values
        x["T1"] = (x.EQ == 1) & (x.pga <= cortes[0])
        x["T2"] = (x.EQ == 1) & (x.pga > cortes[0]) & (x.pga <= cortes[1])
        x["T3"] = (x.EQ == 1) & (x.pga > cortes[1])
        for k in ("T1", "T2", "T3"):
            x[f"D{k}"] = (x.b4 == "6-11") * x[k].astype(float)
        r = wls(x, ["DT1", "DT2", "DT3", "C(b4)", "C(est)", "C(coh)"]
                + controles(x))
        log(f"- {g}, terciles de PGA en la zona afectada (cortes "
            f"{cortes[0]:.0f} y {cortes[1]:.0f} %g), cada uno frente a la "
            "zona no afectada: " + " | ".join(
                f"{k} {fmt(r.params['D' + k], r.bse['D' + k], r.pvalues['D' + k])}"
                for k in ("T1", "T2", "T3")))
    for lab, fuera in (("sin Biobío y Maule", [7, 8]), ("sin Santiago", [13])):
        for g, sx in SEXOS:
            x = d[(d.mujer == sx) & ~d.reg.isin(fuera)]
            r, n = contraste(x)
            log(f"- {lab}, {g}: {fmt(*r)}; N={n:,}")
    pd.DataFrame(FILAS).to_csv("reports/perfil_completo.csv", index=False)
    Path("reports/perfil_completo.md").write_text("\n".join(OUT) + "\n",
                                                  encoding="utf-8")
    print("-> reports/perfil_completo.md, reports/perfil_completo.csv")


if __name__ == "__main__":
    main()
