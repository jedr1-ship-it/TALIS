#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fases 1–3 — todas las estimaciones del paper y sus tablas .tex.

Formato de salida: el estándar del WP de la Jornada (AER-style). Cada
fragmento en paper/tables/*.tex es un entorno {table} COMPLETO: caption
en versalitas via el preámbulo, coeficiente y (EE) en dos líneas, stars
con \\sym{}, paneles con \\panel{}, bloque de efectos fijos y
observaciones al pie, y notas en {wpnotes} que terminan en \\starnote.
Los macros (\\panel, \\sym, wpnotes, \\starnote, \\bindef, \\zonedef,
\\specdef, \\phqdef, \\cbcldef, \\clusternote) los define paper/tablas.tex.

Entradas: data/processed/paper_adolescentes.pkl, paper_atricion.pkl,
          pga_comuna.csv.
Salidas:  paper/tables/t*.tex, paper/figures/*.pdf,
          reports/paper_numeros.md (log).

Uso: python3 scripts/15_paper_estimaciones.py [--solo t3,t7] [--rapido]
"""
import argparse
import importlib.util
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
ROWLAB = {"12-23m": "Exposed at age 1",
          "24-35m": "Exposed at age 2",
          "36-59m": "Exposed at ages 3--4"}
CONTRLAB = "Contrast: ages 3--4 $-$ age 2"
X_PRE = ["mujer", "edad_meses", "edad_madre10", "educ_madre10",
         "tot_per10", "rural10"]
X_POST = ["n_hijos", "mh_madre", "mh_padre", "mh_ofam", "mh_miss"]
CONTR = "I_36 - I_24"
B = 1999
SEED = 27


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def num(s):
    return pd.to_numeric(s, errors="coerce")


def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""


# ------------------------- formato AER ------------------------------------

def fnum(x, dec=3):
    s = f"{x:.{dec}f}"
    return s.replace("-", "$-$", 1) if s.startswith("-") else s


def bcell(b, p, dec=3):
    st = stars(p)
    return fnum(b, dec) + (f"\\sym{{{st}}}" if st else "")


def secell(se, dec=3):
    return f"({se:.{dec}f})"


def coef2(label, triples, dec=3):
    """Fila doble: coeficientes con stars y, debajo, los EE."""
    top = " & ".join(bcell(b, p, dec) if b is not None else ""
                     for b, se, p in triples)
    bot = " & ".join(secell(se, dec) if se is not None else ""
                     for b, se, p in triples)
    return [f"{label} & {top} \\\\", f" & {bot} \\\\"]


def numcols(n, w):
    return f"*{{{n}}}{{>{{\\centering\\arraybackslash}}p{{{w}pt}}}}"


def table_env(fname, caption, label, colspec, header, body, notes,
              sideways=False, extra_pre=""):
    env = "sidewaystable" if sideways else "table"
    pos = "[p]" if sideways else "[htbp]"
    fh = "\\flushhead\n" if sideways else ""
    lines = [f"% ---- begin paper/tables/{fname}.tex",
             f"\\begin{{{env}}}{pos}\\centering",
             fh + f"\\caption{{{caption}}}",
             f"\\label{{{label}}}"]
    if extra_pre:
        lines.append(extra_pre)
    lines += ["\\begin{threeparttable}",
              f"\\begin{{tabular}}{{{colspec}}}",
              "\\toprule"] + header + ["\\midrule"] + body + [
              "\\bottomrule", "\\end{tabular}",
              "\\begin{wpnotes}",
              "\\textit{Notes:} " + notes,
              "\\end{wpnotes}",
              "\\end{threeparttable}",
              f"\\end{{{env}}}",
              f"% ---- end paper/tables/{fname}.tex"]
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / f"{fname}.tex").write_text("\n".join(lines) + "\n",
                                      encoding="utf-8")
    log(f"-> paper/tables/{fname}.tex")


# ------------------------- datos y estimación ------------------------------

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
    binm = np.stack([(d.bin == lab).to_numpy(float) for lab in IV], axis=1)
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
    preps = {}
    for y, res in results.items():
        P = fwl_prep(res)
        c24, ccon = cvec(P["icols"])
        b, V, e = small_ols(P["It"], P["yt"], P["com"])
        preps[y] = dict(P=P, c24=c24, ccon=ccon, b=b, V=V, e=e,
                        fitted=P["It"] @ b)
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
        prev, rest = 0.0, None
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
    P = fwl_prep(res)
    reg = (P["d"].cut // 1000).astype(int).to_numpy() \
        if "cut" in P["d"] else P["d"].region.astype(int).to_numpy()
    c24, ccon = cvec(P["icols"])

    def cr(It, e, groups):
        XtXi = np.linalg.pinv(It.T @ It)
        M = np.zeros((It.shape[1], It.shape[1]))
        for g in np.unique(groups):
            m = groups == g
            s = It[m].T @ e[m]
            M += np.outer(s, s)
        return XtXi @ M @ XtXi
    b, _, e = small_ols(P["It"], P["yt"], P["com"])
    V = cr(P["It"], e, reg)
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
        VV = cr(P["It"], eb, reg)
        if abs((c24 @ (bb - b)) / np.sqrt(c24 @ VV @ c24)) >= abs(tobs["24"]):
            hits["24"] += 1
        if abs((ccon @ (bb - b)) / np.sqrt(ccon @ VV @ ccon)) \
                >= abs(tobs["ct"]):
            hits["ct"] += 1
    return {k: (hits[k] + 1) / (nboot + 1) for k in hits}, len(regs)


# --------------------------- tablas ---------------------------------------

COLHEAD4 = [" & (1) & (2) & (3) & (4) \\\\"]


def ticks4():
    return ["Municipality fixed effects & Yes & Yes & Yes & Yes \\\\",
            "Birth-cohort fixed effects & Yes & Yes & Yes & Yes \\\\",
            "Pre-earthquake controls & No & Yes & Yes & Yes \\\\",
            "2012 controls & No & No & Yes & Yes \\\\",
            "Excludes the Metropolitan Region & No & No & No & Yes \\\\"]


def ticks_col3(n):
    yes = " & ".join("Yes" for _ in range(n))
    return [f"Municipality fixed effects & {yes} \\\\",
            f"Birth-cohort fixed effects & {yes} \\\\",
            f"Pre-earthquake controls & {yes} \\\\",
            f"2012 controls & {yes} \\\\"]


def bins_block(res_by_col, ncols, dec=3, contrast=False):
    rows = []
    for lab in IV:
        rows += coef2(ROWLAB[lab], [r["b"][lab] for r in res_by_col], dec)
        rows.append("\\addlinespace[3pt]")
    if contrast:
        rows += coef2(CONTRLAB, [r["contr"] for r in res_by_col], dec)
    else:
        rows = rows[:-1]
    return rows


def foot_block(res_by_col, unit="Observations"):
    return [f"{unit} & " + " & ".join(f"{r['n']:,}" for r in res_by_col)
            + " \\\\",
            "Selection municipalities (clusters) & "
            + " & ".join(str(r["ncl"]) for r in res_by_col) + " \\\\"]


def t1_descriptivos(d, a):
    g = d.groupby("bin", observed=True)

    def srow(name, s, dec=2, pct=False):
        v = [s.get(b, np.nan) for b in BINS] + [s["all"]]
        cells = " & ".join(
            "--" if pd.isna(x) else
            (f"{100 * x:.1f}" if pct else
             (f"{x:,.0f}" if dec == 0 else f"{x:.{dec}f}")) for x in v)
        return f"{name} & {cells} \\\\"

    def stat(col):
        s = dict(g[col].mean())
        s["all"] = d[col].mean()
        return s
    body = [
        "\\panel{6}{Panel A. Sample}",
        srow("\\hspace{1em}Adolescents",
             {**dict(g.size()), "all": len(d)}, dec=0),
        srow("\\hspace{1em}In the affected zone (\\%)", stat("EQ"),
             pct=True),
        srow("\\hspace{1em}Female (\\%)", stat("mujer"), pct=True),
        srow("\\hspace{1em}Age in 2024 (years)",
             {**dict(g.edad_meses.mean() / 12),
              "all": d.edad_meses.mean() / 12}, dec=1),
        srow("\\hspace{1em}Mother's years of education in 2010",
             stat("educ_madre10")),
        "\\addlinespace",
        "\\panel{6}{Panel B. Mental health at ages 14--18}",
        srow("\\hspace{1em}PHQ-4 score: sum of four items (0--12)", stat("phq4_score")),
        srow("\\hspace{1em}Positive depression screen, PHQ-2 (\\%)",
             stat("phq2_bin"), pct=True),
        srow("\\hspace{1em}Positive anxiety screen, GAD-2 (\\%)",
             stat("gad2_bin"), pct=True),
        srow("\\hspace{1em}CBCL internalizing, caregiver (T)",
             {**dict(g.cbcl2_pt_inter_t.apply(lambda s: num(s).mean())),
              "all": num(d.cbcl2_pt_inter_t).mean()}, dec=1),
        "\\addlinespace",
        "\\panel{6}{Panel C. Retention}"]
    ret = dict(a.groupby("bin", observed=True).in2024.mean())
    ret["all"] = a.in2024.mean()
    body.append(srow("\\hspace{1em}Reinterviewed in 2024 (\\% of 2010)",
                     ret, pct=True))
    header = [" & \\multicolumn{4}{c}{Age when the earthquake struck} & \\\\",
              "\\cmidrule(lr){2-5}",
              " & $<$1 & 1 & 2 & 3--4 & All (0--4) \\\\",
              " & (1) & (2) & (3) & (4) & (5) \\\\"]
    notes = ("Means over the 10,003 adolescents of the 2024 ELPI wave, all "
             "born 2006--2009 and therefore exposed to the 27 February 2010 "
             "earthquake between 6 and 50 months of age, by age on the day "
             "of the earthquake. Column 5 is the sum of columns 1 to 4: the "
             "10,003 adolescents of the wave, all of whom were between 6 "
             "and 50 months old --- ages 0 to 4 --- on the day of the "
             "earthquake; nobody else exists in the 2024 wave. The survey's "
             "two-stage design samples 116 of Chile's 346 municipalities "
             "and keeps them fixed across waves. \\phqdef{} \\zonedef{} Panel C uses the "
             "14,855 children of the 2010 baseline with a valid birth date "
             "and shows that retention into 2024 is flat across "
             "exposure-age groups (Table~\\ref{tab:attrition}).")
    table_env("t1_descriptivos",
              "The Analysis Sample by Age at Exposure to the Earthquake",
              "tab:sample",
              "@{}p{208pt}" + numcols(5, 46) + "@{}",
              header, body, notes)


def t2rep():
    spec = importlib.util.spec_from_file_location(
        "rep", HERE / "08_replicacion_gillmore.py")
    rep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rep)
    R = rep.load_raw()
    st, mt = rep.assemble(R, rep.BEST)
    body = []
    for y, plab in (("z_tvip", "Panel A. Receptive vocabulary: Peabody "
                     "picture--word test (z)"),
                    ("z_cbcl2", "Panel B. Internalizing problems: "
                     "caregiver CBCL checklist (z)")):
        res = [rep.fit(mt, y, c, rep.BEST) for c in (1, 2, 3)]
        body.append(f"\\panel{{4}}{{{plab}}}")
        body += coef2("Affected $\\times$ affected zone",
                      [(r["b"], r["se"], r["p"]) for r in res])
        body.append("\\addlinespace[3pt]")
        body.append("\\hspace{1em}Observations & "
                    + " & ".join(f"{r['n']:,}" for r in res) + " \\\\")
        body.append("\\addlinespace")
        log("T2rep MT", y, [f"{r['b']:+.3f}{stars(r['p'])}" for r in res])
    body = body[:-1]
    body += ["\\midrule",
             "Municipality fixed effects & Yes & Yes & Yes \\\\",
             "Birth-cohort fixed effects & No & Yes & Yes \\\\",
             "Household controls & No & No & Yes \\\\"]
    header = [" & (1) & (2) & (3) \\\\"]
    notes = ("Replication on the public ELPI files of the medium-term "
             "table of Gillmore (2026), in his design: a single "
             "wave (2017), with affected children aged 7--11 compared "
             "with children conceived after the earthquake, aged 2--6. "
             "Column 1 includes municipality fixed effects only; column "
             "2 adds birth-cohort fixed effects; column 3 the household "
             "controls. His published column-3 coefficients are "
             "$-$0.174 for vocabulary (14,069 children) and $-$0.129 for "
             "the CBCL (11,568); the small gaps to ours reflect cleaning "
             "choices in his estimation code, which is not public. "
             "\\zonedef{} Standard errors clustered by municipality in "
             "parentheses; evaluation weights. \\starnote")
    table_env("t2rep_gillmore",
              "Replication of Gillmore's (2026) Main Table",
              "tab:gillmore",
              "@{}p{200pt}" + numcols(3, 74) + "@{}",
              header, body, notes)


def t2_lp():
    spec = importlib.util.spec_from_file_location(
        "lp", HERE / "10_ec1_largo_plazo.py")
    lp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lp)
    df = lp.build()
    body = []
    for y, plab in [("z_tvip", "Panel A. Receptive vocabulary: Peabody "
                     "picture--word test (z)"),
                    ("z_cbcl", "Panel B. Internalizing problems: "
                     "caregiver CBCL checklist (z)")]:
        res = [lp.fit(df, y, c) for c in (1, 2, 3, 4)]
        body.append(f"\\panel{{5}}{{{plab}}}")
        body += coef2("Affected $\\times$ affected zone",
                      [(r["b"], r["se"], r["p"]) for r in res])
        body.append("\\addlinespace[3pt]")
        body.append("\\hspace{1em}Observations & "
                    + " & ".join(f"{r['n']:,}" for r in res) + " \\\\")
        body.append("\\addlinespace")
        log("T2 LP", y, [f"{r['b']:+.3f}{stars(r['p'])}" for r in res])
    body = body[:-1]
    body += ["\\midrule",
             "Municipality fixed effects & Yes & Yes & Yes & Yes \\\\",
             "Cohort and wave fixed effects & No & Yes & Yes & Yes \\\\",
             "Household controls & No & No & Yes & Yes \\\\",
             "Municipality linear trends & No & No & No & Yes \\\\"]
    header = [" & (1) & (2) & (3) & (4) \\\\"]
    notes = ("Gillmore's (2026) specification taken to the 14-year "
             "horizon: the affected group are children exposed between "
             "conception and age four, measured in 2024 at ages 14--18; "
             "the comparison group are children conceived after the "
             "earthquake, measured in 2017. The estimation therefore "
             "pools two waves --- hence the wave fixed effects --- as "
             "Gillmore's own short-term table pools the 2012 and 2017 "
             "waves. The CBCL is oriented as in Gillmore (2026), positive "
             "meaning fewer problems. The municipality linear trends of "
             "column 4 are our addition; his tables end at the household "
             "controls. \\zonedef{} Standard errors clustered "
             "by municipality; evaluation weights. \\starnote")
    table_env("t2_largo_plazo",
              "Long-Run Estimates of Gillmore's (2026) Specification",
              "tab:longrun",
              "@{}p{185pt}" + numcols(4, 62) + "@{}",
              header, body, notes)


def t3_main(d):
    panels = [("z_phq4", "Panel A. Mental health: PHQ-4 index, four questions on low mood, loss of interest, nervousness and worry (0--12, z)", 3),
              ("gad2_bin", "Panel B. The anxiety half of the index: positive GAD-2 screen (its two anxiety questions, subscore of 3 or more)", 3),
              ("phq2_bin", "Panel C. The depression half of the index: positive PHQ-2 screen (its two depression questions, subscore of 3 or more)", 3)]
    body = []
    res3 = None
    for y, plab, dec in panels:
        res = [fit(d, y, c) for c in (1, 2, 3, 4)]
        if y == "z_phq4":
            res3 = res
        body.append(f"\\panel{{5}}{{{plab}}}")
        body += bins_block(res, 4, dec)
        body.append("\\addlinespace")
        log(f"T3 {y} col3:",
            {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in res[2]["b"].items()},
            "contr", f"{res[2]['contr'][0]:+.3f}{stars(res[2]['contr'][2])}")
    body = body[:-1]
    body += ["\\midrule"] + ticks4() + foot_block(res3)
    notes = ("Ordinary least squares estimates of equation~(1) on the "
             "adolescents of the 2024 ELPI wave; seven of the 10,003 "
             "adolescents of Table~\\ref{tab:sample} drop for "
             "incomplete PHQ-4 answers. Panels B and C disaggregate the Panel A "
             "index into its two pairs of questions, expressed as "
             "clinical screens; Appendix Table~\\ref{tab:a_mh} lists "
             "every question verbatim. \\bindef{} "
             "\\zonedef{} \\specdef{} The sample is the same in every "
             "panel; column 4 has 6,430 adolescents in 67 municipalities. "
             "Demanding inference for column 3 is reported in "
             "Table~\\ref{tab:robust}. \\clusternote{} \\starnote")
    table_env("t3_main",
              "Age at Exposure to the Earthquake and Self-Reported Mental "
              "Health at Ages 14--18",
              "tab:main",
              "@{}p{182pt}" + numcols(4, 64) + "@{}",
              COLHEAD4, body, notes,
              extra_pre="\\footnotesize"
                        "\\renewcommand{\\arraystretch}{0.95}")


def t4_informante(d):
    body = []
    resA = None
    for y, plab in [("z_cbcl",
                     "Panel A. CBCL internalizing score in 2024: caregiver checklist (T, z)"),
                    ("d_cbcl",
                     "Panel B. Within-child change in the same CBCL score, 2017 to 2024 (z by wave)")]:
        res = [fit(d, y, c) for c in (1, 2, 3, 4)]
        if resA is None:
            resA = res
        body.append(f"\\panel{{5}}{{{plab}}}")
        body += bins_block(res, 4)
        body.append("\\addlinespace")
        body.append("\\hspace{1em}Observations & "
                    + " & ".join(f"{r['n']:,}" for r in res) + " \\\\")
        body.append("\\addlinespace")
    body = body[:-1]
    body += ["\\midrule"] + ticks4() + [
             "Selection municipalities (clusters) & "
             + " & ".join(str(r["ncl"]) for r in resA) + " \\\\"]
    notes = ("Same design and specifications as Table~\\ref{tab:main}, "
             "with the caregiver's report of the child as the outcome. "
             "\\cbcldef{} Panel B uses the change between the 2017 "
             "measurement (ages 7--11) and the 2024 measurement (ages "
             "14--18) of the same child, each standardized within its "
             "wave and age; with two periods this is equivalent to a "
             "child fixed-effects estimate. Neither panel shows an "
             "exposure-age gradient: the scar of "
             "Table~\\ref{tab:main} appears only in what adolescents "
             "report in private. \\bindef{} \\specdef{} \\clusternote{} "
             "\\starnote")
    table_env("t4_informante",
              "Caregiver-Reported Outcomes",
              "tab:caregiver",
              "@{}p{182pt}" + numcols(4, 64) + "@{}",
              COLHEAD4, body, notes)


def t5_dosis(d):
    if "pga_z" not in d or d.pga_z.isna().all():
        log("T5: sin PGA, omitida")
        return
    doses = [("EQ", "Affected zone (0/1)"), ("pga_z", "PGA (z)"),
             ("mmi_z", "MMI intensity (z)"),
             ("ldist_z", "$-$log distance to epicenter (z)")]
    body = []
    resA = None
    for y, plab in [("z_phq4", "Panel A. PHQ-4 score: sum of four depression--anxiety items (z)"),
                    ("gad2_bin", "Panel B. Positive GAD-2 screen: two anxiety items, subscore of 3 or more")]:
        res = [fit(d, y, 3, dose=dv) for dv, _ in doses]
        if resA is None:
            resA = res
        body.append(f"\\panel{{5}}{{{plab}}}")
        body += bins_block(res, 4)
        body.append("\\addlinespace")
        log(f"T5 {y}: PGA 24-35 {res[1]['b']['24-35m'][0]:+.3f}"
            f"{stars(res[1]['b']['24-35m'][2])}, contr "
            f"{res[1]['contr'][0]:+.3f}{stars(res[1]['contr'][2])}")
    body = body[:-1]
    body += ["\\midrule"] + ticks_col3(4) + foot_block(resA)
    header = [" & \\multicolumn{4}{c}{Seismic dose of the municipality of "
              "selection} \\\\", "\\cmidrule(lr){2-5}",
              " & Affected zone (0/1) & PGA (z) & MMI (z) & $-$log dist.\\ "
              "to epicenter (z) \\\\",
              " & (1) & (2) & (3) & (4) \\\\"]
    notes = ("Estimates of equation~(1) under four measures of the seismic "
             "dose, all with the controls of column 3 of "
             "Table~\\ref{tab:main}. Column 1 repeats the official binary "
             "affected zone. Column 2 uses the peak ground acceleration: the "
             "strongest shaking of the ground during the earthquake, "
             "expressed as a share of the acceleration of gravity, "
             "measured at the centroid of the municipality of selection (from "
             "the ShakeMap of the U.S. Geological Survey) and "
             "standardized; column 3 an intensity scale from the same "
             "source; column 4 minus the log of the distance from the "
             "centroid to the epicenter. The continuous doses vary across the 116 "
             "municipalities, within affected regions, which addresses "
             "inference concerns with a regional treatment. \\bindef{} "
             "\\clusternote{} \\starnote")
    table_env("t5_dosis",
              "The Gradient Under Continuous Seismic Doses",
              "tab:dose",
              "@{}p{170pt}" + numcols(4, 67) + "@{}",
              header, body, notes)


def t6_placebo(d):
    outs = [("z_peso", "Birth weight (z)"),
            ("z_talla", "Birth length (z)"),
            ("z_gest", "Gestation weeks (z)"),
            ("prematuro", "Premature (0/1)"),
            ("z_apgar", "Apgar 5$'$ (z)")]
    res = {y: fit(d, y, 2) for y, _ in outs}
    body = []
    for lab in IV:
        body += coef2(ROWLAB[lab], [res[y]["b"][lab] for y, _ in outs])
        body.append("\\addlinespace[3pt]")
    body = body[:-1]
    yes5 = " & ".join("Yes" for _ in outs)
    body += ["\\midrule",
             f"Municipality fixed effects & {yes5} \\\\",
             f"Birth-cohort fixed effects & {yes5} \\\\",
             f"Pre-earthquake controls & {yes5} \\\\",
             "Observations & " + " & ".join(f"{res[y]['n']:,}"
                                            for y, _ in outs) + " \\\\"]
    for y, _ in outs:
        log("T6 placebo", y,
            {k: f"{v[0]:+.3f}{stars(v[2])}" for k, v in res[y]["b"].items()})
    header = [" & " + " & ".join(lab for _, lab in outs) + " \\\\",
              " & " + " & ".join(f"({i+1})" for i in range(len(outs)))
              + " \\\\"]
    notes = ("Each column reports one estimate of equation~(1) on an "
             "outcome fixed at birth, one to four years \\emph{before} "
             "the earthquake for every cohort in the sample, as reported "
             "by the mother in 2010 (Appendix Table~\\ref{tab:a_birth}). "
             "The design should find nothing. Of fifteen coefficients, "
             "two are significant at the 10 percent level (1.5 expected "
             "by chance), and their sign --- a worse birth endowment of "
             "the age-2 group in affected municipalities --- would work "
             "\\emph{against} the trough of Table~\\ref{tab:main}; the "
             "birth-endowment row of Table~\\ref{tab:robust} confirms "
             "the result does not move. \\bindef{} \\clusternote{} "
             "\\starnote")
    table_env("t6_placebo",
              "Placebo: Outcomes Fixed at Birth, Before the Earthquake",
              "tab:placebo",
              "@{}p{148pt}" + numcols(5, 61) + "@{}",
              header, body, notes)


def t7_robustez(d, ipw, nrep):
    base = fit(d, "z_phq4", 3, keep_model=True)
    variantes = [
        ("Preferred specification (column 3)", base),
        ("Fixed effects only", fit(d, "z_phq4", 1)),
        ("Excluding the Metropolitan Region", fit(d, "z_phq4", 4)),
        ("Unweighted", fit(d, "z_phq4", 3, weights=False)),
        ("PHQ-4 in points (0--12), not standardized",
         fit(d, "phq4_score", 3)),
        ("Balanced sample with a 2017 CBCL",
         fit(d, "z_phq4", 3, sample=lambda x: x.z_cbcl17.notna())),
        ("Controlling for the birth endowment",
         fit(d, "z_phq4", 3, extra_x=["z_peso", "z_gest", "prematuro"])),
    ]
    if ipw is not None:
        d2 = d.merge(ipw, on="folio", how="left")
        d2["w"] = d2.w * d2.ipw.fillna(1.0)
        variantes.append(("Reweighted for attrition (IPW)",
                          fit(d2, "z_phq4", 3)))
    if "pga_z" in d and not d.pga_z.isna().all():
        variantes.append(("Continuous dose: PGA (z) instead of the zone",
                          fit(d, "z_phq4", 3, dose="pga_z")))
    body = []
    for lab, r in variantes:
        rows = coef2(lab, [r["b"]["24-35m"]])
        rows[0] = rows[0][:-3] + f" & {r['n']:,} \\\\"
        rows[1] = rows[1][:-3] + " & \\\\"
        body += rows + ["\\addlinespace"]
        log("T7", lab,
            f"{r['b']['24-35m'][0]:+.3f}{stars(r['b']['24-35m'][2])}",
            f"contr {r['contr'][0]:+.3f}{stars(r['contr'][2])}")
    lor = []
    for rg in (5, 6, 7, 8, 9, 13):
        r = fit(d, "z_phq4", 3, sample=lambda x, rg=rg: x.region != rg)
        lor.append(r["b"]["24-35m"][0])
    body.append("Dropping one affected region at a time (range) & "
                f"[{fnum(min(lor))}, {fnum(max(lor))}] & \\\\")
    body += ["Municipality and birth-cohort fixed effects (all rows) & "
             "Yes & \\\\"]
    pp = perm_test(base, nrep)
    pw, nreg = wild_region(base, nrep)
    body += ["\\midrule",
             "\\panel{3}{Demanding inference for the preferred "
             "specification ($p$-values)}",
             "\\hspace{1em}Permutation of the affected zone across "
             f"municipalities & {pp['24']:.3f} & \\\\",
             "\\hspace{1em}Wild cluster bootstrap by region "
             f"({nreg} regions) & {pw['24']:.3f} & \\\\"]
    header = [" & Dependent variable: PHQ-4 score (z) & \\\\",
              "\\cmidrule(lr){2-2}",
              " & Age 2 $\\times$ affected & Observations \\\\",
              " & (1) & (2) \\\\"]
    notes = ("Each row re-estimates the preferred specification of "
             "Table~\\ref{tab:main}, Panel A, changing one thing. "
             "Column 1 reports the coefficient on exposure at age two "
             "$\\times$ affected zone. The IPW row reweights by the "
             "inverse of the estimated probability of remaining in the "
             "2024 wave (Table~\\ref{tab:attrition}). The permutation "
             "test reassigns the affected-zone status across the 116 "
             "municipalities of selection, keeping the number of treated "
             "municipalities, 2,000 times. The wild cluster bootstrap by "
             "region uses Webb weights and clusters at the level of the "
             "regional treatment. \\clusternote{} \\starnote")
    table_env("t7_robustez",
              "Robustness and Demanding Inference for the Main Result",
              "tab:robust",
              "@{}p{215pt}" + numcols(1, 120) + ">{\\centering"
              "\\arraybackslash}p{62pt}@{}",
              header, body, notes)
    log("T7 inferencia: perm", pp, "| wild region", pw)


def t8_rw(d, nrep):
    fam = {"z_phq4": "PHQ-4 mental-health index (z)",
           "phq2_bin": "Its depression half: PHQ-2 positive",
           "gad2_bin": "Its anxiety half: GAD-2 positive",
           "z_cbcl": "CBCL internalizing, caregiver (z)"}
    results = {y: fit(d, y, 3, keep_model=True) for y in fam}
    stats, rwp = rw_stepdown(results, nrep)
    body = []
    for y, lab in fam.items():
        r = results[y]
        body.append(f"{lab} & {r['b']['24-35m'][2]:.3f} & "
                    f"{rwp[(y, '24')]:.3f} \\\\")
        log("T8 RW", y, "24:", f"{rwp[(y, '24')]:.3f}",
            "ct:", f"{rwp[(y, 'ct')]:.3f}")
    header = [" & \\multicolumn{2}{c}{Age 2 $\\times$ affected} \\\\",
              "\\cmidrule(lr){2-3}",
              " & Unadjusted $p$ & Romano--Wolf $p$ \\\\",
              " & (1) & (2) \\\\"]
    notes = ("Romano--Wolf stepdown $p$-values over the family of four "
             "mental-health outcomes, estimated with the preferred "
             "specification of Table~\\ref{tab:main}. The adjustment "
             "uses a joint wild cluster bootstrap by municipality (Rademacher "
             "weights, 2,000 replications, the same sign flips for "
             "every outcome), for the age-two coefficient.")
    table_env("t8_romanowolf",
              "Multiple-Hypothesis Adjustment Across Mental-Health "
              "Outcomes",
              "tab:rw",
              "@{}p{175pt}" + numcols(2, 90) + "@{}",
              header, body, notes)


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
    body = []
    for lab, v in IV.items():
        body += coef2(ROWLAB[lab] + " $\\times$ affected",
                      [(r.params[v], r.bse[v], r.pvalues[v])])
        body.append("\\addlinespace")
        log("T9 atricion", v, f"{r.params[v]:+.3f}{stars(r.pvalues[v])}")
    body = body[:-1]
    body += ["\\midrule",
             "Exposure-age and region fixed effects & Yes \\\\",
             "Mother's education and age in 2010 & Yes \\\\",
             f"Observations & {int(r.nobs):,} \\\\",
             "Mean retention into 2024 & "
             f"{d.in2024.mean() * 100:.1f} percent \\\\"]
    header = [" & Pr(reinterviewed in 2024) \\\\", " & (1) \\\\"]
    notes = ("Linear probability model over the children of the 2010 "
             "baseline with a valid birth date. The outcome is an "
             "indicator for being reinterviewed in the 2024 wave. The "
             "small and insignificant coefficients show that the loss "
             "of the sample (32.7 percent) does not concentrate in any "
             "treatment-by-age cell; the fitted probabilities feed the "
             "IPW row of Table~\\ref{tab:robust}. The affected zone "
             "enters through the region of residence reported in 2010. "
             "Robust standard errors in parentheses. \\starnote")
    table_env("t9_atricion",
              "Attrition from 2010 to 2024 by Exposure Age and Zone",
              "tab:attrition",
              "@{}p{250pt}>{\\centering\\arraybackslash}p{130pt}@{}",
              header, body, notes)
    phat = r.predict(d).clip(0.05, 0.98)
    return pd.DataFrame({"folio": d.folio, "ipw": 1.0 / phat})


def t10_mecanismos(d):
    bloques = [
        ("t10a_bienestar",
         "Other Adolescent Outcomes I: Well-Being and Victimization",
         "tab:mech1",
         [("z_resil", "Resilience (z)"),
          ("z_satisf", "Life satisf. (z)"),
          ("z_salud", "Poor health (z)"),
          ("z_bull", "Bullying (z)"),
          ("ciber_any", "Cyber-vict. (0/1)")]),
        ("t10b_riesgo",
         "Other Adolescent Outcomes II: Dating Violence and Substance Use",
         "tab:mech2",
         [("viol_pareja", "Dating viol. (0/1)"),
          ("fuma", "Tobacco (0/1)"),
          ("alcohol", "Alcohol (0/1)"),
          ("cannabis", "Cannabis (0/1)")])]
    comps = {"tab:mech1":
             "Resilience is the mean of the six Brief Resilience Scale "
             "items; life satisfaction a single 1--7 item; poor health a "
             "single reversed item; bullying the mean of eight frequency "
             "items, one reverse-coded; cyber-victimization one if any "
             "of six items is answered yes.",
             "tab:mech2":
             "Dating violence is one if any of three items is answered "
             "yes, among adolescents who ever dated; tobacco, alcohol "
             "and cannabis refer to the last 12 months, with alcohol "
             "one if any of four beverage items is answered yes."}
    for fname, cap, lab, outs in bloques:
        res = {y: fit(d, y, 3) for y, _ in outs}
        body = []
        for b in IV:
            body += coef2(ROWLAB[b], [res[y]["b"][b] for y, _ in outs])
            body.append("\\addlinespace[3pt]")
        body = body[:-1]
        body += ["\\midrule"] + ticks_col3(len(outs)) + [
                 "Observations & " + " & ".join(f"{res[y]['n']:,}"
                                                for y, _ in outs)
                 + " \\\\"]
        for y, _ in outs:
            log("T10", y, {k: f"{v[0]:+.3f}{stars(v[2])}"
                           for k, v in res[y]["b"].items()})
        header = [" & " + " & ".join(l for _, l in outs) + " \\\\",
                  " & " + " & ".join(f"({i+1})"
                                     for i in range(len(outs)))
                  + " \\\\"]
        notes = ("Each column reports one estimate of equation~(1) with "
                 "the specification of column 3 of Table~\\ref{tab:main} "
                 "on another outcome of the 2024 wave. " + comps[lab]
                 + " Appendix Table~\\ref{tab:a_other} lists every item "
                 "and scale verbatim. \\bindef{} \\clusternote{} "
                 "\\starnote")
        table_env(fname, cap, lab,
                  "@{}p{148pt}" + numcols(len(outs), 62) + "@{}",
                  header, body, notes)


def t11_madre(d):
    d = d.copy()
    d["vuln"] = ((d.mh_emb_dx == 1) | (d.dep_postparto == 1)
                 | (d.deriv_psic == 1)).astype(float)
    res = {}
    for y in ("z_phq4", "gad2_bin"):
        res[(y, 1)] = fit(d, y, 3, sample=lambda x: x.vuln == 1)
        res[(y, 0)] = fit(d, y, 3, sample=lambda x: x.vuln == 0)
    order = [("z_phq4", 1), ("z_phq4", 0), ("gad2_bin", 1), ("gad2_bin", 0)]
    body = []
    for lab in IV:
        body += coef2(ROWLAB[lab], [res[k]["b"][lab] for k in order])
        body.append("\\addlinespace")
    body = body[:-1]
    body += ["\\midrule",
             "Municipality fixed effects & Yes & Yes & Yes & Yes \\\\",
             "Birth-cohort fixed effects & Yes & Yes & Yes & Yes \\\\",
             "Observations & " + " & ".join(f"{res[k]['n']:,}"
                                             for k in order) + " \\\\"]
    header = [" & \\multicolumn{2}{c}{PHQ-4 score (z)} & "
              "\\multicolumn{2}{c}{Positive GAD-2 screen} \\\\",
              "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}",
              " & Vulnerable mother & Other mothers & Vulnerable mother & "
              "Other mothers \\\\",
              " & (1) & (2) & (3) & (4) \\\\"]
    notes = ("Split-sample estimates of the preferred specification of "
             "Table~\\ref{tab:main}. A vulnerable mother reported, in "
             "2010, a diagnosis of depression, anxiety or post-traumatic "
             "stress during the pregnancy of the child, a psychological "
             "or psychiatric referral, or diagnosed postpartum "
             "depression --- all predating the earthquake by years "
             "(Appendix Table~\\ref{tab:a_mother}). The age-2 coefficient is "
             "nearly identical in the two groups, for both outcomes: the "
             "gradient is not a recomposition of pre-existing family "
             "mental-health burden. \\bindef{} \\clusternote{} \\starnote")
    table_env("t11_madre",
              "Estimates by the Mother's Pre-Earthquake Mental Health",
              "tab:mother",
              "@{}p{168pt}" + numcols(4, 67) + "@{}",
              header, body, notes)
    for y in ("z_phq4", "gad2_bin"):
        log("T11", y, "vuln contr:",
            f"{res[(y, 1)]['contr'][0]:+.3f}{stars(res[(y, 1)]['contr'][2])}",
            "| no-vuln contr:",
            f"{res[(y, 0)]['contr'][0]:+.3f}{stars(res[(y, 0)]['contr'][2])}")


def t12_heterogeneidad(d):
    grupos = [("Girls", lambda x: x.mujer == 1),
              ("Boys", lambda x: x.mujer == 0),
              ("Mother with secondary education or less",
               lambda x: num(x.educ_madre10) <= 12),
              ("Mother with tertiary education",
               lambda x: num(x.educ_madre10) > 12),
              ("Urban household in 2010", lambda x: x.rural10 == 0),
              ("Rural household in 2010", lambda x: x.rural10 == 1)]
    body = ["\\panel{3}{Panel A. The PHQ-4 index (z)}"]
    for lab, sel in grupos:
        r = fit(d, "z_phq4", 3, sample=sel)
        rows = coef2(lab, [r["b"]["24-35m"]])
        rows[0] = rows[0][:-3] + f" & {r['n']:,} \\\\"
        rows[1] = rows[1][:-3] + " & \\\\"
        body += rows + ["\\addlinespace[3pt]"]
        log("T12A", lab,
            f"{r['b']['24-35m'][0]:+.3f}{stars(r['b']['24-35m'][2])}",
            f"contr {r['contr'][0]:+.3f}{stars(r['contr'][2])}")
    body.append("\\panel{3}{Panel B. The two halves of the index, "
                "girls versus boys}")
    for y, half in (("gad2_bin", "anxiety half (GAD-2 positive)"),
                    ("phq2_bin", "depression half (PHQ-2 positive)")):
        for sx, sxlab in ((1, "Girls"), (0, "Boys")):
            r = fit(d, y, 3, sample=lambda x, s=sx: x.mujer == s)
            rows = coef2(f"{sxlab}, {half}",
                         [r["b"]["24-35m"]])
            rows[0] = rows[0][:-3] + f" & {r['n']:,} \\\\"
            rows[1] = rows[1][:-3] + " & \\\\"
            body += rows + ["\\addlinespace[3pt]"]
            log("T12B", y, sxlab,
                f"{r['b']['24-35m'][0]:+.3f}{stars(r['b']['24-35m'][2])}")
    body = body[:-1]
    body += ["\\midrule",
             "Municipality and birth-cohort fixed effects & Yes & \\\\"]
    header = [" & Age 2 $\\times$ affected & Observations \\\\",
              " & (1) & (2) \\\\"]
    notes = ("Each pair of rows estimates the specification of column 3 "
             "of Table~\\ref{tab:main} on the subsample named in the "
             "row. Panel A uses the PHQ-4 index; Panel B splits the "
             "index into its anxiety and depression halves, expressed "
             "as clinical screens, separately for girls and boys. The "
             "baseline level of symptoms is much higher among girls "
             "--- the index averages 4.88 points for girls and 3.76 "
             "for boys. \\clusternote{} \\starnote")
    table_env("t12_heterogeneidad",
              "Heterogeneity of the Main Result",
              "tab:het",
              "@{}p{200pt}" + numcols(1, 100) + ">{\\centering"
              "\\arraybackslash}p{62pt}@{}",
              header, body, notes)


def figuras(d):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    INK, BLUE, GRID = "#0B0B0B", "#2A78D6", "#C9C9C9"
    x = np.arange(4)
    xt_lab = ["$<$1\n(reference)", "Age 1", "Age 2", "Ages 3–4"]
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    for y, colr, lab, off in [
            ("z_phq4", INK, "PHQ-4 mental-health index (z)", -0.07),
            ("gad2_bin", BLUE,
             "Positive anxiety screen, GAD-2 (probability)", 0.07)]:
        r = fit(d, y, 3)
        bs = [0.0] + [r["b"][b][0] for b in IV]
        ses = [0.0] + [r["b"][b][1] for b in IV]
        ax.errorbar(x + off, bs, yerr=[1.96 * s for s in ses], fmt="o",
                    color=colr, ecolor=colr, elinewidth=1.4, capsize=0,
                    markersize=5, label=lab)
    ax.axhline(0, color=GRID, lw=1, zorder=0)
    ax.set_xticks(x, xt_lab)
    ax.set_xlabel("Age when the earthquake struck")
    ax.set_ylabel("Effect relative to children\nstruck before age 1")
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
        ax.set_xticks(x, xt_lab)
        ax.set_xlabel("Age when the earthquake struck")
        ax.set_ylabel("Effect of one SD of ground shaking\non the PHQ-4 index (z)")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.spines["left"].set_color(GRID)
        ax.spines["bottom"].set_color(GRID)
        fig.tight_layout()
        fig.savefig(FIG / "f2_dosis_pga.pdf")
        plt.close(fig)
        log("-> paper/figures/f2_dosis_pga.pdf")


def mapas(d):
    """Coropletas a nivel comunal con los poligonos oficiales (geojson de
    la DPA, data/external/comunas_chile.geojson): dosis sismica (PGA) y
    ansiedad adolescente por municipio; los municipios fuera de la muestra
    ELPI van en gris claro."""
    import json
    import unicodedata
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPoly
    from matplotlib.collections import PatchCollection
    import matplotlib.patheffects as pe
    gj = Path("data/external/comunas_chile.geojson")
    pfile = Path("data/processed/pga_comuna.csv")
    if not (gj.exists() and pfile.exists()):
        log("mapas: faltan insumos, omitidos")
        return

    def norm(x):
        x = unicodedata.normalize("NFKD", str(x))
        return "".join(c for c in x if not unicodedata.combining(c)).lower().strip()
    pg = pd.read_csv(pfile)
    g24 = (d.assign(cut=num(d.cut_comuna_seleccion))
           .groupby("cut").agg(gad=("gad2_bin", "mean")).reset_index())
    pg = pg.merge(g24, on="cut", how="left")
    vals = {norm(r.nombre): (r.pga, r.gad * 100 if pd.notna(r.gad)
                             else np.nan) for _, r in pg.iterrows()}
    feats = json.load(open(gj))["features"]
    polys, keys, cities = [], [], {}
    WANT_CITY = {"santiago", "concepcion", "valparaiso", "temuco",
                 "antofagasta"}
    for f in feats:
        nm = norm(f["properties"]["Comuna"])
        geom = f["geometry"]
        rings = ([geom["coordinates"]] if geom["type"] == "Polygon"
                 else geom["coordinates"])
        for ring in rings:
            ext = np.asarray(ring[0])
            if ext[:, 0].mean() < -76.5 or ext[:, 1].mean() < -56.2:
                continue                      # islas lejanas / antartica
            polys.append(ext)
            keys.append(nm)
            if nm in WANT_CITY and nm not in cities:
                cities[nm] = (ext[:, 0].mean(), ext[:, 1].mean())
    epi = (-72.898, -36.122)
    halo = [pe.withStroke(linewidth=2.2, foreground="white")]
    NICE = {"santiago": "Santiago", "concepcion": "Concepción",
            "valparaiso": "Valparaíso", "temuco": "Temuco",
            "antofagasta": "Antofagasta"}

    def choropleth(idx, cmap, cbar_label, fname, epi_star):
        fig, ax = plt.subplots(figsize=(3.6, 7.8))
        sampled, svals, unsampled = [], [], []
        for xy, nm in zip(polys, keys):
            v = vals.get(nm, (np.nan, np.nan))[idx]
            if pd.notna(v):
                sampled.append(MplPoly(xy, closed=True))
                svals.append(v)
            else:
                unsampled.append(MplPoly(xy, closed=True))
        pc0 = PatchCollection(unsampled, facecolor="#EDEDED",
                              edgecolor="white", linewidth=0.25,
                              rasterized=True)
        ax.add_collection(pc0)
        pc1 = PatchCollection(sampled, cmap=cmap, edgecolor="white",
                              linewidth=0.3, rasterized=True)
        pc1.set_array(np.asarray(svals))
        ax.add_collection(pc1)
        if epi_star:
            ax.scatter(*epi, marker="*", s=170, color="#0B0B0B", zorder=5)
            ax.annotate("Epicenter", epi, textcoords="offset points",
                        xytext=(-10, -13), fontsize=8, ha="right",
                        path_effects=halo, zorder=6)
        offs = {"santiago": (11, -10), "valparaiso": (10, 3)}
        for nm, xy in cities.items():
            ax.annotate(NICE[nm], xy, textcoords="offset points",
                        xytext=offs.get(nm, (10, -2)), fontsize=8,
                        path_effects=halo, zorder=6)
        ax.set_xlim(-76.3, -64.8)
        ax.set_ylim(-56.2, -17.2)
        ax.set_aspect(1.22)
        ax.set_xlabel("Longitude", fontsize=9)
        ax.set_ylabel("Latitude", fontsize=9)
        ax.tick_params(labelsize=8, color="#C9C9C9")
        for sp in ax.spines.values():
            sp.set_color("#C9C9C9")
        cb = fig.colorbar(pc1, ax=ax, shrink=0.5, pad=0.03)
        cb.set_label(cbar_label, fontsize=9)
        cb.ax.tick_params(labelsize=8)
        cb.outline.set_color("#C9C9C9")
        fig.tight_layout()
        fig.savefig(FIG / fname, dpi=300)
        plt.close(fig)
        log(f"-> paper/figures/{fname} "
            f"({len(sampled)} municipios con dato)")
    choropleth(0, "Reds", "Peak ground acceleration (percent of g)",
               "f3_mapa_dosis.pdf", True)
    choropleth(1, "Blues", "Positive GAD-2 anxiety screen (percent)",
               "f4_mapa_sintomas.pdf", False)


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
        mapas(d)
    if go("t2"):
        t2_lp()
    if go("t2rep"):
        t2rep()
    Path("reports").mkdir(exist_ok=True)
    (Path("reports") / "paper_numeros.md").write_text(
        "# Log de estimaciones del paper\n\n```\n" + "\n".join(LOG)
        + "\n```\n", encoding="utf-8")
    log("-> reports/paper_numeros.md")


if __name__ == "__main__":
    main()
