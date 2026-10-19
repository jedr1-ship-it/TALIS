#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Salud mental antes de 2024: qué hay, para quién y qué dice.

  1. Quién está en la ELPI 2024. El Informe Metodológico ELPI 2024 (pp. 6
     y 8) dice que la cuarta ronda solo siguió a la muestra original de 2010
     (nacidos entre enero de 2006 y agosto de 2009): los refrescos de 2012 y
     2017, que traen a los concebidos después del 27-F, no se volvieron a
     encuestar. Aquí se comprueba con los folios y las fechas de nacimiento.
  2. Inventario: cada medida de salud mental anterior a 2024, quién la
     responde y cuántos niños la tienen por grupo de nacimiento (expuestos ya
     nacidos, en gestación el 27-F, concebidos después).
  3. El diseño de Gillmore (2026), columna 3, con el CBCL internalizante y
     el de ansiedad/depresión (lo responde el cuidador), la única medida que
     existe para expuestos y concebidos después:
       corto plazo   expuestos en 2012 frente a concebidos después en 2017,
                     todos a los 18-71 meses (CBCL 1½-5);
       mediano plazo ambos en 2017: expuestos a los 7-12 años frente a
                     concebidos después a los 6-7 (CBCL 6-18).
     Más alto = más síntomas. Con dos placebos: entre cohortes concebidas
     después (2011-2013 frente a 2014-2016) y la geografía falsa norte-sur.
  4. Nuestro diseño (perfil por edad, grupos del paper, frente a 2 años) en
     las medidas anteriores a 2024 de los mismos adolescentes: CBCL de 2012 y
     2017, autoestima, satisfacción con la vida y soledad que responde el
     niño en 2017, y consultas y diagnósticos de salud mental de 2017.

Salida: reports/salud_mental_antes.md y reports/salud_mental_antes.csv
Uso:    python3 scripts/40_salud_mental_antes.py
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
INT = Path("data/interim")


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p08 = modulo("p08", "08_replicacion_gillmore.py")
p33 = modulo("p33", "33_ventanas.py")
p15 = p33.p15
num, stars = p08.num, p15.stars
NORTE = {1, 2, 3, 4, 15}
SEXOS = (("chicas", 1), ("chicos", 0), ("todos", None))
OUT, FILAS = [], []
# autoestima escolar (TAE): 0 = Sí, 1 = No; baja autoestima = "Sí" en los
# ítems negativos y "No" en los positivos
TAE_NEG = [1, 4, 8, 10, 12, 13, 15, 16, 17, 19, 20, 21]
TAE_POS = [2, 3, 5, 6, 7, 9, 11, 14, 18, 22, 23]


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def fmt(b, se, p):
    return f"{b:+.3f}{stars(p)} (ee {se:.3f}, p={p:.3f})"


def nac(fecha):
    fn = fecha.astype(str).str.extract(r"(?P<mm>\d+)/(?P<aa>\d+)")
    return num(fn.aa) * 12 + num(fn.mm) - 1


def grupo_nac(ym):
    return pd.cut(ym, [-np.inf, 2010 * 12 + 1, 2010 * 12 + 11, np.inf],
                  labels=["expuestos", "en gestación", "concebidos después"])


# --------------------------------------------------------- 1. verificación

def verifica():
    log("\n## 1. Quién está en la ELPI 2024")
    e24 = p08.dta(INT / "2024/Base evaluaciones Stata.dta",
                  ["folio", "fecha_nac"])
    ym = nac(e24.fecha_nac)
    f10 = set(p08.dta(INT / "2010/Hogar_2010.dta", ["folio"]).folio)
    f12 = set(p08.dta(INT / "2012/Entrevistada_2012.dta", ["folio"]).folio)
    f17 = set(p08.sav(INT / "2017/Base Cuidador Principal ELPI III "
                            "(SPSS).sav", ["folio"]).folio)
    r12, r17, f24 = f12 - f10, f17 - f10 - f12, set(e24.folio)
    log(f"- 2024: {len(f24):,} adolescentes, nacidos entre "
        f"{int(ym.min() % 12) + 1}/{int(ym.min() // 12)} y "
        f"{int(ym.max() % 12) + 1}/{int(ym.max() // 12)}")
    log(f"- de la muestra de 2010 ({len(f10):,} folios): "
        f"{len(f24 & f10):,}; del refresco de 2012 ({len(r12):,}): "
        f"{len(f24 & r12)}; del refresco de 2017 ({len(r17):,}): "
        f"{len(f24 & r17)}")


