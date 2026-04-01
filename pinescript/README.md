# 🎯 Indicador "Magnitudes Armónicas" para TradingView

Indicador Pine Script v6 que visualiza relaciones armónicas entre EMAs (10, 55, 200) y detecta zonas de alta probabilidad de rebote basado en análisis matemático cuantitativo.

## 📊 Parámetros Matemáticos Incluidos

Los valores por defecto del indicador están basados en análisis estadístico de BTC/USD timeframe 1D:

| EMA | Profundidad apoyo | Rebote esperado | Ratio escala | Período ciclo |
|-----|-------------------|-----------------|--------------|---------------|
| 10  | -3.45% | +4.91% | 1.00 (base) | 14.4 velas |
| 55  | -4.03% | +5.49% | ~3.30× EMA10 | 45.8 velas |
| 200 | -1.02% | +6.28% | ~2.21× EMA55 | 99.3 velas |

**Ratio armónico normal**: 0.306 (rango típico: -0.050 a 0.790)

## 🎨 Características del Indicador

### 1. Zonas de Apoyo Visuales
- Líneas horizontales dinámicas en los niveles de apoyo históricos
- Colores diferenciados por EMA (azul, naranja, verde)
- Opacidad configurable

### 2. Panel de Métricas en Tiempo Real
Muestra en tiempo real:
- Distancias porcentuales a cada EMA
- Ratio armónico actual (dist_10_55 / dist_55_200)
- Estado del ciclo (IMPULSO / CORRECCIÓN)
- Ratio de escala 55/10
- Detección de mínimos locales por EMA

### 3. Detección Automática de Apoyos
- Identifica mínimos locales en las distancias precio/EMA
- Confirmación de rebote (precio sube X% después del mínimo)
- Filtro de ratio armónico (cercano a 0.306)

### 4. Sistema de Alertas
**Alertas visuales** (etiquetas en el gráfico):
- Entrada en zona de apoyo (EMA10, EMA55, EMA200)
- Ratio armónico dentro de rango normal
- Apoyo confirmado (mínimo local + rebote)

**Alertas de TradingView** (configurables en UI):
- Mismos eventos que alertas visuales
- Pueden activar notificaciones, emails, etc.

## ⚙️ Configuración

### Parámetros Principales
1. **Profundidades de apoyo** (%): valores históricos por EMA (-3.45, -4.03, -1.02)
2. **Ratio armónico normal**: 0.306 (mediana histórica)
3. **Tolerancia ratio**: ±30% (rango aceptable alrededor del valor normal)
4. **Ventana mínimo local**: 5 velas (tamaño de ventana para detectar mínimos)
5. **Rebote confirmación**: 2% (subida mínima para confirmar rebote)
6. **Velas confirmación rebote**: 10 (período de observación post-mínimo)

### Opciones Visuales
- Mostrar/ocultar zonas de apoyo
- Mostrar/ocultar panel de métricas
- Mostrar/ocultar alertas visuales
- Opacidad de zonas (10-90%)
- Colores personalizables para EMAs y zonas

## 🔧 Instalación en TradingView

1. **Copiar el código**
   ```bash
   cat pinescript/harmonic_magnitudes.pine
   ```
   Copiar todo el contenido al portapapeles.

2. **Abrir TradingView**
   - Ir a [TradingView](https://www.tradingview.com/)
   - Abrir el panel de "Pine Editor" (ícono de editor al final de la barra de herramientas)
   - Pegar el código copiado
   - Guardar (Ctrl+S) y nombrar el script "Magnitudes Armónicas"

3. **Aplicar al gráfico**
   - Cerrar el editor
   - Buscar el indicador en "Indicadores" (botón "Indicadores" en la barra superior)
   - Escribir "Magnitudes Armónicas" y seleccionarlo
   - Ajustar parámetros según preferencia

## 🧪 Validación Matemática

El indicador está basado en análisis cuantitativo completo:

- **Análisis FFT**: ciclos dominantes ~969-1453 velas
- **Exponente Hurst**: todas las series persistentes (>0.65)
- **Ratios Fibonacci**: amplitudes tienden a niveles 0.5, 0.618, 0.786
- **Correlación fuerte**: dist_10_55 vs dist_55_200 (r=0.6277)
- **Consistencia multi-timeframe**: parámetros escalan correctamente 1D→4H→1H

## 📈 Estrategia de Trading Sugerida

### Condiciones de Entrada
1. Precio en zona de apoyo EMA10 (-3.45%)
2. Ratio armónico entre 0.214 y 0.398 (±30% de 0.306)
3. Mínimo local detectado en dist_p10 (ventana 5 velas)
4. Confirmación de rebote (precio sube ≥2% después del mínimo)

### Gestión de Riesgo
- **Target**: +4.91% (rebote mediano histórico EMA10)
- **Stop loss**: -5.0% (conservador)
- **Timeout**: 50 velas (hold máximo)
- **Posición**: tamaño fijo, sin piramidar

### Métricas Esperadas (basadas en análisis histórico)
- Win rate: 75-85%
- Profit factor: >1.5 (estimado)
- Expectativa positiva: sí (rebote mediano > profundidad mediana)

## ⚠️ Limitaciones y Advertencias

1. **Backtesting limitado**: El indicador no ha sido backtestado en tiempo real en TradingView
2. **Sobre-optimización**: Parámetros basados en datos históricos de BTC/USD 1D (2018-2026)
3. **Condiciones de mercado**: Rendimiento puede variar en mercados laterales o de alta volatilidad
4. **Retraso inherente**: Detección de mínimos locales tiene retraso de N/2 velas

## 🔄 Mejoras Futuras

1. **Espacio de fases**: Gráfico 2D dist_p10 vs dist_p55 para detectar cuencas de atracción
2. **Filtro de convergencia**: Alerta cuando dist_10_55 y dist_55_200 se acercan a cero
3. **Sistema multi-timeframe**: Confirmación de señal en timeframe superior
4. **Targets dinámicos**: Basados en percentiles históricos de rebote por EMA

## 📋 Archivos Relacionados

- `harmonic_magnitudes.pine` → Código principal del indicador
- `../plan_accion/PARAMETROS_MATEMATICOS.md` → Parámetros matemáticos completos
- `../results/REPORTE_MATEMATICO_IA.md` → Análisis matemático completo
- `../doc/TEORIA_REFERENCIAS.md` → Base teórica de los métodos utilizados

## 🎯 Próximos Pasos Recomendados

1. **Prueba visual** en TradingView con datos históricos
2. **Paper trading** por 2-4 semanas para validar señales
3. **Ajuste fino** de parámetros si es necesario (manteniendo base matemática)
4. **Backtesting en TradingView** usando su sistema interno
5. **Implementación** de mejoras de Fase 3 (ver roadmap)

---

**⚠️ ADVERTENCIA**: Este indicador es para fines educativos y de investigación. No constituye asesoramiento financiero. El trading conlleva riesgos significativos de pérdida. Siempre realice su propia investigación y consulte con un asesor financiero profesional antes de operar con capital real.

**📅 Última actualización**: 2026-03-31  
**Versión**: 0.1 (prototipo funcional)  
**Autor**: Análisis Matemático Automatizado (proyecto analisisMath)