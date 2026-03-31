# 📊 REPORTE MAESTRO: Análisis de Magnitudes Armónicas (BTC/USD)

## 1. Contexto y Antecedentes
Este reporte contiene el análisis matemático de las relaciones entre el precio de Bitcoin y tres Medias Móviles Exponenciales (EMAs) de 10, 55 y 200 períodos.
- **Fuente:** Logs de Pine Script v6 (TradingView).
- **Variables de estudio:** Distancias porcentuales del precio a cada EMA (`dist_p10`, `dist_p55`, `dist_p200`) y distancias entre EMAs (`dist_10_55`, `dist_55_200`).
- **Objetivo:** Detectar constantes y magnitudes recurrentes para formalizar el patrón visual en un script algorítmico.

## 2. Metodologías Aplicadas
| Análisis | Qué mide | Por qué es relevante |
|----------|----------|----------------------|
| **FFT (Fourier)** | Ciclos dominantes | Identifica si las oscilaciones tienen una periodicidad fija (velas). |
| **Hurst** | Memoria (Persistencia) | H > 0.5 indica que la serie tiene memoria y tiende a seguir su tendencia. |
| **Hilbert** | Amplitud/Periodo inst. | Muestra cómo cambia la 'fuerza' y la velocidad del ciclo en el tiempo. |
| **Fibonacci** | Ratios armónicos | Busca si los retrocesos y tiempos coinciden con la proporción áurea. |
| **Apoyos** | Profundidad de rebote | Mide cuánto 'perfora' el precio la EMA antes de rebotar. |
| **Correlación** | Sincronía entre EMAs | Determina si las distancias entre EMAs se mueven juntas o con desfase. |
| **Escala** | Relaciones entre rangos | Verifica si las correcciones guardan proporciones matemáticas constantes. |
| **Comparación** | Consistencia multi-timeframe | Evalúa si los patrones se mantienen en diferentes escalas temporales. |

## 3. Resultados Numéricos Consolidados

### 🕒 Timeframe: 1D

#### > Stats
```text
ESTADÍSTICAS DESCRIPTIVAS — 1D
Filas: 2906 | Rango: 2018-04-18 00:00:00 → 2026-03-31 00:26:00


── Distancias precio → EMA (%) ──
  dist_p10:
    media    +0.312%
    std      4.709
    p5/p95   -6.968 / +8.114
    p25/p75  -2.096 / +2.641
    mediana  +0.185
    min/max  -38.023 / +21.329

  dist_p55:
    media    +1.955%
    std      13.269
    p5/p95   -17.465 / +24.895
    p25/p75  -6.258 / +9.702
    mediana  +0.611
    min/max  -45.185 / +67.928

  dist_p200:
    media    +7.396%
    std      28.816
    p5/p95   -31.908 / +62.676
    p25/p75  -13.037 / +21.759
    mediana  +6.168
    min/max  -50.423 / +148.571

── Distancias entre EMAs (%) ──
  dist_10_55:
    media    +1.412%
    std      10.214
    p5/p95   -14.497 / +18.590
    p25/p75  -4.860 / +7.837
    mediana  +0.459
    min/max  -27.734 / +42.822

  dist_55_200:
    media    +4.114%
    std      17.446
    p5/p95   -24.082 / +35.087
    p25/p75  -8.151 / +13.227
    mediana  +4.785
    min/max  -29.073 / +56.677

── Ratio Armónico ──
  ratio_armonico (valores extremos recortados a ±5):
    media    +0.272
    std      1.518
    p5/p95   -2.544 / +2.482
    p25/p75  -0.050 / +0.790
    mediana  +0.306


── Pendientes de EMAs (%) ──
  slope10:
    media    +0.485%
    std      4.587
    p5/p95   -6.479 / +8.573
    p25/p75  -1.974 / +2.692
    mediana  +0.244
    min/max  -24.188 / +20.217

  slope55:
    media    +0.398%
    std      2.430
    p5/p95   -3.130 / +4.571
    p25/p75  -1.090 / +1.863
    mediana  +0.082
    min/max  -6.935 / +12.265

  slope200:
    media    +0.387%
    std      1.458
    p5/p95   -1.564 / +3.194
    p25/p75  -0.640 / +1.058
    mediana  +0.314
    min/max  -2.390 / +7.290
```

