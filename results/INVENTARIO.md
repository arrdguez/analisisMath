# 📦 Inventario de `results/`

Este archivo explica cada archivo generado en esta carpeta, qué script lo produjo
y cómo leerlo.

---

## 📊 Archivos de datos limpios (generados por `parse_csv.py`)

| Archivo | Qué contiene |
|---------|-------------|
| `1D-btc-pine-logs-..._clean.csv` | Datos diarios BTC limpiados. 2906 filas. Rango 2018→2026 |
| `1h-btc-pine-logs-..._clean.csv` | Datos horarios BTC limpiados. 10000 filas. Rango 2025→2026 |
| `4h-btc-pine-logs-..._clean.csv` | Datos 4 horas BTC limpiados. 9960 filas. Rango 2021→2026 |

**Columnas:** `date, close, ema10, ema55, ema200, dist_p10, dist_p55, dist_p200, slope10, slope55, slope200, dist_10_55, dist_55_200, ratio_armonico`

---

## 🔍 Análisis exploratorio (generados por `explore.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `explore_1D_distancias.png` | Serie temporal + histograma de dist_p10/55/200 en 1D | Verde = precio sobre EMA, rojo = bajo. Histograma: línea cyan = mediana, naranja = p5/p95 |
| `explore_1D_ratio.png` | dist_10_55, dist_55_200 y ratio_armonico en 1D | Positivo = estructura alcista. Ratio negativo = estructura mixta |
| `explore_4H_distancias.png` | Idem en 4H | Igual que 1D |
| `explore_4H_ratio.png` | Idem en 4H | Igual que 1D |
| `explore_1H_distancias.png` | Idem en 1H | Igual que 1D |
| `explore_1H_ratio.png` | Idem en 1H | Igual que 1D |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `explore_1D_stats.txt` | Percentiles de todas las variables en 1D | p25/p75 = zona normal. p5/p95 = extremos poco frecuentes |
| `explore_4H_stats.txt` | Idem en 4H | Igual |
| `explore_1H_stats.txt` | Idem en 1H | Igual |

---

## 〰️ Análisis de ciclos FFT (generados por `fft_analysis.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `fft_1D_espectro.png` | Espectro de potencia de las 5 variables en 1D | Pico = ciclo real. Espectro plano = ruido. Eje X = duración en velas (escala log) |
| `fft_4H_espectro.png` | Idem en 4H | Igual |
| `fft_1H_espectro.png` | Idem en 1H | Igual |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `fft_1D_ciclos.txt` | Top 5 ciclos dominantes por variable en 1D | `N velas (X%)` → si X > 10% el ciclo es muy fuerte. Convertir a días: 1D×1, 4H×0.167, 1H×0.042 |
| `fft_4H_ciclos.txt` | Idem en 4H | Igual |
| `fft_1H_ciclos.txt` | Idem en 1H | Igual |

---

## 📍 Análisis de apoyos (generados por `apoyo_stats.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `apoyo_1D_detalle.png` | Apoyos históricos en EMA10/55/200 marcados sobre la serie | Puntos de color = evento de apoyo. Líneas horizontales = percentiles de profundidad |
| `apoyo_1D_rebote.png` | Distribución del rebote 10 velas después del apoyo | Derecha del cero = subió. Línea cyan = mediana. El título dice la tasa de éxito |
| `apoyo_4H_detalle.png` | Idem en 4H | Igual |
| `apoyo_4H_rebote.png` | Idem en 4H | Igual |
| `apoyo_1H_detalle.png` | Idem en 1H | Igual |
| `apoyo_1H_rebote.png` | Idem en 1H | Igual |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `apoyo_1D_stats.txt` | Profundidad y rebote de cada apoyo en 1D | Mediana profundidad = distancia típica. Tasa éxito = % que rebotó |
| `apoyo_4H_stats.txt` | Idem en 4H | Igual |
| `apoyo_1H_stats.txt` | Idem en 1H | Igual |

---

## 🔄 Cuándo regenerar los archivos

Todos los archivos de esta carpeta son **outputs reproducibles**. Si borras cualquiera,
se puede regenerar corriendo el script correspondiente.

| Si cambias... | Vuelve a correr... |
|--------------|-------------------|
| Datos en `data/` | `parse_csv.py` → luego todos los demás |
| Solo quieres actualizar gráficas | `explore.py` |
| Solo quieres actualizar ciclos | `fft_analysis.py` |
| Solo quieres actualizar apoyos | `apoyo_stats.py` |
| Todo desde cero | `python parse_csv.py && python explore.py && python fft_analysis.py && python apoyo_stats.py` |
