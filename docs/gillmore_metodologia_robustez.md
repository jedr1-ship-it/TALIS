# Gillmore (2026, EER): metodología completa y controles de robustez

**Fuente estudiada**: versión publicada — Gillmore, R., "Natural disasters and early
child development: Evidence from an earthquake", *Economics of Education Review* 115
(2026) 102817, doi:10.1016/j.econedurev.2026.102817 — más su apéndice online (39 pp.).
Recibido 17-may-2025; revisado 29-jun-2026; aceptado 7-jul-2026. Autor en el
Departamento de Big Data del Banco Central de Chile (roberto.gillmore@gmail.com).
Agradece a Linden, Murphy, Quezada, Angelucci, Ayesh; editora Sandra McNally; 3 referees.
JEL: I25, O1, Q54, I120.

> Nota: la versión publicada difiere de la tesis doctoral (UT Austin 2023, cap. 2) en
> puntos importantes; ver §9.

---

## 1. Pregunta y resultado central

Efecto del terremoto 27-F (Mw 8,8, 27-feb-2010) sobre desarrollo cognitivo y
no-cognitivo de niños expuestos **entre la gestación y los 4 años**, medidos 2 años
(corto plazo) y 7 años (mediano plazo) después.

Resultado principal (especificación preferida, col. 3):
- **Mediano plazo**: Peabody/TVIP **−0,17 DE** (p<0,05) ≈ pérdida de **0,8 años de
  escolaridad** (equivalencia Evans & Yuan 2019); CBCL2 **−0,13 DE** (p<0,10; RW p=0,10).
- **Corto plazo**: Peabody −0,14 DE (p<0,10) pero **frágil**: no sobrevive la
  corrección de Romano–Wolf (p ajustado = 0,12). Battelle −0,08 n.s.; CBCL1 +0,13 n.s.
- **Niños vs niñas**: el efecto cognitivo lo concentran los **varones** (−0,25 DE
  corto y mediano plazo, p<0,05/0,01; niñas −0,05/−0,09 n.s.; p-valor de la triple
  interacción género = 0,050/0,081). En CBCL2 varones −0,225 (p<0,05) pero la
  diferencia por género no es significativa (p=0,306).
- Interpretación mecanismos: **"stress-budget trap"** — trauma materno (tabaquismo ↑,
  estrés clínico ↑) + shock de activos (reparaciones ≈ 1 mes de ingreso pc) que
  desvía recursos de la calidad del entorno doméstico, con cantidad de inversiones
  formales (vacunas, controles, matrícula) intacta.

---

## 2. Datos (4 fuentes)

1. **ELPI, olas 2012 y 2017** (la 2010 solo para el test de atrición). Tests usados:
   los tres disponibles para todas las cohortes en ambas olas —
   - **Peabody/TVIP** (vocabulario receptivo, ≥30 meses, normas hispanas);
   - **CBCL** (99 ítems reportados por el cuidador; **invierte el puntaje** para que
     más alto = mejor; CBCL1 18–72 m, CBCL2 ≥73 m, normas hispanas);
   - **Battelle screening** (7–84 m; mezcla dominios; el autor advierte que como
     screening no se analiza por subescalas).
   - Estandarización propia: **z-scores (media 0, DE 1) dentro de cada tramo de edad**.
   - Peso/talla/gestación al nacer transcritos del **Carnet de Salud del Niño** (no
     puro recuerdo).
2. **Panel CASEN Post-Terremoto 2009–2010** (misma vivienda antes y ~3 meses después
   del shock): ingreso de corto plazo, daño a la vivienda, costo de reparaciones,
   estrés (escala de trauma de Davidson), problemas de salud atribuidos al terremoto.
3. **Registros Vitales** (universo de nacimientos 2008–2015): resultados al nacer,
   migración (con EF de madre), fecundidad, razón de sexos, selección en observables.
