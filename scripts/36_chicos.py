#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
¿Y los chicos? Si el terremoto también los marcó pero lo expresan distinto,
debería verse en conducta o consumo, que el PHQ-4 no mide; si es un sesgo
de reporte, en lo que ve el cuidador.

Mismo perfil por edad al terremoto que scripts/33 (tramos agrupados:
6-17, 36-41 y 42-49 meses frente a 18-35), por sexo, en:

  síntomas      PHQ-4 (responde el adolescente)
  cuidador      CBCL internalizante y externalizante 2024
  consumo       alcohol, tabaco, cannabis u otras drogas en los últimos
                12 meses (alguno)
  violencia     victimización y clima de curso; violencia en el pololeo

Salida: reports/chicos.md y reports/chicos.csv
Uso:    python3 scripts/36_chicos.py
"""
import importlib.util
import warnings
from pathlib import Path

import pandas as pd

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p33 = modulo("p33", "33_ventanas.py")
p19 = modulo("p19", "19_exploratorio.py")
RESULTADOS = [("z_phq4", "Síntomas PHQ-4, adolescente"),
              ("cbcl_int", "Internalizante, cuidador"),
              ("cbcl_ext", "Externalizante, cuidador"),
              ("consumo", "Consumo de alcohol o drogas"),
              ("z_bull", "Victimización en el colegio"),
              ("viol_pareja", "Violencia en el pololeo")]
OUT = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def main():
    log("# ¿Y los chicos? (scripts/36_chicos.py)")
    log("Zona afectada menos no afectada, frente a 18-35 meses; columna 3 de "
        "la Table 3.")
    d = p19.construye()
    c = d[["alcohol", "fuma", "cannabis", "otras_drogas"]]
    d["consumo"] = c.max(axis=1).where(c.notna().any(axis=1))
    filas = []
    for y, lab in RESULTADOS:
        for g, sx in (("chicas", 1), ("chicos", 0)):
            b, n = p33.perfil(d, y, sx, "ventanas")
            p33.linea(f"{lab}, {g}", (b, n))
            OUT.append(p33.OUT.pop())
            for t, v in b.items():
                filas.append({"resultado": y, "etiqueta": lab, "grupo": g,
                              "tramo": t, "b": v[0], "se": v[1], "p": v[2],
                              "n": n})
    pd.DataFrame(filas).to_csv("reports/chicos.csv", index=False)
    Path("reports/chicos.md").write_text("\n".join(OUT) + "\n",
                                         encoding="utf-8")
    print("-> reports/chicos.md, reports/chicos.csv")


if __name__ == "__main__":
    main()