# ----------------------------------------------------- 2. bases y medidas

def base():
    """Filas de 2012 y 2017 del script 08 con el CBCL internalizante y el de
    ansiedad/depresión; z por ola, versión del CBCL y año de edad."""
    R = p08.load_raw()
    x12 = p08.dta(INT / "2012/Evaluaciones_2012.dta",
                  ["folio", "cbcl1_pt_i", "cbcl1_pb_2", "cbcl2_pt_i",
                   "cbcl2_pb_1", "cbcl1_pt_e", "cbcl2_pt_e",
                   "cbcl2_pt_t"]).drop_duplicates("folio")
    x17 = p08.dta(INT / "2017/Base Evaluaciones ELPI III.dta",
                  ["folio", "cbcl1_pt_inter_i", "cbcl1_pb_2",
                   "cbcl2_pt_inter_i", "cbcl2_pb_1", "cbcl1_pt_inter_e",
                   "cbcl2_pt_inter_e"]).drop_duplicates("folio")
    R["ev12"] = R["ev12"].merge(x12, on="folio", how="left")
    R["ev17"] = R["ev17"].merge(x17, on="folio", how="left")
    df = p08.combina(R, p08.BEST)
    i1 = num(df.cbcl1_pt_i).fillna(num(df.cbcl1_pt_inter_i))
    i2 = num(df.cbcl2_pt_i).fillna(num(df.cbcl2_pt_inter_i))
    df["inst"] = np.where(i1.notna(), 1.0, np.where(i2.notna(), 2.0, np.nan))
    df["t_int"] = i1.where(i1.notna(), i2)
    df["ansdep"] = num(df.cbcl1_pb_2).where(df.inst == 1,
                                            num(df.cbcl2_pb_1))
    e1 = num(df.cbcl1_pt_e).fillna(num(df.cbcl1_pt_inter_e))
    e2 = num(df.cbcl2_pt_e).fillna(num(df.cbcl2_pt_inter_e))
    t1 = num(df.cbcl1_pt_t).fillna(num(df.cbcl1_pt_inter_t))
    t2 = num(df.cbcl2_pt_t).fillna(num(df.cbcl2_pt_inter_t))
    df["t_ext"] = e1.where(df.inst == 1, e2)
    df["t_tot"] = t1.where(df.inst == 1, t2)
    g = [df.wave, df.inst, num(df.edad_meses) // 12]
    for v, s in (("z_int", df.t_int), ("z_ansdep", df.ansdep),
                 ("z_ext", df.t_ext), ("z_tot", df.t_tot)):
        gr = s.groupby(g)
        df[v] = (s - gr.transform("mean")) / gr.transform("std")
    df["grupo"] = grupo_nac(df.birth_ym)
    return df


def nacimientos(df):
    """Fecha de nacimiento por folio: la de 2017 si está, si no la de 2012."""
    return (df.sort_values("wave", ascending=False)
              .drop_duplicates("folio").set_index("folio").birth_ym)


def ninos17():
    n17, _ = pyreadstat.read_sav(
        INT / "2017/Base Niños y Niñas ELPI III (SPSS).sav",
        usecols=["folio", "edad", "e6", "eclis_p2"]
        + [f"tae_p{k}" for k in range(1, 24)])
    n17["folio"] = num(n17.folio).astype("int64")
    n17 = n17.drop_duplicates("folio")
    it = {k: num(n17[f"tae_p{k}"]) for k in range(1, 24)}
    baja = (sum((it[k] == 0).astype(float) for k in TAE_NEG)
            + sum((it[k] == 1).astype(float) for k in TAE_POS))
    n17["tae_baja"] = baja.where(pd.concat(it, axis=1).notna().all(axis=1))
    n17["no_feliz"] = (it[2] == 1).astype(float).where(it[2].notna())
    n17["insatisf"] = 8 - num(n17.e6).where(num(n17.e6).between(1, 7))
    n17["soledad"] = num(n17.eclis_p2).where(num(n17.eclis_p2).between(1, 4))
    for v in ("tae_baja", "insatisf", "soledad"):
        g = n17[v].groupby(num(n17.edad))
        n17[f"z_{v}"] = (n17[v] - g.transform("mean")) / g.transform("std")
    return n17


def cuidador17():
    c, _ = pyreadstat.read_sav(
        INT / "2017/Base Cuidador Principal ELPI III (SPSS).sav",
        usecols=["folio", "sn17d", "sn22_26", "sn22_27"])
    c["folio"] = num(c.folio).astype("int64")
    c = c.dropna(subset=["sn22_26"]).drop_duplicates("folio")
    s = num(c.sn17d)
    c["consulta_sm"] = (s > 0).astype(float).where(s.between(0, 87))
    dep, ans = num(c.sn22_26), num(c.sn22_27)
    c["dx_dep_ans"] = ((dep == 1) | (ans == 1)).astype(float).where(
        dep.isin([1, 2]) & ans.isin([1, 2]))
    return c


def inventario(df, n17, c17):
    log("\n## 2. Medidas de salud mental antes de 2024: quién las tiene")
    log("Niños con dato por grupo de nacimiento: expuestos ya nacidos el "
        "27-F / en gestación (mar-dic 2010) / concebidos después (2011+).")
    cnt = lambda s: " / ".join(
        f"{int(v):,}" for v in s.reindex(
            ["expuestos", "en gestación", "concebidos después"]).fillna(0))
    for ola in (2012, 2017):
        for inst, nom in ((1, "CBCL 1½-5"), (2, "CBCL 6-18")):
            x = df[(df.wave == ola) & (df.inst == inst)]
            e = num(x.edad_meses)
            log(f"- {ola}, {nom}, cuidador ({int(e.min())}-{int(e.max())} "
                f"meses): {cnt(x.grupo.value_counts())}")
    bym = nacimientos(df)
    for nom, d, v in (("2017, autoestima TAE, niño (7-12 años)", n17,
                       "tae_baja"),
                      ("2017, satisfacción con la vida, niño", n17,
                       "insatisf"),
                      ("2017, soledad en el curso, niño", n17, "soledad"),
                      ("2017, consulta de salud mental en 12 meses, "
                       "cuidador", c17, "consulta_sm"),
                      ("2017, diagnóstico de depresión o ansiedad, "
                       "cuidador", c17, "dx_dep_ans")):
        x = d[d[v].notna()]
        gr = grupo_nac(x.folio.map(bym))
        log(f"- {nom}: {cnt(gr.value_counts())}")
    log("- 2024, PHQ-4, adolescente: solo expuestos (10.003)")


# ------------------------------------------------ 3. diseño de Gillmore

def ajusta(d, y, term="AffEq"):
    d = d.dropna(subset=[y, term, "geo", "w", "cohorte"]).copy()
    d = d[d.w > 0]
    d["com"] = d.geo.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    d["ola"] = d.wave.astype(str)
    f = f"{y} ~ {term} + C(com) + C(coh)"
    if d.ola.nunique() > 1:
        f += " + C(ola)"
    xs = []
    for v in p08.XVARS:
        s = d[v]
        if s.notna().sum() == 0 or s.nunique() < 2:
            continue
        if s.isna().any():
            d[f"{v}_mi"] = s.isna().astype(float)
            d[v] = s.fillna(s.median())
            xs += [v, f"{v}_mi"]
        else:
            xs.append(v)
    f += " + " + " + ".join(xs)
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d["com"]})
    return (float(r.params[term]), float(r.bse[term]),
            float(r.pvalues[term])), int(r.nobs), int((d.affected == 1).sum())


