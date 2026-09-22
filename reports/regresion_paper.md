# La regresión del paper: 27-F y salud mental a los 14–18

Ec.: `Y_imc = α + Σ_a β_a(Bin_a×EQ_m) + γ_a Bin_a + ψ_m + θ_c + X'δ + ε`. Referencia: expuestos con **0–11 meses** el 27-F. β>0 = peor salud mental. FE de comuna de selección PRE-terremoto (ψ_m, absorbe EQ) y de cohorte (θ_c). EE cluster por comuna; inferencia clave re-chequeada con wild bootstrap por región. Pesos f_exp 2024. Col. (2) añade X pre-terremoto (sexo, edad, línea base 2010), col. (3) sensibilidad con controles 2012 (nº hijos, salud mental familiar), col. (4) excluye la RM.

## Panel A — niveles 2024 (autorreporte y cuidador)

**PHQ-4 (z), autorreporte**

| | (1) | (2) | (3) | (4) sin RM |
|---|---:|---:|---:|---:|
| 12–23m × EQ | -0.051 (0.080) | -0.044 (0.078) | -0.045 (0.078) | -0.030 (0.079) |
| 24–35m × EQ | -0.144** (0.072) | -0.153** (0.069) | -0.147** (0.069) | -0.120 (0.076) |
| 36–59m × EQ | -0.038 (0.064) | -0.048 (0.060) | -0.044 (0.060) | -0.011 (0.063) |
| Contraste 36–59 − 24–35 | 0.106* (0.060) | 0.105* (0.061) | 0.103* (0.060) | 0.109* (0.066) |
| n | 9,996 | 9,996 | 9,996 | 6,430 |
| Comunas (cluster) | 116 | 116 | 116 | 67 |

Wild cluster bootstrap-t por región (Webb, 4.999 reps, col. 3): 24-35m×EQ: p = 0.138; contraste: p = 0.067 (15 regiones).

**GAD-2 positivo (0/1), autorreporte**

| | (1) | (2) | (3) | (4) sin RM |
|---|---:|---:|---:|---:|
| 12–23m × EQ | -0.014 (0.032) | -0.012 (0.032) | -0.012 (0.033) | -0.018 (0.035) |
| 24–35m × EQ | -0.073** (0.032) | -0.076** (0.032) | -0.073** (0.032) | -0.064* (0.035) |
| 36–59m × EQ | -0.015 (0.027) | -0.018 (0.028) | -0.016 (0.028) | -0.015 (0.030) |
| Contraste 36–59 − 24–35 | 0.058** (0.027) | 0.058** (0.027) | 0.058** (0.027) | 0.049* (0.029) |
| n | 9,996 | 9,996 | 9,996 | 6,430 |
| Comunas (cluster) | 116 | 116 | 116 | 67 |

Wild cluster bootstrap-t por región (Webb, 4.999 reps, col. 3): 24-35m×EQ: p = 0.115; contraste: p = 0.109 (15 regiones).

**PHQ-2 positivo (0/1), autorreporte**

| | (1) | (2) | (3) | (4) sin RM |
|---|---:|---:|---:|---:|
| 12–23m × EQ | -0.017 (0.039) | -0.014 (0.038) | -0.014 (0.038) | -0.020 (0.041) |
| 24–35m × EQ | -0.046 (0.042) | -0.050 (0.041) | -0.048 (0.041) | -0.073 (0.045) |
| 36–59m × EQ | -0.008 (0.032) | -0.011 (0.031) | -0.010 (0.031) | -0.017 (0.035) |
| Contraste 36–59 − 24–35 | 0.038 (0.032) | 0.038 (0.033) | 0.038 (0.033) | 0.056 (0.036) |
| n | 9,996 | 9,996 | 9,996 | 6,430 |
| Comunas (cluster) | 116 | 116 | 116 | 67 |

**CBCL2-T 2024 (z), reporte del cuidador**

| | (1) | (2) | (3) | (4) sin RM |
|---|---:|---:|---:|---:|
| 12–23m × EQ | -0.057 (0.099) | -0.047 (0.096) | -0.055 (0.095) | -0.024 (0.100) |
| 24–35m × EQ | -0.121 (0.074) | -0.121 (0.075) | -0.109 (0.075) | -0.131 (0.084) |
| 36–59m × EQ | -0.086 (0.069) | -0.084 (0.068) | -0.077 (0.069) | -0.069 (0.074) |
| Contraste 36–59 − 24–35 | 0.034 (0.061) | 0.037 (0.059) | 0.032 (0.058) | 0.062 (0.063) |
| n | 9,970 | 9,970 | 9,970 | 6,412 |
| Comunas (cluster) | 116 | 116 | 116 | 67 |

## Panel B — persistencia intra-niño: ΔCBCL 2017→2024 (z)

Mismo niño en ambas olas (z por ola×edad); un ΔY sobre Bin×EQ equivale al FE de niño con dos períodos.

**ΔCBCL 2017→2024**

| | (1) | (2) | (3) | (4) sin RM |
|---|---:|---:|---:|---:|
| 12–23m × EQ | -0.030 (0.131) | -0.011 (0.125) | -0.012 (0.124) | -0.020 (0.128) |
| 24–35m × EQ | -0.009 (0.104) | -0.004 (0.102) | -0.002 (0.102) | -0.045 (0.110) |
| 36–59m × EQ | -0.040 (0.109) | -0.049 (0.106) | -0.050 (0.106) | -0.093 (0.112) |
| Contraste 36–59 − 24–35 | -0.032 (0.072) | -0.045 (0.071) | -0.048 (0.071) | -0.048 (0.071) |
| n | 7,169 | 7,169 | 7,169 | 4,901 |
| Comunas (cluster) | 116 | 116 | 116 | 67 |

## Por qué esta regresión NO está en Gillmore
1. Ningún outcome suyo es autorreportado por el niño/adolescente; PHQ-4/GAD-2 solo existen en la ola 2024, que él no usa.
2. Su horizonte máximo es 2017 (edad 11). Aquí: 14 años post-sismo, adolescencia.
3. La dosis edad-a-la-exposición es su Fig. B.1 (heterogeneidad), nunca su diseño principal; aquí es la única fuente de identificación posible y se defiende como tal.
4. El panel intra-niño (B) exige observar dos veces al mismo niño: su diseño de cortes repetidos no lo permite.
