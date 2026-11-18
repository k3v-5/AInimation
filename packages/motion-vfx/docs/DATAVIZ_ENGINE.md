# Data Visualization Engine (Fase 5A — REQ-025)
## Motor Determinista de Visualización de Datos Editoriales

**Versión del Motor:** `v4.0.0-editorial-master`  
**Versión de Esquema DataVizIR:** `1.0.0`  
**Clasificación:** Production-Critical / Level 5 Production Certified / Determinista / Zero-Inference  
**Requerimientos Cubiertos:** REQ-025 (§1 a §134)

---

## 1. Propósito y Filosofía Arquitectónica

El **Data Visualization Engine** transforma datasets numéricos y cronológicos no estructurados en gráficos editoriales animados de alto impacto estético (*TIME Editorial / Investigative Poster Style*), representados como una Abstract Syntax Tree intermedia canónica (`DataVizIR`) y compilables de manera determinista a código ExtendScript JSX para Adobe After Effects.

### Principio Fundamental: Cero Inferencia en Compilador JSX
> *"El JSX no podrá contener decisiones editoriales, de layout ni de escala que no existan previamente en DataVizIR."*

El compilador de After Effects no recalcula posiciones, escalas, márgenes ni colores. Su única responsabilidad es materializar fielmente la AST `DataVizIR` ya validada matemáticamente.

```
RAW DATASET / JSON
       │
       ▼
1. DataInputValidator (Límites operacionales, unicidad de IDs, Zod)
       │
       ▼
2. DataNormalizationEngine (Escala [0.0, 1.0], precisión 4 decimales, -0 -> 0)
       │
       ▼
3. ScaleEngine & NumberFormatter (LinearScale, Nice Numbers, métricas K/M/B/T)
       │
       ▼
4. LayoutEngine & SafeZoneEngine (16:9 EBU Title Safe, 9:16 Social UI, 1:1)
       │
       ▼
5. LabelEngine & AxisEngine (Detección de colisiones, bloqueo si PRIMARY colisiona)
       │
       ▼
6. AnimationPlanner (Curvas cúbicas analíticas, cálculo de stagger sin jitter)
       │
       ▼
7. DataVizIRBuilder & Hasher (Ordenamiento determinista de claves, SHA-256 canónico)
       │
       ▼
8. DataVizValidator (Validación semántica y geométrica, métricas de ocupación)
       │
       ▼
9. AfterEffectsDataVizCompiler (ExtendScript JSX zero-inference, motion blur activo)
```

---

## 2. Garantías e Invariantes Matemáticas

1. **Normalización Numérica Canónica (`normalizeNumber`):**
   - Redondeo exacto a 4 decimales: `Number(val.toFixed(4))`.
   - Eliminación estricta de `-0`: convertido deterministamente a `+0`.
   - Rechazo de `NaN` e `Infinity` con `DatasetValidationError`.
2. **Tratamiento de Dominios Constantes (REQ-025 §15):**
   - Si $\min = \max$: el valor normalizado se fija exactamente en $0.50$ y se emite la advertencia `CONSTANT_DOMAIN`. No se producen divisiones por cero.
3. **Escala Logarítmica Bloqueada (REQ-025 §16):**
   - Cualquier solicitud de escala `LOG` arroja `UnsupportedScaleError` bloqueante.
4. **Cálculo de Nice Numbers:**
   - Subdivisión de ticks en múltiplos preferidos: $\{1, 2, 2.5, 5, 10\} \times 10^{\lfloor\log_{10}(\text{step})\rfloor}$.
5. **Formateo Numérico Aislado del SO:**
   - Sin dependencia de locales o configuraciones regionales del sistema operativo anfitrión.
   - Sufijos métricos estándar: `K` ($10^3$), `M` ($10^6$), `B` ($10^9$), `T` ($10^{12}$).
   - Porcentajes tratados limpiamente sin alterar valores enteros ($25 \to 25\%$, no $0.25\%$).
   - Sin inferir símbolos de moneda a menos que se declare explícitamente.

---

## 3. Tipos de Visualización Implementados

