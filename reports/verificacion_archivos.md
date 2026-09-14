# Verificación de archivos ELPI

Generado por `scripts/02_verificar_archivos.py` el 2026-09-14.

## 1. Extracción de ZIP

| ZIP de origen | Archivo extraído | Bytes |
|---|---|---:|
| `Cuidado_infantil_2010.dta.zip` | `2010/Cuidado_infantil_2010.dta` | 10,618,795 |
| `Entrevistada_2010.dta.zip` | `2010/Entrevistada_2010.dta` | 32,737,317 |
| `Evaluaciones2010_items_test.dta.zip` | `2010/Evaluaciones2010_items_test.dta` | 29,630,452 |
| `Evaluaciones_2010.dta.zip` | `2010/Evaluaciones_2010.dta` | 13,391,702 |
| `Hogar_2010.dta.zip` | `2010/Hogar_2010.dta` | 35,694,033 |
| `Cuidado_infantil_2012.dta.zip` | `2012/Cuidado_infantil_2012.dta` | 3,896,655 |
| `Entrevistada_2012.dta.zip` | `2012/Entrevistada_2012.dta` | 9,967,536 |
| `Evaluaciones2012_items_test.dta.zip` | `2012/Evaluaciones2012_items_test.dta` | 46,739,140 |
| `Evaluaciones_2012.dta.zip` | `2012/Evaluaciones_2012.dta` | 19,856,240 |
| `Historia_Laboral_2012.dta.zip` | `2012/Historia_Laboral_2012.dta` | 2,057,967 |
| `Hogar_2012.dta.zip` | `2012/Hogar_2012.dta` | 10,912,239 |
| `Base Evaluaciones ELPI III.dta.zip` | `2017/Base Evaluaciones ELPI III.dta` | 41,542,763 |
| `Base_Cuidador_Principal_ELPI_III(STATA)_241010.dta.zip` | `2017/Base_Cuidador_Principal_ELPI_III(STATA)_241010.dta` | 635,199,052 |
| `Base_Niños_y_Niñas_ELPI_III_(SPSS).sav.zip` | `2017/Base Niños y Niñas ELPI III (SPSS).sav` | 2,998,000 |
| `Base_Segundo_Cuidador_Principal_ELPI_III_(SPSS).sav.zip` | `2017/Base Segundo Cuidador Principal ELPI III (SPSS).sav` | 751,267 |
| `Factores_de_expansion_longitudinales_ELPI_III_(SPSS).sav.zip` | `2017/Factores de expansion longitudinales ELPI III (SPSS).sav` | 808,953 |
| `Base_adolescentes_Stata.dta.zip` | `2024/Base adolescentes Stata.dta` | 26,082,171 |
| `Base_evaluaciones_Stata.dta.zip` | `2024/Base evaluaciones Stata.dta` | 10,823,802 |
| `Base_responsable_principal_Stata.dta.zip` | `2024/Base responsable principal Stata.dta` | 192,087,594 |

## 2. Apertura de bases de microdatos

| Ronda | Archivo | Filas | Columnas | Motor de lectura |
|---|---|---:|---:|---|
| 2010 | `Cuidado_infantil_2010.dta` | 95,775 | 83 | pandas.read_stata |
| 2010 | `Entrevistada_2010.dta` | 15,175 | 269 | pyreadstat |
| 2010 | `Evaluaciones2010_items_test.dta` | 14,161 | 1173 | pandas.read_stata |
| 2010 | `Evaluaciones_2010.dta` | 14,161 | 126 | pyreadstat |
| 2010 | `Hogar_2010.dta` | 74,237 | 60 | pyreadstat |
| 2012 | `Cuidado_infantil_2012.dta` | 60,605 | 52 | pyreadstat |
| 2012 | `Entrevistada_2012.dta` | 16,033 | 568 | pyreadstat |
| 2012 | `Evaluaciones2012_items_test.dta` | 14,438 | 1167 | pandas.read_stata |
| 2012 | `Evaluaciones_2012.dta` | 14,438 | 204 | pyreadstat |
| 2012 | `Historia_Laboral_2012.dta` | 44,862 | 25 | pyreadstat |
| 2012 | `Hogar_2012.dta` | 76,977 | 86 | pyreadstat |
| 2017 | `Base Evaluaciones ELPI III.dta` | 15,827 | 258 | pyreadstat |
| 2017 | `Base Niños y Niñas ELPI III (SPSS).sav` | 10,698 | 153 | pyreadstat |
| 2017 | `Base Segundo Cuidador Principal ELPI III (SPSS).sav` | 4,965 | 67 | pyreadstat |
| 2017 | `Base_Cuidador_Principal_ELPI_III(STATA)_241010.dta` | 78,988 | 829 | pandas.read_stata |
| 2017 | `Factores de expansion longitudinales ELPI III (SPSS).sav` | 17,307 | 8 | pyreadstat |
| 2024 | `Base adolescentes Stata.dta` | 10,003 | 217 | pyreadstat |
| 2024 | `Base evaluaciones Stata.dta` | 10,003 | 134 | pyreadstat |
| 2024 | `Base responsable principal Stata.dta` | 41,913 | 332 | pyreadstat |

## 3. Libro de códigos 2024 (xlsx)

`260309_Libro_de_codigos_ELPI_2024.xlsx` abre correctamente; hojas: `Índice`, `Ficha técnica`, `Cuestionarios`, `1. Responsable principal`, `2. Adolescentes`, `3. Evaluaciones`, `Anexo 1`, `Anexo 2`, `Anexo 3`, `Anexo 4`, `Anexo 5`, `Anexo 6`, `Anexo 7`

## 4. Documentos PDF (firma %PDF)

- [ok] `2010/Encuesta_ELPI_2010.pdf` (2,107,264 bytes)
- [ok] `2010/Manual_Usuario_Base_de_Datos_ELPI_2010.pdf` (815,011 bytes)
- [ok] `2012/Cuestionario_ELPI_2012_Cuidador_Principal.pdf` (938,454 bytes)
- [ok] `2012/Manual_Usuario_Base_de_Datos_ELPI_2012.pdf` (867,518 bytes)
- [ok] `2017/Libro de codigo Evaluaciones ELPI III.pdf` (526,394 bytes)
- [ok] `2017/Libro_de_código_Cuidador_Principal_ELPI_III.pdf` (2,372,158 bytes)
- [ok] `2017/Libro_de_código_Niños_y_Niñas_ELPI_III.pdf` (426,252 bytes)
- [ok] `2017/Libro_de_código_Segundo_Cuidador_Principal_ELPI_III.pdf` (278,720 bytes)
- [ok] `2017/Manual_de_usuario_2017_ELPI.pdf` (814,092 bytes)
- [ok] `2024/Ficha_tecnica_ELPI_2024.pdf` (149,400 bytes)
- [ok] `2024/Uso_de_base_de_datos_ELPI_2024.pdf` (521,572 bytes)

## Resultado

Sin errores: todos los archivos abren correctamente.
