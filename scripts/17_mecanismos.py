#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de mecanismos (exploración, fase de discusión — aún sin tablas .tex).

Cinco señales sobre los dos canales de ventana del paper:
  A. Kill-test: el TVIP 2024 por bins de edad de exposición NO debe
     mostrar la U (los portadores de la cognición son los canales
     comunes; la U es propia de la salud mental).
  B. Canal de programación: la angustia del cuidador tras el 27-F
     (módulo h4 de 2012) debería cargar el brazo izquierdo (bebés),
     no el derecho (3-4 años).
  C. Dosis material dentro de la zona afectada: daño a la vivienda
     (h3 de 2012) × bins.
  D. Lactancia: destete en la ventana de los 3 meses posteriores al
     terremoto entre los que mamaban el 27-F, zona afectada vs no
     (con ventana placebo pre-terremoto).
  E. Rival del brazo derecho: corte escolar del 31 de marzo dentro de
     los nacidos feb-may 2006 (misma memoria, distinto año de entrada).

Entradas: data/processed/paper_adolescentes.pkl, interim 2012 y 2024.
Salida:   reports/mecanismos_tests.md (y consola).
Uso:      python3 scripts/17_mecanismos.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p15", HERE / "15_paper_estimaciones.py")
p15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p15)

num, fit, xt, zg = p15.num, p15.fit, p15.xt, p15.zg
X_PRE, X_POST, IV = p15.X_PRE, p15.X_POST, p15.IV
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def cel(r, v):
    return f"{r.params[v]:+.3f} (ee {r.bse[v]:.3f}, p={r.pvalues[v]:.3f})"


def carga():
    d, _, _ = p15.load_data()
    v12, _ = pyreadstat.read_dta(
        "data/interim/2012/Entrevistada_2012.dta",
        usecols=["folio", "h3", "h4_1", "h4_2", "h4_3", "h4_4", "h4_5",
                 "b30", "b32"])
    v12["folio"] = num(v12.folio).astype("int64")
    v12 = v12.drop_duplicates("folio")
    h3 = num(v12.h3)
    v12["dano_mayor"] = np.where(h3.isin([1, 2, 3]), 1.0,
                                 np.where(h3.isin([4, 5]), 0.0, np.nan))
    v12["dano_alguno"] = np.where(h3.isin([1, 2, 3, 4]), 1.0,
                                  np.where(h3 == 5, 0.0, np.nan))
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
    d = (d.merge(v12[["folio", "dano_mayor", "dano_alguno", "angustia12",
                      "mamando"]], on="folio", how="left")
          .merge(t24, on="folio", how="left"))
    d["z_tvip"] = zg(d.tvip_pst_hispano)
    return d


def fino(d, y, dose="EQ", sample=None):
    """Perfil fino en bins de 6 meses (ref. 6-11m), spec col. 3."""
    dd = d.copy()
    if sample is not None:
        dd = dd[sample(dd)]
    dd = dd.dropna(subset=[y, dose, "estrato", "w", "cohorte"])
    dd = dd[(dd.w > 0) & dd.edadq_m.between(6, 49)].copy()
    dd["est"] = dd.estrato.astype(int).astype(str)
    dd["coh"] = dd.cohorte.astype(int).astype(str)
    edges = [6, 12, 18, 24, 30, 36, 42, 50]
    labs = [f"f{a:02d}" for a in edges[:-1]]
    dd["binf"] = pd.cut(dd.edadq_m, edges, right=False, labels=labs)
    ivs = []
    for lb in labs[1:]:
        dd[f"I{lb}"] = (dd.binf == lb).astype(float) * num(dd[dose])
        ivs.append(f"I{lb}")
    rhs = " + ".join(ivs + ["C(binf)", "C(est)", "C(coh)"]
                     + xt(dd, X_PRE) + xt(dd, X_POST))
    r = smf.wls(f"{y} ~ {rhs}", data=dd, weights=dd.w).fit(
        cov_type="cluster", cov_kwds={"groups": dd.est})
    return r, ivs, int(r.nobs)


