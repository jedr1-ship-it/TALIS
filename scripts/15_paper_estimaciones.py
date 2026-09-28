#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fases 1–3 — todas las estimaciones del paper y sus tablas .tex.

Entradas: data/processed/paper_adolescentes.pkl, paper_atricion.pkl,
          pga_comuna.csv (opcional; si falta, la tabla de dosis se omite).
Salidas:  paper/tables/*.tex (fragmentos tabular, booktabs),
          paper/figures/*.pdf, reports/paper_numeros.md (log).

Especificación central (ec. 2 del paper):
  Y = Σ_a β_a (Bin_a × Dosis_m) + γ_a Bin_a + ψ_m + θ_c + X'δ + ε
  ref. 0–11 meses el 27-F; ψ_m comuna de selección pre-terremoto;
  cluster comuna; pesos f_exp 2024.
Columnas: (1) FE; (2) +X pre-27F; (3) +controles 2012; (4) sin RM.

Uso: python3 scripts/15_paper_estimaciones.py [--solo t3,t7] [--rapido]
"""
import argparse
import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
TAB = Path("paper/tables")
FIG = Path("paper/figures")
LOG = []

BINS = ["0-11m", "12-23m", "24-35m", "36-59m"]
IV = {"12-23m": "I_12", "24-35m": "I_24", "36-59m": "I_36"}
LAB = {"12-23m": "Expuesto con 1 a\\~no (12--23 m.)",
       "24-35m": "Expuesto con 2 a\\~nos (24--35 m.)",
       "36-59m": "Expuesto con 3--4 a\\~nos (36--59 m.)"}
X_PRE = ["mujer", "edad_meses", "edad_madre10", "educ_madre10",
         "tot_per10", "rural10"]
X_POST = ["n_hijos", "mh_madre", "mh_padre", "mh_ofam", "mh_miss"]
CONTR = "I_36 - I_24"
B = 1999          # réplicas bootstrap/permutación (--rapido: 499)
SEED = 27


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def num(s):
    return pd.to_numeric(s, errors="coerce")


def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""


def cell(b, se, p, dec=3):
    return f"{b:.{dec}f}{stars(p)} & ({se:.{dec}f})"


def load_data():
    d = pd.read_pickle("data/processed/paper_adolescentes.pkl")
    d["cut"] = num(d.cut_comuna_seleccion).astype("Int64")
    pga = None
    fp = Path("data/processed/pga_comuna.csv")
    if fp.exists():
        pga = pd.read_csv(fp)
        d = d.merge(pga[["cut", "pga", "mmi", "dist_epi_km"]],
                    on="cut", how="left")
        for v in ("pga", "mmi"):
            d[f"{v}_z"] = (d[v] - d[v].mean()) / d[v].std()
        d["ldist"] = -np.log(d.dist_epi_km.clip(lower=1))
        d["ldist_z"] = (d.ldist - d.ldist.mean()) / d.ldist.std()
    a = pd.read_pickle("data/processed/paper_atricion.pkl")
    # outcomes derivados adicionales
    d["z_peso"] = zg(d.peso_nacer)
    d["z_talla"] = zg(d.talla_nacer)
    d["z_gest"] = zg(d.sem_gest)
    d["z_apgar"] = zg(d.apgar5)
    return d, a, pga


def zg(s):
    s = num(s)
    return (s - s.mean()) / s.std()


def xt(d, xs):
    terms = []
    for v in xs:
        if v not in d:
            continue
        if d[v].isna().any():
            d[f"{v}_mi"] = d[v].isna().astype(float)
            d[v] = d[v].fillna(d[v].median())
            terms += [v, f"{v}_mi"]
        else:
            terms.append(v)
    return terms


def fit(d0, y, col=3, dose="EQ", sample=None, weights=True, extra_x=None,
        keep_model=False):
    """Estimación central. dose: 'EQ' | 'pga_z' | 'mmi_z' | 'ldist_z'."""
    d = d0.copy()
    if sample is not None:
        d = d[sample(d)]
    d = d.dropna(subset=[y, dose, "estrato", "w", "cohorte", "bin"])
    d = d[d.w > 0].copy()
    if col == 4:
        d = d[d.region != 13]
    d["est"] = d.estrato.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    dd = num(d[dose]) if dose != "EQ" else d.EQ
    for lab, v in IV.items():
        d[v] = (d.bin == lab).astype(float) * dd
    rhs = " + ".join(list(IV.values()) + ["C(bin)", "C(est)", "C(coh)"])
    if col >= 2:
        rhs += " + " + " + ".join(xt(d, X_PRE))
    if col >= 3:
        rhs += " + " + " + ".join(xt(d, X_POST))
    if extra_x:
        rhs += " + " + " + ".join(xt(d, extra_x))
    w = d.w if weights else pd.Series(1.0, index=d.index)
    r = smf.wls(f"{y} ~ {rhs}", data=d, weights=w).fit(
        cov_type="cluster", cov_kwds={"groups": d.est})
    ct = r.t_test(CONTR)
    out = {"n": int(r.nobs), "ncl": d.est.nunique(),
           "b": {k: (r.params[v], r.bse[v], r.pvalues[v])
                 for k, v in IV.items()},
           "contr": (float(np.ravel(ct.effect)[0]),
                     float(np.ravel(ct.sd)[0]),
                     float(np.ravel(ct.pvalue)[0]))}
    if keep_model:
        out["_d"], out["_f"], out["_w"] = d, f"{y} ~ {rhs}", w
    return out


# ---------- maquinaria FWL para permutación / wild / Romano–Wolf ----------

def fwl_prep(res):
    """Descompone el diseño en (I columnas de interés) vs F (resto),
    absorbe pesos y calcula el aniquilador de F aplicado a y e I."""
    d, f, w = res["_d"], res["_f"], res["_w"]
    ymat, X = patsy.dmatrices(f, d, return_type="dataframe")
    sw = np.sqrt(w.to_numpy())
    icols = [c for c in X.columns if c in IV.values()]
    Fcols = [c for c in X.columns if c not in icols]
    Iw = X[icols].to_numpy() * sw[:, None]
    Fw = X[Fcols].to_numpy() * sw[:, None]
    yw = ymat.to_numpy().ravel() * sw
    FtFi = np.linalg.pinv(Fw.T @ Fw)

    def resid(V):
        return V - Fw @ (FtFi @ (Fw.T @ V))
    It = resid(Iw)
    yt = resid(yw)
    com = d.estrato.astype(int).to_numpy()
    return {"It": It, "yt": yt, "resid": resid, "sw": sw, "com": com,
            "d": d, "icols": icols}


def small_ols(It, yt, com):
    XtXi = np.linalg.pinv(It.T @ It)
    b = XtXi @ (It.T @ yt)
    e = yt - It @ b
    M = np.zeros((It.shape[1], It.shape[1]))
    for g in np.unique(com):
        m = com == g
        s = It[m].T @ e[m]
        M += np.outer(s, s)
    V = XtXi @ M @ XtXi
    return b, V, e


def cvec(icols):
    c24 = np.array([1.0 if c == "I_24" else 0.0 for c in icols])
    ccon = np.array([{"I_36": 1.0, "I_24": -1.0}.get(c, 0.0) for c in icols])
    return c24, ccon


def perm_test(res, nperm, seed=SEED):
    """Permuta la asignación EQ entre comunas (manteniendo el nº de comunas
    tratadas) y recalcula el t del coef 24-35 y del contraste."""
    P = fwl_prep(res)
    d = P["d"]
    c24, ccon = cvec(P["icols"])
    b, V, _ = small_ols(P["It"], P["yt"], P["com"])
    t_obs = {"24": c24 @ b / np.sqrt(c24 @ V @ c24),
             "ct": ccon @ b / np.sqrt(ccon @ V @ ccon)}
    coms = np.sort(d.estrato.astype(int).unique())
    eq_by_com = d.groupby(d.estrato.astype(int)).EQ.first()
    n_treat = int(eq_by_com.sum())
    rng = np.random.default_rng(seed)
    binm = np.stack([(d.bin == lab).to_numpy(float)
                     for lab in IV], axis=1)
    hits = {"24": 0, "ct": 0}
    for _ in range(nperm):
        treat = set(rng.choice(coms, size=n_treat, replace=False))
        eq_new = d.estrato.astype(int).isin(treat).to_numpy(float)
        Iw = binm * eq_new[:, None] * P["sw"][:, None]
        It = P["resid"](Iw)
        bb, VV, _ = small_ols(It, P["yt"], P["com"])
        if abs(c24 @ bb / np.sqrt(c24 @ VV @ c24)) >= abs(t_obs["24"]):
            hits["24"] += 1
        if abs(ccon @ bb / np.sqrt(ccon @ VV @ ccon)) >= abs(t_obs["ct"]):
            hits["ct"] += 1
    return {k: (hits[k] + 1) / (nperm + 1) for k in hits}


def rw_stepdown(results, nboot, seed=SEED):
    """Romano–Wolf stepdown para la familia de outcomes (coef 24-35 y
    contraste por outcome), con wild bootstrap Rademacher conjunto por
    comuna (mismos giros de signo para todos los outcomes)."""
    preps = {}
    for y, res in results.items():
        P = fwl_prep(res)
        c24, ccon = cvec(P["icols"])
        b, V, e = small_ols(P["It"], P["yt"], P["com"])
        fitted = P["It"] @ b
        preps[y] = dict(P=P, c24=c24, ccon=ccon, b=b, V=V, e=e,
                        fitted=fitted)
    stats = {}
    for y, pr in preps.items():
        stats[(y, "24")] = abs(pr["c24"] @ pr["b"]
                               / np.sqrt(pr["c24"] @ pr["V"] @ pr["c24"]))
        stats[(y, "ct")] = abs(pr["ccon"] @ pr["b"]
                               / np.sqrt(pr["ccon"] @ pr["V"] @ pr["ccon"]))
    allcom = np.sort(np.unique(np.concatenate(
        [pr["P"]["com"] for pr in preps.values()])))
    rng = np.random.default_rng(seed)
    tb = {k: [] for k in stats}
    for _ in range(nboot):
        flip = dict(zip(allcom, rng.choice([-1.0, 1.0], size=len(allcom))))
        for y, pr in preps.items():
            fv = np.vectorize(flip.get)(pr["P"]["com"])
            yb = pr["fitted"] + pr["e"] * fv
            bb, VV, _ = small_ols(pr["P"]["It"], yb, pr["P"]["com"])
            tb[(y, "24")].append(abs((pr["c24"] @ (bb - pr["b"]))
                                 / np.sqrt(pr["c24"] @ VV @ pr["c24"])))
            tb[(y, "ct")].append(abs((pr["ccon"] @ (bb - pr["b"]))
                                 / np.sqrt(pr["ccon"] @ VV @ pr["ccon"])))
    tb = {k: np.array(v) for k, v in tb.items()}
    rwp = {}
    for fam in ("24", "ct"):
        keys = sorted([k for k in stats if k[1] == fam],
                      key=lambda k: -stats[k])
        prev = 0.0
        rest = list(keys)
        for k in keys:
            maxb = np.max(np.stack([tb[j] for j in rest]), axis=0)
            p = (1 + (maxb >= stats[k]).sum()) / (nboot + 1)
            p = max(p, prev)
            rwp[k] = p
            prev = p
            rest.remove(k)
    return stats, rwp


def wild_region(res, nboot, seed=SEED):
    """Wild bootstrap-t por región (Webb) para 24-35 y contraste."""
    P = fwl_prep(res)
    reg = (P["d"].cut // 1000).astype(int).to_numpy() \
        if "cut" in P["d"] else P["d"].region.astype(int).to_numpy()
    c24, ccon = cvec(P["icols"])

    def cr(It, yt, e, groups):
        XtXi = np.linalg.pinv(It.T @ It)
        M = np.zeros((It.shape[1], It.shape[1]))
        for g in np.unique(groups):
            m = groups == g
            s = It[m].T @ e[m]
            M += np.outer(s, s)
        return XtXi @ M @ XtXi
    b, _, e = small_ols(P["It"], P["yt"], P["com"])
    V = cr(P["It"], P["yt"], e, reg)
    tobs = {"24": c24 @ b / np.sqrt(c24 @ V @ c24),
            "ct": ccon @ b / np.sqrt(ccon @ V @ ccon)}
    fitted = P["It"] @ b
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5),
                     np.sqrt(0.5), 1, np.sqrt(1.5)])
    rng = np.random.default_rng(seed)
    regs = np.unique(reg)
    hits = {"24": 0, "ct": 0}
    for _ in range(nboot):
        flip = dict(zip(regs, rng.choice(webb, size=len(regs))))
        fv = np.vectorize(flip.get)(reg)
        yb = fitted + e * fv
        bb, _, eb = small_ols(P["It"], yb, P["com"])
        VV = cr(P["It"], yb, eb, reg)
        if abs((c24 @ (bb - b)) / np.sqrt(c24 @ VV @ c24)) >= abs(tobs["24"]):
            hits["24"] += 1
        if abs((ccon @ (bb - b)) / np.sqrt(ccon @ VV @ ccon)) >= abs(tobs["ct"]):
            hits["ct"] += 1
    return {k: (hits[k] + 1) / (nboot + 1) for k in hits}, len(regs)


# --------------------------- tablas ---------------------------------------

def write_tex(name, lines):
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / f"{name}.tex").write_text("\n".join(lines) + "\n",
                                     encoding="utf-8")
    log(f"-> paper/tables/{name}.tex")


def panel_rows(res_by_col, dec=3):
    rows = []
    for lab in IV:
        cells = " & ".join(cell(*r["b"][lab], dec) for r in res_by_col)
        rows.append(f"{LAB[lab]} & {cells} \\\\")
    rows.append("\\addlinespace")
    cells = " & ".join(cell(*r["contr"], dec) for r in res_by_col)
    rows.append("Contraste: 3--4 a\\~nos $-$ 2 a\\~nos & " + cells + " \\\\")
    rows.append("\\midrule")
    rows.append("Adolescentes & " + " & ".join(
        f"\\multicolumn{{2}}{{c}}{{{r['n']:,}}}" for r in res_by_col) + " \\\\")
    rows.append("Comunas (cl\\'uster) & " + " & ".join(
        f"\\multicolumn{{2}}{{c}}{{{r['ncl']}}}" for r in res_by_col) + " \\\\")
    return rows


def head4():
    return ["\\begin{tabular}{l rl rl rl rl}", "\\toprule",
            " & \\multicolumn{2}{c}{(1)} & \\multicolumn{2}{c}{(2)} & "
            "\\multicolumn{2}{c}{(3)} & \\multicolumn{2}{c}{(4)} \\\\",
            " & \\multicolumn{2}{c}{EF} & \\multicolumn{2}{c}{$+X$ pre-27F} &"
            " \\multicolumn{2}{c}{$+$controles 2012} & "
            "\\multicolumn{2}{c}{sin RM} \\\\", "\\midrule"]


def t1_descriptivos(d, a):
    rows = ["\\begin{tabular}{l cccc c}", "\\toprule",
            " & \\multicolumn{4}{c}{Edad el 27-F} & \\\\",
            "\\cmidrule(lr){2-5}",
            " & $<$1 a\\~no & 1 a\\~no & 2 a\\~nos & 3--4 a\\~nos & Total \\\\",
            "\\midrule"]
    g = d.groupby("bin", observed=True)

    def fila(nombre, s, fmt="{:.2f}", pct=False):
        v = [s[b] if b in s else np.nan for b in BINS] + [s["all"]]
        f = " & ".join(("--" if pd.isna(x) else
                        (f"{100*x:.1f}" if pct else fmt.format(x)))
                       for x in v)
        rows.append(f"{nombre} & {f} \\\\")

    def stat(col, fun="mean"):
        s = getattr(g[col], fun)()
        s = {k: v for k, v in s.items()}
        s["all"] = getattr(d[col], fun)()
        return s
    fila("Adolescentes (n)", {**g.size().to_dict(), "all": len(d)},
         fmt="{:,.0f}")
    fila("En zona afectada (\\%)", stat("EQ"), pct=True)
    fila("Mujer (\\%)", stat("mujer"), pct=True)
    fila("Edad en 2024 (a\\~nos)",
         {**(g.edad_meses.mean() / 12).to_dict(),
          "all": d.edad_meses.mean() / 12}, fmt="{:.1f}")
    fila("Educ.\\ de la madre 2010 (a\\~nos)", stat("educ_madre10"))
    fila("PHQ-4 (0--12)", stat("phq4_score"))
    fila("Depresi\\'on positiva, PHQ-2 (\\%)", stat("phq2_bin"), pct=True)
    fila("Ansiedad positiva, GAD-2 (\\%)", stat("gad2_bin"), pct=True)
    fila("CBCL internalizante 2024 (T)",
         {**g.cbcl2_pt_inter_t.mean().to_dict(),
          "all": num(d.cbcl2_pt_inter_t).mean()}, fmt="{:.1f}")
    ret = a.groupby("bin", observed=True).in2024.mean().to_dict()
    ret["all"] = a.in2024.mean()
    fila("Reentrevistado en 2024 (\\% de 2010)", ret, pct=True)
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t1_descriptivos", rows)


def t3_main(d):
    for y, name in [("z_phq4", "t3a_phq4"), ("gad2_bin", "t3b_gad2"),
                    ("phq2_bin", "t3c_phq2")]:
        res = [fit(d, y, c) for c in (1, 2, 3, 4)]
        rows = head4() + panel_rows(res) + ["\\bottomrule", "\\end{tabular}"]
        write_tex(name, rows)
        log(f"T3 {y} col3:",
            {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in res[2]["b"].items()},
            "contr", f"{res[2]['contr'][0]:+.3f}{stars(res[2]['contr'][2])}")
    return


def t4_informante(d):
    for y, name in [("z_cbcl", "t4a_cbcl24"), ("d_cbcl", "t4b_dcbcl")]:
        res = [fit(d, y, c) for c in (1, 2, 3, 4)]
        rows = head4() + panel_rows(res) + ["\\bottomrule", "\\end{tabular}"]
        write_tex(name, rows)


def t5_dosis(d):
    if "pga_z" not in d or d.pga_z.isna().all():
        log("T5: sin PGA, omitida")
        return None
    doses = [("EQ", "Regi\\'on afectada (0/1)"),
             ("pga_z", "PGA (z)"), ("mmi_z", "Intensidad MMI (z)"),
             ("ldist_z", "$-\\log$ dist.\\ epicentro (z)")]
    for y, name in [("z_phq4", "t5a_dosis_phq4"), ("gad2_bin", "t5b_dosis_gad2")]:
        res = [fit(d, y, 3, dose=dv) for dv, _ in doses]
        rows = ["\\begin{tabular}{l rl rl rl rl}", "\\toprule",
                " & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{({i+1})}}"
                                   for i in range(4)) + " \\\\",
                " & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{lab}}}"
                                   for _, lab in doses) + " \\\\",
                "\\midrule"] + panel_rows(res) + \
               ["\\bottomrule", "\\end{tabular}"]
        write_tex(name, rows)
        log(f"T5 {y}: PGA 24-35 {res[1]['b']['24-35m'][0]:+.3f}"
            f"{stars(res[1]['b']['24-35m'][2])}, contr "
            f"{res[1]['contr'][0]:+.3f}{stars(res[1]['contr'][2])}")
    return True


def t6_placebo(d):
    outs = [("z_peso", "Peso al nacer (z)"),
            ("z_talla", "Talla al nacer (z)"),
            ("z_gest", "Semanas de gestaci\\'on (z)"),
            ("prematuro", "Parto prematuro (0/1)"),
            ("z_apgar", "Apgar 5 min.\\ (z)")]
    rows = ["\\begin{tabular}{l rl rl rl c}", "\\toprule",
            " & \\multicolumn{2}{c}{1 a\\~no$\\times$EQ} & "
            "\\multicolumn{2}{c}{2 a\\~nos$\\times$EQ} & "
            "\\multicolumn{2}{c}{3--4 a\\~nos$\\times$EQ} & n \\\\",
            "\\midrule"]
    for y, lab in outs:
        r = fit(d, y, 2)
        cells = " & ".join(cell(*r["b"][b]) for b in IV)
        rows.append(f"{lab} & {cells} & {r['n']:,} \\\\")
        log("T6 placebo", y,
            {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in r["b"].items()})
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t6_placebo", rows)


def t7_robustez(d, ipw, nrep):
    base = fit(d, "z_phq4", 3, keep_model=True)
    variantes = [
        ("Especificaci\\'on preferida (col.\\ 3)", base),
        ("Sin controles (solo EF)", fit(d, "z_phq4", 1)),
        ("Sin Regi\\'on Metropolitana", fit(d, "z_phq4", 4)),
        ("Sin pesos muestrales", fit(d, "z_phq4", 3, weights=False)),
        ("PHQ-4 en puntos (0--12), sin estandarizar",
         fit(d, "phq4_score", 3)),
        ("Muestra con CBCL 2017 (balanceada)",
         fit(d, "z_phq4", 3, sample=lambda x: x.z_cbcl17.notna())),
        ("Controlando dotaci\\'on al nacer (peso, gestaci\\'on, prematuro)",
         fit(d, "z_phq4", 3, extra_x=["z_peso", "z_gest", "prematuro"])),
    ]
    if ipw is not None:
        d2 = d.merge(ipw, on="folio", how="left")
        d2["w"] = d2.w * d2.ipw.fillna(1.0)
        variantes.append(("Reponderada por atrici\\'on (IPW)",
                          fit(d2, "z_phq4", 3)))
    if "pga_z" in d and not d.pga_z.isna().all():
        variantes.append(("Dosis continua: PGA (z) en vez de EQ",
                          fit(d, "z_phq4", 3, dose="pga_z")))
    # leave-one-region-out (solo regiones EQ)
    lor = []
    for rg in (5, 6, 7, 8, 9, 13):
        r = fit(d, "z_phq4", 3, sample=lambda x, rg=rg: x.region != rg)
        lor.append((r["b"]["24-35m"][0], r["contr"][0]))
    rows = ["\\begin{tabular}{l rl rl c}", "\\toprule",
            " & \\multicolumn{2}{c}{2 a\\~nos$\\times$EQ} & "
            "\\multicolumn{2}{c}{Contraste 3--4$-$2} & n \\\\",
            "\\midrule"]
    for lab, r in variantes:
        rows.append(f"{lab} & {cell(*r['b']['24-35m'])} & "
                    f"{cell(*r['contr'])} & {r['n']:,} \\\\")
        log("T7", lab, f"{r['b']['24-35m'][0]:+.3f}{stars(r['b']['24-35m'][2])}",
            f"contr {r['contr'][0]:+.3f}{stars(r['contr'][2])}")
    rows.append("\\addlinespace")
    rows.append("Excluyendo una regi\\'on afectada a la vez (rango) & "
                f"\\multicolumn{{2}}{{c}}{{[{min(x[0] for x in lor):.3f}, "
                f"{max(x[0] for x in lor):.3f}]}} & "
                f"\\multicolumn{{2}}{{c}}{{[{min(x[1] for x in lor):.3f}, "
                f"{max(x[1] for x in lor):.3f}]}} & \\\\")
    # inferencia
    pp = perm_test(base, nrep)
    pw, nreg = wild_region(base, nrep)
    rows.append("\\midrule")
    rows.append("$p$ de permutaci\\'on comunal & "
                f"\\multicolumn{{2}}{{c}}{{{pp['24']:.3f}}} & "
                f"\\multicolumn{{2}}{{c}}{{{pp['ct']:.3f}}} & \\\\")
    rows.append(f"$p$ wild bootstrap por regi\\'on ({nreg} reg.) & "
                f"\\multicolumn{{2}}{{c}}{{{pw['24']:.3f}}} & "
                f"\\multicolumn{{2}}{{c}}{{{pw['ct']:.3f}}} & \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t7_robustez", rows)
    log("T7 inferencia: perm", pp, "| wild region", pw)


def t8_rw(d, nrep):
    fam = {"z_phq4": "PHQ-4 (z)", "phq2_bin": "PHQ-2 positivo",
           "gad2_bin": "GAD-2 positivo", "z_cbcl": "CBCL 2024 (z)"}
    results = {y: fit(d, y, 3, keep_model=True) for y in fam}
    stats, rwp = rw_stepdown(results, nrep)
    rows = ["\\begin{tabular}{l cc cc}", "\\toprule",
            " & \\multicolumn{2}{c}{2 a\\~nos$\\times$EQ} & "
            "\\multicolumn{2}{c}{Contraste 3--4$-$2} \\\\",
            " & $p$ anal\\'itico & $p$ RW & $p$ anal\\'itico & $p$ RW \\\\",
            "\\midrule"]
    for y, lab in fam.items():
        r = results[y]
        rows.append(f"{lab} & {r['b']['24-35m'][2]:.3f} & "
                    f"{rwp[(y, '24')]:.3f} & {r['contr'][2]:.3f} & "
                    f"{rwp[(y, 'ct')]:.3f} \\\\")
        log("T8 RW", y, "24:", f"{rwp[(y, '24')]:.3f}",
            "ct:", f"{rwp[(y, 'ct')]:.3f}")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t8_romanowolf", rows)


def t9_atricion(a):
    d = a.dropna(subset=["bin", "EQ", "region"]).copy()
    d["reg"] = d.region.astype(int).astype(str)
    for lab, v in IV.items():
        d[v] = (d.bin == lab).astype(float) * d.EQ
    d["educ_m"] = num(d.b2n).where(lambda s: s < 30)
    d["edad_m"] = num(d.a19).where(lambda s: s < 99)
    tx = xt(d, ["educ_m", "edad_m"])
    f = ("in2024 ~ " + " + ".join(list(IV.values()))
         + " + C(bin) + C(reg) + " + " + ".join(tx))
    r = smf.ols(f, data=d).fit(cov_type="HC1")
    rows = ["\\begin{tabular}{l rl}", "\\toprule",
            " & \\multicolumn{2}{c}{Pr(reentrevistado 2024)} \\\\",
            "\\midrule"]
    for lab, v in IV.items():
        rows.append(f"{LAB[lab]} $\\times$ EQ & "
                    f"{cell(r.params[v], r.bse[v], r.pvalues[v])} \\\\")
        log("T9 atricion", v, f"{r.params[v]:+.3f}{stars(r.pvalues[v])}")
    ct = r.t_test(CONTR)
    rows.append("Contraste 3--4 $-$ 2 & " + cell(
        float(np.ravel(ct.effect)[0]), float(np.ravel(ct.sd)[0]),
        float(np.ravel(ct.pvalue)[0])) + " \\\\")
    rows.append("\\midrule")
    rows.append(f"Ni\\~nos de la l\\'inea base 2010 & "
                f"\\multicolumn{{2}}{{c}}{{{int(r.nobs):,}}} \\\\")
    rows.append(f"Retenci\\'on media 2010$\\to$2024 & "
                f"\\multicolumn{{2}}{{c}}{{{d.in2024.mean():.1%}}} \\\\"
                .replace("%", "\\%"))
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t9_atricion", rows)
    # pesos IPW para robustez
    phat = r.predict(d).clip(0.05, 0.98)
    ipw = pd.DataFrame({"folio": d.folio, "ipw": 1.0 / phat})
    return ipw


def t10_mecanismos(d):
    outs = [("z_resil", "Resiliencia BRS (z; $+$ = m\\'as resiliente)"),
            ("z_satisf", "Satisfacci\\'on con la vida (z)"),
            ("z_salud", "Salud f\\'isica autorreportada (z; $+$ = peor)"),
            ("z_bull", "Bullying escolar (z)"),
            ("ciber_any", "Cibervictimizaci\\'on (0/1)"),
            ("viol_pareja", "Violencia en la pareja (0/1)"),
            ("fuma", "Fum\\'o tabaco, 12 m.\\ (0/1)"),
            ("alcohol", "Bebi\\'o alcohol, 12 m.\\ (0/1)"),
            ("cannabis", "Consumi\\'o cannabis, 12 m.\\ (0/1)")]
    rows = ["\\begin{tabular}{l rl rl rl c}", "\\toprule",
            " & \\multicolumn{2}{c}{1 a\\~no$\\times$EQ} & "
            "\\multicolumn{2}{c}{2 a\\~nos$\\times$EQ} & "
            "\\multicolumn{2}{c}{3--4 a\\~nos$\\times$EQ} & n \\\\",
            "\\midrule"]
    for y, lab in outs:
        if y not in d or d[y].isna().all():
            continue
        r = fit(d, y, 3)
        cells = " & ".join(cell(*r["b"][b]) for b in IV)
        rows.append(f"{lab} & {cells} & {r['n']:,} \\\\")
        log("T10", y,
            {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in r["b"].items()})
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t10_mecanismos", rows)


def t11_madre(d):
    d = d.copy()
    d["vuln"] = ((d.mh_emb_dx == 1) | (d.dep_postparto == 1)
                 | (d.deriv_psic == 1)).astype(float)
    res = {}
    for y in ("z_phq4", "gad2_bin"):
        res[(y, 1)] = fit(d, y, 3, sample=lambda x: x.vuln == 1)
        res[(y, 0)] = fit(d, y, 3, sample=lambda x: x.vuln == 0)
    rows = ["\\begin{tabular}{l rl rl rl rl}", "\\toprule",
            " & \\multicolumn{4}{c}{PHQ-4 (z)} & "
            "\\multicolumn{4}{c}{GAD-2 positivo} \\\\",
            "\\cmidrule(lr){2-5} \\cmidrule(lr){6-9}",
            " & \\multicolumn{2}{c}{Madre vulnerable} & "
            "\\multicolumn{2}{c}{Madre no vulnerable} & "
            "\\multicolumn{2}{c}{Madre vulnerable} & "
            "\\multicolumn{2}{c}{Madre no vulnerable} \\\\",
            "\\midrule"]
    for lab in IV:
        cells = " & ".join(cell(*res[(y, v)]["b"][lab])
                           for y in ("z_phq4", "gad2_bin") for v in (1, 0))
        rows.append(f"{LAB[lab]} & {cells} \\\\")
    rows.append("\\addlinespace")
    cells = " & ".join(cell(*res[(y, v)]["contr"])
                       for y in ("z_phq4", "gad2_bin") for v in (1, 0))
    rows.append("Contraste 3--4 $-$ 2 & " + cells + " \\\\")
    rows.append("\\midrule")
    rows.append("Adolescentes & " + " & ".join(
        f"\\multicolumn{{2}}{{c}}{{{res[(y, v)]['n']:,}}}"
        for y in ("z_phq4", "gad2_bin") for v in (1, 0)) + " \\\\")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t11_madre", rows)
    for y in ("z_phq4", "gad2_bin"):
        log("T11", y, "vuln contr:",
            f"{res[(y, 1)]['contr'][0]:+.3f}{stars(res[(y, 1)]['contr'][2])}",
            "| no-vuln contr:",
            f"{res[(y, 0)]['contr'][0]:+.3f}{stars(res[(y, 0)]['contr'][2])}")


def t12_heterogeneidad(d):
    grupos = [("Mujeres", lambda x: x.mujer == 1),
              ("Hombres", lambda x: x.mujer == 0),
              ("Madre con educ.\\ media o menos (2010)",
               lambda x: num(x.educ_madre10) <= 12),
              ("Madre con educ.\\ superior (2010)",
               lambda x: num(x.educ_madre10) > 12),
              ("Hogar urbano 2010", lambda x: x.rural10 == 0),
              ("Hogar rural 2010", lambda x: x.rural10 == 1)]
    rows = ["\\begin{tabular}{l rl rl c}", "\\toprule",
            " & \\multicolumn{2}{c}{2 a\\~nos$\\times$EQ} & "
            "\\multicolumn{2}{c}{Contraste 3--4$-$2} & n \\\\",
            "\\midrule"]
    for lab, sel in grupos:
        r = fit(d, "z_phq4", 3, sample=sel)
        rows.append(f"{lab} & {cell(*r['b']['24-35m'])} & "
                    f"{cell(*r['contr'])} & {r['n']:,} \\\\")
        log("T12", lab, f"{r['b']['24-35m'][0]:+.3f}{stars(r['b']['24-35m'][2])}",
            f"contr {r['contr'][0]:+.3f}{stars(r['contr'][2])}")
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t12_heterogeneidad", rows)


def t2_lp():
    spec = importlib.util.spec_from_file_location(
        "lp", HERE / "10_ec1_largo_plazo.py")
    lp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lp)
    df = lp.build()
    rows = head4()
    for y, lab in [("z_tvip", "Vocabulario (Peabody, z)"),
                   ("z_cbcl", "Problemas internalizantes (CBCL, z)")]:
        res = [lp.fit(df, y, c) for c in (1, 2, 3, 4)]
        cells = " & ".join(cell(r["b"], r["se"], r["p"]) for r in res)
        rows.append(f"{lab} & {cells} \\\\")
        rows.append("\\quad Adolescentes & " + " & ".join(
            f"\\multicolumn{{2}}{{c}}{{{r['n']:,}}}" for r in res) + " \\\\")
        rows.append("\\addlinespace")
        log("T2 LP", y, [f"{r['b']:+.3f}{stars(r['p'])}" for r in res])
    rows += ["\\bottomrule", "\\end{tabular}"]
    write_tex("t2_largo_plazo", rows)


def figuras(d):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    INK, BLUE, GRID = "#0B0B0B", "#2A78D6", "#D9D9D9"
    x = np.arange(4)
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    for y, colr, lab, off in [("z_phq4", INK, "PHQ-4 (z), autorreporte", -0.07),
                              ("gad2_bin", BLUE,
                               "GAD-2 positivo (pp/100)", 0.07)]:
        r = fit(d, y, 3)
        bs = [0.0] + [r["b"][b][0] for b in IV]
        ses = [0.0] + [r["b"][b][1] for b in IV]
        ax.errorbar(x + off, bs, yerr=[1.96 * s for s in ses], fmt="o",
                    color=colr, ecolor=colr, elinewidth=1.4, capsize=0,
                    markersize=5, label=lab)
    ax.axhline(0, color=GRID, lw=1, zorder=0)
    ax.set_xticks(x, ["$<$1 año\n(ref.)", "1 año", "2 años", "3–4 años"])
    ax.set_xlabel("Edad cuando golpeó el terremoto del 27-F")
    ax.set_ylabel("Efecto vs. expuestos de bebé")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(color=GRID)
    fig.tight_layout()
    fig.savefig(FIG / "f1_gradiente_u.pdf")
    plt.close(fig)
    log("-> paper/figures/f1_gradiente_u.pdf")
    if "pga_z" in d and not d.pga_z.isna().all():
        fig, ax = plt.subplots(figsize=(6.3, 3.6))
        r = fit(d, "z_phq4", 3, dose="pga_z")
        bs = [0.0] + [r["b"][b][0] for b in IV]
        ses = [0.0] + [r["b"][b][1] for b in IV]
        ax.errorbar(x, bs, yerr=[1.96 * s for s in ses], fmt="o", color=INK,
                    elinewidth=1.4, markersize=5)
        ax.axhline(0, color=GRID, lw=1, zorder=0)
        ax.set_xticks(x, ["$<$1 año\n(ref.)", "1 año", "2 años", "3–4 años"])
        ax.set_xlabel("Edad cuando golpeó el 27-F")
        ax.set_ylabel("Efecto de +1 DE de PGA sobre PHQ-4 (z)")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(GRID)
        ax.spines["bottom"].set_color(GRID)
        fig.tight_layout()
        fig.savefig(FIG / "f2_dosis_pga.pdf")
        plt.close(fig)
        log("-> paper/figures/f2_dosis_pga.pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", default="")
    ap.add_argument("--rapido", action="store_true")
    args = ap.parse_args()
    nrep = 499 if args.rapido else B
    solo = set(x.strip() for x in args.solo.split(",") if x.strip())

    def go(name):
        return not solo or name in solo
    d, a, pga = load_data()
    log(f"datos: {len(d):,} adolescentes | PGA: "
        f"{'ok' if pga is not None else 'NO'}")
    ipw = None
    if go("t9"):
        ipw = t9_atricion(a)
    if go("t1"):
        t1_descriptivos(d, a)
    if go("t3"):
        t3_main(d)
    if go("t4"):
        t4_informante(d)
    if go("t5"):
        t5_dosis(d)
    if go("t6"):
        t6_placebo(d)
    if go("t7"):
        t7_robustez(d, ipw, nrep)
    if go("t8"):
        t8_rw(d, nrep)
    if go("t10"):
        t10_mecanismos(d)
    if go("t11"):
        t11_madre(d)
    if go("t12"):
        t12_heterogeneidad(d)
    if go("fig"):
        figuras(d)
    if go("t2"):
        t2_lp()
    Path("reports").mkdir(exist_ok=True)
    (Path("reports") / "paper_numeros.md").write_text(
        "# Log de estimaciones del paper\n\n```\n" + "\n".join(LOG)
        + "\n```\n", encoding="utf-8")
    log("-> reports/paper_numeros.md")


if __name__ == "__main__":
    main()
