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
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE    = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, 'results')

# ── paleta legible (fondo blanco) ────────────────────────────────────────────
BG_FIG  = 'white'
BG_AX   = '#f7f9fc'
C_ZERO  = '#888888'
COLORS  = {
    'dist_p10':  '#1565c0',   # azul oscuro
    'dist_p55':  '#e65100',   # naranja oscuro
    'dist_p200': '#2e7d32',   # verde oscuro
    'dist_10_55':  '#6a1b9a', # morado
    'dist_55_200': '#c62828', # rojo oscuro
    'ratio':     '#f57f17',   # ámbar
    'precio':    '#37474f',   # gris oscuro
}

# ── helpers ──────────────────────────────────────────────────────────────────

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['date'])
    df = df.dropna(subset=['ema200']).reset_index(drop=True)
    return df


def timeframe_label(filename: str) -> str:
    return os.path.basename(filename).replace('_clean.csv', '').replace('.csv', '')


def estilo_ax(ax, xlabel='', ylabel='', title=''):
    """Aplica estilo uniforme legible a un eje."""
    ax.set_facecolor(BG_AX)
    ax.tick_params(labelsize=8, colors='#222222')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for spine in ax.spines.values():
        spine.set_color('#cccccc')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9, color='#333333')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9, color='#333333')
    if title:
        ax.set_title(title, fontsize=10, color='#111111', fontweight='bold', pad=6)


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
    fig = plt.figure(figsize=(18, 12), facecolor=BG_FIG)
    fig.suptitle(f'Distancias Precio → EMAs  [{tf}]',
                 fontsize=14, fontweight='bold', color='#111111', y=0.98)
    gs = gridspec.GridSpec(4, 2, figure=fig, hspace=0.55, wspace=0.35)

    cols_dist = [
        ('dist_p10',  'EMA10',  COLORS['dist_p10']),
        ('dist_p55',  'EMA55',  COLORS['dist_p55']),
        ('dist_p200', 'EMA200', COLORS['dist_p200']),
    ]

    # — Serie temporal (columna izquierda) —
    for i, (col, label, color) in enumerate(cols_dist):
        ax = fig.add_subplot(gs[i, 0])
        ax.plot(df['date'], df[col], color=color, linewidth=0.8, alpha=0.9,
                label=col)
        ax.axhline(0, color=C_ZERO, linewidth=0.8, linestyle='--', label='0%')
        ax.fill_between(df['date'], df[col], 0,
                        where=df[col] > 0, alpha=0.18, color=color)
        ax.fill_between(df['date'], df[col], 0,
                        where=df[col] < 0, alpha=0.18, color='#e53935')
        ax.legend(fontsize=7, loc='upper left')
        estilo_ax(ax,
                  xlabel='Fecha',
                  ylabel='Distancia (%)',
                  title=f'Precio vs {label} — dist_{col[-3:]}')

    # — Histogramas (columna derecha) —
    for i, (col, label, color) in enumerate(cols_dist):
        ax = fig.add_subplot(gs[i, 1])
        data = df[col].dropna()
        ax.hist(data, bins=80, color=color, alpha=0.75, edgecolor='none',
                label=f'n={len(data)}')
        ax.axvline(0, color=C_ZERO, linewidth=1, linestyle='--', label='0%')
        med = data.median()
        p5, p95 = np.percentile(data, [5, 95])
        ax.axvline(med, color='#111111', linewidth=1.2, linestyle='-',
                   label=f'mediana={med:+.1f}%')
        ax.axvline(p5,  color='#e53935', linewidth=0.9, linestyle=':',
                   label=f'p5={p5:+.1f}%')
        ax.axvline(p95, color='#1565c0', linewidth=0.9, linestyle=':',
                   label=f'p95={p95:+.1f}%')
        ax.legend(fontsize=6, ncol=2)
        estilo_ax(ax,
                  xlabel=f'dist_{col[-3:]} (%)',
                  ylabel='Número de días',
                  title=f'Distribución histórica — Precio vs {label}')

    # — Precio de referencia (fila 4) —
    ax_p = fig.add_subplot(gs[3, :])
    ax_p.plot(df['date'], df['close'], color=COLORS['precio'], linewidth=0.7,
              label='Precio cierre')
    ax_p.legend(fontsize=7)
    estilo_ax(ax_p,
              xlabel='Fecha',
              ylabel='Precio (USD)',
              title='Precio de cierre (referencia temporal)')

    out = os.path.join(RESULTS, f'{tf}_explore_distancias.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')

