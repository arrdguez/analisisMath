"""
contact_dynamics_analysis.py — Análisis de la dinámica y cinemática de contacto
───────────────────────────────────────────────────────────────────────────────
V1.1: Añadidas métricas de Impacto (Velocidad y Aceleración de Llegada)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from scipy.signal import hilbert

# Configuración
DATA_DIR = 'results/'
OUTPUT_DIR = 'results/contact_dynamics/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def n_hurst(series, min_lags=10, max_lags=50):
    if len(series) < max_lags: return 0.5
    lags = range(min_lags, max_lags)
    tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0] * 2.0

def analyze_contacts(df, tf, ema_col='dist_p55'):
    # Normalización por volatilidad (Z-Score)
    volatilidad = df[ema_col].rolling(window=20).std()
    z_score = df[ema_col] / volatilidad
    
    # Identificación de Zonas de Contacto (Z-Score entre -0.5 y 0.5)
    in_contact = (z_score.abs() < 0.5).astype(int)
    df['contact_change'] = in_contact.diff().fillna(0)
    starts = df.index[df['contact_change'] == 1].tolist()
    ends = df.index[df['contact_change'] == -1].tolist()
    
    if len(ends) > 0 and len(starts) > 0:
        if ends[0] < starts[0]: ends.pop(0)
        if len(starts) > len(ends): starts.pop()
    
    results = []
    
    for start, end in zip(starts, ends):
        duration = end - start
        if duration < 3: continue
        
        # ── CINEMÁTICA DE LLEGADA (10 VELAS PREVIAS) ──
        pre_segment = df[ema_col].iloc[max(0, start-10):start]
        if len(pre_segment) < 5: continue
        
        # Velocidad: Pendiente de la aproximación
        arrival_velocity = np.polyfit(range(len(pre_segment)), pre_segment.values, 1)[0]
        # Aceleración: Cambio en la velocidad (segunda derivada simplificada)
        velocities = np.diff(pre_segment.values)
        arrival_acceleration = np.mean(np.diff(velocities)) if len(velocities) > 2 else 0
        
        # ── DINÁMICA DURANTE EL CONTACTO ──
        during_contact = df[ema_col].iloc[start:end]
        h_during = n_hurst(during_contact.values)
        
        # Energía (Hilbert)
        analytic_signal = hilbert(during_contact.values)
        amplitude_envelope = np.abs(analytic_signal)
        energy_slope = np.polyfit(range(len(amplitude_envelope)), amplitude_envelope, 1)[0] if len(amplitude_envelope) > 5 else 0
        
        # ── RESULTADO (POST-CONTACTO) ──
        after_contact = df[ema_col].iloc[end:min(len(df), end+10)]
        outcome_val = after_contact.iloc[-1] if not after_contact.empty else 0
        
        # Clasificación Cinemática
        # Lento: Velocidad baja (< mediana), suele ser absorción
        # Violento: Velocidad alta (> mediana), suele ser ruptura
        impact_type = 'VIOLENTO' if abs(arrival_velocity) > df[ema_col].std() * 0.1 else 'LENTO'
        
        results.append({
            'start_idx': start,
            'duration': duration,
            'arrival_velocity': arrival_velocity,
            'arrival_accel': arrival_acceleration,
            'h_during': h_during,
            'energy_slope': energy_slope,
            'outcome': outcome_val,
            'impact_type': impact_type,
            'dynamics_type': 'PERSISTENTE' if (duration > 12 or h_during < 0.5) else 'TRANSITORIO'
        })
        
    return pd.DataFrame(results)

def main():
    print("🚀 Iniciando Análisis Cinemático de Contacto (V1.1)...")
    paths = glob.glob(os.path.join('results/', '*_clean.csv'))
    
    for path in paths:
        tf = os.path.basename(path).split('-')[0]
        print(f"--- Procesando {tf} ---")
        df = pd.read_csv(path)
        
        for ema in ['dist_p10', 'dist_p55', 'dist_p200']:
            if ema not in df.columns: continue
            print(f"  Analizando {ema}...")
            res_df = analyze_contacts(df, tf, ema)
            
            if not res_df.empty:
                res_df.to_csv(f"{OUTPUT_DIR}{tf}_{ema}_contact_dynamics.csv", index=False)
                
                # Análisis de Correlación: Velocidad vs Resultado
                lento = res_df[res_df['impact_type'] == 'LENTO']
                violento = res_df[res_df['impact_type'] == 'VIOLENTO']
                
                print(f"    Impactos LENTOS (Absorción): {len(lento)}")
                print(f"    Impactos VIOLENTOS (Ruptura): {len(violento)}")
                
                # Graficar Velocidad de Llegada vs Duración
                plt.figure(figsize=(10,6))
                plt.scatter(lento['arrival_velocity'], lento['duration'], color='green', alpha=0.5, label='Lento (Absorción Probable)')
                plt.scatter(violento['arrival_velocity'], violento['duration'], color='red', alpha=0.5, label='Violento (Ruptura Probable)')
                plt.title(f"Cinemática de Llegada {tf} - {ema}\n(Velocidad de aproximación vs Tiempo de residencia)")
                plt.xlabel("Velocidad de Llegada (Pendiente %/vela)")
                plt.ylabel("Duración del contacto (velas)")
                plt.legend()
                plt.savefig(f"{OUTPUT_DIR}{tf}_{ema}_kinematics.png")
                plt.close()

    print(f"\n✅ Análisis completado. Revisa {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
