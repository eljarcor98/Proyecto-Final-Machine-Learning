# 🌍 OSINT Intelligence System: Conflicto en Medio Oriente

Este proyecto implementa un sistema de inteligencia de fuentes abiertas (OSINT) diseñado para el monitoreo, análisis y visualización de la volatilidad geopolítica en el Medio Oriente. El sistema transforma datos no estructurados de noticias globales en conocimiento accionable mediante el uso de Procesamiento de Lenguaje Natural (NLP) y geocodificación.

## 🚀 Características Principales

### 1. Centro de Comando (Dashboard)
Interfaz de usuario desarrollada en **Streamlit** con un diseño optimizado de "Centro de Control". Incluye:
- **Navegación Intuitiva**: Acceso rápido a módulos especializados.
- **Experiencia de Usuario (UX)**: Implementación de efectos de transición (vanish/fade-in) y tipografía moderna (Montserrat).
- **Diseño Limpio**: Interfaz minimalista enfocada en la visualización de datos.

### 2. Módulos de Análisis
- **📡 Radar Aéreo**: Monitoreo de tráfico y detección de anomalías en rutas aéreas críticas de la región.
- **⏳ Timeline Geo-Temporal**: Visualización interactiva mediante `Pydeck`. Mapea eventos críticos basándose en la extracción de entidades geográficas, permitiendo analizar la evolución del conflicto en el tiempo.
- **📊 Análisis NLP**: Implementación de modelos de `spaCy` para el Reconocimiento de Entidades Nombradas (NER), minería de tópicos y análisis de frecuencias textuales.

## 🛠️ Arquitectura Técnica

### Pipeline de Datos
`GNews API` $\rightarrow$ `Python Processing` $\rightarrow$ `PostgreSQL (Supabase)` $\rightarrow$ `Streamlit Dashboard`

### Stack Tecnológico
- **Lenguaje**: Python 3.x
- **Frontend**: Streamlit
- **Base de Datos**: PostgreSQL (Supabase)
- **NLP**: spaCy (Modelos de reconocimiento de entidades)
- **Visualización**: Pydeck, Pandas, Matplotlib
- **Despliegue**: Vercel (vía GitHub)

## 📖 Guía de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/usuario/proyecto-final-ml.git
   cd "Proyecto final Machine Learning"
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   Cree un archivo `.env` con las credenciales de Supabase y APIs necesarias.

4. **Ejecutar el sistema**:
   ```bash
   streamlit run dashboard/app.py
   ```

## 🎯 Objetivos del Proyecto
- Detectar patrones de tensión regional mediante la frecuencia de noticias.
- Visualizar la concentración geográfica de eventos críticos.
- Automatizar la extracción de actores clave y localidades involucradas en el conflicto.

---
*Desarrollado como Proyecto Final de Machine Learning.*