#### > Ciclos
```text
ANÁLISIS FFT — CICLOS DOMINANTES  [1D]
Filas: 2906 | Rango: 2018-04-18 00:00:00 → 2026-03-31 00:26:00


  dist_p10:
    #1  2906 velas  (5.61% de la energía)
    #2  969 velas  (2.55% de la energía)
    #3  39 velas  (2.04% de la energía)
    #4  1453 velas  (1.90% de la energía)
    #5  194 velas  (1.67% de la energía)

  dist_p55:
    #1  969 velas  (11.21% de la energía)
    #2  1453 velas  (9.37% de la energía)
    #3  363 velas  (4.99% de la energía)
    #4  291 velas  (4.76% de la energía)
    #5  726 velas  (4.71% de la energía)

  dist_p200:
    #1  969 velas  (20.64% de la energía)
    #2  1453 velas  (20.24% de la energía)
    #3  2906 velas  (14.03% de la energía)
    #4  726 velas  (6.58% de la energía)
    #5  415 velas  (5.05% de la energía)

  dist_10_55:
    #1  969 velas  (11.74% de la energía)
    #2  1453 velas  (10.33% de la energía)
    #3  2906 velas  (9.68% de la energía)
    #4  363 velas  (5.14% de la energía)
    #5  415 velas  (5.06% de la energía)

  dist_55_200:
    #1  1453 velas  (24.34% de la energía)
    #2  969 velas  (23.62% de la energía)
    #3  2906 velas  (18.97% de la energía)
    #4  726 velas  (7.55% de la energía)
    #5  415 velas  (5.34% de la energía)
```

#### > Apoyos
```text
ESTADÍSTICAS DE APOYOS  [1D]
Filas: 2906 | Rango: 2018-04-18 00:00:00 → 2026-03-31 00:26:00
Parámetros: ventana_min5 velas, rebote10 velas


── Apoyo en EMA10 (225 eventos) ──
  Profundidad (dist precio → EMA10):
    mediana  -3.45%
    p10/p90  -9.04% / +0.19%
    p5/p95   -12.25% / +1.53%
    p25/p75  -6.27% / -1.21%
    min/max  -38.02% / +8.86%
  Rebote 10 velas después:
    tasa éxito (subió)  75.9%
    mediana rebote      +4.91%
    p25/p75 rebote      +0.17% / +10.28%

── Apoyo en EMA55 (199 eventos) ──
  Profundidad (dist precio → EMA55):
    mediana  -4.03%
    p10/p90  -19.73% / +10.80%
    p5/p95   -25.21% / +14.73%
    p25/p75  -11.47% / +3.92%
    min/max  -45.19% / +34.99%
  Rebote 10 velas después:
    tasa éxito (subió)  82.8%
    mediana rebote      +5.49%
    p25/p75 rebote      +1.17% / +11.12%

── Apoyo en EMA200 (187 eventos) ──
  Profundidad (dist precio → EMA200):
    mediana  -1.02%
    p10/p90  -32.24% / +31.15%
    p5/p95   -36.07% / +41.98%
    p25/p75  -19.99% / +14.71%
    min/max  -50.42% / +83.47%
  Rebote 10 velas después:
    tasa éxito (subió)  84.9%
    mediana rebote      +6.28%
    p25/p75 rebote      +1.86% / +10.81%
```

#### > Hurst
```text
EXPONENTE DE HURST  [1D]
Filas: 2906 | Rango: 2018-04-18 00:00:00 → 2026-03-31 00:26:00


Interpretación de H:
  H > 0.65  → Persistente fuerte   (la serie continúa su dirección)
  H 0.55-0.65 → Persistente moderada (algo de memoria)
  H 0.45-0.55 → Casi aleatoria       (sin memoria clara)
  H 0.35-0.45 → Anti-persistente     (tiende a revertir)
  H < 0.35  → Anti-persistente fuerte (revierte muy seguido)

NOTA: Se aplica a las DISTANCIAS, no al precio crudo.
      El precio crudo tiene tendencia que contaminaría el resultado.


  dist_p10:  H0.790 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_p55:  H0.948 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_p200:  H1.001 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_10_55:  H0.943 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_55_200:  H0.993 → Persistente fuerte   — la serie tiende a continuar su dirección
```

#### > Hilbert
```text
ANÁLISIS DE HILBERT  [1D]
Filas: 2906 | Rango: 2018-04-18 00:00:00 → 2026-03-31 00:26:00


Qué mide:
  Envolvente  → amplitud de la oscilación en cada momento
  Período     → cuántas velas dura el ciclo en cada momento
  (Si el período cambia mucho: el ciclo NO es constante en el tiempo)


── EMA10 (dist_p10) ──
  Amplitud media:    5.489%
  Amplitud std:      3.768%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   14.4 velas
  Período p25/p75:   8.8 / 28.6 velas
  Rango intercuartil del período: 19.8 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)

── EMA55 (dist_p55) ──
  Amplitud media:    16.219%
  Amplitud std:      9.430%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   45.8 velas
  Período p25/p75:   24.8 / 103.7 velas
  Rango intercuartil del período: 79.0 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)

── EMA200 (dist_p200) ──
  Amplitud media:    34.729%
  Amplitud std:      21.177%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   99.3 velas
  Período p25/p75:   49.2 / 240.6 velas
  Rango intercuartil del período: 191.4 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)
```

