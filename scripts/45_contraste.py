#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La comparación resumen de la presentación: los primeros 18 meses (6-17)
frente a todas las demás edades, con efectos fijos de tramo de seis meses.

Es exploratoria: se eligió después de ver el perfil completo
(scripts/47_perfil_completo.py), donde las chicas expuestas en el primer año
y medio están por encima y las de 18-35 meses por debajo. Con la misma
especificación (efectos fijos de comuna, año de nacimiento y tramo de seis
meses, controles, pesos ELPI, EE por comuna) y una sola interacción,
primeros 18 meses x zona afectada; para cada resultado, además, la prueba
conjunta de perfil plano (los seis tramos frente al de 24-29 meses):

  phq4      PHQ-4: todos, chicas, chicos, chicas con efectos fijos de mes
            de nacimiento y chicas con el PGA (por 10 puntos de % de g) en
            lugar de la zona (diapositiva 6)
  nivel     PHQ-4 medio por tramo de seis meses y zona (respaldo)
  entorno   los seis indicadores del entorno, chicas (diapositiva 8)
  estres    estrés de la madre reportado en 2012 (el mediador)
  pecho     el efecto de los primeros 18 meses en quienes tomaban pecho el
            27-F y en quienes no; chicas, chicas con la educación y el
            empleo de la madre interactuados con el pecho y con la zona, y
            chicos (diapositiva 9)
  otros     PHQ-4, consumo, victimización y CBCL, chicas y chicos

Con 116 comunas, además del error estándar por comuna se da el p-valor del
wild cluster bootstrap-t (Rademacher, con la hipótesis nula impuesta;
Cameron, Gelbach y Miller, 2008) para el PHQ-4 y la diferencia por
lactancia.

