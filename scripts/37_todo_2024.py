#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Todas las variables de la ELPI 2024, por edad al terremoto.

Recorre las tres bases de 2024 (adolescentes, evaluaciones y responsable
principal) y estima, para cada variable utilizable, la diferencia zona
afectada menos no afectada de cada tramo de edad al terremoto (6-11 meses,
1 año y 3-4 años) frente a los expuestos con 2 años, con la especificación
de scripts/33 (columna 3 de la Table 3).

Qué entra:
  - Variables numéricas con al menos 1.000 respuestas válidas en la muestra.
  - Los códigos de no sabe, no responde, no aplica o sin dato pasan a
    perdidos según sus etiquetas; en las variables sin etiquetas, los
    códigos 88, 99, 888, 999... cuando son valores atípicos.
  - Dicotómicas: 1 = sí (o la categoría que no empieza por «no»).
    Ordinales y continuas: tal como están codificadas. Nominales
    (categorías sin orden): una dicotómica por categoría con entre el 3 % y
    el 97 % de las respuestas.
  - Base del responsable principal: las variables del hogar (iguales en
    todas sus filas) y, para las de cada integrante, las filas del
    adolescente y del cuidador principal.
Qué no entra: identificadores, factores de expansión, estratos, fechas,
códigos geográficos y de ocupación, texto abierto, banderas de
participación y de flujo, y el sexo y la edad del adolescente.

El color del mapa es el estadístico t (b/ee) en la dirección en que está
codificada cada variable: no dice si más alto es mejor o peor.

Salida: reports/todo_2024.csv, reports/todo_2024.md,
        presentacion/figuras/todo_2024_*.pdf
