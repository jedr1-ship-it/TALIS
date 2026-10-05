#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Las chicas expuestas con tres o cuatro años: ¿por qué también salen peor
que las expuestas con dos?

  A. Perfil en 2024 por sexo (PHQ-4, GAD-2, PHQ-2), con los expuestos con
     dos años como referencia.
  B. Placebos al nacer para el contraste 3-4 frente a 2 en las chicas.
  C. La reacción inmediata: CBCL 1.5-5 de la ola 2010, aplicado entre uno
     y nueve meses después del 27-F (mediana: tres), por sexo. Los bebés
     no tienen CBCL en 2010 (se aplica desde los 18 meses), así que aquí
     la comparación es 3-4 frente a 2 y 1 frente a 2.
  D. Canales candidatos en las chicas: daño a la vivienda (h3 2012),
     angustia de la madre tras el terremoto (h4 2012) y entrada a
     prekínder en marzo de 2010.

Misma especificación que la columna 3 de la Table 3 para 2024; para 2010,
controles previos al terremoto, edad en la evaluación y efectos fijos del
mes de evaluación (meses desde el 27-F).

Salida: reports/tres_cuatro.md y reports/tres_cuatro_coefs.json
Uso:    python3 scripts/21_tres_cuatro.py
"""
import importlib.util
import json
import warnings
from pathlib import Path

import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p15 = modulo("p15", "15_paper_estimaciones.py")
p17 = modulo("p17", "17_mecanismos.py")
num, stars, xt, zg = p15.num, p15.stars, p15.xt, p15.zg
X_PRE, X_POST = p15.X_PRE, p15.X_POST
BINS = ["0-11m", "12-23m", "24-35m", "36-59m"]
NOMBRE = {"0-11m": "bebés", "12-23m": "1 año", "24-35m": "2 años",
          "36-59m": "3-4 años"}
CHICAS = lambda x: x.mujer == 1
CHICOS = lambda x: x.mujer == 0
OUT, COEF = [], {}


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(t):
    return f"{t[0]:+.3f}{stars(t[2])} (ee {t[1]:.3f}, p={t[2]:.3f})"


def reg(d0, y, sample=None, ref="24-35m", col=3, dose="EQ", extra=None,
        fe=None, bins=None):
    """Ecuación (1) con `ref` como grupo omitido. Devuelve, para cada
    grupo de edad, su diferencia con `ref` (zona afectada menos no
    afectada) y el N."""
    d = d0 if sample is None else d0[sample(d0)]
    d = d.dropna(subset=[y, dose, "estrato", "w", "cohorte", "bin"])
    d = d[d.w > 0].copy()
    if bins:
        d = d[d.bin.isin(bins)].copy()
    d["est"] = d.estrato.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    labs = [b for b in BINS if b in set(d.bin) and b != ref]
    ivs = []
    for b in labs:
        v = "J" + b.split("-")[0]
        d[v] = (d.bin == b).astype(float) * num(d[dose])
        ivs.append(v)
    rhs = ivs + [f"C(bin, Treatment('{ref}'))", "C(est)", "C(coh)"]
    if col >= 2:
        rhs += xt(d, X_PRE)
    if col >= 3:
        rhs += xt(d, X_POST)
    if extra:
        rhs += xt(d, extra)
    if fe:
        rhs += [f"C({v})" for v in fe]
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d.est})
    out = {b: (float(r.params[v]), float(r.bse[v]), float(r.pvalues[v]))
           for b, v in zip(labs, ivs)}
    return out, int(r.nobs), r, dict(zip(labs, ivs))


def carga():
    d = p17.carga()
    cols = ["folio", "edad_meses", "cbcl1_pb_1", "cbcl1_pb_2",
            "cbcl1_pb_3", "cbcl1_pb_4", "cbcl1_pb_5", "cbcl1_pb_i",
            "cbcl1_pb_e", "cbcl1_pb_t"]
    e10, _ = pyreadstat.read_dta("data/interim/2010/Evaluaciones_2010.dta",
                                 usecols=cols)
    e10["folio"] = num(e10.folio).astype("int64")
    e10 = e10.drop_duplicates("folio").rename(
        columns={c: f"{c}_10" for c in cols if c != "folio"})
    d = d.merge(e10, on="folio", how="left")
    d["edad10"] = num(d.edad_meses_10)
    d["mp"] = (d.edad10 - d.edadq_m).astype("Int64").astype(str)
    for c in ("1", "2", "3", "4", "5", "i", "e", "t"):
        d[f"z_c10_{c}"] = zg(d[f"cbcl1_pb_{c}_10"])
    return d


SALUD = [("z_phq4", "PHQ-4 (DE)"), ("gad2_bin", "ansiedad, GAD-2 positivo"),
         ("phq2_bin", "depresión, PHQ-2 positivo")]
CBCL10 = [("z_c10_2", "ansiedad/depresión"),
          ("z_c10_1", "reactividad emocional"),
          ("z_c10_5", "problemas de sueño"),
          ("z_c10_3", "quejas somáticas"),
          ("z_c10_4", "retraimiento"),
          ("z_c10_i", "internalización (total)"),
          ("z_c10_e", "externalización (total)")]


def seccion_a(d):
    log("\n## A. 2024: diferencia con los expuestos con dos años")
    for g, s in (("chicas", CHICAS), ("chicos", CHICOS), ("todos", None)):
        for y, lab in SALUD:
            b, n, _, _ = reg(d, y, sample=s)
            t = reg(d, y, sample=s, ref="0-11m")[0]["36-59m"]
            log(f"- {g}, {lab}: bebés {fmt(b['0-11m'])} | 1 año "
                f"{fmt(b['12-23m'])} | 3-4 {fmt(b['36-59m'])} | "
                f"3-4 frente a bebés {fmt(t)} | N={n}")
            COEF[f"A|{g}|{y}"] = {k: v for k, v in b.items()}
            COEF[f"A|{g}|{y}"]["n"] = n


def seccion_b(d):
    log("\n## B. Placebos al nacer, chicas: 3-4 frente a 2 (y bebés "
        "frente a 2)")
    for y, lab, col in (("z_peso", "peso al nacer (z)", 2),
                        ("z_talla", "talla al nacer (z)", 2),
                        ("z_gest", "semanas de gestación (z)", 2),
                        ("prematuro", "prematuro (0/1)", 2),
                        ("educ_madre10", "escolaridad de la madre", 1),
                        ("edad_madre10", "edad de la madre", 1)):
        b, n, _, _ = reg(d, y, sample=CHICAS, col=col)
        log(f"- {lab}: 3-4 {fmt(b['36-59m'])} | bebés {fmt(b['0-11m'])}"
            f" | N={n}")
        COEF[f"B|{y}"] = {**b, "n": n}
    log("\nPHQ-4 de las chicas controlando por la dotación al nacer "
        "(peso, gestación, prematuro):")
    for extra, lab in ((None, "sin control"),
                       (["z_peso", "z_gest", "prematuro"], "con control")):
        b, n, _, _ = reg(d, "z_phq4", sample=CHICAS, extra=extra)
        log(f"- {lab}: bebés {fmt(b['0-11m'])} | 3-4 {fmt(b['36-59m'])}"
            f" | N={n}")
        COEF[f"B|dotacion|{lab}"] = {**b, "n": n}


def seccion_c(d):
    log("\n## C. 2010, uno a nueve meses después del 27-F (CBCL 1.5-5 "
        "reportado por la madre)")
    tt = d[d.bin != "0-11m"]
    mp = num(tt.edad10 - tt.edadq_m)
    log(f"Meses entre el 27-F y la evaluación: mediana {mp.median():.0f}, "
        f"rango {mp.min():.0f}-{mp.max():.0f}")
    for g, s in (("chicas", CHICAS), ("chicos", CHICOS), ("todos", None)):
        log(f"\n### {g}")
        for y, lab in CBCL10:
            b, n, _, _ = reg(tt, y, sample=s, col=2, extra=["edad10"],
                             fe=["mp"], bins=BINS[1:])
            log(f"- {lab}: 3-4 frente a 2 {fmt(b['36-59m'])} | 1 frente "
                f"a 2 {fmt(b['12-23m'])} | N={n}")
            COEF[f"C|{g}|{y}"] = {**b, "n": n}


def seccion_d(d):
    log("\n## D. Canales candidatos, chicas, PHQ-4 2024, 3-4 frente a 2")
    # D1. daño a la vivienda, dentro de la zona afectada
    tt = d[(d.EQ == 1) & d.dano_mayor.notna()]
    b, n, _, _ = reg(tt, "z_phq4", sample=CHICAS, dose="dano_mayor",
                     extra=["dano_mayor"])
    log(f"- D1 vivienda destruida o con daño mayor (zona afectada): "
        f"gradiente del daño, 3-4 frente a 2 {fmt(b['36-59m'])}; "
        f"bebés frente a 2 {fmt(b['0-11m'])}; N={n}")
    COEF["D|dano"] = {**b, "n": n}
    # D2. angustia de la madre tras el terremoto
    for k, lab in ((1.0, "con angustia"), (0.0, "sin angustia")):
        s = lambda x, k=k: (x.mujer == 1) & (x.angustia12 == k)
        b, n, _, _ = reg(d, "z_phq4", sample=s)
        log(f"- D2 madre {lab}: 3-4 frente a 2 {fmt(b['36-59m'])}; "
            f"bebés frente a 2 {fmt(b['0-11m'])}; N={n}")
        COEF[f"D|angustia{int(k)}"] = {**b, "n": n}
    # D3. entrada a prekínder en marzo de 2010: nacidas antes del 1 de
    # abril de 2006 frente a nacidas después, comparado con pares de
    # trimestres sin corte (si es la edad y no el corte, también saltan)
    tt = d.copy()
    tt["mabs"] = (tt.birth_ym // 12 - 2006) * 12 + tt.birth_ym % 12 + 1
    pares = [("ene-mar | abr-jun 2006, corte de prekínder", (1, 3), (4, 6)),
             ("feb-mar | abr-may 2006, corte, ventana de dos meses",
              (2, 3), (4, 5)),
             ("mar | abr 2006, corte, ventana de un mes", (3, 3), (4, 4)),
             ("abr-jun | jul-sep 2006, sin corte", (4, 6), (7, 9)),
             ("jul-sep | oct-dic 2006, sin corte", (7, 9), (10, 12)),
             ("oct-dic 2006 | ene-mar 2007, sin corte", (10, 12), (13, 15))]

    def corte(sub, y, a, b, ctr=True):
        t = sub[sub.mabs.between(a[0], b[1])].dropna(
            subset=["w", "estrato", y]).copy()
        t = t[t.w > 0]
        t["est"] = t.estrato.astype(int).astype(str)
        t["temprano"] = t.mabs.between(*a).astype(float)
        t["ExT"] = t.EQ * t.temprano
        c = (xt(t, X_PRE) + xt(t, X_POST)) if ctr else []
        r = smf.wls(f"{y} ~ {' + '.join(['ExT', 'temprano', 'C(est)'] + c)}",
                    data=t, weights=t.w).fit(cov_type="cluster",
                                             cov_kwds={"groups": t.est})
        return (r.params["ExT"], r.bse["ExT"], r.pvalues["ExT"]), int(r.nobs)

    for g, s in (("chicas", CHICAS), ("chicos", CHICOS)):
        for lab, a, b in pares:
            t, n = corte(tt[s(tt)], "z_phq4", a, b)
            log(f"- D3 {g}, {lab}: zona afectada x nacida antes {fmt(t)}; "
                f"N={n}")
            COEF[f"D|escuela|{g}|{lab}"] = t
    for y, ctr in (("z_peso", True), ("z_talla", True), ("z_gest", True),
                   ("educ_madre10", False), ("edad_madre10", False)):
        t, n = corte(tt[CHICAS(tt)], y, (1, 3), (4, 6), ctr=ctr)
        log(f"- D3 placebo al nacer, chicas, ene-mar | abr-jun 2006, {y}: "
            f"{fmt(t)}; N={n}")


def seccion_e(d):
    log("\n## E. Perfil fino (bins de 6 meses, ref. 6-11 meses), PHQ-4")
    for g, s in (("chicas", CHICAS), ("chicos", CHICOS)):
        prof, n = p17.fino(d[s(d)], "z_phq4")
        log(f"- {g}: " + "; ".join(f"{k} {v[0]:+.3f} (p={v[2]:.3f})"
                                    for k, v in prof.items()) + f"; N={n}")
        COEF[f"E|{g}"] = {k: v for k, v in prof.items()}
        COEF[f"E|{g}"]["n"] = n


def main():
    d = carga()
    log("# Las chicas expuestas con tres o cuatro años "
        "(scripts/21_tres_cuatro.py)")
    log("Signo: positivo = más síntomas que el grupo de referencia.")
    seccion_a(d)
    seccion_b(d)
    seccion_c(d)
    seccion_d(d)
    seccion_e(d)
    Path("reports/tres_cuatro.md").write_text("\n".join(OUT) + "\n",
                                              encoding="utf-8")
    Path("reports/tres_cuatro_coefs.json").write_text(
        json.dumps({k: v for k, v in COEF.items()}, indent=1,
                   ensure_ascii=False, default=float), encoding="utf-8")
    log("\n-> reports/tres_cuatro.md, reports/tres_cuatro_coefs.json")


if __name__ == "__main__":
    main()
