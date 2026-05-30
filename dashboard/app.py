import streamlit as st

# Page config
st.set_page_config(page_title="OSINT Intelligence System", layout="wide", page_icon="🛰️")

st.title("🛰️ Sistema de Inteligencia Multifuente (OSINT)")

st.markdown("""
## 🌍 Contexto del Conflicto: Irán – Israel – EE. UU.

Este sistema ha sido desarrollado para monitorear la tensión geopolítica en el Medio Oriente, enfocándose en el triángulo estratégico formado por **Irán**, **Israel** y **Estados Unidos**. La región se encuentra en un estado de volatilidad constante, donde el flujo de información en tiempo real es crítico para la comprensión de los movimientos tácticos y estratégicos.

### 🎯 Objetivos del Monitoreo
El propósito de esta herramienta es transformar datos públicos (Open Source Intelligence) en conocimiento accionable mediante:
1. **Vigilancia Aérea**: Monitoreo de tráfico en tiempo real para detectar anomalías en rutas de vuelo sobre zonas de conflicto.
2. **Análisis de Narrativas**: Extracción de tópicos y entidades geográficas desde noticias globales para mapear la evolución del conflicto.
3. **Sincronización Temporal**: Una línea de tiempo interactiva que permite visualizar dónde y cuándo se concentran las tensiones.

### 🛠️ Metodología
El sistema integra:
- **NLP (Procesamiento de Lenguaje Natural)**: Uso de modelos de `spaCy` para reconocimiento de entidades nombradas (NER).
- **Geocodificación**: Transformación de menciones textuales en coordenadas geográficas precisas.
- **Data Pipeline**: Recolección automatizada desde GNews, RSS y GDELT, almacenada en una base de datos PostgreSQL (Supabase).

---
**Navega a través del menú lateral para explorar el Radar Aéreo, la Línea de Tiempo o el Análisis de Datos.**
""")

st.info("� **Sugerencia**: Comienza por el 'Radar Aéreo' para ver la situación actual del espacio aéreo o el 'Timeline' para analizar la evolución histórica.")