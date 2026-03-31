# 📊 COMPARATIVA ENTRE TIMEFRAMES
## Resumen Ejecutivo
Esta tabla compara métricas clave entre los timeframes 1D, 4H y 1H.
Todas las métricas de tiempo (ciclos) están convertidas a días para comparación directa.

## Tabla Comparativa
| Métrica | 1D | 4H | 1H | Notas |
|---------|----|----|----|-------|
| **ESTADÍSTICAS DESCRIPTIVAS** | | | | |
| dist_p10 Mediana | +0.19% | +0.03% | +0.01% | Distancia precio→EMA |
| dist_p10 p25-p75 | -2.1–+2.6% | -0.7–+0.8% | -0.3–+0.3% | Distancia precio→EMA |
| dist_p55 Mediana | +0.61% | -0.01% | -0.04% | Distancia precio→EMA |
| dist_p55 p25-p75 | -6.3–+9.7% | -2.1–+2.2% | -0.9–+0.8% | Distancia precio→EMA |
| dist_p200 Mediana | +6.17% | -0.19% | -0.12% | Distancia precio→EMA |
| dist_p200 p25-p75 | -13.0–+21.8% | -4.2–+5.4% | -2.0–+1.5% | Distancia precio→EMA |
| **CICLOS DOMINANTES (días)** | | | | |
| dist_p10 ciclo | – | – | – | FFT, ciclo #1 en días |
| dist_p55 ciclo | – | – | – | FFT, ciclo #1 en días |
| dist_p200 ciclo | – | – | – | FFT, ciclo #1 en días |
| dist_10_55 ciclo | – | – | – | FFT, ciclo #1 en días |
| dist_55_200 ciclo | – | – | – | FFT, ciclo #1 en días |
| **APOYOS (profundidad media)** | | | | |
| EMA10 prof. | – | – | – | Profundidad mediana del apoyo |
| EMA55 prof. | – | – | – | Profundidad mediana del apoyo |
| EMA200 prof. | – | – | – | Profundidad mediana del apoyo |
| **EXPONENTE DE HURST** | | | | |
| dist_p10 H | 0.790 | 0.769 | 0.763 | H>0.5=persistente, H<0.5=anti-persistente |
| dist_p55 H | 0.948 | 0.930 | 0.922 | H>0.5=persistente, H<0.5=anti-persistente |
| dist_p200 H | 1.001 | 0.998 | 0.980 | H>0.5=persistente, H<0.5=anti-persistente |
| dist_10_55 H | 0.943 | 0.927 | 0.918 | H>0.5=persistente, H<0.5=anti-persistente |
| dist_55_200 H | 0.993 | 0.996 | 0.988 | H>0.5=persistente, H<0.5=anti-persistente |
| **HILBERT (amplitud media)** | | | | |
| dist_p10 amp. | 5.49% | 1.77% | 0.74% | Amplitud media de la oscilación |
| dist_p55 amp. | 16.22% | 4.84% | 1.89% | Amplitud media de la oscilación |
| dist_p200 amp. | 34.73% | 10.11% | 3.60% | Amplitud media de la oscilación |
| **RATIO ARMÓNICO** | | | | |
| Mediana | 0.306 | 0.302 | 0.313 | dist_10_55 / dist_55_200 |
| Rango IQR | -0.050–0.790 | -0.074–0.837 | -0.168–0.927 | Rango intercuartil (p25–p75) |

## Metadatos
### 1D
- Filas: 2,906
- Rango: 2018-04-18 → 2026-03-31
- Conversión días/vela: 1.0000
### 4H
- Filas: 9,960
- Rango: 2021-09-13 → 2026-03-31
- Conversión días/vela: 0.1667
### 1H
- Filas: 10,000
- Rango: 2025-02-07 → 2026-03-31
- Conversión días/vela: 0.0417

## Conclusiones Clave
1. **Escalas temporales:** Los ciclos en timeframe menores deberían ser proporcionales a la escala temporal.
2. **Consistencia:** Las métricas que se mantienen similares entre timeframes indican patrones universales.
3. **Diseño de indicador:** Considerar relaciones de escala para parámetros adaptativos por timeframe.