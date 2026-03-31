"""
generate_report.py — Generador de Reporte Maestro para IA Matemática
─────────────────────────────────────────────────────────────────────────────
Junta los resultados de todos los scripts (.txt) en un solo archivo Markdown
estructurado para ser "leído" por una IA (como ChatGPT o DeepSeek).

Genera: results/REPORTE_MATEMATICO_IA.md
"""

import os
import re
import glob

BASE = os.path.dirname(__file__)
RESULTS = os.path.join(BASE, "results")
OUT_FILE = os.path.join(RESULTS, "REPORTE_MATEMATICO_IA.md")


def extraer_seccion(texto, inicio, fin=None):
    """Extrae un bloque de texto entre dos marcadores."""
    try:
        idx_start = texto.find(inicio)
        if idx_start == -1:
            return ""
        if fin:
            idx_end = texto.find(fin, idx_start + len(inicio))
            if idx_end == -1:
                return texto[idx_start:]
            return texto[idx_start:idx_end].strip()
        return texto[idx_start:].strip()
    except:
        return ""


def procesar_txt(filepath):
    """Lee un archivo de texto y lo prepara para el MD."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def main():
    print(f"\n🚀 Generando Reporte Maestro en {OUT_FILE}...")

    tfs = ["1D", "4H", "1H"]
    reporte = []

    # 1. Cabecera y Antecedentes
    reporte.append("# 📊 REPORTE MAESTRO: Análisis de Magnitudes Armónicas (BTC/USD)")
    reporte.append("\n## 1. Contexto y Antecedentes")
    reporte.append(
        "Este reporte contiene el análisis matemático de las relaciones entre el precio de Bitcoin y tres Medias Móviles Exponenciales (EMAs) de 10, 55 y 200 períodos."
    )
    reporte.append("- **Fuente:** Logs de Pine Script v6 (TradingView).")
    reporte.append(
        "- **Variables de estudio:** Distancias porcentuales del precio a cada EMA (`dist_p10`, `dist_p55`, `dist_p200`) y distancias entre EMAs (`dist_10_55`, `dist_55_200`)."
    )
    reporte.append(
        "- **Objetivo:** Detectar constantes y magnitudes recurrentes para formalizar el patrón visual en un script algorítmico."
    )

    # 2. Resumen de Parámetros por Análisis
    reporte.append("\n## 2. Metodologías Aplicadas")
    reporte.append("| Análisis | Qué mide | Por qué es relevante |")
    reporte.append("|----------|----------|----------------------|")
    reporte.append(
        "| **FFT (Fourier)** | Ciclos dominantes | Identifica si las oscilaciones tienen una periodicidad fija (velas). |"
    )
    reporte.append(
        "| **Hurst** | Memoria (Persistencia) | H > 0.5 indica que la serie tiene memoria y tiende a seguir su tendencia. |"
    )
    reporte.append(
        "| **Hilbert** | Amplitud/Periodo inst. | Muestra cómo cambia la 'fuerza' y la velocidad del ciclo en el tiempo. |"
    )
    reporte.append(
        "| **Fibonacci** | Ratios armónicos | Busca si los retrocesos y tiempos coinciden con la proporción áurea. |"
    )
    reporte.append(
        "| **Apoyos** | Profundidad de rebote | Mide cuánto 'perfora' el precio la EMA antes de rebotar. |"
    )
    reporte.append(
        "| **Correlación** | Sincronía entre EMAs | Determina si las distancias entre EMAs se mueven juntas o con desfase. |"
    )
    reporte.append(
        "| **Escala** | Relaciones entre rangos | Verifica si las correcciones guardan proporciones matemáticas constantes. |"
    )
    reporte.append(
        "| **Comparación** | Consistencia multi-timeframe | Evalúa si los patrones se mantienen en diferentes escalas temporales. |"
    )

    # 3. Resultados Detallados por Timeframe
    reporte.append("\n## 3. Resultados Numéricos Consolidados")

    for tf in tfs:
        reporte.append(f"\n### 🕒 Timeframe: {tf}")

        # Buscar archivos de este TF
        archivos = {
            "Stats": glob.glob(os.path.join(RESULTS, f"explore_{tf}_stats.txt")),
            "Ciclos": glob.glob(os.path.join(RESULTS, f"fft_{tf}_ciclos.txt")),
            "Apoyos": glob.glob(os.path.join(RESULTS, f"apoyo_{tf}_stats.txt")),
            "Hurst": glob.glob(os.path.join(RESULTS, f"hurst_{tf}_valores.txt")),
            "Hilbert": glob.glob(os.path.join(RESULTS, f"hilbert_{tf}_resumen.txt")),
            "Fib": glob.glob(os.path.join(RESULTS, f"fibonacci_{tf}_stats.txt")),
            "Correlación": glob.glob(
                os.path.join(RESULTS, f"correlation_{tf}_stats.txt")
            ),
            "Escala": glob.glob(os.path.join(RESULTS, f"scale_{tf}_table.txt")),
        }

        for clave, paths in archivos.items():
            if paths:
                reporte.append(f"\n#### > {clave}")
                content = procesar_txt(paths[0])
                # Limpiar un poco el contenido para que sea más legible en MD
                content = content.replace("=", "").strip()
                reporte.append("```text")
                reporte.append(content)
                reporte.append("```")
            else:
                reporte.append(f"\n*Sin datos de {clave} para {tf}*")

    # 4. El PROMPT para la IA
    reporte.append("\n---")
    reporte.append("## 🤖 INSTRUCCIÓN PARA IA (PROMPT)")
    reporte.append("> **Copia y pega el siguiente texto en tu chat con IA:**")
    reporte.append("\n```text")
    reporte.append(
        "Actúa como una IA experta en análisis cuantitativo, procesamiento de señales y trading algorítmico."
    )
    reporte.append(
        "He realizado una serie de análisis matemáticos (Fourier, Hurst, Hilbert, Fibonacci, correlación, escala y comparación entre timeframes) sobre las distancias del precio de BTC a sus EMAs de 10, 55 y 200 períodos en diferentes timeframes (1D, 4H, 1H)."
    )
    reporte.append(
        "\nBasándote en los DATOS NUMÉRICOS proporcionados arriba en el reporte:"
    )
    reporte.append(
        "1. Identifica las MAGNITUDES RECURRENTES de las correcciones (¿a qué distancia típica en % rebotan los apoyos en cada EMA?)."
    )
    reporte.append(
        "2. Detecta si existe una RELACIÓN DE ESCALA constante entre los timeframes (¿se repiten los mismos ratios?)."
    )
    reporte.append(
        "3. Determina si el Exponente de Hurst y la Transformada de Hilbert confirman que el sistema es persistente y tiene ciclos estables."
    )
    reporte.append(
        "4. Concluye con un SET DE PARÁMETROS sugeridos (umbrales de entrada, filtros de tendencia y duraciones de ciclo) para implementar un indicador de 'Magnitudes Armónicas' en Pine Script v6 que detecte zonas de alta probabilidad de rebote."
    )
    reporte.append("```")

    # Guardar
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(reporte))

    print(f"✅ Reporte generado: {os.path.basename(OUT_FILE)}")


if __name__ == "__main__":
    main()
