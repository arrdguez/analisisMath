"""
backtest_apoyo.py — Backtesting usando parámetros del análisis de apoyos
────────────────────────────────────────────────────────────────────────
Utiliza las estadísticas de results/apoyo_*_stats.txt para definir
umbrales realistas de profundidad y targets basados en rebotes históricos.

Parámetros extraídos automáticamente:
  - Profundidad mediana de apoyo por EMA
  - Tasa de éxito histórico (rebote 10 velas)
  - Rebote mediano esperado

Estrategia probada:
  1. Señal cuando dist_pX < profundidad_mediana y slopeX > 0
  2. Entrada en vela siguiente
  3. Target = rebote_mediano (ajustado por timeframe)
  4. Stop loss = profundidad_mediana * 1.5 (conservador)
"""

import os
import sys
import glob
import re
import pandas as pd
import numpy as np
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")
OUTPUT_DIR = os.path.join(BASE, "plan_accion", "resultados_backtest")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_support_stats(tf):
    """Extrae parámetros de archivo apoyo_{tf}_stats.txt."""
    stats_file = os.path.join(RESULTS_DIR, f"apoyo_{tf}_stats.txt")
    if not os.path.exists(stats_file):
        # Intentar con minúsculas/mayúsculas
        stats_file = os.path.join(RESULTS_DIR, f"apoyo_{tf.lower()}_stats.txt")
        if not os.path.exists(stats_file):
            stats_file = os.path.join(RESULTS_DIR, f"apoyo_{tf.upper()}_stats.txt")

    if not os.path.exists(stats_file):
        print(f"⚠️  No se encontró stats file para {tf}")
        return None

    with open(stats_file, "r", encoding="utf-8") as f:
        content = f.read()

    stats = {}

    # EMA10
    ema10_section = re.search(r"Apoyo en EMA10.*?──", content, re.DOTALL)
    if ema10_section:
        section = ema10_section.group(0)
        # Profundidad mediana
        match = re.search(r"mediana\s*=\s*([-\d.]+)%", section)
        if match:
            stats["ema10_median"] = float(match.group(1))
        # Tasa éxito
        match = re.search(r"tasa éxito.*?=\s*([\d.]+)%", section)
        if match:
            stats["ema10_success"] = float(match.group(1))
        # Rebote mediano
        match = re.search(r"mediana rebote\s*=\s*([-\d.]+)%", section)
        if match:
            stats["ema10_rebote"] = float(match.group(1))
        # Percentiles
        match = re.search(r"p25/p75\s*=\s*([-\d.]+)%\s*/\s*([-\d.]+)%", section)
        if match:
            stats["ema10_p25"] = float(match.group(1))
            stats["ema10_p75"] = float(match.group(2))

    # EMA55
    ema55_section = re.search(r"Apoyo en EMA55.*?──", content, re.DOTALL)
    if ema55_section:
        section = ema55_section.group(0)
        match = re.search(r"mediana\s*=\s*([-\d.]+)%", section)
        if match:
            stats["ema55_median"] = float(match.group(1))
        match = re.search(r"tasa éxito.*?=\s*([\d.]+)%", section)
        if match:
            stats["ema55_success"] = float(match.group(1))
        match = re.search(r"mediana rebote\s*=\s*([-\d.]+)%", section)
        if match:
            stats["ema55_rebote"] = float(match.group(1))

    # EMA200
    ema200_section = re.search(r"Apoyo en EMA200.*?──", content, re.DOTALL)
    if ema200_section:
        section = ema200_section.group(0)
        match = re.search(r"mediana\s*=\s*([-\d.]+)%", section)
        if match:
            stats["ema200_median"] = float(match.group(1))
        match = re.search(r"tasa éxito.*?=\s*([\d.]+)%", section)
        if match:
            stats["ema200_success"] = float(match.group(1))
        match = re.search(r"mediana rebote\s*=\s*([-\d.]+)%", section)
        if match:
            stats["ema200_rebote"] = float(match.group(1))

    return stats


def load_clean_data(tf):
    """Carga CSV limpio."""
    patterns = [
        os.path.join(RESULTS_DIR, f"*{tf}*clean.csv"),
        os.path.join(RESULTS_DIR, f"*{tf.lower()}*clean.csv"),
        os.path.join(RESULTS_DIR, f"*{tf.upper()}*clean.csv"),
    ]

    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            filepath = files[0]
            df = pd.read_csv(filepath, parse_dates=["date"])
            break
    else:
        raise FileNotFoundError(f"No CSV limpio para {tf}")

    # Filtrar filas completas y outliers
    df = df.dropna(subset=["ema200"]).reset_index(drop=True)
    for col in ["dist_p10", "dist_p55", "dist_p200"]:
        df = df[(df[col] >= -100) & (df[col] <= 100)]

    # Resetear índice después de filtrar
    df = df.reset_index(drop=True)

    return df, filepath


