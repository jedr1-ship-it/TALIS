# Fase 0 — Ideas candidatas, kill-tests y ranking (28-09-2026)

Regla del juego: ninguna idea se vende sin kill-test barato previo (variación,
n, primera regresión cruda, quién lo hizo ya). Kill-tests internos en
`scripts/12_fase0_kill_tests.py`; competencia y datos externos verificados por
búsqueda web el 28-09-2026. **Gate 1: el usuario elige.**

## Ranking

### 1. La cicatriz adolescente del 27-F (edad de exposición × intensidad) — MI APUESTA
**Una línea**: vivir el terremoto de bebé o a los 3–4 años (no a los 2) aumenta
la depresión-ansiedad autorreportada a los 14–18 en 0,10–0,15 DE, los padres no
lo ven, y el déficit de vocabulario de Gillmore persiste (−0,24 DE).
- Kill-tests: **PASADOS** (scripts 08–11, esta sesión): Peabody largo plazo
  −0,24**; PHQ-4 en U por edad de exposición; CBCL del cuidador sin gradiente.
- Competencia (web, 28-09): con la ola 2024 no hay NINGÚN paper causal; existe
  un paper epidemiológico ELPI de exposición prenatal al 27-F → CBCL infantil
  (PMC10261207) y estudios de sismo+ACEs psicosociales (PubMed 35355336):
  citar y posicionar (adolescencia, autorreporte, dosis por edad = nuestro).
- Pendiente que la blinda: dosis continua PGA/MSK por comuna (crosswalk CUT
  listo), placebo con Battelle 2010, Romano–Wolf, bounds de atrición.
- Mecanismos ya disponibles dentro de ELPI: ACEs 2024 (idea 7), salud mental
  materna 2010/2012 (idea 2), estrés materno 2012 (Tabla 11 de Gillmore).

### 2. Transmisión intergeneracional de salud mental a 14 años — VIVA (sola o como mecanismo de 1)
**Una línea**: la depresión materna medida en 2010–2012 (postparto g19,
diagnóstico b64, checklist b55) predice la depresión-ansiedad autorreportada
del hijo a los 14–18, en el primer panel de 14 años de un país de renta media.
- Kill-test KT-F: **PASADO** — las variables existen y son ricas: 2010
  diagnóstico en embarazo (depresión g4a_1, ansiedad g4a_3, TEPT g4a_7),
  derivación g4b, **depresión postparto g19**; 2012: b2_* (embarazo del
  refresco: gestación DURANTE el 27-F para los nacidos 2010), b55o/p por
  familiar, b64 diagnóstico actual.
- Identificación: asociativa (panel + informantes cruzados); honesto como
  "fact paper" o como capítulo de mecanismos de la idea 1.

### 3. El estallido social como shock adolescente — VIVA con riesgo de datos
**Una línea**: la intensidad de protestas de oct-2019 en la comuna empeora la
trayectoria de salud mental 2017→2024 del mismo niño (11→15 años).
- Kill-test datos: COES Observatorio de Conflictos = base de eventos por
  comuna 2009–2020, ~90 variables, acceso libre (descarga aún no probada);
  la maquinaria intra-niño ΔCBCL 2017→2024 ya está construida (script 09/11).
- Competencia: hay estudios del estallido y salud mental (PubMed 38006846,
  Defensoría de la Niñez) pero ninguno panel intra-adolescente con dosis
  comunal. Confound serio y declarable: la pandemia cae entre las olas
  (mitigación: dosis continua condicional a región × urbano).

### 4. Postnatal de 12→24 semanas (Ley 20.545) y desarrollo a los 5–6 — MALHERIDA (poder)
**Una línea**: nacer justo después de oct-2011 (24 semanas de madre) mejora
el desarrollo a los 5–6 vs nacer justo antes (12 semanas).
- Kill-test KT-C: refresco 2012 con fecha y ola 2017: 2.142; nacidos 2011
  ≈68–87/mes (suave en el corte); ventana jul–dic 2011: n=427 (362 con
  Battelle, 376 con TVIP); ≈215 por lado del corte.
