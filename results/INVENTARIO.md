# 📦 Inventario de `results/`

Este archivo explica cada archivo generado en esta carpeta, qué script lo produjo
y cómo leerlo.

---

## 📊 Archivos de datos limpios (generados por `parse_csv.py`)

| Archivo | Qué contiene |
|---------|-------------|
| `*_clean.csv` | Datos limpiados y listos para análisis. |

**Columnas:** `date, close, ema10, ema55, ema200, dist_p10, dist_p55, dist_p200, slope10, slope55, slope200, dist_10_55, dist_55_200, ratio_armonico`

---

## 🔍 Análisis exploratorio (generados por `explore.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `explore_{TF}_distancias.png` | Serie temporal + histograma de dist_p10/55/200 | Verde = precio sobre EMA, rojo = bajo. Histograma: línea cyan = mediana, naranja = p5/p95 |
| `explore_{TF}_ratio.png` | dist_10_55, dist_55_200 y ratio_armonico | Positivo = estructura alcista. Ratio negativo = estructura mixta |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `explore_{TF}_stats.txt` | Percentiles de todas las variables | p25/p75 = zona normal. p5/p95 = extremos poco frecuentes |

---

## 〰️ Análisis de ciclos FFT (generados por `fft_analysis.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `fft_{TF}_espectro.png` | Espectro de potencia de las 5 variables | Pico = ciclo real. Espectro plano = ruido. Eje X = duración en velas (escala log) |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `fft_{TF}_ciclos.txt` | Top 5 ciclos dominantes por variable | `N velas (X%)` → si X > 10% el ciclo es muy fuerte. Convertir a días: 1D×1, 4H×0.167, 1H×0.042 |

---

## 📍 Análisis de apoyos (generados por `apoyo_stats.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `apoyo_{TF}_detalle.png` | Apoyos históricos en EMA10/55/200 marcados sobre la serie | Puntos de color = evento de apoyo. Líneas horizontales = percentiles de profundidad |
| `apoyo_{TF}_rebote.png` | Distribución del rebote 10 velas después del apoyo | Derecha del cero = subió. Línea cyan = mediana. El título dice la tasa de éxito |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `apoyo_{TF}_stats.txt` | Profundidad y rebote de cada apoyo | Mediana profundidad = distancia típica. Tasa éxito = % que rebotó |

---

## 🧠 Exponente de Hurst (generados por `hurst.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `hurst_{TF}_rs.png` | Gráfica del análisis R/S (Rescaled Range) | Pendiente de la línea = valor de H. Compara con H=0.5 (aleatorio) |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `hurst_{TF}_valores.txt` | Un valor H por cada variable de distancia | H > 0.5 = persistente (memoria), H < 0.5 = anti-persistente (revierte) |

---

## 🌊 Transformada de Hilbert (generados por `hilbert_analysis.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `hilbert_{TF}_envolvente.png` | Amplitud instantánea de las oscilaciones | Muestra cómo crece o decrece la "fuerza" de la oscilación en el tiempo |
| `hilbert_{TF}_frecuencia.png` | Período instantáneo (duración del ciclo actual) | Muestra si el mercado se está acelerando (ciclos cortos) o frenando (ciclos largos) |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `hilbert_{TF}_resumen.txt` | Estadísticas de amplitud y período típicos | Amplitud media y variabilidad del ciclo (rango p25/p75) |

---

## 📐 Análisis de Fibonacci (generados por `fibonacci_analysis.py`)

### Imágenes
| Archivo | Qué muestra | Cómo leerlo |
|---------|-------------|-------------|
| `fibonacci_{TF}_tiempos.png` | Histograma de ratios de tiempo entre apoyos | ¿Los apoyos ocurren en proporciones de 0.618 o 1.618? |
| `fibonacci_{TF}_amplitudes.png` | Histograma de ratios de retroceso (valle/pico) | ¿Las correcciones frenan en niveles Fib (0.382, 0.5, 0.618)? |

### Textos
| Archivo | Qué contiene | Cómo leerlo |
|---------|-------------|-------------|
| `fibonacci_{TF}_stats.txt` | Resumen de proximidad a niveles Fibonacci | Indica qué nivel Fib es el más cercano a la mediana de los datos |

---

## 🔄 Cuándo regenerar los archivos

Todos los archivos de esta carpeta son **outputs reproducibles**. Si borras cualquiera,
se puede regenerar corriendo el script correspondiente o `main.py`.

| Si cambias... | Vuelve a correr... |
|--------------|-------------------|
| Datos en `data/` | `python main.py --pasos parse` → luego todos los demás |
| Solo quieres actualizar un análisis | `python main.py --pasos <nombre_paso>` |
| Todo desde cero | `python main.py` |