def gillmore(df):
    log("\n## 3. Diseño de Gillmore con el CBCL (columna 3; más alto = más "
        "síntomas)")
    st = df[(((df.wave == 2012) & (df.affected == 1))
             | ((df.wave == 2017) & (df.affected == 0)
                & df.cohorte.between(2011, 2015))) & (df.inst == 1)]
    mt = df[(df.wave == 2017) & df.cohorte.between(2006, 2015)
            & (df.inst == 2)]
    mt = mt[(mt.affected == 0) | num(mt.edad_meses).between(84, 151)]
    for hz, d in (("corto plazo: expuestos en 2012 frente a concebidos "
                   "después en 2017, a los 18-71 meses", st),
                  ("mediano plazo: 2017, expuestos a los 7-12 años frente a "
                   "concebidos después a los 6-7", mt)):
        log(f"\n### {hz}")
        for y, lab in (("z_tot", "CBCL total, la medida no cognitiva de "
                                 "Gillmore"),
                       ("z_int", "CBCL internalizante"),
                       ("z_ansdep", "CBCL ansiedad/depresión"),
                       ("z_ext", "CBCL externalizante")):
            for g, sx in SEXOS:
                dd = d if sx is None else d[d.mujer == sx]
                r, n, na = ajusta(dd, y)
                log(f"- {lab}, {g}: {fmt(*r)}; N={n:,} (expuestos {na:,}, "
                    f"controles {n - na:,})")
                FILAS.append({"parte": "gillmore", "horizonte": hz[:13],
                              "y": y, "grupo": g, "b": r[0], "se": r[1],
                              "p": r[2], "n": n})
    log("\n### Placebos")
    c = df[(df.wave == 2017) & (df.affected == 0) & (df.inst == 1)
           & df.cohorte.between(2011, 2016)].copy()
    c["Falso"] = (c.cohorte <= 2013).astype(float) * c.earthquake
    for y, lab in (("z_int", "internalizante"),
                   ("z_ansdep", "ansiedad/depresión")):
        r, n, _ = ajusta(c, y, "Falso")
        log(f"- concebidos después, 2011-2013 frente a 2014-2016, CBCL "
            f"{lab}: {fmt(*r)}; N={n:,}")
    for hz, d in (("corto plazo", st), ("mediano plazo", mt)):
        x = d[d.earthquake == 0].copy()
        x["Falso"] = x.affected * num(x.region).isin(NORTE).astype(float)
        r, n, _ = ajusta(x, "z_int", "Falso")
        log(f"- geografía falsa, {hz}, solo zona no afectada, norte frente "
            f"a sur, CBCL internalizante: {fmt(*r)}; N={n:,}")


