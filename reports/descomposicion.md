# Descomposición de la brecha en salud mental (scripts/31_descomposicion.py)
Gelbach (2016): brecha sin índices - brecha con índices = suma de gamma_k x delta_k. Edad frente a dos años, zona afectada menos no afectada. Bootstrap de comunas, 500 réplicas.

## todos (N=9036)
gamma, efecto de cada índice sobre el PHQ-4 en la regresión completa: adversidad +0.098; familia +0.228; colegio +0.185; economia -0.041
- bebés: brecha +0.142 [+0.017, +0.309]; con índices +0.083 [-0.032, +0.215]; explicado +0.059 [+0.009, +0.114], 41%
    adversidad: +0.016 [+0.000, +0.034]
    familia: +0.029 [-0.001, +0.062]
    colegio: +0.011 [-0.018, +0.044]
    economia: +0.002 [-0.006, +0.010]
    hogar (adversidad + familia + economia): +0.048 [+0.014, +0.082]
- 1 año: brecha +0.102 [-0.041, +0.237]; con índices +0.057 [-0.077, +0.184]; explicado +0.045 [+0.001, +0.092], 44%
    adversidad: +0.011 [-0.003, +0.026]
    familia: +0.009 [-0.017, +0.038]
    colegio: +0.026 [+0.003, +0.049]
    economia: -0.002 [-0.008, +0.004]
    hogar (adversidad + familia + economia): +0.018 [-0.011, +0.054]
- 3-4 años: brecha +0.108 [-0.030, +0.228]; con índices +0.092 [-0.019, +0.200]; explicado +0.016 [-0.036, +0.060], 15%
    adversidad: +0.007 [-0.003, +0.019]
    familia: +0.019 [-0.013, +0.046]
    colegio: -0.004 [-0.032, +0.018]
    economia: -0.005 [-0.013, +0.000]
    hogar (adversidad + familia + economia): +0.021 [-0.011, +0.050]

## chicas (N=4467)
gamma, efecto de cada índice sobre el PHQ-4 en la regresión completa: adversidad +0.125; familia +0.231; colegio +0.230; economia -0.050
- bebés: brecha +0.270 [+0.088, +0.480]; con índices +0.227 [+0.054, +0.421]; explicado +0.043 [-0.033, +0.129], 16%
    adversidad: +0.018 [-0.011, +0.053]
    familia: +0.011 [-0.045, +0.068]
    colegio: +0.016 [-0.035, +0.074]
    economia: -0.003 [-0.019, +0.008]
    hogar (adversidad + familia + economia): +0.027 [-0.035, +0.091]
- 1 año: brecha +0.160 [-0.032, +0.351]; con índices +0.063 [-0.111, +0.224]; explicado +0.097 [+0.027, +0.176], 61%
    adversidad: +0.021 [-0.007, +0.051]
    familia: +0.029 [-0.012, +0.076]
    colegio: +0.054 [+0.016, +0.099]
    economia: -0.006 [-0.017, +0.001]
    hogar (adversidad + familia + economia): +0.043 [-0.009, +0.102]
- 3-4 años: brecha +0.142 [-0.039, +0.327]; con índices +0.122 [-0.038, +0.311]; explicado +0.020 [-0.058, +0.100], 14%
    adversidad: +0.003 [-0.018, +0.028]
    familia: +0.030 [-0.026, +0.081]
    colegio: -0.002 [-0.045, +0.042]
    economia: -0.011 [-0.027, -0.002]
    hogar (adversidad + familia + economia): +0.022 [-0.035, +0.074]
