# FASE 1: HALLazgos de Backtesting

## 📊 Resumen Ejecutivo
El backtesting inicial con reglas simples (umbral de profundidad + pendiente positiva) **no muestra edge estadístico** en los timeframes analizados. Sin embargo, el análisis de apoyos previo (apoyo_stats.py) indica tasas de éxito del 75-85%, sugiriendo que la detección simple no captura la naturaleza de los apoyos reales (mínimos locales).

## 🧪 Metodología
1. **Reglas probadas**: Señal cuando `dist_pX < umbral` y `slopeX > 0`
2. **Umbrales**: Profundidad mediana histórica por EMA y timeframe
3. **Target**: Rebote mediano histórico (10 velas)
4. **Stop loss**: 1.5× profundidad mediana
5. **Período**: Datos completos disponibles (2018-2026 para 1D, 2021-2026 para 4H, 2025-2026 para 1H)

## 📈 Resultados por Timeframe

### 1D (Umbral: -3.50%)
| EMA | Señales | Operaciones | Win Rate | Profit Factor | Retorno Total |
|-----|---------|-------------|----------|---------------|---------------|
| 10  | 27      | 27          | 51.9%    | 0.57          | -29.0%        |
| 55  | 16      | 16          | 56.2%    | 0.69          | -11.5%        |
| 200 | 9       | 9           | 55.6%    | 0.67          | -7.0%         |

### 4H (Umbral: -1.20%)
| EMA | Señales | Operaciones | Win Rate | Profit Factor | Retorno Total |
|-----|---------|-------------|----------|---------------|---------------|
| 10  | 69      | 69          | 62.3%    | 0.88          | -5.5%         |
| 55  | 38      | 38          | 57.9%    | 0.77          | -8.7%         |
| 200 | 25      | 25          | 56.0%    | 0.74          | -5.0%         |

### 1H (Umbral: -0.50%)
| EMA | Señales | Operaciones | Win Rate | Profit Factor | Retorno Total |
|-----|---------|-------------|----------|---------------|---------------|
| 10  | 80      | 80          | 58.8%    | 0.84          | -6.8%         |
| 55  | 62      | 62          | 58.1%    | 0.82          | -8.5%         |
| 200 | 45      | 45          | 57.8%    | 0.80          | -7.2%         |

## 🔍 Comparación con Análisis de Apoyos
| Timeframe | EMA | Éxito histórico* | Win Rate backtest | Diferencia |
|-----------|-----|------------------|-------------------|------------|
| 1D       | 10  | 75.9%           | 51.9%            | -24.0pp    |
| 1D       | 55  | 82.8%           | 56.2%            | -26.6pp    |
| 1D       | 200 | 84.9%           | 55.6%            | -29.3pp    |
| 4H       | 10  | 76.5%           | 62.3%            | -14.2pp    |
| 1H       | 10  | 74.9%           | 58.8%            | -16.1pp    |

*Tasa de éxito del análisis apoyo_stats.py (rebote 10 velas después de apoyo detectado)

## 🧠 Interpretación
1. **La detección simple no equivale a apoyo real**: Un precio por debajo de un umbral no garantiza que sea un mínimo local (apoyo). Los apoyos reales ocurren en mínimos locales que luego rebotan.
2. **La pendiente positiva es insuficiente**: Muchas señales ocurren durante descensos continuos donde la pendiente es positiva momentáneamente pero no hay rebote.
3. **Filtros adicionales necesarios**: Se requieren:
   - Detección de mínimos locales (ventana de N velas)
   - Confirmación de rebote (precio sube después del mínimo)
   - Filtros de ratio armónico y convergencia

## 🎯 Conclusiones para FASE 2
1. **NO proceder con reglas simples** → El edge no existe con esta implementación.
2. **SÍ proceder con detección de mínimos locales** → Usar la misma lógica que `apoyo_stats.py` (ventana de 5 velas, rebote de 10 velas).
3. **Priorizar calidad sobre cantidad** → Menos señales pero más precisas.

## 📋 Recomendaciones para FASE 2
1. **Implementar detección de apoyos reales** en el indicador Pine Script:
   - Mínimo local en `dist_pX` (ventana de 5-10 velas)
   - Confirmación de rebote (precio sube X% en Y velas)
   - Filtro de pendiente EMA positiva
2. **Incluir filtro de ratio armónico**:
   - `dist_10_55 / dist_55_200` cerca de 0.3 (mediana histórica)
3. **Target dinámico** basado en percentiles de rebote histórico:
   - No usar target fijo, sino percentil 75 de rebotes pasados
4. **Backtesting con eventos reales**:
   - Exportar índices de apoyos detectados por `apoyo_stats.py`
   - Simular operaciones solo en esos puntos

## 🚨 Limitaciones del Análisis Actual
- **Detección muy simplista**: No usa mínimos locales
- **Targets/Stops fijos**: No adaptativos al mercado
- **Sin filtro de tendencia**: Operaciones en tendencias bajistas
- **Sin gestión de riesgo**: Posición size fijo

## 📊 Archivos Generados
- `resultados_backtest/backtest_ema*_*.csv` → Detalles de operaciones
- `resultados_backtest/backtest_summary_*.csv` → Resumen general
- `distribucion_*.png` → Gráficos de distribución (analizar_datos.py)

## 🔄 Próximos Pasos Inmediatos
1. **Modificar `apoyo_stats.py`** para exportar CSV con eventos de apoyo detectados
2. **Backtesting con eventos reales** usando ese CSV
3. **Si edge confirmado**, diseñar indicador Pine Script con misma lógica
4. **Si no hay edge**, reevaluar premisa del proyecto

---
*Fecha: 2026-03-31*  
*Estado: FASE 1 completada - Se requiere ajuste de estrategia*