def test_a(d):
    log("\n## A. Kill-test: TVIP 2024 por edad de exposición")
    log("La U es de la salud mental; si aparece tambien en vocabulario, "
        "la historia de ventanas muere.")
    r = fit(d, "z_tvip", col=3)
    log(f"Bins gruesos (ref. 0-11m), N={r['n']}:")
    for k in ("12-23m", "24-35m", "36-59m"):
        b, se, p = r["b"][k]
        log(f"  {k}: {b:+.3f} (ee {se:.3f}, p={p:.3f})")
    b, se, p = r["contr"]
    log(f"  Contraste 3-4 vs 2: {b:+.3f} (ee {se:.3f}, p={p:.3f})")
    rf, ivs, n = fino(d, "z_tvip")
    log(f"Bins finos (ref. 6-11m), N={n}:")
    for v in ivs:
        log(f"  {v}: {cel(rf, v)}")
    rp, ivp, np_ = fino(d, "z_phq4")
    log(f"(referencia PHQ-4, mismos bins, N={np_}:)")
    for v in ivp:
        log(f"  {v}: {cel(rp, v)}")


def test_b(d):
    log("\n## B. Angustia del cuidador (h4 2012) y los dos brazos")
    log("Prediccion de programacion: el brazo del bebe viaja por la "
        "crianza -> mas fuerte en hogares con cuidador angustiado; el "
        "brazo 3-4 viaja por la memoria propia -> no depende de h4.")
    tt = d.dropna(subset=["angustia12"])
    log(f"angustia12 (estres/miedo/recuerdos del cuidador): media "
        f"{tt.angustia12.mean():.3f}; por zona: "
        f"{tt.groupby('EQ').angustia12.mean().round(3).to_dict()}")
    for lab, sub in [("hogares con angustia", lambda x: x.angustia12 == 1),
                     ("hogares sin angustia", lambda x: x.angustia12 == 0)]:
        for y in ("z_phq4", "gad2_bin"):
            r = fit(d, y, col=3, sample=sub)
            b24 = r["b"]["24-35m"]
            ct = r["contr"]
            log(f"  {lab:>20} | {y:8}: edad2 {b24[0]:+.3f} "
                f"(p={b24[2]:.3f}); 3-4 menos 2 {ct[0]:+.3f} "
                f"(p={ct[2]:.3f}); N={r['n']}")


def test_c(d):
    log("\n## C. Dano a la vivienda (h3 2012) dentro de la zona afectada")
    log("Tratamiento dentro de comuna: destruida o dano mayor vs menor "
        "o sin dano, solo zona afectada.")
    tt = d[(d.EQ == 1)].dropna(subset=["dano_mayor"])
    log(f"P(dano mayor | zona afectada) = {tt.dano_mayor.mean():.3f} "
        f"(N={len(tt)})")
    log("(efecto principal del dano incluido: los coeficientes son el "
        "diferencial de cada bin frente a los bebes)")
    for y in ("z_phq4", "gad2_bin", "z_tvip"):
        r = fit(d, y, col=3, dose="dano_mayor", extra_x=["dano_mayor"],
                sample=lambda x: x.EQ == 1, keep_model=True)
        rm = smf.wls(r["_f"], data=r["_d"], weights=r["_w"]).fit(
            cov_type="cluster", cov_kwds={"groups": r["_d"].est})
        cells = "; ".join(f"{k} {v[0]:+.3f} (p={v[2]:.3f})"
                          for k, v in r["b"].items())
        log(f"  {y:8}: dano en bebes {rm.params['dano_mayor']:+.3f} "
            f"(p={rm.pvalues['dano_mayor']:.3f}); {cells}; N={r['n']}")


