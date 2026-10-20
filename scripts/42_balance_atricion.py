#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atrición entre 2010 y 2024 y balance en la línea base.

La ELPI 2010 entrevistó a 15.175 niños; en 2024 respondieron 10.003. Aquí,
con los niños evaluados en 2010:

  1. Atrición diferencial: responder en 2024 frente a los grupos de edad al
     terremoto por zona afectada (6-11 meses, 1 año y 3-4 años frente a 2
     años), chicas, chicos y todos, con la prueba conjunta.
  2. Balance del peso al nacer en toda la muestra de 2010 y, con la misma
     especificación, solo en quienes respondieron en 2024. Si el
     desequilibrio ya está en 2010, no lo crea la atrición.

La edad al terremoto se mide igual para quienes siguen y quienes salen: la
edad en la evaluación de 2010 menos los meses entre el 27-F y el mes
mediano de evaluación de la región (calculado con quienes tienen la fecha
de nacimiento de 2017 o 2024). Usar la fecha exacta solo para quienes
siguen, y una aproximación para quienes salen, mezclaría el error de
medida con la atrición. Por diseño todos nacieron entre enero de 2006 y
agosto de 2009, así que la edad imputada se acota a 6-49 meses.

Los archivos públicos de 2010 no traen comuna, así que los efectos fijos son
de región (la zona afectada se define por región), año de nacimiento y
grupo de edad, sin pesos y con errores robustos (HC1).

Salida: reports/balance_atricion.md
Uso:    python3 scripts/42_balance_atricion.py
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
    "sm27", HERE / "09_salud_mental_27f.py")
sm27 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sm27)
INT = Path("data/interim")
QUAKE_YM = sm27.QUAKE_YM
TRAMOS = ([6, 12, 24, 36, 50], ["6-11", "12-23", "ref", "36-49"])
NOMBRE = {"6-11": "6-11 meses", "12-23": "1 año", "36-49": "3-4 años",
          "6-17": "primeros 18 meses"}
II = ["I6_11", "I12_23", "I36_49"]
GRUPOS = (("chicas", 1), ("chicos", 0), ("todos", None))
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def num(s):
    return pd.to_numeric(s, errors="coerce")


def stars(p):
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else ""


def lee(f, cols, sav=False):
    if sav:
        x, _ = pyreadstat.read_sav(str(f), usecols=cols)
    else:
        x, _ = pyreadstat.read_dta(str(f), usecols=cols, encoding="latin1")
    x["folio"] = num(x.folio).astype("int64")
    return x.drop_duplicates("folio")


def tramos(d, edad):
    d["tramo"] = pd.cut(edad, TRAMOS[0], right=False,
                        labels=TRAMOS[1]).astype(str)
    for t, i in zip(("6-11", "12-23", "36-49"), II):
        d[i] = (d.tramo == t) * d.EQ
    return d


def carga():
    """Los 15.175 niños de 2010, con la edad al terremoto imputada igual
    para todos y la fecha exacta (2017 o 2024) donde la hay."""
    h, _ = pyreadstat.read_dta(str(INT / "2010/Hogar_2010.dta"),
                               usecols=["folio", "a16", "a18", "a19", "b2n"],
                               encoding="latin1")
    h["folio"] = num(h.folio).astype("int64")
    nino = h[num(h.a16) == 13].drop_duplicates("folio").set_index("folio")
    madre = h[num(h.a16) == 1].drop_duplicates("folio").set_index("folio")
    d = pd.DataFrame({"folio": nino.index})
    d["mujer"] = (num(d.folio.map(nino.a18)) == 2).astype(float).where(
        d.folio.map(nino.a18).notna())
    d["educ"] = num(d.folio.map(madre.b2n)).where(lambda s: s < 30)
    d["edad_madre"] = num(d.folio.map(madre.a19)).where(lambda s: s < 99)
    e = lee(INT / "2010/Entrevistada_2010.dta",
            ["folio", "region", "g24", "g23", "g20"])
    ev = lee(INT / "2010/Evaluaciones_2010.dta", ["folio", "edad_meses"])
    d = d.merge(e, on="folio", how="left").merge(ev, on="folio", how="left")
    d["peso"] = num(d.g24).where(lambda s: s.between(0.5, 6.5))
    d["z_peso"] = (d.peso - d.peso.mean()) / d.peso.std()
    d["reg"] = num(d.region).astype("Int64")
    d["EQ"] = d.reg.isin(sm27.EQ_REGIONS).astype(float)
    # fecha exacta: 2024 o, si no, 2017
    e24 = lee(INT / "2024/Base evaluaciones Stata.dta",
              ["folio", "fecha_nac"])
    fn = e24.fecha_nac.astype(str).str.extract(r"(?P<mm>\d+)/(?P<aa>\d+)")
    e24["b24"] = num(fn.aa) * 12 + num(fn.mm) - 1
    r17 = lee(INT / "2017/Base Cuidador Principal ELPI III (SPSS).sav",
              ["folio", "fechanacimientons"], sav=True)
    b = pd.to_datetime(r17.fechanacimientons, errors="coerce")
    r17["b17"] = b.dt.year * 12 + b.dt.month - 1
    d = (d.merge(e24[["folio", "b24"]], on="folio", how="left")
          .merge(r17[["folio", "b17"]], on="folio", how="left"))
    d["in2024"] = d.b24.notna().astype(float)
    d["exacta"] = d.b24.fillna(d.b17)
    # mes mediano de evaluación por región, con quienes tienen la fecha
    mes = (d.exacta + num(d.edad_meses)).groupby(d.reg).median()
    d["mes_eval"] = d.reg.map(mes)
    d["edadq_imp"] = (num(d.edad_meses) - (d.mes_eval - QUAKE_YM)).clip(6, 49)
    d["edadq_exacta"] = QUAKE_YM - d.exacta
    return d