def backtest_support(df, tf, ema="10", stats=None):
    """
    Backtest de estrategia de apoyo en una EMA específica.

    Args:
        ema: "10", "55", o "200"
        stats: diccionario con parámetros de apoyo
    """
    # Configuración por timeframe
    config = {
        "1D": {"min_gap": 10, "max_hold": 50},
        "4H": {"min_gap": 20, "max_hold": 100},
        "1H": {"min_gap": 30, "max_hold": 200},
    }.get(tf, {"min_gap": 20, "max_hold": 100})

    # Parámetros de la EMA
    if ema == "10":
        dist_col = "dist_p10"
        slope_col = "slope10"
        median_key = "ema10_median"
        rebote_key = "ema10_rebote"
        success_key = "ema10_success"
    elif ema == "55":
        dist_col = "dist_p55"
        slope_col = "slope55"
        median_key = "ema55_median"
        rebote_key = "ema55_rebote"
        success_key = "ema55_success"
    elif ema == "200":
        dist_col = "dist_p200"
        slope_col = "slope200"
        median_key = "ema200_median"
        rebote_key = "ema200_rebote"
        success_key = "ema200_success"
    else:
        raise ValueError("EMA debe ser 10, 55 o 200")

    # Umbrales
    if stats and median_key in stats:
        threshold = stats[median_key]
        target_pct = stats.get(rebote_key, abs(threshold) * 0.8)
        historical_success = stats.get(success_key, 70) / 100
    else:
        # Valores por defecto si no hay stats
        threshold = {"1D": -3.5, "4H": -1.2, "1H": -0.5}[tf]
        target_pct = abs(threshold) * 0.8
        historical_success = 0.75

    # Stop loss (más amplio que el threshold)
    stop_pct = abs(threshold) * 1.5

    print(f"   📊 Parámetros EMA{ema}:")
    print(f"      Umbral: {threshold:.2f}%")
    print(f"      Target: {target_pct:.2f}%")
    print(f"      Stop: {stop_pct:.2f}%")
    print(f"      Éxito histórico: {historical_success:.1%}")

    # Detectar señales
    condition = (df[dist_col] < threshold) & (df[slope_col] > 0)

    signal_indices = df[condition].index.tolist()

    # Filtrar señales cercanas
    filtered = []
    last_idx = -config["min_gap"]
    for idx in signal_indices:
        if idx - last_idx >= config["min_gap"]:
            filtered.append(idx)
            last_idx = idx

    print(f"   📈 Señales detectadas: {len(filtered)}")

    # Simular operaciones
    trades = []
    for idx in filtered:
        if idx >= len(df) - config["max_hold"]:
            continue

        entry_idx = idx + 1
        entry_price = df.loc[entry_idx, "close"]
        entry_date = df.loc[entry_idx, "date"]

        target_price = entry_price * (1 + target_pct / 100)
        stop_price = entry_price * (1 - stop_pct / 100)

        exit_idx = None
        exit_price = None
        exit_reason = None

        for lookahead in range(1, config["max_hold"] + 1):
            current_idx = entry_idx + lookahead
            if current_idx >= len(df):
                break

            current_price = df.loc[current_idx, "close"]

            if current_price >= target_price:
                exit_idx = current_idx
                exit_price = target_price
                exit_reason = "target"
                break
            elif current_price <= stop_price:
                exit_idx = current_idx
                exit_price = stop_price
                exit_reason = "stop"
                break

        if exit_idx is None:
            exit_idx = entry_idx + config["max_hold"]
            if exit_idx >= len(df):
                exit_idx = len(df) - 1
            exit_price = df.loc[exit_idx, "close"]
            exit_reason = "timeout"

        pct_return = (exit_price - entry_price) / entry_price * 100
        hold_bars = exit_idx - entry_idx

        trades.append(
            {
                "entry_date": entry_date,
                "entry_price": entry_price,
                "exit_date": df.loc[exit_idx, "date"],
                "exit_price": exit_price,
                "exit_reason": exit_reason,
                "pct_return": pct_return,
                "hold_bars": hold_bars,
                "ema": ema,
                "threshold": threshold,
                "target": target_pct,
                "stop": stop_pct,
            }
        )

    # Calcular métricas
    if trades:
        df_trades = pd.DataFrame(trades)
        df_trades["is_win"] = df_trades["pct_return"] > 0

        total_trades = len(df_trades)
        win_trades = df_trades["is_win"].sum()
        win_rate = win_trades / total_trades

        gains = df_trades[df_trades["pct_return"] > 0]["pct_return"].sum()
        losses = abs(df_trades[df_trades["pct_return"] < 0]["pct_return"].sum())
        profit_factor = gains / losses if losses > 0 else float("inf")

        total_return = df_trades["pct_return"].sum()
        avg_return = df_trades["pct_return"].mean()

        # Comparar con éxito histórico
        success_diff = (win_rate - historical_success) * 100

        metrics = {
            "total_trades": total_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "total_return": total_return,
            "avg_return": avg_return,
            "success_diff": success_diff,
            "avg_hold_bars": df_trades["hold_bars"].mean(),
        }

        print(f"   📊 Resultados:")
        print(f"      Operaciones: {total_trades}")
        print(
            f"      Win rate: {win_rate:.1%} (histórico: {historical_success:.1%}, diff: {success_diff:+.1f}pp)"
        )
        print(f"      Profit factor: {profit_factor:.2f}")
        print(f"      Retorno total: {total_return:.1f}%")
        print(f"      Retorno promedio: {avg_return:.2f}%")
        print(f"      Hold promedio: {metrics['avg_hold_bars']:.1f} velas")

        # Guardar detalles
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = os.path.join(
            OUTPUT_DIR, f"backtest_ema{ema}_{tf}_{timestamp}.csv"
        )
        df_trades.to_csv(output_file, index=False)
        print(f"      💾 Detalles: {os.path.basename(output_file)}")

        return metrics, df_trades
    else:
        print(f"   ❌ No hay operaciones simuladas")
        return None, None


