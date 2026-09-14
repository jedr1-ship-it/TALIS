# Diseños de investigación causal (nivel JMP) posibles con la ELPI

Ideas de papers de economía de alto nivel construibles con este panel
(cohorte nacida 2006-2009, seguida de los 0-4 a los 14-18 años), el contexto
de políticas chileno y una estrategia de identificación explícita. Se indica
para cada uno qué aporta la ELPI, la fuente de variación exógena y las
limitaciones honestas de los datos públicos.

## Activos de identificación que tiene este panel

- **Mes y año de nacimiento** (`fecha_nac`, mm/aaaa en 2024; edad en meses en
  2010-2017): permite explotar reglas y reformas con corte por fecha de
  nacimiento.
- **Resultados medidos ANTES de la exposición escolar** (TVIP/Battelle/CBCL a
  los 0-6): casi ningún estudio de RD de entrada escolar o de shocks tiene
  habilidad pre-tratamiento del propio niño.
- **Geografía**: región en las 4 rondas; comuna en 2017/2024; `estrato` =
  comuna de selección (33 comunas PSU) como proxy de la comuna de origen del
  hogar en 2010.
- **Historias retrospectivas**: quién cuidó al niño a cada edad (cl4*),
  empleo materno por tramo de edad del niño (cl3*), lactancia, embarazo y
  parto.
- 3 rondas pre-COVID + 1 post-COVID; 14 años de trayectoria.

## Diseño 1 — Efectos de largo plazo de Chile Crece Contigo (el flagship)

- **Política**: sistema integrado de protección a la primera infancia;
  piloto 2007 en ~159 comunas, despliegue nacional 2008. La entrada al
  programa es por gestación/nacimiento: los nacidos después de la
  implementación en su comuna se exponen desde la gestación.
- **Identificación**: dif-en-dif de cohorte × comuna (mes de nacimiento ×
  fecha de implementación comunal, datos administrativos públicos del MDSF).
  Exposición completa (desde gestación) vs. parcial vs. nula dentro de la
  misma cohorte ELPI. Primera etapa observable: recepción de materiales ChCC
  reportada en ELPI 2012 (f29-f31) y 2017 (ap6a).
- **Resultados**: TVIP, PHQ-4, conductas de riesgo y escolaridad a los 14-18;
  trayectoria completa 2010-2024.
- **Por qué es high-level**: sería la primera evaluación a 15+ años de un
  programa nacional integrado de primera infancia en un país de ingreso
  medio (el modelo que la región copió); habla directo a la agenda
  Heckman de complementariedad dinámica.
- **Límites**: la geografía de línea base pública son las 33 comunas de
  selección (pocos clusters → wild bootstrap); despliegue comprimido
  2007-2008 (poca variación temporal); migración entre comunas.

## Diseño 2 — Edad de entrada al colegio: RD por el corte del 31 de marzo
   (el más limpio; recomendado como JMP "seguro")

- **Regla**: para entrar a 1º básica hay que tener 6 años cumplidos al 31 de
  marzo (5 para kínder). Nacer el 1 de abril versus el 31 de marzo desplaza
  la entrada casi un año → RD (fuzzy) en fecha de nacimiento.
- **Identificación**: RD/IV con mes de nacimiento como running variable
  (granularidad mensual: donut-RD por mes; precedente chileno con datos
  administrativos: McEwan & Shapiro 2008). El primer paso es visible
  directamente en los datos (gráfico `02_rdd_corte_escolar.png`).
- **Resultados**: curso y rezago escolar en 2017 y 2024; TVIP/WM/CBCL a los
  8-12; PHQ-4, conductas de riesgo e ideación a los 14-18. Con DOS rondas de
  resultados a edades distintas se puede separar efecto edad-al-test vs.
  edad-relativa.
- **El giro que lo hace JMP**: la ELPI mide la habilidad del niño ANTES de
  entrar al colegio (2010/2012) → heterogeneidad del efecto de entrar mayor
  según habilidad temprana = test directo de complementariedad dinámica que
  la literatura de school starting age no ha podido hacer.
