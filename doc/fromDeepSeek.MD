
# Plan de Análisis de Patrones Armónicos con Medias Móviles (10, 55, 200)

## 1. Introducción

El objetivo es transformar una estrategia de trading subjetiva basada en la interacción del precio con las medias móviles exponenciales (EMA) de 10, 55 y 200 periodos en un sistema cuantificable y automatizable. La observación visual muestra que en tendencia alcista el precio se apoya sucesivamente en las EMAs 10, 55 y 200, formando ondas que convergen y divergen con aparente armonía, posiblemente siguiendo proporciones de Fibonacci o comportamientos fractales. Se busca describir matemáticamente este fenómeno, medir sus magnitudes y validar si existen relaciones armónicas repetibles.

## 2. Objetivos

- Definir variables objetivas que capturen la dinámica del precio respecto a las EMAs.
- Extraer datos históricos y transformarlos en series temporales de magnitudes clave.
- Detectar automáticamente los puntos de apoyo del precio en cada EMA.
- Analizar las oscilaciones de las distancias para identificar ciclos dominantes.
- Verificar la existencia de proporciones áureas (0.618, 1.618) en los tiempos entre apoyos y en las amplitudes.
- Evaluar la fractalidad mediante el exponente de Hurst.
- Proporcionar una base sólida para la construcción futura de un indicador o sistema de trading.

## 3. Datos

- **Activo:** BTC/USDT (u otro par).
- **Temporalidad:** 4 horas (puede extenderse a otras).
- **Período:** Desde ~22 de marzo de 2026 hasta 31 de marzo de 2026 (muestra inicial).
- **Fuente:** TradingView, exportación de logs generados por un script Pine Script que calcula las siguientes magnitudes en cada vela:
  - `close`, `ema10`, `ema55`, `ema200`
  - `dist_price_10` = (close - ema10) / ema10 * 100 (%)
  - `dist_price_55` = (close - ema55) / ema55 * 100 (%)
  - `dist_price_200` = (close - ema200) / ema200 * 100 (%)
  - `dist_10_55` = (ema10 - ema55) / ema55 * 100 (%)
  - `dist_55_200` = (ema55 - ema200) / ema200 * 100 (%)
  - `slope10` = (ema10 - ema10[5]) / ema10[5] * 100 (pendiente en 5 velas)
  - `slope55`, `slope200` análogos.

El script original (Pine Script) se encuentra al inicio del historial. Se ha exportado un archivo de log con formato CSV que contiene líneas con timestamp y las 12 columnas numéricas.

## 4. Limpieza de Datos

El archivo exportado presenta duplicados, líneas mal formateadas y algunos valores no numéricos. Se debe realizar una limpieza con Python para obtener un DataFrame ordenado.

### 4.1 Código de limpieza (Python)

```python
import pandas as pd
import re

# Leer archivo de texto (ajustar ruta)
with open('datos_btc.txt', 'r') as f:
    lines = f.readlines()

cleaned = []
for line in lines:
    line = line.strip().strip('"')
    if not line:
        continue
    parts = line.split(',')
    if len(parts) < 2:
        continue
    ts = parts[0].strip()
    rest = ','.join(parts[1:]).strip().strip('"')
    numbers = re.split(r'\s+', rest)
    numbers = [n for n in numbers if n]
    if len(numbers) != 12:
        print(f"Saltando línea con {len(numbers)} números: {ts}")
        continue
    nums = [float(x) for x in numbers]
    cleaned.append([ts] + nums)

columns = ['timestamp', 'close', 'ema10', 'ema55', 'ema200',
           'dist_price_10', 'dist_price_55', 'dist_price_200',
           'dist_10_55', 'dist_55_200',
           'slope10', 'slope55', 'slope200']
df = pd.DataFrame(cleaned, columns=columns)
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp'], keep='first')
print(df.shape)
df.head()
```

## 5. Análisis Exploratorio

