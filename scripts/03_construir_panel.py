#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construye la base panel de niños/as de la ELPI enlazando las 4 rondas
(2010, 2012, 2017 y 2024) a través de la variable llave `folio`.

`folio` identifica al niño/a seleccionado/a (y su entrevista) y es estable
entre rondas; así lo establece el documento oficial "Uso de la Base de Datos
ELPI 2024" (data/raw/2024/Uso_de_base_de_datos_ELPI_2024.pdf): el enlace con
rondas anteriores "se realiza a través de la variable llave folio".

Insumos (generados por 01_descargar_elpi.py + 02_verificar_archivos.py):
    data/interim/2010/  Entrevistada, Hogar, Evaluaciones (.dta)
    data/interim/2012/  Entrevistada, Hogar, Evaluaciones (.dta)
    data/interim/2017/  Cuidador Principal (.dta), Evaluaciones (.dta),
                        Niños y Niñas (.sav), Factores longitudinales (.sav)
    data/interim/2024/  Responsable principal, Adolescentes, Evaluaciones (.dta)

Productos:
    data/processed/elpi_panel_ninos_largo.csv|.dta
        1 fila por niño/a (folio) x ronda en que su hogar participó, con
        indicadores de participación por instrumento, sexo, edad, región,
        comuna, área y factores de expansión transversales.
    data/processed/elpi_panel_ninos_ancho.csv|.dta
        1 fila por niño/a (folio) con flags de participación por ronda,
        patrón de participación (p.ej. "1011"), muestra de origen y
        factores de expansión longitudinales (2012, 2017 y 2024).
    reports/panel_resumen.md
        Verificaciones y conteos (cobertura por ronda, patrones, consistencia).

Uso:
    python3 scripts/03_construir_panel.py
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

INTERIM = Path("data/interim")
OUT = Path("data/processed")
REPORTE = Path("reports/panel_resumen.md")

RONDAS = [2010, 2012, 2017, 2024]


def leer(ruta: Path, cols=None) -> pd.DataFrame:
    """Lee .dta/.sav; con fallback a pandas para .dta con codificación latin-1."""
    ruta = str(ruta)
    if ruta.endswith(".sav"):
        df, _ = pyreadstat.read_sav(ruta, usecols=cols)
        return df
    try:
        df, _ = pyreadstat.read_dta(ruta, usecols=cols)
        return df
    except Exception:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # etiquetas latin-1 en dta antiguos
            return pd.read_stata(ruta, columns=cols, convert_categoricals=False)


def folio_int(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="raise").astype("int64")


def limpiar_edad(s: pd.Series, tope: int = 98) -> pd.Series:
    """Edad en años; 99/999 = no sabe/no responde -> NaN."""
    x = pd.to_numeric(s, errors="coerce")
    return x.where((x >= 0) & (x < tope))


def unica_por_folio(df: pd.DataFrame, nombre: str, avisos: list) -> pd.DataFrame:
    dup = df.folio.duplicated().sum()
    if dup:
        avisos.append(f"AVISO: {nombre}: {dup} folios duplicados; se conserva la primera fila.")
        df = df.drop_duplicates("folio", keep="first")
    return df


# --------------------------------------------------------------------------
# Extracción por ronda: devuelve (panel_ronda, extras_ancho)
# --------------------------------------------------------------------------

def ronda_2010(avisos):
    d = INTERIM / "2010"
    ent = leer(d / "Entrevistada_2010.dta", ["folio", "region", "area", "fexp_enc"])
    hog = leer(d / "Hogar_2010.dta", ["folio", "a16", "a18", "a19"])
    eva = leer(d / "Evaluaciones_2010.dta", ["folio", "edad_meses", "fexp_test"])
    for df in (ent, hog, eva):
        df["folio"] = folio_int(df.folio)

    # fila del niño/a seleccionado/a en el roster del hogar (a16 == 13)
    nino = hog.loc[hog.a16 == 13, ["folio", "a18", "a19"]].rename(
        columns={"a18": "sexo", "a19": "edad_anios"})
    nino = unica_por_folio(nino, "Hogar_2010 (niño seleccionado)", avisos)
    nino["edad_anios"] = limpiar_edad(nino.edad_anios)

    ent = unica_por_folio(ent, "Entrevistada_2010", avisos)
    eva = unica_por_folio(eva, "Evaluaciones_2010", avisos)

    base = ent.assign(en_encuesta=1).merge(nino, on="folio", how="outer")
    base = base.merge(eva.assign(en_evaluaciones=1), on="folio", how="outer")
    base["ronda"] = 2010
    base = base.rename(columns={"fexp_enc": "fexp_transversal_enc",
                                "fexp_test": "fexp_transversal_eval",
                                "edad_meses": "edad_meses_eval"})
    base["en_cuestionario_nino"] = np.nan  # instrumento inexistente en 2010
    return base, None


