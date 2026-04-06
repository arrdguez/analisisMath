import os
import re
import pandas as pd
import numpy as np

results_dir = r'C:\Users\MI29541\ws\mystuff\analisisMath\results'
contact_dir = r'C:\Users\MI29541\ws\mystuff\analisisMath\results\contact_dynamics'

# Study patterns
STUDIES = {
    'Exploración': r'.*_explore_stats\.txt',
    'FFT': r'.*_fft_ciclos\.txt',
    'Hurst': r'.*_hurst_valores\.txt',
    'Hilbert': r'.*_hilbert_resumen\.txt',
    'Fibonacci': r'.*_fibonacci_stats\.txt',
    'Apoyo': r'.*_apoyo_stats\.txt',
    'Correlación': r'.*_correlation_stats\.txt',
    'Escala': r'scale_.*_table\.txt',
    'Contacto': r'.*_contact_dynamics\.csv'
}

def get_base_id(filename):
    # Logs
    if filename.startswith('pine-logs-'):
        # For scale files: scale_pine-logs-..._table.txt
        if filename.startswith('scale_'):
            match = re.search(r'scale_(pine-logs-.*?)(?:_|$)', filename)
            if match: return match.group(1)
        else:
            match = re.search(r'(pine-logs-.*?)(?:_|$)', filename)
            if match: return match.group(1)
    # Contact
    if 'contact_dynamics' in filename:
        match = re.search(r'(pine_dist_p\d+)_contact_dynamics\.csv', filename)
        if match: return match.group(1)
    return None

def get_study_type(filename):
    if 'explore_stats.txt' in filename: return 'Exploración'
    if 'fft_ciclos.txt' in filename: return 'FFT'
    if 'hurst_valores.txt' in filename: return 'Hurst'
    if 'hilbert_resumen.txt' in filename: return 'Hilbert'
    if 'fibonacci_stats.txt' in filename: return 'Fibonacci'
    if 'apoyo_stats.txt' in filename: return 'Apoyo'
    if 'correlation_stats.txt' in filename: return 'Correlación'
    if 'scale_' in filename and ('table.txt' in filename or 'validation.txt' in filename): return 'Escala'
    if 'contact_dynamics.csv' in filename: return 'Contacto'
    return None

files_by_id = {}
all_files = []

for root, dirs, files in os.walk(results_dir):
    for f in files:
        if f.endswith('.txt') or f.endswith('.csv'):
            path = os.path.join(root, f)
            bid = get_base_id(f)
            if bid:
                if bid not in files_by_id: files_by_id[bid] = []
                files_by_id[bid].append(path)
            all_files.append((path, f))

# Report A: By File
report_a = []
ids_sorted = sorted(files_by_id.keys())
chapter_num = 1

for bid in ids_sorted:
    report_a.append(f"# CAPÍTULO {chapter_num}: {bid}\n")
    
    # Sort files by study order
    id_files = files_by_id[bid]
    studies_found = {}
    for p in id_files:
        stype = get_study_type(os.path.basename(p))
        if stype:
            if stype not in studies_found: studies_found[stype] = []
            studies_found[stype].append(p)
    
    for stype in ['Exploración', 'FFT', 'Hurst', 'Hilbert', 'Fibonacci', 'Apoyo', 'Correlación', 'Escala', 'Contacto']:
        if stype in studies_found:
            report_a.append(f"## Estudio {stype}\n")
            for p in sorted(studies_found[stype]):
                if p.endswith('.txt'):
                    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        report_a.append(content)
                        report_a.append("\n" + "="*40 + "\n")
                elif p.endswith('.csv'):
                    df = pd.read_csv(p)
                    report_a.append(f"Archivo CSV: {os.path.basename(p)}\n")
                    report_a.append(df.to_markdown(index=False))
                    report_a.append("\n" + "="*40 + "\n")
    report_a.append("\n" + "-"*60 + "\n\n")
    chapter_num += 1