# edad al 27-F en meses (negativa: en gestación); grupos de los nacidos antes
# del corte de Gillmore, cada uno frente a los concebidos después
EDADES_G = [(-10, -1, "gest", "en gestación"), (0, 5, "m0_5", "0-5 meses"),
            (6, 11, "m6_11", "6-11 meses"), (12, 23, "m12_23", "1 año"),
            (24, 35, "m24_35", "2 años"), (36, 59, "m36_59", "3-4 años")]


def ajusta_varios(d, y, terms):
    d = d.dropna(subset=[y, "geo", "w", "cohorte"]).copy()
    d = d[d.w > 0]
    d["com"] = d.geo.astype(int).astype(str)
    d["coh"] = d.cohorte.astype(int).astype(str)
    d["ola"] = d.wave.astype(str)
    terms = [t for t in terms if d[t].sum() >= 30]
    f = f"{y} ~ {' + '.join(terms)} + C(com) + C(coh)"
    if d.ola.nunique() > 1:
        f += " + C(ola)"
    xs = []
    for v in p08.XVARS:
        s = d[v]
        if s.notna().sum() == 0 or s.nunique() < 2:
            continue
        if s.isna().any():
            d[f"{v}_mi"] = s.isna().astype(float)
            d[v] = s.fillna(s.median())
            xs += [v, f"{v}_mi"]
        else:
            xs.append(v)
    f += " + " + " + ".join(xs)
    r = smf.wls(f, data=d, weights=d.w).fit(
        cov_type="cluster", cov_kwds={"groups": d["com"]})
    return {t: (float(r.params[t]), float(r.bse[t]), float(r.pvalues[t]),
                int((d[t] > 0).sum())) for t in terms}, int(r.nobs)


