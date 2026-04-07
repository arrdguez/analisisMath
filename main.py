"""
main.py — Orquestador Global de Análisis de Magnitudes Armónicas
──────────────────────────────────────────────────────────────────────────────
Objetivo: Punto de entrada único para el pipeline. Detecta datos, valida 
integridad, corre análisis y genera reportes consolidados (MD y PDF).
"""

import os
import sys
import glob
import subprocess
import time
import argparse
from pathlib import Path

# Configuración de scripts en orden lógico
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

REPORT_SCRIPTS = [
    ("REPORTE: master", "generate_master_reports.py", "Generación de síntesis CSV y MD"),
    ("REPORTE: ia-ready", "generate_report.py", "Generación de reporte para IA"),
    ("REPORTE: pdf", "generate_pdf_report.py", "Generación de reporte PDF final"),
]

def check_data_integrity(data_dir):
    """Valida que los archivos en data/ sean realmente exportaciones de TradingView."""
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        return False, "No se encontraron archivos .csv en la carpeta de datos."

    valid_files = 0
    for f in csv_files:
        try:
            with open(f, 'r', encoding='utf-8', errors='replace') as file:
                header = file.readline().strip().lower()
                # TradingView exporta con 'Date,Message' o 'Time,Message' o 'Time;Message'
                has_date  = "date" in header or "time" in header
                has_msg   = "message" in header
                if has_date and has_msg:
                    valid_files += 1
        except:
            continue

    if valid_files == 0:
        return False, (
            "Los archivos CSV encontrados no parecen ser logs de TradingView.\n"
            "   Asegúrate de exportar desde Pine Script Debugger → Logs → Export logs\n"
            "   y guardar el .csv en la carpeta data/"
        )
    return True, f"Detectados {valid_files} archivo(s) válido(s) de TradingView."

def run_script(script_path, description, env=None):
    print(f"\n>> {description} ({os.path.basename(script_path)})...")
    start_time = time.time()
    try:
        # Aseguramos que el script se ejecute con el mismo intérprete
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
        )
        duration = time.time() - start_time
        print(f"[OK] Completado en {duration:.1f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] ejecutando {script_path}")
        if e.stderr:
            print(f"   {e.stderr.strip().splitlines()[-1]}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Pipeline de Análisis de Magnitudes Armónicas")
    parser.add_argument("--data", type=str, default="data", help="Carpeta con CSVs crudos")
    parser.add_argument("--out", type=str, default="results", help="Carpeta para resultados")
    parser.add_argument("--steps", nargs="+", help="Pasos específicos a correr (ej: parse fft)")
    parser.add_argument("--no-pdf", action="store_true", help="Saltar generación de PDF")
    
    args = parser.parse_args()

    # Preparar entorno
    base_path = Path(__file__).parent.absolute()
    data_path = Path(args.data).absolute()
    results_path = Path(args.out).absolute()
    results_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  ANALISIS ESTRUCTURAL DE SERIES TEMPORALES (Global CLI)")
    print(f"  Datos: {data_path}")
    print(f"  Resultados: {results_path}")
    print("=" * 60)

    # Paso 0: Integridad
    ok, msg = check_data_integrity(data_path)
    if not ok:
        print(f"[ERROR] Integridad de datos: {msg}")
        return
    print(f"[INFO] {msg}")

    # Entorno para scripts (pasar rutas si los scripts las aceptaran, 
    # por ahora emulamos el directorio de trabajo si es necesario)
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"

    # Ejecución de análisis
    for label, script_name, desc in SCRIPTS:
        step_key = label.split(":")[1].strip()
        if args.steps and step_key not in args.steps:
            continue
            
        script_full_path = base_path / script_name
        if not run_script(str(script_full_path), label, env=env):
            print(f"[!] Fallo en {label}, continuando...")

    # Ejecución de reportes
    print("\n" + "-" * 60)
    print("  GENERANDO REPORTES FINALES")
    print("-" * 60)
    
    for label, script_name, desc in REPORT_SCRIPTS:
        if "pdf" in script_name and args.no_pdf:
            continue
            
        script_full_path = base_path / script_name
        run_script(str(script_full_path), label, env=env)

    print("\n" + "=" * 60)
    print("  PROCESO COMPLETADO")
    print(f"  Resultados finales en: {results_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
