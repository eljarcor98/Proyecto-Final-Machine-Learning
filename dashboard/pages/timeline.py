import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import sys
import json
from datetime import datetime
from deep_translator import GoogleTranslator

# Ajustar ruta para importar desde src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle, NewsAnalysis, init_db

# Asegurar que la base de datos esté inicializada
init_db()

# Diccionario de coordenadas generales para ciudades comunes del conflicto en Medio Oriente
CITY_COORDINATES = {
    "Gaza": [34.4500, 31.5000],
    "Gaza City": [34.4500, 31.5000],
    "Israel": [34.8516, 31.0461],
    "Tel Aviv": [34.7818, 32.0853],
    "Jerusalem": [35.2137, 31.7683],
    "Hebron": [34.9700, 34.7700],
    "Beirut": [33.8688, 33.8938],
    "Lebanon": [33.8885, 35.8623],
    "Tehran": [51.3892, 35.6892],
    "Iran": [53.6880, 32.4279],
    "Sana'a": [44.1910, 15.3694],
    "Yemen": [48.5164, 15.5527],
    "Damascus": [36.2913, 33.5138],
    "Syria": [38.9972, 34.8113],
    "Baghdad": [44.3611, 33.3152],
    "Iraq": [44.2125, 33.2252],
    "Riyadh": [46.6753, 24.6303],
    "Saudi Arabia": [45.0769, 23.8859],
    "Jordan": [36.2384, 31.2565],
    "Amman": [35.9285, 31.9454],
    "USA": [-100.0000, 37.0000],
    "UK": [-3.4360, 55.3781]
}

st.set_page_config(page_title="Timeline del Conflicto", layout="wide", page_icon="⏳")

# Global CSS for consistency and hiding sidebar
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Montserrat', sans-serif !important; }
    .stApp { animation: vanishIn 0.6s ease-out; }
    @keyframes vanishIn { 0% { opacity: 0; transform: scale(0.98); } 100% { opacity: 1; transform: scale(1); } }
    /* Ocultar Sidebar y Navegación de forma agresiva */
    [data-testid="stSidebar"], 
    section[data-testid="stSidebar"], 
    [data-testid="stSidebarCollapseButton"], 
    div[data-testid="stSidebarNav"],
    .st-emotion-cache-165sq2v, /* Posible selector de contenedor sidebar */
    [data-testid="stSidebarNav"] { 
        display: none !important; 
        visibility: hidden !important;
    }
    /* Forzar que el contenedor principal ocupe todo el ancho */
    .main .block-container {
        padding-left: 5rem;
        padding-right: 5rem;
    }
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

st.title("⏳ Timeline: Conflicto Medio Oriente")
st.markdown("Visualización geo-temporal de eventos críticos y noticias relacionadas con la inestabilidad regional.")

# --- Carga de Datos ---
@st.cache_data(ttl=600)
def load_timeline_data():
    session = get_session()
    try:
        # Intentamos primero el join con análisis NLP, pero mantenemos fallback al texto bruto
        articles = session.query(NewsArticle).all()
        
        # Obtenemos los análisis para evitar múltiples queries en el loop
        analysis_map = {a.article_id: a for a in session.query(NewsAnalysis).all()}
        
        data = []
        for art in articles:
            found_coord = None
            
            # 1. Intentar extraer de NewsAnalysis (si existe)
            analysis = analysis_map.get(art.id)
            if analysis and analysis.locations:
                try:
                    locations_list = json.loads(analysis.locations)
                    for loc in locations_list:
                        for city, coords in CITY_COORDINATES.items():
                            if city.lower() in loc.lower():
                                found_coord = coords
                                break
                        if found_coord: break
                except:
                    pass

            # 2. Fallback: Buscar palabras clave directamente en el título y descripción
            if not found_coord:
                full_text = f"{art.title} {art.description}".lower()
                for city, coords in CITY_COORDINATES.items():
                    if city.lower() in full_text:
                        found_coord = coords
                        break

            if found_coord:
                title_es = getattr(art, 'title_es', None)
                desc_es = getattr(art, 'description_es', None)

                data.append({
                    "id": art.id,
                    "title": title_es or art.title,
                    "description": desc_es or art.description,
                    "url": art.url,
                    "source": art.source,
                    "published_at": art.published_at,
                    "lon": found_coord[0],
                    "lat": found_coord[1]
                })

        df_res = pd.DataFrame(data)
        return df_res
    except Exception as e:
        st.error(f"Error al cargar datos de la línea de tiempo: {e}")
        return pd.DataFrame()
    finally:
        session.close()

df = load_timeline_data()

if not df.empty:
    # Convertir fechas a datetime
    df['published_at'] = pd.to_datetime(df['published_at'])
    min_date = df['published_at'].min()
    max_date = df['published_at'].max()

    # --- UI: Filtro Temporal (Rango de Fechas) ---
    st.markdown("### 📅 Filtro de Periodo Temporal")
    col_date, col_info = st.columns([3, 1])
    with col_date:
        # Slider de rango para acotar fechas de inicio y fin
        selected_range = st.slider(
            "Seleccione el periodo de tiempo para analizar la evolución de los eventos", 
            min_value=min_date.date(), 
            max_value=max_date.date(), 
            value=(min_date.date(), max_date.date())
        )
    
    # Filtrar datos según el rango seleccionado
    start_date, end_date = selected_range
    filtered_df = df[(df['published_at'].dt.date >= start_date) & 
                    (df['published_at'].dt.date <= end_date)].copy()

    with col_info:
        st.metric("Eventos en Periodo", len(filtered_df))

    # --- Mapa Interactivo ---
    # Capa de puntos
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position="[lon, lat]",
        get_color="[255, 0, 0, 160]",
        get_radius=100000, # 100km
        pickable=True,
        id="news_points"
    )

    view = pdk.ViewState(latitude=32.5, longitude=35.0, zoom=4, pitch=0)
    r = pdk.Deck(
        layers=[layer], 
        initial_view_state=view, 
        map_style="dark", 
        tooltip={"text": "{title}\nFuente: {source}"}
    )

    # Renderizado con captura de selección
    selection = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")

    # --- Implementación de Resumen Interactivo (Moved to Main) ---
    if selection and selection.get("selection", {}).get("objects", {}).get("news_points"):
        # Obtener la información del objeto seleccionado
        selected_point = selection["selection"]["objects"]["news_points"][0]
        art_id = selected_point.get('id')
        
        # Buscar el artículo en el DataFrame
        if art_id is not None:
            art_info = filtered_df[filtered_df['id'] == art_id].iloc[0]
            
            with st.expander("📄 Detalle del Evento Seleccionado", expanded=True):
                st.markdown(f"#### {art_info['title']}")
                st.caption(f"Fuente: {art_info['source']} | Fecha: {art_info['published_at'].strftime('%Y-%m-%d')}")
                st.write(art_info['description'] or "Sin descripción disponible.")
                st.link_button("Leer artículo completo", art_info['url'])
    else:
        st.info("💡 Haz clic en un punto rojo del mapa para ver el resumen de la noticia.")

    # --- Tabla de Eventos Recientes ---
    st.markdown("---")
    st.subheader("📝 Listado de Eventos hasta la Fecha Seleccionada")
    st.dataframe(
        filtered_df[['published_at', 'title', 'source']].sort_values('published_at', ascending=False),
        width='stretch'
    )

else:
    st.warning("No se encontraron datos geocodificados para generar la línea de tiempo.")