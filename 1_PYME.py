# ============================================================
# RISK ANALYTICS AI — PYME
# Ruta de Madurez Financiera — 11 Módulos
# Versión simplificada para clientes menores (PYME)
# Ejecutar: streamlit run risk_analytics_pyme.py
# ============================================================

import math
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

if st.sidebar.button("⬅ Volver al árbol de navegación", use_container_width=True):
    st.switch_page("Home.py")
st.sidebar.divider()


# ── Helpers ────────────────────────────────────────────────
def m(x):      return f"S/ {x:,.0f}"
def pct(x):    return f"{x*100:.1f}%"
def safe(n, d):
    try:
        n = float(n); d = float(d)
        return n / d if d not in (0, 0.0) else 0.0
    except (TypeError, ValueError):
        return 0.0
def sem(v, g=0.7, a=0.4):
    return "🟢" if v >= g else ("🟡" if v >= a else "🔴")

st.markdown("""
<style>
[data-testid="stMetricValue"]{font-size:1.2rem;font-weight:700;}
.stTabs [data-baseweb="tab"]{font-size:0.75rem;font-weight:600;}
.block-container{padding-top:1rem;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — DATOS DE LA EMPRESA
# ============================================================
st.sidebar.title("📈 RISK ANALYTICS AI")
st.sidebar.caption("Ruta de Madurez Financiera — Versión PYME")
st.sidebar.divider()

st.sidebar.subheader("🏢 Empresa")
empresa = st.sidebar.text_input("Nombre de la empresa", "Mi Empresa SAC")
sector  = st.sidebar.selectbox("Sector", ["Comercio","Servicios","Manufactura","Construcción","Agroindustria","Otro"])

st.sidebar.divider()
st.sidebar.subheader("📊 Estado de Resultados (año actual)")
ventas      = st.sidebar.number_input("Ventas netas",      value=1_200_000.0, step=10_000.0, min_value=0.0)
costo_v     = st.sidebar.number_input("Costo de ventas",   value=780_000.0,   step=10_000.0, min_value=0.0)
gastos_op   = st.sidebar.number_input("Gastos operativos", value=250_000.0,   step=5_000.0,  min_value=0.0)
dep         = st.sidebar.number_input("Depreciación",      value=30_000.0,    step=1_000.0,  min_value=0.0)
intereses   = st.sidebar.number_input("Gastos financieros",value=25_000.0,    step=1_000.0,  min_value=0.0)
ir_tasa     = st.sidebar.slider("Tasa Impuesto a la Renta (%)", 0.0, 40.0, 29.5, 0.5) / 100

with st.sidebar.expander("Año anterior (para análisis horizontal)"):
    ventas_ant   = st.number_input("Ventas netas (año anterior)",  value=ventas*0.90,  step=10_000.0, min_value=0.0)
    ebitda_ant_in= st.number_input("EBITDA (año anterior)",        value=(ventas-costo_v-gastos_op)*0.85, step=5_000.0)
    un_ant       = st.number_input("Utilidad neta (año anterior)", value=(ventas-costo_v-gastos_op-dep-intereses)*(1-ir_tasa)*0.85, step=5_000.0)

st.sidebar.divider()
st.sidebar.subheader("⚖️ Balance General")
activo_tot  = st.sidebar.number_input("Activo total",          value=1_500_000.0, step=20_000.0, min_value=0.01)
activo_corr = st.sidebar.number_input("Activo corriente",      value=650_000.0,   step=10_000.0, min_value=0.0)
inventario  = st.sidebar.number_input("Inventarios",           value=220_000.0,   step=5_000.0,  min_value=0.0)
caja_saldo  = st.sidebar.number_input("Caja y bancos",         value=120_000.0,   step=5_000.0,  min_value=0.0)
cuentas_cob = st.sidebar.number_input("Cuentas por cobrar",    value=180_000.0,   step=5_000.0,  min_value=0.0)
pasivo_corr = st.sidebar.number_input("Pasivo corriente",      value=420_000.0,   step=10_000.0, min_value=0.0)
cuentas_pag = st.sidebar.number_input("Cuentas por pagar",     value=160_000.0,   step=5_000.0,  min_value=0.0)
deuda_tot   = st.sidebar.number_input("Deuda financiera total",value=380_000.0,   step=10_000.0, min_value=0.0)
patrimonio  = st.sidebar.number_input("Patrimonio neto",       value=700_000.0,   step=10_000.0, min_value=0.01)

st.sidebar.divider()
st.sidebar.subheader("💰 Costo de Capital (simplificado)")
rf   = st.sidebar.number_input("Tasa libre de riesgo (%)", value=5.3, step=0.1) / 100
beta = st.sidebar.number_input("Beta del sector",           value=1.00, step=0.05)
erp  = st.sidebar.number_input("Prima de riesgo mercado (%)", value=6.2, step=0.1) / 100
rp   = st.sidebar.number_input("Riesgo país (%)",           value=1.8, step=0.1) / 100
kd   = st.sidebar.number_input("Costo de deuda Kd, antes IR (%)", value=10.5, step=0.5) / 100

st.sidebar.divider()
st.sidebar.subheader("📦 Días operativos")
dias_cobro = st.sidebar.number_input("Días promedio de cobro", value=55, step=5, min_value=0)
dias_pago  = st.sidebar.number_input("Días promedio de pago",  value=35, step=5, min_value=0)
dias_inv   = st.sidebar.number_input("Días de inventario",     value=45, step=5, min_value=0)

st.sidebar.divider()
st.sidebar.subheader("🏆 Competidores (Inteligencia Competitiva)")
st.sidebar.caption("Edita, agrega o borra filas para comparar tu empresa contra el mercado. "
                    "Si no tienes datos financieros públicos de tu competencia, deja la tabla en blanco "
                    "y usa el Benchmark Interno del módulo M12.")
comp_default_pyme = pd.DataFrame([
    {"Competidor": "Competidor A", "Ventas": round(ventas*1.5, -3), "Margen EBITDA %": 22.0, "ROE %": 15.0,
     "Endeudamiento": 0.55, "Liquidez": 1.5, "Precio promedio (S/)": 120.0, "Participación mercado %": 30.0},
    {"Competidor": "Competidor B", "Ventas": round(ventas*1.1, -3), "Margen EBITDA %": 18.0, "ROE %": 12.0,
     "Endeudamiento": 0.62, "Liquidez": 1.3, "Precio promedio (S/)": 112.0, "Participación mercado %": 20.0},
    {"Competidor": "Competidor C", "Ventas": round(ventas*0.7, -3), "Margen EBITDA %": 14.0, "ROE %": 9.0,
     "Endeudamiento": 0.70, "Liquidez": 1.1, "Precio promedio (S/)": 105.0, "Participación mercado %": 12.0},
])
comp_df_edit = st.sidebar.data_editor(
    comp_default_pyme, num_rows="dynamic", use_container_width=True, key="pyme_comp_editor",
    column_config={
        "Ventas": st.column_config.NumberColumn(format="%.0f"),
        "Margen EBITDA %": st.column_config.NumberColumn(format="%.1f"),
        "ROE %": st.column_config.NumberColumn(format="%.1f"),
        "Endeudamiento": st.column_config.NumberColumn(format="%.2f"),
        "Liquidez": st.column_config.NumberColumn(format="%.2f"),
        "Precio promedio (S/)": st.column_config.NumberColumn(format="%.0f"),
        "Participación mercado %": st.column_config.NumberColumn(format="%.1f"),
    },
)

# ============================================================
# MOTOR DE CÁLCULO
# ============================================================
utilidad_bruta = ventas - costo_v
ebitda         = utilidad_bruta - gastos_op
ebit           = ebitda - dep
uai            = ebit - intereses
utilidad_neta  = uai * (1 - ir_tasa)

margen_bruto   = safe(utilidad_bruta, ventas)
margen_ebitda  = safe(ebitda, ventas)
margen_neto    = safe(utilidad_neta, ventas)
margen_op      = safe(ebit, ventas)

liquidez_corr  = safe(activo_corr, pasivo_corr)
prueba_acida   = safe(activo_corr - inventario, pasivo_corr)
cap_trabajo    = activo_corr - pasivo_corr
endeudamiento  = safe(deuda_tot + pasivo_corr, activo_tot)
cobertura_int  = safe(ebit, intereses) if intereses > 0 else float("inf")
ciclo_cce      = dias_cobro + dias_inv - dias_pago

rot_inventario = safe(costo_v, max(inventario, 1))
rot_cxc        = safe(ventas, max(cuentas_cob, 1))
rot_activos    = safe(ventas, activo_tot)

roa            = safe(utilidad_neta, activo_tot)
roe            = safe(utilidad_neta, patrimonio)

# DuPont
margen_neto_dp = safe(utilidad_neta, ventas)
rotacion_dp    = safe(ventas, activo_tot)
apalancamiento_dp = safe(activo_tot, patrimonio)
roe_dupont     = margen_neto_dp * rotacion_dp * apalancamiento_dp

# Análisis horizontal
var_ventas_h = safe(ventas - ventas_ant, ventas_ant) if ventas_ant > 0 else 0.0
var_ebitda_h = safe(ebitda - ebitda_ant_in, ebitda_ant_in) if ebitda_ant_in != 0 else 0.0
var_un_h     = safe(utilidad_neta - un_ant, un_ant) if un_ant != 0 else 0.0
roe_ant      = safe(un_ant, patrimonio)
var_roe_h    = roe - roe_ant

# Costo de capital / creación de valor
ke   = rf + beta * erp + rp
wd   = safe(deuda_tot, deuda_tot + patrimonio)
we   = 1 - wd
wacc = we * ke + wd * kd * (1 - ir_tasa)
wacc_seg = max(wacc, 0.001)
ic   = patrimonio + deuda_tot
nopat= ebit * (1 - ir_tasa)
roic = safe(nopat, max(ic, 1))
eva  = nopat - ic * wacc
spread_roic = roic - wacc

fcf  = nopat + dep - cap_trabajo * 0.05
g_terminal = 0.03
vt_dcf = safe(fcf * (1 + g_terminal), max(wacc_seg - g_terminal, 0.01))
ev_dcf = fcf / wacc_seg + vt_dcf
eq_dcf = ev_dcf - deuda_tot

# CAMEL — score 0-100 por componente
score_capital = min(100, max(0,
    (min(safe(patrimonio, activo_tot) / 0.40, 1) * 40) +
    (max(0, 1 - endeudamiento / 0.70) * 30) +
    (min(max(cap_trabajo, 0) / max(ventas * 0.10, 1), 1) * 30)
))
dias_cxc_camel = safe(cuentas_cob, max(ventas, 1)) * 365
score_activos = min(100, max(0,
    (max(0, 1 - dias_cxc_camel / 90) * 50) +
    (max(0, 1 - safe(inventario, max(costo_v, 1)) * 365 / 90) * 50)
))
score_gestion = min(100, max(0,
    (min(margen_op / 0.15, 1) * 50) +
    (min(rot_activos / 1.2, 1) * 50)
))
score_rentabilidad = min(100, max(0,
    (min(margen_ebitda / 0.20, 1) * 35) +
    (min(roe / 0.15, 1) * 35) +
    (min(roa / 0.08, 1) * 30)
))
score_liquidez = min(100, max(0,
    (min(liquidez_corr / 1.8, 1) * 50) +
    (max(0, 1 - ciclo_cce / 90) * 50)
))
camel_total = float(np.mean([score_capital, score_activos, score_gestion, score_rentabilidad, score_liquidez]))

# Warren Buffett Score
score_calidad_negocio = min(100, (min(roe/0.15,1)*35 + min(roic/max(wacc,0.01),1.5)/1.5*35 + (100 if fcf>0 else 0)*0.30))
score_fortaleza       = min(100, (max(0,1-endeudamiento/0.6)*40 + min(liquidez_corr/1.8,1)*30 + (min(cobertura_int/3,1) if cobertura_int!=float("inf") else 1)*30))
score_gestion_capital = min(100, (min(rotacion_dp/1.2,1)*50 + (60 if var_ebitda_h>0 else 30)*0.5 + 20))
score_valoracion_wb   = min(100, max(0, (1 - safe(ic, max(eq_dcf,1))) * 100)) if eq_dcf > 0 else 30
score_buffett_total   = float(np.mean([score_calidad_negocio, score_fortaleza, score_gestion_capital, score_valoracion_wb]))

# ============================================================
# ENCABEZADO
# ============================================================
st.title("📈 RISK ANALYTICS AI — PYME")
st.caption(f"{empresa} | Sector: {sector} | {datetime.date.today().strftime('%d/%m/%Y')} | Ruta de madurez financiera")

hc1,hc2,hc3,hc4,hc5 = st.columns(5)
hc1.metric("Ventas", m(ventas), pct(var_ventas_h) if ventas_ant>0 else None)
hc2.metric("EBITDA", m(ebitda), pct(margen_ebitda))
hc3.metric("Utilidad neta", m(utilidad_neta), pct(margen_neto))
hc4.metric("Score CAMEL", f"{camel_total:.0f}/100", sem(camel_total/100))
hc5.metric("Score Buffett", f"{score_buffett_total:.0f}/100", sem(score_buffett_total/100))

st.divider()

# ============================================================
# TABS — 11 MÓDULOS
# ============================================================
(m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12) = st.tabs([
    "M1 · Diagnóstico",
    "M2 · DuPont",
    "M3 · CAMEL",
    "M4 · Controller",
    "M5 · Tesorería",
    "M6 · Instrumentos",
    "M7 · Creación de Valor",
    "M8 · Valoración",
    "M9 · Riesgo",
    "M10 · IA Financiera",
    "M11 · Warren Buffett",
    "M12 · Intel. Competitiva",
])

# ══════════════════════════════════════════════════════════
# M1 — DIAGNÓSTICO FINANCIERO CLÁSICO
# ══════════════════════════════════════════════════════════
with m1:
    st.header("M1 · Diagnóstico Financiero Clásico")
    st.caption("¿Cómo está la empresa hoy?")

    st.subheader("Estado de Resultados — Análisis vertical")
    ver_df = pd.DataFrame([
        ["Ventas netas",       m(ventas),        "100.0%"],
        ["Costo de ventas",    m(costo_v),       pct(safe(costo_v,ventas))],
        ["Utilidad bruta",     m(utilidad_bruta),pct(margen_bruto)],
        ["Gastos operativos",  m(gastos_op),     pct(safe(gastos_op,ventas))],
        ["EBITDA",             m(ebitda),        pct(margen_ebitda)],
        ["Depreciación",       m(dep),           pct(safe(dep,ventas))],
        ["EBIT",               m(ebit),          pct(margen_op)],
        ["Gastos financieros", m(intereses),     pct(safe(intereses,ventas))],
        ["Utilidad neta",      m(utilidad_neta), pct(margen_neto)],
    ], columns=["Concepto","S/","% de ventas"])
    st.dataframe(ver_df, use_container_width=True, hide_index=True)

    st.subheader("Análisis horizontal — vs. año anterior")
    hor_df = pd.DataFrame([
        ["Ventas",        m(ventas_ant),   m(ventas),        pct(var_ventas_h)],
        ["EBITDA",        m(ebitda_ant_in),m(ebitda),        pct(var_ebitda_h)],
        ["Utilidad neta", m(un_ant),       m(utilidad_neta), pct(var_un_h)],
        ["ROE",           pct(roe_ant),    pct(roe),         pct(var_roe_h)],
    ], columns=["Indicador","Año anterior","Año actual","Variación %"])
    st.dataframe(hor_df, use_container_width=True, hide_index=True)

    st.subheader("Ratios financieros")
    ratios_df = pd.DataFrame([
        ["Liquidez corriente",      f"{liquidez_corr:.2f}x",  "🟢 OK" if liquidez_corr>=1.5 else ("🟡 Vigilar" if liquidez_corr>=1.0 else "🔴 Crítico")],
        ["Prueba ácida",            f"{prueba_acida:.2f}x",   "🟢 OK" if prueba_acida>=1.0 else "🟡 Vigilar"],
        ["Capital de trabajo",      m(cap_trabajo),           "🟢 OK" if cap_trabajo>0 else "🔴 Negativo"],
        ["Endeudamiento total",     pct(endeudamiento),       "🟢 OK" if endeudamiento<=0.6 else ("🟡 Alto" if endeudamiento<=0.75 else "🔴 Crítico")],
        ["Cobertura de intereses",  (f"{cobertura_int:.2f}x" if cobertura_int!=float('inf') else "N/A (sin deuda)"), "🟢 OK" if (cobertura_int==float('inf') or cobertura_int>=3) else "🟡 Vigilar"],
        ["Rotación de inventarios",f"{rot_inventario:.2f}x",  ""],
        ["Rotación cuentas x cobrar",f"{rot_cxc:.2f}x",       ""],
        ["Rotación de activos",     f"{rot_activos:.2f}x",    ""],
        ["Margen bruto",            pct(margen_bruto),        ""],
        ["Margen operativo",        pct(margen_op),           ""],
        ["Margen neto",             pct(margen_neto),         ""],
        ["ROA",                     pct(roa),                 ""],
        ["ROE",                     pct(roe),                 ""],
        ["Ciclo de conversión del efectivo",f"{ciclo_cce:.0f} días", "🟢 OK" if ciclo_cce<=45 else ("🟡 Vigilar" if ciclo_cce<=75 else "🔴 Alto")],
    ], columns=["Ratio","Valor","Semáforo"])
    st.dataframe(ratios_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════
# M2 — ANÁLISIS DUPONT
# ══════════════════════════════════════════════════════════
with m2:
    st.header("M2 · Análisis DuPont")
    st.caption("¿Por qué la empresa gana o pierde rentabilidad?")

    d1,d2,d3,d4 = st.columns(4)
    d1.metric("Margen neto",         pct(margen_neto_dp))
    d2.metric("Rotación de activos", f"{rotacion_dp:.2f}x")
    d3.metric("Apalancamiento",      f"{apalancamiento_dp:.2f}x")
    d4.metric("ROE (DuPont)",        pct(roe_dupont))

    st.subheader("Descomposición")
    st.markdown(f"""
```
ROE = Margen Neto × Rotación de Activos × Apalancamiento
{pct(roe_dupont)} = {pct(margen_neto_dp)} × {rotacion_dp:.2f}x × {apalancamiento_dp:.2f}x
```
""")

    factores = pd.DataFrame([
        ["Margen neto", pct(margen_neto_dp), "🟢 Bueno" if margen_neto_dp>=0.08 else ("🟡 Regular" if margen_neto_dp>=0.03 else "🔴 Bajo")],
        ["Rotación de activos", f"{rotacion_dp:.2f}x", "🟢 Bueno" if rotacion_dp>=1.0 else ("🟡 Regular" if rotacion_dp>=0.6 else "🔴 Bajo")],
        ["Apalancamiento financiero", f"{apalancamiento_dp:.2f}x", "🟢 Conservador" if apalancamiento_dp<=2 else ("🟡 Moderado" if apalancamiento_dp<=3 else "🔴 Agresivo")],
    ], columns=["Factor","Valor","Evaluación"])
    st.dataframe(factores, use_container_width=True, hide_index=True)

    # Identificar el factor más débil (normalizado vs benchmark)
    valores_norm = {
        "Margen neto": safe(margen_neto_dp, 0.08),
        "Rotación de activos": safe(rotacion_dp, 1.0),
        "Apalancamiento financiero": 1/max(safe(apalancamiento_dp, 2.0), 0.01),
    }
    factor_debil = min(valores_norm, key=valores_norm.get)
    st.info(f"🧠 El factor que más está afectando la rentabilidad actual es: **{factor_debil}**. "
            f"Enfocar el plan de mejora de ROE en ese factor suele dar el mayor impacto.")

    st.subheader("Árbol DuPont")
    fig_tree = go.Figure(go.Sunburst(
        labels=["ROE","Margen neto","Rotación de activos","Apalancamiento"],
        parents=["", "ROE","ROE","ROE"],
        values=[100, max(margen_neto_dp*100, 1), max(rotacion_dp*30, 1), max(apalancamiento_dp*20, 1)],
        branchvalues="remainder",
    ))
    fig_tree.update_layout(height=380, title="Composición visual del ROE")
    # staticPlot=True: evita el click-to-zoom del Sunburst (mismo riesgo que el
    # Treemap de Home) para que nadie quede "atrapado" dentro de una rama.
    st.plotly_chart(fig_tree, use_container_width=True, config={"staticPlot": True})


# ══════════════════════════════════════════════════════════
# M3 — MODELO CAMEL
# ══════════════════════════════════════════════════════════
with m3:
    st.header("M3 · Modelo CAMEL")
    st.caption("Calificación integral de la salud financiera")

    camel_df = pd.DataFrame([
        ["C — Capital",       round(score_capital,0),      sem(score_capital/100)],
        ["A — Calidad de Activos", round(score_activos,0), sem(score_activos/100)],
        ["M — Gestión (Management)", round(score_gestion,0), sem(score_gestion/100)],
        ["E — Rentabilidad (Earnings)", round(score_rentabilidad,0), sem(score_rentabilidad/100)],
        ["L — Liquidez",      round(score_liquidez,0),     sem(score_liquidez/100)],
    ], columns=["Componente","Puntaje (0-100)","Semáforo"])
    st.dataframe(camel_df, use_container_width=True, hide_index=True)

    st.metric("Score Total CAMEL", f"{camel_total:.0f}/100", sem(camel_total/100))

    fig_camel = go.Figure(go.Scatterpolar(
        r=[score_capital, score_activos, score_gestion, score_rentabilidad, score_liquidez, score_capital],
        theta=["Capital","Activos","Gestión","Rentabilidad","Liquidez","Capital"],
        fill="toself", line_color="#1F3864", fillcolor="rgba(31,56,100,0.25)",
    ))
    fig_camel.update_layout(polar=dict(radialaxis=dict(range=[0,100])), height=400, title="Radar CAMEL")
    st.plotly_chart(fig_camel, use_container_width=True)

    if camel_total >= 80:
        st.success("✅ Empresa con salud financiera sólida (CAMEL ≥ 80). Foco en crecimiento y creación de valor.")
    elif camel_total >= 60:
        st.warning("⚠️ Salud financiera aceptable, con áreas de mejora puntuales. Revisar el componente con menor puntaje.")
    else:
        st.error("🚨 Salud financiera débil. Se recomienda un plan de acción prioritario sobre los componentes en rojo.")


# ══════════════════════════════════════════════════════════
# M4 — CONTROLLER FINANCIERO
# ══════════════════════════════════════════════════════════
with m4:
    st.header("M4 · Controller Financiero")
    st.caption("Presupuesto maestro, forecast y control de variaciones")

    st.subheader("Presupuesto vs Real")
    pv1,pv2 = st.columns(2)
    with pv1:
        pres_ventas = st.number_input("Ventas presupuestadas",  value=ventas*1.05,  step=10_000.0, min_value=0.0)
        pres_cv     = st.number_input("Costo ventas presup.",   value=costo_v*1.03, step=10_000.0, min_value=0.0)
    with pv2:
        pres_gop    = st.number_input("Gastos operat. presup.", value=gastos_op*1.02, step=5_000.0, min_value=0.0)
        crec_fore   = st.slider("Crecimiento esperado próximo periodo (%)", -20, 40, 8) / 100

    pres_ebitda = pres_ventas - pres_cv - pres_gop
    desv_ventas = ventas - pres_ventas
    desv_ebitda = ebitda - pres_ebitda

    ctrl_df = pd.DataFrame([
        ["Ventas",       m(pres_ventas), m(ventas), m(desv_ventas), pct(safe(desv_ventas,pres_ventas)), "🟢" if desv_ventas>=0 else "🔴"],
        ["Costo ventas", m(pres_cv),     m(costo_v),m(costo_v-pres_cv), pct(safe(costo_v-pres_cv,pres_cv)), "🟢" if costo_v<=pres_cv else "🔴"],
        ["Gastos operat.",m(pres_gop),   m(gastos_op),m(gastos_op-pres_gop), pct(safe(gastos_op-pres_gop,pres_gop)), "🟢" if gastos_op<=pres_gop else "🔴"],
        ["EBITDA",       m(pres_ebitda), m(ebitda), m(desv_ebitda), pct(safe(desv_ebitda,pres_ebitda)), "🟢" if desv_ebitda>=0 else "🔴"],
    ], columns=["Concepto","Presupuesto","Real","Desviación S/","Desviación %","Semáforo"])
    st.dataframe(ctrl_df, use_container_width=True, hide_index=True)

    n_alertas = sum(1 for ok in [desv_ventas>=0, desv_ebitda>=0] if not ok)
    if n_alertas == 0:
        st.success("✅ Sin desviaciones negativas relevantes este periodo.")
    else:
        st.warning(f"⚠️ {n_alertas} indicador(es) por debajo del presupuesto. Revisar causas antes del cierre del periodo.")

    st.subheader("Rolling Forecast — próximos 4 trimestres")
    trimestres = ["T+1","T+2","T+3","T+4"]
    ventas_fc  = [ventas/4 * (1+crec_fore)**((i+1)/4) for i in range(4)]
    ebitda_fc  = [v * margen_ebitda for v in ventas_fc]
    fc_df = pd.DataFrame({"Periodo":trimestres, "Ventas proyectadas":[m(v) for v in ventas_fc],
                           "EBITDA proyectado":[m(e) for e in ebitda_fc]})
    st.dataframe(fc_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════
# M5 — INTELIGENCIA DE TESORERÍA
# ══════════════════════════════════════════════════════════
with m5:
    st.header("M5 · Inteligencia de Tesorería")
    st.caption("No solo muestra la caja: la interpreta")

    np.random.seed(42)
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    ingresos_m = ventas/12 * (1 + np.random.normal(0, 0.06, 12))
    egresos_m  = (costo_v+gastos_op)/12 * (1 + np.random.normal(0, 0.05, 12))
    flujo_m    = ingresos_m - egresos_m
    caja_acum  = caja_saldo + np.cumsum(flujo_m)

    fig_caja = go.Figure()
    fig_caja.add_bar(x=meses, y=ingresos_m, name="Ingresos", marker_color="#2ecc71")
    fig_caja.add_bar(x=meses, y=-egresos_m, name="Egresos", marker_color="#e74c3c")
    fig_caja.add_scatter(x=meses, y=caja_acum, name="Caja acumulada", mode="lines+markers",
                         line=dict(color="#1F3864", width=3))
    fig_caja.update_layout(barmode="relative", title="Caja proyectada — 12 meses", height=400)
    st.plotly_chart(fig_caja, use_container_width=True)

    caja_final = float(caja_acum[-1])
    superavit  = caja_final - caja_saldo

    tc1,tc2,tc3 = st.columns(3)
    tc1.metric("Caja actual", m(caja_saldo))
    tc2.metric("Caja proyectada (12M)", m(caja_final))
    tc3.metric("Superávit / Déficit proyectado", m(superavit))

    st.subheader("🧠 Interpretación automática")
    if superavit > 0:
        st.success(f"Existe un exceso de liquidez proyectado de **{m(superavit)}**.")
        st.markdown(f"""
**Recomendación de la IA:**
- Colocar el excedente en depósito a plazo o fondo mutuo de liquidez.
- Evaluar amortizar deuda financiera (ahorro estimado de intereses: {m(min(superavit, deuda_tot) * kd)} al año).
- Si la empresa reparte utilidades, este es un buen momento para hacerlo sin comprometer la operación.
""")
    else:
        st.warning(f"Se proyecta un déficit de caja de **{m(abs(superavit))}** en los próximos 12 meses.")
        st.markdown(f"""
**Recomendación de la IA:**
- Evaluar una línea de crédito revolvente o factoring de cuentas por cobrar ({m(cuentas_cob*0.8)} disponibles al 80%).
- Negociar mayores plazos con proveedores (ampliar {dias_pago} días de pago actuales).
- Revisar el nivel de inventario ({dias_inv} días) — reducirlo libera caja de forma inmediata.
""")

    st.subheader("Ciclo de Conversión del Efectivo")
    st.dataframe(pd.DataFrame([
        ["Días de cobro (DSO)", dias_cobro],
        ["Días de inventario (DIO)", dias_inv],
        ["Días de pago (DPO)", dias_pago],
        ["CCE = DSO + DIO − DPO", ciclo_cce],
    ], columns=["Indicador","Días"]), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════
# M6 — INSTRUMENTOS FINANCIEROS
# ══════════════════════════════════════════════════════════
with m6:
    st.header("M6 · Instrumentos Financieros")
    st.caption("Según la posición de caja del Módulo 5")

    if superavit > 0:
        st.success(f"Con superávit de {m(superavit)}, estas son las opciones recomendadas:")
        st.dataframe(pd.DataFrame([
            ["Depósito a plazo (30-90d)","4-6% anual","Bajo","Rendimiento fijo, sin liquidez antes del plazo"],
            ["Fondo mutuo de liquidez","0.5-1.5% anual","Muy bajo","Máxima disponibilidad, ideal para caja operativa"],
            ["Letras del Tesoro / Bonos corto plazo","4.5-6%","Muy bajo","Buen rendimiento con respaldo soberano"],
            ["Overnight interbancario","3-4%","Muy bajo","Requiere línea bancaria habilitada"],
            ["Amortización de deuda","Ahorro = Kd actual","N/A","Reduce gastos financieros futuros"],
        ], columns=["Instrumento","Rendimiento est.","Riesgo","Comentario"]), use_container_width=True, hide_index=True)
    else:
        st.warning(f"Con déficit de {m(abs(superavit))}, estas son las opciones recomendadas:")
        st.dataframe(pd.DataFrame([
            ["Crédito revolvente","8-12% anual","Línea abierta para necesidades puntuales"],
            ["Factoring de cuentas por cobrar","6-9% anual","Adelanto de facturas vigentes en 24-48h"],
            ["Confirming","6-8% anual","El banco paga al proveedor; tú pagas después"],
            ["Leasing","7-10% anual","Reemplaza compra de activos por cuotas, libera caja"],
        ], columns=["Instrumento","Costo est.","Comentario"]), use_container_width=True, hide_index=True)

    st.subheader("Simulador rápido de Factoring")
    fc1,fc2,fc3 = st.columns(3)
    fact_v = fc1.number_input("Valor de la factura (S/)", value=min(cuentas_cob, 100_000.0), step=5_000.0, min_value=0.0)
    fact_d = fc2.number_input("Plazo (días)", value=60, step=10, min_value=1)
    fact_t = fc3.number_input("Tasa anual (%)", value=9.0, step=0.5, min_value=0.0) / 100
    costo_fact = fact_v * fact_t * fact_d/365
    liquido    = fact_v - costo_fact
    fc4,fc5 = st.columns(2)
    fc4.metric("Costo del factoring", m(costo_fact))
    fc5.metric("Líquido a recibir", m(liquido))


# ══════════════════════════════════════════════════════════
# M7 — CREACIÓN DE VALOR
# ══════════════════════════════════════════════════════════
with m7:
    st.header("M7 · Creación de Valor")
    st.caption("EVA, MVA, ROIC y WACC")

    cv1,cv2,cv3,cv4 = st.columns(4)
    cv1.metric("ROIC", pct(roic))
    cv2.metric("WACC", pct(wacc))
    cv3.metric("Spread (ROIC−WACC)", pct(spread_roic), "🟢 Crea valor" if spread_roic>0 else "🔴 Destruye valor")
    cv4.metric("EVA anual", m(eva))

    if spread_roic > 0:
        st.success(f"✅ La empresa **crea valor**: el ROIC ({pct(roic)}) supera al WACC ({pct(wacc)}). "
                    f"EVA anual = {m(eva)}.")
    else:
        st.error(f"❌ La empresa **destruye valor** porque el ROIC ({pct(roic)}) es inferior al WACC ({pct(wacc)}). "
                  f"EVA anual = {m(eva)}.")

    st.subheader("Composición del WACC")
    wacc_df = pd.DataFrame([
        ["Ke (costo del patrimonio, CAPM)", pct(ke)],
        ["Peso del patrimonio (We)",         pct(we)],
        ["Kd (costo de la deuda, antes IR)", pct(kd)],
        ["Peso de la deuda (Wd)",            pct(wd)],
        ["WACC",                             pct(wacc)],
    ], columns=["Componente","Valor"])
    st.dataframe(wacc_df, use_container_width=True, hide_index=True)

    st.subheader("¿Qué mueve el EVA?")
    st.markdown(f"""
- **Capital Invertido (IC)** = Patrimonio + Deuda = {m(ic)}
- **NOPAT** = EBIT × (1 − Impuesto) = {m(nopat)}
- **EVA = NOPAT − (IC × WACC)** = {m(nopat)} − ({m(ic)} × {pct(wacc)}) = **{m(eva)}**
""")
    if spread_roic <= 0:
        st.info("🧠 Para pasar a crear valor: mejorar el margen operativo, reducir el capital de trabajo inmovilizado, "
                "o negociar un menor costo de deuda.")


# ══════════════════════════════════════════════════════════
# M8 — VALORACIÓN DE EMPRESAS
# ══════════════════════════════════════════════════════════
with m8:
    st.header("M8 · Valoración de Empresas")

    v1,v2 = st.columns(2)
    with v1:
        n_años_v = st.slider("Años de proyección", 3, 10, 5)
        crec_dcf = st.number_input("Crecimiento FCF proyectado (%)", value=6.0, step=1.0) / 100
    with v2:
        mult_ebitda = st.number_input("Múltiplo EV/EBITDA comparable", value=5.5, step=0.5, min_value=0.1)
        mult_pe     = st.number_input("Múltiplo P/E comparable", value=10.0, step=0.5, min_value=0.1)

    fcf_proy = [fcf*(1+crec_dcf)**yr for yr in range(1, n_años_v+1)]
    vp_proy  = sum(f/(1+wacc_seg)**yr for yr,f in enumerate(fcf_proy,1))
    vt       = fcf_proy[-1]*(1+g_terminal)/max(wacc_seg-g_terminal, 0.01)
    vp_vt    = vt/(1+wacc_seg)**n_años_v
    ev_total = vp_proy + vp_vt
    eq_total = ev_total - deuda_tot

    ev_mult  = ebitda * mult_ebitda
    eq_mult_pe = utilidad_neta * mult_pe
    valor_patrimonial = patrimonio
    valor_liquidacion  = activo_corr*0.8 + (activo_tot-activo_corr)*0.5 - pasivo_corr - deuda_tot

    val_df = pd.DataFrame([
        ["DCF — Enterprise Value",     m(ev_total), "Suma de FCF descontados + valor terminal"],
        ["DCF — Equity Value",         m(eq_total), "EV − Deuda financiera"],
        ["Múltiplos — EV/EBITDA",      m(ev_mult),  f"{mult_ebitda}x × EBITDA"],
        ["Múltiplos — P/E",            m(eq_mult_pe), f"{mult_pe}x × Utilidad neta"],
        ["Valor patrimonial contable",  m(valor_patrimonial), "Patrimonio neto en libros"],
        ["Valor de liquidación",        m(valor_liquidacion), "Activos a valor de realización − pasivos"],
    ], columns=["Método","Valor","Nota"])
    st.dataframe(val_df, use_container_width=True, hide_index=True)

    vals = [eq_total, eq_mult_pe, valor_patrimonial]
    vm1,vm2,vm3 = st.columns(3)
    vm1.metric("Valor mínimo", m(min(vals)))
    vm2.metric("Valor mediano", m(float(np.median(vals))))
    vm3.metric("Valor máximo", m(max(vals)))

    st.subheader("Sensibilidad — Equity Value DCF")
    tasas   = [wacc_seg-0.02, wacc_seg-0.01, wacc_seg, wacc_seg+0.01, wacc_seg+0.02]
    crecs   = [crec_dcf-0.02, crec_dcf-0.01, crec_dcf, crec_dcf+0.01, crec_dcf+0.02]
    sens_rows = []
    for w_ in tasas:
        w_s = max(w_, 0.001)
        fila = []
        for c_ in crecs:
            fp = [fcf*(1+c_)**yr for yr in range(1, n_años_v+1)]
            vp = sum(f/(1+w_s)**yr for yr,f in enumerate(fp,1))
            vtx = fp[-1]*(1+g_terminal)/max(w_s-g_terminal, 0.01)
            eqx = vp + vtx/(1+w_s)**n_años_v - deuda_tot
            fila.append(m(eqx))
        sens_rows.append([pct(w_)] + fila)
    sens_df = pd.DataFrame(sens_rows, columns=["WACC \\ Crec."]+[pct(c) for c in crecs])
    st.dataframe(sens_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════
# M9 — RIESGO FINANCIERO
# ══════════════════════════════════════════════════════════
with m9:
    st.header("M9 · Riesgo Financiero")
    st.caption("Monte Carlo, Stress Testing, VaR y CVaR")

    r1,r2 = st.columns(2)
    with r1:
        n_sim    = st.select_slider("Simulaciones", [1000,5000,10000], 10000)
        vol_vent = st.slider("Volatilidad de ventas (%)", 1, 30, 10) / 100
    with r2:
        vol_cv   = st.slider("Volatilidad costo de ventas (%)", 1, 20, 6) / 100
        conf     = st.selectbox("Nivel de confianza VaR", [0.90, 0.95, 0.99], index=1)

    np.random.seed(123)
    sim_v  = ventas * (1+np.random.normal(0, vol_vent, n_sim))
    sim_c  = costo_v * (1+np.random.normal(0, vol_cv, n_sim))
    sim_eb = sim_v - sim_c - gastos_op
    sim_un = (sim_eb - dep - intereses) * (1-ir_tasa)

    var_level = 1-conf
    var_un = float(np.percentile(sim_un, var_level*100))
    cvar_un = float(np.mean(sim_un[sim_un<=var_un]))
    prob_un_neg = float(np.mean(sim_un<0))

    sm1,sm2,sm3 = st.columns(3)
    sm1.metric(f"VaR Utilidad Neta {conf:.0%}", m(var_un))
    sm2.metric(f"CVaR {conf:.0%}", m(cvar_un))
    sm3.metric("P(Utilidad neta < 0)", pct(prob_un_neg))

    fig_mc = go.Figure()
    fig_mc.add_trace(go.Histogram(x=sim_un/1000, nbinsx=70, marker_color="#2980b9", opacity=0.75, name="Utilidad neta sim."))
    fig_mc.add_vline(x=var_un/1000, line_color="red", line_dash="dash", annotation_text=f"VaR {conf:.0%}")
    fig_mc.add_vline(x=0, line_color="black", line_dash="dot", annotation_text="Punto de equilibrio")
    fig_mc.update_layout(title=f"Monte Carlo — Utilidad neta (miles S/) | {n_sim:,} simulaciones", height=400)
    st.plotly_chart(fig_mc, use_container_width=True)

    st.subheader("Stress Testing — escenarios")
    un_base       = utilidad_neta
    un_ventas_menos = (ventas*0.9 - costo_v*0.9 - gastos_op - dep - intereses) * (1-ir_tasa)
    un_costo_mas    = (ventas - costo_v*1.10 - gastos_op - dep - intereses) * (1-ir_tasa)
    un_combinado    = (ventas*0.9 - costo_v*1.10*0.9 - gastos_op - dep - intereses) * (1-ir_tasa)
    escenarios = pd.DataFrame([
        ["Caso base",                 m(un_base),         pct(safe(un_base, ventas))],
        ["Ventas −10%",               m(un_ventas_menos),  pct(safe(un_ventas_menos, ventas*0.9))],
        ["Costo de ventas +10%",      m(un_costo_mas),      pct(safe(un_costo_mas, ventas))],
        ["Ventas −10% y costo +10%",  m(un_combinado),      pct(safe(un_combinado, ventas*0.9))],
    ], columns=["Escenario","Utilidad neta","Margen neto"])
    st.dataframe(escenarios, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════
# M10 — IA FINANCIERA
# ══════════════════════════════════════════════════════════
with m10:
    st.header("M10 · IA Financiera")
    st.caption("Pregúntale al sistema qué pasaría con tu empresa")

    preguntas = [
        "¿Por qué disminuyó el ROE?",
        "¿Qué pasa si las ventas caen 10%?",
        "¿Qué sucede si el dólar sube?",
        "¿Qué ocurre si aumento el inventario en 20 días?",
    ]
    pregunta = st.selectbox("Selecciona una pregunta", preguntas)

    def responder(p):
        if "ROE" in p:
            factor_txt = {
                "Margen neto": "el margen neto se redujo",
                "Rotación de activos": "la rotación de activos bajó (menos ventas por cada sol de activo)",
                "Apalancamiento financiero": "cambió el apalancamiento financiero",
            }.get(factor_debil, "uno de los tres factores DuPont")
            return (f"🧠 El ROE actual es {pct(roe)} (año anterior: {pct(roe_ant)}, variación de {pct(var_roe_h)}). "
                    f"Según la descomposición DuPont, el factor que más está afectando la rentabilidad es **{factor_debil}** — "
                    f"es decir, {factor_txt}. Revisa el módulo M2 (DuPont) para el detalle completo.")
        elif "caen 10" in p or "ventas caen" in p:
            un_menor = (ventas*0.9 - costo_v*0.9 - gastos_op - dep - intereses) * (1-ir_tasa)
            var_un_esc = safe(un_menor - utilidad_neta, max(abs(utilidad_neta),1))
            return (f"🧠 Si las ventas caen 10% (manteniendo el mismo margen de costo variable), la utilidad neta pasaría de "
                    f"{m(utilidad_neta)} a aproximadamente **{m(un_menor)}** ({pct(var_un_esc)}). "
                    f"Además, la liquidez se vería presionada por menor generación de caja operativa. "
                    f"Revisa el módulo M9 (Riesgo) para el detalle de Stress Testing.")
        elif "dólar" in p:
            return ("🧠 Un alza del tipo de cambio afecta principalmente si tienes deuda, compras o ventas en dólares. "
                    "Con los datos actuales del formulario no se ha registrado exposición cambiaria específica; "
                    "si tu empresa importa insumos o tiene deuda en USD, un alza del dólar aumenta el costo de ventas "
                    "y/o el gasto financiero en soles, presionando el margen bruto y el EVA. "
                    "Se recomienda registrar el % de compras/deuda en moneda extranjera para una simulación precisa.")
        elif "inventario" in p:
            dias_extra = 20
            cce_nuevo = ciclo_cce + dias_extra
            capital_inmovilizado = safe(costo_v, 365) * dias_extra
            return (f"🧠 Si el inventario aumenta 20 días adicionales, el Ciclo de Conversión del Efectivo pasaría de "
                    f"{ciclo_cce:.0f} a **{cce_nuevo:.0f} días**, inmovilizando aproximadamente **{m(capital_inmovilizado)}** "
                    f"adicionales de capital de trabajo — capital que deja de estar disponible como caja. "
                    f"Esto también reduce la rotación de inventarios y puede presionar la necesidad de financiamiento de corto plazo.")
        return "🧠 Selecciona una pregunta de la lista para obtener el análisis."

    st.markdown(responder(pregunta))

    st.divider()
    st.caption("Nota: estas respuestas se generan con reglas financieras sobre tus propios datos. "
               "Para preguntas libres en lenguaje natural, este motor puede conectarse a un modelo LLM (OpenAI/Claude) "
               "pasando el contexto financiero de la empresa.")


# ══════════════════════════════════════════════════════════
# M11 — WARREN BUFFETT SCORE
# ══════════════════════════════════════════════════════════
with m11:
    st.header("M11 · Warren Buffett Score")
    st.caption("Traducción práctica de criterios de inversión de calidad")

    wb_df = pd.DataFrame([
        ["Calidad del negocio",     round(score_calidad_negocio,0), sem(score_calidad_negocio/100)],
        ["Fortaleza financiera",    round(score_fortaleza,0),        sem(score_fortaleza/100)],
        ["Gestión del capital",     round(score_gestion_capital,0),  sem(score_gestion_capital/100)],
        ["Valoración",              round(score_valoracion_wb,0),    sem(score_valoracion_wb/100)],
    ], columns=["Componente","Puntaje (0-100)","Semáforo"])
    st.dataframe(wb_df, use_container_width=True, hide_index=True)

    st.metric("Score Final Warren Buffett", f"{score_buffett_total:.0f}/100",
              "🟢 Empresa de calidad" if score_buffett_total>=70 else ("🟡 Evaluar con más detalle" if score_buffett_total>=50 else "🔴 Requiere atención"))

    margen_seguridad = max(0.0, 1 - safe(ic, max(eq_dcf, 1))) if eq_dcf > 0 else 0.0
    st.subheader("Valor intrínseco y margen de seguridad")
    ms1,ms2,ms3 = st.columns(3)
    ms1.metric("Valor intrínseco estimado (Equity DCF)", m(eq_dcf))
    ms2.metric("Capital invertido", m(ic))
    ms3.metric("Margen de seguridad", pct(margen_seguridad), "🟢 Subvalorado" if margen_seguridad>0.20 else "🔴 Sin margen relevante")

    st.subheader("Interpretación")
    if score_buffett_total >= 70:
        st.success("✅ La empresa muestra características de un negocio de calidad: rentabilidad consistente, "
                    "solidez financiera y buena gestión del capital.")
    elif score_buffett_total >= 50:
        st.warning("⚠️ Negocio con potencial, pero con algunos componentes por reforzar antes de considerarlo de calidad Buffett.")
    else:
        st.error("🚨 El negocio, con los datos actuales, no cumple varios criterios de calidad e inversión de largo plazo. "
                  "Priorizar el componente con menor puntaje.")


# ══════════════════════════════════════════════════════════
# M12 — INTELIGENCIA COMPETITIVA
# ══════════════════════════════════════════════════════════
with m12:
    st.header("M12 · Inteligencia Competitiva")
    st.caption("¿Mi empresa está ganando o perdiendo frente a su competencia?")

    comp_cols_num = ["Ventas","Margen EBITDA %","ROE %","Endeudamiento","Liquidez",
                      "Precio promedio (S/)","Participación mercado %"]
    comp_df = comp_df_edit.copy()
    if "Competidor" not in comp_df.columns:
        comp_df["Competidor"] = [f"Competidor {i+1}" for i in range(len(comp_df))]
    comp_df["Competidor"] = comp_df["Competidor"].fillna("").replace("", None)
    comp_df = comp_df.dropna(subset=["Competidor"])
    for col in comp_cols_num:
        if col not in comp_df.columns:
            comp_df[col] = 0.0
        comp_df[col] = pd.to_numeric(comp_df[col], errors="coerce").fillna(0.0)

    hay_competidores = len(comp_df) > 0
    prom_comp = comp_df[comp_cols_num].mean() if hay_competidores else pd.Series({c: 0.0 for c in comp_cols_num})

    mi_fila = pd.DataFrame([{
        "Competidor": f"🏢 {empresa} (mi empresa)",
        "Ventas": ventas,
        "Margen EBITDA %": margen_ebitda*100,
        "ROE %": roe*100,
        "Endeudamiento": endeudamiento,
        "Liquidez": liquidez_corr,
        "Precio promedio (S/)": np.nan,
        "Participación mercado %": np.nan,
    }])
    tabla_comp = pd.concat([mi_fila, comp_df], ignore_index=True)

    sub1, sub2, sub3, sub4, sub5 = st.tabs([
        "📊 Benchmark Financiero", "🥧 Mercado y Precios", "🕸️ Radar Competitivo",
        "📆 Benchmark Interno", "🧠 IA Competitiva",
    ])

    # ---- Sub 1: Benchmark financiero ----
    with sub1:
        st.subheader("Comparación financiera — mi empresa vs. competencia")
        tabla_fmt = tabla_comp.copy()
        tabla_fmt["Margen EBITDA %"] = tabla_fmt["Margen EBITDA %"].map(lambda x: f"{x:.1f}%")
        tabla_fmt["ROE %"] = tabla_fmt["ROE %"].map(lambda x: f"{x:.1f}%")
        tabla_fmt["Endeudamiento"] = tabla_fmt["Endeudamiento"].map(lambda x: f"{x:.2f}")
        tabla_fmt["Liquidez"] = tabla_fmt["Liquidez"].map(lambda x: f"{x:.2f}x")
        tabla_fmt["Ventas"] = tabla_fmt["Ventas"].map(m)
        tabla_fmt["Precio promedio (S/)"] = tabla_fmt["Precio promedio (S/)"].map(lambda x: f"S/ {x:,.0f}" if pd.notna(x) else "—")
        tabla_fmt["Participación mercado %"] = tabla_fmt["Participación mercado %"].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        st.dataframe(tabla_fmt, use_container_width=True, hide_index=True)

        if hay_competidores:
            b1,b2,b3,b4 = st.columns(4)
            b1.metric("Margen EBITDA vs. mercado", pct(margen_ebitda),
                      f"{margen_ebitda*100 - prom_comp['Margen EBITDA %']:+.1f} pts")
            b2.metric("ROE vs. mercado", pct(roe),
                      f"{roe*100 - prom_comp['ROE %']:+.1f} pts")
            b3.metric("Endeudamiento vs. mercado", f"{endeudamiento:.2f}",
                      f"{endeudamiento - prom_comp['Endeudamiento']:+.2f}", delta_color="inverse")
            b4.metric("Liquidez vs. mercado", f"{liquidez_corr:.2f}x",
                      f"{liquidez_corr - prom_comp['Liquidez']:+.2f}")
        else:
            st.info("Agrega competidores en la barra lateral para activar la comparación automática.")

    # ---- Sub 2: Mercado y precios ----
    with sub2:
        st.subheader("Participación de mercado")
        if hay_competidores and comp_df["Participación mercado %"].sum() > 0:
            labels_ms = list(comp_df["Competidor"])
            values_ms = list(comp_df["Participación mercado %"])
            mi_part = max(0.0, 100 - sum(values_ms))
            fig_ms = go.Figure(go.Bar(
                x=[f"🏢 {empresa}"] + labels_ms,
                y=[mi_part] + values_ms,
                marker_color=["#1F3864"] + ["#66BB6A"]*len(labels_ms),
                text=[f"{v:.1f}%" for v in [mi_part]+values_ms], textposition="outside",
            ))
            fig_ms.update_layout(height=380, yaxis_title="Participación de mercado (%)")
            st.plotly_chart(fig_ms, use_container_width=True)
            st.caption("La participación de tu empresa se estima como el residuo (100% − Σ competidores). "
                       "Ajusta las cifras si cuentas con datos propios de mercado (OSIPTEL, gremio, INEI, etc.).")
        else:
            st.info("Ingresa la participación de mercado (%) de tus competidores en la barra lateral para ver este gráfico.")

        st.subheader("Precio promedio de la competencia")
        if hay_competidores and comp_df["Precio promedio (S/)"].sum() > 0:
            fig_precio = go.Figure(go.Bar(
                x=list(comp_df["Competidor"]),
                y=list(comp_df["Precio promedio (S/)"]),
                marker_color="#8E24AA",
                text=[f"S/ {v:,.0f}" for v in comp_df["Precio promedio (S/)"]], textposition="outside",
            ))
            fig_precio.update_layout(height=340, yaxis_title="Precio promedio (S/)")
            st.plotly_chart(fig_precio, use_container_width=True)
        else:
            st.info("Ingresa precios promedio de la competencia en la barra lateral para ver este gráfico.")

    # ---- Sub 3: Radar competitivo ----
    with sub3:
        st.subheader("Radar competitivo — mi empresa vs. promedio del mercado")
        cats = ["Rentabilidad (ROE)","Margen EBITDA","Liquidez","Bajo endeudamiento"]
        def norm(v, ref):
            return min(1.0, max(0.0, safe(v, ref))) if ref else 0.0
        mi_vals = [norm(roe,0.20), norm(margen_ebitda,0.25), norm(liquidez_corr,2.0), norm(1-endeudamiento,0.6)]
        if hay_competidores:
            comp_vals = [
                norm(prom_comp["ROE %"]/100, 0.20),
                norm(prom_comp["Margen EBITDA %"]/100, 0.25),
                norm(prom_comp["Liquidez"], 2.0),
                norm(1-prom_comp["Endeudamiento"], 0.6),
            ]
        else:
            comp_vals = [0,0,0,0]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=mi_vals+[mi_vals[0]], theta=cats+[cats[0]],
                                             fill='toself', name=f"🏢 {empresa}", line_color="#1F3864"))
        fig_radar.add_trace(go.Scatterpolar(r=comp_vals+[comp_vals[0]], theta=cats+[cats[0]],
                                             fill='toself', name="Promedio competencia", line_color="#E53935"))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])), height=460, showlegend=True)
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption("Cada eje está normalizado entre 0 y 1 respecto a una meta de referencia del sector.")

    # ---- Sub 4: Benchmark interno ----
    with sub4:
        st.subheader("Benchmark interno — cuando no hay comparables públicos")
        st.caption("Si tu sector no publica información financiera detallada (empresas privadas, sin obligación de "
                   "reporte), compara tu propio desempeño en el tiempo: siempre es posible y aporta valor.")
        bi1,bi2,bi3 = st.columns(3)
        bi1.metric("Ventas: año actual vs. anterior", m(ventas), pct(var_ventas_h) if ventas_ant>0 else "—")
        bi2.metric("EBITDA: año actual vs. anterior", m(ebitda), pct(var_ebitda_h) if ebitda_ant_in!=0 else "—")
        bi3.metric("Utilidad neta: año actual vs. anterior", m(utilidad_neta), pct(var_un_h) if un_ant!=0 else "—")
        st.info("💡 Complementa este benchmark interno con fuentes públicas agregadas cuando existan "
                "(INEI, SUNAT, gremios sectoriales, OSIPTEL para telecom) para tener una referencia de "
                "\"promedio del sector\" aunque no tengas el detalle financiero de cada competidor.")

    # ---- Sub 5: IA competitiva ----
    with sub5:
        st.subheader("🧠 Análisis automático de posición competitiva")
        insights = []
        if hay_competidores:
            if margen_ebitda*100 >= prom_comp["Margen EBITDA %"]:
                insights.append(f"🟢 Tu margen EBITDA ({pct(margen_ebitda)}) es superior al promedio de la "
                                f"competencia ({prom_comp['Margen EBITDA %']:.1f}%).")
            else:
                insights.append(f"🔴 Tu margen EBITDA ({pct(margen_ebitda)}) está por debajo del promedio de la "
                                f"competencia ({prom_comp['Margen EBITDA %']:.1f}%). Revisar estructura de costos "
                                f"o estrategia comercial.")
            if roe*100 >= prom_comp["ROE %"]:
                insights.append(f"🟢 Tu ROE ({pct(roe)}) supera al promedio del mercado ({prom_comp['ROE %']:.1f}%).")
            else:
                insights.append(f"🟡 Tu ROE ({pct(roe)}) está debajo del promedio del mercado ({prom_comp['ROE %']:.1f}%).")
            if endeudamiento <= prom_comp["Endeudamiento"]:
                insights.append(f"🟢 Tu endeudamiento ({endeudamiento:.2f}) es más conservador que el promedio "
                                f"del mercado ({prom_comp['Endeudamiento']:.2f}).")
            else:
                insights.append(f"🔴 Tu endeudamiento ({endeudamiento:.2f}) es mayor al promedio del mercado "
                                f"({prom_comp['Endeudamiento']:.2f}).")
            if liquidez_corr >= prom_comp["Liquidez"]:
                insights.append(f"🟢 Tu liquidez ({liquidez_corr:.2f}x) es superior al promedio de la competencia "
                                f"({prom_comp['Liquidez']:.2f}x).")
            else:
                insights.append(f"🟡 Tu liquidez ({liquidez_corr:.2f}x) está por debajo del promedio de la "
                                f"competencia ({prom_comp['Liquidez']:.2f}x).")
        else:
            insights.append("Agrega al menos un competidor en la barra lateral para generar el análisis automático.")

        for i in insights:
            st.markdown(i)

        st.divider()
        st.caption("Nota: cuando no existan datos financieros públicos de tu competencia directa (empresas privadas, "
                   "como suele ocurrir en telecomunicaciones u otros sectores regulados), usa el Benchmark Interno "
                   "(año vs. año, meta vs. real) y, si están disponibles, promedios sectoriales de fuentes públicas "
                   "como INEI, SUNAT u OSIPTEL, para mantener una referencia útil de comparación.")

st.divider()
st.caption("RISK ANALYTICS AI — PYME © 2026 | Ruta de Madurez Financiera | Desarrollado con Python + Streamlit")
