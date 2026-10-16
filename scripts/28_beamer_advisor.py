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
  salud_mental.pdf (a) PHQ-4 y CBCL internalizante, todos; (b) PHQ-4 por
                   sexo; frente a los expuestos con dos años
  resto.pdf        los otros resultados (sin comida chatarra ni fruta), frente
                   a los expuestos con dos años, con recuadro en los que
                   podrían explicar la salud mental
  lactancia.pdf    primera etapa del destete y mediación en PHQ-4
                   (reports/lactancia_mediacion.md)
  indices.pdf      perfil por edad de los cuatro índices y brecha en PHQ-4
                   sin y con ellos (reports/indices_mediacion.md)
  descomposicion.pdf  la brecha en PHQ-4 partida en hogar, colegio y sin
                   explicar (reports/descomposicion.csv)
  orden_temporal.pdf  colegio y peleas en el hogar, mismas preguntas en 2017
                   y 2024 (reports/orden_temporal.csv)
  ventanas.pdf     PHQ-4 de las chicas en tramos de seis meses de edad al
                   terremoto, con las dos ventanas (reports/ventanas.csv)
  hogar_2017.pdf   colegio y peleas en el hogar en 2017, a los 8-12 años

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


# estilo de los gráficos de resultados: el de una figura de paper de
# economía (serif, barras de error con remate, leyenda arriba, sin grilla)
AZUL, MARRON, GRISR = "#3D6AA2", "#B5652E", "#7F7F7F"
PAPER = {"font.family": "STIXGeneral", "mathtext.fontset": "stix",
         "font.size": 8, "axes.linewidth": 0.8, "axes.edgecolor": "black",
         "xtick.color": "black", "ytick.color": "black",
         "xtick.labelcolor": "black", "ytick.labelcolor": "black",
         "ytick.direction": "out", "ytick.major.size": 3,
         "ytick.major.width": 0.8, "xtick.major.size": 0}


def ejes_paper(ax):
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.axhline(0, color="#9A9A9A", lw=0.7, ls="--", zorder=1)


def barra(ax, x, t, col, marca, hueco=False, escala=1.0):
    b, se = t[0] * escala, t[1] * escala
    return ax.errorbar(x, b, yerr=1.96 * se, fmt=marca, color=col,
                       mfc="white" if hueco else col, mec=col, mew=1.0,
                       ms=5.5 if marca != "^" else 6.0, capsize=2.6,
                       elinewidth=1.0, capthick=1.0, zorder=3)


def miles(n):
    return f"{n:,}".replace(",", ".")


def frente_a_dos(v, k):
    c = pd.read_csv("reports/exploratorio_coefs.csv")
    r = c[(c.ref == "24-35m") & (c["var"] == v) & (c.edad == k)].iloc[0]
    return (float(r.b), float(r.se), float(r.p))


def salud_mental():
    """Efecto sobre la salud mental: PHQ-4 por edad al terremoto frente a
    quienes tenían dos años, en tres paneles: todos, chicas y chicos."""
    claves = ["0-11m", "12-23m", "36-59m"]
    paneles = [
        (f"Todos (n = {miles(9996)})", AZUL, "o", False,
         [frente_a_dos("z_phq4", k) for k in claves]),
        (f"Chicas (n = {miles(4961)})", MARRON, "^", False,
         [lee(PN, f"- {k}:", "## Perfil PHQ-4, Chicas") for k in claves]),
        (f"Chicos (n = {miles(5035)})", GRISR, "o", True,
         [lee(PN, f"- {k}:", "## Perfil PHQ-4, Chicos") for k in claves])]
    with plt.rc_context(PAPER):
        f = plt.figure(figsize=(144 * MM, 58 * MM))
        ancho, sep, x0 = 0.26, 0.04, 0.135
        for i, (nom, col, marca, hueco, pts) in enumerate(paneles):
            ax = f.add_axes([x0 + i * (ancho + sep), 0.24, ancho, 0.63])
            ejes_paper(ax)
            for x, t in enumerate(pts):
                barra(ax, x, t, col, marca, hueco)
            ax.set_xticks(range(3))
            ax.set_xticklabels(["6–11\nmeses", "1\naño", "3–4\naños"],
                               fontsize=8)
            ax.set_xlim(-0.5, 2.5)
            ax.set_ylim(-0.3, 0.62)
            ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2))
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
                lambda v, _: coma(v, 1, False) if v >= 0 else coma(v, 1)))
            if i == 0:
                ax.set_ylabel("Diferencia con quienes\ntenían 2 años (DE)",
                              fontsize=8.5)
            else:
                ax.set_yticklabels([])
            ax.set_title(nom, fontsize=9, pad=6)
        f.text(x0 + 1.5 * ancho + sep, 0.0, "Edad al terremoto",
               ha="center", va="bottom", fontsize=8.5)
        guarda(f, "salud_mental.pdf")