### 3.1 Animated Bar Chart (`AnimatedBarChartCompiler`)
- **Orientaciones:** `VERTICAL` y `HORIZONTAL`.
- **Eje Cero Real:** Ubicación explícita de `baseline = scale.map(0)`. Las barras positivas crecen hacia arriba; las negativas crecen hacia abajo.
- **Invariante de Separación:** `bar[i].right <= bar[i+1].left`.
- **Animación:** Crecimiento en escala con curva `EASE_OUT_CUBIC`, retardo progresivo determinista (`staggerSeconds`) y animación de conteo numérico sincronizado.

### 3.2 Trend Line Graph (`TrendLineGraphCompiler`)
- **Geometría:** Vértices mapeados y longitud de trazo calculada analíticamente mediante la suma de distancias euclidianas: $\sum \sqrt{\Delta x^2 + \Delta y^2}$.
- **Animación Write-On:** Revelado progresivo del trazo mediante la propiedad `PATH_PROGRESS`.
- **Key Points:** Detección automática de extremos (inicio, fin, mínimo, máximo y puntos con énfasis `PRIMARY`).
- **Aparición Sincronizada:** Los puntos y etiquetas se desvanecen gradualmente a medida que el trazo los alcanza.

### 3.3 Big Stat Card (`BigStatCardGenerator`)
- **Estilo TIME Editorial / Poster:**
  - Valor dominante en tipografía ultra-condensada (`Impact`, `Arial Black`, `Anton`).
  - Línea divisoria vectorial de acento en rojo carmesí `#FF1424` (grosor 4px).
  - Etiqueta secundaria en mayúsculas con interletraje positivo.
  - Formateo inteligente (ej. `1800000` $\to$ `1.8M`).
  - Compatibilidad completa con composiciones verticales 9:16 (ajuste tipográfico automático).

### 3.4 Chronology Timeline (`ChronologyTimelineGenerator`)
- **Normalización Temporal UTC:** Acepta años numéricos de 4 dígitos e identificadores de fecha ISO 8601 sin desfasaje por zona horaria local.
- **Invariante de Monotonía Espacial:**
  $$\text{fecha}(A) < \text{fecha}(B) \implies \text{posición}(A) \le \text{posición}(B)$$
- **Prevención de Colisiones:** Alternancia arriba/abajo de etiquetas y cálculo de radio destacado para eventos de importancia `PEAK` o `HIGH`.

---

## 4. Validación Semántica y Reporte (`DataVizValidator`)

Cada objeto `DataVizIR` es verificado exhaustivamente antes de compilarse:
- **Unicidad de IDs:** Comprobación estricta de identificadores no repetidos en elementos visuales.
- **Integridad Geométrica:** Verificación de finitud en todas las coordenadas y cálculo de cumplimiento de Safe Zone.
- **Contraste de Color WCAG 2.1:** Medición de luminancia relativa y reporte de alertas si el contraste de texto cae por debajo de 3.0:1.
- **Colisión de Etiquetas:** Advertencia en solapamientos regulares; **bloqueo estricto (`CRITICAL_LABEL_COLLISION`)** si la etiqueta solapada tiene énfasis `PRIMARY`.
- **Métricas:** Emisión de `occupiedAreaRatio`, `safeZoneCompliance`, `overlapCount` y `overflowCount`.

---

## 5. Compilador ExtendScript JSX de After Effects

Produce código JSX determinista:
- Nomenclatura ordenada: `[DTV] BAR 001`, `[DTV] VALUE 001`, `[DTV] LABEL 001`, `[DTV] AXIS`.
- Activación obligatoria de desenfoque de movimiento: `comp.motionBlur = true`.
- Transcripción directa de keyframes para escala, opacidad y propiedades de texto.
- Sandbox de seguridad: libre de llamadas a disco o evaluación de strings arbitrarios.

---

## 6. CLI y Comandos npm

- `npm run dataviz:validate -- --input=fixtures/dataviz/bar-chart-basic.json`: Valida un dataset y reporta problemas semánticos.
- `npm run dataviz:compile -- --input=fixtures/dataviz/bar-chart-basic.json`: Compila a `DataVizIR` y emite el script JSX final.
- `npm run dataviz:fixture`: Ejecuta la verificación de las 5 suites de fixtures estándar.