with open('REPORTE_A_POR_ARCHIVO.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(report_a))

# Report B: By Study
report_b = []
studies_all = {}
for bid, paths in files_by_id.items():
    for p in paths:
        stype = get_study_type(os.path.basename(p))
        if stype:
            if stype not in studies_all: studies_all[stype] = []
            studies_all[stype].append((bid, p))

for stype in ['Exploración', 'FFT', 'Hurst', 'Hilbert', 'Fibonacci', 'Apoyo', 'Correlación', 'Escala', 'Contacto']:
    if stype in studies_all:
        report_b.append(f"# CAPÍTULO: {stype}\n")
        # Sort by bid
        for bid, p in sorted(studies_all[stype], key=lambda x: x[0]):
            report_b.append(f"## Archivo ({bid})\n")
            if p.endswith('.txt'):
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    report_b.append(content)
                    report_b.append("\n" + "="*40 + "\n")
            elif p.endswith('.csv'):
                df = pd.read_csv(p)
                report_b.append(df.to_markdown(index=False))
                report_b.append("\n" + "="*40 + "\n")
        report_b.append("\n" + "-"*60 + "\n\n")

with open('REPORTE_B_POR_ESTUDIO.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(report_b))

# Synthesis CSV
rows = []
for bid in ids_sorted:
    row = {'Archivo': bid}
    id_files = files_by_id[bid]
    
    # Default values
    row['Hurst_p55'] = ''
    row['FFT_Ciclo1'] = ''
    row['Hilbert_Periodo'] = ''
    row['Scale_Ratio'] = ''
    row['Apoyo_Exito_p55'] = ''
    row['Corr_Lag'] = ''
    row['Contact_Dur_Mediana'] = ''
    
    for p in id_files:
        fname = os.path.basename(p)
        content = ""
        if p.endswith('.txt'):
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        if 'hurst_valores.txt' in fname:
            m = re.search(r'dist_p55:\s+H=([\d\.]+)', content)
            if m: row['Hurst_p55'] = m.group(1)
            
        if 'fft_ciclos.txt' in fname:
            # Look for dist_p55 section then first cycle
            m_sect = re.search(r'dist_p55:(.*?)dist_', content, re.DOTALL)
            if not m_sect: m_sect = re.search(r'dist_p55:(.*)', content, re.DOTALL)
            if m_sect:
                m = re.search(r'#1\s+(\d+)\s+velas', m_sect.group(1))
                if m: row['FFT_Ciclo1'] = m.group(1)
                
        if 'hilbert_resumen.txt' in fname:
            m_sect = re.search(r'EMA55 \(dist_p55\).*?Período mediana:\s+([\d\.]+)\s+velas', content, re.DOTALL)
            if m_sect: row['Hilbert_Periodo'] = m_sect.group(1)
            
        if 'table.txt' in fname and 'scale_' in fname:
            m = re.search(r'55/10\s+\|\s+([\d\.]+)', content)
            if m: row['Scale_Ratio'] = m.group(1)
            
        if 'apoyo_stats.txt' in fname:
            m_sect = re.search(r'Apoyo en EMA55.*?tasa éxito \(subió\) =\s+([\d\.]+)%', content, re.DOTALL)
            if m_sect: row['Apoyo_Exito_p55'] = m_sect.group(1)
            
        if 'correlation_stats.txt' in fname:
            m = re.search(r'Lag óptimo\s+=\s+(-?\d+)\s+velas', content)
            if m: row['Corr_Lag'] = m.group(1)
            
        if 'contact_dynamics.csv' in fname:
            df = pd.read_csv(p)
            if 'duration' in df.columns:
                row['Contact_Dur_Mediana'] = df['duration'].median()
                
    rows.append(row)

df_synthesis = pd.DataFrame(rows)
df_synthesis.to_csv('SINTESIS_MAESTRA_DATOS.csv', index=False)
