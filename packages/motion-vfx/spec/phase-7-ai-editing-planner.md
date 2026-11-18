# Especificación Técnica: Fase 7 — AI Editing Planner

**Documento:** `spec/phase-7-ai-editing-planner.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/ai-planner/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 7** establece el compilador y planificador editorial autónomo para transformar instrucciones de alto nivel y briefs creativos en un **Editing Plan IR** determinista:

$$\text{LLM} \longrightarrow \text{EditingPlan IR} \longrightarrow \text{Validator \& Repair} \longrightarrow \text{Deterministic Compiler} \longrightarrow \text{Project}$$

```
                NATURAL LANGUAGE / INTENT
                           │
                           ↓
                     CREATIVE BRIEF
             (Platform, Target Duration, Style)
                           │
                           ↓
                      AI PLANNER
             (Editorial Structure & Sections)
                           │
                           ↓
                    EDITING PLAN IR
      (Scenes, Shots, Captions, Graphics, Audio, Camera)
                           │
                           ↓
                  PLAN VALIDATOR & REPAIR
           (Time Bounds, Asset Refs, Constraints)
                           │
                           ↓
               DETERMINISTIC COMPILER
                           │
                           ↓
                     ENGINE PROJECT
                           │
                           ↓
                   AI CRITIC & REVISION
```

---

## 1. Modelo de Datos (`EditingPlan`, `CreativeBrief`, `StyleProfile`)

### 1.1. Brief Creativo y Plataformas
- **`Platform`:** `"youtube" | "youtube-shorts" | "tiktok" | "instagram-reels" | "instagram"`.
- **`CreativeBrief`:** `objective`, `platform`, `targetDuration`, `audience`, `styleId`, `constraints`.
- **`StyleProfile`:** Paleta de colores, tipografía, dinámica de movimiento, transiciones y componentes gráficos.

### 1.2. Estructura Editorial y Tomas
- **`EditorialSection`:** `type` (`hook`, `setup`, `main-point`, `example`, `escalation`, `payoff`, `cta`, `outro`), `start`, `end`, `energy: number [0, 1]`.
- **`ShotPlan`:** `id`, `assetId`, `purpose`, `duration`, `framing` (`wide`, `medium`, `close`, `POV`), `transition`.
- **`CaptionPlan`:** Estilo (`word-pop`, `karaoke`, `minimal`), segmentos con marcas de énfasis.
- **`GraphicsPlan`:** Elementos semánticos (`callout`, `statistic`, `badge`, `progress`, `highlight`).
- **`AudioPlan`:** Pistas de música de fondo, auto-ducking, efectos de sonido (SFX `whoosh`, `impact`, `click`) y sincronización con beats.

---

## 2. Validación, Reparación y Compilación Determinista

1. **`PlanValidator`:** Rechaza timestamps invertidos ($start > end$), activos no existentes y violaciones de restricciones.
2. **`PlanRepairEngine`:** Aplica correcciones deterministas (clamping de duraciones fuera de rango, asignación de transiciones por defecto).
3. **`EditingPlanCompiler`:** Compila el plan estructurado en un `Project` con `Timeline`, `Scene`, `Layer`, `Clip`, `AudioTrack`, `CaptionTrack` y `GraphicsElement`.
4. **`AICritic`:** Evalúa el ritmo (*pacing*), variedad visual (evitando repetición excesiva de encuadres) y presencia de llamadas a la acción (*CTA*).
