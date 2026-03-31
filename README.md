# Analisis de Magnitudes Armonicas

Herramienta para exportar, limpiar y analizar matematicamente las relaciones
entre el precio y tres EMAs (10, 55, 200) en cualquier activo y timeframe.

> El analisis de los resultados y la interpretacion final se hacen por separado,
> de forma agnostica, con otra herramienta o IA. Este proyecto solo produce los datos.

---

## Estructura del proyecto

```
analisisMath/
│
├── main.py              <- PUNTO DE ENTRADA UNICO (empieza aqui)
├── code.js              <- Indicador Pine Script v6 (pegar en TradingView)
│
├── parse_csv.py         <- limpia CSV crudos de TradingView
├── explore.py           <- estadisticas y graficas de oscilaciones
├── fft_analysis.py      <- ciclos dominantes por Fourier
├── apoyo_stats.py       <- profundidad y rebote de apoyos en EMAs
├── hurst.py             <- exponente de Hurst (memoria de la serie)
├── hilbert_analysis.py  <- envolvente y periodo instantaneo
├── fibonacci_analysis.py-> ratios de tiempo y amplitud vs Fibonacci
├── plot_style.py        <- paleta de colores compartida (no se corre directamente)
│
├── data/                <- TU PONES AQUI los CSV crudos de TradingView
├── results/             <- LOS SCRIPTS ESCRIBEN AQUI todos los resultados
│   └── INVENTARIO.md   <- que es cada archivo en results/
│
├── doc/                 <- documentacion detallada
│   ├── COMO_LEER_RESULTADOS.md  <- como interpretar cada grafica y numero
│   ├── PROYECTO_REFERENCIA.md   <- hoja de ruta e hipotesis del proyecto
│   ├── script_parse_csv.md
│   ├── script_explore.md
│   ├── script_fft_analysis.md
│   └── script_apoyo_stats.md
│
└── img/                 <- capturas de pantalla del patron visual (referencia)
```

---

## PASO 0 — Exportar datos desde TradingView

1. Abre TradingView y carga el indicador desde `code.js`
2. Abre el **Pine Script Debugger** (icono de bug, arriba derecha del editor)
3. Ve a la pestaña **Logs** → click en **Export logs**
4. Guarda el `.csv` descargado en la carpeta `data/`
5. Repite para cada timeframe que quieras analizar (1D, 4H, 1H, etc.)

---

## Uso de `main.py` — el punto de entrada unico

`main.py` orquesta toda la cadena. No tienes que recordar el orden de los scripts
ni qué archivos tiene cada uno. Le dices qué quieres y él se encarga.

### Caso mas comun: correr todo

```bash
python main.py
```

Busca automaticamente todos los CSV en `data/`, detecta su formato,
los limpia si son crudos, y corre los 7 analisis en orden.

---

### Pasar un archivo especifico

```bash
python main.py --file "data/1D-btc-pine-logs-....csv"
```

Puedes pasar uno o varios archivos:

```bash
python main.py --file "data/archivo1.csv" "data/archivo2.csv"
```

---

### Correr solo algunos pasos

```bash
python main.py --pasos parse explore fft
```

Pasos disponibles (en este orden):

| Paso | Que hace |
|------|---------|
| `parse` | Limpia los CSV crudos de TradingView → `results/*_clean.csv` |
| `explore` | Estadisticas descriptivas y graficas de oscilaciones |
| `fft` | Ciclos dominantes por Fourier |
| `apoyos` | Profundidad y rebote de apoyos en cada EMA |
| `hurst` | Exponente de Hurst — memoria de la serie |
| `hilbert` | Envolvente y periodo instantaneo |
| `fibonacci` | Ratios de tiempo y amplitud vs niveles Fibonacci |

Puedes combinarlos como quieras:

```bash
# Solo limpiar datos:
python main.py --pasos parse

# Solo analisis matematicos (si ya tienes los _clean.csv):
python main.py --pasos hurst hilbert fibonacci

# Saltarte el parse y hacer todo lo demas:
python main.py --pasos explore fft apoyos hurst hilbert fibonacci
```

---

### Combinando archivo especifico con pasos especificos

```bash
python main.py --file "data/mi_archivo.csv" --pasos parse explore
```

---

### Ver la ayuda

```bash
python main.py --ayuda
```

---

### Lo que hace automaticamente sin que le digas nada

- **Detecta el formato** de cada CSV:
  - `[crudo]` → CSV directo de TradingView con `;` en Message → lo manda al `parse`
  - `[limpio]` → ya fue procesado por `parse_csv.py` → lo manda directo al analisis
  - `[ERROR]` → formato desconocido → te dice exactamente que esta mal y como arreglarlo

