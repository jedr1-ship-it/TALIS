# Proceso adversarial de selección de JMP con la ELPI

Método: se propone un diseño, se estima de verdad sobre los datos, y tres
revisores adversariales independientes (econometría de RD; economía de la
educación/instituciones chilenas; datos y medición) intentan destruirlo.
Solo sobrevive lo que resiste sus objeciones y los tests que exigen.

---

## Candidato 1: RD de edad de entrada escolar (corte del 31 de marzo) — MUERTO

**Diseño**: running variable = mes de nacimiento (mm/aaaa) centrado en el
corte de abril más cercano; 4 cortes (2006-2009) apilados; ventana ±4 meses;
tendencia lineal por lado; EF de cohorte; cluster por celda mes.
Código: `scripts/05_rd_entrada_escolar.py`. Resultados:
`reports/rd_resultados_ronda1*.md`.

**Claims de ronda 1**: (C1) primera etapa: nacer ≥ abril reduce el curso
alcanzado (−0,24, p<0,001); (C2) TVIP estándar +2,4 (p=0,001) a los 8-12
para los nacidos post-corte; (C3) el efecto desaparece a los 14-18
("fade-out"); (C4) ceros en salud mental y conductas de riesgo adolescentes.

### Objeciones letales de los revisores (resumen) y evidencia

1. **Estacionalidad ≡ tratamiento** (R1, R2, R3). Con todos los cortes en
   abril, mes calendario y running variable son colineales: cualquier τ es
   un tramo del perfil estacional (Buckles-Hungerman). Evidencia que lo
   confirma: placebo en julio da TVIP-2017 = −2,31 (p=0,001), tan grande
   como el "efecto" real (+2,44); tamaño del hogar salta en el corte real
   (p=0,002) y en julio con signo opuesto (p=0,010); tabaco "significativo"
   en julio (p=0,015) y alcohol en octubre (p=0,002).
2. **Permutación en los 12 cortes mensuales** (test exigido por R1,
   ejecutado; `scripts/06_permutacion_rd.py`): |τ_abril| ocupa el puesto
   2/12 en TVIP-2017 (septiembre da 2,69 > 2,44; julio −2,31; noviembre
   −2,02) → p permutacional ≈ 0,17. En PHQ-2 abril es el 11/12. Nada
   distingue abril de un mes cualquiera.
3. **La institución era una rampa, no un corte** (R2). Para esta cohorte
   (entradas 2012-2016) regía el corte del 31 de marzo CON discreción del
   director para quienes cumplían 6 años hasta el 30 de junio; el corte
   único duro es posterior (2017/2019, según el revisor institucional). El
   perfil de primera etapa por mes lo dibuja: abr −0,24, may −0,34, jun
   −0,22, jul −0,02. No hay salto EN abril que un RD pueda usar.
4. **Ya está hecho y mejor** (R2): McEwan & Shapiro (2008, *JHR*) con datos
   administrativos chilenos con día exacto de nacimiento. El margen
   restante (outcomes adolescentes) queda sin poder: con primera etapa
   ~0,24, los IC de los "ceros" escalados cubren ±0,3-0,5 DE (±20 pp en
   PHQ-2): ausencia de evidencia, no ceros informativos.
5. **Inferencia inválida** (R1): running variable discreta con 8 puntos de
   soporte y tendencias lineales globales (Kolesár-Rothe 2018), cluster
   sobre la propia running variable, ~35 celdas; el placebo de octubre da
   una "primera etapa" +0,13 (p=0,017) — el piso de ruido supera los EE
   nominales.
6. **Datos y selección** (R3): toda la muestra condiciona en sobrevivir a
   2024 (66%); el test de atrición de ronda 1 era circular (retirado);
   `b2n` (educación madre) tenía códigos 88/99 sin limpiar (balance de
   ronda 1 inválido); "notas" (`e3_asiste`) es categórica de 7 bines y
   está truncada por graduación diferencial exactamente en el corte
   (no-asistencia 2024 en cohorte 2006: ~33% ene-mar vs ~1% jul); TVIP
   con baremos de 1986 en tramos discretos de edad (media muestral 116,6
   en 2017 = zona comprimida de tabla) — el perfil mensual residualizado
   del TVIP-2017 salta ±2 puntos también en meses sin corte (jun→jul
   −1,95), mientras el de 2024 es plano.

### Erratas de los revisores (verificadas contra los datos)

- R1 afirmó que `cbcl2_pt_inter_t` era la subescala internalizante:
  **falso** — la etiqueta es "CBCL2. Puntaje T Internacional TOTAL"
  (internalizante es `_i`).
- R1 sugirió que `e3_asiste` era una variable de asistencia usada como
  notas: **falso** — su etiqueta es "¿Qué promedio de notas tuviste el año
  pasado?" (el punto válido, de R3, es que es categórica y truncada).

