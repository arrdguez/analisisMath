"""
correlation_analysis.py — Análisis de correlación y sincronía entre distancias
──────────────────────────────────────────────────────────────────────────────
FASE 2.3: Analiza la relación entre dist_10_55 y dist_55_200 para determinar
si hay sincronía, desfase o independencia entre las dos distancias entre EMAs.

Preguntas que responde:
1. ¿Hay correlación lineal entre dist_10_55 y dist_55_200?
2. ¿Cuál es el desfase óptimo (en velas) entre las dos series?
3. ¿La relación es estable en el tiempo o cambia con el régimen de mercado?
4. ¿dist_10_55 lidera o sigue a dist_55_200?

Genera en results/:
  - correlation_{TF}_ccf.png       ← Correlación cruzada vs lag
  - correlation_{TF}_scatter.png   ← Diagrama de dispersión con regresión
  - correlation_{TF}_rolling.png   ← Correlación móvil en el tiempo
  - correlation_{TF}_stats.txt     ← Reporte con métricas cuantitativas

Uso:
  python correlation_analysis.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal
from scipy.stats import pearsonr
from plot_style import BG_FIG, BG_AX, COLORS, estilo_ax

BASE = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, "results")

WINDOW_CORR = 252  # ventana para correlación móvil (~1 año en 1D)

# ── helpers ───────────────────────────────────────────────────────────────────


def load(path: str) -> pd.DataFrame:
    """Carga CSV limpio y filtra filas sin EMA200."""
    df = pd.read_csv(path, parse_dates=["date"])
    return df.dropna(subset=["ema200"]).reset_index(drop=True)


def timeframe_label(filename: str) -> str:
    """Extrae el nombre base del archivo sin '_clean' ni extensión."""
    return os.path.basename(filename).replace("_clean.csv", "").replace(".csv", "")


def compute_ccf(x: np.ndarray, y: np.ndarray, max_lag: int = 100) -> tuple:
    """
    Calcula la correlación cruzada (CCF) entre dos series.

    Retorna:
        lags (np.ndarray): valores de lag en velas
        ccf (np.ndarray): valores de correlación para cada lag
        best_lag (int): lag con máxima correlación absoluta
        best_corr (float): valor de correlación en best_lag
    """
    # Normalizar las series (media 0, desviación 1)
    x_norm = (x - np.mean(x)) / (np.std(x) + 1e-10)
    y_norm = (y - np.mean(y)) / (np.std(y) + 1e-10)

    # Correlación cruzada usando scipy (más robusta)
    correlation = signal.correlate(x_norm, y_norm, mode="full")
    lags = signal.correlation_lags(len(x_norm), len(y_norm), mode="full")

    # Filtrar lags dentro del rango especificado
    mask = (lags >= -max_lag) & (lags <= max_lag)
    lags = lags[mask]
    correlation = correlation[mask]

    # Normalizar los valores de correlación
    correlation = correlation / (len(x) - np.abs(lags))

    # Encontrar lag con máxima correlación absoluta
    best_idx = np.argmax(np.abs(correlation))
    best_lag = int(lags[best_idx])
    best_corr = float(correlation[best_idx])

    return lags, correlation, best_lag, best_corr


def rolling_correlation(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """Calcula correlación móvil entre dos series."""
    if len(x) < window:
        return pd.Series([np.nan] * len(x), index=x.index)

    # Alinear índices
    x_aligned = x.reset_index(drop=True)
    y_aligned = y.reset_index(drop=True)

    corrs = []
    for i in range(len(x_aligned)):
        start = max(0, i - window + 1)
        end = i + 1
        if end - start < 10:  # mínimo 10 puntos para correlación significativa
            corrs.append(np.nan)
            continue
        x_win = x_aligned[start:end]
        y_win = y_aligned[start:end]
        # Eliminar NaN en ventana
        mask = ~(x_win.isna() | y_win.isna())
        if mask.sum() < 10:
            corrs.append(np.nan)
            continue
        try:
            r, _ = pearsonr(x_win[mask].values, y_win[mask].values)
            corrs.append(r)
        except:
            corrs.append(np.nan)

    return pd.Series(corrs, index=x.index)


# ── gráfica 1: correlación cruzada (CCF) ──────────────────────────────────────


def plot_ccf(
    lags: np.ndarray, ccf: np.ndarray, best_lag: int, best_corr: float, tf: str
):
    """Gráfica de correlación cruzada vs lag."""
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG_FIG)

    ax.plot(
        lags,
        ccf,
        color=COLORS["dist_10_55"],
        linewidth=1.5,
        alpha=0.8,
        label="Correlación cruzada",
    )
    ax.axvline(
        best_lag,
        color="#e65100",
        linewidth=1.2,
        linestyle="--",
        label=f"Lag óptimo: {best_lag} velas (corr={best_corr:.3f})",
    )
    ax.axvline(0, color="#888888", linewidth=0.8, linestyle=":", label="Lag 0")
    ax.axhline(0, color="#888888", linewidth=0.8, linestyle="-")

    # Rellenar área significativa (|corr| > 0.2)
    ax.fill_between(
        lags,
        ccf,
        0,
        where=ccf > 0.2,
        alpha=0.15,
        color=COLORS["dist_10_55"],
        label="Corr > 0.2",
    )
    ax.fill_between(
        lags,
        ccf,
        0,
        where=ccf < -0.2,
        alpha=0.15,
        color=COLORS["dist_55_200"],
        label="Corr < -0.2",
    )

    ax.legend(fontsize=8)
    estilo_ax(
        ax,
        xlabel="Lag (velas) — positivo = dist_10_55 precede a dist_55_200",
        ylabel="Coeficiente de correlación",
        title=f"Correlación Cruzada: dist_10_55 vs dist_55_200  [{tf}]\n"
        f"Lag óptimo = {best_lag} velas (corr={best_corr:.3f})",
    )

    out = os.path.join(RESULTS, f"{tf}_correlation_ccf.png")
    plt.savefig(out, dpi=130, bbox_inches="tight", facecolor=BG_FIG)
    plt.close()
    print(f"  📊 {os.path.basename(out)}")


# ── gráfica 2: diagrama de dispersión con regresión ───────────────────────────


def plot_scatter(df: pd.DataFrame, tf: str, pearson_r: float):
    """Diagrama de dispersión con línea de regresión."""
    fig, ax = plt.subplots(figsize=(10, 8), facecolor=BG_FIG)

    # Datos
    x = df["dist_55_200"].dropna().values
    y = df["dist_10_55"].dropna().values

    # Scatter con transparencia para densidad
    ax.scatter(
        x,
        y,
        color=COLORS["ratio"],
        s=12,
        alpha=0.4,
        edgecolors="none",
        label=f"n={len(x)} puntos",
    )

    # Regresión lineal
    if len(x) > 2:
        coeffs = np.polyfit(x, y, 1)
        reg_line = np.poly1d(coeffs)
        x_range = np.linspace(x.min(), x.max(), 100)
        ax.plot(
            x_range,
            reg_line(x_range),
            color="#111111",
            linewidth=1.8,
            label=f"y = {coeffs[0]:.3f}x + {coeffs[1]:.3f}",
        )

    ax.axhline(0, color="#888888", linewidth=0.8, linestyle="--")
    ax.axvline(0, color="#888888", linewidth=0.8, linestyle="--")

    # Líneas de referencia para interpretación
    ax.plot(
        [-30, 30],
        [-30, 30],
        color="#1565c0",
        linewidth=0.7,
        linestyle=":",
        alpha=0.6,
        label="y = x (igualdad)",
    )
    ax.plot(
        [-30, 30],
        [-15, 15],
        color="#2e7d32",
        linewidth=0.7,
        linestyle=":",
        alpha=0.6,
        label="y = 0.5x",
    )
    ax.plot(
        [-30, 30],
        [-60, 60],
        color="#e65100",
        linewidth=0.7,
        linestyle=":",
        alpha=0.6,
        label="y = 2x",
    )

    ax.legend(fontsize=7)
    estilo_ax(
        ax,
        xlabel="dist_55_200 (%) — distancia EMA55 vs EMA200",
        ylabel="dist_10_55 (%) — distancia EMA10 vs EMA55",
        title=f"Relación dist_10_55 vs dist_55_200  [{tf}]\n"
        f"Pearson r = {pearson_r:.3f}  |  n = {len(x)} puntos",
    )

    out = os.path.join(RESULTS, f"{tf}_correlation_scatter.png")
    plt.savefig(out, dpi=130, bbox_inches="tight", facecolor=BG_FIG)
    plt.close()
    print(f"  📊 {os.path.basename(out)}")


# ── gráfica 3: correlación móvil en el tiempo ─────────────────────────────────


def plot_rolling_corr(df: pd.DataFrame, rolling_corr: pd.Series, tf: str):
    """Evolución temporal de la correlación."""
    fig, axes = plt.subplots(2, 1, figsize=(16, 9), facecolor=BG_FIG, sharex=True)

    # Panel superior: series originales
    ax1 = axes[0]
    ax1.plot(
        df["date"],
        df["dist_10_55"],
        color=COLORS["dist_10_55"],
        linewidth=0.8,
        alpha=0.8,
        label="dist_10_55",
    )
    ax1.plot(
        df["date"],
        df["dist_55_200"],
        color=COLORS["dist_55_200"],
        linewidth=0.8,
        alpha=0.8,
        label="dist_55_200",
    )
    ax1.axhline(0, color="#888888", linewidth=0.6, linestyle="--")
    ax1.legend(fontsize=8)
    estilo_ax(
        ax1, ylabel="Distancia entre EMAs (%)", title=f"Series originales  [{tf}]"
    )

    # Panel inferior: correlación móvil
    ax2 = axes[1]
    ax2.plot(
        df["date"],
        rolling_corr,
        color=COLORS["ratio"],
        linewidth=1.2,
        label=f"Correlación móvil ({WINDOW_CORR} velas)",
    )
    ax2.axhline(0, color="#888888", linewidth=0.8, linestyle="-")
    ax2.axhline(
        0.5,
        color="#2e7d32",
        linewidth=0.7,
        linestyle=":",
        alpha=0.6,
        label="r = 0.5 (fuerte)",
    )
    ax2.axhline(
        -0.5,
        color="#e65100",
        linewidth=0.7,
        linestyle=":",
        alpha=0.6,
        label="r = -0.5 (fuerte inversa)",
    )

    # Rellenar áreas por nivel de correlación
    ax2.fill_between(
        df["date"],
        rolling_corr,
        0.5,
        where=rolling_corr > 0.5,
        alpha=0.15,
        color="#2e7d32",
        label="Corr > 0.5",
    )
    ax2.fill_between(
        df["date"],
        rolling_corr,
        -0.5,
        where=rolling_corr < -0.5,
        alpha=0.15,
        color="#e65100",
        label="Corr < -0.5",
    )

    ax2.legend(fontsize=7)
    estilo_ax(
        ax2,
        xlabel="Fecha",
        ylabel="Coeficiente de correlación de Pearson",
        title=f"Estabilidad de la relación  [{tf}]",
    )

    plt.tight_layout()
    out = os.path.join(RESULTS, f"{tf}_correlation_rolling.png")
    plt.savefig(out, dpi=130, bbox_inches="tight", facecolor=BG_FIG)
    plt.close()
    print(f"  📊 {os.path.basename(out)}")


# ── reporte txt ───────────────────────────────────────────────────────────────


def write_stats(
    df: pd.DataFrame,
    tf: str,
    pearson_r: float,
    pearson_p: float,
    best_lag: int,
    best_corr: float,
    coeffs: tuple,
):
    """Genera archivo de texto con métricas cuantitativas."""
    lines = [
        f"ANÁLISIS DE CORRELACIÓN  [{tf}]",
        f"Filas: {len(df)} | Rango: {df['date'].iloc[0]} → {df['date'].iloc[-1]}",
        "=" * 60,
        "",
        "── CORRELACIÓN SINCRÓNICA (lag = 0) ──",
        f"  Pearson r   = {pearson_r:.4f}",
        f"  Valor p     = {pearson_p:.4e}",
        f"  Interpretación:",
    ]

    # Interpretación de Pearson
    abs_r = abs(pearson_r)
    if abs_r > 0.7:
        lines.append("    • Correlación MUY FUERTE (> 0.7)")
    elif abs_r > 0.5:
        lines.append("    • Correlación FUERTE (0.5-0.7)")
    elif abs_r > 0.3:
        lines.append("    • Correlación MODERADA (0.3-0.5)")
    elif abs_r > 0.1:
        lines.append("    • Correlación DÉBIL (0.1-0.3)")
    else:
        lines.append("    • Correlación INEXISTENTE (< 0.1)")

    if pearson_p < 0.05:
        lines.append("    • Estadísticamente SIGNIFICATIVA (p < 0.05)")
    else:
        lines.append("    • NO estadísticamente significativa (p ≥ 0.05)")

    lines += [
        "",
        "── CORRELACIÓN CRUZADA (desfase óptimo) ──",
        f"  Lag óptimo  = {best_lag} velas",
        f"  Correlación en lag óptimo = {best_corr:.4f}",
        f"  Interpretación:",
    ]

    # Interpretación del lag
    if best_lag == 0:
        lines.append("    • Las series están SINCRONIZADAS (sin desfase)")
    elif best_lag > 0:
        lines.append(f"    • dist_10_55 PRECEDE a dist_55_200 por {best_lag} velas")
    else:
        lines.append(
            f"    • dist_55_200 PRECEDE a dist_10_55 por {abs(best_lag)} velas"
        )

    if abs(best_corr) > abs(pearson_r) * 1.1:
        lines.append("    • Mejor correlación con desfase que sincrónica")
    else:
        lines.append("    • Correlación máxima similar a la sincrónica")

    lines += [
        "",
        "── RELACIÓN LINEAL (regresión) ──",
        f"  Pendiente   = {coeffs[0]:.4f}",
        f"  Intercepto  = {coeffs[1]:.4f}",
        f"  Ecuación: dist_10_55 = {coeffs[0]:.4f} × dist_55_200 + {coeffs[1]:.4f}",
        "",
        "Interpretación de la pendiente:",
    ]

    # Interpretación de la pendiente
    slope = coeffs[0]
    if slope > 1.5:
        lines.append(
            "    • dist_10_55 AMPLIFICA los movimientos de dist_55_200 (pendiente > 1.5)"
        )
    elif slope > 0.8:
        lines.append(
            "    • dist_10_55 responde PROPORCIONALMENTE a dist_55_200 (pendiente ~1)"
        )
    elif slope > 0.3:
        lines.append(
            "    • dist_10_55 responde ATENUANDO los movimientos de dist_55_200 (pendiente < 1)"
        )
    elif slope > 0:
        lines.append("    • Respuesta POSITIVA pero DÉBIL")
    elif slope > -0.3:
        lines.append("    • Respuesta NEGATIVA pero débil (oposición leve)")
    else:
        lines.append("    • Respuesta INVERSA fuerte (pendiente negativa)")

    lines += [
        "",
        "── RESUMEN PARA INDICADOR ──",
        f"  1. Correlación sincrónica: {'SÍ' if abs(pearson_r) > 0.3 and pearson_p < 0.05 else 'NO'}",
        f"  2. Desfase óptimo: {best_lag} velas",
        f"  3. Relación: dist_10_55 ≈ {coeffs[0]:.2f} × dist_55_200",
        f"  4. Fuerza relación: {'fuerte' if abs(pearson_r) > 0.5 else 'moderada' if abs(pearson_r) > 0.3 else 'débil'}",
    ]

    out = os.path.join(RESULTS, f"{tf}_correlation_stats.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  📄 {os.path.basename(out)}")


# ── main ─────────────────────────────────────────────────────────────────────


def main():
    """Punto de entrada: procesa todos los archivos _clean.csv."""
    clean_files = sorted(glob.glob(os.path.join(RESULTS, "*_clean.csv")))
    if not clean_files:
        print("No se encontraron archivos _clean.csv en results/")
        return

    for path in clean_files:
        tf = timeframe_label(path)
        print(f"\n📂 {tf}")

        df = load(path)
        print(f"   {len(df)} filas con datos completos")

        # Preparar series sin NaN
        dist_10_55 = df["dist_10_55"].dropna().values
        dist_55_200 = df["dist_55_200"].dropna().values

        if len(dist_10_55) < 50 or len(dist_55_200) < 50:
            print(f"  ⚠️  Datos insuficientes para análisis de correlación")
            continue

        # 1. Correlación de Pearson (sincrónica)
        pearson_r, pearson_p = pearsonr(dist_10_55, dist_55_200)
        print(f"   Pearson r = {pearson_r:.3f} (p = {pearson_p:.3e})")

        # 2. Correlación cruzada (desfase óptimo)
        lags, ccf, best_lag, best_corr = compute_ccf(dist_10_55, dist_55_200)
        print(f"   Lag óptimo = {best_lag} velas (corr = {best_corr:.3f})")

        # 3. Regresión lineal
        coeffs = np.polyfit(dist_55_200, dist_10_55, 1)
        print(
            f"   Regresión: dist_10_55 = {coeffs[0]:.3f} × dist_55_200 + {coeffs[1]:.3f}"
        )

        # 4. Correlación móvil
        rolling_corr_series = rolling_correlation(
            df["dist_10_55"], df["dist_55_200"], WINDOW_CORR
        )
        rolling_mean = rolling_corr_series.mean()
        rolling_std = rolling_corr_series.std()
        print(f"   Corr móvil: media = {rolling_mean:.3f}, std = {rolling_std:.3f}")

        # Generar gráficas y reportes
        plot_ccf(lags, ccf, best_lag, best_corr, tf)
        plot_scatter(df, tf, pearson_r)
        plot_rolling_corr(df, rolling_corr_series, tf)
        write_stats(df, tf, pearson_r, pearson_p, best_lag, best_corr, coeffs)

    print("\n✅ Listo. Revisa la carpeta results/")


if __name__ == "__main__":
    main()
