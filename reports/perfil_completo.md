# El perfil completo por edad al terremoto (scripts/47_perfil_completo.py)
PHQ-4 (DE), zona afectada menos no afectada; EF de comuna, año de nacimiento y tramo; controles; pesos ELPI; EE por comuna salvo donde se indica.

## Celdas: adolescentes por sexo, tramo y zona (no afectada / afectada) y comunas
- chicas: 6-11: 167 / 519 | 12-17: 173 / 550 | 18-23: 159 / 507 | 24-29: 161 / 527 | 30-35: 155 / 515 | 36-41: 157 / 526 | 42-49: 189 / 656
- chicos: 6-11: 177 / 555 | 12-17: 172 / 541 | 18-23: 142 / 552 | 24-29: 167 / 524 | 30-35: 150 / 479 | 36-41: 174 / 561 | 42-49: 203 / 638
- comunas de selección: afectada 93, no afectada 23; regiones: afectada 6, no afectada 9

## 1. Tramos de seis meses, centrados (suman cero)
- chicas: 6-11 +0.161* (ee 0.083, p=0.051) | 12-17 +0.143* (ee 0.079, p=0.072) | 18-23 -0.090 (ee 0.088, p=0.303) | 24-29 -0.131* (ee 0.073, p=0.074) | 30-35 -0.151* (ee 0.086, p=0.080) | 36-41 -0.044 (ee 0.073, p=0.542) | 42-49 +0.113 (ee 0.074, p=0.127) | N=4,961
  perfil plano, prueba conjunta: p=0.029; 6-11 menos 12-17: +0.019 (ee 0.121, p=0.877)
  6-11 frente a 12-23: +0.129 (ee 0.124, p=0.299)
- chicos: 6-11 -0.014 (ee 0.071, p=0.845) | 12-17 +0.015 (ee 0.073, p=0.838) | 18-23 +0.032 (ee 0.084, p=0.707) | 24-29 -0.014 (ee 0.071, p=0.848) | 30-35 -0.049 (ee 0.086, p=0.566) | 36-41 +0.070 (ee 0.065, p=0.281) | 42-49 -0.040 (ee 0.092, p=0.664) | N=5,035
  perfil plano, prueba conjunta: p=0.905; 6-11 menos 12-17: -0.029 (ee 0.112, p=0.797)
  6-11 frente a 12-23: -0.036 (ee 0.099, p=0.717)

## 2. 6-11 meses frente al resto, sin el tramo de 2-3 años
- chicas: +0.120 (ee 0.106, p=0.257); N=3,603
- chicos: -0.034 (ee 0.085, p=0.684); N=3,715

## 5. Chicas menos chicos (modelo interactuado)
- chicos -0.016 (ee 0.083, p=0.845); chicas menos chicos +0.197 (ee 0.139, p=0.158)

## 7. Controles (chicas)
- solo efectos fijos: +0.175* (ee 0.096, p=0.070); N=4,961
- con los de 2010, sin los de 2012: +0.178* (ee 0.097, p=0.066); N=4,961
- con los de 2010 y 2012 (principal): +0.180* (ee 0.097, p=0.062); N=4,961
- chicas con registro de nacimiento, sin controles al nacer: +0.138 (ee 0.093, p=0.137); N=4,190

## 4. Inferencia con la zona asignada por región, y dosis
- chicas: coeficiente +0.179; aleatorización por región, p bilateral=0.084, unilateral=0.026 (5,005 asignaciones); EE por región (15): +0.178* (ee 0.099, p=0.072)
- chicos: coeficiente -0.014; aleatorización por región, p bilateral=0.870, unilateral=0.551 (5,005 asignaciones); EE por región (15): -0.017 (ee 0.077, p=0.826)
- chicas, terciles de PGA en la zona afectada (cortes 28 y 33 %g), cada uno frente a la zona no afectada: T1 +0.156 (ee 0.124, p=0.210) | T2 +0.114 (ee 0.116, p=0.326) | T3 +0.264** (ee 0.120, p=0.027)
- chicos, terciles de PGA en la zona afectada (cortes 28 y 33 %g), cada uno frente a la zona no afectada: T1 -0.045 (ee 0.089, p=0.611) | T2 -0.008 (ee 0.110, p=0.939) | T3 +0.007 (ee 0.112, p=0.954)
- sin Biobío y Maule, chicas: +0.180* (ee 0.101, p=0.073); N=3,975
- sin Biobío y Maule, chicos: -0.001 (ee 0.088, p=0.991); N=4,098
- sin Santiago, chicas: +0.198* (ee 0.105, p=0.059); N=3,203
- sin Santiago, chicos: -0.071 (ee 0.083, p=0.395); N=3,227
