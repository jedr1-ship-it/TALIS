#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figuras de la presentación de seminario: la ecuación y un coefplot por
cada diapositiva de evidencia, con la tipografía y la paleta del deck.

  ecuacion.png       la ecuación (1) con el significado de cada término
  perfil_sexo.png    PHQ-4 por edad al terremoto, chicas y chicos
  tamizajes.png      ansiedad (GAD-2) y depresión (PHQ-2), bebés frente a 2
  especificidad.png  chicas: síntomas frente a vocabulario por edad
  lactancia.png      zona afectada x tomaba pecho el 27-F
  lactancia_placebo.png  la misma interacción en variables previas al 27-F
  descartado.png     chicas: peleas y disciplina dura en 2012 y 2017

Todas las diferencias son relativas a los expuestos con dos años salvo
las de lactancia (interacción dentro de un grupo de edad). Intervalos al
95%, errores agrupados por comuna, pesos de 2024.

Salida: reports/figures/presentacion/*.png y reports/presentacion_numeros.md
Uso:    python3 scripts/22_figuras_presentacion.py
"""
import importlib.util
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib import font_manager as fm            # noqa: E402
from matplotlib.lines import Line2D                  # noqa: E402
import numpy as np                                   # noqa: E402
import statsmodels.formula.api as smf                # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
OUTD = Path("reports/figures/presentacion")
OUT = []


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


p20 = modulo("p20", "20_historia_hogar.py")
p21 = modulo("p21", "21_tres_cuatro.py")
p15 = p21.p15
reg, fmt, zg, xt = p21.reg, p21.fmt, p21.zg, p21.xt
CHICAS, CHICOS = p21.CHICAS, p21.CHICOS

# ------------------------------ estilo ------------------------------------
BG, INK, ACC, MUTED = "#F6F5F1", "#17212B", "#2B5FA8", "#55606B"
GRIS, GRID = "#7D8790", "#E2E0D8"
S, DPI = 2, 200                 # 2 px de imagen por px de diapositiva
FONTS = HERE / "fonts"
REG = FONTS / "IBMPlexSans-Regular.ttf"
SEMI = FONTS / "IBMPlexSans-SemiBold.ttf"
for f in (REG, SEMI):
    fm.fontManager.addfont(str(f))
plt.rcParams.update({"font.family": "IBM Plex Sans",
                     "mathtext.fontset": "cm",
                     "axes.unicode_minus": True})


def pt(px):
    """Tamaño en px de diapositiva -> puntos de matplotlib."""
    return px * S * 72 / DPI


def fp(px, bold=False):
    return fm.FontProperties(fname=str(SEMI if bold else REG), size=pt(px))


def coma(x, dec=2, signo=True):
    s = f"{x:+.{dec}f}" if signo else f"{x:.{dec}f}"
    return s.replace("-", "−").replace(".", ",")


def lienzo(w, h):
    return plt.figure(figsize=(w * S / DPI, h * S / DPI), dpi=DPI,
                      facecolor=BG)


def ejes_limpios(ax, eje="y"):
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0, pad=pt(12), colors=INK)
    ax.grid(axis=eje, color=GRID, lw=pt(1.5), zorder=0)
    ax.set_axisbelow(True)


def guarda(f, nombre):
    OUTD.mkdir(parents=True, exist_ok=True)
    f.savefig(OUTD / nombre, dpi=DPI, facecolor=BG)
    plt.close(f)
    log(f"-> {OUTD / nombre}")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def leyenda(ax, series, loc="upper left"):
    h = [Line2D([], [], marker="o", ls="none", ms=pt(16), color=s["color"],
                label=s["name"]) for s in series]
    lg = ax.legend(handles=h, loc=loc, frameon=False, prop=fp(26),
                   handletextpad=0.3, borderaxespad=0.2, ncol=len(series),
                   columnspacing=1.6)
    for t, s in zip(lg.get_texts(), series):
        t.set_color(INK)


def coef_vertical(nombre, cats, series, titulo_eje, w=1664, h=520,
                  ylim=None, escala=1.0, dec=2):
    """Una serie por grupo; cada punto es (b, ee) o None (referencia)."""
    f = lienzo(w, h)
    ax = f.add_axes([0.07, 0.15, 0.92, 0.70])
    ejes_limpios(ax)
    xs = np.arange(len(cats))
    k = len(series)
    off = np.linspace(-0.14, 0.14, k) if k > 1 else [0.0]
    for j, s in enumerate(series):
        for i, p in enumerate(s["pts"]):
            x = xs[i] + off[j]
            if p is None:
                ax.plot(x, 0, "o", ms=pt(16), mfc=BG, mec=s["color"],
                        mew=pt(3), zorder=4)
                continue
            b, se = p[0] * escala, p[1] * escala
            ax.plot([x, x], [b - 1.96 * se, b + 1.96 * se],
                    color=s["color"], lw=pt(5), solid_capstyle="round",
                    zorder=3)
            ax.plot(x, b, "o", ms=pt(18), color=s["color"], mec=BG,
                    mew=pt(2), zorder=4)
            izq = j < k / 2 and k > 1
            # una etiqueta pegada al cero se separa de la línea
            yl = b if abs(b) >= 0.05 else (0.05 if b >= 0 else -0.05)
            ax.text(x + (-0.06 if izq else 0.06), yl, coma(b, dec),
                    ha="right" if izq else "left", va="center",
                    fontproperties=fp(26, bold=True), color=s["color"],
                    zorder=5)
    ax.axhline(0, color=MUTED, lw=pt(2.5), zorder=2)
    ax.set_xticks(xs)
    ax.set_xticklabels(cats)
    for t in ax.get_xticklabels():
        t.set_fontproperties(fp(28))
        t.set_color(INK)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlim(-0.5, len(cats) - 0.5)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: coma(v, 1, v != 0)))
    for t in ax.get_yticklabels():
        t.set_fontproperties(fp(24))
        t.set_color(MUTED)
    f.text(0.07, 0.955, titulo_eje, fontproperties=fp(26), color=MUTED,
           ha="left", va="top")
    if k > 1:
        leyenda(ax, series, loc="upper right")
    guarda(f, nombre)


def coef_horizontal(nombre, filas, series, titulo_eje, w=1664, h=520,
                    xlim=None, escala=1.0, dec=2, izq=0.36):
    f = lienzo(w, h)
    ax = f.add_axes([izq, 0.17, 0.98 - izq, 0.71])
    ejes_limpios(ax, eje="x")
    ys = np.arange(len(filas))[::-1].astype(float)
    k = len(series)
    off = np.linspace(0.13, -0.13, k) if k > 1 else [0.0]
    for j, s in enumerate(series):
        for i, p in enumerate(s["pts"]):
            if p is None:
                continue
            y = ys[i] + off[j]
            b, se = p[0] * escala, p[1] * escala
            ax.plot([b - 1.96 * se, b + 1.96 * se], [y, y],
                    color=s["color"], lw=pt(5), solid_capstyle="round",
                    zorder=3)
            ax.plot(b, y, "o", ms=pt(18), color=s["color"], mec=BG,
                    mew=pt(2), zorder=4)
            ax.text(b + 1.96 * se, y, "  " + coma(b, dec), ha="left",
                    va="center", fontproperties=fp(26, bold=True),
                    color=s["color"], zorder=5,
                    bbox=dict(boxstyle="square,pad=0.15", fc=BG, ec="none"))
    ax.axvline(0, color=MUTED, lw=pt(2.5), zorder=2)
    ax.set_yticks(ys)
    ax.set_yticklabels(filas)
    for t in ax.get_yticklabels():
        t.set_fontproperties(fp(28))
        t.set_color(INK)
    ax.set_ylim(-0.6, len(filas) - 0.4)
    if xlim:
        ax.set_xlim(*xlim)
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(
            lambda v, _: coma(v, 0 if escala == 100 else 1, v != 0)))
    for t in ax.get_xticklabels():
        t.set_fontproperties(fp(24))
        t.set_color(MUTED)
    f.text(izq, 0.955, titulo_eje, fontproperties=fp(26), color=MUTED,
           ha="left", va="top")
    if k > 1:
        leyenda(ax, series, loc="lower right")
    guarda(f, nombre)


# ------------------------------ datos -------------------------------------

def carga():
    d = p21.carga()
    e = p20.carga()
    cols = ["folio", "peleas17", "peleas24", "grito12", "amenaza12",
            "pega12", "grito17", "golpes17", "meses_pecho"]
    d = d.merge(e[cols], on="folio", how="left")
    d["neg_tvip"] = -d.z_tvip
    d["dif_dano"] = d.z_phq4 + d.z_tvip
    d["z_educ_madre"] = zg(d.educ_madre10)
    d["z_edad_madre"] = zg(d.edad_madre10)
    return d


def lactancia(d, binl, y, sexo=None, simple=False):
    """Interacción zona afectada x tomaba pecho el 27-F dentro de un grupo
    de edad (la especificación de scripts/20, prueba P4)."""
    bb = d[d.bin == binl].dropna(subset=["meses_pecho", y, "w", "estrato",
                                         "cohorte"])
    if sexo is not None:
        bb = bb[bb.mujer == sexo]
    bb = bb[bb.w > 0].copy()
    bb["est"] = bb.estrato.astype(int).astype(str)
    bb["coh"] = bb.cohorte.astype(int).astype(str)
    bb["pecho"] = (bb.meses_pecho >= bb.edadq_m).astype(float)
    bb["EQxpecho"] = bb.EQ * bb.pecho
    rhs = ["EQxpecho", "pecho", "C(est)"]
    if not simple:
        rhs += ["C(coh)"] + xt(bb, p15.X_PRE) + xt(bb, p15.X_POST)
    r = smf.wls(f"{y} ~ {' + '.join(rhs)}", data=bb, weights=bb.w).fit(
        cov_type="cluster", cov_kwds={"groups": bb.est})
    return (float(r.params["EQxpecho"]), float(r.bse["EQxpecho"]),
            float(r.pvalues["EQxpecho"])), int(r.nobs), float(bb.pecho.mean())


# ------------------------------ figuras -----------------------------------

def fig_ecuacion():
    f = lienzo(1664, 700)
    eq = (r"$Y_{imc} \;=\; \sum_{a}\,\beta_a\,(\mathrm{Edad}_{ai}\times"
          r"\mathrm{Afectada}_m) \;+\; \sum_{a}\,\gamma_a\,\mathrm{Edad}_{ai}"
          r" \;+\; \psi_m \;+\; \theta_c \;+\; X_i'\delta \;+\;"
          r" \varepsilon_{imc}$")
    t = f.text(0.5, 0.97, eq, fontsize=pt(58), color=INK, ha="center",
               va="top")
    r = f.canvas.get_renderer()
    ancho = t.get_window_extent(r).width / (1664 * S)
    if ancho > 0.98:
        t.set_fontsize(pt(58) * 0.98 / ancho)
    filas = [
        (r"$Y_{imc}$", "Ansiedad y depresión a los 15–18 años (PHQ-4, GAD-2, PHQ-2)"),
        (r"$\mathrm{Edad}_{ai}$", "Edad el día del terremoto: 6–11 meses, 1 año o 3–4 años"),
        (r"$\mathrm{Afectada}_m$", "Comuna en la zona de daño destructivo"),
        (r"$\beta_a$", "Diferencia con los de 2 años, comunas afectadas menos no afectadas"),
        (r"$\gamma_a$", "Diferencia con los de 2 años, común a todas las comunas"),
        (r"$\psi_m$", "Efecto fijo de comuna"),
        (r"$\theta_c$", "Efecto fijo de cohorte de nacimiento"),
        (r"$X_i$", "Controles del niño y del hogar"),
        (r"$\varepsilon_{imc}$", "Error"),
        (r"$i,\ m,\ c,\ a$", "Adolescente, comuna, cohorte, grupo de edad"),
    ]
    y0, paso = 0.745, 0.073
    for i, (sim, txt) in enumerate(filas):
        y = y0 - i * paso
        f.text(0.04, y, sim, fontsize=pt(40), color=ACC, ha="left",
               va="center")
        f.text(0.25, y, txt, fontproperties=fp(30), color=INK, ha="left",
               va="center")
    guarda(f, "ecuacion.png")


def main():
    d = carga()
    log("# Números de la presentación (scripts/22_figuras_presentacion.py)")
    fig_ecuacion()

    # 1. Perfil por edad y sexo, PHQ-4, referencia: dos años
    cats = ["6–11 meses", "1 año", "2 años", "3–4 años"]
    series = []
    for nom, s, col in (("Chicas", CHICAS, ACC), ("Chicos", CHICOS, GRIS)):
        b, n, _, _ = reg(d, "z_phq4", sample=s)
        log(f"\n## Perfil PHQ-4, {nom} (N={n}), frente a 2 años")
        for k in ("0-11m", "12-23m", "36-59m"):
            log(f"- {k}: {fmt(b[k])}")
        series.append({"name": nom, "color": col,
                       "pts": [b["0-11m"], b["12-23m"], None, b["36-59m"]]})
    coef_vertical("perfil_sexo.png", cats, series,
                  "Síntomas PHQ-4 a los 15–18 años frente a los expuestos "
                  "con dos años (desv. estándar)", ylim=(-0.35, 0.62))

    # 2. Tamizajes, bebés frente a dos años, por sexo
    filas = ["Ansiedad\n(GAD-2 positivo)", "Depresión\n(PHQ-2 positivo)"]
    series = []
    for nom, s, col in (("Chicas", CHICAS, ACC), ("Chicos", CHICOS, GRIS)):
        pts = []
        for y in ("gad2_bin", "phq2_bin"):
            b, n, _, _ = reg(d, y, sample=s)
            dd = d[s(d)].dropna(subset=[y, "w"])
            base = np.average(dd[y], weights=dd.w)
            log(f"- {nom}, {y}: bebés frente a 2 {fmt(b['0-11m'])}; "
                f"media ponderada {base:.3f}; N={n}")
            pts.append(b["0-11m"])
        series.append({"name": nom, "color": col, "pts": pts})
    coef_horizontal("tamizajes.png", filas, series,
                    "Expuestos de bebés frente a expuestos con dos años "
                    "(puntos porcentuales)", escala=100, dec=0,
                    xlim=(-14, 32), h=440, izq=0.24)

    # 3. Especificidad en las chicas: síntomas frente a vocabulario
    series = []
    for y, nom, col in (("z_phq4", "Síntomas de ansiedad y depresión", ACC),
                        ("neg_tvip", "Déficit de vocabulario", GRIS)):
        b, n, _, _ = reg(d, y, sample=CHICAS)
        log(f"\n## Chicas, {y} (orientado como daño), frente a 2 años, N={n}")
        for k in ("0-11m", "12-23m", "36-59m"):
            log(f"- {k}: {fmt(b[k])}")
        series.append({"name": nom, "color": col,
                       "pts": [b["0-11m"], b["12-23m"], None, b["36-59m"]]})
    b, n, _, _ = reg(d, "dif_dano", sample=CHICAS)
    log(f"- prueba conjunta (síntomas menos vocabulario): bebés "
        f"{fmt(b['0-11m'])}; 3-4 {fmt(b['36-59m'])}; N={n}")
    coef_vertical("especificidad.png", cats, series,
                  "Chicas: daño frente a las expuestas con dos años "
                  "(desv. estándar; arriba = peor)", ylim=(-0.45, 0.62))

    # 4. Lactancia: zona afectada x tomaba pecho el 27-F
    filas, pts = [], []
    for binl, sexo, lab in (("0-11m", None, "Bebés de 6–11 meses"),
                            ("0-11m", 1, "Bebés de 6–11 meses, chicas"),
                            ("12-23m", None, "Expuestos con un año")):
        t, n, m = lactancia(d, binl, "z_phq4", sexo=sexo)
        log(f"- lactancia {lab}: {fmt(t)}; N={n}; tomaban pecho {m:.2f}")
        filas.append(lab)
        pts.append(t)
    t, n, m = lactancia(d, "24-35m", "z_phq4")
    log(f"- lactancia expuestos con dos años (solo notas): {fmt(t)}; N={n}; "
        f"tomaban pecho {m:.2f}")
    coef_horizontal("lactancia.png", filas,
                    [{"name": "", "color": ACC, "pts": pts}],
                    "Síntomas PHQ-4 (desv. estándar): zona afectada × "
                    "tomaba pecho el 27-F", xlim=(-0.4, 1.15), h=440,
                    izq=0.30)

    # 5. Placebos de la interacción, variables fijadas antes del 27-F
    filas, pts = [], []
    for y, lab, simple in (("z_peso", "Peso al nacer", False),
                           ("z_talla", "Talla al nacer", False),
                           ("z_gest", "Semanas de gestación", False),
                           ("z_educ_madre", "Escolaridad de la madre", True),
                           ("z_edad_madre", "Edad de la madre", True)):
        t, n, _ = lactancia(d, "0-11m", y, simple=simple)
        log(f"- placebo lactancia {lab}: {fmt(t)}; N={n}")
        filas.append(lab)
        pts.append(t)
    coef_horizontal("lactancia_placebo.png", filas,
                    [{"name": "", "color": GRIS, "pts": pts}],
                    "Desv. estándar: zona afectada × tomaba pecho, bebés de "
                    "6–11 meses", xlim=(-0.55, 0.65), h=520, izq=0.30)

    # 6. Lo que no lo explica, chicas, bebés frente a dos años
    filas, pts = [], []
    for y, lab in (("peleas17", "Presenció peleas en casa (2017)"),
                   ("grito12", "La madre le grita (2012)"),
                   ("amenaza12", "La madre la amenaza (2012)"),
                   ("pega12", "La madre le pega (2012)"),
                   ("grito17", "La gritaron o insultaron (2017)"),
                   ("golpes17", "La sacudieron o golpearon (2017)")):
        b, n, _, _ = reg(d, y, sample=CHICAS)
        log(f"- chicas {lab}: bebés frente a 2 {fmt(b['0-11m'])}; N={n}")
        filas.append(lab)
        pts.append(b["0-11m"])
    coef_horizontal("descartado.png", filas,
                    [{"name": "", "color": GRIS, "pts": pts}],
                    "Chicas expuestas de bebés frente a expuestas con dos "
                    "años (puntos porcentuales)", escala=100, dec=0,
                    xlim=(-30, 22), h=520, izq=0.36)
    base = d.dropna(subset=["peleas17", "peleas24"])
    r0, _, _, _ = reg(base, "z_phq4", sample=CHICAS)
    r1, _, _, _ = reg(base, "z_phq4", sample=CHICAS,
                      extra=["peleas17", "peleas24"])
    log(f"- chicas, PHQ-4 bebés frente a 2 sin y con control por peleas "
        f"2017 y 2024: {fmt(r0['0-11m'])} -> {fmt(r1['0-11m'])} "
        f"({100 * (1 - r1['0-11m'][0] / r0['0-11m'][0]):.0f}% menos)")
    b, n, _, _ = reg(d, "peleas24", sample=CHICAS)
    log(f"- chicas, peleas presenciadas 2024: bebés frente a 2 "
        f"{fmt(b['0-11m'])}; N={n}")
    Path("reports/presentacion_numeros.md").write_text(
        "\n".join(OUT) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
