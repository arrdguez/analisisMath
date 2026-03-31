# 📄 parse_csv.py — Limpieza de datos

## ¿Qué hace?
Convierte los CSV crudos exportados desde TradingView (formato sucio con `;` y miles con `,`)
en archivos CSV limpios y estándar listos para analizar.

**No hace ningún análisis. Solo limpia y estandariza.**

---

## Cuándo correrlo
**Siempre primero**, cada vez que descargues datos nuevos de TradingView.

```bash
python parse_csv.py
```

---

## Entrada
- **Carpeta:** `data/`
- **Formato:** CSV exportado desde Pine Script Debugger de TradingView
- **Formato crudo de ejemplo:**
```
Date,Message
2017-10-12T00:00:00.000-00:00,";5,430;4,688.223;NaN;NaN;15.822;NaN;..."
```
- **Problemas que tiene el formato crudo:**
  - Separador de columnas es `;` dentro de las comillas
  - Miles separados con `,` (ej: `4,688.223` = cuatro mil seiscientos)
  - Valores faltantes como `NaN` (las EMAs necesitan N velas para calentarse)
  - Filas duplicadas al final (logs del `barstate.islast`)

---

## Procesamiento interno
1. Lee línea a línea cada archivo en `data/` que tenga `pine-logs` en el nombre
2. Filtra las líneas válidas (las que empiezan con `;`)
3. Elimina la `,` de miles en cada número
4. Convierte `NaN` a vacío (pandas los trata como `NaN` real)
5. Normaliza la fecha a formato `YYYY-MM-DDTHH:mm`
6. Elimina duplicados de la misma fecha (conserva el último)
7. Calcula y añade la columna `ratio_armonico = dist_10_55 / dist_55_200`

---

## Salida
- **Carpeta:** `results/`
- **Nombre:** mismo que el archivo de entrada + `_clean.csv`
- **Formato limpio de ejemplo:**
```
date,close,ema10,ema55,ema200,dist_p10,dist_p55,dist_p200,slope10,slope55,slope200,dist_10_55,dist_55_200,ratio_armonico
2018-04-18T00:00,8173.0,8564.23,8386.12,9650.44,-4.578,-2.539,-15.312,-6.98,-3.12,-0.89,-7.094,-13.096,0.5417
```

### Columnas del CSV limpio

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `date` | datetime | Fecha y hora de la vela `YYYY-MM-DDTHH:mm` |
| `close` | float | Precio de cierre |
| `ema10` | float | EMA 10 períodos |
| `ema55` | float | EMA 55 períodos |
| `ema200` | float | EMA 200 períodos |
| `dist_p10` | float % | `(close - ema10) / ema10 * 100` |
| `dist_p55` | float % | `(close - ema55) / ema55 * 100` |
| `dist_p200` | float % | `(close - ema200) / ema200 * 100` |
| `slope10` | float % | Pendiente EMA10 en 5 velas |
| `slope55` | float % | Pendiente EMA55 en 5 velas |
| `slope200` | float % | Pendiente EMA200 en 5 velas |
| `dist_10_55` | float % | `(ema10 - ema55) / ema55 * 100` |
| `dist_55_200` | float % | `(ema55 - ema200) / ema200 * 100` |
| `ratio_armonico` | float | `dist_10_55 / dist_55_200` (sin unidad) |

> **Nota:** Las primeras ~200 filas del 1D tendrán `NaN` en `ema200` — es normal,
> la EMA200 necesita 200 velas para calentarse. Los demás análisis filtran esas filas.

---

## Cómo saber que funcionó correctamente
El script imprime un reporte por cada archivo:
```
📂 Procesando: 1D-btc-pine-logs-....csv
  ✅ 3105 filas totales
  ✅ 2906 filas con EMA200 completa (93.6%)
  ✅ Rango: 2017-10-01T00:00  →  2026-03-31T00:00
  💾 Guardado en: results/..._clean.csv
```
Si ves `⚠️ Sin datos válidos` significa que el archivo tiene el formato nuevo del
Pine Script corregido — está bien, ese formato se procesa directamente con pandas.