Uso:    python3 scripts/37_todo_2024.py
"""
import importlib.util
import os
import re
import warnings
from multiprocessing import Pool
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import matplotlib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyreadstat  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p33", HERE / "33_ventanas.py")
p33 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p33)
p15 = p33.p15
stars = p15.stars
BASE = Path("data/interim/2024")
TRAMOS = ["6-11", "12-23", "36-49"]
COLUMNAS = ["6–11\nmeses", "1\naño", "3–4\naños"]
MIN_N = 1000
OUT = []

FUERA_NOMBRE = re.compile(
    r"^(folio|estrato|tcuestionario|inicio_|fecha|id_|conf_|nmissing|aux_|"
    r"flujo_|macrozona|r1[27]$|f_exp|cod_|roster_|tipo_persona$|mayor18a$|"
    r"hog$|h9|sg01$)")
FUERA_ETIQUETA = re.compile(
    r"factor de expansi|particip[oó] en elpi|c[oó]digo|encuestador|"
    r"tipo cuestionario|cantidad de items perdidos|^\W*fecha|"
    r"^\W*comuna\W*$|^\W*regi[oó]n\W*$", re.I)
PERDIDO = re.compile(
    r"no sabe|no responde|no aplica|sin dato|ns\s*/?\s*nr|no corresponde|"
    r"rechaz|no recuerda|perdid|missing|sin informaci|prefier[eo] no|"
    r"no contesta|no quiere", re.I)
ORDEN = re.compile(
    r"nunca|siempre|vece|frecuen|casi|nada|poco|algo|bastante|mucho|muy|"
    r"totalmente|acuerdo|satisf|buen|mal[oa]|regular|excelente|mejor|peor|"
    r"igual|m[aá]s|menos|ningun|tod[oa]s|diari|semana|mes|año|d[ií]a|hora|"
    r"minuto|\d", re.I)
CENTINELAS = [88, 99, 888, 999, 8888, 9999, 88888, 99999, 888888, 999999,
              8888888, 9999999]

# (base, prefijo de la variable) -> grupo del mapa; el orden es el del mapa
GRUPOS = [
    ("A", ("phq", "gad"), "Adolescente: salud mental"),
    ("A", ("d",), "Adolescente: salud, resiliencia y satisfacción"),
    ("A", ("g",), "Adolescente: pares, violencia, sexualidad y consumo"),
    ("A", ("c",), "Adolescente: seguridad y violencia"),
    ("A", ("e",), "Adolescente: educación"),
    ("A", ("a", "tot"), "Adolescente: actividades, pantallas, sueño y dieta"),
    ("A", ("f",), "Adolescente: familia y confianza"),
    ("A", ("sg", "os"), "Adolescente: género y orientación sexual"),
    ("A", ("pd",), "Adolescente: discapacidad"),
    ("E", ("cbcl",), "Cuidador: conducta del adolescente (CBCL)"),
    ("E", ("tvip",), "Adolescente: vocabulario (TVIP)"),
    ("E", ("aces",), "Cuidador: experiencias adversas (ACEs)"),
    ("E", ("cesd", "rs", "cat"), "Cuidador: depresión (CES-D)"),
    ("E", ("psi",), "Cuidador: estrés parental (PSI)"),
    ("E", ("pscs",), "Cuidador: competencia parental (PSCS)"),
    ("R", ("sn",), "Responsable: salud del adolescente"),
    ("R", ("e", "en"), "Responsable: educación y colegio"),
    ("R", ("pc", "tot"), "Responsable: crianza, pantallas y sueño"),
    ("R", ("home",), "Responsable: ambiente del hogar (HOME)"),
    ("R", ("p",), "Responsable: el padre"),
    ("R", ("m",), "Responsable: la madre"),
    ("R", ("a",), "Responsable: eventos adversos del hogar"),
    ("R", ("v",), "Responsable: vivienda y barrio"),
    ("R", ("ap",), "Responsable: programas sociales"),
    ("R", ("cn",), "Responsable: cuidados y trabajo doméstico"),
    ("R", ("y", "ytotal", "yaut", "qaut", "daut"), "Responsable: ingresos"),
    ("R", ("h", "numper", "hacinamiento", "tipohogar", "ppadres", "cant",
           "educmadre"), "Responsable: composición del hogar"),
    ("R", ("o", "activ"), "Responsable: trabajo"),
    ("R", ("s", "discapacidad"), "Responsable: salud y discapacidad"),
    ("R", ("esc", "educ", "educc", "educcom", "inmigrante", "etnia", "sexo",
           "edad"), "Responsable: educación y origen"),
]


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def prefijo(v):
    m = re.match(r"[a-z]+", v.lower())
    return m.group(0) if m else v


def grupo(base, v):
    raiz = re.sub(r"_(adol|cuid)$", "", v)
    p = prefijo(raiz)
    for i, (b, pref, nombre) in enumerate(GRUPOS):
        if b == base and (p in pref or raiz in pref):
            return i, nombre
    return len(GRUPOS), {"A": "Adolescente: otras", "E": "Evaluaciones: otras",
                         "R": "Responsable: otras"}[base]


def etiqueta(v, t):
    t = str(t or "")
    t = re.sub(r"%[^%]*adolescente[^%]*%", "el adolescente", t, flags=re.I)
    t = re.sub(r"%mes pasado%", "el mes pasado", t, flags=re.I)
    t = re.sub(r"%[^%]*%", "", t)
    t = re.sub(r"^[^\wÁÉÍÓÚáéíóúÑñ¿¡]+", "", t)
    if t.lower().startswith(v.lower() + "."):
        t = t[len(v) + 1:]
    m = re.match(r"([A-Za-z]+)(\d+)\S*\s+", t)
    if m and v.lower().startswith((m.group(1) + m.group(2)).lower()):
        t = t[m.end():]
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"¿\s+", "¿", t).strip(" .")
    return t or v


def limpia(s, vl):
    """Lista de (sufijo, categoría, serie, tipo) para una variable."""
    s = pd.to_numeric(s, errors="coerce").astype(float)
    if vl:
        perd = [k for k, v in vl.items() if PERDIDO.search(str(v))]
        s = s.where(~s.isin(perd))
        validos = {k: v for k, v in vl.items() if k not in perd}
    else:
        s = s.where(s >= 0)
        resto = s[~s.isin(CENTINELAS)].dropna()
        if len(resto):
            tope = resto.quantile(0.99)
            s = s.where(~(s.isin(CENTINELAS) & (s > 2 * tope)))
        validos = {}
    vals = sorted(s.dropna().unique())
    if len(vals) < 2:
        return []
    if len(vals) == 2:
        a, b = vals
        la, lb = str(validos.get(a, "")), str(validos.get(b, ""))
        uno = b
        if re.match(r"\W*(\d+\W*)?(no\b|no marcad)", lb, re.I) or \
                re.match(r"\W*(\d+\W*)?s[ií]\b", la, re.I):
            uno = a
        cat = str(validos.get(uno, ""))
        return [("", cat if cat and not re.match(r"\W*(\d+\W*)?s[ií]\b",
                                                 cat, re.I) else "",
                 (s == uno).astype(float).where(s.notna()), "dicotómica")]
    con_etiqueta = [v for v in vals if v in validos]
    if vl and len(con_etiqueta) >= 3 and \
            len(con_etiqueta) >= 0.8 * len(vals):
        textos = [re.sub(r"^\s*\d+\s*[\.\)-]\s*", "", str(validos[v]))
                  for v in con_etiqueta]
        orden = sum(bool(ORDEN.search(x)) or not re.sub(r"[\W_]+", "", x)
                    for x in textos)
        if orden >= 0.6 * len(textos):
            return [("", "", s, "ordinal")]
        out = []
        for v in con_etiqueta:
            dm = (s == v).astype(float).where(s.notna())
            if 0.03 <= dm.mean() <= 0.97:
                out.append((f"_c{int(v)}", str(validos[v]), dm, "categoría"))
        return out
    return [("", "", s, "continua")]


def lee(nombre):
    df, m = pyreadstat.read_dta(BASE / nombre)
    df["folio"] = pd.to_numeric(df.folio, errors="coerce")
    return df.dropna(subset=["folio"]).astype({"folio": "int64"}), m


def candidatas(df, m):
    out = []
    for c in df.columns:
        lab = m.column_names_to_labels.get(c)
        if FUERA_NOMBRE.search(c) or FUERA_ETIQUETA.search(str(lab or "")):
            continue
        if df[c].dtype == object:
            continue
        out.append(c)
    return out


def bases():
    """Diccionario base -> (DataFrame por folio, metadatos)."""
    A, ma = lee("Base adolescentes Stata.dta")
    E, me = lee("Base evaluaciones Stata.dta")
    R, mr = lee("Base responsable principal Stata.dta")
    A = A.drop_duplicates("folio").set_index("folio")
    E = E.drop_duplicates("folio").set_index("folio")
    cols = candidatas(R, mr)
    g = R.groupby("folio")
    varia = {c: (g[c].nunique(dropna=True) > 1).mean() for c in cols}
    hogar = [c for c in cols if varia[c] <= 0.02]
    persona = [c for c in cols if varia[c] > 0.02]
    H = g[hogar].first()
    ad = R[R.tipo_persona == 1].drop_duplicates("folio").set_index("folio")
    cu = R[R.tipo_persona == 2].drop_duplicates("folio").set_index("folio")
    P = pd.concat([ad[persona].add_suffix("_adol"),
                   cu[persona].add_suffix("_cuid")], axis=1)
    P = P.drop(columns=[c for c in ("sexo_adol", "edad_adol") if c in P])
    RR = pd.concat([H, P], axis=1)
    vl, lab = dict(mr.variable_value_labels), dict(mr.column_names_to_labels)
    for c in persona:
        for suf, quien in (("_adol", "adolescente"), ("_cuid", "cuidador")):
            vl[c + suf] = mr.variable_value_labels.get(c)
            lab[c + suf] = f"{lab.get(c)} [{quien}]"
    return {"A": (A[candidatas(A, ma)], ma.variable_value_labels,
                  ma.column_names_to_labels),
            "E": (E[candidatas(E, me)], me.variable_value_labels,
                  me.column_names_to_labels),
            "R": (RR, vl, lab)}


def construye():
    d, _, _ = p15.load_data()
    muestra = d[(d.w > 0) & d.edadq_m.between(6, 49)].folio
    filas, columnas = [], {}
    for base, (df, vls, labs) in bases().items():
        df = df[df.index.isin(set(muestra))]
        for c in df.columns:
            for suf, cat, serie, tipo in limpia(df[c], vls.get(c)):
                if serie.notna().sum() < MIN_N or serie.std() == 0:
                    continue
                k = f"v{len(filas):04d}"
                columnas[k] = serie
                gi, gn = grupo(base, c)
                filas.append({"id": k, "base": base, "variable": c + suf,
                              "grupo_orden": gi, "grupo": gn,
                              "etiqueta": etiqueta(c, labs.get(c)),
                              "categoria": cat, "tipo": tipo,
                              "n": int(serie.notna().sum())})
    X = pd.DataFrame(columnas)
    X.index.name = "folio"
    return d.merge(X.reset_index(), on="folio", how="left"), pd.DataFrame(filas)


D = None
Y = None


def estima(k):
    try:
        b, n = p33.perfil(D.assign(**{k: Y[k]}), k, None, "paper")
        return k, n, {t: b[t][:3] for t in TRAMOS}
    except Exception as e:  # noqa: BLE001
        return k, 0, str(e)


# ------------------------------------------------------------------ mapa
for f in font_manager.findSystemFonts([str(HERE / "fonts")]):
    font_manager.fontManager.addfont(f)
MM = 1 / 25.4
CMAP = LinearSegmentedColormap.from_list(
    "dano", ["#2a78d6", "#f1f0ec", "#eb6834"])
FILAS_COL = 40


def corta(t, n):
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


def paginas(res):
    """Filas del mapa (cabeceras de grupo y variables), en columnas de
    FILAS_COL filas y dos columnas por página."""
    filas = []
    for (_, gn), g in res.groupby(["grupo_orden", "grupo"], sort=True):
        filas.append(("grupo", gn, None))
        inicio = g.etiqueta.str[:40].value_counts()
        for _, r in g.iterrows():
            txt = r.etiqueta
            if len(txt) > 60 and inicio[txt[:40]] > 1:
                txt = "…" + txt[-58:]
            txt += f" = {r.categoria}" if r.categoria else ""
            filas.append(("var", txt, r))
    cols = [filas[i:i + FILAS_COL] for i in range(0, len(filas), FILAS_COL)]
    return [cols[i:i + 2] for i in range(0, len(cols), 2)]


def dibuja(col, ax):
    ax.set_xlim(-14.4, 3.2)
    ax.set_ylim(FILAS_COL - 0.5, -2.2)
    ax.axis("off")
    for j, c in enumerate(COLUMNAS):
        ax.text(j + 0.47, -1.15, c, ha="center", va="center", fontsize=4.2,
                color="#55606B", linespacing=0.9)
    for i, (tipo, txt, r) in enumerate(col):
        if tipo == "grupo":
            ax.text(-0.25, i, txt, ha="right", va="center", fontsize=4.6,
                    fontweight="semibold", color="#17212B")
            continue
        ax.text(-14.3, i, r.variable, ha="left", va="center",
                fontsize=3.4, color="#8A939C")
        ax.text(-0.25, i, corta(txt, 60), ha="right", va="center",
                fontsize=4.3, color="#17212B")
        for j, t in enumerate(TRAMOS):
            b, se, p = r[f"b_{t}"], r[f"se_{t}"], r[f"p_{t}"]
            if not np.isfinite(b) or not np.isfinite(se) or se == 0:
                continue
            tt = np.clip(b / se, -3, 3)
            ax.add_patch(plt.Rectangle((j, i - 0.44), 0.94, 0.88, lw=0,
                                       color=CMAP((tt + 3) / 6)))
            st = stars(p)
            if st:
                ax.text(j + 0.47, i + 0.05, st, ha="center", va="center",
                        fontsize=3.6, color="#17212B")


def mapas(res, carpeta):
    paths = []
    with plt.rc_context({"font.family": "IBM Plex Sans", "pdf.fonttype": 42}):
        for k, pag in enumerate(paginas(res), start=1):
            f = plt.figure(figsize=(144 * MM, 76 * MM))
            for j, col in enumerate(pag):
                ax = f.add_axes([0.005 + 0.5 * j, 0.0, 0.49, 1.0])
                dibuja(col, ax)
            p = carpeta / f"todo_2024_{k:02d}.pdf"
            f.savefig(p)
            plt.close(f)
            paths.append(p)
    return paths


def main():
    global D, Y
    log("# Todas las variables de la ELPI 2024 por edad al terremoto "
        "(scripts/37_todo_2024.py)")
    todo, meta = construye()
    Y = todo[list(meta.id)]
    D = todo.drop(columns=list(meta.id))
    nvar = meta.variable.str.replace(r"_c\d+$", "", regex=True).nunique()
    log(f"Resultados: {len(meta)} (variables y categorías) de {nvar} "
        f"variables; por base: "
        + ", ".join(f"{b} {n}" for b, n in meta.base.value_counts().items()))
    with Pool(4) as pool:
        salida = pool.map(estima, list(meta.id), chunksize=4)
    filas = []
    for k, n, r in salida:
        fila = {"id": k, "n_est": n}
        for t in TRAMOS:
            b, se, p = r[t] if isinstance(r, dict) else (np.nan,) * 3
            fila.update({f"b_{t}": b, f"se_{t}": se, f"p_{t}": p})
        filas.append(fila)
    res = meta.merge(pd.DataFrame(filas), on="id")
    res = res[res.n_est > 0].sort_values(["grupo_orden", "id"])
    res.to_csv("reports/todo_2024.csv", index=False)
    log(f"\nEstimados: {len(res)}. Frente a quienes tenían 2 años, zona "
        "afectada menos no afectada; columna 3 de la Table 3.")
    for t, lab in zip(TRAMOS, ["6-11 meses", "1 año", "3-4 años"]):
        p = res[f"p_{t}"]
        log(f"- {lab}: p<0,05 en {(p < 0.05).sum()} de {p.notna().sum()} "
            f"({100 * (p < 0.05).mean():.1f} %; por azar, 5 %); p<0,01 en "
            f"{(p < 0.01).sum()}")
    log("\nLas 30 con mayor |t| en algún tramo:")
    res["tmax"] = np.nanmax(np.abs(np.column_stack(
        [res[f"b_{t}"] / res[f"se_{t}"] for t in TRAMOS])), axis=1)
    for _, r in res.nlargest(30, "tmax").iterrows():
        txt = r.etiqueta + (f" = {r.categoria}" if r.categoria else "")
        log(f"- [{r.base}] {r.variable}: {corta(txt, 70)} | " + " | ".join(
            f"{t} {r[f'b_{t}']:+.3f}{stars(r[f'p_{t}'])}" for t in TRAMOS)
            + f" | N={r.n_est}")
    paths = mapas(res, Path("presentacion/figuras"))
    log(f"\nPáginas del mapa: {len(paths)}")
    Path("reports/todo_2024.md").write_text("\n".join(OUT) + "\n",
                                            encoding="utf-8")
    print("-> reports/todo_2024.md, reports/todo_2024.csv")


if __name__ == "__main__":
    main()