Salida: reports/contraste.csv y reports/contraste.md
Uso:    python3 scripts/45_contraste.py
"""
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    s = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


p34 = modulo("p34", "34_estres_madre.py")
p33, p15 = p34.p33, p34.p15
SEXOS = (("chicas", 1), ("chicos", 0))
OTROS = ["z_phq4", "z_consumo", "z_bull", "cbcl_int", "cbcl_ext"]
OUT, FILAS = [], []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def guarda(tipo, resultado, grupo, b, se, p, n, **extra):
    FILAS.append({"tipo": tipo, "resultado": resultado, "grupo": grupo,
                  "b": b, "se": se, "p": p, "n": n, **extra})


CLAVE = "6-17"


def contraste(d, y, sx, **kw):
    b, n = p33.perfil(d, y, sx, "seis", solo=p33.VENTANA, **kw)
    return b[CLAVE][:3], n


def plano(d, y, sx, **kw):
    """p-valor de la prueba conjunta de perfil plano: los seis tramos de
    seis meses x zona frente al de 24-29 meses."""
    _, _, r, _ = p33.perfil(d, y, sx, "seis_ref", modelo=True, **kw)
    ii = [k for k in r.params.index if k[:1] == "I" and k[1:2].isdigit()]
    return float(r.f_test(", ".join(f"{k} = 0" for k in ii)).pvalue)


def wild(r, grupos, termino, B=9999, semilla=27):
    """p-valor del wild cluster bootstrap-t de un coeficiente de un WLS de
    statsmodels: pesos de Rademacher por comuna e hipótesis nula impuesta.
    Por Frisch-Waugh, cada réplica solo proyecta sobre el resto de
    regresores (una QR calculada una vez)."""
    X, y = np.asarray(r.model.exog), np.asarray(r.model.endog)
    raiz = np.sqrt(np.asarray(r.model.weights))
    j = list(r.model.exog_names).index(termino)
    Xw, yw = X * raiz[:, None], y * raiz
    Q, _ = np.linalg.qr(np.delete(Xw, j, axis=1))

    def proy(z):
        return z - Q @ (Q.T @ z)
    dd = proy(Xw[:, j])
    den = dd @ dd
    g = pd.factorize(np.asarray(grupos))[0]
    G = g.max() + 1

    def t_de(yres):
        b = dd @ yres / den
        sg = np.bincount(g, weights=dd * (yres - dd * b), minlength=G)
        return b / np.sqrt((sg ** 2).sum() / den ** 2)
    yr = proy(yw)
    t0 = t_de(yr)
    rng = np.random.default_rng(semilla)
    ts = np.array([t_de(proy(rng.choice([-1.0, 1.0], size=G)[g] * yr))
                   for _ in range(B)])
    return float((np.abs(ts) >= abs(t0)).mean())


def linea(lab, r, n, pw=None, pp=None):
    extra = "" if pw is None else f", wild bootstrap p={pw:.3f}"
    plano_ = "" if pp is None else f"; perfil plano p={pp:.3f}"
    log(f"- {lab}: {r[0]:+.3f} (ee {r[1]:.3f}, p={r[2]:.3f}{extra}); "
        f"N={n:,}{plano_}")


def phq4():
    d, _, _ = p15.load_data()
    d["pga10"] = d.pga / 10
    log("\n## PHQ-4")
    for g, sx, kw, datos in (("todos", None, {}, d), ("chicas", 1, {}, d),
                             ("chicos", 0, {}, d),
                             ("chicas, mes", 1, {"mes": True}, d),
                             ("chicas, PGA", 1, {}, d.assign(EQ=d.pga10))):
        b, n, r, x = p33.perfil(datos, "z_phq4", sx, "seis",
                                solo=p33.VENTANA, modelo=True, **kw)
        pw = wild(r, x.est, "I_v")
        pp = plano(datos, "z_phq4", sx, **kw)
        linea(g, b[CLAVE][:3], n, pw, pp)
        guarda("phq4", "z_phq4", g, *b[CLAVE][:3], n, p_wild=pw,
               p_plano=pp)
    p44 = modulo("p44", "44_pga_niveles.py")
    x = p44.carga()
    for g, sx in SEXOS:
        m = p44.medias(x[x.mujer == sx], p44.SEIS)
        for (t, e), (b, se, n) in m.items():
            guarda("nivel", "z_phq4", g, b, se, np.nan, n, tramo=t,
                   zona=int(e))


def entorno():
    p35 = modulo("p35", "35_canal_hogar.py")
    d = p35.carga()
    log("\n## Entorno, chicas")
    for i in p35.INDICES:
        r, n = contraste(d, i, 1)
        pp = plano(d, i, 1)
        linea(i, r, n, pp=pp)
        guarda("entorno", i, "chicas", *r, n, p_plano=pp)


def otros():
    p36 = modulo("p36", "36_chicos.py")
    d = p36.p19.construye()
    c = d[["alcohol", "fuma", "cannabis", "otras_drogas"]]
    d["consumo"] = c.max(axis=1).where(c.notna().any(axis=1))
    d["z_consumo"] = (d.consumo - d.consumo.mean()) / d.consumo.std()
    log("\n## Otros resultados")
    for g, sx in SEXOS:
        for y in OTROS:
            r, n = contraste(d, y, sx)
            pp = plano(d, y, sx)
            linea(f"{y}, {g}", r, n, pp=pp)
            guarda("otros", y, g, *r, n, p_plano=pp)


def estres():
    """El estrés de la madre (2012) con la misma comparación: si es el
    canal, debería subir más en la zona afectada para las madres de los
    más pequeños."""
    d = p34.carga()
    log("\n## Estrés de la madre reportado en 2012 (mediador)")
    for g, sx in (("todos", None), ("chicas", 1)):
        r, n = contraste(d, "estres12", sx)
        linea(g, r, n)
        guarda("estres", "estres12", g, *r, n)


def pecho():
    """Primeros 18 meses x zona, por separado para quienes tomaban pecho el
    27-F y quienes no, frente a todas las demás edades; efectos fijos de
    tramo de seis meses x pecho."""
    d = p34.carga()
    log("\n## El efecto de los primeros 18 meses según la lactancia")
    for g, sx, ses in (("chicas", 1, False), ("chicas, SES", 1, True),
                       ("chicos", 0, False)):
        x = d.dropna(subset=["z_phq4", "pecho", "estrato", "w",
                             "cohorte"]).copy()
        x = x[(x.w > 0) & (x.mujer == sx)]
        x["est"] = x.estrato.astype(int).astype(str)
        x["coh"] = x.cohorte.astype(int).astype(str)
        bordes, et = p33.CORTES["seis"]
        x["b6"] = pd.cut(x.edadq_m, bordes, right=False,
                         labels=et).astype(str)
        x["V"] = x.b6.isin(p33.VENTANA).astype(float) * x.EQ
        extra = []
        if ses:
            x = x.dropna(subset=["educ_madre10", "trabaja10"]).copy()
            for v in ("educ_madre10", "trabaja10"):
                x[f"p_{v}"] = x.pecho * x[v]
                x[f"a_{v}"] = x.EQ * x[v]
                extra += [f"p_{v}", f"a_{v}"]
        x["S_bf"] = x.V * x.pecho
        x["S_no"] = x.V * (1 - x.pecho)
        ctr = p34.xt(x, p15.X_PRE) + p34.xt(x, p15.X_POST)
        fe = (["C(b6)", "C(b6):pecho", "pecho", "C(est)", "C(coh)"]
              + ctr + extra)

        def fit(rhs):
            return smf.wls("z_phq4 ~ " + " + ".join(rhs + fe), data=x,
                           weights=x.w).fit(cov_type="cluster",
                                            cov_kwds={"groups": x.est})
        r = fit(["S_bf", "S_no"])
        t = r.t_test("S_bf - S_no")
        dif = (float(np.ravel(t.effect)[0]), float(np.ravel(t.sd)[0]),
               float(np.ravel(t.pvalue)[0]))
        n = int(r.nobs)
        cuota = float(x[x.b6.isin(p33.VENTANA)].pecho.mean())
        for k, lab in (("S_bf", "con pecho"), ("S_no", "sin pecho")):
            res = (float(r.params[k]), float(r.bse[k]), float(r.pvalues[k]))
            linea(f"{g}, {lab}", res, n)
            guarda("pecho", lab, g, *res, n)
        # la diferencia como un solo coeficiente: con V (= S_bf + S_no), el
        # de S_bf es la diferencia entre con y sin pecho
        pw = wild(fit(["S_bf", "V"]), x.est, "S_bf")
        linea(f"{g}, diferencia (tomaban pecho en la ventana: {cuota:.0%})",
              dif, n, pw)
        guarda("pecho", "diferencia", g, *dif, n, p_wild=pw, cuota=cuota)


def main():
    log("# Los primeros 18 meses frente a todas las demás edades "
        "(scripts/45_contraste.py)")
    log("Exploratoria. Zona afectada menos no afectada; EF de comuna, año "
        "de nacimiento y tramo de seis meses; controles; pesos ELPI; EE por "
        "comuna.")
    phq4()
    entorno()
    estres()
    pecho()
    otros()
    pd.DataFrame(FILAS).to_csv("reports/contraste.csv", index=False)
    Path("reports/contraste.md").write_text("\n".join(OUT) + "\n",
                                            encoding="utf-8")
    print("-> reports/contraste.csv, reports/contraste.md")


if __name__ == "__main__":
    main()
