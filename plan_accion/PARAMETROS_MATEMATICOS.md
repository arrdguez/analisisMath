# 🔢 PARÁMETROS MATEMÁTICOS PARA INDICADOR

## 📊 RESUMEN EJECUTIVO
Análisis cuantitativo completo de las relaciones armónicas entre EMAs (10, 55, 200) en BTC/USD timeframe 1D. Estos parámetros deben usarse para construir un indicador en Pine Script que detecte zonas de alta probabilidad de rebote.

---

## 🎯 PARÁMETROS CLAVE POR EMA (1D)

### EMA10
| Parámetro | Valor | Interpretación |
|-----------|-------|----------------|
| **Profundidad mediana de apoyo** | -3.45% | Cuando el precio está 3.45% por debajo de EMA10, hay 75.9% probabilidad de rebote |
| **Rebote mediano esperado** | +4.91% | Tras apoyo, sube ~4.91% en 10 velas |
| **Rango típico (p25-p75)** | -6.27% a -1.21% | La mayoría de apoyos ocurren en este rango |
| **Amplitud media oscilación** | 5.49% | Tamaño promedio de las oscilaciones alrededor de EMA10 |
| **Período mediano ciclo** | 14.4 velas | Ciclo promedio de oscilación |
| **Exponente Hurst** | 0.790 | Serie PERSISTENTE: tiende a continuar su dirección |
| **Ratio Fibonacci más cercano** | 0.5 | Amplitudes tienden a retroceder 50% |

### EMA55
| Parámetro | Valor | Interpretación |
|-----------|-------|----------------|
| **Profundidad mediana de apoyo** | -4.03% | Profundidad típica antes de rebote (82.8% éxito) |
| **Rebote mediano esperado** | +5.49% | Subida promedio post-apoyo |
| **Rango típico (p25-p75)** | -11.47% a +3.92% | Rango amplio (apoyos más profundos) |
| **Amplitud media oscilación** | 16.22% | Oscilaciones más amplias que EMA10 |
| **Período mediano ciclo** | 45.8 velas | Ciclo más largo que EMA10 |
| **Exponente Hurst** | 0.948 | PERSISTENTE FUERTE |
| **Ratio Fibonacci más cercano** | 0.618 | Amplitudes tienden a 61.8% retroceso |

### EMA200
| Parámetro | Valor | Interpretación |
|-----------|-------|----------------|
| **Profundidad mediana de apoyo** | -1.02% | Apoyos más superficiales (84.9% éxito) |
| **Rebote mediano esperado** | +6.28% | Mayor rebote promedio |
| **Rango típico (p25-p75)** | -19.99% a +14.71% | Rango muy amplio |
| **Amplitud media oscilación** | 34.73% | Oscilaciones más grandes |
| **Período mediano ciclo** | 99.3 velas | Ciclo más largo |
| **Exponente Hurst** | 1.001 | PERSISTENTE MUY FUERTE |
| **Ratio Fibonacci más cercano** | 0.786 | Amplitudes tienden a 78.6% retroceso |

---

## 🔗 RELACIONES ENTRE EMAs

### Ratio Armónico (`dist_10_55 / dist_55_200`)
| Parámetro | Valor | Interpretación |
|-----------|-------|----------------|
| **Mediana histórica** | 0.306 | Valor "normal" de la relación |
| **Rango típico (p25-p75)** | -0.050 a 0.790 | 50% de valores caen aquí |
| **Relevancia** | Filtro de calidad | Cuando ratio está cerca de 0.3, mayor probabilidad de patrón armónico |

### Correlación y Escala
| Relación | Valor | Interpretación |
|----------|-------|----------------|
| **Correlación dist_10_55 vs dist_55_200** | r = 0.6277 | Correlación FUERTE y significativa |
| **Desfase óptimo** | -32 velas | dist_55_200 precede a dist_10_55 por 32 velas |
| **Relación lineal** | dist_10_55 ≈ 0.3675 × dist_55_200 | Movimientos atenuados |
| **Ratio escala 55/10** | ~3.30 | EMA55 oscila ~3.3× más que EMA10 |
| **Ratio escala 200/55** | ~2.21 | EMA200 oscila ~2.2× más que EMA55 |
| **Ratio escala 200/10** | ~7.28 | EMA200 oscila ~7.3× más que EMA10 |