FUERA = {"chatarra", "fruta"}
# diferencias con p < 0,10 que podrían explicar la salud mental: el hogar y
# el colegio (las de bienestar son otra cara del mismo resultado, y las que
# favorecen a los otros grupos no la explican)
RECUADRO = {"le_va", "profes", "relacion_cuid", "aces", "aces_peleas",
            "aces_vivienda"}


def resto():
    """Los 48 resultados fuera de la salud mental: estadístico t orientado de
    cada edad frente a los expuestos con dos años."""
    c = pd.read_csv("reports/exploratorio_coefs.csv")
    c = c[(c.ref == "24-35m") & ~c["var"].isin(FUERA)]
    cmap = LinearSegmentedColormap.from_list("dano",
                                             [ACC, "#F2F1EE", NARANJA])
    columnas = [["Well-being", "Peers and victimization", "Risk behaviors"],
                ["Cognition and school", "Daily life"],
                ["Family and social life",
                 "Adverse experiences reported by the caregiver",
                 "Caregiver and household"]]
    edades = [("0-11m", "Bebés"), ("12-23m", "1 año"), ("36-59m", "3–4")]
    nfil = max(sum(1 + c[c.dominio == dm]["var"].nunique() for dm in col)
               for col in columnas)
    W, H = 144 * MM, 59 * MM
    ctx = plt.rc_context(PAPER)
    ctx.__enter__()
    f = plt.figure(figsize=(W, H))
    lab_w, celda, sep = 28.0, 6.1, 1.4          # mm
    ancho = lab_w + 3 * celda
    for i, col in enumerate(columnas):
        x0 = i * (ancho + sep)
        ax = f.add_axes([x0 * MM / W, 0.13, ancho * MM / W, 0.87])
        ax.set_xlim(0, ancho)
        ax.set_ylim(nfil - 0.4, -1.3)
        ax.axis("off")
        for j, (_, e) in enumerate(edades):
            ax.text(lab_w + celda * (j + 0.5), -0.75, e, ha="center",
                    va="center", fontsize=5.6, color=MUTED)
        y = 0
        for dm in col:
            y0 = y
            ax.text(0, y, DOMINIO[dm], ha="left", va="center", fontsize=6.6,
                    fontweight="semibold", color=INK)
            y += 1
            sub = c[c.dominio == dm]
            if dm == "Well-being":
                filas_dm = sub["var"].nunique()
                ax.add_patch(matplotlib.patches.Rectangle(
                    (0.05, y0 - 0.5), ancho - 0.05, filas_dm + 1.0,
                    fill=False, ec=AZUL, lw=0.8, ls="--", zorder=6))
            for v in dict.fromkeys(sub["var"]):
                if v in RECUADRO:
                    ax.add_patch(matplotlib.patches.Rectangle(
                        (0.15, y - 0.5), ancho - 0.15, 1.0, fill=False,
                        ec=INK, lw=0.8, zorder=6))
                ax.text(0.8, y, CORTO[v], ha="left", va="center",
                        fontsize=6.3, color=INK)
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
                                ha="center", va="center", fontsize=5.8,
                                color="white" if lum < 0.5 else INK)
                y += 1
    f.text(0.005, 0.057, "Mejor", ha="left", va="center", fontsize=6.5,
           color=MUTED)
    cax = f.add_axes([0.05, 0.045, 0.16, 0.024])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-3, 3))
    cb = f.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.set_ticks([])
    f.text(0.218, 0.057, "Peor que quienes tenían 2 años", ha="left",
           va="center", fontsize=6.5, color=MUTED)
    f.patches.append(matplotlib.patches.Rectangle(
        (0.47, 0.044), 0.018, 0.026, fill=False, ec=INK, lw=0.8,
        transform=f.transFigure, figure=f))
    f.text(0.494, 0.057, "Podría explicar la salud mental",
           ha="left", va="center", fontsize=6.5, color=MUTED)
    f.patches.append(matplotlib.patches.Rectangle(
        (0.745, 0.044), 0.018, 0.026, fill=False, ec=AZUL, lw=0.8, ls="--",
        transform=f.transFigure, figure=f))
    f.text(0.769, 0.057, "Salud mental y bienestar", ha="left",
           va="center", fontsize=6.5, color=MUTED)
    guarda(f, "resto.pdf")
    ctx.__exit__(None, None, None)


