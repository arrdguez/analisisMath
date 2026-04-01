"""
FASE1_backtesting.py — Validación rápida de reglas basadas en análisis de magnitudes
──────────────────────────────────────────────────────────────────────────────────
Objetivo: Probar reglas simples de trading usando los datos limpios (CSV) para
determinar si existe un edge medible antes de codificar el indicador en Pine Script.

Reglas básicas a probar (por timeframe):
  1. Apoyo en EMA10:
     - Señal: dist_p10 < percentil_25 (umbral negativo) y slope10 > 0
     - Entrada: siguiente vela
     - Objetivo: +1.5% (4H), +5% (1D) o basado en percentil 75 de rebote
     - Stop loss: -2% (4H), -5% (1D) o mínimo local del apoyo

  2. Apoyo en EMA55:
     - Señal: dist_p55 < percentil_25 y slope55 > 0
     - Objetivo: basado en distancia a EMA200 o percentil 75

  3. Filtro de ratio armónico:
     - Requerir que ratio_armonico esté cerca de 0.3 (mediana histórica)

Métricas calculadas:
  - Número total de señales
  - Win rate (% operaciones ganadoras)
  - Profit factor (ganancias totales / pérdidas totales)
  - Máximo drawdown
  - Expectativa matemática

Uso:
  python FASE1_backtesting.py --tf 1D --regla apoyo10
  python FASE1_backtesting.py --all
"""

import os
import sys
import glob
import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Configuración de rutas
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")
PLAN_DIR = os.path.join(BASE, "plan_accion")
OUTPUT_DIR = os.path.join(PLAN_DIR, "resultados_backtest")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──── Configuración de parámetros por timeframe ────────────────────────────────
TF_CONFIG = {
    "1D": {
        "target_pct": 0.05,  # 5%
        "stop_pct": 0.05,  # 5%
        "min_hold_bars": 5,  # velas mínimas
        "max_hold_bars": 50,  # velas máximas
    },
    "4H": {
        "target_pct": 0.015,  # 1.5%
        "stop_pct": 0.02,  # 2%
        "min_hold_bars": 10,
        "max_hold_bars": 100,
    },
    "1H": {
        "target_pct": 0.008,  # 0.8%
        "stop_pct": 0.01,  # 1%
        "min_hold_bars": 20,
        "max_hold_bars": 200,
    },
}

# ──── Funciones de carga y preparación ─────────────────────────────────────────


def load_clean_data(tf):
    """Carga el CSV limpio correspondiente al timeframe."""
    # Intentar diferentes patrones (mayúsculas/minúsculas)
    patterns = [
        os.path.join(RESULTS_DIR, f"*{tf}*clean.csv"),
        os.path.join(RESULTS_DIR, f"*{tf.lower()}*clean.csv"),
        os.path.join(RESULTS_DIR, f"*{tf.upper()}*clean.csv"),
    ]

    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            # Tomar el primero (debería haber solo uno)
            filepath = files[0]
            df = pd.read_csv(filepath, parse_dates=["date"])
            break
    else:
        raise FileNotFoundError(
            f"No se encontró CSV limpio para {tf} (probé {patterns})"
        )

    # Filtrar filas con EMAs completas
    df = df.dropna(subset=["ema200"]).reset_index(drop=True)

    # Filtrar outliers extremos (valores fuera de [-100%, 100%] probablemente erróneos)
    for col in ["dist_p10", "dist_p55", "dist_p200"]:
        df = df[(df[col] >= -100) & (df[col] <= 100)]

    # Calcular percentiles históricos para distancias
    for col in ["dist_p10", "dist_p55", "dist_p200"]:
        # Usar percentil de toda la distribución (puede incluir valores positivos y negativos)
        p25 = df[col].quantile(0.25)
        p50 = df[col].quantile(0.50)
        p75 = df[col].quantile(0.75)
        df[f"{col}_p25"] = p25
        df[f"{col}_p50"] = p50
        df[f"{col}_p75"] = p75

        # También calcular percentil solo de valores negativos (para apoyos)
        neg_values = df[df[col] < 0][col]
        if len(neg_values) > 10:
            p25_neg = neg_values.quantile(0.25)
            df[f"{col}_p25_neg"] = p25_neg
        else:
            df[f"{col}_p25_neg"] = p25  # fallback

    # Calcular mediana del ratio armónico
    ratio_median = df["ratio_armonico"].median()
    df["ratio_median"] = ratio_median

    return df, filepath


