# Tests de mecanismos — exploracion (scripts/17_mecanismos.py)
Muestra base: 10003; con modulo 2012: 8910; con TVIP 2024: 9990

## A. Perfil por edad al terremoto: salud mental y vocabulario
- PHQ-4 (sintomas; alto = peor), N=9996, ref. 6-11m | 12–17: +0.006 (p=0.940); 18–23: -0.102 (p=0.284); 24–29: -0.124 (p=0.136); 30–35: -0.172 (p=0.030); 36–41: -0.058 (p=0.399); 42–49: -0.033 (p=0.646)
- resiliencia (alto = mejor), N=9996, ref. 6-11m | 12–17: +0.055 (p=0.490); 18–23: +0.068 (p=0.454); 24–29: +0.084 (p=0.351); 30–35: +0.202 (p=0.022); 36–41: +0.076 (p=0.320); 42–49: +0.117 (p=0.144)
- satisfaccion vital (alto = mejor), N=9996, ref. 6-11m | 12–17: +0.079 (p=0.203); 18–23: +0.093 (p=0.186); 24–29: +0.066 (p=0.329); 30–35: +0.131 (p=0.057); 36–41: +0.154 (p=0.065); 42–49: +0.082 (p=0.197)
- TVIP (vocabulario; alto = mejor), N=9990, ref. 6-11m | 12–17: -0.069 (p=0.504); 18–23: -0.100 (p=0.251); 24–29: -0.107 (p=0.293); 30–35: -0.064 (p=0.435); 36–41: +0.072 (p=0.445); 42–49: -0.001 (p=0.991)
Tests formales en bins gruesos (spec col. 3):
- Daño en salud mental menos daño en vocabulario (PHQ + TVIP), N=9986: edad 2 frente a bebes -0.236 (ee 0.102, p=0.021); 3-4 frente a 2 +0.218 (ee 0.084, p=0.009)
- Artefacto comun (PHQ menos resiliencia), N=9996: edad 2 frente a bebes -0.288 (ee 0.129, p=0.026); 3-4 frente a 2 +0.146 (ee 0.114, p=0.199)

## B. Angustia del cuidador (h4 2012) y los dos brazos
angustia12 (estres, miedo o recuerdos del cuidador): media 0.351; por zona {0.0: 0.147, 1.0: 0.415}
- cuidador con angustia | z_phq4: bebes frente a 2 +0.133 (ee 0.221, p=0.549); 3-4 frente a 2 +0.173 (ee 0.127, p=0.171); N=3124
- cuidador con angustia | gad2_bin: bebes frente a 2 +0.054 (ee 0.103, p=0.597); 3-4 frente a 2 +0.071 (ee 0.061, p=0.247); N=3124
- cuidador sin angustia | z_phq4: bebes frente a 2 +0.120 (ee 0.084, p=0.154); 3-4 frente a 2 +0.077 (ee 0.073, p=0.292); N=5780
- cuidador sin angustia | gad2_bin: bebes frente a 2 +0.063 (ee 0.039, p=0.105); 3-4 frente a 2 +0.061 (ee 0.033, p=0.060); N=5780

## C. Daño a la vivienda (h3 2012) por edad, zona afectada
P(destruida o daño mayor | zona afectada) = 0.087 (N=6754). Efecto total del daño en cada edad (principal + interaccion):
- z_phq4: 0-11m +0.152 (ee 0.101, p=0.132); 12-23m -0.166 (ee 0.080, p=0.037); 24-35m +0.066 (ee 0.081, p=0.417); 36-59m +0.037 (ee 0.072, p=0.612); N=6750
- gad2_bin: 0-11m +0.083 (ee 0.056, p=0.141); 12-23m -0.069 (ee 0.039, p=0.079); 24-35m +0.051 (ee 0.033, p=0.124); 36-59m -0.018 (ee 0.038, p=0.632); N=6750
- z_tvip: 0-11m +0.069 (ee 0.111, p=0.533); 12-23m -0.002 (ee 0.086, p=0.984); 24-35m -0.299 (ee 0.080, p=0.000); 36-59m -0.025 (ee 0.088, p=0.779); N=6748

## D. Destete alrededor del 27-F (b30/b32 2012)
- destete en los 3 meses tras el 27-F: media 0.234; zona afectada +0.054 (ee 0.027, p=0.049); N=1396
- destete en los 4 meses antes (placebo): media 0.233; zona afectada +0.018 (ee 0.020, p=0.373); N=1820

## E. Corte escolar del 31 de marzo (nacidos feb-may 2006)
- z_phq4: zona afectada x entrada en marzo 2010 +0.334 (ee 0.164, p=0.042); con EF de estrato +0.193 (ee 0.158, p=0.222); N=831
- gad2_bin: zona afectada x entrada en marzo 2010 +0.106 (ee 0.064, p=0.094); con EF de estrato +0.080 (ee 0.071, p=0.262); N=831
- z_tvip: zona afectada x entrada en marzo 2010 -0.039 (ee 0.179, p=0.826); con EF de estrato -0.067 (ee 0.196, p=0.731); N=830
  (nacidos feb-mar: 415; abr-may: 417)
