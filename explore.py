"""
explore.py — Análisis exploratorio visual
─────────────────────────────────────────
Fase 1: describe y grafica las oscilaciones de las 3 distancias
y el ratio armónico. No hace predicciones, solo muestra qué hay.

Genera en results/:
  - explore_1D_distancias.png
  - explore_1D_ratio.png
  - explore_1D_stats.txt
  (idem para 4H y 1H)

Uso:
  python explore.py
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')           # sin ventana, guarda a archivo
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE    = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, 'results')

# ── helpers ──────────────────────────────────────────────────────────────────

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['date'])
    df = df.dropna(subset=['ema200']).reset_index(drop=True)
    return df


def timeframe_label(filename: str) -> str:
    name = os.path.basename(filename).upper()
    for tf in ('1D', '4H', '1H'):
        if tf in name:
            return tf
    return 'UNK'


def stats_block(df: pd.DataFrame, col: str) -> str:
    s = df[col].dropna()
    pcts = np.percentile(s, [5, 25, 50, 75, 95])
    return (
        f"  {col}:\n"
        f"    media   = {s.mean():+.3f}%\n"
        f"    std     = {s.std():.3f}\n"
        f"    p5/p95  = {pcts[0]:+.3f} / {pcts[4]:+.3f}\n"
        f"    p25/p75 = {pcts[1]:+.3f} / {pcts[3]:+.3f}\n"
        f"    mediana = {pcts[2]:+.3f}\n"
        f"    min/max = {s.min():+.3f} / {s.max():+.3f}\n"
    )

# ── gráfica 1: distancias precio → EMAs ──────────────────────────────────────

def plot_distancias(df: pd.DataFrame, tf: str):
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle(f'Distancias Precio → EMAs  [{tf}]', fontsize=14, fontweight='bold')
    gs  = gridspec.GridSpec(4, 2, figure=fig, hspace=0.45, wspace=0.3)

    cols_dist = [
        ('dist_p10',  'EMA10',  '#4fc3f7'),
        ('dist_p55',  'EMA55',  '#fff176'),
        ('dist_p200', 'EMA200', '#ef9a9a'),
    ]

    # — Serie temporal de cada distancia (columna izquierda) —
    for i, (col, label, color) in enumerate(cols_dist):
        ax = fig.add_subplot(gs[i, 0])
        ax.plot(df['date'], df[col], color=color, linewidth=0.7, alpha=0.9)
        ax.axhline(0, color='white', linewidth=0.5, linestyle='--')
        ax.fill_between(df['date'], df[col], 0,
                        where=df[col] > 0, alpha=0.15, color='lime')
        ax.fill_between(df['date'], df[col], 0,
                        where=df[col] < 0, alpha=0.15, color='red')
        ax.set_ylabel(f'% vs {label}', fontsize=8)
        ax.set_title(f'Precio vs {label}', fontsize=9)
        ax.tick_params(labelsize=7)
        ax.set_facecolor('#1a1a2e')
        fig.patch.set_facecolor('#0f0f1a')

    # — Histogramas (columna derecha) —
    for i, (col, label, color) in enumerate(cols_dist):
        ax = fig.add_subplot(gs[i, 1])
        data = df[col].dropna()
        ax.hist(data, bins=80, color=color, alpha=0.8, edgecolor='none')
        ax.axvline(0,           color='white', linewidth=1, linestyle='--')
        ax.axvline(data.median(),color='cyan',  linewidth=1, linestyle=':',
                   label=f'mediana {data.median():+.1f}%')
        # percentiles 5 y 95
        p5, p95 = np.percentile(data, [5, 95])
        ax.axvline(p5,  color='orange', linewidth=0.8, linestyle=':',
                   label=f'p5={p5:+.1f}%')
        ax.axvline(p95, color='orange', linewidth=0.8, linestyle=':',
                   label=f'p95={p95:+.1f}%')
        ax.legend(fontsize=6)
        ax.set_title(f'Histograma {label}', fontsize=9)
        ax.tick_params(labelsize=7)
        ax.set_facecolor('#1a1a2e')

    # — Precio de fondo en fila 4 —
    ax_p = fig.add_subplot(gs[3, :])
    ax_p.plot(df['date'], df['close'], color='white', linewidth=0.6)
    ax_p.set_title('Precio BTC (referencia)', fontsize=9)
    ax_p.tick_params(labelsize=7)
    ax_p.set_facecolor('#1a1a2e')

    out = os.path.join(RESULTS, f'explore_{tf}_distancias.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f'  📊 {os.path.basename(out)}')

# ── gráfica 2: dist entre medias y ratio armónico ────────────────────────────

def plot_ratio(df: pd.DataFrame, tf: str):
    fig, axes = plt.subplots(3, 1, figsize=(18, 10), facecolor='#0f0f1a')
    fig.suptitle(f'Relaciones entre EMAs y Ratio Armónico  [{tf}]',
                 fontsize=14, fontweight='bold')

    # dist_10_55
    ax = axes[0]
    ax.plot(df['date'], df['dist_10_55'], color='#4fc3f7', linewidth=0.7)
    ax.axhline(0, color='white', linewidth=0.5, linestyle='--')
    ax.fill_between(df['date'], df['dist_10_55'], 0,
                    where=df['dist_10_55'] > 0, alpha=0.15, color='lime')
    ax.fill_between(df['date'], df['dist_10_55'], 0,
                    where=df['dist_10_55'] < 0, alpha=0.15, color='red')
    ax.set_ylabel('dist_10_55 (%)', fontsize=8)
    ax.set_title('EMA10 vs EMA55 (azul = alcista)', fontsize=9)
    ax.set_facecolor('#1a1a2e')
    ax.tick_params(labelsize=7)

    # dist_55_200
    ax = axes[1]
    ax.plot(df['date'], df['dist_55_200'], color='#fff176', linewidth=0.7)
    ax.axhline(0, color='white', linewidth=0.5, linestyle='--')
    ax.fill_between(df['date'], df['dist_55_200'], 0,
                    where=df['dist_55_200'] > 0, alpha=0.15, color='lime')
    ax.fill_between(df['date'], df['dist_55_200'], 0,
                    where=df['dist_55_200'] < 0, alpha=0.15, color='red')
    ax.set_ylabel('dist_55_200 (%)', fontsize=8)
    ax.set_title('EMA55 vs EMA200 (tendencia de fondo)', fontsize=9)
    ax.set_facecolor('#1a1a2e')
    ax.tick_params(labelsize=7)

    # ratio armónico — recortado para legibilidad
    ratio = df['ratio_armonico'].clip(-3, 3)
    ax = axes[2]
    ax.plot(df['date'], ratio, color='#ffb74d', linewidth=0.7)
    ax.axhline(0,   color='white',  linewidth=0.5, linestyle='--')
    ax.axhline(1,   color='lime',   linewidth=0.5, linestyle=':',  label='ratio=1')
    ax.axhline(-1,  color='red',    linewidth=0.5, linestyle=':',  label='ratio=-1')
    ax.axhline(0.5, color='cyan',   linewidth=0.4, linestyle='--', label='ratio=0.5')
    ax.fill_between(df['date'], ratio, 0,
                    where=ratio > 0, alpha=0.12, color='lime')
    ax.fill_between(df['date'], ratio, 0,
                    where=ratio < 0, alpha=0.12, color='red')
    ax.set_ylabel('Ratio (clip ±3)', fontsize=8)
    ax.set_title('Ratio Armónico = dist_10_55 / dist_55_200', fontsize=9)
    ax.legend(fontsize=7, loc='upper left')
    ax.set_facecolor('#1a1a2e')
    ax.tick_params(labelsize=7)

    plt.tight_layout()
    out = os.path.join(RESULTS, f'explore_{tf}_ratio.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f'  📊 {os.path.basename(out)}')

# ── estadísticas descriptivas → txt ──────────────────────────────────────────

def write_stats(df: pd.DataFrame, tf: str):
    lines = [
        f'ESTADÍSTICAS DESCRIPTIVAS — {tf}',
        f'Filas: {len(df)} | Rango: {df["date"].iloc[0]} → {df["date"].iloc[-1]}',
        '=' * 60,
        '',
        '── Distancias precio → EMA (%) ──',
    ]
    for col in ['dist_p10', 'dist_p55', 'dist_p200']:
        lines.append(stats_block(df, col))

    lines += ['── Distancias entre EMAs (%) ──']
    for col in ['dist_10_55', 'dist_55_200']:
        lines.append(stats_block(df, col))

    lines += ['── Ratio Armónico ──']
    ra = df['ratio_armonico'].replace([np.inf, -np.inf], np.nan).dropna()
    ra_clip = ra.clip(-5, 5)
    p5, p25, p50, p75, p95 = np.percentile(ra_clip, [5, 25, 50, 75, 95])
    lines.append(
        f"  ratio_armonico (valores extremos recortados a ±5):\n"
        f"    media   = {ra_clip.mean():+.3f}\n"
        f"    std     = {ra_clip.std():.3f}\n"
        f"    p5/p95  = {p5:+.3f} / {p95:+.3f}\n"
        f"    p25/p75 = {p25:+.3f} / {p75:+.3f}\n"
        f"    mediana = {p50:+.3f}\n"
    )

    lines += [
        '',
        '── Pendientes de EMAs (%) ──',
    ]
    for col in ['slope10', 'slope55', 'slope200']:
        lines.append(stats_block(df, col))

    out = os.path.join(RESULTS, f'explore_{tf}_stats.txt')
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
        print(f'   {len(df)} filas con datos completos')
        plot_distancias(df, tf)
        plot_ratio(df, tf)
        write_stats(df, tf)

    print('\n✅ Listo. Revisa la carpeta results/')


if __name__ == '__main__':
    main()
