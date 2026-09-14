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

## Candidato 2: DiD de Chile Crece Contigo a largo plazo — EN EVALUACIÓN (ronda 2)

Propuesto por el revisor institucional como el diseño que absorbe por
construcción la estacionalidad que mató al candidato 1 (EF de mes calendario
de nacimiento; identificación por la interacción cohorte × timing comunal
del despliegue 2007-2008).

**Factibilidad verificada en los datos (previa a la ronda 2)**

- Primera etapa observable: recepción de la "Guía de la gestación y el
  nacimiento" de ChCC (f29a, ELPI 2012) por trimestre de nacimiento del
  niño/a: 2-6% (nacidos 2006-2007) → 14,9% (2008T1) → 25,0% (2008T4) →
  30,9% (2009T1) → ~33% (2009T2-T3). El despliegue del programa dibujado
  en los datos.
- Geografía: `estrato` (comuna de selección de la muestra) tiene 116
  códigos comunales únicos — no 33 como sugería el reporte metodológico —
  más comuna de residencia en 2017 y 2024.
- Pieza externa pendiente: listado oficial de comunas piloto 2007 y fechas
  de incorporación comunal (en verificación por el revisor institucional).

**Amenazas encargadas a los revisores (ronda 2, en curso)**: adopción
escalonada y heterogeneidad (Goodman-Bacon; Callaway-Sant'Anna), recall
diferencial de f29a según edad del niño al reporte, migración comunal,
colinealidad cohorte×edad-al-test, cobertura del sistema público como techo
de la primera etapa, validez de los 116 códigos de `estrato`.
