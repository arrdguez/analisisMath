# 📂 Índice de Documentación — AnalisisMath

Este documento sirve como guía de navegación para todos los archivos de documentación del proyecto. Haz clic en los enlaces para acceder a cada sección.

---

## 📌 Documentos Principales
- **[Hoja de Ruta del Proyecto](PROYECTO_REFERENCIA.md)**: El plan maestro, hipótesis de trabajo y fases del proyecto.
- **[Manual de Interpretación de Resultados](COMO_LEER_RESULTADOS.md)**: Guía detallada para entender cada gráfica (Hurst, FFT, Hilbert, Fibonacci) y cada reporte generado en `results/`.
- **[Fundamentos Teóricos](TEORIA_REFERENCIAS.md)**: Referencias agnósticas de los métodos matemáticos (FFT, Hurst, Hilbert, correlación, etc.) con enlaces a Wikipedia y recursos externos.
- **[Notas de DeepSeek](fromDeepSeek.MD)**: Documentación técnica y sugerencias iniciales recibidas durante la exploración.

---

## 🛠️ Documentación de Scripts
Guía técnica de funcionamiento para cada script del proyecto:

1. **[Limpieza de Datos (parse_csv.py)](script_parse_csv.md)**: Cómo procesar los logs de TradingView.
2. **[Análisis Exploratorio (explore.py)](script_explore.md)**: Gráficas de distancias y percentiles.
3. **[Análisis de Ciclos (fft_analysis.py)](script_fft_analysis.md)**: Ciclos dominantes mediante Fourier.
4. **[Estadísticas de Apoyos (apoyo_stats.py)](script_apoyo_stats.md)**: Medición de rebotes y profundidad en EMAs.

---

## 📦 Otros Recursos
- **[Inventario de Resultados](../results/INVENTARIO.md)**: Qué es cada archivo generado en la carpeta `results/`.
- **[Reporte para IA](../results/REPORTE_MATEMATICO_IA.md)**: El reporte consolidado diseñado para ser procesado por una IA matemática (se genera al correr `main.py`).
---

## 🔮 Extensiones Futuras (Documentación)

El proyecto está funcionalmente completo, pero en la documentación se mencionan dos análisis matemáticos avanzados que podrían implementarse como extensiones:

- **Cadenas de Markov**: análisis de transiciones entre estados de apoyo.
- **Dimensión fractal**: estudio de autosimilaridad del patrón.

Estos métodos se describen brevemente en:
- [`COMO_LEER_RESULTADOS.md`](COMO_LEER_RESULTADOS.md) (sección "Extensiones Futuras")
- [`PROYECTO_REFERENCIA.md`](PROYECTO_REFERENCIA.md) (sección "Extensiones Matemáticas Futuras")
- [`TEORIA_REFERENCIAS.md`](TEORIA_REFERENCIAS.md) (recursos teóricos)

---

*Volver al [README principal](../README.md)*
