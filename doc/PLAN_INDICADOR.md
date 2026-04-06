# 📌 PLAN: Del Análisis Histórico al Indicador

**Fecha de acuerdo:** 2026-04-03  
**Estado:** ACTIVO — Guía de trabajo en curso

---

## 🎯 Objetivo reformulado (acuerdo final)

> Usar los resultados del análisis histórico (ya implementado) para extraer
> **parámetros, constantes y rangos estadísticos** que alimenten un **indicador
> en Pine Script**. El indicador no dirá qué hacer — describirá cuantitativamente
> el estado actual del mercado para que el trader decida.

**El trader decide. El indicador solo informa.**

---

## 🧠 Flujo completo del sistema

```
FASE A — Estudio histórico  (periódico: mensual o semanal)
─────────────────────────────────────────────────────────
  1. Descargar datos desde TradingView (Pine Script → logs CSV)
  2. Correr: python main.py   (pipeline completo)
  3. Obtener resultados en results/  (gráficas + .txt)
  4. Correr: python generate_pdf_report.py
  5. Leer el PDF maestro generado
  6. Extraer manualmente los parámetros clave (ver tabla abajo)
  7. Ingresar esos parámetros como inputs en el indicador Pine Script

FASE B — Indicador en tiempo real  (uso diario)
─────────────────────────────────────────────────────────
  1. Abrir TradingView con el indicador cargado
  2. Los parámetros históricos ya están ingresados
  3. El indicador pinta en tiempo real dónde está el precio
     respecto a esos rangos históricos conocidos
  4. El trader lee la descripción visual y decide

FASE C — Actualización periódica
─────────────────────────────────────────────────────────
  1. Volver a Fase A cada mes (o semana si el mercado cambió mucho)
  2. Comparar nuevos parámetros con los anteriores
  3. Actualizar inputs del indicador si hay cambio significativo
```

---

## 📊 Parámetros que se extraen del estudio histórico

Estos son los números que el trader lee en el PDF y luego ingresa al indicador:

| Parámetro | De dónde sale | Para qué sirve en el indicador |
|-----------|--------------|-------------------------------|
| `p5_dist_p10` | `explore_*_stats.txt` → dist_p10 p5 | Zona extrema inferior vs EMA10 |
| `p95_dist_p10` | `explore_*_stats.txt` → dist_p10 p95 | Zona extrema superior vs EMA10 |
| `p25_dist_p10` | `explore_*_stats.txt` → dist_p10 p25 | Rango normal inferior vs EMA10 |
| `p75_dist_p10` | `explore_*_stats.txt` → dist_p10 p75 | Rango normal superior vs EMA10 |
| `mediana_dist_p10` | `explore_*_stats.txt` | Centro histórico vs EMA10 |
| `p5_dist_p55` | `explore_*_stats.txt` → dist_p55 p5 | Zona extrema inferior vs EMA55 |
| `p95_dist_p55` | idem | Zona extrema superior vs EMA55 |
| `p25_dist_p55` / `p75_dist_p55` | idem | Rango normal vs EMA55 |
| `mediana_dist_p55` | idem | Centro histórico vs EMA55 |
| `p5_dist_p200` | `explore_*_stats.txt` → dist_p200 p5 | Zona extrema inferior vs EMA200 |
| `p95_dist_p200` | idem | Zona extrema superior vs EMA200 |
| `p25_dist_p200` / `p75_dist_p200` | idem | Rango normal vs EMA200 |
| `mediana_dist_p200` | idem | Centro histórico vs EMA200 |
| `ciclo_dominante_velas` | `fft_*_ciclos.txt` → #1 ciclo dist_p55 | Frecuencia esperada del patrón |
| `amplitud_tipica_p10` | `apoyo_*_stats.txt` → mediana profundidad EMA10 | Profundidad típica del apoyo |
| `amplitud_tipica_p55` | `apoyo_*_stats.txt` → mediana profundidad EMA55 | Profundidad típica del apoyo |
| `amplitud_tipica_p200` | `apoyo_*_stats.txt` → mediana profundidad EMA200 | Profundidad típica del apoyo |
| `tasa_exito_p10` | `apoyo_*_stats.txt` → tasa éxito EMA10 | Contexto estadístico del rebote |
| `tasa_exito_p55` | `apoyo_*_stats.txt` → tasa éxito EMA55 | Contexto estadístico del rebote |
| `tasa_exito_p200` | `apoyo_*_stats.txt` → tasa éxito EMA200 | Contexto estadístico del rebote |
| `ratio_armonico_mediana` | `correlation_*_stats.txt` | Proporción típica entre EMAs |
| `hurst_dist_p55` | `hurst_*_valores.txt` | ¿La serie tiene memoria? (H) |

---

## 🔧 Qué hace el indicador con esos parámetros

El indicador **no opina**. Solo describe el estado actual con tres bloques:

### Bloque 1 — Posición del precio (oscilador normalizado)
Para cada EMA calcula:
```
score_actual = (dist_pX_ahora - mediana_historica) / (p95 - p5)
```
- `score = 0`   → precio en su posición histórica típica respecto a esa EMA
- `score = +1`  → precio en el extremo superior histórico (muy extendido arriba)
- `score = -1`  → precio en el extremo inferior histórico (muy extendido abajo)

### Bloque 2 — Geometría de las EMAs (sin etiquetas de dirección)
Muestra los valores actuales de:
- `dist_10_55`   → separación entre EMA10 y EMA55
- `dist_55_200`  → separación entre EMA55 y EMA200
- `ratio_armonico` → proporción entre ambas separaciones

### Bloque 3 — Contexto estadístico (percentil actual)
Para cada `dist_pX` muestra en qué percentil histórico está **ahora**:
- `"estás en el percentil 82 de dist_p55"` → solo el 18% de los días históricos
  el precio estuvo más alejado de la EMA55 que hoy

---

## 🗺️ Tareas pendientes — Backlog ordenado

| # | Tarea | Script | Estado |
|---|-------|--------|--------|
| 1 | **Generador de PDF maestro** | `generate_pdf_report.py` | ✅ Hecho |
| 2 | **Tabla de extracción de parámetros** | En el PDF (sección dedicada) | ✅ En PDF |
| 3 | **Spec matemática del indicador** | `doc/SPEC_INDICADOR.md` | ⏳ Pendiente |
| 4 | **Indicador Pine Script v2** | `pinescript/harmonic_state.pine` | ⏳ Pendiente |

---

## 🚫 Límites acordados (no hacer)

- ❌ El indicador **nunca dirá** "alcista", "bajista", "entra", "sale"
- ❌ No clasificar por régimen de mercado
- ❌ No hacer backtesting de señales
- ❌ No asumir que el patrón predice el futuro

---

## 💡 Cómo usar el resultado

```
Flujo del trader en el día a día:
  1. Miras el indicador en 1D → ves el "estado de marea" (geometría de EMAs)
  2. Bajas a 4H → ves la posición del precio en su rango histórico (score)
  3. Bajas a 1H → ves el percentil actual vs historia
  4. Con esa descripción cuantitativa, aplicas TU criterio y estrategia
```

---

*Documento de referencia del acuerdo de diseño. Actualizar con cada decisión nueva.*