def gillmore_edades(df):
    log("\n### Por edad al terremoto: cada grupo frente a los concebidos "
        "después (columna 3)")
    x = df.copy()
    x["edadq"] = (2010 * 12 + 1) - x.birth_ym
    terms = []
    for lo, hi, k, _ in EDADES_G:
        x[f"G{k}"] = (x.affected * x.earthquake
                      * x.edadq.between(lo, hi).astype(float))
        terms.append(f"G{k}")
    nombre = {f"G{k}": lab for _, _, k, lab in EDADES_G}
    st = x[(((x.wave == 2012) & (x.affected == 1))
            | ((x.wave == 2017) & (x.affected == 0)
               & x.cohorte.between(2011, 2015))) & (x.inst == 1)]
    mt = x[(x.wave == 2017) & x.cohorte.between(2006, 2015) & (x.inst == 2)]
    mt = mt[(mt.affected == 0) | num(mt.edad_meses).between(84, 151)]
    tv = x[(x.wave == 2017) & x.cohorte.between(2006, 2015)]
    tv = tv[(tv.affected == 0) | num(tv.edad_meses).between(84, 151)]
    for hz, d, ys in (("2012 (corto plazo, CBCL 1½-5)", st,
                       (("z_int", "internalizante"),
                        ("z_ansdep", "ansiedad/depresión"))),
                      ("2017 (mediano plazo, CBCL 6-18)", mt,
                       (("z_int", "internalizante"),
                        ("z_ansdep", "ansiedad/depresión"))),
                      ("2017 (mediano plazo, vocabulario TVIP; más alto = "
                       "mejor)", tv, (("z_tvip", "TVIP"),))):
        log(f"\n{hz}")
        for y, lab in ys:
            for g, sx in SEXOS:
                dd = d if sx is None else d[d.mujer == sx]
                b, n = ajusta_varios(dd, y, terms)
                log(f"- {lab}, {g}: " + " | ".join(
                    f"{nombre[t]} {fmt(*v[:3])}" for t, v in b.items())
                    + f" | N={n:,}")
                for t, v in b.items():
                    FILAS.append({"parte": "gillmore_edad", "horizonte": hz,
                                  "y": y, "grupo": g, "tramo": nombre[t],
                                  "b": v[0], "se": v[1], "p": v[2], "n": n})


def gillmore_nino(df, n17):
    log("\n### Lo que responde el niño en 2017 (expuestos a los 7-12 años "
        "frente a concebidos después a los 7)")
    x = (df[(df.wave == 2017) & df.cohorte.between(2006, 2015)]
         .drop(columns=["z_int", "z_ansdep", "z_ext", "z_tot"])
         .merge(n17[["folio", "z_tae_baja", "no_feliz", "z_soledad"]],
                on="folio", how="inner"))
    for y, lab in (("z_soledad", "se siente solo en el curso"),
                   ("no_feliz", "no se considera feliz"),
                   ("z_tae_baja", "baja autoestima")):
        for g, sx in SEXOS:
            dd = x if sx is None else x[x.mujer == sx]
            r, n, na = ajusta(dd, y)
            log(f"- {lab}, {g}: {fmt(*r)}; N={n:,} (expuestos {na:,}, "
                f"controles {n - na:,})")


# ------------------------------------------------- 4. nuestro diseño

