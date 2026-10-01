# Tests de mecanismos — exploracion (scripts/17_mecanismos.py)
Muestra base: 10003; con modulo 2012: 8910; con TVIP 2024: 9990

## A. Kill-test: TVIP 2024 por edad de exposición
La U es de la salud mental; si aparece tambien en vocabulario, la historia de ventanas muere.
Bins gruesos (ref. 0-11m), N=9990:
  12-23m: -0.085 (ee 0.089, p=0.342)
  24-35m: -0.086 (ee 0.079, p=0.282)
  36-59m: +0.034 (ee 0.077, p=0.658)
  Contraste 3-4 vs 2: +0.119 (ee 0.053, p=0.024)
Bins finos (ref. 6-11m), N=9990:
  If12: -0.069 (ee 0.103, p=0.504)
  If18: -0.100 (ee 0.087, p=0.251)
  If24: -0.107 (ee 0.102, p=0.293)
  If30: -0.064 (ee 0.082, p=0.435)
  If36: +0.072 (ee 0.094, p=0.445)
  If42: -0.001 (ee 0.076, p=0.991)
(referencia PHQ-4, mismos bins, N=9996:)
  If12: +0.006 (ee 0.080, p=0.940)
  If18: -0.102 (ee 0.095, p=0.284)
  If24: -0.124 (ee 0.083, p=0.136)
  If30: -0.172 (ee 0.079, p=0.030)
  If36: -0.058 (ee 0.069, p=0.399)
  If42: -0.033 (ee 0.072, p=0.646)

## B. Angustia del cuidador (h4 2012) y los dos brazos
Prediccion de programacion: el brazo del bebe viaja por la crianza -> mas fuerte en hogares con cuidador angustiado; el brazo 3-4 viaja por la memoria propia -> no depende de h4.
angustia12 (estres/miedo/recuerdos del cuidador): media 0.351; por zona: {0.0: 0.147, 1.0: 0.415}
  hogares con angustia | z_phq4  : edad2 -0.133 (p=0.549); 3-4 menos 2 +0.173 (p=0.171); N=3124
  hogares con angustia | gad2_bin: edad2 -0.054 (p=0.597); 3-4 menos 2 +0.071 (p=0.247); N=3124
  hogares sin angustia | z_phq4  : edad2 -0.120 (p=0.154); 3-4 menos 2 +0.077 (p=0.292); N=5780
  hogares sin angustia | gad2_bin: edad2 -0.063 (p=0.105); 3-4 menos 2 +0.061 (p=0.060); N=5780

## C. Dano a la vivienda (h3 2012) dentro de la zona afectada
Tratamiento dentro de comuna: destruida o dano mayor vs menor o sin dano, solo zona afectada.
P(dano mayor | zona afectada) = 0.087 (N=6754)
(efecto principal del dano incluido: los coeficientes son el diferencial de cada bin frente a los bebes)
  z_phq4  : dano en bebes +0.152 (p=0.132); 12-23m -0.318 (p=0.014); 24-35m -0.087 (p=0.516); 36-59m -0.116 (p=0.362); N=6750
  gad2_bin: dano en bebes +0.083 (p=0.141); 12-23m -0.152 (p=0.029); 24-35m -0.032 (p=0.643); 36-59m -0.101 (p=0.132); N=6750
  z_tvip  : dano en bebes +0.069 (p=0.533); 12-23m -0.071 (p=0.529); 24-35m -0.368 (p=0.009); 36-59m -0.094 (p=0.438); N=6748

## D. Destete alrededor del 27-F (b30/b32 2012)
Mamaban el 27-F y edad 1-18m: N=1396; por zona {1.0: 1051, 0.0: 345}
  ventana post (0-3m tras 27-F): media 0.234; EQ +0.054 (ee 0.027, p=0.049); N=1396
  ventana placebo (meses -4 a -1): media 0.233; EQ +0.018 (ee 0.020, p=0.373); N=1820

## E. Corte escolar del 31 de marzo (nacidos feb-may 2006)
Misma capacidad de memoria, distinto ano de entrada al colegio. Si el brazo derecho fuera entrada escolar, saltaria aqui.
  z_phq4  : EQ x entrada temprana +0.334 (ee 0.164, p=0.042); EQ -0.095 (ee 0.126, p=0.454); N=831
           con EF de estrato: +0.192 (ee 0.157, p=0.223)
  gad2_bin: EQ x entrada temprana +0.106 (ee 0.064, p=0.094); EQ -0.040 (ee 0.048, p=0.400); N=831
           con EF de estrato: +0.077 (ee 0.072, p=0.280)
  z_tvip  : EQ x entrada temprana -0.039 (ee 0.179, p=0.826); EQ -0.049 (ee 0.108, p=0.650); N=830
           con EF de estrato: -0.057 (ee 0.195, p=0.772)
  (nacidos feb-mar: 415; abr-may: 416)
