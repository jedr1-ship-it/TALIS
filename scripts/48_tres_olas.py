#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La misma niña en tres rondas: ¿la huella aparece en la adolescencia o ya
estaba antes?

Comentario tipo referee (punto 3). Con los mismos adolescentes de 2024 y el
mismo diseño (EF de comuna de selección, año de nacimiento y tramo de edad;
controles; pesos ELPI de 2024; EE por comuna), cinco medidas de salud
mental internalizante en tres edades:

  2012  CBCL internalizante, cuidador (2-6 años)
  2017  CBCL internalizante, cuidador (8-11 años)
  2017  índice que reporta el niño: baja autoestima (TAE), no se considera
        feliz, se siente solo en el curso (8-11 años)
  2024  CBCL internalizante, cuidador (14-18 años)
  2024  PHQ-4, autorreporte (14-18 años)

Para cada una: 6-11 meses frente a todas las demás edades y el perfil en
tramos de seis meses centrado (suma cero), con la prueba conjunta de perfil
plano. También en la muestra balanceada (las que tienen las cinco).
Lectura: nada antes y algo en 2024 sería emergencia en la adolescencia; lo
mismo ya en 2012 o 2017, persistencia; perfiles sin relación entre rondas,
ruido.

Además, la ventana ancha que sugiere el perfil de 2024 (los primeros 18
meses, 6-17): frente al resto, frente a 3-4 años y frente a 18-35 meses, en
el PHQ-4 de 2024 y en el autorreporte de 2017, y sin cada región de control.
Se eligió después de ver el perfil: es exploratoria.

