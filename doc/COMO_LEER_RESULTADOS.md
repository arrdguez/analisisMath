# 📖 Cómo leer cada resultado — Guía línea por línea

> **Nota importante antes de empezar:**
> Este documento usa los números reales de los archivos generados como ejemplos.
> Cuando un número implica dirección de mercado (ej. precio sobre una media),
> se escribe así: *"ejemplo de lo que significaría si el mercado estuviera en esa
> condición"* — porque los datos históricos mezclan todos los contextos posibles
> y ningún número solo dice "compra" o "vende".

---

## 🗂️ Los 3 tipos de análisis y qué pregunta responde cada uno

| Análisis | Archivos | Pregunta que responde |
|----------|----------|----------------------|
| **Explore** | `explore_*` | *"¿dónde vive el precio normalmente respecto a la EMA?"* |
| **FFT** | `fft_*` | *"¿cada cuánto tiempo ocurre ese hundimiento?"* |
| **Apoyos** | `apoyo_*` | *"¿cuánto se hunde específicamente cuando toca o se acerca a la media?"* |

Ninguno predice el futuro. Los tres describen lo que **ocurrió históricamente**.

---

---

# 📊 PARTE 1 — EXPLORE (Análisis Exploratorio)

## Qué es

"Explorar" significa simplemente: *mirar los datos para entender cómo se comportan*.
No hay ninguna matemática compleja aquí. Son estadísticas básicas y gráficas.

---

## Archivo: `explore_1D_stats.txt` — lectura línea por línea

Este es el archivo real generado. Vamos sección por sección:

```
ESTADÍSTICAS DESCRIPTIVAS — 1D
Filas: 2906  Rango: 2018-04-18 → 2026-03-31
```
→ Se analizaron **2906 días** de datos (los que tienen EMA200 calculada).
→ El rango cubre desde abril 2018 hasta marzo 2026 — casi 8 años completos.

---

### Sección: Distancias precio → EMA (%)

Estas variables miden **qué tan lejos está el precio de cada media**, en porcentaje.
- Valor **positivo** = precio está POR ENCIMA de la media
  *(ejemplo: si ves +5% en dist_p10, el precio está 5% sobre la EMA10 en ese momento)*
- Valor **negativo** = precio está POR DEBAJO de la media
  *(ejemplo: -8% en dist_p55 significaría que el precio está 8% bajo la EMA55)*

```
  dist_p10:
    media   = +0.312%
```
→ En promedio, a lo largo de los 8 años, el precio estuvo apenas **0.3% por encima
  de la EMA10**. Casi cero. Significa que la EMA10 "persigue" al precio muy de cerca —
  lo cual tiene sentido, es la media más rápida.

```
    std     = 4.709
```
→ **Desviación estándar**: qué tanto se aleja el precio de ese promedio típicamente.
  Un valor de 4.7 significa que la oscilación normal (un desvío) es de ±4.7%.
  Esto es la "amplitud típica de la oscilación". A mayor std, más violenta la oscilación.

```
    p5/p95  = -6.968 / +8.114
```
→ **Percentiles 5 y 95**: en el 90% central de los días, el precio estuvo entre
  -7% y +8.1% de la EMA10. Solo el 5% más extremo de los días estuvo más lejos que eso.
  *(ejemplo: si hoy dist_p10 = -9%, estarías en el 5% de días más alejados en la historia)*

```
    p25/p75 = -2.096 / +2.641
```
→ **Zona normal**: en la mitad central de todos los días (el 50% más frecuente),
  el precio osciló entre -2.1% y +2.6% de la EMA10.
  Esta es la **"zona de convivencia normal"** con la EMA10.
  Si el precio está dentro de este rango, está haciendo lo que hace la mayoría del tiempo.

```
    mediana = +0.185
```
→ El valor más típico de todos. En el día "más normal", el precio estaba apenas
  0.18% sobre la EMA10. Prácticamente encima de ella.

```
    min/max = -38.023 / +21.329
```
→ Los valores extremos históricos. En el peor momento (ejemplo: crash), el precio
  llegó a estar **38% por debajo de la EMA10**. En el mejor momento (ejemplo: euforia),
  llegó a estar **21% por encima**. Estos son los límites de lo "posible" en 8 años.

---

### Lo mismo para dist_p55 y dist_p200 — comparación rápida:

```
  dist_p55:
    mediana = +0.611%     ← precio casi sobre la EMA55 en el día típico
    p25/p75 = -6.258 / +9.702   ← zona normal: entre -6% y +10%
    min/max = -45.185 / +67.928  ← rangos más amplios que EMA10

  dist_p200:
    mediana = +6.168%     ← precio típicamente 6% sobre EMA200
    p25/p75 = -13.037 / +21.759  ← zona normal muy amplia
    min/max = -50.423 / +148.571 ← extremos enormes
```

