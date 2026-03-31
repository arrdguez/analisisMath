"""
main.py — Punto de entrada único del proyecto
──────────────────────────────────────────────
Corre toda la cadena de análisis o solo los pasos que elijas.

Uso:
  # Procesar todos los archivos de data/ (modo normal):
  python main.py

  # Procesar un archivo específico:
  python main.py --file "data/1D-btc-pine-logs-....csv"

  # Solo algunos pasos:
  python main.py --pasos parse explore fft

  # Ver ayuda:
  python main.py --ayuda

Pasos disponibles (en orden):
  parse       -> limpia CSV crudos de TradingView -> results/*_clean.csv
  explore     -> estadísticas descriptivas y gráficas de oscilaciones
  fft         -> ciclos dominantes por Fourier
  apoyos      -> profundidad y rebote de apoyos en cada EMA
  hurst       -> exponente de Hurst (memoria de la serie)
  hilbert     -> envolvente y período instantáneo
  fibonacci   -> ratios de tiempo y amplitud vs niveles Fibonacci
"""

import os
import sys
import glob
import argparse

# forzar UTF-8 en stdout para evitar errores en Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE        = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE, 'data')
RESULTS_DIR = os.path.join(BASE, 'results')

# Columnas que debe tener un CSV limpio válido
COLUMNAS_REQUERIDAS = {
    'date', 'close', 'ema10', 'ema55', 'ema200',
    'dist_p10', 'dist_p55', 'dist_p200',
    'slope10', 'slope55', 'slope200',
    'dist_10_55', 'dist_55_200', 'ratio_armonico'
}

# Columnas mínimas que debe tener un CSV crudo de TradingView
COLUMNAS_CRUDAS = {'Date', 'Message'}

PASOS_DISPONIBLES = ['parse', 'explore', 'fft', 'apoyos', 'hurst', 'hilbert', 'fibonacci', 'report']

SEP  = '=' * 60
SEP2 = '-' * 60

# ── validación de archivos ────────────────────────────────────────────────────

def detectar_formato(path: str) -> str:
    """
    Analiza el archivo y devuelve:
      'crudo'   → CSV de TradingView sin limpiar (necesita parse)
      'limpio'  → CSV ya procesado por parse_csv.py
      'invalido'→ no es ninguno de los dos
    """
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            header  = f.readline().strip().lower()
            primera = f.readline().strip()
    except Exception as e:
        return f'invalido: no se pudo leer ({e})'

    cols = set(header.split(','))

    # ¿tiene las columnas del formato limpio?
    if COLUMNAS_REQUERIDAS.issubset(cols):
        return 'limpio'

    # ¿tiene Date y Message (formato TradingView)?
    if {'date', 'message'}.issubset(cols):
        # verificar que Message contenga ';' (formato log de Pine Script)
        if ';' in primera:
            return 'crudo'
        # podría ser el nuevo formato (CSV directo del Pine Script corregido)
        return 'crudo_nuevo'

    return f'invalido: columnas desconocidas -> {", ".join(sorted(cols)[:6])}...'


def validar_archivo(path: str) -> tuple[bool, str]:
    """Retorna (ok, mensaje) sobre si el archivo es usable."""
    if not os.path.exists(path):
        return False, f'[ERROR] El archivo no existe: {path}'

    if not path.lower().endswith('.csv'):
        return False, f'[ERROR] No es un archivo .csv: {os.path.basename(path)}'

    if os.path.getsize(path) < 100:
        return False, f'[ERROR] Archivo demasiado pequeño (posiblemente vacío): {os.path.basename(path)}'

    fmt = detectar_formato(path)
    if fmt.startswith('invalido'):
        return False, (
            f'[ERROR] Formato no reconocido en: {os.path.basename(path)}\n'
            f'   {fmt}\n'
            f'   Formatos validos:\n'
            f'   -> CSV crudo de TradingView (columnas: Date, Message con ";" en Message)\n'
            f'   -> CSV limpio generado por parse_csv.py\n'
            f'      (columnas: date, close, ema10, ema55, ema200, ...)\n'
            f'   Asegurate de exportar desde Pine Script Debugger -> Logs -> Export logs'
        )

    return True, fmt


def buscar_archivos_data() -> list[str]:
    """Busca todos los CSV en data/ que parezcan datos de Pine Script."""
    patron    = os.path.join(DATA_DIR, '*.csv')
    todos     = glob.glob(patron)
    keywords  = ('pine', 'btc', 'log')
    validos   = [f for f in todos
                 if any(k in os.path.basename(f).lower() for k in keywords)]
    return sorted(validos) if validos else sorted(todos)


def buscar_clean_en_results() -> list[str]:
    """Busca CSV limpios en results/."""
    return sorted(glob.glob(os.path.join(RESULTS_DIR, '*_clean.csv')))

# ── runner de pasos ───────────────────────────────────────────────────────────

