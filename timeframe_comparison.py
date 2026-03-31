"""
timeframe_comparison.py — Comparativa consolidada entre timeframes
────────────────────────────────────────────────────────────────────
FASE 2.5: Compara métricas clave entre 1D, 4H y 1H para identificar
patrones que se repiten o varían con la escala temporal.

Objetivos:
1. Convertir todas las métricas a unidades comparables (días)
2. Identificar relaciones de escala entre timeframes
3. Detectar qué patrones son universales vs específicos de timeframe
4. Proporcionar base para diseño de indicador multi-timeframe

Genera en results/:
  - comparison_summary.md       ← Tabla Markdown con todas las métricas
  - comparison_radar.png        ← Gráfico radar de 6 métricas clave
  - comparison_scaling.png      ← Relación de escalas entre TFs
  - comparison_table.txt        ← Tabla ASCII para consulta rápida

Uso:
  python timeframe_comparison.py
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from plot_style import BG_FIG, BG_AX, COLORS, estilo_ax

BASE = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, "results")

# Factores de conversión velas → días
# 1D = 1 día por vela, 4H = 0.167 días por vela (4/24), 1H = 0.0417 días por vela
TF_CONVERSION = {"1D": 1.0, "4H": 1 / 6.0, "1H": 1 / 24.0}
TF_ORDER = ["1D", "4H", "1H"]  # orden de procesamiento

# ── helpers ───────────────────────────────────────────────────────────────────


def load(path: str) -> pd.DataFrame:
    """Carga CSV limpio y filtra filas sin EMA200."""
    df = pd.read_csv(path, parse_dates=["date"])
    return df.dropna(subset=["ema200"]).reset_index(drop=True)


def timeframe_label(filename: str) -> str:
    """Extrae timeframe (1D, 4H, 1H) del nombre del archivo."""
    name = os.path.basename(filename).upper()
    for tf in ("1D", "4H", "1H"):
        if tf in name:
            return tf
    return "UNK"


def parse_fft_ciclos(tf: str) -> dict:
    """
    Lee archivo fft_{TF}_ciclos.txt y extrae ciclos dominantes.
    Retorna: {'dist_p10': [ciclos], 'dist_p55': [ciclos], ...}
    """
    path = os.path.join(RESULTS, f"fft_{tf}_ciclos.txt")
    if not os.path.exists(path):
        return {}

    ciclos = {}
    current_var = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.endswith(":"):
                current_var = line[:-1]  # quitar ':'
                ciclos[current_var] = []
            elif line.startswith("    #"):
                # Formato: #1  15 velas  (12.34% de la energía)
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        velas = int(parts[1].replace("v", "").replace("velas", ""))
                        ciclos[current_var].append(velas)
                    except:
                        continue

    return ciclos


def parse_apoyo_stats(tf: str) -> dict:
    """
    Lee archivo apoyo_{TF}_stats.txt y extrae métricas clave.
    Retorna: {'EMA10': {'prof_mediana': X, 'tasa_exito': Y, ...}, ...}
    """
    path = os.path.join(RESULTS, f"apoyo_{tf}_stats.txt")
    if not os.path.exists(path):
        return {}

    stats = {"EMA10": {}, "EMA55": {}, "EMA200": {}}
    current_ema = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "Apoyo en EMA" in line:
                if "EMA10" in line:
                    current_ema = "EMA10"
                elif "EMA55" in line:
                    current_ema = "EMA55"
                elif "EMA200" in line:
                    current_ema = "EMA200"
            elif current_ema and "mediana =" in line:
                # Ej: "mediana = -3.45%"
                try:
                    value = float(line.split("=")[1].replace("%", "").strip())
                    if "profundidad" in line.lower():
                        stats[current_ema]["prof_mediana"] = value
                    elif "rebote" in line.lower():
                        stats[current_ema]["rebote_mediana"] = value
                except:
                    continue
            elif current_ema and "tasa éxito" in line:
                # Ej: "tasa éxito (subió) = 75.9%"
                try:
                    value = float(line.split("=")[1].replace("%", "").strip())
                    stats[current_ema]["tasa_exito"] = value
                except:
                    continue

    return stats


def parse_hurst(tf: str) -> dict:
    """
    Lee archivo hurst_{TF}_valores.txt y extrae valores H.
    Retorna: {'dist_p10': H, 'dist_p55': H, ...}
    """
    path = os.path.join(RESULTS, f"hurst_{tf}_valores.txt")
    if not os.path.exists(path):
        return {}

    hurst_vals = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "dist_" in line and "H=" in line:
                # Ej: "dist_p10:  H=0.645 → Persistente moderada"
                parts = line.split(":")
                if len(parts) >= 2:
                    var = parts[0].strip()
                    # Extraer valor H
                    h_part = parts[1]
                    h_start = h_part.find("H=")
                    if h_start != -1:
                        h_end = h_part.find(" ", h_start)
                        if h_end == -1:
                            h_end = h_part.find("→", h_start)
                        if h_end != -1:
                            try:
                                h_val = float(h_part[h_start + 2 : h_end].strip())
                                hurst_vals[var] = h_val
                            except:
                                continue

    return hurst_vals


def parse_hilbert(tf: str) -> dict:
    """
    Lee archivo hilbert_{TF}_resumen.txt y extrae amplitud y período.
    Retorna: {'dist_p10': {'amp_media': X, 'periodo_mediana': Y}, ...}
    """
    path = os.path.join(RESULTS, f"hilbert_{tf}_resumen.txt")
    if not os.path.exists(path):
        return {}

    hilbert_vals = {}
    current_var = None

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "──" in line and "(" in line and ")" in line:
                # Ej: "── EMA10 (dist_p10) ──"
                start = line.find("(")
                end = line.find(")")
                if start != -1 and end != -1:
                    current_var = line[start + 1 : end]
                    hilbert_vals[current_var] = {}
            elif current_var and "Amplitud media:" in line:
                try:
                    value = float(line.split(":")[1].replace("%", "").strip())
                    hilbert_vals[current_var]["amp_media"] = value
                except:
                    continue
            elif current_var and "Período mediana:" in line:
                try:
                    value = float(line.split(":")[1].replace("velas", "").strip())
                    hilbert_vals[current_var]["periodo_mediana"] = value
                except:
                    continue

    return hilbert_vals


def collect_metrics():
    """
    Recolecta todas las métricas de los 3 timeframes.
    Retorna: dict anidado {tf: {metric_type: values}}
    """
    all_metrics = {}

    # Buscar archivos clean usando detección flexible de timeframe
    clean_files = {}
    all_clean = glob.glob(os.path.join(RESULTS, "*_clean.csv"))
    for path in all_clean:
        tf = timeframe_label(path)
        if tf in TF_ORDER:  # Solo procesar timeframes conocidos
            clean_files[tf] = path
        else:
            print(f"  ⚠️  Ignorado: {os.path.basename(path)} (timeframe no reconocido)")

    for tf, path in clean_files.items():
        print(f"📂 Procesando {tf}...")
        df = load(path)

        # Estadísticas descriptivas básicas
        desc_stats = {}
        for col in ["dist_p10", "dist_p55", "dist_p200", "dist_10_55", "dist_55_200"]:
            data = df[col].dropna()
            if len(data) > 0:
                desc_stats[col] = {
                    "mediana": float(data.median()),
                    "p25": float(data.quantile(0.25)),
                    "p75": float(data.quantile(0.75)),
                    "media": float(data.mean()),
                    "std": float(data.std()),
                }

        # Ciclos FFT (convertir a días)
        fft_ciclos_raw = parse_fft_ciclos(tf)
        fft_ciclos_dias = {}
        for var, ciclos_velas in fft_ciclos_raw.items():
            if ciclos_velas:
                # Tomar el ciclo dominante (primero de la lista)
                ciclo_dias = ciclos_velas[0] * TF_CONVERSION[tf]
                fft_ciclos_dias[var] = ciclo_dias

        # Apoyos
        apoyo_stats = parse_apoyo_stats(tf)

        # Hurst
        hurst_vals = parse_hurst(tf)

        # Hilbert
        hilbert_vals = parse_hilbert(tf)

        # Ratio Armónico
        ratio_data = df["ratio_armonico"].replace([np.inf, -np.inf], np.nan).dropna()
        ratio_stats = {
            "mediana": float(ratio_data.median()),
            "p25": float(ratio_data.quantile(0.25)),
            "p75": float(ratio_data.quantile(0.75)),
        }

        all_metrics[tf] = {
            "desc_stats": desc_stats,
            "fft_ciclos_dias": fft_ciclos_dias,
            "apoyo_stats": apoyo_stats,
            "hurst_vals": hurst_vals,
            "hilbert_vals": hilbert_vals,
            "ratio_stats": ratio_stats,
            "n_filas": len(df),
            "rango_fechas": f"{df['date'].iloc[0].date()} → {df['date'].iloc[-1].date()}",
        }

    return all_metrics


# ── gráfica 1: radar de métricas clave ───────────────────────────────────────


def plot_radar(metrics: dict):
    """Gráfico radar comparando 6 métricas clave entre timeframes."""
    if len(metrics) < 2:
        print("  ⚠️  Necesita al menos 2 timeframes para comparación radar")
        return

    # Seleccionar métricas para radar (normalizadas)
    radar_metrics = [
        "dist_p10_mediana",
        "dist_p55_mediana",
        "dist_p200_mediana",
        "hurst_promedio",
        "amp_media_p10",
        "tasa_exito_ema10",
    ]

    # Preparar datos
    radar_data = {}
    tfs = list(metrics.keys())

    for tf in tfs:
        m = metrics[tf]
        values = []

        # 1. dist_p10 mediana (normalizar respecto a máximo)
        val = abs(m["desc_stats"].get("dist_p10", {}).get("mediana", 0))
        values.append(val)

        # 2. dist_p55 mediana
        val = abs(m["desc_stats"].get("dist_p55", {}).get("mediana", 0))
        values.append(val)

        # 3. dist_p200 mediana
        val = abs(m["desc_stats"].get("dist_p200", {}).get("mediana", 0))
        values.append(val)

        # 4. Hurst promedio (convertir a escala 0-1, donde 0.5=0, 1.0=1)
        hurst_vals = list(m["hurst_vals"].values())
        if hurst_vals:
            avg_h = np.mean(hurst_vals)
            # Mapear: 0.5→0, 1.0→1
            hurst_scaled = (avg_h - 0.5) * 2
            values.append(max(0, min(1, hurst_scaled)))
        else:
            values.append(0)

        # 5. Amplitud media dist_p10
        amp = m["hilbert_vals"].get("dist_p10", {}).get("amp_media", 0)
        values.append(abs(amp))

        # 6. Tasa éxito EMA10
        tasa = m["apoyo_stats"].get("EMA10", {}).get("tasa_exito", 0)
        values.append(tasa / 100.0)  # convertir % a 0-1

        radar_data[tf] = values

    # Normalizar cada métrica al máximo entre timeframes
    for i in range(len(radar_metrics)):
        col_vals = [radar_data[tf][i] for tf in tfs]
        max_val = max(col_vals) if col_vals else 1
        if max_val > 0:
            for tf in tfs:
                radar_data[tf][i] = radar_data[tf][i] / max_val

    # Crear gráfico radar
    angles = np.linspace(0, 2 * np.pi, len(radar_metrics), endpoint=False).tolist()
    angles += angles[:1]  # cerrar el polígono

    fig, ax = plt.subplots(
        figsize=(10, 10), subplot_kw=dict(projection="polar"), facecolor=BG_FIG
    )

    # Colores por timeframe
    tf_colors = {
        "1D": COLORS["dist_p10"],
        "4H": COLORS["dist_p55"],
        "1H": COLORS["dist_p200"],
    }

    for tf in tfs:
        values = radar_data[tf]
        values += values[:1]  # cerrar el polígono
        ax.plot(
            angles, values, linewidth=2, label=tf, color=tf_colors.get(tf, "#888888")
        )
        ax.fill(angles, values, alpha=0.15, color=tf_colors.get(tf, "#888888"))

    # Configurar ejes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m.replace("_", "\n") for m in radar_metrics], fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=7, color="#666666")
    ax.grid(color="#cccccc", linewidth=0.5, linestyle="--", alpha=0.7)

    # Añadir círculos de referencia
    for r in [0.25, 0.5, 0.75, 1.0]:
        circle = Circle(
            (0, 0),
            r,
            transform=ax.transData._b,
            fill=False,
            edgecolor="#dddddd",
            linewidth=0.5,
            linestyle="--",
        )
        ax.add_artist(circle)

    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0), fontsize=9)
    ax.set_title(
        "Comparativa Radar: Métricas Normalizadas por Timeframe\n"
        "(Valores normalizados al máximo entre TFs)",
        fontsize=11,
        fontweight="bold",
        pad=20,
    )

    out = os.path.join(RESULTS, "comparison_radar.png")
    plt.savefig(out, dpi=130, bbox_inches="tight", facecolor=BG_FIG)
    plt.close()
    print(f"  📊 {os.path.basename(out)}")


# ── gráfica 2: relación de escalas ───────────────────────────────────────────


def plot_scaling(metrics: dict):
    """Gráfica de relaciones de escala entre timeframes."""
    if len(metrics) < 2:
        return

    # Métricas para comparar escalas
    scale_metrics = [
        ("Ciclo dominante dist_p10 (días)", "fft_ciclos_dias", "dist_p10"),
        ("Ciclo dominante dist_p55 (días)", "fft_ciclos_dias", "dist_p55"),
        ("Amplitud media dist_p10 (%)", "hilbert_vals", ("dist_p10", "amp_media")),
        ("Profundidad apoyo EMA10 (%)", "apoyo_stats", ("EMA10", "prof_mediana")),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor=BG_FIG)
    axes = axes.flatten()

    for idx, (title, metric_type, key) in enumerate(scale_metrics):
        if idx >= len(axes):
            break

        ax = axes[idx]
        tfs = []
        values = []

        for tf in TF_ORDER:
            if tf not in metrics:
                continue

            m = metrics[tf]
            if metric_type == "fft_ciclos_dias":
                val = m.get(metric_type, {}).get(key, np.nan)
            elif metric_type == "hilbert_vals":
                if isinstance(key, tuple):
                    val = m.get(metric_type, {}).get(key[0], {}).get(key[1], np.nan)
                else:
                    val = m.get(metric_type, {}).get(key, np.nan)
            elif metric_type == "apoyo_stats":
                if isinstance(key, tuple):
                    val = m.get(metric_type, {}).get(key[0], {}).get(key[1], np.nan)
                else:
                    val = m.get(metric_type, {}).get(key, np.nan)
            else:
                val = np.nan

            if not np.isnan(val):
                tfs.append(tf)
                values.append(abs(val))

        if len(values) >= 2:
            ax.bar(
                tfs,
                values,
                color=[COLORS["dist_p10"], COLORS["dist_p55"], COLORS["dist_p200"]][
                    : len(tfs)
                ],
            )
            ax.set_xlabel("Timeframe", fontsize=9)
            ax.set_ylabel(title.split("(")[-1].replace(")", ""), fontsize=9)
            ax.set_title(title, fontsize=10, fontweight="bold")

            # Añadir valores encima de las barras
            for i, v in enumerate(values):
                ax.text(i, v * 1.02, f"{v:.2f}", ha="center", fontsize=8)

            # Calcular y mostrar ratio de escala
            if len(values) == 3:
                ratio_4H_1D = values[1] / values[0] if values[0] != 0 else np.nan
                ratio_1H_1D = values[2] / values[0] if values[0] != 0 else np.nan
                ax.text(
                    0.5,
                    0.95,
                    f"4H/1D: {ratio_4H_1D:.2f}\n1H/1D: {ratio_1H_1D:.2f}",
                    transform=ax.transAxes,
                    fontsize=8,
                    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                )

        estilo_ax(ax)

    plt.tight_layout()
    out = os.path.join(RESULTS, "comparison_scaling.png")
    plt.savefig(out, dpi=130, bbox_inches="tight", facecolor=BG_FIG)
    plt.close()
    print(f"  📊 {os.path.basename(out)}")


# ── reportes de texto ────────────────────────────────────────────────────────


def write_summary_md(metrics: dict):
    """Genera reporte Markdown con tabla comparativa completa."""
    lines = [
        "# 📊 COMPARATIVA ENTRE TIMEFRAMES",
        "## Resumen Ejecutivo",
        "Esta tabla compara métricas clave entre los timeframes 1D, 4H y 1H.",
        "Todas las métricas de tiempo (ciclos) están convertidas a días para comparación directa.",
        "",
        "## Tabla Comparativa",
        "| Métrica | 1D | 4H | 1H | Notas |",
        "|---------|----|----|----|-------|",
    ]

    # 1. Estadísticas descriptivas
    lines.append("| **ESTADÍSTICAS DESCRIPTIVAS** | | | | |")
    for var in ["dist_p10", "dist_p55", "dist_p200"]:
        for stat_name, stat_key in [("Mediana", "mediana"), ("p25-p75", "range")]:
            row = [f"{var} {stat_name}"]
            for tf in TF_ORDER:
                if tf in metrics:
                    desc = metrics[tf]["desc_stats"].get(var, {})
                    if stat_key == "mediana":
                        val = desc.get("mediana", np.nan)
                        if not np.isnan(val):
                            row.append(f"{val:+.2f}%")
                        else:
                            row.append("–")
                    elif stat_key == "range":
                        p25 = desc.get("p25", np.nan)
                        p75 = desc.get("p75", np.nan)
                        if not np.isnan(p25) and not np.isnan(p75):
                            row.append(f"{p25:+.1f}–{p75:+.1f}%")
                        else:
                            row.append("–")
                else:
                    row.append("–")
            row.append("Distancia precio→EMA")
            lines.append("| " + " | ".join(row) + " |")

    # 2. Ciclos dominantes (en días)
    lines.append("| **CICLOS DOMINANTES (días)** | | | | |")
    for var in ["dist_p10", "dist_p55", "dist_p200", "dist_10_55", "dist_55_200"]:
        row = [f"{var} ciclo"]
        for tf in TF_ORDER:
            if tf in metrics:
                ciclo = metrics[tf]["fft_ciclos_dias"].get(var, np.nan)
                if not np.isnan(ciclo):
                    row.append(f"{ciclo:.1f}d")
                else:
                    row.append("–")
            else:
                row.append("–")
        row.append("FFT, ciclo #1 en días")
        lines.append("| " + " | ".join(row) + " |")

    # 3. Apoyos
    lines.append("| **APOYOS (profundidad media)** | | | | |")
    for ema in ["EMA10", "EMA55", "EMA200"]:
        row = [f"{ema} prof."]
        for tf in TF_ORDER:
            if tf in metrics:
                prof = (
                    metrics[tf]["apoyo_stats"].get(ema, {}).get("prof_mediana", np.nan)
                )
                if not np.isnan(prof):
                    row.append(f"{prof:+.2f}%")
                else:
                    row.append("–")
            else:
                row.append("–")
        row.append("Profundidad mediana del apoyo")
        lines.append("| " + " | ".join(row) + " |")

    # 4. Hurst
    lines.append("| **EXPONENTE DE HURST** | | | | |")
    for var in ["dist_p10", "dist_p55", "dist_p200", "dist_10_55", "dist_55_200"]:
        row = [f"{var} H"]
        for tf in TF_ORDER:
            if tf in metrics:
                h = metrics[tf]["hurst_vals"].get(var, np.nan)
                if not np.isnan(h):
                    row.append(f"{h:.3f}")
                else:
                    row.append("–")
            else:
                row.append("–")
        row.append("H>0.5=persistente, H<0.5=anti-persistente")
        lines.append("| " + " | ".join(row) + " |")

    # 5. Hilbert
    lines.append("| **HILBERT (amplitud media)** | | | | |")
    for var in ["dist_p10", "dist_p55", "dist_p200"]:
        row = [f"{var} amp."]
        for tf in TF_ORDER:
            if tf in metrics:
                amp = metrics[tf]["hilbert_vals"].get(var, {}).get("amp_media", np.nan)
                if not np.isnan(amp):
                    row.append(f"{amp:.2f}%")
                else:
                    row.append("–")
            else:
                row.append("–")
        row.append("Amplitud media de la oscilación")
        lines.append("| " + " | ".join(row) + " |")

    # 6. Ratio Armónico
    lines.append("| **RATIO ARMÓNICO** | | | | |")
    row = ["Mediana"]
    for tf in TF_ORDER:
        if tf in metrics:
            med = metrics[tf]["ratio_stats"].get("mediana", np.nan)
            if not np.isnan(med):
                row.append(f"{med:.3f}")
            else:
                row.append("–")
        else:
            row.append("–")
    row.append("dist_10_55 / dist_55_200")
    lines.append("| " + " | ".join(row) + " |")

    row = ["Rango IQR"]
    for tf in TF_ORDER:
        if tf in metrics:
            p25 = metrics[tf]["ratio_stats"].get("p25", np.nan)
            p75 = metrics[tf]["ratio_stats"].get("p75", np.nan)
            if not np.isnan(p25) and not np.isnan(p75):
                row.append(f"{p25:.3f}–{p75:.3f}")
            else:
                row.append("–")
        else:
            row.append("–")
    row.append("Rango intercuartil (p25–p75)")
    lines.append("| " + " | ".join(row) + " |")

    # 7. Metadatos
    lines.append("")
    lines.append("## Metadatos")
    for tf in TF_ORDER:
        if tf in metrics:
            lines.append(f"### {tf}")
            lines.append(f"- Filas: {metrics[tf]['n_filas']:,}")
            lines.append(f"- Rango: {metrics[tf]['rango_fechas']}")
            lines.append(f"- Conversión días/vela: {TF_CONVERSION[tf]:.4f}")

    lines.append("")
    lines.append("## Conclusiones Clave")
    lines.append(
        "1. **Escalas temporales:** Los ciclos en timeframe menores deberían ser proporcionales a la escala temporal."
    )
    lines.append(
        "2. **Consistencia:** Las métricas que se mantienen similares entre timeframes indican patrones universales."
    )
    lines.append(
        "3. **Diseño de indicador:** Considerar relaciones de escala para parámetros adaptativos por timeframe."
    )

    out = os.path.join(RESULTS, "comparison_summary.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  📄 {os.path.basename(out)}")


def write_table_txt(metrics: dict):
    """Genera tabla ASCII compacta para consulta rápida."""
    lines = [
        "COMPARATIVA TIMEFRAMES - RESUMEN ASCII",
        "=" * 70,
    ]

    # Encabezado
    header = f"{'Métrica':<25} {'1D':>10} {'4H':>10} {'1H':>10}"
    lines.append(header)
    lines.append("-" * 70)

    # Datos clave
    key_metrics = [
        ("dist_p10 mediana%", "desc_stats", "dist_p10", "mediana", "{:+.2f}"),
        ("dist_p10 ciclo(d)", "fft_ciclos_dias", "dist_p10", None, "{:.1f}"),
        ("EMA10 prof.%", "apoyo_stats", ("EMA10", "prof_mediana"), None, "{:+.2f}"),
        ("EMA10 tasa%", "apoyo_stats", ("EMA10", "tasa_exito"), None, "{:.1f}"),
        ("dist_p10 H", "hurst_vals", "dist_p10", None, "{:.3f}"),
        ("dist_p10 amp.%", "hilbert_vals", ("dist_p10", "amp_media"), None, "{:.2f}"),
        ("ratio_arm med", "ratio_stats", "mediana", None, "{:.3f}"),
    ]

    for label, mtype, key, subkey, fmt in key_metrics:
        row = [label]
        for tf in TF_ORDER:
            if tf not in metrics:
                row.append("       –")
                continue

            m = metrics[tf]
            if mtype == "desc_stats":
                val = m[mtype].get(key, {}).get(subkey, np.nan)
            elif mtype == "fft_ciclos_dias":
                val = m[mtype].get(key, np.nan)
            elif mtype == "apoyo_stats":
                val = m[mtype].get(key[0], {}).get(key[1], np.nan)
            elif mtype == "hurst_vals":
                val = m[mtype].get(key, np.nan)
            elif mtype == "hilbert_vals":
                val = m[mtype].get(key[0], {}).get(key[1], np.nan)
            elif mtype == "ratio_stats":
                val = m[mtype].get(key, np.nan)
            else:
                val = np.nan

            if np.isnan(val):
                row.append("       –")
            else:
                row.append(fmt.format(val).rjust(8))

        lines.append("  ".join(row))

    lines.append("")
    lines.append("NOTA: valores en días para ciclos, % para distancias y amplitudes")

    out = os.path.join(RESULTS, "comparison_table.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  📄 {os.path.basename(out)}")


# ── main ─────────────────────────────────────────────────────────────────────


def main():
    """Punto de entrada principal."""
    print("\n🔍 Recolectando métricas de todos los timeframes...")

    # Recolectar métricas
    metrics = collect_metrics()

    if not metrics:
        print("❌ No se encontraron datos suficientes para comparación")
        return

    print(f"✅ Datos recolectados de {len(metrics)} timeframe(s)")

    # Generar visualizaciones y reportes
    plot_radar(metrics)
    plot_scaling(metrics)
    write_summary_md(metrics)
    write_table_txt(metrics)

    print("\n✅ Comparativa completada. Revisa la carpeta results/")


if __name__ == "__main__":
    main()
