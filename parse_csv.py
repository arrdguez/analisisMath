"""
parse_csv.py — Versión Resiliente (Agnóstica)
─────────────────────────────────────────────────────────────────────────────
Limpia los CSV exportados por TradingView, detectando automáticamente el formato.
Soporta:
  - Delimitadores: ',' o ';'
  - Con o sin fecha interna en el mensaje.
  - Con o sin encabezados internos.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import pandas as pd
import numpy as np

# ── Configuración ─────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(__file__)
DATA_DIR    = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
SUFFIX_OUT  = '_clean.csv'

# Columnas esperadas en el orden del indicador
COLUMNS_TARGET = [
    'date', 'close', 'ema10', 'ema55', 'ema200',
    'dist_p10', 'dist_p55', 'dist_p200',
    'slope10', 'slope55', 'slope200',
    'dist_10_55', 'dist_55_200', 'ratio_armonico'
]

def parse_number(s: str):
    if not s: return None
    s = s.strip().strip('"')
    if s.lower() in ('nan', 'null', ''): return None
    s = s.replace(',', '') # Quitar comas de miles
    try:
        return float(s)
    except ValueError:
        return None

def detect_delimiter(line: str) -> str:
    """Detecta si la línea usa coma o punto y coma como separador principal."""
    # Contamos ocurrencias de cada uno fuera de las comillas globales (estimación simple)
    if ';' in line: return ';'
    return ','

def process_file(filepath: str) -> pd.DataFrame:
    """Lee un CSV de TradingView con alta resiliencia."""
    data_rows = []
    
    with open(filepath, encoding='utf-8') as f:
        # Leer primera línea para el delimitador del CSV base
        header_base = f.readline()
        
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Split Date,"Message"
            parts = line.split(',', 1)
            if len(parts) < 2: continue
            
            date_log, message = parts[0], parts[1]
            message = message.strip().strip('"')
            
            # Detectar delimitador interno del mensaje
            delim = detect_delimiter(message)
            msg_parts = [p.strip() for p in message.split(delim)]
            
            # Saltar si es una fila de encabezado (contiene palabras clave)
            if any(x in msg_parts[0].lower() for x in ('date', 'close', 'ema')):
                continue
                
            # Validar si es una fila de datos
            # Escenario A: Primera columna es fecha (2025-...)
            # Escenario B: Primera columna es número (close)
            is_date = '-' in msg_parts[0] and ':' in msg_parts[0]
            first_val = parse_number(msg_parts[0]) if not is_date else parse_number(msg_parts[1])
            
            if is_date or first_val is not None:
                # Normalizar: si no tiene fecha interna, usamos la del log
                row_date = msg_parts[0] if is_date else date_log
                numeric_vals = msg_parts[1:] if is_date else msg_parts
                
                # Construir fila
                row = [row_date] + [parse_number(v) for v in numeric_vals]
                # Ajustar longitud a las columnas target (14)
                row = (row + [None] * 14)[:14]
                data_rows.append(row)

    if not data_rows:
        return pd.DataFrame()

    df = pd.DataFrame(data_rows, columns=COLUMNS_TARGET)
    
    # Limpieza final
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values('date')
    
    # Asegurar que el ratio armónico esté calculado si falta
    mask = df['ratio_armonico'].isna()
    if mask.any():
        df.loc[mask, 'ratio_armonico'] = (df.loc[mask, 'dist_10_55'] / df.loc[mask, 'dist_55_200']).replace([np.inf, -np.inf], np.nan)

    return df.drop_duplicates(subset='date', keep='last').reset_index(drop=True)

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

    if not csv_files:
        print(f"[ERROR] No hay archivos en {DATA_DIR}")
        return

    for filename in sorted(csv_files):
        print(f"[>>] Procesando: {filename}...", end=' ', flush=True)
        in_path = os.path.join(DATA_DIR, filename)
        df = process_file(in_path)

        if df.empty:
            print("[SKIP] Sin datos.")
            continue

        out_name = os.path.splitext(filename)[0] + SUFFIX_OUT
        df.to_csv(os.path.join(RESULTS_DIR, out_name), index=False)
        print(f"[OK] {len(df)} filas -> results/{out_name}")

if __name__ == "__main__":
    main()