def lactancia():
    """(a) ¿Hizo el terremoto dejar el pecho antes?, con la comparación de
    los cuatro meses previos; (b) ¿explica eso la salud mental?: brecha de
    los que tomaban pecho y destetados frente a los que siguieron. Bebés de
    6-11 meses y niños de 12-18 meses (reports/lactancia_mediacion.md)."""
    LM = "reports/lactancia_mediacion.md"
    grupos = [("6-11", "Bebés de\n6 a 11 meses"),
              ("12-18", "Niños de\n12 a 18 meses")]
    with plt.rc_context(PAPER):
        f = plt.figure(figsize=(144 * MM, 60 * MM))
        a = f.add_axes([0.125, 0.2, 0.33, 0.52])
        b = f.add_axes([0.615, 0.2, 0.37, 0.52])
        for ax in (a, b):
            ejes_paper(ax)
        # (a) primera etapa
        for x, (g, _) in enumerate(grupos):
            h1 = barra(a, x - 0.12, lee(LM, f"{g} meses, destete en los 3"),
                       AZUL, "o", escala=100)
            h2 = barra(a, x + 0.12, lee(LM, f"{g} meses, destete en los 4"),
                       GRISR, "o", hueco=True, escala=100)
        a.set_xticks(range(2))
        a.set_xticklabels([g[1] for g in grupos], fontsize=8)
        a.set_xlim(-0.5, 1.5)
        a.set_ylim(-12, 18)
        a.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
        a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: coma(v, 0, False) if v >= 0 else coma(v, 0)))
        a.set_ylabel("Dejaron más el pecho en la\nzona afectada (puntos) →",
                     fontsize=8)
        a.set_title("(a) ¿El terremoto hizo dejar el pecho antes?",
                    loc="left", fontsize=8.5, pad=30)
        a.legend([h1, h2], ["En los 3 meses después del 27-F",
                            "En los 4 meses antes, comparación"],
                 loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1,
                 frameon=False, fontsize=6.8, handletextpad=0.3,
                 columnspacing=0.8, borderaxespad=0.2)
        # (b) salud mental
        brecha = {"6-11": lee(LM, "PHQ-4, zona afectada x tomaba pecho"),
                  "12-18": lee(LM, "12-18 meses, PHQ-4, zona afectada x")}
        destete = {"6-11": lee(LM, "PHQ-4, destetados en los 3 meses"),
                   "12-18": lee(LM, "12-18 meses, PHQ-4, destetados")}
        for x, (g, _) in enumerate(grupos):
            h3 = barra(b, x - 0.12, brecha[g], AZUL, "s")
            h4 = barra(b, x + 0.12, destete[g], MARRON, "^")
        b.set_xticks(range(2))
        b.set_xticklabels([g[1] for g in grupos], fontsize=8)
        b.set_xlim(-0.5, 1.5)
        b.set_ylim(-0.4, 0.7)
        b.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2))
        b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: coma(v, 1, False) if v >= 0 else coma(v, 1)))
        b.set_ylabel("Más síntomas a los 15 (DE) →", fontsize=8)
        b.set_title("(b) ¿Explica eso la salud mental?", loc="left",
                    fontsize=8.5, pad=30)
        b.legend([h3, h4], ["Tomaban pecho el 27-F, brecha",
                            "Dejaron el pecho frente a siguieron"],
                 loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1,
                 frameon=False, fontsize=6.8, handletextpad=0.3,
                 columnspacing=0.8, borderaxespad=0.2)
        guarda(f, "lactancia.pdf")


