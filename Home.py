# ============================================================
# RISK ANALYTICS AI — HOME
# Árbol de navegación · Ruta de Madurez Financiera
# Ejecutar: streamlit run Home.py
# (requiere la carpeta "pages/" en el mismo directorio)
# ============================================================

import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="RISK ANALYTICS AI — Ruta de Madurez Financiera",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
[data-testid="stMetricValue"]{font-size:1.2rem;font-weight:700;}
.block-container{padding-top:2rem; max-width:1150px;}
.raa-card{
    border:1px solid rgba(49,51,63,0.15); border-radius:14px; padding:1.4rem 1.6rem;
    height:100%;
}
.raa-badge{
    display:inline-block; font-size:0.75rem; font-weight:700; letter-spacing:.03em;
    padding:0.15rem 0.6rem; border-radius:999px; margin-bottom:0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# ENCABEZADO
# ============================================================
st.title("🧭 RISK ANALYTICS AI")
st.subheader("Ruta de Madurez Financiera")
st.caption("Un mismo sistema, dos niveles de profundidad — elige dónde empezar según la complejidad de la empresa.")

st.divider()

# ============================================================
# ÁRBOL DE NAVEGACIÓN — TREEMAP
# ============================================================
labels = [
    "RISK ANALYTICS AI",
    "PYME — 12 módulos", "Corporativo — 15 niveles",
    # PYME
    "M1 Diagnóstico", "M2 DuPont", "M3 CAMEL", "M4 Controller", "M5 Tesorería",
    "M6 Instrumentos", "M7 Creación de Valor", "M8 Valoración", "M9 Riesgo",
    "M10 IA Financiera", "M11 Warren Buffett", "M12 Intel. Competitiva",
    # Corporativo
    "N1 Corporate Control", "N2 Tesorería", "N3 Intel. Financiera", "N4 Warren Buffett",
    "N5 Valoración", "N6 Monte Carlo", "N7 Markowitz", "N8 Machine Learning",
    "N9 Instrumentos", "N10 Intel. Tributaria", "N11 Controller", "N12 Intel. Estratégica",
    "N13 IA Financiera", "N14 CEO Dashboard", "N15 Intel. Competitiva",
]
parents = [
    "",
    "RISK ANALYTICS AI", "RISK ANALYTICS AI",
    "PYME — 12 módulos","PYME — 12 módulos","PYME — 12 módulos","PYME — 12 módulos","PYME — 12 módulos",
    "PYME — 12 módulos","PYME — 12 módulos","PYME — 12 módulos","PYME — 12 módulos",
    "PYME — 12 módulos","PYME — 12 módulos","PYME — 12 módulos",
    "Corporativo — 15 niveles","Corporativo — 15 niveles","Corporativo — 15 niveles","Corporativo — 15 niveles",
    "Corporativo — 15 niveles","Corporativo — 15 niveles","Corporativo — 15 niveles","Corporativo — 15 niveles",
    "Corporativo — 15 niveles","Corporativo — 15 niveles","Corporativo — 15 niveles","Corporativo — 15 niveles",
    "Corporativo — 15 niveles","Corporativo — 15 niveles","Corporativo — 15 niveles",
]
colors = (
    ["#1F3864", "#2E7D32", "#8E24AA"] +
    ["#66BB6A"]*12 +
    ["#BA68C8"]*15
)

fig = go.Figure(go.Treemap(
    labels=labels, parents=parents,
    marker=dict(colors=colors),
    root_color="#1F3864",
    textfont=dict(size=13),
))
fig.update_layout(height=520, margin=dict(t=10, l=10, r=10, b=10))
# staticPlot=True desactiva el click-to-zoom, el pan y la modebar.
# El árbol es solo decorativo: la navegación real ocurre con los page_link de abajo,
# así que nadie puede quedar "atrapado" dentro de una caja hoja (como N1 Corporate Control).
st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

st.divider()

# ============================================================
# TARJETAS DE NAVEGACIÓN
# ============================================================
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="raa-card">', unsafe_allow_html=True)
    st.markdown('<span class="raa-badge" style="background:#E8F5E9;color:#2E7D32;">NIVEL DE ENTRADA</span>', unsafe_allow_html=True)
    st.markdown("### 🧩 Versión PYME")
    st.caption("Para empresas que recién estructuran su análisis financiero.")
    st.markdown("""
- Diagnóstico clásico, DuPont y CAMEL
- Controller y Tesorería con recomendaciones automáticas
- Creación de valor, Valoración y Riesgo, en versión guiada
- IA Financiera con preguntas frecuentes ya resueltas
- **Nuevo:** Inteligencia Competitiva — benchmark financiero, mercado y radar vs. la competencia
""")
    st.page_link("pages/1_PYME.py", label="Entrar a la versión PYME", icon="🧩")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="raa-card">', unsafe_allow_html=True)
    st.markdown('<span class="raa-badge" style="background:#F3E5F5;color:#6A1B9A;">NIVEL AVANZADO</span>', unsafe_allow_html=True)
    st.markdown("### 🏦 Versión Corporativa")
    st.caption("Para bancos, fondos, family offices y empresas con equipo financiero propio.")
    st.markdown("""
- Los 15 niveles completos: Markowitz, Machine Learning, Instrumentos derivados
- Simulación Monte Carlo a gran escala y CEO Dashboard
- Inteligencia tributaria (SUNAT, NIIF, BEPS) y Controller avanzado
- Motor de IA Financiera con respuestas estratégicas ampliadas
- **Nuevo:** Inteligencia Competitiva y Benchmarking — ranking, ARPU/Churn, radar y alertas vs. mercado
""")
    st.page_link("pages/2_Corporativo.py", label="Entrar a la versión Corporativa", icon="🏦")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.info(
    "🧭 **¿Cómo funciona la ruta de madurez?** Una empresa suele empezar en la versión PYME, con el lenguaje "
    "tradicional de ratios, presupuestos y CAMEL. A medida que su análisis financiero madura, "
    "puede pasar a la versión Corporativa, que agrega valoración avanzada, riesgo con Monte Carlo, "
    "portafolio (Markowitz) e inteligencia tributaria — sin tener que aprender un sistema nuevo desde cero, "
    "porque los conceptos base (EVA, WACC, ROIC, Warren Buffett Score) son los mismos en ambos niveles."
)
st.caption("RISK ANALYTICS AI © 2026 | Ruta de Madurez Financiera | Desarrollado con Python + Streamlit")