def test_d(d):
    log("\n## D. Destete alrededor del 27-F (b30/b32 2012)")
    tt = d.dropna(subset=["mamando"]).copy()
    tt = tt[tt.edadq_m.between(1, 18)]
    tt = tt[tt.mamando >= tt.edadq_m]          # mamaba el 27-F
    log(f"Mamaban el 27-F y edad 1-18m: N={len(tt)}; por zona "
        f"{tt.EQ.value_counts().to_dict()}")
    tt["destete_post"] = ((tt.mamando >= tt.edadq_m)
                          & (tt.mamando <= tt.edadq_m + 3)).astype(float)
    pre = d.dropna(subset=["mamando"]).copy()
    pre = pre[pre.edadq_m.between(5, 18)]
    pre = pre[pre.mamando >= pre.edadq_m - 4]  # mamaba 4 meses antes
    pre["destete_pre"] = pre.mamando.between(
        pre.edadq_m - 4, pre.edadq_m - 1).astype(float)
    for lab, base, y in [("ventana post (0-3m tras 27-F)", tt,
                          "destete_post"),
                         ("ventana placebo (meses -4 a -1)", pre,
                          "destete_pre")]:
        base = base.dropna(subset=["w", "estrato"])
        base = base[base.w > 0].copy()
        base["est"] = base.estrato.astype(int).astype(str)
        rhs = " + ".join(["EQ", "C(edadq_m)"] + xt(base, X_PRE))
        r = smf.wls(f"{y} ~ {rhs}", data=base, weights=base.w).fit(
            cov_type="cluster", cov_kwds={"groups": base.est})
        log(f"  {lab}: media {base[y].mean():.3f}; "
            f"EQ {cel(r, 'EQ')}; N={int(r.nobs)}")


def test_e(d):
    log("\n## E. Corte escolar del 31 de marzo (nacidos feb-may 2006)")
    log("Misma capacidad de memoria, distinto ano de entrada al colegio. "
        "Si el brazo derecho fuera entrada escolar, saltaria aqui.")
    tt = d.copy()
    tt["by"], tt["bm"] = tt.birth_ym // 12, tt.birth_ym % 12 + 1
    tt = tt[(tt.by == 2006) & tt.bm.between(2, 5)].copy()
    tt["temprano"] = (tt.bm <= 3).astype(float)   # entra un ano antes
    tt = tt.dropna(subset=["z_phq4", "w", "estrato", "cohorte"])
    tt = tt[tt.w > 0].copy()
    tt["est"] = tt.estrato.astype(int).astype(str)
    tt["ExT"] = tt.EQ * tt.temprano
    rhs = " + ".join(["ExT", "EQ", "temprano"] + xt(tt, X_PRE)
                     + xt(tt, X_POST))
    rhs_fe = " + ".join(["ExT", "temprano", "C(est)"] + xt(tt, X_PRE)
                        + xt(tt, X_POST))
    for y in ("z_phq4", "gad2_bin", "z_tvip"):
        ty = tt.dropna(subset=[y])
        r = smf.wls(f"{y} ~ {rhs}", data=ty, weights=ty.w).fit(
            cov_type="cluster", cov_kwds={"groups": ty.est})
        rf = smf.wls(f"{y} ~ {rhs_fe}", data=ty, weights=ty.w).fit(
            cov_type="cluster", cov_kwds={"groups": ty.est})
        log(f"  {y:8}: EQ x entrada temprana {cel(r, 'ExT')}; "
            f"EQ {cel(r, 'EQ')}; N={int(r.nobs)}")
        log(f"           con EF de estrato: {cel(rf, 'ExT')}")
    log(f"  (nacidos feb-mar: {int((tt.temprano == 1).sum())}; "
        f"abr-may: {int((tt.temprano == 0).sum())})")


def main():
    d = carga()
    log("# Tests de mecanismos — exploracion "
        "(scripts/17_mecanismos.py)")
    log(f"Muestra base: {len(d)}; con modulo 2012: "
        f"{d.angustia12.notna().sum()}; con TVIP 2024: "
        f"{d.z_tvip.notna().sum()}")
    test_a(d)
    test_b(d)
    test_c(d)
    test_d(d)
    test_e(d)
    Path("reports").mkdir(exist_ok=True)
    Path("reports/mecanismos_tests.md").write_text(
        "\n".join(OUT) + "\n", encoding="utf-8")
    log("\n-> reports/mecanismos_tests.md")


if __name__ == "__main__":
    main()
