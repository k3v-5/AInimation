# Especificación Técnica: Fase 8 — AI Director & Multi-Agent Editing

**Documento:** `spec/phase-8-ai-director.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/ai-director/`

---

## 0. Propósito y Principio Arquitectónico

La **Fase 8** implementa la capa de dirección creativa y orquestación multi-agente (`AI Director`), donde agentes especialistas independientes formulan propuestas estructuradas y el Director arbitra de manera determinista:

$$\text{User Brief} \longrightarrow \text{AI Director} \rightleftarrows \{\text{Story, Visual, Audio, Caption, Motion Agents}\} \longrightarrow \text{Arbitration} \longrightarrow \text{EditingPlan}$$

```
                           USER BRIEF
                               │
                               ↓
                        ┌─────────────┐
                        │ AI DIRECTOR │
                        └──────┬──────┘
                               │
          ┌────────────────────┼────────────────────┐
          ↓                    ↓                    ↓
     STORY AGENT          VISUAL AGENT         AUDIO AGENT
  (Narrative & Hook)    (B-roll & Shots)    (Music, SFX & Sync)
          │                    │                    │
          ├──────────────┬─────┴──────────────┬─────┤
                         ↓                    ↓
                   CAPTION AGENT        MOTION AGENT
                 (Timing & Density)   (Budget & Springs)
                         │                    │
                         └──────────┬─────────┘
                                    ↓
                           CONFLICT ARBITRATOR
                                    ↓
                              EDITING PLAN
                                    ↓
                             REVISION ENGINE
```

---

## 1. Agentes Especialistas y Contratos (`EditingAgent`, `AgentProposal`)

1. **`StoryAgent`:** Detecta *hooks*, estructura en actos/secciones (`hook`, `setup`, `main-point`, `cta`) y define curvas de retención.
2. **`VisualAgent`:** Selecciona tomas B-roll a partir de `AssetIntelligence`, calcula variedad visual de encuadres y propone transiciones.
3. **`AudioAgent`:** Asigna bandas sonoras, sincroniza puntos de corte con golpes rítmicos (*beats*) y ubica efectos sonoros (*SFX*).
4. **`CaptionAgent`:** Segmenta subtítulos, marca palabras clave de impacto y valida zonas seguras.
5. **`MotionAgent`:** Asigna presupuestos de movimiento (*motion budget*) y propiedades reactivas.

---

## 2. Arbitraje, Sesiones y Replanificación Parcial (`ConflictArbitrator`, `RevisionEngine`)

1. **`ConflictArbitrator`:** Resuelve discrepancias temporales y estilísticas entre propuestas de agentes basándose en prioridades configurables ($\text{Narrative} > \text{Audio/Beats} > \text{B-roll}$).
2. **`PlanningSession` & `TraceLog`:** Mantiene estado, bitácora de decisiones explicables y puntos de control (*checkpoints*).
3. **`RevisionEngine` & Replanificación Parcial:** Procesa retroalimentación del usuario (*"cambia la música"*, *"hazlo más dinámico"*) recalculando únicamente las ramas del grafo de dependencias afectadas.
