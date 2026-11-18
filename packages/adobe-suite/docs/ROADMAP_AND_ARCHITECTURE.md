# Adobe Animation Engine - Roadmap & Architecture

Este documento detalla la visión, arquitectura y plan maestro (roadmap) para construir una **plataforma inteligente de animación** (Operating System for Agentic Animation). El proyecto nace como un motor de animación integral, con **Character Animator como primer objetivo prioritario (P0)**, pero diseñado desde el día cero para soportar cualquier motor gráfico, empezando por la suite de Adobe.

---

## 1. Visión Arquitectónica y Capas Estrictas

La regla de oro del sistema es: **La IA no debería saber cómo controlar Adobe. Debe expresar intención creativa; el Engine decide cómo materializarla.**

### Jerarquía de Capas

```text
User Intent (La petición del usuario)
     ↓
Intent Model (Abstracción semántica)
     ↓
Animation Plan (Pasos universales)
     ↓
Animation Operations (Operaciones a realizar)
     ↓
Provider Commands (Traducción específica de la app)
     ↓
Adobe Runtime (MCP, Scripts, etc.)
     ↓
Perception Layer (Lectura del resultado)
     ↓
Observed State (Estado real actual)
```

### Arquitectura Final

```text
                         ┌─────────────────────┐
                         │        AI           │
                         │ Planner / Agent     │
                         └──────────┬──────────┘
                                    │
                              Intent / Goal
                                    │
                                    ▼
                    ┌────────────────────────────┐
                    │      ANIMATION ENGINE      │
                    │                            │
                    │ Intent Model               │
                    │ Planner                    │
                    │ Workflow Graph              │
                    │ Animation DSL              │
                    │ Scene Graph                │
                    │ Timeline                   │
                    │ Artifact Graph             │
                    │ State (Desired/Observed)   │
                    │ Validation                 │
                    │ Recovery                   │
                    └─────────────┬──────────────┘
                                  │
                            Capability
                              Resolver
                                  │
               ┌──────────────────┼──────────────────┐
               │                  │                  │
               ▼                  ▼                  ▼
        Character Animator   After Effects       Animate
            Provider            Provider         Provider
               │                  │                  │
               └──────────────┬───┴──────────────────┘
                              │
                         Adobe Runtime
                              │
                ┌─────────────┼──────────────┐
                ▼             ▼              ▼
              MCP          Scripts          APIs
                              │
                              ▼
                        Adobe Applications
                              │
                              ▼
                         Perception
                              │
                              ▼
                        Observed State
                              │
                              └──────────► Validation
                                               │
                                  ┌────────────┴───────────┐
                                  │                        │
                                PASS                    FAIL
                                  │                        │
                                Done              Repair / Replan
```

---

## 2. Los 10 Conceptos Centrales (Las Abstracciones Congeladas)

Para sostener este motor, definimos y congelamos 10 abstracciones fundamentales:

### 1. Intent y 2. Plan
La IA produce intenciones (ej. `make_character_wave`) que se traducen en un **Plan** secuencial y universal, independiente del proveedor.

### 3. Operation y Execution State Machine
Cada acción es una `Operation` que vive dentro de una máquina de estados (PLANNED -> VALIDATED -> QUEUED -> EXECUTING -> OBSERVING -> VALIDATED -> SUCCESS / DIVERGED -> RECOVERY). Cada operación tiene historial (intentos, errores, estado).

### 4. Capability y 5. Provider (Capability Contract)
Las capacidades no son solo IDs, son contratos estrictos. Un `Provider` (ej. Character Animator) expone capacidades que declaran:
*   `inputSchema` / `outputSchema`
*   `reliability` (experimental, stable)
*   `reversibility` (reversible, irreversible)
*   `observability`

**Fallback basado en Estrategias:** Si un Goal requiere la capability `audio.lip_sync`, el motor evalúa estrategias (Estrategia A: CA native, Estrategia B: AE + phoneme parser) en lugar de un fallback estricto de app.

### 6. Artifact System
Un `Artifact` es el resultado de una operación (ej. un PSD de personaje, un render intermedio). Cada artefacto tiene identidad, versión y rastrea dependencias, permitiendo regenerar solo lo necesario.

### 7. Desired State y 8. Observed State (EntityState)
El "Shadow State" se reemplaza por un modelo robusto de conciliación:
```typescript
type EntityState<T> = {
  desired: T
  observed?: T
  status: "unknown" | "synchronized" | "pending" | "diverged" | "error"
}
```
Si `desired != observed`, el sistema entra en modo de reparación (Self-healing).

### 9. Workflow Graph
Más allá de dependencias de assets, el Workflow Graph representa el lenguaje de ejecución del agente (Generate Character -> Rig -> Lip Sync -> Animate -> Composite), asignando nodos (Capabilities) dinámicamente a los proveedores disponibles.

### 10. Validation / Recovery (Perception Layer)
La capa de percepción (`Perception`) observa el estado tras la ejecución. Si el estado divirgió (DIVERGED), el subsistema de `Recovery` intenta reparar la inconsistencia antes de marcar un fallo catastrófico.

---

## 3. Universal DSL

El DSL **no se diseña alrededor de Adobe**. Se diseña sobre conceptos universales de animación:
*   `character.create()`, `character.rig()`, `character.pose()`
*   `animation.sequence()`, `animation.transition()`
*   `audio.analyze()`, `speech.lipSync()`
*   `render.preview()`

Esto garantiza que mañana se puedan agregar providers como `BlenderProvider` o `UnrealProvider` sin cambiar el cerebro de la IA.

---

## 4. Plan Maestro y Milestones Actualizados