def detect_signals(df, rule="apoyo10", tf="1D"):
    """Detecta señales de trading según la regla especificada."""
    signals = []

    if rule == "apoyo10":
        # Apoyo en EMA10: precio por debajo del percentil 25 de valores negativos y pendiente positiva
        # Usar p25_neg si existe, sino p25
        p25_col = (
            "dist_p10_p25_neg" if "dist_p10_p25_neg" in df.columns else "dist_p10_p25"
        )
        condition = (
            (
                df["dist_p10"] < df[p25_col]
            )  # Debajo del percentil 25 de valores negativos
            & (df["slope10"] > 0)  # EMA10 con pendiente positiva
        )

        # Filtro opcional: ratio armónico cerca de la mediana
        ratio_threshold = 0.1  # ±10% de la mediana
        ratio_condition = (
            abs(df["ratio_armonico"] - df["ratio_median"]) / abs(df["ratio_median"])
            < ratio_threshold
        )
        condition = condition & ratio_condition

    elif rule == "apoyo55":
        # Apoyo en EMA55
        condition = (df["dist_p55"] < df["dist_p55_p25"]) & (df["slope55"] > 0)
    elif rule == "apoyo200":
        # Apoyo en EMA200
        condition = (df["dist_p200"] < df["dist_p200_p25"]) & (df["slope200"] > 0)
    else:
        raise ValueError(f"Regla desconocida: {rule}")

    # Encontrar índices donde se cumple la condición
    signal_indices = df[condition].index.tolist()

    # Filtrar señales demasiado cercanas (evitar señales repetidas)
    min_gap = TF_CONFIG[tf]["min_hold_bars"]
    filtered_indices = []
    last_idx = -min_gap

    for idx in signal_indices:
        if idx - last_idx >= min_gap:
            filtered_indices.append(idx)
            last_idx = idx

    return filtered_indices


def simulate_trades(df, signal_indices, tf="1D"):
    """Simula operaciones a partir de las señales detectadas."""
    config = TF_CONFIG[tf]
    trades = []

    for idx in signal_indices:
        if idx >= len(df) - config["max_hold_bars"]:
            continue  # No hay suficiente datos adelante

        entry_price = df.loc[idx + 1, "close"]  # Entrar en la siguiente vela
        entry_date = df.loc[idx + 1, "date"]

        # Calcular precios objetivo y stop
        target_price = entry_price * (1 + config["target_pct"])
        stop_price = entry_price * (1 - config["stop_pct"])

        # Simular hacia adelante
        exit_idx = None
        exit_price = None
        exit_reason = None
        exit_date = None

        for lookahead in range(1, config["max_hold_bars"] + 1):
            if idx + 1 + lookahead >= len(df):
                break

            current_price = df.loc[idx + 1 + lookahead, "close"]
            current_date = df.loc[idx + 1 + lookahead, "date"]

            # Verificar si se alcanza objetivo o stop
            if current_price >= target_price:
                exit_idx = idx + 1 + lookahead
                exit_price = target_price  # Asumimos ejecución en target
                exit_reason = "target"
                exit_date = current_date
                break
            elif current_price <= stop_price:
                exit_idx = idx + 1 + lookahead
                exit_price = stop_price  # Asumimos ejecución en stop
                exit_reason = "stop"
                exit_date = current_date
                break

        # Si no se alcanzó ni target ni stop, salir al final del período
        if exit_idx is None:
            exit_idx = idx + config["max_hold_bars"]
            if exit_idx >= len(df):
                exit_idx = len(df) - 1
            exit_price = df.loc[exit_idx, "close"]
            exit_reason = "timeout"
            exit_date = df.loc[exit_idx, "date"]

        # Calcular métricas de la operación
        pct_return = (exit_price - entry_price) / entry_price
        hold_bars = exit_idx - (idx + 1)

        trades.append(
            {
                "entry_date": entry_date,
                "entry_price": entry_price,
                "exit_date": exit_date,
                "exit_price": exit_price,
                "exit_reason": exit_reason,
                "pct_return": pct_return,
                "hold_bars": hold_bars,
                "signal_idx": idx,
            }
        )

    return trades


