# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)
Cobertura de los índices: conflicto 0.96; recursos 0.85; padre_fuera 0.96; sin_empleo 0.94; hacinamiento 0.96

## 1. ¿Cambió el hogar distinto según la edad?
Zona afectada menos no afectada, frente a 2 años (DE del índice; más alto = peor).
- chicas, conflicto: 6-11 -0.188* (ee 0.107, p=0.080) | 12-23 -0.100 (ee 0.074, p=0.175) | 36-49 -0.075 (ee 0.073, p=0.305) | N=4753
- chicas, conflicto, sin controles: 6-11 -0.181* (ee 0.108, p=0.092) | 12-23 -0.085 (ee 0.073, p=0.246) | 36-49 -0.076 (ee 0.074, p=0.305) | N=4753
- chicas, recursos: 6-11 +0.035 (ee 0.089, p=0.695) | 12-23 -0.022 (ee 0.070, p=0.752) | 36-49 +0.041 (ee 0.064, p=0.525) | N=4234
- chicas, recursos, sin controles: 6-11 +0.087 (ee 0.094, p=0.351) | 12-23 +0.055 (ee 0.069, p=0.423) | 36-49 +0.104 (ee 0.072, p=0.149) | N=4234
- chicas, padre_fuera: 6-11 -0.113 (ee 0.100, p=0.257) | 12-23 +0.085 (ee 0.084, p=0.316) | 36-49 -0.030 (ee 0.079, p=0.708) | N=4754
- chicas, padre_fuera, sin controles: 6-11 -0.108 (ee 0.116, p=0.349) | 12-23 +0.082 (ee 0.089, p=0.355) | 36-49 -0.059 (ee 0.087, p=0.495) | N=4754
- chicas, sin_empleo: 6-11 -0.121 (ee 0.114, p=0.289) | 12-23 -0.117 (ee 0.087, p=0.180) | 36-49 -0.091 (ee 0.067, p=0.171) | N=4686
- chicas, sin_empleo, sin controles: 6-11 -0.068 (ee 0.114, p=0.552) | 12-23 -0.065 (ee 0.087, p=0.451) | 36-49 -0.063 (ee 0.068, p=0.358) | N=4686
- chicas, hacinamiento: 6-11 -0.160 (ee 0.124, p=0.200) | 12-23 +0.004 (ee 0.082, p=0.966) | 36-49 +0.039 (ee 0.099, p=0.693) | N=4754
- chicas, hacinamiento, sin controles: 6-11 -0.128 (ee 0.133, p=0.338) | 12-23 +0.041 (ee 0.089, p=0.646) | 36-49 +0.084 (ee 0.098, p=0.390) | N=4754
- todos, conflicto: 6-11 -0.102 (ee 0.067, p=0.126) | 12-23 -0.017 (ee 0.065, p=0.791) | 36-49 -0.063 (ee 0.058, p=0.275) | N=9564
- todos, conflicto, sin controles: 6-11 -0.091 (ee 0.066, p=0.165) | 12-23 -0.001 (ee 0.063, p=0.992) | 36-49 -0.061 (ee 0.058, p=0.292) | N=9564
- todos, recursos: 6-11 +0.009 (ee 0.061, p=0.878) | 12-23 +0.019 (ee 0.047, p=0.694) | 36-49 +0.037 (ee 0.049, p=0.446) | N=8514
- todos, recursos, sin controles: 6-11 +0.018 (ee 0.076, p=0.816) | 12-23 +0.022 (ee 0.053, p=0.685) | 36-49 +0.052 (ee 0.057, p=0.359) | N=8514
- todos, padre_fuera: 6-11 -0.059 (ee 0.073, p=0.416) | 12-23 +0.052 (ee 0.062, p=0.403) | 36-49 -0.060 (ee 0.065, p=0.356) | N=9566
- todos, padre_fuera, sin controles: 6-11 -0.058 (ee 0.081, p=0.469) | 12-23 +0.056 (ee 0.063, p=0.367) | 36-49 -0.080 (ee 0.070, p=0.255) | N=9566
- todos, sin_empleo: 6-11 -0.174*** (ee 0.066, p=0.008) | 12-23 -0.109* (ee 0.063, p=0.084) | 36-49 -0.121*** (ee 0.041, p=0.003) | N=9431
- todos, sin_empleo, sin controles: 6-11 -0.148** (ee 0.072, p=0.041) | 12-23 -0.098 (ee 0.069, p=0.152) | 36-49 -0.114** (ee 0.049, p=0.020) | N=9431
- todos, hacinamiento: 6-11 -0.067 (ee 0.085, p=0.430) | 12-23 -0.022 (ee 0.069, p=0.747) | 36-49 -0.013 (ee 0.076, p=0.869) | N=9566
- todos, hacinamiento, sin controles: 6-11 -0.061 (ee 0.093, p=0.510) | 12-23 -0.024 (ee 0.075, p=0.753) | 36-49 -0.000 (ee 0.084, p=0.996) | N=9566

