"""
analizar_datos.py — Análisis rápido de distribución de distancias
────────────────────────────────────────────────────────────────
Examina los datos limpios para entender distribuciones, outliers,
y determinar umbrales razonables para backtesting.
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")


def analyze_tf(tf):
    """Analiza un timeframe específico."""
    print(f"\n{'=' * 60}")
    print(f"ANÁLISIS DE DISTRIBUCIÓN: {tf}")
    print(f"{'=' * 60}")

    # Cargar datos
    patterns = [
        os.path.join(RESULTS_DIR, f"*{tf}*clean.csv"),
        os.path.join(RESULTS_DIR, f"*{tf.lower()}*clean.csv"),
        os.path.join(RESULTS_DIR, f"*{tf.upper()}*clean.csv"),
    ]

    filepath = None
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            filepath = files[0]
            break

    if not filepath:
        print(f"❌ No se encontró CSV para {tf}")
        return

    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.dropna(subset=["ema200"]).reset_index(drop=True)

    print(f"📂 Archivo: {os.path.basename(filepath)}")
    print(f"   Filas totales: {len(df)}")
    print(f"   Rango: {df['date'].iloc[0].date()} → {df['date'].iloc[-1].date()}")

    # Análisis de dist_p10
    dist = df["dist_p10"].copy()

    print(f"\n📊 DIST_P10 (distancia precio a EMA10):")
    print(f"   Mínimo:    {dist.min():.2f}%")
    print(f"   Máximo:    {dist.max():.2f}%")
    print(f"   Mediana:   {dist.median():.2f}%")
    print(f"   Media:     {dist.mean():.2f}%")
    print(f"   Std:       {dist.std():.2f}%")

    # Percentiles
    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
        print(f"   P{p:02d}:      {dist.quantile(p / 100):.2f}%")

    # Valores extremos
    q1 = dist.quantile(0.25)
    q3 = dist.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = dist[(dist < lower_bound) | (dist > upper_bound)]
    print(
        f"\n🔍 Outliers (IQR method): {len(outliers)} valores ({len(outliers) / len(dist) * 100:.1f}%)"
    )
    if len(outliers) > 0:
        print(f"   Rango outliers: {outliers.min():.2f}% a {outliers.max():.2f}%")

    # Distribución de valores negativos
    neg = dist[dist < 0]
    print(
        f"\n📉 Valores negativos (precio < EMA10): {len(neg)} ({len(neg) / len(dist) * 100:.1f}%)"
    )
    if len(neg) > 0:
        print(f"   Mediana negativos: {neg.median():.2f}%")
        print(f"   P25 negativos:     {neg.quantile(0.25):.2f}%")
        print(f"   P10 negativos:     {neg.quantile(0.10):.2f}%")

    # Distribución de valores positivos
    pos = dist[dist > 0]
    print(
        f"\n📈 Valores positivos (precio > EMA10): {len(pos)} ({len(pos) / len(dist) * 100:.1f}%)"
    )
    if len(pos) > 0:
        print(f"   Mediana positivos: {pos.median():.2f}%")

    # Histograma
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.hist(dist, bins=100, alpha=0.7, edgecolor="black")
    plt.axvline(
        dist.median(),
        color="red",
        linestyle="--",
        label=f"Mediana: {dist.median():.2f}%",
    )
    plt.axvline(0, color="black", linestyle="-", alpha=0.5)
    plt.xlabel("dist_p10 (%)")
    plt.ylabel("Frecuencia")
    plt.title(f"Distribución de dist_p10 ({tf})")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Zoom en el rango [-50%, 50%]
    plt.subplot(1, 2, 2)
    dist_clipped = dist[(dist >= -50) & (dist <= 50)]
    plt.hist(dist_clipped, bins=100, alpha=0.7, edgecolor="black")
    plt.axvline(
        dist.median(),
        color="red",
        linestyle="--",
        label=f"Mediana: {dist.median():.2f}%",
    )
    plt.axvline(0, color="black", linestyle="-", alpha=0.5)
    plt.xlabel("dist_p10 (%)")
    plt.ylabel("Frecuencia")
    plt.title(f"Dist_p10 (zoom -50% a 50%)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = os.path.join(BASE, "plan_accion", f"distribucion_{tf}.png")
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"\n💾 Gráfico guardado en: {os.path.basename(output_path)}")

    # Análisis por períodos (primera mitad vs segunda mitad)
    split_idx = len(df) // 2
    first_half = df["dist_p10"].iloc[:split_idx]
    second_half = df["dist_p10"].iloc[split_idx:]

    print(f"\n🕐 COMPARACIÓN TEMPORAL:")
    print(
        f"   Primera mitad ({df['date'].iloc[0].date()} → {df['date'].iloc[split_idx - 1].date()}):"
    )
    print(
        f"     Mediana: {first_half.median():.2f}% | P25: {first_half.quantile(0.25):.2f}% | P75: {first_half.quantile(0.75):.2f}%"
    )
    print(
        f"   Segunda mitad ({df['date'].iloc[split_idx].date()} → {df['date'].iloc[-1].date()}):"
    )
    print(
        f"     Mediana: {second_half.median():.2f}% | P25: {second_half.quantile(0.25):.2f}% | P75: {second_half.quantile(0.75):.2f}%"
    )

    return {
        "file": filepath,
        "dist_p10_stats": {
            "min": dist.min(),
            "max": dist.max(),
            "median": dist.median(),
            "mean": dist.mean(),
            "std": dist.std(),
            "q1": q1,
            "q3": q3,
            "p25_neg": neg.quantile(0.25) if len(neg) > 0 else None,
            "p10_neg": neg.quantile(0.10) if len(neg) > 0 else None,
        },
    }


def main():
    print("ANÁLISIS DE DISTRIBUCIÓN DE DISTANCIAS")
    print("=" * 60)

    results = {}
    for tf in ["1D", "4H", "1H"]:
        results[tf] = analyze_tf(tf)

    # Resumen comparativo
    print(f"\n{'=' * 60}")
    print("RESUMEN COMPARATIVO")
    print(f"{'=' * 60}")
    print(
        f"{'TF':<5} {'Filas':<8} {'Mediana':<10} {'P25_neg':<10} {'P10_neg':<10} {'Outliers':<10}"
    )
    print(f"{'-' * 60}")

    for tf in ["1D", "4H", "1H"]:
        stats = results[tf]["dist_p10_stats"] if results[tf] else {}
        p25_neg = stats.get("p25_neg", "N/A")
        p10_neg = stats.get("p10_neg", "N/A")

        # Contar outliers
        if results[tf]:
            df = pd.read_csv(results[tf]["file"], parse_dates=["date"])
            dist = df["dist_p10"].dropna()
            q1 = dist.quantile(0.25)
            q3 = dist.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outliers = len(dist[(dist < lower) | (dist > upper)])
        else:
            outliers = "N/A"

        print(
            f"{tf:<5} {len(df) if results[tf] else 'N/A':<8} "
            f"{stats.get('median', 'N/A'):<10.2f} "
            f"{p25_neg if isinstance(p25_neg, (int, float)) else 'N/A':<10.2f} "
            f"{p10_neg if isinstance(p10_neg, (int, float)) else 'N/A':<10.2f} "
            f"{outliers:<10}"
        )

    print(f"\n💡 RECOMENDACIONES PARA BACKTESTING:")
    print("   1. Usar P10_neg o P25_neg como umbral para apoyos")
    print("   2. Considerar filtrar outliers extremos (fuera de ±100%)")
    print("   3. Evaluar diferencias entre primera y segunda mitad del dataset")
    print("   4. Probablemente necesitar ajustar umbrales por timeframe")


if __name__ == "__main__":
    main()
