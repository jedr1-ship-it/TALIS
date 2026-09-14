# ELPI Chile — Bases públicas de las 4 rondas y base panel de niños/as

Este repositorio descarga, verifica y enlaza las bases de datos públicas de la
**Encuesta Longitudinal de Primera Infancia (ELPI)** de Chile en sus cuatro
rondas — **2010, 2012, 2017 y 2024** — con sus libros de códigos, y construye
una **base panel** que sigue a los niños/as a través de las cuatro rondas.

## Fuentes

Los microdatos y la documentación provienen del **Observatorio Social** del
Ministerio de Desarrollo Social y Familia:

| Ronda | Página oficial |
|---|---|
| Portada ELPI | <https://observatorio.ministeriodesarrollosocial.gob.cl/elpi> |
| I — 2010 | <https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-primera-ronda> |
| II — 2012 | <https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-segunda-ronda> |
| III — 2017 | <https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-tercera-ronda> |
| IV — 2024 | <https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-cuarta-ronda> |

Las URLs exactas de cada archivo descargado están en
[`scripts/01_descargar_elpi.py`](scripts/01_descargar_elpi.py) y las sumas de
verificación en [`data/raw/SHA256SUMS.txt`](data/raw/SHA256SUMS.txt).

**BIDAT.** Los mismos estudios están publicados como *datos abiertos* en el
Banco Integrado de Datos del Ministerio, **BIDAT**
(<https://bidat.gob.cl/>; `bidat.midesof.cl` redirige allí), bajo licencia
**Creative Commons Atribución 4.0** y sin necesidad de registro. La ELPI se
encuentra en el directorio "Encuestas Observatorio Social"
(<https://bidat.gob.cl/directorio/Encuestas%20Observatorio%20Social>), con la
ficha de la cuarta ronda en
<https://bidat.gob.cl/details/ficha/dataset/bases-de-datos-elpi-2024>
(las rondas 2010/2012/2017 se alcanzan con el filtro "Año" de esa ficha).
Para la descarga automatizada se usa el Observatorio porque sus URLs son
estables y directas; los enlaces de descarga de BIDAT son tokens opacos
generados por la plataforma y no sirven para un script reproducible.

## Estructura del repositorio

```
├── scripts/
│   ├── 01_descargar_elpi.py      # descarga bases + libros de códigos (URLs exactas)
│   ├── 02_verificar_archivos.py  # extrae los .zip y verifica que todo abre
│   └── 03_construir_panel.py     # enlaza a los niños/as y construye el panel
├── data/
│   ├── raw/                      # descargas tal cual (committeadas; 68 MB)
│   │   ├── 2010/ 2012/ 2017/ 2024/
│   │   └── SHA256SUMS.txt        # manifiesto de integridad
│   ├── interim/                  # extracción de los .zip (NO committeada; regenerable)
│   └── processed/                # base panel (committeada)
├── reports/
│   ├── verificacion_archivos.md  # informe de verificación (filas/columnas por base)
│   └── panel_resumen.md          # verificaciones y conteos del panel
├── requirements.txt
└── README.md
```

## Reproducción

```bash
pip install -r requirements.txt
python3 scripts/01_descargar_elpi.py      # descarga a data/raw/ (~68 MB)
python3 scripts/02_verificar_archivos.py  # extrae a data/interim/ y verifica
python3 scripts/03_construir_panel.py     # genera data/processed/ y reports/
```

`01_descargar_elpi.py` no vuelve a bajar lo que ya existe y admite
`--solo-verificar`. Reintenta cada descarga hasta 4 veces con espera
exponencial (2 s, 4 s, 8 s, 16 s).

## Qué se descarga

Formato preferente **Stata (.dta)**; para las tres bases de 2017 cuya versión
Stata solo se publica en `.rar` se usa la versión **SPSS (.sav)** equivalente
(mismo contenido, y el `.zip` se extrae sin herramientas propietarias).

| Ronda | Bases de microdatos | Libro de códigos / documentación de variables |
|---|---|---|
| 2010 | Hogar, Entrevistada, Evaluaciones, Cuidado infantil, Ítems de test | Manual de Usuario de la Base de Datos 2010 (no existe libro de códigos separado) + cuestionario |
| 2012 | Hogar, Entrevistada, Evaluaciones, Cuidado infantil, Historia laboral, Ítems de test | Manual de Usuario de la Base de Datos 2012 (ídem) + cuestionario |
| 2017 | Cuidador principal (versión corregida 2024-10-10), Evaluaciones, Niños y niñas, Segundo cuidador, Factores de expansión longitudinales | Libros de códigos de las 4 bases (PDF) + Manual de usuario 2017 |
| 2024 | Responsable principal, Adolescentes, Evaluaciones | Libro de códigos 2024 (XLSX) + "Uso de base de datos ELPI 2024" + ficha técnica |

La verificación (informe en
[`reports/verificacion_archivos.md`](reports/verificacion_archivos.md)) abre
cada `.dta`/`.sav` con `pyreadstat`/`pandas`, el XLSX con `openpyxl` y
comprueba la firma de los PDF. Las 19 bases de microdatos abren sin errores.

## Base panel (`data/processed/`)

**Llave de enlace: `folio`**, identificador único del niño/a seleccionado/a,
estable entre rondas. Así lo establece el documento oficial *Uso de la Base de
Datos ELPI 2024*: el enlace con las rondas anteriores "se realiza a través de
la variable llave `folio`". Dentro de 2017, los factores longitudinales usan
la llave `idencuesta` = `folio` sin su último dígito (cruce 1:1 verificado
para los 17.307 hogares).

Cómo se ubica al niño/a en cada ronda:

| Ronda | Encuesta al hogar/cuidador | Fila del niño/a | Evaluaciones | Cuestionario propio |
|---|---|---|---|---|
| 2010 | `Entrevistada_2010` | roster `Hogar_2010` con `a16==13` (sexo `a18`, edad `a19`) | `Evaluaciones_2010` | — |
| 2012 | `Entrevistada_2012` | roster `Hogar_2012` con `i2==13` (sexo `i4`, edad `i1`) | `Evaluaciones_2012` | — |
| 2017 | `Cuidador Principal` | roster con `tipopersona==1` (sexo `h2`, edad `h3`) | `Evaluaciones` | `Niños y Niñas` |
| 2024 | `Responsable principal` | roster con `tipo_persona==1` (sexo `sexo`, edad `edad`) | `Evaluaciones` | `Adolescentes` |

### Archivos

* **`elpi_panel_ninos_largo.csv` / `.dta`** — formato largo: 58.518 filas
  (una por `folio` × ronda participada) con indicadores de participación por
  instrumento, sexo, edad (años y meses), región, comuna (2017/2024), área
  urbano/rural (2010/2012) y factores de expansión transversales.
* **`elpi_panel_ninos_ancho.csv` / `.dta`** — formato ancho: 23.245 filas
  (una por niño/a) con flags de participación por ronda (`en_2010` …
  `en_eval_2024`), patrón de participación (`1111`, `1101`, …), muestra de
  origen, sexo (y su consistencia entre rondas) y **todos los factores de
  expansión longitudinales**: 2012 (`fexp_encP_2012`, `fexp_testP_2012`),
  2017 (`fexp_hogP/encP/evaP_2017` y variantes `_1217`/`_1017`) y 2024
  (`f_exp_1024`, `f_exp_101224`, `f_exp_101724`, `f_exp_10121724`).

### Cifras clave (ver [`reports/panel_resumen.md`](reports/panel_resumen.md))

* 23.245 niños/as distintos; por ronda: 15.175 (2010), 16.033 (2012),
  17.307 (2017), 10.003 (2024).
* **7.012 niños/as presentes en las cuatro rondas** (patrón `1111`).
* Los 10.003 folios de 2024 pertenecen íntegramente a la cohorte original
  2010 (la cuarta ronda re-entrevista a esa cohorte, hoy adolescentes).
* Verificaciones internas: `muestra==1` (2012) coincide exactamente con
  2012∩2010 (12.898) y `espanel==1` (2017) con 2017∩(2010∪2012) (12.372).
* El sexo reportado es consistente entre rondas para el 99,8% de los casos
  (`sexo_consistente` marca el resto; no se corrige).

### Notas de uso

* Los códigos de **región** son los vigentes en cada ronda (la reforma de
  2018 creó la región de Ñuble: los códigos 2024 no son directamente
  comparables con 2010–2017 sin recodificar).
* Para estimaciones longitudinales use el factor de expansión del panel
  correspondiente a la combinación de rondas analizada; cada factor es no
  nulo solo para su submuestra (los NaN son de diseño).
* Faltantes por diseño: `comuna` no se publica en 2010/2012, `area` no se
  publica en 2017/2024 y la edad en meses de evaluaciones no se publica
  en 2024.

## Política de tamaño (>100 MB) y qué está en git

* Ningún archivo **committeado** supera los 100 MB: las descargas de
  `data/raw/` suman ~68 MB (el mayor pesa 24,9 MB) y la base panel ~16 MB.
* `data/interim/` (≈1,1 GB) **no se sube a git**: contiene la extracción de
  los `.zip`, incluidas dos bases que superan los 100 MB
  (`Base_Cuidador_Principal_ELPI_III(STATA)_241010.dta`, ~606 MB, y
  `Base responsable principal Stata.dta`, ~184 MB). Se regenera por completo
  con `python3 scripts/02_verificar_archivos.py` a partir de los `.zip`
  committeados (o re-descargados con el script 01).

## Licencia y cita de los datos

Los microdatos ELPI son datos abiertos del Ministerio de Desarrollo Social y
Familia de Chile, publicados bajo **CC BY 4.0** (según BIDAT). Cite la fuente,
por ejemplo: *Ministerio de Desarrollo Social y Familia, Observatorio Social.
Encuesta Longitudinal de Primera Infancia (ELPI), rondas 2010, 2012, 2017 y
2024.*