def indices_fig():
    """(a) Perfil por edad de los cuatro índices frente a los expuestos con
    dos años; (b) brecha en PHQ-4 sin y con los índices, misma muestra
    (reports/indices_mediacion.md, todos)."""
    import re
    IM = Path("reports/indices_mediacion.md").read_text(encoding="utf-8")

    def tramo(prefijo):
        linea = next(l for l in IM.splitlines() if l.startswith(prefijo))
        out = {}
        for k, lab in (("0-11m", "bebés"), ("12-23m", "1 año"),
                       ("36-59m", "3-4 años")):
            m = re.search(re.escape(lab) + r" ([+-]\d+\.\d+)\**\s+\(ee "
                          r"(\d+\.\d+), p=(\d+\.\d+)\)", linea)
            out[k] = tuple(float(g) for g in m.groups())
        return out
    claves = ["0-11m", "12-23m", "36-59m"]
    etiquetas = ["Bebés", "1 año", "3–4 años"]
    series = [("Adversidad, cuidador", AZUL, "o", False,
               tramo("- todos, adversidad:")),
              ("Familia", MARRON, "^", False, tramo("- todos, familia:")),
              ("Colegio", GRISR, "o", True, tramo("- todos, colegio:")),
              ("Economía", AZUL, "s", True, tramo("- todos, economia:"))]
    sin, con = tramo("- sin índices:"), tramo("- con los cuatro:")
    with plt.rc_context(PAPER):
        f = plt.figure(figsize=(144 * MM, 60 * MM))
        a = f.add_axes([0.115, 0.16, 0.385, 0.5])
        b = f.add_axes([0.62, 0.16, 0.365, 0.5])
        for ax in (a, b):
            ejes_paper(ax)
        dx = [-0.24, -0.08, 0.08, 0.24]
        hs = []
        for (nom, col, marca, hueco, t), d_ in zip(series, dx):
            for x, k in enumerate(claves):
                h = barra(a, x + d_, t[k], col, marca, hueco)
            hs.append(h)
        a.set_xticks(range(3))
        a.set_xticklabels(etiquetas, fontsize=8)
        a.set_xlim(-0.5, 2.5)
        a.set_ylim(-0.25, 0.42)
        a.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.1))
        a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: coma(v, 1, False) if v >= 0 else coma(v, 1)))
        a.set_ylabel("Peor que quienes tenían\n2 años (DE) →", fontsize=8)
        a.set_title("(a) ¿Qué cambia con la edad al terremoto?", loc="left",
                    fontsize=8.5, pad=36)
        a.legend(hs, [s_[0] for s_ in series], loc="lower left",
                 bbox_to_anchor=(0.0, 1.0), ncol=2, frameon=False,
                 fontsize=6.8, handletextpad=0.2, columnspacing=0.8,
                 borderaxespad=0.2)
        h1 = h2 = None
        for x, k in enumerate(claves):
            h1 = barra(b, x - 0.12, sin[k], AZUL, "o")
            h2 = barra(b, x + 0.12, con[k], GRISR, "o", hueco=True)
        b.set_xticks(range(3))
        b.set_xticklabels(etiquetas, fontsize=8)
        b.set_xlim(-0.5, 2.5)
        b.set_ylim(-0.1, 0.32)
        b.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.1))
        b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: coma(v, 1, False) if v >= 0 else coma(v, 1)))
        b.set_ylabel("Más síntomas que quienes\ntenían 2 años (DE) →",
                     fontsize=8)
        b.set_title("(b) ¿Cuánto de la brecha explican?", loc="left",
                    fontsize=8.5, pad=36)
        b.legend([h1, h2], ["Brecha en PHQ-4", "Controlando por los cuatro"],
                 loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1,
                 frameon=False, fontsize=6.8, handletextpad=0.2,
                 columnspacing=0.8, borderaxespad=0.2)
        guarda(f, "indices.pdf")


CLAVES = ["0-11m", "12-23m", "36-59m"]
ETIQUETAS = ["Bebés", "1 año", "3–4 años"]


def formato_eje(ax, paso, decimales=1):
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(paso))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: coma(v, decimales, False) if v >= 0
        else coma(v, decimales)))


