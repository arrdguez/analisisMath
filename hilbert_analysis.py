"""
hilbert_analysis.py — Transformada de Hilbert: envolvente y frecuencia instantánea
────────────────────────────────────────────────────────────────────────────────────
Pregunta que responde:
  "¿La velocidad y amplitud de las oscilaciones cambian con el tiempo?
   ¿O siempre oscilan igual?"

La FFT te dice SI hay un ciclo de N velas, pero asume que ese ciclo
es CONSTANTE en todo el período. La Transformada de Hilbert va más lejos:
te dice si el ciclo se acelera o desacelera, si la amplitud crece o decrece.

Tres cosas que extrae:
  1. ENVOLVENTE   → la "altura" de la onda en cada momento
                    (¿está el mercado oscilando fuerte o suave ahora?)
  2. FASE         → en qué punto del ciclo está la serie en cada momento
                    (¿está en el pico, en el valle, a mitad de camino?)
  3. FRECUENCIA INSTANTÁNEA → qué tan rápido está oscilando AHORA
                    (¿el ciclo se está acelerando o alargando?)

Se aplica a dist_p10, dist_p55, dist_p200 (las distancias precio→EMA).

Genera en results/:
  - hilbert_{TF}_envolvente.png
  - hilbert_{TF}_frecuencia.png
  - hilbert_{TF}_resumen.txt

Uso:
  python hilbert_analysis.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import hilbert, detrend
from plot_style import BG_FIG, BG_AX, COLORS, estilo_ax

BASE    = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, 'results')

VARIABLES = {
    'dist_p10':  ('EMA10',  COLORS['dist_p10']),
    'dist_p55':  ('EMA55',  COLORS['dist_p55']),
    'dist_p200': ('EMA200', COLORS['dist_p200']),
}

# ── helpers ───────────────────────────────────────────────────────────────────

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['date'])
    return df.dropna(subset=['ema200']).reset_index(drop=True)


def timeframe_label(filename: str) -> str:
    return os.path.basename(filename).replace('_clean.csv', '').replace('.csv', '')


def analizar_hilbert(serie: np.ndarray) -> dict:
    """
    Aplica la Transformada de Hilbert a una serie.
    Primero quita la tendencia lineal para que el análisis
    sea sobre las oscilaciones puras, no sobre el drift.
    """
    s = detrend(serie)                     # quitar tendencia lineal
    analytic  = hilbert(s)                 # señal analítica compleja
    envolvente = np.abs(analytic)          # amplitud instantánea
    fase       = np.unwrap(np.angle(analytic))  # fase instantánea
    # frecuencia instantánea: derivada de la fase / 2π
    freq_inst  = np.diff(fase) / (2.0 * np.pi)
    # convertir a "período en velas" para que sea interpretable
    with np.errstate(divide='ignore', invalid='ignore'):
        periodo_inst = np.where(freq_inst > 0, 1.0 / freq_inst, np.nan)
    # recortar outliers para la gráfica
    periodo_inst = np.clip(periodo_inst, 0, np.nanpercentile(periodo_inst, 95) * 2)

    return {
        'serie':         s,
        'envolvente':    envolvente,
        'fase':          fase,
        'freq_inst':     freq_inst,
        'periodo_inst':  periodo_inst,
        'env_media':     float(np.mean(envolvente)),
        'env_std':       float(np.std(envolvente)),
        'periodo_mediana': float(np.nanmedian(periodo_inst)),
        'periodo_p25':   float(np.nanpercentile(periodo_inst, 25)),
        'periodo_p75':   float(np.nanpercentile(periodo_inst, 75)),
    }


# ── gráfica 1: serie + envolvente ─────────────────────────────────────────────

def plot_envolvente(df: pd.DataFrame, resultados: dict, tf: str):
    n_vars = len(resultados)
    fig, axes = plt.subplots(n_vars, 1, figsize=(18, 4 * n_vars),
                             facecolor=BG_FIG, sharex=True)
    if n_vars == 1:
        axes = [axes]
    fig.suptitle(f'Envolvente de amplitud (Hilbert)  [{tf}]',
                 fontsize=13, fontweight='bold', color='#111111')

    for ax, (col, res) in zip(axes, resultados.items()):
        label, color = VARIABLES[col]
        x = df['date'].values
        ax.plot(x, res['serie'], color=color, linewidth=0.7, alpha=0.8,
                label=f'{col} (sin tendencia lineal)')
        ax.plot(x,  res['envolvente'], color='#333333', linewidth=1.3,
                label=f'Envolvente +  (amplitud media={res["env_media"]:.2f}%)')
        ax.plot(x, -res['envolvente'], color='#333333', linewidth=1.3,
                label='Envolvente −')
        ax.fill_between(x,  res['envolvente'], -res['envolvente'],
                        alpha=0.08, color=color)
        ax.axhline(0, color='#888888', linewidth=0.6, linestyle='--')
        ax.legend(fontsize=7, loc='upper left')
        estilo_ax(ax,
                  xlabel='Fecha',
                  ylabel='Distancia a la EMA (%)',
                  title=f'{label}  —  amplitud media={res["env_media"]:.2f}%  '
                        f'std={res["env_std"]:.2f}%  '
                        f'(envolvente = techo/suelo de la onda)')

    plt.tight_layout()
    out = os.path.join(RESULTS, f'{tf}_hilbert_envolvente.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── gráfica 2: período instantáneo ───────────────────────────────────────────

def plot_frecuencia(df: pd.DataFrame, resultados: dict, tf: str):
    n_vars = len(resultados)
    fig, axes = plt.subplots(n_vars, 1, figsize=(18, 4 * n_vars),
                             facecolor=BG_FIG, sharex=True)
    if n_vars == 1:
        axes = [axes]
    fig.suptitle(f'Período instantáneo del ciclo (Hilbert)  [{tf}]',
                 fontsize=13, fontweight='bold', color='#111111')

    for ax, (col, res) in zip(axes, resultados.items()):
        label, color = VARIABLES[col]
        x = df['date'].values[:-1]
        p = res['periodo_inst']
        ax.plot(x, p, color=color, linewidth=0.7, alpha=0.85,
                label='período instantáneo (velas)')
        ax.axhline(res['periodo_mediana'], color='#111111', linewidth=1.2,
                   linestyle='--',
                   label=f'mediana={res["periodo_mediana"]:.0f} velas')
        ax.axhline(res['periodo_p25'], color=color, linewidth=0.8,
                   linestyle=':', alpha=0.7,
                   label=f'p25={res["periodo_p25"]:.0f} velas')
        ax.axhline(res['periodo_p75'], color=color, linewidth=0.8,
                   linestyle=':', alpha=0.7,
                   label=f'p75={res["periodo_p75"]:.0f} velas')
        ax.legend(fontsize=7, loc='upper left')
        estilo_ax(ax,
                  xlabel='Fecha',
                  ylabel='Duración del ciclo (número de velas)',
                  title=f'{label}  —  período típico: '
                        f'{res["periodo_p25"]:.0f}–{res["periodo_p75"]:.0f} velas  '
                        f'(mediana={res["periodo_mediana"]:.0f})  '
                        f'— línea sube = ciclo más lento, baja = más rápido')

    plt.tight_layout()
    out = os.path.join(RESULTS, f'{tf}_hilbert_frecuencia.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── reporte txt ───────────────────────────────────────────────────────────────

def write_resumen(resultados: dict, df: pd.DataFrame, tf: str):
    lines = [
        f'ANÁLISIS DE HILBERT  [{tf}]',
        f'Filas: {len(df)} | Rango: {df["date"].iloc[0]} → {df["date"].iloc[-1]}',
        '=' * 60,
        '',
        'Qué mide:',
        '  Envolvente  → amplitud de la oscilación en cada momento',
        '  Período     → cuántas velas dura el ciclo en cada momento',
        '  (Si el período cambia mucho: el ciclo NO es constante en el tiempo)',
        '=' * 60,
        '',
    ]

    for col, res in resultados.items():
        label = VARIABLES.get(col, (col, ''))[0]
        lines += [
            f'── {label} ({col}) ──',
            f'  Amplitud media:    {res["env_media"]:.3f}%',
            f'  Amplitud std:      {res["env_std"]:.3f}%  '
            f'(qué tanto varía la amplitud — mayor std = más irregular)',
            f'  Período mediana:   {res["periodo_mediana"]:.1f} velas',
            f'  Período p25/p75:   {res["periodo_p25"]:.1f} / {res["periodo_p75"]:.1f} velas',
            f'  Rango intercuartil del período: '
            f'{res["periodo_p75"] - res["periodo_p25"]:.1f} velas',
            f'  (Rango amplio = ciclo variable; rango estrecho = ciclo estable)',
            '',
        ]

    out = os.path.join(RESULTS, f'{tf}_hilbert_resumen.txt')
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

        resultados = {}
        for col in VARIABLES:
            serie = df[col].dropna().values
            resultados[col] = analizar_hilbert(serie)
            res = resultados[col]
            print(f'   {col}: amplitud_media={res["env_media"]:.2f}%  '
                  f'período_mediana={res["periodo_mediana"]:.0f} velas')

        plot_envolvente(df, resultados, tf)
        plot_frecuencia(df, resultados, tf)
        write_resumen(resultados, df, tf)

    print('\n✅ Listo. Revisa la carpeta results/')


if __name__ == '__main__':
    main()
