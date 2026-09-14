# ELPI: informes metodológicos a tener en cuenta

Resumen de los puntos con consecuencias prácticas para el uso del panel,
extraídos de los documentos oficiales descargados en `data/raw/` (se cita el
documento fuente en cada punto).

## Documentos revisados

| Ronda | Documento (en `data/raw/`) | Contenido clave |
|---|---|---|
| Todas | `WEB_Informacion_ELPI.pdf` | Descripción general del estudio |
| 2010 | `2010/Manual_Usuario_Base_de_Datos_ELPI_2010.pdf` | Estructura de bases y variables (hace de libro de códigos) |
| 2010 | `2010/Informe_Resultados_Encuesta_2010.pdf` | Diseño y resultados 1ª ronda |
| 2012 | `2012/Manual_Usuario_Base_de_Datos_ELPI_2012.pdf` | Ídem 2ª ronda |
| 2012 | `2012/Informe_Resultados_Encuesta_Hogares_2012.pdf` | Diseño y resultados 2ª ronda |
| 2017 | `2017/Reporte_Metodologico_ELPI_III.pdf` | **El informe metodológico central de la 3ª ronda** |
| 2017 | `2017/Reporte_metodologico_Evaluaciones.pdf` | Estandarización de cada test 2017 |
| 2017 | `2017/Estandares_Metodologicos_ELPI_III.pdf` | Ética/protocolos de autoreporte infantil |
| 2017 | `2017/Desarrollo_de_Instrumentos_ELPI_III.pdf` | Desarrollo de cuestionarios y tests |
| 2024 | `2024/ELPI_2024_Informe_metodologico.pdf` | **El informe metodológico central de la 4ª ronda** |
| 2024 | `2024/ELPI_2024_Informe_construccion_factores_de_expansion.pdf` | Factores de expansión (INE) |
| 2024 | `2024/ELPI_2024_Informe_estandarizacion_evaluaciones.pdf` | Estandarización de tests 2024 |
| 2024 | `2024/Diseno_y_Muestra_ELPI.pdf`, `2024/Ficha_tecnica_ELPI_2024.pdf` | Diseño, muestra y ficha técnica |
| 2024 | `2024/Uso_de_base_de_datos_ELPI_2024.pdf` | Uso de las bases, llave `folio`, diseño `svyset` |

## 1. Diseño muestral (común a las rondas)

- Muestreo estratificado bietápico: 33 conglomerados de comunas (región ×
  ingreso per cápita × población infantil, Censo 2002); **las mismas comunas
  se mantienen en todas las rondas** para resguardar comparabilidad
  (*Reporte_Metodologico_ELPI_III*, §3).
- Cohorte original: nacidos entre el 01-01-2006 y el 31-08-2009. El marco se
  amplió con refrescos: nacidos 09-2009 a 12-2011 (ronda 2012) y nacidos
  desde 2012 (ronda 2017). Se excluye población extranjera y comunas de
  difícil acceso (*Informe construcción factores 2024*, §II).
- La variable **`estrato`** (comuna de selección) viene en las bases 2017 y
  2024 y es la que pide el diseño para varianzas:
  `svyset folio [pw=f_exp], strata(estrato)`
  (*Uso_de_base_de_datos_ELPI_2024*). Las bases públicas 2010/2012 no
  incluyen variable de estrato. En el panel de este repo, `estrato` está en
  el formato largo para 2017 y 2024.

## 2. El cambio de diseño de 2024 (el punto más importante)

- Por dificultades en la licitación, **la 4ª ronda siguió exclusivamente a la
  cohorte original de 2010** (adolescentes de 14-18 años). Los refrescos de
  2012 y de 2017 **no** fueron seguidos
  (*ELPI_2024_Informe_estandarizacion_evaluaciones*, §1.1;
  *Diseno_y_Muestra_ELPI*). Consecuencias:
  - Un niño incorporado en los refrescos 2012/2017 tiene como máximo 2-3
    rondas posibles; el panel de 4 rondas solo existe para la cohorte 2010.
  - En el panel de este repo esto se refleja en que los 10.003 folios de 2024
    pertenecen íntegramente a la muestra 2010 y no existen patrones de
    participación `0**1`.
- Muestra lograda 2024: 10.003 adolescentes. Campo entre mayo y septiembre-
  octubre de 2024, ejecutado por el Centro de Microdatos (U. de Chile), con
  factores de expansión del INE (*Ficha_tecnica_ELPI_2024*).

## 3. Factores de expansión: cuál usar y sus n

- **2010**: `fexp_enc` (entrevista) y `fexp_test` (evaluaciones), transversales.
- **2012**: transversales `fexp_enc0`/`fexp_test0`; longitudinales 2010-2012
  `fexp_encP`/`fexp_testP` (*Manual_Usuario_2012*).
- **2017** (archivo de factores longitudinales, llave `idencuesta` =
  `folio` sin el último dígito): panel 2010-2012-2017 `fexp_encP` (n=9.196) y
  `fexp_evaP` (n=7.671); combinaciones `_1217` (n=11.338 / 9.698) y `_1017`
  (n=10.230 / 9.018). Construidos por Método de Propensión de Respuesta por
  deciles + postestratificación (*Reporte_Metodologico_ELPI_III*, §3). Cada
  factor es no nulo **solo** para su submuestra: los NaN son de diseño.
