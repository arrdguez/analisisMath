"""
fft_analysis.py — Análisis de frecuencias (FFT) y ciclos
──────────────────────────────────────────────────────────
Fase 2: busca si las oscilaciones de dist_p10, dist_p55, dist_p200
tienen ciclos dominantes medibles (número de velas por ciclo).

Genera en results/:
  - fft_1D_espectro.png
  - fft_1D_ciclos.txt
  (idem para 4H y 1H)

Uso:
  python fft_analysis.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from plot_style import BG_FIG, BG_AX, COLORS, estilo_ax

BASE    = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, 'results')
TOP_N   = 5

# ── helpers ──────────────────────────────────────────────────────────────────

def load(path):
    df = pd.read_csv(path, parse_dates=['date'])
    return df.dropna(subset=['ema200']).reset_index(drop=True)


def timeframe_label(filename):
    name = os.path.basename(filename).upper()
    for tf in ('1D', '4H', '1H'):
        if tf in name:
            return tf
    return 'UNK'


def fft_top_cycles(signal, top_n=TOP_N):
    """
    Devuelve los top_n ciclos dominantes de una señal.
    Retorna lista de (ciclo_en_velas, amplitud, fraccion_energia)
    """
    n      = len(signal)
    # Quitar tendencia lineal para no contaminar bajas frecuencias
    signal = signal - np.linspace(signal[0], signal[-1], n)
    # Ventana de Hanning para reducir spectral leakage
    window = np.hanning(n)
    fft    = np.fft.rfft(signal * window)
    power  = np.abs(fft) ** 2
    freqs  = np.fft.rfftfreq(n)

    # ignorar DC (índice 0)
    power[0] = 0

    total_power = power.sum()
    sorted_idx  = np.argsort(power)[::-1]

    results = []
    for idx in sorted_idx[:top_n]:
        if freqs[idx] == 0:
            continue
        ciclo    = int(round(1.0 / freqs[idx]))
        amplitud = np.sqrt(power[idx])
        fraccion = power[idx] / total_power * 100
        results.append((ciclo, amplitud, fraccion))

    return freqs, power, results


# ── gráfica de espectro ───────────────────────────────────────────────────────

def plot_espectro(df, tf):
    signals = {
        'dist_p10':  (COLORS['dist_p10'],  'Precio vs EMA10'),
        'dist_p55':  (COLORS['dist_p55'],  'Precio vs EMA55'),
        'dist_p200': (COLORS['dist_p200'], 'Precio vs EMA200'),
    }

    fig, axes = plt.subplots(len(signals), 1, figsize=(16, 11), facecolor=BG_FIG)
    fig.suptitle(f'Espectro FFT — ciclos dominantes  [{tf}]',
                 fontsize=14, fontweight='bold', color='#111111')

    for ax, (col, (color, label)) in zip(axes, signals.items()):
        signal = df[col].dropna().values
        if len(signal) < 20:
            continue

        freqs, power, top = fft_top_cycles(signal)

        # Convertir frecuencias a velas-por-ciclo para el eje X
        with np.errstate(divide='ignore'):
            ciclos_eje = np.where(freqs > 0, 1.0 / freqs, np.nan)

        ax.fill_between(ciclos_eje, power, alpha=0.35, color=color)
        ax.plot(ciclos_eje, power, color=color, linewidth=1.0)

        # marcar picos top
        for ciclo, amplitud, fraccion in top:
            ax.axvline(ciclo, color='#333333', linewidth=0.8,
                       linestyle='--', alpha=0.7)
            ymax = ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else power.max()
            ax.text(ciclo, ymax * 0.82,
                    f'{ciclo}v\n{fraccion:.1f}%',
                    color='#111111', fontsize=7, ha='center',
                    bbox=dict(boxstyle='round,pad=0.2', fc='white',
                              ec='#cccccc', alpha=0.85))

        ax.set_xscale('log')
        ax.set_xlim(2, len(signal) // 2)
        top_label = ', '.join(f'{c}v ({f:.1f}%)' for c, _, f in top)
        estilo_ax(ax,
                  xlabel='Duración del ciclo (número de velas)  —  escala logarítmica',
                  ylabel='Potencia espectral',
                  title=f'{label}  —  top ciclos: {top_label}')

    plt.tight_layout()
    out = os.path.join(RESULTS, f'fft_{tf}_espectro.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── reporte txt ───────────────────────────────────────────────────────────────

def write_ciclos(df, tf):
    lines = [
        f'ANÁLISIS FFT — CICLOS DOMINANTES  [{tf}]',
        f'Filas: {len(df)} | Rango: {df["date"].iloc[0]} → {df["date"].iloc[-1]}',
        '=' * 60, '',
    ]
    for col in ['dist_p10', 'dist_p55', 'dist_p200', 'dist_10_55', 'dist_55_200']:
        signal = df[col].dropna().values
        if len(signal) < 20:
            continue
        _, _, top = fft_top_cycles(signal)
        lines.append(f'  {col}:')
        for i, (ciclo, amplitud, fraccion) in enumerate(top, 1):
            lines.append(f'    #{i}  {ciclo} velas  ({fraccion:.2f}% de la energía)')
        lines.append('')
    out = os.path.join(RESULTS, f'fft_{tf}_ciclos.txt')
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
        print(f'\n📂 {tf}  ←  {os.path.basename(path)}')
        df = load(path)
        print(f'   {len(df)} filas')
        plot_espectro(df, tf)
        write_ciclos(df, tf)
    print('\n✅ Listo. Revisa la carpeta results/')


if __name__ == '__main__':
    main()