### 🚩 Milestone 0 — Reality Check (Fase 0)
Auditar APIs reales, MCP, Scripts y UI automation. Identificar qué podemos controlar realmente de Adobe de manera fiable y clasificar el nivel de soporte real.

### 🚩 Milestone 1 — Runtime Foundation (Fases 1 y 2)
Establecer el Core (AnimationEngine, Scene, Timeline, Entity, Artifact, Operation, State) y el Runtime (Provider, Capability, Adapter, Transport, Event Bus).

### 🚩 Milestone 2 — Character Animator (Fase 3)
Empezar pequeño con el primer Provider P0: Project, Puppet, Behavior, Trigger, Recording, Timeline, Export.

### 🚩 Milestone 3 — DSL (Fase 4)
Introducir los lenguajes formales: Intent DSL, Plan DSL, Operation DSL.

### 🚩 Milestone 4 — Closed Loop (Fases 5 y 6)
Integrar el Planner de IA y el ciclo cerrado: Execute -> Observe -> Validate -> Repair. Aquí nace el producto Agentic.

### 🚩 Milestone 5 — Multi-App (Fases posteriores)
Agregar After Effects, Animate, Illustrator, Photoshop, Premiere. Orchestración multi-app donde la IA decide qué aplicación utilizar para cada etapa del Workflow Graph.

## 5. Iteración 2 (Conexión Real, DAG y Resiliencia)
- **Deep Integration con Character Animator:** Spike e implementación de interacción real y lectura de estado con Character Animator (expandiendo adobe-mcp).
- **DAG Inference Engine:** Reemplazo de ejecución lineal por un WorkflowGraph que resuelve dependencias concurrentemente.
- **Graceful Shutdown:** Intercepción de señales SIGINT/SIGTERM y AbortController transversal para limpieza de procesos de adobe-mcp.

## 6. Iteración 3 (Realidad Adobe y DSL Dinámico)
- **Parser Dinámico (Zod):** Validación estricta de un DSL de intenciones complejas (Personajes, Escenas, Audio) y traducción dinámica a nodos del DAG.
- **Layer 0 Blackbox Integration:** Implementación física de la manipulación de Character Animator vía clonación de proyectos `.chproj` y OS Automation.
- **Percepción Física:** Reemplazo de estados mockeados por observadores reales del sistema de archivos (bloqueos, tamaños, existencias de `.mp4` o `.puppet`).

## 7. Iteración 4 (Control Robótico y Cierre de P0)
- **Motor de Macros (UI Automation):** Implementación de secuencias de teclado y ratón con Python (`pyautogui`, `pywinctl`) para manejar operaciones opacas en Character Animator como Lip Sync y Exportación.
- **Resiliencia de Interfaz (Focus Validation):** Prevención de errores inyectando comandos solo cuando Character Animator es la ventana activa confirmada en el SO, con pausas dinámicas ante pérdida de foco.

## 8. Iteración 5 (Orquestación Multi-App y Post-Producción)
- **Paso de Contexto y Artefactos:** Resolución en tiempo real de dependencias usando templating (`${node_1.output}`) en el WorkflowGraphEngine.
- **Provider Routing:** Capacidad de ejecutar grafos cruzando múltiples aplicaciones en el mismo flujo.
- **After Effects Provider:** Integración oficial de ExtendScript para componer y renderizar salidas producidas por Character Animator.

## 9. Iteración 6 (Agent Planner & System Prompting)
- **Ingeniería de Prompts:** Creación del System Prompt del Director de Animación para instruir a la IA sobre cómo armar Grafos válidos respetando dependencias (`${node_id.output}`) y capacidades (`puppet.pose`, `ae.comp.create`).
- **Self-Healing Cognitivo:** Implementación del bucle de reflexión del LLM para auto-corregir JSONs si el Engine devuelve errores de validación de Zod.
- **Clarificación Interactiva:** Comportamiento determinista del Agente para pedir recursos faltantes (como rutas de audio o PSDs) antes de alucinar rutas inexistentes.

## 10. Iteración 7 (La Fábrica de Assets - End-to-End Pipeline)
- **Activación de Providers Estáticos:** Implementación real de `PhotoshopProvider` e `IllustratorProvider` conectando con los comandos nativos de `adobe-mcp` (`adobe_ps_new_document`, `adobe_ps_layers`).
- **Orquestación Asset -> Animación:** Inyección de contexto donde el motor de inferencia toma el `.psd` recién generado en Photoshop y lo pasa dinámicamente como *input* a Character Animator y posteriormente a After Effects.
- **Autonomía Cognitiva (AC-21):** El Agente Planner (LLM) ya no depende de rutas locales proveídas por el usuario, ahora genera proactivamente los assets visuales si no se proporcionan, cerrando el ciclo End-to-End.

## 11. Iteración 8 (CLI de Producción y Observabilidad)
- **TUI (Terminal UI):** Un bucle REPL para chatear con el Agente de IA y visualización en tiempo real del progreso concurrente del DAG (Spinners).
- **Logging Estructurado:** Implementación de `pino` para auditoría de eventos en formato JSON persistente, preparado para servidores `PM2`.
- **Experiencia de Usuario Continua:** El motor pasa a comportarse como un daemon o herramienta de consola interactiva persistente.

## 12. Iteración 9 (Memoria de Proyecto y Contexto Persistente)
- **Persistencia SQLite:** Implementación de `ProjectManager` con `better-sqlite3` para guardar proyectos, assets y ejecuciones.
- **RAG Local:** Herramientas de memoria MCP (`memory.list_projects`, `memory.get_assets`) añadidas al Agente para recordar sesiones pasadas.
- **DAG Cache-Aware:** Inferencia condicional para omitir nodos si los assets de salida ya existen (Ej. no abrir Photoshop si el PSD ya fue creado), con invalidación inteligente usando la capa de percepción física.
