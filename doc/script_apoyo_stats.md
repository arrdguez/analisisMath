# 📄 apoyo_stats.py — Estadísticas de apoyos en EMAs

## ¿Qué hace?
Detecta automáticamente los eventos de **"apoyo"** (mínimos locales del precio
relativo a cada EMA) y mide dos cosas:
1. **Profundidad del apoyo**: qué tan lejos llegó el precio antes de rebotar
2. **Rebote posterior**: cuánto subió (o bajó) el precio en las siguientes N velas

**No decide si fue una buena entrada. Solo mide qué pasó históricamente.**

---

## Cuándo correrlo
Después de `explore.py`. Puede correrse en paralelo con `fft_analysis.py`.

```bash
python apoyo_stats.py
```

---

## Parámetros configurables (al inicio del archivo)
```python
VENTANA_MIN  = 5    # velas a cada lado para detectar un mínimo local
REBOTE_VELAS = 10   # velas hacia adelante para medir el rebote
```
- **`VENTANA_MIN`**: controla qué tan "significativo" debe ser el mínimo. Un valor mayor detecta menos apoyos pero más claros. Un valor menor detecta más pero incluye ruido.
- **`REBOTE_VELAS`**: cuántas velas después del apoyo se mide el precio para calcular el rebote. Cambia según tu horizonte de trading.

---

## Entrada
- **Carpeta:** `results/`
- **Archivos:** todos los `*_clean.csv`
- **Variables analizadas:** `dist_p10`, `dist_p55`, `dist_p200`

---

## Qué es un "apoyo" para este script
Un mínimo local de `dist_pX` = un momento donde el precio estaba más cerca
(o más por debajo) de la EMA que en las velas anteriores y posteriores.

> No es necesariamente un toque exacto de la EMA. Captura el momento de
> **máxima cercanía** del precio a la media antes de alejarse.

---

## Procesamiento interno
1. Toma la serie `dist_pX` y encuentra los mínimos locales con ventana `VENTANA_MIN`
2. Para cada mínimo registra: fecha, precio, valor de `dist_pX` en ese punto
3. Calcula el cambio de precio `REBOTE_VELAS` velas después: `(close_futuro - close_apoyo) / close_apoyo * 100`
4. Genera estadísticas: percentiles de profundidad y distribución de rebotes

---

## Salida — archivos generados en `results/`

### Por cada timeframe (1D, 4H, 1H):

| Archivo | Tipo | Contenido |
|---------|------|-----------|
| `apoyo_{TF}_detalle.png` | Imagen | Izquierda: serie histórica con los apoyos marcados como puntos + líneas de percentiles. Derecha: histograma horizontal de las profundidades |
| `apoyo_{TF}_rebote.png` | Imagen | Histograma del % de rebote N velas después, por EMA. Muestra la tasa de éxito (% que subió) |
| `apoyo_{TF}_stats.txt` | Texto | Tabla completa: número de eventos, percentiles de profundidad, tasa de éxito, mediana de rebote |

---

## Cómo interpretar los resultados

### `apoyo_{TF}_stats.txt` — ejemplo real (1D BTC 2018-2026)
```
── Apoyo en EMA10 (225 eventos) ──
  Profundidad:
    mediana = -3.45%    ← en el apoyo típico, el precio estaba 3.45% bajo la EMA10
    p25/p75 = -6.27% / -1.21%   ← rango donde cae el 50% central de los apoyos
    p10/p90 = -9.04% / +0.19%   ← rango donde cae el 80% de los apoyos
  Rebote 10 velas después:
    tasa éxito = 75.9%  ← 3 de cada 4 veces el precio subió
    mediana rebote = +4.91%
```

### `apoyo_{TF}_detalle.png`
- Cada **punto de color** sobre la serie es un apoyo detectado
- Las **líneas horizontales de puntos** son los percentiles p10/p25/p75/p90
- El **histograma derecho** muestra la distribución de profundidades:
  si es simétrico alrededor de 0 → los apoyos ocurren tanto sobre como bajo la EMA
  si está sesgado a la izquierda → la mayoría de apoyos ocurren con precio bajo la EMA

### `apoyo_{TF}_rebote.png`
- La **línea blanca vertical** es el cero (precio igual al del apoyo)
- La **línea cyan** es la mediana del rebote
- Todo lo que está a la **derecha del cero** = rebote positivo (precio subió)
- El título de cada panel muestra la **tasa de éxito** directamente

### Lectura combinada de los 3 niveles (EMA10 / EMA55 / EMA200)
| EMA | Profundidad típica | Tasa éxito | Rebote mediano | Interpretación |
|-----|--------------------|-----------|----------------|----------------|
| EMA10  | -3.5% | 76% | +5%  | Correcciones normales, rebotan moderado |
| EMA55  | -4.0% | 83% | +5.5%| Correcciones más profundas, más confiables |
| EMA200 | -1.0% | 85% | +6.3%| Máxima confiabilidad, mayor rebote |

> **Nota:** los valores de la tabla son del ejemplo real 1D. Los valores de 4H y 1H
> serán diferentes — consulta los archivos `_stats.txt` correspondientes.
