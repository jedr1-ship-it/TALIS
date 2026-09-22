# 27-F y salud mental adolescente (ELPI 2024) — primera pasada

Maquinaria de la replicación de Gillmore aplicada a la ola 2024 (adolescentes 14–18, todos de la cohorte original expuesta 0–4 años). β>0 = **peor** salud mental. EE cluster por comuna de selección (estrato). Pesos f_exp. Controles: sexo, edad, nº de hijos de la madre, línea base 2010 pre-terremoto (educación y edad de la madre, tamaño del hogar, ruralidad) y salud mental previa familiar (2012), con indicadores de missing.

**Diseño A** — gradiente edad-a-la-exposición × EQ (FE de comuna de selección + cohorte; referencia: 0–11 meses el 27-F; dummies explícitas, diseño de rango completo). Es el análogo a la Fig. B.1 del paper, 14 años después: ¿deja más cicatriz la exposición más temprana?

| Outcome | 12–23m×EQ | 24–35m×EQ | 36–59m×EQ | n | clusters |
|---|---:|---:|---:|---:|---:|
| PHQ-4 (z) | -0.045 (0.078) | -0.147** (0.069) | -0.044 (0.060) | 9,996 | 116 |
| PHQ-2 positivo | -0.014 (0.038) | -0.048 (0.041) | -0.010 (0.031) | 9,996 | 116 |
| GAD-2 positivo | -0.012 (0.033) | -0.073** (0.032) | -0.016 (0.028) | 9,996 | 116 |
| CBCL2-T 2024 (z) | -0.055 (0.095) | -0.109 (0.075) | -0.077 (0.069) | 9,970 | 116 |
| ΔCBCL 2017→2024 (z) | -0.012 (0.124) | -0.002 (0.102) | -0.050 (0.106) | 7,169 | 116 |

**Diseño B** — nivel: comunas EQ vs no-EQ condicional a la línea base 2010 (sin FE de comuna; asociación condicional, no DiD — sin cohorte no expuesta en 2024 el nivel no es identificable tipo Gillmore).

| Outcome | β EQ | (EE) | n | clusters |
|---|---:|---:|---:|---:|
| PHQ-4 (z) | 0.035 | (0.034) | 9,996 | 116 |
| PHQ-2 positivo | 0.014 | (0.014) | 9,996 | 116 |
| GAD-2 positivo | 0.008 | (0.013) | 9,996 | 116 |
| CBCL2-T 2024 (z) | 0.050 | (0.032) | 9,970 | 116 |
| ΔCBCL 2017→2024 (z) | -0.142* | (0.074) | 7,169 | 116 |

**Diseño C** — la fila ΔCBCL 2017→2024 usa al MISMO niño en ambas olas (z por ola): en A identifica si la trayectoria hacia la adolescencia difiere por edad de exposición dentro de comuna; en B, si difiere entre comunas EQ y no-EQ.

## Lectura (corregida)
1. **Gradiente por edad (A)**: patrón en U dentro de comuna. Relativo a los expuestos de bebés (0–11m, ref.), los expuestos a los 24–35 meses muestran MENOS síntomas a los 14–18 (PHQ-4 −0,15**, GAD-2 −0,07**), y los expuestos a los 36–59 meses vuelven al nivel de los bebés (≈−0,04, n.s.). El contraste 36–59 vs 24–35 (la 'edad de memoria' vs el valle) es +0,10* en PHQ-4 y +0,06** en GAD-2 — ver reports/regresion_paper.md (script 11) para la versión definitiva con columnas, contraste y wild bootstrap por región.
2. **Trayectoria CBCL (C)**: SIN gradiente por edad de exposición (contrastes ≈0, n.s.). En nivel (B), en comunas EQ el CBCL cae ≈0,14 DE* 2017→2024 relativo a no-EQ.
3. **Niveles (B) nulos** en 2024: sin cohorte no expuesta, la comparación geográfica pura a 14 años no detecta nivel (esperable: 14 años de recuperación + heterogeneidad regional).

## Nota de corrección
La primera versión de este informe usaba `C(bin):EQ`, que incluía los 4 bins×EQ; su suma es EQ, colineal con los FE de comuna ⇒ diseño singular (rango 139 de 141) resuelto por pseudoinversa: los niveles individuales eran arbitrarios (solo las diferencias entre bins estaban identificadas). En particular, el resultado '+0,24*** de empeoramiento ΔCBCL en los bins jóvenes' era un ARTEFACTO del reparto de la pseudoinversa; con dummies explícitas (rango completo) desaparece. Los gradientes PHQ/GAD sobreviven con la referencia correctamente etiquetada (0–11m).

## Notas de identificación
- La ola 2024 no tiene cohorte concebida post-27F ⇒ el DiD cohorte×geografía del paper no es estimable; A explota la variación de dosis por edad (la que el propio paper usa en su Fig. B.1), B es descriptivo-condicional y C es panel intra-niño.
- Intensidad: binario regional oficial (crosswalk estrato24→CUT →región). Siguiente paso natural: PGA del USGS por comuna (dosis continua) sobre el CUT del crosswalk.
- PHQ-4 construido de los ítems d4_1–d4_4 re-escalados 0–3 (la variable phq4 pública es categórica).