def ronda_2012(avisos):
    d = INTERIM / "2012"
    ent = leer(d / "Entrevistada_2012.dta",
               ["folio", "region", "area", "muestra", "fexp_enc0", "fexp_encP"])
    hog = leer(d / "Hogar_2012.dta", ["folio", "i2", "i4", "i1"])
    eva = leer(d / "Evaluaciones_2012.dta",
               ["folio", "edad_meses", "fexp_test0", "fexp_testP"])
    for df in (ent, hog, eva):
        df["folio"] = folio_int(df.folio)

    nino = hog.loc[hog.i2 == 13, ["folio", "i4", "i1"]].rename(
        columns={"i4": "sexo", "i1": "edad_anios"})
    nino = unica_por_folio(nino, "Hogar_2012 (niño seleccionado)", avisos)
    nino["edad_anios"] = limpiar_edad(nino.edad_anios)

    ent = unica_por_folio(ent, "Entrevistada_2012", avisos)
    eva = unica_por_folio(eva, "Evaluaciones_2012", avisos)

    base = ent.assign(en_encuesta=1).merge(nino, on="folio", how="outer")
    base = base.merge(eva.assign(en_evaluaciones=1), on="folio", how="outer")
    base["ronda"] = 2012
    base = base.rename(columns={"fexp_enc0": "fexp_transversal_enc",
                                "fexp_test0": "fexp_transversal_eval",
                                "edad_meses": "edad_meses_eval"})
    base["en_cuestionario_nino"] = np.nan

    extras = base[["folio", "muestra", "fexp_encP", "fexp_testP"]].rename(
        columns={"muestra": "muestra_2012",
                 "fexp_encP": "fexp_encP_2012",
                 "fexp_testP": "fexp_testP_2012"})
    base = base.drop(columns=["fexp_encP", "fexp_testP"])
    return base, extras