- Veredicto: como RD **muere**; como DiD de cohortes mensuales solo detecta
  efectos ≥0,25 DE (potencia ~80%) — un WP serio necesitaría el censo de
  nacimientos + registros (fuera de la ventana). Competencia: literatura de
  lactancia (INTA/CIAPEC) y equidad (PLOS One 2019); desarrollo infantil de
  largo plazo abierto.

### 5. Replicar Gillmore en Iquique-2014 e Illapel-2015 — MUERTA
**Una línea**: (pretendía) los sismos de 2014/2015 replican la cicatriz del
27-F en cohortes nuevas.
- Kill-test KT-B: la ELPI casi no muestrea el norte: regiones XV+I = 693
  niños en **5 comunas** (146 afectados / 67 controles); región IV = 868 en
  11 comunas (213 / **14 controles**). EE de la DiD cruda ≈ 774. Sin n ni
  clusters: muerta con datos ELPI.

### 6. Expansión de salas cuna JUNJI/Integra 2006–2010, efectos a los 14–18 — CONGELADA (datos)
**Una línea**: abrir sala cuna en tu comuna-cohorte aumenta asistencia y
outcomes adolescentes.
- Kill-test datos: en abierto solo capacidad/cupos ~2015 (datos.gob.cl);
  las aperturas históricas por comuna requieren pedido administrativo a
  JUNJI/Integra → fuera de la ventana de 4–6 horas. Novedad real (el corto
  plazo existe — Noboa-Hidalgo & Urzúa 2012 —, el largo plazo no).

### 7. El 27-F y las experiencias adversas (ACEs) reportadas a los 14–18 — MECANISMO DE 1
**Una línea**: la exposición temprana al terremoto aumenta las ACEs que el
adolescente reporta, y las ACEs median parte del efecto en PHQ/GAD.
- Kill-test: la batería ACEs existe en la ola 2024; cero costo marginal.
  No es paper standalone: entra como sección de mecanismos de la idea 1.

## Apuesta razonada
**Idea 1 con la 2 y la 7 dentro como mecanismos** ("The Adolescent Scar of
Early-Life Disaster: Self-Reports, Parental Blindness, and the Age Profile of
Trauma"): medio camino ya corrido y commiteado, novedad verificada hoy, y la
robustez que la blinda (PGA por comuna) es factible con el crosswalk que ya
construimos. La 3 (estallido) es el mejor plan B y puede ser el segundo paper
del pipeline con la misma maquinaria.

## Fuentes de la verificación de competencia (28-09-2026)
- Paper ELPI prenatal 27-F → CBCL infantil: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10261207/
- Sismo + ACEs psicosocial: https://pubmed.ncbi.nlm.nih.gov/35355336/
- Estallido y salud mental: https://pubmed.ncbi.nlm.nih.gov/38006846
- Defensoría de la Niñez (estado de excepción y NNA): https://www.defensorianinez.cl/estud_y_estadi/estudio-efectos-del-estado-de-excepcion-y-posterior-crisis-social-2019-en-ninos-ninas-y-adolescentes/
- ELPI 2024 prensa (1 de cada 3 adolescentes mujeres con síntomas): https://www.pauta.cl/actualidad/2025/11/14/elpi-2024-una-de-cada-tres-adolescentes-mujeres-presenta-sintomas-moderados-o-severos-de-depresion-o-ansiedad.html
- ELPI cuarta ronda (Observatorio Social): https://observatorio.ministeriodesarrollosocial.gob.cl/elpi-cuarta-ronda
- COES Observatorio de Conflictos (informe anual 2020): https://politologia.cl/2020/11/10/informe-anual-del-observatorio-de-conflictos-2020/
- Ley 20.545 (texto): https://oig.cepal.org/sites/default/files/2011_ley20545_chl.pdf
- Postnatal y lactancia (INTA U. de Chile): https://inta.uchile.cl/noticias/192757/el-impacto-de-la-extension-del-permiso-postnatal-parental-en-chile
- Reforma de protección a la maternidad 2000–2015 (PLOS One): https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0221150
- Jardines infantiles en datos abiertos: https://datos.gob.cl/dataset?tags=Jardines+Infantiles
