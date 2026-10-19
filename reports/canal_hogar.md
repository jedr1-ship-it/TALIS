# El canal hogar por edad al terremoto (scripts/35_canal_hogar.py)
Cobertura de los índices: conflicto 0.96; recursos 0.85

## 1. ¿Cambió el hogar distinto según la edad?
Zona afectada menos no afectada, frente a 2 años (DE del índice; más alto = peor).
- chicas, conflicto: 6-11 -0.188* (ee 0.107, p=0.080) | 12-23 -0.100 (ee 0.074, p=0.175) | 36-49 -0.075 (ee 0.073, p=0.305) | N=4753
- chicas, conflicto, sin controles: 6-11 -0.181* (ee 0.108, p=0.092) | 12-23 -0.085 (ee 0.073, p=0.246) | 36-49 -0.076 (ee 0.074, p=0.305) | N=4753
- chicas, recursos: 6-11 +0.035 (ee 0.089, p=0.695) | 12-23 -0.022 (ee 0.070, p=0.752) | 36-49 +0.041 (ee 0.064, p=0.525) | N=4234
- chicas, recursos, sin controles: 6-11 +0.087 (ee 0.094, p=0.351) | 12-23 +0.055 (ee 0.069, p=0.423) | 36-49 +0.104 (ee 0.072, p=0.149) | N=4234
- todos, conflicto: 6-11 -0.102 (ee 0.067, p=0.126) | 12-23 -0.017 (ee 0.065, p=0.791) | 36-49 -0.063 (ee 0.058, p=0.275) | N=9564
- todos, conflicto, sin controles: 6-11 -0.091 (ee 0.066, p=0.165) | 12-23 -0.001 (ee 0.063, p=0.992) | 36-49 -0.061 (ee 0.058, p=0.292) | N=9564
- todos, recursos: 6-11 +0.009 (ee 0.061, p=0.878) | 12-23 +0.019 (ee 0.047, p=0.694) | 36-49 +0.037 (ee 0.049, p=0.446) | N=8514
- todos, recursos, sin controles: 6-11 +0.018 (ee 0.076, p=0.816) | 12-23 +0.022 (ee 0.053, p=0.685) | 36-49 +0.052 (ee 0.057, p=0.359) | N=8514

## 2. Qué parte de la brecha explica el hogar (Gelbach, bootstrap de comunas, 300 réplicas)

chicas (N=4232)
- 6-11: brecha +0.370 [+0.134, +0.600]; con el hogar +0.383; explicado -0.013 [-0.029, -0.001], -4%
    conflicto: -0.013 [-0.030, -0.001]
    recursos: -0.000 [-0.006, +0.003]
- 12-23: brecha +0.140 [-0.109, +0.382]; con el hogar +0.151; explicado -0.011 [-0.022, -0.000], -8%
    conflicto: -0.011 [-0.023, -0.001]
    recursos: +0.000 [-0.002, +0.004]
- 36-49: brecha +0.190 [-0.033, +0.380]; con el hogar +0.197; explicado -0.007 [-0.019, +0.002], -3%
    conflicto: -0.006 [-0.019, +0.002]
    recursos: -0.000 [-0.004, +0.002]

todos (N=8506)
- 6-11: brecha +0.175 [+0.048, +0.293]; con el hogar +0.180; explicado -0.004 [-0.013, +0.001], -2%
    conflicto: -0.004 [-0.012, +0.000]
    recursos: -0.000 [-0.002, +0.001]
- 12-23: brecha +0.072 [-0.100, +0.210]; con el hogar +0.072; explicado -0.000 [-0.006, +0.005], -1%
    conflicto: -0.000 [-0.006, +0.005]
    recursos: -0.000 [-0.001, +0.001]
- 36-49: brecha +0.087 [-0.066, +0.194]; con el hogar +0.089; explicado -0.002 [-0.009, +0.003], -3%
    conflicto: -0.002 [-0.008, +0.003]
    recursos: -0.000 [-0.002, +0.001]
