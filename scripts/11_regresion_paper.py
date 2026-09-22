#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA regresión del paper: cicatriz de salud mental del 27-F a los 14–18 años.

Qué la separa de Gillmore (EER 2026):
  - Outcome: salud mental AUTORREPORTADA por el adolescente (PHQ-4, GAD-2),
    a solas. Gillmore solo tiene tests cognitivos y reportes del cuidador.
  - Horizonte: 14 años después del sismo (ola 2024). Su paper termina en
    2017 (edad ≤ 11).
  - Diseño: dosis por edad-a-la-exposición dentro de la cohorte expuesta
    (todos los de 2024 vivieron el 27-F con 0–4 años), DiD bin×EQ con FE de
    comuna de selección y de cohorte. Él usa esa variación solo como
    heterogeneidad de su efecto en la niñez (Fig. B.1), nunca como diseño
    principal ni en la adolescencia.
  - Panel B: persistencia INTRA-NIÑO del CBCL 2017→2024 (mismo niño, dos
    olas). Estructuralmente imposible en su repeated cross-section.

Especificación (ec. 2 del paper nuestro):
  Y_imc = α + Σ_a β_a (Bin_a(i) × EQ_m) + γ_a Bin_a(i) + ψ_m + θ_c
          + X'_i δ + ε_imc
  con a ∈ {12–23m, 24–35m, 36–59m}, referencia 0–11 meses el 27-F;
  m = comuna de selección PRE-terremoto (sin sesgo de migración);
  c = cohorte de nacimiento. EQ_m absorbido por ψ_m. Cluster por comuna;
  para la inferencia con tratamiento regional, wild cluster bootstrap-t
  por REGIÓN (pesos de Webb) del contraste clave.

Columnas (formato Gillmore):
  (1) interacciones + FE comuna + FE cohorte + bins
  (2) + X pre-terremoto (sexo, edad, línea base 2010: educ/edad madre,
      tamaño hogar, ruralidad) con indicadores de missing
  (3) + sensibilidad post-27F (nº hijos 2012, salud mental familiar 2012)
  (4) col. (3) sin Región Metropolitana

Salida: reports/regresion_paper.md
Uso:    python3 scripts/11_regresion_paper.py
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import statsmodels.formula.api as smf

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "sm27", HERE / "09_salud_mental_27f.py")
sm27 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sm27)

OUT = Path("reports")
IV = {"12-23m": "I_12_23", "24-35m": "I_24_35", "36-59m": "I_36_59"}
X_PRE = ["mujer", "edad_meses", "edad_madre10", "educ_madre10",
         "tot_per10", "rural10"]
X_POST = ["n_hijos", "mh_madre", "mh_padre", "mh_ofam", "mh_miss"]
CONTR = "I_36_59 - I_24_35"      # memoria (3–5a) vs valle (2a)


def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""


def xt(d, xs):
    terms = []
    for v in xs:
        if d[v].isna().any():
            d[f"{v}_mi"] = d[v].isna().astype(float)
            d[v] = d[v].fillna(d[v].median())
            terms += [v, f"{v}_mi"]
        else:
            terms.append(v)
    return terms


def fit(d, y, col):
    d = d.dropna(subset=[y, "EQ", "estrato", "w", "cohorte", "bin"]).copy()
    d = d[d.w > 0]
    if col == 4:
        d = d[d.region != 13]
    d["est"] = d.estrato.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    for lab, v in IV.items():
        d[v] = ((d.bin == lab) & (d.EQ == 1)).astype(float)
    rhs = " + ".join(list(IV.values()) + ["C(bin)", "C(est)", "C(coh)"])
    if col >= 2:
        rhs += " + " + " + ".join(xt(d, X_PRE))
    if col >= 3:
        rhs += " + " + " + ".join(xt(d, X_POST))
    f = f"{y} ~ {rhs}"
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d.est})
    ct = r.t_test(CONTR)
    return {"f": f, "d": d, "r": r, "n": int(r.nobs),
            "ncl": d.est.nunique(),
            "b": {k: (r.params[v], r.bse[v], r.pvalues[v])
                  for k, v in IV.items()},
            "contr": (float(np.ravel(ct.effect)[0]),
                      float(np.ravel(ct.sd)[0]),
                      float(np.ravel(ct.pvalue)[0]))}


