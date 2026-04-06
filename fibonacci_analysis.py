"""
fibonacci_analysis.py — Relaciones de Fibonacci entre apoyos y amplitudes
──────────────────────────────────────────────────────────────────────────
Pregunta que responde:
  "¿Los tiempos entre apoyos consecutivos guardan proporción áurea?
   ¿Las amplitudes de las correcciones son retrocesos de Fibonacci?"

Fibonacci en trading no es magia — es una hipótesis medible:
  Si el tiempo entre apoyo_EMA10 y apoyo_EMA55 dividido entre
  el tiempo entre apoyo_EMA55 y apoyo_EMA200 tiende a 0.618 o 1.618,
  hay una proporción armónica real en los datos.

Dos análisis:
  1. RATIOS DE TIEMPO entre apoyos consecutivos en los 3 niveles
  2. RATIOS DE AMPLITUD: cuánto retrocede la oscilación respecto al impulso

Niveles de Fibonacci a buscar: 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.618

Genera en results/:
  - fibonacci_{TF}_tiempos.png   ← histograma de ratios de tiempo
  - fibonacci_{TF}_amplitudes.png ← histograma de ratios de amplitud
  - fibonacci_{TF}_stats.txt     ← tabla de resultados

Uso:
  python fibonacci_analysis.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import argrelmin, argrelmax
from plot_style import BG_FIG, BG_AX, COLORS, estilo_ax

BASE    = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, 'results')

FIB_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786, 1.000, 1.618, 2.618]
FIB_COLORS = ['#1565c0','#00838f','#558b2f','#f9a825',
              '#e65100','#c62828','#6a1b9a','#880e4f']
VENTANA = 5

# ── helpers ───────────────────────────────────────────────────────────────────

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['date'])
    return df.dropna(subset=['ema200']).reset_index(drop=True)


def timeframe_label(filename: str) -> str:
    return os.path.basename(filename).replace('_clean.csv', '').replace('.csv', '')


def detectar_extremos(serie: np.ndarray, ventana: int = VENTANA):
    """Retorna índices de mínimos y máximos locales."""
    mins = argrelmin(serie, order=ventana)[0]
    maxs = argrelmax(serie, order=ventana)[0]
    return mins, maxs


def calcular_ratios_tiempo(df: pd.DataFrame) -> list[float]:
    """
    Para cada trío de apoyos (EMA10 → EMA55 → EMA200) calcula:
      ratio = tiempo(EMA10→EMA55) / tiempo(EMA55→EMA200)

    Un apoyo en EMA55 se busca DESPUÉS de cada apoyo en EMA10,
    y un apoyo en EMA200 se busca DESPUÉS de cada apoyo en EMA55.
    """
    # detectar apoyos en cada nivel
    mins_10,  _ = detectar_extremos(df['dist_p10'].values)
    mins_55,  _ = detectar_extremos(df['dist_p55'].values)
    mins_200, _ = detectar_extremos(df['dist_p200'].values)

    ratios = []
    for i10 in mins_10:
        # buscar el siguiente apoyo en EMA55 después del apoyo en EMA10
        futuros_55 = mins_55[mins_55 > i10]
        if len(futuros_55) == 0:
            continue
        i55 = futuros_55[0]

        # buscar el siguiente apoyo en EMA200 después del apoyo en EMA55
        futuros_200 = mins_200[mins_200 > i55]
        if len(futuros_200) == 0:
            continue
        i200 = futuros_200[0]

        dur_10_55  = i55  - i10    # velas entre apoyo EMA10 y EMA55
        dur_55_200 = i200 - i55    # velas entre apoyo EMA55 y EMA200

        if dur_55_200 > 0:
            ratios.append(dur_10_55 / dur_55_200)

    return ratios


def calcular_ratios_amplitud(df: pd.DataFrame) -> dict[str, list[float]]:
    """
    Para cada variable, mide el ratio:
      amplitud_valle / amplitud_pico_anterior

    Es decir: si el precio subió +10% (pico) y luego corrigió hasta -4%,
    el ratio de retroceso es 4/10 = 0.4 (cerca del 0.382 de Fibonacci).
    """
    resultados = {}

    for col in ['dist_p10', 'dist_p55', 'dist_p200']:
        serie = df[col].dropna().values
        mins, maxs = detectar_extremos(serie)

        ratios = []
        # para cada mínimo, buscar el máximo más cercano anterior
        for i_min in mins:
            maxs_previos = maxs[maxs < i_min]
            if len(maxs_previos) == 0:
                continue
            i_max = maxs_previos[-1]

            amplitud_pico  = abs(serie[i_max])
            amplitud_valle = abs(serie[i_min])

            if amplitud_pico > 0:
                ratios.append(amplitud_valle / amplitud_pico)

        resultados[col] = ratios

    return resultados


def fib_mas_cercano(ratio: float) -> tuple[float, float]:
    """Retorna el nivel de Fibonacci más cercano y la distancia."""
    distancias = [(abs(ratio - f), f) for f in FIB_LEVELS]
    dist, nivel = min(distancias)
    return nivel, dist


# ── gráfica 1: ratios de tiempo ───────────────────────────────────────────────

def plot_tiempos(ratios: list[float], tf: str):
    if not ratios:
        print('  ⚠️  Sin ratios de tiempo suficientes')
        return

    ratios_arr  = np.array(ratios)
    ratios_clip = ratios_arr[ratios_arr < np.percentile(ratios_arr, 95)]
    med = np.median(ratios_clip)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=BG_FIG)
    ax.hist(ratios_clip, bins=50, color=COLORS['fibonacci'], alpha=0.75,
            edgecolor='none', label=f'n={len(ratios)} secuencias')
    ax.axvline(med, color='#111111', linewidth=1.5, linestyle='-',
               label=f'mediana={med:.3f}')

    for fib, fcolor in zip(FIB_LEVELS, FIB_COLORS):
        if fib <= ratios_clip.max() * 1.1:
            ax.axvline(fib, color=fcolor, linewidth=1.2, linestyle='--',
                       alpha=0.9, label=f'Fib {fib}')

    ax.legend(fontsize=7, ncol=3)
    estilo_ax(ax,
              xlabel='Ratio: tiempo(EMA10→EMA55) / tiempo(EMA55→EMA200)',
              ylabel='Número de secuencias',
              title=f'Ratios de tiempo entre apoyos consecutivos  [{tf}]\n'
                    f'Mediana={med:.3f}  —  ¿se acumula cerca de 0.618 o 0.786?')

    out = os.path.join(RESULTS, f'{tf}_fibonacci_tiempos.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


def plot_amplitudes(ratios_amp: dict[str, list[float]], tf: str):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor=BG_FIG)
    fig.suptitle(
        f'Ratios amplitud valle/pico  [{tf}]\n'
        f'¿Las correcciones retroceden a niveles de Fibonacci?',
        fontsize=12, fontweight='bold', color='#111111')

    configs = [
        ('dist_p10',  'EMA10',  COLORS['dist_p10'],  axes[0]),
        ('dist_p55',  'EMA55',  COLORS['dist_p55'],  axes[1]),
        ('dist_p200', 'EMA200', COLORS['dist_p200'], axes[2]),
    ]

    for col, label, color, ax in configs:
        ratios = ratios_amp.get(col, [])
        if not ratios:
            ax.set_title(f'{label}\nSin datos')
            continue

        ratios_arr  = np.array(ratios)
        ratios_clip = ratios_arr[ratios_arr < 3]
        med = np.median(ratios_clip)
        fib_near, dist_fib = fib_mas_cercano(med)

        ax.hist(ratios_clip, bins=40, color=color, alpha=0.75, edgecolor='none',
                label=f'n={len(ratios)}')
        ax.axvline(med, color='#111111', linewidth=1.5, linestyle='-',
                   label=f'mediana={med:.3f}')
        for fib, fcolor in zip(FIB_LEVELS[:6], FIB_COLORS[:6]):
            ax.axvline(fib, color=fcolor, linewidth=1, linestyle='--',
                       alpha=0.8, label=f'{fib}')

        ax.legend(fontsize=6, ncol=2)
        estilo_ax(ax,
                  xlabel='amplitud_valle / amplitud_pico  (ratio de retroceso)',
                  ylabel='Número de eventos',
                  title=f'{label}  (n={len(ratios)})\n'
                        f'mediana={med:.3f}  →  Fib más cercano: {fib_near}'
                        f' (dist={dist_fib:.3f})')

    plt.tight_layout()
    out = os.path.join(RESULTS, f'{tf}_fibonacci_amplitudes.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── reporte txt ───────────────────────────────────────────────────────────────

def write_stats(ratios_tiempo: list[float],
                ratios_amp: dict[str, list[float]],
                df: pd.DataFrame, tf: str):
    lines = [
        f'ANÁLISIS DE FIBONACCI  [{tf}]',
        f'Filas: {len(df)} | Rango: {df["date"].iloc[0]} → {df["date"].iloc[-1]}',
        '=' * 60,
        '',
        'Niveles Fibonacci de referencia: 0.236, 0.382, 0.500, 0.618, 0.786, 1.618',
        '',
        '── RATIOS DE TIEMPO (apoyo EMA10 → EMA55 → EMA200) ──',
    ]

    if ratios_tiempo:
        arr = np.array(ratios_tiempo)
        arr_clip = arr[arr < np.percentile(arr, 95)]
        med = np.median(arr_clip)
        fib_near, dist_fib = fib_mas_cercano(med)
        lines += [
            f'  Secuencias encontradas: {len(ratios_tiempo)}',
            f'  Mediana del ratio:  {med:.4f}',
            f'  Media del ratio:    {arr_clip.mean():.4f}',
            f'  p25/p75:            {np.percentile(arr_clip,25):.4f} / {np.percentile(arr_clip,75):.4f}',
            f'  Nivel Fib más cercano a la mediana: {fib_near}  (distancia={dist_fib:.4f})',
            f'  Interpretación: si dist < 0.05 al nivel Fib, la proporción es notable',
            '',
        ]
    else:
        lines += ['  Sin datos suficientes', '']

    lines.append('── RATIOS DE AMPLITUD (valle/pico por EMA) ──')

    for col, label in [('dist_p10','EMA10'),('dist_p55','EMA55'),('dist_p200','EMA200')]:
        ratios = ratios_amp.get(col, [])
        if not ratios:
            lines.append(f'  {label}: sin datos')
            continue
        arr = np.array(ratios)
        arr_clip = arr[arr < 3]
        med = np.median(arr_clip)
        fib_near, dist_fib = fib_mas_cercano(med)
        lines += [
            f'  {label} ({col}):',
            f'    Pares pico/valle: {len(ratios)}',
            f'    Mediana ratio:    {med:.4f}',
            f'    p25/p75:          {np.percentile(arr_clip,25):.4f} / {np.percentile(arr_clip,75):.4f}',
            f'    Fib más cercano:  {fib_near}  (distancia={dist_fib:.4f})',
            '',
        ]

    out = os.path.join(RESULTS, f'{tf}_fibonacci_stats.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'  📄 {os.path.basename(out)}')


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    clean_files = sorted(glob.glob(os.path.join(RESULTS, '*_clean.csv')))
    if not clean_files:
        print('No se encontraron archivos _clean.csv en results/')
        return

    for path in clean_files:
        tf = timeframe_label(path)
        print(f'\n📂 {tf}')
        df = load(path)
        print(f'   {len(df)} filas')

        ratios_tiempo = calcular_ratios_tiempo(df)
        print(f'   Secuencias de tiempo EMA10→55→200: {len(ratios_tiempo)}')

        ratios_amp = calcular_ratios_amplitud(df)
        for col, r in ratios_amp.items():
            print(f'   Pares amplitud {col}: {len(r)}')

        plot_tiempos(ratios_tiempo, tf)
        plot_amplitudes(ratios_amp, tf)
        write_stats(ratios_tiempo, ratios_amp, df, tf)

    print('\n✅ Listo. Revisa la carpeta results/')


if __name__ == '__main__':
    main()
