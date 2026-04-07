#!/bin/bash
# setup.sh — Instalación automática para Linux/macOS
set -e

echo "============================================================"
echo "  Instalador: Análisis de Magnitudes Armónicas"
echo "============================================================"

# ── 1. Verificar Python 3.8+ ──────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado."
    echo "        Instálalo con: sudo apt install python3 python3-venv  (Ubuntu/Debian)"
    echo "                   o: brew install python  (macOS)"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]; }; then
    echo "[ERROR] Se requiere Python 3.8 o superior. Tienes: $PY_VER"
    exit 1
fi
echo "[OK] Python $PY_VER encontrado."

# ── 2. Crear entorno virtual ──────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "[INFO] Creando entorno virtual en .venv/ ..."
    python3 -m venv .venv
fi

# ── 3. Instalar dependencias ──────────────────────────────────────────────
echo "[INFO] Activando entorno e instalando dependencias..."
source .venv/bin/activate

pip install --upgrade pip --quiet
pip install setuptools --upgrade --quiet     # requerido para pip install -e .
pip install -r requirements.txt --quiet
pip install -e . --quiet                     # registra el comando math-analisis

# ── 4. Crear carpetas necesarias ──────────────────────────────────────────
mkdir -p data results

# ── 5. Verificación rápida ────────────────────────────────────────────────
echo "[INFO] Verificando instalación..."
python3 -c "import pandas, numpy, scipy, matplotlib, fpdf; print('[OK] Todas las dependencias verificadas.')"

echo ""
echo "============================================================"
echo "  INSTALACION COMPLETADA"
echo ""
echo "  Opciones para correr el análisis:"
echo ""
echo "  1. Activar el entorno y usar el comando global:"
echo "     source .venv/bin/activate"
echo "     math-analisis"
echo ""
echo "  2. Sin activar el entorno (desde cualquier carpeta):"
echo "     $SCRIPT_DIR/.venv/bin/math-analisis --data $SCRIPT_DIR/data"
echo ""
echo "  3. Con python directamente:"
echo "     python3 $SCRIPT_DIR/main.py"
echo ""
echo "  Coloca tus CSV en: $SCRIPT_DIR/data/"
echo "  Los resultados aparecen en: $SCRIPT_DIR/results/"
echo "============================================================"