def perfiles(df, n17, c17):
    log("\n## 4. Nuestro diseño en las medidas anteriores a 2024")
    log("Mismos adolescentes de 2024; zona afectada menos no afectada, "
        "frente a quienes tenían 2 años; más alto = peor.")
    d, _, _ = p15.load_data()
    for ola in (2012, 2017):
        x = (df[df.wave == ola][["folio", "z_int", "z_ansdep"]]
             .drop_duplicates("folio")
             .rename(columns={"z_int": f"z_int{ola % 100}",
                              "z_ansdep": f"z_ansdep{ola % 100}"}))
        d = d.merge(x, on="folio", how="left")
    d = (d.merge(n17[["folio", "z_tae_baja", "no_feliz", "z_insatisf",
                      "z_soledad"]], on="folio", how="left")
          .merge(c17[["folio", "consulta_sm", "dx_dep_ans"]], on="folio",
                 how="left"))
    zz = lambda s: (s - s.mean()) / s.std()
    tres = pd.concat([zz(d.z_tae_baja), zz(d.no_feliz), zz(d.z_soledad)],
                     axis=1)
    d["z_malestar17"] = zz(tres.mean(axis=1).where(tres.notna().all(axis=1)))
    log("\nCorrelación con el PHQ-4 de 2024 (mismos adolescentes):")
    for v, lab in (("z_int17", "CBCL internalizante 2017"),
                   ("z_tae_baja", "baja autoestima 2017"),
                   ("no_feliz", "no se considera feliz 2017"),
                   ("z_soledad", "se siente solo en el curso 2017"),
                   ("z_malestar17", "índice de las tres, 2017")):
        ok = d[v].notna() & d.z_phq4.notna()
        log(f"- {lab}: {d.loc[ok, v].corr(d.loc[ok, 'z_phq4']):.2f} "
            f"(N={int(ok.sum()):,})")
    medidas = [("z_int12", "2012, CBCL internalizante (cuidador)"),
               ("z_ansdep12", "2012, CBCL ansiedad/depresión (cuidador)"),
               ("z_int17", "2017, CBCL internalizante (cuidador)"),
               ("z_ansdep17", "2017, CBCL ansiedad/depresión (cuidador)"),
               ("z_tae_baja", "2017, baja autoestima, TAE (niño)"),
               ("no_feliz", "2017, no se considera feliz (niño, 0/1)"),
               ("z_insatisf", "2017, insatisfacción con su vida (niño)"),
               ("z_soledad", "2017, se siente solo en el curso (niño)"),
               ("z_malestar17", "2017, índice de autoestima, felicidad y "
                                "soledad (niño)"),
               ("consulta_sm", "2017, consulta de salud mental en 12 meses "
                               "(cuidador, 0/1)"),
               ("dx_dep_ans", "2017, diagnóstico de depresión o ansiedad "
                              "(cuidador, 0/1)"),
               ("z_phq4", "2024, PHQ-4 (adolescente)")]
    for g, sx in SEXOS:
        log(f"\n### {g}")
        for y, lab in medidas:
            b, n = p33.perfil(d, y, sx, "paper")
            log(f"- {lab}: " + " | ".join(
                f"{t} {fmt(*v[:3])}" if v[3] >= 30 else f"{t} sin datos"
                for t, v in b.items()) + f" | N={n:,}")
            for t, v in b.items():
                if v[3] < 30:
                    continue
                FILAS.append({"parte": "perfil", "horizonte": "", "y": y,
                              "grupo": g, "tramo": t, "b": v[0], "se": v[1],
                              "p": v[2], "n": n})


def main():
    log("# Salud mental antes de 2024 (scripts/40_salud_mental_antes.py)")
    verifica()
    df = base()
    n17, c17 = ninos17(), cuidador17()
    inventario(df, n17, c17)
    gillmore(df)
    gillmore_edades(df)
    gillmore_nino(df, n17)
    perfiles(df, n17, c17)
    pd.DataFrame(FILAS).to_csv("reports/salud_mental_antes.csv", index=False)
    Path("reports/salud_mental_antes.md").write_text("\n".join(OUT) + "\n",
                                                     encoding="utf-8")
    print("-> reports/salud_mental_antes.md, reports/salud_mental_antes.csv")


if __name__ == "__main__":
    main()