- **Si no hay archivos en `data/`** → te dice donde descargarlos y como

- **Si pides analisis sin tener `_clean.csv`** → te dice que corras `parse` primero

- **Si un paso falla** → avisa el error y continua con el siguiente paso

- **Al final** resume cuantas graficas y reportes se generaron

---

### Ejemplo de salida tipica

```
============================================================
  Analisis de Magnitudes Armonicas
============================================================
  Pasos: parse, explore, fft, apoyos, hurst, hilbert, fibonacci

  Archivos encontrados en data/:
    [OK] 1D-btc-pine-logs-....csv  [crudo]
    [OK] 1h-btc-pine-logs-....csv  [crudo]
    [OK] 4h-btc-pine-logs-....csv  [crudo]

------------------------------------------------------------
  PASO: parse  (3 archivos)
------------------------------------------------------------
  [>] Procesando: 1D-btc-pine-logs-....csv
  [OK] 3105 filas | 2906 con EMA200 (93.6%)
  [OK] Rango: 2017-10-01T00:00 -> 2026-03-31T00:00
  [>>] results/1D-btc-pine-logs-...._clean.csv
  ...

------------------------------------------------------------
  PASO 2: explore  ->  Analisis exploratorio visual
------------------------------------------------------------
  ...

============================================================
  COMPLETADO
  Resultados en: C:\...\analisisMath\results
  30 graficas  |  18 reportes de texto
============================================================
```

---

## O correr cada script directamente (sin main.py)

```bash
python parse_csv.py          # siempre primero
python explore.py
python fft_analysis.py
python apoyo_stats.py
python hurst.py
python hilbert_analysis.py
python fibonacci_analysis.py
```

---

## Que archivos genera cada script

| Script | Archivos en `results/` |
|--------|----------------------|
| `parse_csv.py` | `*_clean.csv` |
| `explore.py` | `explore_{TF}_distancias.png`, `explore_{TF}_ratio.png`, `explore_{TF}_stats.txt` |
| `fft_analysis.py` | `fft_{TF}_espectro.png`, `fft_{TF}_ciclos.txt` |
| `apoyo_stats.py` | `apoyo_{TF}_detalle.png`, `apoyo_{TF}_rebote.png`, `apoyo_{TF}_stats.txt` |
| `hurst.py` | `hurst_{TF}_rs.png`, `hurst_{TF}_valores.txt` |
| `hilbert_analysis.py` | `hilbert_{TF}_envolvente.png`, `hilbert_{TF}_frecuencia.png`, `hilbert_{TF}_resumen.txt` |
| `fibonacci_analysis.py` | `fibonacci_{TF}_tiempos.png`, `fibonacci_{TF}_amplitudes.png`, `fibonacci_{TF}_stats.txt` |

`{TF}` = timeframe del archivo: `1D`, `4H` o `1H`

> Ver descripcion completa de cada archivo: `results/INVENTARIO.md`
> Ver como interpretar cada grafica y numero: `doc/COMO_LEER_RESULTADOS.md`

---

## El indicador en TradingView — el cuadrito

Aparece en la esquina superior derecha del grafico:

```
+-----------------+----------+
| Magnitud        | Valor (%)| 
+-----------------+----------+
| Relacion 10/55  |  -5.15%  |  <- Azul
| Relacion 55/200 | -15.92%  |  <- Amarillo
| Ratio Armonico  |   0.32   |  <- Naranja
+-----------------+----------+
```

| Fila | Formula | Que dice |
|------|---------|---------|
| **Relacion 10/55** | `(EMA10 - EMA55) / EMA55 x 100` | Positivo = EMA10 sobre EMA55 |
| **Relacion 55/200** | `(EMA55 - EMA200) / EMA200 x 100` | Positivo = EMA55 sobre EMA200 |
| **Ratio Armonico** | `Relacion10/55 / Relacion55/200` | ~0.3-0.6 = proporcion normal. Negativo = estructura mixta |

---

## Requisitos

```bash
pip install pandas matplotlib scipy
```

---

## Estado del proyecto

| Tarea | Estado |
|-------|--------|
| Indicador Pine Script | OK |
| Export de datos limpio | OK |
| `main.py` — punto de entrada unico | OK |
| `parse_csv.py` | OK |
| `explore.py` | OK |
| `fft_analysis.py` | OK |
| `apoyo_stats.py` | OK |
| `hurst.py` | OK |
| `hilbert_analysis.py` | OK |
| `fibonacci_analysis.py` | OK |
| Documentacion de scripts | OK |
| Interpretacion final de resultados | pendiente — analisis agnostico externo |