def descomposicion():
    """La brecha en PHQ-4 frente a los expuestos con dos años, partida en lo
    que acompaña al hogar, al colegio y lo que queda sin explicar
    (reports/descomposicion.csv, Gelbach con bootstrap de comunas)."""
    c = pd.read_csv("reports/descomposicion.csv")
    capas = [("hogar", "Hogar: familia, adversidad y economía", MARRON),
             ("colegio", "Colegio", AZUL),
             ("sin explicar", "Sin explicar", "#D4D4D4")]
    with plt.rc_context(PAPER):
        f = plt.figure(figsize=(144 * MM, 60 * MM))
        for i, (grupo, nom) in enumerate((("todos", "Todos"),
                                          ("chicas", "Chicas"))):
            g = c[c.grupo == grupo].set_index(["edad", "componente"])
            n = 9036 if grupo == "todos" else 4467
            ax = f.add_axes([0.115 + i * 0.45, 0.12, 0.38, 0.63])
            for lado in ("top", "right", "bottom"):
                ax.spines[lado].set_visible(False)
            ax.axhline(0, color="black", lw=0.8, zorder=4)
            hs = []
            for x, k in enumerate(CLAVES):
                arriba = abajo = 0.0
                for comp, lab, col in capas:
                    v = g.loc[(k, comp), "valor"]
                    base = arriba if v >= 0 else abajo
                    h = ax.bar(x, v, 0.52, bottom=base, color=col, lw=0,
                               zorder=2, label=lab)
                    if v >= 0:
                        arriba += v
                    else:
                        abajo += v
                    if x == 0:
                        hs.append(h)
                # en negrita, parte explicada distinta de cero al 95%
                e = g.loc[(k, "explicado")]
                sig = e.lo > 0 or e.hi < 0
                pct = 100 * e.valor / g.loc[(k, "brecha"), "valor"]
                ax.text(x, arriba + 0.012, f"{pct:.0f}%",
                        ha="center", va="bottom", fontsize=8,
                        color="black" if sig else "#8C8C8C",
                        fontweight="bold" if sig else "normal")
            ax.set_xticks(range(3))
            ax.set_xticklabels(ETIQUETAS, fontsize=8)
            ax.set_xlim(-0.55, 2.55)
            ax.set_ylim(-0.012, 0.32)
            formato_eje(ax, 0.1)
            if i == 0:
                ax.set_ylabel("Más síntomas que quienes\ntenían 2 años (DE)",
                              fontsize=8)
            ax.set_title(f"{nom} (n = {miles(n)})", fontsize=9, pad=4)
        f.legend(hs, [lab for _, lab, _ in capas], loc="upper center",
                 bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
                 fontsize=7.5, handlelength=1.0, handletextpad=0.4,
                 columnspacing=1.4)
        guarda(f, "descomposicion.pdf")


def orden_temporal():
    """Las mismas preguntas a los mismos niños en 2017 y en 2024: colegio
    (responde el niño) y peleas en el hogar (responde el cuidador), frente a
    los expuestos con dos años (reports/orden_temporal.csv, todos)."""
    c = pd.read_csv("reports/orden_temporal.csv")
    c = c[c.grupo == "todos"].set_index(["medida", "ola", "edad"])
    paneles = [("colegio", "Le va mal o no le gusta el colegio",
                "Peor que quienes\ntenían 2 años (DE)", 1.0, (-0.3, 0.42),
                0.1),
               ("peleas", "Ha presenciado peleas en el hogar",
                "Más que quienes\ntenían 2 años (pp)", 100.0,
                (-12, 17), 5)]
    with plt.rc_context(PAPER):
        f = plt.figure(figsize=(144 * MM, 60 * MM))
        for i, (m, nom, ylab, esc, lim, paso) in enumerate(paneles):
            ax = f.add_axes([0.135 + i * 0.485, 0.12, 0.35, 0.63])
            ejes_paper(ax)
            for x, k in enumerate(CLAVES):
                t17 = tuple(c.loc[(m, 2017, k), ["b", "se", "p"]])
                t24 = tuple(c.loc[(m, 2024, k), ["b", "se", "p"]])
                h1 = barra(ax, x - 0.13, t17, GRISR, "o", hueco=True,
                           escala=esc)
                h2 = barra(ax, x + 0.13, t24, AZUL, "o", escala=esc)
            ax.set_xticks(range(3))
            ax.set_xticklabels(ETIQUETAS, fontsize=8)
            ax.set_xlim(-0.5, 2.5)
            ax.set_ylim(*lim)
            formato_eje(ax, paso, 1 if esc == 1.0 else 0)
            ax.set_ylabel(ylab, fontsize=8)
            ax.set_title(nom, fontsize=9, pad=4)
            if i == 0:
                hs = [h1, h2]
        f.legend(hs, ["2017, a los 8–12 años", "2024, a los 15–18 años"],
                 loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=2,
                 frameon=False,
                 fontsize=7.5, handletextpad=0.3, columnspacing=1.4)
        guarda(f, "orden_temporal.pdf")


