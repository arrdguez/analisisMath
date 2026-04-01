# 📌 PROYECTO: Análisis de Magnitudes Armónicas en EMAs
**Fecha de inicio:** 2026-03-30  
**Activo principal de estudio:** BTC/USD  
**Estado:** **COMPLETADO** — Todas las fases implementadas (11 scripts, análisis matemáticos completos)

---

## 🎯 OBJETIVO CENTRAL

> Estudiar matemáticamente un patrón que el trader **YA VE con los ojos** y que le funciona en su sistema de trading real. El objetivo NO es crear un indicador todavía. El objetivo es **describir y medir el fenómeno** de manera objetiva, usando herramientas matemáticas/estadísticas para que lo que se ve visualmente quede formalizado en números.
El objetivo o uno de ellos es ecnontrar patrones estadisticos que se repitan y crear u obtener una o mas variables que una vez teniendola podamos usarlas para crear un indicador tectino. 
Se asume que cada mercado y temporalidad sea diferente pero en todas el ser humano está presente y esa comportamiento debe tener una huella, que por minima que sea se desea encontrar y usarla. Muchas veces la magnituda que se busca no es directa si no indirecta. El objetivo es que esta herramienta nos sorva para encontrar variables que luego sean usadas para analizar el mercado, en otras palabras lo que aca hacemos no es perce un analisis del mercado es sun analisis previos para descubri patrones metris variables que luego usaremos para crear una herrmaienta que eso si nos ayudara a leer el mercado. 

---

## 🧠 DESCRIPCIÓN DEL FENÓMENO (en palabras del trader)

El precio, en tendencia alcista, interactúa con tres EMAs (10, 55, 200) de una manera **oscilatoria y jerárquica**:

1. El precio sube **por encima** de la EMA10 y en algún momento **se apoya** en ella (no necesariamente la toca, a veces solo hace el amago y rebota o pasa de largo un poco y hace el rebote).
2. Cuando la corrección es mayor y sigue de paso, el precio se apoya en la **EMA55**, haciendo un poco los mismo que se describio antes en todas las medias.
3. Las correcciones más grandes llevan el precio hasta la zona de la **EMA200**.
4. Esto genera un comportamiento de **ondas armónicas**: oscilaciones que convergen y divergen entre las tres medias, como si hubiera una "respiración" del mercado.
5. En tendencia bajista ocurre lo mismo pero invertido: el precio cae por debajo de las tres medias y rebota hacia arriba hacia ellas.
6. El patrón es **multi-timeframe**: se ve en 1D, 4H, 1W, 1M.
7. Se cree que si superponemos todas las ondas, ej hacemos que el precio sea liso el resto de medias hará ondas que formarra ondas constructivas y destructivas y resonará, de modo que cuando todoas convergenen en espacio y tiempo pueden hacer que sea facil y probabilisticamente mas fiable entrar al alza o a la baja. 

### 🟢 Observación clave del trader:
> "En el SP500 casi nunca llega a tocar las medias, solo hace el amago pero ese amago es de muchos puntos y se le puede sacar $" otros mercados hace lo mismo 

> IMPORTANTE: La herramienta debe ser adnostica no debe estar pensada solo para un mercado o temporalidad. 

Esto implica que **el apoyo no es un toque exacto**, es una **región de intención** donde el precio desacelera y revierte. La distancia mínima al apoyo es en sí misma un dato medible.

---

## 📐 VARIABLES YA CALCULADAS (Pine Script → CSV)

El indicador `Calculador de Magnitudes Armónicas` ya exporta todas las variables necesarias:

| Columna | Variable | Descripción |
|---------|----------|-------------|
| 0 | `close` | Precio de cierre |
| 1 | `ema10` | EMA de 10 períodos |
| 2 | `ema55` | EMA de 55 períodos |
| 3 | `ema200` | EMA de 200 períodos |
| 4 | `dist_price_10` | `(close - ema10) / ema10 * 100` % |
| 5 | `dist_price_55` | `(close - ema55) / ema55 * 100` % |
| 6 | `dist_price_200` | `(close - ema200) / ema200 * 100` % |
| 7 | `slope10` | Pendiente EMA10 en 5 velas (%) |
| 8 | `slope55` | Pendiente EMA55 en 5 velas (%) |
| 9 | `slope200` | Pendiente EMA200 en 5 velas (%) |
| 10 | `dist_10_55` | `(ema10 - ema55) / ema55 * 100` % |
| 11 | `dist_55_200` | `(ema55 - ema200) / ema200 * 100` % |

> **Ratio Armónico** (calculado en tabla visual pero no exportado en log):  
> `dist_10_55 / dist_55_200`

---

## 📁 DATOS DISPONIBLES

