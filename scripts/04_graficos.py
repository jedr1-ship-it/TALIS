#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera los gráficos de apoyo del panel ELPI (reports/figures/*.png):

  01_muestra_atricion.png   composición de la muestra por ronda + retención
  02_rdd_corte_escolar.png  curso 2017 por mes de nacimiento (corte 31 de marzo)
  03_persistencia_tvip.png  TVIP estándar 2017 vs 2024, mismo niño (binscatter)
  04_linea_tiempo.png       cohorte x políticas/shocks (mapa de diseños causales)

Insumos: data/interim/ (script 02) y data/processed/ (script 03).
Uso:  python3 scripts/04_graficos.py
"""
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat

warnings.simplefilter("ignore")

FIG = Path("reports/figures")
FIG.mkdir(parents=True, exist_ok=True)

# Paleta validada (referencia dataviz, modo claro)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASE = "#c3c2b7"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"  # azul, naranjo, aqua

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.size": 10,
    "text.color": INK, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": False,
})


def estilo(ax, ygrid=True):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(BASE)
    if ygrid:
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    ax.tick_params(length=0)


def fuente(fig, extra=""):
    fig.text(0.01, 0.01, ("Fuente: ELPI (Ministerio de Desarrollo Social y "
                          "Familia), elaboración propia. " + extra).strip(),
             fontsize=7.5, color=MUTED)


# ---------------------------------------------------------------- G1
def g1_muestra():
    ancho = pd.read_csv("data/processed/elpi_panel_ninos_ancho.csv")
    rondas = [2010, 2012, 2017, 2024]
    coh, r12, r17 = [], [], []
    for r in rondas:
        en = ancho[ancho[f"en_{r}"] == 1]
        coh.append(int((en.muestra_origen == "original_2010").sum()))
        r12.append(int((en.muestra_origen == "refresco_2012").sum()))
        r17.append(int((en.muestra_origen == "refresco_2017").sum()))

    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    x = np.arange(4)
    kw = dict(width=0.56, edgecolor=SURFACE, linewidth=2)
    b1 = ax.bar(x, coh, color=S1, label="Cohorte original 2010", **kw)
    b2 = ax.bar(x, r12, bottom=coh, color=S2, label="Refresco 2012", **kw)
    b3 = ax.bar(x, r17, bottom=np.array(coh) + np.array(r12), color=S3,
                label="Refresco 2017", **kw)
    for xi, v in zip(x, coh):
        ax.text(xi, v / 2, f"{v:,}".replace(",", "."), ha="center",
                va="center", color="white", fontsize=9)
    for xi, base_, v in zip(x, coh, r12):
        if v:
            ax.text(xi, base_ + v / 2, f"{v:,}".replace(",", "."),
                    ha="center", va="center", color="white", fontsize=9)
    for xi, base_, v in zip(x, np.array(coh) + np.array(r12), r17):
        if v:
            ax.text(xi, base_ + v / 2, f"{v:,}".replace(",", "."),
                    ha="center", va="center", color=INK, fontsize=9)
    tot = np.array(coh) + np.array(r12) + np.array(r17)
    for xi, t in zip(x, tot):
        ax.text(xi, t + 320, f"{t:,}".replace(",", "."), ha="center",
                color=INK2, fontsize=9)

    ax.set_xticks(x, [str(r) for r in rondas])
    ax.set_ylim(0, 19500)
    ax.set_ylabel("Niños/as con encuesta al hogar")
    ax.set_title("Muestra ELPI por ronda: la cohorte 2010 y los refrescos",
                 loc="left", fontsize=12, color=INK, pad=30)
    ax.text(0, 1.02, "La 4ª ronda volvió solo a la cohorte original: "
            "15.175 → 12.898 → 10.230 → 10.003 (atrición 34,1%)",
            transform=ax.transAxes, fontsize=9, color=INK2)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    estilo(ax)
    fuente(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "01_muestra_atricion.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- G2
def g2_rdd():
    e17, _ = pyreadstat.read_dta(
        "data/interim/2017/Base Evaluaciones ELPI III.dta",
        usecols=["folio", "nivel_edu_niño", "curso_edu_niño", "finicio_tn"])
    e24, _ = pyreadstat.read_dta(
        "data/interim/2024/Base evaluaciones Stata.dta",
        usecols=["folio", "fecha_nac"])
    fn = e24.fecha_nac.astype(str).str.extract(r"(?P<m>\d+)/(?P<a>\d+)")
    e24["ym"] = fn.a.astype(float) * 12 + fn.m.astype(float) - 1
    df = e17.merge(e24[["folio", "ym"]], on="folio", how="inner")

    # fecha de evaluación (días Stata desde 1960) -> restringir al año
    # escolar 2018 (marzo-julio 2018), para que el curso sea comparable
    dias = pd.to_numeric(df.finicio_tn, errors="coerce")
    fecha = pd.Timestamp("1960-01-01") + pd.to_timedelta(dias, unit="D")
    df = df[(fecha >= "2018-03-01") & (fecha <= "2018-07-31")]
    # curso alcanzado: básica = curso; pre-básica = 0; se excluye ed. especial
    df = df[df["nivel_edu_niño"].isin([0, 1, 2, 4])].copy()
    df["grado"] = np.where(df["nivel_edu_niño"] == 4, df["curso_edu_niño"], 0)
    g = df.groupby("ym").grado.agg(["mean", "size"]).reset_index()
    g = g[g["size"] >= 30]

    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    cortes = [a * 12 + 3 for a in (2006, 2007, 2008, 2009)]  # 1 de abril
    for c in cortes:
        ax.axvline(c - 0.5, color=BASE, linewidth=1, linestyle=(0, (4, 3)))
    ax.plot(g.ym, g["mean"], color=S1, linewidth=2)
    ax.scatter(g.ym, g["mean"], s=14, color=S1, zorder=3)
    ax.text(cortes[0] - 0.5, ax.get_ylim()[1], "", fontsize=8)

    ticks = [a * 12 + m - 1 for a in range(2006, 2010) for m in (1, 7)]
    ax.set_xticks(ticks, [f"{'ene' if m == 1 else 'jul'}-{a}"
                          for a in range(2006, 2010) for m in (1, 7)])
    ax.set_ylabel("Curso promedio en 2018 (0 = pre-básica)")
    ax.set_xlabel("Mes de nacimiento")
    ax.set_title("Nacer después del 31 de marzo desplaza toda la carrera "
                 "escolar", loc="left", fontsize=12, color=INK, pad=30)
    ax.text(0, 1.02, "Curso alcanzado (año escolar 2018) por mes de "
            "nacimiento; líneas: cortes de abril. n="
            f"{len(df):,}".replace(",", "."),
            transform=ax.transAxes, fontsize=9, color=INK2)
    ax.text(cortes[0] + 0.4, g["mean"].max() - 0.05,
            "cortes del 1 de abril", fontsize=8.5, color=INK2)
    estilo(ax)
    fuente(fig, "Curso 2017/2018 (ELPI III) por fecha de nacimiento (ELPI 2024).")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "02_rdd_corte_escolar.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- G3
def g3_tvip():
    e17, _ = pyreadstat.read_dta(
        "data/interim/2017/Base Evaluaciones ELPI III.dta",
        usecols=["folio", "tvip_ps"])
    e24, _ = pyreadstat.read_dta(
        "data/interim/2024/Base evaluaciones Stata.dta",
        usecols=["folio", "tvip_pst_hispano"])
    df = e17.merge(e24, on="folio").dropna()
    df.columns = ["folio", "t17", "t24"]

    # binscatter: 25 bins de igual tamaño sobre el puntaje 2017
    df["bin"] = pd.qcut(df.t17, 25, duplicates="drop")
    b = df.groupby("bin", observed=True)[["t17", "t24"]].mean()
    slope = np.polyfit(df.t17, df.t24, 1)[0]
    r = df.t17.corr(df.t24)

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    lo, hi = 60, 135
    ax.plot([lo, hi], [lo, hi], color=BASE, linewidth=1,
            linestyle=(0, (4, 3)))
    ax.text(hi - 1, hi - 4.5, "45°", fontsize=8.5, color=MUTED, ha="right")
    ax.scatter(b.t17, b.t24, s=34, color=S1, zorder=3)
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("TVIP estándar 2017 (7-11 años)")
    ax.set_ylabel("TVIP estándar 2024 (14-18 años)")
    ax.set_title("El vocabulario persiste de la niñez a la adolescencia",
                 loc="left", fontsize=12, color=INK, pad=30)
    ax.text(0, 1.02, "Medias por ventil del puntaje 2017; mismo niño/a, "
            f"n={len(df):,}".replace(",", ".")
            + f"; pendiente {slope:.2f}, r={r:.2f}".replace(".", ","),
            transform=ax.transAxes, fontsize=9, color=INK2)
    estilo(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    fuente(fig, "Puntajes estándar TVIP (normas hispanas).")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "03_persistencia_tvip.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- G4
def g4_timeline():
    fig, ax = plt.subplots(figsize=(10.2, 4.4))
    filas = {"Rondas ELPI": 3, "Políticas": 2, "Shocks": 1}

    def span(y, x0, x1, color, etiqueta, arriba=True, alpha=1.0):
        ax.barh(y, x1 - x0, left=x0, height=0.34, color=color, alpha=alpha,
                edgecolor=SURFACE, linewidth=1.5)
        ax.annotate(etiqueta, ((x0 + x1) / 2, y + (0.34 if arriba else -0.34)),
                    ha="center", va="bottom" if arriba else "top",
                    fontsize=8.5, color=INK2)

    def marca(y, x, color, etiqueta, arriba=True):
        ax.scatter([x], [y], s=52, color=color, zorder=3,
                   edgecolor=SURFACE, linewidth=1.5)
        ax.annotate(etiqueta, (x, y + (0.30 if arriba else -0.30)),
                    ha="center", va="bottom" if arriba else "top",
                    fontsize=8.5, color=INK2)

    # nacimiento de la cohorte (fondo)
    ax.axvspan(2006, 2009 + 8 / 12, color=S1, alpha=0.07)
    ax.text(2006.05, 3.62, "nacimiento de la cohorte\n(ene-2006 a ago-2009)",
            fontsize=8.5, color=INK2, va="top")

    # rondas
    marca(filas["Rondas ELPI"], 2010.5, S1, "R1 · 0-4 años")
    marca(filas["Rondas ELPI"], 2012.5, S1, "R2 · 2-6")
    span(filas["Rondas ELPI"], 2017 + 10 / 12, 2018.6, S1, "R3 · 8-12")
    span(filas["Rondas ELPI"], 2024 + 4 / 12, 2024 + 10 / 12, S1, "R4 · 14-18")

    # políticas
    span(filas["Políticas"], 2007, 2008.9, S3, "Chile Crece Contigo\n(despliegue comunal)", arriba=False)
    marca(filas["Políticas"], 2011.8, S3, "posnatal parental\n12→24 semanas", arriba=True)

    # shocks
    marca(filas["Shocks"], 2010.15, S2, "terremoto 27F", arriba=False)
    span(filas["Shocks"], 2020.2, 2021.9, S2, "cierres escolares COVID", arriba=False)

    ax.set_yticks(list(filas.values()), list(filas.keys()))
    ax.set_xlim(2005.7, 2025.5)
    ax.set_ylim(0.3, 3.9)
    ax.set_xticks(range(2006, 2026, 2))
    ax.tick_params(axis="y", colors=INK2)
    ax.set_title("Una cohorte, cuatro experimentos naturales",
                 loc="left", fontsize=12, color=INK, pad=30)
    ax.text(0, 1.02, "Cada política o shock corta a la cohorte 2006-2009 a "
            "edades distintas: la base de los diseños causales (docs/disenos_jmp.md)",
            transform=ax.transAxes, fontsize=9, color=INK2)
    estilo(ax, ygrid=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    fuente(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "04_linea_tiempo.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    g1_muestra()
    g2_rdd()
    g3_tvip()
    g4_timeline()
    print("Gráficos escritos en", FIG)
