# ============================================================
# RISK ANALYTICS AI
# Sistema Integral de Tesorería, Creación de Valor y Valoración Corporativa
# 14 Niveles — Versión Streamlit Completa
# Ejecutar: streamlit run risk_analytics_ai.py
# ============================================================

import math
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.optimize import minimize
import streamlit as st

if st.sidebar.button("⬅ Volver al árbol de navegación", use_container_width=True):
    st.switch_page("Home.py")
st.sidebar.divider()


# ── Helpers ────────────────────────────────────────────────
def m(x):        return f"S/ {x:,.0f}"
def musd(x):     return f"$ {x:,.0f}"
def pct(x):      return f"{x*100:.1f}%"
def safe(n,d):   return n/d if d and d!=0 else 0.0
def sem(v, g=0.7, a=0.4):
    return "🟢" if v>=g else ("🟡" if v>=a else "🔴")

# ── Estilo CSS ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"]{font-size:1.3rem;font-weight:700;}
.stTabs [data-baseweb="tab"]{font-size:0.78rem;font-weight:600;}
.block-container{padding-top:1rem;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — INPUTS MAESTROS
# ============================================================
st.sidebar.image("https://img.icons8.com/fluency/96/bank-building.png", width=60)
st.sidebar.title("RISK ANALYTICS AI")
st.sidebar.caption("Sistema de Inteligencia Financiera Corporativa")
st.sidebar.divider()

st.sidebar.subheader("🏢 Empresa")
empresa     = st.sidebar.text_input("Nombre empresa", "Corporación Ejemplo SAC")
ruc         = st.sidebar.text_input("RUC", "20600000001")
sector      = st.sidebar.selectbox("Sector", ["Manufactura","Retail","Servicios","Minería","Construcción","Tecnología","Agroindustria","Financiero"])
moneda      = st.sidebar.selectbox("Moneda base", ["PEN (S/)","USD ($)"])
tc          = st.sidebar.number_input("Tipo de cambio", value=3.72, step=0.01, format="%.4f")

st.sidebar.divider()
st.sidebar.subheader("📊 Estado de Resultados")
ventas      = st.sidebar.number_input("Ventas netas",         value=8_000_000.0, step=100_000.0)
costo_v     = st.sidebar.number_input("Costo de ventas",      value=5_000_000.0, step=100_000.0)
gastos_op   = st.sidebar.number_input("Gastos operativos",    value=1_200_000.0, step=50_000.0)
dep         = st.sidebar.number_input("Depreciación/Amort.",  value=200_000.0,   step=10_000.0)
intereses   = st.sidebar.number_input("Gastos financieros",   value=180_000.0,   step=10_000.0)
ir_tasa     = st.sidebar.slider("Tasa IR (%)", 0.0, 40.0, 29.5, 0.5) / 100

st.sidebar.divider()
st.sidebar.subheader("⚖️ Balance")
activo_tot  = st.sidebar.number_input("Activo total",         value=12_000_000.0,step=200_000.0)
activo_corr = st.sidebar.number_input("Activo corriente",     value=4_500_000.0, step=100_000.0)
inventario  = st.sidebar.number_input("Inventarios",          value=1_200_000.0, step=50_000.0)
caja_saldo  = st.sidebar.number_input("Caja y bancos",        value=800_000.0,   step=50_000.0)
pasivo_corr = st.sidebar.number_input("Pasivo corriente",     value=2_800_000.0, step=100_000.0)
deuda_tot   = st.sidebar.number_input("Deuda financiera total",value=3_500_000.0,step=100_000.0)
patrimonio  = st.sidebar.number_input("Patrimonio neto",      value=5_200_000.0, step=100_000.0)
cuentas_cob = st.sidebar.number_input("Cuentas por cobrar",   value=1_800_000.0, step=50_000.0)
cuentas_pag = st.sidebar.number_input("Cuentas por pagar",    value=900_000.0,   step=50_000.0)

st.sidebar.divider()
st.sidebar.subheader("💰 Costo de Capital")
rf          = st.sidebar.number_input("Rf — Tasa libre riesgo", value=0.053, step=0.001, format="%.3f")
beta        = st.sidebar.number_input("Beta del sector",         value=1.05,  step=0.05)
erp         = st.sidebar.number_input("Prima de riesgo (ERP)",  value=0.062, step=0.001, format="%.3f")
rp          = st.sidebar.number_input("Riesgo país (EMBI)",     value=0.018, step=0.001, format="%.3f")
kd          = st.sidebar.number_input("Costo deuda Kd (antes IR)", value=0.105, step=0.005, format="%.3f")
g_terminal  = st.sidebar.number_input("Crecimiento perpetuo g", value=0.03, step=0.005, format="%.3f")

st.sidebar.divider()
st.sidebar.subheader("📦 Tesorería y Operaciones")
dias_cobro  = st.sidebar.number_input("Días promedio cobro",   value=60,  step=5)
dias_pago   = st.sidebar.number_input("Días promedio pago",    value=35,  step=5)
dias_inv    = st.sidebar.number_input("Días inventario",       value=45,  step=5)
capex       = st.sidebar.number_input("CAPEX",                 value=350_000.0, step=50_000.0)
n_trabajadores = st.sidebar.number_input("N° de trabajadores", value=120, step=5, min_value=1)

st.sidebar.divider()
st.sidebar.subheader("🏆 Competidores (Inteligencia Competitiva)")
st.sidebar.caption("Edita, agrega o borra filas para comparar tu empresa contra el mercado. "
                    "Si tu competencia no publica información financiera (empresas privadas / no listadas), "
                    "deja la tabla en blanco y usa el Benchmark Sectorial/Interno del módulo N15.")
comp_default_corp = pd.DataFrame([
    {"Competidor": "Competidor A", "Ventas": round(ventas*1.8, -3), "Margen EBITDA %": 24.0, "ROE %": 17.0,
     "Deuda/EBITDA": 2.2, "Liquidez": 1.6, "ARPU / Ticket prom. (S/)": 130.0, "Churn %": 2.5,
     "Participación mercado %": 34.0},
    {"Competidor": "Competidor B", "Ventas": round(ventas*1.3, -3), "Margen EBITDA %": 20.0, "ROE %": 14.0,
     "Deuda/EBITDA": 2.6, "Liquidez": 1.4, "ARPU / Ticket prom. (S/)": 118.0, "Churn %": 3.1,
     "Participación mercado %": 24.0},
    {"Competidor": "Competidor C", "Ventas": round(ventas*0.6, -3), "Margen EBITDA %": 15.0, "ROE %": 9.0,
     "Deuda/EBITDA": 3.4, "Liquidez": 1.1, "ARPU / Ticket prom. (S/)": 105.0, "Churn %": 4.2,
     "Participación mercado %": 11.0},
])
comp_df_edit_corp = st.sidebar.data_editor(
    comp_default_corp, num_rows="dynamic", use_container_width=True, key="corp_comp_editor",
    column_config={
        "Ventas": st.column_config.NumberColumn(format="%.0f"),
        "Margen EBITDA %": st.column_config.NumberColumn(format="%.1f"),
        "ROE %": st.column_config.NumberColumn(format="%.1f"),
        "Deuda/EBITDA": st.column_config.NumberColumn(format="%.2f"),
        "Liquidez": st.column_config.NumberColumn(format="%.2f"),
        "ARPU / Ticket prom. (S/)": st.column_config.NumberColumn(format="%.0f"),
        "Churn %": st.column_config.NumberColumn(format="%.1f"),
        "Participación mercado %": st.column_config.NumberColumn(format="%.1f"),
    },
)

# ============================================================
# MOTOR DE CÁLCULO FINANCIERO
# ============================================================
utilidad_bruta  = ventas - costo_v
ebitda          = utilidad_bruta - gastos_op
ebit            = ebitda - dep
uai             = ebit - intereses
utilidad_neta   = uai * (1 - ir_tasa)
nopat           = ebit * (1 - ir_tasa)

ke              = rf + beta * erp + rp
wd              = safe(deuda_tot, deuda_tot + patrimonio)
we              = 1 - wd
wacc            = we * ke + wd * kd * (1 - ir_tasa)
ic              = patrimonio + deuda_tot
eva             = nopat - ic * wacc
mva             = eva / max(wacc - g_terminal, 0.001) if wacc > g_terminal else 0

roic            = safe(nopat, ic)
roe             = safe(utilidad_neta, patrimonio)
roa             = safe(utilidad_neta, activo_tot)
roi             = safe(utilidad_neta, ic)
margen_neto     = safe(utilidad_neta, ventas)
margen_ebitda   = safe(ebitda, ventas)
margen_bruto    = safe(utilidad_bruta, ventas)

liquidez_corr   = safe(activo_corr, pasivo_corr)
liquidez_ac     = safe(activo_corr - inventario, pasivo_corr)
cap_trabajo     = activo_corr - pasivo_corr
ciclo_cce       = dias_cobro + dias_inv - dias_pago
deuda_ebitda    = safe(deuda_tot, ebitda)
cobertura_int   = safe(ebit, intereses)
deuda_pat       = safe(deuda_tot, patrimonio)

fcf             = nopat + dep - capex - (cap_trabajo * 0.05)
valor_terminal  = safe(fcf * (1 + g_terminal), wacc - g_terminal)
ev_dcf          = fcf / max(wacc, 0.001) + valor_terminal

# Altman Z-Score adaptado
x1 = safe(cap_trabajo, activo_tot)
x2 = safe(utilidad_neta, activo_tot)
x3 = safe(ebit, activo_tot)
x4 = safe(patrimonio, deuda_tot)
x5 = safe(ventas, activo_tot)
altman_z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + x5
altman_zona = "🟢 Zona segura" if altman_z > 2.99 else ("🟡 Zona gris" if altman_z > 1.81 else "🔴 Zona peligro")

# Score global
score_fin = min(100, (
    (min(roic/max(wacc, 0.001), 2)/2 * 25) +
    (min(liquidez_corr/2, 1) * 20) +
    (max(0, min(1, 1 - deuda_ebitda/6)) * 20) +
    (max(0, min(1, margen_ebitda/0.20)) * 20) +
    (max(0, min(1, cobertura_int/3)) * 15)
) )

# ============================================================
# TÍTULO
# ============================================================
st.title("🏦 RISK ANALYTICS AI — Sistema de Inteligencia Financiera Corporativa")
st.caption(f"{empresa} | RUC {ruc} | Sector: {sector} | {datetime.date.today().strftime('%d/%m/%Y')}")

# Score global en banner
bc1,bc2,bc3,bc4,bc5 = st.columns(5)
bc1.metric("Score Financiero",   f"{score_fin:.0f}/100", sem(score_fin/100))
bc2.metric("EVA",                m(eva),  "Crea valor" if eva>0 else "Destruye")
bc3.metric("WACC",               pct(wacc))
bc4.metric("ROIC",               pct(roic), f"vs WACC {pct(wacc)}")
bc5.metric("Altman Z",           f"{altman_z:.2f}", altman_zona)

st.divider()

# ============================================================
# TABS — 14 NIVELES
# ============================================================
(t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15) = st.tabs([
    "N1 · Corporate Control",
    "N2 · Tesorería",
    "N3 · Intel Financiera",
    "N4 · Warren Buffett",
    "N5 · Valoración",
    "N6 · Monte Carlo",
    "N7 · Markowitz",
    "N8 · Machine Learning",
    "N9 · Instrumentos",
    "N10 · Intel Tributaria",
    "N11 · Controller",
    "N12 · Intel Estratégica",
    "N13 · IA Financiera",
    "N14 · CEO Dashboard",
    "N15 · Intel Competitiva",
])


# ══════════════════════════════════════════════════════════════════
# N1 — CORPORATE CONTROL CENTER
# ══════════════════════════════════════════════════════════════════
with t1:
    st.header("N1 · Corporate Control Center — KPIs Ejecutivos")

    r1c1,r1c2,r1c3,r1c4,r1c5 = st.columns(5)
    r1c1.metric("Ventas",        m(ventas))
    r1c2.metric("EBITDA",        m(ebitda),     pct(margen_ebitda))
    r1c3.metric("EBIT",          m(ebit))
    r1c4.metric("Utilidad neta", m(utilidad_neta), pct(margen_neto))
    r1c5.metric("FCF",           m(fcf))

    r2c1,r2c2,r2c3,r2c4,r2c5 = st.columns(5)
    r2c1.metric("EVA",           m(eva),   "🟢 Crea" if eva>0 else "🔴 Destruye")
    r2c2.metric("MVA",           m(mva))
    r2c3.metric("ROIC",          pct(roic), f"WACC {pct(wacc)}")
    r2c4.metric("ROE",           pct(roe))
    r2c5.metric("ROA",           pct(roa))

    r3c1,r3c2,r3c3,r3c4,r3c5 = st.columns(5)
    r3c1.metric("Ke (CAPM)",     pct(ke))
    r3c2.metric("WACC",          pct(wacc))
    r3c3.metric("Liquidez corr.",f"{liquidez_corr:.2f}x", sem(liquidez_corr/2))
    r3c4.metric("Capital trabajo",m(cap_trabajo))
    r3c5.metric("CCE (días)",    f"{ciclo_cce:.0f} días")

    r4c1,r4c2,r4c3,r4c4,r4c5 = st.columns(5)
    r4c1.metric("Deuda/EBITDA",  f"{deuda_ebitda:.2f}x", sem(1-deuda_ebitda/6))
    r4c2.metric("Cobertura int.",f"{cobertura_int:.2f}x", sem(cobertura_int/3))
    r4c3.metric("Deuda/Patrim.", f"{deuda_pat:.2f}x")
    r4c4.metric("Altman Z-Score",f"{altman_z:.2f}",       altman_zona)
    r4c5.metric("Score Global",  f"{score_fin:.0f}/100",  sem(score_fin/100))

    st.divider()
    # Semáforos detallados
    st.subheader("Semáforos por área")
    kpi_rows = [
        ["ROIC vs WACC",        pct(roic),        "🟢 Crea valor" if roic>wacc else "🔴 Destruye"],
        ["Margen EBITDA",       pct(margen_ebitda),"🟢 OK" if margen_ebitda>=0.15 else ("🟡 Bajo" if margen_ebitda>=0.08 else "🔴 Crítico")],
        ["Liquidez corriente",  f"{liquidez_corr:.2f}x","🟢 OK" if liquidez_corr>=1.5 else ("🟡 Vigilar" if liquidez_corr>=1.0 else "🔴 Crítico")],
        ["Deuda/EBITDA",        f"{deuda_ebitda:.2f}x","🟢 OK" if deuda_ebitda<=2.5 else ("🟡 Atención" if deuda_ebitda<=4 else "🔴 Alto")],
        ["Cobertura intereses", f"{cobertura_int:.2f}x","🟢 OK" if cobertura_int>=3 else ("🟡 Mínimo" if cobertura_int>=1.5 else "🔴 Riesgo")],
        ["EVA",                 m(eva),            "🟢 Crea valor" if eva>0 else "🔴 Destruye valor"],
        ["Altman Z-Score",      f"{altman_z:.2f}", altman_zona],
        ["Capital de trabajo",  m(cap_trabajo),    "🟢 OK" if cap_trabajo>0 else "🔴 Negativo"],
        ["Margen neto",         pct(margen_neto),  "🟢 OK" if margen_neto>=0.08 else ("🟡 Bajo" if margen_neto>=0.03 else "🔴 Crítico")],
    ]
    st.dataframe(pd.DataFrame(kpi_rows,columns=["KPI","Valor","Semáforo"]),
                 use_container_width=True, hide_index=True)

    # Gráfico radar
    cats = ["Rentabilidad","Liquidez","Solvencia","Eficiencia","Crecimiento"]
    vals = [
        min(roic/max(wacc,0.001)/2,1),
        min(liquidez_corr/2,1),
        max(0,1-deuda_ebitda/6),
        min(margen_ebitda/0.20,1),
        min(fcf/max(ventas*0.05,1),1),
    ]
    fig_rad = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]],
        fill="toself", line_color="#1F3864", fillcolor="rgba(31,56,100,0.25)",
        name=empresa,
    ))
    fig_rad.update_layout(polar=dict(radialaxis=dict(range=[0,1])),
                          title="Radar Financiero Global", height=380)
    st.plotly_chart(fig_rad, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# N2 — INTELIGENCIA DE TESORERÍA
# ══════════════════════════════════════════════════════════════════
with t2:
    st.header("N2 · Inteligencia de Tesorería")

    st.subheader("Caja proyectada — 12 meses")
    np.random.seed(42)
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    ingresos_m  = ventas/12 * (1 + np.random.normal(0, 0.08, 12))
    egresos_m   = (costo_v+gastos_op)/12 * (1 + np.random.normal(0, 0.06, 12))
    flujo_m     = ingresos_m - egresos_m
    caja_acum   = caja_saldo + np.cumsum(flujo_m)

    fig_caja = go.Figure()
    fig_caja.add_bar(x=meses, y=ingresos_m, name="Ingresos", marker_color="#2ecc71")
    fig_caja.add_bar(x=meses, y=-egresos_m, name="Egresos",  marker_color="#e74c3c")
    fig_caja.add_scatter(x=meses, y=caja_acum, name="Caja acum.", mode="lines+markers",
                         line=dict(color="#1F3864",width=3))
    fig_caja.update_layout(barmode="relative", title="Forecast de Caja 12M", height=400)
    st.plotly_chart(fig_caja, use_container_width=True)

    tc1,tc2,tc3,tc4 = st.columns(4)
    tc1.metric("Caja actual",           m(caja_saldo))
    tc2.metric("Flujo mensual prom.",   m(float(np.mean(flujo_m))))
    tc3.metric("Caja proyectada 12M",   m(float(caja_acum[-1])))
    tc4.metric("Meses de cobertura",    f"{safe(caja_saldo, np.mean(egresos_m)):.1f} meses")

    st.divider()
    st.subheader("💧 Liquidez Inteligente — ¿Qué hacer con tu caja?")
    superavit = float(caja_acum[-1]) - caja_saldo

    if superavit > 0:
        st.success(f"✅ Superávit proyectado: {m(superavit)}")
        opciones_inv = pd.DataFrame([
            ["Fondo Mutuo de Liquidez","0.5-1.5%","T+0 / T+1","Muy bajo","Máxima liquidez, bajo riesgo"],
            ["Depósito a plazo 30-90d","4-6%",    "Al vencimiento","Bajo","Rendimiento fijo, sin liquidez antes del plazo"],
            ["Bonos soberanos corto plazo","5-6%","Mercado secundario","Muy bajo","Respaldo gobierno, buen rendimiento"],
            ["Letras del Tesoro","4.5-5.5%","T+2","Muy bajo","Instrumentos corto plazo del MEF"],
            ["Overnight interbancario","3-4%","T+0","Muy bajo","Solo disponible para empresas con línea bancaria"],
            ["Factoring inverso","Ahorro 1-2% descuento","Variable","Bajo","Acelerar pago a proveedores con descuento pronto pago"],
        ], columns=["Instrumento","Rendimiento est.","Liquidación","Riesgo","Comentario"])
        st.dataframe(opciones_inv, use_container_width=True, hide_index=True)
    else:
        st.warning(f"⚠️ Déficit proyectado: {m(abs(superavit))}")
        opciones_fin = pd.DataFrame([
            ["Crédito revolvente","8-12%","Inmediato","Bajo","Línea abierta para necesidades puntuales de caja"],
            ["Factoring de cuentas por cobrar","6-9%","24-48h","Bajo","Adelanto de facturas vigentes"],
            ["Confirming","6-8%","Según proveedor","Bajo","El banco paga al proveedor, tú pagas al banco después"],
            ["Leasing operativo/financiero","7-10%","Según activo","Medio","Libera caja reemplazando compra por cuotas"],
            ["Préstamo sindicado","7-10%","60-90 días","Medio","Para montos grandes, varios bancos participan"],
            ["Emisión de bonos corporativos","6-9%","3-6 meses","Medio","Mercado de capitales, ticket mínimo S/10MM"],
        ], columns=["Instrumento","Costo est.","Disponibilidad","Riesgo implant.","Comentario"])
        st.dataframe(opciones_fin, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Ciclo de Conversión del Efectivo (CCE)")
    cce_df = pd.DataFrame([
        ["Días de cobro (DSO)",     dias_cobro,  "Días promedio que tarda el cliente en pagar"],
        ["Días de inventario (DIO)", dias_inv,   "Días promedio que el inventario permanece en almacén"],
        ["Días de pago (DPO)",      dias_pago,   "Días promedio que tardas en pagar a proveedores"],
        ["CCE = DSO + DIO - DPO",   ciclo_cce,  "Días que la empresa financia su propio ciclo operativo"],
    ], columns=["Indicador","Días","Interpretación"])
    st.dataframe(cce_df, use_container_width=True, hide_index=True)
    if ciclo_cce > 60:
        st.error(f"🔴 CCE de {ciclo_cce:.0f} días es alto. La empresa financia demasiado tiempo su ciclo. Reducir DSO o ampliar DPO.")
    elif ciclo_cce > 30:
        st.warning(f"🟡 CCE de {ciclo_cce:.0f} días. Optimizar cobranza o negociar mejores plazos con proveedores.")
    else:
        st.success(f"🟢 CCE de {ciclo_cce:.0f} días. Ciclo eficiente.")


# ══════════════════════════════════════════════════════════════════
# N3 — INTELIGENCIA FINANCIERA
# ══════════════════════════════════════════════════════════════════
with t3:
    st.header("N3 · Inteligencia Financiera — Creación y Destrucción de Valor")

    st.subheader("¿Por qué sube o baja el valor?")
    spread_roic = roic - wacc
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("ROIC",         pct(roic))
    c2.metric("WACC",         pct(wacc))
    c3.metric("Spread ROIC-WACC", pct(spread_roic), "🟢 Crea" if spread_roic>0 else "🔴 Destruye")
    c4.metric("EVA anual",    m(eva))

    if spread_roic > 0:
        st.success(f"✅ La empresa crea {m(eva)} de valor anual. El ROIC ({pct(roic)}) supera el costo del capital ({pct(wacc)}) en {pct(spread_roic)}.")
    else:
        st.error(f"❌ La empresa destruye {m(abs(eva))} de valor anual. El ROIC ({pct(roic)}) está {pct(abs(spread_roic))} por debajo del WACC ({pct(wacc)}).")

    # Árbol de valor (DuPont ampliado)
    st.subheader("Árbol de Creación de Valor — DuPont Ampliado")
    dupont = pd.DataFrame([
        ["Nivel 1","EVA = NOPAT − IC × WACC",               m(eva)],
        ["Nivel 2","NOPAT = EBIT × (1−t)",                   m(nopat)],
        ["Nivel 2","IC = Patrimonio + Deuda financiera",      m(ic)],
        ["Nivel 2","WACC = Ke×We + Kd×(1−t)×Wd",            pct(wacc)],
        ["Nivel 3","EBIT = Ventas − CV − Gastos − Dep",      m(ebit)],
        ["Nivel 3","Ke = Rf + β×ERP + Riesgo país",          pct(ke)],
        ["Nivel 3","Kd antes de impuesto",                    pct(kd)],
        ["Nivel 4","Margen EBIT",                             pct(safe(ebit,ventas))],
        ["Nivel 4","Rotación de activos (Ventas/IC)",         f"{safe(ventas,ic):.2f}x"],
        ["Nivel 4","Palanca financiera (Activo/Patrimonio)",  f"{safe(activo_tot,patrimonio):.2f}x"],
    ], columns=["Nivel","Fórmula","Valor"])
    st.dataframe(dupont, use_container_width=True, hide_index=True)

    # Análisis de riesgos
    st.subheader("Mapa de Riesgos Financieros")
    riesgos = pd.DataFrame([
        ["Riesgo de crédito/liquidez",  "Liquidez corriente",     f"{liquidez_corr:.2f}x",  "🟢 OK" if liquidez_corr>=1.5 else "🔴 Riesgo"],
        ["Riesgo país",                 "EMBI Perú",               pct(rp),                  "🟡 Monitorear"],
        ["Riesgo cambiario",            "Tipo de cambio",          f"S/ {tc:.4f}",            "🟡 Cubrir si exposición >30%"],
        ["Riesgo de solvencia",         "Deuda/EBITDA",            f"{deuda_ebitda:.2f}x",   "🟢 OK" if deuda_ebitda<=3 else "🔴 Alto"],
        ["Riesgo operacional",          "Margen EBITDA",           pct(margen_ebitda),        "🟢 OK" if margen_ebitda>=0.12 else "🔴 Bajo"],
        ["Riesgo tributario",           "IR sobre utilidades",     pct(ir_tasa),              "🟡 Monitorear SUNAT"],
        ["Riesgo de quiebra",           "Altman Z-Score",          f"{altman_z:.2f}",         altman_zona],
        ["Riesgo de refinanciamiento",  "Cobertura intereses",     f"{cobertura_int:.2f}x",   "🟢 OK" if cobertura_int>=2.5 else "🔴 Crítico"],
    ], columns=["Tipo de riesgo","Indicador","Valor","Semáforo"])
    st.dataframe(riesgos, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# N4 — WARREN BUFFETT MODULE
# ══════════════════════════════════════════════════════════════════
with t4:
    st.header("N4 · Warren Buffett Module — Calidad del Negocio")
    st.caption("Inspirado en el framework de análisis de Berkshire Hathaway")

    st.subheader("4.1 Calidad del negocio y ventaja competitiva")
    wb1,wb2 = st.columns(2)
    with wb1:
        moat = st.select_slider("Economic Moat (ventaja competitiva)",
            options=["Sin moat","Moat estrecho","Moat moderado","Moat amplio","Moat muy amplio"],
            value="Moat moderado")
        precio_power = st.slider("Poder de fijación de precios (0-10)", 0, 10, 6)
        recurrencia  = st.slider("Recurrencia de ingresos (0-10)",       0, 10, 7)
    with wb2:
        capital_asig = st.select_slider("Calidad de asignación de capital",
            options=["Muy deficiente","Deficiente","Regular","Buena","Excelente"],
            value="Buena")
        reinversion  = st.slider("% NOPAT reinvertido", 0, 100, 40)

    moat_score = {"Sin moat":0,"Moat estrecho":25,"Moat moderado":50,"Moat amplio":75,"Moat muy amplio":100}[moat]

    bm1,bm2,bm3,bm4 = st.columns(4)
    bm1.metric("ROIC",           pct(roic),  "vs WACC " + pct(wacc))
    bm2.metric("ROE",            pct(roe),   "🟢 OK" if roe>=0.15 else "🔴 Bajo")
    bm3.metric("Margen neto",    pct(margen_neto))
    bm4.metric("FCF/Utilidad",   pct(safe(fcf, utilidad_neta)))

    st.subheader("4.2 Score Buffett-Style")
    buffett_scores = {
        "ROIC consistente (≥15%)":      min(100, roic/0.15*100),
        "ROE consistente (≥15%)":       min(100, roe/0.15*100),
        "Margen neto (≥10%)":           min(100, margen_neto/0.10*100),
        "FCF positivo":                  100 if fcf>0 else 0,
        "Cobertura intereses (≥3x)":    min(100, cobertura_int/3*100),
        "Bajo apalancamiento (D/E<1)":  max(0, 100 - deuda_pat*50),
        "Moat score":                    moat_score,
        "Poder de precios":              precio_power*10,
        "Recurrencia ingresos":          recurrencia*10,
    }
    scores_df = pd.DataFrame(
        [(k, round(v,1), "🟢" if v>=70 else ("🟡" if v>=40 else "🔴")) for k,v in buffett_scores.items()],
        columns=["Criterio","Score (0-100)","Semáforo"]
    )
    st.dataframe(scores_df, use_container_width=True, hide_index=True)
    score_buffett = np.mean(list(buffett_scores.values()))
    st.metric("Score Buffett Total", f"{score_buffett:.0f}/100",
              "🟢 Empresa de calidad" if score_buffett>=70 else ("🟡 Evaluar" if score_buffett>=50 else "🔴 Evitar"))

    st.subheader("4.3 Valor Intrínseco (DCF simplificado Buffett)")
    n_años_b = 10
    tasa_desc_b = st.slider("Tasa de descuento Buffett (%)", 8.0, 20.0, 10.0, 0.5) / 100
    crec_b1     = st.slider("Crecimiento FCF años 1-5 (%)",  0.0, 30.0, 10.0, 1.0) / 100
    crec_b2     = st.slider("Crecimiento FCF años 6-10 (%)", 0.0, 20.0,  5.0, 1.0) / 100

    vp_buff = sum([
        fcf * (1+crec_b1)**yr / (1+tasa_desc_b)**yr for yr in range(1,6)
    ]) + sum([
        fcf * (1+crec_b1)**5 * (1+crec_b2)**(yr-5) / (1+tasa_desc_b)**yr for yr in range(6,11)
    ])
    vt_buff = fcf * (1+crec_b1)**5 * (1+crec_b2)**5 * (1+g_terminal) / max(tasa_desc_b-g_terminal,0.01)
    valor_intrinseco = vp_buff + vt_buff / (1+tasa_desc_b)**n_años_b
    margen_seguridad  = max(0, 1 - ic/max(valor_intrinseco, 0.01))

    bi1,bi2,bi3 = st.columns(3)
    bi1.metric("Valor intrínseco FCF", m(valor_intrinseco))
    bi2.metric("Capital invertido IC", m(ic))
    bi3.metric("Margen de seguridad",  pct(margen_seguridad),
               "🟢 Subvalorado" if margen_seguridad>0.25 else "🔴 Sin margen")


# ══════════════════════════════════════════════════════════════════
# N5 — VALORACIÓN DE EMPRESAS
# ══════════════════════════════════════════════════════════════════
with t5:
    st.header("N5 · Valoración de Empresas — Métodos Integrados")

    v1,v2 = st.columns(2)
    with v1:
        n_proy = st.slider("Años proyección", 3, 10, 5)
        crec_v = st.number_input("Crecimiento FCF proyectado (%)", value=8.0, step=1.0) / 100
    with v2:
        prima_ctrl = st.slider("Prima de control (%)", 0, 40, 15) / 100
        desc_liq   = st.slider("Descuento liquidez (%)", 0, 40, 20) / 100

    # DCF
    fcf_proy = [fcf*(1+crec_v)**yr for yr in range(1,n_proy+1)]
    vp_proy  = sum([f/(1+wacc)**yr for yr,f in enumerate(fcf_proy,1)])
    vt_dcf   = fcf_proy[-1]*(1+g_terminal)/max(wacc-g_terminal,0.001)
    vp_vt    = vt_dcf/(1+wacc)**n_proy
    ev_dcf2  = vp_proy + vp_vt
    eq_dcf   = ev_dcf2 - deuda_tot
    eq_ctrl  = eq_dcf * (1+prima_ctrl)
    eq_trans = eq_ctrl * (1-desc_liq)

    # Múltiplos
    mult_ev_ebitda = st.number_input("Múltiplo EV/EBITDA comparable", value=7.0, step=0.5)
    mult_pe        = st.number_input("Múltiplo P/E comparable",        value=15.0, step=0.5)
    mult_pbv       = st.number_input("Múltiplo P/BV comparable",       value=2.0, step=0.25)

    ev_mult_ebitda  = ebitda * mult_ev_ebitda
    val_mult_pe     = utilidad_neta * mult_pe
    val_mult_pbv    = patrimonio * mult_pbv

    val_df = pd.DataFrame([
        ["DCF — Flujos descontados",   m(vp_proy),  "VP de flujos explícitos"],
        ["DCF — Valor terminal",        m(vp_vt),   f"FCF terminal / (WACC-g={pct(g_terminal)})"],
        ["DCF — Enterprise Value",      m(ev_dcf2), "Total EV = VP flujos + VP terminal"],
        ["DCF — Equity Value",          m(eq_dcf),  "EV − Deuda financiera"],
        ["DCF — Con prima de control",  m(eq_ctrl), f"+{pct(prima_ctrl)} prima control"],
        ["DCF — Valor transferencia",   m(eq_trans),f"−{pct(desc_liq)} descuento liquidez"],
        ["Múltiplos — EV/EBITDA",       m(ev_mult_ebitda), f"{mult_ev_ebitda}x × EBITDA"],
        ["Múltiplos — P/E",             m(val_mult_pe),    f"{mult_pe}x × Utilidad neta"],
        ["Múltiplos — P/BV",            m(val_mult_pbv),   f"{mult_pbv}x × Patrimonio"],
        ["EVA — Valor EVA capitalizado",m(ic+mva),         "IC + MVA (EVA/WACC-g)"],
    ], columns=["Método","Valor","Nota"])
    st.dataframe(val_df, use_container_width=True, hide_index=True)

    # Rango de valoración
    vals_list = [eq_trans, val_mult_pe, val_mult_pbv, ic+mva]
    fig_val = go.Figure()
    fig_val.add_trace(go.Box(y=vals_list, name="Rango de valor equity",
                              marker_color="#1F3864", boxpoints="all"))
    fig_val.update_layout(title="Rango de Valoración — Métodos integrados", height=380)
    st.plotly_chart(fig_val, use_container_width=True)

    vm1,vm2,vm3 = st.columns(3)
    vm1.metric("Valor mínimo",  m(min(vals_list)))
    vm2.metric("Valor mediano", m(float(np.median(vals_list))))
    vm3.metric("Valor máximo",  m(max(vals_list)))


# ══════════════════════════════════════════════════════════════════
# N6 — MONTE CARLO
# ══════════════════════════════════════════════════════════════════
with t6:
    st.header("N6 · Simulación Monte Carlo — Miles de Escenarios")

    mc1,mc2 = st.columns(2)
    with mc1:
        n_sim     = st.select_slider("Número de simulaciones", [1000,5000,10000,50000], 10000)
        vol_vent  = st.slider("Volatilidad ventas (%)",    1,  30, 12) / 100
        vol_cm    = st.slider("Volatilidad costo ventas (%)", 1, 20, 8) / 100
    with mc2:
        vol_fx    = st.slider("Volatilidad tipo de cambio (%)", 0, 20, 6) / 100
        vol_int   = st.slider("Volatilidad intereses (%)",       0, 30, 10) / 100
        conf      = st.selectbox("Nivel de confianza VaR", [0.90, 0.95, 0.99], index=1)

    np.random.seed(971)
    sim_vent   = ventas      * (1 + np.random.normal(0, vol_vent, n_sim))
    sim_cm     = costo_v     * (1 + np.random.normal(0, vol_cm,   n_sim))
    sim_int    = intereses   * (1 + np.random.normal(0, vol_int,  n_sim))
    sim_ebitda = sim_vent - sim_cm - gastos_op
    sim_uai    = sim_ebitda - dep - sim_int
    sim_un     = sim_uai * (1 - ir_tasa)
    sim_eva    = sim_un - ic * wacc

    var_level = 1 - conf
    var_ebitda = float(np.percentile(sim_ebitda, var_level*100))
    var_eva    = float(np.percentile(sim_eva,    var_level*100))
    cvar_eva   = float(np.mean(sim_eva[sim_eva <= var_eva]))
    prob_eva_neg = float(np.mean(sim_eva < 0))
    prob_ubi_neg = float(np.mean(sim_un  < 0))

    sm1,sm2,sm3,sm4 = st.columns(4)
    sm1.metric(f"VaR EBITDA {conf:.0%}", m(var_ebitda))
    sm2.metric(f"VaR EVA {conf:.0%}",    m(var_eva))
    sm3.metric(f"CVaR EVA {conf:.0%}",   m(cvar_eva))
    sm4.metric("P(EVA < 0)",             pct(prob_eva_neg))

    fig_mc = go.Figure()
    fig_mc.add_trace(go.Histogram(x=sim_eva/1e6, nbinsx=80, name="EVA sim.",
                                   marker_color="#2980b9", opacity=0.75))
    fig_mc.add_vline(x=var_eva/1e6, line_color="red",    line_dash="dash",
                     annotation_text=f"VaR {conf:.0%}")
    fig_mc.add_vline(x=0,           line_color="black",  line_dash="dot",
                     annotation_text="EVA=0")
    fig_mc.update_layout(title=f"Distribución Monte Carlo — EVA (S/ MM) | {n_sim:,} simulaciones",
                          xaxis_title="EVA S/ MM", height=400)
    st.plotly_chart(fig_mc, use_container_width=True)

    pcts_df = pd.DataFrame([
        [f"P{p}", m(float(np.percentile(sim_eva,p))), m(float(np.percentile(sim_ebitda,p))),
         m(float(np.percentile(sim_un,p)))]
        for p in [1,5,10,25,50,75,90,95,99]
    ], columns=["Percentil","EVA S/","EBITDA S/","Utilidad neta S/"])
    st.dataframe(pcts_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# N7 — MARKOWITZ — PORTAFOLIO CORPORATIVO
# ══════════════════════════════════════════════════════════════════
with t7:
    st.header("N7 · Markowitz — Optimización de Portafolio Corporativo")
    st.info("Aplica la teoría de Markowitz a clientes, líneas de producto, unidades de negocio o proyectos de inversión.")

    st.subheader("Definir portafolio de unidades / segmentos")
    n_assets = st.slider("Número de segmentos/unidades", 2, 6, 4)
    nombres = []
    retornos = []
    vols = []
    cols_a = st.columns(n_assets)
    defaults_n = ["Manufactura","Retail","Exportación","Servicios","Proyectos","Inmobiliario"]
    defaults_r = [0.12, 0.18, 0.22, 0.15, 0.25, 0.14]
    defaults_v = [0.10, 0.20, 0.28, 0.12, 0.35, 0.18]
    for i, col in enumerate(cols_a):
        with col:
            n_ = col.text_input(f"Unidad {i+1}", defaults_n[i], key=f"mn_{i}")
            r_ = col.number_input(f"Retorno % (anual)", value=defaults_r[i]*100, step=1.0, key=f"mr_{i}") / 100
            v_ = col.number_input(f"Volatilidad %",     value=defaults_v[i]*100, step=1.0, key=f"mv_{i}") / 100
            nombres.append(n_); retornos.append(r_); vols.append(v_)

    # Matriz correlaciones simple
    np.random.seed(42)
    corr_matrix = np.eye(n_assets)
    for i in range(n_assets):
        for j in range(i+1, n_assets):
            c = np.random.uniform(0.1, 0.5)
            corr_matrix[i,j] = corr_matrix[j,i] = c

    cov_matrix = np.outer(vols, vols) * corr_matrix

    # Frontera eficiente — simulación
    n_port = 3000
    np.random.seed(99)
    port_ret, port_vol, port_sr, port_w = [], [], [], []
    for _ in range(n_port):
        w = np.random.dirichlet(np.ones(n_assets))
        r = np.dot(w, retornos)
        v = np.sqrt(w @ cov_matrix @ w)
        sr = (r - rf) / max(v, 0.001)
        port_ret.append(r); port_vol.append(v); port_sr.append(sr); port_w.append(w)

    best_idx = np.argmax(port_sr)
    best_w   = port_w[best_idx]

    fig_mark = go.Figure()
    fig_mark.add_scatter(x=port_vol, y=port_ret, mode="markers",
                          marker=dict(color=port_sr, colorscale="Viridis", size=3, opacity=0.5),
                          name="Portafolios simulados")
    fig_mark.add_scatter(x=[port_vol[best_idx]], y=[port_ret[best_idx]],
                          mode="markers", marker=dict(size=14, color="red", symbol="star"),
                          name="Sharpe máximo")
    fig_mark.update_layout(title="Frontera Eficiente — Portafolio Corporativo",
                            xaxis_title="Riesgo (Volatilidad)", yaxis_title="Retorno esperado",
                            height=430)
    st.plotly_chart(fig_mark, use_container_width=True)

    st.subheader("Pesos óptimos (Sharpe máximo)")
    opt_df = pd.DataFrame({
        "Unidad": nombres, "Peso óptimo": [f"{w:.1%}" for w in best_w],
        "Retorno": [pct(r) for r in retornos], "Volatilidad": [pct(v) for v in vols],
    })
    st.dataframe(opt_df, use_container_width=True, hide_index=True)
    st.metric("Retorno portafolio óptimo", pct(port_ret[best_idx]))
    st.metric("Riesgo portafolio óptimo",  pct(port_vol[best_idx]))
    st.metric("Sharpe ratio",              f"{port_sr[best_idx]:.2f}")


# ══════════════════════════════════════════════════════════════════
# N8 — MACHINE LEARNING
# ══════════════════════════════════════════════════════════════════
with t8:
    st.header("N8 · Machine Learning — Predicción Financiera")
    st.info("Modelos predictivos sobre ventas, caja, insolvencia, fraude y abandono de clientes.")

    st.subheader("8.1 Predicción de ventas — Regresión tendencia")
    np.random.seed(7)
    meses_hist = list(range(1, 25))
    ventas_hist = [ventas/12 * (1 + 0.007*i + np.random.normal(0, 0.04)) for i in meses_hist]
    coef = np.polyfit(meses_hist, ventas_hist, 1)
    meses_pred = list(range(1, 31))
    pred_ventas = [coef[0]*x + coef[1] for x in meses_pred]

    fig_ml = go.Figure()
    fig_ml.add_scatter(x=meses_hist, y=ventas_hist, mode="markers+lines", name="Histórico",
                        line=dict(color="#2980b9"))
    fig_ml.add_scatter(x=meses_pred[24:], y=pred_ventas[24:], mode="lines", name="Predicción 6M",
                        line=dict(color="#e74c3c", dash="dash"))
    fig_ml.add_scatter(x=meses_pred, y=pred_ventas, mode="lines", name="Tendencia",
                        line=dict(color="#95a5a6", dash="dot"))
    fig_ml.update_layout(title="Predicción de Ventas — Modelo de Tendencia Lineal", height=380)
    st.plotly_chart(fig_ml, use_container_width=True)

    st.subheader("8.2 Score de insolvencia — Altman Z-Score")
    altman_df = pd.DataFrame([
        ["X1 = Capital trabajo / Activo total", f"{x1:.4f}", "0.30-0.40 = saludable"],
        ["X2 = Utilidades ret. / Activo total", f"{x2:.4f}", "> 0.10 positivo"],
        ["X3 = EBIT / Activo total",            f"{x3:.4f}", "> 0.10 bueno"],
        ["X4 = Patrimonio / Deuda total",       f"{x4:.4f}", "> 1.0 conservador"],
        ["X5 = Ventas / Activo total",          f"{x5:.4f}", "> 1.0 eficiente"],
        ["Z-Score = 1.2X1+1.4X2+3.3X3+0.6X4+X5", f"{altman_z:.2f}", altman_zona],
    ], columns=["Variable","Valor","Benchmark"])
    st.dataframe(altman_df, use_container_width=True, hide_index=True)

    st.subheader("8.3 Mapa de riesgos predictivos")
    pred_risks = pd.DataFrame([
        ["Insolvencia 12M",           f"{max(0,1-altman_z/3):.0%}",       altman_zona],
        ["Incumplimiento deuda",      f"{max(0,1-cobertura_int/3):.0%}",   "🔴" if cobertura_int<2 else "🟢"],
        ["Caída de márgenes",         f"{max(0,0.30-margen_ebitda):.0%}",  "🟡 Monitorear"],
        ["Déficit de caja 6M",        f"{max(0,1-liquidez_corr/1.5):.0%}","🟡 Preventivo"],
        ["Riesgo de refinanciamiento",f"{min(deuda_ebitda/5,1):.0%}",      "🟡 Evaluar"],
    ], columns=["Riesgo predictivo","Probabilidad estimada","Nivel"])
    st.dataframe(pred_risks, use_container_width=True, hide_index=True)
    st.caption("Nota: Modelos referenciales. En producción conectar con scikit-learn, XGBoost o LightGBM sobre datos históricos reales.")


# ══════════════════════════════════════════════════════════════════
# N9 — INSTRUMENTOS FINANCIEROS
# ══════════════════════════════════════════════════════════════════
with t9:
    st.header("N9 · Instrumentos Financieros")

    inst_tabs = st.tabs(["Forward","Swap","Opciones","Leasing","Factoring/Confirming","Bonos","Cartas Fianza"])

    with inst_tabs[0]:
        st.subheader("Forward de Tipo de Cambio")
        fw_spot  = st.number_input("TC Spot",    value=tc, step=0.01, format="%.4f", key="i9fw_s")
        fw_dias  = st.number_input("Plazo días", value=90, step=30, key="i9fw_d")
        fw_rpen  = st.number_input("Tasa PEN %", value=6.0, step=0.5, key="i9fw_rp") / 100
        fw_rusd  = st.number_input("Tasa USD %", value=4.5, step=0.5, key="i9fw_ru") / 100
        fw_monto = st.number_input("Monto USD",  value=100_000.0, step=10_000.0, key="i9fw_m")
        tc_fwd   = fw_spot * (1 + fw_rpen*fw_dias/365) / (1 + fw_rusd*fw_dias/365)
        prima    = tc_fwd - fw_spot
        st.metric("TC Forward", f"{tc_fwd:.4f}")
        st.metric("Prima (diferencial)", f"{prima:.4f}")
        st.metric("Costo cobertura PEN", m(fw_monto * prima))
        st.info(f"Forward {fw_dias}d: TC fijo a {tc_fwd:.4f}. Prima = {prima:.4f} PEN/USD = {prima/fw_spot:.2%} del spot.")

    with inst_tabs[1]:
        st.subheader("Swap de Tasas de Interés (IRS)")
        swap_n    = st.number_input("Nocional (S/)", value=2_000_000.0, step=100_000.0)
        swap_fija = st.number_input("Tasa fija swap (%)", value=7.5, step=0.5) / 100
        swap_var  = st.number_input("Tasa variable actual (%)", value=kd*100, step=0.5) / 100
        swap_años = st.slider("Plazo (años)", 1, 10, 3)
        flujo_fijo = swap_n * swap_fija
        flujo_var  = swap_n * swap_var
        neto_swap  = flujo_var - flujo_fijo
        st.metric("Flujo fijo anual",   m(flujo_fijo))
        st.metric("Flujo variable actual", m(flujo_var))
        st.metric("Neto anual para quien paga fija", m(neto_swap))
        st.info("Swap IRS: empresa paga tasa fija y recibe tasa variable. Útil para convertir deuda variable a costo fijo predecible.")

    with inst_tabs[2]:
        st.subheader("Opciones FX (Black-Scholes)")
        op_s  = st.number_input("Spot S",   value=tc, step=0.01, format="%.4f", key="i9op_s")
        op_k  = st.number_input("Strike K", value=tc*1.02, step=0.01, format="%.4f", key="i9op_k")
        op_t  = st.number_input("Plazo T (años)", value=0.25, step=0.05, key="i9op_t")
        op_v  = st.number_input("Volatilidad σ (%)", value=8.0, step=0.5, key="i9op_v") / 100
        op_r  = st.number_input("Tasa libre riesgo (%)", value=rf*100, step=0.5, key="i9op_r") / 100
        if op_v>0 and op_t>0 and op_s>0 and op_k>0:
            d1 = (math.log(op_s/op_k)+(op_r+0.5*op_v**2)*op_t)/(op_v*math.sqrt(op_t))
            d2 = d1 - op_v*math.sqrt(op_t)
            def N(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
            call_p = op_s*N(d1) - op_k*math.exp(-op_r*op_t)*N(d2)
            put_p  = call_p - op_s + op_k*math.exp(-op_r*op_t)
            col_op1,col_op2 = st.columns(2)
            col_op1.metric("Prima Call", f"{call_p:.4f}")
            col_op1.metric("Delta Call", f"{N(d1):.4f}")
            col_op2.metric("Prima Put",  f"{put_p:.4f}")
            col_op2.metric("Delta Put",  f"{N(d1)-1:.4f}")

    with inst_tabs[3]:
        st.subheader("Leasing Financiero")
        ls_activo = st.number_input("Valor del activo (S/)", value=500_000.0, step=50_000.0)
        ls_cuota  = st.slider("Cuota inicial (%)", 0, 30, 10) / 100
        ls_tasa   = st.number_input("TEA (%)", value=9.5, step=0.5) / 100
        ls_años   = st.slider("Plazo (años)", 2, 7, 4)
        ls_financ = ls_activo * (1 - ls_cuota)
        ls_tm     = (1+ls_tasa)**(1/12)-1
        n_cuotas  = ls_años*12
        ls_cuota_m = ls_financ * ls_tm / (1-(1+ls_tm)**(-n_cuotas))
        ls_total  = ls_cuota_m*n_cuotas + ls_activo*ls_cuota
        ls_interes= ls_total - ls_activo
        l1,l2,l3 = st.columns(3)
        l1.metric("Monto financiado",  m(ls_financ))
        l2.metric("Cuota mensual",     m(ls_cuota_m))
        l3.metric("Interés total",     m(ls_interes))
        st.info(f"Leasing {ls_años} años. Cuota mensual {m(ls_cuota_m)}. Beneficio fiscal: depreciación acelerada + IGV del contrato.")

    with inst_tabs[4]:
        st.subheader("Factoring y Confirming")
        f1,f2 = st.columns(2)
        with f1:
            st.markdown("**Factoring**")
            fact_v = st.number_input("Valor factura (S/)", value=200_000.0, step=10_000.0, key="i9f_v")
            fact_d = st.number_input("Plazo (días)",       value=90, step=30, key="i9f_d")
            fact_t = st.number_input("Tasa anual (%)",     value=9.0, step=0.5, key="i9f_t") / 100
            fact_c = st.number_input("Comisión (%)",       value=1.5, step=0.1, key="i9f_c") / 100
            desc   = fact_v * fact_t * fact_d/365
            com    = fact_v * fact_c
            liq    = fact_v - desc - com
            st.metric("Líquido recibido", m(liq))
            st.metric("Costo total",      m(desc+com))
            st.metric("TEA efectiva",     pct((desc+com)/liq*365/fact_d))
        with f2:
            st.markdown("**Confirming**")
            conf_v = st.number_input("Monto pago proveedor (S/)", value=150_000.0, step=10_000.0, key="i9c_v")
            conf_a = st.number_input("Anticipo (días)",           value=30, step=10, key="i9c_a")
            conf_t = st.number_input("Tasa confirming (%)",       value=7.5, step=0.5, key="i9c_t") / 100
            costo_c= conf_v * conf_t * conf_a/365
            ahorro = conf_v * 0.02
            st.metric("Costo confirming",  m(costo_c))
            st.metric("Ahorro pronto pago",m(ahorro))
            st.metric("Neto",              m(ahorro-costo_c))

    with inst_tabs[5]:
        st.subheader("Valoración de Bono")
        b_vn   = st.number_input("Valor nominal", value=1_000_000.0, step=100_000.0)
        b_cup  = st.number_input("Cupón (%)", value=7.0, step=0.5) / 100
        b_ytm  = st.number_input("YTM / Tasa de descuento (%)", value=8.5, step=0.5) / 100
        b_años = st.slider("Plazo (años)", 1, 20, 5)
        flujos = [b_vn*b_cup/(1+b_ytm)**t for t in range(1,b_años+1)]
        flujos[-1] += b_vn/(1+b_ytm)**b_años
        precio_bono = sum(flujos)
        dur = sum([(i+1)*f/(1+b_ytm)**(i+1) for i,f in enumerate(flujos)]) / max(precio_bono, 0.01)
        conv = sum([(i+1)*(i+2)*b_vn*b_cup/(1+b_ytm)**(i+3) for i in range(b_años)]) / max(precio_bono, 0.01)
        b1,b2,b3 = st.columns(3)
        b1.metric("Precio del bono",  m(precio_bono))
        b2.metric("Duración Macaulay",f"{dur:.2f} años")
        b3.metric("Convexidad",       f"{conv:.4f}")

    with inst_tabs[6]:
        st.subheader("Carta Fianza / Garantía Bancaria")
        cf_v = st.number_input("Monto garantizado (S/)", value=500_000.0, step=50_000.0)
        cf_t = st.number_input("Comisión anual (%)",     value=1.5, step=0.1) / 100
        cf_a = st.slider("Plazo (meses)", 1, 36, 12)
        cf_c = cf_v * cf_t * cf_a/12
        cf1,cf2 = st.columns(2)
        cf1.metric("Comisión total",  m(cf_c))
        cf2.metric("Costo mensual",   m(cf_c/cf_a))
        st.info("La carta fianza garantiza una obligación ante un tercero (entidad pública, cliente, proveedor) sin uso inmediato de caja.")


# ══════════════════════════════════════════════════════════════════
# N10 — INTELIGENCIA TRIBUTARIA
# ══════════════════════════════════════════════════════════════════
with t10:
    st.header("N10 · Inteligencia Tributaria — SUNAT, NIIF y BEPS")

    ir_anual      = max(0, uai) * ir_tasa
    igv_ventas    = ventas * 0.18
    igv_compras   = costo_v * 0.18
    igv_neto      = igv_ventas - igv_compras
    det_pagar     = ventas * 0.001  # percepción estimada 0.1%

    t10c1,t10c2,t10c3,t10c4 = st.columns(4)
    t10c1.metric("IR anual estimado",  m(ir_anual))
    t10c2.metric("IGV ventas",         m(igv_ventas))
    t10c3.metric("IGV compras (CF)",   m(igv_compras))
    t10c4.metric("IGV neto a pagar",   m(igv_neto))

    st.subheader("Score Tributario")
    score_trib = min(100, (
        (1 if igv_neto > 0 else 0) * 20 +
        (min(cobertura_int/3, 1)) * 20 +
        (1 - min(deuda_ebitda/5, 1)) * 20 +
        (min(margen_neto/0.10, 1)) * 20 +
        (min(liquidez_corr/2, 1)) * 20
    ))
    st.metric("Score Tributario", f"{score_trib:.0f}/100",
              "🟢 Bajo riesgo" if score_trib>=70 else ("🟡 Medio" if score_trib>=40 else "🔴 Alto"))

    st.subheader("Checklist NIIF relevantes")
    niif_df = pd.DataFrame([
        ["NIIF 15","Reconocimiento de ingresos","Validar momento de reconocimiento según contrato"],
        ["NIIF 16","Arrendamientos","¿Tienes arrendamientos que activar como activo derecho de uso?"],
        ["NIIF 9", "Instrumentos financieros","Clasificar y medir instrumentos financieros correctamente"],
        ["NIC 12", "Impuesto diferido","¿Existen diferencias temporarias activas/pasivas?"],
        ["NIC 36", "Deterioro de activos","Prueba de deterioro anual de activos de larga vida"],
        ["NIIF 3", "Combinaciones de negocios","Aplicable si hubo adquisiciones empresariales"],
    ], columns=["NIIF","Tema","Consideración clave"])
    st.dataframe(niif_df, use_container_width=True, hide_index=True)

    st.subheader("BEPS — Erosión de base y precios de transferencia")
    st.info(
        "Si tu empresa tiene operaciones vinculadas (grupo empresarial), aplican las reglas "
        "BEPS de la OCDE y las normas de Precios de Transferencia SUNAT. "
        "Obligación de Estudio Técnico si operaciones vinculadas superan S/400,000 anuales."
    )
    ops_vinc = st.number_input("Operaciones vinculadas anuales (S/)", value=0.0, step=50_000.0)
    if ops_vinc >= 400_000:
        st.warning("⚠️ Obligación de presentar Estudio Técnico de Precios de Transferencia ante SUNAT.")
    elif ops_vinc > 0:
        st.info("Operaciones vinculadas sin umbral de obligación, pero documentar preventivamente.")


# ══════════════════════════════════════════════════════════════════
# N11 — CONTROLLER FINANCIERO
# ══════════════════════════════════════════════════════════════════
with t11:
    st.header("N11 · Controller Financiero — Presupuesto y Control de Gestión")

    st.subheader("Presupuesto Maestro vs Real")
    pres_ventas = st.number_input("Ventas presupuestadas", value=ventas*1.05, step=100_000.0, key="pv")
    pres_cm     = st.number_input("Costo ventas presup.", value=costo_v*1.04, step=100_000.0, key="pcm")
    pres_gop    = st.number_input("Gastos operat. presup.",value=gastos_op*1.02,step=50_000.0, key="pgo")
    pres_capex  = st.number_input("CAPEX presupuestado",   value=capex*1.10, step=50_000.0, key="pca")

    pres_ebitda = pres_ventas - pres_cm - pres_gop
    desv_ven    = ventas    - pres_ventas
    desv_ebitda = ebitda    - pres_ebitda
    desv_pct_v  = safe(desv_ven, pres_ventas)
    desv_pct_e  = safe(desv_ebitda, pres_ebitda)

    ctrl_df = pd.DataFrame([
        ["Ventas",        m(pres_ventas), m(ventas),    m(desv_ven),    pct(desv_pct_v),  "🟢" if desv_ven>=0 else "🔴"],
        ["Costo ventas",  m(pres_cm),     m(costo_v),   m(costo_v-pres_cm), pct(safe(costo_v-pres_cm,pres_cm)),"🟢" if costo_v<=pres_cm else "🔴"],
        ["Gastos operat.",m(pres_gop),    m(gastos_op), m(gastos_op-pres_gop), pct(safe(gastos_op-pres_gop,pres_gop)),"🟢" if gastos_op<=pres_gop else "🔴"],
        ["EBITDA",        m(pres_ebitda), m(ebitda),    m(desv_ebitda), pct(desv_pct_e),  "🟢" if desv_ebitda>=0 else "🔴"],
        ["CAPEX",         m(pres_capex),  m(capex),     m(capex-pres_capex), pct(safe(capex-pres_capex,pres_capex)),"🟢" if capex<=pres_capex else "🔴"],
    ], columns=["Concepto","Presupuesto","Real","Desviación S/","Desviación %","Semáforo"])
    st.dataframe(ctrl_df, use_container_width=True, hide_index=True)

    st.subheader("KPIs de Control de Gestión")
    kpig_df = pd.DataFrame([
        ["Eficiencia costo ventas",  pct(safe(costo_v,ventas)),    "< 65% bueno en manufactura"],
        ["Eficiencia gastos operat.",pct(safe(gastos_op,ventas)),  "< 20% objetivo"],
        ["Palanca operativa",        f"{safe(ebitda,ebit):.2f}x",  "> 1 = apalancamiento positivo"],
        ["Rentabilidad ventas",      pct(margen_neto),             "> 8% objetivo mínimo"],
        ["Rotación activos",         f"{safe(ventas,activo_tot):.2f}x","Sector manufactura: 0.8-1.5x"],
        ["Días cuentas por cobrar",  f"{dias_cobro:.0f} días",     "< 45 días objetivo"],
        ["Días cuentas por pagar",   f"{dias_pago:.0f} días",      "> 30 días negociar"],
        ["Días inventario",          f"{dias_inv:.0f} días",       "< 45 días en manufactura"],
    ], columns=["KPI","Valor","Benchmark"])
    st.dataframe(kpig_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# N12 — INTELIGENCIA ESTRATÉGICA
# ══════════════════════════════════════════════════════════════════
with t12:
    st.header("N12 · Inteligencia Estratégica — PESTEL, Porter y BSC")

    s12_1, s12_2 = st.tabs(["PESTEL + Porter","Balanced Scorecard"])

    with s12_1:
        st.subheader("Análisis PESTEL")
        pestel_items = ["Político","Económico","Social","Tecnológico","Ecológico","Legal"]
        pestel_scores = {}
        cols_p = st.columns(3)
        for i, item in enumerate(pestel_items):
            pestel_scores[item] = cols_p[i%3].slider(f"{item} (0=riesgo, 10=oportunidad)", 0, 10, 5, key=f"pes_{i}")

        pestel_df = pd.DataFrame([
            (k, v, "🟢 Oportunidad" if v>=7 else ("🟡 Neutral" if v>=4 else "🔴 Amenaza"))
            for k,v in pestel_scores.items()
        ], columns=["Factor","Puntuación","Evaluación"])
        st.dataframe(pestel_df, use_container_width=True, hide_index=True)

        st.subheader("Fuerzas de Porter")
        porter_items = ["Poder clientes","Poder proveedores","Amenaza sustitutos","Amenaza entrantes","Rivalidad sector"]
        porter_scores = {item: st.slider(f"{item} (0=bajo, 10=alto)", 0, 10, 5, key=f"por_{i}") for i,item in enumerate(porter_items)}
        intensidad = np.mean(list(porter_scores.values()))
        st.metric("Intensidad competitiva", f"{intensidad:.1f}/10",
                  "🔴 Alta" if intensidad>7 else ("🟡 Media" if intensidad>4 else "🟢 Baja"))

    with s12_2:
        st.subheader("Balanced Scorecard — 4 Perspectivas")
        bsc_data = {
            "Financiera": [("ROE",pct(roe),"≥15%","🟢" if roe>=0.15 else "🔴"),
                           ("EVA",m(eva),"Positivo","🟢" if eva>0 else "🔴"),
                           ("Margen EBITDA",pct(margen_ebitda),"≥15%","🟢" if margen_ebitda>=0.15 else "🔴")],
            "Clientes":   [("NPS estimado","70/100","≥60","🟢"),
                           ("Retención clientes","85%","≥80%","🟢"),
                           ("Días cobro",f"{dias_cobro}d","<45d","🟢" if dias_cobro<45 else "🔴")],
            "Procesos":   [("Eficiencia producción",pct(1-safe(costo_v,ventas)),"≥35%","🟢" if costo_v/ventas<=0.65 else "🔴"),
                           ("CCE",f"{ciclo_cce:.0f}d","<40d","🟢" if ciclo_cce<40 else "🔴"),
                           ("Rotación inventario",f"{safe(costo_v,inventario):.1f}x","≥6x","🟢" if safe(costo_v,inventario)>=6 else "🔴")],
            "Aprendizaje":[("Inversión I+D",pct(safe(capex,ventas)),"≥2%","🟢" if capex/ventas>=0.02 else "🟡"),
                           ("Retención talento","82%","≥80%","🟢"),
                           ("Score digital","65/100","≥60","🟢")],
        }
        for perspectiva, kpis in bsc_data.items():
            st.markdown(f"**{perspectiva}**")
            df_ = pd.DataFrame(kpis, columns=["KPI","Valor","Meta","Semáforo"])
            st.dataframe(df_, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════
# N13 — IA FINANCIERA
# ══════════════════════════════════════════════════════════════════
with t13:
    st.header("N13 · IA Financiera — Respuestas Inteligentes Automáticas")
    st.info("El sistema analiza todos los indicadores y responde preguntas estratégicas automáticamente.")

    preguntas = [
        "¿Qué decisión aumenta el valor de la empresa?",
        "¿Dónde estoy destruyendo valor?",
        "¿Cuál es el cuello de botella financiero?",
        "¿Qué pasará en 24 meses si continúa la tendencia actual?",
        "¿Debo endeudarme más o capitalizar?",
        "¿Cuál es mi riesgo de insolvencia?",
        "¿Cómo mejoro mi liquidez sin deuda adicional?",
    ]
    pregunta = st.selectbox("Selecciona una pregunta estratégica", preguntas)

    def ia_responder(pregunta):
        if "aumenta el valor" in pregunta:
            if spread_roic < 0:
                return (f"🧠 **IA Responde:** El ROIC ({pct(roic)}) está {pct(abs(spread_roic))} por debajo del WACC ({pct(wacc)}). "
                        f"Para crear valor debes: (1) Mejorar margen operativo actual {pct(margen_ebitda)} hasta al menos {pct(wacc+0.05)}, "
                        f"(2) Reducir capital invertido {m(ic)} optimizando capital de trabajo ({m(cap_trabajo)}), "
                        f"(3) Reducir WACC negociando menor costo de deuda (actual {pct(kd)}).")
            else:
                return (f"🧠 **IA Responde:** Ya creas valor: ROIC {pct(roic)} > WACC {pct(wacc)} = EVA {m(eva)}. "
                        f"Para aumentarlo: (1) Reinvertir FCF {m(fcf)} en proyectos con ROIC > {pct(wacc)}, "
                        f"(2) Expandir ventas manteniendo margen EBITDA {pct(margen_ebitda)}, "
                        f"(3) Reducir ciclo de caja {ciclo_cce:.0f} días → liberar capital de trabajo.")
        elif "destruyendo valor" in pregunta:
            destruccion = []
            if roic < wacc:    destruccion.append(f"• ROIC {pct(roic)} < WACC {pct(wacc)}: cada sol de capital invertido destruye {pct(wacc-roic)}")
            if margen_ebitda < 0.10: destruccion.append(f"• Margen EBITDA {pct(margen_ebitda)} insuficiente para cubrir costo de capital")
            if ciclo_cce > 60: destruccion.append(f"• CCE de {ciclo_cce:.0f} días inmoviliza capital innecesariamente")
            if deuda_ebitda > 3: destruccion.append(f"• Apalancamiento {deuda_ebitda:.1f}x eleva el riesgo y el WACC")
            return "🧠 **IA Responde — Áreas de destrucción de valor:**\n" + ("\n".join(destruccion) if destruccion else "No se detectan áreas críticas con datos actuales.")
        elif "cuello de botella" in pregunta:
            cuellos = []
            if dias_cobro > 50: cuellos.append(f"• Cobranza lenta: {dias_cobro} días. Cada 10 días de reducción libera {m(ventas/365*10)}")
            if inventario/max(costo_v,1)*365 > 60: cuellos.append(f"• Inventario alto: {inventario/max(costo_v,1)*365:.0f} días. Revisar política de stock mínimo.")
            if margen_bruto < 0.35: cuellos.append(f"• Margen bruto {pct(margen_bruto)} bajo. Revisar estructura de costos y pricing.")
            if gastos_op/ventas > 0.20: cuellos.append(f"• Gastos operativos {pct(gastos_op/ventas)} elevados sobre ventas.")
            return "🧠 **IA Responde — Cuellos de botella financieros:**\n" + ("\n".join(cuellos) if cuellos else "Sin cuellos de botella críticos detectados.")
        elif "24 meses" in pregunta:
            crec_proy = 0.08
            v24 = ventas  * (1+crec_proy)**2
            e24 = ebitda  * (1+crec_proy*0.9)**2
            u24 = utilidad_neta * (1+crec_proy)**2
            ev24 = e24/max(wacc,0.001)*7
            return (f"🧠 **IA Proyección 24 meses** (asumiendo crecimiento {pct(crec_proy)} anual):\n"
                    f"• Ventas: {m(v24)} | EBITDA: {m(e24)} | Utilidad neta: {m(u24)}\n"
                    f"• Valor empresa estimado: {m(ev24)}\n"
                    f"• Riesgo principal: si el margen EBITDA cae bajo {pct(wacc+0.02)}, el EVA volverá negativo.\n"
                    f"• Recomendación: mantener margen EBITDA ≥ {pct(margen_ebitda*0.95)} y reducir CCE {ciclo_cce:.0f}→{max(25,ciclo_cce-15):.0f} días.")
        elif "endeudar" in pregunta:
            if deuda_ebitda < 2.5 and cobertura_int > 3:
                return (f"🧠 **IA Responde:** Tienes espacio para deuda. D/EBITDA actual {deuda_ebitda:.1f}x (límite bancario ~3.5x). "
                        f"Podrías incorporar hasta {m((3.0-deuda_ebitda)*ebitda)} adicionales a costo {pct(kd)} "
                        f"si la inversión genera ROIC > {pct(wacc)}.")
            else:
                return (f"🧠 **IA Responde:** Deuda actual {deuda_ebitda:.1f}x EBITDA es elevada. Priorizar reducción de deuda o capitalización. "
                        f"Alternativas: factoring ({m(cuentas_cob*0.80)} disponible), leasing en lugar de compra de activos.")
        elif "insolvencia" in pregunta:
            return (f"🧠 **IA Responde — Riesgo de insolvencia:**\n"
                    f"• Altman Z-Score: {altman_z:.2f} → {altman_zona}\n"
                    f"• Cobertura intereses: {cobertura_int:.2f}x {'(OK)' if cobertura_int>=2 else '(⚠️ bajo)'}\n"
                    f"• Liquidez corriente: {liquidez_corr:.2f}x {'(OK)' if liquidez_corr>=1.2 else '(⚠️ crítica)'}\n"
                    f"• Probabilidad estimada de dificultad 12M: {max(0,1-altman_z/3):.0%}")
        elif "liquidez" in pregunta:
            return (f"🧠 **IA Responde — Mejorar liquidez sin deuda:**\n"
                    f"• Factorizar cuentas por cobrar: {m(cuentas_cob*0.80)} disponibles\n"
                    f"• Reducir días cobro {dias_cobro}→{max(30,dias_cobro-15):.0f} días: libera {m(ventas/365*15)}\n"
                    f"• Ampliar días pago {dias_pago}→{min(60,dias_pago+15):.0f} días: retiene {m(costo_v/365*15)}\n"
                    f"• Reducir inventario 10%: libera {m(inventario*0.10)}\n"
                    f"• Invertir exceso en fondo mutuo / overnight")
        return "🧠 Pregunta en procesamiento. Conectar con modelo LLM para respuesta extendida."

    respuesta = ia_responder(pregunta)
    st.markdown(respuesta)

    st.divider()
    st.subheader("Pregunta libre al sistema")
    pregunta_libre = st.text_input("¿Qué quieres saber sobre las finanzas de tu empresa?",
                                    placeholder="Ej: ¿Cuándo será rentable si crezco un 15% anual?")
    if pregunta_libre:
        st.info(f"🧠 Para respuestas personalizadas a preguntas libres, conectar con API de OpenAI/Claude "
                f"pasando el contexto financiero de {empresa} (EVA={m(eva)}, WACC={pct(wacc)}, ROIC={pct(roic)}). "
                f"El motor de reglas ya está listo — solo requiere integración LLM.")


# ══════════════════════════════════════════════════════════════════
# N14 — CEO DASHBOARD
# ══════════════════════════════════════════════════════════════════
with t14:
    st.header(f"N14 · CEO Dashboard — {empresa}")
    st.caption(f"Vista ejecutiva consolidada | {datetime.date.today().strftime('%d de %B de %Y')}")

    # Banner principal
    ceo1,ceo2,ceo3,ceo4 = st.columns(4)
    ceo1.metric("Valor empresa (EV DCF)", m(ev_dcf2 if 'ev_dcf2' in dir() else ev_dcf))
    ceo2.metric("Valor creado este año",  m(eva), "🟢 Positivo" if eva>0 else "🔴 Negativo")
    ceo3.metric("Flujo libre de caja",    m(fcf))
    ceo4.metric("Riesgo de quiebra",      altman_zona)

    ceo5,ceo6,ceo7,ceo8 = st.columns(4)
    ceo5.metric("Liquidez",               f"{liquidez_corr:.2f}x",  "🟢" if liquidez_corr>=1.5 else "🔴")
    ceo6.metric("Apalancamiento",         f"{deuda_ebitda:.2f}x",   "🟢" if deuda_ebitda<=3 else "🔴")
    ceo7.metric("Prob. cumplir deuda",    f"{min(cobertura_int/3,1):.0%}")
    ceo8.metric("Score Global",           f"{score_fin:.0f}/100",   sem(score_fin/100))

    # Semáforo global ejecutivo
    st.subheader("Panel de Señales Ejecutivas")
    señales = [
        ("Creación de valor (EVA)",      eva>0,              m(eva)),
        ("ROIC > WACC",                  roic>wacc,          f"{pct(roic)} vs {pct(wacc)}"),
        ("Liquidez suficiente",           liquidez_corr>=1.5, f"{liquidez_corr:.2f}x"),
        ("Apalancamiento controlado",     deuda_ebitda<=3.0,  f"{deuda_ebitda:.2f}x EBITDA"),
        ("Cobertura de intereses ≥2.5x", cobertura_int>=2.5, f"{cobertura_int:.2f}x"),
        ("FCF positivo",                  fcf>0,              m(fcf)),
        ("Altman Z-Score seguro",         altman_z>2.99,      f"{altman_z:.2f}"),
        ("Margen EBITDA ≥12%",           margen_ebitda>=0.12,pct(margen_ebitda)),
    ]
    for label, ok, valor in señales:
        col_s1, col_s2, col_s3 = st.columns([3,2,1])
        col_s1.write(label)
        col_s2.write(valor)
        col_s3.write("🟢 OK" if ok else "🔴 Alerta")

    # Recomendación automática CEO
    st.subheader("🤖 Recomendación Automática para el CEO")
    alertas_ceo = sum([1 for _,ok,_ in señales if not ok])
    if alertas_ceo == 0:
        st.success("✅ Empresa en posición sólida. Foco en reinversión, expansión y creación de valor acelerada.")
    elif alertas_ceo <= 2:
        st.warning(f"⚠️ {alertas_ceo} señales en alerta. Monitorear y corregir. Empresa viable con áreas de mejora.")
    else:
        st.error(f"🚨 {alertas_ceo} señales críticas. Activar plan de turnaround: revisar estructura de capital, "
                 "optimizar caja, renegociar deuda y mejorar márgenes operativos.")

    # Resumen ejecutivo una página
    st.subheader("Resumen Ejecutivo — Una Página")
    resumen_ceo = pd.DataFrame([
        ["Ventas",             m(ventas),          pct(0),             "Base del negocio"],
        ["EBITDA",             m(ebitda),          pct(margen_ebitda), "Eficiencia operativa"],
        ["Utilidad neta",      m(utilidad_neta),   pct(margen_neto),   "Rentabilidad final"],
        ["FCF",                m(fcf),             pct(safe(fcf,ventas)),"Generación de caja"],
        ["EVA",                m(eva),             "",                  "Creación de valor"],
        ["Enterprise Value",   m(ev_dcf2 if 'ev_dcf2' in dir() else ev_dcf),"","Valor de la empresa"],
        ["WACC",               pct(wacc),          "",                  "Costo del capital"],
        ["ROIC",               pct(roic),          f">{pct(wacc)} = {'SÍ crea' if roic>wacc else 'NO crea'}", "Retorno sobre capital"],
        ["Deuda/EBITDA",       f"{deuda_ebitda:.2f}x","","Solvencia"],
        ["Altman Z",           f"{altman_z:.2f}",  altman_zona,        "Riesgo quiebra"],
        ["Score global",       f"{score_fin:.0f}/100","","Salud financiera"],
    ], columns=["KPI","Valor","Referencia","Interpretación"])
    st.dataframe(resumen_ceo, use_container_width=True, hide_index=True)

    # Exportar
    st.divider()
    csv_out = resumen_ceo.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Descargar resumen ejecutivo CSV",
        data=csv_out,
        file_name=f"risk_analytics_{empresa.replace(' ','_')}_{datetime.date.today()}.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════
# N15 — INTELIGENCIA COMPETITIVA Y BENCHMARKING DE MERCADO
# ══════════════════════════════════════════════════════════════════
with t15:
    st.header("N15 · Inteligencia Competitiva y Benchmarking de Mercado")
    st.caption("¿Mi empresa está ganando o perdiendo frente a su competencia? Cuatro preguntas: "
               "¿cómo estoy hoy?, ¿cómo estoy frente al mercado?, ¿dónde estoy perdiendo dinero?, ¿qué debo hacer?")

    comp_cols_num = ["Ventas","Margen EBITDA %","ROE %","Deuda/EBITDA","Liquidez",
                      "ARPU / Ticket prom. (S/)","Churn %","Participación mercado %"]
    comp_df15 = comp_df_edit_corp.copy()
    if "Competidor" not in comp_df15.columns:
        comp_df15["Competidor"] = [f"Competidor {i+1}" for i in range(len(comp_df15))]
    comp_df15["Competidor"] = comp_df15["Competidor"].fillna("").replace("", None)
    comp_df15 = comp_df15.dropna(subset=["Competidor"])
    for col in comp_cols_num:
        if col not in comp_df15.columns:
            comp_df15[col] = 0.0
        comp_df15[col] = pd.to_numeric(comp_df15[col], errors="coerce").fillna(0.0)

    hay_comp15 = len(comp_df15) > 0
    prom15 = comp_df15[comp_cols_num].mean() if hay_comp15 else pd.Series({c: 0.0 for c in comp_cols_num})

    ventas_trab   = safe(ventas, n_trabajadores)
    ebitda_trab   = safe(ebitda, n_trabajadores)
    costo_x_cliente_proxy = safe(gastos_op + costo_v*0.02, max(comp_df15["Participación mercado %"].sum() or 1, 1))

    mi_fila15 = pd.DataFrame([{
        "Competidor": f"🏢 {empresa} (mi empresa)",
        "Ventas": ventas,
        "Margen EBITDA %": margen_ebitda*100,
        "ROE %": roe*100,
        "Deuda/EBITDA": deuda_ebitda,
        "Liquidez": liquidez_corr,
        "ARPU / Ticket prom. (S/)": np.nan,
        "Churn %": np.nan,
        "Participación mercado %": np.nan,
    }])
    tabla15 = pd.concat([mi_fila15, comp_df15], ignore_index=True)

    n15_1, n15_2, n15_3, n15_4, n15_5, n15_6, n15_7 = st.tabs([
        "📊 Benchmark Financiero", "🥇 Ranking y Market Share", "🕸️ Radar Competitivo",
        "🏭 Operativo y Productividad", "📆 Benchmark Interno/Sectorial",
        "🚨 Alertas", "🧠 IA Competitiva",
    ])

    # ---- Benchmark financiero ----
    with n15_1:
        st.subheader("Comparación financiera — mi empresa vs. competencia")
        tabla_fmt15 = tabla15.copy()
        tabla_fmt15["Ventas"] = tabla_fmt15["Ventas"].map(m)
        tabla_fmt15["Margen EBITDA %"] = tabla_fmt15["Margen EBITDA %"].map(lambda x: f"{x:.1f}%")
        tabla_fmt15["ROE %"] = tabla_fmt15["ROE %"].map(lambda x: f"{x:.1f}%")
        tabla_fmt15["Deuda/EBITDA"] = tabla_fmt15["Deuda/EBITDA"].map(lambda x: f"{x:.2f}x")
        tabla_fmt15["Liquidez"] = tabla_fmt15["Liquidez"].map(lambda x: f"{x:.2f}x")
        tabla_fmt15["ARPU / Ticket prom. (S/)"] = tabla_fmt15["ARPU / Ticket prom. (S/)"].map(lambda x: f"S/ {x:,.0f}" if pd.notna(x) else "—")
        tabla_fmt15["Churn %"] = tabla_fmt15["Churn %"].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        tabla_fmt15["Participación mercado %"] = tabla_fmt15["Participación mercado %"].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
        st.dataframe(tabla_fmt15, use_container_width=True, hide_index=True)

        if hay_comp15:
            f1,f2,f3,f4 = st.columns(4)
            f1.metric("Margen EBITDA vs. mercado", pct(margen_ebitda), f"{margen_ebitda*100 - prom15['Margen EBITDA %']:+.1f} pts")
            f2.metric("ROE vs. mercado", pct(roe), f"{roe*100 - prom15['ROE %']:+.1f} pts")
            f3.metric("Deuda/EBITDA vs. mercado", f"{deuda_ebitda:.2f}x", f"{deuda_ebitda - prom15['Deuda/EBITDA']:+.2f}", delta_color="inverse")
            f4.metric("Liquidez vs. mercado", f"{liquidez_corr:.2f}x", f"{liquidez_corr - prom15['Liquidez']:+.2f}")
        else:
            st.info("Agrega competidores en la barra lateral para activar la comparación automática.")

    # ---- Ranking y market share ----
    with n15_2:
        st.subheader("Ranking competitivo")
        if hay_comp15:
            rank_df = tabla15.copy()
            rank_df["Score"] = (
                rank_df["Margen EBITDA %"].rank(pct=True) +
                rank_df["ROE %"].rank(pct=True) +
                rank_df["Liquidez"].rank(pct=True) +
                (1 - rank_df["Deuda/EBITDA"].rank(pct=True))
            )
            rank_df = rank_df.sort_values("Score", ascending=False).reset_index(drop=True)
            medallas = ["🥇","🥈","🥉"] + [""]*max(0, len(rank_df)-3)
            rank_out = pd.DataFrame({
                "Posición": [f"{medallas[i]} {i+1}" for i in range(len(rank_df))],
                "Empresa": rank_df["Competidor"],
                "Score competitivo": rank_df["Score"].map(lambda x: f"{x:.2f}"),
            })
            st.dataframe(rank_out, use_container_width=True, hide_index=True)
        else:
            st.info("Agrega competidores para calcular el ranking.")

        st.subheader("Participación de mercado")
        if hay_comp15 and comp_df15["Participación mercado %"].sum() > 0:
            labels_ms = list(comp_df15["Competidor"])
            values_ms = list(comp_df15["Participación mercado %"])
            mi_part = max(0.0, 100 - sum(values_ms))
            fig_ms15 = go.Figure(go.Bar(
                x=[f"🏢 {empresa}"] + labels_ms, y=[mi_part] + values_ms,
                marker_color=["#1F3864"] + ["#BA68C8"]*len(labels_ms),
                text=[f"{v:.1f}%" for v in [mi_part]+values_ms], textposition="outside",
            ))
            fig_ms15.update_layout(height=380, yaxis_title="Participación de mercado (%)")
            st.plotly_chart(fig_ms15, use_container_width=True)
            st.caption("Tu participación se estima como el residuo (100% − Σ competidores); ajústala si tienes "
                       "datos propios de mercado (regulador sectorial, gremio, estudios de mercado).")
        else:
            st.info("Ingresa participación de mercado (%) de tus competidores en la barra lateral.")

    # ---- Radar competitivo ----
    with n15_3:
        st.subheader("Radar competitivo — mi empresa vs. promedio del mercado")
        cats15 = ["Rentabilidad (ROE)","Margen EBITDA","Liquidez","Bajo apalancamiento","Baja fuga (Churn)"]
        def norm15(v, ref, invert=False):
            x = min(1.0, max(0.0, safe(v, ref))) if ref else 0.0
            return x
        mi_churn_proxy = 1 - min(1.0, safe(prom15["Churn %"], 10.0)) if hay_comp15 else 0.5
        mi_vals15 = [
            norm15(roe, 0.18), norm15(margen_ebitda, 0.25), norm15(liquidez_corr, 2.0),
            norm15(1-min(deuda_ebitda/6,1), 1.0), mi_churn_proxy,
        ]
        if hay_comp15:
            comp_vals15 = [
                norm15(prom15["ROE %"]/100, 0.18),
                norm15(prom15["Margen EBITDA %"]/100, 0.25),
                norm15(prom15["Liquidez"], 2.0),
                norm15(1-min(prom15["Deuda/EBITDA"]/6,1), 1.0),
                1 - min(1.0, safe(prom15["Churn %"], 10.0)),
            ]
        else:
            comp_vals15 = [0,0,0,0,0]

        fig_r15 = go.Figure()
        fig_r15.add_trace(go.Scatterpolar(r=mi_vals15+[mi_vals15[0]], theta=cats15+[cats15[0]],
                                           fill='toself', name=f"🏢 {empresa}", line_color="#1F3864"))
        fig_r15.add_trace(go.Scatterpolar(r=comp_vals15+[comp_vals15[0]], theta=cats15+[cats15[0]],
                                           fill='toself', name="Promedio competencia", line_color="#E53935"))
        fig_r15.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])), height=460, showlegend=True)
        st.plotly_chart(fig_r15, use_container_width=True)

    # ---- Operativo y productividad ----
    with n15_4:
        st.subheader("Productividad — mi empresa")
        p1,p2,p3 = st.columns(3)
        p1.metric("Ventas por trabajador", m(ventas_trab))
        p2.metric("EBITDA por trabajador", m(ebitda_trab))
        p3.metric("N° de trabajadores", f"{n_trabajadores:,}")

        st.subheader("Benchmark comercial — ARPU / Ticket promedio y Churn")
        if hay_comp15 and comp_df15["ARPU / Ticket prom. (S/)"].sum() > 0:
            fig_arpu = go.Figure(go.Bar(
                x=list(comp_df15["Competidor"]), y=list(comp_df15["ARPU / Ticket prom. (S/)"]),
                marker_color="#8E24AA",
                text=[f"S/ {v:,.0f}" for v in comp_df15["ARPU / Ticket prom. (S/)"]], textposition="outside",
            ))
            fig_arpu.update_layout(height=340, yaxis_title="ARPU / Ticket promedio (S/)")
            st.plotly_chart(fig_arpu, use_container_width=True)
        if hay_comp15 and comp_df15["Churn %"].sum() > 0:
            fig_churn = go.Figure(go.Bar(
                x=list(comp_df15["Competidor"]), y=list(comp_df15["Churn %"]),
                marker_color="#EF6C00",
                text=[f"{v:.1f}%" for v in comp_df15["Churn %"]], textposition="outside",
            ))
            fig_churn.update_layout(height=340, yaxis_title="Churn (%)")
            st.plotly_chart(fig_churn, use_container_width=True)
        if not hay_comp15:
            st.info("Ingresa ARPU y Churn de tus competidores en la barra lateral para ver estos gráficos.")

    # ---- Benchmark interno / sectorial ----
    with n15_5:
        st.subheader("Benchmark interno — cuando no hay comparables públicos")
        st.caption("Cuando la competencia no publica estados financieros (empresas privadas, no listadas), "
                   "compara tu propio desempeño en el tiempo: siempre es posible y aporta valor.")
        bi1,bi2,bi3 = st.columns(3)
        bi1.metric("Margen EBITDA actual", pct(margen_ebitda))
        bi2.metric("ROE actual", pct(roe))
        bi3.metric("Deuda/EBITDA actual", f"{deuda_ebitda:.2f}x")
        st.markdown("- Año actual vs. año anterior\n- Mes actual vs. mismo mes del año anterior\n"
                    "- Presupuesto vs. resultado real\n- Sucursal vs. sucursal / unidad de negocio vs. unidad de negocio")

        st.subheader("Benchmark sectorial (fuentes públicas agregadas)")
        st.info("Cuando existan, incorpora promedios sectoriales de fuentes como INEI, SBS, SMV, BCRP, SUNAT "
                "(estadísticas agregadas) u organismos reguladores del sector (p. ej. OSIPTEL en telecomunicaciones), "
                "para comparar tu margen operativo, crecimiento y endeudamiento frente al promedio de la industria, "
                "incluso cuando no tengas el detalle financiero de cada competidor.")

    # ---- Alertas ----
    with n15_6:
        st.subheader("🚨 Alertas competitivas")
        alertas15 = []
        if hay_comp15:
            if margen_ebitda*100 >= prom15["Margen EBITDA %"]:
                alertas15.append(("🟢", f"Margen EBITDA superior al promedio del sector ({pct(margen_ebitda)} vs. {prom15['Margen EBITDA %']:.1f}%)."))
            else:
                alertas15.append(("🔴", f"Margen EBITDA por debajo del promedio del sector ({pct(margen_ebitda)} vs. {prom15['Margen EBITDA %']:.1f}%)."))
            if deuda_ebitda <= prom15["Deuda/EBITDA"]:
                alertas15.append(("🟢", f"Apalancamiento más conservador que el mercado ({deuda_ebitda:.2f}x vs. {prom15['Deuda/EBITDA']:.2f}x)."))
            else:
                alertas15.append(("🟡", f"Apalancamiento por encima del promedio del sector ({deuda_ebitda:.2f}x vs. {prom15['Deuda/EBITDA']:.2f}x)."))
            if liquidez_corr < prom15["Liquidez"]:
                alertas15.append(("🟡", f"Liquidez por debajo del promedio de la competencia ({liquidez_corr:.2f}x vs. {prom15['Liquidez']:.2f}x)."))
            if roe < prom15["ROE %"]/100:
                alertas15.append(("🔴", f"ROE por debajo del promedio del mercado ({pct(roe)} vs. {prom15['ROE %']:.1f}%)."))
        else:
            alertas15.append(("ℹ️", "Agrega competidores en la barra lateral para generar alertas automáticas."))

        for icono, texto in alertas15:
            st.write(f"{icono} {texto}")

    # ---- IA competitiva ----
    with n15_7:
        st.subheader("🧠 Análisis automático de posición competitiva")
        if hay_comp15:
            texto_ia = (
                f"La empresa presenta un margen EBITDA de {pct(margen_ebitda)} frente a un promedio de mercado de "
                f"{prom15['Margen EBITDA %']:.1f}%, y un ROE de {pct(roe)} frente a {prom15['ROE %']:.1f}% del promedio "
                f"de la competencia. Su nivel de apalancamiento (Deuda/EBITDA {deuda_ebitda:.2f}x) se compara contra "
                f"{prom15['Deuda/EBITDA']:.2f}x del mercado, y su liquidez corriente ({liquidez_corr:.2f}x) frente a "
                f"{prom15['Liquidez']:.2f}x del promedio de competidores. "
            )
            if margen_ebitda*100 < prom15["Margen EBITDA %"] and roe < prom15["ROE %"]/100:
                texto_ia += ("En conjunto, esto sugiere que la empresa está por debajo del mercado tanto en "
                             "eficiencia operativa como en rentabilidad patrimonial, lo que amerita revisar la "
                             "estructura de costos, la estrategia comercial y el uso del capital invertido.")
            elif margen_ebitda*100 >= prom15["Margen EBITDA %"] and roe >= prom15["ROE %"]/100:
                texto_ia += ("En conjunto, la empresa muestra una posición competitiva superior al promedio del "
                             "mercado en rentabilidad y eficiencia operativa, lo que representa una ventaja para "
                             "sostener o ganar participación de mercado.")
            else:
                texto_ia += ("Esto sugiere una posición mixta: fuerte en algunos indicadores y rezagada en otros, "
                             "por lo que conviene priorizar el componente con mayor brecha frente al mercado.")
            st.markdown(texto_ia)
        else:
            st.info("Agrega al menos un competidor en la barra lateral para generar el análisis automático de la IA.")

        st.divider()
        st.caption("Nota: cuando no existan datos financieros públicos de la competencia directa (empresas privadas "
                   "o sin obligación de reporte), usa el Benchmark Interno y Sectorial de la pestaña anterior para "
                   "mantener una referencia útil de comparación, en línea con las cuatro capas de la plataforma: "
                   "operación diaria, inteligencia financiera, inteligencia competitiva e inteligencia estratégica.")

st.divider()
st.caption("RISK ANALYTICS AI © 2026 — Sistema de Inteligencia Financiera Corporativa | Desarrollado con Python + Streamlit | Para uso profesional, consultoría y directorios.")
