# Efectos en niveles (scripts/24_niveles.py)

## 1. Intensidad sísmica dentro de la región (PGA/10, expuestos 2024)
Placebos, características fijadas antes del terremoto:
- z_peso: +0.015 (ee 0.021, p=0.456)
- z_gest: +0.030 (ee 0.019, p=0.121)
- educ_madre10: +0.459*** (ee 0.165, p=0.005)
- edad_madre10: +0.501*** (ee 0.172, p=0.004)
- rural10: -0.093*** (ee 0.032, p=0.003)
Dentro de cada región, las comunas más sacudidas tenían madres más educadas y eran más urbanas: el diseño confunde intensidad con nivel socioeconómico y no sirve para niveles.

## 2. Concebidos después como comparación: 2024 (expuestos a los 15-18 frente a concebidos después, medidos en 2017)
- z_tvip, efecto total: -0.240** (ee 0.104, p=0.021); N=13779
  por edad al terremoto: 0-11m -0.256** (ee 0.117, p=0.029); 12-23m -0.279*** (ee 0.102, p=0.006); 24-35m -0.255** (ee 0.104, p=0.015); 36-59m -0.187* (ee 0.112, p=0.093)
  chicas: -0.225* (ee 0.117, p=0.055); N=6816
  chicos: -0.265** (ee 0.110, p=0.016); N=6963
  dosis, exposición x PGA/10 dentro de la comuna: -0.059* (ee 0.034, p=0.082); N=13779
  con tendencias lineales por comuna: -0.412** (ee 0.180, p=0.022); N=13779
- z_cbcl, efecto total: +0.084 (ee 0.088, p=0.345); N=11038
  por edad al terremoto: 0-11m +0.082 (ee 0.101, p=0.418); 12-23m +0.098 (ee 0.091, p=0.283); 24-35m +0.088 (ee 0.092, p=0.335); 36-59m +0.067 (ee 0.094, p=0.479)
  chicas: +0.142 (ee 0.123, p=0.247); N=5459
  chicos: -0.012 (ee 0.118, p=0.921); N=5579
  dosis, exposición x PGA/10 dentro de la comuna: +0.026 (ee 0.028, p=0.350); N=11038
  con tendencias lineales por comuna: -0.066 (ee 0.125, p=0.598); N=11038

## 2. Concebidos después como comparación: 2017 (expuestos a los 7-11 frente a concebidos después, ambos en 2017)
- z_tvip, efecto total: -0.161** (ee 0.073, p=0.027); N=13518
  mismos niños que en 2024: -0.155* (ee 0.081, p=0.056); N=10880
  por edad al terremoto: 0-11m -0.164** (ee 0.081, p=0.043); 12-23m -0.152** (ee 0.073, p=0.038); 24-35m -0.180** (ee 0.080, p=0.025); 36-59m -0.149* (ee 0.091, p=0.099)
  chicas: -0.115 (ee 0.093, p=0.214); N=6655
  chicos: -0.211*** (ee 0.080, p=0.008); N=6863
  dosis, exposición x PGA/10 dentro de la comuna: -0.043* (ee 0.024, p=0.075); N=13518
  con tendencias lineales por comuna: -0.309** (ee 0.131, p=0.019); N=13518
- z_cbcl, efecto total: -0.091 (ee 0.079, p=0.251); N=10949
  mismos niños que en 2024: -0.074 (ee 0.080, p=0.359); N=8261
  por edad al terremoto: 0-11m -0.047 (ee 0.095, p=0.621); 12-23m -0.123 (ee 0.089, p=0.168); 24-35m -0.079 (ee 0.084, p=0.346); 36-59m -0.114 (ee 0.079, p=0.146)
  chicas: -0.068 (ee 0.129, p=0.597); N=5378
  chicos: -0.143 (ee 0.112, p=0.201); N=5571
  dosis, exposición x PGA/10 dentro de la comuna: -0.010 (ee 0.026, p=0.702); N=10949
  con tendencias lineales por comuna: -0.259** (ee 0.128, p=0.043); N=10949