Salida: reports/tres_olas.md, reports/tres_olas.csv y reports/tres_olas.png
Uso:    python3 scripts/48_tres_olas.py
"""
import importlib.util
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
import numpy as np                                   # noqa: E402
import pandas as pd                                  # noqa: E402

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent


def modulo(nombre, archivo):
    s = importlib.util.spec_from_file_location(nombre, HERE / archivo)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


p47 = modulo("p47", "47_perfil_completo.py")
p40 = modulo("p40", "40_salud_mental_antes.py")
p28 = p47.p28
MEDIDAS = [("z_int12", "2012, CBCL internalizing, caregiver (ages 2-6)",
            "2012\nCBCL, caregiver"),
           ("z_int17", "2017, CBCL internalizing, caregiver (ages 8-11)",
            "2017\nCBCL, caregiver"),
           ("malestar17", "2017, child's own report (ages 8-11)",
            "2017\nchild's report"),
           ("z_cbcl", "2024, CBCL internalizing, caregiver (ages 14-18)",
            "2024\nCBCL, caregiver"),
           ("z_phq4", "2024, PHQ-4, own report (ages 14-18)",
            "2024\nPHQ-4, own report")]
OUT, FILAS = [], []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    OUT.append(s)


def carga():
    d = p47.carga()
    df = p40.base()
    for ola in (2012, 2017):
        x = (df[df.wave == ola][["folio", "z_int"]].drop_duplicates("folio")
             .rename(columns={"z_int": f"z_int{ola % 100}"}))
        d = d.merge(x, on="folio", how="left")
    n17 = p40.ninos17()
    d = d.merge(n17[["folio", "z_tae_baja", "no_feliz", "z_soledad"]],
                on="folio", how="left")
    zz = lambda s: (s - s.mean()) / s.std()                   # noqa: E731
    tres = pd.concat([zz(d.z_tae_baja), zz(d.no_feliz), zz(d.z_soledad)],
                     axis=1)
    d["malestar17"] = zz(tres.mean(axis=1).where(tres.notna().all(axis=1)))
    return d


def ventana18(d):
    """6-17 meses x zona, con efectos fijos de tramo de seis meses."""
    def est(x, y, muestra=None, grupos="est"):
        x = x.dropna(subset=[y]).copy()
        if muestra is not None:
            x = x[muestra(x)]
        x["D"] = (x.edadq_m < 18).astype(float) * x.EQ
        r = p47.wls(x, ["D", "C(b6)", "C(est)", "C(coh)"]
                    + p47.controles(x), y=y, grupos=grupos)
        return (float(r.params["D"]), float(r.bse["D"]),
                float(r.pvalues["D"])), int(r.nobs)
    ch = d[d.mujer == 1]
    log("\n## La ventana de los primeros 18 meses (exploratoria), chicas")
    for y, lab in (("z_phq4", "2024, PHQ-4"), ("malestar17",
                                               "2017, autorreporte")):
        for txt, kw in (("frente al resto", {}),
                        ("frente al resto, EE por región",
                         {"grupos": "reg"}),
                        ("frente a 3-4 años (36-49)",
                         {"muestra": lambda x: (x.edadq_m < 18)
                          | (x.edadq_m >= 36)}),
                        ("frente a 18-35 meses",
                         {"muestra": lambda x: x.edadq_m < 36})):
            r, n = est(ch, y, **kw)
            log(f"- {lab}, 6-17 meses {txt}: {p47.fmt(*r)}; N={n:,}")
    log("- 2024, PHQ-4, 6-17 frente al resto, sin cada región de control: "
        + " | ".join(
            f"{r_}: {est(ch, 'z_phq4', muestra=lambda x, r_=r_: x.reg != r_)[0][0]:+.3f}"
            for r_ in sorted(ch[ch.EQ == 0].reg.unique())))


def figura(perf):
    with plt.rc_context(p28.PAPER):
        f = plt.figure(figsize=(150 * p28.MM, 78 * p28.MM))
        centros = [8.5, 14.5, 20.5, 26.5, 32.5, 38.5, 45.5]
        for fila_, (g, nombre) in enumerate((("chicas", "Girls"),
                                             ("chicos", "Boys"))):
            for j, (y, _, corto) in enumerate(MEDIDAS):
                a = f.add_axes([0.09 + j * 0.182, 0.56 - fila_ * 0.43,
                                0.15, 0.3])
                p28.ejes_paper(a)
                res = perf[(g, y)]
                col = p28.OCRE if g == "chicas" else p28.GRISR
                bs = [res[t][0] for t in p47.SEIS[1]]
                se = [res[t][1] for t in p47.SEIS[1]]
                a.errorbar(centros, bs, yerr=1.96 * np.array(se), fmt="o-",
                           color=col, ms=3, lw=0.8, capsize=1.5,
                           elinewidth=0.7)
                a.set_xlim(4, 51)
                a.set_ylim(-0.7, 0.7)
                p28.formato_eje(a, 0.35)
                a.set_xticks([6, 18, 30, 42])
                a.tick_params(labelsize=6.5)
                if j:
                    a.set_yticklabels([])
                else:
                    a.set_ylabel(nombre, fontsize=8)
                if fila_ == 0:
                    a.set_title(corto, fontsize=7, pad=3, linespacing=1.0)
        f.text(0.53, 0.01, "Age at the earthquake (months); affected minus "
               "unaffected, centered (SD)", ha="center", fontsize=7.5)
        f.savefig("reports/tres_olas.png", dpi=220)
        plt.close(f)
    print("-> reports/tres_olas.png")


def main():
    d = carga()
    log("# La misma niña en tres rondas (scripts/48_tres_olas.py)")
    log("Adolescentes de 2024; zona afectada menos no afectada; EF de "
        "comuna de selección, año de nacimiento y tramo; controles; pesos "
        "ELPI 2024; EE por comuna. Más alto = peor.")
    bal = d.dropna(subset=[y for y, _, _ in MEDIDAS])
    log(f"\nMuestra balanceada (las cinco medidas): {len(bal):,} "
        f"({int((bal.mujer == 1).sum()):,} chicas)")
    perf = {}
    for y, lab, _ in MEDIDAS:
        log(f"\n## {lab}")
        for g, sx in p47.SEXOS:
            x = d[d.mujer == sx]
            r, n = p47.contraste(x, y=y)
            rb, nb = p47.contraste(bal[bal.mujer == sx], y=y)
            res, conj, vec, _ = p47.tramos_seis(x, y=y)
            perf[(g, y)] = res
            log(f"- {g}: 6-11 frente al resto {p47.fmt(*r)}; N={n:,} | "
                f"balanceada {p47.fmt(*rb)}; N={nb:,}")
            log(f"  tramos centrados: " + " | ".join(
                f"{t} {v[0]:+.2f}" for t, v in res.items())
                + f" | perfil plano p={conj:.3f}; 6-11 menos 12-17 "
                f"{vec[0]:+.2f} (ee {vec[1]:.2f})")
            FILAS.append({"medida": y, "grupo": g, "b": r[0], "se": r[1],
                          "p": r[2], "n": n, "b_bal": rb[0], "se_bal": rb[1],
                          "p_conjunta": conj,
                          **{f"t{t}": v[0] for t, v in res.items()}})
    log("\n## ¿Se parecen los perfiles entre rondas? Correlación de los "
        "siete tramos centrados con el del PHQ-4 de 2024")
    for g, _ in p47.SEXOS:
        base = np.array([perf[(g, "z_phq4")][t][0] for t in p47.SEIS[1]])
        log(f"- {g}: " + " | ".join(
            f"{y} {np.corrcoef(base, [perf[(g, y)][t][0] for t in p47.SEIS[1]])[0, 1]:+.2f}"
            for y, _, _ in MEDIDAS[:-1]))
    ventana18(d)
    figura(perf)
    pd.DataFrame(FILAS).to_csv("reports/tres_olas.csv", index=False)
    Path("reports/tres_olas.md").write_text("\n".join(OUT) + "\n",
                                            encoding="utf-8")
    print("-> reports/tres_olas.md, reports/tres_olas.csv")


if __name__ == "__main__":
    main()
