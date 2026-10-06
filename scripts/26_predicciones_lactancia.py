#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contraste de las predicciones P2 a P7 de reports/marco_lactancia.md, fijadas
antes de estimarlas (commit 0799302). Muestra: bebés de 6-11 meses el 27-F.

  P2  Lactancia medida en 2010, más cerca del evento.
  P3  Mayor efecto si la madre quedó angustiada (h4) o la vivienda dañada (h3).
  P4  Mayor efecto en niñas (diferencia formal).
  P5  Fenotipo internalizante: CBCL externalizante 2024 nulo.
  P6  Señal temprana en 2010: ASQ:SE a los 12 meses y Battelle personal-social.
  P7  Mayor efecto en bebés de 6-8 meses que en los de 9-11.

Salida: reports/predicciones_lactancia.md
Uso:    python3 scripts/26_predicciones_lactancia.py
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
    "p25", HERE / "25_lactancia_robustez.py")
p25 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p25)
p15 = p25.p15
num, stars, xt = p15.num, p15.stars, p15.xt
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(t):
    return f"{t[0]:+.3f}{stars(t[2])} (ee {t[1]:.3f}, p={t[2]:.3f})"


def reg(bb, y, terms, post=True, extra=None):
    """WLS con EF de comuna y cohorte, controles previos (y de 2012 si
    post=True), errores agrupados por comuna. Devuelve los `terms`."""
    bb = bb.dropna(subset=[y] + [t for t in terms if ":" not in t]).copy()
    rhs = list(terms) + ["C(est)", "C(coh)"] + xt(bb, p15.X_PRE)
    if post:
        rhs += xt(bb, p15.X_POST)
    if extra:
        rhs += extra
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=bb, weights=bb.w).fit(
        cov_type="cluster", cov_kwds={"groups": bb.est})
    out = {t: (float(r.params[t]), float(r.bse[t]), float(r.pvalues[t]))
           for t in terms}
    return out, int(r.nobs), r


def carga():
    d = p25.carga()
    b = p25.bebes(d)
    b["ExP"] = b.EQ * b.pecho
    # 2010: lactancia reportada cerca del evento y medidas socioemocionales
    e10, _ = pyreadstat.read_dta("data/interim/2010/Entrevistada_2010.dta",
                                 usecols=["folio", "g26", "g28"],
                                 encoding="latin1")
    e10["folio"] = num(e10.folio).astype("int64")
    # la edad en la evaluación de 2010 (edad10) ya viene de scripts/21
    ev, _ = pyreadstat.read_dta("data/interim/2010/Evaluaciones_2010.dta",
                                usecols=["folio", "asq_pb_12m", "asq_int_12m",
                                         "batelle_pt_per"])
    ev["folio"] = num(ev.folio).astype("int64")
    b = (b.merge(e10.drop_duplicates("folio"), on="folio", how="left")
          .merge(ev.drop_duplicates("folio"), on="folio", how="left"))
    g26, g28 = num(b.g26), num(b.g28)
    b["pecho10"] = np.where(g26 == 2, 0.0,
                            np.where((g26 == 1) & g28.lt(99),
                                     (g28 >= b.edadq_m).astype(float),
                                     np.nan))
    b["mp"] = (num(b.edad10) - b.edadq_m).round().astype("Int64").astype(str)
    s = num(b.asq_pb_12m)
    b["z_asq"] = (s - s.mean()) / s.std()
    b["asq_riesgo"] = num(b.asq_int_12m).where(num(b.asq_int_12m).isin([0,
                                                                        1]))
    s = -num(b.batelle_pt_per)
    b["z_battelle_ps"] = (s - s.mean()) / s.std()
    E, _ = pyreadstat.read_dta("data/interim/2024/Base evaluaciones Stata.dta",
                               usecols=["folio", "cbcl2_pt_inter_e",
                                        "cbcl2_pt_inter_i"])
    E["folio"] = num(E.folio).astype("int64")
    E = E.drop_duplicates("folio")
    b = b.merge(E, on="folio", how="left")
    for c, k in (("cbcl2_pt_inter_e", "z_cbcl_ext"),
                 ("cbcl2_pt_inter_i", "z_cbcl_int")):
        s = num(b[c])
        b[k] = (s - s.mean()) / s.std()
    return b