**Patrón clave que emerge de la comparación:**
- La EMA10 tiene **oscilaciones pequeñas** (std=4.7, rango normal ±2%)
- La EMA55 tiene **oscilaciones medianas** (std=13.3, rango normal -6/+10%)
- La EMA200 tiene **oscilaciones grandes** (std=28.8, rango normal -13/+22%)

*Esto confirma matemáticamente lo que ves visualmente: las correcciones hacia EMA200
son mucho más amplias y toman más tiempo que las correcciones hacia EMA10.*

---

### Sección: Distancias entre EMAs (%)

Estas variables miden **la separación entre las medias entre sí**, no respecto al precio.

```
  dist_10_55:
    mediana = +0.459
    p25/p75 = -4.860 / +7.837
```
→ La separación típica entre EMA10 y EMA55 es de apenas 0.46%.
  Las medias viven casi juntas la mayor parte del tiempo.
  *(ejemplo: dist_10_55 = +15% significaría que las medias están muy separadas,
  lo cual históricamente ocurre solo en el 5% de los días más extremos)*

```
  dist_55_200:
    mediana = +4.785
    p25/p75 = -8.151 / +13.227
```
→ La EMA55 típicamente vive **4.8% por encima de EMA200**. Esto refleja que en la
  muestra de 8 años, el activo pasó más tiempo en estructuras donde EMA55 > EMA200.
  *(ejemplo de lo opuesto: cuando dist_55_200 es negativa, la EMA55 está bajo la EMA200)*

---

### Sección: Ratio Armónico

```
  ratio_armonico:
    mediana = +0.306
    p25/p75 = -0.050 / +0.790
```
→ Este es el número más interesante. El valor típico es **0.31**.
  Significa: la separación entre EMA10 y EMA55 es **el 31% de** la separación entre
  EMA55 y EMA200.

  ¿Cómo leer los rangos?
  - `p25/p75 = -0.05 / +0.79`: en la mitad de los días el ratio estuvo entre
    casi-cero y 0.79. Muy asimétrico.
  - Cuando el ratio es **negativo**: las dos distancias tienen signos opuestos.
    *(ejemplo: EMA10 está sobre EMA55, pero EMA55 está bajo EMA200 — estructura mixta)*
  - Cuando el ratio es **cercano a 1**: las dos distancias son iguales en magnitud.
  - Cuando el ratio es **muy alto (>2)**: la distancia 10/55 es mucho mayor que la 55/200,
    lo cual históricamente es poco frecuente (solo p95 = 2.48).

---

### Sección: Pendientes de EMAs (%)

```
  slope10:
    mediana = +0.244%
    p25/p75 = -1.974 / +2.692
    min/max = -24.188 / +20.217
```
→ La pendiente mide **qué tan rápido está subiendo o bajando la EMA en 5 velas**.
  - Positivo = la media está subiendo
  - Negativo = la media está bajando
  - La EMA10 es la más volátil (rango -24 a +20) porque reacciona rápido al precio
  - La EMA200 es la más estable (rango -2.4 a +7.3) porque casi no cambia de dirección

---

## Archivos de imagen: `explore_1D_distancias.png` y `explore_1D_ratio.png`

### `explore_1D_distancias.png` — cómo leer la imagen

La imagen tiene **4 filas** y **2 columnas**:

**Columna izquierda (series temporales):**
- Cada fila muestra una variable (dist_p10, dist_p55, dist_p200) a lo largo del tiempo
- La **línea de puntos blanca** horizontal = cero (precio exactamente en la media)
- El **área verde** = precio por encima de la media *(ejemplo: mercado subiendo alejado de ella)*
- El **área roja** = precio por debajo de la media *(ejemplo: precio en corrección o caída)*
- La fila de abajo muestra el precio de cierre como contexto

**Columna derecha (histogramas):**
- Muestra cuántas veces ocurrió cada valor de distancia
- La **barra más alta** = el valor más frecuente (debería estar cerca de 0)
- La **línea cyan** = mediana
- Las **líneas naranja** = percentiles 5 y 95 (los extremos poco frecuentes)
- Si el histograma está **sesgado a la derecha** (cola larga hacia la derecha):
  *(ejemplo: el activo pasó más tiempo sobre esa media que bajo ella en el período)*
- Si está **sesgado a la izquierda**:
  *(ejemplo: el activo pasó más tiempo bajo esa media en el período analizado)*

### `explore_1D_ratio.png` — cómo leer la imagen

Tiene **3 paneles** apilados verticalmente:
1. `dist_10_55` — separación EMA10/EMA55
2. `dist_55_200` — separación EMA55/EMA200
3. `ratio_armonico` — la relación entre ambas (recortado a ±3 para que se pueda ver)

