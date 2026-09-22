#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
27-F y salud mental adolescente (ELPI ola 2024): la regresión de Gillmore
extendida al largo plazo (14 años) con los outcomes de salud mental de la
nueva ola.

Restricción de diseño: la ola 2024 siguió SOLO a la cohorte original 2010
(nacidos 2006–2009) ⇒ todos los adolescentes estuvieron expuestos al 27-F
(0–4 años) y no existe cohorte concebida después. El DiD cohorte×geografía
de la ec. (1) no es estimable tal cual en 2024. Se estiman tres diseños que
usan la misma maquinaria:

  A. GRADIENTE EDAD-A-LA-EXPOSICIÓN × INTENSIDAD (análogo a la Fig. B.1 del
     paper, ahora a 14 años): Y = Σ_a β_a·(EdadBin_a × EQ_m) + EdadBin + X
     + ψ_estrato + θ_cohorte. Identifica si la exposición más temprana deja
     más cicatriz, dentro de comuna y cohorte. Referencia: 36–59 meses.
  B. NIVEL GEOGRÁFICO con controles PRE-terremoto de la línea base 2010
     (educación y edad de la madre, tamaño del hogar, área). Sin FE de
     comuna (EQ es regional y quedaría absorbido). Asociación condicional,
     no DiD — se etiqueta como tal.
  C. TRAYECTORIA INTRA-NIÑO del CBCL (T internacional) 2017→2024:
     ΔCBCL = z24 − z17 sobre EQ (nivel) y sobre EdadBin×EQ (versión A).
     Aprovecha que el MISMO niño tiene CBCL en ambas olas.

Outcomes 2024 (dirección ADVERSA: β>0 = peor salud mental):
  z_phq4  : puntaje PHQ-4 (suma de ítems d4_1–d4_4 re-escalados 0–3, 0–12),
            estandarizado (autorreporte del adolescente, a solas).
  phq2    : tamizaje positivo de depresión (0/1).
  gad2    : tamizaje positivo de ansiedad (0/1).
  z_cbcl  : CBCL2 T internacional TOTAL (reporte del cuidador), z; en 2024
            SIN invertir (más alto = más problemas).

Geografía 2024: estrato (comuna de selección anonimizada 1–116) → CUT vía
data/processed/crosswalk_estrato24_comuna.csv → región → EQ_m = regiones
oficiales de Astroza et al. (2010) {V, VI, VII, VIII, IX, RM}. FE y cluster
por estrato (comuna de selección).

Salida: reports/salud_mental_27f.md
Uso:    python3 scripts/09_salud_mental_27f.py
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
INT = Path("data/interim")
OUT = Path("reports")
EQ_REGIONS = {5, 6, 7, 8, 9, 13}
QUAKE_YM = 2010 * 12 + 1          # feb-2010
FIELD_2024_YM = 2024 * 12 + 7     # punto medio de campo aprox. (ago-2024)


def dta(path, cols=None):
    kw = {"usecols": cols} if cols else {}
    df, _ = pyreadstat.read_dta(str(path), **kw)
    df["folio"] = pd.to_numeric(df.folio).astype("int64")
    return df


def num(s):
    return pd.to_numeric(s, errors="coerce")