#### > Fib
```text
ANÁLISIS DE FIBONACCI  [1D]
Filas: 2906 | Rango: 2018-04-18 00:00:00 → 2026-03-31 00:26:00


Niveles Fibonacci de referencia: 0.236, 0.382, 0.500, 0.618, 0.786, 1.618

── RATIOS DE TIEMPO (apoyo EMA10 → EMA55 → EMA200) ──
  Secuencias encontradas: 224
  Mediana del ratio:  0.7929
  Media del ratio:    1.0241
  p25/p75:            0.3982 / 1.4042
  Nivel Fib más cercano a la mediana: 0.786  (distancia0.0069)
  Interpretación: si dist < 0.05 al nivel Fib, la proporción es notable

── RATIOS DE AMPLITUD (valle/pico por EMA) ──
  EMA10 (dist_p10):
    Pares pico/valle: 225
    Mediana ratio:    0.5520
    p25/p75:          0.2111 / 1.0123
    Fib más cercano:  0.5  (distancia0.0520)

  EMA55 (dist_p55):
    Pares pico/valle: 199
    Mediana ratio:    0.5666
    p25/p75:          0.3226 / 1.3538
    Fib más cercano:  0.618  (distancia0.0514)

  EMA200 (dist_p200):
    Pares pico/valle: 187
    Mediana ratio:    0.7419
    p25/p75:          0.4950 / 1.2340
    Fib más cercano:  0.786  (distancia0.0441)
```

#### > Correlación
```text
ANÁLISIS DE CORRELACIÓN  [1D]
Filas: 2906 | Rango: 2018-04-18 00:00:00 → 2026-03-31 00:26:00


── CORRELACIÓN SINCRÓNICA (lag  0) ──
  Pearson r    0.6277
  Valor p      3.3075e-318
  Interpretación:
    • Correlación FUERTE (0.5-0.7)
    • Estadísticamente SIGNIFICATIVA (p < 0.05)

── CORRELACIÓN CRUZADA (desfase óptimo) ──
  Lag óptimo   -32 velas
  Correlación en lag óptimo  0.7864
  Interpretación:
    • dist_55_200 PRECEDE a dist_10_55 por 32 velas
    • Mejor correlación con desfase que sincrónica

── RELACIÓN LINEAL (regresión) ──
  Pendiente    0.3675
  Intercepto   -0.0996
  Ecuación: dist_10_55  0.3675 × dist_55_200 + -0.0996

Interpretación de la pendiente:
    • dist_10_55 responde ATENUANDO los movimientos de dist_55_200 (pendiente < 1)

── RESUMEN PARA INDICADOR ──
  1. Correlación sincrónica: SÍ
  2. Desfase óptimo: -32 velas
  3. Relación: dist_10_55 ≈ 0.37 × dist_55_200
  4. Fuerza relación: fuerte
```

#### > Escala
```text
TABLA DE RATIOS DE ESCALA  [1D]


── ESTADÍSTICAS DE DISTANCIAS ──
Variable       | Mediana(abs) |   p25   |   p75   |  Rango  |   Media  |
-------------- | ------------ | ------- | ------- | ------- | -------- |
dist_p10      |        2.34% |   -2.10% |    2.64% |    4.74% |     0.31% |
dist_p55      |        7.73% |   -6.26% |    9.70% |   15.96% |     1.96% |
dist_p200     |       17.07% |  -13.04% |   21.76% |   34.80% |     7.40% |

── RATIOS EMPÍRICOS ──
Usando medianas de valores absolutos:
Ratio      | Valor | Escala más cercana | Distancia |
---------- | ----- | ----------------- | --------- |
55/10     |  3.30 | x3                | 0.297     |
200/55    |  2.21 | x2                | 0.209     |
200/10    |  7.28 | x6                | 1.284     |

Usando rangos intercuartiles (p75-p25):
Ratio      | Valor | Escala más cercana | Distancia |
---------- | ----- | ----------------- | --------- |
55/10     |  3.37 | x3                | 0.369     |
200/55    |  2.18 | x2                | 0.180     |
200/10    |  7.35 | x6                | 1.345     |

── INTERPRETACIÓN ──
Distancias pequeñas (<0.05) a escalas teóricas sugieren relación armónica.
Ratios consistentes entre métodos (abs/range) indican robustez.
```

### 🕒 Timeframe: 4H