En el panel del ratio:
- La **línea blanca punteada** = cero
- La **línea verde punteada** = ratio = 1 (las dos distancias son iguales)
- La **línea cyan punteada** = ratio = 0.5 (la mitad)
- Cuando el ratio salta violentamente, significa que una de las dos distancias
  cambió muy rápido respecto a la otra

---

---

# 〰️ PARTE 2 — FFT (Análisis de Ciclos)

## Qué es la FFT y qué es "energía"

**FFT = Transformada Rápida de Fourier.**

La idea es simple: toma una serie de números que oscilan y te dice
*"¿hay algún ritmo que se repita regularmente?"*.

**Analogía:** imagina que grabas el sonido de una canción. La FFT te diría
cuáles notas (frecuencias) están presentes. En nuestro caso, en lugar de
notas musicales, buscamos **ciclos de N velas** que se repiten.

**¿Qué es "energía"?**
No es energía física. Es una metáfora matemática.
Si un ciclo tiene **20% de la energía**, significa que ese ciclo explica
el 20% de toda la variación total de la señal. Es su "peso" o "importancia".
- 20%+ de energía → ese ciclo es muy dominante, la señal lo sigue con fuerza
- 5-10% → ciclo presente pero no dominante
- <5% → ciclo débil, puede ser ruido estadístico

---

## Archivo: `fft_1D_ciclos.txt` — lectura línea por línea

```
ANÁLISIS FFT — CICLOS DOMINANTES  [1D]
Filas: 2906  Rango: 2018-04-18 → 2026-03-31
```
→ La FFT se corrió sobre 2906 puntos diarios. A más puntos, más precisión
  para detectar ciclos largos.

---

### Variable: `dist_p10`

```
  dist_p10:
    #1  2906 velas  (5.61% de la energía)
    #2  969 velas   (2.55% de la energía)
    #3  39 velas    (2.04% de la energía)
    #4  1453 velas  (1.90% de la energía)
    #5  194 velas   (1.67% de la energía)
```

**Línea por línea:**

`#1  2906 velas  (5.61%)`
→ El ciclo más "energético" dura **2906 días** — que es exactamente el tamaño
  total del dataset. Esto es una señal de que hay una **tendencia de largo plazo**
  (el precio estuvo más tiempo sobre la EMA10 que bajo ella en estos 8 años).
  No es un ciclo real que se repite — es el drift de fondo del activo.
  ⚠️ Este primer pico en dist_p10 hay que tomarlo con cautela por eso.

`#3  39 velas    (2.04%)`
→ Hay un patrón que se repite cada **39 días** aproximadamente en la distancia
  precio/EMA10. 2% de la energía es modesto pero visible.
  *(ejemplo de interpretación: si esto fuera robusto, cada ~39 días habría un
  mínimo o máximo local en dist_p10 — un ciclo de corrección/impulso)*

`#5  194 velas   (1.67%)`
→ Ciclo de ~**194 días** (~6.5 meses). También modesto.

**Conclusión de dist_p10:** La energía está muy dispersa (ningún ciclo supera 6%).
La distancia precio/EMA10 no tiene un ritmo claro y dominante — oscila rápido
y de manera relativamente irregular.

---

### Variable: `dist_p55`

```
  dist_p55:
    #1  969 velas   (11.21% de la energía)
    #2  1453 velas  (9.37% de la energía)
    #3  363 velas   (4.99% de la energía)
    #4  291 velas   (4.76% de la energía)
    #5  726 velas   (4.71% de la energía)
```

`#1  969 velas  (11.21%)`
→ El ciclo más fuerte en dist_p55 dura **969 días** (≈2.65 años).
  Con 11% de energía, es significativo. Hay algo que se repite cada ~2.65 años
  en cómo el precio se aleja de la EMA55.

`#2  1453 velas  (9.37%)`
→ Ciclo de **1453 días** (≈4 años). Casi igual de fuerte que el anterior.

`#3  363 velas   (4.99%)`
→ Ciclo de **363 días** (≈1 año). Hay un ritmo anual en dist_p55.

**Conclusión de dist_p55:** Los ciclos son más largos y más concentrados que en
dist_p10. La distancia precio/EMA55 tiene más "memoria" — oscila más lentamente.

---

### Variable: `dist_p200`

```
  dist_p200:
    #1  969 velas   (20.64% de la energía)
    #2  1453 velas  (20.24% de la energía)
    #3  2906 velas  (14.03% de la energía)
    #4  726 velas   (6.58% de la energía)
    #5  415 velas   (5.05% de la energía)
```

