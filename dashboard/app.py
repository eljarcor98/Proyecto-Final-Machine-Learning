import streamlit as st
import sys
import os
import subprocess
import psutil

# Add project root to sys.path to resolve imports in sub-pages
# The project root is one level up from the 'dashboard' folder
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def ensure_orchestrator_running():
    """Check if orchestrator.py is running, if not, start it in background."""
    orchestrator_name = "orchestrator.py"
    running = False
    for proc in psutil.process_iter(['cmdline']):
        try:
            if proc.info['cmdline'] and any(orchestrator_name in arg for arg in proc.info['cmdline']):
                running = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if not running:
        orchestrator_path = os.path.join(project_root, "scripts", "orchestrator.py")
        subprocess.Popen(
            [sys.executable, orchestrator_path],
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True if os.name != 'nt' else False
        )

# Run automation check
ensure_orchestrator_running()

# Initialize database tables
from src.db import init_db
init_db()

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
        background-color: #0f172a;
    }
    
    .stTitle {
        font-weight: 700 !important;
        color: #f8fafc !important;
        text-align: center;
        padding-bottom: 1rem;
    }
    
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
        color: white;
    }

    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .section-header {
        color: #f8fafc;
        font-weight: 600;
        border-bottom: 2px solid #334155;
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

    /* Completely hide the sidebar and its toggle globally */
    [data-testid="stSidebar"], 
    [data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Custom Return Button Style */
    .return-btn {
        display: inline-block;
        padding: 8px 16px;
        background-color: #3b82f6;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Montserrat', sans-serif;
        transition: background-color 0.3s ease;
        border: none;
        cursor: pointer;
    }

    .return-btn:hover {
        background-color: #2563eb;
        color: white !important;
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
            <h3 style="margin:0; font-family: 'Montserrat', sans-serif; color: white;">📡 Radar Aéreo</h3>
            <p style="color:#cbd5e1; font-family: 'Montserrat', sans-serif;">Vigilancia de tráfico en tiempo real y detección de anomalías en rutas críticas.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder al Radar 📡", width='stretch'):
        st.switch_page("pages/radar.py")

with col2:
    st.markdown("""
        <div class="metric-card">
            <h3 style="margin:0; font-family: 'Montserrat', sans-serif; color: white;">⏳ Línea de Tiempo</h3>
            <p style="color:#cbd5e1; font-family: 'Montserrat', sans-serif;">Mapeo geo-temporal de eventos críticos y noticias relacionadas.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder al Timeline ⏳", width='stretch'):
        st.switch_page("pages/timeline.py")

with col3:
    st.markdown("""
        <div class="metric-card">
            <h3 style="margin:0; font-family: 'Montserrat', sans-serif; color: white;">📊 Análisis NLP</h3>
            <p style="color:#cbd5e1; font-family: 'Montserrat', sans-serif;">Minería de datos, nubes de palabras y análisis de entidades nombradas.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder al Análisis 📊", width='stretch'):
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
    - **Automatización**: El Orquestador de Datos se ejecuta automáticamente en segundo plano.
    """)

st.info("💡 **Nota**: Utilice los botones superiores para navegar entre los módulos de análisis.")