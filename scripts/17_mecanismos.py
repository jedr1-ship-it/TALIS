#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de mecanismos (exploración, fase de discusión — aún sin tablas .tex).

Señales sobre los dos canales de ventana del paper:
  A. Perfil fino por edad al terremoto: salud mental (PHQ-4, resiliencia,
     satisfacción vital) frente a vocabulario (TVIP 2024), con dos tests
     formales: perfiles de daño iguales (PHQ frente a TVIP) y artefacto
     de medición común (PHQ frente a resiliencia).
  B. Angustia del cuidador tras el 27-F (módulo h4 de 2012) y los dos
     brazos de la U.
  C. Daño a la vivienda (h3 de 2012) por edad, dentro de la zona afectada.
  D. Destete en los 3 meses posteriores al 27-F entre los que mamaban,
     zona afectada frente a no afectada, con ventana placebo previa.
  E. Corte escolar del 31 de marzo en los nacidos feb-may 2006 (misma
     memoria, distinto año de entrada al colegio).

Todas las figuras orientan el signo como daño: arriba es peor.

Entradas: data/processed/paper_adolescentes.pkl, interim 2012 y 2024.
Salidas:  reports/mecanismos_tests.md, reports/mecanismos_perfil.png,
          reports/mecanismos_senales.png.