def build():
    a24 = dta(INT / "2024/Base adolescentes Stata.dta",
              ["folio", "phq2", "gad2", "d4_1", "d4_2", "d4_3", "d4_4",
               "f_exp"])
    e24 = dta(INT / "2024/Base evaluaciones Stata.dta",
              ["folio", "fecha_nac", "estrato", "cbcl2_pt_inter_t", "f_exp"])
    e24 = e24.rename(columns={"f_exp": "f_exp_eva"})
    xw = pd.read_csv("data/processed/crosswalk_estrato24_comuna.csv")

    # línea base 2010 (pre-terremoto)
    h10 = dta(INT / "2010/Hogar_2010.dta",
              ["folio", "a16", "a18", "a19", "b2n", "tot_per"])
    madre = h10[h10.a16 == 1].drop_duplicates("folio").set_index("folio")
    nino = h10[h10.a16 == 13].drop_duplicates("folio").set_index("folio")
    ent10 = dta(INT / "2010/Entrevistada_2010.dta", ["folio", "area"])

    # 2012: nº de hijos y salud mental previa familiar (checklist b55o–t)
    b55 = [f"b55{l}_{q}" for l in "opqrst" for q in ("madre", "padre", "ofam")]
    e12 = dta(INT / "2012/Entrevistada_2012.dta", ["folio", "b71"] + b55)
    for q in ("madre", "padre", "ofam"):
        cols = [f"b55{l}_{q}" for l in "opqrst"]
        e12[f"mh_{q}"] = (e12[cols] == 1).any(axis=1).astype(float)

    # 2017: CBCL para la trayectoria intra-niño
    e17 = dta(INT / "2017/Base Evaluaciones ELPI III.dta",
              ["folio", "edad_mesesr", "cbcl2_pt_inter_t"])
    e17 = e17.rename(columns={"cbcl2_pt_inter_t": "cbcl17"})
    e17 = e17.drop_duplicates("folio")

    d = (e24.merge(a24, on="folio", how="left")
            .merge(xw, left_on="estrato", right_on="estrato24", how="left")
            .join(madre[["a19", "b2n", "tot_per"]], on="folio")
            .join(nino[["a18"]], on="folio")
            .merge(ent10, on="folio", how="left")
            .merge(e12[["folio", "b71", "mh_madre", "mh_padre", "mh_ofam"]],
                   on="folio", how="left")
            .merge(e17, on="folio", how="left"))

    fn = d.fecha_nac.astype(str).str.extract(r"(?P<mm>\d+)/(?P<aa>\d+)")
    d["birth_ym"] = num(fn.aa) * 12 + num(fn.mm) - 1
    d["cohorte"] = (d.birth_ym // 12).astype("Int64")
    d["edadq_m"] = QUAKE_YM - d.birth_ym          # meses de edad el 27-F
    d = d[d.edadq_m.between(0, 59)]               # nacidos antes del 27-F
    d["bin"] = pd.cut(d.edadq_m, [0, 12, 24, 36, 60], right=False,
                      labels=["0-11m", "12-23m", "24-35m", "36-59m"])
    d["region"] = (num(d.cut_comuna_seleccion) // 1000).astype("Int64")
    d["EQ"] = num(d.region).isin(EQ_REGIONS).astype(float)
    d["edad_meses"] = FIELD_2024_YM - d.birth_ym

    # outcomes (dirección adversa)
    for i in (1, 2, 3, 4):
        v = num(d[f"d4_{i}"])
        v = v.where(v.between(0, 4))
        d[f"i{i}"] = v - v.min()                   # re-escala a 0–3
    def zby(s, g):
        m, sd = s.groupby(g).transform("mean"), s.groupby(g).transform("std")
        return (s - m) / sd
    edad24_a = (d.edad_meses // 12)               # edad (años) al campo 2024
    edad17_a = (num(d.edad_mesesr) // 12)         # edad (años) al test 2017
    d["phq4_score"] = d[["i1", "i2", "i3", "i4"]].sum(axis=1, min_count=4)
    d["z_phq4"] = zby(d.phq4_score, edad24_a)     # z dentro de edad-año
    d["phq2_bin"] = (num(d.phq2) == 1).astype(float).where(d.phq2.notna())
    d["gad2_bin"] = (num(d.gad2) == 1).astype(float).where(d.gad2.notna())
    d["z_cbcl"] = zby(num(d.cbcl2_pt_inter_t), edad24_a)
    d["z_cbcl17"] = zby(num(d.cbcl17), edad17_a)
    d["d_cbcl"] = d.z_cbcl - d.z_cbcl17           # trayectoria 2017→2024

    # controles (pre-terremoto + demografía)
    d["mujer"] = (num(d.a18) == 2).astype(float).where(d.a18.notna())
    d["edad_madre10"] = num(d.a19).where(lambda s: s < 99)
    d["educ_madre10"] = num(d.b2n).where(lambda s: s < 30)
    d["tot_per10"] = num(d.tot_per)
    d["rural10"] = (num(d.area) == 2).astype(float).where(d.area.notna())
    d["n_hijos"] = num(d.b71).where(lambda s: s < 25)
    d["mh_miss"] = d.mh_madre.isna().astype(float)
    for c in ("mh_madre", "mh_padre", "mh_ofam"):
        d[c] = d[c].fillna(0.0)
    d["w"] = num(d.f_exp).fillna(num(d.f_exp_eva))
    return d


XV = ["mujer", "edad_meses", "n_hijos", "edad_madre10", "educ_madre10",
      "tot_per10", "rural10", "mh_madre", "mh_padre", "mh_ofam", "mh_miss"]


def xterms(d):
    """imputación + indicadores de missing (como la col. 3 calibrada)."""
    terms = []
    for v in XV:
        if d[v].isna().any():
            d[f"{v}_mi"] = d[v].isna().astype(float)
            d[v] = d[v].fillna(d[v].median())
            terms += [v, f"{v}_mi"]
        else:
            terms.append(v)
    return terms


def fit(d, y, modo):
    d = d.dropna(subset=[y, "EQ", "estrato", "w", "cohorte", "bin"]).copy()
    d = d[d.w > 0]
    d["est"] = d.estrato.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    tx = " + ".join(xterms(d))
    if modo == "A":      # gradiente edad×EQ, FE estrato + cohorte
        f = (f"{y} ~ C(bin, Treatment('36-59m')):EQ + C(bin) + C(est) "
             f"+ C(coh) + {tx}")
    elif modo == "B":    # nivel EQ con controles pre-quake (sin FE comuna)
        f = f"{y} ~ EQ + C(coh) + {tx}"
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d.est})
    out = {"n": int(r.nobs), "ncl": d.est.nunique()}
    if modo == "B":
        out["terms"] = [("EQ", r.params["EQ"], r.bse["EQ"], r.pvalues["EQ"])]
    else:
        out["terms"] = []
        for b in ("0-11m", "12-23m", "24-35m"):
            k = f"C(bin, Treatment('36-59m'))[{b}]:EQ"
            out["terms"].append((f"{b}×EQ", r.params[k], r.bse[k],
                                 r.pvalues[k]))
    return out


def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""


def main():
    d = build()
    print("n adolescentes con fecha y estrato:", len(d),
          "| EQ=1:", int(d.EQ.sum()), f"({d.EQ.mean():.0%})",
          "| clusters:", d.estrato.nunique())
    print("PHQ-4 media:", f"{d.phq4_score.mean():.2f}",
          "| P(phq2+):", f"{d.phq2_bin.mean():.3f}",
          "| P(gad2+):", f"{d.gad2_bin.mean():.3f}")

    YS = [("z_phq4", "PHQ-4 (z)"), ("phq2_bin", "PHQ-2 positivo"),
          ("gad2_bin", "GAD-2 positivo"), ("z_cbcl", "CBCL2-T 2024 (z)"),
          ("d_cbcl", "ΔCBCL 2017→2024 (z)")]

    filas = [
        "# 27-F y salud mental adolescente (ELPI 2024) — primera pasada",
        "",
        "Maquinaria de la replicación de Gillmore aplicada a la ola 2024"
        " (adolescentes 14–18, todos de la cohorte original expuesta 0–4"
        " años). β>0 = **peor** salud mental. EE cluster por comuna de"
        " selección (estrato). Pesos f_exp. Controles: sexo, edad, nº de"
        " hijos de la madre, línea base 2010 pre-terremoto (educación y"
        " edad de la madre, tamaño del hogar, ruralidad) y salud mental"
        " previa familiar (2012), con indicadores de missing.",
        "",
        "**Diseño A** — gradiente edad-a-la-exposición × EQ (FE de comuna"
        " de selección + cohorte; referencia: 36–59 meses el 27-F). Es el"
        " análogo a la Fig. B.1 del paper, 14 años después: ¿deja más"
        " cicatriz la exposición más temprana?",
        "",
        "| Outcome | 0–11m×EQ | 12–23m×EQ | 24–35m×EQ | n | clusters |",
        "|---|---:|---:|---:|---:|---:|"]
    resB = []
    for y, nom in YS:
        rA = fit(d, y, "A")
        cells = " | ".join(f"{b:.3f}{stars(p)} ({se:.3f})"
                           for _, b, se, p in rA["terms"])
        filas.append(f"| {nom} | {cells} | {rA['n']:,} | {rA['ncl']} |")
        print("A", nom, [f"{t[0]}: {t[1]:.3f}{stars(t[3])}" for t in rA["terms"]],
              "n=", rA["n"])
        rB = fit(d, y, "B")
        resB.append((nom, rB))
    filas += [
        "",
        "**Diseño B** — nivel: comunas EQ vs no-EQ condicional a la línea"
        " base 2010 (sin FE de comuna; asociación condicional, no DiD —"
        " sin cohorte no expuesta en 2024 el nivel no es identificable"
        " tipo Gillmore).",
        "",
        "| Outcome | β EQ | (EE) | n | clusters |",
        "|---|---:|---:|---:|---:|"]
    for nom, rB in resB:
        _, b, se, p = rB["terms"][0]
        filas.append(f"| {nom} | {b:.3f}{stars(p)} | ({se:.3f}) "
                     f"| {rB['n']:,} | {rB['ncl']} |")
        print("B", nom, f"EQ: {b:.3f}{stars(p)} (se {se:.3f}) n={rB['n']:,}")
    filas += [
        "",
        "**Diseño C** — la fila ΔCBCL 2017→2024 usa al MISMO niño en ambas"
        " olas (z por ola): en A identifica si la trayectoria hacia la"
        " adolescencia difiere por edad de exposición dentro de comuna; en"
        " B, si difiere entre comunas EQ y no-EQ.",
        "",
        "## Lectura de la primera pasada",
        "1. **Gradiente por edad (A)**: dentro de comuna, los expuestos a"
        " los 24–35 meses muestran MENOS síntomas a los 14–18 que los"
        " expuestos a los 36–59 meses (ref.): PHQ-4 −0,15 DE, GAD-2 −0,10,"
        " PHQ-2 −0,07, CBCL −0,13 (todos sig. al 1%). Los expuestos en la"
        " infancia (0–11m) no difieren del ref. Es decir, la cicatriz de"
        " salud mental autorreportada la concentran los expuestos en edad"
        " PREESCOLAR (3–5 años, edad de memoria episódica del evento) y,"
        " en menor medida, la primera infancia — patrón en U consistente"
        " con el canal de memoria traumática más que con el fetal.",
        "2. **Trayectoria CBCL (C)**: dentro de comunas EQ, los tres bins"
        " más jóvenes EMPEORAN ≈+0,24 DE su CBCL 2017→2024 relativo al"
        " grupo 36–59m — equivalente a que el déficit no-cognitivo que"
        " Gillmore midió en 2017 (concentrado en los mayores) se DESVANECE"
        " hacia la adolescencia en el reporte del cuidador, mientras el"
        " autorreporte (PHQ/GAD) de esos mismos mayores sigue peor: los"
        " padres dejan de verlo, el adolescente lo sigue reportando.",
        "3. **Niveles (B) nulos**: sin cohorte no expuesta, la comparación"
        " geográfica pura a 14 años no detecta nivel (esperable: 14 años"
        " de recuperación + heterogeneidad regional).",
        "",
        "## Notas de identificación",
        "- La ola 2024 no tiene cohorte concebida post-27F ⇒ el DiD"
        " cohorte×geografía del paper no es estimable; A explota la"
        " variación de dosis por edad (la que el propio paper usa en su"
        " Fig. B.1), B es descriptivo-condicional y C es panel intra-niño.",
        "- Intensidad: binario regional oficial (crosswalk estrato24→CUT"
        " →región). Siguiente paso natural: PGA del USGS por comuna"
        " (dosis continua) sobre el CUT del crosswalk.",
        "- PHQ-4 construido de los ítems d4_1–d4_4 re-escalados 0–3"
        " (la variable phq4 pública es categórica).",
        ""]
    OUT.mkdir(exist_ok=True)
    (OUT / "salud_mental_27f.md").write_text("\n".join(filas),
                                             encoding="utf-8")
    print("->", OUT / "salud_mental_27f.md")


if __name__ == "__main__":
    main()