def ronda_2017(avisos):
    d = INTERIM / "2017"
    cui = leer(d / "Base_Cuidador_Principal_ELPI_III(STATA)_241010.dta",
               ["folio", "idencuesta", "tipopersona", "espanel", "idregion",
                "idcomuna", "estrato", "h2", "h3", "fexp_enc0_2", "fexp_eva0_2"])
    eva = leer(d / "Base Evaluaciones ELPI III.dta",
               ["folio", "espanel", "sexo", "edad_mesesr", "idregion",
                "idcomuna", "estrato", "fexp_enc0_2", "fexp_eva0_2"])
    nyn = leer(d / "Base Niños y Niñas ELPI III (SPSS).sav", ["folio", "sexo", "edad"])
    fac = leer(d / "Factores de expansion longitudinales ELPI III (SPSS).sav")
    for df in (cui, eva, nyn, fac):
        col = "idencuesta" if "idencuesta" in df.columns and "folio" not in df.columns else "folio"
        df[col] = folio_int(df[col])

    # nivel entrevista/hogar: una fila por folio; datos del niño desde su
    # fila de roster (tipopersona == 1 "Niño seleccionado(a)")
    hogar = cui.drop_duplicates("folio")[
        ["folio", "idencuesta", "espanel", "idregion", "idcomuna", "estrato",
         "fexp_enc0_2", "fexp_eva0_2"]]
    nino = cui.loc[cui.tipopersona == 1, ["folio", "h2", "h3"]].rename(
        columns={"h2": "sexo", "h3": "edad_anios"})
    nino = unica_por_folio(nino, "Cuidador_2017 (fila del niño)", avisos)
    nino["edad_anios"] = limpiar_edad(nino.edad_anios)

    # verificación del mapeo folio <-> idencuesta (llave de los factores long.)
    cui["idencuesta"] = folio_int(cui.idencuesta)
    m = cui.drop_duplicates("folio")[["folio", "idencuesta"]]
    if m.idencuesta.duplicated().any() or (m.idencuesta != m.folio // 10).any():
        avisos.append("AVISO: 2017: idencuesta no es exactamente folio//10 o no es 1:1 con folio.")

    eva = unica_por_folio(eva, "Evaluaciones_2017", avisos)
    nyn = unica_por_folio(nyn, "NinosNinas_2017", avisos)

    base = hogar.assign(en_encuesta=1).merge(
        nino, on="folio", how="outer")
    base = base.merge(
        eva[["folio", "sexo", "edad_mesesr", "idregion", "idcomuna", "estrato",
             "fexp_enc0_2", "fexp_eva0_2"]].assign(en_evaluaciones=1),
        on="folio", how="outer", suffixes=("", "_eva"))
    base = base.merge(nyn[["folio"]].assign(en_cuestionario_nino=1),
                      on="folio", how="outer")

    # completar con la base de evaluaciones lo que falte a nivel hogar
    for c in ("sexo", "idregion", "idcomuna", "estrato", "fexp_enc0_2", "fexp_eva0_2"):
        ce = f"{c}_eva"
        if ce in base.columns:
            base[c] = base[c].fillna(base[ce])
            base = base.drop(columns=[ce])

    base["ronda"] = 2017
    base = base.rename(columns={"idregion": "region", "idcomuna": "comuna",
                                "edad_mesesr": "edad_meses_eval",
                                "fexp_enc0_2": "fexp_transversal_enc",
                                "fexp_eva0_2": "fexp_transversal_eval"})

    # factores longitudinales 2017 (llave idencuesta = folio // 10)
    fac = fac.rename(columns={c: f"{c}_2017" for c in fac.columns if c != "idencuesta"})
    extras = base[["folio", "espanel"]].rename(columns={"espanel": "espanel_2017"})
    extras["idencuesta"] = extras.folio // 10
    extras = extras.merge(fac, on="idencuesta", how="left", indicator=True)
    sin_cruce = int((extras["_merge"] != "both").sum())
    if sin_cruce:
        avisos.append(f"AVISO: 2017: {sin_cruce} folios no cruzan con el archivo de "
                      "factores de expansión longitudinales.")
    # Nota: dentro del archivo de factores, cada fexp_*P es no nulo solo para la
    # submuestra panel a la que aplica (p.ej. fexp_encP: panel 2010-2012-2017);
    # los NaN restantes son de diseño, no errores de cruce.
    extras = extras.drop(columns=["idencuesta", "_merge"])
    base = base.drop(columns=["espanel", "idencuesta"], errors="ignore")
    return base, extras


def ronda_2024(avisos):
    d = INTERIM / "2024"
    res = leer(d / "Base responsable principal Stata.dta",
               ["folio", "tipo_persona", "sexo", "edad", "cod_region", "cod_comuna",
                "estrato", "f_exp", "f_exp_1024", "f_exp_101224", "f_exp_101724",
                "f_exp_10121724"])
    ado = leer(d / "Base adolescentes Stata.dta", ["folio"])
    eva = leer(d / "Base evaluaciones Stata.dta", ["folio"])
    for df in (res, ado, eva):
        df["folio"] = folio_int(df.folio)

    hogar = res.drop_duplicates("folio")[
        ["folio", "cod_region", "cod_comuna", "estrato", "f_exp", "f_exp_1024",
         "f_exp_101224", "f_exp_101724", "f_exp_10121724"]]
    # fila de roster del/de la adolescente seleccionado/a (tipo_persona == 1)
    nino = res.loc[res.tipo_persona == 1, ["folio", "sexo", "edad"]].rename(
        columns={"edad": "edad_anios"})
    nino = unica_por_folio(nino, "RespPrincipal_2024 (fila adolescente)", avisos)
    nino["edad_anios"] = limpiar_edad(nino.edad_anios)

    ado = unica_por_folio(ado, "Adolescentes_2024", avisos)
    eva = unica_por_folio(eva, "Evaluaciones_2024", avisos)

    base = hogar.assign(en_encuesta=1).merge(nino, on="folio", how="outer")
    base = base.merge(eva.assign(en_evaluaciones=1), on="folio", how="outer")
    base = base.merge(ado.assign(en_cuestionario_nino=1), on="folio", how="outer")
    base["ronda"] = 2024
    base = base.rename(columns={"cod_region": "region", "cod_comuna": "comuna",
                                "f_exp": "fexp_transversal_enc"})
    base["fexp_transversal_eval"] = base["fexp_transversal_enc"]
    base["edad_meses_eval"] = np.nan  # 2024 no publica edad en meses en evaluaciones

    extras = base[["folio", "f_exp_1024", "f_exp_101224", "f_exp_101724",
                   "f_exp_10121724"]].copy()
    base = base.drop(columns=["f_exp_1024", "f_exp_101224", "f_exp_101724",
                              "f_exp_10121724"])
    return base, extras


# --------------------------------------------------------------------------

COLS_LARGO = ["folio", "ronda", "en_encuesta", "en_evaluaciones",
              "en_cuestionario_nino", "sexo", "edad_anios", "edad_meses_eval",
              "region", "comuna", "area", "estrato",
              "fexp_transversal_enc", "fexp_transversal_eval"]

ETIQUETAS_LARGO = {
    "folio": "Identificador del niño/a seleccionado/a (llave entre rondas)",
    "ronda": "Ronda ELPI (año)",
    "en_encuesta": "1 = hogar con entrevista/encuesta en la ronda",
    "en_evaluaciones": "1 = niño/a en base de evaluaciones de la ronda",
    "en_cuestionario_nino": "1 = respondió cuestionario propio (NyN 2017 / Adolescentes 2024)",
    "sexo": "Sexo del niño/a (1 hombre, 2 mujer; reporte de la ronda)",
    "edad_anios": "Edad en años (roster del hogar de la ronda)",
    "edad_meses_eval": "Edad en meses en evaluaciones (no publicada en 2024)",
    "region": "Región (códigos vigentes en cada ronda)",
    "comuna": "Comuna (solo 2017 y 2024)",
    "area": "Área urbano/rural (solo 2010 y 2012)",
    "estrato": "Estrato de diseño muestral - comuna de selección (solo 2017 y 2024)",
    "fexp_transversal_enc": "Factor de expansión transversal - entrevista/encuesta",
    "fexp_transversal_eval": "Factor de expansión transversal - evaluaciones",
}


def main() -> int:
    avisos: list[str] = []
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTE.parent.mkdir(parents=True, exist_ok=True)

    partes, extras = {}, {}
    partes[2010], _ = ronda_2010(avisos)
    partes[2012], extras[2012] = ronda_2012(avisos)
    partes[2017], extras[2017] = ronda_2017(avisos)
    partes[2024], extras[2024] = ronda_2024(avisos)

    for r in RONDAS:
        for c in COLS_LARGO:
            if c not in partes[r].columns:
                partes[r][c] = np.nan
        partes[r] = partes[r][COLS_LARGO]
        assert partes[r].folio.is_unique, f"folio duplicado en panel {r}"

    largo = pd.concat(partes.values(), ignore_index=True)
    for c in ("en_encuesta", "en_evaluaciones", "en_cuestionario_nino"):
        largo[c] = largo[c].fillna(0).astype("int8") if c != "en_cuestionario_nino" \
            else largo[c].where(largo.ronda.isin([2017, 2024]), np.nan)
    largo.loc[largo.ronda.isin([2017, 2024]), "en_cuestionario_nino"] = (
        largo.loc[largo.ronda.isin([2017, 2024]), "en_cuestionario_nino"].fillna(0))
    largo = largo.sort_values(["folio", "ronda"]).reset_index(drop=True)

    # ----------------- base ancha (1 fila por niño/a) -----------------
    ancho = pd.DataFrame({"folio": np.sort(largo.folio.unique())})
    for r in RONDAS:
        p = partes[r]
        ancho[f"en_{r}"] = ancho.folio.isin(p.folio).astype("int8")
        ancho[f"en_eval_{r}"] = ancho.folio.isin(
            p.loc[p.en_evaluaciones == 1, "folio"]).astype("int8")
    ancho["n_rondas"] = ancho[[f"en_{r}" for r in RONDAS]].sum(axis=1).astype("int8")
    ancho["patron_participacion"] = (
        ancho[[f"en_{r}" for r in RONDAS]].astype(str).agg("".join, axis=1))

    # muestra de origen del niño/a
    ancho["muestra_origen"] = np.select(
        [ancho.en_2010 == 1, ancho.en_2012 == 1],
        ["original_2010", "refresco_2012"], default="refresco_2017")

    # sexo: primer valor no nulo entre rondas + chequeo de consistencia
    sx = largo.pivot(index="folio", columns="ronda", values="sexo")
    sexo_consistente = sx.apply(lambda f: f.dropna().nunique() <= 1, axis=1)
    ancho = ancho.merge(
        sx.bfill(axis=1).iloc[:, 0].rename("sexo").reset_index(), on="folio", how="left")
    ancho = ancho.merge(
        sexo_consistente.rename("sexo_consistente").astype("int8").reset_index(),
        on="folio", how="left")

    for r in (2012, 2017, 2024):
        ancho = ancho.merge(extras[r], on="folio", how="left")

    # ----------------- verificaciones para el informe -----------------
    en = {r: set(partes[r].folio) for r in RONDAS}
    checks = [
        f"- Niños/as (folios) distintos en el panel: **{len(ancho):,}**",
        f"- Por ronda: " + ", ".join(f"{r}: {len(en[r]):,}" for r in RONDAS),
        f"- 2012∩2010: {len(en[2012] & en[2010]):,} "
        f"(muestra==1 en 2012: {int((extras[2012].muestra_2012 == 1).sum()):,})",
        f"- 2017∩(2010∪2012): {len(en[2017] & (en[2010] | en[2012])):,} "
        f"(espanel==1: {int((extras[2017].espanel_2017 == 1).sum()):,})",
        f"- 2024⊂2010: {'sí' if en[2024] <= en[2010] else 'NO'} "
        f"({len(en[2024] & en[2010]):,} de {len(en[2024]):,})",
        f"- Presentes en las 4 rondas: {len(en[2010] & en[2012] & en[2017] & en[2024]):,}",
        f"- Sexo consistente entre rondas: {int(ancho.sexo_consistente.sum()):,} "
        f"({ancho.sexo_consistente.mean():.1%}); el resto presenta discrepancias "
        "de reporte entre rondas y se deja tal cual (columna `sexo_consistente`).",
    ]

    patrones = (ancho.patron_participacion.value_counts()
                .rename_axis("patron").reset_index(name="n"))

    # ----------------- salidas -----------------
    largo.to_csv(OUT / "elpi_panel_ninos_largo.csv", index=False)
    ancho.to_csv(OUT / "elpi_panel_ninos_ancho.csv", index=False)

    # .dta (Stata 14+, UTF-8); mismos datos que el CSV
    et_ancho = {
        "folio": ETIQUETAS_LARGO["folio"],
        "n_rondas": "N.º de rondas con participación del hogar",
        "patron_participacion": "Participación 2010-2012-2017-2024 (1/0)",
        "muestra_origen": "Muestra de ingreso del niño/a al estudio",
        "sexo": "Sexo (primer reporte no nulo entre rondas)",
        "sexo_consistente": "1 = mismo sexo reportado en todas sus rondas",
        "muestra_2012": "2012: 1 panel, 2 refresco",
        "espanel_2017": "2017: 1 pertenece a muestra panel",
    }
    largo_dta = largo.copy()
    largo_dta.columns = [c[:32] for c in largo_dta.columns]
    largo_dta.to_stata(OUT / "elpi_panel_ninos_largo.dta", write_index=False,
                       version=118, variable_labels=ETIQUETAS_LARGO)
    ancho_dta = ancho.copy()
    ancho_dta.to_stata(OUT / "elpi_panel_ninos_ancho.dta", write_index=False,
                       version=118,
                       variable_labels={k: v for k, v in et_ancho.items()
                                        if k in ancho_dta.columns})

    # ----------------- informe -----------------
    lineas = [
        "# Base panel ELPI 2010-2012-2017-2024: resumen y verificaciones",
        "",
        f"Generado por `scripts/03_construir_panel.py` el {date.today().isoformat()}.",
        "",
        "Llave de enlace: `folio` (identificador del niño/a seleccionado/a, estable",
        "entre rondas según el documento oficial *Uso de la Base de Datos ELPI 2024*).",
        "",
        "## Verificaciones",
        "",
        *checks,
        "",
        "## Patrones de participación (2010-2012-2017-2024)",
        "",
        "| Patrón | N niños/as |",
        "|---|---:|",
        *[f"| {p.patron} | {p.n:,} |" for p in patrones.itertuples()],
        "",
        "## Avisos",
        "",
        *(avisos or ["Sin avisos."]),
        "",
        "## Archivos generados",
        "",
        "| Archivo | Filas | Columnas |",
        "|---|---:|---:|",
        f"| `data/processed/elpi_panel_ninos_largo.csv/.dta` | {len(largo):,} | {len(largo.columns)} |",
        f"| `data/processed/elpi_panel_ninos_ancho.csv/.dta` | {len(ancho):,} | {len(ancho.columns)} |",
        "",
    ]
    REPORTE.write_text("\n".join(lineas), encoding="utf-8")

    print("\n".join(checks))
    print(f"\nPanel largo : {len(largo):,} filas x {len(largo.columns)} col")
    print(f"Panel ancho : {len(ancho):,} filas x {len(ancho.columns)} col")
    print(f"Informe     : {REPORTE}")
    if avisos:
        print("\n".join(avisos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
