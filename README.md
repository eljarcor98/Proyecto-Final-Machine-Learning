# 🌍 OSINT Intelligence System: Conflicto en Medio Oriente

Este proyecto implementa un sistema de inteligencia de fuentes abiertas (OSINT) diseñado para el monitoreo, análisis y visualización de la volatilidad geopolítica en el Medio Oriente. El sistema transforma datos no estructurados de noticias globales en conocimiento accionable mediante el uso de Procesamiento de Lenguaje Natural (NLP), geocodificación y monitoreo de tráfico aéreo en tiempo real.

## 🌐 Demo en Vivo
Puedes acceder a la aplicación desplegada aquí: [Proyecto Final ML Streamlit](https://proyecto-final-machine-learning-3dudtmegm7geepk7xs9l6i.streamlit.app/)

## 🚀 Características Principales

### 1. Centro de Comando (Dashboard)
Interfaz de usuario de alto impacto desarrollada en **Streamlit**, diseñada como un centro de control operativo:
- **📡 Radar Aéreo**: Monitoreo de tráfico y detección de anomalías en rutas aéreas críticas utilizando datos de OpenSky Network.
- **⏳ Timeline Geo-Temporal**: Visualización interactiva mediante `Pydeck` que mapea eventos críticos basados en la extracción de entidades geográficas.
- **📊 Análisis NLP**: Procesamiento de texto para reconocimiento de entidades nombradas (NER), minería de tópicos y nubes de palabras basadas en la frecuencia de términos.
- **UX/UI Avanzada**: Diseño minimalista con tipografía Montserrat, animaciones de transición y navegación optimizada.

### 2. Pipeline de Inteligencia (Backend)
Un sistema automatizado de recolección y procesamiento de datos:
- **Orquestador de Datos**: Script centralizado que gestiona la ingesta desde múltiples fuentes: **GNews API**, **Feeds RSS** y **GDELT Project**.
- **Traducción Automatizada**: Herramienta de traducción masiva para normalizar noticias en diferentes idiomas al español/inglés antes del análisis.
- **API de Servicios**: Backend basado en **Flask** que sirve las visualizaciones y datos procesados a través de plantillas HTML dinámicas.

### 3. Gestión de Datos
Soporte híbrido para almacenamiento y migración:
- **Bases de Datos**: Soporte nativo para **SQLite** (desarrollo local) y **PostgreSQL/Supabase** (producción).
- **Herramientas de Migración**: Scripts dedicados para migrar datos de SQLite a PostgreSQL, asegurando la persistencia de la inteligencia recolectada.

## 🛠️ Arquitectura Técnica

### Estructura del Proyecto
```text
proyecto-final-ml/
├── api/                # Backend Flask (API y Templates HTML)
├── dashboard/          # Interfaz Streamlit
│   └── pages/          # Módulos: Radar, Timeline, NLP
├── data/               # Almacenamiento de datos crudos (JSON/CSV)
├── scripts/            # Orquestador y recolectores de datos
├── src/                # Núcleo lógico (Configuración de DB, Modelos)
├── translate_all.py    # Herramienta de traducción de corpus
└── requirements.txt    # Dependencias del sistema
```

### Stack Tecnológico
- **Lenguaje**: Python 3.x
- **Frontend**: Streamlit, Pydeck, Plotly, Matplotlib
- **Backend**: Flask (API), SQLAlchemy
- **NLP**: spaCy, WordCloud, Regex
- **Base de Datos**: PostgreSQL (Supabase) / SQLite
- **APIs Externas**: GNews, OpenSky Network, GDELT

## 📖 Guía de Instalación y Ejecución

### 1. Instalación Local
```bash
# Clonar el repositorio
git clone https://github.com/eljarcor98/Proyecto-Final-Machine-Learning.git
cd "Proyecto final Machine Learning"

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de Variables de Env
Cree un archivo `.env` en la raíz del proyecto con las siguientes claves:
```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase
GNEWS_API_KEY=tu_api_key_de_gnews
```

### 3. Ejecución de Componentes

**A. Recolección de Datos (Orquestador):**
Para poblar la base de datos con noticias actuales:
```bash
python scripts/orchestrator.py
```

**B. Lanzamiento del Dashboard (Streamlit):**
```bash
streamlit run dashboard/app.py
```

**C. Lanzamiento de la API (Flask):**
```bash
python api/index.py
```

## 🎯 Objetivos del Proyecto
- **Detección de Patrones**: Identificar picos de tensión regional mediante la frecuencia de noticias y palabras clave.
- **Geolocalización de Conflictos**: Visualizar la concentración geográfica de eventos críticos en tiempo real.
- **Automatización OSINT**: Reducir el tiempo de análisis transformando miles de artículos en visualizaciones simplificadas.

---
*Desarrollado como Proyecto Final de Machine Learning.*