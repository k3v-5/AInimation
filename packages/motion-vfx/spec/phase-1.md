# Especificación Técnica: Fase 1 — Core Temporal del Motion Engine

**Documento:** `spec/phase-1.md`  
**Estado:** VIGENTE / CONGELADO  
**Versión de Esquema:** `0.1.0`

---

## 1. Objetivo de la Fase

Construir el núcleo matemático y temporal del motor de motion graphics.

Al finalizar esta fase, el motor debe ser capaz de representar y evaluar una composición animada:

```
Composition
    │
    ├── Layer
    │     ├── Property<number>
    │     │      └── Keyframes
    │     │
    │     ├── Property<Vector2>
    │     │      └── Keyframes
    │     │
    │     └── Property<...>
    │
    └── Layer
```

Y debe responder de forma determinista y pura a la pregunta:
**"¿Cuál es el estado exacto de esta composición en el segundo $t$?"**

```typescript
const state = composition.evaluate(2.37);
```

---

## 2. Límites de Alcance Estrictos

Esta fase **NO debe producir ni contener**:
- ❌ Video ni códecs
- ❌ Imágenes ni texturas raster
- ❌ Audio, espectrogramas ni transitorios
- ❌ Efectos visuales ni shaders
- ❌ Partículas ni dinámicas físicas
- ❌ Texto enriquecido ni fuentes tipográficas
- ❌ Renderizadores (Canvas, WebGL, Skia, FFmpeg)
- ❌ UI, GUI ni paneles
- ❌ Servidor MCP ni endpoints de red
- ❌ Integración específica con After Effects o Blender
- ❌ IA ni llamadas a LLMs
- ❌ Tracking ni visión por computador

Todo lo anterior pertenece a fases posteriores y no debe contaminar el Core.

---

## 3. Reglas y Principios Arquitectónicos

### Regla 1 — El Core es Renderer-Agnostic
El motor no depende de ningún entorno de renderizado ni de APIs del navegador (`window`, `document`) o de Node (`fs`, `child_process`). Es lógica computacional pura.

### Regla 2 — El tiempo se representa en segundos
- Tipo base: `type Time = number;`
- Expresado en segundos continuos (ej. `0`, `0.0166667`, `0.5`, `1.25`, `2.37`, `3.75`).
- No se permiten: `NaN`, `Infinity`, `-Infinity`, ni valores $< 0$ para duraciones o marcas de keyframes.
- El FPS sirve exclusivamente para conversiones `seconds ↔ frames`.

### Regla 3 — Todo lo animable es una Property<T>
No existen subsistemas independientes por propiedad (`OpacityAnimation`, `PositionAnimation`, etc.). Toda propiedad animable o estática es una instancia de `Property<T>`.

### Regla 4 — Los Keyframes son datos puros
Un `Keyframe<T>` es una estructura de datos inmutable que contiene únicamente: `time`, `value` y `easing` opcional. La lógica de búsqueda, cálculo de progreso e interpolación reside en `Property<T>`.

### Regla 5 — La Evaluación es determinista y produce Snapshots inmutables
- Múltiples llamadas a `composition.evaluate(t)` con el mismo proyecto e instante $t$ producen exactamente el mismo snapshot.
- Los snapshots devueltos son copias profundas/desacopladas inmutables; modificar un snapshot nunca muta el estado interno de la composición.

### Regla 6 — Extensibilidad Espacial en Keyframes
Aunque la Fase 1 se concentra en la interpolación temporal, la interfaz `Keyframe<T>` y el esquema de serialización admiten metadatos espaciales opcionales (`spatialIn`, `spatialOut`, `spatialInterpolation`) para garantizar compatibilidad hacia adelante con curvas de movimiento en 2D/3D sin romper contratos.

### Regla 7 — Generación Determinista de Identificadores
Cualquier ID generado automáticamente (cuando una `Composition` o `Layer` se instancia sin ID explícito) utiliza un generador determinista secuencial (`comp_1`, `layer_1`, etc.) reiniciable mediante `resetIdGenerators()`. No se utilizan UUIDs aleatorios ni `Math.random()`.

### Regla 8 — Garantía Estricta de Bordes en Easing e Interpolación
Todas las funciones de easing garantizan de forma exacta que $t \le 0 \implies 0$ y $t \ge 1 \implies 1$ para evitar fluctuaciones de punto flotante (ej. $1.00000000000002$) en aserciones de igualdad estricta. Igualmente, $\text{interpolate}(a, b, 0) \equiv a$ e $\text{interpolate}(a, b, 1) \equiv b$.

---

## 4. Criterios de Aceptación

1. **Core:** `Composition`, `Layer`, `Property<T>`, `Keyframe<T>`, `Timeline` implementados y operativos.
2. **Matemáticas e Interpolación:**
   - Interpolación de `number`, `Vector2`, `Vector3`.
   - Clamping del progreso de interpolación en $[0, 1]$.
   - Curvas de Easing puras: `linear`, `easeIn`, `easeOut`, `easeInOut`.
   - El easing pertenece al segmento iniciado por el keyframe anterior.
3. **Comportamiento Temporal:**
   - Evaluación antes del primer keyframe $\rightarrow$ devuelve valor del primer keyframe (hold).
   - Evaluación después del último keyframe $\rightarrow$ devuelve valor del último keyframe (hold).
   - Evaluación en un keyframe exacto $\rightarrow$ devuelve el valor del keyframe.
   - Evaluación entre dos keyframes $\rightarrow$ calcula progreso, aplica easing del keyframe previo e interpola.
   - Reemplazo automático al insertar un keyframe con timestamp duplicado.
   - Ordenamiento automático ascendente de keyframes independientemente del orden de inserción.
   - Estado de capa activo en $[ \text{startTime}, \text{endTime} )$.
4. **Serialización y Validación:**
   - `composition.toJSON()` genera JSON determinista con `schemaVersion: "0.1.0"`.
   - `Composition.fromJSON(json)` valida exhaustivamente la estructura y lanza errores tipados (`ValidationError`, `SerializationError`).
5. **Calidad y Robustez:**
   - TypeScript en modo `strict: true` sin `any` injustificado.
   - Suite completa de tests unitarios y de integración.
