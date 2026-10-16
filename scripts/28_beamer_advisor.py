#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figuras vectoriales de la presentación en LaTeX para el advisor
(presentacion/advisor.tex): fondo blanco, IBM Plex Sans como en las
diapositivas, intervalos al 95% y nada más.

  mapa.pdf         aceleración máxima del suelo por comuna, centro-sur
  hallazgos.pdf    (a) PHQ-4 por edad al terremoto, chicas y chicos;
                   (b) bebés de 6-11 meses, tomaba pecho x zona afectada
  diseno.pdf       (a) intensidad sísmica, balance en variables previas;
                   (b) diseño entre cohortes y su placebo
  trayectoria.pdf  tomaba pecho x zona afectada, de 2010 a 2024
  variables.pdf    los 54 resultados de 2024 por edad al terremoto, frente
                   a los expuestos con dos años (reports/exploratorio_coefs.csv)

Los coeficientes se leen de los informes commiteados (reports/*.md); el
mapa y la edad de los bebés en cada ola usan los datos.

Salida: presentacion/figuras/*.pdf
Uso:    python3 scripts/28_beamer_advisor.py
"""
import importlib.util
import json
import unicodedata
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe                  # noqa: E402
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.collections import PatchCollection   # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D                  # noqa: E402
from matplotlib.patches import Polygon               # noqa: E402
import numpy as np                                   # noqa: E402
import pandas as pd                                  # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "p27", HERE / "27_figuras_advisor.py")
p27 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p27)
lee, edades_bebes, coma = p27.lee, p27.edades_bebes, p27.coma
OUTD = Path("presentacion/figuras")
INK, ACC, MUTED = "#17212B", "#2B5FA8", "#55606B"
GRIS, NARANJA, EJE, GRID = "#8A939B", "#B4561B", "#9AA3AB", "#E6E8EB"
BANDA = "#E8EDF5"
MM = 1 / 25.4
plt.rcParams.update({
    "font.family": "IBM Plex Sans", "font.size": 8,
    "axes.unicode_minus": True, "pdf.fonttype": 42,
    "axes.linewidth": 0.6, "axes.edgecolor": EJE,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelcolor": INK, "ytick.labelcolor": INK,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 0,
    "savefig.facecolor": "white", "figure.facecolor": "white"})
PR = "reports/predicciones_lactancia.md"
RB = "reports/lactancia_robustez.md"
NV = "reports/niveles.md"
PN = "reports/presentacion_numeros.md"


def estrellas(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 \
        else ""


def ejes(ax, eje="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=eje, color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def guarda(f, nombre):
    OUTD.mkdir(parents=True, exist_ok=True)
    f.savefig(OUTD / nombre)
    plt.close(f)
    print(f"-> {OUTD / nombre}")


def ic(ax, x, t, col, marca="o", hueco=False, vertical=True, ms=4.6):
    b, se = t[0], t[1]
    lo, hi = b - 1.96 * se, b + 1.96 * se
    if vertical:
        ax.plot([x, x], [lo, hi], color=col, lw=1.3, zorder=3,
                solid_capstyle="butt")
        ax.plot(x, b, marca, ms=ms, color=col, mfc="white" if hueco else col,
                mew=1.1, zorder=4)
    else:
        ax.plot([lo, hi], [x, x], color=col, lw=1.3, zorder=3,
                solid_capstyle="butt")
        ax.plot(b, x, marca, ms=ms, color=col, mfc="white" if hueco else col,
                mew=1.1, zorder=4)


def titulo(ax, txt):
    ax.set_title(txt, loc="left", fontsize=8.5, fontweight="semibold",
                 color=INK, pad=6)


# --------------------------------- mapa -----------------------------------

def mapa():
    """Zona afectada (las seis regiones con sacudida destructiva; Ñuble era
    parte del Biobío en 2010) frente al resto, centro-sur de Chile."""
    afect = {5, 6, 7, 8, 9, 13, 16}
    feats = json.load(open("data/external/comunas_chile.geojson"))[
        "features"]
    si, no, centros = [], [], {}
    CIUDAD = {13101: "Santiago", 5101: "Valparaíso", 8101: "Concepción",
              9101: "Temuco", 7101: "Talca"}
    for ft in feats:
        cod = int(ft["properties"]["cod_comuna"])
        reg = int(ft["properties"]["codregion"])
        g = ft["geometry"]
        anillos = ([g["coordinates"]] if g["type"] == "Polygon"
                   else g["coordinates"])
        for an in anillos:
            ext = np.asarray(an[0])
            if not (-43 < ext[:, 1].mean() < -28.5
                    and ext[:, 0].mean() > -76):
                continue
            (si if reg in afect else no).append(Polygon(ext, closed=True))
            if cod in CIUDAD and cod not in centros:
                centros[cod] = (ext[:, 0].mean(), ext[:, 1].mean())
    f = plt.figure(figsize=(50 * MM, 68 * MM))
    ax = f.add_axes([0.0, 0.10, 1.0, 0.90])
    ax.add_collection(PatchCollection(no, facecolor="#E4E6E9",
                                      edgecolor="white", lw=0.12,
                                      rasterized=True))
    ax.add_collection(PatchCollection(si, facecolor="#E3A27A",
                                      edgecolor="white", lw=0.12,
                                      rasterized=True))
    halo = [pe.withStroke(linewidth=1.6, foreground="white")]
    epi = (-72.898, -36.122)
    ax.plot(*epi, marker="*", ms=9, color=INK, mec="white", mew=0.5,
            zorder=5)
    ax.annotate("Epicentro", epi, xytext=(-5, 0), textcoords="offset points",
                ha="right", va="center", fontsize=7, color=INK,
                path_effects=halo, zorder=6)
    for cod, xy in centros.items():
        ax.plot(*xy, "o", ms=2.2, color=INK, zorder=5)
        ax.annotate(CIUDAD[cod], xy, xytext=(4, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=7, color=INK,
                    path_effects=halo, zorder=6)
    ax.set_xlim(-75.2, -68.6)
    ax.set_ylim(-41.6, -30.4)
    ax.set_aspect(1 / np.cos(np.radians(36)))
    ax.axis("off")
    h = [matplotlib.patches.Patch(color="#E3A27A", label="Zona afectada"),
         matplotlib.patches.Patch(color="#E4E6E9", label="No afectada")]
    f.legend(handles=h, loc="lower center", ncol=2, frameon=False,
             fontsize=7, handlelength=1.0, handleheight=0.8,
             columnspacing=1.0, handletextpad=0.4, borderaxespad=0.1)
    guarda(f, "mapa.pdf")


# ------------------------------ hallazgos ---------------------------------

def hallazgos():
    f = plt.figure(figsize=(144 * MM, 54 * MM))
    a = f.add_axes([0.085, 0.20, 0.52, 0.66])
    b = f.add_axes([0.70, 0.20, 0.29, 0.66])
    for ax in (a, b):
        ejes(ax)
        ax.axhline(0, color=MUTED, lw=0.7, zorder=2)
    cats = ["6–11 meses", "1 año", "2 años", "3–4 años"]
    xs = np.arange(4)
    for nom, sec, col, hueco, dx in (
            ("Chicas", "## Perfil PHQ-4, Chicas", ACC, False, -0.11),
            ("Chicos", "## Perfil PHQ-4, Chicos", GRIS, True, 0.11)):
        t = [lee(PN, f"- {k}:", sec) for k in ("0-11m", "12-23m")] + \
            [None] + [lee(PN, "- 36-59m:", sec)]
        for x, ti in zip(xs, t):
            if ti is None:
                a.plot(x + dx, 0, "o", ms=4.6, color=col, mfc="white",
                       mew=1.1, zorder=4)
                continue
            ic(a, x + dx, ti, col, hueco=hueco)
            if not hueco:
                a.text(x + dx - 0.07, ti[0], coma(ti[0]) + estrellas(ti[2]),
                       ha="right", va="center", fontsize=7.5, color=col,
                       fontweight="semibold")
    a.set_xticks(xs)
    a.set_xticklabels(cats)
    a.set_xlim(-0.5, 3.5)
    a.set_ylim(-0.3, 0.7)
    a.tick_params(axis="x", length=0)
    a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: coma(v, 1, v != 0)))
    a.set_ylabel("PHQ-4, DE", color=MUTED, fontsize=7.5)
    titulo(a, "(a) Por edad al terremoto, frente a 2 años")
    h = [Line2D([], [], marker="o", ls="none", ms=4.6, color=ACC,
                label="Chicas"),
         Line2D([], [], marker="o", ls="none", ms=4.6, color=GRIS,
                mfc="white", mew=1.1, label="Chicos")]
    a.legend(handles=h, loc="upper right", frameon=False, ncol=2,
             fontsize=7.5, handletextpad=0.2, columnspacing=1.0,
             borderaxespad=0.1)
    # (b) lactancia
    t = [lee(PR, "Referencia, PHQ-4"), lee(RB, "CBCL 2024")]
    for x, ti in zip((0, 1), t):
        ic(b, x, ti, ACC)
        b.text(x + 0.09, ti[0], coma(ti[0]) + estrellas(ti[2]), ha="left",
               va="center", fontsize=7.5, color=ACC, fontweight="semibold")
    b.set_xticks([0, 1])
    b.set_xticklabels(["PHQ-4\nadolescente", "CBCL\ncuidador"])
    b.set_xlim(-0.5, 1.6)
    b.set_ylim(-0.3, 0.7)
    b.tick_params(axis="x", length=0)
    b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: coma(v, 1, v != 0)))
    titulo(b, "(b) Lactancia en bebés")
    guarda(f, "hallazgos.pdf")


# ------------------------------- diseño -----------------------------------

def diseno():
    f = plt.figure(figsize=(144 * MM, 53 * MM))
    a = f.add_axes([0.235, 0.23, 0.215, 0.62])
    b = f.add_axes([0.745, 0.23, 0.245, 0.62])
    for ax in (a, b):
        ejes(ax, eje="x")
        ax.axvline(0, color=MUTED, lw=0.7, zorder=2)
        ax.tick_params(axis="y", length=0)

    def fila(ax, y, t, col):
        ic(ax, y, t, col, vertical=False)
        # la etiqueta nunca cruza la línea del cero
        x = max(t[0] + 1.96 * t[1], 0.0) + 0.03
        ax.text(x, y, coma(t[0]) + estrellas(t[2]),
                ha="left", va="center", fontsize=7.5, color=col,
                fontweight="semibold")

    # (a) intensidad: balance en variables fijadas antes del terremoto
    filas = [("Peso al nacer", "- z_peso:"),
             ("Semanas de gestación", "- z_gest:"),
             ("Escolaridad de la madre", "- z_educ_madre10:"),
             ("Edad de la madre", "- z_edad_madre10:"),
             ("Comuna rural", "- z_rural10:")]
    ys = np.arange(len(filas))[::-1]
    for y, (lab, et) in zip(ys, filas):
        t = lee(NV, et)
        fila(a, y, t, NARANJA if t[2] < 0.05 else ACC)
    a.set_yticks(ys)
    a.set_yticklabels([r[0] for r in filas])
    a.set_xlim(-0.6, 0.55)
    a.set_ylim(-0.6, len(filas) - 0.4)
    a.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: coma(v, 1, v != 0)))
    a.set_xlabel("DE por cada 10 puntos de PGA, % de g", color=MUTED,
                 fontsize=7.5)
    f.text(0.005, 0.955, "(a) Intensidad sísmica dentro de la región",
           fontsize=8.5, fontweight="semibold", color=INK, va="top")
    # (b) concebidos después y placebo entre no expuestos
    s2 = "## 3. Pruebas del diseño"
    s24 = "## 2. Concebidos después como comparación: 2024"
    expu = [("Vocabulario, 2024", lee(NV, "- z_tvip, efecto total:", s24)),
            ("Talla, 2017", lee(NV, "- talla (z por edad y sexo):", s2)),
            ("Función ejecutiva, 2017",
             lee(NV, "- Hearts & Flowers, condición mixta", s2))]
    plac = [("Vocabulario", lee(NV, "- vocabulario, TVIP (z):", s2)),
            ("Talla", lee(NV, "- talla (z):", s2)),
            ("Función ejecutiva", lee(NV, "- Hearts & Flowers (z):", s2))]
    ys = [7, 6, 5, 3, 2, 1]
    for y, (lab, t), col in zip(ys, expu + plac, [ACC] * 3 + [NARANJA] * 3):
        fila(b, y, t, col)
    b.set_yticks(ys + [8, 4])
    b.set_yticklabels([r[0] for r in expu + plac]
                      + ["Expuestos frente a después", "Placebo sin terremoto"])
    for tl in b.get_yticklabels()[-2:]:
        tl.set_fontweight("semibold")
    b.get_yticklabels()[-2].set_color(ACC)
    b.get_yticklabels()[-1].set_color(NARANJA)
    b.set_xlim(-0.5, 0.78)
    b.set_ylim(0.4, 8.6)
    b.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: coma(v, 1, v != 0)))
    b.set_xlabel("DE", color=MUTED, fontsize=7.5)
    f.text(0.505, 0.955, "(b) Diseño entre cohortes", fontsize=8.5,
           fontweight="semibold", color=INK, va="top")
    guarda(f, "diseno.pdf")


# ----------------------------- trayectoria --------------------------------

def trayectoria():
    edad = edades_bebes()
    madre = [(0.0, lee(PR, "ASQ:SE 12 meses"), "ASQ:SE"),
             (1.0, lee(RB, "CBCL total 2012"), "CBCL"),
             (2.0, lee(RB, "CBCL 2017"), "CBCL"),
             (2.88, lee(RB, "CBCL 2024"), "CBCL")]
    propio = (3.12, lee(PR, "Referencia, PHQ-4"), "PHQ-4")
    f = plt.figure(figsize=(70 * MM, 57 * MM))
    ax = f.add_axes([0.2, 0.2, 0.79, 0.76])
    ejes(ax)
    ax.axvspan(-0.5, 0.5, color=BANDA, lw=0, zorder=1)
    ax.text(-0.44, 0.72, "Donde la\nmedicina\npredice\nel efecto",
            fontsize=6.8, color=MUTED, ha="left", va="top",
            linespacing=1.2, zorder=2)
    ax.axhline(0, color=MUTED, lw=0.7, zorder=2)
    for i, (x, t, nom) in enumerate(madre):
        ic(ax, x, t, ACC)
        izq = i >= 2
        yl = t[0] if abs(t[0]) >= 0.15 else (-0.2 if t[0] < 0 else 0.2)
        ax.text(x + (-0.07 if izq else 0.07), yl,
                f"{coma(t[0])}{estrellas(t[2])}\n{nom}",
                ha="right" if izq else "left", va="center", fontsize=7,
                color=ACC, fontweight="semibold", linespacing=1.1)
    x, t, nom = propio
    ic(ax, x, t, NARANJA, marca="D", ms=4.2)
    ax.text(x + 0.07, t[0], f"{coma(t[0])}{estrellas(t[2])}\n{nom}",
            ha="left", va="center", fontsize=7, color=NARANJA,
            fontweight="semibold", linespacing=1.1)
    olas = (2010, 2012, 2017, 2024)
    ax.set_xticks(range(4))
    ax.set_xticklabels([f"{round(edad[o])} {'año' if round(edad[o]) == 1 else 'años'}\n{o}"
                        for o in olas])
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.5, 3.98)
    ax.set_ylim(-0.75, 0.75)
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.25))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: coma(v, 2, v != 0) if v else "0"))
    ax.set_ylabel("DE; arriba, más problemas", color=MUTED, fontsize=7.5)
    h = [Line2D([], [], marker="o", ls="none", ms=4.6, color=ACC,
                label="Reporta la madre o el cuidador"),
         Line2D([], [], marker="D", ls="none", ms=4.2, color=NARANJA,
                label="Reporta el adolescente")]
    ax.legend(handles=h, loc="lower right", frameon=False, fontsize=7,
              handletextpad=0.3, borderaxespad=0.2)
    guarda(f, "trayectoria.pdf")


CORTO = {
    "z_phq4": "Síntomas PHQ-4", "gad2_bin": "Ansiedad, GAD-2",
    "phq2_bin": "Depresión, PHQ-2", "cbcl_int": "CBCL internalizante",
    "cbcl_ext": "CBCL externalizante", "cbcl_aten": "CBCL atención",
    "z_resil": "Resiliencia", "sat_vida": "Satisfacción con la vida",
    "sat_familia": "Satisf. con la familia",
    "sat_amigos": "Satisf. con los amigos",
    "sat_colegio": "Satisf. con el colegio",
    "sat_si_mismo": "Satisf. consigo mismo",
    "sat_barrio": "Satisf. con el barrio",
    "sat_cuerpo": "Satisf. con su cuerpo",
    "z_salud": "Mala salud percibida", "tvip": "Vocabulario, TVIP",
    "asiste": "Asiste al colegio", "nota": "Promedio de notas",
    "le_va": "Le va bien en el colegio", "gusta": "Le gusta ir al colegio",
    "profes": "Le agradan los profesores", "univ": "Espera la universidad",
    "no_sabe": "No sabe cuánto estudiará",
    "z_bull": "Victimización en el curso", "ciber_any": "Ciberacoso",
    "viol_pareja": "Violencia en el pololeo", "fuma": "Tabaco",
    "alcohol": "Alcohol", "cannabis": "Marihuana",
    "otras_drogas": "Otras drogas", "sin_anticonc": "Sin anticonceptivo",
    "sueno": "Horas de sueño", "celular_noche": "Celular en la cama",
    "redes": "Redes sociales", "deporte": "Actividad física",
    "lectura": "Lectura", "chatarra": "Comida chatarra", "fruta": "Fruta",
    "supervision": "La familia sabe qué hace",
    "relacion_cuid": "Relación con el cuidador",
    "confia_nadie": "No confía en nadie",
    "tiempo_familia": "Actividades en familia",
    "participa": "Participa en grupos", "aces": "Experiencias adversas",
    "aces_peleas": "Peleas en el hogar",
    "aces_separacion": "Separación del cuidador",
    "aces_vivienda": "Problemas de vivienda", "aces_hambre": "Pasó hambre",
    "cesd": "Depresión del cuidador", "psi_total": "Estrés parental",
    "psi_malestar": "Malestar parental",
    "psi_interaccion": "Interacción disfuncional",
    "pscs": "Competencia parental", "log_ingreso": "Ingreso per cápita"}
DOMINIO = {
    "Mental health": "Salud mental", "Well-being": "Bienestar",
    "Peers and victimization": "Pares",
    "Cognition and school": "Colegio", "Risk behaviors": "Conductas de riesgo",
    "Daily life": "Vida diaria", "Family and social life": "Familia",
    "Adverse experiences reported by the caregiver":
        "Adversidad, reporta el cuidador",
    "Caregiver and household": "Cuidador y hogar"}


def variables():
    """Mapa de calor de los 54 resultados en tres columnas: estadístico t
    orientado (positivo = peor) de cada edad frente a los expuestos con dos
    años, zona afectada menos no afectada."""
    c = pd.read_csv("reports/exploratorio_coefs.csv")
    c = c[c.ref == "24-35m"]
    cmap = LinearSegmentedColormap.from_list("dano",
                                             [ACC, "#F2F1EE", NARANJA])
    columnas = [["Mental health", "Well-being", "Peers and victimization"],
                ["Cognition and school", "Risk behaviors", "Daily life"],
                ["Family and social life",
                 "Adverse experiences reported by the caregiver",
                 "Caregiver and household"]]
    edades = [("0-11m", "Bebés"), ("12-23m", "1 año"), ("36-59m", "3–4")]
    nfil = max(sum(1 + c[c.dominio == dm]["var"].nunique() for dm in col)
               for col in columnas)
    W, H = 144 * MM, 58 * MM
    f = plt.figure(figsize=(W, H))
    lab_w, celda, sep = 25.5, 6.6, 2.0          # mm
    ancho = lab_w + 3 * celda
    for i, col in enumerate(columnas):
        x0 = i * (ancho + sep)
        ax = f.add_axes([x0 * MM / W, 0.12, ancho * MM / W, 0.88])
        ax.set_xlim(0, ancho)
        ax.set_ylim(nfil - 0.4, -1.3)
        ax.axis("off")
        for j, (_, e) in enumerate(edades):
            ax.text(lab_w + celda * (j + 0.5), -0.75, e, ha="center",
                    va="center", fontsize=6, color=MUTED)
        y = 0
        for dm in col:
            ax.text(0, y, DOMINIO[dm], ha="left", va="center", fontsize=6.3,
                    fontweight="semibold", color=INK)
            y += 1
            sub = c[c.dominio == dm]
            for v in dict.fromkeys(sub["var"]):
                ax.text(0.8, y, CORTO[v], ha="left", va="center",
                        fontsize=5.8, color=INK)
                for j, (k, _) in enumerate(edades):
                    r = sub[(sub["var"] == v) & (sub.edad == k)].iloc[0]
                    t = float(np.clip(r.sgn * r.b / r.se, -3, 3))
                    color = cmap((t + 3) / 6)
                    ax.add_patch(matplotlib.patches.Rectangle(
                        (lab_w + celda * j + 0.3, y - 0.44), celda - 0.6,
                        0.88, color=color, lw=0))
                    st = estrellas(r.p)
                    if st:
                        lum = (0.299 * color[0] + 0.587 * color[1]
                               + 0.114 * color[2])
                        ax.text(lab_w + celda * (j + 0.5), y + 0.08, st,
                                ha="center", va="center", fontsize=5.5,
                                color="white" if lum < 0.5 else INK)
                y += 1
    cax = f.add_axes([0.38, 0.04, 0.24, 0.024])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-3, 3))
    cb = f.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.set_ticks([-3, 0, 3])
    cb.ax.tick_params(labelsize=5.5, length=0, pad=1)
    cb.ax.set_xticklabels(["−3", "0", "3"])
    f.text(0.37, 0.052, "Mejor", ha="right", va="center", fontsize=6,
           color=MUTED)
    f.text(0.63, 0.052, "Peor", ha="left", va="center", fontsize=6,
           color=MUTED)
    guarda(f, "variables.pdf")


def main():
    mapa()
    hallazgos()
    diseno()
    trayectoria()
    variables()


if __name__ == "__main__":
    main()