### Veredicto candidato 1 (unánime, compartido por el autor)

| Claim | Veredicto |
|---|---|
| C1 primera etapa | HERIDO: existe como rampa institucional descriptiva; no como salto RD; inferencia inválida |
| C2 TVIP +2,4 a los 8-12 | MUERTO (placebos del mismo tamaño; artefacto de baremos + estacionalidad) |
| C3 fade-out | MUERTO (resta de un artefacto y un nulo; además resultado canónico: Elder-Lubotsky 2009) |
| C4 ceros adolescentes | MUERTO como "ceros informativos" (IC escalados enormes; placebos significativos) |

**Conclusión metodológica que sí sobrevive**: con granularidad mensual de
fecha de nacimiento y cortes fijos en abril, el RD de entrada escolar no es
identificable en Chile; la batería de placebos mensuales lo demuestra y es
el estándar honesto de inferencia para cualquier intento futuro
(inferencia permutacional estilo Ganong-Jäger).

---

## Candidato 2: DiD de Chile Crece Contigo a largo plazo — SOBREVIVE (condicional)

Propuesto por el revisor institucional: la estacionalidad que mató al
candidato 1 se absorbe por construcción (EF de mes calendario de
nacimiento); la identificación es la interacción cohorte × timing comunal
del despliegue 2007-2008. Pitch: **primera evaluación de un sistema
nacional integrado de primera infancia con outcomes de adolescencia y
salud mental (15+ años después)**.

### Ronda 2: ataques y resolución

1. **"El gradiente de f29a es recuerdo, no rollout"** (R1, confirmado
   empíricamente por R3): nacidos 2009 y 2010 están igualmente expuestos
   (rollout nacional completo en 2008) pero reportan recepción 24% vs 50%
   — al menos la mitad del gradiente 2006-2009 es decaimiento del
   recuerdo. Además, el 2-6% de los nacidos 2006 (gestación pre-programa)
   es el piso de falsos positivos, y los ítems del PARN (inicio nacional
   sep-2009: cuna f29d, bolso f29e) muestran 1,1-1,4% pre / 46-64% post —
   la misatribución es baja. **Resolución**: f29a queda SOLO como
   validación del despliegue; la exposición debe ser ITT por comuna × mes
   de nacimiento con fechas administrativas. IV sobre el autorreporte:
   MUERTO (error de medición no clásico).
2. **"No tienes la geografía del tratamiento"** (R3: `estrato` 2024 está
   anonimizado como códigos secuenciales 1-116). Resuelto con datos
   públicos: en 2017 `estrato` sí trae los códigos CUT reales de la comuna
   de selección; con los 7.213 niños presentes en ambas rondas el mapeo
   2024↔2017 es **1:1 perfecto en ambas direcciones (116/116)** →
   crosswalk completo reconstruido:
   `data/processed/crosswalk_estrato24_comuna.csv`. La geografía de
   asignación existe para toda la muestra 2024. Advertencia vigente: es la
   comuna de MUESTREO 2010, no la de gestación (ITT con error para
   migrantes pre-2010; movilidad 2017→2024 medida: 7,7%).
3. **Instituciones verificadas con fuentes** (R2): entrada al PADB por el
   primer control gestacional en el sistema público, sin incorporación
   retroactiva de niños ya nacidos; 159 comunas piloto desde mediados de
   2007 (seleccionadas por infraestructura de maternidades — NO aleatorio),
   cobertura nacional a inicios de 2008; techo de cobertura 75-80% de los
   nacimientos. Las fechas comunales exactas existen en el MDS (las usó
   Clarke, Cortés & Vergara, *J. Population Economics* 2020) pero no están
   publicadas online: obtenerlas vía Ley de Transparencia o de los autores.
4. **Novedad acotada** (R2): nacimiento ya evaluado (Clarke et al. 2020);
   niñez media ya evaluada (Rude 2022, ifo WP 372, con SIMCE 4º básico).
   La adolescencia y la salud mental siguen libres — ese es el margen.
5. **Econometría exigida** (R1): el rollout es corto (~6-12 meses entre
   piloto y cobertura nacional) → el estimando honesto es "diferencial de
   exposición temprana a un programa inmaduro", no efecto de régimen;
   estimadores robustos a adopción escalonada (Callaway-Sant'Anna /
   Sun-Abraham, solo not-yet-treated), descomposición de Goodman-Bacon,
   event-study en tiempo-a-adopción, inferencia por wild cluster bootstrap
   y aleatorización permutando fechas de adopción entre comunas, familias
   de outcomes con q-values.
6. **Líneas base asimétricas** (R3): TVIP 2010 solo existía para 30+ meses
   → los expuestos (nacidos 2008-09) no tienen TVIP de línea base; las
   pre-tendencias se testean con Battelle/EEDP 2010 (aplicados desde los
   6 meses) sobre los NO expuestos por ola de adopción.

