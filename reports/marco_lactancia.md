# Marco conceptual: estrés materno durante la lactancia y salud mental de la hija o el hijo

Escrito el 6 de octubre de 2026, **antes** de estimar las predicciones nuevas
(P2 a P7). P1 y P8 ya estaban estimadas (scripts/20 y 25). El commit que
añade este archivo fija las predicciones; las estimaciones van en un commit
posterior (scripts/26_predicciones_lactancia.py).

## 1. Qué dice la literatura

**El estrés de la madre llega a la leche.** En 51 madres holandesas, el
estrés y la ansiedad maternos predicen más cortisol en la leche; los
síntomas depresivos, no (Aparicio et al. 2020, PLoS One 15(5): e0233554).
En ratas, la corticosterona de la madre pasa a la leche, al estómago, a la
sangre y al cerebro de las crías (Brummelte et al. 2010, Developmental
Neurobiology). Revisión del canal: Hollanders et al. (2017), Best Practice
& Research Clinical Endocrinology & Metabolism 31(4): 397-408.

**El cortisol materno, vía la leche, predice el temperamento del bebé.**
- Glynn et al. (2007), Early Human Development: el cortisol de la madre en
  los días tras el parto predice más miedo a los 2 meses en bebés
  amamantados, no en los alimentados con fórmula (253 díadas).
- Grey, Davis, Sandman y Glynn (2013), Psychoneuroendocrinology 38:
  1178-1185: el cortisol de la leche a los 3 meses se asocia con más afecto
  negativo, **en niñas y no en niños** (52 díadas).
- Nolvi et al. (2018), Developmental Science (FinnBrain): el cortisol de la
  leche a los 2,5 meses predice más miedo inducido en laboratorio a los 8
  meses, **en niñas y no en niños**.
- Cohorte Wirral (2021), Biology of Sex Differences: el efecto de la
  depresión posparto sobre el malestar del bebé a los 14 meses es **mayor en
  las niñas amamantadas**; en los niños no es significativo.
- En monos rhesus, el cortisol de la leche predice un temperamento más
  nervioso y menos seguro, con ventanas de sensibilidad distintas por sexo
  (Hinde et al. 2015, Behavioral Ecology 26(1): 269-281), y peor
  funcionamiento social y cognitivo posterior (Dettmer et al. 2018, Child
  Development). Otro estudio rhesus encuentra la asociación en machos y no
  en hembras (Sullivan et al. 2011, Developmental Psychobiology): la
  dirección por sexo no es unánime en primates.

**Contrapesos.**
- En ratas, dosis **bajas** de corticosterona en el agua de la madre
  lactante producen crías **menos** miedosas y menos reactivas al estrés,
  en parte porque la madre las lame y asea más (Catalani et al. 1993 y
  2000). El efecto depende de la dosis y del cuidado materno.
- En el único ensayo aleatorizado grande (PROBIT, Belarús), promover la
  lactancia no cambió la conducta a los 6,5 años (Kramer et al. 2008,
  Pediatrics 121(3): e435-e440). La asociación protectora observacional
  entre lactancia y salud mental adolescente (Oddy et al. 2010, Journal of
  Pediatrics 156(4): 568-574) puede ser selección.

**Desastres y lactancia.** Tras terremotos, el estrés reduce la producción
de leche y aumenta el destete (estudios del terremoto de Turquía 2023).
La exposición prenatal a un desastre eleva la ansiedad y la depresión en
niñas y los problemas de atención y conducta en niños (Nomura et al. 2023,
Journal of Child Psychology and Psychiatry, huracán Sandy). El cortisol
materno prenatal se asocia con mayor amígdala y más problemas afectivos en
niñas, no en niños (Buss et al. 2012, PNAS). Sobre el 27-F hay evidencia de
efectos prenatales en el peso y la gestación al nacer, no sobre lactancia.

**Lo que falta en la literatura.** Todos los estudios humanos del canal de
la leche miden el temperamento en el primer año o poco después. No
encontramos ninguno que siga a los niños hasta la adolescencia ni que use un
shock exógeno de estrés materno. Esa es la contribución posible.

## 2. El mecanismo, en una línea

Desastre → estrés y ansiedad de la madre lactante → más glucocorticoides en
la leche → calibración del sistema de estrés y del miedo del bebé, más en
niñas → vulnerabilidad latente que aflora como ansiedad y depresión en la
adolescencia.

## 3. Predicciones (fijadas antes de estimarlas)

| | Predicción | Fuente | Cómo se contrasta |
|---|---|---|---|
| P1 | Importa tomar pecho **en el momento** del shock, no haberlo tomado alguna vez | Glynn 2007 | Ya estimada: alguna vez −0,06 (n.s.) |
| P2 | El resultado se mantiene con el reporte de lactancia de 2010, más cercano al evento | medición | Misma interacción con g26/g28 de 2010 |
| P3 | El efecto es mayor si la madre quedó estresada o ansiosa tras el terremoto | Aparicio 2020 | Triple interacción con la angustia de la madre (h4, 2012) y con el daño a la vivienda (h3) |
| P4 | El efecto es mayor en niñas | Grey 2013, Nolvi 2018, Wirral 2021 | Diferencia formal niñas menos niños |
| P5 | El fenotipo es miedo y ansiedad, internalizante, no externalizante | Glynn 2007, Nolvi 2018 | CBCL externalizante 2024 nulo; GAD-2 mayor que PHQ-2 |
| P6 | Hay señal temprana: peor desarrollo socioemocional en la infancia | Glynn, Grey, Nolvi, Wirral | ASQ:SE a los 12 meses y Battelle personal-social, ola 2010 (1 a 9 meses tras el terremoto) |
| P7 | El efecto es mayor cuanto más depende el bebé de la leche: bebés de 6-8 meses frente a 9-11 | Hinde 2015 (ventanas) | Interacción por edad dentro de los bebés |
| P8 | No hay daño cognitivo general | especificidad | Ya estimada: vocabulario no empeora |

Una predicción que falle no se esconde: se reporta igual que las que se
cumplan.
