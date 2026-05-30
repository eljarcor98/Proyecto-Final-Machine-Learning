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
from src.db import get_session, NewsArticle

st.set_page_config(page_title="Radar Aéreo OSINT", layout="wide", page_icon="🛰️")

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
        # Ejecutamos el script de recolección
        os.system("py scripts/fetch_opensky_data.py")
    st.success("Radar actualizado")

# Sidebar: Control y Estado
st.sidebar.title("🎮 Controles")
if st.sidebar.button("🔄 Actualizar Radar Ahora"):
    update_data_manual()

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Estado del Orquestador")
st.sidebar.info("El orquestador automatiza GNews, RSS y GDELT.")
st.sidebar.caption("Sugerencia: Ejecuta `py scripts/orchestrator.py` en tu servidor para automatización total.")

def load_data():
    data_dir = 'data/raw'
    if not os.path.exists(data_dir):
        return pd.DataFrame()
    files = [f for f in os.listdir(data_dir) if f.startswith('opensky_states_')]
    if not files: return pd.DataFrame()
    latest = sorted(files, reverse=True)[0]
    try:
        with open(os.path.join(data_dir, latest), 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data, columns=['icao24', 'callsign', 'country', 'time', 'contact', 'lon', 'lat', 'alt', 'ground', 'vel', 'track', 'vert', 'sensors', 'geo_alt', 'squawk', 'spi', 'pos_src'])
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Actualización de Historial para Rutas
    for _, row in df.iterrows():
        icao = row['icao24']
        if icao not in st.session_state.history: 
            st.session_state.history[icao] = []
        pos = [row['lon'], row['lat']]
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

    df['fill_color'] = df['icao24'].apply(get_color)

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
            st.sidebar.success(f"Seguimiento: {sel_row.iloc[0]['callsign']}")
            if st.sidebar.button("❌ Dejar de seguir"): 
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

    st.sidebar.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("Esperando datos de radar... Pulsa 'Actualizar' en la barra lateral si es necesario.")