`#1  969 velas  (20.64%)` y `#2  1453 velas  (20.24%)`
→ **ESTOS SON LOS HALLAZGOS MÁS FUERTES DEL ANÁLISIS FFT.**
  Dos ciclos con ~20% de energía cada uno, y juntos representan el 40% de
  toda la variación en dist_p200.
  - 969 días ≈ 2.65 años
  - 1453 días ≈ 3.98 años ≈ 4 años

  Estos dos números, convertidos a tiempo real sobre BTC, corresponden
  a ciclos conocidos del activo. **Pero el análisis los encontró solo con
  los números, sin saber qué activo era.**

**Conclusión de dist_p200:** La distancia precio/EMA200 es la más cíclica de las tres.
Tiene ritmos claros y dominantes. Es la variable más "predecible" en su oscilación.

---

### Variable: `dist_55_200`

```
  dist_55_200:
    #1  1453 velas  (24.34% de la energía)
    #2  969 velas   (23.62% de la energía)
```

→ **El par de ciclos más dominante de todo el análisis.**
  La separación entre EMA55 y EMA200 oscila con ciclos de ~4 años y ~2.65 años,
  y juntos representan casi el **50% de toda la variación**. La otra mitad
  son frecuencias más cortas y ruido.

---

## Comparación FFT entre timeframes

**En 4H:**
```
  dist_p55:
    #1  9960 velas  (31.45% de la energía)
```
→ 9960 velas × 4h = 39840 horas = **1660 días ≈ 4.5 años**
  El mismo ciclo largo aparece, pero medido en velas de 4H.

**Cómo convertir velas a tiempo real:**
```
  1D  → velas × 1 día
  4H  → velas × 4 horas  (÷6 para días)
  1H  → velas × 1 hora   (÷24 para días)
```

**Cuando el mismo ciclo aparece en múltiples timeframes convertido a la misma
duración en días:** eso es una señal de que el patrón no es artefacto del
timeframe sino algo real en los datos.

---

## ⚠️ Cómo NO leer la FFT

- ❌ "El ciclo de 39 días dice que en 39 días el precio sube" — NO. Solo dice
  que dist_p10 tiende a completar una oscilación cada ~39 días.
- ❌ Un ciclo con 2% de energía no es una señal de trading.
- ❌ Los ciclos muy largos (igual al tamaño del dataset) suelen ser la tendencia
  de fondo, no ciclos reales.
- ✅ Ciclos que aparecen con >10% de energía Y en múltiples variables
  merecen atención.

---

---

# 📍 PARTE 3 — APOYOS (apoyo_stats)

## Primero: la distinción más importante de todo el proyecto

Hay dos análisis que usan la misma materia prima (la distancia precio→EMA)
pero responden preguntas completamente distintas:

> **`explore`** → *"¿dónde vive el precio normalmente respecto a la EMA?"*
> **`apoyo_stats`** → *"¿cuánto se hunde específicamente cuando toca o se acerca a la media?"*

La diferencia es como preguntar:
- *"¿en qué parte de la ciudad vive la gente normalmente?"* (explore — todos los días)
- *"¿hasta dónde se alejan cuando salen de vacaciones?"* (apoyo_stats — solo los momentos de máxima distancia antes de volver)

`explore` usa **todos los días** del histórico.
`apoyo_stats` usa **solo los días donde la distancia llegó a un mínimo local** — el momento exacto de mayor cercanía antes de alejarse de nuevo.

---

## Qué es un "apoyo" para el script

El script busca **mínimos locales** en las series `dist_p10`, `dist_p55`, `dist_p200`.

Un mínimo local = un momento donde la distancia llegó a su punto más bajo
(precio más cercano o más bajo respecto a la media) dentro de una ventana
de ±5 velas, antes de subir de nuevo.

> No es un cruce exacto de precio con la media. Es el punto de
> **máxima cercanía o inmersión** antes de alejarse.

---

## Archivo: `apoyo_1D_stats.txt` — lectura línea por línea

```
Parámetros: ventana_min=5 velas, rebote=10 velas
```
→ Para detectar un mínimo, el algoritmo requiere que sea el punto más bajo
  dentro de ±5 días. Y mide qué pasa **10 días después** de cada mínimo.

---

### Apoyo en EMA10 (225 eventos)

```
── Apoyo en EMA10 (225 eventos) ──
```
→ En 2906 días de historia, se detectaron **225 veces** que el precio llegó
  a un mínimo local respecto a la EMA10. Eso es aproximadamente
  **1 apoyo cada 13 días** en promedio.

```
  Profundidad:
    mediana = -3.45%
```
→ En el apoyo típico, el precio estaba **3.45% por debajo de la EMA10**.
  *(ejemplo: si la EMA10 estuviera en $100,000, el precio típicamente
  llegó hasta ~$96,550 antes de rebotar)*

