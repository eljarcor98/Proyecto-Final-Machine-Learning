@echo off
title OSINT Intelligence Agent
echo ==========================================
echo    SISTEMA DE INTELIGENCIA OSINT
echo ==========================================
echo.

:: Detectar Python (Prioridad al entorno virtual .venv)
set PYTHON_EXE=py
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=".venv\Scripts\python.exe"
    echo [INFO] Usando entorno virtual detectado.
)

:: 1. Iniciar PostgreSQL
echo [1/3] Iniciando Base de Datos (PostgreSQL)...
set PG_BIN="f:\Repositorios Machine Learning\Proyecto final Machine Learning\pgsql\bin\pg_ctl.exe"
set PG_DATA="f:\Repositorios Machine Learning\Proyecto final Machine Learning\postgres_data"

%PG_BIN% -D %PG_DATA% start
timeout /t 5

:: 2. Iniciar el Orquestador
echo.
echo [2/3] Iniciando Orquestador (Captura de datos)...
start /min "OSINT Orchestrator" %PYTHON_EXE% scripts/orchestrator.py

:: 3. Iniciar el Dashboard
echo.
echo [3/3] Iniciando Dashboard (Visualizacion)...
echo.
%PYTHON_EXE% -m streamlit run dashboard/app.py

pause
