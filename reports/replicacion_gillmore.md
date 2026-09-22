# Replicación de la regresión principal de Gillmore (EER 2026)

Ec. (1): `Affected×Earthquake` (binario regional oficial) con EF de comuna (de selección), cohorte y ola; WLS con pesos transversales; EE cluster por comuna. Columnas como en las Tablas 2–3 del paper: (1) EF comuna + dummy Affected; (2) + EF cohorte y ola; (3) + controles X (con indicadores de missing, que es lo que mantiene el n constante entre columnas, como en el paper).

Configuración calibrada: geo=idcomuna, pesos=eva, corte de concepción=dic-2010, X=dummy.

| Horizonte | Outcome | col | β nuestro | (EE) | n | clusters | β paper | (EE paper) | n paper |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| ST | Battelle | 1 | -0.109 | (0.089) | 12,526 | 199 | -0.098 | (0.094) | 13,070 |
| ST | Battelle | 2 | -0.109 | (0.089) | 12,526 | 199 | -0.108 | (0.093) | 13,070 |
| ST | Battelle | 3 | -0.090 | (0.091) | 12,526 | 199 | -0.081 | (0.094) | 13,070 |
| ST | Peabody/TVIP | 1 | -0.116 | (0.106) | 12,061 | 197 | -0.148 | (0.092) | 14,205 |
| ST | Peabody/TVIP | 2 | -0.117 | (0.107) | 12,061 | 197 | -0.158 | (0.089) | 14,205 |
| ST | Peabody/TVIP | 3 | -0.113 | (0.106) | 12,061 | 197 | -0.141 | (0.086) | 14,205 |
| ST | CBCL1 | 1 | 0.149 | (0.111) | 11,044 | 195 | 0.098 | (0.104) | 11,654 |
| ST | CBCL1 | 2 | 0.148 | (0.111) | 11,044 | 195 | 0.094 | (0.103) | 11,654 |
| ST | CBCL1 | 3 | 0.183* | (0.109) | 11,044 | 195 | 0.126 | (0.100) | 11,654 |
| MT | Peabody/TVIP | 1 | -0.157** | (0.074) | 14,183 | 205 | -0.180 | (0.075) | 14,069 |
| MT | Peabody/TVIP | 2 | -0.158** | (0.074) | 14,183 | 205 | -0.190 | (0.073) | 14,069 |
| MT | Peabody/TVIP | 3 | -0.160** | (0.072) | 14,183 | 205 | -0.174 | (0.069) | 14,069 |
| MT | CBCL2 | 1 | -0.091 | (0.080) | 11,628 | 199 | -0.123 | (0.076) | 11,568 |
| MT | CBCL2 | 2 | -0.092 | (0.080) | 11,628 | 199 | -0.126 | (0.076) | 11,568 |
| MT | CBCL2 | 3 | -0.103 | (0.082) | 11,628 | 199 | -0.129 | (0.076) | 11,568 |

## Desviaciones respecto al original (datos públicos)
- **D1 comuna**: 2010/2012 públicos no traen comuna → `estrato` (comuna de selección) de 2017 heredado vía folio; filas 2012 sin enlace usan una celda regional de reserva (conservan el n).
- **D2 fecha de nacimiento**: 2024 (exacta) → 2017 (`fechanacimientons`, exacta) → 2017 (finicio−edad) → edad 2012 + jul-2012.
- **D3 educación de la madre 2012**: b2n de la línea base 2010; 2017 usa e4/m10 (niveles).
- **D4 salud mental previa**: checklist b55o–t (2012) vía folio; cohortes 2013–15 sin checklist → indicador de missing.
- **D5 orden de nacimiento**: proxy nº de hijos de la madre (2012: b71; 2017: c56 → m8+1 → hermanos en roster +1). Tamaño del hogar 2017: numper; padre presente y edad de la madre 2017: roster h1/h3.
- z-scores dentro de (ola × tramo de 12 meses); CBCL invertido; puntaje base: T (2012) y estándar/T internacional (2017).
