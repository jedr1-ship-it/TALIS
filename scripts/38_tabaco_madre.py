#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
El tabaco de la madre, el mecanismo de Gillmore (2026) que depende de la
edad: ¿cambia según la edad del hijo al terremoto?

La ELPI 2010 pregunta si la madre fumó durante el embarazo (g7a) y durante
los primeros 6 meses de vida del niño (g8a). Gillmore encuentra más
tabaquismo cuando el terremoto cayó en esas ventanas: embarazo o 0-6 meses.
En nuestros grupos (6 a 49 meses el 27-F) las dos ventanas terminaron antes
del terremoto, así que no pudo cambiarlas: el perfil por edad es una prueba
de balance, no un mecanismo.

Mismo perfil que el resto: grupos del paper (6-11 meses, 1 año y 3-4 años
frente a 2 años), zona afectada menos no afectada, columna 3 de la Table 3.

Salida: reports/tabaco_madre.md
Uso:    python3 scripts/38_tabaco_madre.py
"""
import importlib.util
import warnings
from pathlib import Path

import pandas as pd
import pyreadstat

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p33", HERE / "33_ventanas.py")
p33 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p33)
p15 = p33.p15
num = p15.num
OUT = []


def main():
    d, _, _ = p15.load_data()
    e, _ = pyreadstat.read_dta("data/interim/2010/Entrevistada_2010.dta",
                               usecols=["folio", "g7a", "g8a"],
                               encoding="latin1")
    e["folio"] = num(e.folio).astype("int64")
    e = e.drop_duplicates("folio")
    for v, k in (("g7a", "fuma_embarazo"), ("g8a", "fuma_6meses")):
        s = num(e[v])
        e[k] = (s == 1).astype(float).where(s.isin([1, 2]))
    d = d.merge(e[["folio", "fuma_embarazo", "fuma_6meses"]], on="folio",
                how="left")
    OUT.append("# Tabaco de la madre por edad al terremoto "
               "(scripts/38_tabaco_madre.py)")
    OUT.append("Zona afectada menos no afectada, frente a 2 años; ventanas "
               "anteriores al 27-F en todos los grupos (prueba de balance).")
    for y, lab in (("fuma_embarazo", "Fumó en el embarazo"),
                   ("fuma_6meses", "Fumó en los primeros 6 meses")):
        OUT.append(f"\nMedia en la muestra: {d[y].mean():.3f}")
        for g, sx in (("todos", None), ("chicas", 1)):
            p33.linea(f"{lab}, {g}", p33.perfil(d, y, sx, "paper"))
            OUT.append(p33.OUT.pop())
    Path("reports/tabaco_madre.md").write_text("\n".join(OUT) + "\n",
                                               encoding="utf-8")
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
