import streamlit as st
import pandas as pd
import pydeck as pdk
import airportsdata
import os
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(page_title="Radar OSINT", layout="wide")

# Autorefresh cada 10 segundos
st_autorefresh(interval=10000, key="radar_refresh")

st.title("🛰️ Radar de Inteligencia Aérea")

# --- Session State ---
if 'history' not in st.session_state:
    st.session_state.history = {}
if 'selected_icao' not in st.session_state:
    st.session_state.selected_icao = None

# --- Data ---
@st.cache_resource
def load_airport_data():
    return airportsdata.load('IATA')

airports_db = load_airport_data()

def update_data():
    # Solo intentamos actualizar si ha pasado suficiente tiempo o manualmente
    os.system("python scripts/fetch_opensky_data.py")

def load_data():
    data_dir = 'data/raw'
    files = [f for f in os.listdir(data_dir) if f.startswith('opensky_states_')]
    if not files: return pd.DataFrame()
    latest = sorted(files, reverse=True)[0]
    try:
        with open(os.path.join(data_dir, latest), 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data, columns=['icao24', 'callsign', 'country', 'time', 'contact', 'lon', 'lat', 'alt', 'ground', 'vel', 'track', 'vert', 'sensors', 'geo_alt', 'squawk', 'spi', 'pos_src'])
    except:
        return pd.DataFrame()

update_data()
df = load_data()

if not df.empty:
    # Update History
    for _, row in df.iterrows():
        icao = row['icao24']
        if icao not in st.session_state.history: st.session_state.history[icao] = []
        pos = [row['lon'], row['lat']]
        if not st.session_state.history[icao] or st.session_state.history[icao][-1] != pos:
            st.session_state.history[icao].append(pos)
            if len(st.session_state.history[icao]) > 30: st.session_state.history[icao].pop(0)

    # Pre-calculate colors in Python to avoid Pydeck expression errors
    def get_color(icao):
        if icao == st.session_state.selected_icao:
            return [255, 0, 255, 255] # Magenta
        return [0, 128, 255, 200]    # Azul

    df['fill_color'] = df['icao24'].apply(get_color)

    # Prepare Layers
    layers = []

    # 1. Airports
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_color="[200, 200, 200, 30]",
        get_radius=5000,
    ))

    # 2. Trace
    if st.session_state.selected_icao:
        trace = st.session_state.history.get(st.session_state.selected_icao, [])
        if len(trace) > 1:
            layers.append(pdk.Layer(
                "PathLayer",
                data=[{"path": trace}],
                get_path="path",
                get_color="[255, 0, 255, 255]",
                get_width=5,
            ))

    # 3. Aircrafts
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_fill_color="fill_color", # Usamos la columna pre-calculada
        get_radius=15000,
        pickable=True,
        id="planes"
    ))

    # Render
    view = pdk.ViewState(latitude=33, longitude=45, zoom=4, pitch=0)
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style="light",
        tooltip={"text": "{callsign}\nPaís: {country}"}
    )
    
    # Catch Selection
    selection = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")
    
    if selection and selection.get("selection", {}).get("objects", {}).get("planes"):
        new_icao = selection["selection"]["objects"]["planes"][0]['icao24']
        if st.session_state.selected_icao != new_icao:
            st.session_state.selected_icao = new_icao
            st.rerun()

    # Panel
    if st.session_state.selected_icao:
        sel_row = df[df['icao24'] == st.session_state.selected_icao]
        if not sel_row.empty:
            st.sidebar.success(f"Seguimiento: {sel_row.iloc[0]['callsign']}")
            if st.sidebar.button("❌ Dejar de seguir"): 
                st.session_state.selected_icao = None
                st.rerun()
    
    st.sidebar.caption(f"Radar Activo: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("Cargando señales de radar...")
