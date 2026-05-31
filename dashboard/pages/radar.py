import streamlit as st
import pandas as pd
import pydeck as pdk
import airportsdata
import os
import json
import sys
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Ajustar ruta para importar desde src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle, init_db, db

# Asegurar que la base de datos esté inicializada
init_db()

st.set_page_config(page_title="Radar Aéreo OSINT", layout="wide", page_icon="🛰️")

# Global CSS for consistency and hiding sidebar
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    
    /* Use a more targeted font application to avoid overlapping/layout issues */
    html, body, st.markdown, .stApp { 
        font-family: 'Montserrat', sans-serif !important; 
    }
    
    /* Force line-height in all streamlit elements to prevent "montadas" (overlapping) text */
    div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stAlertContentInfo"] p, 
    div[data-testid="stCaptionContainer"] p {
        line-height: 1.6 !important;
        margin-bottom: 0.5rem !important;
    }

    .stApp { animation: vanishIn 0.6s ease-out; }
    @keyframes vanishIn { 0% { opacity: 0; transform: scale(0.98); } 100% { opacity: 1; transform: scale(1); } }
    [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], div[data-testid="stSidebarNav"] { display: none !important; }
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
    .return-btn:hover { background-color: #2563eb; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Return button
st.markdown('<a href="/" target="_self" class="return-btn">⬅️ Volver al Index</a>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.title("🛰️ Radar de Vigilancia Aérea")
st.markdown("Monitoreo de tráfico aéreo en tiempo real sobre zonas de conflicto.")

# Autorefresh cada 60 segundos
st_autorefresh(interval=60000, key="radar_refresh")

# --- Session State ---
if 'history' not in st.session_state:
    st.session_state.history = {}
if 'selected_icao' not in st.session_state:
    st.session_state.selected_icao = None

def update_data_manual():
    with st.spinner("Actualizando datos de radar..."):
        try:
            from scripts.fetch_opensky_data import fetch_opensky_states
            fetch_opensky_states()
            st.success("Radar actualizado correctamente")
        except Exception as e:
            st.error(f"Error al actualizar radar: {e}")

# Controls Section (Moved from Sidebar to Main)
with st.expander("🎮 Controles y Estado del Sistema", expanded=False):
    # Button on its own line for clarity and to prevent overlapping
    if st.button("🔄 Actualizar Radar Ahora", use_container_width=True):
        update_data_manual()
    
    st.markdown("---")
    
    # Status section using full width
    st.markdown("**🤖 Estado del Orquestador**")
    st.info("El orquestador automatiza GNews, RSS y GDELT.")
    st.caption("Sugerencia: Ejecuta `py scripts/orchestrator.py` en tu servidor para automatización total.")

def load_data():
    """Retrieve the latest flights data from the database."""
    data = db.get_all_flights()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

df = load_data()

if not df.empty and 'icao24' in df.columns:
    # Actualización de Historial para Rutas
    for _, row in df.iterrows():
        icao = row.get('icao24')
        if icao is None:
            continue
        if icao not in st.session_state.history: 
            st.session_state.history[icao] = []
        pos = [row.get('lon'), row.get('lat')]
        # Solo agregar si la posición cambió significativamente para evitar ruido
        if not st.session_state.history[icao] or \
           (abs(st.session_state.history[icao][-1][0] - pos[0]) > 0.01 or \
            abs(st.session_state.history[icao][-1][1] - pos[1]) > 0.01):
            st.session_state.history[icao].append(pos)
            if len(st.session_state.history[icao]) > 50: 
                st.session_state.history[icao].pop(0)

    def get_color(icao):
        if icao == st.session_state.selected_icao:
            return [255, 0, 255, 255] # Magenta
        return [0, 128, 255, 200]    # Azul

    if 'icao24' in df.columns:
        df['fill_color'] = df['icao24'].apply(get_color)
    else:
        df['fill_color'] = [get_color(None)] * len(df)

    layers = []
    # Capa de fondo (estática)
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_color="[200, 200, 200, 30]",
        get_radius=5000,
    ))

    # --- CORRECCIÓN DE RUTA DE VUELO ---
    # Si hay un avión seleccionado, dibujamos su trayectoria histórica
    if st.session_state.selected_icao:
        trace = st.session_state.history.get(st.session_state.selected_icao, [])
        if len(trace) > 1:
            layers.append(pdk.Layer(
                "PathLayer",
                data=[{"path": trace}],
                get_path="path",
                get_color="[255, 0, 255, 255]",
                get_width=8, # Aumentado para visibilidad
                capped=True
            ))

    # Capa de aviones activos
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_fill_color="fill_color",
        get_radius=15000,
        pickable=True,
        id="planes"
    ))

    view = pdk.ViewState(latitude=33, longitude=45, zoom=4, pitch=0)
    r = pdk.Deck(layers=layers, initial_view_state=view, map_style="light", tooltip={"text": "{callsign}\nPaís: {country}"})
    
    selection = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")
    
    if selection and selection.get("selection", {}).get("objects", {}).get("planes"):
        new_icao = selection["selection"]["objects"]["planes"][0]['icao24']
        if st.session_state.selected_icao != new_icao:
            st.session_state.selected_icao = new_icao
            st.rerun()

    if st.session_state.selected_icao:
        sel_row = df[df['icao24'] == st.session_state.selected_icao]
        if not sel_row.empty:
            st.success(f"🛰️ Seguimiento activo: {sel_row.iloc[0]['callsign']}")
            if st.button("❌ Dejar de seguir avión"): 
                st.session_state.selected_icao = None
                st.session_state.history = {} # Resetear historial al dejar de seguir
                st.rerun()
    
    st.markdown("---")
    st.subheader("📰 Últimas Noticias de Inteligencia")
    
    session = get_session()
    try:
        from sqlalchemy import desc
        articles = session.query(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(10).all()
        cols = st.columns(2)
        for i, art in enumerate(articles):
            with cols[i % 2]:
                with st.expander(f"{art.source} | {art.title[:60]}..."):
                    st.write(f"**Publicado:** {art.published_at}")
                    st.write(art.description or "Sin descripción")
                    st.link_button("Ver noticia completa", art.url)
    except Exception as e:
        st.error(f"Error cargando noticias: {e}")
    finally:
        session.close()

    st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("Esperando datos de radar... Pulsa 'Actualizar' en los controles superiores si es necesario.")
