# Especificación Técnica: Fase 11 — Advanced Motion Graphics Engine

**Documento:** `spec/phase-11-advanced-motion-graphics.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/motion-graphics/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 11** construye el motor avanzado de gráficos en movimiento (*Motion Graphics Engine*), permitiendo animaciones cinéticas de nivel profesional ("viral/wow") mediante tipografía cinética por carácter/palabra, dinámicas de cámara 2D deterministas, emisores de partículas, macros cinéticos de alto nivel y presupuestos de movimiento (*Motion Budget*):

$$\text{Editing Directive} \longrightarrow \text{Motion Compiler} \longrightarrow \{\text{Kinetic Type, Shapes, Camera, Particles, Macros}\} \longrightarrow \text{Motion Graph} \longrightarrow \text{Render Graph}$$

```
                          AI DIRECTIVE / USER
                                  │
                                  ↓
                           MOTION COMPILER
                                  │
          ┌───────────────┬───────┴───────┬───────────────┐
          ↓               ↓               ↓               ↓
    KINETIC TYPE    MOTION MACROS     2D CAMERA       PARTICLES
   (Stagger/Glow)  (Hook, Statistic) (Seeded Shake) (Confetti/Spark)
          │               │               │               │
          └───────────────┼───────────────┴───────────────┘
                          ↓
                MOTION BUDGET & COMPLEXITY
              (Scoring, Clamping & Priorities)
                          ↓
                AUDIO-REACTIVE BINDING
               (Beat Punch & Glow Pulse)
                          ↓
                    MOTION GRAPH
```

---

## 1. Módulos y Capacidades Clave

### 1.1. Tipografía Cinética (`KineticTypographyEngine`)
- Segmentación por palabras (`word`) y caracteres (`character`).
- Distribución de desfases (*staggers*) deterministas: `forward`, `reverse`, `center`.
- Resaltado semántico de palabras clave con escala elástica, resplandor (*glow*) y cambio de color.

### 1.2. Dinámicas de Cámara 2D y Sacudida Determinista (`CameraDynamicsEngine`)
- Movimientos de cámara: `snapZoom`, `subtlePush`, `dramaticPush`, `horizontalPan`.
- Sacudida orgánica determinista con PRNG pseudoaleatorio inicializado con semilla fija (*seeded randomness*).

### 1.3. Sistema de Partículas (`ParticleEngine`)
- Emisores deterministas de partículas: `confetti`, `spark`, `dust`, `celebration`.

### 1.4. Macros de Movimiento y Presupuesto (`MotionMacroRegistry`, `MotionBudgetManager`)
- Macros predefinidos: `high-impact-hook`, `statistic-pop`, `keyword-highlight`, `subscribe-cta`.
- Medición de complejidad visual $C \in [0, 1]$ y control de presupuesto (`low`, `medium`, `high`).