### Ciclos Dominantes (FFT)
| Serie | Ciclo #1 | Ciclo #2 | Interpretación |
|-------|----------|----------|----------------|
| **dist_p10** | 2906 velas | 969 velas | Ciclo muy largo dominante |
| **dist_p55** | 969 velas | 1453 velas | Ciclos ~3-4 años |
| **dist_p200** | 969 velas | 1453 velas | Mismos ciclos que EMA55 |
| **dist_10_55** | 969 velas | 1453 velas | Ciclos sincronizados |
| **dist_55_200** | 1453 velas | 969 velas | Ciclos inversamente relacionados |

---

## 🎨 DISEÑO DE INDICADOR (Propuesta)

### 1. Zonas de Apoyo Visuales
```pine
// EMA10
support_zone_10 = price * (1 - 0.0345)  // -3.45%
// EMA55  
support_zone_55 = price * (1 - 0.0403)  // -4.03%
// EMA200
support_zone_200 = price * (1 - 0.0102) // -1.02%
```

### 2. Detección de Apoyos (Mínimos Locales)
```pine
// Ventana de 5 velas para mínimo local
is_local_min_10 = lowest(dist_p10, 5) == dist_p10[2]  // mínimo en centro de ventana
// Confirmación de rebote: precio sube X% en Y velas
rebote_confirmed = close > close[5] * 1.02  // +2% en 5 velas
```

### 3. Filtro de Ratio Armónico
```pine
ratio_actual = dist_10_55 / dist_55_200
ratio_normal = 0.306
ratio_ok = abs(ratio_actual - ratio_normal) / abs(ratio_normal) < 0.3  // ±30%
```

### 4. Panel de Métricas en Tiempo Real
```
┌─────────────────────────────┐
│ MAGNITUDES ARMÓNICAS (1D)   │
├─────────────────────────────┤
│ Distancia a EMA10:  -2.1%   │
│ Distancia a EMA55:  -5.3%   │
│ Distancia a EMA200: +8.7%   │
│ Ratio armónico:     0.28    │
│ Ciclo actual:       14 v    │
│ Estado:             IMPULSO │
└─────────────────────────────┘
```

### 5. Alertas Configurables
- **Alerta 1**: Precio entra en zona de apoyo EMA10 (-3.45%)
- **Alerta 2**: Ratio armónico cerca de 0.3 (±30%)
- **Alerta 3**: Mínimo local detectado + rebote confirmado
- **Alerta 4**: Convergencia crítica (dist_10_55 y dist_55_200 < percentil 10)

---

## ⚙️ PARÁMETROS CONFIGURABLES EN PINE SCRIPT

### Inputs del Usuario
```pine
// Profundidades de apoyo
input_depth_ema10 = input.float(-3.45, "Profundidad EMA10 (%)", minval=-20, maxval=0)
input_depth_ema55 = input.float(-4.03, "Profundidad EMA55 (%)", minval=-30, maxval=0)
input_depth_ema200 = input.float(-1.02, "Profundidad EMA200 (%)", minval=-50, maxval=0)

// Filtros
input_ratio_threshold = input.float(0.3, "Umbral ratio armónico (±)", minval=0.1, maxval=1.0)
input_window_min = input.int(5, "Ventana mínimo local", minval=3, maxval=20)
input_rebote_bars = input.int(10, "Velas para confirmar rebote", minval=5, maxval=50)

// Visualización
input_show_zones = input.bool(true, "Mostrar zonas de apoyo")
input_show_panel = input.bool(true, "Mostrar panel de métricas")
input_alerts = input.bool(true, "Activar alertas")
```

### Parámetros Calculados Automáticamente
```pine
// Basados en análisis histórico
typical_range_10 = array.new_float(2)
array.set(typical_range_10, 0, -6.27)  // p25
array.set(typical_range_10, 1, -1.21)  // p75

rebote_median_10 = 4.91  // %
cycle_period_10 = 14.4   // velas
hurst_10 = 0.790
```

---

## 🧪 VALIDACIÓN MATEMÁTICA

### 1. Consistencia Multi-Timeframe
| Parámetro | 1D | 4H | 1H | Consistencia |
|-----------|----|----|----|--------------|
| Win rate apoyo EMA10 | 75.9% | 76.5% | 74.9% | ✅ ALTA |
| Profundidad mediana | -3.45% | -1.21% | -0.47% | ✅ ESCALADO |
| Ratio armónico mediano | 0.306 | 0.302 | 0.313 | ✅ ALTA |