#### > Stats
```text
ESTADÍSTICAS DESCRIPTIVAS — 4H
Filas: 9960 | Rango: 2021-09-13 08:00:00 → 2026-03-31 00:25:00


── Distancias precio → EMA (%) ──
  dist_p10:
    media    +0.015%
    std      1.580
    p5/p95   -2.531 / +2.460
    p25/p75  -0.686 / +0.763
    mediana  +0.029
    min/max  -11.822 / +9.635

  dist_p55:
    media    +0.098%
    std      4.097
    p5/p95   -6.204 / +6.955
    p25/p75  -2.116 / +2.187
    mediana  -0.013
    min/max  -22.709 / +17.561

  dist_p200:
    media    +0.404%
    std      8.178
    p5/p95   -12.550 / +14.592
    p25/p75  -4.231 / +5.417
    mediana  -0.194
    min/max  -35.823 / +29.100

── Distancias entre EMAs (%) ──
  dist_10_55:
    media    +0.062%
    std      3.162
    p5/p95   -4.788 / +5.429
    p25/p75  -1.680 / +1.678
    mediana  +0.018
    min/max  -16.332 / +10.672

  dist_55_200:
    media    +0.197%
    std      5.336
    p5/p95   -8.383 / +9.355
    p25/p75  -2.884 / +3.449
    mediana  -0.139
    min/max  -18.645 / +15.193

── Ratio Armónico ──
  ratio_armonico (valores extremos recortados a ±5):
    media    +0.321
    std      1.640
    p5/p95   -2.534 / +3.148
    p25/p75  -0.074 / +0.837
    mediana  +0.302


── Pendientes de EMAs (%) ──
  slope10:
    media    +0.031%
    std      1.517
    p5/p95   -2.368 / +2.394
    p25/p75  -0.681 / +0.761
    mediana  +0.034
    min/max  -9.739 / +8.334

  slope55:
    media    +0.021%
    std      0.738
    p5/p95   -1.117 / +1.262
    p25/p75  -0.385 / +0.394
    mediana  -0.002
    min/max  -3.662 / +2.917

  slope200:
    media    +0.021%
    std      0.408
    p5/p95   -0.618 / +0.734
    p25/p75  -0.209 / +0.273
    mediana  -0.011
    min/max  -1.691 / +1.381
```

#### > Ciclos
```text
ANÁLISIS FFT — CICLOS DOMINANTES  [4H]
Filas: 9960 | Rango: 2021-09-13 08:00:00 → 2026-03-31 00:25:00


  dist_p10:
    #1  9960 velas  (9.47% de la energía)
    #2  83 velas  (0.89% de la energía)
    #3  498 velas  (0.88% de la energía)
    #4  84 velas  (0.85% de la energía)
    #5  82 velas  (0.80% de la energía)

  dist_p55:
    #1  9960 velas  (31.45% de la energía)
    #2  498 velas  (3.16% de la energía)
    #3  1992 velas  (2.22% de la energía)
    #4  192 velas  (1.75% de la energía)
    #5  830 velas  (1.53% de la energía)

  dist_p200:
    #1  9960 velas  (30.21% de la energía)
    #2  1992 velas  (7.49% de la energía)
    #3  498 velas  (5.16% de la energía)
    #4  1660 velas  (4.25% de la energía)
    #5  830 velas  (3.77% de la energía)

  dist_10_55:
    #1  9960 velas  (34.31% de la energía)
    #2  498 velas  (3.54% de la energía)
    #3  1992 velas  (2.48% de la energía)
    #4  192 velas  (1.89% de la energía)
    #5  830 velas  (1.71% de la energía)

  dist_55_200:
    #1  9960 velas  (20.75% de la energía)
    #2  1992 velas  (10.86% de la energía)
    #3  498 velas  (6.80% de la energía)
    #4  1660 velas  (6.06% de la energía)
    #5  830 velas  (5.24% de la energía)
```

#### > Apoyos
```text
ESTADÍSTICAS DE APOYOS  [4H]
Filas: 9960 | Rango: 2021-09-13 08:00:00 → 2026-03-31 00:25:00
Parámetros: ventana_min5 velas, rebote10 velas


── Apoyo en EMA10 (713 eventos) ──
  Profundidad (dist precio → EMA10):
    mediana  -1.21%
    p10/p90  -3.64% / -0.00%
    p5/p95   -4.77% / +0.22%
    p25/p75  -2.30% / -0.41%
    min/max  -11.82% / +2.08%
  Rebote 10 velas después:
    tasa éxito (subió)  76.5%
    mediana rebote      +1.46%
    p25/p75 rebote      +0.10% / +3.32%

── Apoyo en EMA55 (630 eventos) ──
  Profundidad (dist precio → EMA55):
    mediana  -1.60%
    p10/p90  -7.24% / +2.25%
    p5/p95   -9.29% / +4.42%
    p25/p75  -4.09% / +0.43%
    min/max  -22.71% / +11.19%
  Rebote 10 velas después:
    tasa éxito (subió)  80.4%
    mediana rebote      +1.65%
    p25/p75 rebote      +0.35% / +3.66%

── Apoyo en EMA200 (632 eventos) ──
  Profundidad (dist precio → EMA200):
    mediana  -1.81%
    p10/p90  -12.10% / +8.08%
    p5/p95   -15.00% / +12.01%
    p25/p75  -6.70% / +3.23%
    min/max  -35.82% / +21.86%
  Rebote 10 velas después:
    tasa éxito (subió)  81.1%
    mediana rebote      +1.65%
    p25/p75 rebote      +0.35% / +3.66%
```

