"""
main.py — Orquestador del Análisis de Series Temporales (Agnóstico)
──────────────────────────────────────────────────────────────────────────────
Objetivo: Analizar cualquier archivo CSV de la carpeta data/ sin sesgos
de nombre de activo o temporalidad. El sistema auto-descubre y procesa.
"""

import os
import sys
import glob
import subprocess
import time
import io

# Forzar codificación UTF-8 para evitar errores en consola Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
RESULTS_DIR = os.path.join(BASE, "results")

# Listado de scripts de análisis en orden lógico
SCRIPTS = [
    ("PASO 1: parse_csv", "parse_csv.py", "Limpieza y normalización de datos"),
    ("PASO 2: explore", "explore.py", "Análisis exploratorio visual y estadístico"),
    ("PASO 3: fft", "fft_analysis.py", "Análisis de ciclos y frecuencias (FFT)"),
    ("PASO 4: hurst", "hurst.py", "Análisis de memoria y persistencia"),
    ("PASO 5: hilbert", "hilbert_analysis.py", "Análisis de envolvente y fase"),
    ("PASO 6: fibonacci", "fibonacci_analysis.py", "Relaciones de tiempo y amplitud"),
    ("PASO 7: apoyo", "apoyo_stats.py", "Estadísticas de rebotes y profundidades"),
    ("PASO 8: correlation", "correlation_analysis.py", "Correlación entre distancias"),
    ("PASO 9: scale", "scale_analysis.py", "Relaciones de escala armónica"),
    ("PASO 10: contact", "contact_dynamics_analysis.py", "Dinámica de contacto cinemática"),
    ("PASO 11: comparison", "timeframe_comparison.py", "Comparativa estructural consolidada"),
]

def run_script(script_name, description):
    print(f"\n>> {description} ({script_name})...")
    start_time = time.time()
    # Propagar PYTHONUTF8=1 para que los hijos no fallen con emojis en Windows
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
        )
        duration = time.time() - start_time
        print(f"[OK] Completado en {duration:.1f}s")
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines[-3:]:
            print(f"   {line}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ejecutando {script_name}")
        if e.stderr:
            for line in e.stderr.strip().split('\n')[-5:]:
                print(f"   {line}")
    except Exception as e:
        print(f"[ERROR] inesperado: {e}")

def main():
    print("=" * 60)
    print("  ANALISIS ESTRUCTURAL DE SERIES TEMPORALES")
    print("  Modo: AGNOSTICO (Blind Analysis)")
    print("=" * 60)

    run_script("parse_csv.py", "PASO 1: parse_csv")

    clean_files = glob.glob(os.path.join(RESULTS_DIR, "*_clean.csv"))
    if not clean_files:
        print("[ERROR] No se generaron archivos limpios. Revisa la carpeta data/.")
        return

    print(f"\n[INFO] Detectados {len(clean_files)} conjuntos de datos para analizar.")

    for i in range(1, len(SCRIPTS)):
        label, name, desc = SCRIPTS[i]
        run_script(name, label)

    print("\n" + "=" * 60)
    print("  PROCESO COMPLETADO")
    print(f"  Resultados en: {RESULTS_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
