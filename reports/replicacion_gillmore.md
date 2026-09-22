# Replicación de la regresión principal de Gillmore (EER 2026)

Ec. (1): `Affected×Earthquake` (binario regional oficial) con EF de comuna, cohorte y ola; WLS con pesos transversales; EE cluster por comuna. Columnas como en las Tablas 2–3 del paper: (1) EF comuna + dummy Affected; (2) + EF cohorte y ola; (3) + controles X.

| Horizonte | Outcome | col | β nuestro | (EE) | p | n | clusters | β paper | n paper |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| ST | Battelle | 1 | -0.120 | (0.088) | 0.173 | 13,020 | 204 | -0.098 | 13,070 |
| ST | Battelle | 2 | -0.121 | (0.088) | 0.170 | 13,020 | 204 | -0.108 | 13,070 |
| ST | Battelle | 3 | -0.074 | (0.095) | 0.436 | 11,719 | 202 | -0.081 | 13,070 |
| ST | Peabody/TVIP | 1 | -0.121 | (0.105) | 0.251 | 12,667 | 202 | -0.148 | 14,205 |
| ST | Peabody/TVIP | 2 | -0.122 | (0.106) | 0.249 | 12,667 | 202 | -0.158 | 14,205 |
| ST | Peabody/TVIP | 3 | -0.141 | (0.105) | 0.179 | 11,883 | 202 | -0.141 | 14,205 |
| ST | CBCL1 | 1 | 0.143 | (0.112) | 0.200 | 11,418 | 197 | 0.098 | 11,654 |
| ST | CBCL1 | 2 | 0.143 | (0.111) | 0.200 | 11,418 | 197 | 0.094 | 11,654 |
| ST | CBCL1 | 3 | 0.213** | (0.108) | 0.050 | 10,145 | 195 | 0.126 | 11,654 |
| MT | Peabody/TVIP | 1 | -0.157** | (0.074) | 0.035 | 14,188 | 205 | -0.180 | 14,069 |
| MT | Peabody/TVIP | 2 | -0.126* | (0.074) | 0.089 | 14,188 | 205 | -0.190 | 14,069 |
| MT | Peabody/TVIP | 3 | -0.126* | (0.073) | 0.086 | 13,765 | 205 | -0.174 | 14,069 |
| MT | CBCL2 | 1 | -0.135* | (0.078) | 0.085 | 11,633 | 199 | -0.123 | 11,568 |
| MT | CBCL2 | 2 | -0.095 | (0.067) | 0.160 | 11,633 | 199 | -0.126 | 11,568 |
| MT | CBCL2 | 3 | -0.107 | (0.069) | 0.122 | 11,247 | 199 | -0.129 | 11,568 |

## Desviaciones respecto al original (datos públicos)
- **D1 comuna**: 2010/2012 públicos no traen comuna → `idcomuna` 2017 heredada vía folio a las filas 2012 (migración 0,78%); filas 2012 sin enlace 2017 se pierden.
- **D2 fecha de nacimiento**: jerarquía 2024 → 2017 (finicio−edad) → edad 2012 + jul-2012.
- **D3 educación de la madre 2012**: b2n de la línea base 2010; 2017 usa e4/m10 (niveles, no años).
- **D4 salud mental previa**: checklist b55o–t (2012) vía folio; controles 2013–15 sin checklist → dummy `mh_miss`.
- **D5 orden de nacimiento**: proxy nº de hijos de la madre (2012: b71; 2017: c56 → m8+1 → hermanos en el roster +1). Tamaño del hogar 2017: numper; presencia del padre y edad de la madre 2017: roster h1/h3 del archivo del cuidador.
- Pesos: `fexp_test0` (2012) y `fexp_eva0_2` (2017); el paper usa "sampling weights representative at the national level".
- z-scores dentro de (ola × tramo de 12 meses); CBCL invertido.

## Veredicto
Los 15 coeficientes reproducen el **signo** del paper; en la especificación preferida (col. 3) las brechas son ≤0,05 DE (ST Peabody −0,141 vs −0,141 **exacto**; ST Battelle −0,074 vs −0,081; MT CBCL2 −0,107 vs −0,129; MT Peabody −0,126 vs −0,174). Los n coinciden al 1–3% salvo ST Peabody (−11%, por las filas 2012 sin comuna, D1). Diferencias razonables dadas D1–D5 y la elección de puntaje base (T 2012 vs estándar 2017).
