# -*- coding: utf-8 -*-
import re, os, json
"""Dashboard HTML Gerencial v2 — Interactivo, pastel, con análisis completo"""
import os, json
from datetime import date

def generar_dashboard_gerencial(df_ag, df_cc, label, fd, fh, carpeta, logo_path=None):
    import pandas as pd

    total   = len(df_ag)
    recib   = int((df_ag["_estado"]=="RECIBIDO").sum())
    rechaz  = int((df_ag["_estado"]=="RECHAZADO").sum())
    no_ll   = int(df_ag["_estado"].str.contains("LLEG",na=False).sum())
    pct_ef  = recib/total if total else 0
    pct_rch = rechaz/total if total else 0
    pct_nl  = no_ll/total if total else 0
    min_ok  = df_cc[df_cc["_min"]>0]["_min"]
    prom_t  = min_ok.mean() if len(min_ok) else 0
    sin_nov = int((df_cc["_novedad"].str.strip()=="SIN NOVEDAD").sum())
    pct_ok  = sin_nov/len(df_cc) if len(df_cc) else 0
    fecha_g = date.today().strftime("%d/%m/%Y")
    sin_placa  = int(df_cc["_novedad"].str.strip().eq("SIN PLACA").sum())
    no_msd     = int(df_cc["_novedad"].str.strip().eq("NO DEJA AGENDAR MSD").sum())
    llega_t    = int(df_cc["_novedad"].str.strip().eq("LLEGA TARDE").sum())

    # ── Evolución mensual
    df2 = df_ag.copy()
    df2["_mes"] = pd.to_datetime(df2["_fecha"].astype(str)).dt.to_period("M")
    evo_m = df2.groupby("_mes").agg(
        total    =("_estado","count"),
        recibidos=("_estado",lambda x:(x=="RECIBIDO").sum()),
        rechazados=("_estado",lambda x:(x=="RECHAZADO").sum()),
        no_llego =("_estado",lambda x:x.str.contains("LLEG",na=False).sum()),
    ).reset_index()
    m_lbl = [str(m) for m in evo_m["_mes"]]
    m_tot = evo_m["total"].tolist()
    m_rec = evo_m["recibidos"].tolist()
    m_rch = evo_m["rechazados"].tolist()
    m_nll = evo_m["no_llego"].tolist()
    m_pct = [round(r/t*100,1) if t else 0 for r,t in zip(m_rec,m_tot)]

    # ── Proveedores
    gp = df_ag.groupby("_proveedor").agg(
        visitas   =("_estado","count"),
        recibidos =("_estado",lambda x:(x=="RECIBIDO").sum()),
        rechazados=("_estado",lambda x:(x=="RECHAZADO").sum()),
        no_llego  =("_estado",lambda x:x.str.contains("LLEG",na=False).sum()),
    ).reset_index()
    gp["pct_ef"]     = (gp["recibidos"]/gp["visitas"].replace(0,1)*100).round(1)
    gp["incumplidos"]= gp["rechazados"]+gp["no_llego"]
    gp_json = gp.sort_values("visitas",ascending=False).to_dict("records")
    for r in gp_json:
        for k in list(r.keys()):
            r[k] = int(r[k]) if isinstance(r[k], int) else \
                   float(round(r[k],1)) if isinstance(r[k],float) else r[k]

    # Top efectivos / incumplidores
    top_ef_l = gp[gp["visitas"]>=3].nlargest(10,"pct_ef")["_proveedor"].str[:24].tolist()
    top_ef_v = [round(x,1) for x in gp[gp["visitas"]>=3].nlargest(10,"pct_ef")["pct_ef"]]
    top_inc_l= gp.nlargest(10,"incumplidos")["_proveedor"].str[:24].tolist()
    top_inc_v= gp.nlargest(10,"incumplidos")["incumplidos"].tolist()

    # Sin registro en CC
    cc_p    = set(df_cc["_proveedor"].str.strip().str.upper())
    sin_cc  = [p for p in gp["_proveedor"].str.upper() if p not in cc_p]

    # ── Novedades
    nov = df_cc.groupby("_novedad").size().sort_values(ascending=False).reset_index(name="n")
    nov_lbl = nov["_novedad"].str.strip().tolist()
    nov_val = nov["n"].tolist()

    # ── Tiempo por proveedor
    df_t  = df_cc[df_cc["_min"]>0]
    tp    = df_t.groupby("_proveedor")["_min"].mean().sort_values(ascending=False).head(10)
    tp_l  = tp.index.str[:24].tolist()
    tp_v  = [round(x,1) for x in tp.values]

    # ── Análisis de alineación horaria CC
    ret_mes = {}
    if "_retraso" in df_cc.columns and df_cc["_retraso"].notna().any():
        df_ret = df_cc.copy()
        df_ret["_mes2"] = pd.to_datetime(df_ret["_fecha"].astype(str)).dt.to_period("M")
        ret_g = df_ret.groupby("_mes2")["_retraso"].mean()
        ret_mes = {str(k): round(v,1) for k,v in ret_g.items()}

    # Logo
    logo_b64 = ""
    if logo_path and os.path.exists(logo_path):
        import base64
        with open(logo_path,"rb") as f: logo_b64 = base64.b64encode(f.read()).decode()
    logo_html = (f'<img src="data:image/jpeg;base64,{logo_b64}" class="logo">'
                 if logo_b64 else '<span class="logo-text">ALPINA</span>')

    # ── Alertas para tabla
    alertas = [
        (pct_ef>=.85, "Efectividad de recepción", f"{pct_ef:.1%}",
         "≥85% CUMPLE" if pct_ef>=.85 else "BAJO meta 85%"),
        (prom_t<=60,  "Tiempo prom. descargue",   f"{prom_t:.0f} min",
         "≤60 min OK" if prom_t<=60 else "Supera 60 min"),
        (no_msd==0,   "Sin agenda MSD",            str(no_msd),
         "Sin incidentes" if no_msd==0 else "Riesgo trazabilidad"),
        (sin_placa==0,"Sin placa registrada",       str(sin_placa),
         "Documentación completa" if sin_placa==0 else "Revisar agendamiento"),
        (llega_t==0,  "Vehículos llegan tarde",    str(llega_t),
         "Sin tardanzas" if llega_t==0 else "Afecta programación"),
        (len(sin_cc)==0,"Proveed. sin reg. CC",    str(len(sin_cc)),
         "Cobertura total" if not sin_cc else f"{len(sin_cc)} sin registro"),
    ]
    alerta_rows = "".join(
        f"""<tr>
          <td style="text-align:center;font-size:16px">{'✅' if ok else '🔴'}</td>
          <td style="font-weight:600;color:{'#15803D' if ok else '#B91C1C'}">{ind}</td>
          <td style="font-weight:700;font-size:15px;color:{'#15803D' if ok else '#B91C1C'}">{val}</td>
          <td style="color:{'#15803D' if ok else '#B91C1C'};font-size:12px">{det}</td>
        </tr>"""
        for ok,ind,val,det in alertas
    )

    # Pre-calcular JSONs
    datos_ag_json = json.dumps([
        {"fecha": str(r["_fecha"]), "estado": r["_estado"],
         "proveedor": r["_proveedor"],
         "mes": pd.to_datetime(str(r["_fecha"])).strftime("%Y-%m")}
        for _,r in df_ag.iterrows()
    ])

    HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard Gerencial — {label}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{{
  --bg:#F8FAFC; --card:#FFFFFF; --border:#E2E8F0;
  --azul:#2563EB; --azul-p:#DBEAFE; --azul-t:#1E3A8A;
  --dor:#D97706;  --dor-p:#FEF3C7;  --dor-t:#92400E;
  --verde:#16A34A;--verde-p:#DCFCE7;--verde-t:#14532D;
  --rojo:#DC2626; --rojo-p:#FEE2E2; --rojo-t:#7F1D1D;
  --nar:#EA580C;  --nar-p:#FFEDD5;  --nar-t:#7C2D12;
  --gris:#64748B; --texto:#0F172A;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--texto);font-size:14px}}
.header{{background:linear-gradient(135deg,#1E3A8A 0%,#2563EB 100%);padding:18px 28px;
          display:flex;align-items:center;gap:16px;box-shadow:0 3px 10px #0002}}
.logo{{height:48px;border-radius:6px}}
.logo-text{{font-size:22px;font-weight:900;color:#FEF3C7;
            background:#D97706;padding:6px 14px;border-radius:8px}}
.hd h1{{font-size:18px;font-weight:700;color:#fff}}
.hd .sub{{font-size:12px;color:#BFDBFE;margin-top:3px}}
.badge{{display:inline-block;background:#FEF3C7;color:#92400E;
         border-radius:20px;padding:3px 14px;font-size:11px;font-weight:700;margin-top:5px}}
.filtros{{background:#fff;border-bottom:1px solid var(--border);padding:10px 28px;
           display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
.filtros label{{font-size:12px;font-weight:600;color:var(--gris)}}
.filtros select{{border:1px solid var(--border);border-radius:6px;padding:5px 10px;
  font-size:12px;background:#fff;color:var(--texto);outline:none}}
.filtros select:focus{{border-color:var(--azul)}}
.btn-r{{background:var(--dor-p);color:var(--dor-t);border:none;border-radius:6px;
         padding:5px 14px;font-size:12px;font-weight:600;cursor:pointer}}
.btn-r:hover{{background:var(--dor);color:#fff}}
.main{{padding:20px 28px;max-width:1600px;margin:0 auto}}
.kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px}}
.kpi{{background:#fff;border-radius:12px;padding:18px;border-top:4px solid var(--c);
       box-shadow:0 2px 6px #0001}}
.kpi .val{{font-size:32px;font-weight:900;color:var(--c)}}
.kpi .lbl{{font-size:10px;font-weight:700;color:var(--gris);margin-top:5px;text-transform:uppercase}}
.kpi .meta{{font-size:11px;color:#94A3B8;margin-top:4px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}}
.card{{background:#fff;border-radius:12px;padding:18px;box-shadow:0 1px 4px #0001;border:1px solid var(--border)}}
.card.gold{{border-top:3px solid var(--dor)}}
.card h3{{font-size:12px;font-weight:700;color:var(--azul-t);margin-bottom:14px;
           text-transform:uppercase;letter-spacing:.5px}}
canvas{{max-height:240px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:var(--dor-p);color:var(--dor-t);padding:8px 10px;text-align:left;font-weight:700;font-size:11px}}
td{{padding:7px 10px;border-bottom:1px solid var(--border)}}
tr:hover td{{background:#FFFBEB}}
.prov{{max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500}}
.chip{{display:inline-block;border-radius:8px;padding:2px 10px;font-size:11px;font-weight:700}}
.chip-ok{{background:var(--verde-p);color:var(--verde-t)}}
.chip-warn{{background:var(--nar-p);color:var(--nar-t)}}
.chip-mal{{background:var(--rojo-p);color:var(--rojo-t)}}
.search-box{{width:100%;border:1px solid var(--border);border-radius:6px;padding:7px 12px;
              font-size:12px;margin-bottom:10px;outline:none}}
.search-box:focus{{border-color:var(--dor)}}
.tag{{display:inline-block;background:var(--nar-p);color:var(--nar-t);border-radius:6px;
       padding:2px 8px;font-size:10px;font-weight:600;margin:2px}}
.footer{{text-align:center;font-size:10px;color:#94A3B8;padding:16px;margin-top:8px}}
</style>
</head>
<body>
<div class="header">
  {logo_html}
  <div class="hd">
    <h1>🏛️ DASHBOARD GERENCIAL — RECEPCIÓN DE MATERIALES</h1>
    <div class="sub">Planta Entrerrios · Visión estratégica · Generado: {fecha_g}</div>
    <div class="badge">📅 {label} &nbsp;·&nbsp; {fd.strftime("%d/%m/%Y")} al {fh.strftime("%d/%m/%Y")}</div>
  </div>
</div>

<div class="filtros">
  <label>Filtrar por mes:</label>
  <select id="sel_mes" onchange="filtrarMes()">
    <option value="">Todos los meses</option>
    {"".join(f'<option value="{m}">{m}</option>' for m in m_lbl)}
  </select>
  <label>Proveedor:</label>
  <select id="sel_prov" onchange="filtrarMes()">
    <option value="">Todos</option>
    {"".join(f'<option value="{r["_proveedor"]}">{r["_proveedor"][:35]}</option>' for r in gp.nlargest(20,"visitas").to_dict("records"))}
  </select>
  <button class="btn-r" onclick="resetG()">↺ Resetear</button>
  <span id="lbl_g" style="font-size:12px;color:var(--dor-t);font-weight:600"></span>
</div>

<div class="main">

<!-- KPIs -->
<div class="kpis">
  <div class="kpi" style="--c:{'var(--verde)' if pct_ef>=.85 else 'var(--rojo)'}">
    <div class="val">{pct_ef:.1%}</div>
    <div class="lbl">Efectividad</div>
    <div class="meta">{'✅ Cumple ≥85%' if pct_ef>=.85 else '⚠️ Bajo meta 85%'}</div>
  </div>
  <div class="kpi" style="--c:{'var(--verde)' if prom_t<=60 else 'var(--nar)'}">
    <div class="val">{prom_t:.0f}<span style="font-size:16px"> min</span></div>
    <div class="lbl">Prom. Descargue</div>
    <div class="meta">{'✅ ≤60 min' if prom_t<=60 else '⚠️ Supera 60 min'}</div>
  </div>
  <div class="kpi" style="--c:var(--azul)">
    <div class="val">{pct_ok:.1%}</div>
    <div class="lbl">Sin Novedad CC</div>
    <div class="meta">{sin_nov}/{len(df_cc)} registros</div>
  </div>
  <div class="kpi" style="--c:{'var(--rojo)' if no_msd>0 else 'var(--verde)'}">
    <div class="val">{no_msd}</div>
    <div class="lbl">Sin Agenda MSD</div>
    <div class="meta">{'⚠️ Riesgo trazabilidad' if no_msd>0 else '✅ Sin incidentes'}</div>
  </div>
  <div class="kpi" style="--c:var(--dor)">
    <div class="val">{total}</div>
    <div class="lbl">Total Vehículos</div>
    <div class="meta">{(fh-fd).days+1} días de operación</div>
  </div>
</div>

<!-- Alertas + Evolución mensual -->
<div class="grid2">
  <div class="card gold">
    <h3>🚨 Alertas y Hallazgos Críticos</h3>
    <table>
      <thead><tr><th></th><th>Indicador</th><th>Valor</th><th>Diagnóstico</th></tr></thead>
      <tbody>{alerta_rows}</tbody>
    </table>
  </div>
  <div class="card gold">
    <h3>📈 Evolución Mensual</h3>
    <canvas id="evoMChart"></canvas>
  </div>
</div>

<!-- % Ef mensual + Novedades -->
<div class="grid2">
  <div class="card gold">
    <h3>📊 % Efectividad por Mes</h3>
    <canvas id="pctMChart"></canvas>
  </div>
  <div class="card gold">
    <h3>🍩 Composición de Novedades</h3>
    <canvas id="novDonut"></canvas>
  </div>
</div>

<!-- Proveedores efectivos + incumplidores -->
<div class="grid2">
  <div class="card gold">
    <h3>🏆 Proveedores más Efectivos (≥3 visitas)</h3>
    <canvas id="efChart"></canvas>
  </div>
  <div class="card gold">
    <h3>⚠️ Mayores Incumplidores</h3>
    <canvas id="incChart"></canvas>
  </div>
</div>

<!-- Tiempo por proveedor -->
<div class="grid2">
  <div class="card gold">
    <h3>⏱️ Tiempo Prom. Descargue por Proveedor (min)</h3>
    <canvas id="tPrvChart"></canvas>
  </div>
  <div class="card gold">
    <h3>📋 Desvío Promedio Cita→Ingreso por Mes (min)</h3>
    <canvas id="retMChart"></canvas>
  </div>
</div>

<!-- Tabla gerencial filtrable -->
<div class="card" style="margin-bottom:16px">
  <h3>📋 Resumen Ejecutivo por Proveedor</h3>
  <input class="search-box" type="text" id="buscar_g" placeholder="🔍 Buscar proveedor..." onkeyup="filtrarTablaG()">
  <div style="overflow-x:auto">
    <table id="tbl_g">
      <thead><tr>
        <th>Proveedor</th><th>Visitas</th><th>% Part.</th>
        <th>Recibidos</th><th>Incumpl.</th><th>% Ef.</th>
      </tr></thead>
      <tbody id="tbody_g"></tbody>
    </table>
  </div>
</div>

<!-- Proveedores sin CC -->
{f'''<div class="card" style="margin-bottom:16px">
  <h3>🔍 Proveedores SIN Registro en Control Citas ({len(sin_cc)} detectados)</h3>
  <p style="font-size:11px;color:var(--gris);margin-bottom:8px">
    Tienen visitas registradas en Agenda pero no aparecen en Control de Citas.</p>
  <div>{"".join(f'<span class="tag">{p}</span>' for p in sin_cc[:40])}</div>
</div>''' if sin_cc else ''}

</div>
<div class="footer">Dashboard Gerencial · Planta Entrerrios · {fecha_g} · {label}</div>

<script>
const C={{azul:"#2563EB",azulP:"#DBEAFE",dor:"#D97706",dorP:"#FEF3C7",
          verde:"#16A34A",verdeP:"#DCFCE7",rojo:"#DC2626",rojoP:"#FEE2E2",
          nar:"#EA580C",narP:"#FFEDD5",gris:"#94A3B8",texto:"#0F172A"}};

const PROVS  = {json.dumps(gp_json)};
const DATOS_AG = {datos_ag_json};

const M_LBL={json.dumps(m_lbl)};
const M_TOT={json.dumps(m_tot)};const M_REC={json.dumps(m_rec)};
const M_RCH={json.dumps(m_rch)};const M_NLL={json.dumps(m_nll)};
const M_PCT={json.dumps(m_pct)};
const NOV_L={json.dumps(nov_lbl)};const NOV_V={json.dumps(nov_val)};
const EF_L={json.dumps(top_ef_l)};const EF_V={json.dumps(top_ef_v)};
const INC_L={json.dumps(top_inc_l)};const INC_V={json.dumps(top_inc_v)};
const TP_L={json.dumps(tp_l)};const TP_V={json.dumps(tp_v)};
const RET_M={json.dumps(ret_mes)};

const OPTS={{responsive:true,
  plugins:{{legend:{{labels:{{color:C.texto,font:{{size:11}}}}}}}},
  scales:{{x:{{ticks:{{color:C.gris,font:{{size:9}}}},grid:{{color:"#F1F5F9"}}}},
            y:{{ticks:{{color:C.gris,font:{{size:10}}}},grid:{{color:"#F1F5F9"}}}}
  }}
}};
let charts={{}};
const ctx=id=>document.getElementById(id).getContext('2d');
function mk(id,cfg){{if(charts[id])charts[id].destroy();charts[id]=new Chart(ctx(id),cfg);}}

function dibujarFijos(){{
  // Efectivos
  mk('efChart',{{type:'bar',data:{{
    labels:EF_L.map(l=>l.length>20?l.slice(0,20)+'…':l),
    datasets:[{{label:'% Efectividad',data:EF_V,
      backgroundColor:EF_V.map(v=>v>=80?C.verdeP:v>=60?C.dorP:C.rojoP),
      borderColor:EF_V.map(v=>v>=80?C.verde:v>=60?C.dor:C.rojo),borderWidth:1}}]
  }},options:{{...OPTS,indexAxis:'y',
    scales:{{...OPTS.scales,x:{{...OPTS.scales.x,max:105,
      ticks:{{...OPTS.scales.x.ticks,callback:v=>v+'%'}}}}}}}}}});

  // Incumplidores
  mk('incChart',{{type:'bar',data:{{
    labels:INC_L.map(l=>l.length>20?l.slice(0,20)+'…':l),
    datasets:[{{label:'Incumplimientos',data:INC_V,
      backgroundColor:INC_V.map(v=>v>10?C.rojoP:C.narP),
      borderColor:INC_V.map(v=>v>10?C.rojo:C.nar),borderWidth:1}}]
  }},options:{{...OPTS,indexAxis:'y'}}}});

  // Tiempo por proveedor
  mk('tPrvChart',{{type:'bar',data:{{
    labels:TP_L.map(l=>l.length>18?l.slice(0,18)+'…':l),
    datasets:[
      {{label:'Prom. min',data:TP_V,
        backgroundColor:TP_V.map(v=>v>60?C.rojoP:v>45?C.dorP:C.verdeP),
        borderColor:TP_V.map(v=>v>60?C.rojo:v>45?C.dor:C.verde),borderWidth:1}},
      {{label:'Límite 60',data:Array(TP_L.length).fill(60),type:'line',
        borderColor:C.rojo,borderDash:[6,4],borderWidth:1.5,pointRadius:0}}
    ]
  }},options:{{...OPTS,indexAxis:'y'}}}});

  // Novedades donut
  const ncol=NOV_L.map(n=>n.includes('SIN NOVEDAD')?C.verdeP:
    (n.includes('PLACA')||n.includes('HORARIO')||n.includes('TARDE'))?C.dorP:C.rojoP);
  const nbd=NOV_L.map(n=>n.includes('SIN NOVEDAD')?C.verde:
    (n.includes('PLACA')||n.includes('HORARIO')||n.includes('TARDE'))?C.dor:C.rojo);
  mk('novDonut',{{type:'doughnut',data:{{
    labels:NOV_L,
    datasets:[{{data:NOV_V,backgroundColor:ncol,borderColor:nbd,borderWidth:2}}]
  }},options:{{responsive:true,cutout:'55%',
    plugins:{{legend:{{position:'right',labels:{{color:C.texto,font:{{size:10}},boxWidth:12}}}},
      tooltip:{{callbacks:{{label:ctx=>`${{ctx.label}}: ${{ctx.parsed}}`}}}}
    }}}}}});

  // Retraso por mes
  const retK=Object.keys(RET_M).sort();
  const retV=retK.map(k=>RET_M[k]);
  mk('retMChart',{{type:'bar',data:{{
    labels:retK,
    datasets:[{{label:'Desvío prom. (min)',data:retV,
      backgroundColor:retV.map(v=>v>5?C.rojoP:v<-5?C.azulP:C.verdeP),
      borderColor:retV.map(v=>v>5?C.rojo:v<-5?C.azul:C.verde),borderWidth:1}}]
  }},options:{{...OPTS,
    scales:{{...OPTS.scales,y:{{...OPTS.scales.y,
      ticks:{{...OPTS.scales.y.ticks,callback:v=>(v>=0?'+':'')+v+' min'}}}}}}}}}});
}}

function dibujarEvo(lbl,tot,rec,nll,rch,pct){{
  mk('evoMChart',{{type:'bar',data:{{
    labels:lbl,
    datasets:[
      {{label:'Agendados',data:tot,backgroundColor:C.azulP,borderColor:C.azul,borderWidth:1}},
      {{label:'Recibidos',data:rec,backgroundColor:C.verdeP,borderColor:C.verde,borderWidth:1}},
      {{label:'No Llegó', data:nll,backgroundColor:C.narP,borderColor:C.nar,borderWidth:1}},
      {{label:'Rechazados',data:rch,backgroundColor:C.rojoP,borderColor:C.rojo,borderWidth:1}},
    ]
  }},options:OPTS}});
  mk('pctMChart',{{type:'bar',data:{{
    labels:lbl,
    datasets:[
      {{label:'% Efectividad',data:pct,
        backgroundColor:pct.map(v=>v>=85?C.verdeP:v>=70?C.dorP:C.rojoP),
        borderColor:pct.map(v=>v>=85?C.verde:v>=70?C.dor:C.rojo),borderWidth:1}},
      {{label:'Meta 85%',data:Array(lbl.length).fill(85),type:'line',
        borderColor:C.rojo,borderDash:[6,4],borderWidth:1.5,pointRadius:0}}
    ]
  }},options:{{...OPTS,
    scales:{{...OPTS.scales,y:{{...OPTS.scales.y,max:110,
      ticks:{{...OPTS.scales.y.ticks,callback:v=>v+'%'}}}}}}}}}});
}}

function filtrarMes(){{
  const mes  = document.getElementById('sel_mes').value;
  const prov = document.getElementById('sel_prov').value;
  let fil = DATOS_AG.filter(d=>(!mes||d.mes===mes)&&(!prov||d.proveedor===prov));
  document.getElementById('lbl_g').textContent =
    fil.length<DATOS_AG.length?`🔍 ${{fil.length}} de ${{DATOS_AG.length}} registros`:'';
  if(mes){{
    const idx=M_LBL.indexOf(mes);
    dibujarEvo([M_LBL[idx]],[M_TOT[idx]],[M_REC[idx]],[M_NLL[idx]],[M_RCH[idx]],[M_PCT[idx]]);
  }}else{{
    dibujarEvo(M_LBL,M_TOT,M_REC,M_NLL,M_RCH,M_PCT);
  }}
}}
function resetG(){{
  document.getElementById('sel_mes').value='';
  document.getElementById('sel_prov').value='';
  filtrarMes();
}}

function filtrarTablaG(){{
  const q = document.getElementById('buscar_g').value.toLowerCase();
  const datos = PROVS.filter(r=>r._proveedor.toLowerCase().includes(q))
                     .sort((a,b)=>b.visitas-a.visitas);
  const tot = DATOS_AG.length || 1;
  document.getElementById('tbody_g').innerHTML = datos.map(r=>{{
    const ch=r.pct_ef>=80?'chip-ok':r.pct_ef>=60?'chip-warn':'chip-mal';
    return `<tr>
      <td class="prov" title="${{r._proveedor}}">${{r._proveedor}}</td>
      <td>${{r.visitas}}</td>
      <td>${{(r.visitas/tot*100).toFixed(1)}}%</td>
      <td>${{r.recibidos}}</td>
      <td>${{r.incumplidos}}</td>
      <td><span class="chip ${{ch}}">${{r.pct_ef}}%</span></td>
    </tr>`;
  }}).join('');
}}

window.addEventListener('load',()=>{{
  dibujarFijos();
  dibujarEvo(M_LBL,M_TOT,M_REC,M_NLL,M_RCH,M_PCT);
  filtrarTablaG();
}});
</script>
</body></html>"""

    fname = f"DASHBOARD_GERENCIAL_{re.sub(r'[/\\\\:*?\"<>|]', '-', label).replace(' ','_')}_{date.today().strftime('%Y%m%d')}.html"
    ruta  = os.path.join(carpeta, fname)
    with open(ruta,"w",encoding="utf-8") as f: f.write(HTML)
    return ruta
