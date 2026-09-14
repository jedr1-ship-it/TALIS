#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae y verifica los archivos ELPI descargados por 01_descargar_elpi.py.

1. Descomprime cada .zip de data/raw/<ronda>/ en data/interim/<ronda>/.
2. Abre cada base de microdatos (.dta con pandas/pyreadstat, .sav con
   pyreadstat) y registra n.º de filas y columnas.
3. Abre el libro de códigos 2024 (.xlsx) y verifica sus hojas.
4. Comprueba la firma de los PDF (%PDF).
5. Escribe el informe reproducible en reports/verificacion_archivos.md.

Requisitos: pandas, pyreadstat, openpyxl  (pip install pandas pyreadstat openpyxl)

Uso:
    python3 scripts/02_verificar_archivos.py
"""
import sys
import unicodedata
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import pyreadstat

RAW = Path("data/raw")
INTERIM = Path("data/interim")
REPORTE = Path("reports/verificacion_archivos.md")


def extraer_zips() -> list[str]:
    lineas = []
    for z in sorted(RAW.glob("*/*.zip")):
        destino = INTERIM / z.parent.name
        destino.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(z) as zf:
            for miembro in zf.infolist():
                if miembro.is_dir():
                    continue
                # aplanar rutas internas y evitar path traversal
                nombre = Path(miembro.filename).name
                if not nombre or nombre.startswith("."):
                    continue
                # zipfile decodifica como cp437 si el ZIP no marca UTF-8;
                # se revierte esa decodificación y se normaliza a NFC para
                # evitar nombres corruptos (p.ej. "Nin╠âos" -> "Niños").
                if not (miembro.flag_bits & 0x800):
                    try:
                        nombre = nombre.encode("cp437").decode("utf-8")
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        pass
                nombre = unicodedata.normalize("NFC", nombre)
                salida = destino / nombre
                with zf.open(miembro) as fin, open(salida, "wb") as fout:
                    fout.write(fin.read())
                lineas.append(f"| `{z.name}` | `{destino.name}/{nombre}` | "
                              f"{salida.stat().st_size:,} |")
    return lineas


def abrir_microdato(p: Path):
    """Devuelve (filas, columnas, motor). Lanza excepción si no abre."""
    if p.suffix == ".dta":
        try:
            df, meta = pyreadstat.read_dta(str(p))
            return len(df), len(df.columns), "pyreadstat"
        except Exception:
            df = pd.read_stata(str(p), convert_categoricals=False)
            return len(df), len(df.columns), "pandas.read_stata"
    if p.suffix == ".sav":
        df, meta = pyreadstat.read_sav(str(p))
        return len(df), len(df.columns), "pyreadstat"
    raise ValueError(f"extensión no reconocida: {p}")


def main() -> int:
    fallos = []
    filas_reporte = [
        "# Verificación de archivos ELPI",
        "",
        f"Generado por `scripts/02_verificar_archivos.py` el {date.today().isoformat()}.",
        "",
        "## 1. Extracción de ZIP",
        "",
        "| ZIP de origen | Archivo extraído | Bytes |",
        "|---|---|---:|",
    ]

    try:
        filas_reporte += extraer_zips()
    except zipfile.BadZipFile as e:
        print(f"ERROR de ZIP: {e}")
        return 1

    filas_reporte += [
        "",
        "## 2. Apertura de bases de microdatos",
        "",
        "| Ronda | Archivo | Filas | Columnas | Motor de lectura |",
        "|---|---|---:|---:|---|",
    ]
    for p in sorted(INTERIM.glob("*/*")):
        if p.suffix not in (".dta", ".sav"):
            continue
        try:
            filas, cols, motor = abrir_microdato(p)
            filas_reporte.append(
                f"| {p.parent.name} | `{p.name}` | {filas:,} | {cols} | {motor} |")
            print(f"[ok] {p} -> {filas:,} x {cols} ({motor})")
        except Exception as e:
            fallos.append(f"{p}: {e}")
            filas_reporte.append(f"| {p.parent.name} | `{p.name}` | ERROR | — | {e} |")
            print(f"[ERROR] {p}: {e}")

    filas_reporte += ["", "## 3. Libro de códigos 2024 (xlsx)", ""]
    xlsx = RAW / "2024" / "260309_Libro_de_codigos_ELPI_2024.xlsx"
    try:
        hojas = pd.ExcelFile(xlsx).sheet_names
        filas_reporte.append(f"`{xlsx.name}` abre correctamente; hojas: "
                             + ", ".join(f"`{h}`" for h in hojas))
        print(f"[ok] {xlsx} hojas={hojas}")
    except Exception as e:
        fallos.append(f"{xlsx}: {e}")
        filas_reporte.append(f"ERROR al abrir `{xlsx.name}`: {e}")

    filas_reporte += ["", "## 4. Documentos PDF (firma %PDF)", ""]
    for p in sorted(RAW.glob("*/*.pdf")):
        with open(p, "rb") as f:
            ok = f.read(5) == b"%PDF-"
        marca = "ok" if ok else "ERROR: no es PDF"
        filas_reporte.append(f"- [{marca}] `{p.parent.name}/{p.name}` ({p.stat().st_size:,} bytes)")
        if not ok:
            fallos.append(f"{p}: firma PDF inválida")

    filas_reporte += [
        "",
        "## Resultado",
        "",
        "Sin errores: todos los archivos abren correctamente." if not fallos
        else "ERRORES:\n" + "\n".join(f"- {f}" for f in fallos),
        "",
    ]
    REPORTE.parent.mkdir(parents=True, exist_ok=True)
    REPORTE.write_text("\n".join(filas_reporte), encoding="utf-8")
    print(f"\nInforme escrito en {REPORTE}")
    if fallos:
        print(f"{len(fallos)} error(es).")
        return 1
    print("Verificación completa sin errores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
