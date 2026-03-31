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

BASE    = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, 'results')

# ── parámetros ────────────────────────────────────────────────────────────────
VENTANA_MIN  = 5    # velas a cada lado para detectar mínimo local
REBOTE_VELAS = 10   # velas hacia adelante para medir rebote

# ── helpers ───────────────────────────────────────────────────────────────────

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['date'])
    return df.dropna(subset=['ema200']).reset_index(drop=True)


def timeframe_label(filename: str) -> str:
    name = os.path.basename(filename).upper()
    for tf in ('1D', '4H', '1H'):
        if tf in name:
            return tf
    return 'UNK'


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
    """
    apoyos = {'dist_p10': df_eventos, 'dist_p55': df_eventos, ...}
    """
    fig, axes = plt.subplots(3, 2, figsize=(18, 12), facecolor='#0f0f1a')
    fig.suptitle(f'Profundidad de Apoyos en EMAs  [{tf}]',
                 fontsize=14, fontweight='bold')

    configs = [
        ('dist_p10',  'EMA10',  '#4fc3f7', axes[0, 0], axes[0, 1]),
        ('dist_p55',  'EMA55',  '#fff176', axes[1, 0], axes[1, 1]),
        ('dist_p200', 'EMA200', '#ef9a9a', axes[2, 0], axes[2, 1]),
    ]

    for col, label, color, ax_serie, ax_hist in configs:
        ev = apoyos.get(col)
        if ev is None or ev.empty:
            continue

        # — Serie de profundidades en el tiempo —
        ax_serie.plot(df['date'], df[col], color='#444', linewidth=0.5,
                      alpha=0.6)
        ax_serie.scatter(ev['date'], ev['profundidad'],
                         color=color, s=15, zorder=5, alpha=0.8)
        ax_serie.axhline(0, color='white', linewidth=0.5, linestyle='--')
        # líneas de percentiles
        for pct, val in zip([10, 25, 75, 90],
                            np.percentile(ev['profundidad'], [10, 25, 75, 90])):
            ax_serie.axhline(val, color=color, linewidth=0.4,
                             linestyle=':', alpha=0.5,
                             label=f'p{pct}={val:.1f}%')
        ax_serie.set_title(f'Apoyos en {label} ({len(ev)} eventos)', fontsize=9)
        ax_serie.set_facecolor('#1a1a2e')
        ax_serie.tick_params(labelsize=7)
        ax_serie.legend(fontsize=6, ncol=2)

        # — Histograma de profundidades —
        data = ev['profundidad'].dropna()
        ax_hist.hist(data, bins=40, color=color, alpha=0.8, edgecolor='none',
                     orientation='horizontal')
        ax_hist.axhline(0, color='white', linewidth=0.5, linestyle='--')
        ax_hist.axhline(data.median(), color='cyan', linewidth=1,
                        linestyle=':', label=f'mediana={data.median():.1f}%')
        p10, p25, p75, p90 = np.percentile(data, [10, 25, 75, 90])
        for pval in [p10, p25, p75, p90]:
            ax_hist.axhline(pval, color=color, linewidth=0.6,
                            linestyle='--', alpha=0.6)
        ax_hist.set_title(f'Distribución profundidad {label}', fontsize=9)
        ax_hist.legend(fontsize=7)
        ax_hist.set_facecolor('#1a1a2e')
        ax_hist.tick_params(labelsize=7)

    plt.tight_layout()
    out = os.path.join(RESULTS, f'apoyo_{tf}_detalle.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── gráfica 2: rebote tras el apoyo ──────────────────────────────────────────

def plot_rebotes(apoyos: dict, tf: str):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor='#0f0f1a')
    fig.suptitle(
        f'Rebote {REBOTE_VELAS} velas después del apoyo  [{tf}]',
        fontsize=14, fontweight='bold')

    configs = [
        ('dist_p10',  'EMA10',  '#4fc3f7', axes[0]),
        ('dist_p55',  'EMA55',  '#fff176', axes[1]),
        ('dist_p200', 'EMA200', '#ef9a9a', axes[2]),
    ]

    for col, label, color, ax in configs:
        ev = apoyos.get(col)
        if ev is None or ev.empty:
            continue

        data = ev['rebote_pct'].dropna()
        positivos = (data > 0).sum()
        total     = len(data)
        tasa      = positivos / total * 100 if total > 0 else 0

        ax.hist(data, bins=50, color=color, alpha=0.8, edgecolor='none')
        ax.axvline(0, color='white', linewidth=1, linestyle='--')
        ax.axvline(data.median(), color='cyan', linewidth=1.2,
                   label=f'mediana={data.median():.1f}%')
        ax.set_title(
            f'Apoyo en {label}\n'
            f'{total} eventos | {tasa:.0f}% subieron\n'
            f'mediana rebote: {data.median():.1f}%',
            fontsize=9)
        ax.legend(fontsize=7)
        ax.set_xlabel('Cambio de precio (%)', fontsize=8)
        ax.set_facecolor('#1a1a2e')
        ax.tick_params(labelsize=7)

    plt.tight_layout()
    out = os.path.join(RESULTS, f'apoyo_{tf}_rebote.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=fig.get_facecolor())
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

    out = os.path.join(RESULTS, f'apoyo_{tf}_stats.txt')
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
