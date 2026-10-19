# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)
Cobertura de los índices: ingreso 0.90; sin_empleo 0.99; dano 0.89; conflicto 0.95; hacinamiento 1.00; precaria 1.00

## 1. ¿Cambió el hogar distinto según la edad?
Zona afectada menos no afectada, frente a 2 años (DE del índice; más alto = peor).
- chicas, ingreso: 6-11 +0.056 (ee 0.084, p=0.504) | 12-23 +0.024 (ee 0.081, p=0.772) | 36-49 +0.021 (ee 0.086, p=0.807) | N=4478
- chicas, ingreso, sin controles: 6-11 +0.090 (ee 0.088, p=0.307) | 12-23 +0.066 (ee 0.091, p=0.469) | 36-49 +0.060 (ee 0.089, p=0.498) | N=4478
- chicas, sin_empleo: 6-11 -0.167 (ee 0.103, p=0.106) | 12-23 -0.116 (ee 0.092, p=0.209) | 36-49 -0.011 (ee 0.075, p=0.880) | N=4925
- chicas, sin_empleo, sin controles: 6-11 -0.127 (ee 0.104, p=0.221) | 12-23 -0.081 (ee 0.098, p=0.411) | 36-49 +0.012 (ee 0.076, p=0.878) | N=4925
- chicas, dano: 6-11 +0.044 (ee 0.069, p=0.524) | 12-23 +0.013 (ee 0.051, p=0.802) | 36-49 +0.063 (ee 0.054, p=0.245) | N=4423
- chicas, dano, sin controles: 6-11 +0.045 (ee 0.069, p=0.514) | 12-23 +0.024 (ee 0.050, p=0.633) | 36-49 +0.064 (ee 0.056, p=0.254) | N=4423
- chicas, conflicto: 6-11 -0.143 (ee 0.096, p=0.135) | 12-23 -0.154* (ee 0.084, p=0.066) | 36-49 +0.002 (ee 0.062, p=0.976) | N=4701
- chicas, conflicto, sin controles: 6-11 -0.138 (ee 0.095, p=0.146) | 12-23 -0.148* (ee 0.082, p=0.073) | 36-49 +0.009 (ee 0.061, p=0.885) | N=4701
- chicas, hacinamiento: 6-11 +0.114 (ee 0.099, p=0.248) | 12-23 +0.121 (ee 0.100, p=0.223) | 36-49 +0.188** (ee 0.087, p=0.031) | N=4961
- chicas, hacinamiento, sin controles: 6-11 +0.146 (ee 0.101, p=0.150) | 12-23 +0.160 (ee 0.099, p=0.106) | 36-49 +0.245*** (ee 0.088, p=0.006) | N=4961
- chicas, precaria: 6-11 +0.094 (ee 0.095, p=0.327) | 12-23 +0.048 (ee 0.083, p=0.559) | 36-49 +0.108 (ee 0.081, p=0.183) | N=4960
- chicas, precaria, sin controles: 6-11 +0.126 (ee 0.098, p=0.197) | 12-23 +0.081 (ee 0.085, p=0.339) | 36-49 +0.122 (ee 0.081, p=0.130) | N=4960
- todos, ingreso: 6-11 +0.004 (ee 0.057, p=0.937) | 12-23 -0.060 (ee 0.078, p=0.442) | 36-49 -0.064 (ee 0.065, p=0.323) | N=8997
- todos, ingreso, sin controles: 6-11 +0.024 (ee 0.062, p=0.698) | 12-23 -0.046 (ee 0.082, p=0.577) | 36-49 -0.055 (ee 0.067, p=0.412) | N=8997
- todos, sin_empleo: 6-11 -0.121* (ee 0.067, p=0.070) | 12-23 -0.136** (ee 0.063, p=0.031) | 36-49 -0.099* (ee 0.052, p=0.057) | N=9908
- todos, sin_empleo, sin controles: 6-11 -0.101 (ee 0.073, p=0.167) | 12-23 -0.127* (ee 0.069, p=0.065) | 36-49 -0.097* (ee 0.055, p=0.075) | N=9908
- todos, dano: 6-11 +0.021 (ee 0.047, p=0.664) | 12-23 +0.036 (ee 0.033, p=0.274) | 36-49 +0.024 (ee 0.035, p=0.487) | N=8902
- todos, dano, sin controles: 6-11 +0.020 (ee 0.048, p=0.683) | 12-23 +0.041 (ee 0.033, p=0.214) | 36-49 +0.026 (ee 0.035, p=0.463) | N=8902
- todos, conflicto: 6-11 -0.074 (ee 0.086, p=0.393) | 12-23 -0.075 (ee 0.061, p=0.224) | 36-49 +0.037 (ee 0.052, p=0.485) | N=9483
- todos, conflicto, sin controles: 6-11 -0.068 (ee 0.087, p=0.436) | 12-23 -0.071 (ee 0.060, p=0.238) | 36-49 +0.041 (ee 0.052, p=0.439) | N=9483
- todos, hacinamiento: 6-11 +0.057 (ee 0.055, p=0.297) | 12-23 -0.014 (ee 0.077, p=0.857) | 36-49 +0.026 (ee 0.063, p=0.677) | N=9996
- todos, hacinamiento, sin controles: 6-11 +0.065 (ee 0.062, p=0.297) | 12-23 -0.010 (ee 0.082, p=0.900) | 36-49 +0.041 (ee 0.071, p=0.569) | N=9996
- todos, precaria: 6-11 -0.024 (ee 0.056, p=0.666) | 12-23 -0.016 (ee 0.063, p=0.795) | 36-49 +0.034 (ee 0.068, p=0.622) | N=9994
- todos, precaria, sin controles: 6-11 -0.012 (ee 0.056, p=0.825) | 12-23 -0.013 (ee 0.066, p=0.847) | 36-49 +0.035 (ee 0.071, p=0.616) | N=9994

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
