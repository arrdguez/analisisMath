@echo off
chcp 65001 >nul
:: setup.bat — Instalación automática para Windows

echo ============================================================
echo   Instalador: Analisis de Magnitudes Armonicas (Windows)
echo ============================================================

:: ── 1. Verificar Python ──────────────────────────────────────────────────
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo         Descargalo desde: https://www.python.org/downloads/
    echo         Marca la opcion "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

python -c "import sys; assert sys.version_info >= (3,8), 'VERSION'" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Se requiere Python 3.8 o superior.
    python --version
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"') do set PY_VER=%%v
echo [OK] Python %PY_VER% encontrado.

:: ── 2. Entorno virtual ───────────────────────────────────────────────────
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist .venv (
    echo [INFO] Creando entorno virtual en .venv\ ...
    python -m venv .venv
)

:: ── 3. Instalar dependencias ─────────────────────────────────────────────
echo [INFO] Activando entorno e instalando dependencias...
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip --quiet
python -m pip install setuptools --upgrade --quiet
python -m pip install -r requirements.txt --quiet
python -m pip install -e . --quiet

:: ── 4. Crear carpetas necesarias ─────────────────────────────────────────
if not exist data mkdir data
if not exist results mkdir results

:: ── 5. Verificación rápida ───────────────────────────────────────────────
echo [INFO] Verificando instalacion...
python -c "import pandas, numpy, scipy, matplotlib, fpdf; print('[OK] Todas las dependencias verificadas.')"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la verificacion de dependencias.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   INSTALACION COMPLETADA
echo.
echo   Opciones para correr el analisis:
echo.
echo   1. Doble clic en este archivo setup.bat (ya lo hiciste)
echo      Luego ejecuta desde esta carpeta:
echo        .venv\Scripts\activate.bat
echo        math-analisis
echo.
echo   2. Sin activar el entorno (una sola linea):
echo        .venv\Scripts\math-analisis.exe
echo.
echo   3. Con python directamente:
echo        python main.py
echo.
echo   Coloca tus CSV en: %SCRIPT_DIR%data\
echo   Los resultados aparecen en: %SCRIPT_DIR%results\
echo ============================================================
pause
