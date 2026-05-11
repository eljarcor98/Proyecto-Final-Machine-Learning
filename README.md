# Proyecto Final ML1: Sistema de Inteligencia Multifuente

## Propósito
Este proyecto busca construir un sistema de inteligencia multifuente (OSINT) alrededor de la escalada del conflicto **Irán–Israel–EE. UU.**, utilizando exclusivamente fuentes gratuitas y públicas.

## Estructura del Repositorio
- `data/`:
    - `raw/`: Datos originales obtenidos de APIs o web scraping.
    - `processed/`: Datasets limpios e integrados.
- `notebooks/`: Análisis exploratorio (EDA) y experimentación con modelos.
- `src/`: Código fuente modular (limpieza, ingeniería de variables, pipelines).
- `scripts/`: Scripts de orquestación para la recolección y procesamiento.
- `models/`: Artefactos de modelos entrenados.
- `dashboard/`: Código de la aplicación web desplegada.

## Alcance Mínimo
- Entre 3 y 5 fuentes (1 textual, 1 estructurada, 1 de contexto).
- Unidad de análisis definida.
- Comparación de al menos 3 modelos.
- Dashboard interactivo desplegado.

## Instalación
```bash
pip install -r requirements.txt
```

## Docente
Julián Zuluaga — Universidad Externado de Colombia
