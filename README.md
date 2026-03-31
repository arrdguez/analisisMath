# 📊 Análisis de Magnitudes Armónicas

Herramienta para exportar, limpiar y analizar matemáticamente las relaciones
entre el precio y tres EMAs (10, 55, 200) en cualquier activo y timeframe.

> El análisis de los resultados y la interpretación final se hacen por separado,
> de forma agnóstica, con otra herramienta o IA. Este proyecto solo produce los datos.

---

## 🗂️ Estructura del proyecto

```
analisisMath/
│
├── code.js              ← Indicador Pine Script v6 (pegar en TradingView)
├── parse_csv.py         ← PASO 1: limpia los CSV crudos
├── explore.py           ← PASO 2: análisis exploratorio visual
├── fft_analysis.py      ← PASO 3: ciclos y frecuencias (FFT)
├── apoyo_stats.py       ← PASO 4: estadísticas de apoyos en EMAs
│
├── data/                ← CSV crudos exportados de TradingView  ← TÚ PONES AQUÍ
├── results/             ← Todo lo que generan los scripts       ← SCRIPTS ESCRIBEN AQUÍ
│   └── INVENTARIO.md    ← Qué es cada archivo en results/
│
├── doc/                 ← Documentación detallada de cada script
│   ├── script_parse_csv.md
│   ├── script_explore.md
│   ├── script_fft_analysis.md
│   └── script_apoyo_stats.md
│
└── img/                 ← Capturas de pantalla del patrón visual (referencia)
```

---

## ▶️ Flujo completo — paso a paso

### PASO 0 — Exportar datos desde TradingView
1. Abre TradingView y carga el indicador desde `code.js`
2. Abre el **Pine Script Debugger** (ícono bug, arriba derecha del editor)
3. Ve a la pestaña **Logs** → click en **Export logs**
4. Guarda el `.csv` descargado en la carpeta **`data/`**
5. Repite para cada timeframe (1D, 4H, 1H, etc.)

---

### PASO 1 — Limpiar los datos
```bash
python parse_csv.py
```
Lee todo lo que haya en `data/` y genera archivos `*_clean.csv` en `results/`.  
📖 Ver documentación completa: `doc/script_parse_csv.md`

---

### PASO 2 — Análisis exploratorio
```bash
python explore.py
```
Genera gráficas de las oscilaciones y estadísticas descriptivas.  
📖 Ver documentación completa: `doc/script_explore.md`

---

### PASO 3 — Ciclos y frecuencias
```bash
python fft_analysis.py
```
Detecta si las oscilaciones tienen ciclos repetibles medibles en velas.  
📖 Ver documentación completa: `doc/script_fft_analysis.md`

---

### PASO 4 — Estadísticas de apoyos
```bash
python apoyo_stats.py
```
Mide profundidad histórica de los apoyos en cada EMA y rebote posterior.  
📖 Ver documentación completa: `doc/script_apoyo_stats.md`

---

### Correr todo de una vez
```bash
python parse_csv.py && python explore.py && python fft_analysis.py && python apoyo_stats.py
```

---

## 📦 ¿Qué archivos genera cada script?

| Script | Archivos en `results/` |
|--------|----------------------|
| `parse_csv.py` | `*_clean.csv` (3 archivos, uno por timeframe) |
| `explore.py` | `explore_{TF}_distancias.png`, `explore_{TF}_ratio.png`, `explore_{TF}_stats.txt` |
| `fft_analysis.py` | `fft_{TF}_espectro.png`, `fft_{TF}_ciclos.txt` |
| `apoyo_stats.py` | `apoyo_{TF}_detalle.png`, `apoyo_{TF}_rebote.png`, `apoyo_{TF}_stats.txt` |

> Ver descripción completa de cada archivo: `results/INVENTARIO.md`

---

## 🟧 El indicador en TradingView — el cuadrito

Aparece en la **esquina superior derecha** del gráfico:

```
┌─────────────────┬──────────┐
│ Magnitud        │ Valor (%)│
├─────────────────┼──────────┤
│ Relación 10/55  │  -5.15%  │  ← Azul
│ Relación 55/200 │ -15.92%  │  ← Amarillo
│ Ratio Armónico  │   0.32   │  ← Naranja
└─────────────────┴──────────┘
```

| Fila | Fórmula | Qué dice |
|------|---------|---------|
| **Relación 10/55** | `(EMA10 - EMA55) / EMA55 × 100` | Positivo = EMA10 sobre EMA55 = alcista corto plazo |
| **Relación 55/200** | `(EMA55 - EMA200) / EMA200 × 100` | Positivo = EMA55 sobre EMA200 = alcista largo plazo |
| **Ratio Armónico** | `Relación10/55 ÷ Relación55/200` | ~0.3–0.6 = proporción normal. Negativo = estructura mixta |

---

## ⚙️ Requisitos

```bash
pip install pandas matplotlib scipy
```

---

## 📝 Estado del proyecto

| Tarea | Estado |
|-------|--------|
| Indicador Pine Script | ✅ |
| Export de datos limpio | ✅ |
| `parse_csv.py` | ✅ |
| `explore.py` | ✅ |
| `fft_analysis.py` | ✅ |
| `apoyo_stats.py` | ✅ |
| Documentación de scripts | ✅ |
| Interpretación final de resultados | ⬜ pendiente (análisis agnóstico externo) |
