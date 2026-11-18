# Especificación Técnica: Fase 12 — Tracking, Rotoscoping & Object-Aware Effects

**Documento:** `spec/phase-12-tracking-rotoscoping.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/tracking-rotoscopy/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 12** implementa el motor de seguimiento (*Tracking*), rotoscopia (*Rotoscoping*) y efectos basados en sujetos y objetos (*Object-Aware Effects*), permitiendo vincular gráficos, desenfoques y llamadas de atención a elementos visuales específicos mediante directivas semánticas de alto nivel:

$$\text{Semantic Directive} \longrightarrow \text{Target Resolver} \longrightarrow \text{Track Data \& RotoMask} \longrightarrow \text{Object-Aware Effects} \longrightarrow \text{Render Graph}$$

```
                          AI DIRECTIVE
                               │
                               ↓
                    SEMANTIC TARGET RESOLVER
                   ("main_person", "laptop")
                               │
                               ↓
                       TRACKING ENGINE
          ┌────────────────────┼────────────────────┐
          ↓                    ↓                    ↓
     Object Track          Face Track           RotoMask
    (Point/Bounds)       (Landmarks/Avoid)  (Cutout/Feather)
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ↓
                     OBJECT-AWARE EFFECTS
          ┌────────────────────┼────────────────────┐
          ↓                    ↓                    ↓
    Background Blur     Highlight Outline    Callout & Arrow
   (Subject Sharp)      (Neon Glow Edge)     (Tracking Anchor)
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ↓
                         RENDER GRAPH
```

---

## 1. Módulos y Capacidades Clave

### 1.1. Estructura y Procesamiento de Seguimiento (`TrackProcessor`)
- Abstracción de datos temporales `Track` con muestras `TrackSample` (posición, límites, rotación, escala, confianza).
- Suavizado adaptativo (*adaptive smoothing*) para eliminar vibraciones sin comprometer movimientos intencionales rápidos.
- Interpolación y extrapolación determinista entre fotogramas clave de tracking.

### 1.2. Vinculación a Objetos y Flechas Inteligentes (`TrackBindingEngine`)
- Vinculación de capas a objetos con desplazamiento relativo (*relative offset*).
- Cálculo automático de orientación, longitud y rotación de flechas y etiquetas (*smart callouts*).

### 1.3. Rotoscopia y Composición por Oclusión (`RotoMaskEngine`)
- Máscaras de recorte de sujeto (*subject cutout*) con desvanecimiento de borde (*feather*).
- Composición por oclusión para colocar gráficos y texto detrás de personas (*text behind person*).

### 1.4. Efectos Orientados a Objetos (`ObjectAwareEffectRegistry`)
- Presets: `background-blur`, `object-blur`, `subject-pop`, `object-focus`, `highlight-outline`.
