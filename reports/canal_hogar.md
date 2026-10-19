# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)
Cobertura de los índices: conflicto 0.95; recursos 0.98; hacinamiento 1.00; precaria 1.00

## 1. ¿Cambió el hogar distinto según la edad?
Zona afectada menos no afectada, frente a 2 años (DE del índice; más alto = peor).
- chicas, conflicto: 6-11 -0.144 (ee 0.096, p=0.134) | 12-23 -0.154* (ee 0.084, p=0.066) | 36-49 +0.002 (ee 0.062, p=0.975) | N=4702
- chicas, conflicto, sin controles: 6-11 -0.138 (ee 0.095, p=0.145) | 12-23 -0.148* (ee 0.082, p=0.073) | 36-49 +0.009 (ee 0.061, p=0.885) | N=4702
- chicas, recursos: 6-11 +0.041 (ee 0.081, p=0.617) | 12-23 +0.012 (ee 0.065, p=0.858) | 36-49 +0.065 (ee 0.069, p=0.346) | N=4885
- chicas, recursos, sin controles: 6-11 +0.060 (ee 0.079, p=0.445) | 12-23 +0.043 (ee 0.071, p=0.547) | 36-49 +0.080 (ee 0.074, p=0.279) | N=4885
- chicas, hacinamiento: 6-11 +0.112 (ee 0.099, p=0.256) | 12-23 +0.121 (ee 0.100, p=0.222) | 36-49 +0.188** (ee 0.087, p=0.031) | N=4962
- chicas, hacinamiento, sin controles: 6-11 +0.146 (ee 0.101, p=0.149) | 12-23 +0.160 (ee 0.099, p=0.106) | 36-49 +0.245*** (ee 0.088, p=0.006) | N=4962
- chicas, precaria: 6-11 +0.092 (ee 0.095, p=0.336) | 12-23 +0.049 (ee 0.083, p=0.558) | 36-49 +0.108 (ee 0.081, p=0.182) | N=4961
- chicas, precaria, sin controles: 6-11 +0.125 (ee 0.098, p=0.201) | 12-23 +0.081 (ee 0.085, p=0.339) | 36-49 +0.122 (ee 0.081, p=0.130) | N=4961
- todos, conflicto: 6-11 -0.074 (ee 0.086, p=0.391) | 12-23 -0.073 (ee 0.062, p=0.237) | 36-49 +0.037 (ee 0.053, p=0.486) | N=9489
- todos, conflicto, sin controles: 6-11 -0.068 (ee 0.087, p=0.434) | 12-23 -0.069 (ee 0.060, p=0.252) | 36-49 +0.040 (ee 0.052, p=0.440) | N=9489
- todos, recursos: 6-11 +0.024 (ee 0.050, p=0.625) | 12-23 -0.017 (ee 0.055, p=0.756) | 36-49 -0.029 (ee 0.048, p=0.554) | N=9844
- todos, recursos, sin controles: 6-11 +0.035 (ee 0.052, p=0.506) | 12-23 -0.007 (ee 0.058, p=0.900) | 36-49 -0.027 (ee 0.051, p=0.596) | N=9844
- todos, hacinamiento: 6-11 +0.056 (ee 0.055, p=0.307) | 12-23 -0.014 (ee 0.077, p=0.860) | 36-49 +0.025 (ee 0.062, p=0.695) | N=10003
- todos, hacinamiento, sin controles: 6-11 +0.065 (ee 0.062, p=0.298) | 12-23 -0.010 (ee 0.082, p=0.902) | 36-49 +0.039 (ee 0.071, p=0.585) | N=10003
- todos, precaria: 6-11 -0.025 (ee 0.056, p=0.656) | 12-23 -0.015 (ee 0.063, p=0.812) | 36-49 +0.034 (ee 0.068, p=0.615) | N=10001
- todos, precaria, sin controles: 6-11 -0.013 (ee 0.056, p=0.819) | 12-23 -0.011 (ee 0.066, p=0.865) | 36-49 +0.036 (ee 0.070, p=0.607) | N=10001

## 2. Qué parte de la brecha explica el hogar (Gelbach, bootstrap de comunas, 300 réplicas)

chicas (N=4961)
- 6-11: brecha +0.300 [+0.100, +0.525]; con el hogar +0.305; explicado -0.005 [-0.017, +0.004], -2%
    conflicto: -0.003 [-0.012, +0.003]
    recursos: -0.001 [-0.007, +0.004]
    hacinamiento: -0.002 [-0.011, +0.003]
    precaria: +0.000 [-0.007, +0.005]
- 12-23: brecha +0.171 [-0.034, +0.386]; con el hogar +0.176; explicado -0.004 [-0.014, +0.005], -2%
    conflicto: -0.002 [-0.009, +0.004]
    recursos: -0.000 [-0.005, +0.003]
    hacinamiento: -0.002 [-0.010, +0.004]
    precaria: +0.000 [-0.003, +0.004]
- 36-49: brecha +0.182 [-0.011, +0.349]; con el hogar +0.186; explicado -0.004 [-0.015, +0.006], -2%
    conflicto: +0.000 [-0.005, +0.005]
    recursos: -0.001 [-0.004, +0.003]
    hacinamiento: -0.003 [-0.013, +0.005]
    precaria: -0.000 [-0.006, +0.004]

todos (N=9996)
- 6-11: brecha +0.147 [+0.007, +0.267]; con el hogar +0.148; explicado -0.001 [-0.005, +0.005], -0%
    conflicto: +0.000 [-0.004, +0.003]
    recursos: +0.000 [-0.002, +0.002]
    hacinamiento: -0.001 [-0.003, +0.001]
    precaria: -0.000 [-0.002, +0.002]
- 12-23: brecha +0.102 [-0.051, +0.239]; con el hogar +0.102; explicado +0.000 [-0.004, +0.006], 0%
    conflicto: -0.000 [-0.004, +0.003]
    recursos: +0.000 [-0.002, +0.003]
    hacinamiento: +0.000 [-0.002, +0.004]
    precaria: -0.000 [-0.002, +0.002]
- 36-49: brecha +0.103 [-0.039, +0.201]; con el hogar +0.103; explicado -0.000 [-0.003, +0.004], -0%
    conflicto: -0.000 [-0.002, +0.002]
    recursos: -0.000 [-0.002, +0.002]
    hacinamiento: -0.000 [-0.003, +0.002]
    precaria: +0.000 [-0.001, +0.003]
