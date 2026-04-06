import os
import re
from collections import Counter

def process_hurst(file_path):
    hurst_values = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'H=([\d\.]+)', content)
        for m in matches:
            hurst_values.append(float(m))
    return hurst_values

def process_fft(file_path):
    cycles = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'#\d+\s+(\d+)\s+velas', content)
        for m in matches:
            cycles.append(int(m))
    return cycles

def process_apoyo(file_path):
    success_rate = None
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Look specifically for EMA55 section
        ema55_section = re.search(r'── Apoyo en EMA55.*?──(.*?)── Apoyo en EMA200', content, re.DOTALL)
        if not ema55_section:
            # Maybe it's at the end
            ema55_section = re.search(r'── Apoyo en EMA55.*?──(.*)', content, re.DOTALL)
        
        if ema55_section:
            section_text = ema55_section.group(1)
            match = re.search(r'tasa éxito \(subió\) = ([\d\.]+)%', section_text)
            if match:
                success_rate = float(match.group(1))
    return success_rate

results_dir = 'results'
hurst_all = []
fft_all = []
apoyo_all = []
file_stats = {}

files = os.listdir(results_dir)

for i in range(43):
    suffix = f" ({i})" if i > 0 else ""
    base_name = f"pine-logs-Calculador de Magnitudes Armónicas{suffix}"
    
    hurst_file = os.path.join(results_dir, f"{base_name}_hurst_valores.txt")
    fft_file = os.path.join(results_dir, f"{base_name}_fft_ciclos.txt")
    apoyo_file = os.path.join(results_dir, f"{base_name}_apoyo_stats.txt")
    
    current_file_stats = {'base': base_name}
    
    if os.path.exists(hurst_file):
        h_vals = process_hurst(hurst_file)
        hurst_all.extend(h_vals)
        current_file_stats['hurst_avg'] = sum(h_vals)/len(h_vals) if h_vals else None
        current_file_stats['hurst_min'] = min(h_vals) if h_vals else None
        current_file_stats['hurst_max'] = max(h_vals) if h_vals else None
        
    if os.path.exists(fft_file):
        f_vals = process_fft(fft_file)
        fft_all.extend(f_vals)
        
    if os.path.exists(apoyo_file):
        s_rate = process_apoyo(apoyo_file)
        if s_rate is not None:
            apoyo_all.append(s_rate)
            current_file_stats['apoyo_ema55'] = s_rate
            
    file_stats[base_name] = current_file_stats

# 1. Hurst Range
h_min = min(hurst_all) if hurst_all else 0
h_max = max(hurst_all) if hurst_all else 0

# 2. Top 3 FFT Cycles
fft_counts = Counter(fft_all).most_common(3)

# 3. Avg Success EMA55
apoyo_avg = sum(apoyo_all)/len(apoyo_all) if apoyo_all else 0

# 4. Outliers
# Simple outlier detection based on Hurst or Apoyo
outliers = []
if apoyo_all:
    mean_apoyo = sum(apoyo_all)/len(apoyo_all)
    std_apoyo = (sum((x - mean_apoyo)**2 for x in apoyo_all) / len(apoyo_all))**0.5
    for name, stats in file_stats.items():
        if 'apoyo_ema55' in stats:
            if abs(stats['apoyo_ema55'] - mean_apoyo) > 2 * std_apoyo:
                outliers.append(f"{name} (Apoyo EMA55: {stats['apoyo_ema55']}%)")

print(f"HURST_RANGE: {h_min} - {h_max}")
print(f"TOP_3_FFT: {fft_counts}")
print(f"AVG_EMA55_SUCCESS: {apoyo_avg:.2f}%")
print(f"OUTLIERS: {', '.join(outliers)}")
