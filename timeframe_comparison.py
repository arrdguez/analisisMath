"""
timeframe_comparison.py — Comparativa estructural entre series de datos
────────────────────────────────────────────────────────────────────
FASE 2.5: Compara métricas clave entre diferentes archivos para identificar
patrones estructurales que se repiten o varían entre activos/escalas.

Objetivos:
1. Comparar métricas en unidades relativas (velas y %)
2. Detectar qué patrones son universales
3. Proporcionar base para diseño de indicador adaptativo

Genera en results/:
  - comparison_summary.md       ← Tabla Markdown con todas las métricas
  - comparison_radar.png        ← Gráfico radar de métricas clave
  - comparison_table.txt        ← Tabla ASCII para consulta rápida
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from plot_style import BG_FIG, BG_AX, COLORS, estilo_ax

BASE = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, "results")

def timeframe_label(filename: str) -> str:
    base = os.path.basename(filename)
    return base.replace("_clean.csv", "").replace(".csv", "")

def parse_fft_ciclos(tf: str) -> dict:
    path = os.path.join(RESULTS, f"{tf}_fft_ciclos.txt")
    if not os.path.exists(path): return {}
    ciclos = {}
    current_var = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.endswith(":"):
                current_var = line[:-1]
                ciclos[current_var] = []
            elif line.startswith("    #"):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        velas = int(parts[1].replace("v", "").replace("velas", ""))
                        ciclos[current_var].append(velas)
                    except: continue
    return ciclos

def parse_apoyo_stats(tf: str) -> dict:
    path = os.path.join(RESULTS, f"{tf}_apoyo_stats.txt")
    if not os.path.exists(path): return {}
    stats = {"EMA10": {}, "EMA55": {}, "EMA200": {}}
    current_ema = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "EMA10" in line: current_ema = "EMA10"
            elif "EMA55" in line: current_ema = "EMA55"
            elif "EMA200" in line: current_ema = "EMA200"
            if current_ema:
                if "mediana =" in line:
                    val = line.split("=")[1].replace("%", "").strip()
                    stats[current_ema]["prof_mediana"] = float(val)
                elif "tasa éxito" in line:
                    val = line.split("=")[1].replace("%", "").strip()
                    stats[current_ema]["tasa_exito"] = float(val)
    return stats

def parse_hurst_valores(tf: str) -> dict:
    path = os.path.join(RESULTS, f"{tf}_hurst_valores.txt")
    if not os.path.exists(path): return {}
    hurst = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line and "H=" in line:
                parts = line.split(":")
                var = parts[0].strip()
                val = parts[1].split("H=")[1].split("→")[0].strip()
                hurst[var] = float(val)
    return hurst

def parse_hilbert_resumen(tf: str) -> dict:
    path = os.path.join(RESULTS, f"{tf}_hilbert_resumen.txt")
    if not os.path.exists(path): return {}
    hilbert = {}
    current_var = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "──" in line and "(" in line:
                current_var = line.split("(")[1].split(")")[0].strip()
                hilbert[current_var] = {}
            if current_var:
                if "Amplitud media:" in line:
                    val = line.split(":")[1].replace("%", "").strip()
                    hilbert[current_var]["amp_media"] = float(val)
                elif "Período mediana:" in line:
                    val = line.split(":")[1].replace("velas", "").strip()
                    hilbert[current_var]["periodo_mediana"] = float(val)
    return hilbert

def collect_all_metrics():
    clean_files = sorted(glob.glob(os.path.join(RESULTS, "*_clean.csv")))
    metrics = {}
    for path in clean_files:
        tf = timeframe_label(path)
        metrics[tf] = {
            "fft_ciclos": parse_fft_ciclos(tf),
            "apoyo_stats": parse_apoyo_stats(tf),
            "hurst_vals": parse_hurst_valores(tf),
            "hilbert_vals": parse_hilbert_resumen(tf),
        }
    return metrics

def plot_radar(metrics):
    if not metrics: return
    labels = ["Hurst EMA55", "Prob. Rebote 55", "Amplitud 55", "Periodo 55", "Hurst EMA200", "Prob. Rebote 200"]
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True), facecolor=BG_FIG)
    
    for tf, m in metrics.items():
        # Extraer valores normalizados para el radar (0-1)
        values = [
            m["hurst_vals"].get("dist_p55", 0.5),
            m["apoyo_stats"].get("EMA55", {}).get("tasa_exito", 50) / 100,
            min(1, m["hilbert_vals"].get("dist_p55", {}).get("amp_media", 0) / 20),
            min(1, m["hilbert_vals"].get("dist_p55", {}).get("periodo_mediana", 0) / 100),
            m["hurst_vals"].get("dist_p200", 0.5),
            m["apoyo_stats"].get("EMA200", {}).get("tasa_exito", 50) / 100,
        ]
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=tf)
        ax.fill(angles, values, alpha=0.1)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.title("Comparativa de Estructura Estocástica", y=1.1, fontweight='bold')
    plt.savefig(os.path.join(RESULTS, "comparison_radar.png"), dpi=130, bbox_inches="tight")
    plt.close()

def main():
    print("🚀 Iniciando Comparativa Agnóstica...")
    metrics = collect_all_metrics()
    if not metrics:
        print("❌ No hay métricas suficientes para comparar.")
        return
    plot_radar(metrics)
    print("✅ Comparativa completada. Revisa results/comparison_radar.png")

if __name__ == "__main__":
    main()
