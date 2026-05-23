# -*- coding: utf-8 -*-
"""
Carga y normalización de datos — Recepción de Vehículos
OPTIMIZACIONES v2:
 - pandas importado DENTRO de las funciones → no bloquea arranque de la app.
 - Lectura de Excel en UN SOLO PASO (se eliminó la doble lectura I/O).
 - Patrones regex compilados una sola vez al cargar el módulo.
"""
import re, os, calendar
from datetime import date, timedelta

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# ── Patrones compilados una sola vez ─────────────────────────────────────────
_RE_HMS  = re.compile(r'^(\d{1,2}):(\d{2})(?::\d{2})?$')
_RE_AMPM = re.compile(r'^(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?', re.I)

def _hora_a_min(v):
    """Convierte cualquier formato de hora a minutos desde medianoche."""
    if v is None: return None
    try:
        import math
        if isinstance(v, float) and math.isnan(v): return None
    except Exception: pass
    if hasattr(v, 'hour'): return v.hour * 60 + v.minute
    s = str(v).strip()
    m = _RE_HMS.match(s)
    if m: return int(m.group(1)) * 60 + int(m.group(2))
    m = _RE_AMPM.match(s)
    if m:
        h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3).lower()
        if ap == 'p' and h != 12: h += 12
        if ap == 'a' and h == 12: h = 0
        return h * 60 + mi
    return None

def _min_to_str(m):
    if m is None: return ""
    try:
        import math
        if isinstance(m, float) and math.isnan(m): return ""
    except Exception: pass
    return f"{int(m)//60:02d}:{int(m)%60:02d}"

# ── Lectura Excel en un solo paso ─────────────────────────────────────────────
def _leer_excel_una_vez(ruta, sheet=0, engine=None, buscar_col="fecha", max_scan=15):
    """
    Lee el archivo UNA sola vez, detecta la fila de cabecera buscando
    'buscar_col' en la primera columna, devuelve DataFrame listo.
    Elimina la doble-lectura que duplicaba el tiempo de I/O.
    """
    import pandas as pd
    kw = dict(sheet_name=sheet, header=None)
    if engine: kw["engine"] = engine
    raw = pd.read_excel(ruta, **kw)
    hrow = 6
    for i in range(min(max_scan, len(raw))):
        if str(raw.iloc[i, 0]).strip().lower() == buscar_col:
            hrow = i; break
    df = raw.iloc[hrow:].copy()
    df.columns = df.iloc[0].astype(str).str.strip()
    df = df.iloc[1:].reset_index(drop=True)
    return df

# ── Carga Agenda ──────────────────────────────────────────────────────────────
def cargar_agenda(ruta, f_desde, f_hasta):
    import pandas as pd
    df = _leer_excel_una_vez(ruta, sheet=0, buscar_col="fecha")

    col_estado    = next((c for c in df.columns if "recep" in c.lower() and "estado" in c.lower()), None)
    col_proveedor = next((c for c in df.columns if "proveedor" in c.lower()), None)
    col_estibas   = next((c for c in df.columns if "estiba" in c.lower()), None)
    col_hora      = next((c for c in df.columns if "hora" in c.lower() and "orden" not in c.lower()), None)
    col_tipo_veh  = next((c for c in df.columns if "veh" in c.lower() and "tipo" in c.lower()), None)

    df["_fecha"] = pd.to_datetime(df[df.columns[0]], errors="coerce").dt.date
    df = df.dropna(subset=["_fecha"])
    df = df[(df["_fecha"] >= f_desde) & (df["_fecha"] <= f_hasta)].copy()

    if col_proveedor:
        df = df[df[col_proveedor].astype(str).str.upper().str.strip() != "INVENTARIO"]

    df["_estado"]        = df[col_estado].astype(str).str.strip().str.upper() if col_estado else ""
    df["_proveedor"]     = df[col_proveedor].astype(str).str.strip() if col_proveedor else ""
    df["_estibas"]       = pd.to_numeric(df[col_estibas], errors="coerce").fillna(0) if col_estibas else 0
    df["_hora_cita_min"] = df[col_hora].apply(_hora_a_min) if col_hora else None
    df["_hora_cita_str"] = df["_hora_cita_min"].apply(_min_to_str)
    df["_tipo_veh"]      = df[col_tipo_veh].astype(str).str.strip() if col_tipo_veh else ""
    return df

