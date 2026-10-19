# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)
Cobertura de los índices: ingreso 0.90; sin_empleo 0.99; dano 0.89; conflicto 0.95; hacinamiento 1.00; precaria 1.00

## 1. ¿Cambió el hogar distinto según la edad?
Zona afectada menos no afectada, frente a 2 años (DE del índice; más alto = peor).
- chicas, ingreso: 6-11 +0.054 (ee 0.084, p=0.524) | 12-23 +0.024 (ee 0.081, p=0.770) | 36-49 +0.021 (ee 0.086, p=0.805) | N=4479
- chicas, ingreso, sin controles: 6-11 +0.089 (ee 0.088, p=0.312) | 12-23 +0.066 (ee 0.091, p=0.469) | 36-49 +0.060 (ee 0.089, p=0.498) | N=4479
- chicas, sin_empleo: 6-11 -0.167 (ee 0.103, p=0.105) | 12-23 -0.116 (ee 0.092, p=0.209) | 36-49 -0.011 (ee 0.075, p=0.880) | N=4926
- chicas, sin_empleo, sin controles: 6-11 -0.127 (ee 0.104, p=0.223) | 12-23 -0.081 (ee 0.098, p=0.411) | 36-49 +0.012 (ee 0.076, p=0.878) | N=4926
- chicas, dano: 6-11 +0.042 (ee 0.069, p=0.539) | 12-23 +0.013 (ee 0.051, p=0.800) | 36-49 +0.063 (ee 0.054, p=0.244) | N=4424
- chicas, dano, sin controles: 6-11 +0.044 (ee 0.068, p=0.523) | 12-23 +0.024 (ee 0.050, p=0.632) | 36-49 +0.064 (ee 0.056, p=0.254) | N=4424
- chicas, conflicto: 6-11 -0.144 (ee 0.096, p=0.134) | 12-23 -0.154* (ee 0.084, p=0.066) | 36-49 +0.002 (ee 0.062, p=0.975) | N=4702
- chicas, conflicto, sin controles: 6-11 -0.138 (ee 0.095, p=0.145) | 12-23 -0.148* (ee 0.082, p=0.073) | 36-49 +0.009 (ee 0.061, p=0.885) | N=4702
- chicas, hacinamiento: 6-11 +0.112 (ee 0.099, p=0.256) | 12-23 +0.121 (ee 0.100, p=0.222) | 36-49 +0.188** (ee 0.087, p=0.031) | N=4962
- chicas, hacinamiento, sin controles: 6-11 +0.146 (ee 0.101, p=0.149) | 12-23 +0.160 (ee 0.099, p=0.106) | 36-49 +0.245*** (ee 0.088, p=0.006) | N=4962
- chicas, precaria: 6-11 +0.092 (ee 0.095, p=0.336) | 12-23 +0.049 (ee 0.083, p=0.558) | 36-49 +0.108 (ee 0.081, p=0.182) | N=4961
- chicas, precaria, sin controles: 6-11 +0.125 (ee 0.098, p=0.201) | 12-23 +0.081 (ee 0.085, p=0.339) | 36-49 +0.122 (ee 0.081, p=0.130) | N=4961
- todos, ingreso: 6-11 +0.003 (ee 0.056, p=0.955) | 12-23 -0.062 (ee 0.077, p=0.420) | 36-49 -0.064 (ee 0.065, p=0.324) | N=9003
- todos, ingreso, sin controles: 6-11 +0.024 (ee 0.062, p=0.703) | 12-23 -0.048 (ee 0.082, p=0.557) | 36-49 -0.056 (ee 0.067, p=0.408) | N=9003
- todos, sin_empleo: 6-11 -0.121* (ee 0.067, p=0.070) | 12-23 -0.137** (ee 0.063, p=0.029) | 36-49 -0.097* (ee 0.052, p=0.062) | N=9915
- todos, sin_empleo, sin controles: 6-11 -0.101 (ee 0.073, p=0.169) | 12-23 -0.128* (ee 0.069, p=0.061) | 36-49 -0.095* (ee 0.055, p=0.084) | N=9915
- todos, dano: 6-11 +0.020 (ee 0.047, p=0.675) | 12-23 +0.037 (ee 0.033, p=0.260) | 36-49 +0.024 (ee 0.035, p=0.486) | N=8908
- todos, dano, sin controles: 6-11 +0.019 (ee 0.048, p=0.688) | 12-23 +0.042 (ee 0.033, p=0.203) | 36-49 +0.025 (ee 0.035, p=0.465) | N=8908
- todos, conflicto: 6-11 -0.074 (ee 0.086, p=0.391) | 12-23 -0.073 (ee 0.062, p=0.237) | 36-49 +0.037 (ee 0.053, p=0.486) | N=9489
- todos, conflicto, sin controles: 6-11 -0.068 (ee 0.087, p=0.434) | 12-23 -0.069 (ee 0.060, p=0.252) | 36-49 +0.040 (ee 0.052, p=0.440) | N=9489
- todos, hacinamiento: 6-11 +0.056 (ee 0.055, p=0.307) | 12-23 -0.014 (ee 0.077, p=0.860) | 36-49 +0.025 (ee 0.062, p=0.695) | N=10003
- todos, hacinamiento, sin controles: 6-11 +0.065 (ee 0.062, p=0.298) | 12-23 -0.010 (ee 0.082, p=0.902) | 36-49 +0.039 (ee 0.071, p=0.585) | N=10003
- todos, precaria: 6-11 -0.025 (ee 0.056, p=0.656) | 12-23 -0.015 (ee 0.063, p=0.812) | 36-49 +0.034 (ee 0.068, p=0.615) | N=10001
- todos, precaria, sin controles: 6-11 -0.013 (ee 0.056, p=0.819) | 12-23 -0.011 (ee 0.066, p=0.865) | 36-49 +0.036 (ee 0.070, p=0.607) | N=10001