| Archivo | Timeframe | Filas | Rango | EMA200 completa |
|---------|-----------|-------|-------|-----------------|
| `1D-..._clean.csv` | 1 Día | 3,104 | 2017-10-01 → 2026-03-31 | 2,905 filas (93.6%) |
| `1h-..._clean.csv` | 1 Hora | 418 | 2025-02-07 → 2026-03-31 | 418 filas (100%) |
| `4h-..._clean.csv` | 4 Horas | 1,661 | 2021-09-13 → 2026-03-31 | 1,661 filas (100%) |

### ⚠️ Formato del CSV (importante para el parser)
```
Date,Message
2017-10-12T00:00:00.000-00:00,";5,430;4,688.223;NaN;NaN;15.822;NaN;..."
```
- Separador de columnas dentro del mensaje: **`;`**
- Separador de miles en números: **`,`** (ej: `4,688.223` = cuatro mil seiscientos ochenta y ocho)
- Valores faltantes: **`NaN`** (EMA10 disponible desde vela 10, EMA55 desde vela 55, EMA200 desde vela 200)
- Al final del archivo hay **filas duplicadas** con formato diferente (líneas `barstate.islast` del Pine Script) — deben filtrarse.

---

## 🖼️ IMÁGENES DE REFERENCIA VISUAL

Ubicadas en `/img/`. Muestran el patrón en múltiples timeframes con marcas visuales del trader:

| Archivo | Timeframe | Contenido |
|---------|-----------|-----------|
| `1D- 2026-03-30 190642.png` | 1 Día | Vista general del patrón en diario |
| `1W - btc - 2026-03-30 191625.png` | 1 Semana | Ondas en semanal |
| `1M - btc - 2026-03-30 191807.png` | 1 Mes | Ciclos en mensual |
| `4H - btc - 2026-03-30 191211.png` | 4 Horas | Patrón en 4H |
| `4h -btc- 2026-03-30 191352 - A.png` | 4 Horas | Detalle / anotación A |

---

## 🗺️ HOJA DE RUTA DEL PROYECTO (COMPLETADA ✅)

### FASE 1 — Descripción del fenómeno (COMPLETADA)
**Meta:** Formalizar en números lo que se ve con los ojos. No construir nada, solo medir.

- [x] **1.1** Parser correcto para el formato CSV propio → `parse_csv.py` ✅
- [x] **1.2** Análisis exploratorio visual (gráficas de las variables ya calculadas) → `explore.py` ✅
- [x] **1.3** Caracterizar las oscilaciones de `dist_price_10`, `dist_price_55`, `dist_price_200` → `explore.py` + `scale_analysis.py` ✅
  - ¿Cuál es la amplitud típica de cada oscilación? ✅ (percentiles, rangos)
  - ¿Cuánto dura cada ciclo en velas? ✅ (FFT, Hilbert)
  - ¿Hay diferencia entre la profundidad del apoyo en EMA10 vs EMA55 vs EMA200? ✅ (`apoyo_stats.py`)
- [x] **1.4** Medir la "profundidad mínima de apoyo": el valor mínimo de `dist_price_X` antes de que el precio revierta hacia arriba → `apoyo_stats.py` ✅
- [x] **1.5** Calcular el **Ratio Armónico** (`dist_10_55 / dist_55_200`) y ver cómo evoluciona → `correlation_analysis.py` + `scale_analysis.py` ✅

### FASE 2 — Análisis matemático de las oscilaciones (COMPLETADA)
**Meta:** Encontrar si hay estructura matemática detrás del patrón visual.

- [x] **2.1** Análisis de Fourier (FFT) sobre `dist_price_10` y `dist_price_55` → ¿hay frecuencias dominantes? → `fft_analysis.py` ✅
- [x] **2.2** Exponente de Hurst → ¿la serie tiene memoria? (H > 0.5 = tendencia persistente, confirmaría el patrón) → `hurst.py` ✅
- [x] **2.3** Análisis de la relación entre `dist_10_55` y `dist_55_200` → ¿hay sincronía o desfase? → `correlation_analysis.py` ✅
- [x] **2.4** Distribución estadística de las profundidades de apoyo → ¿hay niveles que se repiten? → `apoyo_stats.py` + `explore.py` ✅
- [x] **2.5** Comparar comportamiento en los 3 timeframes (1D, 4H, 1H) → `timeframe_comparison.py` ✅

### FASE 3 — Parametrización (COMPLETADA)
**Meta:** Traducir los hallazgos en parámetros concretos y medibles.

- [x] **3.1** Definir umbral(es) de "zona de apoyo" basado en percentiles históricos → `explore.py` (p5/p95) + `apoyo_stats.py` (profundidad mediana) ✅
- [x] **3.2** Definir condiciones de "apoyo válido" (distancia + pendiente de EMA + dirección previa) → `apoyo_stats.py` (detecta mínimos locales) ✅
- [x] **3.3** Medir la tasa de éxito histórica del rebote desde cada zona → `apoyo_stats.py` (tasa éxito) ✅

