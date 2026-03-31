# 📄 fft_analysis.py — Análisis de ciclos (FFT)

## ¿Qué hace?
Aplica la **Transformada Rápida de Fourier (FFT)** a las series de distancias
para detectar si las oscilaciones tienen **ciclos repetibles** con una duración
medible en velas. Si el patrón visual es real, deberían aparecer picos de
frecuencia claros en el espectro.

**No predice. Mide si hay estructura periódica en los datos.**

---

## Cuándo correrlo
Después de `explore.py`. Es el segundo nivel de análisis.

```bash
python fft_analysis.py
```

---

## Entrada
- **Carpeta:** `results/`
- **Archivos:** todos los `*_clean.csv`
- **Variables analizadas:** `dist_p10`, `dist_p55`, `dist_p200`, `dist_10_55`, `dist_55_200`

---

## Procesamiento interno
1. Carga cada serie y quita la tendencia lineal (para que la FFT no se contamine con el drift de largo plazo)
2. Aplica ventana de **Hanning** para reducir el "spectral leakage" (artefactos del borde)
3. Calcula la FFT y convierte las frecuencias a **duración en velas** (`1 / frecuencia`)
4. Identifica los **top 5 picos de potencia** por señal
5. Calcula qué porcentaje de la energía total representa cada ciclo

---

## Salida — archivos generados en `results/`

### Por cada timeframe (1D, 4H, 1H):

| Archivo | Tipo | Contenido |
|---------|------|-----------|
| `fft_{TF}_espectro.png` | Imagen | Espectro de potencia en escala logarítmica. Los picos marcados con líneas blancas son los ciclos dominantes. El eje X es "duración del ciclo en velas", el eje Y es potencia |
| `fft_{TF}_ciclos.txt` | Texto | Top 5 ciclos dominantes por variable, con su duración en velas y % de energía que representan |

---

## Cómo interpretar los resultados

### `fft_{TF}_espectro.png`
- **Pico pronunciado = ciclo real** → hay algo que se repite con esa duración
- **Espectro plano = ruido** → no hay estructura periódica clara
- El **eje X está en escala logarítmica** para ver bien tanto los ciclos cortos como los largos
- Los números sobre cada pico muestran `{N}v` (N velas) y `{%}` de la energía

### `fft_{TF}_ciclos.txt`
```
dist_p55:
  #1  969 velas  (11.21% de la energía)   ← ciclo dominante
  #2  1453 velas  (9.37% de la energía)
  #3  363 velas  (4.99% de la energía)
```
**Cómo leer los números:**
- `969 velas en 1D` = 969 días ≈ **2.7 años**
- `1453 velas en 1D` = 1453 días ≈ **4 años** (ciclo de halving de Bitcoin)
- `39 velas en 1D` = 39 días ≈ **ciclo mensual-bimestral**
- `969 velas en 4H` = 969 × 4h ≈ **161 días** ≈ 5 meses

**Para convertir velas a tiempo:**

| Timeframe | × velas = días |
|-----------|---------------|
| 1D | velas × 1 |
| 4H | velas × 0.167 (÷6) |
| 1H | velas × 0.042 (÷24) |

### ¿Qué % de energía es significativo?
- **> 10%** → ciclo muy dominante, estructura fuerte
- **5–10%** → ciclo relevante
- **< 5%** → posible ruido, tomar con cautela

### Señal de alerta: si los ciclos del mismo fenómeno coinciden en 1D, 4H y 1H
al convertirlos a días → **el patrón es multi-timeframe y robusto**.