# ── gráfica 2: dist entre medias y ratio armónico ────────────────────────────

def plot_ratio(df: pd.DataFrame, tf: str):
    fig, axes = plt.subplots(3, 1, figsize=(18, 11), facecolor=BG_FIG)
    fig.suptitle(f'Relaciones entre EMAs y Ratio Armónico  [{tf}]',
                 fontsize=14, fontweight='bold', color='#111111', y=0.99)

    # dist_10_55
    ax = axes[0]
    c = COLORS['dist_10_55']
    ax.plot(df['date'], df['dist_10_55'], color=c, linewidth=0.8, label='dist_10_55')
    ax.axhline(0, color=C_ZERO, linewidth=0.8, linestyle='--', label='0%')
    ax.fill_between(df['date'], df['dist_10_55'], 0,
                    where=df['dist_10_55'] > 0, alpha=0.15, color=c)
    ax.fill_between(df['date'], df['dist_10_55'], 0,
                    where=df['dist_10_55'] < 0, alpha=0.15, color='#e53935')
    ax.legend(fontsize=8)
    estilo_ax(ax,
              xlabel='Fecha',
              ylabel='(EMA10 − EMA55) / EMA55 × 100 (%)',
              title='Separación EMA10 vs EMA55  —  positivo = EMA10 sobre EMA55')

    # dist_55_200
    ax = axes[1]
    c = COLORS['dist_55_200']
    ax.plot(df['date'], df['dist_55_200'], color=c, linewidth=0.8, label='dist_55_200')
    ax.axhline(0, color=C_ZERO, linewidth=0.8, linestyle='--', label='0%')
    ax.fill_between(df['date'], df['dist_55_200'], 0,
                    where=df['dist_55_200'] > 0, alpha=0.15, color=c)
    ax.fill_between(df['date'], df['dist_55_200'], 0,
                    where=df['dist_55_200'] < 0, alpha=0.15, color='#e53935')
    ax.legend(fontsize=8)
    estilo_ax(ax,
              xlabel='Fecha',
              ylabel='(EMA55 − EMA200) / EMA200 × 100 (%)',
              title='Separación EMA55 vs EMA200  —  tendencia de fondo del activo')

    # ratio armónico
    ratio = df['ratio_armonico'].clip(-3, 3)
    ax = axes[2]
    c = COLORS['ratio']
    ax.plot(df['date'], ratio, color=c, linewidth=0.8, label='ratio_armonico (clip ±3)')
    ax.axhline(0,    color=C_ZERO,   linewidth=0.8, linestyle='--', label='0')
    ax.axhline(1,    color='#2e7d32', linewidth=0.7, linestyle=':',  label='ratio = 1')
    ax.axhline(-1,   color='#e53935', linewidth=0.7, linestyle=':',  label='ratio = −1')
    ax.axhline(0.5,  color='#1565c0', linewidth=0.6, linestyle='--', label='ratio = 0.5')
    ax.fill_between(df['date'], ratio, 0,
                    where=ratio > 0, alpha=0.12, color=c)
    ax.fill_between(df['date'], ratio, 0,
                    where=ratio < 0, alpha=0.12, color='#e53935')
    ax.legend(fontsize=7, ncol=3)
    estilo_ax(ax,
              xlabel='Fecha',
              ylabel='dist_10_55 / dist_55_200  (adimensional)',
              title='Ratio Armónico = dist_10_55 / dist_55_200  (recortado a ±3)')

    plt.tight_layout()
    out = os.path.join(RESULTS, f'{tf}_explore_ratio.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
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

    lines += ['', '── Pendientes de EMAs (%) ──']
    for col in ['slope10', 'slope55', 'slope200']:
        lines.append(stats_block(df, col))

    out = os.path.join(RESULTS, f'{tf}_explore_stats.txt')
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
        print(f'   {len(df)} filas con datos completos')
        plot_distancias(df, tf)
        plot_ratio(df, tf)
        write_stats(df, tf)

    print('\n✅ Listo. Revisa la carpeta results/')


if __name__ == '__main__':
    main()
