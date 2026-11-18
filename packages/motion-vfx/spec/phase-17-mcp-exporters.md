# Especificación Técnica: Fase 17 — MCP Control Plane, Multi-Format Exporters & After Effects JSX Compiler

**Documento:** `spec/phase-17-mcp-exporters.md`  
**Estado:** VIGENTE / NORMATIVO  
**Versión de Esquema:** `v1.7.0`  
**Módulos Principales:** `src/mcp/`, `src/export/`

---

## 1. Propósito y Alcance

La **Fase 17** implementa el plano de control externo (**MCP Control Plane**) y la cadena de exportación multi-formato (**Multi-Format Exporters**) del motor audiovisual determinista (Fases 1–16).

### 1.1. Invariante Arquitectónica Fundamental
$$\text{LLM Intent} \xrightarrow{\text{Validated Tool Input}} \text{Application Orchestrator} \xrightarrow{\text{Canonical IR}} \text{Deterministic Evaluator / Exporter}$$

> **Regla de Oro:** MCP es una interfaz de control; la **IR Canónica** y el motor existente son la **única fuente de verdad**. Ninguna herramienta MCP ni exportador duplicará lógica audiovisual del core ni creará líneas de tiempo paralelas.

### 1.2. Alcance Explícito
- **Incluye:**
  - Modularización completa de `src/index.ts` hacia `src/mcp/`.
  - Herramientas MCP de alto nivel: `create_video_from_script`, `export_to_after_effects_jsx`, `get_timeline_preview_frame`, `apply_viral_caption_style`.
  - Recursos MCP declarativos (`capabilities://after-effects`, `capabilities://fcpxml`, `capabilities://edl`, `presets://captions`, `project://{projectId}`).
  - Identidad determinista desacoplada: `projectId` (identidad de briefing/contenido) y `revisionId` (versión incremental de modificaciones).
  - Compilador determinista unidireccional $\text{IR} \to \text{ExtendScript JSX}$ basado en AST tipado con escape seguro anti-inyección.
  - Exportador a Apple FCPXML (v1.9/v1.10) y CMX 3600 EDL con reporte honesto de características degradadas/lossy.
  - Conversión estandarizada de Timecode y manifiesto criptográfico SHA-256 sin contaminación de timestamps dinámicos.
- **NO Incluye (Reservado para fases posteriores):**
  - Descompilación inversa $\text{JSX} \to \text{IR}$ (ExtendScript AST parsing).
  - Renderers paralelos en formato SVG independiente (el preview es un adaptador directo de `Evaluate(t)`).

---

## 2. Identidad del Proyecto y Revisiones

### 2.1. Fórmula de Identidad de Proyecto (`projectId`)
$$\text{projectId} = \text{SHA-256}(\text{canonical}(\text{script} + \text{styleId} + \text{aspectRatio} + \text{durationTarget} + \text{fps} + \text{seed} + \text{engineVersion}))_{0..16}$$

### 2.2. Identidad de Revisión (`revisionId`)
- Al crear el proyecto: `revisionId = "rev_1"`.
- Al aplicar una modificación o estilo (ej. `apply_viral_caption_style`): `revisionId = "rev_2"`, preservando el `projectId` base.

---

## 3. Matriz de Capacidades y Políticas de Exportación

### 3.1. Estados de Capacidad (`CapabilityStatus`)
```typescript
export type CapabilityStatus = "exact" | "approximate" | "lossy" | "unsupported";
```
- **`exact`**: La característica se mapea de forma nativa e idéntica en el formato destino.
- **`approximate`**: La característica se adapta mediante un mecanismo cercano (ej. easing Bezier complejo convertido a aproximación cúbica `KeyframeEase`).
- **`lossy`**: La característica se simplifica perdiendo información (ej. animación kinetic word-by-word exportada como subtítulo estático en EDL).
- **`unsupported`**: La característica no tiene representación en el formato destino (ej. efectos procedurales en EDL).

### 3.2. Política de Modo Estricto (`strict`)
- Si `strict === true`: Cualquier característica con estado `"approximate"`, `"lossy"` o `"unsupported"` genera un `ExportCapabilityError` impidiendo la exportación.
- Si `strict === false`: La exportación continúa, emitiendo un `ExportReport` con diagnósticos estructurados.

---

## 4. Matriz de Capacidades por Formato

| Concepto IR | After Effects JSX | Apple FCPXML | CMX 3600 EDL | Observaciones |
|---|---|---|---|---|
| **Composition / Sequence** | Exact | Exact | Exact | Ancho, alto, fps, duración, timebase |
| **Video Clips / Tracks** | Exact | Exact | Exact | In/Out points, pistas secuenciales |
| **Audio Clips / Levels** | Exact | Exact | Lossy / Exact | Volumen, canales de audio |
| **Text Layers / Captions** | Exact / Aprox | Exact / Aprox | Lossy / Unsupported | EDL no soporta texto formateado |
| **Transforms (Pos, Scale, Rot)**| Exact | Exact | Unsupported | EDL solo representa cortes de EDL |
| **Keyframes / Easing** | Exact / Aprox | Approximate | Unsupported | Curvas Bezier e interpolación |
| **Effects (Blur, Shadow, Glow)** | Exact / Aprox | Approximate | Unsupported | Mapeo de Effect Parade |
| **Bezier Masks** | Exact | Approximate | Unsupported | Vértices y tangentes |
| **Transitions (Cut, Dissolve)** | Exact | Exact | Exact | Cuts y Dissolves CMX |
| **Expressions** | Exact | Unsupported | Unsupported | ExtendScript eval seguro |

---

## 5. Seguridad: Prevención de Inyecciones y Path Traversal

1. **Compilador JSX Basado en AST (`JSXSerializer`):**
   - Prohibida la interpolación libre de texto `${userInput}`.
   - Todo nodo literal pasa por `escapeJSXString()` y validación numérica finita (`isFiniteNumber`).
2. **Validación de Rutas (Sandbox Path Safety):**
   - Verificación de rutas contra traversal (`../`, `..\`, `%2e%2e`).
   - Restricción de escritura a directorios permitidos (`outputDir`).
   - Prohibición estricta de extensiones ejecutables del SO (`.exe`, `.bat`, `.cmd`, `.sh`, `.ps1`).
3. **Límites de Recursos (`RESOURCE_LIMIT_EXCEEDED`):**
   - Máximo de capas por proyecto: 5,000.
   - Máximo de keyframes por propiedad: 20,000.
   - Máximo tamaño de script de entrada: 250,000 caracteres.
   - Máximo de duración: 7,200 segundos (2 horas).

---

## 6. Timecode y Manifiesto Determinista

### 6.1. Conversión de Timecode
Conversión pura sin pérdida para 24, 25, 29.97 (DF/NDF), 30, 50, 59.94 y 60 fps:
$$f = \lfloor t \cdot \text{fps} + 0.5 \rfloor$$
$$\text{Timecode} = \text{format}(\text{HH}:\text{MM}:\text{SS}:\text{FF})$$

### 6.2. Hash de Exportación Reproducible
$$\text{Hash}_{\text{export}} = \text{SHA-256}(\text{CanonicalIR} + \text{ExporterVersion} + \text{ExportConfig})$$
Excluye marcas de tiempo de generación y variables volátiles del host.