4. **Intensidad sísmica**: clasificación oficial de comunas/regiones afectadas de
   **Astroza et al. (2010)** (binaria) y **PGA de los ShakeMaps del USGS** (continua,
   0–0,53 m/s²; robustez). 145 clusters comunales (179 comunas en ELPI; 143 marcadas
   como terremoto ≈ 79–80% de la población).

**Definición de grupos por horizonte** (Tabla C.2/ap. T4, el punto más sutil del
diseño):
- *Corto plazo*: afectados (cohortes 2006–2010) medidos en la **ola 2012** con 2–6
  años vs. controles nacidos después (2011–2015) medidos en la **ola 2017** con 2–6
  años → compara **a la misma edad**, en distinta ola (EF de ola η_w).
- *Mediano plazo*: ambos grupos en la **ola 2017**: afectados con 7–11 años vs.
  controles con 2–6 → misma ola, distinta edad (tests normalizados por edad; ver
  robustez de edad-al-test, §7.11).

---

## 3. Especificación econométrica (ec. 1 publicada)

Y_imtw = α + β·(Affected_it × Earthquake_m) + X_imt + ψ_m + θ_t + η_w + e_imtw

- **Affected_it** = 1 si el niño estaba **en gestación o tenía hasta 4 años** el
  27-F (cohortes 2006–2010); 0 si fue concebido después.
