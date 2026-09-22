# 27-F y salud mental adolescente (ELPI 2024) — primera pasada

Maquinaria de la replicación de Gillmore aplicada a la ola 2024 (adolescentes 14–18, todos de la cohorte original expuesta 0–4 años). β>0 = **peor** salud mental. EE cluster por comuna de selección (estrato). Pesos f_exp. Controles: sexo, edad, nº de hijos de la madre, línea base 2010 pre-terremoto (educación y edad de la madre, tamaño del hogar, ruralidad) y salud mental previa familiar (2012), con indicadores de missing.

**Diseño A** — gradiente edad-a-la-exposición × EQ (FE de comuna de selección + cohorte; referencia: 36–59 meses el 27-F). Es el análogo a la Fig. B.1 del paper, 14 años después: ¿deja más cicatriz la exposición más temprana?

| Outcome | 0–11m×EQ | 12–23m×EQ | 24–35m×EQ | n | clusters |
|---|---:|---:|---:|---:|---:|
| PHQ-4 (z) | -0.000 (0.049) | -0.045 (0.049) | -0.147*** (0.041) | 9,996 | 116 |
| PHQ-2 positivo | -0.025 (0.028) | -0.039* (0.021) | -0.072*** (0.023) | 9,996 | 116 |
| GAD-2 positivo | -0.032 (0.022) | -0.044** (0.021) | -0.105*** (0.019) | 9,996 | 116 |
| CBCL2-T 2024 (z) | -0.020 (0.061) | -0.075 (0.047) | -0.129*** (0.040) | 9,970 | 116 |
| ΔCBCL 2017→2024 (z) | 0.245*** (0.085) | 0.234*** (0.068) | 0.244*** (0.040) | 7,169 | 116 |

**Diseño B** — nivel: comunas EQ vs no-EQ condicional a la línea base 2010 (sin FE de comuna; asociación condicional, no DiD — sin cohorte no expuesta en 2024 el nivel no es identificable tipo Gillmore).

| Outcome | β EQ | (EE) | n | clusters |
|---|---:|---:|---:|---:|
| PHQ-4 (z) | 0.035 | (0.034) | 9,996 | 116 |
| PHQ-2 positivo | 0.014 | (0.014) | 9,996 | 116 |
| GAD-2 positivo | 0.008 | (0.013) | 9,996 | 116 |
| CBCL2-T 2024 (z) | 0.050 | (0.032) | 9,970 | 116 |
| ΔCBCL 2017→2024 (z) | -0.142* | (0.074) | 7,169 | 116 |

**Diseño C** — la fila ΔCBCL 2017→2024 usa al MISMO niño en ambas olas (z por ola): en A identifica si la trayectoria hacia la adolescencia difiere por edad de exposición dentro de comuna; en B, si difiere entre comunas EQ y no-EQ.

## Lectura de la primera pasada
1. **Gradiente por edad (A)**: dentro de comuna, los expuestos a los 24–35 meses muestran MENOS síntomas a los 14–18 que los expuestos a los 36–59 meses (ref.): PHQ-4 −0,15 DE, GAD-2 −0,10, PHQ-2 −0,07, CBCL −0,13 (todos sig. al 1%). Los expuestos en la infancia (0–11m) no difieren del ref. Es decir, la cicatriz de salud mental autorreportada la concentran los expuestos en edad PREESCOLAR (3–5 años, edad de memoria episódica del evento) y, en menor medida, la primera infancia — patrón en U consistente con el canal de memoria traumática más que con el fetal.
2. **Trayectoria CBCL (C)**: dentro de comunas EQ, los tres bins más jóvenes EMPEORAN ≈+0,24 DE su CBCL 2017→2024 relativo al grupo 36–59m — equivalente a que el déficit no-cognitivo que Gillmore midió en 2017 (concentrado en los mayores) se DESVANECE hacia la adolescencia en el reporte del cuidador, mientras el autorreporte (PHQ/GAD) de esos mismos mayores sigue peor: los padres dejan de verlo, el adolescente lo sigue reportando.
3. **Niveles (B) nulos**: sin cohorte no expuesta, la comparación geográfica pura a 14 años no detecta nivel (esperable: 14 años de recuperación + heterogeneidad regional).

## Notas de identificación
- La ola 2024 no tiene cohorte concebida post-27F ⇒ el DiD cohorte×geografía del paper no es estimable; A explota la variación de dosis por edad (la que el propio paper usa en su Fig. B.1), B es descriptivo-condicional y C es panel intra-niño.
- Intensidad: binario regional oficial (crosswalk estrato24→CUT →región). Siguiente paso natural: PGA del USGS por comuna (dosis continua) sobre el CUT del crosswalk.
- PHQ-4 construido de los ítems d4_1–d4_4 re-escalados 0–3 (la variable phq4 pública es categórica).