#### > Hurst
```text
EXPONENTE DE HURST  [4H]
Filas: 9960 | Rango: 2021-09-13 08:00:00 → 2026-03-31 00:25:00


Interpretación de H:
  H > 0.65  → Persistente fuerte   (la serie continúa su dirección)
  H 0.55-0.65 → Persistente moderada (algo de memoria)
  H 0.45-0.55 → Casi aleatoria       (sin memoria clara)
  H 0.35-0.45 → Anti-persistente     (tiende a revertir)
  H < 0.35  → Anti-persistente fuerte (revierte muy seguido)

NOTA: Se aplica a las DISTANCIAS, no al precio crudo.
      El precio crudo tiene tendencia que contaminaría el resultado.


  dist_p10:  H0.769 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_p55:  H0.930 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_p200:  H0.998 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_10_55:  H0.927 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_55_200:  H0.996 → Persistente fuerte   — la serie tiende a continuar su dirección
```

#### > Hilbert
```text
ANÁLISIS DE HILBERT  [4H]
Filas: 9960 | Rango: 2021-09-13 08:00:00 → 2026-03-31 00:25:00


Qué mide:
  Envolvente  → amplitud de la oscilación en cada momento
  Período     → cuántas velas dura el ciclo en cada momento
  (Si el período cambia mucho: el ciclo NO es constante en el tiempo)


── EMA10 (dist_p10) ──
  Amplitud media:    1.773%
  Amplitud std:      1.359%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   14.2 velas
  Período p25/p75:   8.4 / 28.1 velas
  Rango intercuartil del período: 19.6 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)

── EMA55 (dist_p55) ──
  Amplitud media:    4.841%
  Amplitud std:      3.177%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   42.2 velas
  Período p25/p75:   21.8 / 94.1 velas
  Rango intercuartil del período: 72.3 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)

── EMA200 (dist_p200) ──
  Amplitud media:    10.114%
  Amplitud std:      5.553%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   97.3 velas
  Período p25/p75:   48.6 / 229.6 velas
  Rango intercuartil del período: 181.0 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)
```

#### > Fib
```text
ANÁLISIS DE FIBONACCI  [4H]
Filas: 9960 | Rango: 2021-09-13 08:00:00 → 2026-03-31 00:25:00


Niveles Fibonacci de referencia: 0.236, 0.382, 0.500, 0.618, 0.786, 1.618

── RATIOS DE TIEMPO (apoyo EMA10 → EMA55 → EMA200) ──
  Secuencias encontradas: 711
  Mediana del ratio:  0.7931
  Media del ratio:    0.9627
  p25/p75:            0.4189 / 1.3636
  Nivel Fib más cercano a la mediana: 0.786  (distancia0.0071)
  Interpretación: si dist < 0.05 al nivel Fib, la proporción es notable

── RATIOS DE AMPLITUD (valle/pico por EMA) ──
  EMA10 (dist_p10):
    Pares pico/valle: 711
    Mediana ratio:    0.6206
    p25/p75:          0.2307 / 1.1746
    Fib más cercano:  0.618  (distancia0.0026)

  EMA55 (dist_p55):
    Pares pico/valle: 629
    Mediana ratio:    0.5540
    p25/p75:          0.2785 / 1.4442
    Fib más cercano:  0.5  (distancia0.0540)

  EMA200 (dist_p200):
    Pares pico/valle: 631
    Mediana ratio:    0.8218
    p25/p75:          0.4919 / 1.3924
    Fib más cercano:  0.786  (distancia0.0358)
```

#### > Correlación
```text
ANÁLISIS DE CORRELACIÓN  [4H]
Filas: 9960 | Rango: 2021-09-13 08:00:00 → 2026-03-31 00:25:00


── CORRELACIÓN SINCRÓNICA (lag  0) ──
  Pearson r    0.5909
  Valor p      0.0000e+00
  Interpretación:
    • Correlación FUERTE (0.5-0.7)
    • Estadísticamente SIGNIFICATIVA (p < 0.05)

── CORRELACIÓN CRUZADA (desfase óptimo) ──
  Lag óptimo   -28 velas
  Correlación en lag óptimo  0.7386
  Interpretación:
    • dist_55_200 PRECEDE a dist_10_55 por 28 velas
    • Mejor correlación con desfase que sincrónica

── RELACIÓN LINEAL (regresión) ──
  Pendiente    0.3501
  Intercepto   -0.0073
  Ecuación: dist_10_55  0.3501 × dist_55_200 + -0.0073

Interpretación de la pendiente:
    • dist_10_55 responde ATENUANDO los movimientos de dist_55_200 (pendiente < 1)

── RESUMEN PARA INDICADOR ──
  1. Correlación sincrónica: SÍ
  2. Desfase óptimo: -28 velas
  3. Relación: dist_10_55 ≈ 0.35 × dist_55_200
  4. Fuerza relación: fuerte
```