### 5.1 Visualización de Series Temporales

Graficar precio con EMAs y las series de distancias para identificar visualmente los apoyos y las fases del patrón.

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

axes[0].plot(df['timestamp'], df['close'], label='Precio', alpha=0.7)
axes[0].plot(df['timestamp'], df['ema10'], label='EMA10', linestyle='--')
axes[0].plot(df['timestamp'], df['ema55'], label='EMA55', linestyle='--')
axes[0].plot(df['timestamp'], df['ema200'], label='EMA200', linestyle='--')
axes[0].legend()
axes[0].set_title('Precio y EMAs')

axes[1].plot(df['timestamp'], df['dist_price_10'], label='Dist a EMA10')
axes[1].plot(df['timestamp'], df['dist_price_55'], label='Dist a EMA55')
axes[1].plot(df['timestamp'], df['dist_price_200'], label='Dist a EMA200')
axes[1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
axes[1].legend()
axes[1].set_title('Distancias relativas precio-EMA (%)')

axes[2].plot(df['timestamp'], df['dist_10_55'], label='EMA10 - EMA55 (%)')
axes[2].plot(df['timestamp'], df['dist_55_200'], label='EMA55 - EMA200 (%)')
axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.3)
axes[2].legend()
axes[2].set_title('Diferencia entre EMAs (%)')

plt.tight_layout()
plt.show()
```

### 5.2 Detección de Apoyos (Cruces desde abajo)

Un apoyo ocurre cuando el precio cruza la EMA desde abajo (o toca un rango de tolerancia). Inicialmente se define como:

```python
df['support_10'] = (df['close'] > df['ema10']) & (df['close'].shift(1) <= df['ema10'].shift(1))
df['support_55'] = (df['close'] > df['ema55']) & (df['close'].shift(1) <= df['ema55'].shift(1))
df['support_200'] = (df['close'] > df['ema200']) & (df['close'].shift(1) <= df['ema200'].shift(1))
```

Para mayor precisión, se puede añadir una condición de distancia máxima a la EMA (ej. dentro de un ±0.5% en el momento del cruce) para filtrar falsos apoyos.

## 6. Análisis de Oscilaciones

### 6.1 Transformada de Fourier (FFT)

Se aplica a la serie `dist_price_10` (o `dist_price_55`, `dist_price_200`) para identificar frecuencias dominantes. La periodicidad en horas se obtiene como 1/frecuencia.

```python
import numpy as np
from scipy.fft import fft, fftfreq

serie = df['dist_price_10'].dropna().values
n = len(serie)
fft_vals = fft(serie)
freqs = fftfreq(n, d=4)  # d=4 horas
magnitudes = np.abs(fft_vals)