def main():
    b = carga()
    log("# Predicciones de la lactancia, contrastadas "
        "(scripts/26_predicciones_lactancia.py)")
    log("Predicciones fijadas en reports/marco_lactancia.md, commit 0799302.")
    base, n, _ = reg(b, "z_phq4", ["ExP", "pecho"])
    log(f"\nReferencia, PHQ-4: {fmt(base['ExP'])}; N={n}")

    log("\n## P2. Lactancia medida en 2010")
    ok = b.pecho10.notna() & b.pecho.notna()
    log(f"Coinciden 2010 y 2012 en {100 * (b.pecho10[ok] == b.pecho[ok]).mean():.0f}% "
        f"de {ok.sum()} bebés; tomaban pecho según 2010: "
        f"{b.pecho10.mean():.2f}")
    b["ExP10"] = b.EQ * b.pecho10
    r, n, _ = reg(b, "z_phq4", ["ExP10", "pecho10"])
    log(f"- PHQ-4 con la medida de 2010: {fmt(r['ExP10'])}; N={n}")

    log("\n## P3. Mayor efecto si la madre quedó angustiada o la vivienda "
        "dañada")
    for v, lab in (("angustia12", "madre con angustia tras el terremoto "
                                  "(h4)"),):
        bb = b.dropna(subset=[v]).copy()
        bb["ExPxV"] = bb.ExP * bb[v]
        bb["ExV"] = bb.EQ * bb[v]
        bb["PxV"] = bb.pecho * bb[v]
        r, n, _ = reg(bb, "z_phq4", ["ExP", "ExPxV", "pecho", "ExV", "PxV",
                                     v])
        log(f"- {lab}: zona x pecho sin angustia {fmt(r['ExP'])}; adicional "
            f"con angustia {fmt(r['ExPxV'])}; N={n}; "
            f"con angustia {bb[v].mean():.2f}")
        for k, sel in (("con", 1.0), ("sin", 0.0)):
            r2, n2, _ = reg(bb[bb[v] == sel], "z_phq4", ["ExP", "pecho"])
            log(f"  {k} angustia: {fmt(r2['ExP'])}; N={n2}")
    a = b[(b.EQ == 1)].dropna(subset=["dano_mayor"]).copy()
    a["PxD"] = a.pecho * a.dano_mayor
    r, n, _ = reg(a, "z_phq4", ["PxD", "pecho", "dano_mayor"])
    log(f"- dentro de la zona afectada, tomaba pecho x vivienda destruida o "
        f"con daño mayor: {fmt(r['PxD'])}; N={n}; con daño "
        f"{a.dano_mayor.mean():.2f}")

    log("\n## P4. Mayor efecto en niñas")
    b["ExPxM"] = b.ExP * b.mujer
    b["ExM"] = b.EQ * b.mujer
    b["PxM"] = b.pecho * b.mujer
    r, n, _ = reg(b, "z_phq4", ["ExP", "ExPxM", "pecho", "ExM", "PxM"])
    log(f"- niños: {fmt(r['ExP'])}; diferencia niñas menos niños: "
        f"{fmt(r['ExPxM'])}; N={n}")
    rr = r["ExP"][0] + r["ExPxM"][0]
    log(f"  niñas (suma): {rr:+.3f}")
    for y, lab in (("gad2_bin", "GAD-2"), ("phq2_bin", "PHQ-2")):
        r, n, _ = reg(b, y, ["ExP", "ExPxM", "pecho", "ExM", "PxM"])
        log(f"- {lab}: niños {fmt(r['ExP'])}; diferencia niñas menos "
            f"niños {fmt(r['ExPxM'])}")

    log("\n## P5. Fenotipo internalizante, no externalizante")
    for y, lab in (("z_cbcl_int", "CBCL internalizante 2024 (cuidador)"),
                   ("z_cbcl_ext", "CBCL externalizante 2024 (cuidador)"),
                   ("gad2_bin", "ansiedad, GAD-2 positivo"),
                   ("phq2_bin", "depresión, PHQ-2 positivo")):
        r, n, _ = reg(b, y, ["ExP", "pecho"])
        log(f"- {lab}: {fmt(r['ExP'])}; N={n}")

    log("\n## P6. Señal temprana en 2010 (1 a 9 meses después del 27-F)")
    for y, lab in (("z_asq", "ASQ:SE 12 meses, problemas socioemocionales "
                             "(z)"),
                   ("asq_riesgo", "ASQ:SE sobre el punto de corte (0/1)"),
                   ("z_battelle_ps", "Battelle personal-social, invertido "
                                     "(z)")):
        bb = b.dropna(subset=[y, "edad10"]).copy()
        r, n, _ = reg(bb, y, ["ExP", "pecho"], post=False,
                      extra=["edad10", "C(mp)"])
        log(f"- {lab}: {fmt(r['ExP'])}; N={n}")

    log("\n## P7. Mayor efecto cuanto más depende el bebé de la leche")
    b["joven"] = (b.edadq_m <= 8).astype(float)
    b["ExPxJ"] = b.ExP * b.joven
    b["ExJ"] = b.EQ * b.joven
    b["PxJ"] = b.pecho * b.joven
    r, n, _ = reg(b, "z_phq4", ["ExP", "ExPxJ", "pecho", "ExJ", "PxJ"])
    log(f"- 9-11 meses: {fmt(r['ExP'])}; adicional 6-8 meses: "
        f"{fmt(r['ExPxJ'])}; N={n}; de 6-8 meses {b.joven.mean():.2f}")
    for k, sel in (("6-8 meses", 1.0), ("9-11 meses", 0.0)):
        r2, n2, _ = reg(b[b.joven == sel], "z_phq4", ["ExP", "pecho"])
        log(f"  {k}: {fmt(r2['ExP'])}; N={n2}; tomaban pecho "
            f"{b[b.joven == sel].pecho.mean():.2f}")
    Path("reports/predicciones_lactancia.md").write_text(
        "\n".join(OUT) + "\n", encoding="utf-8")
    log("\n-> reports/predicciones_lactancia.md")


if __name__ == "__main__":
    main()