### 2. Robustez Estadística
- **Hurst > 0.65** en todas las series → Patrones persistentes
- **Correlación significativa** (p < 0.05) entre distancias
- **Ratios de escala consistentes** entre métodos (abs/range)
- **Ciclos sincronizados** entre EMAs

### 3. Relaciones Armónicas Confirmadas
1. **Ratio 55/10 ≈ 3.3** → Cerca de 3 (entero)
2. **Ratio 200/55 ≈ 2.2** → Cerca de 2 (entero)  
3. **Ratio tiempo apoyos ≈ 0.786** → Nivel Fibonacci
4. **Ratio amplitud ≈ 0.5-0.786** → Niveles Fibonacci

---

## 🚀 IMPLEMENTACIÓN RECOMENDADA

### Fase 1: Indicador Visual Básico
1. **Zonas de apoyo** (líneas horizontales en -3.45%, -4.03%, -1.02%)
2. **Panel de métricas** (distancias actuales, ratio, estado)
3. **Alertas simples** (entrada en zona)

### Fase 2: Detección Automática
1. **Mínimos locales** (ventana de N velas)
2. **Confirmación de rebote** (precio sube X% en Y velas)
3. **Filtro de ratio armónico** (cercano a 0.3)

### Fase 3: Mejoras Avanzadas
1. **Espacio de fases** (gráfico 2D dist_p10 vs dist_p55)
2. **Filtro de convergencia** (alerta cuando distancias se acercan a cero)
3. **Targets dinámicos** (basados en percentiles históricos de rebote)

---

## 📈 BACKTESTING EN TRADINGVIEW

### Estrategia Simple a Probar
```
CONDICIÓN ENTRADA:
  1. Precio en zona de apoyo EMA10 (-3.45%)
  2. Ratio armónico entre 0.214 y 0.398 (±30% de 0.306)
  3. Mínimo local detectado (ventana 5 velas)

CONDICIÓN SALIDA:
  Target: +4.91% (rebote mediano)
  Stop loss: -5.0% (conservador)
  Timeout: 50 velas (max hold)

GESTIÓN:
  Tamaño posición fijo
  Sin piramidar
  Una operación activa máxima
```

### Métricas Esperadas (Basadas en Análisis)
- **Win rate**: 75-85% (según análisis de apoyos)
- **Profit factor**: > 1.5 (estimado)
- **Expectativa positiva**: Sí (rebote mediano > profundidad mediana)
- **Drawdown controlado**: Stop loss definido

---

## 🧠 PRINCIPIOS DE DISEÑO

1. **Simple primero**: Comenzar con indicador visual, luego añadir señales
2. **Parámetros basados en datos**: Usar valores cuantificados, no intuiciones
3. **Transparencia**: Mostrar cálculos y métricas en panel
4. **Configurabilidad**: Permitir ajustes pero con valores por defecto validados
5. **Validación visual**: El indicador debe coincidir con lo que se ve a simple vista

---

## 📋 ARCHIVOS DE REFERENCIA

- `results/REPORTE_MATEMATICO_IA.md` → Análisis completo
- `results/apoyo_1D_stats.txt` → Estadísticas de apoyos
- `results/correlation_1D_stats.txt` → Relaciones entre distancias
- `results/scale_1D_table.txt` → Ratios de escala
- `results/hurst_1D_valores.txt` → Persistencia de series
- `results/fft_1D_ciclos.txt` → Ciclos dominantes
- `results/hilbert_1D_resumen.txt` → Amplitud y período instantáneo
- `results/fibonacci_1D_stats.txt` → Ratios Fibonacci

---

## 🎯 PRÓXIMOS PASOS

1. **Codificar indicador básico** en Pine Script con zonas visuales
2. **Probar en TradingView** con datos históricos (verificación visual)
3. **Ajustar parámetros** si es necesario (pero mantener base matemática)
4. **Añadir detección automática** de apoyos (mínimos locales)
5. **Implementar alertas** configurables
6. **Documentar** uso y limitaciones

---
*Última actualización: 2026-03-31*  
*Base de datos: BTC/USD 1D (2018-04-18 → 2026-03-31)*