- **2024** (INE, metodología renovada: ajuste de no contacto por *propensity
  score*, ajuste simple de no respuesta por estrato, suavizamiento "método
  mixto" y calibración raking): `f_exp` transversal; `f_exp_10121724`
  (respondió las 4 rondas, n=7.012), `f_exp_1024` (2010 y 2024, sin exigir
  rondas intermedias), `f_exp_101224`, `f_exp_101724`
  (*ELPI_2024_Informe_construccion_factores_de_expansion*, Tabla 1 y §IV).
- **Aviso de comparabilidad**: los totales poblacionales usados en la
  calibración 2024 fueron **actualizados** ("presenta diferencias a las
  versiones anteriores de la ELPI, debido a desactualizaciones del Marco
  Muestral"); las estimaciones expandidas de 2024 no son directamente
  contrastables con expansiones de rondas anteriores sin considerar ese
  cambio de marco (*ELPI_2024_Informe_construccion_factores*, notas 2-3).

## 4. No respuesta y atrición (2017)

- Tasas de respuesta 2017: hoja de ruta 67,4%; cuestionario del cuidador
  principal 65,7%; **cuestionario del segundo cuidador 27,3%** — usar la base
  Segundo Cuidador con mucha cautela. La Región Metropolitana tiene las
  peores tasas (70,5% panel; 45,3% refresco); el contacto en la muestra
  refresco (56,9%) fue muy inferior al panel (81,8%)
  (*Reporte_Metodologico_ELPI_III*, §6).
- Del total de evaluaciones de 2010 (14.161), el 54% (7.671) fue evaluado
  también en 2012 y 2017.

## 5. Comparabilidad de los tests entre rondas

Instrumentos presentes en las bases de evaluaciones (verificado sobre los
archivos):

| Instrumento | 2010 | 2012 | 2017 | 2024 |
|---|---|---|---|---|
| TVIP (vocabulario) | ✔ | ✔ | ✔ | ✔ |
| CBCL (conducta) | ✔ (CBCL1) | ✔ | ✔ | ✔ (CBCL2) |
| EEDP | ✔ | — | — | — |
| TADI | — | ✔ | — | — |
| Battelle / BDI-ST2 | ✔ | ✔ | ✔ | — |
| Woodcock-Muñoz | — | — | ✔ | — |
| PSI (estrés parental) | — | ✔ | ✔ | ✔ |
| CESD-10, PSCS | — | — | ✔ | ✔ |

- **El TVIP es el único test cognitivo aplicado en las cuatro rondas** (con
  normas hispanoamericanas de 1986, M=100, DE=15); es el parámetro de interés
  que el propio INE usa para evaluar los factores 2024.
- En 2017, **BDI-ST2 y Woodcock-Muñoz se estandarizaron con la propia muestra
  ELPI 2017** (normas internas por mes de edad, no normas externas): sus
  puntajes T son relativos a la muestra de esa ronda y no son comparables
  directamente con normas internacionales ni entre rondas
  (*Reporte_metodologico_Evaluaciones*, §estandarización; Tabla 52 del
  reporte metodológico).
- Tests de función ejecutiva 2017 (Hearts & Flowers, BDST) **sin normas**;
  el reporte advierte además que ciertos ítems de H&F y del PSI requieren
  recodificación por parte del investigador.
- En 2024 el **PSI se aplicó fuera de su rango normativo original**
  (cuidadores de niños de 1 mes a 12 años, aplicado a cuidadores de
  adolescentes): se mantuvieron las normas originales "como referencia
  comparativa"; interpretar con cautela y revisar la escala de respuesta
  defensiva (*ELPI_2024_Informe_estandarizacion_evaluaciones*, §2.3).
- CBCL 2024: puntajes T internacionales por sexo; si faltaban exactamente 4
  ítems se imputó por IRT; persisten faltantes en adolescentes que viven sin
  responsable principal (mismo informe, §2.2).
- CESD-10 y PSCS: solo puntajes brutos (CESD-10 se interpreta por punto de
  corte; PSCS no tiene normas).
- Antropometría (2010-2017): z-scores según estándares OMS (WHO Anthro);
  los perfiles estandarizados cubren hasta 61 meses (talla/CC) o 121 meses
  (peso) (*Reporte_metodologico_Evaluaciones*, Tabla 32).

## 6. Otras advertencias prácticas

- **Códigos de región**: 2010-2017 usan la división de 15 regiones; 2024 usa
  la vigente con 16 (Ñuble, creada en 2018). Recodificar antes de comparar.
- **Edad en meses**: no se publica en las evaluaciones 2024 (sí fecha de
  nacimiento y edad en años).
- **Versión de la base Cuidador Principal 2017**: la página oficial enlaza la
  versión Stata re-publicada el 10-10-2024
  (`Base_Cuidador_Principal_ELPI_III(STATA)_241010`). La versión SPSS
  disponible es la publicación anterior y conserva 8 variables de
  identificación del establecimiento educacional (`e6id_est`, `e6rbd_sup`,
  `e6com_cod`, etc.) que la re-publicación eliminó; para respetar el criterio
  de anonimización vigente, usar la versión Stata 241010 (verificado
  comparando ambas bases: 78.988 filas en ambas; 837 vs 829 columnas).
- **2010 y 2012 no tienen informe metodológico separado**: el diseño y el
  trabajo de campo se documentan en el Manual de Usuario y en el Informe de
  Resultados de cada ronda; el Reporte Metodológico de la 3ª ronda (§3)
  reconstruye además el diseño muestral y los factores de 2010 y 2012.