def calculate_metrics(trades):
    """Calcula métricas de performance a partir de la lista de operaciones."""
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "total_return": 0,
            "avg_return": 0,
            "max_drawdown": 0,
            "expectancy": 0,
        }

    df_trades = pd.DataFrame(trades)
    df_trades["is_win"] = df_trades["pct_return"] > 0

    # Métricas básicas
    total_trades = len(df_trades)
    win_trades = df_trades["is_win"].sum()
    win_rate = win_trades / total_trades if total_trades > 0 else 0

    # Ganancias y pérdidas
    gains = df_trades[df_trades["pct_return"] > 0]["pct_return"].sum()
    losses = abs(df_trades[df_trades["pct_return"] < 0]["pct_return"].sum())
    profit_factor = gains / losses if losses > 0 else float("inf")

    # Retorno total y promedio
    total_return = df_trades["pct_return"].sum()
    avg_return = df_trades["pct_return"].mean()

    # Drawdown (simplificado)
    cumulative = (1 + df_trades["pct_return"]).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min() if len(drawdown) > 0 else 0

    # Expectativa
    avg_win = (
        df_trades[df_trades["is_win"]]["pct_return"].mean() if win_trades > 0 else 0
    )
    avg_loss = (
        df_trades[~df_trades["is_win"]]["pct_return"].mean()
        if total_trades - win_trades > 0
        else 0
    )
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "total_return": total_return,
        "avg_return": avg_return,
        "max_drawdown": max_drawdown,
        "expectancy": expectancy,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
    }


