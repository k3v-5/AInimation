# Especificación Técnica: Fase 14 — AI Director & Editing Intelligence

**Documento:** `spec/phase-14-ai-director-editing-intelligence.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/editing-intelligence/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 14** implementa el cerebro editorial del sistema (*AI Director & Editing Intelligence*), transformando el material en crudo en un plan de edición estructurado y validable en dos niveles (Semántico $\to$ Ejecución), con resolución determinista de restricciones (*Constraint Solver*) y reparación automática:

$$\text{Raw Material} \longrightarrow \text{ContentModel} \longrightarrow \text{AI Director} \longrightarrow \text{Semantic Edit Plan} \longrightarrow \text{Constraint Solver \& Repair} \longrightarrow \text{Validated Plan}$$

```
                           RAW MATERIAL
                   (Transcript, Audio, Vision)
                                │
                                ↓
                          CONTENT MODEL
                 (Segments, Hooks, Importance)
                                │
                                ↓
                           AI DIRECTOR
                 ┌──────────────┼──────────────┐
                 ↓              ↓              ↓
               STORY          PACING         STYLE
                 │              │              │
                 └──────────────┼──────────────┘
                                ↓
                       SEMANTIC EDIT PLAN
                   (Nivel 1: Qué conseguir)
                                │
                                ↓
                        EXECUTION PLANNER
                   (Nivel 2: Cómo conseguirlo)
                                │
                                ↓
                        CONSTRAINT SOLVER
               (Spatial, Temporal & Style Conflicts)
                                │
                                ↓
                     VALIDATOR & AUTO-REPAIR
                                │
                                ↓
                         VALIDATED PLAN
```

---

## 1. Módulos y Capacidades Clave

### 1.1. Modelo de Contenido y Detección de Hooks (`ContentModelBuilder`)
- Segmentación con puntuaciones de importancia $I \in [0, 1]$ y etiquetas semánticas.
- Detección y puntuación de candidatos a *hook* inicial (`curiosity`, `statement`, `question`).

### 1.2. Estructura Narrativa y Motor de Ritmo (`StoryAndPacingPlanner`)
- Grafo narrativo canónico: `hook -> context -> problem -> explanation -> reveal -> CTA`.
- Perfiles de ritmo (*pacing profiles*): `fast_social`, `medium_social`, `educational`, `cinematic`.

### 1.3. Plan de Edición en Dos Niveles (`SemanticEditPlanner`)
- Nivel 1 (Semántico): directivas abstractas (`"enfatizar palabra IA"`, `"insertar B-roll de servidor"`).
- Nivel 2 (Ejecución): asignación concreta de capas, keyframes, SFX y parámetros.
- Registro explicativo de decisiones (*Edit Decision Log*) con nivel de confianza.

### 1.4. Resolvedor de Restricciones y Reparación Automática (`ConstraintSolver`, `PlanValidatorAndRepair`)
- Detección de colisiones espaciales (subtítulos sobre rostros) y temporales ($\pm 100\text{ms}$ para SFX).
- Reparación automática determinista sin necesidad de re-consultar al modelo de lenguaje.

### 1.5. Edición Iterativa por Parches (`IterativePlanPatcher`)
- Aplicación de deltas (`"hazlo 20% más rápido"`, `"menos SFX"`) mediante parches parciales (`PlanPatch`).
