"""
generate_master_reports.py — Compilador Maestro de Resultados
─────────────────────────────────────────────────────────────────────────────
Genera tres entregables:
1. REPORTE_A_POR_ARCHIVO.md (Estructura por Activo)
2. REPORTE_B_POR_ESTUDIO.md (Estructura por Técnica)
3. SINTESIS_MAESTRA_DATOS.csv (Tabla plana de métricas)
"""

import os
import glob
import re
import pandas as pd

# ── Configuración ─────────────────────────────────────────────────────────────
RESULTS_DIR = 'results/'
CONTACT_DIR = 'results/contact_dynamics/'
OUTPUT_A = 'REPORTE_A_POR_ARCHIVO.md'
OUTPUT_B = 'REPORTE_B_POR_ESTUDIO.md'
OUTPUT_CSV = 'SINTESIS_MAESTRA_DATOS.csv'

# Mapeo de estudios y sus sufijos de archivo
STUDIES = {
    'Exploracion': '_explore_stats.txt',
    'FFT': '_fft_ciclos.txt',
    'Hurst': '_hurst_valores.txt',
    'Hilbert': '_hilbert_resumen.txt',
    'Fibonacci': '_fibonacci_stats.txt',
    'Apoyo': '_apoyo_stats.txt',
    'Correlacion': '_correlation_stats.txt',
    'Escala': '_scale_table.txt',
    'ValidacionEscala': '_scale_validation.txt'
}

def get_base_ids():
    """Identifica los IDs de activos basados en los archivos _clean.csv."""
    files = glob.glob(os.path.join(RESULTS_DIR, '*_clean.csv'))
    return sorted([os.path.basename(f).replace('_clean.csv', '') for f in files])

def extract_metric(text, pattern, group_idx=1):
    """Extrae un valor numérico de un bloque de texto usando regex."""
    match = re.search(pattern, text)
    if match:
        try:
            return match.group(group_idx).replace('%', '').strip()
        except:
            return None
    return None

def generate_report_a(ids):
    """Genera el reporte estructurado por Activo (Capítulos)."""
    print(f"📄 Generando {OUTPUT_A}...")
    with open(OUTPUT_A, 'w', encoding='utf-8') as f:
        f.write("# 📚 REPORTE MAESTRO: ANÁLISIS POR ACTIVO\n\n")
        for asset_id in ids:
            f.write(f"\n# CAPÍTULO: {asset_id}\n")
            f.write("=" * 60 + "\n")
            
            for study_name, suffix in STUDIES.items():
                file_path = os.path.join(RESULTS_DIR, f"{asset_id}{suffix}")
                if os.path.exists(file_path):
                    f.write(f"\n## Estudio: {study_name}\n")
                    with open(file_path, 'r', encoding='utf-8') as sf:
                        f.write("```text\n")
                        f.write(sf.read())
                        f.write("\n```\n")
                else:
                    f.write(f"\n## Estudio: {study_name} [SIN DATOS]\n")

def generate_report_b(ids):
    """Genera el reporte estructurado por Técnica (Capítulos)."""
    print(f"📄 Generando {OUTPUT_B}...")
    with open(OUTPUT_B, 'w', encoding='utf-8') as f:
        f.write("# 🔬 REPORTE MAESTRO: ANÁLISIS POR TÉCNICA\n\n")
        for study_name, suffix in STUDIES.items():
            f.write(f"\n# TÉCNICA: {study_name}\n")
            f.write("=" * 60 + "\n")
            
            for asset_id in ids:
                file_path = os.path.join(RESULTS_DIR, f"{asset_id}{suffix}")
                if os.path.exists(file_path):
                    f.write(f"\n## Archivo: {asset_id}\n")
                    with open(file_path, 'r', encoding='utf-8') as sf:
                        f.write("```text\n")
                        f.write(sf.read())
                        f.write("\n```\n")

def generate_synthesis_csv(ids):
    """Extrae métricas clave y genera CSV."""
    print(f"📊 Generando {OUTPUT_CSV}...")
    data = []
    
    for aid in ids:
        row = {'Archivo': aid}
        
        # 1. Hurst (dist_p55)
        hurst_path = os.path.join(RESULTS_DIR, f"{aid}_hurst_valores.txt")
        if os.path.exists(hurst_path):
            with open(hurst_path, 'r', encoding='utf-8') as f:
                content = f.read()
                row['Hurst_p55'] = extract_metric(content, r'dist_p55:\s+H=([\d\.]+)')
        
        # 2. FFT Ciclo 1 (dist_p55)
        fft_path = os.path.join(RESULTS_DIR, f"{aid}_fft_ciclos.txt")
        if os.path.exists(fft_path):
            with open(fft_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Buscar el bloque dist_p55 y luego el primer ciclo
                p55_block = re.search(r'dist_p55:(.*?)dist_', content, re.DOTALL)
                if p55_block:
                    row['FFT_Ciclo1'] = extract_metric(p55_block.group(1), r'#1\s+([\d\.]+)\s+velas')

        # 3. Hilbert Periodo (dist_p55)
        hilbert_path = os.path.join(RESULTS_DIR, f"{aid}_hilbert_resumen.txt")
        if os.path.exists(hilbert_path):
            with open(hilbert_path, 'r', encoding='utf-8') as f:
                content = f.read()
                p55_block = re.search(r'EMA55(.*?)──', content, re.DOTALL)
                if p55_block:
                    row['Hilbert_Periodo'] = extract_metric(p55_block.group(1), r'Período mediana:\s+([\d\.]+)')

        # 4. Scale Ratio (55/10)
        scale_path = os.path.join(RESULTS_DIR, f"{aid}_scale_table.txt")
        if os.path.exists(scale_path):
            with open(scale_path, 'r', encoding='utf-8') as f:
                content = f.read()
                row['Scale_55_10'] = extract_metric(content, r'55/10\s+\|\s+([\d\.]+)')

        # 5. Apoyo Exito (EMA55)
        apoyo_path = os.path.join(RESULTS_DIR, f"{aid}_apoyo_stats.txt")
        if os.path.exists(apoyo_path):
            with open(apoyo_path, 'r', encoding='utf-8') as f:
                content = f.read()
                p55_block = re.search(r'EMA55(.*?)EMA200', content, re.DOTALL)
                if p55_block:
                    row['Exito_Apoyo_55'] = extract_metric(p55_block.group(1), r'tasa éxito.*?=\s+([\d\.]+)')

        # 6. Correlation Lag
        corr_path = os.path.join(RESULTS_DIR, f"{aid}_correlation_stats.txt")
        if os.path.exists(corr_path):
            with open(corr_path, 'r', encoding='utf-8') as f:
                content = f.read()
                row['Corr_Lag'] = extract_metric(content, r'Lag óptimo\s+=\s+(-?[\d\.]+)')

        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_CSV, index=False)

def main():
    print("🚀 Iniciando Compilador de Reportes...")
    ids = get_base_ids()
    if not ids:
        print("❌ No se encontraron archivos en results/. ¿Corriste el pipeline?")
        return
    
    print(f"📂 Detectados {len(ids)} archivos únicos.")
    
    generate_report_a(ids)
    generate_report_b(ids)
    generate_synthesis_csv(ids)
    
    print("\n✅ ¡Todo listo!")
    print(f"   - Reporte A: {OUTPUT_A}")
    print(f"   - Reporte B: {OUTPUT_B}")
    print(f"   - Síntesis:  {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
