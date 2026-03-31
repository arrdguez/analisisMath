"""
parse_csv.py
─────────────────────────────────────────────────────────────────────────────
Limpia los CSV exportados por TradingView Pine Script (formato antiguo con ';')
y los convierte al formato limpio nuevo (coma-separado, sin miles con coma).

Formato de entrada (TradingView logs):
  Date,Message
  2017-10-12T00:00:00.000-00:00,";5,430;4,688.223;NaN;NaN;15.822;..."

Formato de salida:
  date,close,ema10,ema55,ema200,dist_p10,dist_p55,dist_p200,
  slope10,slope55,slope200,dist_10_55,dist_55_200,ratio_armonico
  2017-10-12,5430.0,4688.223,,,...

Uso:
  python parse_csv.py
  (procesa todos los CSV en /doc y genera versiones _clean.csv)
─────────────────────────────────────────────────────────────────────────────
"""

import re
import os
import pandas as pd

# ── Configuración ─────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(__file__)
DATA_DIR    = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
SUFFIX_IN   = 'pine-logs'        # identifica los archivos a procesar
SUFFIX_OUT  = '_clean.csv'

COLUMNS = [
    'close', 'ema10', 'ema55', 'ema200',
    'dist_p10', 'dist_p55', 'dist_p200',
    'slope10', 'slope55', 'slope200',
    'dist_10_55', 'dist_55_200'
]

# ── Funciones ─────────────────────────────────────────────────────────────────

def parse_number(s: str):
    """
    Convierte string de TradingView a float.
    Maneja:  '4,688.223' → 4688.223
             'NaN'       → None
             ''          → None
    """
    s = s.strip()
    if not s or s == 'NaN':
        return None
    # Quitar comas de miles (solo si hay punto decimal también)
    s = s.replace(',', '')
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(iso_str: str) -> str:
    """
    Normaliza el campo fecha a 'YYYY-MM-DDTHH:mm'.
    Soporta:
      - TradingView export antiguo: '2017-10-12T00:00:00.000-00:00'
      - Nuevo Pine Script 1D:       '2017-10-12'
      - Nuevo Pine Script 1H/4H:    '2017-10-12T14:00'
    """
    s = iso_str.strip()
    # Formato TradingView export: tiene milisegundos y timezone
    if len(s) > 16:
        s = s[:16]           # '2017-10-12T00:00'
    # Solo fecha sin hora → agregar T00:00
    if len(s) == 10:
        s = s + 'T00:00'
    return s


def is_data_row(message: str) -> bool:
    """
    Filtra las filas válidas del log principal.
    Soporta:
      - Formato antiguo: empieza con ';'
      - Formato nuevo: empieza directamente con el valor de 'close'
    Descarta las filas del barstate.islast (formato 'HH:mm:ss,close,...').
    """
    msg = message.strip().strip('"')
    # Formato antiguo: claramente identificado por ';'
    if msg.startswith(';'):
        return True
    
    # Formato nuevo: debe tener al menos 10 separadores (';') y el primero debe ser numérico
    # (close suele ser un número positivo > 0)
    parts = msg.split(';')
    if len(parts) >= 10:
        first_val = parse_number(parts[0])
        return first_val is not None
        
    return False


def parse_message(message: str) -> list:
    """
    Parsea el campo Message del CSV de TradingView.
    Input:  ';5,430;4,688.223;NaN;...'  O  '5,430;4,688.223;NaN;...'
    Output: [5430.0, 4688.223, None, ...]
    """
    # Quitar comillas externas si las hay
    message = message.strip().strip('"')
    # Quitar el ';' inicial si existe
    if message.startswith(';'):
        message = message[1:]
    
    parts = message.split(';')
    return [parse_number(p) for p in parts]


def compute_ratio(row: pd.Series) -> float | None:
    """Calcula ratio_armonico = dist_10_55 / dist_55_200 (None si div/0)"""
    d55_200 = row.get('dist_55_200')
    d10_55  = row.get('dist_10_55')
    if d55_200 is None or d10_55 is None or d55_200 == 0:
        return None
    return round(d10_55 / d55_200, 6)


def process_file(filepath: str) -> pd.DataFrame:
    """Lee un CSV de TradingView y devuelve un DataFrame limpio."""
    rows = []

    with open(filepath, encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')

            # Saltar header
            if i == 0:
                continue

            # Parsear la línea: Date,"Message"
            # Usamos split con maxsplit=1 para no romper por comas internas
            parts = line.split(',', 1)
            if len(parts) < 2:
                continue

            date_raw, message = parts[0], parts[1]

            # Filtrar solo filas del log principal
            # (las del barstate.islast tienen formato diferente)
            msg_clean = message.strip().strip('"')
            if not is_data_row(msg_clean):
                continue

            date_str = parse_date(date_raw)
            values   = parse_message(msg_clean)

            # Asegurar que tenga exactamente 12 valores
            values = (values + [None] * 12)[:12]

            row = {'date': date_str}
            row.update(dict(zip(COLUMNS, values)))
            rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        print(f'  ⚠️  Sin datos válidos en {os.path.basename(filepath)}')
        return df

    # Eliminar duplicados de fecha (quedarse con el último registro del día)
    df = df.drop_duplicates(subset='date', keep='last')
    df = df.sort_values('date').reset_index(drop=True)

    # Añadir ratio armónico calculado
    df['ratio_armonico'] = df.apply(compute_ratio, axis=1)

    # Convertir columnas numéricas
    for col in COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    csv_files = [
        f for f in os.listdir(DATA_DIR)
        if SUFFIX_IN in f and f.endswith('.csv')
    ]

    if not csv_files:
        print(f'No se encontraron archivos con "{SUFFIX_IN}" en {DATA_DIR}')
        return

    for filename in sorted(csv_files):
        in_path  = os.path.join(DATA_DIR, filename)
        out_name = filename.replace('.csv', SUFFIX_OUT)
        out_path = os.path.join(RESULTS_DIR, out_name)

        print(f'\n📂 Procesando: {filename}')
        df = process_file(in_path)

        if df.empty:
            continue

        # Guardar CSV limpio en results/
        df.to_csv(out_path, index=False, float_format='%.6f')

        # Reporte rápido
        total     = len(df)
        completas = df['ema200'].notna().sum()
        print(f'  ✅ {total} filas totales')
        print(f'  ✅ {completas} filas con EMA200 completa ({completas/total*100:.1f}%)')
        print(f'  ✅ Rango: {df["date"].iloc[0]}  →  {df["date"].iloc[-1]}')
        print(f'  💾 Guardado en: results/{out_name}')

        # Vista previa
        print(f'\n  Muestra (primeras 3 filas con datos completos):')
        preview = df[df['ema200'].notna()].head(3)
        print(preview[['date', 'close', 'dist_p10', 'dist_p55', 'dist_p200',
                        'dist_10_55', 'dist_55_200', 'ratio_armonico']].to_string(index=False))


if __name__ == '__main__':
    main()