- **Límites**: mes (no día) de nacimiento en datos públicos; cumplimiento
  imperfecto del corte (fuzzy).

## Diseño 3 — Terremoto del 27F (feb-2010): shock temprano y capital humano

- **Shock**: terremoto 8.8 Mw + tsunami (27-02-2010), intensidad concentrada
  en O'Higgins-Maule-Biobío-Araucanía; la cohorte tenía 0-4 años (y la
  muestra refresco 2012, nacida sep-2009-dic-2011, estuvo parcialmente in
  utero).
- **Identificación**: dif-en-dif de intensidad (región/comuna, escala
  Mercalli o PGA) × edad al momento del shock dentro de la cohorte; ELPI
  2012 trae módulo directo de exposición al terremoto (h4*).
- **Resultados**: trayectoria completa hasta la adolescencia (TVIP, CBCL,
  salud mental 2024) → "fetal origins/early shocks" con 14 años de
  seguimiento, mucho más largo que la literatura estándar (Torche 2011 llega
  a resultados al nacer).
- **Límites**: intensidad asignable solo a nivel regional en 2010-2012;
  migración post-terremoto; el levantamiento 2010 es posterior al sismo (no
  hay línea base pre-shock dentro de la ronda 1).

## Diseño 4 — Extensión del posnatal parental (Ley 20.545, oct-2011)

- **Reforma**: licencia maternal de 12 → 24 semanas, vigente octubre 2011,
  con elegibilidad por fecha de nacimiento del hijo.
- **Identificación**: RD en fecha de nacimiento alrededor del umbral de
  elegibilidad, usando la muestra refresco 2012 (nacidos sep-2009-dic-2011;
  n=3.135, de los cuales 2.142 fueron seguidos a 2017).
- **Resultados**: lactancia, empleo materno (historia laboral), TADI 2012,
  Battelle/WM/CBCL 2017 → efectos de licencia extendida a mediano plazo
  (edad 6-7) en un país de ingreso medio.
- **Límites**: n chico; el refresco no fue seguido a 2024; granularidad
  mensual.

## Diseño 5 — Cierres escolares COVID y la trayectoria 2017→2024

- **Shock**: Chile tuvo de los cierres escolares más largos del mundo
  (2020-2021), con reapertura escalonada por comuna/establecimiento.
- **Identificación**: cambio intra-niño 2017→2024 (TVIP, CBCL) con dosis de
  cierre a nivel de comuna (datos MINEDUC, cruzables por la comuna 2017),
  validando tendencias previas con las 3 rondas pre-COVID (event-study).
- **Por qué importa**: una de las primeras cohortes del mundo con medición
  estandarizada pre-pandemia en niñez y post-pandemia en adolescencia.
- **Límites**: reapertura no aleatoria (endógena a condiciones locales) →
  venderlo como DiD con pre-tendencias, no como experimento puro.

## Descartes honestos

- **RD por puntaje de focalización (IEF/SUF, Ficha de Protección Social)**:
  el puntaje no está en los datos públicos.
- **Efectos de establecimientos/SEP con vínculo escolar**: el RBD del
  colegio fue eliminado de las bases públicas por anonimización (solo quedó
  en la versión SPSS antigua de 2017, que no corresponde usar).

## Gráficos de apoyo (en `reports/figures/`, generados por `scripts/04_graficos.py`)

1. `01_muestra_atricion.png` — composición de la muestra por ronda y
   retención de la cohorte original.
2. `02_rdd_corte_escolar.png` — curso alcanzado en 2017 por mes de
   nacimiento: el "serrucho" del corte del 31 de marzo (primer paso del
   Diseño 2).
3. `03_persistencia_tvip.png` — persistencia del TVIP estándar 2017→2024
   dentro del mismo niño (n=7.088).
4. `04_linea_tiempo.png` — cohorte × políticas y shocks: qué diseño explota
   qué variación.
