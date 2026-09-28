#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fase 1 — dataset del paper "The Adolescent Scar of Early-Life Disaster".

Construye y cachea dos frames en data/processed/:

  paper_adolescentes.pkl : unidad = adolescente ELPI 2024 (n≈10.003).
    Base del script 09 (bins de edad el 27-F, EQ, X, PHQ/GAD/CBCL/ΔCBCL)
    + mecanismos 2024 (resiliencia BRS d2, satisfacción vital d3_1,
      bullying g1, cibervictimización g2, violencia g9, tabaco g11,
      alcohol g12, cannabis g13)
    + salud mental materna pre y post (2010: dx en embarazo g4a_1/3/7,
      derivación g4b, depresión postparto g19; 2012: dx depresión b64)
    + placebos predeterminados al nacer (2010: peso g24, talla g23,
      semanas de gestación g20, prematuro g17_6, Apgar-5' g25b1).

  paper_atricion.pkl : unidad = niño de la línea base 2010 (n≈15.175).
    región 2010 → EQ, edad aproximada el 27-F → bins, educación/edad de la
    madre 2010, y banderas in2012/in2017/in2024 (por folio) para la tabla
    de atrición diferencial y los bounds de Lee.

Uso: python3 scripts/13_paper_dataset.py
"""
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import warnings

warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
INT = Path("data/interim")
OUT = Path("data/processed")

spec = importlib.util.spec_from_file_location(
    "sm27", HERE / "09_salud_mental_27f.py")
sm27 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sm27)


def num(s):
    return pd.to_numeric(s, errors="coerce")


def sino(s):
    """1=sí, 2=no; el resto NaN."""
    v = num(s)
    return (v == 1).astype(float).where(v.isin([1, 2]))


def zstd(s):
    s = num(s)
    return (s - s.mean()) / s.std()


def extras_2024():
    cols = (["folio", "d1", "d3_1", "g11"]
            + [f"d2_{i}" for i in range(1, 7)]
            + [f"g1_{i}" for i in range(1, 9)]
            + [f"g2_{i}" for i in range(1, 9)]
            + [f"g9_{i}" for i in (1, 2, 3)]
            + [f"g12_{i}" for i in (1, 2, 3, 4)]
            + [f"g13_{i}" for i in range(1, 9)])
    df, meta = pyreadstat.read_dta(
        str(INT / "2024/Base adolescentes Stata.dta"))
    have = [c for c in cols if c in df.columns]
    df = df[have].copy()
    df["folio"] = num(df.folio).astype("int64")
    print("extras 2024: columnas encontradas:", len(have))
    for c in ("d2_1", "g1_1", "g2_1", "g9_1", "g11", "g12_1", "g13_1"):
        if c in df:
            print(f"  {c} values:", num(df[c]).value_counts().head(6).to_dict())
    e = pd.DataFrame({"folio": df.folio})
    # Brief Resilience Scale: 6 ítems 1-5, 2/4/6 invertidos (estándar BRS)
    brs = []
    for i in range(1, 7):
        v = num(df.get(f"d2_{i}")).where(lambda s: s.between(1, 5))
        if i in (2, 4, 6):
            v = 6 - v
        brs.append(v)
    e["z_resil"] = zstd(pd.concat(brs, axis=1).mean(axis=1, skipna=False))
    e["z_satisf"] = zstd(num(df.get("d3_1")).where(lambda s: s.between(1, 7)))
    e["z_salud"] = zstd(-num(df.get("d1")).where(lambda s: s.between(1, 5)))
    g1 = df[[c for c in df.columns if c.startswith("g1_")]].apply(num)
    g1 = g1.where((g1 >= 1) & (g1 <= 4))
    if "g1_3" in g1:                      # ítem positivo: se invierte
        g1["g1_3"] = 5 - g1["g1_3"]
    e["z_bull"] = zstd(g1.mean(axis=1))
    g2 = df[[c for c in df.columns if c.startswith("g2_")]].apply(sino)
    e["ciber_any"] = g2.max(axis=1)
    # g9: violencia en la pareja (módulo de pololeo), codificada 0/1
    g9 = df[[c for c in df.columns if c.startswith("g9_")]].apply(num)
    g9 = g9.where(g9.isin([0, 1]))
    e["viol_pareja"] = g9.max(axis=1)
    e["fuma"] = sino(df.get("g11"))
    g12 = df[[c for c in df.columns if c.startswith("g12_")]].apply(sino)
    e["alcohol"] = g12.max(axis=1)
    g13 = df[[c for c in df.columns if c.startswith("g13_")]].apply(sino)
    e["cannabis"] = g13.max(axis=1)
    return e


def extras_2010():
    df, _ = pyreadstat.read_dta(
        str(INT / "2010/Entrevistada_2010.dta"),
        usecols=["folio", "g24", "g23", "g20", "g17_6", "g25b1",
                 "g4a_1", "g4a_3", "g4a_7", "g4b", "g19", "region"])
    df["folio"] = num(df.folio).astype("int64")
    e = pd.DataFrame({"folio": df.folio})
    e["peso_nacer"] = num(df.g24).where(lambda s: s.between(0.5, 6.5))  # kg
    e["talla_nacer"] = num(df.g23).where(lambda s: s.between(30, 65))   # cm
    e["sem_gest"] = num(df.g20).where(lambda s: s.between(24, 45))
    e["prematuro"] = sino(df.g17_6)
    e["apgar5"] = num(df.g25b1).where(lambda s: s.between(0, 10))
    dx = pd.concat([sino(df[c]) for c in ("g4a_1", "g4a_3", "g4a_7")], axis=1)
    e["mh_emb_dx"] = dx.max(axis=1)
    e["deriv_psic"] = sino(df.g4b)
    e["dep_postparto"] = sino(df.g19)
    e["region10"] = num(df.region).astype("Int64")
    print("extras 2010: peso nacer no-nulo:", e.peso_nacer.notna().sum(),
          "| dep_postparto:", e.dep_postparto.value_counts(dropna=False).to_dict())
    return e.drop_duplicates("folio")


def extras_2012():
    df, _ = pyreadstat.read_dta(str(INT / "2012/Entrevistada_2012.dta"),
                                usecols=["folio", "b64"])
    df["folio"] = num(df.folio).astype("int64")
    e = pd.DataFrame({"folio": df.folio, "dep_madre12": sino(df.b64)})
    return e.drop_duplicates("folio")


def frame_adolescentes():
    d = sm27.build()
    d = (d.merge(extras_2024(), on="folio", how="left")
          .merge(extras_2010(), on="folio", how="left")
          .merge(extras_2012(), on="folio", how="left"))
    print("paper_adolescentes:", d.shape, "| EQ:", f"{d.EQ.mean():.0%}",
          "| z_resil:", d.z_resil.notna().sum(),
          "| peso_nacer:", d.peso_nacer.notna().sum(),
          "| viol_pareja:", d.viol_pareja.notna().sum())
    return d


def frame_atricion():
    h10, _ = pyreadstat.read_dta(str(INT / "2010/Hogar_2010.dta"),
                                 usecols=["folio", "a16", "a18", "a19", "b2n"])
    h10["folio"] = num(h10.folio).astype("int64")
    madre = (h10[num(h10.a16) == 1].drop_duplicates("folio")
             .set_index("folio")[["a19", "b2n"]])
    base = pd.DataFrame({"folio": h10.folio.unique()})
    ent, _ = pyreadstat.read_dta(str(INT / "2010/Entrevistada_2010.dta"),
                                 usecols=["folio", "region", "area"])
    ent["folio"] = num(ent.folio).astype("int64")
    ev, _ = pyreadstat.read_dta(str(INT / "2010/Evaluaciones_2010.dta"),
                                usecols=["folio", "edad_meses"])
    ev["folio"] = num(ev.folio).astype("int64")
    base = (base.merge(ent.drop_duplicates("folio"), on="folio", how="left")
                .merge(ev.drop_duplicates("folio"), on="folio", how="left")
                .join(madre, on="folio"))
    # fecha de nacimiento: exacta si el folio llega a 2017/2024; si no,
    # aproximada con la edad en la evaluación 2010 (campo ~sep-2010).
    ad = pd.read_pickle(OUT / "paper_adolescentes.pkl")[["folio", "birth_ym"]]
    ro, _ = pyreadstat.read_sav(
        str(INT / "2017/Base Cuidador Principal ELPI III (SPSS).sav"),
        usecols=["folio", "fechanacimientons"])
    ro["folio"] = num(ro.folio).astype("int64")
    bd17 = ro.groupby("folio", as_index=False).first()
    b = pd.to_datetime(bd17.fechanacimientons, errors="coerce")
    bd17["birth_ym17"] = b.dt.year * 12 + (b.dt.month - 1)
    base = (base.merge(ad, on="folio", how="left")
                .merge(bd17[["folio", "birth_ym17"]], on="folio", how="left"))
    aprox = (2010 * 12 + 8) - num(base.edad_meses)
    base["birth_ym"] = base.birth_ym.fillna(base.birth_ym17).fillna(aprox)
    base["edadq_m"] = (2010 * 12 + 1) - base.birth_ym
    base = base[base.edadq_m.between(0, 59)]
    base["bin"] = pd.cut(base.edadq_m, [0, 12, 24, 36, 60], right=False,
                         labels=["0-11m", "12-23m", "24-35m", "36-59m"])
    base["EQ"] = num(base.region).isin(sm27.EQ_REGIONS).astype(float)
    for yr, f in [("2012", "2012/Entrevistada_2012.dta")]:
        d12, _ = pyreadstat.read_dta(str(INT / f), usecols=["folio"])
        base["in2012"] = base.folio.isin(
            set(num(d12.folio).astype("int64"))).astype(float)
    base["in2017"] = base.folio.isin(set(bd17.folio)).astype(float)
    y24, _ = pyreadstat.read_dta(
        str(INT / "2024/Base evaluaciones Stata.dta"), usecols=["folio"])
    base["in2024"] = base.folio.isin(
        set(num(y24.folio).astype("int64"))).astype(float)
    print("paper_atricion:", base.shape,
          "| in2024:", f"{base.in2024.mean():.1%}",
          "| EQ:", f"{base.EQ.mean():.0%}",
          "| bins:", base.bin.value_counts().to_dict())
    return base


def main():
    OUT.mkdir(exist_ok=True)
    d = frame_adolescentes()
    d.to_pickle(OUT / "paper_adolescentes.pkl")
    a = frame_atricion()
    a.to_pickle(OUT / "paper_atricion.pkl")
    print("-> data/processed/paper_adolescentes.pkl y paper_atricion.pkl")


if __name__ == "__main__":
    main()
