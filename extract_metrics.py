import os
import re

results_dir = r"C:\Users\MI29541\ws\mystuff\analisisMath\results"

metrics = {}

for i in range(1, 43):
    metrics[i] = {
        "Hurst": "N/A",
        "FFT": "N/A",
        "Hilbert": "N/A",
        "Scale": "N/A",
        "Apoyo": "N/A",
        "Correlation": "N/A"
    }

# Regex patterns
hurst_re = re.compile(r"dist_p55:\s+H=([0-9.]+)")
fft_re = re.compile(r"dist_p55:.*?#1\s+([0-9.]+)\s+velas", re.DOTALL)
hilbert_re = re.compile(r"EMA55 \(dist_p55\).*?Período mediana:\s+([0-9.]+)\s+velas", re.DOTALL)
scale_re = re.compile(r"55/10\s+\|\s+([0-9.]+)\s+\|")
apoyo_re = re.compile(r"Apoyo en EMA55.*?tasa éxito \(subió\) = ([0-9.]+)%", re.DOTALL)
corr_re = re.compile(r"Lag óptimo\s+=\s+([+-]?[0-9.]+)\s+velas")

for i in range(1, 43):
    # 1. Hurst
    file_path = os.path.join(results_dir, f"pine-logs-Calculador de Magnitudes Armónicas ({i})_hurst_valores.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = hurst_re.search(content)
            if match:
                metrics[i]["Hurst"] = match.group(1)

    # 2. FFT
    file_path = os.path.join(results_dir, f"pine-logs-Calculador de Magnitudes Armónicas ({i})_fft_ciclos.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Need to find dist_p55 section specifically
            p55_part = re.search(r"dist_p55:(.*?)dist_p200:", content, re.DOTALL)
            if not p55_part:
                p55_part = re.search(r"dist_p55:(.*?)dist_10_55:", content, re.DOTALL)
            if p55_part:
                match = re.search(r"#1\s+([0-9.]+)\s+velas", p55_part.group(1))
                if match:
                    metrics[i]["FFT"] = match.group(1)

    # 3. Hilbert
    file_path = os.path.join(results_dir, f"pine-logs-Calculador de Magnitudes Armónicas ({i})_hilbert_resumen.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = hilbert_re.search(content)
            if match:
                metrics[i]["Hilbert"] = match.group(1)

    # 4. Scale
    file_path = os.path.join(results_dir, f"scale_pine-logs-Calculador de Magnitudes Armónicas ({i})_table.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = scale_re.search(content)
            if match:
                metrics[i]["Scale"] = match.group(1)

    # 5. Apoyo
    file_path = os.path.join(results_dir, f"pine-logs-Calculador de Magnitudes Armónicas ({i})_apoyo_stats.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = apoyo_re.search(content)
            if match:
                metrics[i]["Apoyo"] = match.group(1) + "%"

    # 6. Correlation
    file_path = os.path.join(results_dir, f"pine-logs-Calculador de Magnitudes Armónicas ({i})_correlation_stats.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = corr_re.search(content)
            if match:
                metrics[i]["Correlation"] = match.group(1)

# Generate Reports
print("REPORTE 1: Bloques por Archivo")
print("==============================")
for i in range(1, 43):
    m = metrics[i]
    print(f"ARCHIVO {i}: Hurst={m['Hurst']}, FFT={m['FFT']}, Hilbert={m['Hilbert']}, Scale={m['Scale']}, Apoyo={m['Apoyo']}, Correlation={m['Correlation']}")

print("\nREPORTE 2: Bloques por Estudio")
print("==============================")
for study in ["Hurst", "FFT", "Hilbert", "Scale", "Apoyo", "Correlation"]:
    print(f"\nESTUDIO {study.upper()}:")
    line = ""
    for i in range(1, 43):
        line += f"Archivo {i}={metrics[i][study]}, "
        if i % 5 == 0:
            print(line.strip())
            line = ""
    if line:
        print(line.strip())

print("\nTABLA COMPARATIVA FINAL")
print("=======================")
header = f"{'Arch':<5} | {'Hurst':<6} | {'FFT':<7} | {'Hilbert':<8} | {'Scale':<6} | {'Apoyo':<7} | {'Corr':<5}"
print(header)
print("-" * len(header))
for i in range(1, 43):
    m = metrics[i]
    print(f"{i:<5} | {m['Hurst']:<6} | {m['FFT']:<7} | {m['Hilbert']:<8} | {m['Scale']:<6} | {m['Apoyo']:<7} | {m['Correlation']:<5}")