def ventanas():
    """PHQ-4 de las chicas por edad al terremoto en tramos de seis meses,
    frente a las expuestas con 24-35 meses, con las dos ventanas sombreadas
    (reports/ventanas.csv)."""
    c = pd.read_csv("reports/ventanas.csv")
    c = c[c.grupo == "chicas"].set_index("tramo")
    tramos = ["6-11", "12-17", "18-23", "ref", "36-41", "42-49"]
    etiquetas = ["6–11", "12–17", "18–23", "24–35", "36–41", "42–49"]
    with plt.rc_context(PAPER):
        f = plt.figure(figsize=(144 * MM, 57 * MM))
        ax = f.add_axes([0.13, 0.21, 0.84, 0.72])
        ejes_paper(ax)
        for x0, x1, txt in ((-0.5, 1.5, "Estrés"), (4.5, 5.5, "Memoria")):
            ax.axvspan(x0, x1, color="#F1F1F1", lw=0, zorder=0)
            ax.text((x0 + x1) / 2, 0.66, txt, ha="center", va="top",
                    fontsize=8.5, color="#5A5A5A")
        for x, t in enumerate(tramos):
            if t == "ref":
                ax.plot(x, 0, "^", ms=6.0, color=MARRON, mfc="white",
                        mew=1.0, zorder=3)
                ax.text(x, -0.07, "referencia", ha="center", va="top",
                        fontsize=7.5, color="#5A5A5A")
                continue
            barra(ax, x, tuple(c.loc[t, ["b", "se", "p"]]), MARRON, "^")
        ax.set_xticks(range(len(tramos)))
        ax.set_xticklabels(etiquetas, fontsize=8)
        ax.set_xlim(-0.5, len(tramos) - 0.5)
        ax.set_ylim(-0.25, 0.7)
        formato_eje(ax, 0.2)
        ax.set_ylabel("Más síntomas que quienes\ntenían 2 años (DE)",
                      fontsize=8.5)
        ax.set_xlabel("Edad al terremoto, en meses", fontsize=8.5)
        guarda(f, "ventanas.pdf")


def hogar_2017():
    """Colegio (responde el niño) y peleas en el hogar (responde el
    cuidador) en 2017, a los 8-12 años, por edad al terremoto frente a los
    expuestos con dos años (reports/orden_temporal.csv, todos)."""
    c = pd.read_csv("reports/orden_temporal.csv")
    c = c[(c.grupo == "todos") & (c.ola == 2017)].set_index(
        ["medida", "edad"])
    paneles = [("colegio", "Le va mal o no le gusta el colegio",
                "Peor que quienes\ntenían 2 años (DE)", 1.0, (-0.3, 0.42),
                0.1),
               ("peleas", "Ha presenciado peleas en el hogar",
                "Más que quienes\ntenían 2 años (pp)", 100.0, (-12, 17), 5)]
    with plt.rc_context(PAPER):
        f = plt.figure(figsize=(144 * MM, 58 * MM))
        for i, (m, nom, ylab, esc, lim, paso) in enumerate(paneles):
            ax = f.add_axes([0.135 + i * 0.485, 0.13, 0.35, 0.72])
            ejes_paper(ax)
            for x, k in enumerate(CLAVES):
                barra(ax, x, tuple(c.loc[(m, k), ["b", "se", "p"]]), AZUL,
                      "o", escala=esc)
            ax.set_xticks(range(3))
            ax.set_xticklabels(ETIQUETAS, fontsize=8)
            ax.set_xlim(-0.5, 2.5)
            ax.set_ylim(*lim)
            formato_eje(ax, paso, 1 if esc == 1.0 else 0)
            ax.set_ylabel(ylab, fontsize=8)
            ax.set_title(nom, fontsize=9, pad=4)
        guarda(f, "hogar_2017.pdf")


def main():
    mapa()
    hallazgos()
    diseno()
    trayectoria()
    variables()
    salud_mental()
    resto()
    lactancia()
    indices_fig()
    descomposicion()
    orden_temporal()
    ventanas()
    hogar_2017()


if __name__ == "__main__":
    main()
