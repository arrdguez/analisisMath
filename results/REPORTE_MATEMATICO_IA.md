# 📊 REPORTE MAESTRO: Análisis de Magnitudes Armónicas (BTC/USD)

## 1. Contexto y Antecedentes
Este reporte contiene el análisis matemático de las relaciones entre el precio de Bitcoin y tres Medias Móviles Exponenciales (EMAs) de 10, 55 y 200 períodos.
- **Fuente:** Logs de Pine Script v6 (TradingView).
- **Variables de estudio:** Distancias porcentuales del precio a cada EMA (`dist_p10`, `dist_p55`, `dist_p200`) y distancias entre EMAs (`dist_10_55`, `dist_55_200`).
- **Objetivo:** Detectar constantes y magnitudes recurrentes para formalizar el patrón visual en un script algorítmico.

## 2. Metodologías Aplicadas
| Análisis | Qué mide | Por qué es relevante |
|----------|----------|----------------------|
| **FFT (Fourier)** | Ciclos dominantes | Identifica si las oscilaciones tienen una periodicidad fija (velas). |
| **Hurst** | Memoria (Persistencia) | H > 0.5 indica que la serie tiene memoria y tiende a seguir su tendencia. |
| **Hilbert** | Amplitud/Periodo inst. | Muestra cómo cambia la 'fuerza' y la velocidad del ciclo en el tiempo. |
| **Fibonacci** | Ratios armónicos | Busca si los retrocesos y tiempos coinciden con la proporción áurea. |
| **Apoyos** | Profundidad de rebote | Mide cuánto 'perfora' el precio la EMA antes de rebotar. |
| **Correlación** | Sincronía entre EMAs | Determina si las distancias entre EMAs se mueven juntas o con desfase. |
| **Escala** | Relaciones entre rangos | Verifica si las correcciones guardan proporciones matemáticas constantes. |
| **Comparación** | Consistencia multi-timeframe | Evalúa si los patrones se mantienen en diferentes escalas temporales. |

## 3. Resultados Numéricos Consolidados

### 🕒 Timeframe: 1D

*Sin datos de Stats para 1D*

*Sin datos de Ciclos para 1D*

*Sin datos de Apoyos para 1D*

*Sin datos de Hurst para 1D*

*Sin datos de Hilbert para 1D*

*Sin datos de Fib para 1D*

*Sin datos de Correlación para 1D*

*Sin datos de Escala para 1D*

### 🕒 Timeframe: 4H

*Sin datos de Stats para 4H*

*Sin datos de Ciclos para 4H*

*Sin datos de Apoyos para 4H*

*Sin datos de Hurst para 4H*

*Sin datos de Hilbert para 4H*

*Sin datos de Fib para 4H*

*Sin datos de Correlación para 4H*

*Sin datos de Escala para 4H*

### 🕒 Timeframe: 1H

*Sin datos de Stats para 1H*

*Sin datos de Ciclos para 1H*

*Sin datos de Apoyos para 1H*

*Sin datos de Hurst para 1H*

*Sin datos de Hilbert para 1H*

*Sin datos de Fib para 1H*

*Sin datos de Correlación para 1H*

*Sin datos de Escala para 1H*

---
## 🤖 INSTRUCCIÓN PARA IA (PROMPT)
> **Copia y pega el siguiente texto en tu chat con IA:**

```text
Actúa como una IA experta en análisis cuantitativo, procesamiento de señales y trading algorítmico.
He realizado una serie de análisis matemáticos (Fourier, Hurst, Hilbert, Fibonacci, correlación, escala y comparación entre timeframes) sobre las distancias del precio de BTC a sus EMAs de 10, 55 y 200 períodos en diferentes timeframes (1D, 4H, 1H).

Basándote en los DATOS NUMÉRICOS proporcionados arriba en el reporte:
1. Identifica las MAGNITUDES RECURRENTES de las correcciones (¿a qué distancia típica en % rebotan los apoyos en cada EMA?).
2. Detecta si existe una RELACIÓN DE ESCALA constante entre los timeframes (¿se repiten los mismos ratios?).
3. Determina si el Exponente de Hurst y la Transformada de Hilbert confirman que el sistema es persistente y tiene ciclos estables.
4. Concluye con un SET DE PARÁMETROS sugeridos (umbrales de entrada, filtros de tendencia y duraciones de ciclo) para implementar un indicador de 'Magnitudes Armónicas' en Pine Script v6 que detecte zonas de alta probabilidad de rebote.
```