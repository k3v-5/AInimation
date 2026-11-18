# Especificación Técnica: Fase 9 — Render & Export Pipeline

**Documento:** `spec/phase-9-render-export-pipeline.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/rendering/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 9** construye el motor de renderizado, composición de píxeles, planificación de fotogramas (*Frame Scheduling*), gestión de perfiles de exportación y codificación audiovisual determinista:

$$\text{Project} \longrightarrow \text{Render Graph (DAG)} \longrightarrow \text{Frame Scheduler} \longrightarrow \text{Compositor \& Color} \longrightarrow \text{Encoder} \longrightarrow \text{Output Video}$$

```
                          PROJECT
                             │
                             ↓
                      RENDER PLANNER
                             │
                             ↓
                    RENDER GRAPH (DAG)
                             │
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
     Video Nodes       Graphics Nodes      Audio Nodes
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ↓
                      FRAME SCHEDULER
                 (Progress & Incremental)
                             │
                             ↓
                      PIXEL COMPOSITOR
                 (Alpha Blending & Layers)
                             │
                             ↓
                       FRAME CACHE
                    (Deterministic Key)
                             │
                             ↓
                      VIDEO ENCODER
                 (Output Profiles & Specs)
                             │
                             ↓
                      RENDER VALIDATOR
                 (Duration, Codec, Bounds)
```

---

## 1. Perfiles de Exportación y Trabajos de Render (`OutputProfile`, `RenderJob`)

### 1.1. Perfiles Estándar (`OutputProfile`)
- **`youtube-1080p`:** $1920 \times 1080$, 30/60 fps, H.264, AAC, MP4.
- **`tiktok-1080x1920` / `shorts-1080x1920`:** $1080 \times 1920$ (9:16 vertical), 30 fps, H.264, AAC, MP4.
- **`master-prores`:** $3840 \times 2160$, ProRes 422 HQ / 4444, PCM, MOV.
- **`preview`:** $960 \times 540$ o $540 \times 960$ (50% draft scale), 30 fps.

### 1.2. Estados del Trabajo de Render (`RenderState` & `RenderProgress`)
- Estados: `queued`, `preparing`, `rendering`, `encoding`, `completed`, `failed`, `cancelled`.
- Fases: `preparing`, `loading-assets`, `evaluating`, `compositing`, `encoding`, `finalizing`.

---

## 2. Composición de Píxeles y Grafo de Render (`Compositor`, `RenderGraph`)

1. **Grafo de Render (DAG):**
   - Nodos de fuente, transformación, desenfoque (*blur*), máscaras, texto, gráficos vectoriales y mezcla.
   - Clave de caché determinista: $\text{Hash}(\text{nodeType}, \text{params}, \text{frame}, \text{rendererVersion})$.
2. **Compositor de Píxeles:**
   - Composición ordenada de capas de fondo a frente con mezcla Porter-Duff y modos de fusión (`normal`, `multiply`, `screen`, `overlay`, `add`, `darken`, `lighten`).
3. **Planificador de Fotogramas y Muestreo Subframe:**
   - Generador asíncrono determinista de fotogramas, cálculo de tiempo estimado (*ETA*) y acumulación de subframes para desenfoque de movimiento (*motion blur*).
4. **Validación Post-Render:**
   - Verificación de existencia de archivo, duración exacta, resolución y tasa de fotogramas frente al perfil objetivo.
