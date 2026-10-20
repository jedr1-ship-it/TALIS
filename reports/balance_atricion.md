# Atrición entre 2010 y 2024 y balance en la línea base (scripts/42_balance_atricion.py)
Zona afectada menos no afectada, frente a quienes tenían 2 años; EF de región, año de nacimiento y grupo de edad; sin pesos; EE robustos (HC1).

Línea base 2010: 15,175 niños; evaluados 14,161; responden en 2024 10,003 (65.9%); entre los evaluados, 67.1%.
Mes mediano de evaluación por región (meses desde el 27-F): 1: 3, 2: 3, 3: 2, 4: 3, 5: 3, 6: 3, 7: 3, 8: 4, 9: 3, 10: 3, 11: 2, 12: 2, 13: 4, 14: 2, 15: 2
Validación con los 11,871 que tienen fecha exacta: error medio -0.08 meses (zona afectada -0.12, no afectada +0.05); mismo grupo de edad 93.4%.

## Atrición diferencial (responde en 2024, 0/1)
- chicas: 6-11 meses -0.047 (ee 0.044) | 1 año +0.009 (ee 0.035) | 3-4 años +0.019 (ee 0.035) | conjunta p=0.47 | media 0.673 | N=6,990
- chicos: 6-11 meses +0.019 (ee 0.043) | 1 año +0.049 (ee 0.035) | 3-4 años +0.028 (ee 0.034) | conjunta p=0.57 | media 0.669 | N=7,171
- todos: 6-11 meses -0.019 (ee 0.030) | 1 año +0.026 (ee 0.025) | 3-4 años +0.019 (ee 0.024) | conjunta p=0.43 | media 0.671 | N=14,161

## Peso al nacer de las chicas (DE)
- toda la muestra de 2010: 6-11 meses +0.064 (ee 0.098) | 1 año +0.087 (ee 0.075) | 3-4 años +0.145* (ee 0.076) | conjunta p=0.30 | media -0.115 | N=6,409
- solo quienes responden en 2024: 6-11 meses +0.120 (ee 0.115) | 1 año +0.073 (ee 0.092) | 3-4 años +0.189** (ee 0.093) | conjunta p=0.24 | media -0.090 | N=4,300

## 6-11 meses frente a todas las demás edades
- responde en 2024, chicas: 6-11 meses -0.057 (ee 0.038) | conjunta p=0.14 | media 0.673 | N=6,990
- responde en 2024, chicos: 6-11 meses -0.007 (ee 0.037) | conjunta p=0.85 | media 0.669 | N=7,171
- responde en 2024, todos: 6-11 meses -0.034 (ee 0.027) | conjunta p=0.20 | media 0.671 | N=14,161
- peso al nacer de las chicas, toda la muestra de 2010: 6-11 meses -0.015 (ee 0.087) | conjunta p=0.86 | media -0.115 | N=6,409
- peso al nacer de las chicas, quienes responden en 2024: 6-11 meses +0.031 (ee 0.103) | conjunta p=0.76 | media -0.090 | N=4,300

## Robustez de la atrición
- chicas, sin quienes están a un mes de un corte: 6-11 meses -0.054 (ee 0.049) | 1 año -0.013 (ee 0.041) | 3-4 años -0.002 (ee 0.039) | conjunta p=0.68 | media 0.675 | N=5,514
- chicos, sin quienes están a un mes de un corte: 6-11 meses +0.032 (ee 0.048) | 1 año +0.083** (ee 0.042) | 3-4 años +0.037 (ee 0.039) | conjunta p=0.26 | media 0.663 | N=5,679
- todos, sin quienes están a un mes de un corte: 6-11 meses -0.014 (ee 0.034) | 1 año +0.030 (ee 0.029) | 3-4 años +0.011 (ee 0.027) | conjunta p=0.57 | media 0.669 | N=11,193
- chicas, fecha exacta donde la hay: 6-11 meses -0.046 (ee 0.042) | 1 año +0.013 (ee 0.035) | 3-4 años +0.020 (ee 0.034) | conjunta p=0.42 | media 0.677 | N=7,331
- chicos, fecha exacta donde la hay: 6-11 meses +0.007 (ee 0.041) | 1 año +0.064* (ee 0.035) | 3-4 años +0.039 (ee 0.033) | conjunta p=0.26 | media 0.670 | N=7,524
- todos, fecha exacta donde la hay: 6-11 meses -0.024 (ee 0.029) | 1 año +0.036 (ee 0.025) | 3-4 años +0.025 (ee 0.024) | conjunta p=0.16 | media 0.673 | N=14,855

## Resto del balance en 2010 (chicas)
- educación de la madre (años), toda la muestra de 2010: 6-11 meses -0.247 (ee 0.296) | 1 año -0.564** (ee 0.243) | 3-4 años -0.105 (ee 0.235) | conjunta p=0.11 | media 10.338 | N=6,866
- edad de la madre (años), toda la muestra de 2010: 6-11 meses +0.219 (ee 0.644) | 1 año +0.034 (ee 0.519) | 3-4 años +0.604 (ee 0.520) | conjunta p=0.63 | media 29.303 | N=6,924
- educación de la madre (años), solo quienes responden en 2024: 6-11 meses -0.499 (ee 0.349) | 1 año -0.585** (ee 0.279) | 3-4 años -0.066 (ee 0.273) | conjunta p=0.11 | media 10.241 | N=4,632
- edad de la madre (años), solo quienes responden en 2024: 6-11 meses +0.334 (ee 0.780) | 1 año +0.197 (ee 0.634) | 3-4 años +0.488 (ee 0.642) | conjunta p=0.89 | media 29.575 | N=4,668
