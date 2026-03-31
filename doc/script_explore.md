# 📄 explore.py — Análisis exploratorio visual

## ¿Qué hace?
Grafica y calcula estadísticas descriptivas de todas las variables calculadas
por el indicador. **No detecta patrones ni hace predicciones** — solo muestra
cómo se comportan los datos: rangos, distribuciones, tendencias históricas.

Es el primer análisis que debes revisar. Te da una foto completa del dataset.

---

## Cuándo correrlo
Después de `parse_csv.py`, como primer paso de análisis.
Cada vez que tengas datos nuevos, córrelo de nuevo para actualizar las gráficas.

```bash
python explore.py
```

---

## Entrada
- **Carpeta:** `results/`
- **Archivos:** todos los `*_clean.csv` generados por `parse_csv.py`
- **Requisito:** columna `ema200` con datos (filas sin EMA200 se descartan)

---

## Procesamiento interno
1. Carga cada `_clean.csv` y filtra filas con EMA200 vacía
2. **Gráfica de distancias:** serie temporal + histograma de `dist_p10`, `dist_p55`, `dist_p200`
3. **Gráfica de ratio:** serie temporal de `dist_10_55`, `dist_55_200` y `ratio_armonico`
4. **Estadísticas:** calcula media, std, mediana, percentiles 5/25/75/95, min/max de todas las variables

---

## Salida — archivos generados en `results/`

### Por cada timeframe (1D, 4H, 1H):

| Archivo | Tipo | Contenido |
|---------|------|-----------|
| `explore_{TF}_distancias.png` | Imagen | Serie temporal + histograma de las 3 distancias precio→EMA. El precio de cierre se muestra abajo como referencia |
| `explore_{TF}_ratio.png` | Imagen | Serie temporal de `dist_10_55` (azul), `dist_55_200` (amarillo) y `ratio_armonico` (naranja, recortado a ±3) |
| `explore_{TF}_stats.txt` | Texto | Tabla de estadísticas descriptivas de todas las variables |

---

## Cómo interpretar los resultados

### `explore_{TF}_distancias.png`
- El **área verde** (sobre el cero) = precio por encima de la EMA → estructura alcista
- El **área roja** (bajo el cero) = precio por debajo de la EMA → corrección o bajista
- La **línea de mediana** (cyan) en el histograma: si está cerca de 0, el precio pasa tiempo similar arriba y abajo de la EMA. Si está positiva, el mercado estuvo más tiempo en tendencia alcista en el período analizado
- Los **percentiles p5/p95** (naranja) en el histograma: definen los extremos estadísticos. Valores fuera de ese rango son poco frecuentes

### `explore_{TF}_ratio.png`
- `dist_10_55` > 0 y `dist_55_200` > 0 = estructura completamente alcista (EMAs en orden: 10 > 55 > 200)
- `ratio_armonico` estable y positivo = las EMAs se mueven en proporción armónica
- `ratio_armonico` negativo = las dos distancias tienen signos opuestos → transición o estructura mixta

### `explore_{TF}_stats.txt`
Ejemplo de lectura para `dist_p10` en 1D:
```
dist_p10:
  mediana = +0.19%   → el precio pasa la mitad del tiempo apenas sobre la EMA10
  p25/p75 = -2.1% / +2.6%  → zona "normal" de oscilación respecto a EMA10
  p5/p95  = -7.0% / +8.1%  → extremos poco frecuentes
  min/max = -38% / +21%     → movimientos excepcionales (crashes / euforia)
```
**Lo útil:** los rangos p25/p75 y p5/p95 definen las zonas operativas del patrón.