```
    p25/p75 = -6.27% / -1.21%
```
→ La **zona normal** de profundidad: en la mitad de los apoyos, el precio llegó
  entre -6.27% y -1.21% de la EMA10.
  - El límite de -1.21% (p75) dice: en el 25% de los apoyos más superficiales,
    el precio ni siquiera bajó 1.2% de la EMA10 — *(ejemplo: apenas rozó la media)*
  - El límite de -6.27% (p25) dice: en el 25% más profundo, el precio bajó más
    de 6.27% *(ejemplo: corrección real, no solo un amago)*

```
    p10/p90 = -9.04% / +0.19%
```
→ El 80% de los apoyos ocurrió entre -9% y +0.2%.
  El +0.19% (p90) es interesante: significa que el 10% de los "apoyos" detectados
  ocurrieron con el precio **sobre** la EMA10 — el precio bajó hacia la media
  pero nunca la tocó. Eso es exactamente el "amago" que describes.

```
    min/max = -38.02% / +8.86%
```
→ El extremo máximo: una vez el precio llegó 38% bajo la EMA10 antes de rebotar.
  *(ejemplo: eso sería en un crash severo donde la media tardó en bajar)*

```
  Rebote 10 velas después:
    tasa éxito (subió) = 75.9%
```
→ De los 225 apoyos detectados, **en el 75.9% de los casos el precio 10 días
  después estaba más alto** que en el día del apoyo.
  Ojo: esto incluye TODOS los contextos de mercado (subiendo, bajando,
  lateral). No filtra por régimen.

```
    mediana rebote = +4.91%
```
→ En la mitad de los casos, 10 días después el precio estaba al menos
  **4.91% más alto**. *(ejemplo: si el apoyo fue en $60,000, en la mitad de
  los casos 10 días después el precio superó $62,946)*

```
    p25/p75 rebote = +0.17% / +10.28%
```
→ En la mitad central de los casos, el rebote estuvo entre +0.17% y +10.28%.
  - El +0.17% (p25) dice: hay muchos casos donde el "rebote" fue casi nulo
    *(ejemplo: el precio apenas se movió después del apoyo)*
  - El +10.28% (p75) dice: en un cuarto de los casos el rebote fue mayor a 10%

---

### Comparación entre los 3 niveles de apoyo (1D):

| Nivel | Eventos | Profundidad típica | % que subió | Rebote mediano |
|-------|---------|-------------------|-------------|----------------|
| EMA10  | 225 | -3.45% | 75.9% | +4.91% |
| EMA55  | 199 | -4.03% | 82.8% | +5.49% |
| EMA200 | 187 | -1.02% | 84.9% | +6.28% |

**Lectura de esta tabla:**
- Los apoyos en EMA55 son **menos frecuentes** que en EMA10 (199 vs 225) — tiene sentido,
  son correcciones más grandes que ocurren con menos frecuencia
- La **tasa de éxito sube** al ir de EMA10 → EMA55 → EMA200 (76% → 83% → 85%)
  *(ejemplo de lo que esto significa: los apoyos más profundos, históricamente,
  tuvieron mayor probabilidad de ser seguidos por subida en 10 días)*
- La **profundidad típica en EMA200** es solo -1.02% pero los rangos son enormes
  (p25/p75 = -20% / +15%) — hay mucha varianza, los apoyos en EMA200 son muy
  heterogéneos

---

## Archivo: `apoyo_1D_detalle.png` — cómo leer la imagen

La imagen tiene **3 filas** (una por EMA) y **2 columnas**:

**Columna izquierda — Serie histórica con apoyos marcados:**
- La **línea gris oscura** es la serie de distancia (dist_p10, dist_p55 o dist_p200)
- Los **puntos de color** son cada apoyo detectado
- Las **líneas horizontales punteadas** son los percentiles (p10, p25, p75, p90)
- Puedes ver visualmente si los apoyos son más frecuentes en ciertos períodos

**Columna derecha — Histograma de profundidades:**
- El eje Y es la profundidad (el valor de la distancia en el momento del apoyo)
- El eje X es cuántas veces ocurrió esa profundidad
- La **línea cyan** = mediana de profundidad
- Si la barra más alta está cerca de 0, los apoyos típicos son superficiales
- Si hay una cola larga hacia abajo (valores muy negativos), hay algunos apoyos
  extremos poco frecuentes

---

## Archivo: `apoyo_1D_rebote.png` — cómo leer la imagen

Tiene **3 paneles** lado a lado (uno por EMA):

- El eje X es el **cambio de precio 10 días después del apoyo** (en %)
- El eje Y es cuántas veces ocurrió ese cambio
- La **línea blanca vertical** = cero (precio igual que en el apoyo)
- Todo lo que está a la **derecha del cero** = precio subió después del apoyo
- Todo a la **izquierda** = precio bajó después del apoyo
- La **línea cyan** = mediana del rebote
- En el título de cada panel está la **tasa de éxito** directamente