#### > Escala
```text
TABLA DE RATIOS DE ESCALA  [4H]


── ESTADÍSTICAS DE DISTANCIAS ──
Variable       | Mediana(abs) |   p25   |   p75   |  Rango  |   Media  |
-------------- | ------------ | ------- | ------- | ------- | -------- |
dist_p10      |        0.72% |   -0.69% |    0.76% |    1.45% |     0.01% |
dist_p55      |        2.15% |   -2.12% |    2.19% |    4.30% |     0.10% |
dist_p200     |        4.85% |   -4.23% |    5.42% |    9.65% |     0.40% |

── RATIOS EMPÍRICOS ──
Usando medianas de valores absolutos:
Ratio      | Valor | Escala más cercana | Distancia |
---------- | ----- | ----------------- | --------- |
55/10     |  2.97 | x3                | 0.030     |
200/55    |  2.25 | x2.5              | 0.249     |
200/10    |  6.69 | x6                | 0.687     |

Usando rangos intercuartiles (p75-p25):
Ratio      | Valor | Escala más cercana | Distancia |
---------- | ----- | ----------------- | --------- |
55/10     |  2.97 | x3                | 0.030     |
200/55    |  2.24 | x2                | 0.242     |
200/10    |  6.66 | x6                | 0.658     |

── INTERPRETACIÓN ──
Distancias pequeñas (<0.05) a escalas teóricas sugieren relación armónica.
Ratios consistentes entre métodos (abs/range) indican robustez.
```

### 🕒 Timeframe: 1H

#### > Stats
```text
ESTADÍSTICAS DESCRIPTIVAS — 1H
Filas: 10000 | Rango: 2025-02-07 10:00:00 → 2026-03-31 00:26:00


── Distancias precio → EMA (%) ──
  dist_p10:
    media    -0.017%
    std      0.683
    p5/p95   -1.131 / +0.978
    p25/p75  -0.290 / +0.294
    mediana  +0.008
    min/max  -5.053 / +6.566

  dist_p55:
    media    -0.102%
    std      1.661
    p5/p95   -2.978 / +2.415
    p25/p75  -0.863 / +0.831
    mediana  -0.039
    min/max  -12.179 / +9.587

  dist_p200:
    media    -0.375%
    std      3.045
    p5/p95   -5.830 / +4.328
    p25/p75  -2.014 / +1.488
    mediana  -0.116
    min/max  -19.236 / +9.011

── Distancias entre EMAs (%) ──
  dist_10_55:
    media    -0.088%
    std      1.263
    p5/p95   -2.264 / +1.822
    p25/p75  -0.676 / +0.633
    mediana  -0.035
    min/max  -8.464 / +5.580

  dist_55_200:
    media    -0.287%
    std      1.945
    p5/p95   -3.788 / +2.717
    p25/p75  -1.280 / +0.960
    mediana  -0.132
    min/max  -9.469 / +4.429

── Ratio Armónico ──
  ratio_armonico (valores extremos recortados a ±5):
    media    +0.339
    std      1.753
    p5/p95   -2.893 / +3.704
    p25/p75  -0.168 / +0.927
    mediana  +0.313


── Pendientes de EMAs (%) ──
  slope10:
    media    -0.016%
    std      0.655
    p5/p95   -1.096 / +0.946
    p25/p75  -0.283 / +0.294
    mediana  +0.004
    min/max  -4.555 / +5.393

  slope55:
    media    -0.018%
    std      0.298
    p5/p95   -0.536 / +0.438
    p25/p75  -0.157 / +0.149
    mediana  -0.008
    min/max  -2.098 / +1.606

  slope200:
    media    -0.019%
    std      0.151
    p5/p95   -0.291 / +0.215
    p25/p75  -0.101 / +0.075
    mediana  -0.005
    min/max  -0.933 / +0.440
```

#### > Ciclos
```text
ANÁLISIS FFT — CICLOS DOMINANTES  [1H]
Filas: 10000 | Rango: 2025-02-07 10:00:00 → 2026-03-31 00:26:00


  dist_p10:
    #1  83 velas  (0.85% de la energía)
    #2  40 velas  (0.82% de la energía)
    #3  111 velas  (0.82% de la energía)
    #4  84 velas  (0.80% de la energía)
    #5  45 velas  (0.78% de la energía)

  dist_p55:
    #1  667 velas  (3.66% de la energía)
    #2  10000 velas  (3.04% de la energía)
    #3  455 velas  (2.90% de la energía)
    #4  323 velas  (2.86% de la energía)
    #5  476 velas  (2.77% de la energía)

  dist_p200:
    #1  10000 velas  (21.16% de la energía)
    #2  2000 velas  (7.64% de la energía)
    #3  667 velas  (6.83% de la energía)
    #4  455 velas  (3.70% de la energía)
    #5  476 velas  (3.70% de la energía)

  dist_10_55:
    #1  10000 velas  (5.00% de la energía)
    #2  667 velas  (4.27% de la energía)
    #3  455 velas  (3.38% de la energía)
    #4  323 velas  (3.30% de la energía)
    #5  476 velas  (3.22% de la energía)

  dist_55_200:
    #1  10000 velas  (31.03% de la energía)
    #2  2000 velas  (8.77% de la energía)
    #3  667 velas  (7.44% de la energía)
    #4  455 velas  (3.78% de la energía)
    #5  476 velas  (3.76% de la energía)
```