## 2. Qué parte de la brecha explica el hogar (Gelbach, bootstrap de comunas, 300 réplicas)

chicas (N=4961)
- 6-11: brecha +0.300 [+0.100, +0.525]; con el hogar +0.300; explicado +0.001 [-0.012, +0.015], 0%
    ingreso: +0.001 [-0.006, +0.010]
    sin_empleo: +0.006 [-0.000, +0.017]
    dano: -0.001 [-0.006, +0.002]
    conflicto: -0.003 [-0.012, +0.003]
    hacinamiento: -0.002 [-0.011, +0.003]
    precaria: +0.000 [-0.007, +0.005]
- 12-23: brecha +0.171 [-0.034, +0.386]; con el hogar +0.170; explicado +0.002 [-0.010, +0.017], 1%
    ingreso: +0.001 [-0.005, +0.006]
    sin_empleo: +0.005 [-0.002, +0.019]
    dano: -0.000 [-0.003, +0.002]
    conflicto: -0.002 [-0.009, +0.004]
    hacinamiento: -0.002 [-0.011, +0.004]
    precaria: +0.000 [-0.003, +0.004]
- 36-49: brecha +0.182 [-0.011, +0.349]; con el hogar +0.186; explicado -0.005 [-0.015, +0.009], -3%
    ingreso: -0.000 [-0.006, +0.008]
    sin_empleo: +0.000 [-0.005, +0.011]
    dano: -0.001 [-0.006, +0.001]
    conflicto: +0.000 [-0.005, +0.005]
    hacinamiento: -0.004 [-0.014, +0.005]
    precaria: -0.000 [-0.006, +0.004]

todos (N=9996)
- 6-11: brecha +0.147 [+0.007, +0.267]; con el hogar +0.145; explicado +0.002 [-0.005, +0.009], 1%
    ingreso: +0.000 [-0.002, +0.003]
    sin_empleo: +0.003 [-0.000, +0.008]
    dano: -0.000 [-0.003, +0.002]
    conflicto: +0.000 [-0.004, +0.003]
    hacinamiento: -0.001 [-0.003, +0.001]
    precaria: -0.000 [-0.002, +0.002]
- 12-23: brecha +0.102 [-0.051, +0.239]; con el hogar +0.099; explicado +0.003 [-0.003, +0.009], 3%
    ingreso: -0.001 [-0.004, +0.002]
    sin_empleo: +0.003 [-0.000, +0.008]
    dano: +0.000 [-0.001, +0.002]
    conflicto: -0.000 [-0.004, +0.003]
    hacinamiento: +0.000 [-0.002, +0.004]
    precaria: -0.000 [-0.002, +0.002]
- 36-49: brecha +0.103 [-0.039, +0.201]; con el hogar +0.101; explicado +0.001 [-0.003, +0.008], 1%
    ingreso: -0.001 [-0.004, +0.002]
    sin_empleo: +0.002 [-0.000, +0.006]
    dano: +0.000 [-0.001, +0.002]
    conflicto: -0.000 [-0.002, +0.002]
    hacinamiento: -0.000 [-0.003, +0.002]
    precaria: +0.000 [-0.001, +0.003]