Si el histograma está claramente sesgado a la derecha (mayoría de barras a la
derecha del cero): *(ejemplo de lo que significaría: históricamente los apoyos
en esa EMA fueron seguidos de subida más veces que de bajada)*

---

---

# 🔄 Cómo se relacionan los 3 análisis entre sí

Cada análisis responde una pregunta diferente sobre el mismo fenómeno:

> **`explore`** → *"¿dónde vive el precio normalmente respecto a la EMA?"*
> **`apoyo_stats`** → *"¿cuánto se hunde específicamente cuando toca o se acerca a la media?"*
> **`fft`** → *"¿cada cuánto tiempo ocurre ese hundimiento?"*

Juntos forman una sola respuesta completa:

```
EXPLORE dice:    "La zona normal de dist_p10 es entre -2% y +2.6%
                  — ahí vive el precio la mayor parte del tiempo"

APOYOS dice:     "Cuando dist_p10 llega a su mínimo local (-3.45% típico),
                  el precio sube 10 días después en el 76% de los casos"

FFT dice:        "Esos mínimos ocurren con un ritmo de ~39 días"
```

Separados, cada uno solo ve una cara del fenómeno.
Juntos responden: **¿dónde está?, ¿qué tan hondo llega?, ¿cada cuánto?**

---

# 📐 PARTE 4 — HURST (Memoria de la serie)

## Qué pregunta responde

> *"¿Cuando una distancia lleva varios días alejándose de la EMA, tiende a seguir alejándose... o tiende a volver?"*

Esa es la pregunta del exponente de Hurst. Mide si la serie tiene **memoria**.

## La escala de H

| Valor de H | Nombre | Significado en nuestras variables |
|------------|--------|----------------------------------|
| H > 0.65 | Persistente fuerte | Si dist_p55 lleva días creciendo, tenderá a seguir creciendo |
| H 0.55–0.65 | Persistente moderada | Hay algo de inercia pero débil |
| H ≈ 0.50 | Aleatorio | Como lanzar una moneda — sin memoria |
| H 0.35–0.45 | Anti-persistente | Después de alejarse, tiende a volver (oscilación fuerte) |
| H < 0.35 | Anti-persistente fuerte | Revierte casi siempre |

## Archivo: `hurst_1D_valores.txt` — lectura línea por línea

```
  dist_p10:   H=0.790 → Persistente fuerte
  dist_p55:   H=0.948 → Persistente fuerte
  dist_p200:  H=1.001 → Persistente fuerte
  dist_10_55: H=0.943 → Persistente fuerte
  dist_55_200:H=0.993 → Persistente fuerte
```

**Línea por línea:**

`dist_p10: H=0.790`
→ La distancia precio/EMA10 tiene memoria fuerte. Cuando el precio se aleja
  de la EMA10, tiende a continuar alejándose antes de volver.
  *(ejemplo de lo que esto implica: las correcciones hacia EMA10 no son instantáneas
  — hay inercia, el precio se toma su tiempo antes de rebotar)*

`dist_p55: H=0.948`
→ Memoria muy fuerte. Las correcciones hacia EMA55 son procesos lentos con mucha inercia.

`dist_p200: H=1.001`
→ H≈1 es el límite superior del rango esperado — indica que esta variable
  se comporta casi como una **tendencia pura** en escalas de tiempo largas.
  La distancia precio/EMA200 tarda muchísimo en revertir.
  ⚠️ Un valor de H>1 puede indicar que la tendencia de largo plazo del activo
  contamina ligeramente el cálculo, incluso después de quitar la tendencia lineal.

**¿Por qué se aplica a las distancias y no al precio?**
El precio de BTC tiene una tendencia alcista estructural de largo plazo.
Si calculamos H del precio directamente, obtendríamos H≈1 simplemente por
esa tendencia, no por el patrón que nos interesa.
Las distancias ya están "centradas en cero" — miden la oscilación pura.

## Archivo: `hurst_{TF}_rs.png` — cómo leer la imagen

Cada panel muestra una gráfica **log-log** de R/S vs lag:
- Los **puntos** son los valores calculados
- La **línea de color** es el ajuste lineal cuya pendiente = H
- La **línea blanca punteada** es la referencia de H=0.5 (aleatorio puro)
- Si la línea de color tiene **pendiente mayor** que la blanca → H > 0.5 → memoria
- Si todas las líneas son casi paralelas y más empinadas que la referencia:
  *(ejemplo: todas las variables tienen memoria, el fenómeno no es aleatorio)*

---

---

# 〜 PARTE 5 — HILBERT (Amplitud y velocidad del ciclo)

## Qué pregunta responde

> *"¿La oscilación siempre tiene la misma 'fuerza' y velocidad? ¿O hay momentos donde se acelera, se amplifica, o se aplana?"*

La FFT asume que el ciclo es constante en el tiempo.
Hilbert va más lejos: mide si el ciclo **cambia** con el tiempo.

