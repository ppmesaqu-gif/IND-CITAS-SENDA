# -*- coding: utf-8 -*-
import re, os, json
"""Dashboard HTML Operativo v2 — Interactivo, pastel, con análisis de horas"""
import os, json
from datetime import date

def generar_dashboard_operativo(df_ag, df_cc, label, fd, fh, carpeta, logo_path=None):
    import pandas as pd

    total   = len(df_ag)
    recib   = int((df_ag["_estado"]=="RECIBIDO").sum())
    rechaz  = int((df_ag["_estado"]=="RECHAZADO").sum())
    no_ll   = int(df_ag["_estado"].str.contains("LLEG",na=False).sum())
    pend    = int((df_ag["_estado"]=="PENDIENTE").sum())
    pct_ef  = recib/total if total else 0
    fecha_g = date.today().strftime("%d/%m/%Y")

    # ── Evolucion diaria (todos los datos para filtros JS)
    df2 = df_ag.copy(); df2["_ds"] = df2["_fecha"].astype(str)
    ev = df2.groupby("_ds").agg(
        total    =("_estado","count"),
        recibidos=("_estado",lambda x:(x=="RECIBIDO").sum()),
        rechazados=("_estado",lambda x:(x=="RECHAZADO").sum()),
        no_llego =("_estado",lambda x:x.str.contains("LLEG",na=False).sum()),
    ).reset_index().sort_values("_ds")
    evo_fechas = ev["_ds"].tolist()
    evo_tot    = ev["total"].tolist()
    evo_rec    = ev["recibidos"].tolist()
    evo_rch    = ev["rechazados"].tolist()
    evo_nll    = ev["no_llego"].tolist()
    evo_pct    = [round(r/t*100,1) if t else 0 for r,t in zip(evo_rec,evo_tot)]

    # ── Distribución por hora de cita
    hora_dist = {}
    if "_hora_cita_min" in df_ag.columns:
        h_ok = df_ag["_hora_cita_min"].dropna()
        for m in h_ok:
            h = int(m)//60
            hora_dist[h] = hora_dist.get(h,0)+1
    h_labels = [f"{h:02d}:00" for h in sorted(hora_dist)]
    h_vals   = [hora_dist[h] for h in sorted(hora_dist)]

    # ── Analisis alineacion cita vs inicio real
    ret_data   = {"puntual":0,"tarde":0,"anticipado":0,"prom":0}
    ret_por_hr = {}
    if "_retraso" in df_cc.columns and df_cc["_retraso"].notna().any():
        ret = df_cc["_retraso"].dropna()
        ret_data["puntual"]    = int((ret.abs()<=5).sum())
        ret_data["tarde"]      = int((ret>5).sum())
        ret_data["anticipado"] = int((ret<-5).sum())
        ret_data["prom"]       = round(ret.mean(),1)
        # por hora de cita
        df_hr = df_cc[df_cc["_cita_min"].notna() & df_cc["_retraso"].notna()].copy()
        df_hr["_h"] = (df_hr["_cita_min"]//60).astype(int)
        hr_grp = df_hr.groupby("_h")["_retraso"].mean()
        ret_por_hr = {int(k):round(v,1) for k,v in hr_grp.items()}

    # ── Proveedores (dataset completo para tabla filtrable)
    gp = df_ag.groupby("_proveedor").agg(
        visitas   =("_estado","count"),
        recibidos =("_estado",lambda x:(x=="RECIBIDO").sum()),
        rechazados=("_estado",lambda x:(x=="RECHAZADO").sum()),
        no_llego  =("_estado",lambda x:x.str.contains("LLEG",na=False).sum()),
    ).reset_index()
    gp["pct_ef"]     = (gp["recibidos"]/gp["visitas"].replace(0,1)*100).round(1)
    gp["incumplidos"]= gp["rechazados"]+gp["no_llego"]
    # Top clientes: primero los más críticos (incumplidos desc), máx 50 para tabla
    gp_json = (gp.sort_values(["incumplidos","visitas"], ascending=[False,False])
                 .head(50)
                 .to_dict("records"))
    for r in gp_json:
        for k in list(r.keys()):
            r[k] = int(r[k]) if isinstance(r[k], (int,)) else \
                   float(round(r[k],1)) if isinstance(r[k],float) else r[k]

    # ── Novedades CC
    nov = df_cc.groupby("_novedad").size().sort_values(ascending=False).reset_index(name="n")
    nov_lbl = nov["_novedad"].str.strip().tolist()
    nov_val = nov["n"].tolist()

    # ── Tiempos CC por hora de cita (alineación horaria)
    cc_hora_lbl, cc_hora_prom, cc_hora_cnt = [], [], []
    if "_cita_min" in df_cc.columns and df_cc["_cita_min"].notna().any():
        df_th = df_cc[df_cc["_min"]>0].copy()
        df_th["_h"] = (df_th["_cita_min"].fillna(0)//60).astype(int)
        th = df_th.groupby("_h")["_min"].agg(["mean","count"]).reset_index()
        cc_hora_lbl  = [f"{int(r['_h']):02d}:00" for _,r in th.iterrows()]
        cc_hora_prom = [round(r["mean"],1) for _,r in th.iterrows()]
        cc_hora_cnt  = [int(r["count"]) for _,r in th.iterrows()]

    # ── Logo
    logo_b64 = ""
    if logo_path and os.path.exists(logo_path):
        import base64
        with open(logo_path,"rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    logo_html = (f'<img src="data:image/jpeg;base64,{logo_b64}" class="logo">'
                 if logo_b64 else
                 '<span class="logo-text">ALPINA</span>')

    # Pre-calcular JSONs para evitar conflicto con f-string
    datos_ag_json = json.dumps([
        {"fecha": str(r["_fecha"]), "estado": r["_estado"],
         "proveedor": r["_proveedor"]}
        for _,r in df_ag.iterrows()
    ])
    datos_ag_mes_json = json.dumps([
        {"fecha": str(r["_fecha"]), "estado": r["_estado"],
         "proveedor": r["_proveedor"],
         "mes": str(r["_fecha"])[:7].replace("-", "-")}
        for _,r in df_ag.iterrows()
    ])

    HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard Operativo — {label}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{{
  --bg:#F7F9FC; --card:#FFFFFF; --border:#E2E8F0;
  --azul:#3B82F6; --azul-p:#DBEAFE; --azul-t:#1D4ED8;
  --verde:#22C55E; --verde-p:#DCFCE7; --verde-t:#15803D;
  --rojo:#EF4444;  --rojo-p:#FEE2E2;  --rojo-t:#B91C1C;
  --nar:#F59E0B;   --nar-p:#FEF3C7;   --nar-t:#B45309;
  --gris:#6B7280;  --texto:#1E293B;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--texto);font-size:14px}}
/* HEADER */
.header{{background:#fff;border-bottom:3px solid var(--azul);padding:16px 28px;
          display:flex;align-items:center;gap:16px;box-shadow:0 2px 8px #0001}}
.logo{{height:48px;border-radius:6px}}
.logo-text{{font-size:22px;font-weight:900;color:var(--azul-t);
            background:var(--azul-p);padding:6px 14px;border-radius:8px}}
.hd{{flex:1}}
.hd h1{{font-size:18px;font-weight:700;color:var(--azul-t)}}
.hd .sub{{font-size:12px;color:var(--gris);margin-top:3px}}
.badge{{display:inline-block;background:var(--azul-p);color:var(--azul-t);
         border-radius:20px;padding:3px 14px;font-size:11px;font-weight:600;margin-top:5px}}
/* FILTROS */
.filtros{{background:#fff;border-bottom:1px solid var(--border);padding:10px 28px;
           display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
.filtros label{{font-size:12px;font-weight:600;color:var(--gris)}}
.filtros select,.filtros input{{border:1px solid var(--border);border-radius:6px;
  padding:5px 10px;font-size:12px;background:#fff;color:var(--texto);outline:none}}
.filtros select:focus,.filtros input:focus{{border-color:var(--azul)}}
.btn-reset{{background:var(--azul-p);color:var(--azul-t);border:none;border-radius:6px;
             padding:5px 14px;font-size:12px;font-weight:600;cursor:pointer}}
.btn-reset:hover{{background:var(--azul);color:#fff}}
/* MAIN */
.main{{padding:20px 28px;max-width:1600px;margin:0 auto}}
/* KPIs */
.kpis{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:20px}}
.kpi{{background:#fff;border-radius:12px;padding:16px;border-left:4px solid var(--c);
       box-shadow:0 1px 4px #0001}}
.kpi .val{{font-size:28px;font-weight:800;color:var(--c)}}
.kpi .lbl{{font-size:11px;font-weight:600;color:var(--gris);margin-top:4px;text-transform:uppercase}}
.kpi .sub{{font-size:11px;color:#94A3B8;margin-top:3px}}
/* Cards */
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}}
.card{{background:#fff;border-radius:12px;padding:18px;box-shadow:0 1px 4px #0001;border:1px solid var(--border)}}
.card h3{{font-size:12px;font-weight:700;color:var(--azul-t);margin-bottom:14px;
           text-transform:uppercase;letter-spacing:.5px;display:flex;align-items:center;gap:6px}}
canvas{{max-height:240px}}
/* Tabla filtrable */
.tbl-wrap{{overflow-x:auto}}
.search-box{{width:100%;border:1px solid var(--border);border-radius:6px;padding:7px 12px;
              font-size:12px;margin-bottom:10px;outline:none}}
.search-box:focus{{border-color:var(--azul)}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:var(--azul-p);color:var(--azul-t);padding:8px 10px;text-align:left;
    font-weight:700;font-size:11px;cursor:pointer;user-select:none}}
th:hover{{background:#BFDBFE}}
th.sort-asc::after{{content:" ▲"}} th.sort-desc::after{{content:" ▼"}}
td{{padding:7px 10px;border-bottom:1px solid var(--border)}}
tr:hover td{{background:#F8FAFC}}
.prov{{max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500}}
.chip{{display:inline-block;border-radius:8px;padding:2px 10px;font-size:11px;font-weight:700}}
.chip-ok{{background:var(--verde-p);color:var(--verde-t)}}
.chip-warn{{background:var(--nar-p);color:var(--nar-t)}}
.chip-mal{{background:var(--rojo-p);color:var(--rojo-t)}}
/* Nota estibas */
.nota{{background:#FEF9C3;border:1px solid #FDE047;border-radius:8px;padding:8px 14px;
        font-size:11px;color:#713F12;margin-bottom:12px}}
.footer{{text-align:center;font-size:10px;color:#94A3B8;padding:16px;margin-top:8px}}
/* Retraso gauge */
.gauge-row{{display:flex;gap:10px;margin-bottom:10px}}
.gauge-box{{flex:1;background:var(--bg);border-radius:8px;padding:10px;text-align:center;border:1px solid var(--border)}}
.gauge-box .gv{{font-size:22px;font-weight:800}}
.gauge-box .gl{{font-size:10px;color:var(--gris);text-transform:uppercase;font-weight:600}}
</style>
</head>
<body>
<div class="header">
  {logo_html}
  <div class="hd">
    <h1>📊 DASHBOARD OPERATIVO — RECEPCIÓN DE VEHÍCULOS</h1>
    <div class="sub">Planta Entrerrios · Análisis detallado de recepciones · Generado: {fecha_g}</div>
    <div class="badge">📅 {label} &nbsp;·&nbsp; {fd.strftime("%d/%m/%Y")} al {fh.strftime("%d/%m/%Y")} &nbsp;·&nbsp; {(fh-fd).days+1} días</div>
  </div>
</div>

<!-- FILTROS INTERACTIVOS -->
<div class="filtros">
  <label>📅 Desde:</label>
  <input type="date" id="fi" onchange="filtrar()">
  <label>Hasta:</label>
  <input type="date" id="ff" onchange="filtrar()">
  <label>Estado:</label>
  <select id="sel_estado" onchange="filtrar()">
    <option value="">Todos</option>
    <option value="RECIBIDO">Recibido</option>
    <option value="NO LLEGÓ">No Llegó</option>
    <option value="RECHAZADO">Rechazado</option>
    <option value="PENDIENTE">Pendiente</option>
  </select>
  <button class="btn-reset" onclick="resetFiltros()">↺ Resetear</button>
  <span id="lbl_filtro" style="font-size:12px;color:var(--azul-t);font-weight:600"></span>
</div>

<div class="main">

<!-- KPIs -->
<div class="kpis" id="kpi_wrap">
  <div class="kpi" style="--c:var(--azul)">
    <div class="val" id="k_total">{total}</div>
    <div class="lbl">Agendados</div>
    <div class="sub">Total período</div>
  </div>
  <div class="kpi" style="--c:{'var(--verde)' if pct_ef>=.85 else 'var(--rojo)'}">
    <div class="val" id="k_ef">{pct_ef:.1%}</div>
    <div class="lbl">Efectividad</div>
    <div class="sub">Meta ≥85%</div>
  </div>
  <div class="kpi" style="--c:var(--verde)">
    <div class="val" id="k_rec">{recib}</div>
    <div class="lbl">Recibidos</div>
    <div class="sub">{recib/total:.0%} del total</div>
  </div>
  <div class="kpi" style="--c:var(--nar)">
    <div class="val" id="k_nll">{no_ll}</div>
    <div class="lbl">No Llegó</div>
    <div class="sub">{no_ll/total:.0%} del total</div>
  </div>
  <div class="kpi" style="--c:var(--rojo)">
    <div class="val" id="k_rch">{rechaz}</div>
    <div class="lbl">Rechazados</div>
    <div class="sub">{rechaz/total:.0%} del total</div>
  </div>
  <div class="kpi" style="--c:#8B5CF6">
    <div class="val" id="k_pend">{pend}</div>
    <div class="lbl">Pendientes</div>
    <div class="sub">Sin clasificar</div>
  </div>
</div>

<!-- Nota estibas -->
<div class="nota">
  ⚠️ <strong>Nota sobre Estibas:</strong> Este dato es ingresado manualmente en el agendamiento
  y puede contener errores. Úselo con referencia, no para métricas críticas.
</div>

<!-- Evolución + Estado -->
<div class="grid2">
  <div class="card">
    <h3>📈 Evolución Diaria — Agendados vs Recibidos</h3>
    <canvas id="evoChart"></canvas>
  </div>
  <div class="card">
    <h3>🍩 Distribución por Estado</h3>
    <canvas id="estadoChart"></canvas>
  </div>
</div>

<!-- % Ef + Hora de cita -->
<div class="grid2">
  <div class="card">
    <h3>📊 % Efectividad Diaria</h3>
    <canvas id="pctChart"></canvas>
  </div>
  <div class="card">
    <h3>🕐 Distribución de Citas por Hora</h3>
    <canvas id="horaChart"></canvas>
  </div>
</div>

<!-- ANALISIS DE ALINEACIÓN HORARIA -->
<div class="card" style="margin-bottom:16px">
  <h3>⏱️ Alineación Cita vs Ingreso Real</h3>
  <div class="gauge-row">
    <div class="gauge-box">
      <div class="gv" style="color:var(--verde)">{ret_data['puntual']}</div>
      <div class="gl">A tiempo (±5 min)</div>
    </div>
    <div class="gauge-box">
      <div class="gv" style="color:var(--rojo)">{ret_data['tarde']}</div>
      <div class="gl">Tarde (&gt;5 min)</div>
    </div>
    <div class="gauge-box">
      <div class="gv" style="color:var(--azul)">{ret_data['anticipado']}</div>
      <div class="gl">Anticipado (&lt;-5 min)</div>
    </div>
    <div class="gauge-box">
      <div class="gv" style="color:{'var(--verde)' if ret_data['prom']<=5 else 'var(--rojo)'}">{ret_data['prom']:+.0f} min</div>
      <div class="gl">Desvío promedio</div>
    </div>
  </div>
  <canvas id="retChart" style="max-height:200px"></canvas>
</div>

<!-- Tabla proveedores filtrable -->
<div class="card" style="margin-bottom:16px">
  <h3>🏭 Análisis por Proveedor</h3>
  <div class="grid2" style="gap:8px;margin-bottom:8px">
    <input class="search-box" type="text" id="buscar_prov" placeholder="🔍 Buscar proveedor..." onkeyup="filtrarTabla()">
    <div style="display:flex;gap:8px;align-items:center">
      <label style="font-size:12px">Ordenar por:</label>
      <select id="orden_prov" onchange="filtrarTabla()" style="border:1px solid var(--border);border-radius:6px;padding:5px 10px;font-size:12px">
        <option value="visitas">Visitas ↓</option>
        <option value="incumplidos">Incumplimientos ↓</option>
        <option value="pct_ef_asc">% Efectividad ↑</option>
        <option value="pct_ef_desc">% Efectividad ↓</option>
      </select>
    </div>
  </div>
  <div class="tbl-wrap">
    <table id="tbl_prov">
      <thead><tr>
        <th onclick="sortTabla('_proveedor')">Proveedor</th>
        <th onclick="sortTabla('visitas')">Visitas</th>
        <th onclick="sortTabla('recibidos')">Recibidos</th>
        <th onclick="sortTabla('rechazados')">Rechaz.</th>
        <th onclick="sortTabla('no_llego')">No Llegó</th>
        <th onclick="sortTabla('incumplidos')">Incumpl.</th>
        <th onclick="sortTabla('pct_ef')">% Ef.</th>
      </tr></thead>
      <tbody id="tbody_prov"></tbody>
    </table>
  </div>
</div>

<!-- Novedades CC + Tiempo por hora -->
<div class="grid2">
  <div class="card">
    <h3>🚨 Novedades de Descargue</h3>
    <canvas id="novChart"></canvas>
  </div>
  <div class="card">
    <h3>⏱️ Tiempo Prom. Descargue por Hora de Cita (min)</h3>
    <canvas id="tHoraChart"></canvas>
  </div>
</div>

</div>
<div class="footer">Dashboard Operativo · Planta Entrerrios · {fecha_g} · {label} · Datos: agenda {total} reg. / control citas {len(df_cc)} reg.</div>

<script>
// ── DATOS GLOBALES ─────────────────────────────────────────────────────────
const DATOS_AG = {datos_ag_json};

const EVO_F = {json.dumps(evo_fechas)};
const EVO_T = {json.dumps(evo_tot)};
const EVO_R = {json.dumps(evo_rec)};
const EVO_RC= {json.dumps(evo_rch)};
const EVO_NL= {json.dumps(evo_nll)};
const EVO_P = {json.dumps(evo_pct)};
const PROVS  = {json.dumps(gp_json)};
const NOV_L  = {json.dumps(nov_lbl)};
const NOV_V  = {json.dumps(nov_val)};
const H_L    = {json.dumps(h_labels)};
const H_V    = {json.dumps(h_vals)};
const RET    = {json.dumps(ret_por_hr)};
const CC_H_L = {json.dumps(cc_hora_lbl)};
const CC_H_P = {json.dumps(cc_hora_prom)};
const CC_H_C = {json.dumps(cc_hora_cnt)};

// ── PALETA PASTEL ──────────────────────────────────────────────────────────
const C = {{
  azul:"#3B82F6", azulP:"#DBEAFE", verde:"#22C55E", verdeP:"#DCFCE7",
  rojo:"#EF4444",  rojoP:"#FEE2E2", nar:"#F59E0B",   narP:"#FEF3C7",
  lila:"#8B5CF6", lilaP:"#EDE9FE", gris:"#94A3B8",   texto:"#1E293B"
}};

// ── HELPERS ────────────────────────────────────────────────────────────────
const OPTS_BASE = {{
  responsive:true,
  plugins:{{ legend:{{ labels:{{ color:C.texto, font:{{size:11}} }} }} }},
  scales:{{
    x:{{ ticks:{{ color:C.gris, maxRotation:45, font:{{size:9}} }}, grid:{{ color:"#F1F5F9" }} }},
    y:{{ ticks:{{ color:C.gris, font:{{size:10}} }}, grid:{{ color:"#F1F5F9" }} }}
  }}
}};
let charts = {{}};
const ctx = id => document.getElementById(id).getContext('2d');

function mkChart(id, cfg) {{
  if(charts[id]) charts[id].destroy();
  charts[id] = new Chart(ctx(id), cfg);
}}

// ── CHARTS FIJOS ───────────────────────────────────────────────────────────
function dibujarFijos() {{
  // Estado donut
  mkChart('estadoChart', {{type:'doughnut', data:{{
    labels:['Recibidos','No Llegó','Rechazados','Pendientes'],
    datasets:[{{
      data:[{recib},{no_ll},{rechaz},{pend}],
      backgroundColor:[C.verdeP,C.narP,C.rojoP,C.lilaP],
      borderColor:[C.verde,C.nar,C.rojo,C.lila], borderWidth:2
    }}]}},
    options:{{responsive:true,cutout:'60%',
      plugins:{{legend:{{position:'right',labels:{{color:C.texto,font:{{size:11}},boxWidth:14}}}},
        tooltip:{{callbacks:{{label:ctx=>`${{ctx.label}}: ${{ctx.parsed}} (${{(ctx.parsed/{total}*100).toFixed(1)}}%)`}}}}
    }}}}
  }});

  // Horas de cita
  mkChart('horaChart',{{type:'bar',data:{{
    labels:H_L,
    datasets:[{{label:'Vehículos',data:H_V,backgroundColor:C.azulP,borderColor:C.azul,borderWidth:1}}]
  }},options:{{...OPTS_BASE,plugins:{{...OPTS_BASE.plugins,legend:{{display:false}}}}}}}});

  // Novedades
  const NOV_COLORS = NOV_L.map(n=>
    n.includes('SIN NOVEDAD')?C.verdeP:
    (n.includes('PLACA')||n.includes('HORARIO')||n.includes('TARDE'))?C.narP:C.rojoP);
  const NOV_BORDER = NOV_L.map(n=>
    n.includes('SIN NOVEDAD')?C.verde:
    (n.includes('PLACA')||n.includes('HORARIO')||n.includes('TARDE'))?C.nar:C.rojo);
  mkChart('novChart',{{type:'bar',data:{{
    labels:NOV_L.map(n=>n.length>22?n.slice(0,22)+'…':n),
    datasets:[{{label:'Cantidad',data:NOV_V,backgroundColor:NOV_COLORS,borderColor:NOV_BORDER,borderWidth:1}}]
  }},options:{{...OPTS_BASE,indexAxis:'y',plugins:{{...OPTS_BASE.plugins,legend:{{display:false}}}}}}}});

  // Retraso por hora de cita
  const retHrs = Object.keys(RET).map(Number).sort((a,b)=>a-b);
  const retVals= retHrs.map(h=>RET[h]);
  mkChart('retChart',{{type:'bar',data:{{
    labels:retHrs.map(h=>`${{String(h).padStart(2,'0')}}:00`),
    datasets:[{{
      label:'Desvío promedio (min)',
      data:retVals,
      backgroundColor:retVals.map(v=>v>5?C.rojoP:v<-5?C.azulP:C.verdeP),
      borderColor:retVals.map(v=>v>5?C.rojo:v<-5?C.azul:C.verde), borderWidth:1
    }}]
  }},options:{{...OPTS_BASE,
    scales:{{...OPTS_BASE.scales,y:{{...OPTS_BASE.scales.y,ticks:{{...OPTS_BASE.scales.y.ticks,callback:v=>(v>0?'+':'')+v+' min'}}}}}}
  }}}});

  // Tiempo por hora de cita
  mkChart('tHoraChart',{{type:'bar',data:{{
    labels:CC_H_L,
    datasets:[
      {{label:'Prom. min',data:CC_H_P,backgroundColor:CC_H_P.map(v=>v>60?C.rojoP:v>45?C.narP:C.verdeP),
        borderColor:CC_H_P.map(v=>v>60?C.rojo:v>45?C.nar:C.verde),borderWidth:1,yAxisID:'y'}},
      {{label:'# Vehículos',data:CC_H_C,type:'line',borderColor:C.azul,backgroundColor:C.azulP,
        borderWidth:2,pointRadius:4,yAxisID:'y2'}}
    ]
  }},options:{{...OPTS_BASE,
    scales:{{
      x:OPTS_BASE.scales.x,
      y:{{...OPTS_BASE.scales.y,title:{{display:true,text:'Minutos',color:C.gris,font:{{size:10}}}}}},
      y2:{{position:'right',ticks:{{color:C.azul,font:{{size:10}}}},grid:{{drawOnChartArea:false}},
            title:{{display:true,text:'# Vehículos',color:C.azul,font:{{size:10}}}}}}
    }}
  }}}});
}}

// ── FILTROS DINÁMICOS ──────────────────────────────────────────────────────
let sortCol = 'visitas'; let sortDir = -1;

function filtrar() {{
  const fi = document.getElementById('fi').value;
  const ff = document.getElementById('ff').value;
  const est= document.getElementById('sel_estado').value;

  let fil = DATOS_AG.filter(d=>(
    (!fi || d.fecha >= fi) &&
    (!ff || d.fecha <= ff) &&
    (!est|| d.estado === est)
  ));

  // Recalcular KPIs
  const tot  = fil.length || 1;
  const rec  = fil.filter(d=>d.estado==='RECIBIDO').length;
  const nll  = fil.filter(d=>d.estado.includes('LLEG')).length;
  const rch  = fil.filter(d=>d.estado==='RECHAZADO').length;
  const pen  = fil.filter(d=>d.estado==='PENDIENTE').length;
  const ef   = tot>0 ? rec/tot : 0;

  document.getElementById('k_total').textContent = fil.length;
  document.getElementById('k_ef').textContent    = (ef*100).toFixed(1)+'%';
  document.getElementById('k_rec').textContent   = rec;
  document.getElementById('k_nll').textContent   = nll;
  document.getElementById('k_rch').textContent   = rch;
  document.getElementById('k_pend').textContent  = pen;
  document.getElementById('lbl_filtro').textContent = fil.length < DATOS_AG.length ?
    `🔍 Mostrando ${{fil.length}} de ${{DATOS_AG.length}} registros` : '';

  // Evolución con filtro
  const grupoD = {{}};
  fil.forEach(d=>{{
    if(!grupoD[d.fecha]) grupoD[d.fecha]={{tot:0,rec:0,rch:0,nll:0}};
    grupoD[d.fecha].tot++;
    if(d.estado==='RECIBIDO') grupoD[d.fecha].rec++;
    if(d.estado==='RECHAZADO') grupoD[d.fecha].rch++;
    if(d.estado.includes('LLEG')) grupoD[d.fecha].nll++;
  }});
  const fechas = Object.keys(grupoD).sort();
  const gT=fechas.map(f=>grupoD[f].tot), gR=fechas.map(f=>grupoD[f].rec);
  const gRC=fechas.map(f=>grupoD[f].rch), gNL=fechas.map(f=>grupoD[f].nll);
  const gP=gT.map((t,i)=>t>0?+(gR[i]/t*100).toFixed(1):0);

  mkChart('evoChart',{{type:'bar',data:{{
    labels:fechas.map(f=>f.slice(5)),
    datasets:[
      {{label:'Agendados',data:gT,backgroundColor:C.azulP,borderColor:C.azul,borderWidth:1}},
      {{label:'Recibidos',data:gR,backgroundColor:C.verdeP,borderColor:C.verde,borderWidth:1}},
      {{label:'No Llegó', data:gNL,backgroundColor:C.narP,borderColor:C.nar,borderWidth:1}},
      {{label:'Rechazados',data:gRC,backgroundColor:C.rojoP,borderColor:C.rojo,borderWidth:1}},
    ]
  }},options:OPTS_BASE}});

  mkChart('pctChart',{{type:'line',data:{{
    labels:fechas.map(f=>f.slice(5)),
    datasets:[
      {{label:'% Efectividad',data:gP,borderColor:C.verde,backgroundColor:C.verdeP,
        fill:true,tension:.3,pointRadius:3}},
      {{label:'Meta 85%',data:Array(fechas.length).fill(85),borderColor:C.rojo,
        borderDash:[6,4],borderWidth:1.5,pointRadius:0}}
    ]
  }},options:{{...OPTS_BASE,
    scales:{{...OPTS_BASE.scales,y:{{...OPTS_BASE.scales.y,min:0,max:110,
      ticks:{{...OPTS_BASE.scales.y.ticks,callback:v=>v+'%'}}}}}}
  }}}});
}}

function resetFiltros() {{
  document.getElementById('fi').value='';
  document.getElementById('ff').value='';
  document.getElementById('sel_estado').value='';
  filtrar();
}}

// ── TABLA PROVEEDORES FILTRABLE / ORDENABLE ────────────────────────────────
function filtrarTabla() {{
  const q    = document.getElementById('buscar_prov').value.toLowerCase();
  const ord  = document.getElementById('orden_prov').value;
  let datos  = PROVS.filter(r=>r._proveedor.toLowerCase().includes(q));

  if(ord==='visitas')      datos.sort((a,b)=>b.visitas-a.visitas);
  if(ord==='incumplidos')  datos.sort((a,b)=>b.incumplidos-a.incumplidos);
  if(ord==='pct_ef_asc')   datos.sort((a,b)=>a.pct_ef-b.pct_ef);
  if(ord==='pct_ef_desc')  datos.sort((a,b)=>b.pct_ef-a.pct_ef);
  if(sortCol) datos.sort((a,b)=>sortDir*(b[sortCol]>a[sortCol]?1:b[sortCol]<a[sortCol]?-1:0));

  const tbody = document.getElementById('tbody_prov');
  tbody.innerHTML = datos.map(r=>{{
    const chip = r.pct_ef>=80?'chip-ok':r.pct_ef>=60?'chip-warn':'chip-mal';
    return `<tr>
      <td class="prov" title="${{r._proveedor}}">${{r._proveedor}}</td>
      <td>${{r.visitas}}</td><td>${{r.recibidos}}</td>
      <td>${{r.rechazados}}</td><td>${{r.no_llego}}</td>
      <td><strong>${{r.incumplidos}}</strong></td>
      <td><span class="chip ${{chip}}">${{r.pct_ef}}%</span></td>
    </tr>`;
  }}).join('');
}}

function sortTabla(col) {{
  if(sortCol===col) sortDir=-sortDir; else {{sortCol=col;sortDir=-1;}}
  filtrarTabla();
}}

// ── INIT ───────────────────────────────────────────────────────────────────
window.addEventListener('load',()=>{{
  dibujarFijos();
  filtrar();
  filtrarTabla();
}});
</script>
</body></html>"""

    fname = f"DASHBOARD_OPERATIVO_{re.sub(r'[/\\\\:*?\"<>|]', '-', label).replace(' ','_')}_{date.today().strftime('%Y%m%d')}.html"
    ruta  = os.path.join(carpeta, fname)
    with open(ruta,"w",encoding="utf-8") as f: f.write(HTML)
    return ruta