plt.figure(figsize=(10,4))
plt.stem(freqs[:n//2], magnitudes[:n//2], basefmt=" ")
plt.xlabel('Frecuencia (ciclos/hora)')
plt.ylabel('Magnitud')
plt.title('Espectro de Fourier - distancia a EMA10')
plt.xlim(0, 0.1)
plt.show()
```

Si se encuentran picos significativos, se registran sus períodos. Luego se comparan con los tiempos entre apoyos detectados manualmente.

### 6.2 Transformada de Hilbert (Fase Instantánea)

Para series cuasi-periódicas, la transformada de Hilbert permite extraer la envolvente y la fase instantánea, lo que ayuda a ver si la frecuencia cambia con el tiempo (modulación).

```python
from scipy.signal import hilbert

analytic_signal = hilbert(serie)
amplitude_envelope = np.abs(analytic_signal)
instantaneous_phase = np.unwrap(np.angle(analytic_signal))
instantaneous_frequency = np.diff(instantaneous_phase) / (2.0*np.pi) * (1/4)  # en ciclos/hora
```

## 7. Relaciones de Fibonacci

### 7.1 Análisis de Duración entre Apoyos

Se extraen los timestamps de los apoyos en cada EMA y se calculan las duraciones (en horas) entre apoyo en EMA10 y el siguiente en EMA55, y entre EMA55 y el siguiente en EMA200. Se calcula el ratio `duración10_55 / duración55_200`.

```python
ts_10 = df[df['support_10']]['timestamp'].values
ts_55 = df[df['support_55']]['timestamp'].values
ts_200 = df[df['support_200']]['timestamp'].values

ratios = []
for t10 in ts_10:
    futuros_55 = ts_55[ts_55 > t10]
    if len(futuros_55) == 0: continue
    t55 = futuros_55[0]
    futuros_200 = ts_200[ts_200 > t55]
    if len(futuros_200) == 0: continue
    t200 = futuros_200[0]
    dur10_55 = (t55 - t10).total_seconds() / 3600
    dur55_200 = (t200 - t55).total_seconds() / 3600
    if dur55_200 != 0:
        ratios.append(dur10_55 / dur55_200)
```

Se grafica un histograma de los ratios y se superponen líneas en 0.618 y 1.618.

### 7.2 Relación entre Amplitudes

Se miden los picos de `dist_price_10` (máximo alejamiento) y los valles (apoyos) para ver si las correcciones guardan proporción de Fibonacci (0.382, 0.5, 0.618). Se puede usar la función `scipy.signal.find_peaks` para detectar máximos y mínimos locales.

## 8. Fractalidad: Exponente de Hurst

El exponente de Hurst se calcula mediante el análisis R/S para determinar si la serie es persistente (H > 0.5), aleatoria (H ≈ 0.5) o anti-persistente (H < 0.5). Se aplica a la serie de precios y a las distancias.

```python
def hurst(ts):
    lags = range(2, min(len(ts)//2, 100))
    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0] * 2.0

hurst_price = hurst(df['close'].values)
hurst_dist10 = hurst(df['dist_price_10'].dropna().values)
print(f"Hurst precio: {hurst_price:.3f}")
print(f"Hurst dist10: {hurst_dist10:.3f}")
```

Si H es consistentemente > 0.6, hay memoria larga y podría justificarse un modelo fractal.

## 9. Modelado de Fases (Opcional)

Una vez identificadas las fases (impulso, apoyo en EMA10, apoyo en EMA55, apoyo en EMA200, convergencia), se puede etiquetar el dataset y analizar transiciones mediante una cadena de Markov o árboles de decisión para predecir la siguiente fase.

## 10. Herramientas y Recursos

- **Python 3.8+** con librerías: pandas, numpy, matplotlib, scipy, scikit-learn (opcional).
- **Jupyter Notebook** para el análisis interactivo.
- **TradingView** para exportar datos (mediante script Pine Script mejorado).
- **Git** para versionado del código.

## 11. Próximos Pasos

1. Limpiar y estructurar los datos exportados.
2. Realizar análisis exploratorio y visualizaciones.
3. Detectar apoyos con reglas ajustables y validar con observaciones visuales.
4. Aplicar FFT, Hilbert y análisis de Fibonacci.
5. Calcular exponente de Hurst.
6. Documentar resultados y decidir si se justifica la creación de un indicador/trading system.
7. Opcional: entrenar un modelo de clasificación de fases.

## 12. Consideraciones Finales

- El análisis debe repetirse en diferentes temporalidades (1h, 1d) y activos para verificar generalidad.
- Se deben probar diferentes tipos de medias (SMA vs EMA) y períodos (por ejemplo, 10, 55, 200 son valores comunes; podrían optimizarse).
- La subjetividad del trader debe traducirse en umbrales cuantitativos (ej. “apoyo” = distancia < 0.2% y pendiente de la media positiva, etc.).

---

Este plan proporciona una hoja de ruta completa para transformar una observación cualitativa en un modelo cuantificable. La implementación de cada paso debe ser realizada con cuidado, documentando los resultados intermedios para asegurar que el patrón armónico se reproduce de manera consistente.


