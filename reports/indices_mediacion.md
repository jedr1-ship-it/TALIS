# Índices por dominio y mediación (scripts/30_indices_mediacion.py)
Correlaciones entre índices:
            adversidad  familia  colegio  economia
adversidad        1.00     0.13     0.12      0.44
familia           0.13     1.00     0.36      0.05
colegio           0.12     0.36     1.00      0.04
economia          0.44     0.05     0.04      1.00

## 1. ¿Los que tienen más adversidad tienen más síntomas?
PHQ-4 (DE) por cada DE del índice, EF de comuna y cohorte y controles; cada índice por separado y todos juntos.
- adversidad: adversidad +0.132*** (ee 0.011, p=0.000); N=9827
- familia: familia +0.298*** (ee 0.010, p=0.000); N=9970
- colegio: colegio +0.274*** (ee 0.011, p=0.000); N=9176
- economia: economia +0.021** (ee 0.010, p=0.038); N=9908
- adversidad + familia + colegio + economia: adversidad +0.098*** (ee 0.013, p=0.000); familia +0.228*** (ee 0.012, p=0.000); colegio +0.185*** (ee 0.012, p=0.000); economia -0.041*** (ee 0.011, p=0.000); N=9036

## 2. Qué pinta el terremoto: perfil por edad de cada índice
Diferencia con los expuestos con dos años, zona afectada menos no afectada (DE del índice; más alto = peor).
- todos, adversidad: bebés +0.173** (ee 0.082, p=0.035) | 1 año +0.113 (ee 0.070, p=0.109) | 3-4 años +0.079 (ee 0.058, p=0.176) | N=9834
- todos, familia: bebés +0.137** (ee 0.067, p=0.042) | 1 año +0.032 (ee 0.058, p=0.577) | 3-4 años +0.029 (ee 0.064, p=0.648) | N=9970
- todos, colegio: bebés +0.073 (ee 0.086, p=0.398) | 1 año +0.141** (ee 0.060, p=0.019) | 3-4 años -0.017 (ee 0.074, p=0.818) | N=9176
- todos, economia: bebés -0.039 (ee 0.089, p=0.661) | 1 año +0.039 (ee 0.071, p=0.578) | 3-4 años +0.115* (ee 0.061, p=0.061) | N=9915
- chicas, adversidad: bebés +0.151 (ee 0.129, p=0.241) | 1 año +0.162 (ee 0.111, p=0.144) | 3-4 años +0.034 (ee 0.102, p=0.738) | N=4874
- chicas, familia: bebés +0.060 (ee 0.122, p=0.620) | 1 año +0.122 (ee 0.092, p=0.183) | 3-4 años +0.053 (ee 0.104, p=0.610) | N=4946
- chicas, colegio: bebés +0.082 (ee 0.118, p=0.488) | 1 año +0.238*** (ee 0.087, p=0.006) | 3-4 años +0.012 (ee 0.097, p=0.905) | N=4539
- chicas, economia: bebés +0.071 (ee 0.126, p=0.576) | 1 año +0.132 (ee 0.091, p=0.145) | 3-4 años +0.199** (ee 0.082, p=0.015) | N=4919

## 3. Mediación: PHQ-4 con y sin los índices

todos (misma muestra, N=9036)
- sin índices: bebés +0.142** (ee 0.069, p=0.039) | 1 año +0.102 (ee 0.071, p=0.150) | 3-4 años +0.108* (ee 0.064, p=0.092)
- con adversidad: bebés +0.121* (ee 0.067, p=0.073) (15% explicado) | 1 año +0.087 (ee 0.068, p=0.198) (14% explicado) | 3-4 años +0.099 (ee 0.063, p=0.117) (8% explicado)
- con familia: bebés +0.103 (ee 0.065, p=0.114) (27% explicado) | 1 año +0.090 (ee 0.070, p=0.197) (12% explicado) | 3-4 años +0.082 (ee 0.062, p=0.184) (24% explicado)
- con colegio: bebés +0.125** (ee 0.061, p=0.041) (12% explicado) | 1 año +0.063 (ee 0.065, p=0.338) (38% explicado) | 3-4 años +0.114* (ee 0.059, p=0.052) (-6% explicado)
- con economia: bebés +0.143** (ee 0.069, p=0.038) (-1% explicado) | 1 año +0.101 (ee 0.070, p=0.151) (1% explicado) | 3-4 años +0.105 (ee 0.064, p=0.100) (2% explicado)
- con los cuatro: bebés +0.083 (ee 0.059, p=0.158) (41% explicado) | 1 año +0.057 (ee 0.065, p=0.379) (44% explicado) | 3-4 años +0.092 (ee 0.059, p=0.121) (15% explicado)

chicas (misma muestra, N=4467)
- sin índices: bebés +0.270*** (ee 0.103, p=0.009) | 1 año +0.160 (ee 0.099, p=0.105) | 3-4 años +0.142 (ee 0.092, p=0.124)
- con adversidad: bebés +0.247** (ee 0.098, p=0.012) (9% explicado) | 1 año +0.134 (ee 0.093, p=0.150) (16% explicado) | 3-4 años +0.138 (ee 0.087, p=0.112) (3% explicado)
- con familia: bebés +0.254** (ee 0.103, p=0.014) (6% explicado) | 1 año +0.119 (ee 0.094, p=0.206) (25% explicado) | 3-4 años +0.100 (ee 0.096, p=0.297) (29% explicado)
- con colegio: bebés +0.247** (ee 0.098, p=0.012) (9% explicado) | 1 año +0.084 (ee 0.090, p=0.349) (48% explicado) | 3-4 años +0.145* (ee 0.086, p=0.092) (-2% explicado)
- con economia: bebés +0.268*** (ee 0.102, p=0.009) (1% explicado) | 1 año +0.157 (ee 0.098, p=0.110) (2% explicado) | 3-4 años +0.136 (ee 0.091, p=0.137) (4% explicado)
- con los cuatro: bebés +0.227** (ee 0.094, p=0.015) (16% explicado) | 1 año +0.063 (ee 0.084, p=0.454) (61% explicado) | 3-4 años +0.122 (ee 0.087, p=0.162) (14% explicado)