## Tres cosas que extrae

| Concepto | Analogía | En nuestras variables |
|----------|---------|----------------------|
| **Envolvente** | El "volumen" de la música | La amplitud de la oscilación de dist_pX en cada momento |
| **Fase** | En qué compás de la canción estás | Si la distancia está subiendo, bajando, en pico o en valle |
| **Frecuencia instantánea** | Si la música se acelera o frena | Cuántas velas dura el ciclo en cada momento específico |

## Archivo: `hilbert_1D_resumen.txt` — lectura línea por línea

```
── EMA10 (dist_p10) ──
  Amplitud media:    5.489%
  Amplitud std:      3.768%
  Período mediana:   14.4 velas
  Período p25/p75:   8.8 / 28.6 velas
  Rango intercuartil: 19.8 velas
```

`Amplitud media: 5.489%`
→ En promedio, la oscilación de dist_p10 tiene una amplitud de ±5.5%.
  *(ejemplo: el precio típicamente se aleja hasta ~5.5% de la EMA10 en cada ciclo)*
  Comparar con `explore_1D_stats.txt` donde std=4.7% — son consistentes.

`Amplitud std: 3.768%`
→ La amplitud **varía bastante** (std casi tan grande como la media).
  Hay momentos donde las oscilaciones son pequeñas (~2%) y momentos donde
  son grandes (~9%). El ciclo no siempre tiene la misma "fuerza".

`Período mediana: 14.4 velas`
→ El ciclo típico de dist_p10 dura **14 días** (en 1D).
  *(ejemplo: si hoy el precio tocó mínimo relativo a EMA10, en ~14 días
  podría estar en el próximo mínimo — pero con alta varianza)*

`Período p25/p75: 8.8 / 28.6 velas`
→ El 50% central de los ciclos duró entre 9 y 29 días.
  Rango muy amplio — el ciclo es **irregular**.

```
── EMA55 (dist_p55) ──
  Período mediana:   45.8 velas
  Período p25/p75:   24.8 / 103.7 velas
  Rango intercuartil: 79.0 velas
```
→ El ciclo de dist_p55 dura ~46 días pero con rango intercuartil de 79 días.
  Extremadamente variable. Los ciclos de largo plazo no tienen un ritmo fijo.

```
── EMA200 (dist_p200) ──
  Período mediana:   99.3 velas
  Período p25/p75:   49.2 / 240.6 velas
```
→ El ciclo de dist_p200 dura ~100 días en la mediana, pero puede ser
  desde 49 hasta 240 días. El rango es enorme — confirma que los ciclos
  de largo plazo son muy irregulares.

## Patrón clave que emerge de los 3 niveles (1D):

| EMA | Amplitud media | Período mediana |
|-----|---------------|----------------|
| EMA10  | 5.5%  | ~14 días |
| EMA55  | 16.2% | ~46 días |
| EMA200 | 34.7% | ~99 días |

> *"¿La amplitud y el período escalan proporcionalmente entre niveles?"*
> EMA10→EMA55: amplitud ×3, período ×3.2
> EMA55→EMA200: amplitud ×2.1, período ×2.2
> Hay una **proporcionalidad aproximada** — las oscilaciones de mayor escala
> no son solo más grandes, también son más lentas, en proporción similar.

## Archivos de imagen: cómo leerlos

### `hilbert_{TF}_envolvente.png`
- La **línea de color** es la señal (dist_pX sin tendencia)
- Las **líneas blancas** forman la "envoltura" — el techo y suelo de la onda
- El **área sombreada** entre las envolventes muestra cuándo las oscilaciones son grandes o pequeñas
- Cuando las envolventes se **abren** (se separan): *(ejemplo: amplitud creciendo, mercado más volátil)*
- Cuando se **cierran** (convergen hacia cero): *(ejemplo: amplitud decreciendo, mercado comprimido)*

### `hilbert_{TF}_frecuencia.png`
- La **línea de color** es el período instantáneo en velas
- La **línea cyan** es la mediana histórica
- Cuando la línea sube: el ciclo se está **alargando** (oscila más despacio)
- Cuando baja: el ciclo se **abrevia** (oscila más rápido)
- Mucha varianza en esta gráfica = el ciclo no es constante
  *(ejemplo: si la línea salta de 10 a 80 velas sin patrón, el ciclo es irregular)*

---

---

# 🌀 PARTE 6 — FIBONACCI (¿Hay proporciones áureas?)

## Qué pregunta responde

> *"¿El tiempo que tarda el mercado en ir de apoyo en EMA10 a apoyo en EMA55 guarda proporción con el tiempo de EMA55 a EMA200?"*
> *"¿Las correcciones retroceden hasta los niveles 0.382, 0.5 o 0.618 del movimiento previo?"*

