# Guía de Mejora: Análisis de Dinámica de Contacto (Pausado)

## Contexto
Este script (`contact_dynamics_analysis.py`) intentó capturar la intuición de "Beso vs Abrazo" (Contacto Transitorio vs Persistente).

## Hallazgos de la V1.1
1. **Hurst es inútil en ventanas cortas:** Da 0.5 siempre porque no hay suficientes datos en 5-15 velas.
2. **Velocidad de Llegada:** No predice la duración, pero en 1D/EMA55, impactos violentos suelen preceder a rupturas fuertes.
3. **Persistentes (Abrazos):** Son minoría (~3%), pero son los eventos con mayor colapso de energía.

## Ideas para la V2 (Futuro)
- **Sustituir Hurst por Ratio de Eficiencia (Kaufman):** Funciona mejor en pocas velas para medir direccionalidad.
- **Medir Varianza de la Distancia:** Un "Abrazo" es matemáticamente un colapso de la varianza durante el contacto.
- **Foco en EMA55 y EMA200:** La EMA10 tiene demasiado ruido para este análisis.
