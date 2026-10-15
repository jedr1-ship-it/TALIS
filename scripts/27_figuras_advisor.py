#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figuras de la presentación de cinco diapositivas para el advisor: la idea,
la base, lo que encontré y por qué lo descarté. Usa el estilo de
scripts/22_figuras_presentacion.py y toma los coeficientes de los informes
ya commiteados, así que no reestima nada:

  perfil.png       PHQ-4 por edad al terremoto, chicas y chicos, frente a los
                   expuestos con dos años (reports/presentacion_numeros.md)
  trayectoria.png  zona afectada x tomaba pecho el 27-F, de 2010 a 2024
                   (reports/predicciones_lactancia.md y
                   reports/lactancia_robustez.md), en el eje de la edad media
                   de los bebés en cada ola

Intervalos al 95%. La edad media en cada ola se calcula con los datos.

Salida: reports/figures/advisor/*.png y reports/advisor_numeros.md
Uso:    python3 scripts/27_figuras_advisor.py
"""
import importlib.util
import re
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.lines import Line2D                  # noqa: E402
import numpy as np                                   # noqa: E402
import pandas as pd                                  # noqa: E402
import pyreadstat                                    # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p22", HERE / "22_figuras_presentacion.py")
p22 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p22)
p22.OUTD = Path("reports/figures/advisor")
BG, INK, ACC, MUTED = p22.BG, p22.INK, p22.ACC, p22.MUTED
GRIS, GRID, NARANJA = p22.GRIS, p22.GRID, p22.NARANJA
pt, fp, coma = p22.pt, p22.fp, p22.coma
BANDA = "#E4E9F1"               # primer año de vida
NUM = re.compile(r"([+-]\d+\.\d+)\**\s+\(ee (\d+\.\d+), p=(\d+\.\d+)\)")


def lee(archivo, etiqueta, seccion=None):
    """(b, ee, p) de la primera línea que contiene `etiqueta`, dentro de la
    sección que empieza con `seccion` si se da."""
    texto = Path(archivo).read_text(encoding="utf-8")
    if seccion:
        texto = texto[texto.index(seccion):]
        texto = texto.split("\n## ")[0]
    for linea in texto.splitlines():
        if etiqueta in linea:
            m = NUM.search(linea[linea.index(etiqueta):])
            if m:
                return tuple(float(x) for x in m.groups())
    raise ValueError(f"{etiqueta!r} no está en {archivo}")


def edades_bebes():
    """Edad media, en años, de los expuestos con 6-11 meses en cada ola."""
    d = pd.read_pickle("data/processed/paper_adolescentes.pkl")
    b = d[d["bin"].astype(str) == "0-11m"][["folio", "edad_meses"]]
    out = {}
    for ola, f, col in (
            (2010, "data/interim/2010/Evaluaciones_2010.dta", "edad_meses"),
            (2012, "data/interim/2012/Evaluaciones_2012.dta", "edad_meses"),
            (2017, "data/interim/2017/Base Evaluaciones ELPI III.dta",
             "edad_mesesr")):
        e, _ = pyreadstat.read_dta(f, usecols=["folio", col])
        e["folio"] = pd.to_numeric(e.folio, errors="coerce").astype("int64")
        m = b[["folio"]].merge(e.drop_duplicates("folio"), on="folio")
        out[ola] = float(pd.to_numeric(m[col], errors="coerce").mean() / 12)
    out[2024] = float(pd.to_numeric(b.edad_meses, errors="coerce").mean()
                      / 12)
    return out


def perfil():
    archivo = "reports/presentacion_numeros.md"
    cats = ["6–11 meses", "1 año", "2 años", "3–4 años"]
    series = []
    for nom, sec, col in (("Chicas", "## Perfil PHQ-4, Chicas", ACC),
                          ("Chicos", "## Perfil PHQ-4, Chicos", GRIS)):
        b = {k: lee(archivo, f"- {k}:", sec) for k in ("0-11m", "12-23m",
                                                       "36-59m")}
        for k, v in b.items():
            p22.log(f"- perfil {nom} {k}: {v[0]:+.3f} (ee {v[1]:.3f}, "
                    f"p={v[2]:.3f})")
        series.append({"name": nom, "color": col,
                       "pts": [b["0-11m"], b["12-23m"], None, b["36-59m"]]})
    p22.coef_vertical("perfil.png", cats, series,
                      "PHQ-4 a los 15–18 años, en desv. estándar",
                      w=1000, h=470, ylim=(-0.35, 0.72))


def trayectoria():
    pr, rb = ("reports/predicciones_lactancia.md",
              "reports/lactancia_robustez.md")
    edad = edades_bebes()
    for ola, a in edad.items():
        p22.log(f"- edad media de los bebés en {ola}: {a:.1f} años")
    madre = [(edad[2010], lee(pr, "ASQ:SE 12 meses"), "ASQ:SE"),
             (edad[2012], lee(rb, "CBCL total 2012"), "CBCL"),
             (edad[2017], lee(rb, "CBCL 2017"), "CBCL"),
             (edad[2024], lee(rb, "CBCL 2024"), "CBCL")]
    propio = [(edad[2024], lee(pr, "Referencia, PHQ-4"), "PHQ-4")]
    for x, t, nom in madre + propio:
        p22.log(f"- trayectoria {nom} a los {x:.1f} años: {t[0]:+.3f} "
                f"(ee {t[1]:.3f}, p={t[2]:.3f})")

    f = p22.lienzo(1000, 600)
    ax = f.add_axes([0.085, 0.17, 0.895, 0.70])
    p22.ejes_limpios(ax)
    ax.axvspan(0, 2.0, color=BANDA, lw=0, zorder=1)
    ax.text(0.15, 0.80, "Donde la\nmedicina\npredice\nel efecto",
            fontproperties=fp(22), color=MUTED, ha="left", va="top",
            linespacing=1.25, zorder=2)
    ax.axhline(0, color=MUTED, lw=pt(2.5), zorder=2)

    def punto(x, t, nom, col, lado):
        b, se = t[0], t[1]
        ax.plot([x, x], [b - 1.96 * se, b + 1.96 * se], color=col,
                lw=pt(5), solid_capstyle="round", zorder=3)
        ax.plot(x, b, "o", ms=pt(18), color=col, mec=BG, mew=pt(2),
                zorder=4)
        dx = 0.32 if lado == "der" else -0.32
        # una etiqueta pegada al cero se separa de la línea
        yl = b if abs(b) >= 0.15 else (-0.2 if b < 0 else 0.2)
        ax.text(x + dx, yl, f"{coma(b)}\n{nom}", ha="left" if lado == "der"
                else "right", va="center", fontproperties=fp(22, bold=True),
                color=col, linespacing=1.15, zorder=5)

    for i, (x, t, nom) in enumerate(madre):
        punto(x - (0.4 if i == 3 else 0.0), t, nom, ACC,
              "izq" if i == 3 else "der")
    for x, t, nom in propio:
        punto(x + 0.4, t, nom, NARANJA, "der")

    ax.set_xlim(0, 17.6)
    ax.set_ylim(-0.8, 0.8)
    ticks = [edad[o] for o in (2010, 2012, 2017, 2024)]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{round(edad[o])} {'año' if round(edad[o]) == 1 else 'años'}\n{o}"
                        for o in (2010, 2012, 2017, 2024)])
    for t in ax.get_xticklabels():
        t.set_fontproperties(fp(24))
        t.set_color(INK)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.4))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: coma(v, 1, v != 0)))
    for t in ax.get_yticklabels():
        t.set_fontproperties(fp(22))
        t.set_color(MUTED)
    f.text(0.085, 0.965, "En desv. estándar; arriba, más problemas",
           fontproperties=fp(22), color=MUTED, ha="left", va="top")
    h = [Line2D([], [], marker="o", ls="none", ms=pt(14), color=c, label=n)
         for c, n in ((ACC, "Reporta la madre o el cuidador"),
                      (NARANJA, "Reporta el adolescente"))]
    lg = ax.legend(handles=h, loc="lower right", frameon=False,
                   prop=fp(22), handletextpad=0.3, borderaxespad=0.3)
    for t in lg.get_texts():
        t.set_color(INK)
    p22.guarda(f, "trayectoria.png")


def main():
    p22.log("# Números de la presentación para el advisor "
            "(scripts/27_figuras_advisor.py)")
    perfil()
    trayectoria()
    Path("reports/advisor_numeros.md").write_text(
        "\n".join(p22.OUT) + "\n", encoding="utf-8")
    print("-> reports/advisor_numeros.md")


if __name__ == "__main__":
    main()