### Carga de la prueba antes de escribir el paper

1. Conseguir las fechas de implementación comunal del MDS (Transparencia o
   Clarke). Sin ellas no hay diseño.
2. Primera etapa within-cohorte entre comunas (piloto vs resto, EF de
   año-mes de nacimiento) ≥ ~15 pp en recepción/uso ChCC.
3. Pre-tendencias planas en Battelle/EEDP 2010 de los nacidos 2006-07 por
   ola de adopción comunal.
4. Balance de características comunales por ola + robustez a excluir
   regiones más golpeadas por el 27F.

### Veredicto final del proceso

| Resultado | Estado |
|---|---|
| RD corte escolar (cualquier claim causal) | MUERTO |
| Conclusión metodológica: RD mensual no identificable en Chile; batería permutacional como estándar | SOBREVIVE |
| Primera etapa institucional (rampa abril-junio) como hecho descriptivo | SOBREVIVE |
| DiD ChCC con outcomes adolescentes (ITT comuna×mes, fechas MDS) | SOBREVIVE condicional a la carga de la prueba 1-4 |
| Plan B nominado por los revisores si (1) falla | Terremoto 27F: dosis regional × edad, outcomes salud mental 2024 |

---

## Candidato 3: Desastres naturales y desarrollo humano (27F → adolescencia) — VIVO con matices

Plantilla "school prayer": shock fechado (27-02-2010), exposición diferencial
por intensidad comunal × edad al golpe (gestación a 4 años), outcomes de vida
14 años después, sobre una cohorte que ya estaba siendo medida antes del shock.

**Verificación de literatura (dos rastreadores con fuentes, sep-2026):**

- El campo publica en JDE (Caruso & Miller 2015; Caruso 2017), JOLE
  (Karbownik & Wray 2019), JHR 2023 (terremoto Pakistán: Andrabi, Daniels &
  Das; huracán Brasil), Demography (Torche 2011, 2018 — seguimiento a los
  7 años), y el techo del paradigma estrés temprano → salud mental es AER
  2018 (Persson & Rossin-Slater). Demanda viva: Annual Review of Resource
  Economics 2025 sobre desastres y capital humano; salud mental adolescente
  en JPE 2026 (Cuddy & Currie).
- **Competencia directa sobre 27F + ELPI**: Gillmore, "Natural Disasters
  and Early Child Development: Evidence from an Earthquake" — SSRN 5106675
  (feb-2025) y **ya publicado en Economics of Education Review 115 (2026),
  art. 102817** (capítulo de su tesis en UT Austin 2023): dif-en-dif
  intensidad Mercalli comunal × ELPI, exposición prenatal-4 años, TVIP
  −0,06 DE por unidad Mercalli medido ~7 años después (ronda 2017, edades
  8-12), peor en varones; mecanismos: tabaquismo/estrés materno, caída
  transitoria de ingreso ("stress-budget trap"). Berthelon, Kruger &
  Sánchez (Economics & Human Biology 2021) cubren estrés in utero → 0-3
  años; Morales et al. (Soc Psychiatry 2023) CBCL a 1½-3 años con
  matching. Nada toca la ronda 2024.

**Veredicto**: muere la versión fuerte ("nadie ha estudiado a los niños del
27F") — la infancia de estos niños YA está estudiada. Sobrevive la versión
precisa: **nadie ha llegado a la adolescencia** (ronda 2024, n=10.003,
14-18 años, PHQ-4, conductas de riesgo, liberada nov-2025) ni a la salud
mental adolescente, que en economía del desastre temprano es una celda
vacía a nivel mundial. El paper viable es "el primer seguimiento a la
adolescencia y a la salud mental", citando y diferenciándose explícitamente
de Gillmore (horizonte, outcomes, canal parental medido ronda a ronda:
depresión materna, PSI, HOME) y explotando además edad-al-golpe como test
de períodos críticos.

**Riesgo estratégico (actualizado)**: el paper de Gillmore ya está
publicado y cerrado — extenderlo a 2024 sería para él un proyecto nuevo,
lo que baja la temperatura de la carrera sin eliminarla; a cambio, deja
evidencia publicada y citable de la herida en la infancia sobre la que la
pregunta de adolescencia es la continuación natural. Ejecutar rápido sigue
siendo ventaja.

**Ejecución (todo con datos ya en mano o públicos):** intensidad sísmica
por comuna del ShakeMap USGS del 27F × las 116 comunas de selección
(crosswalk ya construido) × edad al 27F por mes de nacimiento; primera
etapa/validación con el módulo de terremoto de ELPI 2012 (h4*); outcomes
2024 (PHQ-4, GAD-2, riesgo, TVIP) y trayectoria 2010-2017; canal parental
(CESD/EPDS materna, ingresos, HOME, PSI).
