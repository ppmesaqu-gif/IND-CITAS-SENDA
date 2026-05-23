@echo off
title Control de Recepcion — Planta Entrerrios

:: Buscar Python (3.9 a 3.13)
set PYTHON=
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if "%PYTHON%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if "%PYTHON%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
if "%PYTHON%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set PYTHON=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
if "%PYTHON%"=="" if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"  set PYTHON=%LOCALAPPDATA%\Programs\Python\Python39\python.exe
if "%PYTHON%"=="" where python >nul 2>&1 && set PYTHON=python
if "%PYTHON%"=="" (
    echo ERROR: Python no encontrado. Instale desde https://www.python.org
    pause & exit /b 1
)

:: Instalar dependencias si faltan (incluye lxml y numpy requeridos por pptx_generador)
%PYTHON% -c "import pandas,openpyxl,pptx,matplotlib,PIL,lxml,numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias (solo la primera vez)...
    %PYTHON% -m pip install pandas openpyxl python-pptx matplotlib pillow lxml numpy --quiet
)

:: Lanzar app sin mostrar consola (pythonw)
cd /d "%~dp0"
set PYTHONW=%PYTHON:python.exe=pythonw.exe%
if exist "%PYTHONW%" (
    start "" "%PYTHONW%" generar_informe.py
) else (
    start "" "%PYTHON%" generar_informe.py
)
