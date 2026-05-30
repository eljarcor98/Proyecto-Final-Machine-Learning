import streamlit as st

# Page config
st.set_page_config(page_title="Conflicto en Medio Oriente", layout="wide", page_icon="🌍")

# Custom CSS for the "Command Center" look with requested enhancements
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    
    .stTitle {
        font-weight: 700 !important;
        color: #1e293b !important;
        text-align: center;
        padding-bottom: 1rem;
    }
    
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .section-header {
        color: #334155;
        font-weight: 600;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Vanish / Fade-in effect for page transitions */
    .stApp {
        animation: vanishIn 0.6s ease-out;
    }

    @keyframes vanishIn {
        0% { opacity: 0; transform: scale(0.98); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* Completely hide the sidebar on the index page */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide the sidebar toggle button as well */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 Conflicto en Medio Oriente")

# --- Hero Section ---
st.markdown("<div class='section-header'>🛰️ Centro de Monitoreo Estratégico de Inteligencia</div>", unsafe_allow_html=True)
st.markdown("""
Este sistema de inteligencia monitorea la volatilidad geopolítica en el Medio Oriente, enfocándose en el análisis de datos abiertos (OSINT) para comprender la dinámica entre los actores regionales y globales.
""")

st.markdown("---")

# --- Index/Quick Navigation ---
st.subheader("🚀 Navegación de Módulos")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="metric-card">
            <h3 style="margin:0; font-family: 'Montserrat', sans-serif;">📡 Radar Aéreo</h3>
            <p style="color:#64748b; font-family: 'Montserrat', sans-serif;">Vigilancia de tráfico en tiempo real y detección de anomalías en rutas críticas.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder al Radar 📡", use_container_width=True):
        st.switch_page("pages/radar.py")

with col2:
    st.markdown("""
        <div class="metric-card">
            <h3 style="margin:0; font-family: 'Montserrat', sans-serif;">⏳ Línea de Tiempo</h3>
            <p style="color:#64748b; font-family: 'Montserrat', sans-serif;">Mapeo geo-temporal de eventos críticos y noticias relacionadas.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder al Timeline ⏳", use_container_width=True):
        st.switch_page("pages/timeline.py")

with col3:
    st.markdown("""
        <div class="metric-card">
            <h3 style="margin:0; font-family: 'Montserrat', sans-serif;">📊 Análisis NLP</h3>
            <p style="color:#64748b; font-family: 'Montserrat', sans-serif;">Minería de datos, nubes de palabras y análisis de entidades nombradas.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder al Análisis 📊", use_container_width=True):
        st.switch_page("pages/nlp.py")

st.markdown("---")

# --- Methodology & Goals ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<div class='section-header'>🎯 Objetivos del Monitoreo</div>", unsafe_allow_html=True)
    st.markdown("""
    - **Vigilancia Aérea**: Monitoreo de tráfico para detectar anomalías.
    - **Análisis de Narrativas**: Extracción de tópicos y entidades geográficas.
    - **Sincronización Temporal**: Visualización de concentración de tensiones.
    """)

with col_right:
    st.markdown("<div class='section-header'>🛠️ Arquitectura del Sistema</div>", unsafe_allow_html=True)
    st.markdown("""
    - **NLP**: Modelos `spaCy` para Reconocimiento de Entidades Nombradas (NER).
    - **Geocodificación**: Mapeo de menciones textuales a coordenadas GPS.
    - **Pipeline**: Ingesta automatizada GNews $\rightarrow$ PostgreSQL (Supabase).
    """)

st.info("💡 **Nota**: Utilice los botones superiores para navegar entre los módulos de análisis.")