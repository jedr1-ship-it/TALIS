#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fase 2 — dosis sísmica continua por comuna de selección.

Pipeline:
  1. Nombres de las comunas de selección (CUT del crosswalk estrato24):
     API oficial DPA (apis.digital.gob.cl/dpa/comunas) + mapeo manual de los
     CUT antiguos de Ñuble (84xx, provincia que en 2018 pasó a región 16).
  2. Centroides: Nominatim (OpenStreetMap), 1 consulta/seg, con caché.
  3. ShakeMap del USGS para el Maule 2010 (evento oficial): grid.xml con
     PGA (%g) y MMI en malla lat/lon → vecino más cercano al centroide.
     Comunas fuera de la malla → PGA=0 (lejos de la ruptura).
  4. Distancia al epicentro (km, haversine) como dosis alternativa.

Salida: data/processed/pga_comuna.csv (cut, nombre, lat, lon, pga, mmi,
        dist_epi_km, fuente_coord)
Uso:    python3 scripts/14_pga_dose.py
"""
import json
import math
import subprocess
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("data/processed")
CACHE = Path("data/interim/pga_cache")
EVENT = "official20100227063411530_30"
REGION_NOM = {1: "Región de Tarapacá", 2: "Región de Antofagasta",
              3: "Región de Atacama", 4: "Región de Coquimbo",
              5: "Región de Valparaíso", 6: "Región de O'Higgins",
              7: "Región del Maule", 8: "Región del Biobío",
              9: "Región de la Araucanía", 10: "Región de Los Lagos",
              11: "Región de Aysén", 12: "Región de Magallanes",
              13: "Región Metropolitana de Santiago",
              14: "Región de Los Ríos", 15: "Región de Arica y Parinacota"}

NUBLE_84 = {  # CUT 2010 de la antigua provincia de Ñuble (región 8)
    8401: "Chillán", 8402: "Bulnes", 8403: "Cobquecura", 8404: "Coelemu",
    8405: "Coihueco", 8406: "Chillán Viejo", 8407: "El Carmen",
    8408: "Ninhue", 8409: "Ñiquén", 8410: "Pemuco", 8411: "Pinto",
    8412: "Portezuelo", 8413: "Quillón", 8414: "Quirihue",
    8415: "Ránquil", 8416: "San Carlos", 8417: "San Fabián",
    8418: "San Ignacio", 8419: "San Nicolás", 8420: "Treguaco",
    8421: "Yungay"}


def curl(url, out=None, extra=None):
    cmd = ["curl", "-sSL", "--max-time", "120",
           "-H", "User-Agent: TALIS-ELPI-research/1.0 (academico)"]
    if extra:
        cmd += extra
    if out:
        cmd += ["-o", str(out)]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=(out is None))
    if r.returncode != 0:
        raise RuntimeError(f"curl fallo {url}: {r.stderr[:200]}")
    return r.stdout if out is None else None


def nombres_comunas(cuts):
    """CUT→nombre desde la tabla de Wikipedia (Anexo:Comunas de Chile),
    con los CUT antiguos de Ñuble resueltos a mano."""
    CACHE.mkdir(parents=True, exist_ok=True)
    page = CACHE / "comunas_wiki.html"
    if not page.exists():
        curl("https://es.wikipedia.org/wiki/Anexo:Comunas_de_Chile", out=page)
    tablas = pd.read_html(str(page))
    wiki = {}
    for t in tablas:
        cols = [str(c).lower() for c in t.columns]
        icut = next((i for i, c in enumerate(cols) if "cut" in c), None)
        inom = next((i for i, c in enumerate(cols)
                     if "nombre" in c or "comuna" in c), None)
        if icut is None or inom is None or len(t) < 100:
            continue
        for _, r in t.iterrows():
            try:
                wiki[int(r.iloc[icut])] = str(r.iloc[inom]).strip()
            except (ValueError, TypeError):
                pass
    print(f"wikipedia: {len(wiki)} comunas en la tabla")
    out, falta = {}, []
    for cut in cuts:
        if cut in wiki:
            out[cut] = wiki[cut]
        elif cut in NUBLE_84:
            out[cut] = NUBLE_84[cut]
        else:
            falta.append(cut)
    print(f"nombres: {len(out)}/{len(cuts)} resueltos; faltan: {falta}")
    return out


def norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().replace("'", "").replace("-", " ").strip()


def wikidata_comunas():
    """Una sola consulta SPARQL: todas las comunas de Chile con coords."""
    q = ("SELECT ?itemLabel ?coord WHERE { ?item wdt:P31 wd:Q2555896 . "
         "?item wdt:P625 ?coord . SERVICE wikibase:label "
         "{ bd:serviceParam wikibase:language \"es\" . } }")
    from urllib.parse import quote
    raw = curl("https://query.wikidata.org/sparql?format=json&query="
               + quote(q))
    js = json.loads(raw)
    out = {}
    for b in js["results"]["bindings"]:
        lab = b["itemLabel"]["value"]
        pt = b["coord"]["value"]          # 'Point(lon lat)'
        lon, lat = (float(x) for x in
                    pt.replace("Point(", "").rstrip(")").split())
        if -57 < lat < -17 and -78 < lon < -66:
            out[norm(lab)] = (lat, lon)
    print(f"wikidata: {len(out)} comunas con coordenadas")
    return out


def centroide_nominatim(nombre, region):
    reg = REGION_NOM.get(region, "")
    for q in (f"{nombre}, {reg}, Chile", f"{nombre}, Chile"):
        try:
            raw = curl("https://nominatim.openstreetmap.org/search?"
                       f"q={q.replace(' ', '+')}&format=json&limit=1")
            js = json.loads(raw)
        except Exception:
            js = []
        if js:
            la, lo = float(js[0]["lat"]), float(js[0]["lon"])
            if -57 < la < -17 and -78 < lo < -66:
                return la, lo
        time.sleep(3.0)
    return None


def coords(nombres):
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_f = CACHE / "centroides.csv"
    cache = {}
    if cache_f.exists():
        for _, r in pd.read_csv(cache_f).iterrows():
            if pd.notna(r.lat):
                cache[int(r.cut)] = (r.lat, r.lon)
    wd = wikidata_comunas()
    rows, miss = [], []
    for cut, nom in nombres.items():
        c = cache.get(cut) or wd.get(norm(nom))
        if c is None:
            miss.append((cut, nom))
            rows.append((cut, nom, np.nan, np.nan))
        else:
            rows.append((cut, nom, c[0], c[1]))
    print(f"tras wikidata/cache: faltan {len(miss)}: "
          f"{[n for _, n in miss]}")
    for i, (cut, nom) in enumerate(miss):
        c = centroide_nominatim(nom, cut // 1000)
        if c:
            for j, r in enumerate(rows):
                if r[0] == cut:
                    rows[j] = (cut, nom, c[0], c[1])
        time.sleep(3.0)
    df = pd.DataFrame(rows, columns=["cut", "nombre", "lat", "lon"])
    df.to_csv(cache_f, index=False)
    print(f"centroides: {df.lat.notna().sum()}/{len(df)} con coordenadas")
    return df


def shakemap_grid():
    CACHE.mkdir(parents=True, exist_ok=True)
    gxml = CACHE / "grid.xml"
    if not gxml.exists():
        raw = curl("https://earthquake.usgs.gov/fdsnws/event/1/query?"
                   f"eventid={EVENT}&format=geojson")
        ev = json.loads(raw)
        prods = ev["properties"]["products"]["shakemap"]
        prod = prods[0]
        cont = prod["contents"]
        key = next((k for k in ("download/grid.xml", "download/grid.xml.zip")
                    if k in cont), None)
        url = cont[key]["url"]
        print("shakemap:", url)
        dst = CACHE / ("grid.xml.zip" if key.endswith("zip") else "grid.xml")
        curl(url, out=dst)
        if dst.suffix == ".zip":
            with zipfile.ZipFile(dst) as z:
                n = [x for x in z.namelist() if x.endswith("grid.xml")][0]
                gxml.write_bytes(z.read(n))
        epi = ev["geometry"]["coordinates"]
        (CACHE / "epicentro.json").write_text(json.dumps(epi))
    txt = gxml.read_text()
    # campos de grid_data según <grid_field>
    import re
    fields = re.findall(r'<grid_field index="\d+" name="([A-Za-z0-9_]+)"',
                        txt)
    body = txt.split("<grid_data>")[1].split("</grid_data>")[0].strip()
    arr = np.loadtxt(body.splitlines())
    g = pd.DataFrame(arr, columns=[f.lower() for f in fields])
    print("grid:", g.shape, "campos:", list(g.columns),
          "| lat", g.lat.min(), "a", g.lat.max(),
          "| lon", g.lon.min(), "a", g.lon.max())
    return g


def haversine(la1, lo1, la2, lo2):
    R = 6371.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    dp = p2 - p1
    a = (math.sin(dp / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def main():
    xw = pd.read_csv("data/processed/crosswalk_estrato24_comuna.csv")
    cuts = sorted(int(c) for c in xw.cut_comuna_seleccion.unique())
    print(f"{len(cuts)} comunas de selección")
    noms = nombres_comunas(cuts)
    cc = coords(noms)
    g = shakemap_grid()
    epi = json.loads((CACHE / "epicentro.json").read_text())
    elon, elat = epi[0], epi[1]
    print("epicentro:", elat, elon)
    glat, glon = g.lat.to_numpy(), g.lon.to_numpy()
    pga_col = "pga" if "pga" in g.columns else None
    mmi_col = "mmi" if "mmi" in g.columns else None
    rows = []
    for _, r in cc.iterrows():
        if pd.isna(r.lat):
            rows.append((r.cut, r.nombre, np.nan, np.nan, np.nan, np.nan,
                         np.nan, "sin_coord"))
            continue
        dist = haversine(r.lat, r.lon, elat, elon)
        inside = (g.lat.min() - .05 <= r.lat <= g.lat.max() + .05 and
                  g.lon.min() - .05 <= r.lon <= g.lon.max() + .05)
        if inside:
            d2 = (glat - r.lat) ** 2 + (glon - r.lon) ** 2
            i = int(np.argmin(d2))
            pga = g[pga_col].iloc[i] if pga_col else np.nan
            mmi = g[mmi_col].iloc[i] if mmi_col else np.nan
            src = "grid"
        else:
            pga, mmi, src = 0.0, 1.0, "fuera_grid"
        rows.append((r.cut, r.nombre, r.lat, r.lon, pga, mmi, dist, src))
    out = pd.DataFrame(rows, columns=["cut", "nombre", "lat", "lon", "pga",
                                      "mmi", "dist_epi_km", "fuente"])
    OUT.mkdir(exist_ok=True)
    out.to_csv(OUT / "pga_comuna.csv", index=False)
    print(out.fuente.value_counts().to_dict())
    print("PGA: media", f"{out.pga.mean():.1f}", "| p90",
          f"{out.pga.quantile(.9):.1f}", "| >0:", (out.pga > 0).sum())
    print("-> data/processed/pga_comuna.csv")


if __name__ == "__main__":
    main()
