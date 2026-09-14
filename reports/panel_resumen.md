# Base panel ELPI 2010-2012-2017-2024: resumen y verificaciones

Generado por `scripts/03_construir_panel.py` el 2026-09-14.

Llave de enlace: `folio` (identificador del niño/a seleccionado/a, estable
entre rondas según el documento oficial *Uso de la Base de Datos ELPI 2024*).

## Verificaciones

- Niños/as (folios) distintos en el panel: **23,245**
- Por ronda: 2010: 15,175, 2012: 16,033, 2017: 17,307, 2024: 10,003
- 2012∩2010: 12,898 (muestra==1 en 2012: 12,898)
- 2017∩(2010∪2012): 12,372 (espanel==1: 12,372)
- 2024⊂2010: sí (10,003 de 10,003)
- Presentes en las 4 rondas: 7,012
- Sexo consistente entre rondas: 23,191 (99.8%); el resto presenta discrepancias de reporte entre rondas y se deja tal cual (columna `sexo_consistente`).

## Patrones de participación (2010-2012-2017-2024)

| Patrón | N niños/as |
|---|---:|
| 1111 | 7,012 |
| 0010 | 4,935 |
| 1110 | 2,184 |
| 0110 | 2,142 |
| 1101 | 1,898 |
| 1100 | 1,804 |
| 0100 | 993 |
| 1000 | 806 |
| 1011 | 656 |
| 1001 | 437 |
| 1010 | 378 |

## Avisos

Sin avisos.

## Archivos generados

| Archivo | Filas | Columnas |
|---|---:|---:|
| `data/processed/elpi_panel_ninos_largo.csv/.dta` | 58,518 | 14 |
| `data/processed/elpi_panel_ninos_ancho.csv/.dta` | 23,245 | 29 |