def wild_region(res, combos, B=4999, seed=27):
    """Wild cluster bootstrap-t (no restringido, pesos Webb) con clusters
    de REGIÓN para las combinaciones lineales `combos` (dict nombre→str).
    Devuelve {nombre: (t_obs, p_wild, n_regiones)}."""
    d = res["d"]
    y, X = patsy.dmatrices(res["f"], d, return_type="dataframe")
    keep = ~X.isna().any(axis=1) & ~y.iloc[:, 0].isna()
    Xd, yv = X[keep], y[keep].iloc[:, 0]
    w = d.loc[Xd.index, "w"].to_numpy()
    g = d.loc[Xd.index, "region"].astype(int).to_numpy()
    sw = np.sqrt(w)
    Xw = Xd.to_numpy() * sw[:, None]
    yw = yv.to_numpy() * sw
    XtXi = np.linalg.pinv(Xw.T @ Xw)
    A = XtXi @ Xw.T
    bhat = A @ yw
    ehat = yw - Xw @ bhat
    regs = np.unique(g)
    idx = [np.where(g == r)[0] for r in regs]

    def crve(e):
        M = np.zeros((Xw.shape[1], Xw.shape[1]))
        for ii in idx:
            s = Xw[ii].T @ e[ii]
            M += np.outer(s, s)
        return XtXi @ M @ XtXi

    cvecs = {}
    names = list(Xd.columns)
    for nm, expr in combos.items():
        c = np.zeros(len(names))
        for tok in expr.replace(" ", "").replace("-", "+-").split("+"):
            if not tok:
                continue
            sgn = -1.0 if tok.startswith("-") else 1.0
            c[names.index(tok.lstrip("-"))] = sgn
        cvecs[nm] = c
    V0 = crve(ehat)
    tobs = {nm: float(c @ bhat / np.sqrt(c @ V0 @ c))
            for nm, c in cvecs.items()}
    rng = np.random.default_rng(seed)
    webb = np.array([-np.sqrt(1.5), -1, -np.sqrt(0.5),
                     np.sqrt(0.5), 1, np.sqrt(1.5)])
    hits = {nm: 0 for nm in cvecs}
    for _ in range(B):
        sg = rng.choice(webb, size=len(regs))
        e_b = ehat * np.repeat(1.0, len(ehat))
        for j, ii in enumerate(idx):
            e_b[ii] = ehat[ii] * sg[j]
        yb = Xw @ bhat + e_b
        bb = A @ yb
        Vb = crve(yb - Xw @ bb)
        for nm, c in cvecs.items():
            tb = (c @ (bb - bhat)) / np.sqrt(c @ Vb @ c)
            if abs(tb) >= abs(tobs[nm]):
                hits[nm] += 1
    return {nm: (tobs[nm], (hits[nm] + 1) / (B + 1), len(regs))
            for nm in cvecs}


def cell(b, se, p):
    return f"{b:.3f}{stars(p)} ({se:.3f})"