def run_backtest(tf, rule):
    """Ejecuta backtest completo para un timeframe y regla."""
    print(f"\n{'=' * 60}")
    print(f"BACKTEST: {tf} | Regla: {rule}")
    print(f"{'=' * 60}")

    # Cargar datos
    try:
        df, filepath = load_clean_data(tf)
        print(f"📂 Datos: {os.path.basename(filepath)}")
        print(
            f"   Filas: {len(df)} | Rango: {df['date'].iloc[0].date()} → {df['date'].iloc[-1].date()}"
        )
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return None

    # Detectar señales
    signal_indices = detect_signals(df, rule, tf)
    print(f"📈 Señales detectadas: {len(signal_indices)}")

    if len(signal_indices) < 5:
        print("⚠️  Pocas señales, métricas pueden no ser confiables")

    # Simular operaciones
    trades = simulate_trades(df, signal_indices, tf)
    print(f"📊 Operaciones simuladas: {len(trades)}")

    # Calcular métricas
    metrics = calculate_metrics(trades)

    # Mostrar resultados
    print(f"\n📊 RESULTADOS:")
    print(f"   Total operaciones: {metrics['total_trades']}")
    print(f"   Win rate: {metrics['win_rate']:.1%}")
    print(f"   Profit factor: {metrics['profit_factor']:.2f}")
    print(f"   Retorno total: {metrics['total_return']:.1%}")
    print(f"   Expectativa: {metrics['expectancy']:.3%}")
    print(f"   Drawdown máximo: {metrics['max_drawdown']:.1%}")

    # Guardar resultados detallados
    if trades:
        output_file = os.path.join(
            OUTPUT_DIR,
            f"backtest_{tf}_{rule}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        )
        pd.DataFrame(trades).to_csv(output_file, index=False)
        print(f"\n💾 Detalles guardados en: {os.path.basename(output_file)}")

    return {
        "timeframe": tf,
        "rule": rule,
        "metrics": metrics,
        "trades_count": len(trades),
        "signal_count": len(signal_indices),
    }


def run_sensitivity_analysis(tf="1D"):
    """Ejecuta análisis de sensibilidad para diferentes parámetros."""
    print(f"\n{'=' * 60}")
    print(f"ANÁLISIS DE SENSIBILIDAD: {tf}")
    print(f"{'=' * 60}")

    # Cargar datos
    try:
        df, _ = load_clean_data(tf)
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Probar diferentes percentiles como umbral
    percentiles = [0.1, 0.2, 0.25, 0.3, 0.35]
    results = []

    for pct in percentiles:
        # Calcular umbral basado en percentil
        threshold = df["dist_p10"].quantile(pct)

        # Detectar señales con este umbral
        condition = (df["dist_p10"] < threshold) & (df["slope10"] > 0)
        signal_indices = df[condition].index.tolist()

        # Filtrar señales cercanas
        min_gap = 10
        filtered = []
        last_idx = -min_gap
        for idx in signal_indices:
            if idx - last_idx >= min_gap:
                filtered.append(idx)
                last_idx = idx

        # Simular operaciones
        trades = simulate_trades(df, filtered, tf)
        metrics = calculate_metrics(trades)

        results.append(
            {
                "percentil": pct,
                "umbral": threshold,
                "señales": len(filtered),
                "operaciones": len(trades),
                "win_rate": metrics["win_rate"],
                "profit_factor": metrics["profit_factor"],
                "expectancy": metrics["expectancy"],
            }
        )

        print(
            f"  P{pct * 100:.0f} ({threshold:.2%}) → {len(filtered)} señales, {len(trades)} ops, WR: {metrics['win_rate']:.1%}, PF: {metrics['profit_factor']:.2f}"
        )

    # Guardar resultados
    df_results = pd.DataFrame(results)
    output_file = os.path.join(
        OUTPUT_DIR, f"sensibilidad_{tf}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    )
    df_results.to_csv(output_file, index=False)

    print(f"\n💾 Resultados guardados en: {os.path.basename(output_file)}")

    # Encontrar mejor configuración
    if len(results) > 0:
        best = max(results, key=lambda x: x["expectancy"])
        print(f"\n🎯 MEJOR CONFIGURACIÓN:")
        print(f"   Percentil: {best['percentil']}")
        print(f"   Umbral: {best['umbral']:.2%}")
        print(f"   Expectativa: {best['expectancy']:.3%}")
        print(f"   Win rate: {best['win_rate']:.1%}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Backtesting rápido para Magnitudes Armónicas"
    )
    parser.add_argument(
        "--tf", choices=["1D", "4H", "1H"], default="1D", help="Timeframe a analizar"
    )
    parser.add_argument(
        "--regla",
        choices=["apoyo10", "apoyo55", "apoyo200"],
        default="apoyo10",
        help="Regla de trading",
    )
    parser.add_argument(
        "--all", action="store_true", help="Ejecutar todos los timeframes y reglas"
    )
    parser.add_argument(
        "--sensibilidad", action="store_true", help="Ejecutar análisis de sensibilidad"
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("FASE 1: BACKTESTING RÁPIDO - MAGNITUDES ARMÓNICAS")
    print("=" * 60)

    if args.sensibilidad:
        run_sensitivity_analysis(args.tf)
        return

    if args.all:
        # Ejecutar todas las combinaciones
        all_results = []
        for tf in ["1D", "4H", "1H"]:
            for rule in ["apoyo10", "apoyo55", "apoyo200"]:
                result = run_backtest(tf, rule)
                if result:
                    all_results.append(result)

        # Generar reporte consolidado
        if all_results:
            df_summary = pd.DataFrame(
                [
                    {
                        "timeframe": r["timeframe"],
                        "rule": r["rule"],
                        "trades": r["trades_count"],
                        "win_rate": r["metrics"]["win_rate"],
                        "profit_factor": r["metrics"]["profit_factor"],
                        "expectancy": r["metrics"]["expectancy"],
                        "max_dd": r["metrics"]["max_drawdown"],
                    }
                    for r in all_results
                ]
            )

            output_file = os.path.join(
                OUTPUT_DIR,
                f"resumen_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            )
            df_summary.to_csv(output_file, index=False)

            print(f"\n📋 RESUMEN COMPLETO guardado en: {os.path.basename(output_file)}")
            print(df_summary.to_string())
    else:
        # Ejecutar solo una combinación
        run_backtest(args.tf, args.regla)


if __name__ == "__main__":
    main()
