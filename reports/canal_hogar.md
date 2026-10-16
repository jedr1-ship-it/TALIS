# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)
Cobertura de los índices: estres_padres 0.95; conflicto 0.96; recursos 0.85

## 1. ¿Cambió el hogar distinto según la edad?
Zona afectada menos no afectada, frente a 18-35 meses (DE del índice; más alto = peor).
- chicas, estres_padres: 6-17 -0.011 (ee 0.081, p=0.888) | 36-41 +0.062 (ee 0.086, p=0.470) | 42-49 +0.020 (ee 0.083, p=0.808) | N=4722
- chicas, estres_padres, sin controles: 6-17 +0.014 (ee 0.080, p=0.864) | 36-41 +0.064 (ee 0.086, p=0.460) | 42-49 +0.016 (ee 0.083, p=0.849) | N=4722
- chicas, conflicto: 6-17 -0.101 (ee 0.078, p=0.196) | 36-41 -0.109 (ee 0.106, p=0.305) | 42-49 +0.027 (ee 0.074, p=0.714) | N=4753
- chicas, conflicto, sin controles: 6-17 -0.106 (ee 0.079, p=0.176) | 36-41 -0.128 (ee 0.105, p=0.223) | 42-49 +0.025 (ee 0.076, p=0.744) | N=4753
- chicas, recursos: 6-17 -0.036 (ee 0.066, p=0.586) | 36-41 -0.034 (ee 0.078, p=0.661) | 42-49 +0.070 (ee 0.072, p=0.329) | N=4234
- chicas, recursos, sin controles: 6-17 -0.012 (ee 0.071, p=0.867) | 36-41 -0.004 (ee 0.089, p=0.960) | 42-49 +0.103 (ee 0.080, p=0.201) | N=4234
- todos, estres_padres: 6-17 +0.029 (ee 0.046, p=0.529) | 36-41 +0.095* (ee 0.056, p=0.094) | 42-49 +0.047 (ee 0.057, p=0.409) | N=9513
- todos, estres_padres, sin controles: 6-17 +0.053 (ee 0.048, p=0.269) | 36-41 +0.084 (ee 0.061, p=0.168) | 42-49 +0.052 (ee 0.054, p=0.328) | N=9513
- todos, conflicto: 6-17 -0.041 (ee 0.044, p=0.361) | 36-41 -0.093 (ee 0.057, p=0.104) | 42-49 -0.014 (ee 0.059, p=0.816) | N=9564
- todos, conflicto, sin controles: 6-17 -0.035 (ee 0.043, p=0.421) | 36-41 -0.098* (ee 0.057, p=0.088) | 42-49 -0.018 (ee 0.060, p=0.761) | N=9564
- todos, recursos: 6-17 -0.024 (ee 0.042, p=0.567) | 36-41 +0.023 (ee 0.056, p=0.683) | 42-49 +0.013 (ee 0.048, p=0.792) | N=8514
- todos, recursos, sin controles: 6-17 -0.021 (ee 0.047, p=0.655) | 36-41 +0.037 (ee 0.065, p=0.570) | 42-49 +0.024 (ee 0.054, p=0.653) | N=8514

## 2. Qué parte de la brecha explica el hogar (Gelbach, bootstrap de comunas, 300 réplicas)

chicas (N=4230)
- 6-17: brecha +0.328 [+0.158, +0.525]; con el hogar +0.340; explicado -0.012 [-0.029, +0.005], -4%
    estres_padres: -0.005 [-0.017, +0.010]
    conflicto: -0.008 [-0.018, -0.001]
    recursos: +0.001 [-0.003, +0.005]
- 36-41: brecha +0.172 [-0.025, +0.364]; con el hogar +0.172; explicado +0.000 [-0.020, +0.022], 0%
    estres_padres: +0.004 [-0.009, +0.020]
    conflicto: -0.005 [-0.018, +0.006]
    recursos: +0.001 [-0.003, +0.006]
- 42-49: brecha +0.212 [-0.021, +0.454]; con el hogar +0.212; explicado +0.001 [-0.022, +0.021], 0%
    estres_padres: +0.002 [-0.015, +0.019]
    conflicto: -0.001 [-0.009, +0.007]
    recursos: -0.001 [-0.007, +0.002]

todos (N=8504)
- 6-17: brecha +0.150 [+0.028, +0.256]; con el hogar +0.152; explicado -0.001 [-0.009, +0.006], -1%
    estres_padres: +0.000 [-0.007, +0.006]
    conflicto: -0.002 [-0.006, +0.001]
    recursos: +0.000 [-0.001, +0.002]
- 36-41: brecha +0.093 [-0.056, +0.214]; con el hogar +0.092; explicado +0.001 [-0.012, +0.012], 2%
    estres_padres: +0.005 [-0.004, +0.014]
    conflicto: -0.003 [-0.009, +0.000]
    recursos: -0.000 [-0.003, +0.002]
- 42-49: brecha +0.075 [-0.088, +0.224]; con el hogar +0.070; explicado +0.006 [-0.005, +0.015], 7%
    estres_padres: +0.006 [-0.004, +0.016]
    conflicto: -0.000 [-0.004, +0.003]
    recursos: -0.000 [-0.002, +0.002]