## 2. Qué parte de la brecha explica el hogar (Gelbach, bootstrap de comunas, 300 réplicas)

chicas (N=4961)
- 6-11: brecha +0.300 [+0.100, +0.525]; con el hogar +0.305; explicado -0.005 [-0.022, +0.012], -2%
    conflicto: -0.005 [-0.018, +0.004]
    recursos: -0.000 [-0.005, +0.004]
    padre_fuera: -0.004 [-0.011, +0.002]
    sin_empleo: +0.005 [-0.006, +0.022]
    hacinamiento: -0.001 [-0.010, +0.007]
- 12-23: brecha +0.171 [-0.034, +0.386]; con el hogar +0.169; explicado +0.002 [-0.011, +0.016], 1%
    conflicto: -0.001 [-0.012, +0.007]
    recursos: -0.000 [-0.003, +0.005]
    padre_fuera: +0.001 [-0.006, +0.008]
    sin_empleo: +0.004 [-0.004, +0.013]
    hacinamiento: -0.002 [-0.007, +0.004]
- 36-49: brecha +0.182 [-0.011, +0.349]; con el hogar +0.181; explicado +0.000 [-0.012, +0.013], 0%
    conflicto: +0.001 [-0.011, +0.009]
    recursos: -0.000 [-0.004, +0.005]
    padre_fuera: -0.003 [-0.009, +0.005]
    sin_empleo: +0.004 [-0.007, +0.017]
    hacinamiento: -0.002 [-0.008, +0.004]

todos (N=9996)
- 6-11: brecha +0.147 [+0.007, +0.267]; con el hogar +0.146; explicado +0.001 [-0.010, +0.012], 1%
    conflicto: -0.002 [-0.016, +0.018]
    recursos: +0.000 [-0.002, +0.003]
    padre_fuera: -0.002 [-0.015, +0.005]
    sin_empleo: +0.004 [-0.000, +0.012]
    hacinamiento: -0.000 [-0.012, +0.007]
- 12-23: brecha +0.102 [-0.051, +0.239]; con el hogar +0.098; explicado +0.005 [-0.002, +0.011], 4%
    conflicto: +0.001 [-0.015, +0.021]
    recursos: +0.001 [-0.001, +0.003]
    padre_fuera: +0.000 [-0.009, +0.008]
    sin_empleo: +0.003 [-0.000, +0.009]
    hacinamiento: -0.001 [-0.010, +0.009]
- 36-49: brecha +0.103 [-0.039, +0.201]; con el hogar +0.103; explicado -0.000 [-0.007, +0.007], -0%
    conflicto: -0.006 [-0.031, +0.006]
    recursos: +0.000 [-0.002, +0.003]
    padre_fuera: +0.001 [-0.004, +0.014]
    sin_empleo: +0.003 [-0.002, +0.007]
    hacinamiento: +0.002 [-0.004, +0.015]