Uso:      python3 scripts/17_mecanismos.py
"""
import importlib.util
import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p15", HERE / "15_paper_estimaciones.py")
p15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p15)

num, fit, xt, zg = p15.num, p15.fit, p15.xt, p15.zg
X_PRE, X_POST = p15.X_PRE, p15.X_POST
OUT = []
Z = 1.96

EDGES = [6, 12, 18, 24, 30, 36, 42, 50]
FLABS = [f"f{a:02d}" for a in EDGES[:-1]]
FMID = {lb: (a + b - 1) / 2 for lb, a, b in zip(FLABS, EDGES, EDGES[1:])}
FTXT = [f"{a}–{b - 1}" for a, b in zip(EDGES, EDGES[1:])]

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e2e1dc"
MH, VOC, NEU = "#2a78d6", "#eb6834", "#52514e"


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def bse(r, expr):
    t = r.t_test(expr)
    return (float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]),
            float(np.ravel(t.pvalue)[0]))


def fmt(t):
    return f"{t[0]:+.3f} (ee {t[1]:.3f}, p={t[2]:.3f})"


def carga():
    d, _, _ = p15.load_data()
    v12, _ = pyreadstat.read_dta(
        "data/interim/2012/Entrevistada_2012.dta",
        usecols=["folio", "h3", "h4_2", "h4_4", "h4_5", "b30", "b32"])
    v12["folio"] = num(v12.folio).astype("int64")
    v12 = v12.drop_duplicates("folio")
    h3 = num(v12.h3)
    v12["dano_mayor"] = np.where(h3.isin([1, 2, 3]), 1.0,
                                 np.where(h3.isin([4, 5]), 0.0, np.nan))
    sx = [num(v12[f"h4_{i}"]) for i in (2, 4, 5)]
    resp = [s.isin([1, 2]) for s in sx]
    v12["angustia12"] = np.where(
        np.any([s == 1 for s in sx], axis=0), 1.0,
        np.where(np.all(resp, axis=0), 0.0, np.nan))
    b30, b32 = num(v12.b30), num(v12.b32)
    v12["mamando"] = np.nan        # mes de vida hasta el que mamó
    v12.loc[b30 == 3, "mamando"] = 0.0
    v12.loc[b30.isin([1, 2]), "mamando"] = b32.where(~b32.isin([88, 99]))
    v12.loc[b30 == 2, "mamando"] = 990.0   # seguía mamando en 2012
    t24, _ = pyreadstat.read_dta(
        "data/interim/2024/Base evaluaciones Stata.dta",
        usecols=["folio", "tvip_pst_hispano"])
    t24["folio"] = num(t24.folio).astype("int64")
    t24 = t24.groupby("folio", as_index=False).first()
    d = (d.merge(v12[["folio", "dano_mayor", "angustia12", "mamando"]],
                 on="folio", how="left")
          .merge(t24, on="folio", how="left"))
    d["z_tvip"] = zg(d.tvip_pst_hispano)
    return d


def fino(d, y):
    """Perfil en bins de 6 meses (ref. 6-11m), especificación col. 3."""
    dd = d.dropna(subset=[y, "EQ", "estrato", "w", "cohorte"])
    dd = dd[(dd.w > 0) & dd.edadq_m.between(6, 49)].copy()
    dd["est"] = dd.estrato.astype(int).astype(str)
    dd["coh"] = dd.cohorte.astype(int).astype(str)
    dd["binf"] = pd.cut(dd.edadq_m, EDGES, right=False, labels=FLABS)
    ivs = []
    for lb in FLABS[1:]:
        dd[f"I{lb}"] = (dd.binf == lb).astype(float) * dd.EQ
        ivs.append(f"I{lb}")
    rhs = " + ".join(ivs + ["C(binf)", "C(est)", "C(coh)"]
                     + xt(dd, X_PRE) + xt(dd, X_POST))
    r = smf.wls(f"{y} ~ {rhs}", data=dd, weights=dd.w).fit(
        cov_type="cluster", cov_kwds={"groups": dd.est})
    prof = {FLABS[0]: (0.0, 0.0, 1.0)}
    prof.update({lb: (r.params[f"I{lb}"], r.bse[f"I{lb}"],
                      r.pvalues[f"I{lb}"]) for lb in FLABS[1:]})
    return prof, int(r.nobs)


def test_a(d):
    log("\n## A. Perfil por edad al terremoto: salud mental y vocabulario")
    res = {}
    for y, lab in [("z_phq4", "PHQ-4 (sintomas; alto = peor)"),
                   ("z_resil", "resiliencia (alto = mejor)"),
                   ("z_satisf", "satisfaccion vital (alto = mejor)"),
                   ("z_tvip", "TVIP (vocabulario; alto = mejor)")]:
        prof, n = fino(d, y)
        res[y] = prof
        cells = "; ".join(f"{t}: {prof[lb][0]:+.3f} (p={prof[lb][2]:.3f})"
                          for t, lb in zip(FTXT[1:], FLABS[1:]))
        log(f"- {lab}, N={n}, ref. 6-11m | {cells}")
    log("Tests formales en bins gruesos (spec col. 3):")
    d = d.copy()
    d["dif_dano"] = d.z_phq4 + d.z_tvip
    d["dif_artef"] = d.z_phq4 - d.z_resil
    r = fit(d, "dif_dano", col=3)
    res["dif_dano"] = r
    log(f"- Daño en salud mental menos daño en vocabulario "
        f"(PHQ + TVIP), N={r['n']}: edad 2 frente a bebes "
        f"{fmt(r['b']['24-35m'])}; 3-4 frente a 2 {fmt(r['contr'])}")
    r = fit(d, "dif_artef", col=3)
    res["dif_artef"] = r
    log(f"- Artefacto comun (PHQ menos resiliencia), N={r['n']}: edad 2 "
        f"frente a bebes {fmt(r['b']['24-35m'])}; 3-4 frente a 2 "
        f"{fmt(r['contr'])}")
    return res


def test_b(d):
    log("\n## B. Angustia del cuidador (h4 2012) y los dos brazos")
    tt = d.dropna(subset=["angustia12"])
    log(f"angustia12 (estres, miedo o recuerdos del cuidador): media "
        f"{tt.angustia12.mean():.3f}; por zona "
        f"{tt.groupby('EQ').angustia12.mean().round(3).to_dict()}")
    res = {}
    for g, sub in [(1, lambda x: x.angustia12 == 1),
                   (0, lambda x: x.angustia12 == 0)]:
        for y in ("z_phq4", "gad2_bin"):
            r = fit(d, y, col=3, sample=sub)
            b24 = r["b"]["24-35m"]
            bebe = (-b24[0], b24[1], b24[2])
            res[(g, y)] = {"bebe": bebe, "memoria": r["contr"], "n": r["n"]}
            log(f"- cuidador {'con' if g else 'sin'} angustia | {y}: "
                f"bebes frente a 2 {fmt(bebe)}; 3-4 frente a 2 "
                f"{fmt(r['contr'])}; N={r['n']}")
    return res


def test_c(d):
    log("\n## C. Daño a la vivienda (h3 2012) por edad, zona afectada")
    tt = d[d.EQ == 1].dropna(subset=["dano_mayor"])
    log(f"P(destruida o daño mayor | zona afectada) = "
        f"{tt.dano_mayor.mean():.3f} (N={len(tt)}). Efecto total del "
        f"daño en cada edad (principal + interaccion):")
    res = {}
    for y in ("z_phq4", "gad2_bin", "z_tvip"):
        r = fit(d, y, col=3, dose="dano_mayor", extra_x=["dano_mayor"],
                sample=lambda x: x.EQ == 1, keep_model=True)
        rm = smf.wls(r["_f"], data=r["_d"], weights=r["_w"]).fit(
            cov_type="cluster", cov_kwds={"groups": r["_d"].est})
        tot = {"0-11m": bse(rm, "dano_mayor = 0")}
        for k, v in (("12-23m", "I_12"), ("24-35m", "I_24"),
                     ("36-59m", "I_36")):
            tot[k] = bse(rm, f"dano_mayor + {v} = 0")
        res[y] = tot
        log(f"- {y}: " + "; ".join(f"{k} {fmt(v)}" for k, v in tot.items())
            + f"; N={r['n']}")
    return res


def test_d(d):
    log("\n## D. Destete alrededor del 27-F (b30/b32 2012)")
    tt = d.dropna(subset=["mamando"]).copy()
    tt = tt[tt.edadq_m.between(1, 18) & (tt.mamando >= tt.edadq_m)]
    tt["destete"] = (tt.mamando <= tt.edadq_m + 3).astype(float)
    pre = d.dropna(subset=["mamando"]).copy()
    pre = pre[pre.edadq_m.between(5, 18)
              & (pre.mamando >= pre.edadq_m - 4)]
    pre["destete"] = pre.mamando.between(
        pre.edadq_m - 4, pre.edadq_m - 1).astype(float)
    res = {}
    for k, lab, base in [("post", "3 meses tras el 27-F", tt),
                         ("pre", "4 meses antes (placebo)", pre)]:
        base = base.dropna(subset=["w", "estrato"])
        base = base[base.w > 0].copy()
        base["est"] = base.estrato.astype(int).astype(str)
        rhs = " + ".join(["EQ", "C(edadq_m)"] + xt(base, X_PRE))
        r = smf.wls(f"destete ~ {rhs}", data=base, weights=base.w).fit(
            cov_type="cluster", cov_kwds={"groups": base.est})
        res[k] = (r.params["EQ"], r.bse["EQ"], r.pvalues["EQ"],
                  base.destete.mean(), int(r.nobs))
        log(f"- destete en los {lab}: media {base.destete.mean():.3f}; "
            f"zona afectada {fmt(res[k])}; N={int(r.nobs)}")
    return res


def test_e(d):
    log("\n## E. Corte escolar del 31 de marzo (nacidos feb-may 2006)")
    tt = d.copy()
    tt["by"], tt["bm"] = tt.birth_ym // 12, tt.birth_ym % 12 + 1
    tt = tt[(tt.by == 2006) & tt.bm.between(2, 5)].copy()
    tt["temprano"] = (tt.bm <= 3).astype(float)   # entra en marzo 2010
    tt = tt.dropna(subset=["w", "estrato", "cohorte"])
    tt = tt[tt.w > 0].copy()
    tt["est"] = tt.estrato.astype(int).astype(str)
    tt["ExT"] = tt.EQ * tt.temprano
    ctr = xt(tt, X_PRE) + xt(tt, X_POST)
    res = {}
    for y in ("z_phq4", "gad2_bin", "z_tvip"):
        ty = tt.dropna(subset=[y])
        for k, rhs in (("sin", ["ExT", "EQ", "temprano"]),
                       ("con", ["ExT", "temprano", "C(est)"])):
            r = smf.wls(f"{y} ~ {' + '.join(rhs + ctr)}", data=ty,
                        weights=ty.w).fit(cov_type="cluster",
                                          cov_kwds={"groups": ty.est})
            res[(y, k)] = (r.params["ExT"], r.bse["ExT"], r.pvalues["ExT"])
        log(f"- {y}: zona afectada x entrada en marzo 2010 "
            f"{fmt(res[(y, 'sin')])}; con EF de estrato "
            f"{fmt(res[(y, 'con')])}; N={len(ty)}")
    log(f"  (nacidos feb-mar: {int((tt.temprano == 1).sum())}; "
        f"abr-may: {int((tt.temprano == 0).sum())})")
    return res


# ------------------------------- figuras -------------------------------

def estilo(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b9b8b2")
    ax.tick_params(colors=INK2, labelsize=11.5)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.axhline(0, color="#8d8c86", lw=1.1, zorder=1)


def fig_perfil(a, path):
    fig, ax = plt.subplots(figsize=(11, 6.6), facecolor=SURF)
    estilo(ax)
    ax.axvspan(23.5, 35.5, color="#efeeea", zorder=0)
    ax.axvline(35.5, color="#8d8c86", lw=1.2, ls=(0, (4, 3)), zorder=1)
    series = [("z_phq4", +1, MH, "o", "-", 2.4, -0.55, True,
               "Síntomas de ansiedad y depresión (PHQ-4)"),
              ("z_resil", -1, MH, "s", (0, (5, 2)), 1.3, 0, False,
               "Resiliencia perdida"),
              ("z_satisf", -1, MH, "^", (0, (1, 2)), 1.3, 0, False,
               "Satisfacción vital perdida"),
              ("z_tvip", -1, VOC, "o", "-", 2.4, +0.55, True,
               "Vocabulario perdido (TVIP)")]
    for y, sg, col, mk, ls, lw, dx, ci, lab in series:
        prof = a[y]
        xs = np.array([FMID[lb] for lb in FLABS]) + dx
        xs[0] = FMID[FLABS[0]]
        bs = np.array([sg * prof[lb][0] for lb in FLABS])
        ses = np.array([prof[lb][1] for lb in FLABS])
        ax.plot(xs, bs, color=col, lw=lw, ls=ls, zorder=3, label=lab)
        if ci:
            ax.errorbar(xs[1:], bs[1:], yerr=Z * ses[1:], fmt="none",
                        ecolor=col, elinewidth=1.4, alpha=0.55, zorder=2)
            ax.scatter(xs[1:], bs[1:], s=58, color=col, zorder=4,
                       edgecolor=SURF, linewidth=1.5)
        else:
            ax.scatter(xs[1:], bs[1:], s=30, marker=mk, color=col,
                       zorder=4, edgecolor=SURF, linewidth=1.0)
    ax.scatter([FMID[FLABS[0]]], [0], s=64, facecolor=SURF, edgecolor=INK2,
               linewidth=1.6, zorder=5)
    ax.set_xticks([FMID[lb] for lb in FLABS])
    ax.set_xticklabels(FTXT)
    ax.set_xlim(6.5, 50.5)
    ax.set_xlabel("Edad al terremoto (meses)", fontsize=12.5, color=INK)
    ax.set_ylabel("Daño adicional frente a los expuestos\n"
                  "a los 6–11 meses (desv. estándar)",
                  fontsize=12.5, color=INK)
    lo, hi = ax.get_ylim()
    ax.text(29.5, hi - 0.012, "2 años", ha="center", va="top",
            fontsize=12, color=INK2, fontweight="bold")
    ax.text(36.2, lo + 0.015, "desde aquí el niño ya\nforma recuerdos "
            "duraderos", ha="left", va="bottom", fontsize=10.5,
            color=INK2)
    ax.text(6.9, hi - 0.012, "▲ peor", ha="left", va="top",
            fontsize=10.5, color=INK2)
    ax.text(6.9, lo + 0.015, "▼ mejor", ha="left", va="bottom",
            fontsize=10.5, color=INK2)
    leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13),
                    ncol=2, frameon=False, fontsize=11.5,
                    handlelength=2.6)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.suptitle("Daño por edad al terremoto, salud mental y vocabulario",
                 x=0.075, ha="left", fontsize=15.5, fontweight="bold",
                 color=INK, y=0.985)
    fig.text(0.075, 0.915,
             "Adolescentes de 15–18 años en 2024, zona afectada frente a "
             "no afectada. Barras = IC 95%.", fontsize=11, color=INK2,
             ha="left")
    fig.subplots_adjust(left=0.105, right=0.975, top=0.885, bottom=0.25)
    fig.savefig(path, dpi=150, facecolor=SURF)
    plt.close(fig)


def dot(ax, x, t, col, filled=True, mk="o", s=70, scale=1.0):
    b, se = t[0] * scale, t[1] * abs(scale)
    ax.errorbar([x], [b], yerr=[Z * se], fmt="none", ecolor=col,
                elinewidth=1.8, alpha=0.6, zorder=2)
    ax.scatter([x], [b], s=s, marker=mk, zorder=3, linewidth=1.8,
               facecolor=col if filled else SURF, edgecolor=col)


def fig_senales(res, path):
    fig, axs = plt.subplots(2, 2, figsize=(12, 9.6), facecolor=SURF)
    (ax1, ax2), (ax3, ax4) = axs
    for ax in axs.flat:
        estilo(ax)

    # destete
    dd = res["D"]
    dot(ax1, 0, dd["post"], NEU, True, scale=100)
    dot(ax1, 1, dd["pre"], NEU, False, scale=100)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["En los 3 meses\ntras el 27-F",
                         "En los 4 meses antes\n(placebo)"])
    ax1.set_xlim(-0.6, 1.6)
    ax1.set_ylabel("Efecto de la zona afectada\n(puntos porcentuales)",
                   fontsize=11.5, color=INK)
    ax1.set_title("Destete entre los que mamaban el 27-F", loc="left",
                  fontsize=13, fontweight="bold", color=INK)
    for x, k in ((0, "post"), (1, "pre")):
        ax1.annotate(f"{dd[k][0] * 100:+.1f}", (x, dd[k][0] * 100),
                     xytext=(10, 0), textcoords="offset points",
                     va="center", fontsize=11.5, color=INK)

    # daño a la vivienda
    cc = res["C"]
    bins = ["0-11m", "12-23m", "24-35m", "36-59m"]
    for y, sg, col, dx in (("z_phq4", 1, MH, -0.11), ("z_tvip", -1, VOC,
                                                       0.11)):
        for i, k in enumerate(bins):
            dot(ax2, i + dx, cc[y][k], col, True, scale=sg, s=60)
    ax2.set_xticks(range(4))
    ax2.set_xticklabels(["bebés", "1 año", "2 años", "3–4 años"])
    ax2.set_xlabel("Edad al terremoto", fontsize=11.5, color=INK)
    ax2.set_ylabel("Efecto de vivienda destruida o\ncon daño mayor "
                   "(desv. estándar)", fontsize=11.5, color=INK)
    ax2.set_title("Daño a la vivienda, solo zona afectada", loc="left",
                  fontsize=13, fontweight="bold", color=INK)

    # angustia del cuidador
    bb = res["B"]
    for i, arm in enumerate(("bebe", "memoria")):
        dot(ax3, i - 0.12, bb[(1, "z_phq4")][arm], MH, True)
        dot(ax3, i + 0.12, bb[(0, "z_phq4")][arm], MH, False)
    ax3.set_xticks([0, 1])
    ax3.set_xticklabels(["Bebés frente a 2 años", "3–4 frente a 2 años"])
    ax3.set_xlim(-0.6, 1.6)
    ax3.set_ylabel("Síntomas PHQ-4 de más\n(desv. estándar)",
                   fontsize=11.5, color=INK)
    ax3.set_title("Los dos brazos según la angustia del cuidador",
                  loc="left", fontsize=13, fontweight="bold", color=INK)
    ax3.scatter([], [], s=60, color=MH, label="cuidador con angustia")
    ax3.scatter([], [], s=60, facecolor=SURF, edgecolor=MH, linewidth=1.8,
                label="cuidador sin angustia")
    ax3.legend(loc="lower right", frameon=False, fontsize=10.5)

    # corte escolar
    ee = res["E"]
    for i, (y, sg, col) in enumerate((("z_phq4", 1, MH),
                                      ("z_tvip", -1, VOC))):
        dot(ax4, i - 0.12, ee[(y, "sin")], col, True, scale=sg)
        dot(ax4, i + 0.12, ee[(y, "con")], col, True, mk="D", s=55,
            scale=sg)
    ax4.set_xticks([0, 1])
    ax4.set_xticklabels(["Síntomas PHQ-4", "Vocabulario perdido"])
    ax4.set_xlim(-0.6, 1.6)
    ax4.set_ylabel("Efecto de entrar al colegio en marzo\n2010 en zona "
                   "afectada (desv. estándar)", fontsize=11.5, color=INK)
    ax4.set_title("Corte escolar, nacidos feb–may 2006", loc="left",
                  fontsize=13, fontweight="bold", color=INK)
    ax4.scatter([], [], s=60, color=INK2, label="sin EF de estrato")
    ax4.scatter([], [], s=50, marker="D", color=INK2,
                label="con EF de estrato")
    ax4.legend(loc="upper right", frameon=False, fontsize=10.5)

    for ax in (ax2, ax3, ax4):
        lo, hi = ax.get_ylim()
        ax.text(0.01, 0.99, "▲ peor", transform=ax.transAxes, ha="left",
                va="top", fontsize=10, color=INK2)
    hs = [plt.Line2D([], [], ls="", marker="o", ms=9, color=c, label=t)
          for c, t in ((MH, "síntomas PHQ-4"), (VOC, "vocabulario perdido"),
                       (NEU, "destete"))]
    fig.legend(handles=hs, loc="upper left", bbox_to_anchor=(0.055, 0.935),
               ncol=3, frameon=False, fontsize=11.5, handletextpad=0.3,
               columnspacing=1.6)
    fig.suptitle("Cuatro señales sobre los canales", x=0.06, ha="left",
                 fontsize=15.5, fontweight="bold", color=INK, y=0.99)
    fig.text(0.06, 0.951, "Puntos con IC 95%. Signo orientado para que "
             "arriba sea peor.", fontsize=11, color=INK2, ha="left")
    fig.subplots_adjust(left=0.1, right=0.98, top=0.86, bottom=0.07,
                        hspace=0.42, wspace=0.32)
    fig.savefig(path, dpi=150, facecolor=SURF)
    plt.close(fig)


def main():
    d = carga()
    log("# Tests de mecanismos — exploracion "
        "(scripts/17_mecanismos.py)")
    log(f"Muestra base: {len(d)}; con modulo 2012: "
        f"{d.angustia12.notna().sum()}; con TVIP 2024: "
        f"{d.z_tvip.notna().sum()}")
    res = {"A": test_a(d), "B": test_b(d), "C": test_c(d),
           "D": test_d(d), "E": test_e(d)}
    Path("reports").mkdir(exist_ok=True)
    fig_perfil(res["A"], "reports/mecanismos_perfil.png")
    fig_senales(res, "reports/mecanismos_senales.png")
    Path("reports/mecanismos_tests.md").write_text(
        "\n".join(OUT) + "\n", encoding="utf-8")
    log("\n-> reports/mecanismos_tests.md, mecanismos_perfil.png, "
        "mecanismos_senales.png")


if __name__ == "__main__":
    main()
