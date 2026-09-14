#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descarga las bases de datos públicas y libros de códigos de la ELPI
(Encuesta Longitudinal de Primera Infancia, Chile) para sus 4 rondas:
2010 (I), 2012 (II), 2017 (III) y 2024 (IV).

Fuente oficial (Observatorio Social, Ministerio de Desarrollo Social y Familia):
  https://observatorio.ministeriodesarrollosocial.gob.cl/elpi
  - Primera ronda : https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-primera-ronda
  - Segunda ronda : https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-segunda-ronda
  - Tercera ronda : https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-tercera-ronda
  - Cuarta ronda  : https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-cuarta-ronda

Los mismos estudios están publicados como datos abiertos (CC BY 4.0, sin
registro) en BIDAT, el Banco Integrado de Datos del Ministerio
(https://bidat.gob.cl/ ; bidat.midesof.cl redirige allí). Se usa el
Observatorio como fuente de descarga porque sus URLs son estables y
directas; los enlaces de descarga de BIDAT son tokens opacos generados por
la plataforma y no sirven para un script reproducible (ver README.md).

Notas:
  * 2010 y 2012 no tienen "libro de códigos" separado: la documentación de
    variables está en el Manual de Usuario de la Base de Datos de cada ronda.
  * Se descargan TODOS los formatos publicados de cada base de microdatos
    (Stata .dta, SPSS .sav y, en 2024, R .rds). En 2017 las bases "Niños y
    Niñas", "Segundo Cuidador" y los factores de expansión longitudinales
    solo se publican en .rar para Stata; extraer .rar requiere 7-Zip/unar
    (el script 02 lo hace si detecta la herramienta), por lo que las
    versiones SPSS (.sav.zip) siguen siendo la vía sin dependencias extra.
  * Se descargan además los informes metodológicos de cada ronda
    (categoría "metodologia").
  * Todas las URLs se registran tal como aparecen en el sitio; los espacios,
    paréntesis y caracteres acentuados se codifican (percent-encoding) al
    momento de la petición.

Uso:
    python3 scripts/01_descargar_elpi.py [--dest data/raw] [--solo-verificar]

    --solo-verificar : no descarga; comprueba existencia/tamaño de lo ya bajado.
"""
import argparse
import hashlib
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://observatorio.ministeriodesarrollosocial.gob.cl/storage/docs/elpi"

# (subruta_remota, subcarpeta_local, categoria)
# categoria: "base" (base de datos), "codigo" (libro de códigos / manual de usuario),
#            "doc" (documentación complementaria: cuestionario, ficha técnica),
#            "metodologia" (informes metodológicos y de diseño)
ARCHIVOS = [
    # ---------------- Ronda 1 - 2010 (formato Stata) ----------------
    ("2010/Hogar_2010.dta.zip",                          "2010", "base"),
    ("2010/Entrevistada_2010.dta.zip",                   "2010", "base"),
    ("2010/Evaluaciones_2010.dta.zip",                   "2010", "base"),
    ("2010/Cuidado_infantil_2010.dta.zip",               "2010", "base"),
    ("2010/Evaluaciones2010_items_test.dta.zip",         "2010", "base"),
    ("2010/Manual_Usuario_Base_de_Datos_ELPI_2010.pdf",  "2010", "codigo"),
    ("2010/Encuesta_ELPI_2010.pdf",                      "2010", "doc"),
    # 2010 no publica informe metodológico separado; el diseño y el trabajo de
    # campo se documentan en el Manual de Usuario y en el informe de resultados:
    ("2010/Informe_Resultados_Encuesta_2010.pdf",        "2010", "metodologia"),
    ("WEB_Informacion_ELPI.pdf",                         ".",    "metodologia"),

    # ---------------- Ronda 2 - 2012 (formato Stata) ----------------
    ("2012/Hogar_2012.dta.zip",                          "2012", "base"),
    ("2012/Entrevistada_2012.dta.zip",                   "2012", "base"),
    ("2012/Evaluaciones_2012.dta.zip",                   "2012", "base"),
    ("2012/Cuidado_infantil_2012.dta.zip",               "2012", "base"),
    ("2012/Historia_Laboral_2012.dta.zip",               "2012", "base"),
    ("2012/Evaluaciones2012_items_test.dta.zip",         "2012", "base"),
    ("2012/Manual_Usuario_Base_de_Datos_ELPI_2012.pdf",  "2012", "codigo"),
    ("2012/Cuestionario_ELPI_2012_Cuidador_Principal.pdf", "2012", "doc"),
    ("2012/Informe_Resultados_Encuesta_Hogares_2012.pdf", "2012", "metodologia"),

    # ---------------- Ronda 3 - 2017 ----------------
    # Cuidador principal: versión Stata corregida publicada el 2024-10-10
    # (es la enlazada en la página oficial de la tercera ronda).
    ("2017/Base_Cuidador_Principal_ELPI_III(STATA)_241010.dta.zip", "2017", "base"),
    ("2017/Base_Cuidador_Principal_ELPI_III_(SPSS).sav.zip",        "2017", "base"),
    ("2017/Base Evaluaciones ELPI III.dta.zip",                     "2017", "base"),
    ("2017/Base Evaluaciones ELPI III.sav.zip",                     "2017", "base"),
    ("2017/Base_Niños_y_Niñas_ELPI_III_(SPSS).sav.zip",             "2017", "base"),
    ("2017/Base_Ninos_y_Ninas_ELPI_III.rar",                        "2017", "base"),
    ("2017/Base_Segundo_Cuidador_Principal_ELPI_III_(SPSS).sav.zip","2017", "base"),
    ("2017/Base_Segundo_Cuidador_Principal_ELPI_III.rar",           "2017", "base"),
    ("2017/Factores_de_expansion_longitudinales_ELPI_III_(SPSS).sav.zip", "2017", "base"),
    ("2017/factores_de_expansion_longitudinales_ELPI_III.rar",      "2017", "base"),
    # Libros de códigos (uno por base) y manual de usuario:
    ("2017/Libro_de_código_Cuidador_Principal_ELPI_III.pdf",        "2017", "codigo"),
    ("2017/Libro_de_código_Niños_y_Niñas_ELPI_III.pdf",             "2017", "codigo"),
    ("2017/Libro_de_código_Segundo_Cuidador_Principal_ELPI_III.pdf","2017", "codigo"),
    ("2017/Libro de codigo Evaluaciones ELPI III.pdf",              "2017", "codigo"),
    ("2017/Manual_de_usuario_2017_ELPI.pdf",                        "2017", "codigo"),
    ("2017/Reporte_Metodologico_ELPI_III.pdf",                      "2017", "metodologia"),
    ("2017/Reporte_metodologico_Evaluaciones.pdf",                  "2017", "metodologia"),
    ("2017/Estandares_Metodologicos_ELPI_III.pdf",                  "2017", "metodologia"),
    ("2017/Desarrollo_de_Instrumentos_ELPI_III.pdf",                "2017", "metodologia"),

    # ---------------- Ronda 4 - 2024 (formato Stata) ----------------
    ("2024/Base_responsable_principal_Stata.dta.zip",    "2024", "base"),
    ("2024/Base_responsable_principal_SPSS.sav.zip",     "2024", "base"),
    ("2024/Base_responsable_principal_R.rds.zip",        "2024", "base"),
    ("2024/Base_adolescentes_Stata.dta.zip",             "2024", "base"),
    ("2024/Base_adolescentes_SPSS.sav.zip",              "2024", "base"),
    ("2024/Base_adolescentes_R.rds.zip",                 "2024", "base"),
    ("2024/Base_evaluaciones_Stata.dta.zip",             "2024", "base"),
    ("2024/Base_evaluaciones_SPSS.sav.zip",              "2024", "base"),
    ("2024/Base_evaluaciones_R.rds.zip",                 "2024", "base"),
    ("2024/260309_Libro_de_codigos_ELPI_2024.xlsx",      "2024", "codigo"),
    ("2024/Uso_de_base_de_datos_ELPI_2024.pdf",          "2024", "codigo"),
    ("2024/Ficha_tecnica_ELPI_2024.pdf",                 "2024", "doc"),
    ("2024/ELPI_2024_Informe_metodologico.pdf",          "2024", "metodologia"),
    ("2024/ELPI_2024_Informe_construccion_factores_de_expansion.pdf", "2024", "metodologia"),
    ("2024/ELPI_2024_Informe_estandarizacion_evaluaciones.pdf", "2024", "metodologia"),
    ("2024/Diseno_y_Muestra_ELPI.pdf",                   "2024", "metodologia"),
    ("2024/Proceso_de_Diseno_de_la_Encuesta_Longitudinal_de_Primera_Infancia  ELPI_cuarta_ronda.pdf", "2024", "metodologia"),
]

REINTENTOS = 4
ESPERA_BASE = 2  # backoff exponencial: 2s, 4s, 8s, 16s


def url_de(subruta: str) -> str:
    """URL absoluta con percent-encoding (espacios, ñ, tildes, paréntesis)."""
    return f"{BASE}/{urllib.parse.quote(subruta)}"


def descargar(url: str, destino: Path) -> None:
    ultimo_error = None
    for intento in range(REINTENTOS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=300) as resp, open(destino, "wb") as f:
                while True:
                    bloque = resp.read(1 << 20)
                    if not bloque:
                        break
                    f.write(bloque)
            return
        except Exception as e:  # red o HTTP
            ultimo_error = e
            if intento < REINTENTOS:
                espera = ESPERA_BASE * (2 ** intento)
                print(f"    reintento {intento + 1}/{REINTENTOS} en {espera}s ({e})")
                time.sleep(espera)
    raise RuntimeError(f"Fallo definitivo al descargar {url}: {ultimo_error}")


def sha256_de(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dest", default="data/raw",
                    help="carpeta destino (por defecto data/raw)")
    ap.add_argument("--solo-verificar", action="store_true",
                    help="no descarga: solo comprueba lo ya existente")
    args = ap.parse_args()

    raiz = Path(args.dest)
    fallos = []
    filas_sha = []

    for subruta, carpeta, _cat in ARCHIVOS:
        nombre = subruta.split("/")[-1]
        destino = raiz / carpeta / nombre
        destino.parent.mkdir(parents=True, exist_ok=True)
        url = url_de(subruta)

        if destino.exists() and destino.stat().st_size > 0:
            print(f"[ok existente] {destino} ({destino.stat().st_size:,} bytes)")
        elif args.solo_verificar:
            print(f"[FALTA] {destino}")
            fallos.append(nombre)
            continue
        else:
            print(f"[descargando] {url}")
            try:
                descargar(url, destino)
                print(f"    -> {destino} ({destino.stat().st_size:,} bytes)")
            except RuntimeError as e:
                print(f"    ERROR: {e}")
                fallos.append(nombre)
                continue

        filas_sha.append(f"{sha256_de(destino)}  {destino.as_posix()}")

    manifiesto = raiz / "SHA256SUMS.txt"
    manifiesto.parent.mkdir(parents=True, exist_ok=True)
    manifiesto.write_text("\n".join(filas_sha) + "\n", encoding="utf-8")
    print(f"\nManifiesto de integridad escrito en {manifiesto}")

    if fallos:
        print(f"\nERROR: {len(fallos)} archivo(s) con problemas: {fallos}")
        return 1
    print(f"\nListo: {len(ARCHIVOS)} archivos disponibles bajo {raiz}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