### FASE 4 — Formalización / Indicador (FUTURO)
**Meta:** Solo si las fases anteriores muestran estructura real y medible. **No implementado en este proyecto**, corresponde a desarrollo posterior.

- [ ] **4.1** Construir el indicador en Pine Script con los parámetros de la Fase 3
- [ ] **4.2** Backtesting

---

### 🔮 Extensiones Matemáticas Futuras (Opcionales)
Además de las fases principales, se identificaron dos análisis matemáticos avanzados que pueden añadirse posteriormente:

| Análisis | Qué encontraría | Script | Estado |
|----------|----------------|--------|--------|
| **Cadenas de Markov** | Probabilidad condicional de transiciones entre estados (apoyo EMA10 → EMA55 → EMA200) | – | ⬜ Futura extensión |
| **Dimensión fractal** | Autosimilaridad del patrón en diferentes escalas (box‑counting, dimensión de correlación) | – | ⬜ Futura extensión |

> **Nota:** El pipeline actual genera **11 scripts funcionales** que responden todas las preguntas planteadas inicialmente. Las extensiones anteriores ampliarían el análisis a transiciones y autosimilaridad, pero no son necesarias para la descripción básica del fenómeno.

---

## 🔬 PREGUNTAS CONCRETAS A RESPONDER EN FASE 1

Estas son las preguntas que guían el análisis exploratorio inicial:

1. **¿Cuál es el rango típico (min/max/percentiles) de `dist_price_10` en tendencia alcista?**  
   → Esto define "qué tan lejos llega la corrección hacia la EMA10"

2. **¿Cuál es el rango típico de `dist_price_55`?**  
   → Idem para correcciones hacia EMA55

3. **¿Cuál es el rango típico de `dist_price_200`?**  
   → Idem para correcciones hacia EMA200

4. **¿Hay una relación de escala entre los tres rangos?**  
   → Si el apoyo en EMA10 es ~2%, ¿el de EMA55 es ~6% y el de EMA200 ~15%? ¿Hay un múltiplo?

5. **¿Las oscilaciones de `dist_price_10` tienen una duración típica en velas?**  
   → Esto daría la "frecuencia" del patrón

6. **¿El Ratio Armónico (`dist_10_55 / dist_55_200`) es estable o fluctúa mucho?**  
   → Si es estable, es una firma matemática del patrón

---

## 🚫 QUÉ NO HACER (límites acordados)

- ❌ No clasificar por régimen de mercado (bull/bear) — el patrón aplica en cualquier régimen
- ❌ No definir "apoyo" como cruce exacto de precio con EMA — es una región, no un punto
- ❌ No construir el indicador hasta tener los parámetros medidos en Fase 3
- ❌ No usar el código de limpieza genérico de DeepSeek — no funciona con el formato real del CSV

---

## 🛠️ STACK TECNOLÓGICO

- **Pine Script v6** → generación de datos (ya implementado)
- **Python** → análisis de datos (pandas, numpy, scipy, matplotlib)
- **Jupyter Notebook** → exploración visual e iterativa (recomendado)

---

## 📝 NOTAS Y DECISIONES TOMADAS

| Fecha | Decisión | Razón |
|-------|----------|-------|
| 2026-03-30 | Separar miles con `.` en Pine para evitar conflicto con CSV | TradingView usa `,` como sep. de miles, choca con formato tabla |
| 2026-03-30 | Exportar 12 variables vía `log.info` en Pine Script | Permite análisis completo sin depender de la UI de TradingView |
| 2026-03-30 | No segmentar por régimen de mercado | El patrón es universal según el trader, validar primero visualmente |
| 2026-03-30 | Empezar por descripción antes de modelos matemáticos | Evitar sobreingeniería antes de entender el fenómeno |
| 2026-03-30 | Reescribir Pine Script: un solo `log.info` por vela, formato CSV limpio | Eliminar el log duplicado de `barstate.islast` y el `;` inicial |
| 2026-03-30 | Añadir `ratio_armonico` al export del Pine Script | Era calculado en tabla visual pero no en log; ahora sí |
| 2026-03-30 | Añadir header CSV en `barstate.isfirst` | Los nuevos exports se abren directamente en pandas sin parser |

---

## 💡 HIPÓTESIS DE TRABAJO

> **H1:** Las variables `dist_price_10`, `dist_price_55` y `dist_price_200` oscilan de forma cuasi-periódica alrededor de cero, con amplitudes que guardan una relación de escala aproximadamente proporcional (armónica).

> **H2:** La profundidad mínima del apoyo (valor más negativo de `dist_price_X` antes de un rebote) no es aleatoria, sino que cae dentro de rangos estadísticamente predecibles.

> **H3:** El Ratio Armónico (`dist_10_55 / dist_55_200`) es relativamente estable en el tiempo, lo que indicaría que la estructura interna de las tres EMAs mantiene una proporción consistente independientemente del precio absoluto.

---

*Este documento es la referencia viva del proyecto. Actualizar con cada hallazgo relevante.*
