# 📚 Referencias Teóricas — Métodos Matemáticos

Esta guía proporciona los fundamentos teóricos de los métodos matemáticos utilizados en el proyecto, con enlaces a recursos externos para profundizar. Es **agnóstica** (no asume conocimiento previo) y está diseñada para ayudarte a entender qué significan los números y gráficas generadas.

> **¿Cómo usar esta guía?**
> 1. Si ves un término que no comprendes (ej. "FFT", "Hurst", "correlación cruzada"), búscalo en esta tabla de contenidos.
> 2. Lee la explicación breve y, si quieres más detalle, sigue los enlaces a Wikipedia u otros recursos.
> 3. Relaciona la teoría con los resultados concretos de tu análisis (archivos en `results/`).

---

## 📊 Tabla de Contenidos Rápido

| Método | Qué responde | Dónde aparece en los resultados |
|--------|--------------|--------------------------------|
| [Transformada de Fourier (FFT)](#-transformada-de-fourier-fft) | *"¿Hay ciclos repetitivos en las oscilaciones?"* | `fft_{TF}_espectro.png`, `fft_{TF}_ciclos.txt` |
| [Exponente de Hurst](#-exponente-de-hurst) | *"¿La serie tiene memoria (persistencia) o es aleatoria?"* | `hurst_{TF}_rs.png`, `hurst_{TF}_valores.txt` |
| [Transformada de Hilbert](#-transformada-de-hilbert) | *"¿Cómo cambian la amplitud y la velocidad del ciclo en el tiempo?"* | `hilbert_{TF}_envolvente.png`, `hilbert_{TF}_frecuencia.png`, `hilbert_{TF}_resumen.txt` |
| [Correlación y Regresión Lineal](#-correlación-y-regresión-lineal) | *"¿Hay relación lineal entre dos variables? ¿Cuál es su desfase óptimo?"* | `correlation_{TF}_ccf.png`, `correlation_{TF}_scatter.png`, `correlation_{TF}_rolling.png`, `correlation_{TF}_stats.txt` |
| [Análisis de Escalas y Proporciones](#-análisis-de-escalas-y-proporciones) | *"¿Las correcciones en diferentes EMAs guardan relaciones de tamaño constantes (ej. ×2, ×3)?"* | `scale_{TF}_ratios.png`, `scale_{TF}_evolution.png`, `scale_{TF}_table.txt`, `scale_{TF}_validation.txt` |
| [Análisis de Fibonacci](#-análisis-de-fibonacci) | *"¿Los tiempos entre apoyos y las amplitudes de retroceso siguen proporciones áureas (0.618, 1.618)?"* | `fibonacci_{TF}_tiempos.png`, `fibonacci_{TF}_amplitudes.png`, `fibonacci_{TF}_stats.txt` |
| [Conceptos Estadísticos Básicos](#-conceptos-estadísticos-básicos) | Percentiles, valor p, mediana, etc. | Presentes en todos los reportes de texto |

---

## 〰️ Transformada de Fourier (FFT)

### ¿Qué es?
La **Transformada Rápida de Fourier (FFT)** es un algoritmo que descompone una señal temporal (como la serie de `dist_p10`) en sus frecuencias componentes. Identifica si hay ciclos (patrones repetitivos) y cuál es su "fuerza" (energía).

### Conceptos clave
- **Frecuencia**: cuántas veces se repite un ciclo por unidad de tiempo (en velas⁻¹).
- **Período**: duración de un ciclo completo (en velas). Período = 1 / frecuencia.
- **Espectro de potencia**: gráfica que muestra la "energía" de cada frecuencia.
- **Energía relativa (%)**: porcentaje de la variación total de la señal explicada por ese ciclo.

### Interpretación en trading
- Un ciclo con **>10% de energía** es dominante: la oscilación sigue ese ritmo con fuerza.
- Un ciclo con **<5% de energía** es débil; podría ser ruido estadístico.
- Si el primer ciclo tiene período igual al tamaño total del dataset, representa la **tendencia de fondo** (no un ciclo real).

### Recursos para profundizar
- [Transformada de Fourier (Wikipedia)](https://es.wikipedia.org/wiki/Transformada_de_Fourier)
- [Análisis espectral (Wikipedia)](https://es.wikipedia.org/wiki/An%C3%A1lisis_espectral)
- [Understanding the FFT](https://betterexplained.com/articles/an-interactive-guide-to-the-fourier-transform/) (inglés, muy visual)

---

## 🧠 Exponente de Hurst

### ¿Qué es?
El **exponente de Hurst (H)** mide la "memoria a largo plazo" de una serie temporal. Indica si los movimientos pasados influyen en los futuros.

### Escala de H
| Valor de H | Tipo de serie | Significado en trading |
|------------|---------------|------------------------|
| **0.5** | Aleatoria (ruido blanco) | Sin memoria; el próximo movimiento es impredecible |
| **0.5 < H < 1** | Persistente (memoria positiva) | Si la serie sube, tenderá a seguir subiendo; si baja, a seguir bajando |
| **0 < H < 0.5** | Anti-persistente (memoria negativa) | Si la serie sube, tenderá a bajar después (reversión a la media) |

### Interpretación en trading
- **H > 0.65**: fuerte persistencia → las correcciones son procesos lentos con inercia.
- **H ≈ 0.5**: comportamiento aleatorio → las oscilaciones no tienen memoria.
- **H < 0.45**: fuerte reversión a la media → los movimientos se corrigen rápidamente.

### Recursos para profundizar
- [Exponente de Hurst (Wikipedia)](https://es.wikipedia.org/wiki/Exponente_de_Hurst)
- [Hurst exponent in finance](https://en.wikipedia.org/wiki/Hurst_exponent#Applications) (inglés)
- [Understanding Market Memory with Hurst](https://www.quantstart.com/articles/Hurst-Exponent-and-Market-Memory/) (inglés)

---

## 🌊 Transformada de Hilbert

### ¿Qué es?
La **Transformada de Hilbert** extrae la **amplitud instantánea** (envolvente) y la **frecuencia instantánea** de una señal cuasi-periódica. A diferencia de la FFT (que asume ciclos constantes), Hilbert muestra cómo cambian el ciclo en el tiempo.

### Conceptos clave
- **Señal analítica**: representación compleja de la señal original.
- **Amplitud instantánea**: magnitud de la oscilación en cada momento (la "fuerza").
- **Frecuencia instantánea**: velocidad del ciclo (cuántas velas dura el ciclo actual).
- **Fase instantánea**: posición dentro del ciclo (pico, valle, subida, bajada).

### Interpretación en trading
- **Amplitud creciente**: el mercado se vuelve más volátil; las oscilaciones son mayores.
- **Amplitud decreciente**: el mercado se comprime; posible ruptura próxima.
- **Período instantáneo corto (< mediana)**: el ciclo se acelera; el mercado está "nervioso".
- **Período instantáneo largo (> mediana)**: el ciclo se alarga; el mercado está "calmado".

### Recursos para profundizar
- [Transformada de Hilbert (Wikipedia)](https://es.wikipedia.org/wiki/Transformada_de_Hilbert)
- [Instantaneous amplitude and frequency](https://en.wikipedia.org/wiki/Instantaneous_phase_and_frequency) (inglés)
- [Hilbert–Huang transform](https://en.wikipedia.org/wiki/Hilbert%E2%80%93Huang_transform) (inglés, más avanzado)

---

## 🔗 Correlación y Regresión Lineal

### ¿Qué es?
- **Correlación de Pearson (r)**: mide la relación lineal entre dos variables. Valores entre -1 y 1.
- **Correlación cruzada (CCF)**: correlación con desfase (lag); identifica cuál variable "lidera" a la otra.
- **Regresión lineal**: ajusta una línea recta que mejor describe la relación.

### Escala de correlación
| Valor de r | Fuerza de relación | Interpretación |
|------------|-------------------|----------------|
| **±0.7 a ±1** | Muy fuerte | Las dos variables se mueven casi juntas (o en dirección opuesta si es negativo) |
| **±0.5 a ±0.7** | Fuerte | Relación clara pero con ruido |
| **±0.3 a ±0.5** | Moderada | Relación débil pero detectable |
| **±0.1 a ±0.3** | Débil | Relación casi imperceptible |
| **0** | Nula | No hay relación lineal |

### Conceptos clave
- **Valor p (p-value)**: probabilidad de que la correlación observada sea por azar. **p < 0.05** se considera estadísticamente significativo.
- **Lag óptimo**: desfase (en velas) que maximiza la correlación cruzada.
- **Coeficientes de regresión**: pendiente (β₁) e intercepto (β₀) de la línea ajustada.

### Interpretación en trading
- **r alto positivo**: `dist_10_55` y `dist_55_200` se mueven juntas → las EMAs se expanden/contraen sincrónicamente.
- **r negativo**: cuando una distancia crece, la otra decrece → estructura mixta.
- **Lag negativo**: `dist_10_55` lidera a `dist_55_200` por N velas.
- **Lag positivo**: `dist_55_200` lidera a `dist_10_55`.

### Recursos para profundizar
- [Coeficiente de correlación de Pearson (Wikipedia)](https://es.wikipedia.org/wiki/Coeficiente_de_correlaci%C3%B3n_de_Pearson)
- [Correlación cruzada (Wikipedia)](https://es.wikipedia.org/wiki/Correlaci%C3%B3n_cruzada)
- [Regresión lineal (Wikipedia)](https://es.wikipedia.org/wiki/Regresi%C3%B3n_lineal)
- [Understanding p-values](https://es.wikipedia.org/wiki/Valor_p) (español)

---

## 📐 Análisis de Escalas y Proporciones

### ¿Qué es?
Examina si las magnitudes de corrección en diferentes niveles (EMA10, EMA55, EMA200) guardan **relaciones de escala constantes**. Por ejemplo: ¿es `dist_p55_range ≈ 2 × dist_p10_range`?

### Métodos empleados
- **Ratios absolutos**: `|mediana(dist_p55)| / |mediana(dist_p10)|`
- **Ratios de rangos**: `(p75-p25)_dist_p55 / (p75-p25)_dist_p10`
- **Comparación con escalas teóricas**: 2, 3, 6, φ (1.618), √2 (1.414)

### Hipótesis comunes
1. **Escala ×2**: la corrección hacia EMA55 es el doble de amplia que hacia EMA10.
2. **Escala ×3**: la corrección hacia EMA200 es el triple que hacia EMA55.
3. **Escala ×6**: la corrección hacia EMA200 es seis veces mayor que hacia EMA10.
4. **Proporción áurea (φ)**: relación natural en sistemas armónicos.

### Interpretación en trading
- **Ratio cercano a 2**: confirma que las correcciones escalan linealmente entre EMA10 y EMA55.
- **Ratio estable en el tiempo**: la relación es robusta y predecible.
- **Ratio variable**: la relación cambia con el régimen de mercado (ej. alta vs baja volatilidad).

### Recursos para profundizar
- [Escala (matemáticas)](https://es.wikipedia.org/wiki/Escala_(matem%C3%A1ticas))
- [Proporción áurea (Wikipedia)](https://es.wikipedia.org/wiki/N%C3%BAmero_%C3%A1ureo)
- [Fractales y escalas en finanzas](https://en.wikipedia.org/wiki/Fractal_market_hypothesis) (inglés)

---

## 📏 Análisis de Fibonacci

### ¿Qué es?
Busca si los **tiempos entre apoyos** y las **amplitudes de retroceso** se aproximan a los niveles de Fibonacci: **0.236, 0.382, 0.500, 0.618, 0.786, 1.000, 1.618**.

### Conceptos clave
- **Ratios de tiempo**: `(tiempo entre apoyo_EMA10 y apoyo_EMA55) / (tiempo entre apoyo_EMA55 y apoyo_EMA200)`
- **Ratios de amplitud**: `(amplitud del valle) / (amplitud del pico previo)` (cuánto retrocede una corrección)
- **Distancia a nivel Fib**: diferencia absoluta entre el ratio observado y el nivel Fibonacci más cercano.

### Interpretación en trading
- **Distancia < 0.05**: el ratio está "notablemente cerca" del nivel Fibonacci.
- **Mediana cerca de 0.618 o 0.786**: el patrón temporal sigue la proporción áurea.
- **Histograma con pico en un nivel Fib**: muchos eventos ocurren en esa proporción.

### Recursos para profundizar
- [Sucesión de Fibonacci (Wikipedia)](https://es.wikipedia.org/wiki/Sucesi%C3%B3n_de_Fibonacci)
- [Retroceso de Fibonacci (Wikipedia)](https://es.wikipedia.org/wiki/Retroceso_de_Fibonacci)
- [Fibonacci en análisis técnico](https://en.wikipedia.org/wiki/Fibonacci_retracement) (inglés)

---

## 📈 Conceptos Estadísticos Básicos

### Percentiles (p5, p25, p75, p95)
- **p5**: valor por debajo del cual está el 5% de los datos (extremo inferior).
- **p25 (primer cuartil)**: valor por debajo del cual está el 25% de los datos.
- **p75 (tercer cuartil)**: valor por debajo del cual está el 75% de los datos.
- **p95**: valor por debajo del cual está el 95% de los datos (extremo superior).
- **Rango intercuartil (IQR)**: p75 - p25 (dispersión de la mitad central de los datos).

### Mediana vs Media
- **Mediana**: valor que divide los datos en dos mitades iguales. **Robusta a valores atípicos**.
- **Media (promedio)**: suma de todos los valores dividida entre el número de datos. **Sensible a valores extremos**.

### Desviación estándar (std)
Mide cuánto se dispersan los datos alrededor de la media. Valores altos indican alta volatilidad.

### Valor p (p-value)
Probabilidad de obtener un resultado igual o más extremo que el observado, asumiendo que la hipótesis nula (ej. "no hay correlación") es cierta.
- **p < 0.05**: resultado estadísticamente significativo (solo 5% de probabilidad de ser casual).
- **p > 0.05**: no se puede rechazar la hipótesis nula; el resultado podría ser aleatorio.

### Recursos para profundizar
- [Percentil (Wikipedia)](https://es.wikipedia.org/wiki/Percentil)
- [Mediana (Wikipedia)](https://es.wikipedia.org/wiki/Mediana_(estad%C3%ADstica))
- [Desviación estándar (Wikipedia)](https://es.wikipedia.org/wiki/Desviaci%C3%B3n_t%C3%ADpica)
- [Valor p (Wikipedia)](https://es.wikipedia.org/wiki/Valor_p)

---

## 🧭 Cómo Combinar Todo Esto

Los métodos no son independientes; juntos responden preguntas complementarias:

> **Ejemplo:** Para entender una corrección hacia EMA10:
> 1. **Explore** → ¿Dónde vive normalmente `dist_p10`? (percentiles)
> 2. **Apoyos** → ¿Cuánto se hunde típicamente? (profundidad mediana)
> 3. **FFT** → ¿Cada cuánto ocurre? (ciclo de ~39 velas)
> 4. **Hurst** → ¿Tiene memoria? (H > 0.5 → persistente)
> 5. **Hilbert** → ¿La amplitud está creciendo o decreciendo?
> 6. **Fibonacci** → ¿El retroceso se acerca a 0.618?
> 7. **Correlación** → ¿Se mueve junto con `dist_p55`?
> 8. **Escala** → ¿Es la mitad de `dist_p55_range`?

**Conclusión agnóstica:** No hay "señal de compra/venta". Solo descripciones matemáticas de lo ocurrido históricamente. Usa estos resultados para:
- Diseñar reglas cuantitativas (umbrales, filtros).
- Validar hipótesis visuales.
- Construir indicadores con parámetros basados en datos reales.

---

## 📖 Recursos Adicionales (Libros, Cursos, Herramientas)

### Libros recomendados
- **"An Introduction to Wavelets and Other Filtering Methods in Finance and Economics"** (Ramsey) – Para FFT y Hilbert.
- **"The Hurst Exponent: Predictability of Time Series"** (Peters) – Exhaustivo sobre memoria de mercado.
- **"Fibonacci Applications and Strategies for Traders"** (Fischer) – Aplicación práctica de Fibonacci.
- **"Statistical Analysis of Financial Data in R"** (Carmona) – Estadística aplicada a finanzas.

### Cursos en línea
- [Coursera: "Practical Time Series Analysis"](https://www.coursera.org/learn/practical-time-series-analysis)
- [edX: "Introduction to Computational Finance and Financial Econometrics"](https://www.edx.org/learn/finance/university-of-washington-introduction-to-computational-finance-and-financial-econometrics)
- [Khan Academy: Estadística y probabilidad](https://es.khanacademy.org/math/statistics-probability)

### Herramientas de software
- **Python**: librerías `numpy`, `scipy`, `statsmodels`, `pandas`.
- **R**: paquetes `forecast`, `tseries`, `fractal`.
- **MATLAB**: toolbox de procesamiento de señales.

### Comunidades y foros
- [Quant Stack Exchange](https://quant.stackexchange.com/) – Preguntas técnicas sobre finanzas cuantitativas.
- [Cross Validated (Stats Stack Exchange)](https://stats.stackexchange.com/) – Estadística y análisis de datos.
- [Reddit: r/algotrading](https://www.reddit.com/r/algotrading/) – Trading algorítmico (discusiones prácticas).

### 🔮 Métodos mencionados como extensiones futuras
En la documentación del proyecto se mencionan dos métodos matemáticos adicionales que podrían implementarse en extensiones futuras:

| Método | Qué mide | Recursos |
|--------|----------|----------|
| **Cadenas de Markov** | Probabilidad condicional de transiciones entre estados (ej. apoyo EMA10 → apoyo EMA55) | [Cadena de Markov (Wikipedia)](https://es.wikipedia.org/wiki/Cadena_de_Markov) |
| **Dimensión fractal** | Autosimilaridad y complejidad del patrón en diferentes escalas | [Dimensión fractal (Wikipedia)](https://es.wikipedia.org/wiki/Dimensi%C3%B3n_fractal) |

---

## 🔄 Actualización de esta guía

Esta guía se actualizará periódicamente con nuevos métodos y recursos. Si encuentras un enlace roto o quieres sugerir una referencia, edita el archivo `doc/TEORIA_REFERENCIAS.md` directamente o abre un issue en el repositorio.

> **Recordatorio final:** La matemática no predice el futuro; describe el pasado. Usa estos análisis para **entender**, no para adivinar.

---

*Volver al [índice de documentación](README.md)*