def correr_parse(archivos_origen: list[str]) -> list[str]:
    """Importa y corre parse_csv con los archivos especificados."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'parse_csv', os.path.join(BASE, 'parse_csv.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    generados = []

    for path in archivos_origen:
        nombre = os.path.basename(path)
        print(f'\n  [>] Procesando: {nombre}')
        df = mod.process_file(path)
        if df.empty:
            print(f'  [!] Sin datos validos en {nombre}')
            continue
        out_name = nombre.replace('.csv', '_clean.csv')
        out_path = os.path.join(RESULTS_DIR, out_name)
        df.to_csv(out_path, index=False, float_format='%.6f')
        total     = len(df)
        completas = df['ema200'].notna().sum()
        print(f'  [OK] {total} filas | {completas} con EMA200 ({completas/total*100:.1f}%)')
        print(f'  [OK] Rango: {df["date"].iloc[0]} -> {df["date"].iloc[-1]}')
        print(f'  [>>] results/{out_name}')
        generados.append(out_path)

    return generados


def correr_modulo(nombre_script: str):
    """Importa y corre el main() de cualquier script del proyecto."""
    import importlib.util
    path = os.path.join(BASE, f'{nombre_script}.py')
    spec = importlib.util.spec_from_file_location(nombre_script, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()

# ── lógica principal ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog='python main.py',
        description='Analisis de Magnitudes Armonicas - punto de entrada unico',
        add_help=False
    )
    parser.add_argument('--file', '-f', nargs='+', metavar='ARCHIVO')
    parser.add_argument('--pasos', '-p', nargs='+', metavar='PASO',
                        choices=PASOS_DISPONIBLES)
    parser.add_argument('--ayuda', '-a', action='store_true')
    args = parser.parse_args()

    if args.ayuda:
        print(__doc__)
        return

    pasos = args.pasos or PASOS_DISPONIBLES

    print(f'\n{SEP}')
    print('  Analisis de Magnitudes Armonicas')
    print(SEP)
    print(f'  Pasos: {", ".join(pasos)}')

    # ── resolver archivos de entrada ──────────────────────────────────────────
    archivos_crudos  = []
    archivos_limpios = []

    if args.file:
        for f in args.file:
            path = f if os.path.isabs(f) else os.path.join(BASE, f)
            ok, info = validar_archivo(path)
            if not ok:
                print(f'\n{info}')
                sys.exit(1)
            print(f'  [archivo] {os.path.basename(path)} -> formato: {info}')
            if info in ('crudo', 'crudo_nuevo'):
                archivos_crudos.append(path)
            elif info == 'limpio':
                archivos_limpios.append(path)
    else:
        candidatos = buscar_archivos_data()
        if not candidatos:
            print(f'\n[ERROR] No se encontraron archivos CSV en: {DATA_DIR}')
            print('  Descarga los datos desde TradingView:')
            print('  Pine Script Debugger -> pestana Logs -> Export logs')
            print(f'  Guarda el archivo en: {DATA_DIR}')
            sys.exit(1)

        print(f'\n  Archivos encontrados en data/:')
        for f in candidatos:
            ok, info = validar_archivo(f)
            marca = '[OK]' if ok else '[!!]'
            print(f'    {marca} {os.path.basename(f)}  [{info}]')
            if ok:
                if info in ('crudo', 'crudo_nuevo'):
                    archivos_crudos.append(f)
                elif info == 'limpio':
                    archivos_limpios.append(f)
            else:
                # imprimir el detalle del error con sangría
                for linea in info.split('\n'):
                    print(f'       {linea}')

    # ── PASO: parse ───────────────────────────────────────────────────────────
    if 'parse' in pasos:
        if archivos_crudos:
            print(f'\n{SEP2}')
            print(f'  PASO: parse  ({len(archivos_crudos)} archivo/s)')
            print(SEP2)
            nuevos = correr_parse(archivos_crudos)
            archivos_limpios.extend(nuevos)
        else:
            print('\n  [i] parse: no hay archivos crudos nuevos que procesar')
            if not archivos_limpios:
                archivos_limpios = buscar_clean_en_results()
    else:
        if not archivos_limpios:
            archivos_limpios = buscar_clean_en_results()

    # ── verificar limpios disponibles ─────────────────────────────────────────
    pasos_analisis = [p for p in pasos if p != 'parse']
    if pasos_analisis and not archivos_limpios:
        print('\n[ERROR] No hay archivos limpios (_clean.csv) en results/')
        print('  Corre primero:  python main.py --pasos parse')
        sys.exit(1)

    if archivos_limpios:
        print(f'\n  Archivos limpios disponibles para analisis:')
        for f in archivos_limpios:
            print(f'    [OK] {os.path.basename(f)}')

    # ── PASOS de análisis ─────────────────────────────────────────────────────
    mapa = {
        'explore':   ('explore',          'Analisis exploratorio visual'),
        'fft':       ('fft_analysis',     'Ciclos FFT'),
        'apoyos':    ('apoyo_stats',      'Estadisticas de apoyos en EMAs'),
        'hurst':     ('hurst',            'Exponente de Hurst'),
        'hilbert':   ('hilbert_analysis', 'Transformada de Hilbert'),
        'fibonacci': ('fibonacci_analysis','Ratios de Fibonacci'),
        'report':    ('generate_report',  'Generacion de reporte maestro para IA'),
    }

    num = 2 if 'parse' in pasos else 1
    for paso in [p for p in pasos if p != 'parse']:
        script, nombre = mapa[paso]
        print(f'\n{SEP2}')
        print(f'  PASO {num}: {paso}  ->  {nombre}')
        print(SEP2)
        try:
            correr_modulo(script)
            num += 1
        except Exception as e:
            print(f'\n[ERROR] en {paso}: {e}')
            import traceback
            traceback.print_exc()
            print('  Continuando con el siguiente paso...')

    # ── resumen final ─────────────────────────────────────────────────────────
    pngs = glob.glob(os.path.join(RESULTS_DIR, '*.png'))
    txts = glob.glob(os.path.join(RESULTS_DIR, '*.txt'))
    print(f'\n{SEP}')
    print(f'  COMPLETADO')
    print(f'  Resultados en: {RESULTS_DIR}')
    print(f'  {len(pngs)} graficas  |  {len(txts)} reportes de texto')
    print(SEP + '\n')


if __name__ == '__main__':
    main()
