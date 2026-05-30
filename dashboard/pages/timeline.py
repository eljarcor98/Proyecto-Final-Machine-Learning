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

st.title("⏳ Timeline: Conflicto Medio Oriente")
st.markdown("Visualización geo-temporal de eventos críticos y noticias relacionadas con la inestabilidad regional.")

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

    view = pdk.ViewState(latitude=32.5, longitude=35.0, zoom=4, pitch=0)
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