- **Earthquake_m** = 1 si la comuna pertenece a las regiones oficialmente afectadas
  (Valparaíso, Metropolitana, O'Higgins, Maule, Biobío, Araucanía; Astroza et al. 2010).
- **X_imt**: sexo, edad en meses al test, orden de nacimiento, edad y escolaridad de
  la madre, presencia del padre, tamaño del hogar, condición de salud mental previa
  de madre/padre/pariente. (Los "pre-quake controls" de la tesis desaparecen del set
  principal.)
- **ψ_m** EF de comuna; **θ_t** EF de cohorte de nacimiento; **η_w** EF de ola.
- **Tendencias lineales por comuna NO están en la especificación principal**: son la
  col. 4, tratadas como robustez (duplican el efecto por el artefacto de la cohorte
  2015; ver §6.1).
- Errores estándar **cluster por comuna (145)**; pesos muestrales de representatividad
  nacional.
- **β = intention-to-treat** y **cota inferior**: tres grupos de control (comunas poco
  afectadas; concebidos después en comunas afectadas y no afectadas); los concebidos
  después pueden estar indirectamente expuestos (estrés/ingresos), lo que atenúa β.
- Supuestos declarados: (i) los nacidos después son contrafactual válido (la
  heterogeneidad local no varía entre cohortes condicional a θ_t); (ii) las
  diferencias entre cohortes son comparables entre comunas afectadas y no (ψ_m).

---

## 4. Validez de la identificación (sección 3.4 del paper)

1. **Event-study de cohortes (paralel trends)** — Figs. 2 y 3: interacción cohorte ×
   terremoto, referencia = cohorte 2011; cohortes placebo 2012–2015 primero.
   Coeficientes 2012–2014 ≈ 0 (Peabody); cohortes expuestas 2006–2010 negativas.
   **Test F conjunto de placebos 2011–2014: p = 0,25**. Tendencias crudas de apoyo en
   Figs. D.2/D.3.
2. **Anomalía de la cohorte 2015** (ap. B.1): coeficiente negativo significativo que
   NO es violación de tendencias paralelas sino **efecto suelo psicométrico** del
   Peabody a los 2,5 años: media inflada (105,6 vs 104,6), varianza comprimida (DE
   12,8 vs ≈18,5), mínimo censurado (80 vs 66), n=512 y seleccionado (solo los mayores
   del año cumplen la edad mínima). Consecuencia: **con la 2015 dentro, las tendencias
   lineales comunales duplican β; sin la 2015 (Tabla C.22/ap. T24) los estimados son
   estables con y sin tendencias** (Peabody MP −0,218*** sin trends / −0,222** con).
3. **Placebo "terremoto falso"** (Tabla C.14): solo concebidos post-27F, misma
   clasificación de comunas, mitad vieja = tratada → **todo n.s.**
4. **Falsificaciones** (C.16, C.17): solo regiones no afectadas con su PGA → n.s.;
   norte "tratado" vs sur → ruido, n.s.
5. **Migración**: 0,78% entre olas 2010–2012 (afectada→no afectada 0,02%); Registros
   Vitales con **EF de madre** (madres con ≥2 partos, uno antes y otro después):
   efectos significativos pero minúsculos (C.18); 1,32% migra de afectada a no
   afectada; 80% de la población vive en zona afectada.
6. **Fecundidad endógena** (C.19): nº de nacimientos por comuna-tiempo (Vitales) n.s.;
   "¿embarazo planificado?" (ELPI, ec. 1) n.s.; características de madres pre/post en
   ELPI (C.6) n.s.; en el universo de Vitales (C.8) significativas por potencia pero
   económicamente irrelevantes.
7. **Mortalidad selectiva** (Trivers-Willard): razón de sexos al nacer à la
   Karbownik & Wray (2019) con Vitales y ELPI a nivel comuna×mes-año → **sin efecto**
   (C.19 cols. 3–4); letalidad <9 años ≈ 2,09/100.000 (Lastra et al. 2012) y C.13.
8. **Atrición**: regresión de "missing en 2017 | entrevistado 2010/2012" sobre el
   tratamiento → **+6 pp en comunas afectadas** (C.20) → sesgo hacia cero (los más
   golpeados salen más). Mitigación: (a) pesos longitudinales en todo el paper;
   (b) estimados sin pesos ≈ iguales (C.32); (c) **bounds de Lee (2009) y de
   Kling–Liebman** (C.21/ap. T22): Peabody MP acotado en [−0,137**, −0,291***] (Lee) y
   robusto a imputar ±0,1 DE; con ±0,25 DE pierde significancia (escenario que implica
   0,5 DE de brecha entre attritors, considerado extremo); CBCL2 análogo. El autor
   argumenta que los bounds relevantes son los superiores (atrición correlacionada con
   daño).

---

## 5. Controles de robustez del resultado principal (sección 4.3 + apéndice)

| # | Check | Tabla | Resultado |
|---|-------|-------|-----------|
| 1 | Tendencias lineales por comuna | col. 4 de T2/T3 | Peabody MP −0,28***; CBCL2 −0,22**; ver caveat cohorte 2015 |
| 2 | Excluir cohorte 2015 | C.22 | estable con/sin trends (−0,218***/−0,222**) |
| 3 | **PGA continuo** como exposición | C.23 | Peabody CP −0,0054**, MP −0,0062***, CBCL2 −0,0041* por 0,01 m/s²; mismo patrón |
| 4 | **Distancia al epicentro** | C.24 | consistente CP y MP |
| 5 | Cutoffs alternativos del binario: PGA p25/p50/p75 | C.26 | robusto en todos los umbrales (no depende de la clasificación oficial) |
| 6 | **EF regionales + cluster regional con Wild Cluster Bootstrap** (15 regiones) | C.27 | magnitudes y significancia estables |
| 7 | Justificación del nivel comunal | C.12 | PGA varía mucho dentro de región (Biobío 0,25–0,53); dosis-respuesta monótona; política post-desastre descentralizada |
| 8 | Cambiar grupo de control: comunas **adyacentes** vs **extremos** del país | C.28 | magnitud y signo estables; pierde algo de significancia (mitad de control) |
| 9 | Excluir cohorte 2011 (control potencialmente contaminado) | C.30 | Peabody estable; CBCL MP se vuelve impreciso (solo 250 obs. de control) |
| 10 | Excluir región del Maule (44% del daño estructural) | C.29 | consistente con lo principal |
| 11 | **Edad-al-test** (MP compara 7–11 vs 2–6): ventanas locales 2010-vs-2011 (12 meses de brecha) y ampliaciones | C.31 | Peabody −0,249 DE en la ventana estrecha; ≈−0,20 en 2009–2012; CBCL −0,20→−0,15 → el efecto NO se disipa al igualar edades (se refuerza) |
| 12 | **DDD tsunami**: triple interacción con comunas costeras | C.25 | n.s. y pequeña → no es daño localizado del tsunami |
| 13 | Sin pesos muestrales | C.32 | cuantitativamente similar |
| 14 | **Romano–Wolf** (FWER, 500 reps; preferido sobre q-values de Anderson) | C.33 | p ajustados: Battelle CP 0,26; Peabody CP 0,12; CBCL1 0,22; **Peabody MP 0,02; CBCL2 MP 0,10** |
| 15 | Especificación pooled 2012+2017 con X×η_w | nota 11 | similar, "available upon request" |
| 16 | Validación de intensidad con microdatos | T10, C.13 | binario y PGA predicen estrés (Davidson) y destrucción; letalidad concentrada donde PGA máximo |

---

## 6. Mecanismos (sección 5) y su propia validación

1. **Resultados al nacer** (T5, solo in utero; control = nacidos antes): talla al
   nacer **−0,38 cm***; peso, LBW, semanas y prematurez n.s. Validación: tendencias
   crudas por cohorte (Fig. D.5); réplica con el universo de **Registros Vitales**
   (C.39): talla −0,125 cm significativa, económicamente modesta. Conclusión: el canal
   neonatal clásico NO explica el déficit.
2. **Inputs de salud** (T6): vacunas, lactancia (meses), control de embarazo (=1 y nº)
   → todo n.s.; tendencias crudas D.6; matrícula de sala cuna/colegio estable a 3
   meses (CASEN) y 2 años (ELPI) (C.11) → la **cantidad institucional se preservó**.
3. **Ingreso y trabajo materno** (T7; DiD geográfico × tiempo del hogar, no cohorte):
   a 3 meses (CASEN panel): ingreso pc **−10%** (−12.833 CLP**) y **LFP materna −5,4
   pp** (−12%); a 2 años (ELPI): −6% n.s. y LFP n.s. → shock transitorio de flujo.
4. **Shock estructural de activos** (T8, CASEN, corte transversal con PGA):
   daño mayor +8,7 pp***; daño menor +32,6 pp***; costo de reparación ≈ **98.577 CLP***
   (≈ 1 mes de ingreso pc); **+10,2 pp*** de probabilidad de financiar reparaciones
   con recursos propios. Defensa de exogeneidad: **PGA no correlaciona con
   características 2009** (ingreso, educación y edad de la madre, presencia del padre,
   calidad de la vivienda; C.10).
5. **Conductas de riesgo maternas** (T9; tratadas: embarazo o 0–6 meses el 27-F;
   control: >6 meses y no nacidos): índice "cualquiera" **+8,0 pp** (+42% relativo);
   **fumar +4,6 pp*** (+41% relativo — ≈8× la elasticidad de un alza de impuestos,
   Evans & Ringel 1999); alcohol +5,6 pp n.s.; drogas +3,0 pp n.s. (y D.4 muestra que
   para alcohol/drogas las tendencias paralelas NO se sostienen → el autor
   explícitamente limita su interpretación).
   - **Margen extensivo vs intensivo**: intensidad incondicional (cigarrillos/mes) por
     **PPML** −19% n.s.; recortando el top 1% (≥70 cig/mes) se vuelve +0,825
     significativa; condicional en fumar (>0) −0,36 n.s. (C.41) → el efecto es
     **iniciación/recaída**, no más cigarrillos entre fumadoras — y la literatura
     médica (DeCicca et al. 2022) dice que el daño marginal fetal es máximo justo a
     niveles bajos.
   - Control alternativo solo ">6 meses" (C.40): misma magnitud, menos precisión
     (muestra −37%).
   - Error de recuerdo: discutido de frente (nota 39): sería amenaza solo si fuera
     **diferencial** por tratamiento; D.4 no muestra divergencia en cohortes placebo.
6. **Estrés materno** (T10 CASEN transversal: +9,2 pp*** de estrés clínico Davidson;
   +2,3 pp*** de problemas de salud atribuidos; T11 **DiD en ELPI 2012**: madres de
   cohortes 2006–2010 vs madres nuevas de 2011 → **+2 pp*** de estrés clínico
   [insomnio, pánico, recuerdos traumáticos], robusto a 3 definiciones clínicas
   (PC-PTSD-5 ≥3; sindrómica; núcleo clínico) y a binario/PGA.
7. **Síntesis (stress-budget trap)**: dos cicatrices — biológica-conductual para
   gestación–6 meses (tabaco+estrés), estructural-de-recursos para 0–4 años
   (reparaciones desvían liquidez de la calidad del entorno) — con cantidad formal de
   inversión intacta. Latencia del CBCL (nulo a los 2 años, −0,13 a los 7) leída con
   Currie-Almond/Conti como desventaja latente que aflora al subir la exigencia.

---

## 7. Heterogeneidad

- **Género** (T4): motor del resultado cognitivo (varones −0,25** / −0,26***;
  niñas n.s.; triple interacción p=0,05 CP / 0,08 MP). Balance por género ok (C.5,
  C.7).
- **Educación de la madre** (C.36): <media −0,172** MP vs ≥media −0,204* — **sin
  diferencia** (p=0,57). Ídem edad de la madre (C.34; leve ventaja de madres mayores
  en CP que se disipa), presencia del padre (C.35), educación del padre (C.37),
  ingreso (C.38, con caveat de endogeneidad del ingreso 2017). Lectura del autor: el
  desastre **desbordó los amortiguadores privados** de todos los estratos.

---

## 8. Numeritos de referencia rápida

| Outcome | CP col.3 | CP col.4 (trends) | MP col.3 | MP col.4 | RW p (col.3) |
|---|---|---|---|---|---|
| Battelle | −0,081 (0,094) | −0,232* | — | — | 0,26 |
| Peabody | −0,141* (0,086) | −0,292*** | **−0,174**\*\* (0,069) | −0,280*** | CP 0,12 / **MP 0,02** |
| CBCL | +0,126 (0,100) | +0,043 | **−0,129*** (0,076) | −0,220** | CP 0,22 / MP 0,10 |

n: 13.070 / 14.205 / 11.654 (CP); 14.069 / 11.568 (MP). 145 clusters.

---

## 9. Tesis (2023) vs. versión publicada — qué cambió

| Dimensión | Tesis UT Austin 2023 | EER 2026 |
|---|---|---|
| Tratamiento | in utero–**5** años | in utero–**4** años |
| Exposición principal | **Mercalli continuo** (Affected×Mercalli_j) | **Binario oficial** (Affected×Earthquake_m); Mercalli desaparece, PGA/distancia como robustez |
| Tendencias comunales λ_jt | en la especificación principal | movidas a robustez (col. 4) por el artefacto 2015 |
| CBCL mediano plazo | −0,035 **n.s.** | **−0,13*** (significativo) |
| Magnitud titular | −0,06 DE por unidad Mercalli | −0,17 DE (binario) ≈ 0,8 años de escolaridad |
| Paralel trends | no había event-study | event-study de cohortes + F conjunto + raw trends |
| Atrición | regresión simple (B.12) | +6 pp diferencial + **bounds Lee y Kling–Liebman** |
| MHT | no | **Romano–Wolf** |
| Tsunami | no tratado | DDD costero |
| Inferencia regional | no | EF región + **wild cluster bootstrap** |
| Mecanismos | fumar +1,1 pp/unidad; ingreso −12%/unidad a 2 meses | fumar +4,6 pp (margen extensivo, PPML); ingreso −10% + **LFP −5,4 pp**; **reparaciones/activos**; **estrés Davidson + DiD madres**; talla −0,38 cm |
| Marco interpretativo | mecanismos sueltos | **"stress-budget trap"** |
| Magnitud del sismo citada | "8th strongest" (tesis)/"12th" (según ranking usado) | "6th strongest ever recorded" |
| Controles X | incluía pre-quake controls (ingreso pc pre, madre trabajaba, nº hermanos + dummy missing) | set más corto sin pre-quake en la principal |

---

## 10. ¿Está disponible el código? **NO.**

Verificado el 2026-09-22:

- El artículo **no tiene sección "Data availability" ni repositorio de replicación**.
  El único material suplementario ("Appendix A. Supplementary data") es el PDF del
  apéndice online (39 pp. de tablas/figuras), no código ni datos.
- *Economics of Education Review* (Elsevier) **no exige depósito de código** (a
  diferencia de las revistas AEA con openICPSR).
- Búsquedas web (GitHub, SSRN, páginas de autor, Banco Central de Chile): **ningún
  repositorio público** asociado al paper ni al autor.
- El propio texto usa la fórmula "results… available upon request" (nota 11) → la vía
  es **escribir al autor**: roberto.gillmore@gmail.com.

**Pero todos los datos son públicos**, así que la replicación completa es factible sin
el autor:

| Insumo | Fuente pública | Estado en nuestro repo |
|---|---|---|
| ELPI 2012 y 2017 (+2010 para atrición) | observatorio.ministeriodesarrollosocial.gob.cl | **ya descargado y verificado** (data/raw, data/interim) |
| Panel CASEN Post-Terremoto 2009–2010 | Observatorio MDS (Encuesta Post Terremoto) | descargable; no lo tenemos aún |
| Registros/Estadísticas Vitales de nacimientos 2008–2015 | INE/DEIS-MINSAL (microdato público) | no lo tenemos aún |
| Intensidades Astroza et al. (2010) | PDF citado en el paper: eqclearinghouse.org (Informe de Intensidades) | pendiente de digitalizar (tabla por comuna) |
| PGA por comuna | USGS ShakeMap del evento (official20100227063411530_30) | pendiente (raster→centroides comunales) |

---

## 11. Lecciones para nuestro paper (27F → adolescencia, ELPI 2024)

Checklist de lo que los referees de este mismo journal le exigieron y nos exigirán:

1. Event-study por cohorte con F conjunto de placebos + tendencias crudas.
2. Robustez a: intensidad continua (PGA/Mercalli) y binaria con cutoffs, distancia al
   epicentro, EF regionales + wild bootstrap, excluir Maule, DDD costero (tsunami),
   controles adyacentes/lejanos, tendencias comunales (con cuidado psicométrico).
3. Atrición: diferencial por tratamiento + bounds Lee y Kling–Liebman (nuestra
   atrición 2010→2024 es 34,1%, mucho mayor que su 6% 2012→2017 → esto será LA
   objeción n.º 1; tenemos factores longitudinales oficiales f_exp_10121724 y
   podremos además condicionar en covariables de línea base 2010 pre-shock).
4. Romano–Wolf sobre la familia de outcomes (PHQ-2/GAD-2/PHQ-4, CBCL, TVIP, riesgo).
5. Fecundidad/sex-ratio/migración con Vitales (mismas tablas, ventana ampliada).
6. Edad-al-test: nosotros no tenemos ese problema en 2024 (todos 14–18, un solo grupo
   etario) pero sí la comparación de cohortes dentro de la ventana 2006–09 (edad al
   shock 0–4): gemelo del análisis de su Fig. B.1 con la ventaja de que TODA nuestra
   muestra estuvo expuesta y la variación es dosis × edad-al-shock.
7. Ventajas nuestras sobre su diseño: (i) medimos al MISMO niño antes y después
   (panel intra-individuo; él compara cohortes distintas); (ii) salud mental
   adolescente autorreportada (PHQ/GAD/ACEs), no reporte parental; (iii) su cota
   inferior por contaminación del control no nos aplica igual (nuestro margen es
   dosis-respuesta dentro de expuestos); (iv) su módulo h4/h5 de 2012 (síntomas y
   consulta psicológica post-27F) nos da la "primera etapa" psicológica a nivel hogar.