Fibonacci en mercados es una **hipótesis**, no una ley. El análisis la mide
sin asumir que es verdad — deja que los datos digan si la proporción aparece
o no en el histograma.

Los niveles de referencia son: **0.236, 0.382, 0.500, 0.618, 0.786, 1.000, 1.618**

## Archivo: `fibonacci_1D_stats.txt` — lectura línea por línea

### Sección: Ratios de tiempo

```
── RATIOS DE TIEMPO (apoyo EMA10 → EMA55 → EMA200) ──
  Secuencias encontradas: 224
  Mediana del ratio:  0.7929
  Nivel Fib más cercano a la mediana: 0.786  (distancia=0.0069)
  Interpretación: si dist < 0.05 al nivel Fib, la proporción es notable
```

`Secuencias encontradas: 224`
→ Se encontraron 224 veces donde ocurrió la secuencia completa:
  apoyo en EMA10 → después apoyo en EMA55 → después apoyo en EMA200.
  Con 224 casos en 8 años de datos 1D, hay suficiente muestra para que
  la estadística sea significativa.

`Mediana del ratio: 0.7929`
→ En la secuencia típica, el tiempo entre apoyo_EMA10 y apoyo_EMA55 es
  el **79.3% del tiempo** entre apoyo_EMA55 y apoyo_EMA200.
  *(ejemplo: si tardó 10 días de EMA10 a EMA55, tardó ~12.6 días de EMA55 a EMA200)*

`Nivel Fib más cercano: 0.786  (distancia=0.0069)`
→ La mediana de 0.7929 está a solo **0.007 del nivel 0.786 de Fibonacci**.
  Una distancia < 0.05 se considera notable.
  0.007 es muy cercano — **la proporción temporal está alineada con Fibonacci**.
  ⚠️ Esto no significa que siempre ocurra así. La mediana cae cerca de 0.786,
  pero el p25/p75 va de 0.40 a 1.40 — hay mucha dispersión.

### Sección: Ratios de amplitud

```
  EMA10 (dist_p10):
    Mediana ratio:    0.5520
    Fib más cercano:  0.500  (distancia=0.0520)

  EMA55 (dist_p55):
    Mediana ratio:    0.5666
    Fib más cercano:  0.618  (distancia=0.0514)

  EMA200 (dist_p200):
    Mediana ratio:    0.7419
    Fib más cercano:  0.786  (distancia=0.0441)
```

`EMA10: mediana=0.552, Fib más cercano=0.500, distancia=0.052`
→ Las correcciones hacia EMA10 retroceden típicamente el **55.2% de la amplitud
  del impulso previo**. El nivel 0.5 de Fibonacci está a 0.052 de distancia —
  justo en el límite de "notable" (umbral = 0.05).
  *(ejemplo: si dist_p10 llegó a +8% en el pico, la corrección típica llega hasta -4.4%)*

`EMA55: mediana=0.567, Fib más cercano=0.618, distancia=0.051`
→ Las correcciones hacia EMA55 retroceden ~56.7% del impulso previo.
  El nivel 0.618 (proporción áurea) está a 0.051 — también cerca del umbral.

`EMA200: mediana=0.742, Fib más cercano=0.786, distancia=0.044`
→ Las correcciones hacia EMA200 retroceden ~74.2% del impulso previo.
  El nivel 0.786 está a 0.044 — **por debajo del umbral de 0.05**, la más notable.

## Archivos de imagen: cómo leerlos

### `fibonacci_{TF}_tiempos.png`
- Es un histograma de los ratios de tiempo entre apoyos
- El eje X es el ratio (tiempo_EMA10→55 / tiempo_EMA55→200)
- Las **líneas verticales de colores** son los niveles de Fibonacci
- Si el histograma tiene un **pico visible cerca de una línea Fibonacci**:
  *(ejemplo: si la barra más alta cae justo en 0.618, la proporción áurea aparece en los datos)*
- Si el histograma es **plano o disperso**: la proporción no es consistente

### `fibonacci_{TF}_amplitudes.png`
- Tres histogramas (uno por EMA) de los ratios amplitud_valle/amplitud_pico
- Cada barra = cuántas veces esa corrección tuvo ese ratio de retroceso
- Las líneas de colores = niveles Fibonacci de referencia
- El título de cada panel muestra la mediana y el nivel Fibonacci más cercano

---

# ❓ Análisis pendientes

| Análisis | Qué encontraría | Estado |
|----------|----------------|--------|
| **Cadenas de Markov** | Probabilidad de pasar de "apoyo EMA10" a "apoyo EMA55" | ⬜ Pendiente |
| **Dimensión fractal** | Si el patrón se auto-repite en diferentes escalas | ⬜ Pendiente |

Estos análisis no se implementan hasta que los 3 actuales estén bien interpretados.
