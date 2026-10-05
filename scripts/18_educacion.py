#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exploración: ¿la edad al terremoto mueve la trayectoria escolar y lo que el
adolescente espera estudiar y trabajar? (ola 2024, 15-18 años; todavía no
hay resultados universitarios observados).

Outcomes del adolescente (Base adolescentes): asistencia (e1), notas del
año pasado (e3_asiste, tramo convertido a su punto medio en escala 1-7),
cómo le va (e2_asiste), cuánto le gusta el colegio (e5), expectativa de
completar la universidad o un postgrado (e7 = 6, 7) y no saber qué nivel
alcanzará (e7 = 88). Del cuidador (Base responsable principal): la
ocupación que espera para el adolescente (cn7_cod), resumida en una
ocupación profesional (códigos 2xx).

Misma especificación que la columna 3 de la Table 3.
Salida: reports/educacion_tests.md
Uso:    python3 scripts/18_educacion.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p15", HERE / "15_paper_estimaciones.py")
p15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p15)
num, fit, stars, zg = p15.num, p15.fit, p15.stars, p15.zg
OUT = []

NOTA_MEDIA = {1: 3.7, 2: 4.2, 3: 4.7, 4: 5.2, 5: 5.7, 6: 6.2, 7: 6.75}


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def carga():
    d, _, _ = p15.load_data()
    a, _ = pyreadstat.read_dta(
        "data/interim/2024/Base adolescentes Stata.dta",
        usecols=["folio", "e1", "e2_asiste", "e3_asiste", "e5", "e7"])
    a = a.apply(num)
    a["folio"] = a.folio.astype("int64")
    a = a.drop_duplicates("folio")
    a["asiste"] = np.where(a.e1.isin([1, 2]), (a.e1 == 1).astype(float),
                           np.nan)
    a["nota"] = a.e3_asiste.map(NOTA_MEDIA)
    a["z_le_va"] = zg(a.e2_asiste.where(a.e2_asiste.between(1, 5)))
    a["z_gusta"] = zg(a.e5.where(a.e5.between(1, 5)))
    a["univ"] = np.where(a.e7.between(1, 7),
                         a.e7.isin([6, 7]).astype(float), np.nan)
    a["no_sabe"] = np.where(a.e7.between(1, 7) | (a.e7 == 88),
                            (a.e7 == 88).astype(float), np.nan)
    r, _ = pyreadstat.read_dta(
        "data/interim/2024/Base responsable principal Stata.dta",
        usecols=["folio", "cn7_cod"])
    r = r.apply(num)
    r["folio"] = r.folio.astype("int64")
    r = r.dropna(subset=["cn7_cod"])
    distintos = r.groupby("folio").cn7_cod.nunique()
    log(f"cn7_cod: {len(r)} filas, {r.folio.nunique()} folios; folios con "
        f"más de un código: {(distintos > 1).sum()}")
    r = r.drop_duplicates("folio")
    c = r.cn7_cod
    r["prof_cuid"] = np.where(c.between(110, 799),
                              c.between(200, 299).astype(float), np.nan)
    return (d.merge(a[["folio", "asiste", "nota", "z_le_va", "z_gusta",
                       "univ", "no_sabe"]], on="folio", how="left")
             .merge(r[["folio", "prof_cuid"]], on="folio", how="left"))


def main():
    d = carga()
    outs = [("asiste", "asiste a un establecimiento (0/1)"),
            ("nota", "notas del año pasado (escala 1-7)"),
            ("z_le_va", "cómo le va en el colegio (z)"),
            ("z_gusta", "cuánto le gusta el colegio (z)"),
            ("univ", "espera completar universidad o postgrado (0/1)"),
            ("no_sabe", "no sabe qué nivel educativo alcanzará (0/1)"),
            ("prof_cuid", "el cuidador espera una ocupación profesional "
                          "(0/1)"),
            ("z_tvip", None), ("z_phq4", None)]
    t, _ = pyreadstat.read_dta(
        "data/interim/2024/Base evaluaciones Stata.dta",
        usecols=["folio", "tvip_pst_hispano"])
    t["folio"] = num(t.folio).astype("int64")
    t = t.groupby("folio", as_index=False).first()
    d = d.merge(t, on="folio", how="left")
    d["z_tvip"] = zg(d.tvip_pst_hispano)
    log("\n# Escuela, expectativas y carrera por edad al terremoto "
        "(scripts/18_educacion.py)")
    log("Especificación de la columna 3 de la Table 3; coeficientes "
        "relativos a los expuestos a 0-11 meses.")
    for grupo, sel in (("Todos", None), ("Chicas", lambda x: x.mujer == 1)):
        log(f"\n## {grupo}")
        for y, lab in outs:
            if lab is None:
                lab = {"z_tvip": "referencia: vocabulario TVIP (z)",
                       "z_phq4": "referencia: síntomas PHQ-4 (z)"}[y]
            r = fit(d, y, 3, sample=sel)
            dd = d if sel is None else d[sel(d)]
            media = dd[y].mean()
            b1, b2, b3 = (r["b"][k] for k in ("12-23m", "24-35m", "36-59m"))
            ct = r["contr"]
            log(f"- {lab}: media {media:.3f} | edad 1 {b1[0]:+.3f}"
                f"{stars(b1[2])} | edad 2 {b2[0]:+.3f}{stars(b2[2])} "
                f"(p={b2[2]:.3f}) | 3-4 {b3[0]:+.3f}{stars(b3[2])} | "
                f"3-4 menos 2 {ct[0]:+.3f}{stars(ct[2])} (p={ct[2]:.3f}) "
                f"| N={r['n']}")
    Path("reports/educacion_tests.md").write_text("\n".join(OUT) + "\n",
                                                  encoding="utf-8")
    log("\n-> reports/educacion_tests.md")


if __name__ == "__main__":
    main()