#### > Apoyos
```text
ESTADÍSTICAS DE APOYOS  [1H]
Filas: 10000 | Rango: 2025-02-07 10:00:00 → 2026-03-31 00:26:00
Parámetros: ventana_min5 velas, rebote10 velas


── Apoyo en EMA10 (727 eventos) ──
  Profundidad (dist precio → EMA10):
    mediana  -0.47%
    p10/p90  -1.65% / -0.01%
    p5/p95   -2.21% / +0.10%
    p25/p75  -0.93% / -0.20%
    min/max  -5.05% / +1.36%
  Rebote 10 velas después:
    tasa éxito (subió)  74.9%
    mediana rebote      +0.58%
    p25/p75 rebote      +0.00% / +1.29%

── Apoyo en EMA55 (625 eventos) ──
  Profundidad (dist precio → EMA55):
    mediana  -0.65%
    p10/p90  -3.15% / +0.79%
    p5/p95   -4.54% / +1.31%
    p25/p75  -1.72% / +0.08%
    min/max  -12.18% / +3.45%
  Rebote 10 velas después:
    tasa éxito (subió)  79.0%
    mediana rebote      +0.67%
    p25/p75 rebote      +0.13% / +1.40%

── Apoyo en EMA200 (622 eventos) ──
  Profundidad (dist precio → EMA200):
    mediana  -0.71%
    p10/p90  -5.32% / +2.06%
    p5/p95   -7.13% / +3.10%
    p25/p75  -2.77% / +0.67%
    min/max  -19.24% / +6.78%
  Rebote 10 velas después:
    tasa éxito (subió)  80.0%
    mediana rebote      +0.68%
    p25/p75 rebote      +0.16% / +1.45%
```

#### > Hurst
```text
EXPONENTE DE HURST  [1H]
Filas: 10000 | Rango: 2025-02-07 10:00:00 → 2026-03-31 00:26:00


Interpretación de H:
  H > 0.65  → Persistente fuerte   (la serie continúa su dirección)
  H 0.55-0.65 → Persistente moderada (algo de memoria)
  H 0.45-0.55 → Casi aleatoria       (sin memoria clara)
  H 0.35-0.45 → Anti-persistente     (tiende a revertir)
  H < 0.35  → Anti-persistente fuerte (revierte muy seguido)

NOTA: Se aplica a las DISTANCIAS, no al precio crudo.
      El precio crudo tiene tendencia que contaminaría el resultado.


  dist_p10:  H0.763 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_p55:  H0.922 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_p200:  H0.980 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_10_55:  H0.918 → Persistente fuerte   — la serie tiende a continuar su dirección
  dist_55_200:  H0.988 → Persistente fuerte   — la serie tiende a continuar su dirección
```

#### > Hilbert
```text
ANÁLISIS DE HILBERT  [1H]
Filas: 10000 | Rango: 2025-02-07 10:00:00 → 2026-03-31 00:26:00


Qué mide:
  Envolvente  → amplitud de la oscilación en cada momento
  Período     → cuántas velas dura el ciclo en cada momento
  (Si el período cambia mucho: el ciclo NO es constante en el tiempo)


── EMA10 (dist_p10) ──
  Amplitud media:    0.738%
  Amplitud std:      0.622%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   13.8 velas
  Período p25/p75:   8.4 / 25.9 velas
  Rango intercuartil del período: 17.5 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)

── EMA55 (dist_p55) ──
  Amplitud media:    1.890%
  Amplitud std:      1.378%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   37.5 velas
  Período p25/p75:   20.4 / 78.8 velas
  Rango intercuartil del período: 58.5 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)

── EMA200 (dist_p200) ──
  Amplitud media:    3.602%
  Amplitud std:      2.246%  (qué tanto varía la amplitud — mayor std  más irregular)
  Período mediana:   79.4 velas
  Período p25/p75:   42.0 / 177.4 velas
  Rango intercuartil del período: 135.4 velas
  (Rango amplio  ciclo variable; rango estrecho  ciclo estable)
```