def prepara(d, edad="edadq_imp"):
    x = d.dropna(subset=[edad, "reg"]).copy()
    x = x[x[edad].between(6, 49)]
    x = tramos(x, x[edad])
    x["t6"] = pd.cut(x[edad], [6, 12, 18, 24, 30, 36, 42, 50], right=False,
                     labels=["6-11", "12-17", "18-23", "24-29", "30-35",
                             "36-41", "42-49"]).astype(str)
    x["V"] = (x[edad] < 18).astype(float) * x.EQ
    for t in ("6-11", "12-17", "18-23", "30-35", "36-41", "42-49"):
        x["T" + t.replace("-", "_")] = (x.t6 == t) * x.EQ
    x["cohorte"] = ((QUAKE_YM - x[edad]) // 12).astype(int).astype(str)
    x["region"] = x.reg.astype(int).astype(str)
    return x


def ajusta(x, y, solo=False, ventana=False):
    """Perfil frente a 2-3 años; con solo=True, 6-11 meses frente a todas
    las demás edades; con ventana=True, los primeros 18 meses frente al
    resto, con efectos fijos de tramo de seis meses, y en "conjunta" el
    p-valor de la prueba de perfil plano en tramos de seis meses."""
    x = x.dropna(subset=[y])
    if ventana:
        f = " + C(t6) + C(region) + C(cohorte)"
        r = smf.ols(f"{y} ~ V{f}", data=x).fit(cov_type="HC1")
        tt = [c for c in x.columns if c.startswith("T") and c[1:2].isdigit()]
        rp = smf.ols(f"{y} ~ {' + '.join(tt)}{f}", data=x).fit(
            cov_type="HC1")
        conj = float(rp.f_test(", ".join(f"{t} = 0" for t in tt)).pvalue)
        b = {"6-17": (float(r.params["V"]), float(r.bse["V"]),
                      float(r.pvalues["V"]))}
        return b, int(r.nobs), conj, float(x[y].mean())
    ii = II[:1] if solo else II
    r = smf.ols(f"{y} ~ {' + '.join(ii)} + C(tramo) + C(region) "
                "+ C(cohorte)", data=x).fit(cov_type="HC1")
    conj = float(r.f_test(", ".join(f"{i} = 0" for i in ii)).pvalue)
    b = {t: (float(r.params[i]), float(r.bse[i]), float(r.pvalues[i]))
         for t, i in zip(("6-11", "12-23", "36-49"), ii)}
    return b, int(r.nobs), conj, float(x[y].mean())


def linea(lab, res):
    b, n, conj, m = res
    log(f"- {lab}: " + " | ".join(
        f"{NOMBRE[t]} {v[0]:+.3f}{stars(v[2])} (ee {v[1]:.3f})"
        for t, v in b.items()) + f" | conjunta p={conj:.2f} | media {m:.3f}"
        f" | N={n:,}")


def resultados(d=None, solo=False, ventana=False):
    """Lo que usa la tabla del apéndice (scripts/41_tablas_apendice.py):
    responder en 2024 (chicas, chicos, todos) y el peso al nacer de las
    chicas en 2010 y en quienes responden en 2024."""
    x = prepara(carga() if d is None else d)
    res = [ajusta(x[x.mujer == sx] if sx is not None else
                  x[x.mujer.notna()], "in2024", solo, ventana)
           for _, sx in GRUPOS]
    ch = x[x.mujer == 1]
    res += [ajusta(ch, "z_peso", solo, ventana),
            ajusta(ch[ch.in2024 == 1], "z_peso", solo, ventana)]
    return res, x


def main():
    d = carga()
    log("# Atrición entre 2010 y 2024 y balance en la línea base "
        "(scripts/42_balance_atricion.py)")
    log("Zona afectada menos no afectada, frente a quienes tenían 2 años; "
        "EF de región, año de nacimiento y grupo de edad; sin pesos; EE "
        "robustos (HC1).")
    ev = d.edad_meses.notna()
    log(f"\nLínea base 2010: {len(d):,} niños; evaluados {ev.sum():,}; "
        f"responden en 2024 {int(d.in2024.sum()):,} "
        f"({d.in2024.mean():.1%}); entre los evaluados, "
        f"{d.loc[ev, 'in2024'].mean():.1%}.")
    log("Mes mediano de evaluación por región (meses desde el 27-F): " +
        ", ".join(f"{int(r)}: {int(m - QUAKE_YM)}" for r, m in
                  d.groupby("reg").mes_eval.first().items()))
    v = d[ev & d.exacta.notna()]
    exacto = pd.cut(v.edadq_exacta, TRAMOS[0], right=False,
                    labels=TRAMOS[1]).astype(str)
    imp = pd.cut(v.edadq_imp, TRAMOS[0], right=False,
                 labels=TRAMOS[1]).astype(str)
    err = v.edadq_imp - v.edadq_exacta
    log(f"Validación con los {len(v):,} que tienen fecha exacta: error medio "
        f"{err.mean():+.2f} meses (zona afectada {err[v.EQ == 1].mean():+.2f}"
        f", no afectada {err[v.EQ == 0].mean():+.2f}); mismo grupo de edad "
        f"{(exacto == imp).mean():.1%}.")
    res, x = resultados(d)
    log("\n## Atrición diferencial (responde en 2024, 0/1)")
    for (g, _), r in zip(GRUPOS, res[:3]):
        linea(g, r)
    log("\n## Peso al nacer de las chicas (DE)")
    linea("toda la muestra de 2010", res[3])
    linea("solo quienes responden en 2024", res[4])
    log("\n## Los primeros 18 meses frente al resto (conjunta: perfil plano"
        " en tramos de seis meses)")
    sol, _ = resultados(d, ventana=True)
    for lab, r in zip(("responde en 2024, chicas", "responde en 2024, chicos",
                       "responde en 2024, todos",
                       "peso al nacer de las chicas, toda la muestra de 2010",
                       "peso al nacer de las chicas, quienes responden en "
                       "2024"), sol):
        linea(lab, r)
    log("\n## Robustez de la atrición")
    for g, sx in GRUPOS:
        s = x[x.mujer == sx] if sx is not None else x[x.mujer.notna()]
        corte = np.abs(s.edadq_imp.values[:, None]
                       - np.array([12, 24, 36])[None, :]).min(axis=1)
        linea(f"{g}, sin quienes están a un mes de un corte",
              ajusta(s[corte > 1], "in2024"))
    y = prepara(d.assign(mixta=d.edadq_exacta.fillna(d.edadq_imp)), "mixta")
    for g, sx in GRUPOS:
        s = y[y.mujer == sx] if sx is not None else y[y.mujer.notna()]
        linea(f"{g}, fecha exacta donde la hay", ajusta(s, "in2024"))
    log("\n## Resto del balance en 2010 (chicas)")
    ch = x[x.mujer == 1]
    for nombre, sub in (("toda la muestra de 2010", ch),
                        ("solo quienes responden en 2024",
                         ch[ch.in2024 == 1])):
        for y_, lab in (("educ", "educación de la madre (años)"),
                        ("edad_madre", "edad de la madre (años)")):
            linea(f"{lab}, {nombre}", ajusta(sub, y_))
    Path("reports/balance_atricion.md").write_text("\n".join(OUT) + "\n",
                                                   encoding="utf-8")
    print("-> reports/balance_atricion.md")


if __name__ == "__main__":
    main()
