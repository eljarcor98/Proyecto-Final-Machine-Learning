import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import sys
import json
from datetime import datetime

# Ajustar ruta para importar desde src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.db import get_session, NewsArticle, NewsAnalysis

# Diccionario de coordenadas generales para ciudades comunes del conflicto
CITY_COORDINATES = {
    "Kyiv": [30.5234, 50.4501],
    "Kiev": [30.5234, 50.4501],
    "Moscow": [37.6173, 55.7558],
    "Moscú": [37.6173, 55.7558],
    "Donetsk": [37.8000, 48.1100],
    "Luhansk": [39.1667, 48.5833],
    "Kharkiv": [36.2304, 50.0000],
    "Kharkov": [36.2304, 50.0000],
    "Mariupol": [37.5000, 47.1100],
    "Crimea": [34.0000, 45.0000],
    "Ukraine": [31.1656, 48.3794],
    "Russia": [105.3188, 61.5240],
    "USA": [-100.0000, 37.0000],
    "UK": [-3.4360, 55.3781],
    "EU": [15.0000, 50.0000]
}

st.set_page_config(page_title="Timeline del Conflicto", layout="wide", page_icon="⏳")

st.title("⏳ Línea de Tiempo del Conflicto")
st.markdown("Visualización geo-temporal de eventos críticos y noticias relacionadas.")

# --- Carga de Datos ---
@st.cache_data(ttl=600)
def load_timeline_data():
    session = get_session()
    try:
        # Join entre NewsArticle y NewsAnalysis para obtener las localidades extraídas por NLP
        query = session.query(NewsArticle, NewsAnalysis).join(
            NewsAnalysis, NewsArticle.id == NewsAnalysis.article_id
        )
        results = query.all()
        
        data = []
        for art, analysis in results:
            # Intentar extraer coordenadas de la lista de localidades en NewsAnalysis
            locations_list = []
            try:
                if analysis.locations:
                    locations_list = json.loads(analysis.locations)
            except:
                locations_list = []

            # Buscar si alguna localidad coincide con nuestro diccionario de coordenadas
            found_coord = None
            for loc in locations_list:
                # Comparación simple: si la ciudad está en el diccionario (ignorando mayúsculas/minúsculas)
                for city, coords in CITY_COORDINATES.items():
                    if city.lower() in loc.lower():
                        found_coord = coords
                        break
                if found_coord: break

            if found_coord:
                data.append({
                    "id": art.id,
                    "title": art.title,
                    "description": art.description,
                    "url": art.url,
                    "source": art.source,
                    "published_at": art.published_at,
                    "lon": found_coord[0],
                    "lat": found_coord[1]
                })
        
        return pd.DataFrame(data)
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

    # --- UI: Filtro Temporal ---
    st.sidebar.header("📅 Filtro Temporal")
    selected_date = st.sidebar.slider(
        "Seleccione la fecha de corte", 
        min_value=min_date.date(), 
        max_value=max_date.date(), 
        value=max_date.date()
    )

    # Filtrar datos según fecha
    filtered_df = df[df['published_at'].dt.date <= selected_date]

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

    view = pdk.ViewState(latitude=32, longitude=45, zoom=3, pitch=0)
    r = pdk.Deck(
        layers=[layer], 
        initial_view_state=view, 
        map_style="dark", 
        tooltip={"text": "{title}\nFuente: {source}"}
    )

    # Renderizado con captura de selección
    selection = st.pydeck_chart(r, on_select="rerun", selection_mode="single-object")

    # --- Implementación de Resumen Interactivo ---
    if selection and selection.get("selection", {}).get("objects", {}).get("news_points"):
        # Obtener la información del objeto seleccionado
        selected_point = selection["selection"]["objects"]["news_points"][0]
        art_id = selected_point.get('id')
        
        # Buscar el artículo en el DataFrame
        if art_id is not None:
            art_info = filtered_df[filtered_df['id'] == art_id].iloc[0]
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("📄 Resumen del Evento")
            st.sidebar.markdown(f"**{art_info['title']}**")
            st.sidebar.caption(f"Fuente: {art_info['source']} | Fecha: {art_info['published_at'].strftime('%Y-%m-%d')}")
            st.sidebar.write(art_info['description'] or "Sin descripción disponible.")
            st.sidebar.link_button("Leer artículo completo", art_info['url'])
    else:
        st.sidebar.info("Haz clic en un punto rojo del mapa para ver el resumen de la noticia.")

    # --- Tabla de Eventos Recientes ---
    st.markdown("---")
    st.subheader("📝 Listado de Eventos hasta la Fecha Seleccionada")
    st.dataframe(
        filtered_df[['published_at', 'title', 'source']].sort_values('published_at', ascending=False),
        use_container_width=True
    )

else:
    st.warning("No se encontraron datos geocodificados para generar la línea de tiempo.")