def main():
    print("=" * 70)
    print("BACKTEST BASADO EN ANÁLISIS DE APOYOS")
    print("=" * 70)

    timeframes = ["1D", "4H", "1H"]
    emas = ["10", "55", "200"]

    all_results = []

    for tf in timeframes:
        print(f"\n{'=' * 50}")
        print(f"TIMEFRAME: {tf}")
        print(f"{'=' * 50}")

        # Cargar stats
        stats = parse_support_stats(tf)
        if stats:
            print(f"📖 Parámetros cargados de análisis de apoyos")
        else:
            print(f"⚠️  Usando parámetros por defecto")

        # Cargar datos
        try:
            df, filepath = load_clean_data(tf)
            print(f"📂 Datos: {os.path.basename(filepath)}")
            print(
                f"   Filas: {len(df)} | Rango: {df['date'].iloc[0].date()} → {df['date'].iloc[-1].date()}"
            )
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            continue

        for ema in emas:
            print(f"\n  ── EMA{ema} ──")
            metrics, trades = backtest_support(df, tf, ema, stats)

            if metrics:
                all_results.append(
                    {
                        "timeframe": tf,
                        "ema": ema,
                        "trades": metrics["total_trades"],
                        "win_rate": metrics["win_rate"],
                        "profit_factor": metrics["profit_factor"],
                        "total_return": metrics["total_return"],
                        "avg_return": metrics["avg_return"],
                        "success_diff": metrics["success_diff"],
                    }
                )

    # Resumen general
    if all_results:
        print(f"\n{'=' * 70}")
        print("RESUMEN GENERAL")
        print(f"{'=' * 70}")

        df_summary = pd.DataFrame(all_results)
        print(df_summary.to_string(index=False))

        # Guardar resumen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        summary_file = os.path.join(OUTPUT_DIR, f"backtest_summary_{timestamp}.csv")
        df_summary.to_csv(summary_file, index=False)

        print(f"\n💾 Resumen guardado en: {os.path.basename(summary_file)}")

        # Análisis de mejores configuraciones
        print(f"\n{'=' * 70}")
        print("MEJORES CONFIGURACIONES")
        print(f"{'=' * 70}")

        # Mejor win rate (mínimo 5 trades)
        filtered = df_summary[df_summary["trades"] >= 5]
        if len(filtered) > 0:
            best_win = filtered.loc[filtered["win_rate"].idxmax()]
            print(f"🎯 Mejor win rate (>5 trades):")
            print(f"   {best_win['timeframe']} - EMA{best_win['ema']}")
            print(
                f"   Win rate: {best_win['win_rate']:.1%} | Trades: {best_win['trades']}"
            )
            print(f"   Profit factor: {best_win['profit_factor']:.2f}")

        # Mejor profit factor
        if len(filtered) > 0:
            best_pf = filtered.loc[filtered["profit_factor"].idxmax()]
            print(f"\n💰 Mejor profit factor (>5 trades):")
            print(f"   {best_pf['timeframe']} - EMA{best_pf['ema']}")
            print(
                f"   Profit factor: {best_pf['profit_factor']:.2f} | Win rate: {best_pf['win_rate']:.1%}"
            )

        # Mejor retorno total
        if len(filtered) > 0:
            best_ret = filtered.loc[filtered["total_return"].idxmax()]
            print(f"\n📈 Mejor retorno total (>5 trades):")
            print(f"   {best_ret['timeframe']} - EMA{best_ret['ema']}")
            print(
                f"   Retorno total: {best_ret['total_return']:.1f}% | Trades: {best_ret['trades']}"
            )

    print(f"\n{'=' * 70}")
    print("BACKTEST COMPLETADO")
    print(f"Resultados guardados en: {OUTPUT_DIR}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
