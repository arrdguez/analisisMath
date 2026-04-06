"""
apoyo_stats.py — Estadísticas de apoyos en cada EMA
─────────────────────────────────────────────────────
Fase 3: detecta eventos de "apoyo" (mínimos locales de dist_pX)
y mide su profundidad, duración y qué pasa después del rebote.

Un "apoyo" se define como:
  - dist_pX llega a un mínimo local (ventana configurable)
  - el mínimo es negativo (precio por debajo o cerca de la EMA)
  - después de N velas el precio sube (rebote)

Genera en results/:
  - apoyo_1D_detalle.png    ← profundidades históricas
  - apoyo_1D_rebote.png     ← cuánto subió después del apoyo
  - apoyo_1D_stats.txt      ← tabla con todos los eventos

Uso:
  python apoyo_stats.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import argrelmin
from plot_style import BG_FIG, BG_AX, COLORS, C_NEG, estilo_ax

BASE    = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, 'results')

VENTANA_MIN  = 5
REBOTE_VELAS = 10

# ── helpers ───────────────────────────────────────────────────────────────────

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['date'])
    return df.dropna(subset=['ema200']).reset_index(drop=True)


def timeframe_label(filename: str) -> str:
    return os.path.basename(filename).replace('_clean.csv', '').replace('.csv', '')


def detectar_apoyos(df: pd.DataFrame, col: str,
                    ventana: int = VENTANA_MIN) -> pd.DataFrame:
    """
    Detecta mínimos locales de la columna col.
    Devuelve DataFrame con los eventos de apoyo y su contexto.
    """
    signal = df[col].ffill().values
    # índices de mínimos locales
    idx_mins = argrelmin(signal, order=ventana)[0]

    eventos = []
    for i in idx_mins:
        profundidad = signal[i]
        # rebote: cambio de close en las siguientes REBOTE_VELAS velas
        if i + REBOTE_VELAS < len(df):
            close_now    = df['close'].iloc[i]
            close_future = df['close'].iloc[i + REBOTE_VELAS]
            rebote_pct   = (close_future - close_now) / close_now * 100
        else:
            rebote_pct = np.nan

        eventos.append({
            'date':        df['date'].iloc[i],
            'close':       df['close'].iloc[i],
            'profundidad': profundidad,   # valor de dist_pX en el mínimo
            'rebote_pct':  rebote_pct,    # % que subió/bajó tras N velas
        })

    return pd.DataFrame(eventos)


# ── gráfica 1: profundidades históricas ──────────────────────────────────────

def plot_profundidades(df: pd.DataFrame, apoyos: dict, tf: str):
    fig, axes = plt.subplots(3, 2, figsize=(18, 13), facecolor=BG_FIG)
    fig.suptitle(f'Profundidad de Apoyos en EMAs  [{tf}]',
                 fontsize=14, fontweight='bold', color='#111111')

    configs = [
        ('dist_p10',  'EMA10',  COLORS['dist_p10'],  axes[0, 0], axes[0, 1]),
        ('dist_p55',  'EMA55',  COLORS['dist_p55'],  axes[1, 0], axes[1, 1]),
        ('dist_p200', 'EMA200', COLORS['dist_p200'], axes[2, 0], axes[2, 1]),
    ]

    for col, label, color, ax_serie, ax_hist in configs:
        ev = apoyos.get(col)
        if ev is None or ev.empty:
            continue

        # — Serie histórica con apoyos marcados —
        ax_serie.plot(df['date'], df[col], color='#aaaaaa', linewidth=0.5,
                      alpha=0.8, label=col)
        ax_serie.scatter(ev['date'], ev['profundidad'],
                         color=color, s=18, zorder=5, alpha=0.85,
                         label=f'apoyos (n={len(ev)})')
        ax_serie.axhline(0, color='#888888', linewidth=0.8, linestyle='--')
        for pct, val in zip([10, 25, 75, 90],
                            np.percentile(ev['profundidad'], [10, 25, 75, 90])):
            ax_serie.axhline(val, color=color, linewidth=0.7,
                             linestyle=':', alpha=0.7,
                             label=f'p{pct}={val:.1f}%')
        ax_serie.legend(fontsize=6, ncol=2)
        estilo_ax(ax_serie,
                  xlabel='Fecha',
                  ylabel=f'dist_p{label[-3:]} (%)',
                  title=f'Apoyos detectados en {label}  ({len(ev)} eventos)')

        # — Histograma de profundidades —
        data = ev['profundidad'].dropna()
        ax_hist.hist(data, bins=40, color=color, alpha=0.75, edgecolor='none',
                     orientation='horizontal', label=f'n={len(data)}')
        ax_hist.axhline(0, color='#888888', linewidth=0.8, linestyle='--')
        ax_hist.axhline(data.median(), color='#111111', linewidth=1.2,
                        linestyle='-', label=f'mediana={data.median():.1f}%')
        p10, p25, p75, p90 = np.percentile(data, [10, 25, 75, 90])
        for pval, lbl in zip([p10, p90], ['p10', 'p90']):
            ax_hist.axhline(pval, color=color, linewidth=0.8,
                            linestyle='--', alpha=0.7, label=f'{lbl}={pval:.1f}%')
        ax_hist.legend(fontsize=7)
        estilo_ax(ax_hist,
                  xlabel='Número de eventos',
                  ylabel=f'Profundidad del apoyo (%)',
                  title=f'Distribución de profundidades — {label}')

    plt.tight_layout()
    out = os.path.join(RESULTS, f'{tf}_apoyo_detalle.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── gráfica 2: rebote tras el apoyo ──────────────────────────────────────────

def plot_rebotes(apoyos: dict, tf: str):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor=BG_FIG)
    fig.suptitle(
        f'Rebote {REBOTE_VELAS} velas después del apoyo  [{tf}]',
        fontsize=14, fontweight='bold', color='#111111')

    configs = [
        ('dist_p10',  'EMA10',  COLORS['dist_p10'],  axes[0]),
        ('dist_p55',  'EMA55',  COLORS['dist_p55'],  axes[1]),
        ('dist_p200', 'EMA200', COLORS['dist_p200'], axes[2]),
    ]

    for col, label, color, ax in configs:
        ev = apoyos.get(col)
        if ev is None or ev.empty:
            continue

        data      = ev['rebote_pct'].dropna()
        positivos = (data > 0).sum()
        total     = len(data)
        tasa      = positivos / total * 100 if total > 0 else 0

        ax.hist(data, bins=50, color=color, alpha=0.75, edgecolor='none',
                label=f'n={total}')
        ax.axvline(0, color='#888888', linewidth=1, linestyle='--', label='0%')
        ax.axvline(data.median(), color='#111111', linewidth=1.2,
                   label=f'mediana={data.median():.1f}%')
        ax.legend(fontsize=7)
        estilo_ax(ax,
                  xlabel=f'Cambio de precio en {REBOTE_VELAS} velas después del apoyo (%)',
                  ylabel='Número de eventos',
                  title=f'Apoyo en {label}\n'
                        f'{total} eventos  |  {tasa:.0f}% subieron  |  '
                        f'mediana rebote: {data.median():.1f}%')

    plt.tight_layout()
    out = os.path.join(RESULTS, f'{tf}_apoyo_rebote.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── reporte de eventos → txt ──────────────────────────────────────────────────

def write_stats(apoyos: dict, df: pd.DataFrame, tf: str):
    lines = [
        f'ESTADÍSTICAS DE APOYOS  [{tf}]',
        f'Filas: {len(df)} | Rango: {df["date"].iloc[0]} → {df["date"].iloc[-1]}',
        f'Parámetros: ventana_min={VENTANA_MIN} velas, rebote={REBOTE_VELAS} velas',
        '=' * 60,
        '',
    ]

    for col, label in [('dist_p10', 'EMA10'), ('dist_p55', 'EMA55'),
                        ('dist_p200', 'EMA200')]:
        ev = apoyos.get(col)
        if ev is None or ev.empty:
            continue

        data   = ev['profundidad'].dropna()
        rebote = ev['rebote_pct'].dropna()
        tasa   = (rebote > 0).sum() / len(rebote) * 100 if len(rebote) > 0 else 0

        p5, p10, p25, p50, p75, p90, p95 = np.percentile(
            data, [5, 10, 25, 50, 75, 90, 95])

        lines += [
            f'── Apoyo en {label} ({len(ev)} eventos) ──',
            f'  Profundidad (dist precio → {label}):',
            f'    mediana = {p50:+.2f}%',
            f'    p10/p90 = {p10:+.2f}% / {p90:+.2f}%',
            f'    p5/p95  = {p5:+.2f}% / {p95:+.2f}%',
            f'    p25/p75 = {p25:+.2f}% / {p75:+.2f}%',
            f'    min/max = {data.min():+.2f}% / {data.max():+.2f}%',
            f'  Rebote {REBOTE_VELAS} velas después:',
            f'    tasa éxito (subió) = {tasa:.1f}%',
            f'    mediana rebote     = {rebote.median():+.2f}%',
            f'    p25/p75 rebote     = {rebote.quantile(0.25):+.2f}% / {rebote.quantile(0.75):+.2f}%',
            '',
        ]

    out = os.path.join(RESULTS, f'{tf}_apoyo_stats.txt')
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

        apoyos = {}
        for col in ['dist_p10', 'dist_p55', 'dist_p200']:
            ev = detectar_apoyos(df, col)
            print(f'   {col}: {len(ev)} apoyos detectados')
            apoyos[col] = ev

        plot_profundidades(df, apoyos, tf)
        plot_rebotes(apoyos, tf)
        write_stats(apoyos, df, tf)

    print('\n✅ Listo. Revisa la carpeta results/')


if __name__ == '__main__':
    main()
