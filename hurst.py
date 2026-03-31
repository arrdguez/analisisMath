"""
hurst.py — Exponente de Hurst y memoria de las series
──────────────────────────────────────────────────────
Pregunta que responde:
  "¿Las oscilaciones de cada distancia tienen MEMORIA?
   ¿O son completamente aleatorias?"

El exponente de Hurst H dice:
  H > 0.5  → la serie tiene MEMORIA → si estaba subiendo tiende a seguir subiendo
             (ejemplo: si dist_p55 lleva varios días alejándose de EMA55,
              tenderá a seguir alejándose antes de volver)
  H ≈ 0.5  → movimiento aleatorio, sin memoria (como lanzar monedas)
  H < 0.5  → anti-persistente → si subió, tenderá a bajar (oscilación fuerte)

Se aplica a las distancias (dist_p10, dist_p55, dist_p200, dist_10_55, dist_55_200)
y NO al precio crudo, porque el precio tiene tendencia de largo plazo que
contamina el cálculo.

Genera en results/:
  - hurst_{TF}_valores.txt   ← un H por variable
  - hurst_{TF}_rs.png        ← gráfica del análisis R/S (cómo se calculó H)

Uso:
  python hurst.py
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

VARIABLES = ['dist_p10', 'dist_p55', 'dist_p200', 'dist_10_55', 'dist_55_200']

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


def hurst_rs(serie: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    """
    Calcula el exponente de Hurst via análisis R/S (Rescaled Range).

    Idea central:
      Para una ventana de tamaño n, calcula cuánto "rango" recorre la serie
      respecto a su desviación estándar. Si H>0.5, ese rango crece más rápido
      que una caminata aleatoria.

    Retorna: (H, lags, rs_values) para poder graficar
    """
    n      = len(serie)
    max_lag = min(n // 2, 500)
    lags   = np.unique(np.logspace(1, np.log10(max_lag), 40).astype(int))
    rs_vals = []

    for lag in lags:
        # partir la serie en bloques de tamaño lag
        rs_block = []
        for start in range(0, n - lag, lag):
            block = serie[start:start + lag]
            mean  = block.mean()
            # serie desviada de su media
            deviations  = np.cumsum(block - mean)
            R = deviations.max() - deviations.min()   # rango
            S = block.std(ddof=1)                      # desviación std
            if S > 0:
                rs_block.append(R / S)
        if rs_block:
            rs_vals.append(np.mean(rs_block))
        else:
            rs_vals.append(np.nan)

    rs_vals = np.array(rs_vals)
    # filtrar NaN
    mask   = ~np.isnan(rs_vals) & (rs_vals > 0)
    lags_f = lags[mask]
    rs_f   = rs_vals[mask]

    if len(lags_f) < 2:
        return np.nan, lags_f, rs_f

    # H es la pendiente en escala log-log
    coeffs = np.polyfit(np.log(lags_f), np.log(rs_f), 1)
    H = coeffs[0]
    return H, lags_f, rs_f


def interpretar_h(h: float) -> str:
    if np.isnan(h):
        return "No calculable"
    if h > 0.65:
        return f"H={h:.3f} → Persistente fuerte   — la serie tiende a continuar su dirección"
    if h > 0.55:
        return f"H={h:.3f} → Persistente moderada  — hay algo de memoria"
    if h > 0.45:
        return f"H={h:.3f} → Casi aleatoria        — sin memoria clara"
    if h > 0.35:
        return f"H={h:.3f} → Anti-persistente      — tiende a revertir (oscilación)"
    return     f"H={h:.3f} → Anti-persistente fuerte — revierte muy seguido"


# ── gráfica R/S ───────────────────────────────────────────────────────────────

def plot_rs(resultados: dict, tf: str):
    n_vars = len(resultados)
    fig, axes = plt.subplots(1, n_vars, figsize=(4 * n_vars, 5), facecolor=BG_FIG)
    fig.suptitle(f'Análisis R/S — Exponente de Hurst  [{tf}]',
                 fontsize=13, fontweight='bold', color='#111111')

    var_colors = [COLORS['dist_p10'], COLORS['dist_p55'], COLORS['dist_p200'],
                  COLORS['dist_10_55'], COLORS['dist_55_200']]

    for ax, (col, (H, lags, rs)), color in zip(axes, resultados.items(), var_colors):
        if len(lags) < 2:
            ax.set_title(f'{col}\nNo calculable', fontsize=8)
            continue

        ax.scatter(np.log(lags), np.log(rs), color=color, s=20, zorder=5,
                   label='valores R/S')

        fit   = np.polyfit(np.log(lags), np.log(rs), 1)
        x_line = np.linspace(np.log(lags[0]), np.log(lags[-1]), 50)
        ax.plot(x_line, np.polyval(fit, x_line), color=color,
                linewidth=1.8, label=f'H={H:.3f}')

        # referencia H=0.5 (aleatorio)
        offset = np.polyval(fit, x_line).mean() - 0.5 * x_line.mean()
        ax.plot(x_line, 0.5 * x_line + offset,
                color='#888888', linewidth=1, linestyle='--', alpha=0.7,
                label='H=0.5 (aleatorio)')

        estilo_ax(ax,
                  xlabel='log(ventana de tiempo)',
                  ylabel='log(R/S)',
                  title=f'{col}\n{interpretar_h(H)[:30]}')
        ax.legend(fontsize=6)

    plt.tight_layout()
    out = os.path.join(RESULTS, f'hurst_{tf}_rs.png')
    plt.savefig(out, dpi=130, bbox_inches='tight', facecolor=BG_FIG)
    plt.close()
    print(f'  📊 {os.path.basename(out)}')


# ── reporte txt ───────────────────────────────────────────────────────────────

def write_valores(resultados: dict, df: pd.DataFrame, tf: str):
    lines = [
        f'EXPONENTE DE HURST  [{tf}]',
        f'Filas: {len(df)} | Rango: {df["date"].iloc[0]} → {df["date"].iloc[-1]}',
        '=' * 60,
        '',
        'Interpretación de H:',
        '  H > 0.65  → Persistente fuerte   (la serie continúa su dirección)',
        '  H 0.55-0.65 → Persistente moderada (algo de memoria)',
        '  H 0.45-0.55 → Casi aleatoria       (sin memoria clara)',
        '  H 0.35-0.45 → Anti-persistente     (tiende a revertir)',
        '  H < 0.35  → Anti-persistente fuerte (revierte muy seguido)',
        '',
        'NOTA: Se aplica a las DISTANCIAS, no al precio crudo.',
        '      El precio crudo tiene tendencia que contaminaría el resultado.',
        '=' * 60,
        '',
    ]

    for col, (H, _, _) in resultados.items():
        lines.append(f'  {col}:  {interpretar_h(H)}')

    out = os.path.join(RESULTS, f'hurst_{tf}_valores.txt')
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

        resultados = {}
        for col in VARIABLES:
            serie = df[col].dropna().values
            H, lags, rs = hurst_rs(serie)
            resultados[col] = (H, lags, rs)
            print(f'   {col}: {interpretar_h(H)}')

        plot_rs(resultados, tf)
        write_valores(resultados, df, tf)

    print('\n✅ Listo. Revisa la carpeta results/')


if __name__ == '__main__':
    main()
