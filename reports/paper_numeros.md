# Log de estimaciones del paper

```
datos: 10,003 adolescentes | PGA: ok
T9 atricion I_12 +0.038
T9 atricion I_24 +0.028
T9 atricion I_36 +0.038
-> paper/tables/t9_atricion.tex
-> paper/tables/t1_descriptivos.tex
T3 z_phq4 col3: {'12-23m': '-0.045', '24-35m': '-0.147**', '36-59m': '-0.044'} contr +0.103*
T3 gad2_bin col3: {'12-23m': '-0.012', '24-35m': '-0.073**', '36-59m': '-0.016'} contr +0.058**
T3 phq2_bin col3: {'12-23m': '-0.014', '24-35m': '-0.048', '36-59m': '-0.010'} contr +0.038
-> paper/tables/t3_main.tex
-> paper/tables/t4_informante.tex
T5 z_phq4: PGA 24-35 -0.068**, contr +0.031
T5 gad2_bin: PGA 24-35 -0.039***, contr +0.023**
-> paper/tables/t5_dosis.tex
T6 placebo z_peso {'12-23m': '-0.013', '24-35m': '-0.082', '36-59m': '+0.017'}
T6 placebo z_talla {'12-23m': '-0.029', '24-35m': '-0.074', '36-59m': '+0.014'}
T6 placebo z_gest {'12-23m': '-0.023', '24-35m': '-0.166**', '36-59m': '-0.001'}
T6 placebo prematuro {'12-23m': '+0.017', '24-35m': '+0.041*', '36-59m': '+0.003'}
T6 placebo z_apgar {'12-23m': '-0.083', '24-35m': '-0.043', '36-59m': '-0.013'}
-> paper/tables/t6_placebo.tex
T7 Preferred specification (column 3) -0.147** contr +0.103*
T7 Fixed effects only -0.144** contr +0.106*
T7 Excluding the Metropolitan Region -0.120 contr +0.109*
T7 Unweighted -0.129* contr +0.097
T7 PHQ-4 in points (0--12), not standardized -0.391** contr +0.277*
T7 Balanced sample with a 2017 CBCL -0.114 contr +0.083
T7 Controlling for the birth endowment -0.144** contr +0.100*
T7 Reweighted for attrition (IPW) -0.149** contr +0.104*
T7 Continuous dose: PGA (z) instead of the zone -0.068** contr +0.031
-> paper/tables/t7_robustez.tex
T7 inferencia: perm {'24': 0.0455, 'ct': 0.107} | wild region {'24': 0.132, 'ct': 0.069}
T8 RW z_phq4 24: 0.120 ct: 0.235
T8 RW phq2_bin 24: 0.299 ct: 0.468
T8 RW gad2_bin 24: 0.102 ct: 0.111
T8 RW z_cbcl 24: 0.299 ct: 0.615
-> paper/tables/t8_romanowolf.tex
T10 z_resil {'12-23m': '+0.096', '24-35m': '+0.037', '36-59m': '+0.058'}
T10 z_satisf {'12-23m': '+0.086*', '24-35m': '+0.098*', '36-59m': '+0.116*'}
T10 z_salud {'12-23m': '-0.086', '24-35m': '-0.072', '36-59m': '-0.054'}
T10 z_bull {'12-23m': '+0.028', '24-35m': '-0.047', '36-59m': '+0.037'}
T10 ciber_any {'12-23m': '-0.015', '24-35m': '-0.007', '36-59m': '-0.005'}
-> paper/tables/t10a_bienestar.tex
T10 viol_pareja {'12-23m': '+0.025', '24-35m': '+0.005', '36-59m': '+0.028'}
T10 fuma {'12-23m': '+0.012', '24-35m': '-0.002', '36-59m': '-0.022'}
T10 alcohol {'12-23m': '-0.038', '24-35m': '-0.037', '36-59m': '-0.078**'}
T10 cannabis {'12-23m': '+0.018', '24-35m': '+0.014', '36-59m': '+0.013'}
-> paper/tables/t10b_riesgo.tex
-> paper/tables/t11_madre.tex
T11 z_phq4 vuln contr: +0.097 | no-vuln contr: +0.107
T11 gad2_bin vuln contr: +0.008 | no-vuln contr: +0.072**
T12 Girls -0.300*** contr +0.182**
T12 Boys -0.016 contr +0.042
T12 Mother with secondary education or less -0.107 contr +0.071
T12 Mother with tertiary education -0.201 contr +0.182
T12 Urban household in 2010 -0.139* contr +0.129**
T12 Rural household in 2010 -0.238 contr -0.213
-> paper/tables/t12_heterogeneidad.tex
-> paper/figures/f1_gradiente_u.pdf
-> paper/figures/f2_dosis_pga.pdf
-> paper/figures/f3_mapa_dosis.pdf (2195 municipios con dato)
-> paper/figures/f4_mapa_sintomas.pdf (2195 municipios con dato)
T2 LP z_tvip ['-0.226**', '-0.227**', '-0.240**', '-0.412**']
T2 LP z_cbcl ['+0.057', '+0.059', '+0.084', '-0.066']
-> paper/tables/t2_largo_plazo.tex
```