def panel(md, d, y, titulo, wild_for=None):
    filas = {k: [] for k in IV}
    contr, meta = [], []
    wild = None
    for col in (1, 2, 3, 4):
        res = fit(d, y, col)
        for k in IV:
            filas[k].append(cell(*res["b"][k]))
        contr.append(cell(*res["contr"]))
        meta.append(res)
        print(f"  {y} col{col}: " +
              " ".join(f"{k}={res['b'][k][0]:+.3f}{stars(res['b'][k][2])}"
                       for k in IV) +
              f" contr={res['contr'][0]:+.3f}{stars(res['contr'][2])}"
              f" n={res['n']:,}")
        if wild_for == col:
            wild = wild_region(res, {"24-35m×EQ": "I_24_35", "contraste": CONTR})
            print(f"    wild región: " + ", ".join(
                f"{nm}: t={t:.2f} p={p:.3f} ({nr} reg.)"
                for nm, (t, p, nr) in wild.items()))
    md += [f"**{titulo}**", "",
           "| | (1) | (2) | (3) | (4) sin RM |", "|---|---:|---:|---:|---:|"]
    lab = {"12-23m": "12–23m × EQ", "24-35m": "24–35m × EQ",
           "36-59m": "36–59m × EQ"}
    for k in IV:
        md.append(f"| {lab[k]} | " + " | ".join(filas[k]) + " |")
    md.append("| Contraste 36–59 − 24–35 | " + " | ".join(contr) + " |")
    md.append("| n | " + " | ".join(f"{m['n']:,}" for m in meta) + " |")
    md.append("| Comunas (cluster) | " +
              " | ".join(str(m["ncl"]) for m in meta) + " |")
    if wild:
        md.append("")
        md.append("Wild cluster bootstrap-t por región (Webb, 4.999 reps, "
                  "col. 3): " + "; ".join(
                      f"{nm}: p = {p:.3f}" for nm, (t, p, nr) in wild.items())
                  + f" ({wild['contraste'][2]} regiones).")
    md.append("")
    return md


def main():
    d = sm27.build()
    print("n =", len(d), "| EQ:", f"{d.EQ.mean():.0%}",
          "| comunas:", d.estrato.nunique(),
          "| regiones:", d.region.nunique())
    md = [
        "# La regresión del paper: 27-F y salud mental a los 14–18",
        "",
        "Ec.: `Y_imc = α + Σ_a β_a(Bin_a×EQ_m) + γ_a Bin_a + ψ_m + θ_c "
        "+ X'δ + ε`. Referencia: expuestos con **0–11 meses** el 27-F. "
        "β>0 = peor salud mental. FE de comuna de selección PRE-terremoto "
        "(ψ_m, absorbe EQ) y de cohorte (θ_c). EE cluster por comuna; "
        "inferencia clave re-chequeada con wild bootstrap por región. "
        "Pesos f_exp 2024. Col. (2) añade X pre-terremoto (sexo, edad, "
        "línea base 2010), col. (3) sensibilidad con controles 2012 "
        "(nº hijos, salud mental familiar), col. (4) excluye la RM.",
        "",
        "## Panel A — niveles 2024 (autorreporte y cuidador)",
        ""]
    md = panel(md, d, "z_phq4", "PHQ-4 (z), autorreporte", wild_for=3)
    md = panel(md, d, "gad2_bin", "GAD-2 positivo (0/1), autorreporte")
    md = panel(md, d, "phq2_bin", "PHQ-2 positivo (0/1), autorreporte")
    md = panel(md, d, "z_cbcl", "CBCL2-T 2024 (z), reporte del cuidador")
    md += ["## Panel B — persistencia intra-niño: ΔCBCL 2017→2024 (z)", "",
           "Mismo niño en ambas olas (z por ola×edad); un ΔY sobre "
           "Bin×EQ equivale al FE de niño con dos períodos.", ""]
    md = panel(md, d, "d_cbcl", "ΔCBCL 2017→2024")
    md += [
        "## Por qué esta regresión NO está en Gillmore",
        "1. Ningún outcome suyo es autorreportado por el niño/adolescente; "
        "PHQ-4/GAD-2 solo existen en la ola 2024, que él no usa.",
        "2. Su horizonte máximo es 2017 (edad 11). Aquí: 14 años "
        "post-sismo, adolescencia.",
        "3. La dosis edad-a-la-exposición es su Fig. B.1 (heterogeneidad), "
        "nunca su diseño principal; aquí es la única fuente de "
        "identificación posible y se defiende como tal.",
        "4. El panel intra-niño (B) exige observar dos veces al mismo "
        "niño: su diseño de cortes repetidos no lo permite.",
        ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "regresion_paper.md").write_text("\n".join(md), encoding="utf-8")
    print("->", OUT / "regresion_paper.md")


if __name__ == "__main__":
    main()