#### > Fib
```text
ANÁLISIS DE FIBONACCI  [1H]
Filas: 10000 | Rango: 2025-02-07 10:00:00 → 2026-03-31 00:26:00


Niveles Fibonacci de referencia: 0.236, 0.382, 0.500, 0.618, 0.786, 1.618

── RATIOS DE TIEMPO (apoyo EMA10 → EMA55 → EMA200) ──
  Secuencias encontradas: 725
  Mediana del ratio:  0.7778
  Media del ratio:    0.9894
  p25/p75:            0.4000 / 1.4189
  Nivel Fib más cercano a la mediana: 0.786  (distancia0.0082)
  Interpretación: si dist < 0.05 al nivel Fib, la proporción es notable

── RATIOS DE AMPLITUD (valle/pico por EMA) ──
  EMA10 (dist_p10):
    Pares pico/valle: 726
    Mediana ratio:    0.6183
    p25/p75:          0.2520 / 1.2106
    Fib más cercano:  0.618  (distancia0.0003)

  EMA55 (dist_p55):
    Pares pico/valle: 625
    Mediana ratio:    0.5368
    p25/p75:          0.2680 / 1.4529
    Fib más cercano:  0.5  (distancia0.0368)

  EMA200 (dist_p200):
    Pares pico/valle: 622
    Mediana ratio:    0.7661
    p25/p75:          0.4473 / 1.5543
    Fib más cercano:  0.786  (distancia0.0199)
```

#### > Correlación
```text
ANÁLISIS DE CORRELACIÓN  [1H]
Filas: 10000 | Rango: 2025-02-07 10:00:00 → 2026-03-31 00:26:00


── CORRELACIÓN SINCRÓNICA (lag  0) ──
  Pearson r    0.5524
  Valor p      0.0000e+00
  Interpretación:
    • Correlación FUERTE (0.5-0.7)
    • Estadísticamente SIGNIFICATIVA (p < 0.05)

── CORRELACIÓN CRUZADA (desfase óptimo) ──
  Lag óptimo   -25 velas
  Correlación en lag óptimo  0.7052
  Interpretación:
    • dist_55_200 PRECEDE a dist_10_55 por 25 velas
    • Mejor correlación con desfase que sincrónica

── RELACIÓN LINEAL (regresión) ──
  Pendiente    0.3588
  Intercepto   0.0149
  Ecuación: dist_10_55  0.3588 × dist_55_200 + 0.0149

Interpretación de la pendiente:
    • dist_10_55 responde ATENUANDO los movimientos de dist_55_200 (pendiente < 1)

── RESUMEN PARA INDICADOR ──
  1. Correlación sincrónica: SÍ
  2. Desfase óptimo: -25 velas
  3. Relación: dist_10_55 ≈ 0.36 × dist_55_200
  4. Fuerza relación: fuerte
```

#### > Escala
```text
TABLA DE RATIOS DE ESCALA  [1H]


── ESTADÍSTICAS DE DISTANCIAS ──
Variable       | Mediana(abs) |   p25   |   p75   |  Rango  |   Media  |
-------------- | ------------ | ------- | ------- | ------- | -------- |
dist_p10      |        0.29% |   -0.29% |    0.29% |    0.58% |    -0.02% |
dist_p55      |        0.84% |   -0.86% |    0.83% |    1.69% |    -0.10% |
dist_p200     |        1.73% |   -2.01% |    1.49% |    3.50% |    -0.37% |

── RATIOS EMPÍRICOS ──
Usando medianas de valores absolutos:
Ratio      | Valor | Escala más cercana | Distancia |
---------- | ----- | ----------------- | --------- |
55/10     |  2.89 | x3                | 0.106     |
200/55    |  2.05 | x2                | 0.048     |
200/10    |  5.93 | x6                | 0.074     |

Usando rangos intercuartiles (p75-p25):
Ratio      | Valor | Escala más cercana | Distancia |
---------- | ----- | ----------------- | --------- |
55/10     |  2.90 | x3                | 0.099     |
200/55    |  2.07 | x2                | 0.067     |
200/10    |  6.00 | x6                | 0.004     |

── INTERPRETACIÓN ──
Distancias pequeñas (<0.05) a escalas teóricas sugieren relación armónica.
Ratios consistentes entre métodos (abs/range) indican robustez.
```

---
## 🤖 INSTRUCCIÓN PARA IA (PROMPT)
> **Copia y pega el siguiente texto en tu chat con IA:**

```text
Actúa como una IA experta en análisis cuantitativo, procesamiento de señales y trading algorítmico.
He realizado una serie de análisis matemáticos (Fourier, Hurst, Hilbert, Fibonacci, correlación, escala y comparación entre timeframes) sobre las distancias del precio de BTC a sus EMAs de 10, 55 y 200 períodos en diferentes timeframes (1D, 4H, 1H).

Basándote en los DATOS NUMÉRICOS proporcionados arriba en el reporte:
1. Identifica las MAGNITUDES RECURRENTES de las correcciones (¿a qué distancia típica en % rebotan los apoyos en cada EMA?).
2. Detecta si existe una RELACIÓN DE ESCALA constante entre los timeframes (¿se repiten los mismos ratios?).
3. Determina si el Exponente de Hurst y la Transformada de Hilbert confirman que el sistema es persistente y tiene ciclos estables.
4. Concluye con un SET DE PARÁMETROS sugeridos (umbrales de entrada, filtros de tendencia y duraciones de ciclo) para implementar un indicador de 'Magnitudes Armónicas' en Pine Script v6 que detecte zonas de alta probabilidad de rebote.
```