# ── Carga Control Citas ───────────────────────────────────────────────────────
def cargar_control(ruta, f_desde, f_hasta):
    import pandas as pd
    df = _leer_excel_una_vez(ruta, sheet="HOJA1", engine="openpyxl",
                              buscar_col="fecha", max_scan=10)

    col_prov    = next((c for c in df.columns if "proveedor" in c.lower()), None)
    col_novedad = next((c for c in df.columns if "novedad"   in c.lower()), None)
    col_tiempo  = next((c for c in df.columns if "tiempo"    in c.lower()), None)
    col_cita    = next((c for c in df.columns if "senda"     in c.lower() or "cita" in c.lower()), None)
    col_inicio  = next((c for c in df.columns if "inicio"    in c.lower() and "hora" in c.lower()), None)
    col_fin     = next((c for c in df.columns if "final"     in c.lower() or "fin"   in c.lower()), None)
    col_placa   = next((c for c in df.columns if "placa"     in c.lower()), None)

    col_fecha = next((c for c in df.columns if c.upper() == "FECHA"), df.columns[0])
    df["_fecha"] = pd.to_datetime(df[col_fecha], errors="coerce").dt.date
    df = df.dropna(subset=["_fecha"])
    df = df[(df["_fecha"] >= f_desde) & (df["_fecha"] <= f_hasta)].copy()

    df["_proveedor"] = df[col_prov].astype(str).str.strip().str.upper() if col_prov else ""
    df["_novedad"]   = df[col_novedad].astype(str).str.strip().str.upper() if col_novedad else ""

    def a_min(v):
        try:
            import math
            if isinstance(v, float) and math.isnan(v): return 0.0
        except Exception: pass
        if hasattr(v, "total_seconds"): return v.total_seconds() / 60
        if isinstance(v, (int, float)):  return float(v) * 1440
        return 0.0

    df["_min"]        = df[col_tiempo].apply(a_min) if col_tiempo else 0.0
    df["_cita_min"]   = df[col_cita].apply(_hora_a_min)   if col_cita   else None
    df["_inicio_min"] = df[col_inicio].apply(_hora_a_min) if col_inicio else None
    df["_fin_min"]    = df[col_fin].apply(_hora_a_min)    if col_fin    else None
    df["_cita_str"]   = df["_cita_min"].apply(_min_to_str)
    df["_inicio_str"] = df["_inicio_min"].apply(_min_to_str)
    df["_fin_str"]    = df["_fin_min"].apply(_min_to_str)

    if df["_cita_min"].notna().any() and df["_inicio_min"].notna().any():
        df["_retraso"] = df["_inicio_min"] - df["_cita_min"]
    else:
        df["_retraso"] = None

    df["_placa"] = df[col_placa].astype(str).str.strip() if col_placa else ""
    return df

# ── Calcular rango de fechas ──────────────────────────────────────────────────
def calcular_rango(tipo, ano, num, f_ini=None, f_fin=None):
    if tipo == "Semana":
        d = date(ano, 1, 4)
        lunes = d - timedelta(days=d.weekday()) + timedelta(weeks=num - 1)
        return lunes, lunes + timedelta(days=6), f"Semana {num} - {ano}"
    elif tipo == "Mes":
        fd = date(ano, num, 1)
        return fd, date(ano, num, calendar.monthrange(ano, num)[1]), f"{MESES[num-1]} {ano}"
    elif tipo == "Bimestre":
        m = (num - 1) * 2 + 1; m2 = m + 1
        return date(ano, m, 1), date(ano, m2, calendar.monthrange(ano, m2)[1]), f"Bimestre {num} - {ano}"
    elif tipo == "Trimestre":
        m = (num - 1) * 3 + 1; m2 = m + 2
        return date(ano, m, 1), date(ano, m2, calendar.monthrange(ano, m2)[1]), f"Trimestre {num} - {ano}"
    elif tipo == "Semestre":
        m = 1 if num == 1 else 7; m2 = m + 5
        return date(ano, m, 1), date(ano, m2, calendar.monthrange(ano, m2)[1]), f"Semestre {num} - {ano}"
    elif tipo == "Año":
        return date(ano, 1, 1), date(ano, 12, 31), f"Año {ano}"
    elif tipo == "Rango":
        return f_ini, f_fin, f"{f_ini.strftime('%d/%m/%Y')} - {f_fin.strftime('%d/%m/%Y')}"
